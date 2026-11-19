# CS207 Operating Systems Design - Assignment 1

**Student 1:** [Name and roll number]  
**Student 2:** [Name and roll number]  
**Environment:** Oracle VirtualBox with Ubuntu [write the version used]  
**Date:** [Submission date]

## 1. Introduction

In this assignment, we worked with a few important operating system ideas. We first set up an Ubuntu environment and then wrote programs for CPU scheduling, process synchronization, deadlock avoidance, memory management and disk scheduling. We also used Linux commands to look at directories, file permissions and running processes.

We divided the work between two members. Student 1 worked on Parts A, B and C. Student 2 worked on Parts D, E and F. Both members helped with testing and putting the final files together.

## 2. Environment setup (Part A)

- Host operating system: [fill this in]
- VirtualBox version: [fill this in]
- Ubuntu version: [fill this in]
- RAM assigned to VM: [fill this in]
- Number of virtual CPUs: [fill this in]
- Virtual disk size: [fill this in]
- Compiler version: [paste `gcc --version`]

**Commands used:**

```bash
uname -a
lscpu
free -h
df -h
gcc --version
```

**Host OS and guest OS:** The host OS is the operating system running on the physical laptop. The guest OS is the Ubuntu system running inside VirtualBox. One advantage of a VM is that it gives us a separate environment without installing Ubuntu directly over Windows. One limitation is that the VM shares the laptop's RAM and CPU, so it can run slower when the laptop has limited resources.

**Screenshot:** [Add the actual VM and terminal screenshot here.]

## 3. CPU scheduling (Part B)

We implemented FCFS, non-preemptive SJF and Round Robin. The input contains a process ID, arrival time and burst time. We tested at least six processes, including processes with the same arrival time and one that arrives after time zero.

**Test input:** [Name the file used.]  
**Round Robin time quantum:** [Value]

| Algorithm | Average turnaround time | Average waiting time | Average response time |
|---|---:|---:|---:|
| FCFS | [value] | [value] | [value] |
| Non-preemptive SJF | [value] | [value] | [value] |
| Round Robin | [value] | [value] | [value] |

**What we noticed:** [Explain which result was best for this particular input and why. Do not say that one algorithm is always best.]

**Screenshot/output:** [Add the real output and screenshot.]

## 4. Producer-consumer synchronization (Part C)

We used two producer threads and two consumer threads. They share a circular buffer with five slots. A mutex protects the shared buffer, and two counting semaphores keep track of empty and filled slots.

We ran the program with at least 100 items. The program checks that every item is produced and consumed exactly once and that the buffer is empty at the end.

**Test item count:** [Value]  
**Result:** [Paste the final verification lines from the real run.]  
**Screenshot:** [Add the real terminal screenshot.]

**Concepts:** A critical section is the part of the program that uses shared data. A race condition can happen when threads update the same data without correct synchronization. The mutex gives mutual exclusion. The semaphores stop a producer from adding to a full buffer and stop a consumer from taking from an empty buffer.

**Incorrect design:** [Briefly describe the version without a mutex and explain how two producers or consumers could update the same buffer position.]

## 5. Deadlock avoidance (Part D)

We used the Banker's safety algorithm. The program reads Allocation, Maximum and Available values. It calculates Need as Maximum minus Allocation and tries to find an order in which every process can finish.

| Test | Expected result | Observed result |
|---|---|---|
| Safe state | A safe sequence should be printed | [fill in] |
| Unsafe state | No safe sequence should be printed | [fill in] |
| Multiple safe sequences | The state should still be safe | [fill in] |

**Safe sequence from the supplied safe test:** [Paste the sequence from your run.]

An unsafe state does not automatically mean that the system is already deadlocked. It means that the algorithm cannot guarantee a safe order for all processes from that state.

**Four deadlock conditions:** mutual exclusion, hold and wait, no preemption and circular wait. [Explain each briefly in your own words.]

**Prevention, avoidance, detection and recovery:** [Use the explanation in `docs/part_d_bankers.md`, but rewrite it in your own words after reading it.]

**Screenshot/output:** [Add the real run.]

## 6. Memory management and disk scheduling (Part E)

### Page replacement

We tested FIFO and LRU with two reference strings. The program displays the frame contents after each reference and counts page faults.

| Test | Frames | FIFO faults | LRU faults |
|---|---:|---:|---:|
| Case 1 | 3 | [fill in] | [fill in] |
| Case 2 | 3 | [fill in] | [fill in] |

For the supplied second test, the expected counts are 7 FIFO faults and 6 LRU faults. Confirm these from your own terminal run.

### Disk scheduling

We tested FCFS and SSTF with two request queues. The program displays the order serviced and the total head movement.

| Test | Initial head | FCFS movement | SSTF movement |
|---|---:|---:|---:|
| Case 1 | 53 | [fill in] | [fill in] |
| Case 2 | 50 | [fill in] | [fill in] |

For the supplied inputs, the expected totals are 640 and 236 tracks for Case 1, and 240 and 110 tracks for Case 2. Confirm these with your own runs.

**Discussion:** [Explain why a lower number in one test does not prove that the algorithm is always better. Mention that FIFO/LRU depend on the page reference string and SSTF can keep postponing far-away requests.]

**Screenshots/output:** [Add real outputs and screenshots.]

## 7. File system and case study (Part F)

We ran `scripts/part_f_demo.sh` in Ubuntu. It created a sample directory tree and printed absolute and relative paths, permissions, owner, group, file sizes and running processes.

**Actual directory path:** [Paste the path printed by your VM.]  
**Current user and group:** [Paste the output of `id`.]

| Topic | Linux observation | Windows comparison |
|---|---|---|
| Process management | [Commands used and what they showed] | Task Manager / PowerShell `Get-Process` |
| File-system organization | [Root directory and paths] | Drive letters and NTFS |
| Permissions | [Owner/group/other permissions shown by `ls -l` or `stat`] | Windows access control lists and UAC |
| Command-line tools | Bash commands such as `pwd`, `ls`, `find`, `stat`, `ps` | PowerShell and Command Prompt |

The Windows column is a comparison of the usual tools and organization. Be clear about which commands you actually ran in Ubuntu.

**Screenshot:** [Add the real directory listing and `stat` output.]

## 8. Conclusion

[Write a short paragraph about what you understood from the assignment. Mention one thing that was difficult and how you checked that the programs were working.]

## 9. Contributions

| Member | Parts completed | Other work |
|---|---|---|
| Student 1: [name] | A, B, C | [actual integration, tests or report work] |
| Student 2: [name] | D, E, F | [actual integration, tests or report work] |

## 10. References

- CS207 Operating Systems Design - Assignment 1 handout.
- Course notes or textbook used for the operating-system concepts: [add the actual title and edition].
- Ubuntu manual pages used while testing: `man pthreads`, `man sem_overview`, `man stat`, `man chmod` and other pages actually consulted.

---

Before exporting this report to PDF, replace every square-bracket note, add the actual screenshots, and make sure the numbers match the output files saved from your Ubuntu VM. Keep the final report within the assignment's suggested maximum of 12 pages.
