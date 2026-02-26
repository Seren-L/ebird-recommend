"""eBird API 2.0 client.

Docs: https://documenter.getpostman.com/view/664302/S1ENwy59
Attribution: Data provided by eBird (https://ebird.org), Cornell Lab of Ornithology.
"""

import json
import httpx
from typing import Optional
from .models import Hotspot, Observation, NotableObservation
from .cache import Cache

BASE_URL = "https://api.ebird.org/v2"


class EBirdClient:
    def __init__(self, api_key: str, cache: Cache | None = None):
        self._headers = {"X-eBirdApiToken": api_key}
        self._cache = cache

    def _get(self, path: str, params: dict) -> list | dict:
        cache_key = path + json.dumps(params, sort_keys=True)

        if self._cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        url = f"{BASE_URL}{path}"
        response = httpx.get(url, headers=self._headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if self._cache:
            self._cache.set(cache_key, data)

        return data

    # ------------------------------------------------------------------
    # Hotspots
    # ------------------------------------------------------------------

    def nearby_hotspots(
        self,
        lat: float,
        lng: float,
        dist_km: int = 50,
    ) -> list[Hotspot]:
        """Return hotspots within dist_km kilometres of the given coordinates."""
        data = self._get(
            "/ref/hotspot/geo",
            {"lat": lat, "lng": lng, "dist": dist_km, "fmt": "json"},
        )
        return [Hotspot(**h) for h in data]

    # ------------------------------------------------------------------
    # Recent observations
    # ------------------------------------------------------------------

    def recent_obs_at_location(
        self,
        loc_id: str,
        back: int = 14,
    ) -> list[Observation]:
        """Recent observations at a specific hotspot."""
        data = self._get(
            f"/data/obs/{loc_id}/recent",
            {"back": back, "detail": "simple"},
        )
        return [Observation(**o) for o in data]

    def nearby_notable_obs(
        self,
        lat: float,
        lng: float,
        dist_km: int = 50,
        back: int = 14,
    ) -> list[NotableObservation]:
        """Recent notable (rare/flagged) observations near a location."""
        data = self._get(
            "/data/obs/geo/recent/notable",
            {"lat": lat, "lng": lng, "dist": dist_km, "back": back, "detail": "simple"},
        )
        return [NotableObservation(**o) for o in data]

    def nearby_recent_obs(
        self,
        lat: float,
        lng: float,
        dist_km: int = 50,
        back: int = 14,
    ) -> list[Observation]:
        """All recent observations near a location (not just notable)."""
        data = self._get(
            "/data/obs/geo/recent",
            {"lat": lat, "lng": lng, "dist": dist_km, "back": back, "detail": "simple"},
        )
        return [Observation(**o) for o in data]
