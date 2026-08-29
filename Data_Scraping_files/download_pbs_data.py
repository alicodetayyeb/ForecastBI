import os
import re
import sys
import time
import urllib3
import requests
import chompjs
from datetime import datetime

# Configure UTF-8 encoding for standard outputs
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://www.pbs.gov.pk/price-statistics/"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pbs_monthly_data")
MISSING_LOG_FILE = os.path.join(OUTPUT_DIR, "missing_months.txt")
DELAY_BETWEEN_DOWNLOADS = 1.5  # 1.5 seconds delay between downloads

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

MONTH_MAP = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12
}

def get_target_60_months():
    """Generates a list of the last 60 months (YYYY-MM) ending at current month (2026-08)."""
    current_year = 2026
    current_month = 8
    target_months = []
    
    y = current_year
    m = current_month
    for _ in range(60):
        target_months.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    return target_months

def parse_month_string(m_str):
    """Parses arbitrary month string (e.g. 'July 2026', 'Feb 2026') to 'YYYY-MM' format."""
    if not m_str:
        return None
    m_clean = m_str.strip().lower()
    match = re.search(r'([a-z]+)[^\d]*(\d{4})', m_clean)
    if match:
        m_name = match.group(1)
        year = int(match.group(2))
        month_num = MONTH_MAP.get(m_name)
        if month_num:
            return f"{year:04d}-{month_num:02d}"
    return None

def main():
    print("=" * 70)
    print("PBS Monthly Price Index Annexure-1 Downloader (5 Years / 60 Months)")
    print("=" * 70)
    
    # 1. Create target directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[+] Output folder: {OUTPUT_DIR}")
    
    # Generate expected 60 months range
    target_60_months = get_target_60_months()
    print(f"[+] Target 60-Month Window: {target_60_months[-1]} to {target_60_months[0]}")
    
    # 2. Fetch page and extract Monthly Consumer Price Index dataset
    print(f"\n[+] Fetching page: {BASE_URL} ...")
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, verify=False, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[-] Error fetching source page: {e}")
        sys.exit(1)
        
    print(f"[OK] Page loaded successfully ({len(resp.text):,} bytes)")
    
    # Extract cpidata1 array (the exact data model backing reportTable1)
    match = re.search(r'const\s+cpidata1\s*=\s*(\[\s*\{.*?\}\s*\]);', resp.text, re.DOTALL)
    if not match:
        print("[-] Could not find 'cpidata1' table dataset in the page source.")
        sys.exit(1)
        
    try:
        raw_items = chompjs.parse_js_object(match.group(1))
        print(f"[OK] Extracted {len(raw_items)} month records from Monthly CPI table")
    except Exception as e:
        print(f"[-] Error parsing table dataset: {e}")
        sys.exit(1)
        
    # Map extracted records by YYYY-MM
    table_data_by_month = {}
    for item in raw_items:
        m_raw = item.get("month", "")
        ym = parse_month_string(m_raw)
        if ym:
            table_data_by_month[ym] = item
            
    print(f"[OK] Standardized {len(table_data_by_month)} valid months in table")
    
    # 3. Process the target 60 months
    downloaded_count = 0
    missing_records = []
    
    print("\n[+] Processing downloads...")
    for ym in target_60_months:
        if ym not in table_data_by_month:
            reason = "Month record not published in table on PBS website"
            missing_records.append((ym, reason))
            print(f"  [-] {ym}: MISSING ({reason})")
            continue
            
        record = table_data_by_month[ym]
        annex_url = record.get("annex", "").strip() if record.get("annex") else None
        
        if not annex_url or annex_url == "" or annex_url.lower() == "none":
            reason = "No Annexure-1 download link provided in table"
            missing_records.append((ym, reason))
            print(f"  [-] {ym}: MISSING ({reason})")
            continue
            
        # Determine file extension
        ext = ".xlsx"
        url_lower = annex_url.lower()
        if ".pdf" in url_lower:
            ext = ".pdf"
        elif ".xls" in url_lower and not ".xlsx" in url_lower:
            ext = ".xls"
            
        filename = f"{ym}_Annexure1{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Download file
        print(f"  [DL] {ym} -> Downloading '{filename}' ...", end="", flush=True)
        try:
            dl_resp = requests.get(annex_url, headers=HEADERS, verify=False, timeout=45)
            if dl_resp.status_code == 200 and len(dl_resp.content) > 0:
                with open(filepath, "wb") as f:
                    f.write(dl_resp.content)
                size_kb = len(dl_resp.content) / 1024
                print(f" Done ({size_kb:.1f} KB)")
                downloaded_count += 1
            else:
                reason = f"HTTP {dl_resp.status_code} when downloading from {annex_url}"
                missing_records.append((ym, reason))
                print(f" FAILED ({reason})")
        except Exception as e:
            reason = f"Download exception: {e}"
            missing_records.append((ym, reason))
            print(f" ERROR ({e})")
            
        # Politeness delay
        time.sleep(DELAY_BETWEEN_DOWNLOADS)
        
    # 4. Write missing months log
    with open(MISSING_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"PBS Monthly Price Index - Missing Months Log\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Target Months: {len(target_60_months)}\n")
        f.write(f"Total Missing / Unavailable: {len(missing_records)}\n\n")
        f.write("=" * 70 + "\n")
        f.write(f"{'Month (YYYY-MM)':<18} | Reason\n")
        f.write("-" * 70 + "\n")
        for ym, reason in missing_records:
            f.write(f"{ym:<18} | {reason}\n")
            
    # 5. Print Final Summary
    print("\n" + "=" * 70)
    print("EXECUTION SUMMARY")
    print("=" * 70)
    print(f"  * Total Months in 5-Year Target Window: {len(target_60_months)}")
    print(f"  * Total Months Found in PBS Table:      {len(table_data_by_month)}")
    print(f"  * Total Files Downloaded Successfully:  {downloaded_count}")
    print(f"  * Total Missing / Unavailable Months:   {len(missing_records)}")
    print(f"  * Output Directory:  {OUTPUT_DIR}")
    print(f"  * Missing Log:       {MISSING_LOG_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
