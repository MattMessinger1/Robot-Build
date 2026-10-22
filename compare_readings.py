#!/usr/bin/env python3
"""Compare logged sensor angles with independent, manually recorded angles.

This is an offline bench experiment. It is not a safety system and does not
send a stop request to a robot.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = ("sample_id", "reference_angle_deg", "sensor_angle_deg")
RESULT_COLUMNS = (
    "original_sensor_angle_deg",
    "injected",
    "difference_deg",
    "difference_warning",
    "sensor_above_45",
    "reference_above_45",
    "angle_warning_outcome",
)


def number(value: str, field: str, line: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"line {line}: {field} must be a number") from exc
    if not math.isfinite(result):
        raise ValueError(f"line {line}: {field} must be finite")
    return result


def read_samples(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        fields = reader.fieldnames
        if not fields or any(not field for field in fields):
            raise ValueError("CSV must have a header with named columns")
        if len(set(fields)) != len(fields):
            raise ValueError("CSV contains duplicate column names")
        missing = set(REQUIRED_COLUMNS) - set(fields)
        if missing:
            raise ValueError("missing required columns: " + ", ".join(sorted(missing)))
        conflicts = set(RESULT_COLUMNS) & set(fields)
        if conflicts:
            raise ValueError("input already contains output columns: " + ", ".join(sorted(conflicts)))

        samples: list[dict[str, str]] = []
        seen: set[str] = set()
        for row in reader:
            line = reader.line_num
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"line {line}: CSV row does not match the header")
            sample_id = row["sample_id"].strip()
            if not sample_id:
                raise ValueError(f"line {line}: sample_id must not be empty")
            if sample_id in seen:
                raise ValueError(f"line {line}: duplicate sample_id {sample_id!r}")
            seen.add(sample_id)
            row["sample_id"] = sample_id
            number(row["reference_angle_deg"], "reference_angle_deg", line)
            number(row["sensor_angle_deg"], "sensor_angle_deg", line)
            samples.append(row)
        if not samples:
            raise ValueError("CSV contains no data rows")
        return fields, samples


def analyze(samples: list[dict[str, str]], injections: set[str]) -> tuple[list[dict[str, str]], Counter]:
    ids = {row["sample_id"] for row in samples}
    unknown = injections - ids
    if unknown:
        raise ValueError("unknown sample_id for injection: " + ", ".join(sorted(unknown)))

    counts: Counter = Counter()
    results: list[dict[str, str]] = []
    for row in samples:
        reference = float(row["reference_angle_deg"])
        original = float(row["sensor_angle_deg"])
        injected = row["sample_id"] in injections
        sensor = original + (10.0 if injected else 0.0)
        difference = abs(sensor - reference)
        if not math.isfinite(sensor) or not math.isfinite(difference):
            raise ValueError(f"sample {row['sample_id']!r}: arithmetic produced a nonfinite value")
        difference_warning = difference > 5.0
        sensor_warning = sensor > 45.0
        reference_warning = reference > 45.0
        if sensor_warning and reference_warning:
            outcome = "true_positive"
        elif sensor_warning:
            outcome = "false_positive"
        elif reference_warning:
            outcome = "false_negative"
        else:
            outcome = "true_negative"

        counts[outcome] += 1
        counts["difference_warnings"] += difference_warning
        counts["sensor_warnings"] += sensor_warning
        counts["injected"] += injected
        counts["injected_without_difference_warning"] += injected and not difference_warning
        result = dict(row)
        # Keep the original textual reading, and put any simulated change only in
        # this new result row. Additional input columns are preserved for tracing.
        result["original_sensor_angle_deg"] = row["sensor_angle_deg"]
        result["sensor_angle_deg"] = repr(sensor) if injected else row["sensor_angle_deg"]
        result["injected"] = str(injected).lower()
        result["difference_deg"] = repr(difference)
        result["difference_warning"] = str(difference_warning).lower()
        result["sensor_above_45"] = str(sensor_warning).lower()
        result["reference_above_45"] = str(reference_warning).lower()
        result["angle_warning_outcome"] = outcome
        results.append(result)
    return results, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV with sample_id, reference_angle_deg and sensor_angle_deg")
    parser.add_argument("--output", type=Path, required=True, help="new output CSV; existing files are never overwritten")
    parser.add_argument("--inject", action="append", default=[], metavar="SAMPLE_ID", help="add 10 degrees to this sample in the output copy; repeat for more samples")
    args = parser.parse_args(argv)

    try:
        fields, samples = read_samples(args.input)
        results, counts = analyze(samples, set(args.inject))
        with args.output.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields + list(RESULT_COLUMNS))
            writer.writeheader()
            writer.writerows(results)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Experimental offline comparison only; this does not stop a robot.")
    print(f"Samples: {len(results)}")
    print(f"Differences over 5 degrees: {counts['difference_warnings']}")
    print(f"Sensor readings over 45 degrees: {counts['sensor_warnings']}")
    print("Threshold comparisons treat entered angles as exact; consider measurement uncertainty.")
    print("For the >45 degree warning, using the independent reference >45 degrees as the comparison:")
    print(f"  true positives: {counts['true_positive']}; false positives: {counts['false_positive']}; "
          f"false negatives (missed): {counts['false_negative']}; true negatives: {counts['true_negative']}")
    print(f"Injected +10-degree copies: {counts['injected']}; injected copies without a >5-degree difference warning: "
          f"{counts['injected_without_difference_warning']}")
    print("An injection label is not an independent fault label; difference-warning misses and false alarms require separately recorded labels.")
    print(f"Results saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
