# eBird Recommender

Recommends nearby birding hotspots and target species based on your eBird life list and recent local observations.

**Data provided by [eBird](https://ebird.org), Cornell Lab of Ornithology.**

---

## Features

- Ranks (species, location) pairs by recency, report frequency, and distance
- Marks lifers (species not yet on your life list) and eBird notable observations
- Filters: lifer status (all / lifers only / seen before), eBird notable (all / notable only / non-notable)
- 4-hour file-based cache to avoid repeated API calls
- CLI for local use; FastAPI backend + Vue 3 frontend for web use
- API key supplied per-request — no server-side key required for multi-user deployment

---

## Quickstart

### Prerequisites

- Python 3.11+
- Node 18+ (frontend only)
- An [eBird API key](https://ebird.org/api/keygen)

### Backend (CLI + API)

```bash
pip install -e .

# CLI usage
ebird-rec info --csv data/MyEBirdData.csv
ebird-rec rec --lat -33.8623 --lng 151.2077 --csv data/MyEBirdData.csv

# API dev server
python serve.py          # http://localhost:8000
                         # http://localhost:8000/docs  (Swagger UI)
```

Set your API key in `.env`:
```
EBIRD_API_KEY=your_key_here
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend

```bash
cd frontend
npm install
npm run dev              # http://localhost:5173
```

Open Settings (⚙️) → paste API key → upload `MyEBirdData.csv` from [ebird.org/downloadMyData](https://ebird.org/downloadMyData).
The CSV is parsed in the browser and stored in `localStorage` — it is never uploaded to the server.

### Docker (local)

```bash
docker compose up
```

Backend runs on `http://localhost:8000`. Frontend is served separately via `npm run dev`.

---

## Project Structure

```
ebird_recommend/
  core/
    client.py       eBird API wrapper (httpx, sync)
    models.py       Pydantic v2 models
    recommender.py  Scoring and deduplication engine
    user_data.py    CSV parser (file + string variants)
    cache.py        File-based JSON cache with TTL
  cli/
    app.py          Typer CLI (info, hotspots, notable, rec)
  api/
    app.py          FastAPI routes
    deps.py         API key dependency + client factory

frontend/
  src/
    api.ts          fetch wrapper for POST /recommend
    store.ts        localStorage helpers + CSV parser
    types.ts        TypeScript interfaces
    components/
      SettingsPanel.vue   API key input + CSV upload
      RecommendForm.vue   Search parameters form
      ResultsTable.vue    Results display

data/
  MyEBirdData.csv   (gitignored) your eBird export
  .cache/           (gitignored) API response cache

serve.py            uvicorn dev server entry point
Dockerfile          production backend image
docker-compose.yml  local dev stack
```

---

## API

### `POST /recommend`

**Header:** `X-EBird-Api-Token: <your_key>` (falls back to `EBIRD_API_KEY` env var)

**Body:**
```json
{
  "life_list": [{"scientific_name": "Cacatua galerita", "common_name": "Sulphur-crested Cockatoo"}],
  "lat": -33.8623,
  "lng": 151.2077,
  "radius": 50,
  "days": 14,
  "top": 20,
  "lifer": "all",
  "notable": "all"
}
```

`lifer` and `notable` each accept `"all"` / `"yes"` / `"no"`. Filtering is applied after scoring; `top` truncates the final filtered list.

### `GET /hotspots?lat&lng&radius`
### `GET /notable?lat&lng&radius&days`
### `GET /healthz`

---

## Scoring

Results are ranked by a score combining:

| Factor | Points |
|--------|--------|
| Seen today | +15 |
| Seen 2–3 days ago | +10 |
| Seen 4–7 days ago | +5 |
| Seen 8–14 days ago | +2 |
| Report frequency | +1.5 × min(count, 8) |
| Distance penalty | −(dist / max_dist) × 10 |

Lifer and notable status are **not** included in the score — use the filter parameters to focus on them instead.

---

## Deployment

### Backend → Railway

1. Push to GitHub (monorepo)
2. New project in Railway → connect repo → auto-detects `Dockerfile`
3. Set env vars: `EBIRD_API_KEY` (optional fallback), `ALLOWED_ORIGINS` (your GitHub Pages URL)

### Frontend → GitHub Pages

Handled automatically by `.github/workflows/deploy-frontend.yml` on every push to `main`/`master` that touches `frontend/`.

To set up manually:
1. Go to repo **Settings → Pages → Source → GitHub Actions**
2. Edit `frontend/.env.production` with your Railway URL
3. Push — the workflow builds and deploys `frontend/dist/` to GitHub Pages

### Live

- Frontend: https://seren-l.github.io/ebird-recommend
- Backend: https://ebird-recommend-production.up.railway.app
