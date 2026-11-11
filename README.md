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
