"""
Shared fixtures for backend tests.

Uses an in-memory SQLite database so tests are isolated and fast.
The get_db dependency is overridden to point at the test DB.
"""

import os

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import database as db_module
from database import Base
from main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a fresh in-memory SQLite DB for each test."""
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[db_module.get_db] = override_get_db

    yield session_factory

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """HTTPX async client wired to the FastAPI app with the test DB."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Shared menu fixture ───────────────────────────────────────────────────────

VALID_MENU = {
    "week_start": "2026-04-28",
    "days": [
        {
            "day": day,
            "lunch": {
                "dishes": [
                    {
                        "name": f"鱼香肉丝_{day}",
                        "tag": "meat",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "猪里脊、木耳、胡萝卜",
                        "steps": ["切丝备用", "热锅下油", "翻炒均匀"],
                        "search_query": "鱼香肉丝做法",
                    },
                    {
                        "name": f"醋熘土豆丝_{day}",
                        "tag": "veg",
                        "style": "多料炒",
                        "diff": 2,
                        "ingredients": "土豆、青椒、醋",
                        "steps": ["土豆切丝", "泡水去淀粉", "快炒出锅"],
                        "search_query": "醋熘土豆丝",
                    },
                ],
                "optional": {
                    "name": f"凉拌黄瓜_{day}",
                    "tag": "opt",
                    "style": "凉拌",
                    "diff": 1,
                    "ingredients": "黄瓜、蒜、醋",
                    "steps": ["拍黄瓜", "加调料拌匀"],
                    "search_query": "凉拌黄瓜",
                },
            },
            "dinner": {
                "dishes": [
                    {
                        "name": f"红烧鸡块_{day}",
                        "tag": "meat",
                        "style": "炖烧",
                        "diff": 3,
                        "ingredients": "鸡腿、酱油、葱姜蒜",
                        "steps": ["鸡块焯水", "热锅炒糖色", "加水炖煮", "收汁出锅"],
                        "search_query": "红烧鸡块",
                    },
                    {
                        "name": f"蒜蓉菠菜_{day}",
                        "tag": "veg",
                        "style": "快炒",
                        "diff": 1,
                        "ingredients": "菠菜、蒜",
                        "steps": ["菠菜焯水", "蒜末爆香", "下菠菜翻炒"],
                        "search_query": "蒜蓉菠菜",
                    },
                ],
                "soup": {
                    "name": f"番茄蛋花汤_{day}",
                    "tag": "soup",
                    "style": "汤",
                    "diff": 1,
                    "ingredients": "番茄、鸡蛋",
                    "steps": ["番茄切块", "热锅炒番茄", "加水煮开打蛋花"],
                    "search_query": "番茄蛋花汤",
                },
            },
        }
        for day in ["周一", "周二", "周三", "周四", "周五"]
    ],
}
