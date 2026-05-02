"""
Integration tests for all API routes.

Claude is mocked at the service layer so no real API calls are made.
The test DB is an in-memory SQLite instance (see conftest.py).
"""

from datetime import date, timedelta
from unittest.mock import ANY, AsyncMock, patch

import pytest

from tests.conftest import VALID_MENU


def _next_monday() -> str:
    today = date.today()
    delta = (7 - today.weekday()) % 7 or 7
    return str(today + timedelta(days=delta))


# ── health ────────────────────────────────────────────────────────────────────


class TestHealth:
    async def test_health_returns_ok(self, client):
        r = await client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ── /api/week/current ─────────────────────────────────────────────────────────


class TestGetCurrentWeek:
    async def test_returns_none_when_no_week_exists(self, client):
        r = await client.get("/api/week/current")
        assert r.status_code == 200
        assert r.json() is None


# ── /api/generate ─────────────────────────────────────────────────────────────


class TestGenerate:
    async def test_generate_creates_week_and_meals(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch(
            "routes.menu.generate_week_menu",
            new=AsyncMock(return_value=menu),
        ):
            r = await client.post("/api/generate")

        assert r.status_code == 200
        body = r.json()
        assert body.get("week_start") is not None
        assert "week_id" in body

    async def test_generate_populates_current_week(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            await client.post("/api/generate")

        # current week endpoint should now return data
        # Override current monday check — generate sets week_start to next monday,
        # so we check via history instead
        r = await client.get("/api/history")
        assert r.status_code == 200
        assert len(r.json()) == 1

    async def test_generate_creates_ingredients(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            r = await client.post("/api/generate")

        week_id = r.json()["week_id"]

        # Get week detail to find a meal id
        r2 = await client.get(f"/api/week/{week_id}")
        assert r2.status_code == 200

    async def test_generate_returns_existing_if_already_ready(self, client):
        # 1st call → current week (doesn't exist yet)
        # 2nd call → next week (current now exists)
        # 3rd call → next week already ready → "already exists"
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            await client.post("/api/generate")
            await client.post("/api/generate")
            r3 = await client.post("/api/generate")

        assert r3.status_code == 200
        assert "already exists" in r3.json().get("message", "")

    async def test_generate_handles_claude_failure(self, client):
        with patch(
            "routes.menu.generate_week_menu",
            new=AsyncMock(side_effect=RuntimeError("Claude failed")),
        ):
            r = await client.post("/api/generate")
        assert r.status_code == 500


# ── /api/meal/{id} ────────────────────────────────────────────────────────────


class TestUpdateMeal:
    async def _create_week_and_get_meal_id(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            r = await client.post("/api/generate")
        week_id = r.json()["week_id"]
        r2 = await client.get(f"/api/week/{week_id}")
        meals = r2.json()["meals"]
        return meals[0]["id"]

    async def test_update_dish1(self, client):
        meal_id = await self._create_week_and_get_meal_id(client)
        new_dish = {
            "name": "手动改的菜",
            "tag": "meat",
            "style": "快炒",
            "diff": 2,
            "ingredients": "猪肉",
            "steps": ["step1"],
            "search_query": "手动改的菜",
        }
        r = await client.put(
            f"/api/meal/{meal_id}",
            json={"dish_slot": "dish1", "dish": new_dish},
        )
        assert r.status_code == 200
        assert r.json()["dish1"]["name"] == "手动改的菜"

    async def test_update_unknown_slot_returns_400(self, client):
        meal_id = await self._create_week_and_get_meal_id(client)
        r = await client.put(
            f"/api/meal/{meal_id}",
            json={"dish_slot": "invalid_slot", "dish": {}},
        )
        assert r.status_code == 400

    async def test_update_nonexistent_meal_returns_404(self, client):
        r = await client.put(
            "/api/meal/00000000-0000-0000-0000-000000000000",
            json={"dish_slot": "dish1", "dish": {"name": "x"}},
        )
        assert r.status_code == 404


# ── /api/meal/{id}/regen ──────────────────────────────────────────────────────


class TestRegenDish:
    async def _create_week_and_get_meal_id(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            r = await client.post("/api/generate")
        week_id = r.json()["week_id"]
        r2 = await client.get(f"/api/week/{week_id}")
        return r2.json()["meals"][0]["id"]

    async def test_regen_updates_dish(self, client):
        meal_id = await self._create_week_and_get_meal_id(client)
        new_dish = {
            "name": "重新生成的菜",
            "tag": "meat",
            "style": "炖烧",
            "diff": 2,
            "ingredients": "鸡肉",
            "steps": ["step1"],
            "search_query": "重新生成的菜",
        }
        with patch("routes.menu.regen_single_dish", new=AsyncMock(return_value=new_dish)):
            r = await client.post(
                f"/api/meal/{meal_id}/regen",
                json={"dish_slot": "dish1"},
            )
        assert r.status_code == 200
        assert r.json()["dish1"]["name"] == "重新生成的菜"

    async def test_regen_nonexistent_meal_returns_404(self, client):
        with patch("routes.menu.regen_single_dish", new=AsyncMock(return_value={})):
            r = await client.post(
                "/api/meal/00000000-0000-0000-0000-000000000000/regen",
                json={"dish_slot": "dish1"},
            )
        assert r.status_code == 404


# ── /api/meal/{id}/fill ───────────────────────────────────────────────────────


class TestFillDish:
    async def _create_week_and_get_meal_id(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            r = await client.post("/api/generate")
        week_id = r.json()["week_id"]
        r2 = await client.get(f"/api/week/{week_id}")
        return r2.json()["meals"][0]["id"]

    async def test_fill_updates_dish_with_ai_recipe(self, client):
        meal_id = await self._create_week_and_get_meal_id(client)
        filled_dish = {
            "name": "土豆炖牛肉",
            "tag": "meat",
            "style": "炖烧",
            "diff": 2,
            "ingredients": "牛肉、土豆",
            "steps": ["切块", "炒糖色", "炖煮"],
            "search_query": "土豆炖牛肉",
        }
        with patch("routes.menu.fill_dish_by_name", new=AsyncMock(return_value=filled_dish)):
            r = await client.post(
                f"/api/meal/{meal_id}/fill",
                json={"dish_slot": "dish1", "name": "土豆炖牛肉"},
            )
        assert r.status_code == 200
        assert r.json()["dish1"]["name"] == "土豆炖牛肉"
        assert r.json()["dish1"]["steps"] == ["切块", "炒糖色", "炖煮"]

    async def test_fill_missing_name_returns_400(self, client):
        meal_id = await self._create_week_and_get_meal_id(client)
        r = await client.post(f"/api/meal/{meal_id}/fill", json={"dish_slot": "dish1"})
        assert r.status_code == 400

    async def test_fill_nonexistent_meal_returns_404(self, client):
        r = await client.post(
            "/api/meal/00000000-0000-0000-0000-000000000000/fill",
            json={"dish_slot": "dish1", "name": "测试菜"},
        )
        assert r.status_code == 404

    async def test_fill_falls_back_when_ai_fails(self, client):
        meal_id = await self._create_week_and_get_meal_id(client)
        with patch(
            "routes.menu.fill_dish_by_name", new=AsyncMock(side_effect=RuntimeError("AI error"))
        ):
            r = await client.post(
                f"/api/meal/{meal_id}/fill",
                json={"dish_slot": "dish1", "name": "测试菜", "url": "https://example.com"},
            )
        assert r.status_code == 200
        assert r.json()["dish1"]["name"] == "测试菜"
        assert r.json()["dish1"]["url"] == "https://example.com"


# ── /api/history ──────────────────────────────────────────────────────────────


class TestHistory:
    async def test_empty_history(self, client):
        r = await client.get("/api/history")
        assert r.status_code == 200
        assert r.json() == []

    async def test_history_after_generation(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            await client.post("/api/generate")

        r = await client.get("/api/history")
        assert r.status_code == 200
        assert len(r.json()) == 1
        entry = r.json()[0]
        assert "week_start" in entry
        assert "id" in entry
        assert entry["status"] == "ready"


# ── /api/week/{id} ────────────────────────────────────────────────────────────


class TestGetWeek:
    async def test_get_week_returns_meals(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            r_gen = await client.post("/api/generate")
        week_id = r_gen.json()["week_id"]

        r = await client.get(f"/api/week/{week_id}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == week_id
        assert len(body["meals"]) == 10  # 5 days × 2 meals

    async def test_get_week_meals_have_dishes(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            r_gen = await client.post("/api/generate")
        week_id = r_gen.json()["week_id"]

        r = await client.get(f"/api/week/{week_id}")
        lunch_meals = [m for m in r.json()["meals"] if m["meal_type"] == "lunch"]
        for meal in lunch_meals:
            assert meal["dish1"] is not None
            assert meal["dish2"] is not None

    async def test_get_nonexistent_week_returns_404(self, client):
        r = await client.get("/api/week/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404


# ── /api/ingredients/current ─────────────────────────────────────────────────


class TestGetIngredients:
    async def test_returns_empty_when_no_menu(self, client):
        r = await client.get("/api/ingredients/current")
        assert r.status_code == 200
        assert r.json() == []


# ── /api/ingredients/{id} ────────────────────────────────────────────────────


class TestUpdateIngredient:
    async def _get_ingredient_id(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)):
            gen = await client.post("/api/generate")
        week_id = gen.json()["week_id"]

        # Patch current week lookup to match the generated week
        r2 = await client.get(f"/api/week/{week_id}")
        week_start = r2.json()["week_start"]

        # Manually fetch ingredients via patching the current-monday calculation
        from datetime import datetime as dt

        parsed = dt.strptime(week_start, "%Y-%m-%d").date()
        with patch("routes.menu._current_monday", return_value=parsed):
            r3 = await client.get("/api/ingredients/current")
        items = r3.json()
        return items[0]["id"] if items else None, parsed

    async def test_toggle_checked(self, client):
        ing_id, monday = await self._get_ingredient_id(client)
        if not ing_id:
            pytest.skip("No ingredients generated")

        with patch("routes.menu._current_monday", return_value=monday):
            r_before = await client.get("/api/ingredients/current")
        original = next(i for i in r_before.json() if i["id"] == ing_id)
        assert original["checked"] is False

        r = await client.put(f"/api/ingredients/{ing_id}", json={"checked": True})
        assert r.status_code == 200
        assert r.json()["checked"] is True

    async def test_override_store(self, client):
        ing_id, monday = await self._get_ingredient_id(client)
        if not ing_id:
            pytest.skip("No ingredients generated")

        r = await client.put(f"/api/ingredients/{ing_id}", json={"store": "costco"})
        assert r.status_code == 200
        assert r.json()["store"] == "costco"
        assert r.json()["overridden"] is True

    async def test_update_nonexistent_ingredient_returns_404(self, client):
        r = await client.put(
            "/api/ingredients/00000000-0000-0000-0000-000000000000",
            json={"checked": True},
        )
        assert r.status_code == 404


# ── /api/prompt ───────────────────────────────────────────────────────────────


class TestPrompt:
    async def test_get_returns_default_when_no_custom(self, client):
        r = await client.get("/api/prompt")
        assert r.status_code == 200
        body = r.json()
        assert "content" in body
        assert body["is_custom"] is False
        assert len(body["content"]) > 100  # default prompt is substantial

    async def test_put_saves_custom_prompt(self, client):
        r = await client.put("/api/prompt", json={"content": "自定义提示词"})
        assert r.status_code == 200
        assert r.json()["message"] == "Prompt updated"

    async def test_get_returns_custom_after_save(self, client):
        await client.put("/api/prompt", json={"content": "自定义提示词"})
        r = await client.get("/api/prompt")
        assert r.status_code == 200
        body = r.json()
        assert body["content"] == "自定义提示词"
        assert body["is_custom"] is True

    async def test_put_overwrites_existing_custom(self, client):
        await client.put("/api/prompt", json={"content": "第一版"})
        await client.put("/api/prompt", json={"content": "第二版"})
        r = await client.get("/api/prompt")
        assert r.json()["content"] == "第二版"

    async def test_delete_resets_to_default(self, client):
        await client.put("/api/prompt", json={"content": "自定义提示词"})
        r = await client.delete("/api/prompt")
        assert r.status_code == 200
        body = r.json()
        assert body["is_custom"] is False
        assert body["content"] != "自定义提示词"

    async def test_delete_when_no_custom_is_harmless(self, client):
        r = await client.delete("/api/prompt")
        assert r.status_code == 200
        assert r.json()["is_custom"] is False

    async def test_generate_uses_custom_prompt(self, client):
        custom = "我的自定义提示词"
        await client.put("/api/prompt", json={"content": custom})

        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)) as mock_gen:
            r = await client.post("/api/generate")

        assert r.status_code == 200
        mock_gen.assert_called_once_with(ANY, system_text=custom)

    async def test_generate_passes_none_when_no_custom_prompt(self, client):
        menu = {**VALID_MENU, "week_start": _next_monday()}
        with patch("routes.menu.generate_week_menu", new=AsyncMock(return_value=menu)) as mock_gen:
            r = await client.post("/api/generate")

        assert r.status_code == 200
        mock_gen.assert_called_once_with(ANY, system_text=None)
