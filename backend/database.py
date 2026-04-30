import os
import ssl
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./wokly.db")

if DATABASE_URL.startswith("sqlite"):
    connect_args: dict = {"check_same_thread": False}
else:
    # asyncpg does not accept sslmode/channel_binding as URL query params.
    # Strip them from the URL and pass an SSL context via connect_args instead.
    _parsed = urlparse(DATABASE_URL)
    _params = {
        k: v[0]
        for k, v in parse_qs(_parsed.query).items()
        if k not in ("sslmode", "channel_binding")
    }
    DATABASE_URL = urlunparse(_parsed._replace(query=urlencode(_params)))
    _ssl_ctx = ssl.create_default_context()
    connect_args = {"ssl": _ssl_ctx}

engine = create_async_engine(DATABASE_URL, connect_args=connect_args)

if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, _rec):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")  # allow concurrent reads during write
        cur.execute("PRAGMA busy_timeout=5000")  # wait up to 5s instead of failing immediately
        cur.close()


AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
