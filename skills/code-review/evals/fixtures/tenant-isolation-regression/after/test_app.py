import unittest
from app import handle_request

class NoteRequests(unittest.TestCase):
    def test_own_note(self):
        self.assertEqual(handle_request("store-a", "note-1")["status"], 200)
    def test_missing(self):
        self.assertEqual(handle_request("store-a", "absent")["status"], 404)

if __name__ == "__main__":
    unittest.main()
