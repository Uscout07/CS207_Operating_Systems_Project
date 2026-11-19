#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_REQUESTS 10000
#define MAX_TRACK_POSITION 1000000000LL

typedef long long Track;

static Track distance_between(Track a, Track b) {
    return a >= b ? a - b : b - a;
}

static void run_fcfs(Track initial_head, const Track *requests, int count) {
    Track current = initial_head;
    Track total_movement = 0;

    puts("FCFS disk scheduling:");
    printf("Service order: %lld", initial_head);
    for (int i = 0; i < count; i++) {
        Track movement = distance_between(current, requests[i]);
        total_movement += movement;
        printf(" -> %lld (move %lld)", requests[i], movement);
        current = requests[i];
    }
    putchar('\n');
    printf("FCFS total head movement: %lld tracks\n\n", total_movement);
}

static void run_sstf(Track initial_head, const Track *requests, int count) {
    bool served[MAX_REQUESTS] = {false};
    Track current = initial_head;
    Track total_movement = 0;

    puts("SSTF disk scheduling:");
    printf("Service order: %lld", initial_head);

    for (int step = 0; step < count; step++) {
        int best_index = -1;
        Track best_distance = 0;

        for (int i = 0; i < count; i++) {
            if (served[i]) continue;
            Track distance = distance_between(current, requests[i]);
            if (best_index == -1 || distance < best_distance) {
                best_index = i;
                best_distance = distance;
            }
        }

        served[best_index] = true;
        total_movement += best_distance;
        printf(" -> %lld (move %lld)", requests[best_index], best_distance);
        current = requests[best_index];
    }

    putchar('\n');
    printf("SSTF total head movement: %lld tracks\n", total_movement);
}

int main(int argc, char **argv) {
    FILE *input = stdin;
    Track initial_head;
    Track requests[MAX_REQUESTS];
    int request_count;

    if (argc > 2) {
        fprintf(stderr, "Usage: %s [input_file]\n", argv[0]);
        return EXIT_FAILURE;
    }

    if (argc == 2) {
        input = fopen(argv[1], "r");
        if (input == NULL) {
            perror("Could not open input file");
            return EXIT_FAILURE;
        }
    }

    if (fscanf(input, "%lld %d", &initial_head, &request_count) != 2 ||
        initial_head < 0 || initial_head > MAX_TRACK_POSITION ||
        request_count < 1 || request_count > MAX_REQUESTS) {
        fprintf(stderr, "Input must contain a non-negative head position and a valid request count.\n");
        if (input != stdin) fclose(input);
        return EXIT_FAILURE;
    }

    for (int i = 0; i < request_count; i++) {
        if (fscanf(input, "%lld", &requests[i]) != 1 || requests[i] < 0 ||
            requests[i] > MAX_TRACK_POSITION) {
            fprintf(stderr, "Invalid disk request at position %d.\n", i + 1);
            if (input != stdin) fclose(input);
            return EXIT_FAILURE;
        }
    }

    if (input != stdin) fclose(input);

    printf("Initial head position: %lld | Requests: %d\n\n", initial_head, request_count);
    run_fcfs(initial_head, requests, request_count);
    run_sstf(initial_head, requests, request_count);

    return EXIT_SUCCESS;
}
