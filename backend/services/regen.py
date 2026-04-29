import json
import os

import anthropic

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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
    context = (
        f"餐次：{meal_type}，位置：{dish_slot}，难度：{diff_level} 星\n"
        f"本周已有菜品（不得重复）：{', '.join(existing_dishes)}"
    )
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": REGEN_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": context}],
    )
    return json.loads(response.content[0].text)
