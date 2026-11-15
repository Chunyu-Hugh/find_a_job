#!/usr/bin/env bash
#
# refresh.sh — pull the latest jobs FROM YOUR OWN COMPUTER and push them up.
#
# Why run it here instead of GitHub Actions: HigherEdJobs throttles requests
# coming from datacenter IPs (like GitHub's servers) down to ~90 rows. From a
# normal home/office connection it does not, so running this locally captures
# the full ~1,700-row dataset.
#
# Usage:
#   1. Open a terminal in this folder (the repo you cloned).
#   2. Run:   bash refresh.sh
#   3. When it finishes, your site updates automatically in a minute or two.
#
# First time only: it installs the three Python packages it needs.

set -e  # stop on first error

echo "==> CS Faculty Job Atlas — local refresh"
echo

# --- 0. sanity: are we in the repo? ---
if [ ! -f build_data.py ]; then
  echo "ERROR: run this from inside the find_a_job folder (where build_data.py is)."
  exit 1
fi

# --- 1. make sure we have the latest code/data before rebuilding ---
echo "==> Pulling latest from GitHub..."
git pull --no-rebase origin main || {
  echo "WARNING: git pull failed (maybe you have local changes). Continuing anyway."
}

# --- 2. install Python deps (quietly; harmless if already installed) ---
echo "==> Checking Python packages..."
python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt || {
  echo "Trying pip install with --break-system-packages (newer Python)..."
  python3 -m pip install --quiet --break-system-packages -r requirements.txt
}

# --- 3. scrape the FULL dataset (LOCAL_FULL lifts the server-side page caps) ---
echo "==> Scraping full dataset (this takes a few minutes)..."
# To also let DeepSeek label untitled jobs, export your key first:
#   export DEEPSEEK_API_KEY=sk-....
LOCAL_FULL=1 python3 build_data.py

# --- 4. did the data actually change? ---
if git diff --quiet -- data.json; then
  echo
  echo "==> No change in data.json — nothing to push. Done."
  exit 0
fi

# --- 5. commit + push; the site redeploys automatically ---
COUNT=$(python3 -c "import json;print(len(json.load(open('data.json'))['jobs']))")
echo
echo "==> data.json now has $COUNT US jobs. Committing and pushing..."
git add data.json
git commit -m "Refresh job data ($(date +%Y-%m-%d)) — $COUNT US openings"
git push origin main

echo
echo "==> Done. Your site will update at:"
echo "    https://chunyu-hugh.github.io/find_a_job/"
echo "    (give GitHub Pages a minute or two, then hard-refresh)"
