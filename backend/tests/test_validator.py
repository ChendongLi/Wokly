"""
Unit tests for validate_menu() and ingredient extraction helpers.
No DB or Claude calls needed.
"""

import pytest

from services.generator import classify_category, classify_store, extract_ingredients, validate_menu


def make_dish(name, tag="meat", diff=2, **kwargs):
    return {
        "name": name,
        "tag": tag,
        "style": "快炒",
        "diff": diff,
        "ingredients": kwargs.get("ingredients", "猪肉、葱"),
        "steps": ["步骤1"],
        "search_query": name,
    }


def make_week(*day_overrides):
    """Build a minimal valid 5-day week. Optionally override individual day dicts."""
    days = []
    day_names = ["周一", "周二", "周三", "周四", "周五"]
    for i, day in enumerate(day_names):
        override = day_overrides[i] if i < len(day_overrides) else {}
        days.append(
            {
                "day": day,
                "lunch": override.get(
                    "lunch",
                    {
                        "dishes": [make_dish(f"肉菜_{day}"), make_dish(f"素菜_{day}", tag="veg")],
                    },
                ),
                "dinner": override.get(
                    "dinner",
                    {
                        "dishes": [
                            make_dish(f"晚肉_{day}"),
                            make_dish(f"晚素_{day}", tag="veg", diff=1),
                        ],
                        "soup": make_dish(f"汤_{day}", tag="soup", diff=1),
                    },
                ),
            }
        )
    return {"week_start": "2026-04-28", "days": days}


# ── validate_menu: happy path ─────────────────────────────────────────────────


class TestValidateMenuHappyPath:
    def test_valid_week_returns_no_errors(self):
        errors = validate_menu(make_week())
        assert errors == []

    def test_empty_days_returns_no_errors(self):
        errors = validate_menu({"days": []})
        assert errors == []

    def test_hard_dish_count_exactly_two_is_ok(self):
        week = make_week()
        week["days"][0]["dinner"]["dishes"][0]["diff"] = 3
        week["days"][1]["dinner"]["dishes"][0]["diff"] = 3
        errors = validate_menu(week)
        assert errors == []


# ── validate_menu: dish repeat ────────────────────────────────────────────────


class TestDishRepeatRule:
    def test_same_dish_twice_is_ok(self):
        week = make_week()
        week["days"][0]["lunch"]["dishes"][0]["name"] = "鱼香肉丝"
        week["days"][1]["lunch"]["dishes"][0]["name"] = "鱼香肉丝"
        errors = validate_menu(week)
        assert errors == []

    def test_same_dish_three_times_is_error(self):
        week = make_week()
        for i in range(3):
            week["days"][i]["lunch"]["dishes"][0]["name"] = "鱼香肉丝"
        errors = validate_menu(week)
        assert any("鱼香肉丝" in e and "2×" in e for e in errors)

    def test_dish_repeated_across_lunch_and_dinner(self):
        week = make_week()
        week["days"][0]["lunch"]["dishes"][0]["name"] = "番茄炒鸡蛋"
        week["days"][0]["dinner"]["dishes"][0]["name"] = "番茄炒鸡蛋"
        week["days"][1]["lunch"]["dishes"][0]["name"] = "番茄炒鸡蛋"
        errors = validate_menu(week)
        assert any("番茄炒鸡蛋" in e for e in errors)


# ── validate_menu: lunch protein restriction ──────────────────────────────────


class TestLunchProteinRule:
    @pytest.mark.parametrize("forbidden", ["牛腩红烧", "肥牛炒饭", "肥羊卷"])
    def test_forbidden_protein_in_lunch_raises_error(self, forbidden):
        week = make_week()
        week["days"][0]["lunch"]["dishes"][0]["name"] = forbidden
        errors = validate_menu(week)
        assert any("forbidden" in e for e in errors)

    def test_beef_brisket_allowed_in_dinner(self):
        week = make_week()
        week["days"][0]["dinner"]["dishes"][0]["name"] = "番茄炖牛腩"
        errors = validate_menu(week)
        assert errors == []


# ── validate_menu: salmon rule ────────────────────────────────────────────────


class TestSalmonRule:
    def test_salmon_once_is_ok(self):
        week = make_week()
        week["days"][0]["dinner"]["dishes"][0]["name"] = "三文鱼饭"
        errors = validate_menu(week)
        assert errors == []

    def test_salmon_twice_is_error(self):
        week = make_week()
        week["days"][0]["lunch"]["dishes"][0]["name"] = "三文鱼沙拉"
        week["days"][1]["dinner"]["dishes"][0]["name"] = "三文鱼豆腐"
        errors = validate_menu(week)
        assert any("Salmon" in e for e in errors)

    def test_salmon_in_optional_counts(self):
        week = make_week()
        week["days"][0]["lunch"]["optional"] = make_dish("三文鱼凉拌", tag="opt", diff=1)
        week["days"][1]["dinner"]["dishes"][0]["name"] = "三文鱼饭"
        errors = validate_menu(week)
        assert any("Salmon" in e for e in errors)


# ── validate_menu: hard dish rule ─────────────────────────────────────────────


class TestHardDishRule:
    def test_three_hard_dishes_is_error(self):
        week = make_week()
        week["days"][0]["dinner"]["dishes"][0]["diff"] = 3
        week["days"][1]["dinner"]["dishes"][0]["diff"] = 3
        week["days"][2]["dinner"]["dishes"][0]["diff"] = 3
        errors = validate_menu(week)
        assert any("⭐⭐⭐" in e for e in errors)


# ── classify_store ────────────────────────────────────────────────────────────


class TestClassifyStore:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("猪里脊", "costco"),
            ("排骨", "costco"),
            ("鸡腿", "costco"),
            ("牛腩", "costco"),
            ("虾", "costco"),
            ("三文鱼", "costco"),
            ("鸡蛋", "costco"),
            ("白菜", "tnt"),
            ("豆腐", "tnt"),
            ("土豆", "tnt"),
            ("香菇", "tnt"),
        ],
    )
    def test_store_classification(self, name, expected):
        assert classify_store(name) == expected


# ── classify_category ─────────────────────────────────────────────────────────


class TestClassifyCategory:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("猪肉", "protein"),
            ("排骨", "protein"),
            ("鸡腿", "protein"),
            ("酱油", "pantry"),
            ("料酒", "pantry"),
            ("白菜", "veggie"),
            ("香菇", "veggie"),
        ],
    )
    def test_category_classification(self, name, expected):
        assert classify_category(name) == expected


# ── extract_ingredients ───────────────────────────────────────────────────────


class TestExtractIngredients:
    def test_extracts_unique_ingredients(self):
        menu = {
            "days": [
                {
                    "day": "周一",
                    "lunch": {
                        "dishes": [
                            {
                                "ingredients": "猪肉、葱",
                                "name": "a",
                                "tag": "meat",
                                "diff": 2,
                                "steps": [],
                                "search_query": "",
                                "style": "",
                            }
                        ],
                    },
                    "dinner": {
                        "dishes": [
                            {
                                "ingredients": "猪肉、白菜",
                                "name": "b",
                                "tag": "meat",
                                "diff": 2,
                                "steps": [],
                                "search_query": "",
                                "style": "",
                            }
                        ],
                        "soup": None,
                    },
                }
            ]
        }
        result = extract_ingredients(menu)
        names = [i["name"] for i in result]
        assert names.count("猪肉") == 1  # deduplicated
        assert "葱" in names
        assert "白菜" in names

    def test_includes_soup_ingredients(self):
        menu = {
            "days": [
                {
                    "day": "周一",
                    "lunch": {"dishes": []},
                    "dinner": {
                        "dishes": [],
                        "soup": {
                            "ingredients": "番茄、鸡蛋",
                            "name": "s",
                            "tag": "soup",
                            "diff": 1,
                            "steps": [],
                            "search_query": "",
                            "style": "",
                        },
                    },
                }
            ]
        }
        result = extract_ingredients(menu)
        names = [i["name"] for i in result]
        assert "番茄" in names
        assert "鸡蛋" in names

    def test_includes_optional_dish_ingredients(self):
        menu = {
            "days": [
                {
                    "day": "周一",
                    "lunch": {
                        "dishes": [],
                        "optional": {
                            "ingredients": "黄瓜、蒜",
                            "name": "o",
                            "tag": "opt",
                            "diff": 1,
                            "steps": [],
                            "search_query": "",
                            "style": "",
                        },
                    },
                    "dinner": {"dishes": []},
                }
            ]
        }
        result = extract_ingredients(menu)
        names = [i["name"] for i in result]
        assert "黄瓜" in names

    def test_handles_comma_separated_ingredients(self):
        menu = {
            "days": [
                {
                    "day": "周一",
                    "lunch": {
                        "dishes": [
                            {
                                "ingredients": "猪肉,葱,姜",
                                "name": "a",
                                "tag": "meat",
                                "diff": 2,
                                "steps": [],
                                "search_query": "",
                                "style": "",
                            }
                        ],
                    },
                    "dinner": {"dishes": []},
                }
            ]
        }
        result = extract_ingredients(menu)
        names = [i["name"] for i in result]
        assert "猪肉" in names
        assert "葱" in names
        assert "姜" in names
