"""FastAPI backend for eBird lifer recommender.

All routes call the same core/ functions used by the CLI.
Attribution: Data provided by eBird (https://ebird.org), Cornell Lab of Ornithology.
"""

import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from ebird_recommend.core.models import Hotspot, HotspotDetailResponse, NotableObservation, RecommendRequest, Recommendation
from ebird_recommend.core.recommender import recommend
from .deps import api_key_dep, get_client

app = FastAPI(
    title="eBird Recommender API",
    description="Recommends birding hotspots and target species based on your eBird life list.",
    version="0.1.0",
)

_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
_origins = [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/hotspots", response_model=list[Hotspot])
def hotspots(
    lat: Annotated[float, Query(description="Latitude")],
    lng: Annotated[float, Query(description="Longitude")],
    radius: Annotated[int, Query(ge=1, le=500, description="Search radius in km")] = 50,
    api_key: Annotated[str, Depends(api_key_dep)] = ...,
):
    """Return eBird hotspots within radius km of the given coordinates."""
    try:
        return get_client(api_key).nearby_hotspots(lat, lng, radius)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/notable", response_model=list[NotableObservation])
def notable(
    lat: Annotated[float, Query(description="Latitude")],
    lng: Annotated[float, Query(description="Longitude")],
    radius: Annotated[int, Query(ge=1, le=500, description="Search radius in km")] = 50,
    days: Annotated[int, Query(ge=1, le=30, description="Days back to search")] = 14,
    api_key: Annotated[str, Depends(api_key_dep)] = ...,
):
    """Return recent notable (rare/flagged) observations near the given coordinates."""
    try:
        return get_client(api_key).nearby_notable_obs(lat, lng, radius, days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/recommend", response_model=list[Recommendation])
def recommend_route(
    body: RecommendRequest,
    api_key: Annotated[str, Depends(api_key_dep)] = ...,
):
    """Return ranked bird/hotspot recommendations based on the submitted life list."""
    seen = {s.scientific_name: s for s in body.life_list}

    try:
        client = get_client(api_key)
        all_obs     = client.nearby_recent_obs(body.lat, body.lng, body.radius, body.days)
        notable_obs = client.nearby_notable_obs(body.lat, body.lng, body.radius, body.days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    recs = recommend(body.lat, body.lng, seen, all_obs, notable_obs, max_dist_km=body.radius)

    if body.lifer == "yes":
        recs = [r for r in recs if r.is_lifer]
    elif body.lifer == "no":
        recs = [r for r in recs if not r.is_lifer]

    if body.notable == "yes":
        recs = [r for r in recs if r.is_notable]
    elif body.notable == "no":
        recs = [r for r in recs if not r.is_notable]

    return recs[:body.top]


@app.get("/hotspot/{loc_id}", response_model=HotspotDetailResponse)
def hotspot_detail(
    loc_id: str,
    days: Annotated[int, Query(ge=1, le=30, description="Days back to search")] = 14,
    limit: Annotated[int, Query(ge=1, le=200, description="Max checklists to return")] = 10,
    api_key: Annotated[str, Depends(api_key_dep)] = ...,
):
    """Return notable obs, all recent obs, and recent checklists for a specific hotspot."""
    try:
        client = get_client(api_key)
        notable  = client.notable_obs_at_location(loc_id, days)
        recent   = client.recent_obs_at_location(loc_id, days)
        checklists = client.checklists_at_location(loc_id, limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return HotspotDetailResponse(notable=notable, recent=recent, checklists=checklists)
