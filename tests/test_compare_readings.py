"""Behavioral tests for the offline, experimental angle comparison CLI."""

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "compare_readings.py"


class CompareReadingsTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "comparison script must exist")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.input = self.directory / "input.csv"
        self.output = self.directory / "output.csv"

    def run_cli(self, *extra, output=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.input), "--output",
             str(output or self.output), *extra],
            text=True, capture_output=True, check=False,
        )

    def write_input(self, rows, fieldnames=None):
        if fieldnames is None:
            fieldnames = ["sample_id", "reference_angle_deg", "sensor_angle_deg", "photo"]
        with self.input.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def read_output(self):
        with self.output.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_independent_thresholds_and_labeled_injection_leave_input_unchanged(self):
        self.write_input([
            {"sample_id": "boundary", "reference_angle_deg": "45", "sensor_angle_deg": "45", "photo": "one.jpg"},
            {"sample_id": "false_alarm", "reference_angle_deg": "44", "sensor_angle_deg": "50", "photo": "two.jpg"},
            {"sample_id": "missed", "reference_angle_deg": "50", "sensor_angle_deg": "44", "photo": "three.jpg"},
            {"sample_id": "true_alarm", "reference_angle_deg": "50", "sensor_angle_deg": "55", "photo": "four.jpg"},
            {"sample_id": "injected", "reference_angle_deg": "35", "sensor_angle_deg": "35", "photo": "five.jpg"},
        ])
        original_bytes = self.input.read_bytes()

        result = self.run_cli("--inject", "injected")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.input.read_bytes(), original_bytes)
        rows = {row["sample_id"]: row for row in self.read_output()}
        self.assertEqual(set(rows), {"boundary", "false_alarm", "missed", "true_alarm", "injected"})
        self.assertEqual(rows["boundary"]["sensor_above_45"], "false")
        self.assertEqual(rows["boundary"]["reference_above_45"], "false")
        self.assertEqual(rows["boundary"]["angle_warning_outcome"], "true_negative")
        self.assertEqual(rows["false_alarm"]["angle_warning_outcome"], "false_positive")
        self.assertEqual(rows["missed"]["angle_warning_outcome"], "false_negative")
        self.assertEqual(rows["true_alarm"]["angle_warning_outcome"], "true_positive")
        self.assertEqual(rows["true_alarm"]["difference_warning"], "false")  # exactly 5°
        self.assertEqual(rows["missed"]["difference_warning"], "true")
        self.assertEqual(rows["injected"]["injected"], "true")
        self.assertEqual(rows["boundary"]["injected"], "false")
        self.assertEqual(float(rows["injected"]["original_sensor_angle_deg"]), 35.0)
        self.assertEqual(float(rows["injected"]["sensor_angle_deg"]), 45.0)
        self.assertEqual(float(rows["injected"]["difference_deg"]), 10.0)
        self.assertEqual(rows["injected"]["difference_warning"], "true")
        self.assertEqual(rows["injected"]["photo"], "five.jpg")
        self.assertIn("Differences over 5 degrees: 3", result.stdout)
        self.assertIn("Sensor readings over 45 degrees: 2", result.stdout)
        self.assertIn("Injected +10-degree copies: 1", result.stdout)
        self.assertIn("true positives: 1", result.stdout)
        self.assertIn("false positives: 1", result.stdout)
        self.assertIn("false negatives (missed): 1", result.stdout)
        self.assertIn("true negatives: 2", result.stdout)

    def test_injected_change_can_cancel_existing_difference(self):
        self.write_input([{"sample_id": "a", "reference_angle_deg": "40", "sensor_angle_deg": "30", "photo": "p.jpg"}])
        result = self.run_cli("--inject", "a")
        self.assertEqual(result.returncode, 0, result.stderr)
        row, = self.read_output()
        self.assertEqual(row["injected"], "true")
        self.assertEqual(row["difference_warning"], "false")
        self.assertIn("injected copies without a >5-degree difference warning: 1", result.stdout)

    def test_bad_inputs_are_rejected_without_output_or_input_changes(self):
        cases = {
            "missing column": "sample_id,reference_angle_deg\na,10\n",
            "no rows": "sample_id,reference_angle_deg,sensor_angle_deg\n",
            "blank id": "sample_id,reference_angle_deg,sensor_angle_deg\n,10,11\n",
            "duplicate id": "sample_id,reference_angle_deg,sensor_angle_deg\na,10,11\na,20,21\n",
            "missing value": "sample_id,reference_angle_deg,sensor_angle_deg\na,10,\n",
            "invalid number": "sample_id,reference_angle_deg,sensor_angle_deg\na,10,nope\n",
            "nonfinite number": "sample_id,reference_angle_deg,sensor_angle_deg\na,10,nan\n",
            "extra column": "sample_id,reference_angle_deg,sensor_angle_deg\na,10,11,unexpected\n",
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                self.input.write_text(content, encoding="utf-8")
                result = self.run_cli()
                self.assertNotEqual(result.returncode, 0, name)
                self.assertFalse(self.output.exists(), name)
                self.assertEqual(self.input.read_text(encoding="utf-8"), content)

    def test_unknown_injection_and_existing_outputs_never_overwrite_data(self):
        self.write_input([{"sample_id": "a", "reference_angle_deg": "10", "sensor_angle_deg": "11", "photo": "p.jpg"}])
        original = self.input.read_bytes()
        unknown = self.run_cli("--inject", "not-present")
        self.assertNotEqual(unknown.returncode, 0)
        self.assertFalse(self.output.exists())

        self.output.write_text("previous results", encoding="utf-8")
        existing = self.run_cli()
        self.assertNotEqual(existing.returncode, 0)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous results")

        same_as_input = self.run_cli(output=self.input)
        self.assertNotEqual(same_as_input.returncode, 0)
        self.assertEqual(self.input.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
