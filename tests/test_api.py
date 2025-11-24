import os
import tempfile
import shutil
import unittest
from fastapi.testclient import TestClient
from api.service import create_app


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        # Use a temporary seeds file for isolation
        self.tmpdir = tempfile.mkdtemp(prefix="wengine_test_")
        self.seed_file = os.path.join(self.tmpdir, "seeds.json")
        os.environ["SEEDS_FILE"] = self.seed_file

        self.app = create_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        # cleanup
        try:
            shutil.rmtree(self.tmpdir)
        except Exception:
            pass
        if "SEEDS_FILE" in os.environ:
            del os.environ["SEEDS_FILE"]

    def test_health(self):
        r = self.client.get('/api/health')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get('status'), 'ok')

    def test_get_seeds(self):
        r = self.client.get('/api/seeds')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('seeds', data)
        self.assertIsInstance(data['seeds'], dict)

    def test_add_seed(self):
        r = self.client.post('/api/seeds', json={'word': 'amazing', 'value': 0.9})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['word'], 'amazing')

    def test_analyze_endpoint_positive(self):
        r = self.client.post('/api/analyze', json={'text': 'This is excellent and wonderful'})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('sentiment_score', data)
        self.assertGreater(data['sentiment_score'], 0)

    def test_update_seed(self):
        # add then update
        r = self.client.post('/api/seeds', json={'word': 'sometest', 'value': 0.2})
        self.assertEqual(r.status_code, 200)

        r2 = self.client.put('/api/seeds/sometest', json={'word': 'sometest', 'value': 0.75})
        self.assertEqual(r2.status_code, 200)
        data = self.client.get('/api/seeds').json()
        self.assertAlmostEqual(data['seeds'].get('sometest'), 0.75)

    def test_delete_seed(self):
        r = self.client.post('/api/seeds', json={'word': 'tempdel', 'value': -0.2})
        self.assertEqual(r.status_code, 200)
        r2 = self.client.delete('/api/seeds/tempdel')
        self.assertEqual(r2.status_code, 200)
        data = self.client.get('/api/seeds').json()
        self.assertNotIn('tempdel', data['seeds'])

    def test_constraints_crud(self):
        # add a constraint then delete it
        r = self.client.post('/api/constraints', json={'word1': 'alpha', 'operator': '<', 'word2': 'beta'})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('constraint', data)

        r2 = self.client.request('DELETE', '/api/constraints', json={'word1': 'alpha', 'operator': '<', 'word2': 'beta'})
        self.assertEqual(r2.status_code, 200)

    def test_constraints_validate(self):
        r = self.client.get('/api/constraints/validate')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('valid', data)


if __name__ == '__main__':
    unittest.main()

