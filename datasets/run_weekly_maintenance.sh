#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/2] Refresh England GP catchments and registration flags"
python3 datasets/catchments/fetch_gp_catchments_england.py --outdir datasets/catchments/.cache/gp-catchments-england
python3 datasets/catchments/fetch_gp_registration_flags_england.py --outdir datasets/catchments/.cache/gp-registration-flags-england
python3 datasets/catchments/build_site_catchment_bundles.py

echo "[2/2] Refresh CQC GP ratings"
python3 datasets/scripts/fetch_cqc_gp_ratings.py
