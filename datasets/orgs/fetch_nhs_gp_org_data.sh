#!/usr/bin/env bash
set -uo pipefail
shopt -s nullglob

ROOT="${1:-uk-gp-org-data-$(date +%F)}"
UA="nhs-gp-org-data-fetcher/1.0 (+https://chat.openai.com)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p \
  "$ROOT/_meta" \
  "$ROOT/england/ods_gp" \
  "$ROOT/england/ods_orgs" \
  "$ROOT/england/cqc" \
  "$ROOT/england/performance" \
  "$ROOT/wales/statswales" \
  "$ROOT/scotland/open-data" \
  "$ROOT/ni/ods" \
  "$ROOT/ni/opendatani"

LOG="$ROOT/_meta/fetch.log"
SRC="$ROOT/_meta/sources.tsv"
FAIL="$ROOT/_meta/failed.tsv"

: > "$LOG"
printf 'path\turl\tnote\n' > "$SRC"
printf 'path\turl\terror\n' > "$FAIL"

FAILED=0

tlog() {
  printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG" >&2
}

record_source() {
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$SRC"
}

record_fail() {
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$FAIL"
  FAILED=$((FAILED + 1))
}

download() {
  local url="$1"
  local out="$2"
  local note="$3"
  local errfile
  mkdir -p "$(dirname "$out")"
  record_source "${out#$ROOT/}" "$url" "$note"
  if [[ -s "$out" ]]; then
    tlog "SKIP $out"
    return 0
  fi
  tlog "GET  $url"
  errfile="$(mktemp)"
  if ! curl -fL --retry 5 --retry-delay 2 --retry-all-errors --connect-timeout 20 \
      -A "$UA" -o "$out" "$url" 2>"$errfile"; then
    tlog "FAIL $url"
    rm -f "$out"
    record_fail "${out#$ROOT/}" "$url" "$(tr '\n' ' ' < "$errfile" | sed 's/[[:space:]]\+/ /g')"
  fi
  rm -f "$errfile"
}

ods_report() {
  local folder="$1"
  local report="$2"
  local note="$3"
  download "https://www.odsdatasearchandexport.nhs.uk/api/getReport?report=${report}" \
           "$ROOT/$folder/${report}.csv" \
           "$note"
}

scrape_links() {
  local page_url="$1"
  local regex="$2"
  local prefix="$3"
  local tmp
  tmp="$(mktemp)"
  curl -fsSL -A "$UA" "$page_url" -o "$tmp" || {
    rm -f "$tmp"
    return 1
  }
  grep -oE "$regex" "$tmp" | sed -E "s#^/#${prefix}/#" | sort -u
  rm -f "$tmp"
}

# England: ODS GP / organisation relationship data.
ods_report "england/ods_gp" epraccur "ODS GP practices"
ods_report "england/ods_gp" ebranchs "ODS branch surgeries"
ods_report "england/ods_gp" epcmem "ODS GP practices linked to commissioner / LHG"
ods_report "england/ods_gp" epracmem "ODS GPs by GP practice"
ods_report "england/ods_gp" epcn "ODS primary care networks"
ods_report "england/ods_gp" epcncorepartnerdetails "ODS PCN core partner details"
ods_report "england/ods_gp" epracarc "ODS archived GP practices"
ods_report "england/ods_gp" eabeydispgp "ODS abeyance and dispersal GP codes"

ods_report "england/ods_orgs" ephp "ODS independent sector healthcare providers"
ods_report "england/ods_orgs" ephpsite "ODS independent sector healthcare provider sites"
ods_report "england/ods_orgs" enonnhs "ODS non-NHS independent providers"
ods_report "england/ods_orgs" etr "ODS NHS trusts"
ods_report "england/ods_orgs" ets "ODS NHS trust sites"
ods_report "england/ods_orgs" eccg "ODS clinical commissioning groups"
ods_report "england/ods_orgs" eccgsite "ODS CCG sites"
ods_report "england/ods_orgs" ect "ODS care trusts"
ods_report "england/ods_orgs" ectsite "ODS care trust sites"
ods_report "england/ods_orgs" wlhb "ODS Welsh local health boards"
ods_report "england/ods_orgs" wlhbsite "ODS Welsh local health board sites"
download "https://digital.nhs.uk/binaries/content/assets/website-assets/services/ods/other-nhs-organisations/icb-partners-master.xlsx" \
         "$ROOT/england/ods_orgs/icb-partners-master.xlsx" \
         "ODS ICB partner organisations"
download "https://digital.nhs.uk/binaries/content/assets/website-assets/services/ods/other-nhs-organisations/provider-to-commissioning-hub-relationship-v4.0-may-2021.xlsx" \
         "$ROOT/england/ods_orgs/provider-to-commissioning-hub-relationship-v4.0-may-2021.xlsx" \
         "ODS provider to commissioning hub mapping"

# England: CQC data sheets, scraped so the current filenames roll forward automatically.
tlog "SCRAPE CQC data sheet links"
mapfile -t cqc_urls < <(
  scrape_links \
    "https://www.cqc.org.uk/about-us/transparency/using-cqc-data" \
    "https://www\.cqc\.org\.uk/sites/default/files/[^\"[:space:]]+" \
    "https://www.cqc.org.uk" \
  | grep -E '(_CQC_directory\.(csv|zip)|HSCA_Active_Locations\.ods|Latest_ratings\.ods|Deactivated_Locations\.ods)$' || true
)
if [[ ${#cqc_urls[@]} -eq 0 ]]; then
  cqc_urls=(
    "https://www.cqc.org.uk/sites/default/files/2026-03/18_March_2026_CQC_directory.csv"
    "https://www.cqc.org.uk/sites/default/files/2026-03/18_March_2026_CQC_directory.zip"
    "https://www.cqc.org.uk/sites/default/files/2026-03/01_March_2026_HSCA_Active_Locations.ods"
    "https://www.cqc.org.uk/sites/default/files/2026-03/01_March_2026_Latest_ratings.ods"
    "https://www.cqc.org.uk/sites/default/files/2026-03/01_March_2026_Deactivated_Locations.ods"
  )
fi
for url in "${cqc_urls[@]}"; do
  download "$url" "$ROOT/england/cqc/$(basename "${url%%\?*}")" "CQC care directory / ratings / archived locations"
done

# England: performance / operating context.
download "https://files.digital.nhs.uk/A7/B0FFAB/GPWIndividualCSV.012026.zip" \
         "$ROOT/england/performance/GPWIndividualCSV.012026.zip" \
         "General Practice Workforce individual-level CSV, January 2026"
download "https://files.digital.nhs.uk/EC/203865/GPWPracticeCSV.012026.zip" \
         "$ROOT/england/performance/GPWPracticeCSV.012026.zip" \
         "General Practice Workforce practice-level CSVs, January 2026"
download "https://files.digital.nhs.uk/7A/651D52/nhspaymentsgp-23-24-prac-csv.csv" \
         "$ROOT/england/performance/nhspaymentsgp-23-24-prac-csv.csv" \
         "NHS Payments to General Practice practice-level CSV, England 2023/24"
download "https://files.digital.nhs.uk/F6/3E59E7/nhspaymentsgp-23-24-pcn-csv.csv" \
         "$ROOT/england/performance/nhspaymentsgp-23-24-pcn-csv.csv" \
         "NHS Payments to General Practice PCN-level CSV, England 2023/24"
download "https://files.digital.nhs.uk/95/4708D7/QOF2425.zip" \
         "$ROOT/england/performance/QOF2425.zip" \
         "Quality and Outcomes Framework raw data, 2024/25"
download "https://files.digital.nhs.uk/02/B37640/Core%20GP%20Contract%202024-25%20csv%20files.zip" \
         "$ROOT/england/performance/Core-GP-Contract-2024-25-csv-files.zip" \
         "GP Contract Services core GP contract data, 2024/25"

# Wales: StatsWales zipped OData exports plus metadata.
for code in HLTH0426 HLTH0464 HLTH1113; do
  download "https://statswales.gov.wales/Download/File?fileName=${code}.zip" \
           "$ROOT/wales/statswales/${code}.zip" \
           "StatsWales dataset ${code} zipped OData export"
  download "https://statswales.gov.wales/Download/File?fileName=${code}.xml" \
           "$ROOT/wales/statswales/${code}.xml" \
           "StatsWales dataset ${code} metadata XML"
  download "https://statswales.gov.wales/Download/File?fileName=${code}_dimensions.csv" \
           "$ROOT/wales/statswales/${code}_dimensions.csv" \
           "StatsWales dataset ${code} dimensions"
  download "https://statswales.gov.wales/Download/File?fileName=${code}_dimensionitems.csv" \
           "$ROOT/wales/statswales/${code}_dimensionitems.csv" \
           "StatsWales dataset ${code} dimension items"
done

# Scotland: scrape every CSV resource currently on the GP practice contact details page.
tlog "SCRAPE Scotland GP practice list-size resources"
mapfile -t scotland_urls < <(
  scrape_links \
    "https://www.opendata.nhs.scot/dataset/gp-practice-contact-details-and-list-sizes" \
    "(https://www\.opendata\.nhs\.scot)?/dataset/[^\"[:space:]]+/download/[^\"[:space:]]+\.csv" \
    "https://www.opendata.nhs.scot" || true
)
if [[ ${#scotland_urls[@]} -eq 0 ]]; then
  scotland_urls=(
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/ceddbf27-0686-4f4b-b9a2-0090d28c3864/download/practice_contact_details_20260101_opendata.csv"
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/47557411-7eda-4278-9d6d-d26ed2ceab5a/download/practice_contact_details_20251001_opendata.csv"
  )
fi
for url in "${scotland_urls[@]}"; do
  download "$url" "$ROOT/scotland/open-data/$(basename "${url%%\?*}")" "Scotland GP practice contact details and list sizes"
done

# Northern Ireland: ODS home-country reports plus the quarterly practice list-size page from OpenDataNI.
ods_report "ni/ods" ngpcur "ODS GPs in Northern Ireland"
ods_report "ni/ods" npraccur "ODS GP practices in Northern Ireland"
ods_report "ni/ods" niorg "ODS boards, trusts and local HSC groups in Northern Ireland"
ods_report "ni/ods" nlhscgpr "ODS Northern Ireland GP practices making up each LHSCG"
download "https://files.digital.nhs.uk/assets/ods/current/niarchive.csv" \
         "$ROOT/ni/ods/niarchive.csv" \
         "ODS Northern Ireland archive"

tlog "SCRAPE Northern Ireland GP practice list-size resources"
mapfile -t ni_urls < <(
  scrape_links \
    "https://www.data.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/gp-practice-list-sizes" \
    "(https://admin\.opendatani\.gov\.uk)?/dataset/[^\"[:space:]]+/download/[^\"[:space:]]+\.csv" \
    "https://admin.opendatani.gov.uk" || true
)
if [[ ${#ni_urls[@]} -eq 0 ]]; then
  ni_urls=(
    "https://admin.opendatani.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/resource/8578e0d4-47f6-4909-9ac4-32643a701e13/download/gp-practice-reference-file-january-2026.csv"
  )
fi
for url in "${ni_urls[@]}"; do
  download "$url" "$ROOT/ni/opendatani/$(basename "${url%%\?*}")" "OpenDataNI GP practice list sizes"
done

# Human-readable inventory.
declare -A DESC
DESC["_meta"]="Fetch logs and a machine-readable source index."
DESC["england/ods_gp"]="ODS GP/practice reference and relationship files: practices, branches, commissioner links, GP memberships, PCNs, PCN core partners, archived GP codes."
DESC["england/ods_orgs"]="ODS organisation tables that GP practices can link to: independent providers, trusts, sites, local health boards, legacy commissioner structures, ICB partner mapping."
DESC["england/cqc"]="CQC care directory files for England, including provider/location linkage, current ratings, and deactivated locations."
DESC["england/performance"]="England operating / performance context files: workforce, payments, QOF raw data, and core GP contract service data."
DESC["wales/statswales"]="StatsWales zipped OData extracts and metadata for practice population / cluster / health board context and related practice-level indicators."
DESC["scotland/open-data"]="Public Health Scotland GP practice contact details and list-size CSV resources discovered from the official dataset page."
DESC["ni/ods"]="ODS Northern Ireland organisation and GP reference files."
DESC["ni/opendatani"]="OpenDataNI quarterly GP practice list-size CSV resources discovered from the official dataset page."

README="$ROOT/README.md"
{
  echo "# NHS GP organisation data bundle"
  echo
  echo "Generated: $TS"
  echo
  echo "This bundle is raw official source material for GP ownership-adjacent, membership and organisational-relationship mapping."
  echo
  echo "The root source index is in [_meta/sources.tsv](./_meta/sources.tsv)."
  echo
  for dir in _meta england/ods_gp england/ods_orgs england/cqc england/performance wales/statswales scotland/open-data ni/ods ni/opendatani; do
    echo "## $dir"
    echo
    echo "${DESC[$dir]}"
    echo
    files=("$ROOT/$dir"/*)
    if [[ ${#files[@]} -eq 0 ]]; then
      echo "- _empty_"
      echo
      continue
    fi
    for f in "${files[@]}"; do
      [[ -e "$f" ]] || continue
      size="$(du -h "$f" | awk '{print $1}')"
      echo "- $(basename "$f") ($size)"
    done | sort
    echo
  done

  if [[ -s "$FAIL" && $(wc -l < "$FAIL") -gt 1 ]]; then
    echo "## Failed downloads"
    echo
    echo "Some endpoints failed. See [_meta/failed.tsv](./_meta/failed.tsv)."
    echo
  fi

  echo "## Notes"
  echo
  echo "- ODS DSE report endpoints are current-state exports and are refreshed nightly by ODS."
  echo "- CQC files are England-only and are useful for provider/location linkage and historic re-registration trails."
  echo "- StatsWales files are zipped OData exports and include separate XML / dimension metadata files."
  echo "- Scotland and Northern Ireland lists are scraped from their official dataset pages at run time so newly-published quarterly CSVs are picked up automatically."
} > "$README"

tlog "DONE root=$ROOT failed_downloads=$FAILED"
printf 'Created %s\n' "$ROOT"
if [[ $FAILED -gt 0 ]]; then
  printf 'Some downloads failed. See %s\n' "$FAIL"
fi
