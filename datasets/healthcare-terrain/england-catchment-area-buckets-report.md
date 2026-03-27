# England Catchment Area Buckets

Generated: 2026-03-27 05:10 UTC

This report is **England only** and uses the hard polygon catchment cache under `datasets/catchments/.cache/gp-catchments-england/by_practice/`.

## Area Method

- Each practice area is the sum of all polygon / multipolygon feature parts in its England catchment cache file.
- Area is calculated directly from lon/lat rings using a spherical polygon-area approximation with the Web Mercator Earth radius used elsewhere in the healthcare-terrain tooling.
- Invalid or non-ODS cache filenames are excluded from the ranked pool.

## Distribution Summary

- Valid England catchments ranked: `7,650`
- Minimum area: `0.001` km²
- Median area: `22.86` km²
- 90th percentile area: `158.6` km²
- Maximum area: `9,994.2` km²

## Bucket Design

Buckets use human-readable round-number area bands instead of equal-count splits. The aim is to show the real shape of the England catchment spread in ranges that are easy to think about, even if that means the counts are front-weighted and the long tail stays visible.

Full member codes are exported separately to `england-catchment-area-bucket-members.tsv` as TSV cells, one row per bucket.

| Bucket | Members | Share | Range |
| --- | ---: | ---: | --- |
| 1 | 92 | 1.2% | <= 1 km² |
| 2 | 199 | 2.6% | > 1 to <= 2 km² |
| 3 | 737 | 9.6% | > 2 to <= 5 km² |
| 4 | 1,037 | 13.6% | > 5 to <= 10 km² |
| 5 | 1,487 | 19.4% | > 10 to <= 20 km² |
| 6 | 1,806 | 23.6% | > 20 to <= 50 km² |
| 7 | 985 | 12.9% | > 50 to <= 100 km² |
| 8 | 779 | 10.2% | > 100 to <= 200 km² |
| 9 | 487 | 6.4% | > 200 to <= 500 km² |
| 10 | 34 | 0.4% | > 500 to <= 1,000 km² |
| 11 | 7 | 0.1% | > 1,000 km² |

## New Bank Health

- Practice code: `Y02960`
- Catchment area: `2.107` km²
- Bucket: `> 2 to <= 5 km²`
- Global England rank by smallest catchment area: `314` / `7650`
- Global England area percentile, smaller-first: `4.1`
- Put plainly: `95.9%` of England practices have larger catchments than New Bank
- Published Manchester extended England rank by smallest catchment area: `14` / `358`
- Published Manchester extended England percentile, smaller-first: `3.9`
- GTD England rank by smallest catchment area: `2` / `13`
- GTD England percentile, smaller-first: `15.4`

Scope note:
All catchment areas in this report come from the one England catchment cache. The only scope changes here are whether New Bank is compared with all England catchments, the published Manchester-extended England pool, or just the GTD England subset.

## Score Patterns By Catchment Size

- England practices with catchment area plus survey score: `6,051`
- England practices with catchment area plus Google score: `5,974`
- Overall survey vs catchment-area correlation is weak: Pearson `0.135`, Spearman `0.138`
- Overall Google vs catchment-area correlation is also weak: Pearson `0.148`, Spearman `0.125`
- Inside the more normal `<= 100 km²` range, the relationship is close to flat: survey Pearson `0.041`, Google Pearson `0.034`

The visible lift is mostly in the large-catchment tail rather than across ordinary urban and suburban sizes. That makes this look more like a rurality or population-sparsity effect than a simple rule that bigger catchments directly produce better scores.

| Bucket | Practices with area | Survey mean | Survey >= 75% | Google mean | Google >= 4.0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| <= 1 km² | `69` | `77.2` | `59.7%` | `3.15` | `22.1%` |
| > 1 to <= 2 km² | `149` | `75.9` | `56.4%` | `3.20` | `19.3%` |
| > 2 to <= 5 km² | `570` | `76.4` | `59.4%` | `3.19` | `21.7%` |
| > 5 to <= 10 km² | `805` | `75.2` | `55.2%` | `3.13` | `19.0%` |
| > 10 to <= 20 km² | `1,158` | `75.7` | `56.0%` | `3.09` | `17.0%` |
| > 20 to <= 50 km² | `1,423` | `76.3` | `57.8%` | `3.12` | `17.9%` |
| > 50 to <= 100 km² | `795` | `77.1` | `62.0%` | `3.21` | `20.3%` |
| > 100 to <= 200 km² | `655` | `80.8` | `72.4%` | `3.49` | `31.2%` |
| > 200 to <= 500 km² | `414` | `80.9` | `70.9%` | `3.55` | `35.0%` |
| > 500 to <= 1,000 km² | `20` | `82.9` | `75.0%` | `3.56` | `31.6%` |
| > 1,000 km² | `4` | `80.2` | `75.0%` | `3.48` | `25.0%` |

## GTD England Practices

| Practice | Code | Area | Bucket | England rank | England percentile |
| --- | --- | ---: | --- | ---: | ---: |
| Charlestown MD | `Y02325` | `1.986` km² | > 1 to <= 2 km² | `290` / `7650` | `3.8` |
| New Bank Health | `Y02960` | `2.107` km² | > 2 to <= 5 km² | `314` / `7650` | `4.1` |
| Simpson Medical Practice | `Y02520` | `3.722` km² | > 2 to <= 5 km² | `705` / `7650` | `9.2` |
| Droylsden Medical Practice | `Y02663` | `6.385` km² | > 5 to <= 10 km² | `1326` / `7650` | `17.3` |
| Gordon Street Medical Centre | `P89011` | `6.497` km² | > 5 to <= 10 km² | `1353` / `7650` | `17.7` |
| The Smithy Surgery | `P89602` | `7.897` km² | > 5 to <= 10 km² | `1629` / `7650` | `21.3` |
| Mossley Medical Practice | `P89612` | `10.42` km² | > 10 to <= 20 km² | `2148` / `7650` | `28.1` |
| Hattersley Group Practice | `P89013` | `11.65` km² | > 10 to <= 20 km² | `2381` / `7650` | `31.1` |
| Ashton Gp Service | `Y02586` | `12.24` km² | > 10 to <= 20 km² | `2450` / `7650` | `32.0` |
| Guide Bridge Medical Practice | `Y02713` | `12.83` km² | > 10 to <= 20 km² | `2534` / `7650` | `33.1` |
| City Health Centre | `Y02849` | `23.67` km² | > 20 to <= 50 km² | `3890` / `7650` | `50.8` |
| Millbrook Medical Practice | `Y02936` | `27.83` km² | > 20 to <= 50 km² | `4237` / `7650` | `55.4` |
| Lindley House Health Centre | `Y02875` | `71.12` km² | > 50 to <= 100 km² | `5885` / `7650` | `76.9` |

## Bucket Summaries

### Bucket 1: <= 1 km²

- Members: `92`
- Share of England catchments: `1.2%`
- Smallest member area: `0.001` km²
- Largest member area: `1.000` km²

### Bucket 2: > 1 to <= 2 km²

- Members: `199`
- Share of England catchments: `2.6%`
- Smallest member area: `1.005` km²
- Largest member area: `1.994` km²

### Bucket 3: > 2 to <= 5 km²

- Members: `737`
- Share of England catchments: `9.6%`
- Smallest member area: `2.006` km²
- Largest member area: `4.999` km²

### Bucket 4: > 5 to <= 10 km²

- Members: `1,037`
- Share of England catchments: `13.6%`
- Smallest member area: `5.006` km²
- Largest member area: `9.997` km²

### Bucket 5: > 10 to <= 20 km²

- Members: `1,487`
- Share of England catchments: `19.4%`
- Smallest member area: `10.00` km²
- Largest member area: `19.99` km²

### Bucket 6: > 20 to <= 50 km²

- Members: `1,806`
- Share of England catchments: `23.6%`
- Smallest member area: `20.03` km²
- Largest member area: `49.95` km²

### Bucket 7: > 50 to <= 100 km²

- Members: `985`
- Share of England catchments: `12.9%`
- Smallest member area: `50.05` km²
- Largest member area: `99.98` km²

### Bucket 8: > 100 to <= 200 km²

- Members: `779`
- Share of England catchments: `10.2%`
- Smallest member area: `100.0` km²
- Largest member area: `199.9` km²

### Bucket 9: > 200 to <= 500 km²

- Members: `487`
- Share of England catchments: `6.4%`
- Smallest member area: `200.1` km²
- Largest member area: `499.1` km²

### Bucket 10: > 500 to <= 1,000 km²

- Members: `34`
- Share of England catchments: `0.4%`
- Smallest member area: `501.3` km²
- Largest member area: `931.2` km²

### Bucket 11: > 1,000 km²

- Members: `7`
- Share of England catchments: `0.1%`
- Smallest member area: `1,062.8` km²
- Largest member area: `9,994.2` km²

