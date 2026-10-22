# Bench experiment plan

## What we are testing

**Test 1 checks the sensor.** A servo will move a ruler with an MPU-6050 attached. We will pause the ruler and compare the sensor's estimated angle with a protractor. For example, if the protractor reads 30° and the sensor estimates 31°, the difference is 1°. This checks how closely the sensor sees the movement.

**Test 2 checks the software.** Give the software a sensor estimate and a separately labeled pretend robot reading. If they differ by a chosen test amount, does it flag the difference? Try both matching readings and known mismatches. A trustworthy sensor check makes the comparison more meaningful.

This is a bench experiment, not a safety system. A warning or acknowledged stop command does not show that a motor or robot physically stopped. The repository's current scripts do not operate the servo or read the sensor.

## 1. Find the earlier work

Locate the earlier motor-control code, exact run commands, wiring and setup photos, and original results, including failed runs. Keep the originals intact. Review what the code actually does and how to run it before adapting it. Record what is confirmed and what is still missing.

The project notes report four normal runs and four runs with communication faults, with faults detected and stop commands acknowledged. The original files and test conditions are not in this repository yet.

## 2. Set up the ruler test

The parts are reported to be on hand. Confirm the actual servo model and whether it can hold commanded positions, its power supply and controller or driver, the MPU-6050 breakout board and voltage, compatible wires, secure ruler and sensor attachments, and a protractor. See the [inventory](inventory.md).

Check the actual devices' specifications and wiring before applying power. The Pi can provide a control signal, but GPIO pins are not a general-purpose motor power supply. The servo's supply and signal connections depend on its model. Do not guess a board's pinout or voltage.

Secure the setup so the servo can move the ruler in a vertical plane. Attach the sensor firmly and without conductive contact. Keep space around the moving ruler, supervise the test, and make servo power easy to remove. A change in tilt relative to gravity can be checked at still positions; a flat turn on a table does not provide the same angle reference. Put the protractor's center at the servo pivot so it independently shows the ruler's actual angle. The servo's commanded position is not proof of the ruler's actual angle.

## 3. Check the sensor

1. Record the hardware, code version, sensor orientation, wiring, calibration, and protractor reading precision. Agree on the same zero and positive direction for the sensor estimate and protractor.
2. If the setup can safely reach them, have the servo move the ruler to 0°, 30°, and 60°. Pause and let it settle at each position. Read the actual angle from the protractor and record the sensor estimate.
3. Record three readings at each position, nine in total. For each sample, save an ID, time, protractor reading, sensor estimate, uncertainty, and raw sensor data. Keep any errors or unsuccessful readings too.
4. Compare each estimate with the independent protractor reading. Record the differences, including the largest one, and decide whether the readings are useful enough for the next test. Consider uncertainty before treating a small difference as an error.

The existing `compare_readings.py` can compare recorded reference and sensor angles offline. It does not collect live readings. Its warning for a difference over 5° and its 10° injected change are experiment settings, not safety limits.

## 4. Check the comparison

Use the sensor readings with separately labeled pretend robot readings. Start with matching values, then introduce known differences. Check which cases warn, which mismatches are missed, and which matching cases warn by mistake. Keep the measured sensor values, pretend values, and test labels distinct.

This requires comparison code or a configuration that understands the pretend robot reading; the existing offline comparator currently compares a sensor angle with a reference angle. Preserve the existing tool's defaults and tests when adding a separate experiment.

## 5. Save results and choose the next test

Keep the setup, calibration, original code and logs, raw readings, protractor observations, analysis, and unsuccessful runs together. The [evidence guide](../evidence/README.md) explains what stays local and how to preserve a copy for the team.

The next challenge is learning whether a robot can provide useful live data, how to recognize a meaningful problem, and whether the robot supports a stop request from an owner-controlled device. A single robot data feed may not independently confirm what the robot is actually doing. The request and the physical response would need separate, reviewed tests. Those connections and tests are future work.
