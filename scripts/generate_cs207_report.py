#!/usr/bin/env python3
"""Build the CS207 Operating Systems Design Assignment 1 report from screenshots.

Expected screenshot layout:
    screenshots/part_a/1.png
    screenshots/part_a/2.png
    screenshots/part_b/1.png
    ...

The script creates an editable DOCX and, when LibreOffice is installed, report.pdf.
It never invents execution output. Missing evidence is listed in the report and
in report/report_generation_manifest.txt.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

try:
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor
    from PIL import Image
except ImportError as exc:
    print(f"Missing Python dependency: {exc}", file=sys.stderr)
    print(
        "Install dependencies with:\n"
        "  sudo apt update\n"
        "  sudo apt install -y python3-docx python3-pil libreoffice-writer",
        file=sys.stderr,
    )
    raise SystemExit(2)


REPORT_TITLE = "OPERATING SYSTEMS DESIGN"
COURSE_CODE = "CS207"
ASSIGNMENT_TITLE = "ASSIGNMENT 1"
INSTITUTION = "DELHI TECHNOLOGICAL UNIVERSITY"
PAGE_WIDTH = 8.27
PAGE_HEIGHT = 11.69

PARTS: list[dict[str, Any]] = [
    {
        "key": "part_a",
        "title": "Part A - VirtualBox and Linux Environment Setup",
        "marks": 5,
        "aim": (
            "To configure a reproducible Ubuntu development environment inside Oracle VirtualBox, "
            "install the required development tools, and verify the guest operating system from its terminal."
        ),
        "theory": [
            ("Host and guest operating systems:", "The host OS runs directly on the physical computer. The guest OS runs inside a virtual machine managed by a hypervisor. In this assignment, Windows is the host and Ubuntu is the guest."),
            ("Virtualization:", "VirtualBox presents virtual CPU, memory, storage and network devices to the guest. This provides an isolated environment that can be recreated without replacing the host OS. The trade-off is additional resource overhead and potentially lower performance than direct hardware execution."),
            ("Environment verification:", "The required checks are gcc --version, uname -a, lscpu, free -h and df -h. Together they identify the compiler, guest kernel, virtual CPU information, available memory and mounted storage."),
        ],
        "commands": [
            "gcc --version", "uname -a", "lscpu", "free -h", "df -h",
            "make --version", "git --version",
        ],
        "evidence": [
            "Ubuntu VM running in VirtualBox", "Required environment command output", "Virtual machine CPU, RAM and disk configuration",
        ],
        "columns": 2,
        "max_image_height": 1.75,
    },
    {
        "key": "part_b",
        "title": "Part B - Process Creation and CPU Scheduling",
        "marks": 9,
        "aim": "To implement and compare FCFS, non-preemptive SJF and Round Robin CPU scheduling using a process table supplied through a file.",
        "theory": [
            ("FCFS:", "First Come First Served executes ready processes in arrival order. It is straightforward, but a long CPU burst near the front of the queue can delay shorter processes."),
            ("Non-preemptive SJF:", "Shortest Job First selects the ready process with the smallest CPU burst. Once selected, that process runs until completion. The choice is based only on processes that have arrived and are ready."),
            ("Round Robin:", "Round Robin gives each ready process up to a user-supplied time quantum. An unfinished process returns to the end of the ready queue, providing regular CPU access to competing processes."),
            ("Scheduling metrics:", "Completion time (CT) is the time a process finishes. Turnaround time (TAT) is CT minus arrival time. Waiting time (WT) is TAT minus CPU burst time. Response time (RT) is first CPU start time minus arrival time."),
        ],
        "formulas": [
            "Turnaround Time = Completion Time - Arrival Time",
            "Waiting Time = Turnaround Time - Burst Time",
            "Response Time = First CPU Start Time - Arrival Time",
        ],
        "commands": [
            "make clean && make",
            "./bin/scheduler tests/part_b/processes.csv 2",
            "bash tests/part_b/run_tests.sh",
        ],
        "evidence": [
            "FCFS and SJF timelines, process metrics and averages", "Round Robin timeline, selected quantum, process metrics and averages",
        ],
        "columns": 2,
        "max_image_height": 1.85,
    },
    {
        "key": "part_c",
        "title": "Part C - POSIX Threads and Producer-Consumer Synchronization",
        "marks": 8,
        "aim": "To implement a bounded-buffer producer-consumer system using POSIX threads, a mutex and semaphores, and verify correct item production and consumption under concurrency.",
        "theory": [
            ("Shared bounded buffer:", "The producers insert uniquely identified items into a finite circular buffer and consumers remove them. The required buffer capacity is five, with at least two producer threads and two consumer threads."),
            ("Synchronization:", "A mutex provides mutual exclusion while shared buffer state is modified. A counting semaphore for empty slots prevents insertion into a full buffer; a counting semaphore for filled slots prevents removal from an empty buffer."),
            ("Correctness:", "The implementation must avoid race conditions, overflow and underflow. A stress test of at least 100 items should demonstrate that each produced ID is consumed exactly once. A deliberately unsafe design should be discussed in the report."),
        ],
        "commands": [
            "make clean && make",
            "./bin/producer_consumer 100",
            "bash tests/part_c/run_tests.sh",
        ],
        "evidence": [
            "Producer and consumer thread activity", "At least 100 items and final exactly-once verification",
        ],
        "columns": 1,
        "max_image_height": 3.0,
    },
    {
        "key": "part_d",
        "title": "Part D - Deadlock Avoidance Using Banker's Algorithm",
        "marks": 7,
        "aim": "To analyse resource-allocation states using Allocation, Maximum and Available data, and determine whether a safe execution sequence exists.",
        "theory": [
            ("Need matrix:", "For each process and resource type, Need is calculated as Maximum minus Allocation. It represents the additional resources a process may still request to finish."),
            ("Safety algorithm:", "The algorithm starts with Work equal to Available. It repeatedly finds an unfinished process whose Need is no greater than Work, marks it finished and adds its Allocation back to Work. If all processes can finish, the state is safe and the selected order is a safe sequence."),
            ("Unsafe state:", "An unsafe state means the algorithm cannot guarantee that all processes can finish in some order. An unsafe state is not automatically proof that the system is already deadlocked."),
            ("Deadlock concepts:", "The four necessary conditions are mutual exclusion, hold and wait, no preemption and circular wait. Prevention breaks at least one condition; avoidance checks whether allocations preserve safety; detection identifies existing deadlocks; recovery releases resources or terminates/rolls back processes."),
        ],
        "commands": [
            "./bin/bankers tests/part_d/safe.txt",
            "./bin/bankers tests/part_d/unsafe.txt",
            "./bin/bankers tests/part_d/multiple_safe_sequences.txt",
            "bash tests/part_d/run_tests.sh",
        ],
        "evidence": [
            "Safe state and safe sequence", "Unsafe state result", "Third test: multiple safe sequences or resource-request decision",
        ],
        "columns": 2,
        "max_image_height": 2.1,
    },
    {
        "key": "part_e",
        "title": "Part E - Memory Management and Disk Scheduling",
        "marks": 7,
        "aim": "To simulate FIFO and LRU page replacement, and FCFS and SSTF disk scheduling, showing intermediate states and comparing their results on multiple inputs.",
        "theory": [
            ("FIFO page replacement:", "FIFO replaces the page that has been resident in memory for the longest time. It uses arrival order and does not consider how recently a page was accessed."),
            ("LRU page replacement:", "LRU replaces the page whose most recent access is farthest in the past. It uses recent reference history to estimate which page is least likely to be needed soon."),
            ("FCFS disk scheduling:", "FCFS services disk requests in the order they arrive. The total head movement is the sum of the absolute movements between consecutive head positions."),
            ("SSTF disk scheduling:", "SSTF chooses the pending request closest to the current head position. It can reduce immediate movement, but distant requests may wait longer."),
            ("Comparison:", "The report should show frame contents after every page reference, page-fault totals, disk service order and total head movement. Results depend on the reference string, frame count, initial head position and request queue; no policy is best for every workload."),
        ],
        "commands": [
            "./bin/page_replacement tests/part_e/pages_case1.txt",
            "./bin/page_replacement tests/part_e/pages_case2_fifo_lru_difference.txt",
            "./bin/disk_scheduling tests/part_e/disk_case1.txt",
            "./bin/disk_scheduling tests/part_e/disk_case2.txt",
            "bash tests/part_e/run_tests.sh",
        ],
        "evidence": [
            "FIFO and LRU frame states and faults for page test 1", "FIFO and LRU frame states and faults for page test 2", "FCFS and SSTF service order and head movement for disk test 1", "Second disk test and comparison",
        ],
        "columns": 2,
        "max_image_height": 2.0,
    },
    {
        "key": "part_f",
        "title": "Part F - File-System and OS Case-Study Analysis",
        "marks": 4,
        "aim": "To create and inspect a sample Linux directory tree and compare Linux and Windows in process management, file-system organization, access control and command-line tools.",
        "theory": [
            ("Directory hierarchy:", "Linux organises files beneath a single root directory, /. Absolute paths start at the root; relative paths are interpreted from the current working directory."),
            ("Permissions and ownership:", "Linux file metadata records an owner, group and permission bits for the owner, group and others. Read, write and execute permissions control access. Commands such as ls -l and stat display permissions, ownership and metadata."),
            ("Linux and Windows:", "Both systems support processes, hierarchical storage and user access controls, but expose different system interfaces and administrative tools. Linux commonly uses POSIX permissions and shell utilities; Windows commonly uses drive-letter paths, NTFS ACLs, Task Manager and PowerShell."),
        ],
        "commands": [
            "pwd", "tree", "ls -l", "stat <filename>", "realpath <path>",
        ],
        "evidence": [
            "Directory tree, absolute path and relative path", "Permissions, ownership and file metadata",
        ],
        "columns": 2,
        "max_image_height": 1.85,
    },
]


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_margins(cell, top: int = 70, start: int = 85, bottom: int = 70, end: int = 85) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn("w:" + side))
        if node is None:
            node = OxmlElement("w:" + side)
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, color: str = "B7C3D0", size: int = 5) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:color"), color)


def prevent_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))


def set_run(run, size: float = 9.5, bold: bool | None = None, color: str | None = None, font: str = "Times New Roman") -> None:
    run.font.name = font
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def set_page_field(paragraph) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, text, end])
    set_run(run, size=8, color="667085")


def setup_document() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(PAGE_WIDTH)
    section.page_height = Inches(PAGE_HEIGHT)
    section.top_margin = Inches(0.56)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)
    section.header_distance = Inches(0.25)
    section.footer_distance = Inches(0.25)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(9.2)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.paragraph_format.space_after = Pt(3)
    normal.paragraph_format.line_spacing = 1.02

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.paragraph_format.space_after = Pt(0)
    set_run(header.add_run("DELHI TECHNOLOGICAL UNIVERSITY  |  CS207  |  ASSIGNMENT 1"), size=8, bold=True, color="52637A")

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.space_before = Pt(0)
    set_run(footer.add_run("Operating Systems Design  |  Page "), size=8, color="667085")
    set_page_field(footer)
    return doc


def add_centered(doc: Document, text: str, size: float, bold: bool = False, color: str = "1D3557", before: float = 0, after: float = 2) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    set_run(paragraph.add_run(text), size=size, bold=bold, color=color)


def add_cover(doc: Document, args: argparse.Namespace, logo_path: Path | None) -> None:
    add_centered(doc, INSTITUTION, 18, True, before=34, after=6)
    add_centered(doc, "OPERATING SYSTEMS DESIGN", 16, True, after=3)
    add_centered(doc, f"{COURSE_CODE}  |  {ASSIGNMENT_TITLE}", 13, True, color="52637A", after=16)

    if logo_path and logo_path.is_file():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(18)
        p.add_run().add_picture(str(logo_path), width=Inches(1.25))
    else:
        add_centered(doc, "A - F", 25, True, color="7B8CA5", before=14, after=18)

    add_centered(doc, "ASSIGNMENT REPORT", 20, True, color="1D3557", after=7)
    add_centered(doc, "Virtualization, CPU Scheduling, Synchronization, Deadlocks,\nMemory Management, Disk Scheduling and File Systems", 11, color="52637A", after=32)

    table = doc.add_table(rows=4, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(1.65)
    table.columns[1].width = Inches(4.8)
    rows = [
        ("Submitted by", f"{args.student1}  |  Roll No.: {args.roll1}"),
        ("Team member", f"{args.student2}  |  Roll No.: {args.roll2}"),
        ("Submitted to", args.submitted_to),
        ("Submission date", args.submission_date),
    ]
    for row, values in zip(table.rows, rows):
        prevent_row_split(row)
        for i, (cell, value) in enumerate(zip(row.cells, values)):
            cell.width = Inches(1.65 if i == 0 else 4.8)
            set_cell_margins(cell, top=115, bottom=115, start=120, end=120)
            set_cell_border(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if i == 0:
                set_cell_shading(cell, "EAF0F6")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            set_run(p.add_run(value), size=9.2, bold=(i == 0), color="1D3557" if i == 0 else "202833")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    set_run(p.add_run("All execution evidence in this report is taken from the screenshots supplied in the project repository."), size=8.5, color="667085")


def add_contents(doc: Document) -> None:
    doc.add_page_break()
    add_centered(doc, "CONTENTS", 15, True, before=5, after=13)
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = [0.65, 3.55, 2.55]
    for i, width in enumerate(widths):
        table.columns[i].width = Inches(width)
    headings = ["Part", "Title", "Assessment focus"]
    for i, cell in enumerate(table.rows[0].cells):
        cell.width = Inches(widths[i])
        set_cell_shading(cell, "DCE6F1")
        set_cell_margins(cell, top=115, bottom=115)
        set_cell_border(cell)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        set_run(p.add_run(headings[i]), size=9, bold=True, color="1D3557")
    entries = [
        ("A", "VirtualBox and Linux environment", "VM setup and toolchain (5 marks)"),
        ("B", "Process creation and CPU scheduling", "FCFS, SJF and Round Robin (9 marks)"),
        ("C", "POSIX threads and synchronization", "Bounded-buffer producer-consumer (8 marks)"),
        ("D", "Deadlock avoidance", "Banker's safety algorithm (7 marks)"),
        ("E", "Memory and disk scheduling", "FIFO/LRU and FCFS/SSTF (7 marks)"),
        ("F", "File-system case study", "Linux files and Windows comparison (4 marks)"),
        ("-", "Conclusion and references", "Reproducibility and sources"),
    ]
    for n, entry in enumerate(entries):
        row = table.add_row()
        prevent_row_split(row)
        for i, (cell, value) in enumerate(zip(row.cells, entry)):
            cell.width = Inches(widths[i])
            set_cell_margins(cell, top=125, bottom=125)
            set_cell_border(cell)
            if n % 2 == 1:
                set_cell_shading(cell, "F7F9FC")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            set_run(p.add_run(value), size=8.5, bold=(i == 0), color="263445")

    add_heading(doc, "Project implementation overview", 11, before=15, after=4)
    add_body(doc, "The project is organised as separate parts, with source code under src/, input files and test scripts under tests/, execution evidence under screenshots/, and generated deliverables under report/. The Makefile is used to build the C programs from the repository root.")
    add_heading(doc, "Build and test", 10.5, before=5, after=2)
    add_code_block(doc, ["make clean && make", "make test"])
    doc.add_page_break()


def add_heading(doc: Document, text: str, size: float = 11, before: float = 5, after: float = 2, color: str = "1D3557"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(text), size=size, bold=True, color=color)
    return p


def add_body(doc: Document, text: str, size: float = 9.1) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.widow_control = True
    set_run(p.add_run(text), size=size, color="263445")


def add_bold_label_paragraph(doc: Document, label: str, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    set_run(p.add_run(label + " "), size=9.1, bold=True, color="1D3557")
    set_run(p.add_run(text), size=9.1, color="263445")


def add_code_block(doc: Document, lines: list[str]) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_shading(cell, "F3F5F7")
    set_cell_margins(cell, top=75, bottom=75, start=120, end=120)
    set_cell_border(cell, color="D8DEE7", size=4)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    for i, line in enumerate(lines):
        if i:
            p.add_run().add_break()
        set_run(p.add_run(line), size=7.5, color="263445", font="Consolas")


def add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.22)
    p.paragraph_format.first_line_indent = Inches(-0.12)
    p.paragraph_format.space_after = Pt(1)
    set_run(p.add_run(text), size=8.9, color="263445")


def screenshot_sort_key(path: Path):
    stem = path.stem
    if stem.isdigit():
        return (0, int(stem), path.name.lower())
    digits = "".join(ch for ch in stem if ch.isdigit())
    if digits:
        return (1, int(digits), path.name.lower())
    return (2, stem.lower(), path.name.lower())


def discover_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    valid = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in valid]
    good: list[Path] = []
    for path in sorted(files, key=screenshot_sort_key):
        try:
            with Image.open(path) as image:
                image.verify()
            good.append(path)
        except Exception as exc:
            print(f"Warning: skipping unreadable image {path}: {exc}", file=sys.stderr)
    return good


def image_dimensions(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def add_picture_fit(paragraph, path: Path, max_width: float, max_height: float) -> None:
    width_px, height_px = image_dimensions(path)
    if width_px <= 0 or height_px <= 0:
        raise ValueError(f"Invalid screenshot dimensions: {path}")
    scale = min(max_width / width_px, max_height / height_px)
    paragraph.add_run().add_picture(str(path), width=Inches(width_px * scale), height=Inches(height_px * scale))


def add_screenshot_gallery(doc: Document, part: dict[str, Any], images: list[Path]) -> None:
    """Insert every screenshot from a part folder as one unlabelled sequence."""
    add_heading(doc, "Screenshots", 10.5, before=6, after=4)
    if not images:
        add_body(doc, "No screenshots were found in this part's folder. Add images and regenerate the report.", 8.7)
        return

    # Keep screenshots in numeric filename order (1.png, 2.png, 10.png).
    # Do not add per-image captions, figure numbers, filenames or borders.
    for index, image_path in enumerate(images):
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_before = Pt(2)
        paragraph.paragraph_format.space_after = Pt(7)
        paragraph.paragraph_format.keep_together = True
        add_picture_fit(paragraph, image_path, 6.75, 3.25)


def add_part_section(doc: Document, part: dict[str, Any], images: list[Path], first: bool = False) -> None:
    if not first:
        doc.add_page_break()
    title = add_heading(doc, part["title"], 14, before=0, after=5)
    title.paragraph_format.keep_with_next = True
    add_bold_label_paragraph(doc, "Assessment weight:", f"{part['marks']} marks")
    add_bold_label_paragraph(doc, "Aim:", part["aim"])

    add_heading(doc, "Theory and design", 10.5, before=4, after=2)
    for label, body in part["theory"]:
        add_bold_label_paragraph(doc, label, body)

    if part.get("formulas"):
        add_heading(doc, "Scheduling formulas", 10, before=4, after=2)
        add_code_block(doc, part["formulas"])

    add_heading(doc, "Build and execution commands", 10, before=5, after=2)
    add_code_block(doc, part["commands"])

    if part["key"] == "part_f":
        add_heading(doc, "Linux and Windows comparison", 10, before=5, after=2)
        rows = [
            ("Area", "Linux", "Windows"),
            ("Process management", "ps, top, kill, signals and /proc", "Task Manager, Services and PowerShell process cmdlets"),
            ("File-system layout", "Single directory tree rooted at /", "Drive letters and mounted volumes, e.g. C:\\"),
            ("Access control", "Owner/group/other permission bits and ACLs", "NTFS access-control lists and user/group security tokens"),
            ("Command line", "Shells such as Bash and POSIX utilities", "PowerShell and Command Prompt"),
        ]
        add_simple_table(doc, rows, [1.35, 2.65, 2.65], font_size=7.6)

    if part["key"] == "part_c":
        add_heading(doc, "Core synchronization roles", 10, before=5, after=2)
        add_bullet(doc, "empty semaphore: counts free buffer slots; a producer waits before inserting.")
        add_bullet(doc, "full semaphore: counts occupied slots; a consumer waits before removing.")
        add_bullet(doc, "mutex: protects the buffer indices, count and item storage during each critical section.")

    if part["key"] == "part_d":
        add_heading(doc, "Deadlock conditions", 10, before=5, after=2)
        add_bullet(doc, "Mutual exclusion - at least one resource is non-shareable.")
        add_bullet(doc, "Hold and wait - a process holds resources while requesting more.")
        add_bullet(doc, "No preemption - resources cannot be forcibly taken away.")
        add_bullet(doc, "Circular wait - processes form a cycle of resource dependencies.")

    add_screenshot_gallery(doc, part, images)


def add_simple_table(doc: Document, rows: list[tuple[str, ...]], widths: list[float], font_size: float = 8) -> None:
    table = doc.add_table(rows=0, cols=len(widths))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, width in enumerate(widths):
        table.columns[i].width = Inches(width)
    for row_index, values in enumerate(rows):
        row = table.add_row()
        prevent_row_split(row)
        for i, (cell, value) in enumerate(zip(row.cells, values)):
            cell.width = Inches(widths[i])
            set_cell_margins(cell, top=65, bottom=65, start=75, end=75)
            set_cell_border(cell)
            if row_index == 0:
                set_cell_shading(cell, "DCE6F1")
            elif row_index % 2 == 0:
                set_cell_shading(cell, "F7F9FC")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            set_run(p.add_run(value), size=font_size, bold=(row_index == 0), color="1D3557" if row_index == 0 else "263445")


def add_closing_sections(doc: Document, args: argparse.Namespace, missing: list[str], image_counts: dict[str, int]) -> None:
    doc.add_page_break()
    add_heading(doc, "Conclusion", 14, before=0, after=5)
    add_body(doc, "The assignment brings together operating-system environment setup, process scheduling, thread synchronization, deadlock avoidance, memory management, disk scheduling and file-system inspection. The implementation is intended to be reproducible from the supplied source code, Makefile, test inputs and execution instructions. The screenshots in this report provide visual evidence of the runs supplied in the repository.")
    add_body(doc, "The measured results should be interpreted using the exact input data shown in the corresponding evidence. Scheduling averages, page-fault counts and disk-head movement are workload-dependent; they should not be generalised beyond the test cases used.")

    add_heading(doc, "Evidence completeness", 11, before=7, after=3)
    for part in PARTS:
        actual = image_counts.get(part["key"], 0)
        status = f"{actual} screenshot(s) included" if actual else "No screenshots found - add evidence"
        add_bullet(doc, f"{part['title']}: {status}")
    if missing:
        add_body(doc, "A part folder is empty. Add the relevant screenshots to that folder and regenerate this report. No sample or fabricated images are used.", 8.6)
    else:
        add_body(doc, "Every part folder contains at least one screenshot. Verify that all screenshots show readable commands and output.", 8.6)

    add_heading(doc, "Team contributions", 11, before=7, after=3)
    add_body(doc, "Student 1 contribution: [Enter the parts and tasks completed by Student 1].")
    add_body(doc, "Student 2 contribution: [Enter the parts and tasks completed by Student 2].")
    add_body(doc, "Joint work: [Enter integration, cross-testing, report preparation and final verification completed by both members].")

    add_heading(doc, "References", 11, before=7, after=3)
    references = [
        "CS207 Operating Systems Design - Assignment 1, course assignment brief.",
        "Oracle VM VirtualBox User Manual: https://www.virtualbox.org/manual/",
        "GNU Compiler Collection documentation: https://gcc.gnu.org/onlinedocs/",
        "Linux man-pages project: https://www.kernel.org/doc/man-pages/",
        "The Open Group Base Specifications (POSIX): https://pubs.opengroup.org/onlinepubs/9699919799/",
    ]
    for item in references:
        add_bullet(doc, item)


def resolve_project_root(arg_value: str) -> Path:
    if arg_value:
        return Path(arg_value).expanduser().resolve()
    script_path = Path(__file__).resolve()
    if script_path.parent.name == "scripts":
        return script_path.parent.parent
    return Path.cwd().resolve()


def convert_to_pdf(docx_path: Path, pdf_destination: Path) -> bool:
    office = shutil.which("libreoffice") or shutil.which("soffice")
    if not office:
        print("LibreOffice was not found. The editable DOCX is ready; install libreoffice-writer to export report.pdf.", file=sys.stderr)
        return False
    pdf_destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cs207_lo_") as tmp:
        temp_dir = Path(tmp)
        profile = temp_dir / "lo_profile"
        export_dir = temp_dir / "pdf"
        export_dir.mkdir()
        command = [
            office,
            f"-env:UserInstallation=file://{profile}",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(export_dir),
            str(docx_path),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            print("PDF export timed out. The DOCX is still available.", file=sys.stderr)
            return False
        produced = export_dir / f"{docx_path.stem}.pdf"
        if result.returncode != 0 or not produced.is_file() or produced.stat().st_size == 0:
            print("PDF export failed. The DOCX is still available.", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False
        shutil.copy2(produced, pdf_destination)
    return True


def build_report(args: argparse.Namespace) -> tuple[Path, Path | None, dict[str, Any]]:
    root = resolve_project_root(args.project_root)
    screenshot_root = Path(args.screenshots).expanduser()
    if not screenshot_root.is_absolute():
        screenshot_root = (root / screenshot_root).resolve()

    output_dir = Path(args.output_dir).expanduser()
    if not output_dir.is_absolute():
        output_dir = (root / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    image_map: dict[str, list[Path]] = {}
    image_counts: dict[str, int] = {}
    missing: list[str] = []
    for part in PARTS:
        folder = screenshot_root / part["key"]
        images = discover_images(folder)
        image_map[part["key"]] = images
        image_counts[part["key"]] = len(images)
        if not images:
            missing.append(f"{part['key']}/ - no screenshot images found")

    doc = setup_document()
    logo_path = Path(args.logo).expanduser().resolve() if args.logo else None
    if logo_path and not logo_path.exists():
        print(f"Warning: logo not found, using text-only cover: {logo_path}", file=sys.stderr)
        logo_path = None

    add_cover(doc, args, logo_path)
    add_contents(doc)
    for index, part in enumerate(PARTS):
        add_part_section(doc, part, image_map[part["key"]], first=(index == 0))
    add_closing_sections(doc, args, missing, image_counts)

    docx_path = output_dir / "CS207_Assignment1_Report.docx"
    doc.save(docx_path)

    pdf_destination = root / args.pdf_name
    pdf_ok = convert_to_pdf(docx_path, pdf_destination)
    pdf_path = pdf_destination if pdf_ok else None

    manifest = {
        "assignment": "CS207 Operating Systems Design - Assignment 1",
        "project_root": str(root),
        "screenshot_root": str(screenshot_root),
        "docx": str(docx_path),
        "pdf": str(pdf_path) if pdf_path else None,
        "images": {key: [str(p.relative_to(root)) if p.is_relative_to(root) else str(p) for p in value] for key, value in image_map.items()},
        "image_counts": image_counts,
        "missing_evidence": missing,
        "note": "Missing evidence is flagged; no program output or screenshot is fabricated.",
    }
    manifest_path = output_dir / "report_generation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    notes_path = output_dir / "report_generation_manifest.txt"
    lines = [
        "CS207 REPORT GENERATION SUMMARY",
        "================================",
        f"DOCX: {docx_path}",
        f"PDF: {pdf_path if pdf_path else 'NOT CREATED - LibreOffice export unavailable or failed'}",
        "",
        "SCREENSHOT COUNTS:",
    ]
    for part in PARTS:
        lines.append(f"{part['key']}: {image_counts[part['key']]} file(s) found")
    lines.extend(["", "MISSING EVIDENCE:"])
    lines.extend(missing or ["None; every part folder contains at least one image."])
    lines.extend(["", "All images found in each screenshots/part_*/ folder are inserted together, in numeric filename order, without individual labels or captions. No output has been fabricated."])
    notes_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return docx_path, pdf_path, manifest


def count_pdf_pages(pdf_path: Path) -> int | None:
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        return None
    try:
        result = subprocess.run([pdfinfo, str(pdf_path)], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.strip().startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the CS207 Assignment 1 report from screenshots/part_a/1.png etc."
    )
    parser.add_argument("--project-root", default="", help="Repository root (default: parent of this script if it is in scripts/)")
    parser.add_argument("--screenshots", default="screenshots", help="Screenshot directory, relative to project root")
    parser.add_argument("--output-dir", default="report", help="Directory for the editable DOCX and generation manifest")
    parser.add_argument("--pdf-name", default="report.pdf", help="PDF filename at the repository root")
    parser.add_argument("--student1", default="[Enter Student 1 name]")
    parser.add_argument("--roll1", default="[Enter roll number]")
    parser.add_argument("--student2", default="[Enter Student 2 name]")
    parser.add_argument("--roll2", default="[Enter roll number]")
    parser.add_argument("--submitted-to", default="[Enter faculty name]")
    parser.add_argument("--submission-date", default=date.today().strftime("%d %B %Y"))
    parser.add_argument("--logo", default="", help="Optional DTU logo image path")
    parser.add_argument("--max-pages", type=int, default=12, help="Warn if the generated PDF exceeds this page count (default: 12)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        docx_path, pdf_path, manifest = build_report(args)
    except Exception as exc:
        print(f"Report generation failed: {exc}", file=sys.stderr)
        return 1

    print("\nCS207 report generation complete")
    print(f"DOCX: {docx_path}")
    if pdf_path:
        print(f"PDF:  {pdf_path}")
    else:
        print("PDF:  not created (see LibreOffice note above)")
    page_count = count_pdf_pages(pdf_path) if pdf_path else None
    if page_count is not None:
        print(f"PDF pages: {page_count}")
        if args.max_pages > 0 and page_count > args.max_pages:
            print(f"WARNING: report exceeds the suggested {args.max_pages}-page limit. Review screenshot sizes/layout.", file=sys.stderr)
    missing = manifest["missing_evidence"]
    if missing:
        print(f"Evidence check: {len(missing)} expected screenshot(s) missing. See report/report_generation_manifest.txt")
    else:
        print("Evidence check: all template screenshot slots have at least one image.")
    print("\nAll screenshots in each part folder are included together in numeric filename order, without individual labels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
