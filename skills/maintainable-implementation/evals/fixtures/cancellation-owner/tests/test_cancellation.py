import unittest
import web
import cli
from repository import MemoryJobs


class CancellationContract(unittest.TestCase):
    def test_pending_cancels(self):
        for entry in (web.cancel_export, cli.cancel_export):
            with self.subTest(entry=entry.__module__):
                repo = MemoryJobs("pending")
                result = entry(repo, "job-1")
                self.assertEqual(result["status"], "cancelled")
                self.assertEqual(repo.get("job-1")["status"], "cancelled")
                self.assertEqual(repo.save_count, 1)

    def test_running_rejected(self):
        for entry in (web.cancel_export, cli.cancel_export):
            with self.subTest(entry=entry.__module__):
                repo = MemoryJobs("running")
                with self.assertRaisesRegex(ValueError, "job cannot be cancelled"):
                    entry(repo, "job-1")
                self.assertEqual(repo.save_count, 0)


if __name__ == "__main__":
    unittest.main()
