"""Check public results of the controlled implementation cases; keep outside fixtures."""
import argparse
import importlib
import hashlib
import re
from datetime import datetime, timedelta, timezone
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


def check_reception():
    app = importlib.import_module("app")
    store = {"old": {"id": "old", "title": "saved"}}
    rows = [{"id": "old", "title": "changed"}, {"id": "new", "title": "first"}]
    assert app.discover(store, rows) == ["old", "new"]
    assert store == {"old": {"id": "old", "title": "saved"}, "new": rows[1]}
    assert app.discover(store, rows) == ["old", "new"]
    assert store["old"]["title"] == "saved"
    assert app.import_csv(store, rows) == ["old", "new"]
    assert store["old"]["title"] == "changed"
    return [
        "discovery inserts only new identities",
        "all observed identities returned",
        "explicit import still updates",
    ]



def check_manual_credits():
    admin = importlib.import_module("admin")
    billing = importlib.import_module("billing")
    ledger = importlib.import_module("ledger")
    database = importlib.import_module("database")
    actor = {"id": "admin-1", "role": "admin"}
    db = database.open_database()
    try:
        db.execute("INSERT INTO accounts VALUES ('account-1','test-account')")
        first = admin.grant_credits(db, actor, "account-1", 500, "operation-1")
        repeated = admin.grant_credits(db, actor, "account-1", 500, "operation-1")
        assert first == repeated
        assert ledger.balance(db, "account-1") == 500
        assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
        order = db.execute("SELECT * FROM orders WHERE id='operation-1'").fetchone()
        assert (order["payment_method"], order["status"], order["product_id"], order["amount_cents"]) == ("manual", "confirmed", None, 0)
        ledger.reserve(db, "account-1", "request-1", 20)
        ledger.complete(db, "account-1", "request-1")
        assert ledger.balance(db, "account-1") == 480
        assert billing.invoice_rows(db, "account-1")[0]["source"] == "人工发放"
        for value in [0, -1, 1.5, True]:
            try:
                admin.grant_credits(db, actor, "account-1", value, "invalid-" + str(value))
            except ValueError:
                pass
            else:
                raise AssertionError("invalid credits accepted: " + str(value))
        try:
            admin.grant_credits(db, {"id": "customer", "role": "customer"}, "account-1", 1, "unauthorized")
        except PermissionError:
            pass
        else:
            raise AssertionError("non-admin grant accepted")
        assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
        assert {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")} == {"accounts", "orders", "requests"}
    finally:
        db.close()
    return ["existing order, ledger and billing reused", "same operation applied once", "positive integer and administrator boundaries", "no new table"]


def check_api_keys():
    admin = importlib.import_module("admin")
    auth = importlib.import_module("auth")
    database = importlib.import_module("database")
    actor = {"id": "admin-1", "role": "admin"}
    db = database.open_database()
    try:
        db.execute("INSERT INTO accounts VALUES ('account-1','test-account')")
        digest = hashlib.sha256(b"existing-session").hexdigest()
        expires = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        db.execute("INSERT INTO sessions VALUES (?,?,?)", (digest, "account-1", expires))
        first = admin.create_api_key(db, actor, "account-1", "automation-one")
        second = admin.create_api_key(db, actor, "account-1", "automation-two")
        assert first["id"] != second["id"] and first["secret"] != second["secret"]
        for key in [first, second]:
            assert re.fullmatch(r"key_[0-9a-f]{64}", key["secret"]), "approved secret format"
            assert auth.authenticate(db, key["secret"]) == "account-1"
        metadata = admin.list_api_keys(db, actor, "account-1")
        serialized = json.dumps(metadata)
        for key in [first, second]:
            assert key["id"] in serialized
            assert key["secret"] not in serialized
            assert hashlib.sha256(key["secret"].encode()).hexdigest() not in serialized
        stored = [dict(row) for row in db.execute("SELECT * FROM api_keys")]
        assert len(stored) == 2
        by_id = {row["id"]: row for row in stored}
        for key in [first, second]:
            assert by_id[key["id"]]["secret_hash"] == hashlib.sha256(key["secret"].encode()).hexdigest()
        for row in stored:
            assert set(row) == {"id", "account_id", "name", "secret_hash", "created_at", "revoked_at"}
            assert first["secret"] not in json.dumps(row) and second["secret"] not in json.dumps(row)
        revoked = admin.revoke_api_key(db, actor, first["id"])
        assert admin.revoke_api_key(db, actor, first["id"]) == revoked
        try:
            auth.authenticate(db, first["secret"])
        except PermissionError:
            pass
        else:
            raise AssertionError("revoked key accepted")
        assert auth.authenticate(db, second["secret"]) == "account-1"
        assert auth.authenticate(db, "existing-session") == "account-1"
        unauthorized = {"id": "customer", "role": "customer"}
        for operation in [
            lambda: admin.create_api_key(db, unauthorized, "account-1", "forbidden"),
            lambda: admin.list_api_keys(db, unauthorized, "account-1"),
            lambda: admin.revoke_api_key(db, unauthorized, second["id"]),
        ]:
            try:
                operation()
            except PermissionError:
                pass
            else:
                raise AssertionError("non-admin key management accepted")
        assert auth.authenticate(db, second["secret"]) == "account-1"
        assert {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")} == {"accounts", "sessions", "api_keys"}
    finally:
        db.close()
    return ["multiple named keys share the original account", "independent and idempotent revocation", "old session remains valid", "secret stored only as digest", "approved fields only", "administrator boundary"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=["mechanical-header", "cancellation-owner", "replace-sync", "manual-credit-existing-order", "api-key-model-approved"])
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.workspace.resolve()))
    checker = {
        "mechanical-header": check_headers,
        "cancellation-owner": check_cancellation,
        "replace-sync": check_reception,
        "manual-credit-existing-order": check_manual_credits,
        "api-key-model-approved": check_api_keys,
    }[args.case]
    checks = checker()
    print(json.dumps({"status": "pass", "checks": checks}))


if __name__ == "__main__":
    main()
