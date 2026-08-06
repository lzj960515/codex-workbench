#!/usr/bin/python3

import hashlib
import json
import mmap
import os
import sys
from pathlib import Path
from typing import Iterator, Optional, Tuple


HANDOFF_THRESHOLD_PERCENT = 70
HANDOFF_REMINDER = (
    "上下文使用率已达到 70%。继续工作前，按照 AGENTS.md 的“长任务状态交接”"
    "创建或更新目标项目 tmp/ 中当前任务的状态文件。"
)


def read_records_in_reverse(transcript_path: Path) -> Iterator[Tuple[int, dict]]:
    with transcript_path.open("rb") as transcript:
        if transcript.seek(0, 2) == 0:
            return

        with mmap.mmap(transcript.fileno(), 0, access=mmap.ACCESS_READ) as records:
            end = len(records)
            while end > 0:
                if records[end - 1] == ord("\n"):
                    end -= 1
                    continue

                start = records.rfind(b"\n", 0, end) + 1
                yield start, json.loads(records[start:end])
                end = start


def usage_percent(usage: dict) -> float:
    used_tokens = usage["last_token_usage"]["total_tokens"]
    return used_tokens / usage["model_context_window"] * 100


def is_handoff_reminder(record: dict) -> bool:
    if record.get("type") != "response_item":
        return False

    payload = record.get("payload", {})
    if payload.get("type") != "message" or payload.get("role") != "developer":
        return False

    return any(
        item.get("type") == "input_text"
        and item.get("text") == HANDOFF_REMINDER
        for item in payload.get("content", [])
    )


def is_user_message(record: dict) -> bool:
    if record.get("type") != "response_item":
        return False

    payload = record.get("payload", {})
    return payload.get("type") == "message" and payload.get("role") == "user"


def user_turn_key(transcript_path: Path, record_position: int) -> str:
    identity = f"{transcript_path.resolve()}:{record_position}"
    return hashlib.sha256(identity.encode()).hexdigest()


def read_handoff_state(
    transcript_path: Path,
) -> Tuple[Optional[dict], bool, Optional[str]]:
    latest_usage = None
    new_user_message_seen = False
    current_user_turn = None

    for record_position, record in read_records_in_reverse(transcript_path):
        payload = record.get("payload", {})

        if is_user_message(record):
            current_user_turn = current_user_turn or user_turn_key(
                transcript_path, record_position
            )
            if latest_usage:
                return latest_usage, False, current_user_turn
            new_user_message_seen = True
            continue

        if latest_usage and is_handoff_reminder(record):
            return latest_usage, True, current_user_turn

        if payload.get("type") != "token_count":
            continue

        usage = payload.get("info")
        if latest_usage is None:
            latest_usage = usage
            if usage_percent(usage) < HANDOFF_THRESHOLD_PERCENT:
                return latest_usage, False, current_user_turn
            if new_user_message_seen:
                return latest_usage, False, current_user_turn
            continue

        if usage_percent(usage) < HANDOFF_THRESHOLD_PERCENT:
            return latest_usage, False, current_user_turn

    return latest_usage, False, current_user_turn


def claim_handoff_reminder(user_turn: str) -> bool:
    state_directory = Path(
        os.environ.get(
            "TASK_HANDOFF_STATE_DIRECTORY",
            Path(__file__).with_name(".task_handoff_state"),
        )
    )
    state_directory.mkdir(parents=True, exist_ok=True)
    state_path = state_directory / user_turn
    try:
        descriptor = os.open(state_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False
    os.close(descriptor)
    return True


def emit_additional_context(event_name: str, context: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        )
    )


hook_input = json.load(sys.stdin)
event_name = hook_input["hook_event_name"]

if event_name == "SessionStart" and hook_input.get("source") == "compact":
    emit_additional_context(
        event_name,
        "上下文刚完成压缩。继续工作前，按照 AGENTS.md 的“长任务状态交接”先读取目标项目 tmp/ 中当前任务的状态文件，并结合当前 Git 状态和差异恢复完整任务上下文。",
    )

if event_name in {"UserPromptSubmit", "PostToolUse"}:
    transcript_value = hook_input.get("transcript_path")
    usage, handoff_reminded, current_user_turn = (
        read_handoff_state(Path(transcript_value))
        if transcript_value and Path(transcript_value).is_file()
        else (None, False, None)
    )

    if (
        usage
        and usage_percent(usage) >= HANDOFF_THRESHOLD_PERCENT
        and not handoff_reminded
        and current_user_turn
        and claim_handoff_reminder(current_user_turn)
    ):
        emit_additional_context(event_name, HANDOFF_REMINDER)
