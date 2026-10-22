# Robot Build: an independent safety experiment

Our first test uses a Raspberry Pi, a servo, a ruler, an MPU-6050 sensor, and a protractor. The servo will move the ruler. We will check the sensor's estimated angle against the protractor, then see whether software notices a difference between the sensor and a pretend robot reading.

The longer-term idea is an owner-controlled device that looks for a defined problem in robot data and asks the robot to stop. Access to the right data and a supported way to request a stop still need research. This is an experiment, not a robot safety system.

## Open the project

1. Open [Robot-Build on GitHub](https://github.com/MattMessinger1/Robot-Build). If you need permission to push, the owner can invite you under **Settings > Collaborators > Add people**. Accept the invitation when it arrives. The public repository can be viewed without an invitation.
2. If you already have a copy, open it. Otherwise, use **Code > Open with GitHub Desktop** and choose where to save it. In Codex, add a project and select that `Robot-Build` folder. If Codex clones it for you, approve the action and location first.
3. Before starting, check the branch and whether the folder has uncommitted changes. Preserve those changes, then pull the latest work. When your work is ready, review and commit it locally, then push it so others can get it. If Codex pulls or pushes for you, approve each action first.

Find the earlier motor code, setup notes, and original results on the device where they were saved. Preserve them and inspect how they work before adapting them. They are not included in this repository yet.

## What is here now

The current programs run on a computer without a sensor or robot. They provide a missing-data simulation and an offline comparison of recorded angles. They do not drive the servo or read the MPU-6050. No physical measurements, original earlier test logs, or working robot connection are included here yet.

Python 3.10 or newer is required. The programs use only the Python standard library; there are no packages to install. From the project folder, run the simulation and software tests:

```sh
python3 heartbeat_demo.py
python3 -m unittest discover -s tests -v
```

The heartbeat demonstration uses simulated readings and simulated time. It exercises warning and reset behavior and saves a dated CSV log; it does not check real-world timing, hardware, or a robot connection.

The original copy-and-run example from the [project steps page](https://independent-robot-safety.matt-messinger.chatgpt.site/steps) is also saved as `examples/steps-page-heartbeat-demo.py`. It writes its dated CSV in the current directory. Both examples are simulations, not earlier test results. Logs in `logs/` stay local and are not included in Git; preserve any evidence you want to share separately.

To compare recorded angles, prepare a CSV with unique `sample_id`, `reference_angle_deg`, and `sensor_angle_deg` columns. Additional columns, such as run and photo references, can be included. For example, put your readings in `evidence/runs/run-01/readings.csv` and use a new output filename:

```sh
python3 compare_readings.py evidence/runs/run-01/readings.csv --output evidence/runs/run-01/analysis.csv
```

This run folder is ignored by Git, so the readings and analysis stay local. Keep a separate copy and agree on a way to share the results with the team.

To try the comparison before real readings exist, use the clearly labeled synthetic data:

```sh
python3 compare_readings.py examples/synthetic-readings.csv --output sample-analysis.csv --inject example-40
```

The output file must be new; choose another filename for each run. The original CSV is not changed.

To test a known error without changing the input, add `--inject SAMPLE_ID` for each selected sample. The tool adds 10° to those sensor readings in its output copy and marks them as injected. It reports differences over 5° and sensor readings over 45°, comparing the latter with the independent reference. It treats the entered angles as exact; consider the recorded reference uncertainty, especially near a threshold. These values are experiment settings, not safety limits.

This offline tool compares recorded sensor and reference angles. Testing a pretend robot reading may need separate code or a deliberate configuration; the tool does not already connect to a robot or read its data.

See [the experiment plan](docs/experiment-plan.md), [inventory checklist](docs/inventory.md), and [evidence guide](evidence/README.md) for the proposed bench test and records to collect.
