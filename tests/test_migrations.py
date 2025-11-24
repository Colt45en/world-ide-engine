import os
import sqlite3
import tempfile
import shutil
import unittest
from scales.migrations import run_migrations

class TestMigrations(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='wengine_migtest_')
        self.dbfile = os.path.join(self.tmpdir, 'seeds.db')

    def tearDown(self):
        try:
            shutil.rmtree(self.tmpdir)
        except Exception:
            pass

    def test_run_migrations_and_tables(self):
        # ensure migrations can be applied on empty db
        run_migrations(self.dbfile)
        self.assertTrue(os.path.exists(self.dbfile))

        conn = sqlite3.connect(self.dbfile)
        cur = conn.cursor()
        # check migrations table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        self.assertIsNotNone(cur.fetchone())
        # check seeds table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='seeds'")
        self.assertIsNotNone(cur.fetchone())
        # check constraints table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='constraints'")
        self.assertIsNotNone(cur.fetchone())
        conn.close()

if __name__ == '__main__':
    unittest.main()
