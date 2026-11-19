# Part D - Banker's Algorithm

## What this program does

This program checks whether a resource-allocation state is safe. It reads the number of processes and resource types, then reads the Allocation matrix, the Maximum matrix and the Available vector.

The program calculates the remaining Need of each process using:

`Need = Maximum - Allocation`

It then tries to find a process whose remaining Need can be covered by the resources currently available. If that process finishes, its allocated resources are treated as available again. The program keeps doing this until every process can finish or no more process can be selected.

## Input format

The first line has two numbers: number of processes, then number of resource types.

After that, enter the Allocation matrix, one row per process. Enter the Maximum matrix in the same way. The final line contains the Available values.

For example, `tests/part_d/safe.txt` starts with:

```text
5 3
```

That means there are five processes and three resource types. The next five rows are Allocation, the next five are Maximum, and the last row is Available.

## Run it

```bash
make bankers
./bin/bankers tests/part_d/safe.txt
./bin/bankers tests/part_d/unsafe.txt
```

You can also run it without a file and type the same numbers in the terminal:

```bash
./bin/bankers
```

## Test cases and what they show

- `safe.txt`: the program should print `State: SAFE` and one safe sequence.
- `unsafe.txt`: neither process can get the resources it still needs, so the program should print `State: UNSAFE`.
- `multiple_safe_sequences.txt`: both processes can finish first, so more than one safe order is possible. The program prints one of them.

The unsafe case is not described as an existing deadlock. It only means that the system cannot guarantee that all processes can finish from that state.

## The four conditions needed for deadlock

1. **Mutual exclusion:** at least one resource can be used by only one process at a time.
2. **Hold and wait:** a process keeps the resources it already has while waiting for more.
3. **No preemption:** resources are not forcibly taken away; the process releases them itself.
4. **Circular wait:** a group of processes is waiting in a cycle, where each one needs a resource held by the next process.

All four conditions must be present for a deadlock to happen.

## Prevention, avoidance, detection and recovery

- **Prevention:** arrange the system so at least one of the four deadlock conditions cannot happen.
- **Avoidance:** check a resource request before granting it. The Banker's algorithm is an example because it only accepts a request when the resulting state stays safe.
- **Detection:** allow resource allocation to happen, then check later whether a deadlock has occurred.
- **Recovery:** take action after detection, for example by stopping a process or taking back a resource where the system allows it.

## What I noticed

A state can be unsafe even when the processes are not deadlocked at that exact moment. The important point is that an unsafe state does not give us a safe order in which every process is guaranteed to finish.
