# CS Faculty Job Atlas

An interactive US map of computer-science, data-science, and computer/electrical
engineering **faculty** openings, pulled from HigherEdJobs and the CRA Job Board.
Each job is tagged with its official **2025 Carnegie** tier (R1/R2/…), an
**HBCU** flag, a position type, and a research direction. You can **star** jobs,
set a **status** (interested / applied / interview / offer), and record
**applied** and **deadline** dates — all saved in your browser and exportable to
this repo.

A GitHub Action refreshes the data every week and redeploys the site, so it
stays current with zero manual work.

**Live site:** `https://<your-username>.github.io/<repo-name>/`

---

## Files

| File | What it is |
|------|------------|
| `index.html` | The whole web app (no build step, no framework). |
| `data.json` | The job data the page loads. Rebuilt by the Action. |
| `build_data.py` | Scrapes the sources, classifies, dedupes, geocodes, writes `data.json`. |
| `carnegie2025.py` | Official 2025 Carnegie R1/R2 classifier. |
| `hbcu.py` | Official U.S. Dept. of Education HBCU flag. |
| `llm_tag.py` | Optional: uses DeepSeek to tag jobs whose titles have no field keyword. |
| `states_path.txt` | Pre-computed US state borders for the map (fixed, don't edit). |
| `requirements.txt` | Python dependencies. |
| `.github/workflows/update.yml` | The weekly auto-update + deploy workflow. |

---

## One-time setup (about 10 minutes)

### 1. Create the repository
1. Go to <https://github.com/new>.
2. Name it (e.g. `cs-faculty-atlas`), set it **Public**, click **Create repository**.
3. Upload all the files in this folder: on the new repo page click
   **uploading an existing file**, drag everything in (keep the
   `.github/workflows/` folder structure), and **Commit**.
   - If the drag-and-drop loses the `.github` folder, use the web editor:
     **Add file → Create new file**, type `.github/workflows/update.yml` as the
     name, paste the file's contents, commit.

### 2. Turn on GitHub Pages
1. Repo **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
   (Not "Deploy from a branch" — this project deploys via the workflow.)

### 3. Run the workflow once
1. Repo **Actions** tab. If it asks you to enable workflows, click **I understand… enable**.
2. Pick **Update job data and deploy** on the left → **Run workflow** → **Run workflow**.
3. Wait ~2–4 min. When it's green, your site is live at the URL above.
   (It also runs automatically every Monday and on every push.)

### 4. (Optional) Turn on smarter tagging with DeepSeek
Without this, jobs whose titles don't name a field show as "General/Other".
Turn it on to have the AI read those titles and classify them:
1. **Get a fresh DeepSeek API key** at <https://platform.deepseek.com>.
   **Do not paste a key into any file** — only into the secret below.
2. Repo **Settings → Secrets and variables → Actions → New repository secret**.
3. Name: `DEEPSEEK_API_KEY`  Value: your key. Save.
4. Re-run the workflow (step 3). It now classifies the untitled jobs too.

> ⚠️ **Never commit an API key.** Keys live only in the repo secret. Anyone can
> read a public repo's files, so a key in a file would be stolen within minutes.
> If a key is ever exposed, revoke it in the DeepSeek dashboard and make a new one.

---

## Your personal tracking data

Starring, statuses, and dates are stored in **your browser** (localStorage), so
they stay on your device and aren't shared. To keep a durable copy or move
between devices:

- **Export my data** → downloads (or copies) `my_applications.json`.
  Commit that file into this repo to keep a versioned backup of your pipeline.
- **Import** → load a `my_applications.json` back in on another device.

(The job data itself is public; your application notes are only yours unless you
choose to commit them.)

---

## Updating the data

- **Automatic:** every Monday, and on every push. Nothing to do.
- **On demand:** Actions tab → Run workflow.
- **Locally** (optional): `pip install -r requirements.txt && python build_data.py`,
  then commit the new `data.json`.

## How classification works

- **Carnegie R1/R2 and HBCU:** matched against official 2025 name lists (code,
  deterministic — these are facts, not guesses).
- **Position type:** keyword rules on the title (tenure-track, lecturer, postdoc…).
- **Research direction:** keyword rules first; if `DEEPSEEK_API_KEY` is set, the
  LLM re-reads whatever the rules left as "General/Other".

## Notes & limits

This covers two aggregators (HigherEdJobs + CRA). AcademicJobsOnline and schools'
own HR portals are **not** included, so some R1 and SciML-targeted positions
won't appear. Research-direction tags are inferred from titles and can be wrong.
Treat it as a fast way to scan the market, not a complete registry.
