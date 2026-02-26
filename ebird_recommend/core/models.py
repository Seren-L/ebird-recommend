from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import date
from typing import Literal, Optional


class Hotspot(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    loc_id: str
    name: str = Field(alias="locName")
    lat: float
    lng: float
    country_code: str
    subnational1_code: str
    latest_obs_dt: Optional[str] = None
    num_species_all_time: Optional[int] = None


class Observation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    species_code: str
    common_name: str = Field(alias="comName")
    scientific_name: str = Field(alias="sciName")
    loc_id: str
    loc_name: str
    obs_dt: str
    how_many: Optional[int] = None
    lat: float
    lng: float
    obs_valid: bool = True
    obs_reviewed: bool = False
    location_private: bool = False
    sub_id: str = ""


class NotableObservation(Observation):
    """Notable (rare/unusual) observation flagged by eBird."""
    pass


class SeenSpecies(BaseModel):
    """A species the user has previously observed."""
    scientific_name: str
    common_name: str
    species_code: Optional[str] = None  # not in CSV export
    last_seen: Optional[date] = None


EBIRD_WEB = "https://ebird.org"


FilterMode = Literal["all", "yes", "no"]


class RecommendRequest(BaseModel):
    """Request body for POST /recommend — life list parsed and stored by the frontend."""
    life_list: list[SeenSpecies]
    lat: float
    lng: float
    radius: int = 50
    days: int = 14
    top: int = 20
    lifer: FilterMode = "all"    # "all" | "yes" = lifers only | "no" = seen only
    notable: FilterMode = "all"  # "all" | "yes" = rare only   | "no" = non-rare only


class Recommendation(BaseModel):
    """A recommended (species, location) pair with a score."""
    species_code: str
    common_name: str
    scientific_name: str
    loc_id: str
    loc_name: str
    lat: float
    lng: float
    distance_km: float
    last_reported: str
    report_count: int
    is_notable: bool
    is_lifer: bool
    score: float = 0.0
    reason: str = ""
    # Links
    species_url: str = ""
    hotspot_url: str = ""
