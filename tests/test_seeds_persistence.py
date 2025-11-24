import os
import tempfile
import unittest
from scales.seeds import SeedManager


class TestSeedPersistence(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="wengine_seedtest_")
        self.seed_file = os.path.join(self.tmpdir, "seeds.json")

    def tearDown(self):
        try:
            import shutil

            shutil.rmtree(self.tmpdir)
        except Exception:
            pass

    def test_save_and_load(self):
        m1 = SeedManager()
        m1.add_seed("persist_test", 0.33)
        m1.add_constraint("persist_test", "<", "excellent")
        m1.save_to_file(self.seed_file)

        self.assertTrue(os.path.exists(self.seed_file))

        m2 = SeedManager()
        loaded = m2.load_from_file(self.seed_file)
        self.assertTrue(loaded)
        self.assertIn("persist_test", m2.seeds)
        self.assertAlmostEqual(m2.get_seed("persist_test"), 0.33, places=3)
        self.assertTrue(any(c[0] == "persist_test" for c in m2.constraints))


if __name__ == "__main__":
    unittest.main()
