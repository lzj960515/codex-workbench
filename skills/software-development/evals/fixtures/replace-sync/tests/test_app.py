import unittest
from app import discover, import_csv


class ReceptionTests(unittest.TestCase):
    def test_discover_stores_returned_rows(self):
        store = {}
        self.assertEqual(discover(store, [{'id': 'a', 'title': 'first'}]), ['a'])
        self.assertEqual(store['a']['title'], 'first')

    def test_import_updates_existing_title(self):
        store = {'a': {'id': 'a', 'title': 'old'}}
        self.assertEqual(import_csv(store, [{'id': 'a', 'title': 'new'}]), ['a'])
        self.assertEqual(store['a']['title'], 'new')
