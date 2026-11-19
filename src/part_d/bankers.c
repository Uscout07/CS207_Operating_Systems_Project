#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_PROCESSES 100
#define MAX_RESOURCES 100
#define MAX_RESOURCE_VALUE 1000000000LL

typedef long long Resource;

static bool read_number(FILE *input, Resource *value) {
    return fscanf(input, "%lld", value) == 1;
}

int main(int argc, char **argv) {
    FILE *input = stdin;
    Resource allocation[MAX_PROCESSES][MAX_RESOURCES];
    Resource maximum[MAX_PROCESSES][MAX_RESOURCES];
    Resource need[MAX_PROCESSES][MAX_RESOURCES];
    Resource available[MAX_RESOURCES];
    Resource work[MAX_RESOURCES];
    bool finished[MAX_PROCESSES] = {false};
    int safe_sequence[MAX_PROCESSES];
    int process_count;
    int resource_count;
    int completed = 0;

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

    if (fscanf(input, "%d %d", &process_count, &resource_count) != 2 ||
        process_count < 1 || process_count > MAX_PROCESSES ||
        resource_count < 1 || resource_count > MAX_RESOURCES) {
        fprintf(stderr, "Input must start with valid process and resource counts.\n");
        if (input != stdin) fclose(input);
        return EXIT_FAILURE;
    }

    for (int i = 0; i < process_count; i++) {
        for (int j = 0; j < resource_count; j++) {
            if (!read_number(input, &allocation[i][j]) || allocation[i][j] < 0 ||
                allocation[i][j] > MAX_RESOURCE_VALUE) {
                fprintf(stderr, "Invalid allocation value for P%d, resource %d.\n", i, j);
                if (input != stdin) fclose(input);
                return EXIT_FAILURE;
            }
        }
    }

    for (int i = 0; i < process_count; i++) {
        for (int j = 0; j < resource_count; j++) {
            if (!read_number(input, &maximum[i][j]) ||
                maximum[i][j] < allocation[i][j] ||
                maximum[i][j] > MAX_RESOURCE_VALUE) {
                fprintf(stderr, "Invalid maximum value for P%d, resource %d.\n", i, j);
                if (input != stdin) fclose(input);
                return EXIT_FAILURE;
            }
            need[i][j] = maximum[i][j] - allocation[i][j];
        }
    }

    for (int j = 0; j < resource_count; j++) {
        if (!read_number(input, &available[j]) || available[j] < 0 ||
            available[j] > MAX_RESOURCE_VALUE) {
            fprintf(stderr, "Invalid available value for resource %d.\n", j);
            if (input != stdin) fclose(input);
            return EXIT_FAILURE;
        }
        work[j] = available[j];
    }

    if (input != stdin) fclose(input);

    puts("Banker's safety algorithm");
    printf("Processes: %d | Resource types: %d\n\n", process_count, resource_count);
    puts("Need matrix (Maximum - Allocation):");
    for (int i = 0; i < process_count; i++) {
        printf("P%d: ", i);
        for (int j = 0; j < resource_count; j++) {
            printf("%lld%s", need[i][j], j + 1 == resource_count ? "" : "  ");
        }
        putchar('\n');
    }

    printf("\nProcesses that can finish with the initial Available values: ");
    int initially_ready = 0;
    for (int i = 0; i < process_count; i++) {
        bool can_finish = true;
        for (int j = 0; j < resource_count; j++) {
            if (need[i][j] > available[j]) {
                can_finish = false;
                break;
            }
        }
        if (can_finish) {
            printf("%sP%d", initially_ready == 0 ? "" : ", ", i);
            initially_ready++;
        }
    }
    if (initially_ready == 0) printf("none");
    putchar('\n');
    if (initially_ready > 1) {
        puts("More than one process can start, so there is more than one possible first choice.");
    }

    puts("\nChecking which processes can finish:");
    while (completed < process_count) {
        bool found = false;

        for (int i = 0; i < process_count; i++) {
            bool can_finish = true;

            if (finished[i]) continue;

            for (int j = 0; j < resource_count; j++) {
                if (need[i][j] > work[j]) {
                    can_finish = false;
                    break;
                }
            }

            if (can_finish) {
                printf("P%d can finish. It releases its allocated resources.\n", i);
                for (int j = 0; j < resource_count; j++) {
                    work[j] += allocation[i][j];
                }
                finished[i] = true;
                safe_sequence[completed++] = i;
                found = true;
            }
        }

        if (!found) break;
    }

    if (completed == process_count) {
        puts("\nState: SAFE");
        printf("One safe sequence: ");
        for (int i = 0; i < process_count; i++) {
            printf("P%d%s", safe_sequence[i], i + 1 == process_count ? "\n" : " -> ");
        }
        puts("All processes can finish in this order.");
    } else {
        puts("\nState: UNSAFE");
        puts("No safe sequence was found with the currently available resources.");
        printf("Processes that could not finish: ");
        bool first = true;
        for (int i = 0; i < process_count; i++) {
            if (!finished[i]) {
                printf("%sP%d", first ? "" : ", ", i);
                first = false;
            }
        }
        putchar('\n');
        puts("This means the system cannot guarantee that every process can finish.");
        puts("An unsafe state is not automatically the same thing as a deadlock.");
    }

    return EXIT_SUCCESS;
}
