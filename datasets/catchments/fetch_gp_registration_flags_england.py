#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR.parent
DEFAULT_OUTDIR = BASE_DIR / ".cache" / "gp-registration-flags-england"
BUILD_SCRIPT_PATH = DATASETS_DIR / "build_gtd_gp_practice_dataset.py"


def log(*args: object) -> None:
    print(*args, file=sys.stderr)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_manifest(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "practice_code",
                "practice_name",
                "profile_url",
                "accepting_new_patients",
                "accepts_out_of_area_registrations",
                "search_hits",
                "search_areas",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_build_module():
    if str(DATASETS_DIR) not in sys.path:
        sys.path.insert(0, str(DATASETS_DIR))
    module_name = "build_gtd_gp_practice_dataset"
    spec = importlib.util.spec_from_file_location(module_name, BUILD_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load build script from {BUILD_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def search_areas(build_module) -> list[dict[str, Any]]:
    areas: list[dict[str, Any]] = []
    for anchor in build_module.GTD_ANCHORS:
        geo = build_module.postcode_lookup(anchor.postcode)
        lat = float(geo["latitude"])
        lon = float(geo["longitude"])
        areas.append(
            {
                "kind": "gtd_anchor",
                "name": anchor.gtd_site_name,
                "postcode": anchor.postcode,
                "latitude": lat,
                "longitude": lon,
                "search_url": build_module.anchor_search_url(lat, lon, anchor.gtd_site_name),
            }
        )
    for center in build_module.SUPPLEMENTAL_SEARCH_CENTERS:
        geo = build_module.postcode_lookup(center.postcode)
        lat = float(geo["latitude"])
        lon = float(geo["longitude"])
        areas.append(
            {
                "kind": "supplemental_center",
                "name": center.name,
                "postcode": center.postcode,
                "latitude": lat,
                "longitude": lon,
                "search_url": build_module.anchor_search_url(lat, lon, center.name),
            }
        )
    return areas


def collect_flags(build_module) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    flags_by_practice: dict[str, dict[str, Any]] = {}
    search_runs: list[dict[str, Any]] = []

    for area in search_areas(build_module):
        log(f"fetching {area['kind']}: {area['name']} ({area['postcode']})")
        html = build_module.fetch_text(area["search_url"])
        rows = build_module.parse_nhs_search_results(html)
        search_runs.append(
            {
                **area,
                "result_count": len(rows),
            }
        )
        for row in rows:
            code = str(row.get("ods_code") or "").strip().upper()
            if not code:
                continue
            entry = flags_by_practice.setdefault(
                code,
                {
                    "practice_code": code,
                    "practice_name": str(row.get("name") or "").strip(),
                    "profile_url": str(row.get("profile_url") or "").strip(),
                    "accepting_new_patients": False,
                    "accepts_out_of_area_registrations": False,
                    "search_hits": 0,
                    "search_areas": [],
                },
            )
            practice_name = str(row.get("name") or "").strip()
            profile_url = str(row.get("profile_url") or "").strip()
            if practice_name and not entry["practice_name"]:
                entry["practice_name"] = practice_name
            if profile_url and not entry["profile_url"]:
                entry["profile_url"] = profile_url
            entry["accepting_new_patients"] = bool(entry["accepting_new_patients"]) or bool(row.get("accepting_new_patients"))
            entry["accepts_out_of_area_registrations"] = bool(entry["accepts_out_of_area_registrations"]) or bool(
                row.get("accepts_out_of_area_registrations")
            )
            entry["search_hits"] = int(entry["search_hits"]) + 1
            if area["name"] not in entry["search_areas"]:
                entry["search_areas"].append(area["name"])

    return flags_by_practice, search_runs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch NHS GP registration flags used for out-of-area registration support."
    )
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR, help="Local cache/output directory")
    args = parser.parse_args()

    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    build_module = load_build_module()
    flags_by_practice, search_runs = collect_flags(build_module)

    normalized_flags = {
        code: {
            "practice_name": row["practice_name"],
            "profile_url": row["profile_url"],
            "accepting_new_patients": bool(row["accepting_new_patients"]),
            "accepts_out_of_area_registrations": bool(row["accepts_out_of_area_registrations"]),
            "search_hits": int(row["search_hits"]),
            "search_areas": list(row["search_areas"]),
        }
        for code, row in sorted(flags_by_practice.items())
    }
    manifest_rows = [
        {
            "practice_code": code,
            "practice_name": row["practice_name"],
            "profile_url": row["profile_url"],
            "accepting_new_patients": bool(row["accepting_new_patients"]),
            "accepts_out_of_area_registrations": bool(row["accepts_out_of_area_registrations"]),
            "search_hits": int(row["search_hits"]),
            "search_areas": " | ".join(row["search_areas"]),
        }
        for code, row in sorted(flags_by_practice.items())
    ]

    write_json(outdir / "flags_by_practice.json", normalized_flags)
    write_json(outdir / "search_runs.json", search_runs)
    write_json(
        outdir / "source.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "script": str(Path(__file__).resolve()),
            "build_script": str(BUILD_SCRIPT_PATH.resolve()),
            "search_area_count": len(search_runs),
            "practice_count": len(normalized_flags),
            "search_runs": search_runs,
        },
    )
    write_manifest(outdir / "manifest.csv", manifest_rows)

    print(
        json.dumps(
            {
                "flags_by_practice_json": str(outdir / "flags_by_practice.json"),
                "manifest_csv": str(outdir / "manifest.csv"),
                "search_runs_json": str(outdir / "search_runs.json"),
                "source_metadata": str(outdir / "source.json"),
                "practice_count": len(normalized_flags),
                "search_area_count": len(search_runs),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
