#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

make bankers

safe_output="$(./bin/bankers tests/part_d/safe.txt)"
grep -q "State: SAFE" <<< "$safe_output"
echo "PASS: the safe-state example has a safe sequence"

unsafe_output="$(./bin/bankers tests/part_d/unsafe.txt)"
grep -q "State: UNSAFE" <<< "$unsafe_output"
grep -q "not automatically the same thing as a deadlock" <<< "$unsafe_output"
echo "PASS: the unsafe-state example is identified without calling it a deadlock"

multiple_output="$(./bin/bankers tests/part_d/multiple_safe_sequences.txt)"
grep -q "State: SAFE" <<< "$multiple_output"
grep -q "More than one process can start" <<< "$multiple_output"
echo "PASS: the example shows more than one possible first process and is accepted"

if ./bin/bankers tests/part_d/does_not_exist.txt >/dev/null 2>&1; then
    echo "FAIL: a missing input file was accepted" >&2
    exit 1
fi
echo "PASS: a missing input file is rejected"

echo "All Part D tests passed."
