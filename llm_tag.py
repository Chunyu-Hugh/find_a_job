#!/usr/bin/env python3
"""
llm_tag.py — optional LLM fallback for research-direction tags.

The keyword tagger in build_data.py labels many jobs "General/Other" because
their titles carry no field keyword (e.g. "Faculty Position in Computer
Science"). This module asks an LLM to read those titles and assign a direction.

It is OFF unless an API key is present in the environment, so build_data.py
runs fine with pure code when no key is set.

Key: read from env var DEEPSEEK_API_KEY. NEVER hard-code a key here or anywhere
in the repo. In GitHub Actions, store it as a repository secret and pass it in
the workflow:  env: DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}

DeepSeek exposes an OpenAI-compatible endpoint, so this uses the plain REST API
with `requests` (no extra SDK needed).
"""
import os, json, time, re
import requests

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
VALID_TAGS = ["AI/ML", "Robotics", "Vision", "NLP", "Bio/Health", "Quantum",
              "Systems/Hardware", "Security/Cyber", "HCI", "Theory", "CS-Ed",
              "General/Other"]
BATCH = 20          # titles per request
MAX_JOBS = 1200     # safety cap so a run can't blow up cost

SYS = (
    "You label US computer-science faculty job postings by research direction. "
    "For each numbered title, reply with the single best direction from this exact list: "
    + ", ".join(VALID_TAGS) + ". "
    "Use 'General/Other' only when the title truly names no field. "
    "Many titles say only 'Computer Science' or 'Faculty Position' - those are General/Other. "
    "Reply as compact JSON: a list of objects {\"n\": <number>, \"tag\": \"<one tag>\"}. No prose."
)

def _call(titles, key):
    msg = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
    body = {
        "model": MODEL, "temperature": 0,
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": msg}],
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for attempt in range(3):
        try:
            r = requests.post(API_URL, headers=headers, json=body, timeout=60)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                # the model may wrap the list in a key; find the first JSON array/obj
                m = re.search(r"\[.*\]", content, re.S)
                data = json.loads(m.group(0)) if m else json.loads(content)
                if isinstance(data, dict):           # {"results":[...]} shape
                    for v in data.values():
                        if isinstance(v, list): data = v; break
                return data
            print(f"  [llm] HTTP {r.status_code}: {r.text[:120]}")
        except Exception as e:
            print(f"  [llm] {e}")
        time.sleep(2 * (attempt + 1))
    return None

def enrich(jobs):
    """Mutate jobs in place: replace ['General/Other'] tags using the LLM.
    Returns the number of jobs relabeled. No-op (returns 0) without a key."""
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        print("llm_tag: no DEEPSEEK_API_KEY set -> skipping LLM tagging (keyword tags kept).")
        return 0

    targets = [j for j in jobs if j.get("tg") == ["General/Other"]][:MAX_JOBS]
    print(f"llm_tag: asking DeepSeek to classify {len(targets)} untagged titles...")
    relabeled = 0
    for i in range(0, len(targets), BATCH):
        chunk = targets[i:i + BATCH]
        res = _call([j["t"] for j in chunk], key)
        if not res:
            continue
        by_n = {int(d["n"]): d.get("tag", "") for d in res if isinstance(d, dict) and "n" in d}
        for n, j in enumerate(chunk, start=1):
            tag = by_n.get(n, "")
            if tag in VALID_TAGS and tag != "General/Other":
                j["tg"] = [tag]
                relabeled += 1
        print(f"  llm batch {i//BATCH+1}: +{sum(1 for n,jj in enumerate(chunk,1) if by_n.get(n) in VALID_TAGS and by_n.get(n)!='General/Other')}")
        time.sleep(0.5)
    print(f"llm_tag: relabeled {relabeled} jobs.")
    return relabeled
