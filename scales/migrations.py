"""Simple SQLite migrations runner for seeds DB.

Migrations live in db/migrations and are named with a numeric prefix. This module
applies any migrations that have not yet been applied (tracked in the `migrations` table).
"""
import os
import sqlite3
from datetime import datetime

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'migrations')


def run_migrations(db_path: str):
    """Run any new migrations in MIGRATIONS_DIR against `db_path`.
    Creates the migrations table if necessary.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # ensure migrations table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)
        conn.commit()

        # gather applied ids
        cur.execute("SELECT id FROM migrations")
        applied = {r[0] for r in cur.fetchall()}

        # list migration files sorted
        if not os.path.isdir(MIGRATIONS_DIR):
            return

        migrations = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])

        for mfile in migrations:
            mid = mfile
            if mid in applied:
                continue
            path = os.path.join(MIGRATIONS_DIR, mfile)
            with open(path, 'r', encoding='utf-8') as fh:
                sql = fh.read()
            # apply migration (support multiple statements)
            cur.executescript(sql)
            cur.execute("INSERT INTO migrations(id, applied_at) VALUES (?, ?)", (mid, datetime.utcnow().isoformat()))
            conn.commit()
    finally:
        conn.close()
