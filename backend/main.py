import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)

# load_dotenv must run before database.py reads DATABASE_URL
load_dotenv()  # noqa: E402

from database import Base, engine  # noqa: E402
from routes.menu import router  # noqa: E402

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    import os

    from services.llm import provider

    p = provider()
    if p == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if key:
            log.info("AI provider: openai — OPENAI_API_KEY loaded (starts with %s...)", key[:12])
        else:
            log.warning("AI provider: openai — OPENAI_API_KEY is NOT set")
    else:
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if key:
            log.info(
                "AI provider: anthropic — ANTHROPIC_API_KEY loaded (starts with %s...)", key[:12]
            )
        else:
            log.warning("AI provider: anthropic — ANTHROPIC_API_KEY is NOT set")
    yield


app = FastAPI(title="Wokly API", lifespan=lifespan)

_cors_env = os.getenv("CORS_ORIGINS", "")
_cors_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
