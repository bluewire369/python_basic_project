import os
import argparse

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# ---------------- SIGNATURES ----------------

signatures = {
    "PNG": bytes.fromhex("89504E470D0A1A0A"),
    "PDF": bytes.fromhex("25504446"),
    "JPEG": bytes.fromhex("FFD8FF"),
    "ZIP": bytes.fromhex("504B0304")
}

# ---------------- ARGPARSE ----------------

parser = argparse.ArgumentParser(
    prog="Hexscope",
    description="Binary File Signature Detector and Hex Dump Analyzer"
)

parser.add_argument(
    "--file",
    required=True,
    help="Path of the file to analyze"
)

parser.add_argument(
    "--output",
    default="test.txt",
    help="Output file for the hex dump (default: test.txt)"
)

parser.add_argument(
    "--version",
    action="version",
    version="Hexscope 1.0"
)

args = parser.parse_args()

path = args.file
output_path = args.output

# ---------------- FILE CHECK ----------------

if not os.path.isfile(path):
    console.print("[bold red]Error:[/bold red] File does not exist.")
    raise SystemExit(1)

with open(path, "rb") as f:

    check = f.read(32)

    if check == b'':
        console.print("[bold red]No data found in the file.[/bold red]")
        raise SystemExit(1)

    # ---------------- SIGNATURE DETECTION ----------------

    f.seek(0)

    file_type = "Unknown"

    for key, value in signatures.items():
        if check.startswith(value):
            file_type = key
            break

    # ---------------- RICH HEADER ----------------

    console.print(
        Panel(
            "[bold cyan]HEXSCOPE[/bold cyan]\n"
            "[dim]Binary File Analyzer | Version 1.0[/dim]",
            border_style="bright_blue",
            box=box.DOUBLE
        )
    )

    # ---------------- SIGNATURE REPORT ----------------

    status = (
        "[bold green]Signature recognized[/bold green]"
        if file_type != "Unknown"
        else "[bold yellow]Unknown file type[/bold yellow]"
    )

    signature_table = Table(
        title="SIGNATURE ANALYSIS",
        box=box.ROUNDED,
        border_style="bright_blue",
        expand=True
    )

    signature_table.add_column("Property", style="cyan")
    signature_table.add_column("Result", style="white")

    signature_table.add_row("File", os.path.basename(path))
    signature_table.add_row("Detected Format", file_type)
    signature_table.add_row("Status", status)

    console.print(signature_table)

    # ---------------- HEX DUMP ----------------

    count = 0

    dump_table = Table(
        title="HEXADECIMAL DUMP",
        box=box.SIMPLE_HEAVY,
        border_style="bright_blue",
        header_style="bold cyan",
        expand=True
    )

    dump_table.add_column("OFFSET", style="bright_blue", width=12)
    dump_table.add_column("HEX DATA", style="white", ratio=3)
    dump_table.add_column("ASCII", style="green", ratio=1)

    with open(output_path, "w", encoding="utf-8") as output:

        output.write(
            "Offset                         Hexdata                          Ascii\n"
        )

        output.write(
            "-------------------------------------------------------------------------------------------------------\n"
        )

        while True:

            data = f.read(16)

            if data == b'':
                break

            offset = f"{count:08X}"
            count += len(data)

            hexdata = data.hex(' ').upper().ljust(47)

            Ascii = ''.join(
                chr(var) if 32 <= var <= 126 else '.'
                for var in data
            )

            f_data = f"{offset}    {hexdata}    {Ascii}\n"

            output.write(f_data)

            dump_table.add_row(
                offset,
                hexdata,
                Ascii
            )

        # ---------------- FILE INFORMATION ----------------

        info = (
            f"\nFile Type : {file_type}\n"
            f"File      : {os.path.basename(path)}\n"
            f"File Size : {count / 1024:.2f} KiB\n"
        )

        output.write(info)

    console.print()
    console.print(dump_table)

    # ---------------- FINAL REPORT ----------------

    report = Table(
        title="ANALYSIS REPORT",
        box=box.ROUNDED,
        border_style="bright_blue",
        expand=True
    )

    report.add_column("Property", style="cyan")
    report.add_column("Result", style="white")

    report.add_row("Total Bytes", str(count))
    report.add_row("Hex Dump", "[bold green]Generated[/bold green]")
    report.add_row("Output File", output_path)

    console.print()
    console.print(report)

    console.print(
        Panel(
            "[bold green]ANALYSIS COMPLETED[/bold green]\n"
            "[dim]Hex dump successfully saved.[/dim]",
            border_style="green",
            box=box.ROUNDED
        )
    )
