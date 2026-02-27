# Feature: Hotspot Detail View

## Goal

When the user clicks a hotspot in the recommendation results, open a detail panel
showing all species and checklists recently recorded at that specific location.

---

## User Stories

1. **Notable species** — As a birder, I want to see all eBird-notable species at a
   hotspot so I can judge whether a rare bird is worth the trip.

2. **Full species list** — As a birder, I want to see every species recently recorded
   there (not just the top recommendation), with lifer status marked, so I know what
   else I might tick off.

3. **Recent checklists** — As a birder, I want to see a list of recent checklists
   (date, observer count, species count, link to eBird) so I can gauge how actively
   birded the spot is.

---

## Scope

### In scope
- Detail panel (side sheet or modal) triggered by clicking a hotspot in ResultsTable
- Three tabs or sections: **Notable** / **All Species** / **Checklists**
- Lifer badges on species (cross-referenced against the user's life list in localStorage)
- Link to the hotspot's eBird page
- `days` parameter reused from the main search

### Out of scope (future)
- Map view
- Historical trends / charts
- Comparing two hotspots side-by-side

---

## eBird API Calls Needed

| Data | Endpoint | Already in client.py? |
|------|----------|-----------------------|
| All recent obs at hotspot | `GET /data/obs/{locId}/recent` | Yes (`recent_obs_at_location`) |
| Notable obs at hotspot | `GET /data/obs/{locId}/recent/notable` | No — needs adding |
| Recent checklists at hotspot | `GET /product/lists/{locId}` | No — needs adding |

---

## Backend Changes

### New client methods (core/client.py)
```python
def notable_obs_at_location(self, loc_id: str, back: int = 14) -> list[NotableObservation]
def checklists_at_location(self, loc_id: str, back: int = 14) -> list[Checklist]
```

### New Pydantic model (core/models.py)
```python
class Checklist(BaseModel):
    sub_id: str        # subId
    loc_id: str        # locId
    obs_dt: str        # obsDt
    num_species: int   # numSpecies
    # (obs_time, duration_hrs optional)
```

### New API endpoint (api/app.py)
```
GET /hotspot/{loc_id}?days=14
```
Returns:
```json
{
  "notable":    [ ...NotableObservation ],
  "recent":     [ ...Observation ],
  "checklists": [ ...Checklist ]
}
```
Accepts the same `X-EBird-Api-Token` header as `/recommend`.

---

## Frontend Changes

### New component: HotspotDetail.vue
- Receives `locId`, `locName`, `days`, `lifeList` as props
- Fetches `GET /hotspot/{loc_id}?days={days}` on mount
- Three sections: Notable / All Species / Checklists
- Species rows show Lifer badge if not in life list
- "View on eBird" link: `https://ebird.org/hotspot/{locId}`

### Trigger
- In ResultsTable.vue: make the location name a clickable button
- Opens HotspotDetail as a side panel (fixed right drawer, ~400px wide)
  - Simple v-if toggle, no router needed at this stage

### Extensibility note
The side panel (DetailPanel.vue) should be a generic shell that accepts a `component`
slot — so future detail views (e.g. species detail, checklist detail) can reuse the
same open/close/loading/error skeleton without duplicating code.

---

## Decisions

1. **Checklists** — Show 10 most recent by default. Backend accepts a `limit`
   query param (default 10) for future extensibility.

2. **Panel vs. page** — Independent page at `/hotspot/:locId`. Requires adding
   vue-router. Makes URLs shareable and browser back button works. The home page
   (`/`) keeps the existing recommend flow.

3. **Caching** — Reuse the existing 4-hour file cache (no change needed).

---

## Routing Plan (vue-router)

| Path | Component | Notes |
|------|-----------|-------|
| `/` | App.vue (existing) | Recommend form + results |
| `/hotspot/:locId` | HotspotDetail.vue | Hotspot detail page |

`locId` from eBird (e.g. `L232592`). Page fetches its own data on mount.
