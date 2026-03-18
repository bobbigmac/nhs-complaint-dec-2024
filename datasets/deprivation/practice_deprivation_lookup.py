from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path
from typing import Any, Iterable


BASE_DIR = Path(__file__).resolve().parents[1]
DEPRIVATION_SUBSET_GEOJSON = BASE_DIR / "deprivation" / "output" / "catchment_lsoa_imd_2025.geojson"


@dataclass(frozen=True)
class DeprivationPoint:
    code: str
    lon: float
    lat: float
    imd_decile: int | None
    health_decile: int | None
    imd_rank: int | None
    imd_score: float | None


def _load_deprivation_points(path: Path = DEPRIVATION_SUBSET_GEOJSON) -> list[DeprivationPoint]:
    if not path.exists():
        return []
    import json

    payload = json.loads(path.read_text(encoding="utf-8"))
    features: Iterable[dict[str, Any]] = payload.get("features", [])
    points: list[DeprivationPoint] = []
    for feature in features:
        props = feature.get("properties", {}) or {}
        geom = feature.get("geometry") or {}
        if geom.get("type") != "Polygon":
            continue
        coords = geom.get("coordinates") or []
        if not coords or not coords[0]:
            continue
        # Use first ring and a simple centroid-like average of its vertices as an inexpensive proxy
        ring = coords[0]
        xs = [float(p[0]) for p in ring]
        ys = [float(p[1]) for p in ring]
        if not xs or not ys:
            continue
        lon = sum(xs) / len(xs)
        lat = sum(ys) / len(ys)
        points.append(
            DeprivationPoint(
                code=str(props.get("lsoa21cd", "")).strip(),
                lon=lon,
                lat=lat,
                imd_decile=int(props["imd_decile"]) if props.get("imd_decile") not in (None, "") else None,
                health_decile=int(props["health_decile"]) if props.get("health_decile") not in (None, "") else None,
                imd_rank=int(props["imd_rank"]) if props.get("imd_rank") not in (None, "") else None,
                imd_score=float(props["imd_score"]) if props.get("imd_score") not in (None, "") else None,
            )
        )
    return points


def build_practice_deprivation_lookup(
    rows: list[dict[str, Any]],
    *,
    deprivation_points: list[DeprivationPoint] | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Build a lightweight lookup keyed by practice code with nearest LSOA deprivation.
    """
    if deprivation_points is None:
        deprivation_points = _load_deprivation_points()
    if not deprivation_points:
        return {}

    lookup: dict[str, dict[str, Any]] = {}
    for row in rows:
        try:
            code = str(row["canonical_code"]).strip()
            lon = float(row["longitude"])
            lat = float(row["latitude"])
        except (KeyError, TypeError, ValueError):
            continue

        # Nearest-neighbour in lon/lat space; good enough within this catchment
        best: DeprivationPoint | None = None
        best_dist = float("inf")
        for point in deprivation_points:
            dist = hypot(point.lon - lon, point.lat - lat)
            if dist < best_dist:
                best_dist = dist
                best = point

        if best is None:
            continue

        lookup[code] = {
            "lsoa_code": best.code,
            "imd_decile": best.imd_decile,
            "health_decile": best.health_decile,
            "imd_rank": best.imd_rank,
            "imd_score": best.imd_score,
        }

    return lookup


def write_practice_deprivation_lookup(path: Path, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Convenience wrapper for builds: compute and write JSON, returning the lookup.
    """
    import json

    lookup = build_practice_deprivation_lookup(rows)
    path.write_text(json.dumps(lookup, indent=2, ensure_ascii=False), encoding="utf-8")
    return lookup


__all__ = ["build_practice_deprivation_lookup", "write_practice_deprivation_lookup", "DeprivationPoint"]

