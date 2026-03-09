import json
from pathlib import Path
import pandas as pd
import re

rows = [
    # Robert Darbishire Practice PCN
    {"practice_name":"New Bank Health Centre","ods_code":"Y02960","pcn_name":"Robert Darbishire Practice PCN","borough_group":"Manchester","site_or_address":"339 Stockport Road","postcode":"M12 4JE","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Not yet inspected by current provider; inherited Good"},
    {"practice_name":"The Robert Darbishire Practice","ods_code":"P84072","pcn_name":"Robert Darbishire Practice PCN","borough_group":"Manchester","site_or_address":"Rusholme Health Centre, Walmer Street","postcode":"M14 5NP","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"The Whitswood Practice","ods_code":"P84635","pcn_name":"Robert Darbishire Practice PCN","borough_group":"Manchester","site_or_address":"Alexandra Park Health Centre, 2 Whitswood Close","postcode":"M16 7AP","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},

    # Ardwick and Longsight PCN
    {"practice_name":"Ailsa Craig Medical Centre","ods_code":"P84009","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"270 Dickenson Road, Longsight","postcode":"M13 0YL","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Ardwick Medical Practice","ods_code":"P84037","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"The Vallance Medical Centre, Wadeson Road","postcode":"M13 9UJ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Dickenson Road Medical Centre","ods_code":"P84026","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"357-359 Dickenson Road","postcode":"M13 0WQ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Drs Chiu, Koh and Gan","ods_code":"P84611","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"The Vallance Medical Centre, Wadeson Road","postcode":"M13 9UJ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Manchester Integrative Medical Practice","ods_code":"P84689","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"526-528 Stockport Road, Longsight","postcode":"M13 0RR","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Parkside Surgery","ods_code":"P84644","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"187 Northmoor Road","postcode":"M12 5RU","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Surrey Lodge Group Practice","ods_code":"P84023","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"11 Anson Road","postcode":"M14 5BY","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Dr Ngan and Partners (Vallance Medical)","ods_code":"P84005","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"The Vallance Medical Centre, Wadeson Road","postcode":"M13 9UJ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Wilmslow Road Surgery","ods_code":"P84626","pcn_name":"Ardwick and Longsight PCN","borough_group":"Manchester","site_or_address":"156 Wilmslow Road","postcode":"M14 5LQ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Good"},

    # City Centre and Ancoats PCN
    {"practice_name":"Ancoats Urban Village Medical Practice","ods_code":"P84673","pcn_name":"City Centre and Ancoats PCN","borough_group":"Manchester","site_or_address":"Ancoats Primary Care Centre, Old Mill Street","postcode":"M4 6EE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"City Health Centre","ods_code":"Y02849","pcn_name":"City Centre and Ancoats PCN","borough_group":"Manchester","site_or_address":"2nd Floor, Boots, 32 Market Street","postcode":"M1 1PL","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"New Islington Medical Practice","ods_code":"P84064","pcn_name":"City Centre and Ancoats PCN","borough_group":"Manchester","site_or_address":"Ancoats Primary Care Centre, Old Mill Street","postcode":"M4 6EE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},

    # Higher Blackley, Harpurhey and Charlestown PCN
    {"practice_name":"The Avenue Medical Centre","ods_code":"P84049","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"51-53 Victoria Avenue, Blackley","postcode":"M9 6BA","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Beacon Medical Centre","ods_code":"P84033","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"156 Victoria Avenue, Blackley","postcode":"M9 0FN","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Charlestown Medical Practice","ods_code":"Y02325","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"Charlestown Road / Charlestown Health Centre","postcode":"M9 7ED","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Not yet inspected by current provider; inherited Good"},
    {"practice_name":"Church View Medical Centre","ods_code":"P84065","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"1 Church Lane, Harpurhey","postcode":"M9 4BE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Conran Medical Centre","ods_code":"P84040","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"77 Church Lane, Harpurhey","postcode":"M9 5BH","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Dam Head Medical Centre","ods_code":"P84690","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"1020 Rochdale Road, Blackley","postcode":"M9 7HD","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Fernclough Surgery","ods_code":"P84605","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"Tavistock Square","postcode":"M9 5RD","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Valentine Medical Centre","ods_code":"P84019","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"2 Smethurst Street, Blackley","postcode":"M9 8PP","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Willowbank Surgery","ods_code":"P84679","pcn_name":"Higher Blackley, Harpurhey and Charlestown PCN","borough_group":"Manchester","site_or_address":"1 Willow Bank, Church Lane","postcode":"M9 4WH","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},

    # Miles Platting, Newton Heath and Moston PCN
    {"practice_name":"Droylsden Road Family Practice","ods_code":"","pcn_name":"Miles Platting, Newton Heath and Moston PCN","borough_group":"Manchester","site_or_address":"Newton Heath Health Centre, 2 Old Church Street","postcode":"M40 2JF","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":"Appears on CQC as GoToDoc-run site; active status should be checked separately"},
    {"practice_name":"Hazeldene Medical Centre","ods_code":"P84067","pcn_name":"Miles Platting, Newton Heath and Moston PCN","borough_group":"Manchester","site_or_address":"97 Moston Lane East, New Moston","postcode":"M40 3HD","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Newton Heath Medical Centre","ods_code":"P84070","pcn_name":"Miles Platting, Newton Heath and Moston PCN","borough_group":"Manchester","site_or_address":"Newton Heath Health Centre, 2 Old Church Street","postcode":"M40 2JF","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Simpson Medical Practice","ods_code":"Y02520","pcn_name":"Miles Platting, Newton Heath and Moston PCN","borough_group":"Manchester","site_or_address":"361 Moston Lane","postcode":"M40 9NB","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Not yet inspected by current provider; inherited Good"},
    {"practice_name":"St George's Medical Centre","ods_code":"P84025","pcn_name":"Miles Platting, Newton Heath and Moston PCN","borough_group":"Manchester","site_or_address":"St Georges Drive, Moston","postcode":"M40 5HP","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Victoria Mill Medical Practice","ods_code":"","pcn_name":"Miles Platting, Newton Heath and Moston PCN","borough_group":"Manchester","site_or_address":"10 Lower Vickers Street, Miles Platting","postcode":"M40 7LH","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Whitley Road Medical Centre","ods_code":"P84054","pcn_name":"Miles Platting, Newton Heath and Moston PCN","borough_group":"Manchester","site_or_address":"1 Whitley Road, Collyhurst","postcode":"M40 7QH","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},

    # Denton / Droylsden / Audenshaw
    {"practice_name":"Denton Medical Practice","ods_code":"P89018","pcn_name":"Denton PCN","borough_group":"Tameside","site_or_address":"100 Ashton Road, Denton","postcode":"M34 3JE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Droylsden Medical Practice","ods_code":"Y02663","pcn_name":"Denton PCN","borough_group":"Tameside","site_or_address":"1-3 Albion Drive, Droylsden","postcode":"M43 7NP","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Guide Bridge Medical Practice","ods_code":"Y02713","pcn_name":"Denton PCN","borough_group":"Tameside","site_or_address":"Guide Lane Clinic, Guide Lane, Audenshaw","postcode":"M34 5HY","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Market Street Medical Practice","ods_code":"P89029","pcn_name":"Denton PCN","borough_group":"Tameside","site_or_address":"76 Market Street, Droylsden","postcode":"M43 6DE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Medlock Vale Medical Practice","ods_code":"P89010","pcn_name":"Denton PCN","borough_group":"Tameside","site_or_address":"58 Ashton Road, Droylsden","postcode":"M43 7BW","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Millgate Healthcare Partnership","ods_code":"P89015","pcn_name":"Denton PCN","borough_group":"Tameside","site_or_address":"Ann Street, Denton","postcode":"M34 2AJ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},

    # Ashton PCN
    {"practice_name":"Albion Medical Practice","ods_code":"P89003","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"1 Albion Street, Ashton-under-Lyne","postcode":"OL6 6HF","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Ashton GP Service","ods_code":"Y02586","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"Ashton Primary Care Centre, 193 Old Street","postcode":"OL6 7SR","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Ashton Medical Group","ods_code":"P89008","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"Chapel Street","postcode":"OL6 6EW","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Gordon Street Medical Centre","ods_code":"P89011","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"171 Mossley Road","postcode":"OL6 6NE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"HT Practice","ods_code":"P89020","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"156 Stockport Road, Ashton-under-Lyne","postcode":"OL7 0NW","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Stamford House","ods_code":"P89609","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"2 Princess Street, Ashton-under-Lyne","postcode":"OL6 9QH","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Waterloo Medical Centre","ods_code":"P89613","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"1 Dunkerley Street, Ashton-under-Lyne","postcode":"OL7 9EJ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"West End Medical Centre","ods_code":"P89030","pcn_name":"Ashton PCN","borough_group":"Tameside","site_or_address":"98-102 Stockport Road, Ashton-under-Lyne","postcode":"OL7 0LH","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},

    # Stalybridge, Dukinfield and Mossley PCN
    {"practice_name":"Staveleigh Medical Centre","ods_code":"P89007","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"King Street, Stalybridge","postcode":"SK15 2AE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Grosvenor Medical Centre","ods_code":"P89026","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"62 Grosvenor Street, Stalybridge","postcode":"SK15 1RZ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"St Andrew's House Medical Centre","ods_code":"P89023","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"2 Waterloo Road, Stalybridge","postcode":"SK15 2AU","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Lockside Medical Centre","ods_code":"P89005","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"85 Huddersfield Road, Stalybridge","postcode":"SK15 2PT","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Millbrook Medical Practice","ods_code":"Y02936","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"Hollybank House, Hollybank, Millbrook, Stalybridge","postcode":"SK15 3BJ","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Mossley Medical Practice","ods_code":"P89612","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"187 Manchester Road, Mossley","postcode":"OL5 9AB","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Pike Medical Practice","ods_code":"P89618","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"Market Place, Mossley","postcode":"OL5 0HE","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Town Hall Surgery","ods_code":"P89025","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"112 King Street, Dukinfield","postcode":"SK16 4LD","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"King Street Medical Centre","ods_code":"P89022","pcn_name":"Stalybridge, Dukinfield and Mossley PCN","borough_group":"Tameside","site_or_address":"96-98 King Street, Dukinfield","postcode":"SK16 4JZ","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},

    # Oldham Central PCN
    {"practice_name":"Alexander Group Medical Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"Glodwick Primary Care Centre, 137 Glodwick Road","postcode":"OL4 1YN","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Dr Perkins' Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"1st Floor Integrated Care Centre, New Radcliffe Street","postcode":"OL1 1NL","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Glodwick Medical Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"137 Glodwick Road","postcode":"OL4 1YN","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Greenbank Medical Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"Barley Clough Medical Centre, Nugget Street","postcode":"OL4 1BN","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Hopwood House Medical Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"Lees Road","postcode":"OL4 1JN","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"John Street Medical Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"1 John Street","postcode":"OL8 1DF","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"Lindley Medical Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"Ground Floor, Integrated Care Centre, New Radcliffe Street","postcode":"OL1 1NL","gtd_managed":True,"inclusion_basis":"GTD-managed anchor","cqc_overall":"Good"},
    {"practice_name":"Oldham Family Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"1st Floor Integrated Care Centre, New Radcliffe Street","postcode":"OL1 1NL","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"St Mary's Medical Centre","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"Rock Street","postcode":"OL1 3UL","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"The Chowdhury Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"Integrated Care Centre, New Radcliffe Street","postcode":"OL1 1NL","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
    {"practice_name":"The Jalal Practice","ods_code":"","pcn_name":"Oldham Central PCN","borough_group":"Oldham","site_or_address":"1st Floor Integrated Care Centre, New Radcliffe Street","postcode":"OL1 1NL","gtd_managed":False,"inclusion_basis":"Same PCN as GTD-managed anchor","cqc_overall":""},
]

df = pd.DataFrame(rows)
df["postcode_district"] = df["postcode"].str.extract(r"^([A-Z]{1,2}\d{1,2}[A-Z]?)")
df["search_key"] = (
    df["practice_name"].fillna("") + " | " +
    df["pcn_name"].fillna("") + " | " +
    df["site_or_address"].fillna("") + " | " +
    df["postcode"].fillna("") + " | " +
    df["borough_group"].fillna("")
).str.lower()

# a few useful review estimates previously surfaced publicly; leave blank elsewhere
google_est = {
    "Manchester Integrative Medical Practice": (2.2, 91, "third-party snippet"),
    "Surrey Lodge Group Practice": (2.6, 128, "third-party snippet"),
    "The Robert Darbishire Practice": (2.5, 234, "third-party snippet"),
}
df["google_review_score_estimate"] = df["practice_name"].map(lambda x: google_est.get(x, (None, None, ""))[0])
df["google_review_count_estimate"] = df["practice_name"].map(lambda x: google_est.get(x, (None, None, ""))[1])
df["google_review_source"] = df["practice_name"].map(lambda x: google_est.get(x, (None, None, ""))[2])

df = df.sort_values(["borough_group", "pcn_name", "postcode", "practice_name"]).reset_index(drop=True)

outdir = Path("/mnt/data")
csv_path = outdir / "gtd_manchester_area_practices_postcode_first.csv"
json_path = outdir / "gtd_manchester_area_practices_postcode_first.json"
html_path = outdir / "gtd_manchester_area_practices_postcode_first.html"
summary_path = outdir / "gtd_manchester_area_practices_postcode_first_summary.json"

df.to_csv(csv_path, index=False)
json_path.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")

summary = {
    "generated_date": "2026-03-09",
    "scope_note": "Postcode-first generous Manchester-area catchment around GTD-managed GP practices and their surrounding PCN memberships. Coordinates intentionally omitted.",
    "row_count": int(len(df)),
    "gtd_managed_count": int(df["gtd_managed"].sum()),
    "borough_counts": df["borough_group"].value_counts().to_dict(),
    "pcn_counts": df["pcn_name"].value_counts().to_dict(),
    "postcode_district_counts": df["postcode_district"].value_counts().sort_index().to_dict(),
}
summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

district_counts = (
    df.groupby("postcode_district")
      .size()
      .reset_index(name="count")
      .sort_values(["postcode_district"])
)

pcn_counts = (
    df.groupby(["borough_group", "pcn_name"])
      .size()
      .reset_index(name="count")
      .sort_values(["borough_group", "pcn_name"])
)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Manchester-area GP practices (postcode-first)</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
  font: 14px/1.45 system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  margin: 24px;
  color: #111;
}}
h1 {{ margin: 0 0 8px; font-size: 24px; }}
p {{ margin: 0 0 14px; }}
.controls {{
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 10px;
  margin: 18px 0;
}}
input, select {{
  padding: 8px 10px;
  border: 1px solid #bbb;
  border-radius: 8px;
  font: inherit;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}}
th, td {{
  border-bottom: 1px solid #e5e5e5;
  padding: 8px 6px;
  text-align: left;
  vertical-align: top;
}}
th {{
  position: sticky;
  top: 0;
  background: #fff;
}}
.tag {{
  display: inline-block;
  border: 1px solid #d0d0d0;
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 12px;
  white-space: nowrap;
}}
.small {{ color: #555; font-size: 12px; }}
.grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin: 18px 0 10px;
}}
pre {{
  background: #fafafa;
  border: 1px solid #eee;
  padding: 12px;
  border-radius: 10px;
  overflow: auto;
}}
button {{
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #bbb;
  background: white;
  cursor: pointer;
}}
</style>
</head>
<body>
<h1>GTD Manchester-area GP practices, postcode-first</h1>
<p>This is the generous overscoped set around GTD-managed GP anchors in Manchester / Tameside / Oldham. Search by postcode prefix like <code>M1</code>, <code>M9</code>, <code>M40</code>, <code>OL1</code>, <code>SK15</code>.</p>

<div class="grid">
  <div>
    <strong>District counts</strong>
    <pre>{district_counts.to_string(index=False)}</pre>
  </div>
  <div>
    <strong>PCN counts</strong>
    <pre>{pcn_counts.to_string(index=False)}</pre>
  </div>
</div>

<div class="controls">
  <input id="q" placeholder="Search practice / postcode / district / street / borough">
  <select id="borough">
    <option value="">All borough groups</option>
  </select>
  <select id="pcn">
    <option value="">All PCNs</option>
  </select>
  <select id="gtd">
    <option value="">All practices</option>
    <option value="true">GTD-managed only</option>
    <option value="false">Non-GTD only</option>
  </select>
</div>

<div class="small" id="count"></div>
<p>
  <button id="downloadCsv">Download filtered CSV</button>
</p>

<table id="tbl">
  <thead>
    <tr>
      <th>Practice</th>
      <th>Postcode</th>
      <th>PCN</th>
      <th>Borough</th>
      <th>GTD</th>
      <th>Address/site</th>
      <th>CQC</th>
      <th>Google est.</th>
    </tr>
  </thead>
  <tbody></tbody>
</table>

<script>
const rows = {json.dumps(df.to_dict(orient="records"))};

const boroughs = [...new Set(rows.map(r => r.borough_group).filter(Boolean))].sort();
const pcns = [...new Set(rows.map(r => r.pcn_name).filter(Boolean))].sort();

const boroughSel = document.getElementById("borough");
const pcnSel = document.getElementById("pcn");
for (const v of boroughs) {{
  const o = document.createElement("option");
  o.value = v; o.textContent = v; boroughSel.appendChild(o);
}}
for (const v of pcns) {{
  const o = document.createElement("option");
  o.value = v; o.textContent = v; pcnSel.appendChild(o);
}}

function filteredRows() {{
  const q = document.getElementById("q").value.trim().toLowerCase();
  const borough = boroughSel.value;
  const pcn = pcnSel.value;
  const gtd = document.getElementById("gtd").value;
  return rows.filter(r => {{
    if (q && !r.search_key.includes(q)) return false;
    if (borough && r.borough_group !== borough) return false;
    if (pcn && r.pcn_name !== pcn) return false;
    if (gtd === "true" && !r.gtd_managed) return false;
    if (gtd === "false" && r.gtd_managed) return false;
    return true;
  }});
}}

function render() {{
  const tbody = document.querySelector("#tbl tbody");
  tbody.innerHTML = "";
  const data = filteredRows();
  document.getElementById("count").textContent = `${{data.length}} rows`;

  for (const r of data) {{
    const tr = document.createElement("tr");
    const google = r.google_review_score_estimate ? `${{r.google_review_score_estimate}} (${{r.google_review_count_estimate}})` : "";
    tr.innerHTML = `
      <td><div><strong>${{r.practice_name}}</strong></div><div class="small">${{r.ods_code || ""}}</div></td>
      <td><div>${{r.postcode}}</div><div class="small">${{r.postcode_district}}</div></td>
      <td>${{r.pcn_name}}</td>
      <td>${{r.borough_group}}</td>
      <td>${{r.gtd_managed ? '<span class="tag">GTD</span>' : ''}}</td>
      <td>${{r.site_or_address || ""}}</td>
      <td>${{r.cqc_overall || ""}}</td>
      <td>${{google}}</td>
    `;
    tbody.appendChild(tr);
  }}
}}

function downloadFilteredCsv() {{
  const data = filteredRows();
  const cols = Object.keys(rows[0]).filter(c => c !== "search_key");
  const esc = v => {{
    if (v === null || v === undefined) return "";
    const s = String(v);
    return /[",\\n]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s;
  }};
  const csv = [cols.join(",")]
    .concat(data.map(r => cols.map(c => esc(r[c])).join(",")))
    .join("\\n");
  const blob = new Blob([csv], {{type: "text/csv;charset=utf-8;"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "filtered_gtd_manchester_area_practices_postcode_first.csv";
  a.click();
  URL.revokeObjectURL(url);
}}

document.getElementById("q").addEventListener("input", render);
boroughSel.addEventListener("change", render);
pcnSel.addEventListener("change", render);
document.getElementById("gtd").addEventListener("change", render);
document.getElementById("downloadCsv").addEventListener("click", downloadFilteredCsv);
render();
</script>
</body>
</html>
"""
html_path.write_text(html, encoding="utf-8")

preview = df[["practice_name","postcode","postcode_district","pcn_name","borough_group","gtd_managed"]]
try:
    from caas_jupyter_tools import display_dataframe_to_user
    display_dataframe_to_user("GTD Manchester-area practices, postcode-first", preview)
except Exception:
    print(preview.head(20).to_string(index=False))

print(f"Saved: {csv_path}")
print(f"Saved: {json_path}")
print(f"Saved: {html_path}")
print(f"Saved: {summary_path}")
print(f"Rows: {len(df)}")