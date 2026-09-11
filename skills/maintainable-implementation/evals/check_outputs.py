"""Check public results of the controlled implementation cases; keep outside fixtures."""
import argparse
import importlib
import json
import sys
from pathlib import Path


def check_headers():
    cli = importlib.import_module("cli")
    actual = cli.response_metadata("request-42")
    assert actual == {"Content-Type": "application/json", "X-Request-Id": "request-42"}, actual
    return ["new header contract"]


def check_cancellation():
    web = importlib.import_module("web")
    cli = importlib.import_module("cli")
    MemoryJobs = importlib.import_module("repository").MemoryJobs
    checks = []
    for entry in (web.cancel_export, cli.cancel_export):
        for status in ("pending", "queued", "running", "completed", "cancelled"):
            repo = MemoryJobs(status)
            if status in ("pending", "queued"):
                result = entry(repo, "job-1")
                assert result == {"id": "job-1", "status": "cancelled"}, result
                assert repo.get("job-1") == result
                assert repo.save_count == 1, repo.save_count
            else:
                try:
                    entry(repo, "job-1")
                except ValueError as error:
                    assert str(error) == "job cannot be cancelled", str(error)
                else:
                    raise AssertionError("unsupported state accepted: " + status)
                assert repo.get("job-1")["status"] == status
                assert repo.save_count == 0
            checks.append(entry.__module__ + ":" + status)
        repo = MemoryJobs("pending")
        try:
            entry(repo, "missing")
        except KeyError:
            pass
        else:
            raise AssertionError("missing job did not propagate")
        assert repo.save_count == 0
        failure = OSError("controlled save failure")

        def fail_save(job):
            raise failure

        repo.save = fail_save
        try:
            entry(repo, "job-1")
        except OSError as error:
            assert error is failure
        else:
            raise AssertionError("save failure was swallowed")
        checks.append(entry.__module__ + ":failures propagate")
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=["mechanical-header", "cancellation-owner"])
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.workspace.resolve()))
    checks = check_headers() if args.case == "mechanical-header" else check_cancellation()
    print(json.dumps({"status": "pass", "checks": checks}))


if __name__ == "__main__":
    main()
