#!/usr/bin/env python3
"""Simulate missing sensor readings; this does not control a real robot.

Times below are simulated, not wall-clock measurements. A missing-reading
warning stays on until a new reading arrives and a reset is requested.
Neither the timeout nor a successful simulation is a safety claim.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
import sys


@dataclass(frozen=True)
class State:
    warning: bool
    reset_accepted: bool


class HeartbeatMonitor:
    """A small, simulated, latched missing-reading indicator."""

    def __init__(self, timeout_seconds: float):
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")
        self.timeout_seconds = timeout_seconds
        self._now = 0.0
        self._last_reading: float | None = None
        self.warning = False

    def advance(self, now: float, *, reading: bool = False, reset: bool = False) -> State:
        """Advance simulated time, optionally receiving a reading or reset.

        A late reading cannot erase the fact that a timeout occurred. A reset
        is accepted only after a fresh reading and while a warning is latched.
        """
        if not math.isfinite(now) or now < self._now:
            raise ValueError("simulated time must be finite and nondecreasing")
        self._now = now
        reference = self._last_reading if self._last_reading is not None else 0.0
        if now - reference >= self.timeout_seconds:
            self.warning = True
        if reading:
            self._last_reading = now

        reset_accepted = bool(
            reset
            and self.warning
            and self._last_reading is not None
            and now - self._last_reading < self.timeout_seconds
        )
        if reset_accepted:
            self.warning = False
        return State(warning=self.warning, reset_accepted=reset_accepted)


@dataclass(frozen=True)
class Step:
    time_seconds: float
    action: str
    reading: bool
    reset: bool
    expected_warning: bool
    expected_reset: bool = False


def run_case(scenario: str, case_number: int) -> list[dict[str, object]]:
    """Run one of ten varied-timeout examples and return its checked trace."""
    if scenario not in ("normal", "dropout") or not 1 <= case_number <= 10:
        raise ValueError("unknown scenario or case")
    timeout = float(case_number)
    monitor = HeartbeatMonitor(timeout)
    if scenario == "normal":
        steps = [
            Step(0.0, "reading", True, False, False),
            Step(timeout * 0.25, "reading", True, False, False),
            Step(timeout * 0.75, "reading", True, False, False),
            Step(timeout * 1.25, "reading", True, False, False),
            Step(timeout * 1.50, "wait", False, False, False),
        ]
    else:
        steps = [
            Step(0.0, "reading", True, False, False),
            Step(timeout * 0.5, "wait", False, False, False),
            Step(timeout, "early reset", False, True, True),
            Step(timeout * 1.1, "reading returns", True, False, True),
            Step(timeout * 1.2, "wait", False, False, True),
            Step(timeout * 1.3, "manual reset", False, True, False, True),
            Step(timeout * 1.4, "wait", False, False, False),
        ]
    rows = []
    for step in steps:
        actual = monitor.advance(step.time_seconds, reading=step.reading, reset=step.reset)
        passed = (actual.warning == step.expected_warning
                  and actual.reset_accepted == step.expected_reset)
        rows.append({
            "scenario": scenario,
            "case": case_number,
            "timeout_seconds": timeout,
            "simulated_time_seconds": step.time_seconds,
            "action": step.action,
            "warning_latched": actual.warning,
            "reset_accepted": actual.reset_accepted,
            "expected_warning_latched": step.expected_warning,
            "expected_reset_accepted": step.expected_reset,
            "check_passed": passed,
        })
    return rows


def run_demo(output_dir: Path) -> tuple[dict[str, int], Path]:
    """Save checked simulated traces and return counts of passing cases."""
    counts = {"normal": 0, "dropout": 0}
    all_rows = []
    for scenario in counts:
        for case_number in range(1, 11):
            rows = run_case(scenario, case_number)
            counts[scenario] += int(all(row["check_passed"] for row in rows))
            all_rows.extend(rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output_path = output_dir / f"heartbeat_demo_{stamp}.csv"
    with output_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    return counts, output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("logs"),
                        help="directory for the dated CSV trace (default: logs)")
    args = parser.parse_args(argv)
    try:
        counts, output_path = run_demo(args.output_dir)
    except OSError as error:
        print(f"Could not save the CSV log: {error}", file=sys.stderr)
        return 1
    print("Simulation only; this does not measure real timing or stop a robot.")
    print("Example dropout trace:")
    for row in run_case("dropout", 1):
        if row["action"] in ("early reset", "reading returns", "manual reset"):
            reset = ("accepted" if row["reset_accepted"] else "refused") if "reset" in row["action"] else "not requested"
            print(f"  t={row['simulated_time_seconds']:.1f}s {row['action']}: "
                  f"warning={'ON' if row['warning_latched'] else 'off'}, reset={reset}")
    for scenario, count in counts.items():
        print(f"{scenario}: {count}/10 passed")
    print(f"CSV log: {output_path}")
    return 0 if all(count == 10 for count in counts.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
