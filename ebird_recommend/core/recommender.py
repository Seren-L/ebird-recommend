"""Core recommendation engine.

Given the user's life list and nearby eBird observations, produce a ranked
list of (species, location) pairs worth chasing.
"""

import math
from datetime import date, datetime
from collections import defaultdict

from .models import Observation, NotableObservation, SeenSpecies, Recommendation, EBIRD_WEB


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return great-circle distance in kilometres."""
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dφ = math.radians(lat2 - lat1)
    dλ = math.radians(lng2 - lng1)
    a = math.sin(dφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(dλ / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _parse_obs_date(obs_dt: str) -> date | None:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(obs_dt[:16], fmt).date()
        except ValueError:
            continue
    return None


def score(
    days_ago: int,
    report_count: int,
    distance_km: float,
    max_dist_km: float,
) -> float:
    s = 0.0

    # Recency
    if days_ago <= 1:
        s += 15
    elif days_ago <= 3:
        s += 10
    elif days_ago <= 7:
        s += 5
    elif days_ago <= 14:
        s += 2

    # Frequency (capped — many reports = reliable)
    s += min(report_count, 8) * 1.5

    # Distance penalty (−10 at max_dist, 0 at origin)
    s -= (distance_km / max_dist_km) * 10

    return round(s, 2)


def _reason(is_lifer: bool, is_notable: bool, days_ago: int, report_count: int) -> str:
    parts = []
    if is_lifer:
        parts.append("lifer")
    if is_notable:
        parts.append("notable")
    if days_ago <= 1:
        parts.append("seen today")
    elif days_ago <= 3:
        parts.append(f"seen {days_ago}d ago")
    else:
        parts.append(f"seen {days_ago}d ago")
    if report_count > 1:
        parts.append(f"{report_count} reports")
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Main recommendation function
# ---------------------------------------------------------------------------

def recommend(
    user_lat: float,
    user_lng: float,
    seen: dict[str, SeenSpecies],          # scientific_name → SeenSpecies
    all_obs: list[Observation],
    notable_obs: list[NotableObservation],
    max_dist_km: float,
) -> list[Recommendation]:
    """Return all recommended (species, location) pairs, ranked by score.

    Filtering and top-N truncation are the caller's responsibility,
    so they happen after any post-processing filters.
    """

    today = date.today()

    # Build a set of notable (speciesCode, locId) for O(1) lookup
    notable_keys: set[tuple[str, str]] = {
        (o.species_code, o.loc_id) for o in notable_obs
    }

    # Aggregate observations by (speciesCode, locId)
    # value: { lat, lng, loc_name, common_name, sci_name, dates: list[date], count }
    Key = tuple[str, str]
    agg: dict[Key, dict] = defaultdict(lambda: {
        "dates": [],
        "common_name": "",
        "scientific_name": "",
        "loc_name": "",
        "lat": 0.0,
        "lng": 0.0,
    })

    for obs in all_obs + list(notable_obs):  # type: ignore[operator]
        key: Key = (obs.species_code, obs.loc_id)
        bucket = agg[key]
        bucket["common_name"] = obs.common_name
        bucket["scientific_name"] = obs.scientific_name
        bucket["loc_name"] = obs.loc_name
        bucket["lat"] = obs.lat
        bucket["lng"] = obs.lng
        d = _parse_obs_date(obs.obs_dt)
        if d:
            bucket["dates"].append(d)

    # Build recommendations
    recs: list[Recommendation] = []

    for (species_code, loc_id), bucket in agg.items():
        sci = bucket["scientific_name"]
        is_lifer = sci not in seen
        is_notable = (species_code, loc_id) in notable_keys

        dates = bucket["dates"]
        if not dates:
            continue
        last_date = max(dates)
        days_ago = (today - last_date).days
        report_count = len(dates)

        dist = haversine(user_lat, user_lng, bucket["lat"], bucket["lng"])

        s = score(days_ago, report_count, dist, max_dist_km)

        recs.append(Recommendation(
            species_code=species_code,
            common_name=bucket["common_name"],
            scientific_name=sci,
            loc_id=loc_id,
            loc_name=bucket["loc_name"],
            lat=bucket["lat"],
            lng=bucket["lng"],
            distance_km=round(dist, 1),
            last_reported=str(last_date),
            report_count=report_count,
            is_notable=is_notable,
            is_lifer=is_lifer,
            score=s,
            reason=_reason(is_lifer, is_notable, days_ago, report_count),
            species_url=f"{EBIRD_WEB}/species/{species_code}",
            hotspot_url=f"{EBIRD_WEB}/hotspot/{loc_id}",
        ))

    recs.sort(key=lambda r: r.score, reverse=True)

    # Deduplicate by species: keep the best-scored location per species.
    # Score already encodes both distance penalty and frequency bonus,
    # so the top entry naturally reflects the optimal distance/reliability balance.
    seen_codes: dict[str, int] = {}   # species_code → count of other locations
    deduped: list[Recommendation] = []
    for r in recs:
        if r.species_code not in seen_codes:
            seen_codes[r.species_code] = 0
            deduped.append(r)
        else:
            seen_codes[r.species_code] += 1

    # Append "also at N other spots" to the reason of deduplicated entries
    for r in deduped:
        n = seen_codes.get(r.species_code, 0)
        if n > 0:
            r.reason += f" | +{n} spot{'s' if n > 1 else ''}"

    return deduped
