import unittest
from rows import visible_rows

class RowsTest(unittest.TestCase):
    def test_page_order(self):
        self.assertEqual(visible_rows({"page": [{"name": "B"}, {"name": "A"}]}), [{"name": "B"}, {"name": "A"}])
