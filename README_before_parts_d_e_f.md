# Part B — Process creation and CPU scheduling simulator

## Requirements

On Linux (Ubuntu/WSL included), install GCC and Make:

```bash
sudo apt update
sudo apt install build-essential
```

## Input format

The CSV must have this exact header:

```csv
PID,arrival_time,burst_time
```

Each following row contains a unique positive PID, a non-negative integer arrival time, and a strictly positive integer CPU burst time. Blank lines are ignored. Values are limited to 10^12 to keep simulated-time arithmetic bounded.

## Build and run

From the project root:

```bash
make
./bin/scheduler tests/part_b/processes.csv 2
```

The optional second argument is the positive Round Robin time quantum; it defaults to 2 when omitted. The program runs FCFS, non-preemptive SJF, and Round Robin independently from the same input.

To save output:

```bash
./bin/scheduler tests/part_b/processes.csv 2 | tee outputs/part_b-scheduler-q2.txt
```

To test a different quantum:

```bash
./bin/scheduler tests/part_b/processes.csv 3
```

## Implementation notes

- `CPU_IDLE_PID` is `-1`; it is printed as `IDLE` in the timeline.
- FCFS ties use original input order after arrival time.
- Non-preemptive SJF ties use earlier arrival, then original input order.
- Round Robin enqueues arrivals that occurred during a time slice before re-enqueuing the process whose quantum expired.
- Process metric tables preserve CSV input order.
- Each algorithm receives a fresh process-array copy.

## Linux terminal screenshots

Run the program in a terminal with a readable font size, then capture the terminal using your desktop screenshot shortcut. Save screenshots under `screenshots/part_b/`. For example, on GNOME use `Print Screen`; from a terminal you can also use `gnome-screenshot` if installed.


# Part C — POSIX Threads and Producer–Consumer Synchronization

Part C is implemented in `src/part_c/producer_consumer.c`. It uses two producer threads, two consumer threads, a circular buffer of capacity 5, a pthread mutex, and the POSIX counting semaphores `empty_slots` and `full_slots`.

## Build and run

Add this line at the end of the existing root `Makefile` once:

```make
include Makefile.part_c
```

Then run:

```bash
make part-c
./bin/producer_consumer
./bin/producer_consumer 250
make test-part-c
```

The default execution processes 100 items. An optional item count from 100 to 1,000,000 can be supplied. The program logs each producer and consumer operation and verifies that every item was consumed exactly once.

For a saved run:

```bash
mkdir -p outputs screenshots/part_c
./bin/producer_consumer 100 | tee outputs/part_c-producer-consumer.txt
```

See [`docs/part_c_producer_consumer.md`](docs/part_c_producer_consumer.md) for the algorithm, synchronization explanation, deliberately incorrect pseudocode, tests, and report material.
