# Part B — Observed scheduling results

Dataset: `tests/part_b/processes.csv` (6 processes, total CPU burst = 23 time units).

## Average metrics

| Algorithm | RR quantum | Avg. turnaround | Avg. waiting | Avg. response |
|---|---:|---:|---:|---:|
| FCFS | — | 11.83 | 8.00 | 8.00 |
| Non-preemptive SJF | — | **10.33** | **6.50** | 6.50 |
| Round Robin | 2 | 11.83 | 8.00 | **3.17** |
| Round Robin | 3 | 12.50 | 8.67 | 4.00 |

## Gantt timelines

- FCFS: `P1(0–8) → P2(8–12) → P3(12–14) → P4(14–15) → P5(15–20) → P6(20–23)`
- Non-preemptive SJF: `P1(0–8) → P4(8–9) → P3(9–11) → P6(11–14) → P2(14–18) → P5(18–23)`
- Round Robin, q=2: `P1(0–2) → P2(2–4) → P3(4–6) → P1(6–8) → P4(8–9) → P2(9–11) → P5(11–13) → P1(13–15) → P6(15–17) → P5(17–19) → P1(19–21) → P6(21–22) → P5(22–23)`
- Round Robin, q=3: `P1(0–3) → P2(3–6) → P3(6–8) → P4(8–9) → P1(9–12) → P5(12–15) → P2(15–16) → P6(16–19) → P1(19–21) → P5(21–23)`

## Interpretation

For this particular dataset, non-preemptive SJF produces the lowest average turnaround time (10.33) and waiting time (6.50). It can do this because, after P1 finishes, it chooses the shortest available job. It does not preempt P1 when shorter jobs arrive during P1's execution.

Round Robin with quantum 2 produces the lowest average response time (3.17). A process gets an early opportunity to use the CPU rather than waiting behind a long non-preemptive burst. This is useful for time-sharing and interactive workloads, although it does not minimize average waiting or turnaround time on this dataset.

Increasing the quantum from 2 to 3 changes the execution order and reduces the number of slices, but here it increases average turnaround (11.83 to 12.50), waiting (8.00 to 8.67), and response (3.17 to 4.00). A smaller quantum generally improves responsiveness but causes more context switches in a real operating system; a larger quantum reduces switching overhead but behaves more like FCFS and can worsen responsiveness. This simulator models scheduling time, not actual context-switch overhead.

No algorithm is universally best. Results depend on arrival patterns, burst lengths, workload goals, and quantum size.

## Process-level output

The complete process metric tables for FCFS, SJF, and Round Robin q=2 are in `part_b-scheduler-q2.txt`. The program prints process rows in original CSV order.

## Validation

Run `./tests/part_b/run_tests.sh` or `make test`. The test script checks the main six-process dataset, all-at-zero arrivals, initial CPU idle time, equal burst times, one process, non-preemptive SJF behavior, malformed CSV, duplicate PID, negative arrival, zero burst, invalid quantum, and the effect of changing the Round Robin quantum.
