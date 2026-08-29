"""
Script to inspect the client-side JavaScript pagination logic for reportTable1.
"""

import re
import urllib3
import requests

urllib3.disable_warnings()

resp = requests.get("https://www.pbs.gov.pk/price-statistics/", verify=False, timeout=20)
scripts = re.findall(r'<script>(.*?)</script>', resp.text, re.DOTALL)
for s in scripts:
    if "cpidata1" in s:
        print("=== SCRIPT FOR TABLE 1 ===")
        cleaned = re.sub(r'const\s+cpidata1\s*=\s*\[.*?\];', 'const cpidata1 = [ /* items array */ ];', s, flags=re.DOTALL)
        print(cleaned[:1500])
