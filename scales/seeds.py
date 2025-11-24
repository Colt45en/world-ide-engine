"""
Seed Manager - Hand-labeled words with semantic values.
Core truth values for semantic analysis, not ML-generated.
"""

DEFAULT_SEEDS = {
    # Negative sentiments
    "terrible": -0.8,
    "awful": -0.75,
    "bad": -0.6,
    "poor": -0.5,
    "negative": -0.4,
    "unfortunate": -0.45,
    
    # Neutral
    "neutral": 0.0,
    "average": 0.0,
    "okay": 0.0,
    
    # Positive sentiments
    "good": 0.6,
    "great": 0.7,
    "excellent": 0.8,
    "wonderful": 0.85,
    "fantastic": 0.9,
    "positive": 0.4,
    "fortunate": 0.45,
}

DEFAULT_CONSTRAINTS = [
    # Ordering relationships - explicit semantic constraints
    ("terrible", "<", "awful"),
    ("awful", "<", "bad"),
    ("bad", "<", "poor"),
    ("poor", "<", "negative"),
    ("negative", "<", "neutral"),
    ("neutral", "<", "positive"),
    ("positive", "<", "good"),
    ("good", "<", "great"),
    ("great", "<", "excellent"),
    ("excellent", "<", "wonderful"),
    ("wonderful", "<", "fantastic"),
]


import json
import os
from typing import Optional


class SeedManager:
    """Manages hand-labeled semantic seed words and their values."""
    
    def __init__(self):
        self.seeds = {}
        self.constraints = []
    
    def add_seed(self, word: str, value: float):
        """Add a hand-labeled seed word with semantic value (-1.0 to 1.0)."""
        if not -1.0 <= value <= 1.0:
            raise ValueError(f"Seed value must be between -1.0 and 1.0, got {value}")
        self.seeds[word.lower()] = value
    
    def get_seed(self, word: str) -> float | None:
        """Get semantic value for a seed word."""
        return self.seeds.get(word.lower())
    
    def add_constraint(self, word1: str, operator: str, word2: str):
        """Add ordering constraint between two words."""
        if operator not in ("<", ">", "="):
            raise ValueError(f"Invalid operator: {operator}")
        self.constraints.append((word1.lower(), operator, word2.lower()))

    def delete_seed(self, word: str) -> bool:
        """Delete a seed from the manager. Returns True if deleted, False if not found."""
        key = word.lower()
        if key in self.seeds:
            del self.seeds[key]
            return True
        return False

    def delete_constraint(self, word1: str, operator: str, word2: str) -> bool:
        """Delete a constraint. Returns True if deleted, False if not found."""
        tpl = (word1.lower(), operator, word2.lower())
        if tpl in self.constraints:
            self.constraints = [c for c in self.constraints if c != tpl]
            return True
        return False
    
    def validate_constraints(self) -> list[str]:
        """Validate all constraints against current seed values."""
        violations = []
        for word1, op, word2 in self.constraints:
            val1 = self.seeds.get(word1)
            val2 = self.seeds.get(word2)
            
            if val1 is None or val2 is None:
                continue
            
            if op == "<" and not val1 < val2:
                violations.append(f"{word1} ({val1}) should be < {word2} ({val2})")
            elif op == ">" and not val1 > val2:
                violations.append(f"{word1} ({val1}) should be > {word2} ({val2})")
            elif op == "=" and not val1 == val2:
                violations.append(f"{word1} ({val1}) should be = {word2} ({val2})")
        
        return violations
    
    def load_defaults(self):
        """Load default seeds and constraints."""
        for word, value in DEFAULT_SEEDS.items():
            self.add_seed(word, value)
        
        for word1, op, word2 in DEFAULT_CONSTRAINTS:
            self.add_constraint(word1, op, word2)

    # Persistence helpers -------------------------------------------------
    def save_to_file(self, path: str):
        """Save current seeds and constraints to a JSON file at `path`.

        Ensures the directory exists before writing.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
            "seeds": self.seeds,
            "constraints": self.constraints,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

    def load_from_file(self, path: str) -> bool:
        """Load seeds and constraints from JSON file at `path`.

        Returns True if file existed and was loaded, False otherwise.
        """
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)

        seeds = payload.get("seeds", {})
        constraints = payload.get("constraints", [])

        # reset current data and load
        self.seeds = {k.lower(): float(v) for k, v in seeds.items()}
        self.constraints = [(w1.lower(), op, w2.lower()) for w1, op, w2 in constraints]
        return True

    # SQLite persistence --------------------------------------------------
    def save_to_db(self, path: str):
        """Persist seeds and constraints to a sqlite3 database file."""
        import sqlite3

        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Ensure migrations are applied first
        try:
            from scales.migrations import run_migrations
            run_migrations(path)
        except Exception:
            # If migrations cannot run, continue with best-effort
            pass

        conn = sqlite3.connect(path, timeout=10)
        try:
            cur = conn.cursor()
            # enable WAL for better concurrent write/read behavior
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS seeds (
                    word TEXT PRIMARY KEY,
                    value REAL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS constraints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word1 TEXT,
                    operator TEXT,
                    word2 TEXT
                )
            """)

            # Upsert seeds
            for word, value in self.seeds.items():
                cur.execute("INSERT OR REPLACE INTO seeds(word, value) VALUES (?, ?)", (word, float(value)))

            # Clear existing constraints then insert
            cur.execute("DELETE FROM constraints")
            for w1, op, w2 in self.constraints:
                cur.execute("INSERT INTO constraints(word1, operator, word2) VALUES (?, ?, ?)", (w1, op, w2))

            conn.commit()
        finally:
            conn.close()

    def load_from_db(self, path: str) -> bool:
        """Load seeds and constraints from sqlite3 DB file. Returns True if loaded, False otherwise."""
        import sqlite3

        if not os.path.exists(path):
            return False
        # ensure migrations are applied, then load
        try:
            from scales.migrations import run_migrations
            run_migrations(path)
        except Exception:
            pass

        conn = sqlite3.connect(path, timeout=10)
        try:
            cur = conn.cursor()
            cur.execute("SELECT word, value FROM seeds")
            rows = cur.fetchall()
            self.seeds = {r[0].lower(): float(r[1]) for r in rows}

            cur.execute("SELECT word1, operator, word2 FROM constraints")
            rows = cur.fetchall()
            self.constraints = [(r[0].lower(), r[1], r[2].lower()) for r in rows]
            return True
        finally:
            conn.close()

