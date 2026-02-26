import os
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ebird_recommend.core.client import EBirdClient
from ebird_recommend.core.user_data import load_life_list
from ebird_recommend.core.recommender import recommend
from ebird_recommend.core.cache import Cache

load_dotenv()
app = typer.Typer(help="eBird lifer recommender — find birds worth chasing nearby.")
console = Console()

_DEFAULT_CACHE_DIR = Path("data/.cache")
_DEFAULT_CACHE_TTL = 4.0  # hours


def _get_client(no_cache: bool = False, cache_ttl: float = _DEFAULT_CACHE_TTL) -> EBirdClient:
    key = os.getenv("EBIRD_API_KEY")
    if not key:
        rprint("[bold red]Error:[/] EBIRD_API_KEY not set. Add it to your .env file.")
        raise typer.Exit(1)
    cache = None if no_cache else Cache(_DEFAULT_CACHE_DIR, ttl_hours=cache_ttl)
    return EBirdClient(key, cache=cache)


@app.command()
def info(
    csv: Path = typer.Option(
        Path("data/MyEBirdData.csv"),
        "--csv",
        help="Path to your eBird data export CSV.",
        show_default=True,
    ),
):
    """Show a summary of your personal eBird data."""
    try:
        life_list = load_life_list(csv)
    except FileNotFoundError as e:
        rprint(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    console.print(f"\n[bold green]Your eBird life list:[/] {len(life_list)} species\n")

    table = Table(title="Most recently seen species (top 10)", show_lines=False)
    table.add_column("Common Name", style="cyan")
    table.add_column("Scientific Name", style="italic")
    table.add_column("Last Seen", justify="right")

    recent = sorted(
        life_list.values(),
        key=lambda s: s.last_seen or __import__("datetime").date.min,
        reverse=True,
    )[:10]

    for sp in recent:
        table.add_row(sp.common_name, sp.scientific_name, str(sp.last_seen or "—"))

    console.print(table)


@app.command()
def hotspots(
    lat: float = typer.Option(..., help="Latitude of your location."),
    lng: float = typer.Option(..., help="Longitude of your location."),
    radius: int = typer.Option(50, help="Search radius in kilometres."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache and fetch fresh data."),
):
    """List eBird hotspots near a location."""
    client = _get_client(no_cache=no_cache)

    with console.status("Fetching nearby hotspots…"):
        spots = client.nearby_hotspots(lat, lng, radius)

    console.print(f"\nFound [bold]{len(spots)}[/] hotspots within {radius} km\n")

    table = Table(title=f"Hotspots near ({lat}, {lng})", show_lines=False)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Location ID", style="dim")
    table.add_column("Species (all time)", justify="right")

    for i, spot in enumerate(spots[:20], 1):
        table.add_row(
            str(i),
            spot.name,
            spot.loc_id,
            str(spot.num_species_all_time or "—"),
        )

    console.print(table)


@app.command()
def notable(
    lat: float = typer.Option(..., help="Latitude of your location."),
    lng: float = typer.Option(..., help="Longitude of your location."),
    radius: int = typer.Option(50, help="Search radius in kilometres."),
    days: int = typer.Option(14, help="How many days back to look."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache and fetch fresh data."),
):
    """Show recent notable (rare/flagged) observations near a location."""
    client = _get_client(no_cache=no_cache)

    with console.status("Fetching notable observations…"):
        obs_list = client.nearby_notable_obs(lat, lng, radius, days)

    console.print(f"\nFound [bold]{len(obs_list)}[/] notable observations in the last {days} days\n")

    table = Table(title="Notable observations", show_lines=False)
    table.add_column("Common Name", style="cyan")
    table.add_column("Location", style="green")
    table.add_column("Date", justify="right")
    table.add_column("Count", justify="right")

    for obs in obs_list:
        table.add_row(
            obs.common_name,
            obs.loc_name,
            obs.obs_dt,
            str(obs.how_many or "—"),
        )

    console.print(table)


@app.command()
def rec(
    lat: float = typer.Option(..., help="Latitude of your location."),
    lng: float = typer.Option(..., help="Longitude of your location."),
    radius: int = typer.Option(50, help="Search radius in kilometres."),
    days: int = typer.Option(14, help="How many days back to look."),
    top: int = typer.Option(20, help="Number of recommendations to show."),
    csv: Path = typer.Option(
        Path("data/MyEBirdData.csv"),
        "--csv",
        help="Path to your eBird data export CSV.",
        show_default=True,
    ),
    lifers_only: bool = typer.Option(False, "--lifers-only", help="Show only species you haven't seen."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache and fetch fresh data."),
    cache_ttl: float = typer.Option(_DEFAULT_CACHE_TTL, "--cache-ttl", help="Cache TTL in hours.", show_default=True),
):
    """Recommend birds and hotspots worth visiting near you."""
    client = _get_client(no_cache=no_cache, cache_ttl=cache_ttl)

    try:
        seen = load_life_list(csv)
    except FileNotFoundError as e:
        rprint(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    cache_label = "[dim](cached)[/]" if not no_cache else "[dim](live)[/]"
    with console.status(f"Fetching observations within {radius} km (last {days} days)… {cache_label}"):
        all_obs     = client.nearby_recent_obs(lat, lng, radius, days)
        notable_obs = client.nearby_notable_obs(lat, lng, radius, days)

    console.print(
        f"\nLoaded [bold]{len(seen)}[/] species from your life list | "
        f"[bold]{len(all_obs)}[/] recent obs | "
        f"[bold]{len(notable_obs)}[/] notable obs\n"
    )

    recs = recommend(lat, lng, seen, all_obs, notable_obs, max_dist_km=radius)

    if lifers_only:
        recs = [r for r in recs if r.is_lifer]

    recs = recs[:top]

    if not recs:
        console.print("[yellow]No recommendations found.[/]")
        raise typer.Exit(0)

    table = Table(
        title=f"Top {len(recs)} recommendations near ({lat}, {lng})",
        show_lines=True,
    )
    table.add_column("Score", justify="right", style="bold yellow", no_wrap=True)
    table.add_column("Common Name", style="cyan", no_wrap=True)
    table.add_column("Flags", no_wrap=True)
    table.add_column("Location", style="green")
    table.add_column("Dist", justify="right", no_wrap=True)
    table.add_column("Last Seen", justify="right", no_wrap=True)
    table.add_column("Why", style="dim")

    for r in recs:
        flags = []
        if r.is_lifer:
            flags.append("[bold magenta]LIFER[/]")
        if r.is_notable:
            flags.append("[bold red]RARE[/]")

        table.add_row(
            f"{r.score:.1f}",
            r.common_name,
            " ".join(flags) if flags else "—",
            r.loc_name,
            f"{r.distance_km} km",
            r.last_reported,
            r.reason,
        )

    console.print(table)
    console.print(
        "\n[dim]Data: eBird (https://ebird.org), Cornell Lab of Ornithology[/]\n"
    )
