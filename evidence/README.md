# Experiment evidence

When the arm test begins, keep each run in its own folder under `evidence/runs/`, named with a date and run ID. Include the setup and board details, servo model and supply, encoder and magnet placement, sensor orientation, calibration, zero and direction, code version, raw timestamped readings, commanded positions, derived angles, independent protractor observations and their precision, and notes on errors or failed runs. Keep useful setup photos, analysis, and copies of the original earlier results with the records. Preserve the originals where they are. Link each sample ID and timestamp to its reference observation.

Keep raw data, derived angles, and any pretend or changed readings clearly labeled and separate. Record alignment, clock or timing assumptions, and measurement uncertainty. Preserve original inputs and identify changed copies. A stop request or acknowledgement is not proof of a physical stop; record those events separately if they are tested later.

Both `evidence/runs/` and `logs/` are ignored by Git. They remain local and will not appear in another person's clone. Keep an additional copy in a location you control, and agree separately on a suitable place to share the evidence with collaborators. Review any files before sharing; this repository is public. Do not put credentials or private information in it.
