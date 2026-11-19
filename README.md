# CS207 Operating Systems Design - Assignment 1

This is our group assignment for CS207. We have split the work so that one person handles Parts A, B and C, and the other person handles Parts D, E and F. We are keeping the code, test inputs and instructions in one repository so both of us can run the same work.

The programs are written in C. The small Part F demonstration is a Bash script because that part is about using Linux commands.

## What is in the repository

```text
src/
  part_b/                 CPU scheduling program (existing work)
  part_c/                 Producer-consumer program (existing work)
  part_d/bankers.c        Banker's safety algorithm
  part_e/
    page_replacement.c    FIFO and LRU
    disk_scheduling.c     FCFS and SSTF

tests/
  part_b/                 Process input used by Part B
  part_c/                 Producer-consumer tests
  part_d/                 Banker's test cases
  part_e/                 Page and disk test cases

scripts/
  bootstrap-ubuntu.sh     Installs the basic tools in Ubuntu
  capture-environment.sh Saves the system information for Part A
  part_f_demo.sh         Creates and checks a sample directory tree

docs/                     Simple explanations of the programs
report/                   Report template or final report
outputs/                  Text output captured while testing
screenshots/               Screenshots taken in the Ubuntu VM
```

For the exact copy steps, see [`APPLY_INSTRUCTIONS.md`](APPLY_INSTRUCTIONS.md). The short handoff for the person doing Parts D, E and F is in [`PARTNER_HANDOFF.md`](PARTNER_HANDOFF.md).

## Before running the programs

The assignment asks us to use an Ubuntu VM made with Oracle VirtualBox. Open the Ubuntu VM and open a terminal. Clone this repository there, or pull the latest changes if you already cloned it.

```bash
git clone https://github.com/Uscout07/CS207_Operating_Systems_Project.git
cd CS207_Operating_Systems_Project
```

If the repository is already on your machine, use `cd` to enter its folder and run:

```bash
git pull
```

Install the required tools once:

```bash
bash scripts/bootstrap-ubuntu.sh
```

## Build the programs

From the main project folder:

```bash
make clean
make
```

The build should create these programs in `bin/`:

- `scheduler` - Part B
- `producer_consumer` - Part C
- `bankers` - Part D
- `page_replacement` - Part E
- `disk_scheduling` - Part E

If the root Makefile already had Part B and Part C targets, keep them. The `Makefile.part_de` file adds the Part D and Part E targets without replacing the earlier ones.

## How to run each part

### Part A - Ubuntu setup

Run these from the project folder inside Ubuntu:

```bash
bash scripts/capture-environment.sh
```

It records information such as the Ubuntu kernel, CPU, memory and disk. Also take a screenshot of the running Ubuntu VM and terminal. Put the screenshots in `screenshots/part_a/`.

### Part B - CPU scheduling

The scheduler already exists in `src/part_b/`. It has the FCFS, non-preemptive SJF and Round Robin work. Keep using the input format and command that are already in the Part B source and tests. The Part D/E additions do not change that program.

### Part C - Producer and consumer

Run the normal 100-item example:

```bash
make part-c
./bin/producer_consumer 100
```

Run the automated Part C tests:

```bash
bash tests/part_c/run_tests.sh
```

The program should finish with `Verification: PASS` and `Buffer bounds: PASS`.

### Part D - Banker's algorithm

The input file contains the process count and resource count, then the Allocation matrix, the Maximum matrix and the Available vector.

```bash
make bankers
./bin/bankers tests/part_d/safe.txt
./bin/bankers tests/part_d/unsafe.txt
./bin/bankers tests/part_d/multiple_safe_sequences.txt
```

Run all Part D checks:

```bash
make test-part-d
```

### Part E - Page replacement and disk scheduling

Page replacement input starts with the number of frames and number of page references. The next line contains the page-reference string.

```bash
make page-replacement
./bin/page_replacement tests/part_e/pages_case1.txt
./bin/page_replacement tests/part_e/pages_case2_fifo_lru_difference.txt
```

Disk scheduling input starts with the initial head position and number of requests. The next line contains the request queue.

```bash
make disk-scheduling
./bin/disk_scheduling tests/part_e/disk_case1.txt
./bin/disk_scheduling tests/part_e/disk_case2.txt
```

Run all Part E checks:

```bash
make test-part-e
```

### Part F - File system demonstration

Run:

```bash
make part-f-demo
```

This creates a directory called `part_f_demo/` with sample folders and files. It prints absolute and relative paths, file permissions, ownership, metadata and a few running processes. The comparison of Linux and Windows is in `docs/part_f_filesystem.md`.

## Run the tests together

The `make test-all` command runs the Part B test script if `tests/part_b/run_tests.sh` is present, then runs the repository's existing `make test` target, followed by the Part D and Part E tests. If your Part B test script has a different name, run it separately using the command already used in that part:

```bash
make test-all
```

To run the Part D and Part E tests separately, use `make test-part-d` and `make test-part-e`.

## Save output for the report

Run the programs from inside the Ubuntu VM and save the output. These files are useful when writing the report, but they do not replace the screenshots requested in the assignment.

```bash
mkdir -p outputs screenshots/part_d screenshots/part_e screenshots/part_f

./bin/bankers tests/part_d/safe.txt | tee outputs/part_d_safe.txt
./bin/bankers tests/part_d/unsafe.txt | tee outputs/part_d_unsafe.txt

./bin/page_replacement tests/part_e/pages_case1.txt | tee outputs/part_e_pages_case1.txt
./bin/page_replacement tests/part_e/pages_case2_fifo_lru_difference.txt | tee outputs/part_e_pages_case2.txt

./bin/disk_scheduling tests/part_e/disk_case1.txt | tee outputs/part_e_disk_case1.txt
./bin/disk_scheduling tests/part_e/disk_case2.txt | tee outputs/part_e_disk_case2.txt

bash scripts/part_f_demo.sh | tee outputs/part_f_filesystem.txt
```

Take your own screenshots after running the commands in Ubuntu. Save them in the matching `screenshots/part_*/` folder. Do not use screenshots from another person's computer because the username, paths and system information will be different.

## Who did which part

Fill in the real names and roll numbers before submitting:

| Part | Student | Work |
|---|---|---|
| A, B, C | Student 1: __________________ | VM setup, CPU scheduling, producer-consumer |
| D, E, F | Student 2: __________________ | Banker's algorithm, page replacement, disk scheduling, filesystem case study |
| Integration and report | Both | Testing, README, report and final ZIP |

Also update `docs/contributions.md` and the contribution section in the report with the actual work and commits. Do not leave the placeholders in the final submission.

## A few things to remember

- Run the final build and tests in the Ubuntu VM, not only on Windows.
- The output order of Part C can change because the threads do not always run in the same order. The final verification should still pass.
- The Banker's program prints one safe sequence. There can be more than one valid safe sequence.
- The page and disk results depend on the input file. Use the supplied files when comparing the algorithms.
- Part F creates sample files under `part_f_demo/`. It is okay to run the script more than once.
- Before making the final ZIP, check that the report, source code, README, test inputs, outputs and your own screenshots are present.
