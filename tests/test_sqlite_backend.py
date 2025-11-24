import os
import sqlite3
import tempfile
import shutil
import unittest
from fastapi.testclient import TestClient

from api.service import create_app


class TestSQLiteBackend(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="wengine_sqltest_")
        self.dbfile = os.path.join(self.tmpdir, "seeds.db")
        os.environ['SEEDS_FILE'] = self.dbfile
        self.app = create_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        try:
            shutil.rmtree(self.tmpdir)
        except Exception:
            pass
        if 'SEEDS_FILE' in os.environ:
            del os.environ['SEEDS_FILE']

    def test_add_seed_persist_db(self):
        # Add a seed
        r = self.client.post('/api/seeds', json={'word': 'sqlite_test', 'value': 0.42})
        self.assertEqual(r.status_code, 200)

        # DB file should exist
        self.assertTrue(os.path.exists(self.dbfile))

        # Inspect database directly
        conn = sqlite3.connect(self.dbfile)
        cur = conn.cursor()
        cur.execute('SELECT value FROM seeds WHERE word = ?', ('sqlite_test',))
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row[0], 0.42, places=3)

        # Recreate app (simulate restart) and check seed loaded
        app2 = create_app()
        client2 = TestClient(app2)
        r2 = client2.get('/api/seeds')
        self.assertEqual(r2.status_code, 200)
        data = r2.json()
        self.assertAlmostEqual(data['seeds'].get('sqlite_test'), 0.42)


if __name__ == '__main__':
    unittest.main()
