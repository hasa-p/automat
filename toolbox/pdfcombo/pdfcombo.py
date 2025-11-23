#!/usr/bin/env python3
"""
Merge every PDF inside the specified directory.
Output: merged.pdf inside the same directory.

Install dependency:
    pip install pypdf
"""

from pathlib import Path
from pypdf import PdfWriter

# ------------------------------------------------------------------
# PATH CONFIGURATION
# ------------------------------------------------------------------
RESOURCES_FOLDER = Path(__file__).with_name("resources")
# ------------------------------------------------------------------

def prefix_parts(filename: str):
    """Turns a filename prefix into a tuple of
    (type_flag, value) for natural sorting.
    
    Examples:
      '13.3-a' -> ((0, 13), (0, 3), (1, 'a'))
    """
    prefix = filename.split("_", 1)[0].replace("-", ".")
    parts = prefix.split(".")
    key = []
    for p in parts:
        if p.isdigit():
            key.append((0, int(p)))
        else:
            key.append((1, p.lower()))
    return tuple(key)

def gather_pdfs(folder: Path):
    """Return a list of Path objects in natural order."""
    files = [p for p in folder.glob("*.pdf") if "_" in p.stem]
    # Use the stem (name without suffix) as that's what prefix_parts expects.
    return sorted(files, key=lambda p: prefix_parts(p.stem))

def merge_pdfs(file_list, output: Path):
    writer = PdfWriter()
    for pdf in file_list:
        try:
            writer.append(str(pdf))
        except Exception as exc:  # continue if one file is bad
            print(f"Warning: couldn't append {pdf}: {exc}")
    # Write to a binary file handle
    with output.open("wb") as f:
        writer.write(f)
    writer.close()
    print(f"Merged {len(file_list)} files into {output}")

def main():
    if not RESOURCES_FOLDER.is_dir():
        print(f"Folder not found: {RESOURCES_FOLDER}")
        return

    pdfs = gather_pdfs(RESOURCES_FOLDER)
    if not pdfs:
        print("No PDF files found.")
        return

    merge_pdfs(pdfs, RESOURCES_FOLDER / "merged.pdf")

if __name__ == "__main__":
    main()
