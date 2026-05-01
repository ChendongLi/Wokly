-- Add config table for storing key-value settings (e.g., custom prompt)
CREATE TABLE IF NOT EXISTS config (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
