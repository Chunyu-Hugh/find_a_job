#!/usr/bin/env python3
"""One-off diagnostic: print the real HTML structure of the two job sources
so we can fix the scraper selectors. Safe to delete after."""
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

def probe(name, url):
    print(f"\n{'='*70}\n{name}\n{url}\n{'='*70}")
    try:
        r = requests.get(url, headers=UA, timeout=30)
        print(f"HTTP {r.status_code}, {len(r.text)} bytes")
        soup = BeautifulSoup(r.text, "html.parser")
        print("TITLE:", (soup.title.string if soup.title else "")[:100])
        links = soup.find_all("a", href=True)
        job_links = [a for a in links if any(k in a["href"].lower()
                     for k in ["details.cfm", "/job/", "jobdetail", "/jobs/", "display.cfm"])]
        print(f"\nTotal <a>: {len(links)}; job-detail-looking links: {len(job_links)}")
        for a in job_links[:6]:
            print(f"  href={a['href'][:80]!r}  text={a.get_text(strip=True)[:60]!r}")
            p = a
            chain = []
            for _ in range(4):
                p = p.parent
                if p is None or p.name is None:
                    break
                cls = ".".join(p.get("class", []))
                chain.append(f"{p.name}{('.'+cls) if cls else ''}")
            print(f"     parents: {' > '.join(chain)}")
        # Also show the first 1200 chars of body text to eyeball layout / blocks
        print("\n--- body snippet ---")
        print(r.text[r.text.lower().find("<body"):r.text.lower().find("<body")+1200])
    except Exception as e:
        print("ERROR:", e)

probe("HigherEdJobs CS (102)",
      "https://www.higheredjobs.com/faculty/search.cfm?JobCat=102")
probe("HigherEdJobs search_action",
      "https://www.higheredjobs.com/search/advanced_action.cfm?JobCat=102&PosType=1")
probe("CRA Job Board",
      "https://careercenter.cra.org/jobs/")
