# Part E - Page Replacement and Disk Scheduling

This part has two small programs. One compares page replacement methods and the other compares disk scheduling methods. Both programs read their input from a text file, so the same test can be run again without typing the values every time.

## 1. FIFO and LRU page replacement

The input file contains the number of frames, the number of page references, and then the page reference string.

Example:

```text
3 8
1 2 3 1 4 1 2 5
```

This means there are three frames and eight page references.

Run it with:

```bash
make page-replacement
./bin/page_replacement tests/part_e/pages_case1.txt
./bin/page_replacement tests/part_e/pages_case2_fifo_lru_difference.txt
```

The program prints the frame contents after every page reference and marks it as a HIT or FAULT.

- **FIFO:** the page that entered memory first is removed first when a new page needs space.
- **LRU:** the page that has not been used for the longest time is removed.

The second test is included because it clearly shows a difference: with three frames, FIFO has 7 page faults and LRU has 6 for that reference string.

## 2. FCFS and SSTF disk scheduling

The input file contains the starting head position, the number of requests, and then the request queue.

Example:

```text
50 4
15 90 20 80
```

Run it with:

```bash
make disk-scheduling
./bin/disk_scheduling tests/part_e/disk_case1.txt
./bin/disk_scheduling tests/part_e/disk_case2.txt
```

The program prints the order in which requests are handled and the movement from one position to the next.

- **FCFS:** requests are handled in the same order in which they were received.
- **SSTF:** the next request is the one closest to the current head position.

For the first test, the total movement is 640 tracks with FCFS and 236 tracks with SSTF. For the second test, it is 240 tracks with FCFS and 110 tracks with SSTF.

## Why the lower number is not always the best choice

The results depend on the input. LRU does better in the second page test, but this does not mean that it will always have fewer faults for every possible reference string. FIFO is simple, while LRU needs to remember when pages were last used.

SSTF usually reduces movement in these examples because it picks a nearby request. But it can keep delaying a request that is far away if nearer requests keep arriving. FCFS is not always the shortest route, but it handles requests in their arrival order and does not keep changing the order to favour nearby requests.

Also, the disk program only adds up the distance moved by the head. It does not model every part of real disk access time.

## Test commands

```bash
make test-part-e
```
