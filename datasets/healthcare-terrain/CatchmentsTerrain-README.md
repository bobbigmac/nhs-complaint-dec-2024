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
- no terrain-processing code has been started yet
- this folder is the placeholder for the later analysis pipeline
