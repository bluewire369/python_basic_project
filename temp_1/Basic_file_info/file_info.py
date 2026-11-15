import os
import argparse

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

file_name = 'Not found'
file_type = 'Not found'
file_size = 'Not found'
file_extension = 'Not found'
file_validation = 'Mismatch'
metadata = 'Not found'

# ---------------- SIGNATURES ----------------

signatures = {
    "JPEG": bytes.fromhex("FFD8FF"),
    "PNG": bytes.fromhex("89504E470D0A1A0A"),
    "GIF87a": bytes.fromhex("474946383761"),
    "GIF89a": bytes.fromhex("474946383961"),
    "PDF": bytes.fromhex("25504446"),
    "ZIP": bytes.fromhex("504B0304"),
    "BMP": bytes.fromhex("424D"),
    "TIFF (Little Endian)": bytes.fromhex("49492A00"),
    "TIFF (Big Endian)": bytes.fromhex("4D4D002A")
}

# ---------------- EXTENSION MAP ----------------

extension_map = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".jpe": "JPEG",
    ".jfif": "JPEG",
    ".jif": "JPEG",
    ".png": "PNG",
    ".gif": "GIF",
    ".tif": "TIFF",
    ".tiff": "TIFF",
    ".bmp": "BMP",
    ".dib": "BMP",
    ".pdf": "PDF",
    ".zip": "ZIP"
}

# ---------------- FUNCTIONS ----------------

def check_exist(usr_path):
    return os.path.isfile(usr_path)


def read_file(usr_path, size):
    with open(usr_path, 'rb') as f:
        data = f.read(size)
    return data


# ---------------- ARGPARSE ----------------

parser = argparse.ArgumentParser(
    description="MetaScope - Binary Metadata Inspector"
)

parser.add_argument(
    "--file",
    required=True,
    help="Path of the file to inspect"
)

args = parser.parse_args()
path = args.file


# ---------------- FILE INSPECTION ----------------

if check_exist(path):

    file_name = os.path.basename(path)
    file_extension = os.path.splitext(path)[1]

    data = read_file(path, 50)
    read_1 = data[:40]

    for key, value in signatures.items():
        if read_1.startswith(value):
            file_type = key
            break

    # File size calculation

    count = 0

    with open(path, 'rb') as s:
        while True:
            data1 = s.read(1024 * 1024)

            if not data1:
                break

            count += len(data1)

    kilo_bytes = count / 1000
    mega_bytes = kilo_bytes / 1000
    giga_bytes = mega_bytes / 1000

    if kilo_bytes > 999:
        if mega_bytes > 999:
            file_size = f"{giga_bytes:.2f} GB"
        else:
            file_size = f"{mega_bytes:.2f} MB"
    else:
        file_size = f"{kilo_bytes:.2f} KB"

    # Extension validation

    val = None

    for keys, values in extension_map.items():

        if keys == file_extension:
            val = values

            if values == file_type:
                file_validation = 'Match'

    # ASCII extraction

    extracted = ''

    with open(path, "rb") as n:
        data2 = n.read(500)

        for useful in data2:
            if 32 <= useful <= 126:
                extracted += chr(useful)
            elif useful == 44:
                extracted += "\n"

    metadata = extracted

    # ---------------- RICH OUTPUT ----------------

    table = Table(title="File Information", show_header=True)

    table.add_column("Property", style="cyan")
    table.add_column("Result", style="white")

    table.add_row("File Name", file_name)
    table.add_row("File Size", file_size)
    table.add_row("Detected Format", file_type)
    table.add_row("File Extension", file_extension)
    table.add_row("Extension Validation", file_validation)

    console.print(
        Panel(
            "[bold cyan]METASCOPE[/bold cyan]\n"
            "[dim]Binary Metadata Inspector[/dim]",
            border_style="cyan"
        )
    )

    console.print(table)

    console.print(
        Panel(
            metadata[10:1000] or "No readable text found",
            title="Extracted ASCII Text",
            border_style="green"
        )
    )

else:
    console.print("[bold red]Error:[/bold red] File does not exist.")
