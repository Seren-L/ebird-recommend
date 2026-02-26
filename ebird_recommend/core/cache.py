"""Simple file-based JSON cache for eBird API responses.

Cache files live in data/.cache/ and are invalidated after a configurable TTL.
Each entry is a JSON file keyed by an MD5 hash of the request parameters.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta


class Cache:
    def __init__(self, cache_dir: str | Path, ttl_hours: float = 4.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _path(self, key: str) -> Path:
        h = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{h}.json"

    def get(self, key: str) -> list | dict | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(data["cached_at"])
            if datetime.now() - cached_at > self.ttl:
                path.unlink(missing_ok=True)
                return None
            return data["payload"]
        except (json.JSONDecodeError, KeyError, ValueError):
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, payload: list | dict) -> None:
        path = self._path(key)
        path.write_text(
            json.dumps({"cached_at": datetime.now().isoformat(), "payload": payload}),
            encoding="utf-8",
        )

    def clear(self) -> int:
        """Delete all cache files. Returns the count of files removed."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            f.unlink(missing_ok=True)
            count += 1
        return count
