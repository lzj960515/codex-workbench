import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]
VIEWER_SCRIPT = SKILL_ROOT / "eval-viewer" / "generate_review.py"


def load_viewer_module():
    spec = importlib.util.spec_from_file_location("generate_review", VIEWER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvaluationContractTest(unittest.TestCase):
    def test_viewer_reads_metadata_from_eval_root(self) -> None:
        viewer = load_viewer_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            eval_dir = root / "eval-normal-release"
            run_dir = eval_dir / "new_skill" / "run-1"
            (run_dir / "outputs").mkdir(parents=True)
            (eval_dir / "eval_metadata.json").write_text(
                json.dumps(
                    {
                        "eval_id": 7,
                        "eval_name": "Normal release",
                        "prompt": "Release the project.",
                    }
                )
            )

            run = viewer.build_run(root, run_dir)

            self.assertEqual(run["eval_id"], 7)
            self.assertEqual(run["eval_name"], "Normal release")
            self.assertEqual(run["prompt"], "Release the project.")

    def test_advanced_reference_uses_the_schema_expectations_field(self) -> None:
        references = [
            (SKILL_ROOT / "references" / "advanced-evaluation.md").read_text(),
            (SKILL_ROOT / "references" / "schemas.md").read_text(),
        ]

        for reference in references:
            self.assertIn('"expectations"', reference)
            self.assertIsNone(re.search(r'"assertions"\s*:', reference))


if __name__ == "__main__":
    unittest.main()
