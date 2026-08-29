"""
Script to inspect PBS page structure, arrays, and scripts.
"""

import re
import urllib3
import requests
import chompjs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

PAGES = [
    "https://www.pbs.gov.pk/price-statistics/",
    "https://www.pbs.gov.pk/cpi",
    "https://www.pbs.gov.pk/content/price-statistics"
]

def inspect_page_data():
    for url in PAGES:
        print(f"\n{'='*60}\nInspecting: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, verify=False, timeout=20)
            print(f"Status: {resp.status_code}, Content Size: {len(resp.text):,} bytes")
            matches = re.findall(r'const\s+([a-zA-Z0-9_]+)\s*=\s*(\[\s*\{.*?\}\s*\]);', resp.text, re.DOTALL)
            for name, arr in matches:
                try:
                    parsed = chompjs.parse_js_object(arr)
                    print(f"  Found array '{name}' with {len(parsed)} items")
                    if parsed and isinstance(parsed[0], dict) and 'month' in parsed[0]:
                        print(f"    Latest:   {parsed[0].get('month')}")
                        print(f"    Earliest: {parsed[-1].get('month')}")
                except Exception as e:
                    print(f"  Array '{name}' parsing error: {e}")
        except Exception as e:
            print(f"Failed to load {url}: {e}")

if __name__ == "__main__":
    inspect_page_data()
