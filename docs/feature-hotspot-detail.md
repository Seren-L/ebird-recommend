# Feature: Hotspot Detail Page

## Goal

When the user clicks a location name in the recommendation results, navigate to a
dedicated page showing everything recently recorded at that specific hotspot.

**Status: Shipped** (`feat/hotspot-detail` → merged to master)

---

## User Stories

1. **Notable species** — See all eBird-notable species at a hotspot to judge whether
   a rarity is worth the trip.
2. **Full species list** — See every species recently recorded there, with Lifer badges
   cross-referenced against the life list stored in localStorage.
3. **Recent checklists** — See the 10 most recent trip reports (date, species count,
   link to eBird) to gauge how actively birded the location is.

---

## Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Side panel vs. page | Independent page at `/#/hotspot/:locId` | URL shareable, back button works |
| Checklist count | Default 10, `limit` param for future extensibility | Avoids overwhelming the UI |
| Caching | Reuse existing 4-hour file cache | No extra complexity needed |
| Router history | `createWebHashHistory()` | Works with GitHub Pages static hosting |

---

## API

### `GET /hotspot/{loc_id}?days=14&limit=10`

Header: `X-EBird-Api-Token: <key>`

Response:
```json
{
  "notable":    [ ...Observation (camelCase, eBird aliases) ],
  "recent":     [ ...Observation (camelCase, eBird aliases) ],
  "checklists": [ ...Checklist (snake_case, constructed manually) ]
}
```

#### eBird endpoints used

| Data | eBird endpoint |
|------|----------------|
| Notable obs at hotspot | `GET /data/obs/{locId}/recent/notable` |
| All recent obs at hotspot | `GET /data/obs/{locId}/recent` |
| Recent checklists | `GET /product/lists/{locId}?maxResults=limit` |

#### Serialisation note

`Observation` / `NotableObservation` use `alias_generator=to_camel` and serialize
with camelCase keys (`comName`, `sciName`, `speciesCode` …). `Checklist` is
constructed manually in `client.py` (not from raw JSON) because the eBird response
has an inconsistent shape: `locName` is nested inside a `loc` sub-object and the
usable date is in `isoObsDate`, not `obsDt`. TypeScript types reflect this split.

---

## File Map

| File | Change |
|------|--------|
| `ebird_recommend/core/models.py` | Added `Checklist`, `HotspotDetailResponse` |
| `ebird_recommend/core/client.py` | Added `notable_obs_at_location()`, `checklists_at_location()` |
| `ebird_recommend/api/app.py` | Added `GET /hotspot/{loc_id}` route |
| `frontend/package.json` | Added `vue-router@4` |
| `frontend/src/main.ts` | Router setup with hash history, two routes |
| `frontend/src/App.vue` | Refactored to shell: header + `<RouterView>` + SettingsPanel |
| `frontend/src/views/HomeView.vue` | New — original App.vue main content |
| `frontend/src/views/HotspotDetailView.vue` | New — hotspot detail page |
| `frontend/src/components/ResultsTable.vue` | Location name → `<RouterLink>` |
| `frontend/src/api.ts` | Added `fetchHotspotDetail()` |
| `frontend/src/types.ts` | Added `Observation` (camelCase), `Checklist`, `HotspotDetail` |

---

## Routes

| Path | Component | Notes |
|------|-----------|-------|
| `/#/` | `HomeView.vue` | Recommend form + results (unchanged UX) |
| `/#/hotspot/:locId` | `HotspotDetailView.vue` | Fetches on mount, shows 3 sections |

---

## Out of Scope (Future)

- Map view of the hotspot
- Historical species trends / charts
- Side-by-side hotspot comparison
- Pagination for checklists beyond 10
