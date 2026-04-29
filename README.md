# Wokly

AI-powered weekly Chinese family menu generator. Shandong + Northeast Chinese cuisine, mobile-first, Claude-generated menus every Friday.

## Tech Stack

| Layer     | Technology                                    |
| --------- | --------------------------------------------- |
| Frontend  | React + Vite + Tailwind CSS                   |
| Backend   | FastAPI (Python 3.12)                         |
| Database  | SQLite (local) / Neon PostgreSQL (production) |
| AI        | Claude Sonnet (`claude-sonnet-4-6`)           |
| Container | Docker + Docker Compose                       |

---

## Code Quality

Pre-commit hooks enforce formatting and linting on every commit.

| Tool               | What it checks                                             |
| ------------------ | ---------------------------------------------------------- |
| `ruff`             | Python lint (pyflakes, pycodestyle, isort, pyupgrade)      |
| `ruff-format`      | Python formatting (replaces black)                         |
| `prettier`         | JS/JSX/CSS/JSON/Markdown formatting                        |
| `eslint`           | JS/JSX linting (React + React Hooks rules)                 |
| `pre-commit-hooks` | Trailing whitespace, YAML/JSON validity, no-commit-to-main |

### Setup

```bash
pip install pre-commit          # or: pip install -r backend/requirements-dev.txt
pre-commit install              # wire hooks into .git/hooks/pre-commit
```

After this, hooks run automatically on `git commit`. To run manually against all files:

```bash
pre-commit run --all-files
```

### Tests

```bash
# Backend (57 tests)
cd backend && pytest tests/ -v

# Frontend (46 tests)
cd frontend && npm test
```

---

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Environment variables

```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API running at http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# UI running at http://localhost:5173
```

### 4. Generate a menu

Open `http://localhost:5173`, tap **菜单** tab, then tap **生成菜单**. Claude generates the full week and saves it to SQLite.

---

## Docker Compose (alternative)

```bash
cp .env.example .env  # set ANTHROPIC_API_KEY
docker-compose up --build
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

---

## API Routes

| Method | Path                       | Description                   |
| ------ | -------------------------- | ----------------------------- |
| `GET`  | `/api/week/current`        | Current week menu             |
| `POST` | `/api/generate`            | Trigger full week generation  |
| `PUT`  | `/api/meal/{id}`           | Edit a single dish            |
| `POST` | `/api/meal/{id}/regen`     | AI-regenerate a single dish   |
| `GET`  | `/api/history`             | List past weeks               |
| `GET`  | `/api/week/{id}`           | Read a past week              |
| `GET`  | `/api/ingredients/current` | Current week shopping list    |
| `PUT`  | `/api/ingredients/{id}`    | Toggle checked / change store |
| `GET`  | `/api/health`              | Backend health check          |

---

## Production (Neon + GCP Cloud Run)

Switch `DATABASE_URL` in your environment to a Neon PostgreSQL URL:

```
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
```

Run `migrations/001_init.sql` against your Neon database once to initialize the schema.

GCP Cloud Run deployment scripts are tracked separately in a future PR.

---

## Project Structure

```
wokly/
├── backend/
│   ├── main.py           # FastAPI entry point
│   ├── database.py       # Async SQLAlchemy engine
│   ├── models.py         # ORM models + Pydantic schemas
│   ├── routes/menu.py    # All API routes
│   ├── services/
│   │   ├── generator.py  # Full-week Claude generation + validation
│   │   └── regen.py      # Single-dish regeneration
│   └── prompts/
│       └── menu_system.txt  # Chinese system prompt
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── components/   # MenuTab, DishCard, RecipeDrawer, ShopTab, ...
│       └── hooks/        # React Query API hooks
├── migrations/
│   └── 001_init.sql      # Neon PostgreSQL schema reference
├── Dockerfile
└── docker-compose.yml
```
