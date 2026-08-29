"""
Script to inspect layout and text extraction of downloaded PBS PDF Annexure files.
"""

import os
from pathlib import Path
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
PBS_DIR = BASE_DIR / "pbs_monthly_data"
pdf_files = sorted([f for f in os.listdir(PBS_DIR) if f.endswith(".pdf")])

print(f"Found {len(pdf_files)} PDF files in {PBS_DIR.name}:")

for fname in [pdf_files[0], pdf_files[len(pdf_files)//2], pdf_files[-1]]:
    fpath = PBS_DIR / fname
    print("\n" + "=" * 60)
    print(f"File: {fname}")
    reader = PdfReader(fpath)
    print(f"Pages: {len(reader.pages)}")
    for p_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"--- Page {p_idx+1} (Length: {len(text)}) ---")
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:20]:
            print(f"  {line}")
        print("  ...")
        for line in lines[-5:]:
            print(f"  {line}")
