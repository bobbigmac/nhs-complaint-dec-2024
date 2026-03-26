# Catchments Terrain

This folder is for an analysis-only tool that turns GP catchments plus practice quality signals into a spatial "healthcare terrain" or "healthcare desert" map.

It is not part of the patient-facing picker for now.

## Objective

Estimate, for every point in the study area:

- how many practices are realistically available
- how many of those are above a chosen quality threshold
- where availability drops sharply
- where residents may sit outside all published catchments

This is intended as a report / analysis layer first, not a GitHub Pages runtime feature.

## Product Shape

Primary outputs should be static analysis artifacts such as:

- bucketed GeoJSON polygons
- summary rasters or tiles
- CSV summaries by area
- narrative reports and maps

Possible headline views:

- total practice availability
- availability above Google / survey / blended threshold
- "good options within catchment"
- "out-of-area fallback only"
- likely healthcare deserts

## Core Inputs

- England GP catchment polygons from `datasets/catchments`
- GP registration flags such as `accepts_out_of_area_registrations`
- practice quality metrics already used in the map build
- optional deprivation overlays for comparison, not as a hard dependency

## Basic Design

1. Define a sampling grid or raster over the area of interest.
2. For each sample point, test which practice catchments contain it.
3. Attach practice scores and registration flags to those matches.
4. Compute derived measures such as:
   - raw count of in-catchment practices
   - count above threshold
   - best available score
   - average of top N
   - fallback out-of-area count within radius
5. Bucket the resulting point values into simple ranges.
6. Convert adjacent equal-value cells into merged polygons where practical.
7. Export analysis artifacts and summaries.

## Delivery Constraints

- Raw point-by-point output will get large quickly.
- Client-side delivery on GitHub Pages is only realistic if the output is aggressively simplified.
- Any public map version should prefer merged polygons or coarse tiles over dense point features.
- The first implementation should run offline / dev-time only.

## Shape Merging Strategy

If this ever ships as a browser map, the output should be bucketed and merged before publication.

Candidate buckets:

- `0` in-catchment practices
- `1`
- `2-3`
- `4-6`
- `7+`

Candidate quality buckets:

- no "good" practice available
- at least one acceptable option
- several good options
- strong choice density

This lets large contiguous areas collapse into sensible emergent polygons instead of flooding the generated map with tiny cells.

## Suggested Implementation Plan

Phase 1:

- prototype a Manchester-only grid analysis
- write summary CSV and PNG / notebook-style outputs
- validate obvious zero-catchment and low-choice zones

Phase 2:

- add threshold variants and out-of-area fallback scoring
- compare with deprivation and density
- test polygon merging

Phase 3:

- decide whether a simplified public artifact is small enough for Pages
- if not, keep this as an internal report pipeline only

## Open Questions

- What is the right base geography: raster grid, hex bins, LSOA centroids, or road-network points?
- Should "availability" require `accepting_new_patients`, or should closed lists still count as structural supply?
- How should out-of-area fallback be weighted against true in-catchment availability?
- Which score threshold is defensible enough for a public "desert" claim?

## Current Status

- catchment and registration-flag inputs now exist
- first-pass raster generator now exists as `build_catchment_availability_raster.py`
- current implementation measures raw in-catchment overlap count only

## Current Prototype

Run:

```bash
python3 datasets/healthcare-terrain/build_catchment_availability_raster.py
python3 datasets/healthcare-terrain/build_distance_strength_rasters.py
```

Default outputs land in `datasets/healthcare-terrain/output/england-catchment-availability/`:

- `availability-bands.png`
- `summary.txt`
- `summary.json`
- `metadata.json`
- `tiles/{z}/{x}/{y}.png`

Distance-strength outputs land in `datasets/healthcare-terrain/output/distance-strength/{nation_or_overlay}/`:

- `distance-strength-bands.png`
- `summary.txt`
- `summary.json`
- `metadata.json`
- `tiles/{z}/{x}/{y}.png`

What it does:

1. scans the England per-practice catchment GeoJSON cache
2. projects the data bbox into Web Mercator
3. rasterizes polygons by scanline fill into a coarse overlap grid
4. buckets counts into fixed bands:
   - `0`
   - `1-2`
   - `3-5`
   - `6-9`
   - `10-19`
   - `20+`
5. writes a banded PNG preview plus XYZ tile images for server-side overlay use
6. writes rough area and histogram summaries as a quick sanity check
7. flood-fills the contiguous exterior zero-value area from the raster edge and makes only that outside region transparent in the preview and tiles, so sea/outside-bbox pixels drop away without erasing genuine inland zero bands

The distance-strength generator is the softer fallback / supplement model used for:

- England out-of-area support
- Scotland
- Wales
- Northern Ireland

That model:

1. starts from the national supplemental practice point set with usable coordinates
2. gives each practice full strength inside a near radius
3. linearly tapers that strength down to zero at a wider far radius
4. sums those strengths into a coarse raster
5. writes nation-specific PNGs, summaries and tiles
6. applies the same exterior flood-fill transparency mask so only the connected outside-zero area is clipped away

This is intentionally softer than the England catchment layer. It is meant to show likely structural availability gradients, not a hard registration boundary.

England note:

- the England terrain layer is built directly from the full England catchment polygon cache, not from national supplementals
- where the Manchester core review dataset contains a practice with coordinates but no cached England catchment polygon, the raster builder adds a small local point fallback so those reviewed practices do not create artificial low-coverage holes
- England out-of-area support is now a separate distance-strength layer built only from locally logged practices flagged as accepting out-of-area registrations, so it can be toggled on alongside or instead of the hard England catchment layer

Current distance-strength assumptions:

- England out-of-area: `3.0` miles near, `10.0` miles far
- Scotland: `3.0` miles near, `12.0` miles far
- Wales: `3.0` miles near, `10.0` miles far
- Northern Ireland: `3.0` miles near, `10.0` miles far

## Why This Approach

This avoids the bad version of the problem, which is:

- test every sample point against every catchment polygon

Instead, the prototype cost is dominated by:

- reading each polygon once
- filling the raster rows touched by that polygon

On the current England cache this is fast enough for offline builds at coarse national resolution.

## Current Caveat

The `0` bucket is still measured across the raster bbox, not against an England land boundary or population mask.

That means:

- sea and outside-land cells inside the bbox also show as `0`
- the zero band is useful for a first overlap picture, but not yet a defensible "healthcare desert" claim

The next sensible upgrade is to clip or mask against one of:

- England boundary
- population-weighted geography such as LSOA centroids / polygons
- a denser inhabited-area mask
