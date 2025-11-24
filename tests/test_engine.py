"""
Tests for the engine.
"""

import unittest
from engine.core import Engine

class TestEngine(unittest.TestCase):
    def test_engine_init(self):
        engine = Engine()
        self.assertIsNotNone(engine.screen)
        self.assertIsNotNone(engine.clock)

if __name__ == "__main__":
    unittest.main()