#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DEMO_DIR="part_f_demo"
mkdir -p "$DEMO_DIR/course/notes" \
         "$DEMO_DIR/course/labs" \
         "$DEMO_DIR/course/projects/cs207" \
         "$DEMO_DIR/personal"

cat > "$DEMO_DIR/course/notes/week1.txt" <<'TEXT'
These are sample notes for the CS207 operating systems assignment.
TEXT
cat > "$DEMO_DIR/course/labs/permissions.txt" <<'TEXT'
This file is used to demonstrate Linux file permissions.
TEXT
cat > "$DEMO_DIR/course/projects/cs207/README.txt" <<'TEXT'
This is a small sample project directory for the filesystem exercise.
TEXT
cat > "$DEMO_DIR/course/projects/cs207/todo.txt" <<'TEXT'
Check paths, ownership and file metadata for the assignment.
TEXT
cat > "$DEMO_DIR/personal/todo.txt" <<'TEXT'
Remember to take a screenshot after running the filesystem commands.
TEXT

chmod 755 "$DEMO_DIR" "$DEMO_DIR/course" "$DEMO_DIR/course/notes" \
    "$DEMO_DIR/course/labs" "$DEMO_DIR/course/projects" \
    "$DEMO_DIR/course/projects/cs207" "$DEMO_DIR/personal"
chmod 644 "$DEMO_DIR/course/notes/week1.txt" \
    "$DEMO_DIR/course/projects/cs207/README.txt" \
    "$DEMO_DIR/personal/todo.txt"
chmod 640 "$DEMO_DIR/course/labs/permissions.txt" \
    "$DEMO_DIR/course/projects/cs207/todo.txt"

printf '\n--- Current user and group ---\n'
id

printf '\n--- Absolute path of the sample directory ---\n'
realpath "$DEMO_DIR"

printf '\n--- Example relative path ---\n'
cd "$DEMO_DIR/course/notes"
pwd
printf 'Relative path from the repository root: %s\n' "${DEMO_DIR#./}/course/notes"
cd "$ROOT_DIR"

printf '\n--- Directory tree and permissions ---\n'
ls -lR "$DEMO_DIR"

printf '\n--- File owner, group, permissions and size ---\n'
find "$DEMO_DIR" -type f -exec stat -c '%n | owner: %U | group: %G | permissions: %A (%a) | size: %s bytes' {} \;

printf '\n--- A few running processes ---\n'
ps -ef | head -n 8

printf '\nThe sample directory has been created at: %s\n' "$(realpath "$DEMO_DIR")"
printf 'Run this script again any time; it recreates the same small sample files.\n'
