#!/usr/bin/env python3
"""Check which HigherEdJobs JobCat codes actually return results."""
import re, requests
from bs4 import BeautifulSoup
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

def count(cat):
    url = f"https://www.higheredjobs.com/faculty/search.cfm?JobCat={cat}&Page=1&NumJobs=25&SortBy=1"
    try:
        r = requests.get(url, headers=UA, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("div.row.record")
        titles = [row.select_one("a[href*='details.cfm']").get_text(strip=True)[:45]
                  for row in rows[:3] if row.select_one("a[href*='details.cfm']")]
        return len(rows), titles
    except Exception as e:
        return "ERR", [str(e)]

# Probe a range of codes to find the real CS-family categories.
# Known: 102 works (CS). Test the ones we guessed plus neighbors.
for cat in [102, 290, 116, 117, 101, 103, 104, 105, 106, 107, 108, 109, 110,
            111, 112, 113, 114, 115, 118, 119, 120, 291, 292]:
    n, titles = count(cat)
    print(f"JobCat={cat}: {n} rows   {titles}")

# Also fetch the search form to read the real category dropdown values.
print("\n--- category dropdown options from the search form ---")
try:
    r = requests.get("https://www.higheredjobs.com/faculty/", headers=UA, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    for sel in soup.select("select"):
        name = sel.get("name","")
        if "cat" in name.lower() or "JobCat" in name:
            print(f"select name={name}")
            for opt in sel.select("option")[:60]:
                v = opt.get("value","")
                if v and ("comput" in opt.get_text().lower() or "data" in opt.get_text().lower()
                          or "electr" in opt.get_text().lower() or "engineer" in opt.get_text().lower()
                          or "information" in opt.get_text().lower()):
                    print(f"   {v} = {opt.get_text(strip=True)}")
except Exception as e:
    print("ERR", e)
