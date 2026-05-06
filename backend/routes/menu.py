from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from database import get_db
from models import (
    Config,
    Ingredient,
    IngredientSchema,
    IngredientUpdateRequest,
    Meal,
    MealSchema,
    MealUpdateRequest,
    PromptUpdateRequest,
    Week,
    WeekSchema,
    WeekSummarySchema,
)
from services.generator import extract_ingredients, generate_week_menu
from services.regen import fill_dish_by_name, regen_single_dish

_SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "menu_system.txt"

router = APIRouter(prefix="/api")


def _next_monday() -> date:
    today = date.today()
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


def _current_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


async def _get_all_dish_names(db: AsyncSession, week_id: str) -> list[str]:
    result = await db.execute(select(Meal).where(Meal.week_id == week_id))
    meals = result.scalars().all()
    names = []
    for meal in meals:
        for slot in [meal.dish1, meal.dish2, meal.optional_dish, meal.soup]:
            if slot and isinstance(slot, dict):
                names.append(slot.get("name", ""))
    return [n for n in names if n]


# ── GET /api/week/current ─────────────────────────────────────────────────────


@router.get("/week/current", response_model=WeekSchema | None)
async def get_current_week(db: AsyncSession = Depends(get_db)):
    monday = _current_monday()
    result = await db.execute(select(Week).where(Week.week_start == monday))
    week = result.scalar_one_or_none()
    if not week:
        return None
    await db.refresh(week, ["meals"])
    return week


# ── POST /api/generate ────────────────────────────────────────────────────────


@router.post("/generate")
async def generate_menu(db: AsyncSession = Depends(get_db)):
    # Use current week if it has no menu yet; otherwise generate next week
    current = _current_monday()
    existing = await db.execute(select(Week).where(Week.week_start == current))
    monday = current if not existing.scalar_one_or_none() else _next_monday()

    result = await db.execute(select(Week).where(Week.week_start == monday))
    week = result.scalar_one_or_none()

    if week and week.status == "ready":
        return {"message": "Menu already exists", "week_id": week.id}

    if not week:
        week = Week(week_start=monday, status="pending")
        db.add(week)
        await db.flush()

    week.status = "pending"

    prompt_result = await db.execute(select(Config).where(Config.key == "menu_system_prompt"))
    prompt_config = prompt_result.scalar_one_or_none()
    custom_prompt = prompt_config.value if prompt_config else None

    prev_result = await db.execute(
        select(Week)
        .where(Week.week_start < monday, Week.status == "ready")
        .order_by(Week.week_start.desc())
        .limit(1)
    )
    prev_week = prev_result.scalar_one_or_none()
    prev_dishes: list[str] = []
    if prev_week:
        await db.refresh(prev_week, ["meals"])
        prev_dishes = await _get_all_dish_names(db, prev_week.id)

    try:
        menu = await generate_week_menu(
            str(monday), system_text=custom_prompt, prev_dishes=prev_dishes
        )
    except RuntimeError as e:
        week.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    days_order = ["周一", "周二", "周三", "周四", "周五"]

    for day_data in menu.get("days", []):
        day_name = day_data.get("day")
        if day_name not in days_order:
            continue

        for meal_type in ["lunch", "dinner"]:
            meal_data = day_data.get(meal_type, {})
            dishes = meal_data.get("dishes", [])

            existing = await db.execute(
                select(Meal).where(
                    Meal.week_id == week.id,
                    Meal.day == day_name,
                    Meal.meal_type == meal_type,
                )
            )
            meal = existing.scalar_one_or_none()
            if not meal:
                meal = Meal(week_id=week.id, day=day_name, meal_type=meal_type)
                db.add(meal)

            meal.dish1 = dishes[0] if len(dishes) > 0 else None
            meal.dish2 = dishes[1] if len(dishes) > 1 else None
            meal.optional_dish = meal_data.get("optional")
            meal.soup = meal_data.get("soup")

    # extract and store ingredients
    existing_ing = await db.execute(select(Ingredient).where(Ingredient.week_id == week.id))
    for ing in existing_ing.scalars().all():
        await db.delete(ing)

    for ing_data in extract_ingredients(menu):
        db.add(
            Ingredient(
                week_id=week.id,
                name=ing_data["name"],
                store=ing_data["store"],
                category=ing_data["category"],
            )
        )

    week.generated_at = datetime.now(UTC).replace(tzinfo=None)
    week.status = "ready"
    await db.commit()

    return {"message": "Menu generated", "week_id": week.id, "week_start": str(monday)}


# ── PUT /api/meal/{id} ────────────────────────────────────────────────────────


@router.put("/meal/{meal_id}", response_model=MealSchema)
async def update_meal(meal_id: str, body: MealUpdateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meal).where(Meal.id == meal_id))
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    slot = body.dish_slot
    if slot == "dish1":
        meal.dish1 = body.dish
    elif slot == "dish2":
        meal.dish2 = body.dish
    elif slot == "optional_dish":
        meal.optional_dish = body.dish
    elif slot == "soup":
        meal.soup = body.dish
    else:
        raise HTTPException(status_code=400, detail=f"Unknown dish_slot: {slot}")
    flag_modified(meal, slot)

    await db.commit()
    await db.refresh(meal)
    return meal


# ── POST /api/meal/{id}/regen ─────────────────────────────────────────────────


@router.post("/meal/{meal_id}/regen", response_model=MealSchema)
async def regen_meal_dish(
    meal_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Meal).where(Meal.id == meal_id))
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    dish_slot = body.get("dish_slot", "dish1")
    current_dish = getattr(meal, dish_slot, None) or {}
    diff_level = current_dish.get("diff", 2)

    existing_names = await _get_all_dish_names(db, meal.week_id)

    new_dish = await regen_single_dish(
        meal_type=meal.meal_type,
        dish_slot=dish_slot,
        diff_level=diff_level,
        existing_dishes=existing_names,
    )

    if dish_slot == "dish1":
        meal.dish1 = new_dish
    elif dish_slot == "dish2":
        meal.dish2 = new_dish
    elif dish_slot == "optional_dish":
        meal.optional_dish = new_dish
    elif dish_slot == "soup":
        meal.soup = new_dish
    flag_modified(meal, dish_slot)

    await db.commit()
    await db.refresh(meal)
    return meal


# ── POST /api/meal/{id}/fill ──────────────────────────────────────────────────


@router.post("/meal/{meal_id}/fill", response_model=MealSchema)
async def fill_meal_dish(
    meal_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Meal).where(Meal.id == meal_id))
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    dish_slot = body.get("dish_slot", "dish1")
    name = body.get("name", "").strip()
    url = body.get("url") or None

    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    current_dish = getattr(meal, dish_slot, None) or {}
    tag = current_dish.get("tag", "veg") if isinstance(current_dish, dict) else "veg"

    try:
        new_dish = await fill_dish_by_name(name=name, tag=tag, url=url)
    except Exception:
        new_dish = {
            "name": name,
            "tag": tag,
            "diff": 2,
            "style": "",
            "ingredients": "",
            "steps": [],
        }
        if url:
            new_dish["url"] = url

    if dish_slot == "dish1":
        meal.dish1 = new_dish
    elif dish_slot == "dish2":
        meal.dish2 = new_dish
    elif dish_slot == "optional_dish":
        meal.optional_dish = new_dish
    elif dish_slot == "soup":
        meal.soup = new_dish
    flag_modified(meal, dish_slot)

    await db.commit()
    await db.refresh(meal)
    return meal


# ── GET /api/history ──────────────────────────────────────────────────────────


@router.get("/history", response_model=list[WeekSummarySchema])
async def get_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Week).where(Week.status == "ready").order_by(Week.week_start.desc())
    )
    weeks = result.scalars().all()

    summaries = []
    for week in weeks:
        count_result = await db.execute(select(func.count()).where(Meal.week_id == week.id))
        dish_count = count_result.scalar() or 0
        summaries.append(
            WeekSummarySchema(
                id=week.id,
                week_start=week.week_start,
                generated_at=week.generated_at,
                status=week.status,
                dish_count=dish_count * 2,  # rough estimate: 2 main dishes per meal
            )
        )
    return summaries


# ── GET /api/week/{id} ────────────────────────────────────────────────────────


@router.get("/week/{week_id}", response_model=WeekSchema)
async def get_week(week_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Week).where(Week.id == week_id))
    week = result.scalar_one_or_none()
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    await db.refresh(week, ["meals"])
    return week


# ── GET /api/ingredients/current ─────────────────────────────────────────────


@router.get("/ingredients/current", response_model=list[IngredientSchema])
async def get_current_ingredients(db: AsyncSession = Depends(get_db)):
    monday = _current_monday()
    result = await db.execute(select(Week).where(Week.week_start == monday))
    week = result.scalar_one_or_none()
    if not week:
        return []

    ing_result = await db.execute(select(Ingredient).where(Ingredient.week_id == week.id))
    return ing_result.scalars().all()


# ── PUT /api/ingredients/{id} ─────────────────────────────────────────────────


@router.put("/ingredients/{ing_id}", response_model=IngredientSchema)
async def update_ingredient(
    ing_id: str, body: IngredientUpdateRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Ingredient).where(Ingredient.id == ing_id))
    ing = result.scalar_one_or_none()
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if body.checked is not None:
        ing.checked = body.checked
    if body.store is not None:
        ing.store = body.store
        ing.overridden = True

    await db.commit()
    await db.refresh(ing)
    return ing


# ── DELETE /api/week/{id} ─────────────────────────────────────────────────────


@router.delete("/week/{week_id}")
async def delete_week(week_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Week).where(Week.id == week_id))
    week = result.scalar_one_or_none()
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    await db.delete(week)
    await db.commit()
    return {"message": "Week deleted"}


# ── GET /api/health ───────────────────────────────────────────────────────────


@router.get("/health")
async def health():
    return {"status": "ok"}


# ── GET /api/prompt ───────────────────────────────────────────────────────────


@router.get("/prompt")
async def get_prompt(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Config).where(Config.key == "menu_system_prompt"))
    config = result.scalar_one_or_none()
    if config:
        return {"content": config.value, "is_custom": True}
    return {"content": _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"), "is_custom": False}


# ── PUT /api/prompt ───────────────────────────────────────────────────────────


@router.put("/prompt")
async def update_prompt(body: PromptUpdateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Config).where(Config.key == "menu_system_prompt"))
    config = result.scalar_one_or_none()
    if config:
        config.value = body.content
    else:
        config = Config(key="menu_system_prompt", value=body.content)
        db.add(config)
    await db.commit()
    return {"message": "Prompt updated"}


# ── DELETE /api/prompt ────────────────────────────────────────────────────────


@router.delete("/prompt")
async def reset_prompt(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Config).where(Config.key == "menu_system_prompt"))
    config = result.scalar_one_or_none()
    if config:
        await db.delete(config)
        await db.commit()
    return {"content": _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"), "is_custom": False}
