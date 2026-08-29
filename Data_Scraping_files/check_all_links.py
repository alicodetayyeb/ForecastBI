"""
Script to list all months and check their Annexure-1 URLs in the PBS table array.
"""

import re
import urllib3
import requests
import chompjs

urllib3.disable_warnings()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

resp = requests.get("https://www.pbs.gov.pk/price-statistics/", headers=headers, verify=False, timeout=20)
match = re.search(r'const\s+cpidata1\s*=\s*(\[\s*\{.*?\}\s*\]);', resp.text, re.DOTALL)
data = chompjs.parse_js_object(match.group(1))

print(f"Total months in table: {len(data)}")
for i, item in enumerate(data):
    month_str = item.get("month", "").strip()
    annex_url = item.get("annex", "").strip() if item.get("annex") else "None"
    print(f"{i+1:2d}. Month: {month_str:20s} | Annex link: {annex_url}")
