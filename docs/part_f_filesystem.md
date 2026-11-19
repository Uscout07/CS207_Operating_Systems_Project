# Part F - File System and Operating System Case Study

## Sample directory tree

Run the following from the project root:

```bash
bash scripts/part_f_demo.sh
```

It creates a small directory named `part_f_demo`. It has more than three nested directories and five text files. The script also prints the current user and group, an absolute path, an example relative path, directory listings, file permissions, ownership, sizes and a few running processes.

The files are only sample files for this assignment. Running the script again recreates them, so it is okay to run it more than once.

## Commands used

These are the main Linux commands shown by the script:

- `pwd`: shows the directory we are currently in.
- `realpath`: shows the full absolute path of a file or directory.
- `ls -lR`: lists the directories and shows permissions and ownership.
- `find`: walks through the directory tree and finds files.
- `stat`: shows file details such as owner, group, permissions and size.
- `id`: shows the current user's user ID and groups.
- `ps -ef`: shows running processes.

Linux permissions are commonly shown as read (`r`), write (`w`) and execute (`x`) for the owner, group and others. For example, `-rw-r--r--` means the owner can read and write the file, while the group and other users can only read it.

## Linux and Windows comparison

| Topic | Linux | Windows |
|---|---|---|
| Process management | Commands such as `ps`, `top` and `kill` are commonly used. | Task Manager and PowerShell commands such as `Get-Process` and `Stop-Process` are commonly used. |
| File-system layout | One directory tree starts at `/`. Other disks and partitions are attached (mounted) at directories. | Drives commonly have letters such as `C:` and `D:`. NTFS is commonly used. |
| Permissions | Owner, group and others have read, write and execute permissions. Linux also supports tools such as `chmod` and `chown`. | Access is commonly controlled using Windows security permissions (ACLs), with UAC helping control administrative actions. |
| Command line | Bash and tools such as `ls`, `pwd`, `find` and `grep` are common. | PowerShell and Command Prompt are common. |

The commands in the script are observations from the Ubuntu environment. The Windows column is a short comparison of the usual Windows tools and layout; it was not run inside the Ubuntu VM.

## What to include in the report

After running the script, take a screenshot that shows the directory listing and `stat` output. Add the actual path printed on your VM to the report. Mention the permission difference between the `644` and `640` sample files. Do not copy a path or username from somebody else's computer.
