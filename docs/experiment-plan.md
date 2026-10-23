# Bench experiment plan

## What we are testing

**Test 1 checks the readings.** The proposed MG996R servo moves a small arm. An AS5600 at the joint measures its angle; an MPU-6050 on the forearm estimates tilt. Pause the arm and compare both with a protractor. This shows how well each reading matches the physical position.

**Test 2 checks the software.** Compare the commanded position, the measured joint angle, and the forearm's estimated tilt after putting them in the same units, direction, and reference position. For example, the command might be 45°, the joint reading 43°, and the tilt estimate 47°. These are example numbers, not results. Test matching readings and known differences to see what the software flags. Checking the sensors first makes the comparison more meaningful.

This is a bench experiment, not a safety system. A warning or acknowledged stop command does not show that a motor or robot physically stopped. The repository's current scripts do not operate the servo or read the sensor.

## 1. Find the earlier work

Locate the earlier motor-control code, exact run commands, wiring and setup photos, and original results, including failed runs. Keep the originals intact. Review what the code actually does and how to run it before adapting it. Record what is confirmed and what is still missing.

The project notes report four normal runs and four runs with communication faults, with faults detected and stop commands acknowledged. The original files and test conditions are not in this repository yet.

## 2. Check the parts and proposed arm

The concept is a Raspberry Pi Pico controlling an MG996R servo, an AS5600 angle sensor fixed at the joint with a magnet turning with the joint, and an MPU-6050 mounted to the moving forearm. Confirm each actual part, including the encoder and its magnet, the servo's supply, mounting hardware, board versions, and the earlier motor setup. See the [inventory](inventory.md). The C1 drawing is a concept, not verified print-ready files or proof the parts fit.

Inspect the existing design and parts before ordering or printing. Check the servo, magnet, encoder position, sensor mounts, fasteners, clearances, and the range of movement. A small fit test may resolve uncertain dimensions; decide whether any extra versions are needed after checking it. Scaling the whole model also changes holes and mounts for fixed-size parts, so do not assume 95% and 105% versions will fit.

Check the actual devices' specifications and wiring before applying power. GPIO pins are not a motor power supply. Do not guess pinouts, voltages, the servo supply, or the encoder's magnet alignment and spacing.

Secure the setup and keep space around the moving arm. For a held-position tilt check against gravity, the joint axis must be horizontal so the forearm moves in a vertical plane. A rig lying flat may need to be mounted on its side after checking stability and clearance. A flat turn on a table cannot be measured this way with gravity alone. Make the servo power easy to remove, and supervise movement. Place the protractor's center at the joint so it independently shows the arm's angle.

## 3. Check the sensor

1. Together, check the mounting, protractor alignment, safe travel, and power. Record the hardware, code version, wiring, sensor orientation, calibration, and protractor precision. Define the same zero, axis, positive direction and units for each reading, and record the times so readings can be matched. Account for angle wraparound if needed. With the arm supported and still, record a short baseline before moving it.
2. If the setup can safely reach them, command the servo to 0°, 30°, and 60°. Pause and let the arm settle at each position. Record the command, the protractor reading, the AS5600 joint angle, the MPU-6050 tilt estimate, and anything unusual. One person operates and supervises; the other stays clear, observes, and records. They may switch roles.
3. At each position, move away and return at least three times after the first hold, ideally approaching from both directions when safe. Take multiple readings at each hold. Save each sample's ID, time, original sensor data, derived angles, protractor reading, and reading uncertainty. Keep the original logs, notes, errors, and unsuccessful readings. Photos of held positions are optional.
4. Check the encoder against the protractor before using it as a reference, and check the MPU-6050 estimate against them both. Record the differences and the largest one. The encoder is a measured reference with its own error, not perfect ground truth. Consider uncertainty before treating a small difference as an error.

The existing `compare_readings.py` can compare recorded reference and sensor angles offline. It does not collect live readings. Its warning for a difference over 5° and its 10° injected change are experiment settings, not safety limits.

## 4. Check the comparison

Compare the commanded position and the independently measured angles, after aligning their zero, direction, units, and times. A command is a target, not proof of where the arm actually moved. Start with close readings, then introduce clearly labeled pretend or altered values with known differences. Check which cases warn, which mismatches are missed, and which matching cases warn by mistake. Keep real and pretend values separate.

This requires comparison code or a configuration that understands the pretend robot reading; the existing offline comparator currently compares a sensor angle with a reference angle. Preserve the existing tool's defaults and tests when adding a separate experiment.

## 5. Save results and choose the next test

Keep the setup, calibration, original code and logs, raw readings, derived angles, protractor observations, analysis, and unsuccessful runs together. The [evidence guide](../evidence/README.md) explains what stays local and how to preserve a copy for the team.

The next challenge is learning whether a robot can provide useful live data, how to recognize a meaningful problem, and whether the robot supports a stop request from an owner-controlled device. A single robot data feed may not independently confirm what the robot is actually doing. The request and the physical response would need separate, reviewed tests. Those connections and tests are future work.
