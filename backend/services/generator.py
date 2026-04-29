import json
import os
from pathlib import Path

import anthropic

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SYSTEM_PROMPT = Path(__file__).parent.parent / "prompts" / "menu_system.txt"


async def generate_week_menu(week_start: str) -> dict:
    system_text = SYSTEM_PROMPT.read_text(encoding="utf-8")

    for attempt in range(3):
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": system_text,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"请生成从 {week_start} 开始那一周（周一至周五）的菜单。",
                }
            ],
        )
        try:
            menu = json.loads(response.content[0].text)
            errors = validate_menu(menu)
            if not errors:
                return menu
            print(f"Attempt {attempt + 1} validation errors: {errors}")
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1} JSON parse error: {e}")

    raise RuntimeError("Menu generation failed after 3 attempts")


def validate_menu(menu: dict) -> list[str]:
    errors = []
    dish_counts: dict[str, int] = {}
    salmon_count = 0
    hard_dish_count = 0

    for day in menu.get("days", []):
        for meal_type in ["lunch", "dinner"]:
            meal = day.get(meal_type, {})
            dishes = meal.get("dishes", [])
            optional = meal.get("optional")
            soup = meal.get("soup")

            all_dishes = dishes + ([optional] if optional else []) + ([soup] if soup else [])

            for dish in all_dishes:
                name = dish.get("name", "")
                diff = dish.get("diff", 0)
                tag = dish.get("tag", "")

                dish_counts[name] = dish_counts.get(name, 0) + 1
                if dish_counts[name] > 2:
                    errors.append(f"Dish '{name}' appears more than 2× in the week")

                if "三文鱼" in name or "salmon" in name.lower():
                    salmon_count += 1

                if diff == 3:
                    hard_dish_count += 1

                if meal_type == "lunch" and tag == "meat":
                    forbidden = ["牛腩", "肥牛", "肥羊"]
                    if any(f in name for f in forbidden):
                        errors.append(f"Lunch dish '{name}' uses forbidden protein")

    if salmon_count > 1:
        errors.append(f"Salmon appears {salmon_count}× (max 1)")
    if hard_dish_count > 2:
        errors.append(f"{hard_dish_count} ⭐⭐⭐ dishes (max 2)")

    return errors


# ── Ingredient extraction ─────────────────────────────────────────────────────

COSTCO_KEYWORDS = [
    "猪肉",
    "里脊",
    "五花",
    "猪排",
    "排骨",
    "鸡肉",
    "鸡翅",
    "鸡腿",
    "牛腩",
    "肥牛",
    "肥羊",
    "虾",
    "三文鱼",
    "鸡蛋",
    "鸡",
]


def classify_store(name: str) -> str:
    for keyword in COSTCO_KEYWORDS:
        if keyword in name:
            return "costco"
    return "tnt"


def classify_category(name: str) -> str:
    protein_keywords = ["猪", "鸡", "牛", "羊", "虾", "鱼", "肉", "排骨"]
    pantry_keywords = ["酱油", "醋", "盐", "糖", "油", "料酒", "花椒", "淀粉", "鸡蛋"]
    if any(k in name for k in protein_keywords):
        return "protein"
    if any(k in name for k in pantry_keywords):
        return "pantry"
    return "veggie"


def extract_ingredients(menu: dict) -> list[dict]:
    seen: set[str] = set()
    result = []

    for day in menu.get("days", []):
        for meal_type in ["lunch", "dinner"]:
            meal = day.get(meal_type, {})
            all_dishes = meal.get("dishes", [])
            if meal.get("optional"):
                all_dishes = all_dishes + [meal["optional"]]
            if meal.get("soup"):
                all_dishes = all_dishes + [meal["soup"]]

            for dish in all_dishes:
                raw = dish.get("ingredients", "")
                for part in raw.replace("，", "、").replace(",", "、").split("、"):
                    name = part.strip().split("(")[0].split("（")[0].strip()
                    if name and name not in seen:
                        seen.add(name)
                        result.append(
                            {
                                "name": name,
                                "store": classify_store(name),
                                "category": classify_category(name),
                            }
                        )
    return result
