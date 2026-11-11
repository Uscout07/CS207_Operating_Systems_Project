CC := gcc
CFLAGS := -std=c17 -Wall -Wextra -Wpedantic -O2
TARGET := bin/scheduler
SOURCE := src/part_b/scheduler.c

.PHONY: all run test clean
all: $(TARGET)

$(TARGET): $(SOURCE)
	mkdir -p bin
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET)

run: $(TARGET)
	./$(TARGET) tests/part_b/processes.csv 2

test: $(TARGET)
	./tests/part_b/run_tests.sh

clean:
	rm -f $(TARGET)
