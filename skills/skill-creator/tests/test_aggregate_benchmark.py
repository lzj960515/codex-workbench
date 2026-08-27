import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "aggregate_benchmark.py"


class AggregateBenchmarkTest(unittest.TestCase):
    def write_metadata(
        self,
        root: Path,
        eval_id: int = 1,
        eval_name: str = "Queue inspection",
    ) -> None:
        eval_dir = root / "eval-1"
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / "eval_metadata.json").write_text(
            json.dumps(
                {
                    "eval_id": eval_id,
                    "eval_name": eval_name,
                    "prompt": "Inspect the queue.",
                }
            )
        )

    def write_run(
        self,
        root: Path,
        config: str,
        pass_rate: float,
        run_number: int = 1,
        grading: dict | None = None,
    ) -> None:
        run_dir = root / "eval-1" / config / f"run-{run_number}"
        run_dir.mkdir(parents=True)
        (run_dir / "outputs").mkdir()
        (run_dir / "grading.json").write_text(
            json.dumps(
                grading
                or {
                    "summary": {
                        "pass_rate": pass_rate,
                        "passed": int(pass_rate == 1),
                        "failed": int(pass_rate != 1),
                        "total": 1,
                    },
                    "expectations": [],
                }
            )
        )

    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_standard_skill_comparison_uses_primary_minus_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_metadata(root)
            self.write_run(root, "with_skill", 1.0)
            self.write_run(root, "without_skill", 0.25)

            result = self.run_script(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            benchmark = json.loads((root / "benchmark.json").read_text())
            self.assertEqual(
                benchmark["metadata"]["primary_configuration"], "with_skill"
            )
            self.assertEqual(
                benchmark["metadata"]["baseline_configuration"], "without_skill"
            )
            self.assertEqual(benchmark["metadata"]["runs_per_configuration"], 1)
            self.assertEqual(benchmark["runs"][0]["eval_name"], "Queue inspection")
            self.assertEqual(benchmark["run_summary"]["delta"]["pass_rate"], "+0.75")
            self.assertEqual(
                list(benchmark["run_summary"])[:2],
                ["with_skill", "without_skill"],
            )

    def test_custom_comparison_requires_explicit_roles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_run(root, "candidate", 0.75)
            self.write_run(root, "control", 0.5)

            ambiguous = self.run_script(root)
            explicit = self.run_script(
                root,
                "--primary-config",
                "candidate",
                "--baseline-config",
                "control",
            )

            self.assertEqual(ambiguous.returncode, 2)
            self.assertIn("Cannot infer comparison roles", ambiguous.stderr)
            self.assertEqual(explicit.returncode, 0, explicit.stderr)
            benchmark = json.loads((root / "benchmark.json").read_text())
            self.assertEqual(benchmark["run_summary"]["delta"]["pass_rate"], "+0.25")

    def test_existing_skill_comparison_recognizes_new_and_old_roles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_run(root, "new_skill", 0.8)
            self.write_run(root, "old_skill", 0.9)

            result = self.run_script(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            benchmark = json.loads((root / "benchmark.json").read_text())
            self.assertEqual(
                benchmark["metadata"]["primary_configuration"], "new_skill"
            )
            self.assertEqual(
                benchmark["metadata"]["baseline_configuration"], "old_skill"
            )
            self.assertEqual(benchmark["run_summary"]["delta"]["pass_rate"], "-0.10")

    def test_run_count_uses_loaded_runs_instead_of_largest_number(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for config in ("with_skill", "without_skill"):
                self.write_run(root, config, 1.0, run_number=1)
                self.write_run(root, config, 1.0, run_number=3)

            result = self.run_script(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            benchmark = json.loads((root / "benchmark.json").read_text())
            self.assertEqual(benchmark["metadata"]["runs_per_configuration"], 2)

    def test_unbalanced_run_counts_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_run(root, "with_skill", 1.0, run_number=1)
            self.write_run(root, "with_skill", 1.0, run_number=2)
            self.write_run(root, "without_skill", 1.0, run_number=1)

            result = self.run_script(root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Inconsistent loaded run counts", result.stderr)

    def test_tokens_come_from_timing_instead_of_output_character_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            grading = {
                "summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1},
                "timing": {"total_duration_seconds": 5.0},
                "execution_metrics": {"output_chars": 9_999},
                "expectations": [],
            }
            for config in ("with_skill", "without_skill"):
                self.write_run(root, config, 1.0, grading=grading)
                timing_file = root / "eval-1" / config / "run-1" / "timing.json"
                timing_file.write_text(json.dumps({"total_tokens": 123}))

            result = self.run_script(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            benchmark = json.loads((root / "benchmark.json").read_text())
            self.assertTrue(all(run["result"]["tokens"] == 123 for run in benchmark["runs"]))

    def test_missing_expectation_evidence_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            grading = {
                "summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1},
                "expectations": [{"text": "The result exists", "passed": True}],
            }
            for config in ("with_skill", "without_skill"):
                self.write_run(root, config, 1.0, grading=grading)

            result = self.run_script(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("missing required fields (text, passed, evidence)", result.stdout)


if __name__ == "__main__":
    unittest.main()
