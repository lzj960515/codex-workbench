from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CREATE_SCRIPT = SKILL_DIR / "scripts" / "create_mindmap.py"
INSPECT_SCRIPT = SKILL_DIR / "scripts" / "inspect_mindmap.py"
VALIDATE_SCRIPT = SKILL_DIR / "scripts" / "validate_mindmap.py"


class MindmapScriptTest(unittest.TestCase):
    def run_create(self, outline: dict, *extra_args: str) -> tuple[subprocess.CompletedProcess[str], Path, tempfile.TemporaryDirectory[str]]:
        temporary = tempfile.TemporaryDirectory()
        directory = Path(temporary.name)
        source = directory / "outline.json"
        output = directory / "topic.drawio"
        source.write_text(json.dumps(outline, ensure_ascii=False), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(CREATE_SCRIPT), str(source), str(output), *extra_args],
            capture_output=True,
            text=True,
            check=False,
        )
        return completed, output, temporary

    def test_creates_editable_bilateral_sketch(self) -> None:
        outline = {
            "title": "发布流程",
            "layout": "both",
            "branches": [
                {"text": "准备", "children": [{"text": "检查版本"}]},
                {"text": "验证", "children": [{"text": "运行测试"}]},
                {"text": "交付", "children": [{"text": "导出 PNG"}]},
                {"text": "复盘", "children": [{"text": "收集反馈"}]},
            ],
        }
        completed, output, temporary = self.run_create(outline)
        self.addCleanup(temporary.cleanup)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["node_count"], 9)
        self.assertEqual(summary["edge_count"], 8)
        self.assertEqual(summary["sides"], {"left": 2, "right": 2})

        xml = output.read_text(encoding="utf-8")
        self.assertIn("sketch=1", xml)
        self.assertIn("endArrow=none", xml)
        self.assertIn('mindmapRole="root"', xml)

        inspected = subprocess.run(
            [sys.executable, str(INSPECT_SCRIPT), str(output), "--format", "markdown"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertIn("# 发布流程", inspected.stdout)
        self.assertIn("  - 检查版本", inspected.stdout)

    def test_layout_override_places_all_branches_on_right(self) -> None:
        outline = {
            "title": "单向阅读",
            "layout": "both",
            "branches": [{"text": "一"}, {"text": "二"}, {"text": "三"}],
        }
        completed, output, temporary = self.run_create(outline, "--layout", "right")
        self.addCleanup(temporary.cleanup)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["sides"], {"left": 0, "right": 3})
        root = ET.fromstring(output.read_text(encoding="utf-8"))
        sides = {
            element.get("mindmapSide")
            for element in root.iter("object")
            if element.get("mindmapRole") == "topic"
        }
        self.assertEqual(sides, {"right"})

    def test_rejects_nested_branch_color(self) -> None:
        outline = {
            "title": "颜色归属",
            "branches": [
                {
                    "text": "主分支",
                    "color": "blue",
                    "children": [{"text": "子主题", "color": "red"}],
                }
            ],
        }
        completed, _, temporary = self.run_create(outline)
        self.addCleanup(temporary.cleanup)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("color is only supported on first-level branches", completed.stderr)

    def test_preserves_xml_sensitive_text(self) -> None:
        outline = {
            "title": "A & B",
            "branches": [{"text": "x < y", "children": [{"text": "T > 0"}]}],
        }
        completed, output, temporary = self.run_create(outline)
        self.addCleanup(temporary.cleanup)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        root = ET.fromstring(output.read_text(encoding="utf-8"))
        labels = [element.get("label") for element in root.iter("object")]
        self.assertEqual(labels, ["A & B", "x < y", "T > 0"])

    def test_validates_synchronized_source_and_png(self) -> None:
        source = SKILL_DIR / "assets" / "mindmap-sketch-template.drawio"
        png = SKILL_DIR / "assets" / "mindmap-sketch-template.png"
        completed = subprocess.run(
            [sys.executable, str(VALIDATE_SCRIPT), str(source), str(png)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertTrue(result["embedded_diagram"])
        self.assertTrue(result["source_matches_png"])

    def test_rejects_png_with_stale_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "topic.drawio"
            png = directory / "topic.png"
            template_source = SKILL_DIR / "assets" / "mindmap-sketch-template.drawio"
            template_png = SKILL_DIR / "assets" / "mindmap-sketch-template.png"
            shutil.copyfile(template_source, source)
            shutil.copyfile(template_png, png)
            source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(VALIDATE_SCRIPT), str(source), str(png)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("embedded source does not match", completed.stderr)


if __name__ == "__main__":
    unittest.main()
