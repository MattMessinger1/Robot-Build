import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from heartbeat_demo import HeartbeatMonitor, run_case


class HeartbeatMonitorTests(unittest.TestCase):
    def test_dropout_latches_until_recovery_and_manual_reset(self):
        monitor = HeartbeatMonitor(2)
        self.assertFalse(monitor.advance(0, reading=True).warning)
        self.assertFalse(monitor.advance(1.9).warning)
        early_reset = monitor.advance(2, reset=True)
        self.assertTrue(early_reset.warning)
        self.assertFalse(early_reset.reset_accepted)
        self.assertTrue(monitor.advance(2.1, reading=True).warning)
        self.assertTrue(monitor.advance(2.2).warning)
        recovered = monitor.advance(2.3, reset=True)
        self.assertTrue(recovered.reset_accepted)
        self.assertFalse(recovered.warning)

    def test_late_reading_does_not_hide_timeout(self):
        monitor = HeartbeatMonitor(1)
        monitor.advance(0, reading=True)
        self.assertTrue(monitor.advance(1, reading=True).warning)
        self.assertFalse(monitor.advance(1.1, reset=True).warning)

    def test_reset_requires_fresh_reading(self):
        monitor = HeartbeatMonitor(1)
        self.assertFalse(monitor.advance(1, reset=True).reset_accepted)
        self.assertTrue(monitor.advance(2, reading=True).warning)
        self.assertFalse(monitor.advance(3, reset=True).reset_accepted)
        self.assertTrue(monitor.warning)

    def test_invalid_times_and_timeout_are_rejected(self):
        for timeout in (0, -1, float("nan"), float("inf")):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                HeartbeatMonitor(timeout)
        monitor = HeartbeatMonitor(1)
        monitor.advance(1, reading=True)
        for moment in (0, float("nan"), float("inf")):
            with self.subTest(moment=moment), self.assertRaises(ValueError):
                monitor.advance(moment)

    def test_twenty_simulated_cases_match_expected_trace(self):
        for scenario in ("normal", "dropout"):
            for case in range(1, 11):
                with self.subTest(scenario=scenario, case=case):
                    self.assertTrue(all(row["check_passed"] for row in run_case(scenario, case)))

    def test_cli_writes_trace_and_reports_counts(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(root / "heartbeat_demo.py"), "--output-dir", directory],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("normal: 10/10 passed", result.stdout)
            self.assertIn("dropout: 10/10 passed", result.stdout)
            self.assertIn("reset=refused", result.stdout)
            self.assertIn("reset=accepted", result.stdout)
            logs = list(Path(directory).glob("heartbeat_demo_*.csv"))
            self.assertEqual(len(logs), 1)
            with logs[0].open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 120)
            self.assertEqual({(row["scenario"], row["case"]) for row in rows},
                             {(scenario, str(case)) for scenario in ("normal", "dropout")
                              for case in range(1, 11)})
            self.assertTrue(all(row["check_passed"] == "True" for row in rows))


if __name__ == "__main__":
    unittest.main()
