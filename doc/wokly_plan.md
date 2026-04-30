# Wokly — Execution Plan

> AI-powered weekly Chinese family menu generator for a nanny-operated household.
> Shandong + Northeast Chinese cuisine, mobile-first, Claude-generated menus every Friday.

---

## Project Overview

| Item               | Detail                  |
| ------------------ | ----------------------- |
| Project name       | Wokly                   |
| Total phases       | 4                       |
| Estimated timeline | 3–4 weeks               |
| Core tasks         | 14                      |
| Phase 4 extension  | Online grocery shopping |

## Tech Stack

| Layer     | Technology          | Rationale                                                 |
| --------- | ------------------- | --------------------------------------------------------- |
| Frontend  | React SPA           | Mobile-first, component model fits meal cards             |
| Backend   | FastAPI (Python)    | Lightweight, async, easy Claude API integration           |
| Database  | Neon PostgreSQL     | Serverless Postgres, free tier, scales for Phase 4        |
| Hosting   | GCP Cloud Run       | Containerized, scales to zero, fits existing GCP workflow |
| Cron      | GCP Cloud Scheduler | Native GCP, triggers generation every Friday 11am PST     |
| AI        | Claude Sonnet API   | Menu generation + ingredient store classification         |
| Container | Docker              | Multi-stage build, single container deployment            |

---

## Menu Rules (System Prompt Source of Truth)

### Cuisine Style

- Shandong (鲁菜) + Northeast Chinese (东北家常) — savory, soy-forward, heavy on scallion/ginger/garlic
- Emphasis on braised dishes, soy-glazed, scallion-roasted, scallion-seared
- Sichuan peppercorn (花椒) allowed for aroma — not classified as spicy
- Prohibited: chili peppers, chili sauce, numbing-spicy (mala) seasoning

### Protein Pool

| Protein                  | Lunch          | Dinner         |
| ------------------------ | -------------- | -------------- |
| Pork (loin / belly)      | ✅             | ✅             |
| Ground pork              | ✅             | ✅             |
| Pork ribs                | ✅             | ✅             |
| Chicken                  | ✅             | ✅             |
| Shrimp                   | ✅             | ✅             |
| Salmon                   | ✅ max 1×/week | ✅ max 1×/week |
| Beef brisket (牛腩)      | ❌             | ✅             |
| Fatty beef slices (肥牛) | ❌             | ✅             |
| Fatty lamb slices (肥羊) | ❌             | ✅             |

- Same dish name must not appear more than 2× in a week
- Salmon appears at most 1× total per week (lunch + dinner combined)

### Meal Structure & Difficulty

```
Lunch:
  dish_1:    ⭐⭐  meat dish   (multi-ingredient stir-fry / scallion-sear)
  dish_2:    ⭐⭐  veg dish    (Lotus Pond Stir-fry / Di San Xian / Braised Tofu / Mixed Stir-fry)
  optional:  ⭐   simple dish (cold salad / tomato egg — shown when wife WFH toggle is ON)

Dinner:
  dish_1:    ⭐⭐ or ⭐⭐⭐  meat dish  (braise / scallion-roast)
  dish_2:    ⭐             veg dish   (quick stir-fry / cold salad)
  soup:      ⭐ or ⭐⭐     (from approved soup list)

Max ⭐⭐⭐ dishes per week: 2
```

### Difficulty Levels

**⭐ Easy (under 10 min)**

- Quick stir-fry: Garlic broccoli, Stir-fried zucchini, Garlic spinach, Stir-fried cabbage, Tomato egg, Vinegar potato shreds
- Cold salads: Smashed cucumber, Cold eggplant, Century egg tofu, Cold okra, Apple cucumber salad
- Soups: Seaweed egg drop soup, Tomato egg drop soup, Tofu mushroom soup, Winter melon shrimp soup

**⭐⭐ Medium (20–30 min)**

- Multi-ingredient stir-fry: Moo shu pork, Fish-fragrant pork shreds, Lotus Pond Stir-fry, Celery pork shreds, Green pepper potato shreds, Spicy pepper dry tofu, Lettuce pork slices, Mixed stir-fry (炒合菜)
- Scallion dishes: Scallion-seared lamb, Scallion-seared pork, Scallion-braised tofu, Fatty beef with onion
- Braise: Cola chicken wings, Di San Xian (地三鲜)
- Soups: Winter melon rib soup, Tomato meatball soup, Mushroom chicken soup, Yam rib soup

**⭐⭐⭐ Advanced (40+ min, max 2× per week)**

- Braise/stew: Red-braised chicken, Potato braised ribs, Pork with vermicelli, Pork with green beans, Soy-braised eggplant, Scallion-roasted ribs, Tomato beef brisket, Sweet and sour pork loin

**❌ Prohibited (too difficult or disliked)**

- Crispy pork (锅包肉), Northeast stew (东北乱炖), Red-braised pork belly
- Steamed fish, Steam-powder pork
- Garlic stir-fried shrimp, Plain stir-fried broccoli, Salmon with tofu, Corn chicken soup
- Any dish using 空心菜 (water spinach) — not available locally

### Approved Soup List

Winter melon rib soup, Seaweed egg drop soup, Tomato egg drop soup, Tofu mushroom soup, White radish beef brisket soup, Winter melon shrimp soup, Tomato meatball soup, Mushroom soup, Mushroom chicken soup, Yam rib soup

### Vegetable Pool

| Category   | Vegetables                                                                                                       |
| ---------- | ---------------------------------------------------------------------------------------------------------------- |
| Leafy      | Cabbage, oil lettuce (油麦菜), spinach                                                                           |
| Gourd      | Winter melon, zucchini, cucumber                                                                                 |
| Root/stem  | White radish, carrot, potato, romaine lettuce stem (莴笋), lotus root, celery, yam                               |
| Bean/fungi | Green beans, bean sprouts, shiitake, king oyster mushroom, button mushroom, wood ear, tofu (soft/firm), dry tofu |
| Other      | Tomato, broccoli, green pepper, onion, eggplant, okra, corn, snow peas, apple (used in salads)                   |

### Pre-generation Validation Checklist

1. No dish name appears more than 2× in the week
2. Lunch contains no beef brisket, fatty beef, or fatty lamb
3. Salmon appears at most 1× total
4. No more than 2 dishes rated ⭐⭐⭐ per week
5. Lunch: ⭐⭐ meat + ⭐⭐ veg + ⭐ optional
6. Dinner: ⭐⭐/⭐⭐⭐ meat + ⭐ veg + ⭐/⭐⭐ soup
7. No prohibited dishes used
8. Every meal has at least 1 meat dish and 1 vegetable dish

---

## Claude System Prompt (menu_system.txt)

> Note: All rule content is in Chinese — Claude generates Chinese dish names, steps, and ingredients.
> JSON field names (keys) stay in English for reliable parsing.

```
你是一位专做山东鲁菜和东北家常菜的家庭厨师助手。
每周五为一个有保姆的家庭生成周一至周五的午餐和晚餐菜单。

只返回合法的JSON，不要加任何解释或markdown代码块。

=== 口味风格 ===
- 山东鲁菜 + 东北家常：咸鲜酱香，葱姜蒜重口
- 多炖菜、酱焖、葱烧、葱爆
- 花椒可以使用（增香，不算辣）
- 禁止：辣椒、辣酱、麻辣（花椒除外）

=== 蛋白质规则 ===
可用食材：猪肉（里脊/五花）、碎猪肉、猪排骨、鸡肉、虾、
          牛腩、肥牛、肥羊、三文鱼（全周最多出现1次）
午餐禁止：牛腩、肥牛、肥羊
同一道菜整周不超过2次

=== 每餐结构 ===
午餐：
  dish_1：⭐⭐ 荤菜（多料炒 / 葱爆）
  dish_2：⭐⭐ 素菜（荷塘月色 / 地三鲜 / 葱烧豆腐 / 炒合菜等）
  optional：⭐ 简单菜（凉拌 / 番茄炒鸡蛋，太太在家时显示）

晚餐：
  dish_1：⭐⭐ 或 ⭐⭐⭐ 荤菜（炖烧 / 葱烧）
  dish_2：⭐ 素菜（快炒 / 凉拌）
  soup：⭐ 或 ⭐⭐（只能从汤单中选择）

每周⭐⭐⭐菜最多出现2次

=== 难度分级 ===
⭐ 简单（10分钟内）
  快炒：蒜蓉西兰花、清炒丝瓜、蒜蓉菠菜、清炒白菜、番茄炒鸡蛋、醋熘土豆丝
  凉拌：凉拌黄瓜、拌茄子、皮蛋豆腐、凉拌秋葵、苹果拌黄瓜
  汤：紫菜蛋花汤、番茄蛋花汤、豆腐菌菇汤、冬瓜虾汤

⭐⭐ 中等（20–30分钟）
  多料炒：木须肉、鱼香肉丝、荷塘月色、芹菜炒肉丝、青椒土豆丝、
          尖椒干豆腐、莴笋炒肉片、炒合菜
  葱烧/爆：葱爆羊肉、葱爆猪肉、葱烧豆腐、肥牛炒洋葱
  炖烧：可乐鸡翅、地三鲜
  汤：冬瓜排骨汤、番茄丸子汤、蘑菇鸡汤、山药排骨汤

⭐⭐⭐ 稍难（40分钟以上，每周最多2次）
  炖烧：红烧鸡块、土豆烧排骨、猪肉炖粉条、猪肉炖豆角、
        酱焖茄子、葱烧排骨、番茄炖牛腩、糖醋里脊

=== 汤单（晚餐专用，只能从以下选择）===
冬瓜排骨汤、紫菜蛋花汤、番茄蛋花汤、豆腐菌菇汤、
白萝卜炖牛腩汤、冬瓜虾汤、番茄丸子汤、蘑菇汤、
蘑菇鸡汤、山药排骨汤

=== 禁止菜品 ===
锅包肉、东北乱炖、红烧猪肉、蒸鱼、粉蒸肉、蒜蓉炒虾、
清炒西兰花、三文鱼煎豆腐、玉米鸡肉汤、空心菜

=== 蔬菜池 ===
叶菜：白菜、油麦菜、菠菜
瓜类：冬瓜、丝瓜、黄瓜
根茎：白萝卜、胡萝卜、土豆、莴笋、荷藕、芹菜、山药
豆/菌：豆角、豆芽、金针菇、香菇、杏鲍菇、口蘑、木耳、豆腐（嫩/老）、干豆腐
其他：番茄、西兰花、青椒、洋葱、茄子、秋葵、玉米、荷兰豆、苹果（入菜）

=== 输出格式（严格JSON，字段名保持英文）===
{
  "week_start": "YYYY-MM-DD",
  "days": [
    {
      "day": "周一",
      "lunch": {
        "dishes": [
          {
            "name": "菜名",
            "tag": "meat",
            "style": "多料炒",
            "diff": 2,
            "ingredients": "食材列表",
            "steps": ["步骤1（不超过30字）", "步骤2", "步骤3"],
            "search_query": "小红书搜索关键词"
          },
          {
            "name": "菜名",
            "tag": "veg",
            "style": "多料炒",
            "diff": 2,
            "ingredients": "食材列表",
            "steps": ["步骤1", "步骤2", "步骤3"],
            "search_query": "搜索关键词"
          }
        ],
        "optional": {
          "name": "菜名",
          "tag": "opt",
          "style": "凉拌",
          "diff": 1,
          "ingredients": "食材列表",
          "steps": ["步骤1", "步骤2"],
          "search_query": "搜索关键词"
        }
      },
      "dinner": {
        "dishes": [
          {
            "name": "菜名",
            "tag": "meat",
            "style": "炖烧",
            "diff": 3,
            "ingredients": "食材列表",
            "steps": ["步骤1", "步骤2", "步骤3", "步骤4", "步骤5"],
            "search_query": "搜索关键词"
          },
          {
            "name": "菜名",
            "tag": "veg",
            "style": "快炒",
            "diff": 1,
            "ingredients": "食材列表",
            "steps": ["步骤1", "步骤2", "步骤3"],
            "search_query": "搜索关键词"
          }
        ],
        "soup": {
          "name": "汤名",
          "tag": "soup",
          "style": "汤",
          "diff": 1,
          "ingredients": "食材列表",
          "steps": ["步骤1", "步骤2", "步骤3"],
          "search_query": "搜索关键词"
        }
      }
    }
  ]
}

=== 返回前自检（必须验证以下所有项）===
1. 同一菜名整周不超过2次
2. 午餐无牛腩、无肥牛、无肥羊
3. 三文鱼全周仅出现1次
4. 每周⭐⭐⭐菜不超过2次
5. 午餐：⭐⭐荤 + ⭐⭐素 + ⭐选填
6. 晚餐：⭐⭐或⭐⭐⭐荤 + ⭐素 + ⭐或⭐⭐汤
7. 无禁止菜品
8. 所有汤来自汤单
9. 每餐至少1荤1素
```

---

## Phase 1 — Database + Backend API (Days 1–2)

### Task 1: Neon DB Schema

```sql
-- migrations/001_init.sql

CREATE TABLE weeks (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start    DATE NOT NULL UNIQUE,
  generated_at  TIMESTAMP,
  status        TEXT DEFAULT 'pending'  -- pending | ready | failed
);

CREATE TABLE meals (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_id       UUID REFERENCES weeks(id) ON DELETE CASCADE,
  day           TEXT NOT NULL,          -- 周一 | 周二 | 周三 | 周四 | 周五
  meal_type     TEXT NOT NULL,          -- lunch | dinner
  dish1         JSONB,                  -- {name, tag, style, diff, ingredients, steps, search_query}
  dish2         JSONB,
  optional_dish JSONB,                  -- lunch only (wife WFH)
  soup          JSONB,                  -- dinner only
  UNIQUE (week_id, day, meal_type)
);

CREATE TABLE ingredients (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_id     UUID REFERENCES weeks(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  quantity    TEXT,
  store       TEXT DEFAULT 'tnt',       -- costco | tnt | either
  category    TEXT,                     -- protein | veggie | pantry
  checked     BOOLEAN DEFAULT false,
  overridden  BOOLEAN DEFAULT false     -- user manually changed store
);

CREATE INDEX idx_meals_week_id ON meals(week_id);
CREATE INDEX idx_ingredients_week_id ON ingredients(week_id);
```

**Output files:** `schema.sql`, `migrations/001_init.sql`

---

### Task 2: FastAPI Routes

```python
# routes/menu.py

GET    /api/week/current        # fetch current week menu
POST   /api/generate            # trigger full week generation (called by Cloud Scheduler)
PUT    /api/meal/{id}           # manually edit a single dish name
POST   /api/meal/{id}/regen     # AI regenerate a single dish
GET    /api/history             # list all past weeks
GET    /api/week/{id}           # get a specific past week (read-only)
GET    /api/ingredients/current # get current week shopping list
PUT    /api/ingredients/{id}    # toggle checked / override store
```

**Output files:** `main.py`, `routes/menu.py`, `models.py`

---

### Task 3: Claude Menu Generator

```python
# services/generator.py

import anthropic
import json
from pathlib import Path

client = anthropic.AsyncAnthropic()
SYSTEM_PROMPT = Path("prompts/menu_system.txt").read_text()

async def generate_week_menu(week_start: str) -> dict:
    """Generate a full week menu. Retries up to 3 times on validation failure."""
    for attempt in range(3):
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Generate the menu for the week starting {week_start}."
            }]
        )
        try:
            menu = json.loads(response.content[0].text)
            errors = validate_menu(menu)
            if not errors:
                return menu
            print(f"Attempt {attempt+1} failed validation: {errors}")
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt+1} JSON parse error: {e}")

    raise RuntimeError("Menu generation failed after 3 attempts")


def validate_menu(menu: dict) -> list[str]:
    """Returns list of validation errors. Empty list = valid."""
    errors = []
    dish_counts = {}
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

                # Count dish name occurrences
                dish_counts[name] = dish_counts.get(name, 0) + 1
                if dish_counts[name] > 2:
                    errors.append(f"Dish '{name}' appears more than 2× in the week")

                # Count salmon
                if "三文鱼" in name or "salmon" in name.lower():
                    salmon_count += 1

                # Count hard dishes
                if diff == 3:
                    hard_dish_count += 1

                # Check lunch protein restriction
                if meal_type == "lunch" and tag == "meat":
                    forbidden = ["牛腩", "肥牛", "肥羊"]
                    if any(f in name for f in forbidden):
                        errors.append(f"Lunch dish '{name}' uses forbidden protein")

    if salmon_count > 1:
        errors.append(f"Salmon appears {salmon_count}× (max 1)")
    if hard_dish_count > 2:
        errors.append(f"{hard_dish_count} ⭐⭐⭐ dishes (max 2)")

    return errors
```

**Output files:** `services/generator.py`, `prompts/menu_system.txt`

---

### Task 4: Single Dish Regeneration

```python
# services/regen.py

REGEN_PROMPT = """
你是一位专做山东鲁菜和东北家常菜的家庭厨师助手。
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
}
"""

async def regen_single_dish(
    meal_type: str,       # "lunch" | "dinner"
    dish_slot: str,       # "dish1" | "dish2" | "optional" | "soup"
    diff_level: int,      # 1 | 2 | 3
    existing_dishes: list[str]
) -> dict:
    context = (
        f"Meal: {meal_type}, Slot: {dish_slot}, Difficulty: {diff_level} stars\n"
        f"Existing dishes this week (do not repeat): {', '.join(existing_dishes)}"
    )
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=REGEN_PROMPT,
        messages=[{"role": "user", "content": context}]
    )
    return json.loads(response.content[0].text)
```

**Output files:** `services/regen.py`

---

## Phase 2 — React Frontend (Days 3–7)

### Task 5: Menu Tab

**Component tree:**

```
App
└── MenuTab
    ├── DayNav          (Mon–Fri horizontal scroll pills)
    ├── LunchCard
    │   ├── DishCard    dish_1  ⭐⭐ meat
    │   ├── DishCard    dish_2  ⭐⭐ veg
    │   ├── WfhToggle   (per-day toggle, label: 太太在家)
    │   └── DishCard    optional ⭐  (shown when toggle ON)
    └── DinnerCard
        ├── DishCard    dish_1  ⭐⭐/⭐⭐⭐ meat
        ├── DishCard    dish_2  ⭐ veg
        └── DishCard    soup    ⭐/⭐⭐
```

Each `DishCard` shows:

- Difficulty stars + meat/veg/soup/opt badge + cooking style pill
- Tap → `RecipeDrawer` (ingredients + 3–5 steps + 小红书 / YouTube search links)
- ↺ button → calls `POST /api/meal/{id}/regen`

**Output files:** `components/MenuTab.jsx`, `components/DishCard.jsx`, `components/RecipeDrawer.jsx`

---

### Task 6: Shopping Tab

- Two columns: **Costco** (bulk proteins) and **T&T** (fresh veg + specialty)
- Heuristic classification:
  - Costco: pork, ribs, chicken, beef brisket, fatty beef, fatty lamb, frozen shrimp, eggs
  - T&T: all vegetables, tofu, mushrooms, pantry staples
- Manual drag-to-swap between columns
- Checkbox per item, strikethrough when checked

**Output files:** `components/ShopTab.jsx`, `components/ShopItem.jsx`

---

### Task 7: History Tab

- Card list of past weeks (week of MM/DD, dish count, generated date)
- Tap → read-only view of that week's full menu
- Data from `GET /api/history` + `GET /api/week/{id}`

**Output files:** `components/HistoryTab.jsx`, `components/WeekCard.jsx`

---

### Task 8: Settings Page

- API Key is stored in GCP Secret Manager — never exposed to frontend
- Settings page shows connection status (backend health check endpoint)
- Language toggle: Chinese UI (default for nanny) / English UI (for you)

**Output files:** `components/Settings.jsx`

---

## Phase 3 — Deployment + Cron (Days 8–10)

### Task 9: Dockerfile

```dockerfile
# Multi-stage build: React → Python slim

# Stage 1: Build React frontend
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python backend + static files
FROM python:3.12-slim AS backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=frontend /app/dist ./static

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Output files:** `Dockerfile`, `.dockerignore`, `docker-compose.yml`

---

### Task 10: GCP Cloud Run Deployment

```bash
#!/bin/bash
# deploy.sh

PROJECT_ID="your-gcp-project-id"
REGION="us-west1"
SERVICE="wokly"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE"

# Build and push
docker build -t $IMAGE .
docker push $IMAGE

# Deploy
gcloud run deploy $SERVICE \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --min-instances 0 \
  --max-instances 2 \
  --memory 512Mi \
  --set-secrets ANTHROPIC_API_KEY=wokly-anthropic-key:latest \
  --set-secrets NEON_DATABASE_URL=wokly-neon-url:latest \
  --allow-unauthenticated
```

**Output files:** `cloudbuild.yaml`, `deploy.sh`

---

### Task 11: Cloud Scheduler Cron Job

```bash
# Trigger menu generation every Friday at 11:00 AM PST (= 19:00 UTC)
gcloud scheduler jobs create http wokly-weekly-gen \
  --schedule="0 19 * * 5" \
  --uri="https://your-wokly-url/api/generate" \
  --http-method=POST \
  --time-zone="America/Los_Angeles" \
  --attempt-deadline=300s \
  --max-retry-attempts=3 \
  --message-body='{"source": "scheduler"}'
```

**Output files:** `scheduler.tf`, `README.md`

---

## Phase 4 — Online Grocery Shopping (Next Phase, TBD)

### Task 12: T&T Online Cart Integration

- Research T&T online store API availability
- Fallback: Playwright browser automation
- Extend DB with `orders` table:

```sql
-- migrations/002_orders.sql
CREATE TABLE orders (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_id     UUID REFERENCES weeks(id),
  store       TEXT NOT NULL,           -- costco | tnt
  items       JSONB,                   -- [{name, qty, sku, price}]
  status      TEXT DEFAULT 'draft',    -- draft | submitted | delivered
  created_at  TIMESTAMP DEFAULT now()
);
```

**Output files:** `services/tnt_cart.py`, `migrations/002_orders.sql`

---

### Task 13: Costco.ca Integration

- Research Costco.ca cart API or automation approach
- Auto-match bulk protein SKUs from ingredient names

**Output files:** `services/costco_cart.py`

---

### Task 14: Smart Ingredient Matching

- Claude maps recipe ingredients → purchase quantities
  - e.g. `pork loin 150g × 5 meals` → `pork loin 1kg × 1 pack`
- Cross-week quantity optimization (buy once, use over 2 weeks)

---

## Project Structure

```
wokly/
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── models.py                 # Pydantic models + DB schemas
│   ├── routes/
│   │   └── menu.py               # All API routes
│   ├── services/
│   │   ├── generator.py          # Full week menu generation
│   │   └── regen.py              # Single dish regeneration
│   ├── prompts/
│   │   └── menu_system.txt       # Claude system prompt (Chinese content)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── MenuTab.jsx
│   │   │   ├── DishCard.jsx
│   │   │   ├── RecipeDrawer.jsx
│   │   │   ├── ShopTab.jsx
│   │   │   ├── ShopItem.jsx
│   │   │   ├── HistoryTab.jsx
│   │   │   ├── WeekCard.jsx
│   │   │   └── Settings.jsx
│   │   └── hooks/
│   │       └── useMenu.js
│   └── package.json
├── migrations/
│   ├── 001_init.sql
│   └── 002_orders.sql            # Phase 4
├── Dockerfile
├── .dockerignore
├── docker-compose.yml            # local dev
├── cloudbuild.yaml
├── deploy.sh
├── scheduler.tf
└── README.md
```

---

## Execution Order

```
Day 1    schema.sql → create Neon DB tables
Day 2    FastAPI skeleton + routes + Claude generator service
Day 3    React MenuTab + DishCard + RecipeDrawer components
Day 4    ShopTab + HistoryTab components
Day 5    Frontend ↔ Backend integration + WFH toggle logic
Day 6    Full local test with Docker Compose
Day 7    Buffer / bug fixes
Day 8    GCP Artifact Registry + Cloud Run deployment
Day 9    GCP Secret Manager + environment variables
Day 10   Cloud Scheduler setup + end-to-end validation
```

---

## Key Risks & Mitigations

| Risk                                         | Mitigation                                                              |
| -------------------------------------------- | ----------------------------------------------------------------------- |
| Claude returns malformed JSON                | Client-side validation + retry up to 3× with same prompt                |
| Single dish regen duplicates existing dishes | Pass full existing dish name list as context to Claude                  |
| Cloud Run cold start latency                 | Set `min-instances=1` if latency is unacceptable (adds ~$5/month)       |
| Neon DB connection pool exhaustion           | Use `asyncpg` with connection pooling, max 10 connections               |
| Cloud Scheduler fires during outage          | Retry 3× with 5min backoff, email alert on final failure                |
| Menu constraint violations slip through      | Validate on both backend (before DB write) and frontend (before render) |

---

## Prerequisites (Before Starting)

- [ ] Neon account created → copy `DATABASE_URL`
- [ ] GCP project created → enable Cloud Run, Artifact Registry, Cloud Scheduler, Secret Manager APIs
- [ ] Anthropic API key ready
- [ ] Domain name for Wokly (optional — Cloud Run provides a default URL)
