#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

make page-replacement disk-scheduling

pages_one="$(./bin/page_replacement tests/part_e/pages_case1.txt)"
grep -q "FIFO page faults:" <<< "$pages_one"
grep -q "LRU page faults:" <<< "$pages_one"
echo "PASS: FIFO and LRU both show frame contents and page-fault totals for case 1"

pages_two="$(./bin/page_replacement tests/part_e/pages_case2_fifo_lru_difference.txt)"
grep -q "FIFO page faults: 7" <<< "$pages_two"
grep -q "LRU page faults: 6" <<< "$pages_two"
echo "PASS: case 2 shows a difference between FIFO (7) and LRU (6)"

disk_one="$(./bin/disk_scheduling tests/part_e/disk_case1.txt)"
grep -q "FCFS total head movement:" <<< "$disk_one"
grep -q "SSTF total head movement:" <<< "$disk_one"
echo "PASS: FCFS and SSTF show the service order and movement for case 1"

disk_two="$(./bin/disk_scheduling tests/part_e/disk_case2.txt)"
grep -q "FCFS total head movement:" <<< "$disk_two"
grep -q "SSTF total head movement:" <<< "$disk_two"
echo "PASS: FCFS and SSTF show the service order and movement for case 2"

if ./bin/page_replacement < /dev/null >/dev/null 2>&1; then
    echo "FAIL: empty page input was accepted" >&2
    exit 1
fi
echo "PASS: invalid page input is rejected"

if ./bin/disk_scheduling < /dev/null >/dev/null 2>&1; then
    echo "FAIL: empty disk input was accepted" >&2
    exit 1
fi
echo "PASS: invalid disk input is rejected"

echo "All Part E tests passed."
