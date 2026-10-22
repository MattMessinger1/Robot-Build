"""Run the original example from the project steps page in isolation."""

import csv
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class StepsPageExampleTests(unittest.TestCase):
    def test_original_example_and_saved_event_evidence(self):
        root = Path(__file__).resolve().parents[1]
        example = root / "examples" / "steps-page-heartbeat-demo.py"
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(example)], cwd=directory,
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("normal: 10/10 passed", result.stdout)
            self.assertIn("dropout: 10/10 passed", result.stdout)

            logs = list(Path(directory).glob("heartbeat-events-*.csv"))
            self.assertEqual(len(logs), 1)
            filename = logs[0].name
            self.assertRegex(filename, r"^heartbeat-events-\d{8}T\d{12}Z\.csv$")
            datetime.strptime(filename.removeprefix("heartbeat-events-").removesuffix(".csv"),
                              "%Y%m%dT%H%M%S%fZ")
            self.assertIn(f"Event log: {filename}", result.stdout)
            with logs[0].open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, ["trial", "case", "time_ms", "event", "detail"])
                rows = list(reader)

        for case in ("normal", "dropout"):
            for trial in range(1, 11):
                with self.subTest(case=case, trial=trial):
                    events = [row for row in rows
                              if row["case"] == case and row["trial"] == str(trial)]
                    self.assertTrue(events)
                    samples = [row for row in events if row["event"] == "sample"]
                    self.assertEqual(len(samples), 100 if case == "normal" else 90)
                    if case == "normal":
                        self.assertFalse(any(row["event"] == "request_on" for row in events))
                        continue

                    def event(name):
                        matches = [row for row in events if row["event"] == name]
                        self.assertEqual(len(matches), 1, name)
                        return matches[0]

                    self.assertEqual(event("dropout_start")["time_ms"], "5000")
                    self.assertEqual(event("request_on")["time_ms"], "5400")
                    self.assertEqual(event("reset_refused")["time_ms"], "5700")
                    self.assertEqual(event("dropout_end")["time_ms"], "6000")
                    self.assertTrue(any(row["time_ms"] == "6000" for row in samples))
                    resumed = event("request_after_resume")
                    self.assertEqual((resumed["time_ms"], resumed["detail"]), ("6100", "on"))
                    reset = event("reset_accepted")
                    self.assertEqual((reset["time_ms"], reset["detail"]), ("6200", "request_off"))


if __name__ == "__main__":
    unittest.main()
