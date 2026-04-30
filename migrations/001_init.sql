-- Neon PostgreSQL schema (reference only — SQLite is used for local dev)
-- Run against your Neon database to initialize the schema.

CREATE TABLE weeks (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start    DATE NOT NULL UNIQUE,
  generated_at  TIMESTAMP,
  status        TEXT DEFAULT 'pending'   -- pending | ready | failed
);

CREATE TABLE meals (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_id       UUID REFERENCES weeks(id) ON DELETE CASCADE,
  day           TEXT NOT NULL,           -- 周一 | 周二 | 周三 | 周四 | 周五
  meal_type     TEXT NOT NULL,           -- lunch | dinner
  dish1         JSONB,
  dish2         JSONB,
  optional_dish JSONB,                   -- lunch only (wife WFH)
  soup          JSONB,                   -- dinner only
  UNIQUE (week_id, day, meal_type)
);

CREATE TABLE ingredients (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_id     UUID REFERENCES weeks(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  quantity    TEXT,
  store       TEXT DEFAULT 'tnt',        -- costco | tnt | either
  category    TEXT,                      -- protein | veggie | pantry
  checked     BOOLEAN DEFAULT false,
  overridden  BOOLEAN DEFAULT false
);

CREATE INDEX idx_meals_week_id ON meals(week_id);
CREATE INDEX idx_ingredients_week_id ON ingredients(week_id);
