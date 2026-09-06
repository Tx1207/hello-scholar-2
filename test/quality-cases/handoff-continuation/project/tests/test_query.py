import unittest
from src.query import normalize_query


class QueryTests(unittest.TestCase):
    def test_plain_query(self):
        self.assertEqual("hello", normalize_query("hello"))

    def test_empty_query(self):
        self.assertEqual("", normalize_query(""))


if __name__ == "__main__":
    unittest.main()
