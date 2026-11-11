#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
make >/dev/null
BIN="$ROOT/bin/scheduler"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

# Main six-process case: all three algorithms and required metric labels.
"$BIN" tests/part_b/processes.csv 2 > "$TMP/main.out" || fail 'main dataset runs'
grep -q 'FIRST COME, FIRST SERVED' "$TMP/main.out" || fail 'FCFS output'
grep -q 'NON-PREEMPTIVE SJF' "$TMP/main.out" || fail 'SJF output'
grep -q 'ROUND ROBIN' "$TMP/main.out" || fail 'Round Robin output'
grep -q 'Averages: turnaround' "$TMP/main.out" || fail 'average metrics'
pass 'main six-process dataset'

# All arrivals at time zero; also exercises equal-arrival tie-breaking.
cat > "$TMP/all_zero.csv" <<'CSV'
PID,arrival_time,burst_time
10,0,5
11,0,2
12,0,2
CSV
"$BIN" "$TMP/all_zero.csv" 2 > "$TMP/all_zero.out" || fail 'all-zero-arrival case'
pass 'all processes arrive at time zero'

# First arrival after zero must produce an idle interval.
cat > "$TMP/idle.csv" <<'CSV'
PID,arrival_time,burst_time
20,4,2
21,7,1
CSV
"$BIN" "$TMP/idle.csv" 2 > "$TMP/idle.out" || fail 'idle case'
grep -q '\[IDLE: 0-4\]' "$TMP/idle.out" || fail 'idle interval missing'
pass 'CPU idle interval before first arrival'

# Equal burst times: SJF uses earlier arrival, then input order.
cat > "$TMP/equal_burst.csv" <<'CSV'
PID,arrival_time,burst_time
30,0,3
31,0,2
32,0,2
CSV
"$BIN" "$TMP/equal_burst.csv" 1 > "$TMP/equal_burst.out" || fail 'equal-burst case'
pass 'equal burst-time tie case'

# One process only.
cat > "$TMP/one.csv" <<'CSV'
PID,arrival_time,burst_time
40,2,4
CSV
"$BIN" "$TMP/one.csv" 2 > "$TMP/one.out" || fail 'single-process case'
grep -q '\[IDLE: 0-2\]' "$TMP/one.out" || fail 'single-process idle interval missing'
pass 'single process'

# A short process arriving while a long process runs must not preempt SJF.
cat > "$TMP/nonpreemptive.csv" <<'CSV'
PID,arrival_time,burst_time
50,0,9
51,2,1
CSV
"$BIN" "$TMP/nonpreemptive.csv" 2 > "$TMP/nonpreemptive.out" || fail 'non-preemptive case'
grep -q '\[P50: 0-9\] -> \[P51: 9-10\]' "$TMP/nonpreemptive.out" || fail 'SJF unexpectedly preempted'
pass 'SJF remains non-preemptive when a shorter job arrives'

# Invalid inputs must return non-zero.
cat > "$TMP/malformed.csv" <<'CSV'
PID,arrival_time,burst_time
1,0
CSV
if "$BIN" "$TMP/malformed.csv" 2 >/dev/null 2>&1; then fail 'malformed CSV rejected'; fi
pass 'malformed CSV rejected'

cat > "$TMP/duplicate.csv" <<'CSV'
PID,arrival_time,burst_time
1,0,2
1,1,3
CSV
if "$BIN" "$TMP/duplicate.csv" 2 >/dev/null 2>&1; then fail 'duplicate PID rejected'; fi
pass 'duplicate PID rejected'

cat > "$TMP/negative_arrival.csv" <<'CSV'
PID,arrival_time,burst_time
1,-1,2
CSV
if "$BIN" "$TMP/negative_arrival.csv" 2 >/dev/null 2>&1; then fail 'negative arrival rejected'; fi
pass 'negative arrival rejected'

cat > "$TMP/zero_burst.csv" <<'CSV'
PID,arrival_time,burst_time
1,0,0
CSV
if "$BIN" "$TMP/zero_burst.csv" 2 >/dev/null 2>&1; then fail 'zero burst rejected'; fi
pass 'zero burst rejected'

if "$BIN" tests/part_b/processes.csv 0 >/dev/null 2>&1; then fail 'zero quantum rejected'; fi
if "$BIN" tests/part_b/processes.csv -2 >/dev/null 2>&1; then fail 'negative quantum rejected'; fi
if "$BIN" tests/part_b/processes.csv abc >/dev/null 2>&1; then fail 'non-numeric quantum rejected'; fi
pass 'invalid Round Robin quantum rejected'

# Changing quantum must change the Round Robin timeline on this dataset.
"$BIN" tests/part_b/processes.csv 3 > "$TMP/q3.out" || fail 'quantum 3 run'
Q2_RR="$(sed -n '/^ROUND ROBIN$/,/^Process metrics/p' "$TMP/main.out" | grep '^\[' | head -n 1)"
Q3_RR="$(sed -n '/^ROUND ROBIN$/,/^Process metrics/p' "$TMP/q3.out" | grep '^\[' | head -n 1)"
[[ "$Q2_RR" != "$Q3_RR" ]] || fail 'quantum changes RR schedule'
pass 'Round Robin quantum changes the schedule'

printf '\nAll Part B tests passed.\n'
