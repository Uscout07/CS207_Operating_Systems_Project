# How to add Parts D, E and F to our existing GitHub project

This file is just the order I would follow when adding these files. The script copies the new files into the right folders and leaves the existing Part B and Part C source files alone.

## 1. Get the latest project first

Open Ubuntu and go to the place where you keep projects. If you have not cloned the project yet:

```bash
git clone https://github.com/Uscout07/CS207_Operating_Systems_Project.git
cd CS207_Operating_Systems_Project
```

If it is already cloned:

```bash
cd ~/CS207_Operating_Systems_Project
git pull
```

Check that you are in the correct folder:

```bash
pwd
ls
```

You should see the root `Makefile` and the `src` folder.

## 2. Extract this completion package

Extract `CS207_Completion_Parts_D_E_F.zip`. It will create a folder called `CS207_Completion_Parts_D_E_F`.

For example, if it was extracted in Downloads, its path may be:

```text
~/Downloads/CS207_Completion_Parts_D_E_F
```

Use the actual location on your computer in the next command.

## 3. Run the copy script

From anywhere, run:

```bash
bash ~/Downloads/CS207_Completion_Parts_D_E_F/apply_to_repo.sh ~/CS207_Operating_Systems_Project
```

Change either path if your folders are somewhere else.

The script copies these things:

| Package file | Goes into the repository |
|---|---|
| `src/part_d/bankers.c` | `src/part_d/bankers.c` |
| `src/part_e/page_replacement.c` | `src/part_e/page_replacement.c` |
| `src/part_e/disk_scheduling.c` | `src/part_e/disk_scheduling.c` |
| `tests/part_d/` | `tests/part_d/` |
| `tests/part_e/` | `tests/part_e/` |
| `docs/` | `docs/` |
| `scripts/part_f_demo.sh` | `scripts/part_f_demo.sh` |
| `Makefile.part_de` | repository root |
| `README.md` | repository root |

The existing README is saved as `README_before_parts_d_e_f.md` before the new combined README is copied. The script adds `include Makefile.part_de` to the root Makefile only if that line is not already there.

## 4. Build and run the new parts

```bash
cd ~/CS207_Operating_Systems_Project
make clean
make
make test-part-d
make test-part-e
```

Try the programs manually as well:

```bash
./bin/bankers tests/part_d/safe.txt
./bin/page_replacement tests/part_e/pages_case2_fifo_lru_difference.txt
./bin/disk_scheduling tests/part_e/disk_case1.txt
make part-f-demo
```

Then run the combined tests. It will run `tests/part_b/run_tests.sh` if that file exists, then the existing root `make test` target, and finally the Part D and Part E tests:

```bash
make test-all
```

## 5. Save the screenshots and output from your own VM

The folders already have places for screenshots. Take real screenshots while the programs are running in your Ubuntu VM.

- Part D: save them under `screenshots/part_d/`.
- Part E: save them under `screenshots/part_e/`.
- Part F: save them under `screenshots/part_f/`.

Save terminal output using the commands in the README. Do not say that a screenshot was taken if it was not.

## 6. Check and push the changes

```bash
git status
git diff -- Makefile README.md
```

Make sure the old Part B and Part C files are still there. Then add the new files and commit:

```bash
git add Makefile Makefile.part_de README.md README_before_parts_d_e_f.md \
    src/part_d src/part_e tests/part_d tests/part_e docs scripts/part_f_demo.sh \
    APPLY_INSTRUCTIONS.md PARTNER_HANDOFF.md report/assignment_report_template.md

git commit -m "Complete Parts D E and F"
git push
```

If you are using a separate branch, push that branch and open a pull request instead of pushing straight to `main`.

## If you want to copy files manually

Copy the three C files into `src/part_d/` and `src/part_e/`. Copy the test files into `tests/part_d/` and `tests/part_e/`. Copy the three explanation files into `docs/`, and copy `scripts/part_f_demo.sh` into `scripts/`.

Copy `Makefile.part_de` into the repository root. Open the root `Makefile` and add this line at the end:

```make
include Makefile.part_de
```

Finally, copy this package's `README.md` to the repository root after keeping a backup of the old README. The automatic script does these same steps for you.
