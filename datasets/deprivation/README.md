# Catchment Deprivation Subset

This folder holds a one-time small-area deprivation subset for the current GTD catchment map.

Files:

- `build_catchment_subset.py` - one-off prep script that fetches the official 2025 deprivation CSV and the official 2021 LSOA boundary service, then writes the local catchment subset.
- `output/catchment_lsoa_imd_2025.geojson` - the prepared polygon subset used by the map layer.
- `output/catchment_lsoa_imd_2025_summary.json` - fetch metadata, bbox, feature counts and source URLs.

Source data:

- English Indices of Deprivation 2025 release page:
  https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025
- Official CSV used here:
  https://assets.publishing.service.gov.uk/media/691ded56d140bbbaa59a2a7d/File_7_IoD2025_All_Ranks_Scores_Deciles_Population_Denominators.csv
- Official ONS 2021 LSOA boundary service used here:
  https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-areas-december-2021-boundaries-ew-bsc-v4/about

This data is deliberately prepared outside the normal site/map build. The build only reads the checked-in subset.
