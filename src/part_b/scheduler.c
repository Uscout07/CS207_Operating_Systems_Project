

#define _POSIX_C_SOURCE 200809L
#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CPU_IDLE_PID (-1)
#define MAX_TIME_VALUE INT64_C(1000000000000)
#define MAX_LINE_LENGTH 4096

typedef struct {
  int pid;
  int64_t arrival_time;
  int64_t burst_time;
  int64_t remaining_time;
  int64_t first_start_time;
  int64_t completion_time;
  int64_t turnaround_time;
  int64_t waiting_time;
  int64_t response_time;
  size_t input_order;
  bool started;
  bool completed;
  bool enqueued;
} Process;

typedef struct {
  int pid;
  int64_t start_time;
  int64_t end_time;
} TimelineEvent;

typedef struct {
  TimelineEvent *items;
  size_t count;
  size_t capacity;
} Timeline;

typedef struct {
  size_t *items;
  size_t capacity;
  size_t head;
  size_t tail;
  size_t count;
} ReadyQueue;

static char *trim(char *s) {
  while (isspace((unsigned char)*s))
    s++;
  if (*s == '\0')
    return s;
  char *end = s + strlen(s) - 1;
  while (end > s && isspace((unsigned char)*end))
    *end-- = '\0';
  return s;
}

static bool parse_int64_field(const char *text, int64_t *out) {
  char *end = NULL;
  errno = 0;
  long long value = strtoll(text, &end, 10);
  if (text == end || errno == ERANGE || value < 0 || value > MAX_TIME_VALUE)
    return false;
  while (*end && isspace((unsigned char)*end))
    end++;
  if (*end != '\0')
    return false;
  *out = (int64_t)value;
  return true;
}

static bool parse_process_line(char *line, Process *out, size_t input_order,
                               const char *path, size_t line_number) {
  char *fields[3];
  char *cursor = line;
  for (size_t i = 0; i < 3; i++) {
    fields[i] = cursor;
    char *comma = strchr(cursor, ',');
    if (i < 2) {
      if (!comma) {
        fprintf(stderr, "%s:%zu: expected exactly 3 comma-separated fields\n",
                path, line_number);
        return false;
      }
      *comma = '\0';
      cursor = comma + 1;
    } else if (comma) {
      fprintf(stderr, "%s:%zu: too many CSV fields\n", path, line_number);
      return false;
    }
    fields[i] = trim(fields[i]);
    if (*fields[i] == '\0') {
      fprintf(stderr, "%s:%zu: empty CSV field\n", path, line_number);
      return false;
    }
  }

  char *pid_end = NULL;
  errno = 0;
  long pid_value = strtol(fields[0], &pid_end, 10);
  while (pid_end && *pid_end && isspace((unsigned char)*pid_end))
    pid_end++;
  if (errno == ERANGE || fields[0] == pid_end || (pid_end && *pid_end) ||
      pid_value <= 0 || pid_value > INT_MAX) {
    fprintf(stderr, "%s:%zu: invalid PID '%s' (must be 1..%d)\n", path,
            line_number, fields[0], INT_MAX);
    return false;
  }

  int64_t arrival, burst;
  if (!parse_int64_field(fields[1], &arrival)) {
    fprintf(stderr, "%s:%zu: invalid arrival_time '%s'\n", path, line_number,
            fields[1]);
    return false;
  }
  if (!parse_int64_field(fields[2], &burst) || burst == 0) {
    fprintf(stderr, "%s:%zu: invalid burst_time '%s' (must be positive)\n",
            path, line_number, fields[2]);
    return false;
  }

  *out = (Process){.pid = (int)pid_value,
                   .arrival_time = arrival,
                   .burst_time = burst,
                   .remaining_time = burst,
                   .first_start_time = -1,
                   .completion_time = -1,
                   .input_order = input_order,
                   .started = false,
                   .completed = false,
                   .enqueued = false};
  return true;
}

static bool validate_processes(const Process *processes, size_t count,
                               const char *path) {
  if (count == 0) {
    fprintf(stderr, "%s: input contains no processes\n", path);
    return false;
  }
  int64_t total_burst = 0;
  for (size_t i = 0; i < count; i++) {
    if (processes[i].arrival_time < 0 || processes[i].burst_time <= 0) {
      fprintf(stderr, "%s: invalid values for PID %d\n", path,
              processes[i].pid);
      return false;
    }
    if (total_burst > MAX_TIME_VALUE - processes[i].burst_time) {
      fprintf(stderr, "%s: total CPU burst exceeds supported time range\n",
              path);
      return false;
    }
    total_burst += processes[i].burst_time;
    for (size_t j = i + 1; j < count; j++) {
      if (processes[i].pid == processes[j].pid) {
        fprintf(stderr, "%s: duplicate PID %d\n", path, processes[i].pid);
        return false;
      }
    }
  }
  return true;
}

static bool load_processes(const char *path, Process **out_processes,
                           size_t *out_count) {
  FILE *file = fopen(path, "r");
  if (!file) {
    fprintf(stderr, "cannot open '%s': %s\n", path, strerror(errno));
    return false;
  }

  Process *items = NULL;
  size_t count = 0, capacity = 0, line_number = 0;
  char line[MAX_LINE_LENGTH];
  bool header_seen = false, ok = true;

  while (fgets(line, sizeof line, file)) {
    line_number++;
    if (!strchr(line, '\n') && !feof(file)) {
      fprintf(stderr, "%s:%zu: line exceeds %d characters\n", path, line_number,
              MAX_LINE_LENGTH - 1);
      ok = false;
      break;
    }
    char *row = trim(line);
    if (*row == '\0')
      continue;
    if (!header_seen) {
      char expected[] = "PID,arrival_time,burst_time";
      if (strcmp(row, expected) != 0) {
        fprintf(stderr, "%s:%zu: expected header: %s\n", path, line_number,
                expected);
        ok = false;
        break;
      }
      header_seen = true;
      continue;
    }

    Process process;
    if (!parse_process_line(row, &process, count, path, line_number)) {
      ok = false;
      break;
    }
    if (count == capacity) {
      size_t new_capacity = capacity ? capacity * 2 : 8;
      if (new_capacity < capacity || new_capacity > SIZE_MAX / sizeof *items) {
        fprintf(stderr, "%s:%zu: process table is too large\n", path,
                line_number);
        ok = false;
        break;
      }
      Process *grown = realloc(items, new_capacity * sizeof *items);
      if (!grown) {
        fprintf(stderr, "out of memory while loading '%s'\n", path);
        ok = false;
        break;
      }
      items = grown;
      capacity = new_capacity;
    }
    items[count++] = process;
  }

  if (ferror(file)) {
    fprintf(stderr, "error reading '%s'\n", path);
    ok = false;
  }
  fclose(file);

  if (ok && !header_seen) {
    fprintf(stderr, "%s: missing CSV header\n", path);
    ok = false;
  }
  if (ok)
    ok = validate_processes(items, count, path);
  if (!ok) {
    free(items);
    return false;
  }
  *out_processes = items;
  *out_count = count;
  return true;
}

static Process *copy_or_reset_processes(const Process *source, size_t count) {
  if (count > SIZE_MAX / sizeof(Process))
    return NULL;
  Process *copy = malloc(count * sizeof *copy);
  if (!copy)
    return NULL;
  for (size_t i = 0; i < count; i++) {
    copy[i] = source[i];
    copy[i].remaining_time = copy[i].burst_time;
    copy[i].first_start_time = -1;
    copy[i].completion_time = -1;
    copy[i].turnaround_time = 0;
    copy[i].waiting_time = 0;
    copy[i].response_time = 0;
    copy[i].started = false;
    copy[i].completed = false;
    copy[i].enqueued = false;
  }
  return copy;
}

static void free_processes(Process *processes) { free(processes); }

static bool append_event(Timeline *timeline, int pid, int64_t start,
                         int64_t end) {
  if (end <= start)
    return true;
  /* Merge adjacent intervals for the same PID, including consecutive idle
   * spans. */
  if (timeline->count > 0) {
    TimelineEvent *last = &timeline->items[timeline->count - 1];
    if (last->pid == pid && last->end_time == start) {
      last->end_time = end;
      return true;
    }
  }
  if (timeline->count == timeline->capacity) {
    size_t new_capacity = timeline->capacity ? timeline->capacity * 2 : 16;
    if (new_capacity < timeline->capacity ||
        new_capacity > SIZE_MAX / sizeof *timeline->items)
      return false;
    TimelineEvent *grown =
        realloc(timeline->items, new_capacity * sizeof *timeline->items);
    if (!grown)
      return false;
    timeline->items = grown;
    timeline->capacity = new_capacity;
  }
  timeline->items[timeline->count++] = (TimelineEvent){pid, start, end};
  return true;
}

static void record_first_start(Process *process, int64_t current_time) {
  if (!process->started) {
    process->first_start_time = current_time;
    process->started = true;
  }
}

static bool calculate_metrics(Process *processes, size_t count) {
  for (size_t i = 0; i < count; i++) {
    Process *p = &processes[i];
    if (!p->completed || p->completion_time < p->arrival_time || !p->started ||
        p->first_start_time < p->arrival_time) {
      fprintf(stderr, "internal scheduling error for PID %d\n", p->pid);
      return false;
    }
    p->turnaround_time = p->completion_time - p->arrival_time;
    p->waiting_time = p->turnaround_time - p->burst_time;
    p->response_time = p->first_start_time - p->arrival_time;
    if (p->waiting_time < 0 || p->response_time < 0 ||
        p->response_time > p->waiting_time) {
      fprintf(stderr, "internal metric invariant failed for PID %d\n", p->pid);
      return false;
    }
  }
  return true;
}

static void print_gantt_chart(const Timeline *timeline) {
  puts("\nGantt timeline:");
  if (timeline->count == 0) {
    puts("(empty)");
    return;
  }
  for (size_t i = 0; i < timeline->count; i++) {
    const TimelineEvent *e = &timeline->items[i];
    if (e->pid == CPU_IDLE_PID)
      printf("[IDLE: %" PRId64 "-%" PRId64 "]", e->start_time, e->end_time);
    else
      printf("[P%d: %" PRId64 "-%" PRId64 "]", e->pid, e->start_time,
             e->end_time);
    if (i + 1 < timeline->count)
      printf(" -> ");
  }
  putchar('\n');
}

static void print_process_table(const Process *processes, size_t count) {
  puts("\nProcess metrics (original input order):");
  printf("%-6s %-8s %-8s %-10s %-11s %-8s %-9s\n", "PID", "Arrival", "Burst",
         "Complete", "Turnaround", "Waiting", "Response");
  for (size_t i = 0; i < count; i++) {
    const Process *p = &processes[i];
    printf("%-6d %-8" PRId64 " %-8" PRId64 " %-10" PRId64 " %-11" PRId64
           " %-8" PRId64 " %-9" PRId64 "\n",
           p->pid, p->arrival_time, p->burst_time, p->completion_time,
           p->turnaround_time, p->waiting_time, p->response_time);
  }
}

static void print_averages(const Process *processes, size_t count) {
  long double turnaround = 0, waiting = 0, response = 0;
  for (size_t i = 0; i < count; i++) {
    turnaround += processes[i].turnaround_time;
    waiting += processes[i].waiting_time;
    response += processes[i].response_time;
  }
  printf("\nAverages: turnaround = %.2Lf, waiting = %.2Lf, response = %.2Lf\n",
         turnaround / (long double)count, waiting / (long double)count,
         response / (long double)count);
}

static bool next_arrival(const Process *p, size_t count, int64_t current_time,
                         int64_t *arrival_out) {
  bool found = false;
  int64_t earliest = INT64_MAX;
  for (size_t i = 0; i < count; i++) {
    if (!p[i].completed && p[i].arrival_time > current_time &&
        p[i].arrival_time < earliest) {
      earliest = p[i].arrival_time;
      found = true;
    }
  }
  if (found)
    *arrival_out = earliest;
  return found;
}

static bool run_fcfs(Process *p, size_t count, Timeline *timeline) {
  int64_t current_time = 0;
  size_t completed = 0;
  while (completed < count) {
    size_t chosen = count;
    for (size_t i = 0; i < count; i++) {
      if (p[i].completed || p[i].arrival_time > current_time)
        continue;
      if (chosen == count || p[i].arrival_time < p[chosen].arrival_time ||
          (p[i].arrival_time == p[chosen].arrival_time &&
           p[i].input_order < p[chosen].input_order))
        chosen = i;
    }
    if (chosen == count) {
      int64_t next;
      if (!next_arrival(p, count, current_time, &next))
        return false;
      if (!append_event(timeline, CPU_IDLE_PID, current_time, next))
        return false;
      current_time = next;
      continue;
    }
    Process *job = &p[chosen];
    record_first_start(job, current_time);
    if (current_time > MAX_TIME_VALUE - job->burst_time)
      return false;
    int64_t end = current_time + job->burst_time;
    if (!append_event(timeline, job->pid, current_time, end))
      return false;
    current_time = end;
    job->remaining_time = 0;
    job->completion_time = current_time;
    job->completed = true;
    completed++;
  }
  return calculate_metrics(p, count);
}

static bool run_sjf(Process *p, size_t count, Timeline *timeline) {
  int64_t current_time = 0;
  size_t completed = 0;
  while (completed < count) {
    size_t chosen = count;
    for (size_t i = 0; i < count; i++) {
      if (p[i].completed || p[i].arrival_time > current_time)
        continue;
      if (chosen == count || p[i].burst_time < p[chosen].burst_time ||
          (p[i].burst_time == p[chosen].burst_time &&
           (p[i].arrival_time < p[chosen].arrival_time ||
            (p[i].arrival_time == p[chosen].arrival_time &&
             p[i].input_order < p[chosen].input_order))))
        chosen = i;
    }
    if (chosen == count) {
      int64_t next;
      if (!next_arrival(p, count, current_time, &next))
        return false;
      if (!append_event(timeline, CPU_IDLE_PID, current_time, next))
        return false;
      current_time = next;
      continue;
    }
    Process *job = &p[chosen];
    record_first_start(job, current_time);
    if (current_time > MAX_TIME_VALUE - job->burst_time)
      return false;
    int64_t end = current_time + job->burst_time;
    if (!append_event(timeline, job->pid, current_time, end))
      return false;
    current_time = end;
    job->remaining_time = 0;
    job->completion_time = current_time;
    job->completed = true;
    completed++;
  }
  return calculate_metrics(p, count);
}

static bool queue_init(ReadyQueue *q, size_t capacity) {
  q->items = malloc(capacity * sizeof *q->items);
  if (!q->items)
    return false;
  q->capacity = capacity;
  q->head = q->tail = q->count = 0;
  return true;
}

static void queue_free(ReadyQueue *q) { free(q->items); }

static bool enqueue(ReadyQueue *q, size_t value) {
  if (q->count == q->capacity)
    return false;
  q->items[q->tail] = value;
  q->tail = (q->tail + 1) % q->capacity;
  q->count++;
  return true;
}

static bool dequeue(ReadyQueue *q, size_t *value) {
  if (q->count == 0)
    return false;
  *value = q->items[q->head];
  q->head = (q->head + 1) % q->capacity;
  q->count--;
  return true;
}

static bool enqueue_arrivals(Process *p, size_t count, int64_t current_time,
                             ReadyQueue *q) {
  for (size_t i = 0; i < count; i++) {
    if (!p[i].completed && !p[i].enqueued &&
        p[i].arrival_time <= current_time) {
      if (!enqueue(q, i))
        return false;
      p[i].enqueued = true;
    }
  }
  return true;
}

static bool run_round_robin(Process *p, size_t count, int64_t quantum,
                            Timeline *timeline) {
  ReadyQueue queue = {0};
  if (!queue_init(&queue, count))
    return false;
  int64_t current_time = 0;
  size_t completed = 0;
  bool ok = true;

  while (completed < count && ok) {
    ok = enqueue_arrivals(p, count, current_time, &queue);
    if (!ok)
      break;
    if (queue.count == 0) {
      int64_t next;
      if (!next_arrival(p, count, current_time, &next)) {
        ok = false;
        break;
      }
      if (!append_event(timeline, CPU_IDLE_PID, current_time, next)) {
        ok = false;
        break;
      }
      current_time = next;
      continue;
    }

    size_t index;
    if (!dequeue(&queue, &index)) {
      ok = false;
      break;
    }
    Process *job = &p[index];
    /* Keep the running process marked as reserved so arrival scanning
       cannot enqueue it while its time slice is executing. */
    job->enqueued = true;
    record_first_start(job, current_time);
    int64_t duration =
        job->remaining_time < quantum ? job->remaining_time : quantum;
    if (current_time > MAX_TIME_VALUE - duration) {
      ok = false;
      break;
    }
    int64_t end = current_time + duration;
    if (!append_event(timeline, job->pid, current_time, end)) {
      ok = false;
      break;
    }
    current_time = end;
    job->remaining_time -= duration;

    /* Newly arrived jobs enter the queue before the preempted job. */
    ok = enqueue_arrivals(p, count, current_time, &queue);
    if (!ok)
      break;
    job->enqueued = false;
    if (job->remaining_time == 0) {
      job->completion_time = current_time;
      job->completed = true;
      completed++;
    } else {
      if (!enqueue(&queue, index)) {
        ok = false;
        break;
      }
      job->enqueued = true;
    }
  }

  queue_free(&queue);
  if (!ok)
    return false;
  return calculate_metrics(p, count);
}

static bool parse_quantum(const char *arg, int64_t *quantum) {
  int64_t value;
  if (!parse_int64_field(arg, &value) || value == 0)
    return false;
  *quantum = value;
  return true;
}

static bool run_and_print(const char *name, const Process *original,
                          size_t count, int algorithm, int64_t quantum) {
  Process *copy = copy_or_reset_processes(original, count);
  if (!copy) {
    fprintf(stderr, "out of memory while preparing %s\n", name);
    return false;
  }
  Timeline timeline = {0};
  bool ok;
  if (algorithm == 0)
    ok = run_fcfs(copy, count, &timeline);
  else if (algorithm == 1)
    ok = run_sjf(copy, count, &timeline);
  else
    ok = run_round_robin(copy, count, quantum, &timeline);

  if (!ok) {
    fprintf(stderr, "%s simulation failed (allocation or time-range error)\n",
            name);
  } else {
    printf(
        "\n============================================================\n%s\n",
        name);
    if (algorithm == 2)
      printf("Time quantum: %" PRId64 "\n", quantum);
    print_gantt_chart(&timeline);
    print_process_table(copy, count);
    print_averages(copy, count);
  }
  free(timeline.items);
  free_processes(copy);
  return ok;
}

int main(int argc, char **argv) {
  if (argc < 2 || argc > 3) {
    fprintf(stderr, "Usage: %s <processes.csv> [positive_time_quantum]\n",
            argv[0]);
    return EXIT_FAILURE;
  }
  int64_t quantum = 2;
  if (argc == 3 && !parse_quantum(argv[2], &quantum)) {
    fprintf(stderr, "invalid time quantum '%s': provide a positive integer\n",
            argv[2]);
    return EXIT_FAILURE;
  }

  Process *processes = NULL;
  size_t count = 0;
  if (!load_processes(argv[1], &processes, &count))
    return EXIT_FAILURE;

  bool ok = run_and_print("FIRST COME, FIRST SERVED (FCFS)", processes, count,
                          0, quantum) &&
            run_and_print("SHORTEST JOB FIRST (NON-PREEMPTIVE SJF)", processes,
                          count, 1, quantum) &&
            run_and_print("ROUND ROBIN", processes, count, 2, quantum);
  free_processes(processes);
  return ok ? EXIT_SUCCESS : EXIT_FAILURE;
}
