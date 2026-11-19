#!/usr/bin/env bash
set -Eeuo pipefail

# CS207 Assignment 1 - run the project checks and save screenshots.
# Run this from a terminal opened inside the Ubuntu VirtualBox desktop.

ROOT_DIR="${1:-$PWD}"
if [[ ! -d "$ROOT_DIR" ]]; then
    echo "I cannot find the project folder: $ROOT_DIR" >&2
    echo "Usage: bash capture_cs207_all_screenshots.sh /path/to/CS207_Operating_Systems_Project" >&2
    exit 1
fi
ROOT_DIR="$(cd "$ROOT_DIR" && pwd)"

if [[ ! -f "$ROOT_DIR/Makefile" || ! -d "$ROOT_DIR/src" ]]; then
    echo "That folder does not look like the project root." >&2
    echo "It should contain both Makefile and src/." >&2
    echo "Usage: bash capture_cs207_all_screenshots.sh /path/to/CS207_Operating_Systems_Project" >&2
    exit 1
fi

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
    echo "I cannot see an Ubuntu desktop session." >&2
    echo "Open Terminal inside the Ubuntu VM desktop and run this script there." >&2
    exit 1
fi

# These commands are normally already present in Ubuntu after build-essential
# and the standard command-line tools have been installed.
missing=()
for command_name in gcc make timeout uname lscpu free df find stat realpath; do
    command -v "$command_name" >/dev/null 2>&1 || missing+=("$command_name")
done
if ((${#missing[@]} > 0)); then
    echo "Some required commands are missing: ${missing[*]}" >&2
    echo "Run this once, then start this script again:" >&2
    echo "sudo apt update && sudo apt install -y build-essential make coreutils util-linux" >&2
    exit 1
fi

# Find a tool that can take a screenshot of the Ubuntu desktop.
SCREENSHOT_TOOL=""
for tool in gnome-screenshot xfce4-screenshooter scrot; do
    if command -v "$tool" >/dev/null 2>&1; then
        SCREENSHOT_TOOL="$tool"
        break
    fi
done

if [[ -z "$SCREENSHOT_TOOL" ]]; then
    echo "No screenshot utility was found. I will install gnome-screenshot." >&2
    if ! command -v sudo >/dev/null 2>&1 || ! command -v apt-get >/dev/null 2>&1; then
        echo "Please install gnome-screenshot, then run this script again." >&2
        exit 1
    fi
    sudo apt-get update
    sudo apt-get install -y gnome-screenshot
    if command -v gnome-screenshot >/dev/null 2>&1; then
        SCREENSHOT_TOOL="gnome-screenshot"
    else
        echo "gnome-screenshot could not be installed. Install it with: sudo apt install gnome-screenshot" >&2
        exit 1
    fi
fi

cd "$ROOT_DIR"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="$ROOT_DIR/outputs/evidence_capture_$RUN_ID"
mkdir -p "$OUT_DIR" \
    "$ROOT_DIR/screenshots/part_a" \
    "$ROOT_DIR/screenshots/part_b" \
    "$ROOT_DIR/screenshots/part_c" \
    "$ROOT_DIR/screenshots/part_d" \
    "$ROOT_DIR/screenshots/part_e" \
    "$ROOT_DIR/screenshots/part_f"

# Keep the result of each section for the final summary.
declare -A RESULT
record_result() {
    RESULT["$1"]="$2"
}

run_logged() {
    local name="$1"
    local logfile="$2"
    shift 2
    if "$@" >"$logfile" 2>&1; then
        record_result "$name" "PASS"
        return 0
    else
        local exit_code=$?
        record_result "$name" "CHECK LOG (exit $exit_code)"
        return "$exit_code"
    fi
}

capture_screen() {
    local part="$1"
    local filename="$2"
    local title="$3"
    local content_file="$4"
    local destination="$ROOT_DIR/screenshots/$part/${filename}_$RUN_ID.png"

    # Clear the terminal and show a short, readable summary before taking the
    # screenshot. The detailed output remains saved in outputs/.
    printf '\033[2J\033[H'
    printf '%s\n' '============================================================'
    printf 'CS207 OPERATING SYSTEMS - %s\n' "$title"
    printf '%s\n' '============================================================'
    if [[ -s "$content_file" ]]; then
        sed -n "1,${CS207_SCREEN_LINES:-30}p" "$content_file"
    else
        printf 'No output was produced. Check: %s\n' "$content_file"
    fi
    printf '\nSaving screenshot...\n'
    sleep "${CS207_CAPTURE_DELAY:-2}"

    case "$SCREENSHOT_TOOL" in
        gnome-screenshot)
            gnome-screenshot --file="$destination" >/dev/null 2>&1
            ;;
        xfce4-screenshooter)
            xfce4-screenshooter --window --save "$destination" >/dev/null 2>&1
            ;;
        scrot)
            scrot "$destination" >/dev/null 2>&1
            ;;
    esac

    if [[ ! -s "$destination" ]]; then
        echo "Screenshot was not created: $destination" >&2
        return 1
    fi
    printf 'Saved screenshot: %s\n' "$destination"
}

# Part A: capture the actual Ubuntu guest environment.
{
    echo "Date: $(date)"
    echo "Computer name: $(hostname)"
    if [[ -r /etc/os-release ]]; then
        . /etc/os-release
        echo "Operating system: ${PRETTY_NAME:-unknown}"
    fi
    echo
    echo "GCC version:"
    gcc --version | sed -n '1p'
    echo
    echo "Kernel and system:"
    uname -a
    echo
    echo "CPU details:"
    lscpu | grep -E '^(Architecture|CPU\(s\)|Model name|Virtualization):' || true
    echo
    echo "Memory:"
    free -h
    echo
    echo "Disk space:"
    df -h /
} > "$OUT_DIR/part_a_environment.txt" 2>&1
record_result "Part A environment information" "PASS"
{
    echo "Ubuntu: $(. /etc/os-release && echo "${PRETTY_NAME:-unknown}")"
    echo "GCC: $(gcc --version | sed -n '1p')"
    echo "Kernel: $(uname -sr)"
    echo
    echo "CPU and VM details:"
    lscpu | grep -E '^(Architecture|CPU\(s\)|Model name):' || true
    echo
    echo "Memory:"
    free -h | sed -n '1,2p'
    echo
    echo "Disk space:"
    df -h / | sed -n '1,2p'
} > "$OUT_DIR/part_a_screen.txt" 2>&1
capture_screen part_a 01_environment "PART A - UBUNTU VM AND ENVIRONMENT" "$OUT_DIR/part_a_screen.txt"

# Build the repository's normal default target. Individual programs are also
# built below, so the script can continue even if the default target is limited.
if run_logged "Project default build" "$OUT_DIR/build.log" make -j1; then
    :
fi
mkdir -p bin

# Build Parts C, D and E directly as a backup to the Makefile targets.
if [[ -f src/part_c/producer_consumer.c ]]; then
    if gcc -std=c11 -Wall -Wextra -Wpedantic -O2 -pthread \
        src/part_c/producer_consumer.c -o bin/producer_consumer \
        >"$OUT_DIR/build_part_c.log" 2>&1; then
        record_result "Part C compile" "PASS"
    else
        record_result "Part C compile" "FAIL - see build_part_c.log"
    fi
else
    record_result "Part C compile" "NOT FOUND"
fi

if [[ -f src/part_d/bankers.c ]]; then
    if gcc -std=c17 -Wall -Wextra -Wpedantic -O2 \
        src/part_d/bankers.c -o bin/bankers \
        >"$OUT_DIR/build_part_d.log" 2>&1; then
        record_result "Part D compile" "PASS"
    else
        record_result "Part D compile" "FAIL - see build_part_d.log"
    fi
else
    record_result "Part D compile" "NOT FOUND"
fi

if [[ -f src/part_e/page_replacement.c && -f src/part_e/disk_scheduling.c ]]; then
    if gcc -std=c17 -Wall -Wextra -Wpedantic -O2 \
        src/part_e/page_replacement.c -o bin/page_replacement \
        >"$OUT_DIR/build_page_replacement.log" 2>&1 &&
       gcc -std=c17 -Wall -Wextra -Wpedantic -O2 \
        src/part_e/disk_scheduling.c -o bin/disk_scheduling \
        >"$OUT_DIR/build_disk_scheduling.log" 2>&1; then
        record_result "Part E compile" "PASS"
    else
        record_result "Part E compile" "FAIL - see Part E build logs"
    fi
else
    record_result "Part E compile" "NOT FOUND"
fi

# Part B: use the real test runner already in the project. Do not invent an
# input format or call a placeholder test a pass.
PART_B_TEST=""
for candidate in \
    tests/part_b/run_tests.sh \
    tests/part_b/test_scheduler.sh \
    tests/part_b/test.sh \
    tests/test_part_b.sh \
    tests/run_part_b_tests.sh \
    scripts/test_part_b.sh \
    scripts/test_scheduler.sh; do
    if [[ -f "$candidate" ]]; then
        PART_B_TEST="$candidate"
        break
    fi
done

if [[ -n "$PART_B_TEST" ]]; then
    if run_logged "Part B scheduler tests" "$OUT_DIR/part_b_tests.txt" bash "$PART_B_TEST"; then
        if grep -Eiq 'placeholder|TODO|not implemented' "$OUT_DIR/part_b_tests.txt"; then
            record_result "Part B scheduler tests" "REVIEW - runner contains placeholder text"
        elif ! grep -Eiq 'PASS|passed|success' "$OUT_DIR/part_b_tests.txt"; then
            record_result "Part B scheduler tests" "REVIEW - check test output"
        fi
    fi
elif grep -q '^test-part-b:' Makefile; then
    if run_logged "Part B scheduler tests" "$OUT_DIR/part_b_tests.txt" make test-part-b; then
        if grep -Eiq 'placeholder|TODO|not implemented' "$OUT_DIR/part_b_tests.txt"; then
            record_result "Part B scheduler tests" "REVIEW - runner contains placeholder text"
        fi
    fi
else
    {
        echo "No Part B test runner was found."
        echo "I have not guessed the scheduler's input format."
        echo
        echo "Files under tests/part_b:"
        if [[ -d tests/part_b ]]; then
            find tests/part_b -maxdepth 2 -type f -print | sed -n '1,15p'
        else
            echo "tests/part_b is missing."
        fi
        echo
        echo "Please add or run the Part B test script before submission."
    } > "$OUT_DIR/part_b_tests.txt"
    record_result "Part B scheduler tests" "REVIEW - runner not found"
fi

{
    echo "Test runner: ${PART_B_TEST:-Makefile target or not found}"
    echo "Result: ${RESULT["Part B scheduler tests"]:-NOT RUN}"
    echo
    if [[ -s "$OUT_DIR/part_b_tests.txt" ]]; then
        tail -n 14 "$OUT_DIR/part_b_tests.txt"
    fi
} > "$OUT_DIR/part_b_screen.txt"
capture_screen part_b 02_cpu_scheduling "PART B - CPU SCHEDULING" "$OUT_DIR/part_b_screen.txt"

# Part C: one visible 100-item run plus the full automated test script.
if [[ -x bin/producer_consumer ]]; then
    if timeout 30s ./bin/producer_consumer 100 >"$OUT_DIR/part_c_run_100.txt" 2>&1; then
        if grep -Fq 'Verification: PASS' "$OUT_DIR/part_c_run_100.txt" &&
           grep -Fq 'Buffer bounds: PASS' "$OUT_DIR/part_c_run_100.txt"; then
            record_result "Part C 100-item run" "PASS"
        else
            record_result "Part C 100-item run" "CHECK OUTPUT"
        fi
    else
        record_result "Part C 100-item run" "FAIL - see output log"
    fi
else
    record_result "Part C 100-item run" "NOT RUN - binary missing"
    : > "$OUT_DIR/part_c_run_100.txt"
fi

if [[ -f tests/part_c/run_tests.sh ]]; then
    if run_logged "Part C automated tests" "$OUT_DIR/part_c_tests.txt" bash tests/part_c/run_tests.sh; then
        :
    fi
else
    record_result "Part C automated tests" "NOT FOUND"
    echo "tests/part_c/run_tests.sh was not found." > "$OUT_DIR/part_c_tests.txt"
fi
{
    echo "Two producers and two consumers share a buffer of capacity 5."
    echo "100-item execution: ${RESULT["Part C 100-item run"]}"
    echo "Automated tests: ${RESULT["Part C automated tests"]}"
    echo
    echo "Example activity:"
    grep -m1 -E '^Producer [12] produced' "$OUT_DIR/part_c_run_100.txt" || true
    grep -m1 -E '^Consumer [12] consumed' "$OUT_DIR/part_c_run_100.txt" || true
    echo
    grep -E '^(Verification:|Buffer bounds:)' "$OUT_DIR/part_c_run_100.txt" || true
    echo
    grep -E '^(PASS:|All Part C tests passed|FAIL:)' "$OUT_DIR/part_c_tests.txt" | tail -n 8 || true
} > "$OUT_DIR/part_c_screen.txt"
capture_screen part_c 03_producer_consumer "PART C - PRODUCER AND CONSUMER" "$OUT_DIR/part_c_screen.txt"

# Part D: run all supplied Banker's algorithm examples.
PART_D_RUN_OK=1
: > "$OUT_DIR/part_d_runs.txt"
if [[ -x bin/bankers ]]; then
    for input in tests/part_d/safe.txt tests/part_d/unsafe.txt tests/part_d/multiple_safe_sequences.txt; do
        {
            echo "--- $input ---"
            if [[ -f "$input" ]]; then
                ./bin/bankers "$input"
            else
                echo "Input file missing: $input"
                PART_D_RUN_OK=0
            fi
            echo
        } >> "$OUT_DIR/part_d_runs.txt" 2>&1 || PART_D_RUN_OK=0
    done
else
    echo "bin/bankers is missing; check build_part_d.log." > "$OUT_DIR/part_d_runs.txt"
    PART_D_RUN_OK=0
fi
if [[ "$PART_D_RUN_OK" -eq 1 ]] &&
   grep -q 'State: SAFE' "$OUT_DIR/part_d_runs.txt" &&
   grep -q 'State: UNSAFE' "$OUT_DIR/part_d_runs.txt"; then
    record_result "Part D sample cases" "PASS"
else
    record_result "Part D sample cases" "CHECK LOG"
fi
if [[ -f tests/part_d/run_tests.sh ]]; then
    if run_logged "Part D automated tests" "$OUT_DIR/part_d_tests.txt" bash tests/part_d/run_tests.sh; then
        :
    fi
else
    record_result "Part D automated tests" "NOT FOUND"
    echo "tests/part_d/run_tests.sh was not found." > "$OUT_DIR/part_d_tests.txt"
fi
{
    echo "Banker's algorithm test results:"
    grep -E '^(--- tests/|State:|One safe sequence:|More than one process can start|An unsafe state)' "$OUT_DIR/part_d_runs.txt" || true
    echo
    grep -E '^(PASS:|All Part D tests passed|FAIL:)' "$OUT_DIR/part_d_tests.txt" || true
} > "$OUT_DIR/part_d_screen.txt"
capture_screen part_d 04_bankers_algorithm "PART D - BANKER'S ALGORITHM" "$OUT_DIR/part_d_screen.txt"

# Part E: two page-reference strings and two disk-request queues.
PART_E_RUN_OK=1
: > "$OUT_DIR/part_e_runs.txt"
if [[ -x bin/page_replacement && -x bin/disk_scheduling ]]; then
    for input in tests/part_e/pages_case1.txt tests/part_e/pages_case2_fifo_lru_difference.txt; do
        {
            echo "--- Page replacement: $input ---"
            if [[ -f "$input" ]]; then
                ./bin/page_replacement "$input"
            else
                echo "Input file missing: $input"
                PART_E_RUN_OK=0
            fi
            echo
        } >> "$OUT_DIR/part_e_runs.txt" 2>&1 || PART_E_RUN_OK=0
    done
    for input in tests/part_e/disk_case1.txt tests/part_e/disk_case2.txt; do
        {
            echo "--- Disk scheduling: $input ---"
            if [[ -f "$input" ]]; then
                ./bin/disk_scheduling "$input"
            else
                echo "Input file missing: $input"
                PART_E_RUN_OK=0
            fi
            echo
        } >> "$OUT_DIR/part_e_runs.txt" 2>&1 || PART_E_RUN_OK=0
    done
else
    echo "Part E binaries are missing; check the Part E build logs." > "$OUT_DIR/part_e_runs.txt"
    PART_E_RUN_OK=0
fi
if [[ "$PART_E_RUN_OK" -eq 1 ]]; then
    record_result "Part E sample cases" "PASS"
else
    record_result "Part E sample cases" "CHECK LOG"
fi
if [[ -f tests/part_e/run_tests.sh ]]; then
    if run_logged "Part E automated tests" "$OUT_DIR/part_e_tests.txt" bash tests/part_e/run_tests.sh; then
        :
    fi
else
    record_result "Part E automated tests" "NOT FOUND"
    echo "tests/part_e/run_tests.sh was not found." > "$OUT_DIR/part_e_tests.txt"
fi
{
    echo "Input: tests/part_e/pages_case2_fifo_lru_difference.txt"
    echo "This example has 3 frames and 8 page references."
    echo
    awk '/--- Page replacement: tests\/part_e\/pages_case2_fifo_lru_difference.txt ---/{show=1; next} /--- Disk scheduling:/{show=0} show {print}' "$OUT_DIR/part_e_runs.txt"
    echo
    grep -E '^(PASS:|All Part E tests passed|FAIL:)' "$OUT_DIR/part_e_tests.txt" | head -n 4 || true
} > "$OUT_DIR/part_e_pages_screen.txt"
{
    echo "Disk scheduling results from both test queues:"
    echo
    awk '/--- Disk scheduling:/{show=1} show {print}' "$OUT_DIR/part_e_runs.txt"
    echo
    grep -E '^(PASS:|All Part E tests passed|FAIL:)' "$OUT_DIR/part_e_tests.txt" | tail -n 4 || true
} > "$OUT_DIR/part_e_disk_screen.txt"
capture_screen part_e 05a_page_replacement "PART E - FIFO AND LRU PAGE REPLACEMENT" "$OUT_DIR/part_e_pages_screen.txt"
capture_screen part_e 05b_disk_scheduling "PART E - FCFS AND SSTF DISK SCHEDULING" "$OUT_DIR/part_e_disk_screen.txt"

# Part F: create the sample directory tree and record paths, permissions,
# ownership and file metadata.
if [[ -f scripts/part_f_demo.sh ]]; then
    if run_logged "Part F filesystem demo" "$OUT_DIR/part_f_demo.txt" bash scripts/part_f_demo.sh; then
        record_result "Part F filesystem demo" "PASS"
    else
        record_result "Part F filesystem demo" "CHECK LOG"
    fi
else
    record_result "Part F filesystem demo" "NOT FOUND"
    echo "scripts/part_f_demo.sh was not found." > "$OUT_DIR/part_f_demo.txt"
fi
{
    echo "Current user: $(id -un)"
    echo "Current group: $(id -gn)"
    echo
    echo "Absolute path:"
    realpath part_f_demo 2>/dev/null || true
    echo
    echo "Directories and files (permissions and owner):"
    find part_f_demo -maxdepth 4 -printf '%M %u:%g %p\n' 2>/dev/null | sed -n '1,12p' || true
    echo
    echo "File metadata:"
    find part_f_demo -type f -exec stat -c '%n | %A (%a) | %U:%G | %s bytes' {} \; 2>/dev/null | sed -n '1,5p' || true
    echo
    echo "Part F demo result: ${RESULT["Part F filesystem demo"]}"
} > "$OUT_DIR/part_f_screen.txt"
capture_screen part_f 06_filesystem_demo "PART F - LINUX FILESYSTEM DEMONSTRATION" "$OUT_DIR/part_f_screen.txt"

# Final summary.
{
    echo "CS207 evidence capture finished: $(date)"
    echo "Project folder: $ROOT_DIR"
    echo "Output folder: $OUT_DIR"
    echo
    for key in \
        "Part A environment information" \
        "Project default build" \
        "Part B scheduler tests" \
        "Part C compile" \
        "Part C 100-item run" \
        "Part C automated tests" \
        "Part D compile" \
        "Part D sample cases" \
        "Part D automated tests" \
        "Part E compile" \
        "Part E sample cases" \
        "Part E automated tests" \
        "Part F filesystem demo"; do
        printf '%-34s %s\n' "$key" "${RESULT[$key]:-NOT RUN}"
    done
    echo
    echo "Screenshots: $ROOT_DIR/screenshots/part_a through part_f"
    echo "Detailed logs: $OUT_DIR"
    echo
    echo "A REVIEW result is not a pass. Open its log and fix it before submission."
} > "$OUT_DIR/summary.txt"
capture_screen part_a 99_capture_summary "FINAL EVIDENCE CAPTURE SUMMARY" "$OUT_DIR/summary.txt"

printf '\nEvidence capture has finished.\n'
printf 'Screenshots: %s/screenshots/\n' "$ROOT_DIR"
printf 'Logs:        %s\n' "$OUT_DIR"
printf '\nPlease open the screenshots folder and check that the text is readable.\n'
printf 'Do not submit any section marked REVIEW or CHECK LOG until you have checked it.\n'
