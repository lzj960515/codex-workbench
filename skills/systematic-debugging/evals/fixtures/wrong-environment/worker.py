import argparse
import json
from pathlib import Path

root = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument("--environment", choices=["sandbox", "production"])
args = parser.parse_args()
settings = json.loads((root / "settings.json").read_text())
event = json.loads((root / "event.json").read_text())
environment = args.environment or settings["environment"]
records = json.loads((root / "snapshots" / (environment + ".json")).read_text())
for attempt in range(1, settings["attempts"] + 1):
    record = records.get(event["job_id"])
    print(json.dumps({"environment": environment, "job_id": event["job_id"], "attempt": attempt, "status": 200 if record else 404}))
    if record:
        break
