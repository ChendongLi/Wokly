import json
import logging
import os
from pathlib import Path

from services import llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = Path(__file__).parent.parent / "prompts" / "menu_system.txt"


_MOCK_MENU = {
    "week_start": "__WEEK_START__",
    "days": [
        {
            "day": "周一",
            "lunch": {
                "dishes": [
                    {
                        "name": "木须肉",
                        "tag": "meat",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "猪里脊150g、鸡蛋2个、木耳50g、黄瓜半根、葱姜蒜",
                        "steps": [
                            "里脊切片腌10分钟",
                            "鸡蛋炒散木耳黄瓜备用",
                            "爆香葱姜蒜炒肉片下配料翻炒均匀",
                        ],
                        "search_query": "木须肉做法",
                    },
                    {
                        "name": "地三鲜",
                        "tag": "veg",
                        "style": "炖烧",
                        "diff": 2,
                        "ingredients": "茄子1根、土豆1个、青椒1个、葱姜蒜、生抽老抽",
                        "steps": ["茄子土豆过油", "爆香葱姜蒜下蔬菜翻炒", "加生抽老抽焖5分钟"],
                        "search_query": "地三鲜做法",
                    },
                ],
                "optional": {
                    "name": "凉拌黄瓜",
                    "tag": "opt",
                    "style": "凉拌",
                    "diff": 1,
                    "ingredients": "黄瓜1根、蒜末、醋、盐、香油",
                    "steps": ["黄瓜拍碎切段", "加蒜末醋盐香油拌匀"],
                    "search_query": "凉拌黄瓜",
                },
            },
            "dinner": {
                "dishes": [
                    {
                        "name": "红烧鸡块",
                        "tag": "meat",
                        "style": "炖烧",
                        "diff": 3,
                        "ingredients": "鸡半只、土豆1个、葱姜蒜、生抽老抽料酒冰糖",
                        "steps": [
                            "鸡块焯水",
                            "炒糖色下鸡块翻炒上色",
                            "加生抽老抽料酒加水焖30分钟",
                            "下土豆焖10分钟收汁",
                        ],
                        "search_query": "红烧鸡块做法",
                    },
                    {
                        "name": "蒜蓉菠菜",
                        "tag": "veg",
                        "style": "快炒",
                        "diff": 1,
                        "ingredients": "菠菜300g、蒜末、盐、香油",
                        "steps": ["菠菜焯水过凉", "蒜末爆香下菠菜翻炒调味"],
                        "search_query": "蒜蓉菠菜",
                    },
                ],
                "soup": {
                    "name": "紫菜蛋花汤",
                    "tag": "soup",
                    "style": "汤",
                    "diff": 1,
                    "ingredients": "紫菜10g、鸡蛋1个、葱花、盐、香油",
                    "steps": ["水烧开下紫菜", "蛋液冲入汤中", "加盐香油葱花即可"],
                    "search_query": "紫菜蛋花汤",
                },
            },
        },
        {
            "day": "周二",
            "lunch": {
                "dishes": [
                    {
                        "name": "鱼香肉丝",
                        "tag": "meat",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "猪里脊200g、木耳30g、胡萝卜半根、葱姜蒜、豆瓣酱、生抽醋糖",
                        "steps": [
                            "肉丝腌制配料切丝",
                            "爆香葱姜蒜豆瓣酱",
                            "下肉丝配料翻炒调鱼香汁收汁",
                        ],
                        "search_query": "鱼香肉丝做法",
                    },
                    {
                        "name": "荷塘月色",
                        "tag": "veg",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "莲藕150g、木耳30g、荷兰豆50g、胡萝卜半根、葱姜",
                        "steps": ["蔬菜切好焯水备用", "热锅爆香葱姜", "下全部蔬菜翻炒调味"],
                        "search_query": "荷塘月色做法",
                    },
                ],
                "optional": {
                    "name": "番茄炒鸡蛋",
                    "tag": "opt",
                    "style": "快炒",
                    "diff": 1,
                    "ingredients": "番茄2个、鸡蛋3个、葱、盐、糖",
                    "steps": ["鸡蛋炒散盛出", "番茄炒软下鸡蛋翻炒调味"],
                    "search_query": "番茄炒鸡蛋",
                },
            },
            "dinner": {
                "dishes": [
                    {
                        "name": "可乐鸡翅",
                        "tag": "meat",
                        "style": "炖烧",
                        "diff": 2,
                        "ingredients": "鸡翅500g、可乐1罐、生抽老抽、姜片",
                        "steps": ["鸡翅焯水", "煎至两面金黄", "倒可乐生抽老抽焖20分钟收汁"],
                        "search_query": "可乐鸡翅做法",
                    },
                    {
                        "name": "清炒丝瓜",
                        "tag": "veg",
                        "style": "快炒",
                        "diff": 1,
                        "ingredients": "丝瓜1根、蒜末、盐",
                        "steps": ["丝瓜切块", "蒜末爆香下丝瓜大火翻炒调味"],
                        "search_query": "清炒丝瓜",
                    },
                ],
                "soup": {
                    "name": "番茄蛋花汤",
                    "tag": "soup",
                    "style": "汤",
                    "diff": 1,
                    "ingredients": "番茄1个、鸡蛋1个、葱花、盐",
                    "steps": ["番茄切块炒软加水煮开", "蛋液冲入加盐葱花"],
                    "search_query": "番茄蛋花汤",
                },
            },
        },
        {
            "day": "周三",
            "lunch": {
                "dishes": [
                    {
                        "name": "葱爆猪肉",
                        "tag": "meat",
                        "style": "葱爆",
                        "diff": 2,
                        "ingredients": "猪里脊200g、大葱2根、生抽料酒淀粉",
                        "steps": ["肉片腌制10分钟", "大葱切段备用", "大火爆香葱段下肉片翻炒调味"],
                        "search_query": "葱爆猪肉做法",
                    },
                    {
                        "name": "炒合菜",
                        "tag": "veg",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "白菜100g、粉丝50g、木耳30g、胡萝卜半根、葱姜",
                        "steps": [
                            "粉丝泡发蔬菜切好",
                            "爆香葱姜下胡萝卜木耳翻炒",
                            "下白菜粉丝翻炒调味",
                        ],
                        "search_query": "炒合菜做法",
                    },
                ],
                "optional": {
                    "name": "皮蛋豆腐",
                    "tag": "opt",
                    "style": "凉拌",
                    "diff": 1,
                    "ingredients": "皮蛋2个、嫩豆腐1块、葱花、生抽、香油",
                    "steps": ["豆腐切块装盘皮蛋切块摆放", "淋生抽香油撒葱花即可"],
                    "search_query": "皮蛋豆腐",
                },
            },
            "dinner": {
                "dishes": [
                    {
                        "name": "土豆烧排骨",
                        "tag": "meat",
                        "style": "炖烧",
                        "diff": 3,
                        "ingredients": "排骨500g、土豆2个、葱姜蒜、生抽老抽料酒",
                        "steps": [
                            "排骨焯水",
                            "炒香葱姜蒜下排骨翻炒上色",
                            "加调料加水焖30分钟",
                            "下土豆再焖15分钟收汁",
                        ],
                        "search_query": "土豆烧排骨做法",
                    },
                    {
                        "name": "醋熘土豆丝",
                        "tag": "veg",
                        "style": "快炒",
                        "diff": 1,
                        "ingredients": "土豆2个、醋、盐、葱丝",
                        "steps": [
                            "土豆切丝泡水去淀粉",
                            "热锅爆香葱丝大火翻炒土豆丝",
                            "加醋盐调味出锅",
                        ],
                        "search_query": "醋熘土豆丝",
                    },
                ],
                "soup": {
                    "name": "豆腐菌菇汤",
                    "tag": "soup",
                    "style": "汤",
                    "diff": 1,
                    "ingredients": "嫩豆腐1块、香菇3朵、金针菇50g、盐、葱花",
                    "steps": ["水烧开下香菇金针菇煮5分钟", "下豆腐煮开加盐葱花即可"],
                    "search_query": "豆腐菌菇汤",
                },
            },
        },
        {
            "day": "周四",
            "lunch": {
                "dishes": [
                    {
                        "name": "芹菜炒肉丝",
                        "tag": "meat",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "猪里脊150g、芹菜300g、胡萝卜半根、葱姜蒜、生抽盐",
                        "steps": [
                            "肉丝腌制芹菜胡萝卜切丝",
                            "爆香葱姜蒜滑炒肉丝",
                            "下芹菜胡萝卜翻炒调味",
                        ],
                        "search_query": "芹菜炒肉丝",
                    },
                    {
                        "name": "葱烧豆腐",
                        "tag": "veg",
                        "style": "葱烧",
                        "diff": 2,
                        "ingredients": "老豆腐1块、大葱1根、生抽老抽盐",
                        "steps": [
                            "豆腐切块煎至两面金黄",
                            "下葱段爆香",
                            "加生抽老抽加水焖5分钟收汁",
                        ],
                        "search_query": "葱烧豆腐做法",
                    },
                ],
                "optional": {
                    "name": "凉拌秋葵",
                    "tag": "opt",
                    "style": "凉拌",
                    "diff": 1,
                    "ingredients": "秋葵200g、蒜末、生抽、醋、香油",
                    "steps": ["秋葵焯水切段", "加蒜末生抽醋香油拌匀"],
                    "search_query": "凉拌秋葵",
                },
            },
            "dinner": {
                "dishes": [
                    {
                        "name": "肥牛炒洋葱",
                        "tag": "meat",
                        "style": "葱烧",
                        "diff": 2,
                        "ingredients": "肥牛片300g、洋葱1个、生抽老抽料酒",
                        "steps": ["洋葱切丝备用", "热锅下洋葱炒软", "下肥牛片大火翻炒加调料调味"],
                        "search_query": "肥牛炒洋葱做法",
                    },
                    {
                        "name": "蒜蓉西兰花",
                        "tag": "veg",
                        "style": "快炒",
                        "diff": 1,
                        "ingredients": "西兰花300g、蒜末、盐",
                        "steps": ["西兰花焯水备用", "蒜末爆香下西兰花翻炒调味"],
                        "search_query": "蒜蓉西兰花",
                    },
                ],
                "soup": {
                    "name": "冬瓜虾汤",
                    "tag": "soup",
                    "style": "汤",
                    "diff": 1,
                    "ingredients": "冬瓜300g、虾100g、姜片、盐、葱花",
                    "steps": ["冬瓜切块加水煮开", "下虾和姜片煮熟", "加盐葱花调味"],
                    "search_query": "冬瓜虾汤",
                },
            },
        },
        {
            "day": "周五",
            "lunch": {
                "dishes": [
                    {
                        "name": "莴笋炒肉片",
                        "tag": "meat",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "猪里脊150g、莴笋1根、胡萝卜半根、葱姜蒜",
                        "steps": [
                            "肉片腌制莴笋胡萝卜切片",
                            "爆香葱姜蒜滑炒肉片",
                            "下莴笋胡萝卜翻炒调味",
                        ],
                        "search_query": "莴笋炒肉片",
                    },
                    {
                        "name": "青椒土豆丝",
                        "tag": "veg",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "土豆2个、青椒2个、葱姜、盐、醋",
                        "steps": [
                            "土豆青椒切丝土豆丝泡水",
                            "爆香葱姜下土豆丝翻炒",
                            "下青椒翻炒加盐醋调味",
                        ],
                        "search_query": "青椒土豆丝",
                    },
                ],
                "optional": {
                    "name": "苹果拌黄瓜",
                    "tag": "opt",
                    "style": "凉拌",
                    "diff": 1,
                    "ingredients": "黄瓜1根、苹果半个、盐、糖、醋",
                    "steps": ["黄瓜苹果切片", "加盐糖醋拌匀即可"],
                    "search_query": "苹果拌黄瓜",
                },
            },
            "dinner": {
                "dishes": [
                    {
                        "name": "葱爆羊肉",
                        "tag": "meat",
                        "style": "葱爆",
                        "diff": 2,
                        "ingredients": "羊肉片300g、大葱2根、生抽料酒淀粉",
                        "steps": [
                            "羊肉片腌制10分钟",
                            "大葱切段备用",
                            "大火爆香葱段下羊肉片翻炒调味",
                        ],
                        "search_query": "葱爆羊肉做法",
                    },
                    {
                        "name": "番茄炒鸡蛋",
                        "tag": "veg",
                        "style": "快炒",
                        "diff": 1,
                        "ingredients": "番茄2个、鸡蛋3个、葱、盐、糖",
                        "steps": ["鸡蛋炒散盛出", "番茄炒软下鸡蛋翻炒调味"],
                        "search_query": "番茄炒鸡蛋",
                    },
                ],
                "soup": {
                    "name": "山药排骨汤",
                    "tag": "soup",
                    "style": "汤",
                    "diff": 2,
                    "ingredients": "排骨400g、山药200g、姜片、盐",
                    "steps": [
                        "排骨焯水",
                        "加水姜片大火煮开转小火炖40分钟",
                        "下山药再炖15分钟加盐调味",
                    ],
                    "search_query": "山药排骨汤",
                },
            },
        },
    ],
}


async def generate_week_menu(
    week_start: str,
    system_text: str | None = None,
    prev_dishes: list[str] | None = None,
) -> dict:
    if os.getenv("USE_MOCK_MENU") == "1":
        import copy

        logger.info("USE_MOCK_MENU=1: returning fixture (no API call)")
        mock = copy.deepcopy(_MOCK_MENU)
        mock["week_start"] = week_start
        return mock

    if system_text is None:
        system_text = SYSTEM_PROMPT.read_text(encoding="utf-8")

    user_content = f"请生成从 {week_start} 开始那一周（周一至周五）的菜单。"
    if prev_dishes:
        names = "、".join(prev_dishes)
        user_content += (
            f"\n\n上周菜品列表如下。本周允许最多重复2道菜，" f"其余菜名请确保与上周不同：{names}"
        )

    messages: list[dict] = [{"role": "user", "content": user_content}]

    for attempt in range(3):
        raw_text, stop_reason = await llm.chat(system_text, messages, max_tokens=8192)

        if stop_reason == "max_tokens":
            logger.error("Attempt %d: response truncated (max_tokens).", attempt + 1)
            continue

        raw_text = raw_text.strip()
        if not raw_text:
            logger.error("Attempt %d: empty response.", attempt + 1)
            continue

        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        try:
            menu = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.error(
                "Attempt %d JSON parse error: %s\nRaw text (first 500 chars): %.500s",
                attempt + 1,
                e,
                raw_text,
            )
            continue

        menu = fix_menu(menu)
        errors = validate_menu(menu)
        if not errors:
            return menu

        logger.warning("Attempt %d validation errors after fix: %s", attempt + 1, errors)
        error_summary = "；".join(errors)
        messages = messages + [
            {"role": "assistant", "content": raw_text},
            {
                "role": "user",
                "content": f"菜单有以下问题，请重新生成整份菜单（仍返回纯JSON）：{error_summary}",
            },
        ]

    raise RuntimeError("Menu generation failed after 3 attempts")


def fix_menu(menu: dict) -> dict:
    """Deterministically fix simple numeric violations without a retry."""
    hard_dishes = []
    for day in menu.get("days", []):
        for meal_type in ["lunch", "dinner"]:
            meal = day.get(meal_type, {})
            all_dishes = (
                meal.get("dishes", [])
                + ([meal["optional"]] if meal.get("optional") else [])
                + ([meal["soup"]] if meal.get("soup") else [])
            )
            for dish in all_dishes:
                if dish.get("diff") == 3:
                    hard_dishes.append(dish)

    # downgrade excess hard dishes to diff=2
    for dish in hard_dishes[2:]:
        dish["diff"] = 2
        logger.info("Auto-fixed: downgraded '%s' from ⭐⭐⭐ to ⭐⭐", dish.get("name"))

    return menu


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
