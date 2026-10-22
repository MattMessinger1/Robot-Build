# Robot Build: an independent safety experiment

This project starts with an unpowered, printed forearm and hand moved by hand. An MPU-6050 sensor will record its movement so we can compare an estimated tilt with a separate angle reference. The eventual idea is a device that can detect a defined problem and ask a humanoid robot to stop; how it would get data and connect to a robot is still unknown.

The current software runs on a computer without a sensor or robot. It provides a missing-data simulation and an offline comparison of recorded angles. A warning or simulated stop request is a test signal: it does not stop a robot or demonstrate that a physical system is safe.

## Getting started

Python 3.10 or newer is required. The current programs use only the Python standard library; there are no packages to install.

From the repository directory, run the missing-data demonstration and the tests:

```sh
python3 heartbeat_demo.py
python3 -m unittest discover -s tests -v
```

The heartbeat demonstration uses simulated readings and simulated time. It exercises warning and reset behavior and saves a dated CSV log; it does not check real-world timing, hardware, or a robot connection.

The original copy-and-run example from the [project steps page](https://independent-robot-safety.matt-messinger.chatgpt.site/steps) is also saved as `examples/steps-page-heartbeat-demo.py`. It writes its dated CSV in the current directory. Both examples are simulations, not earlier test results. Logs in `logs/` stay local and are not included in Git; preserve any evidence you want to share separately.

To compare recorded angles, prepare a CSV with unique `sample_id`, `reference_angle_deg`, and `sensor_angle_deg` columns. Additional columns, such as run and photo references, can be included. Use a new output filename:

```sh
python3 compare_readings.py readings.csv --output analysis.csv
```

To try the comparison before real readings exist, use the clearly labeled synthetic data:

```sh
python3 compare_readings.py examples/synthetic-readings.csv --output sample-analysis.csv --inject example-40
```

The output file must be new; choose another filename for each run. The original CSV is not changed.

To test a known error without changing the input, add `--inject SAMPLE_ID` for each selected sample. The tool adds 10° to those readings in its output copy and marks them as injected. It reports differences over 5° and sensor readings over 45°, comparing the latter with the independent reference. These values are experiment settings, not safety limits.

See [the experiment plan](docs/experiment-plan.md), [inventory checklist](docs/inventory.md), and [evidence guide](evidence/README.md) for the repeatable bench procedure, materials, and evidence to collect. No physical measurements, prior test logs, or working robot connection are included in this repository yet.
