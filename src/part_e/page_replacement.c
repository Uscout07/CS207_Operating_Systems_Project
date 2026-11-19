#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_FRAMES 100
#define MAX_REFERENCES 10000

static void print_frames(const int *frames, int frame_count) {
    printf("[");
    for (int i = 0; i < frame_count; i++) {
        if (frames[i] == -1) printf("-");
        else printf("%d", frames[i]);
        if (i + 1 < frame_count) printf(" ");
    }
    printf("]");
}

static int find_page(const int *frames, int frame_count, int page) {
    for (int i = 0; i < frame_count; i++) {
        if (frames[i] == page) return i;
    }
    return -1;
}

static int first_empty_frame(const int *frames, int frame_count) {
    for (int i = 0; i < frame_count; i++) {
        if (frames[i] == -1) return i;
    }
    return -1;
}

static int run_fifo(const int *references, int reference_count, int frame_count) {
    int frames[MAX_FRAMES];
    int next_to_replace = 0;
    int faults = 0;

    for (int i = 0; i < frame_count; i++) frames[i] = -1;

    puts("FIFO page replacement:");
    for (int i = 0; i < reference_count; i++) {
        int page = references[i];
        int slot = find_page(frames, frame_count, page);
        bool fault = slot == -1;

        if (fault) {
            int empty = first_empty_frame(frames, frame_count);
            faults++;
            if (empty != -1) {
                slot = empty;
                frames[slot] = page;
                next_to_replace = (slot + 1) % frame_count;
            } else {
                frames[next_to_replace] = page;
                next_to_replace = (next_to_replace + 1) % frame_count;
            }
        }

        printf("Reference %2d: page %-4d ", i + 1, page);
        print_frames(frames, frame_count);
        printf("  %s\n", fault ? "FAULT" : "HIT");
    }

    printf("FIFO page faults: %d\n\n", faults);
    return faults;
}

static int run_lru(const int *references, int reference_count, int frame_count) {
    int frames[MAX_FRAMES];
    int last_used[MAX_FRAMES] = {0};
    int faults = 0;

    for (int i = 0; i < frame_count; i++) frames[i] = -1;

    puts("LRU page replacement:");
    for (int i = 0; i < reference_count; i++) {
        int page = references[i];
        int slot = find_page(frames, frame_count, page);
        bool fault = slot == -1;

        if (fault) {
            slot = first_empty_frame(frames, frame_count);
            faults++;
            if (slot == -1) {
                slot = 0;
                for (int j = 1; j < frame_count; j++) {
                    if (last_used[j] < last_used[slot]) slot = j;
                }
            }
            frames[slot] = page;
        }

        last_used[slot] = i + 1;
        printf("Reference %2d: page %-4d ", i + 1, page);
        print_frames(frames, frame_count);
        printf("  %s\n", fault ? "FAULT" : "HIT");
    }

    printf("LRU page faults: %d\n", faults);
    return faults;
}

int main(int argc, char **argv) {
    FILE *input = stdin;
    int frame_count;
    int reference_count;
    int references[MAX_REFERENCES];

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

    if (fscanf(input, "%d %d", &frame_count, &reference_count) != 2 ||
        frame_count < 1 || frame_count > MAX_FRAMES ||
        reference_count < 1 || reference_count > MAX_REFERENCES) {
        fprintf(stderr, "Input must contain a valid frame count and reference count.\n");
        if (input != stdin) fclose(input);
        return EXIT_FAILURE;
    }

    for (int i = 0; i < reference_count; i++) {
        if (fscanf(input, "%d", &references[i]) != 1 || references[i] < 0) {
            fprintf(stderr, "Invalid page reference at position %d.\n", i + 1);
            if (input != stdin) fclose(input);
            return EXIT_FAILURE;
        }
    }

    if (input != stdin) fclose(input);

    printf("Frames: %d | Page references: %d\n\n", frame_count, reference_count);
    int fifo_faults = run_fifo(references, reference_count, frame_count);
    int lru_faults = run_lru(references, reference_count, frame_count);

    puts("\nComparison:");
    printf("FIFO faults = %d, LRU faults = %d\n", fifo_faults, lru_faults);
    if (fifo_faults < lru_faults) puts("FIFO had fewer faults for this input.");
    else if (lru_faults < fifo_faults) puts("LRU had fewer faults for this input.");
    else puts("Both algorithms had the same number of faults for this input.");

    return EXIT_SUCCESS;
}
