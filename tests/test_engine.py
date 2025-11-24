"""
Tests for the World Engine semantic analysis system.
"""

import unittest
from scales.seeds import SeedManager, DEFAULT_SEEDS, DEFAULT_CONSTRAINTS
from context.parser import TextParser
from api.service import WorldEngineAPI


class TestSeedManager(unittest.TestCase):
    def setUp(self):
        self.manager = SeedManager()
    
    def test_add_seed(self):
        self.manager.add_seed("test", 0.5)
        self.assertEqual(self.manager.get_seed("test"), 0.5)
    
    def test_seed_value_range(self):
        with self.assertRaises(ValueError):
            self.manager.add_seed("invalid", 1.5)
    
    def test_case_insensitive(self):
        self.manager.add_seed("Test", 0.5)
        self.assertEqual(self.manager.get_seed("test"), 0.5)
        self.assertEqual(self.manager.get_seed("TEST"), 0.5)
    
    def test_load_defaults(self):
        self.manager.load_defaults()
        self.assertIsNotNone(self.manager.get_seed("excellent"))
        self.assertIsNotNone(self.manager.get_seed("terrible"))
    
    def test_constraints_validation(self):
        self.manager.add_seed("bad", -0.6)
        self.manager.add_seed("good", 0.6)
        self.manager.add_constraint("bad", "<", "good")
        
        violations = self.manager.validate_constraints()
        self.assertEqual(len(violations), 0)


class TestTextParser(unittest.TestCase):
    def setUp(self):
        self.parser = TextParser()
    
    def test_parse_text(self):
        result = self.parser.parse("This is a test.")
        self.assertIn("tokens", result)
        self.assertIn("entities", result)
        self.assertIn("sentences", result)
        self.assertEqual(len(result["tokens"]), 5)  # This, is, a, test, .
    
    def test_extract_keywords(self):
        keywords = self.parser.extract_keywords("The excellent product works great")
        self.assertIn("excellent", keywords)
        self.assertIn("product", keywords)


class TestWorldEngineAPI(unittest.TestCase):
    def setUp(self):
        self.api = WorldEngineAPI()
    
    def test_analyze_positive_text(self):
        result = self.api.analyze_text("This is an excellent product!")
        self.assertGreater(result["sentiment_score"], 0)
    
    def test_analyze_negative_text(self):
        result = self.api.analyze_text("This is a terrible experience.")
        self.assertLess(result["sentiment_score"], 0)
    
    def test_analyze_neutral_text(self):
        result = self.api.analyze_text("This is a thing.")
        self.assertAlmostEqual(result["sentiment_score"], 0, places=1)


if __name__ == "__main__":
    unittest.main()