import os
import tempfile
import shutil
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from api.service import create_app


class TestConcurrentDBWrites(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='wengine_concurrent_')
        self.dbfile = os.path.join(self.tmpdir, 'seeds.db')
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

    def _add_seed(self, i):
        word = f'concurrent_{i}'
        value = (i % 10) / 10.0
        r = self.client.post('/api/seeds', json={'word': word, 'value': value})
        return (word, r.status_code)

    def test_concurrent_adds(self):
        tasks = 50
        results = []
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(self._add_seed, i) for i in range(tasks)]
            for fut in as_completed(futures):
                results.append(fut.result())

        # all posts succeeded
        self.assertTrue(all(code == 200 for _, code in results))

        r = self.client.get('/api/seeds')
        seeds = r.json()['seeds']
        for i in range(tasks):
            self.assertIn(f'concurrent_{i}', seeds)

    def test_concurrent_updates_same_key(self):
        # create base seed
        r = self.client.post('/api/seeds', json={'word': 'sharedkey', 'value': 0.0})
        self.assertEqual(r.status_code, 200)

        def update_value(i):
            v = (i % 100) / 100.0
            return self.client.put('/api/seeds/sharedkey', json={'word': 'sharedkey', 'value': v}).status_code

        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(update_value, i) for i in range(100)]
            codes = [f.result() for f in futures]
        # all updates responded OK
        self.assertTrue(all(c == 200 for c in codes))

        # final value should be a float in DB
        r2 = self.client.get('/api/seeds')
        val = r2.json()['seeds'].get('sharedkey')
        self.assertIsInstance(val, float)


if __name__ == '__main__':
    unittest.main()
