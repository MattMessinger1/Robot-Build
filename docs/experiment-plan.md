# Bench experiment plan

## Goal and scope

Learn what an MPU-6050 can measure while a person moves an unpowered printed forearm and fixed hand. Compare the sensor's estimated tilt with an independent reference, and test warning logic using recorded or clearly labeled simulated data. The arm is a test prop; the eventual device is not an arm. There are no working joints, motors, wiring, or sensor mounts in the display model.

This is an experiment, not a robot safety system. An on-screen warning or LED is only a test signal. A warning or acknowledged command does not establish that a robot physically stops. Do not use this software to control a robot or powered mechanism.

## Gather what we have

Record sources and dates for earlier code, commands, wiring photos, and results. The working plan reports four normal runs and four runs with communication faults in earlier tests, with faults detected and stop commands acknowledged. The supporting files and test conditions are not yet in this repository, so those results have not been verified here.

| Item | Status to confirm |
| --- | --- |
| MPU-6050 | A sensor is reported available; identify the exact board, dimensions, pin labels, voltage, connectors, and its wiring instructions. |
| Computer | Identify the Raspberry Pi or laptop, power supply, microSD card, and reader on hand. Preserve existing card data; Raspberry Pi Imager erases the card it prepares. |
| Printed pieces | Confirm the forearm and fixed hand at 95%, 100%, and 105%, plus one reusable holder and one reusable sensor pad. Check printer capacity: the largest piece is about 298.2 mm long. |
| Mounting | Check the holder on all three sizes and the pad against the actual sensor board. Neither fit is verified. Gather two hook-and-loop straps and nonconductive mounting tape. |
| Independent reference | Obtain a marked angle scale or protractor and note its reading precision. |
| Prior work | Locate earlier source, commands, setup and wiring photos, raw readings, and results, including failed runs. |

Ask Rapid Axis to quote the five pieces and check fit; scaling an arm does not scale the hardware. No upper arm, covers, elbow cap, or motor is required for this experiment. Confirm board wiring and voltage from its instructions before connecting power. Do not infer pinout or a safe supply voltage from the sensor name alone.

## Set up the measurement

1. Confirm the holder and sensor pad fit, secure the sensor without conductive contact, and record the board and mounting orientation. Check wiring before powering the sensor. Save timed readings on a laptop or Pi.
2. Place the arm alongside an independently marked angle scale or protractor. Use a vertical tilt that gravity makes observable to the sensor; a flat turn on a table is not a reliable still-position angle check for this sensor.
3. Calibrate and use the same zero position and positive direction for the sensor estimate and the reference. Note reference reading precision. Reset the zero when changing arm sizes.
4. For each sample, keep a unique sample ID, run number, arm size, timestamp, marked reference angle, sensor reading or estimate, and a link or filename for the photo. Keep raw sensor data and configuration so the estimate can be revisited. The reference must be independent of the sensor reading being checked.

## Collect and compare

1. Hold the unpowered piece still at zero and record a 30-second baseline.
2. Move it by hand to 0°, 20°, 40°, and 70°, holding each position for a reading and photo. Complete five runs in total across all three sizes—for example, two runs at one size, two at another, and one at the third. That yields 20 angle comparisons. Record the actual marked angle and any setup or reading uncertainty.
3. Compare the estimated sensor angles with the separate reference. Begin with a goal of agreement within 5°; this is a study goal, not a safety threshold. Record disagreements and limitations rather than excluding failed runs.
4. Film a slow movement while logging the sensor, and mark the start in both recordings so they can be aligned. Keep the video and its run ID with the data.

## Exercise the warnings

Flag a difference greater than 5° between sensor and reference. To exercise a known change, add 10° to copies of selected sensor readings and label the changes; preserve original readings and reference values. Separately flag sensor estimates above 45° and compare them with the marked reference. Record false and missed warnings. A wrong sensor reading and unexpected physical movement are different problems, and these checks do not establish danger.

Replay readings to test an on-screen light or a properly wired LED. Keep the warning latched until the difference clears and a person resets it; record warning and reset times. This signal does not stop a robot. Use the simulated heartbeat demo to explore missing readings and reset logic; its simulated timing is not a real-world timing test.

## Save the evidence

Keep the setup description, sensor details, calibration, code version, wiring and setup photos, raw readings, marked angles, comparison results, warning and reset logs, video, and limitations together. Record errors, missed warnings, false warnings, and failed runs. The first finish line is evidence another person can inspect and use to repeat the test, not a finished safety product.

After that, choose a movement and detection goal with a safety expert; check a robot maker's supported data and stop-request interfaces; and plan a separately reviewed powered test that measures both the request and the physical response. These later steps have not been carried out by the current software.
