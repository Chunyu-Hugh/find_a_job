#!/usr/bin/env python3
"""Diagnose HigherEdJobs pagination: find the URL form that actually turns pages.
Safe to delete after."""
import re, requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

def codes(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        cs = [re.search(r"JobCode=(\d+)", a["href"]).group(1)
              for a in soup.select("div.row.record a[href*='details.cfm']")
              if re.search(r"JobCode=(\d+)", a["href"])]
        # also look for pagination links / result count on the page
        pag = soup.select("a[href*='StartRow'], a[href*='startrow'], ul.pagination a, a.page-link")
        pag_hrefs = sorted(set(a.get("href","")[:90] for a in pag))[:8]
        total = ""
        m = re.search(r"([\d,]+)\s+(?:jobs|results|positions)", r.text, re.I)
        if m: total = m.group(0)
        return r.status_code, cs, pag_hrefs, total
    except Exception as e:
        return "ERR", [str(e)], [], ""

CAT = 102
forms = {
    "faculty StartRow=1":   f"https://www.higheredjobs.com/faculty/search.cfm?JobCat={CAT}&StartRow=1&NumJobs=25",
    "faculty StartRow=26":  f"https://www.higheredjobs.com/faculty/search.cfm?JobCat={CAT}&StartRow=26&NumJobs=25",
    "faculty Page=2":       f"https://www.higheredjobs.com/faculty/search.cfm?JobCat={CAT}&Page=2&NumJobs=25",
    "faculty StartRow=26 noNum": f"https://www.higheredjobs.com/faculty/search.cfm?JobCat={CAT}&StartRow=26",
    "faculty page 2 path":  f"https://www.higheredjobs.com/faculty/search.cfm?JobCat={CAT}&StartRow=26&SortBy=1&Keyword=&PosType=",
}
first = None
for name, url in forms.items():
    st, cs, pag, total = codes(url)
    tag = ""
    if first is None:
        first = cs
        tag = "(baseline page 1)"
    else:
        same = cs == first
        overlap = len(set(cs) & set(first))
        tag = f"SAME-as-p1={same}  overlap={overlap}/{len(cs)}"
    print(f"\n[{name}] HTTP {st}  n={len(cs)}  {tag}")
    print(f"   total-on-page: {total!r}")
    print(f"   first codes: {cs[:5]}")
    if pag:
        print(f"   pagination hrefs seen: {pag}")
