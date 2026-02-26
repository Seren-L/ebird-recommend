"""Parse the user's personal eBird data export (CSV).

Download from: My eBird → https://ebird.org/downloadMyData
The file is named MyEBirdData.csv
"""

import csv
import io
from datetime import date, datetime
from pathlib import Path
from .models import SeenSpecies

_COL_COMMON     = "Common Name"
_COL_SCIENTIFIC = "Scientific Name"
_COL_DATE       = "Date"


def _parse_rows(reader: csv.DictReader) -> dict[str, SeenSpecies]:
    seen: dict[str, SeenSpecies] = {}
    for row in reader:
        sci = row.get(_COL_SCIENTIFIC, "").strip()
        if not sci:
            continue

        raw_date = row.get(_COL_DATE, "").strip()
        obs_date: date | None = None
        if raw_date:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    obs_date = datetime.strptime(raw_date, fmt).date()
                    break
                except ValueError:
                    continue

        existing = seen.get(sci)
        if existing is None:
            seen[sci] = SeenSpecies(
                scientific_name=sci,
                common_name=row.get(_COL_COMMON, "").strip(),
                last_seen=obs_date,
            )
        elif obs_date and (existing.last_seen is None or obs_date > existing.last_seen):
            existing.last_seen = obs_date

    return seen


def load_life_list(csv_path: str | Path) -> dict[str, SeenSpecies]:
    """Return a dict of scientific_name → SeenSpecies from the user's eBird CSV.

    Keeps only the most recent observation date per species.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"eBird data file not found: {path}")

    with path.open(newline="", encoding="utf-8") as f:
        return _parse_rows(csv.DictReader(f))


def load_life_list_from_string(csv_text: str) -> dict[str, SeenSpecies]:
    """Parse a life list from CSV text (e.g. uploaded by the frontend).

    Keeps only the most recent observation date per species.
    """
    return _parse_rows(csv.DictReader(io.StringIO(csv_text)))
