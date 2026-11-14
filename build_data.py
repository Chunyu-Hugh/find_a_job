#!/usr/bin/env python3
"""
build_data.py — rebuild data.json for the CS Faculty Job Atlas.

Pipeline:
  1. Scrape HigherEdJobs (CS, Data Science, Computer Eng, Electrical Eng)
  2. Scrape the CRA Job Board
  3. Clean, dedupe (within and across sources)
  4. Classify each job: Carnegie tier (official 2025), HBCU flag, position type,
     research-direction tags
  5. Geocode city+state -> lat/lng (offline, via geonamescache + manual coords)
  6. Write data.json (same schema the web page reads)

Run:  python build_data.py
Deps: requests, beautifulsoup4, geonamescache   (see requirements.txt)
Keeps the fixed US state-border path from states_path.txt.

Designed to run unattended (e.g. in GitHub Actions). It is defensive: if one
source fails or a site's markup shifts, it logs a warning and continues with
whatever it did collect, so a partial refresh still succeeds.
"""
import re, sys, json, time, html, datetime, pathlib
import requests
from bs4 import BeautifulSoup

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from carnegie2025 import carnegie, norm            # official 2025 R1/R2 classifier
from hbcu import is_hbcu                            # official HBCU flag

UA = {"User-Agent": "Mozilla/5.0 (compatible; CSJobAtlas/1.0; research/non-commercial)"}
TIMEOUT = 30
RETRIES = 3

def get(url, **kw):
    """GET with retries; returns response or None (never raises)."""
    for i in range(RETRIES):
        try:
            r = requests.get(url, headers=UA, timeout=TIMEOUT, **kw)
            if r.status_code == 200:
                return r
            print(f"  [warn] {url} -> HTTP {r.status_code}")
        except Exception as e:
            print(f"  [warn] {url} -> {e}")
        time.sleep(2 * (i + 1))
    return None

# ---------------------------------------------------------------- HigherEdJobs
# Category codes: CS=102, Data Science=290, Computer Eng=116, Electrical Eng=117
HEJ_CATS = {102: "Computer Science", 290: "Data Science",
            116: "Computer Engineering", 117: "Electrical Engineering"}

def _hej_textnodes(col):
    """Return the non-empty text lines inside a col-sm-7 block, split on <br>.
    Layout is:  <a>title</a> <br> institution <br> 'City, ST'."""
    from bs4 import NavigableString
    lines, cur = [], ""
    for node in col.children:
        if getattr(node, "name", None) == "br":
            if cur.strip():
                lines.append(cur.strip())
            cur = ""
        elif getattr(node, "name", None) == "a":
            # the title link; keep as its own line
            if cur.strip():
                lines.append(cur.strip())
            lines.append(node.get_text(" ", strip=True))
            cur = ""
        elif isinstance(node, NavigableString):
            cur += " " + str(node)
        else:
            cur += " " + node.get_text(" ", strip=True)
    if cur.strip():
        lines.append(cur.strip())
    return [l for l in lines if l]

def scrape_higheredjobs():
    jobs = []
    seen_codes = set()
    prev_first = {c: None for c in HEJ_CATS}      # last page's first code, per category
    done = set()                                   # categories that reached their end
    # Per-category page budget: CS (102) has by far the most US faculty jobs and
    # its deeper pages are dense with them, so give it more pages; the three
    # engineering/data categories contribute mostly from their first pages.
    PAGE_BUDGET = {102: 8, 290: 3, 116: 3, 117: 3}
    MAX_PAGES = max(PAGE_BUDGET.values())
    # Round-robin across categories so each one's early (most valuable) pages
    # are fetched before HigherEdJobs starts rate-limiting a long single-category run.
    for page in range(1, MAX_PAGES + 1):
        if len(done) == len(HEJ_CATS):
            break
        for cat, label in HEJ_CATS.items():
            if cat in done or page > PAGE_BUDGET[cat]:
                continue
            url = (f"https://www.higheredjobs.com/faculty/search.cfm"
                   f"?JobCat={cat}&Page={page}&NumJobs=25&SortBy=1")
            r = get(url)
            if not r:
                print(f"  HEJ {label}: page {page} fetch failed")
                time.sleep(4)
                continue                           # try this category again next round
            soup = BeautifulSoup(r.text, "html.parser")
            rows = soup.select("div.row.record")
            if not rows:
                done.add(cat)
                continue
            page_codes = [re.search(r"JobCode=(\d+)", row.select_one("a[href*='details.cfm']")["href"]).group(1)
                          for row in rows if row.select_one("a[href*='details.cfm']")]
            if prev_first[cat] and page_codes and page_codes[0] == prev_first[cat]:
                done.add(cat)                       # wrapped back to page 1 = past the end
                continue
            prev_first[cat] = page_codes[0] if page_codes else prev_first[cat]
            new_on_page = [c for c in page_codes if c not in seen_codes]
            if page > 1 and not new_on_page:
                done.add(cat)
                continue
            added = 0
            for row in rows:
                col = row.select_one("div.col-sm-7")
                if not col:
                    continue
                a = col.select_one("a[href*='details.cfm']")
                if not a:
                    continue
                title = a.get_text(" ", strip=True)
                href = a.get("href", "")
                mcode = re.search(r"JobCode=(\d+)", href)
                code = mcode.group(1) if mcode else None
                if code and code in seen_codes:
                    continue
                if code:
                    seen_codes.add(code)
                if href and not href.startswith("http"):
                    href = "https://www.higheredjobs.com/faculty/" + href.lstrip("/")
                lines = _hej_textnodes(col)
                lines = [l for l in lines if l != title]
                inst = lines[0] if lines else ""
                loc = lines[1] if len(lines) > 1 else ""
                jobs.append({"t": title, "i": inst, "loc": loc, "u": href,
                             "src": "HEJ", "cat": label, "p": ""})
                added += 1
            print(f"  HEJ {label}: page {page}, +{added}")
            if len(rows) < 25:
                done.add(cat)
            time.sleep(2)                           # pace between requests
    print(f"HigherEdJobs: {len(jobs)} raw rows")
    return jobs

# ---------------------------------------------------------------------- CRA
def scrape_cra():
    jobs = []
    page = 1
    while True:
        url = f"https://careercenter.cra.org/jobs/?page={page}"
        r = get(url)
        if not r:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("li.search-item")
        if not cards:
            break
        added = 0
        for c in cards:
            a = c.select_one("h2 a[href*='/job/'], a[data-testid='jobs-list-item-link']")
            if not a:
                continue
            title = a.get_text(" ", strip=True)
            href = a.get("href", "")
            if href and not href.startswith("http"):
                href = "https://careercenter.cra.org" + href
            # institution + location are the two div.small inside div.location
            smalls = c.select("div.location div.small")
            inst = smalls[0].get_text(" ", strip=True) if smalls else ""
            loc = smalls[1].get_text(" ", strip=True) if len(smalls) > 1 else ""
            if not inst:
                logo = c.select_one("img[alt]")
                if logo:
                    inst = logo.get("alt", "").replace(" logo", "").strip()
            jobs.append({"t": title, "i": inst, "loc": loc, "u": href,
                         "src": "CRA", "cat": "Computer Science", "p": ""})
            added += 1
        print(f"  CRA: page {page}, +{added}")
        if added == 0 or len(cards) < 10:
            break
        page += 1
        if page > 60:
            break
        time.sleep(1)
    print(f"CRA: {len(jobs)} raw rows")
    return jobs

# -------------------------------------------------------------- classification
def position_type(title):
    t = title.lower()
    if re.search(r"tenure.track|tenured|assistant professor|associate professor|full professor", t):
        if "non-tenure" in t or "teaching professor" in t: return "Teaching/NTT"
        return "Tenure-track/Tenured"
    if re.search(r"lecturer|instructor|teaching|adjunct", t):
        return "Teaching/NTT" if "adjunct" not in t else "Adjunct/PT"
    if re.search(r"post.?doc", t): return "Postdoc"
    if re.search(r"research (scientist|professor|faculty|associate)", t): return "Research-track"
    if re.search(r"chair|dean|director|head", t): return "Leadership/Chair"
    if re.search(r"fellow", t): return "Fellowship"
    if re.search(r"professor|faculty", t): return "Tenure-track/Tenured"
    return "Other"

TAG_RULES = [
    ("AI/ML", r"artificial intelligence|machine learning|deep learning|\bai\b|\bml\b|foundation model|"
              r"generative|neural|ai.?for.?science|ai4science|scientific machine learning|sciml|"
              r"physics.informed|surrogate model|data scien"),
    ("Robotics", r"robot|autonomous|control system|mechatron"),
    ("Vision", r"computer vision|image|visual comput"),
    ("NLP", r"natural language|\bnlp\b|computational linguist|speech"),
    ("Bio/Health", r"bioinformatic|computational bio|health|medical|biomedical|genomic|clinical"),
    ("Quantum", r"quantum"),
    ("Systems/Hardware", r"systems|architecture|hardware|embedded|vlsi|circuit|fpga|compiler|operating system|distributed"),
    ("Security/Cyber", r"security|cyber|cryptograph|privacy|network security"),
    ("HCI", r"human.computer|\bhci\b|user experience|interaction design"),
    ("Theory", r"theory|algorithm|theoretical|complexity"),
    ("CS-Ed", r"computer science education|cs.?ed|teaching of computing|broadening participation"),
]
def tags(title):
    t = title.lower()
    out = [name for name, pat in TAG_RULES if re.search(pat, t)]
    return out or ["General/Other"]

# FAMU and a few HBCU/branch names the Carnegie matcher misses by short form
CARNEGIE_PATCH = {
    norm("Florida A&M University"): "R1",
    norm("Florida Agricultural and Mechanical University"): "R1",
}
def carnegie_tier(inst):
    c = carnegie(inst)
    if c: return c
    n = norm(inst)
    if n in CARNEGIE_PATCH: return CARNEGIE_PATCH[n]
    # sub-buckets for non-R1/R2
    low = inst.lower()
    if "community college" in low or "technical college" in low:
        return "Community College"
    if re.search(r"\bcollege\b", low) and "university" not in low:
        return "College/Other"
    if "university" in low or "institute" in low or "school of" in low or "polytechnic" in low:
        return "Other 4-yr"
    return "Other"

# ---------------------------------------------------------------- geocoding
def build_geocoder():
    import geonamescache
    gc = geonamescache.GeonamesCache()
    cities = gc.get_cities()
    idx = {}
    for cid, c in cities.items():
        if c.get("countrycode") != "US":
            continue
        key = (c["name"].lower(), c["admin1code"])
        # keep the most populous match per (name,state)
        if key not in idx or c.get("population", 0) > idx[key][2]:
            idx[key] = (c["latitude"], c["longitude"], c.get("population", 0))
    return idx

MANUAL = {  # campus towns / names geonames misses
    ("new york", "NY"): (40.7128, -74.0060), ("college station", "TX"): (30.628, -96.334),
    ("west lafayette", "IN"): (40.4259, -86.9081), ("ann arbor", "MI"): (42.2808, -83.7430),
    ("chapel hill", "NC"): (35.9132, -79.0558), ("college park", "MD"): (38.9897, -76.9378),
    ("storrs", "CT"): (41.8084, -72.2495), ("blacksburg", "VA"): (37.2296, -80.4139),
    ("amherst", "MA"): (42.3732, -72.5199), ("ithaca", "NY"): (42.4440, -76.5019),
    ("norman", "OK"): (35.2226, -97.4395), ("boulder", "CO"): (40.0150, -105.2705),
    ("stillwater", "OK"): (36.1156, -97.0584), ("manhattan", "KS"): (39.1836, -96.5717),
    ("west point", "NY"): (41.3915, -73.9560),
}
def geocode(jobs, idx):
    hits = 0
    for j in jobs:
        key = (j["c"].lower(), j["s"])
        ll = MANUAL.get(key)
        if not ll and key in idx:
            ll = (idx[key][0], idx[key][1])
        if not ll:  # loose: match city name in same state
            for (nm, st), v in idx.items():
                if st == j["s"] and (nm == j["c"].lower() or j["c"].lower() in nm or nm in j["c"].lower()):
                    ll = (v[0], v[1]); break
        if ll:
            j["lat"], j["lng"] = round(float(ll[0]), 4), round(float(ll[1]), 4)
            hits += 1
    return hits

# ---------------------------------------------------------------- dedupe
STATE_NAMES = {
 "alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA",
 "colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA",
 "hawaii":"HI","idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS",
 "kentucky":"KY","louisiana":"LA","maine":"ME","maryland":"MD","massachusetts":"MA",
 "michigan":"MI","minnesota":"MN","mississippi":"MS","missouri":"MO","montana":"MT",
 "nebraska":"NE","nevada":"NV","new hampshire":"NH","new jersey":"NJ","new mexico":"NM",
 "new york":"NY","north carolina":"NC","north dakota":"ND","ohio":"OH","oklahoma":"OK",
 "oregon":"OR","pennsylvania":"PA","rhode island":"RI","south carolina":"SC",
 "south dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT",
 "virginia":"VA","washington":"WA","west virginia":"WV","wisconsin":"WI","wyoming":"WY",
 "district of columbia":"DC","washington dc":"DC","puerto rico":"PR"}
def split_loc(loc):
    """Return (city, 2-letter-state). Handles 'City, ST', 'City, State Name',
    and a trailing country. Non-US -> empty state (filtered out later)."""
    loc = re.sub(r"\s+", " ", (loc or "").strip())
    if "," not in loc:
        return loc, ""
    parts = [p.strip() for p in loc.split(",")]
    city = parts[0]
    tail = parts[-1]
    low = tail.lower()
    if low in STATE_NAMES:
        return city, STATE_NAMES[low]
    up = tail[:2].upper()
    # second-to-last may be the state when last is a country ("City, ST, USA")
    if len(parts) >= 3:
        mid = parts[-2].lower()
        if mid in STATE_NAMES:
            return city, STATE_NAMES[mid]
        if re.fullmatch(r"[A-Za-z]{2}", parts[-2]):
            up = parts[-2][:2].upper()
    return city, up

STOP = re.compile(r"\b(faculty|position|positions|open rank|tenure|track|assistant|associate|professor|of|in|the|and|department|for)\b")
def title_key(t):
    return re.sub(r"\s+", " ", STOP.sub(" ", t.lower())).strip()

def dedupe(jobs):
    # within source: by URL
    by_url = {}
    for j in jobs:
        by_url.setdefault(j["u"] or (j["t"] + j["i"]), j)
    jobs = list(by_url.values())
    # cross source: (institution canon, state, title-key) ; keep CRA over HEJ
    out = {}
    for j in sorted(jobs, key=lambda x: 0 if x["src"] == "CRA" else 1):
        k = (norm(j["i"]), j["s"], title_key(j["t"]))
        if k not in out:
            out[k] = j
    return list(out.values())

# ---------------------------------------------------------------- main
def main():
    raw = scrape_higheredjobs() + scrape_cra()
    if not raw:
        print("ERROR: no jobs scraped from any source; keeping existing data.json")
        return 1

    # normalize location
    for j in raw:
        c, s = split_loc(j.pop("loc", ""))
        j["c"], j["s"] = c, s
        j["jt"] = position_type(j["t"])
        j["tg"] = tags(j["t"])
        j["cn"] = carnegie_tier(j["i"])
        j["hb"] = is_hbcu(j["i"])            # NEW: HBCU flag

    US_STATES = {"AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL",
        "IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
        "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX",
        "UT","VT","VA","WA","WV","WI","WY","DC","PR","VI","GU"}
    us = [j for j in raw if j.get("s", "") in US_STATES]
    intl = len(raw) - len(us)
    us = dedupe(us)

    # Optional LLM fallback: relabel "General/Other" titles if a key is set.
    try:
        from llm_tag import enrich as llm_enrich
        llm_enrich(us)
    except Exception as e:
        print(f"  [llm] skipped: {e}")

    idx = build_geocoder()
    geo = geocode(us, idx)

    # assemble output rows in the page's schema
    rows = []
    for j in us:
        rows.append({
            "t": j["t"], "i": j["i"], "c": j["c"], "s": j["s"],
            "lat": j.get("lat"), "lng": j.get("lng"),
            "jt": j["jt"], "tg": j["tg"], "cn": j["cn"], "hb": j["hb"],
            "src": j["src"], "u": j["u"], "p": j.get("p", ""),
        })

    from collections import Counter
    by_carn = dict(Counter(j["cn"] for j in rows))
    hbcu_n = sum(1 for j in rows if j["hb"])

    states_path = (HERE / "states_path.txt").read_text().strip()
    data = {
        "meta": {
            "generated": datetime.date.today().isoformat(),
            "sources": [
                "HigherEdJobs - Computer Science, Data Science, Computer & Electrical Engineering",
                "CRA Job Board (careercenter.cra.org)",
            ],
            "note_ajo": ("Covers two aggregators (HigherEdJobs and CRA). "
                         "AcademicJobsOnline and schools' own HR portals are not included, "
                         "so some R1 and SciML-targeted positions will not appear here."),
            "total_us": len(rows), "geocoded": geo, "intl_count": intl,
            "by_carnegie": by_carn, "hbcu_count": hbcu_n,
            "carnegie_source": ("Official 2025 Carnegie Research Activity Designation "
                                "(ACE and Indiana University): 187 R1, 139 R2."),
            "hbcu_source": "U.S. Dept. of Education, White House Initiative on HBCUs.",
        },
        "jobs": rows,
        "states_path": states_path,
    }
    out = HERE / "data.json"
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    print(f"\nWrote {out}")
    print(f"  US jobs: {len(rows)}  geocoded: {geo}  intl excluded: {intl}")
    print(f"  Carnegie: {by_carn}")
    print(f"  HBCU: {hbcu_n}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
