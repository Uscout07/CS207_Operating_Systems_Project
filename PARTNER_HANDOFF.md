# Notes for the person doing Parts D, E and F

Hi! Parts D, E and F are in this folder now. The main thing is to clone the same GitHub project, add these files, and run the tests in Ubuntu. You should not need to change the Part B or Part C programs to use these parts.

## First time setup

```bash
git clone https://github.com/Uscout07/CS207_Operating_Systems_Project.git
cd CS207_Operating_Systems_Project
bash scripts/bootstrap-ubuntu.sh
```

If the repository already has the Part A setup script, that command installs the usual build tools. If it does not, install them with:

```bash
sudo apt update
sudo apt install -y build-essential git
```

## Add the files

Follow `APPLY_INSTRUCTIONS.md`. It explains where the files go and includes a script to copy them.

## Run your parts

```bash
make bankers
make test-part-d

make page-replacement
make disk-scheduling
make test-part-e

make part-f-demo
```

For the actual commands with the sample files, look at the main `README.md`.

## What to read before explaining it

- Part D: `docs/part_d_bankers.md`
- Part E: `docs/part_e_memory_and_disk.md`
- Part F: `docs/part_f_filesystem.md`

Please read through the code before the evaluation. The report explanation is there to help, but we should both be able to explain what the program does and why the test results came out that way.

## What still needs to be done by us

- Run the programs inside the Ubuntu VM.
- Take our own screenshots.
- Keep the output files from those runs.
- Add our real names, roll numbers and contributions to the report.
- Check that the full project builds after pulling the final changes.
