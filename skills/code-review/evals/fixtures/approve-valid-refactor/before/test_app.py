import unittest
from app import run

class EntryContract(unittest.TestCase):
    def test_modes(self):
        self.assertEqual(run({"mode": "normal"}), {"attempt_limit": 3})
        self.assertEqual(run({"mode": "fast"}), {"attempt_limit": 5})
    def test_default(self):
        self.assertEqual(run({}), {"attempt_limit": 3})
    def test_invalid(self):
        for value in ["other", None, 7, [], {}]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                run({"mode": value})

if __name__ == "__main__":
    unittest.main()
