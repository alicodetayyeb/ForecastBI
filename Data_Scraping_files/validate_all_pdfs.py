"""
Validation suite to check extraction accuracy on all 28 PDF Annexure files.
"""

import os
import re
from pathlib import Path
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
PBS_DIR = BASE_DIR / "pbs_monthly_data"
pdf_files = sorted([f for f in os.listdir(PBS_DIR) if f.endswith(".pdf")])

print(f"Validating {len(pdf_files)} PDF files in {PBS_DIR.name}...")

def parse_pdf_all_items(filepath):
    reader = PdfReader(filepath)
    extracted = {}
    
    full_text = ""
    for p in reader.pages:
        full_text += p.extract_text() + "\n"
        
    for line in full_text.split("\n"):
        line = line.strip()
        m = re.match(r'^(\d{1,2})\s+([A-Za-z].*?)\s+(\d+\.\d{2}.*)$', line)
        if m:
            sno = int(m.group(1))
            if 1 <= sno <= 51:
                desc_part = m.group(2).strip()
                nums_part = m.group(3).strip()
                floats = [float(t) for t in re.findall(r'[-+]?\d*\.?\d+', nums_part) if t not in ['-', '+', '.']]
                
                nat_avg = None
                if len(floats) >= 18:
                    nat_avg = floats[17]
                elif len(floats) > 0:
                    nat_avg = sum(floats[:min(17, len(floats))]) / min(17, len(floats))
                    
                if sno not in extracted or (nat_avg is not None and extracted[sno]["national_average"] is None):
                    extracted[sno] = {
                        "sno": sno,
                        "desc_raw": desc_part,
                        "floats_count": len(floats),
                        "national_average": nat_avg
                    }
    return extracted

for f in pdf_files:
    res = parse_pdf_all_items(PBS_DIR / f)
    missing = [i for i in range(1, 52) if i not in res]
    print(f"[{f}] Extracted {len(res)}/51 items | Missing: {len(missing)} | Tomatoes: Rs {res.get(23, {}).get('national_average')}")
