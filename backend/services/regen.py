import json
import logging
import os

from services import llm

logger = logging.getLogger(__name__)

_MOCK_DISHES = {
    "meat": {
        "name": "可乐鸡翅（替换）",
        "tag": "meat",
        "style": "炖烧",
        "diff": 2,
        "ingredients": "鸡翅500g、可乐1罐、生抽老抽、姜片",
        "steps": ["鸡翅焯水", "煎至两面金黄", "倒可乐生抽老抽焖20分钟收汁"],
        "search_query": "可乐鸡翅做法",
    },
    "veg": {
        "name": "蒜蓉菠菜（替换）",
        "tag": "veg",
        "style": "快炒",
        "diff": 1,
        "ingredients": "菠菜300g、蒜末、盐、香油",
        "steps": ["菠菜焯水过凉", "蒜末爆香下菠菜翻炒调味"],
        "search_query": "蒜蓉菠菜",
    },
    "soup": {
        "name": "紫菜蛋花汤（替换）",
        "tag": "soup",
        "style": "汤",
        "diff": 1,
        "ingredients": "紫菜10g、鸡蛋1个、葱花、盐",
        "steps": ["水烧开下紫菜", "蛋液冲入加盐葱花"],
        "search_query": "紫菜蛋花汤",
    },
    "opt": {
        "name": "凉拌黄瓜（替换）",
        "tag": "opt",
        "style": "凉拌",
        "diff": 1,
        "ingredients": "黄瓜1根、蒜末、醋、盐、香油",
        "steps": ["黄瓜拍碎切段", "加蒜末醋盐香油拌匀"],
        "search_query": "凉拌黄瓜",
    },
}


REGEN_SYSTEM = """你是一位专做山东鲁菜和东北家常菜的家庭厨师助手。
请重新生成一道菜来替换现有的菜品。

规则：
- 难度必须与指定难度等级匹配
- 不能使用 existing_dishes 列表中的任何菜名
- 遵守所有烹饪规则（无辣椒、花椒可用、无禁止菜品）
- 口味风格：山东鲁菜 + 东北家常，咸鲜酱香
- 只返回单个菜品的JSON对象（不要数组，不要整周结构）

{
  "name": "菜名",
  "tag": "meat|veg|soup|opt",
  "style": "多料炒|快炒|葱爆|葱烧|凉拌|炖烧|汤",
  "diff": 1,
  "ingredients": "食材列表",
  "steps": ["步骤1", "步骤2", "步骤3"],
  "search_query": "小红书搜索关键词"
}"""


async def regen_single_dish(
    meal_type: str,
    dish_slot: str,
    diff_level: int,
    existing_dishes: list[str],
) -> dict:
    if os.getenv("USE_MOCK_MENU") == "1":
        import copy

        tag = (
            "soup"
            if dish_slot == "soup"
            else (
                "opt" if dish_slot == "optional" else ("meat" if dish_slot == "dish_1" else "veg")
            )
        )
        logger.info("USE_MOCK_MENU=1: returning mock regen dish (no API call)")
        return copy.deepcopy(_MOCK_DISHES.get(tag, _MOCK_DISHES["veg"]))

    context = (
        f"餐次：{meal_type}，位置：{dish_slot}，难度：{diff_level} 星\n"
        f"本周已有菜品（不得重复）：{', '.join(existing_dishes)}"
    )
    raw_text, _ = await llm.chat(
        REGEN_SYSTEM, [{"role": "user", "content": context}], max_tokens=512
    )

    raw_text = raw_text.strip()
    if not raw_text:
        raise RuntimeError("Empty regen response from AI provider")
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    return json.loads(raw_text)
