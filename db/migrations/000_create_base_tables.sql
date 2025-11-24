-- 000_create_base_tables.sql
-- Create base tables for seeds and constraints, and migrations tracking

BEGIN;

CREATE TABLE IF NOT EXISTS migrations (
  id TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS seeds (
  word TEXT PRIMARY KEY,
  value REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS constraints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word1 TEXT,
  operator TEXT,
  word2 TEXT
);

COMMIT;
