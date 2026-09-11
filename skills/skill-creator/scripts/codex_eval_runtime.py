"""Codex app-server session and single-turn evidence capture.

Extracted from the local discovery-helper used by the September Skill trials.
"""
import json
import queue
import subprocess
import threading
import time
from pathlib import Path

class EvaluationBlocked(RuntimeError):
    """The runtime needs input or cannot provide a comparable execution."""


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def resolve_path(base, value):
    return (base / value).resolve()


def toml_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(toml_value(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(k) + "=" + toml_value(v) for k, v in value.items()) + "}"
    raise ValueError(f"Unsupported TOML configuration value: {type(value).__name__}")


class CodexSession:
    def __init__(self, cwd, output, config):
        args = ["codex", "app-server", "--listen", "stdio://"]
        for key, value in config.items():
            args.extend(["-c", key + "=" + toml_value(value)])
        self.events = queue.Queue()
        self.next_id = 0
        self.journal = (output / "protocol.jsonl").open("w")
        self.stderr = (output / "runtime.log").open("w")
        try:
            self.process = subprocess.Popen(args, cwd=cwd, stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=self.stderr,
                                            text=True, bufsize=1)
        except OSError:
            self.journal.close()
            self.stderr.close()
            raise
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        for line in self.process.stdout:
            try:
                self.events.put(json.loads(line))
            except json.JSONDecodeError:
                self.events.put({"unparsed_stdout": line})
        self.events.put({"process_eof": True})

    def send(self, value):
        self.journal.write(json.dumps({"direction": "sent", "message": value}, ensure_ascii=False) + "\n")
        self.journal.flush()
        self.process.stdin.write(json.dumps(value) + "\n")
        self.process.stdin.flush()

    def receive(self, timeout=30):
        value = self.events.get(timeout=timeout)
        self.journal.write(json.dumps({"direction": "received", "message": value}, ensure_ascii=False) + "\n")
        self.journal.flush()
        if value.get("process_eof"):
            raise EvaluationBlocked("Codex process ended before completing the request")
        if "method" in value and "id" in value:
            raise EvaluationBlocked("Runtime requested input: " + value["method"])
        return value

    def request(self, method, params, timeout=30):
        self.next_id += 1
        request_id = self.next_id
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Runtime request timed out: " + method)
            value = self.receive(timeout=remaining)
            if value.get("id") == request_id:
                if "error" in value:
                    raise EvaluationBlocked(json.dumps(value["error"], ensure_ascii=False))
                return value["result"]

    def initialize(self):
        self.request("initialize", {"clientInfo": {"name": "skill_evaluation", "version": "1.0"},
                                    "capabilities": {"experimentalApi": True}})
        self.send({"method": "initialized", "params": {}})

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.reader.join(timeout=2)
        self.journal.close()
        self.stderr.close()
        self.process.stdin.close()
        self.process.stdout.close()


def run_turn(session, case, workspace, result, output, timeout):
    started = session.request("thread/start", {"cwd": str(workspace), "ephemeral": True,
                              "approvalPolicy": "never", "sandbox": case.get("sandbox", "read-only")})
    thread = started["thread"]
    result["runtime"] = {k: thread.get(k) for k in ("cliVersion", "model", "modelProvider", "reasoningEffort", "ephemeral")}
    result["thread_id"] = thread["id"]
    turn_started = session.request("turn/start", {"threadId": thread["id"],
                    "input": [{"type": "text", "text": case["prompt"]}]})
    target_turn = turn_started["turn"]["id"]
    result["turn_id"] = target_turn
    deadline = time.monotonic() + timeout
    items = {}
    messages = []
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Turn deadline exceeded")
        try:
            event = session.receive(timeout=min(remaining, 30))
        except queue.Empty:
            continue
        method, params = event.get("method"), event.get("params", {})
        # app-server also emits child-agent events; only the requested turn
        # can supply this run's answer, token record, or completion evidence.
        if params.get("threadId") != thread["id"]:
            continue
        event_turn = params.get("turn", {}).get("id") if method == "turn/completed" else params.get("turnId")
        if event_turn != target_turn:
            continue
        if method == "item/completed":
            item = params["item"]
            items[item["id"]] = item
            if item["type"] == "agentMessage":
                messages.append(item.get("text", ""))
            write_json(output / "items.json", list(items.values()))
            (output / "response.md").write_text("\n\n".join(messages))
        elif method == "thread/tokenUsage/updated":
            result["token_usage"] = params.get("tokenUsage")
        elif method == "turn/completed":
            result["status"] = params["turn"]["status"]
            result["turn_error"] = params["turn"].get("error")
            result["item_count"] = len(items)
            result["agent_message_count"] = len(messages)
            return
