import csv
from datetime import datetime, timezone

# Experiment settings only: simulated time, not a safety requirement.
PERIOD_MS = 100
TIMEOUT_MS = 500
TRIALS_PER_CASE = 10
LOG = 'heartbeat-events-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.csv'


def run_trial(trial, case, writer):
    last_seen = None
    request = False
    raised_at = None
    held_after_resume = False
    refused_early_reset = False
    cleared_after_reset = False

    def record(time_ms, event, detail=''):
        writer.writerow([trial, case, time_ms, event, detail])

    def attempt_reset(time_ms, stale):
        nonlocal request
        if request and not stale:
            request = False
            record(time_ms, 'reset_accepted', 'request_off')
            return True
        record(time_ms, 'reset_refused', 'stale or no request')
        return False

    record(0, 'settings', f'period_ms={PERIOD_MS};timeout_ms={TIMEOUT_MS}')
    for tick in range(100):  # 10 seconds of simulated time
        time_ms = tick * PERIOD_MS
        dropout = case == 'dropout' and 50 <= tick < 60
        if case == 'dropout' and tick in (50, 60):
            record(time_ms, 'dropout_start' if tick == 50 else 'dropout_end')
        if not dropout:
            last_seen = time_ms
            record(time_ms, 'sample', tick)

        stale = last_seen is None or time_ms - last_seen >= TIMEOUT_MS
        if stale and not request:
            request = True
            raised_at = time_ms
            record(time_ms, 'request_on', 'no fresh sample')

        if case == 'dropout' and tick == 57:
            was_on = request
            accepted = attempt_reset(time_ms, stale)
            refused_early_reset = was_on and not accepted and request
        if case == 'dropout' and tick == 61:
            held_after_resume = request and not stale
            record(time_ms, 'request_after_resume', 'on' if request else 'FAIL')
        if case == 'dropout' and tick == 62:
            accepted = attempt_reset(time_ms, stale)  # simulated manual reset
            cleared_after_reset = accepted and not request

    if case == 'normal':
        return raised_at is None and not request
    return (raised_at == 5400 and refused_early_reset and held_after_resume
            and cleared_after_reset and not request)


with open(LOG, 'w', newline='', encoding='utf-8') as output:
    writer = csv.writer(output)
    writer.writerow(['trial', 'case', 'time_ms', 'event', 'detail'])
    results = []
    for case in ('normal', 'dropout'):
        passed = sum(run_trial(n, case, writer) for n in range(1, TRIALS_PER_CASE + 1))
        results.append(passed)
        print(f'{case}: {passed}/{TRIALS_PER_CASE} passed')

print(f'Event log: {LOG}')
if results != [TRIALS_PER_CASE, TRIALS_PER_CASE]:
    raise SystemExit('A check failed. Inspect the event log.')
