import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HOOK_PATH = Path(__file__).with_name("task_handoff.py")
HANDOFF_REMINDER = (
    "上下文使用率已达到 80%。继续工作前，按照 AGENTS.md 的“长任务状态交接”"
    "创建或更新目标项目 tmp/ 中当前任务的状态文件。"
)


def token_count(used_tokens: int) -> dict:
    return {
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {
                "last_token_usage": {"total_tokens": used_tokens},
                "model_context_window": 100,
            },
        },
    }


def user_message(text: str) -> dict:
    return {
        "type": "response_item",
        "payload": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": text}],
        },
    }


def handoff_reminder() -> dict:
    return {
        "type": "response_item",
        "payload": {
            "type": "message",
            "role": "developer",
            "content": [{"type": "input_text", "text": HANDOFF_REMINDER}],
        },
    }


def hook_environment(state_directory: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment["TASK_HANDOFF_STATE_DIRECTORY"] = str(state_directory)
    return environment


def run_hook(records: list[dict], event_name: str = "UserPromptSubmit") -> str:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        transcript_path = root / "transcript.jsonl"
        transcript_path.write_text(
            "".join(f"{json.dumps(record, ensure_ascii=False)}\n" for record in records),
            encoding="utf-8",
        )
        hook_input = {
            "hook_event_name": event_name,
            "transcript_path": str(transcript_path),
        }
        result = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            check=True,
            env=hook_environment(root / "state"),
        )
        return result.stdout


class TaskHandoffHookTest(unittest.TestCase):
    def test_below_threshold_remains_silent(self) -> None:
        output = run_hook([token_count(79), user_message("继续当前任务")])

        self.assertEqual("", output)

    def test_high_usage_without_reminder_emits_handoff(self) -> None:
        output = run_hook([token_count(80), user_message("继续当前任务")])

        self.assertIn(HANDOFF_REMINDER, output)

    def test_new_user_message_resets_previous_handoff_reminder(self) -> None:
        output = run_hook(
            [
                token_count(85),
                handoff_reminder(),
                token_count(90),
                user_message("开始处理另一个任务"),
            ]
        )

        self.assertIn(HANDOFF_REMINDER, output)

    def test_same_user_message_is_only_reminded_once(self) -> None:
        output = run_hook(
            [
                token_count(85),
                user_message("开始处理另一个任务"),
                handoff_reminder(),
                token_count(90),
            ],
            event_name="PostToolUse",
        )

        self.assertEqual("", output)

    def test_old_reminder_remains_valid_until_next_user_message(self) -> None:
        output = run_hook(
            [token_count(85), handoff_reminder(), token_count(90)],
            event_name="PostToolUse",
        )

        self.assertEqual("", output)

    def test_post_tool_use_honors_new_user_message_after_old_reminder(self) -> None:
        output = run_hook(
            [
                token_count(85),
                handoff_reminder(),
                user_message("开始处理另一个任务"),
                token_count(90),
            ],
            event_name="PostToolUse",
        )

        self.assertIn(HANDOFF_REMINDER, output)

    def test_parallel_callbacks_emit_one_reminder_for_the_same_user_turn(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transcript_path = root / "transcript.jsonl"
            transcript_path.write_text(
                "".join(
                    f"{json.dumps(record, ensure_ascii=False)}\n"
                    for record in [token_count(85), user_message("继续当前任务")]
                ),
                encoding="utf-8",
            )
            hook_input = json.dumps(
                {
                    "hook_event_name": "PostToolUse",
                    "transcript_path": str(transcript_path),
                }
            )
            processes = [
                subprocess.Popen(
                    [sys.executable, str(HOOK_PATH)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=hook_environment(root / "state"),
                )
                for _ in range(4)
            ]

            outputs = [process.communicate(hook_input, timeout=5)[0] for process in processes]

            self.assertTrue(all(process.returncode == 0 for process in processes))
            self.assertEqual(1, sum(HANDOFF_REMINDER in output for output in outputs))


if __name__ == "__main__":
    unittest.main()
