# Cantus — Sheet Music Library

A progressive web app (PWA) for managing a choral sheet music collection. Built with plain HTML, CSS, and JavaScript. Core library features run fully client-side; Claude image scanning uses a lightweight proxy endpoint.

---

## Project Summary (for AI assistant context)

This is a single-file PWA (`index.html` + `manifest.json` + `sw.js`) deployed on GitHub Pages. It manages a choral sheet music library with a warm dark gold aesthetic using Playfair Display and Crimson Pro fonts. For Claude Vision scanning in local dev, it uses `proxy_server.py` as a same-origin API relay.

---

## Fields

Each piece in the library stores:

| Field | Type | Notes |
|---|---|---|
| Title | Text | Required |
| Composer | Text | |
| Arranger | Text | |
| Publisher | Text | |
| Year Published | Number | |
| Voicing | Select | SATB, SAB, SSA, SSAA, TTBB, TB, Unison, 2-Part, 3-Part Mixed, SATB + Soloists, Other |
| Last Performed Date | Date | |
| Number of Copies Owned | Number | |
| Liturgical Season | Select | Advent, Christmas, Lent, Palm Sunday, Maundy Thursday/Good Friday, Easter, Pentecost |
| Notes | Textarea | Free text |

Each record also has an auto-generated `id` (used for deduplication) and a `lastModified` ISO timestamp (used for merge logic).

---

## Storage Architecture

- **Working cache:** Browser `localStorage` — all edits write here instantly
- **Persistent file:** Manual JSON export to the user's machine via the **Export** button
- **No server, no cloud, no account required**
- Data survives browser restarts via localStorage
- JSON file is the source of truth for multi-device use

### Multi-Machine Sync Workflow
1. Edit on Machine A → click **Export** → downloads `cantus-library-YYYY-MM-DD.json`
2. Copy JSON file to Machine B (USB, email, cloud drive, etc.)
3. On Machine B → **Import** → choose JSON tab → select merge strategy → import
4. Summary shows: X added · Y updated · Z skipped

---

## Import System

### JSON Import (Full Sync)
Four merge strategies:
- **Skip duplicates** — keep existing record if ID already exists
- **Update if newer** — replace only if `lastModified` timestamp is more recent
- **Always overwrite** — imported data replaces any matching record
- **Replace entire library** — discard current library and load fresh

### CSV Import (Spreadsheet)
- Always **additive only** — never overwrites existing records
- If CSV has an `id` column, deduplication applies; otherwise new IDs are generated
- Required column headers (row 1, case-insensitive):
  ```
  title, composer, arranger, publisher, year, voicing, season, lastPerformed, copies, notes
  ```
- Supports drag-and-drop on both import types

---

## Responsive Layout

| Device | Breakpoint | Layout |
|---|---|---|
| Phone | < 600px | Vertical card list + floating + button + bottom nav bar |
| Tablet | 600–1023px | Card grid (auto-fill, min 290px) + floating + button + side detail panel |
| Desktop | 1024px+ | Full table view with sortable columns + optional grid toggle |

### Detail Panel
- **Phone:** Slides up from bottom as a sheet
- **Tablet/Desktop:** Slides in from the right side

### Modals (Add/Edit/Import)
- **Phone:** Bottom sheet style
- **Tablet/Desktop:** Centered modal

### iOS / Android PWA Support
- `viewport-fit=cover` for notched iPhones
- `env(safe-area-inset-*)` CSS variables used throughout
- `apple-mobile-web-app-capable` and status bar meta tags set
- **Android Chrome:** Menu → "Add to Home Screen"
- **iOS Safari:** Share → "Add to Home Screen"

---

## Sorting & Filtering

**Sortable by:**
- Title (A–Z / Z–A)
- Composer (A–Z / Z–A)
- Voicing (A–Z)
- Last Performed (most/least recent)
- Liturgical Season (canonical order)

**Filterable by:**
- Text search (title, composer, arranger, publisher, notes)
- Voicing dropdown
- Liturgical Season chips (multi-select)

---

## Export / Unsaved State

- **Unsaved indicator** pulses gold in the header when changes haven't been exported
- **5-minute reminder toast** if unsaved changes exist
- **`beforeunload` warning** if you try to close the tab with unsaved changes
- **Ctrl+S** (or Cmd+S) triggers Export from anywhere
- **Ctrl+K** focuses the search box

---

## AI Scan (Claude Vision)

### What It Does
- Add/Edit modal includes **Scan Sheet Music** to process a photo and prefill metadata.
- Uses Claude Vision with multi-pass image strategy: top 50%, top 75%, then full page.
- Automatically pre-processes images (resized/compressed) for better speed and request size safety.

### Fields Prefilled
- Title
- Composer
- Arranger
- Publisher
- Year
- Notes
- Voicing (when explicit label is detected or high-confidence inference is available)

### Voicing Behavior
- Voicing values map to app options: `SATB`, `SAB`, `SSA`, `SSAA`, `TTBB`, `TB`, `Unison`, `2-Part`, `3-Part Mixed`, `SATB + Soloists`, `Other`.
- App is intentionally conservative to avoid wrong auto-selection.
- If source image does not clearly show voicing labels, voicing may remain blank and should be set manually.

### API Key Handling (Current)
- Key is entered via **Settings** and stored locally with 8-hour TTL.
- Key can be deleted immediately using **Delete Key Now**.
- For production security, server-side key storage is still recommended.

---

## File Structure

```
/
├── index.html       ← Entire app (HTML + CSS + JS in one file)
├── manifest.json    ← PWA manifest (name, theme, icons, orientation)
├── sw.js            ← Service worker (offline caching, cache-first strategy)
├── proxy_server.py  ← Local dev server + Claude proxy endpoint
├── cloudflare-worker/
│   ├── worker.js                ← Cloudflare Worker proxy template (safe to publish)
│   ├── wrangler.toml.example    ← Wrangler config template
│   └── README.md                ← Worker setup guide
└── README.md        ← This file
```

## Local Development (Claude Scan)

For local testing of Claude image scan, run the proxy server instead of the plain static server:

```bash
cd /home/keng/Programming/sheet-music-library
python3 proxy_server.py 8080 --bind 0.0.0.0
```

Then open `http://localhost:8080/` (or LAN URL on phone). The app posts scans to
`/api/claude/messages`, which forwards to Anthropic.

### Local Scan Checklist
1. Start `proxy_server.py` and keep the terminal running.
2. Open `http://localhost:8080/`.
3. In app Settings, paste Claude API key.
4. Use **Add Piece -> Scan Sheet Music**.

### If Scan Fails
- `Could not reach Claude scan endpoint`: proxy is not running or wrong URL.
- `Invalid API key`: check key in Settings.
- `Image payload is too large`: retake/tighten image or reduce source resolution.
- Blank/missing voicing: retake image with visible voicing labels or set voicing manually.

---

## GitHub Pages Note

- Static GitHub Pages cannot reliably call Claude API directly from browser due to CORS and key exposure concerns.
- For scanning on deployed site, use a hosted same-origin proxy (Cloudflare Worker, serverless function, or small backend) and route `/api/claude/messages` through it.

## Cloudflare Worker Deployment (Recommended)

Use this for production-style scan support without running Python on user machines.

### Is it safe to upload Worker code to GitHub?

Yes. You should publish the Worker template files.

- Safe to publish: `cloudflare-worker/worker.js`, `wrangler.toml.example`
- Never publish: real API keys, `.env` with secrets, `wrangler.toml` containing secrets
- Store real key only with `wrangler secret put ANTHROPIC_API_KEY`

### Setup Steps

1. Create a Cloudflare account and a Worker project.
2. In `cloudflare-worker/`, copy `wrangler.toml.example` to `wrangler.toml`.
3. Set secret:
  ```bash
  wrangler secret put ANTHROPIC_API_KEY
  ```
4. Deploy Worker:
  ```bash
  wrangler deploy
  ```
5. Copy Worker URL.
6. Point Cantus frontend to that URL by setting a global override before app script:
  ```html
  <script>
    window.CANTUS_CLAUDE_ENDPOINT = "https://YOUR-WORKER.workers.dev/api/claude/messages";
  </script>
  ```

### CORS and Origin Security

- Set `CORS_ALLOW_ORIGIN` in Worker config to your real app origin (for example your GitHub Pages URL).
- Worker template now hard-blocks requests if `CORS_ALLOW_ORIGIN` is blank or `*`.
- Browser requests from unlisted origins return `403 Forbidden`.

### Cost Overview

- GitHub Pages: free (public repo)
- Cloudflare Worker: typically free at small volume (check current Cloudflare pricing)
- Claude API: main variable cost, based on image tokens and request volume

---

## Deploying to GitHub Pages

1. Create a new GitHub repository (e.g. `cantus-library`)
2. Push all files to the `main` branch root
3. Go to **Settings → Pages → Deploy from branch → main → / (root)**
4. App will be live at `https://yourusername.github.io/cantus-library`

---

## Known Issues & Notes

- `localStorage` is browser and device specific — clearing browser data wipes the working cache (the exported JSON file is unaffected)
- The `-webkit-line-clamp` CSS hack was replaced with `max-height` clamp to avoid linter errors
- Service worker caches `index.html`, `manifest.json`, and `sw.js` for offline use
- Voicing extraction is most reliable when the page clearly shows voice labels (e.g., SATB/SAB)
- Online/cropped sample images can underperform vs. straight-on full-page phone photos

---

## Design

- **Color palette:** Dark warm brown/black background (`#12100e`) with gold accent (`#c9a84c`)
- **Fonts:** Playfair Display (headings/titles) + Crimson Pro (body) via Google Fonts
- **Theme:** Refined liturgical — feels like a proper music library catalog

---

## Resuming Development with an AI Assistant

Paste this README and your current `index.html` into a new chat. The assistant will have full context to continue work. Key things to mention if making changes:

- All styles are in a single `<style>` block in `index.html`
- All JavaScript is in a single `<script>` block at the bottom of `index.html`
- Responsive breakpoints: phone `<600px`, tablet `600–1023px`, desktop `1024px+`
- The three render functions are `rPhone()`, `rGrid()`, and `rTable()`
- `renderAll()` is the main orchestrator — call it after any data or filter change
