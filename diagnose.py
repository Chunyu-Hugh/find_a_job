#!/usr/bin/env python3
"""Inspect CRA location parsing: why do 529 raw CRA rows collapse to ~34 US jobs?"""
import re, requests, collections
from bs4 import BeautifulSoup
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

locs = []
inst_loc = []
for page in range(1, 6):   # first 5 pages is plenty to see the pattern
    r = requests.get(f"https://careercenter.cra.org/jobs/?page={page}", headers=UA, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    for c in soup.select("li.search-item"):
        smalls = c.select("div.location div.small")
        inst = smalls[0].get_text(" ", strip=True) if smalls else ""
        loc = smalls[1].get_text(" ", strip=True) if len(smalls) > 1 else ""
        locs.append(loc)
        if len(inst_loc) < 25:
            inst_loc.append((inst[:30], loc[:40], len(smalls)))

print(f"sampled {len(locs)} CRA rows")
print("\n--- 25 sample (institution | location | #small divs) ---")
for i, l, n in inst_loc:
    print(f"  {n}  {i:32s} | {l!r}")
print("\n--- location format tally ---")
has_comma = sum(1 for l in locs if "," in l)
empty = sum(1 for l in locs if not l.strip())
print(f"  with comma: {has_comma} | empty: {empty} | total: {len(locs)}")
# what do the last tokens look like?
tails = collections.Counter()
for l in locs:
    if "," in l:
        tails[l.rsplit(",",1)[-1].strip()[:15]] += 1
print("\n--- top 20 location tails (after last comma) ---")
for t, n in tails.most_common(20):
    print(f"  {n:3d}  {t!r}")
