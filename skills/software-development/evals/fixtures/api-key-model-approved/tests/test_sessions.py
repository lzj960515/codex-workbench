import hashlib
import unittest
from datetime import datetime,timedelta,timezone
from database import open_database
from auth import authenticate

class Sessions(unittest.TestCase):
    def test_existing_session_resolves_account(self):
        db=open_database()
        self.addCleanup(db.close)
        db.execute("INSERT INTO accounts VALUES ('account-1','test-account')")
        digest=hashlib.sha256(b'existing-session').hexdigest()
        expires=(datetime.now(timezone.utc)+timedelta(minutes=15)).isoformat()
        db.execute("INSERT INTO sessions VALUES (?,?,?)",(digest,'account-1',expires))
        self.assertEqual(authenticate(db,'existing-session'),'account-1')
        with self.assertRaises(PermissionError):authenticate(db,'unknown-session')
