"""Shared FastAPI dependencies."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Header, HTTPException

from ebird_recommend.core.cache import Cache
from ebird_recommend.core.client import EBirdClient

load_dotenv()

_CACHE_DIR = Path("data/.cache")
_CACHE_TTL = 4.0


@lru_cache(maxsize=32)
def get_client(api_key: str) -> EBirdClient:
    """Return a cached EBirdClient for the given API key."""
    cache = Cache(_CACHE_DIR, ttl_hours=_CACHE_TTL)
    return EBirdClient(api_key, cache=cache)


def api_key_dep(
    x_ebird_api_token: Annotated[str | None, Header()] = None,
) -> str:
    """Resolve the eBird API key from the request header or env var.

    Priority: X-EBird-Api-Token header > EBIRD_API_KEY env var.
    """
    key = x_ebird_api_token or os.getenv("EBIRD_API_KEY")
    if not key:
        raise HTTPException(
            status_code=401,
            detail="eBird API key required. Pass the X-EBird-Api-Token header.",
        )
    return key
