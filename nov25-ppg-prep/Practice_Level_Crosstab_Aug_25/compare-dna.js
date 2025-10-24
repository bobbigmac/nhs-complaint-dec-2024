// compare-dna.js
// Usage:
//   node compare-dna.js <csv-file> <ODS_CODE> [--scope subicb|pcn|supplier|all] [--supplier "Name"]
//   node compare-dna.js --inspect [dir] [--rows 3]
// Examples:
//   node compare-dna.js GPAD_Annex1_Practice_Level_Data_August_2025.csv Y02960 --scope pcn
//   node compare-dna.js GPAD_Annex1_Practice_Level_Data_August_2025.csv Y02960 --scope supplier
//   node compare-dna.js GPAD_Annex1_Practice_Level_Data_August_2025.csv Y02960 --scope supplier --supplier "EMIS"

import fs from "node:fs";
import path from "node:path";
import { parse } from "csv-parse";

const argv = process.argv.slice(2);

// --- helpers ---
const norm = s => String(s ?? "").trim();
const lc = s => norm(s).toLowerCase();
function argVal(flag) {
  const i = argv.indexOf(flag);
  if (i !== -1 && i + 1 < argv.length) return argv[i + 1];
  return null;
}
const toNum = v => {
  if (v == null) return 0;
  const n = Number(String(v).replace(/[, ]/g, ""));
  return Number.isFinite(n) ? n : 0;
};

const PRACTICE_CODE_KEYS = [
  "practice ods code","practice_ods_code","ods code","gp code","gp_code","practice code","practice code (ods)"
];
const PRACTICE_NAME_KEYS = ["practice name","gp name","gp_name","gp practice name","practice"];
const STATUS_KEYS = ["appointment status","status","appt_status"];
const COUNT_KEYS = ["appointments","count","number of appointments","number_of_appointments","count_of_appointments"];
const SUBICB_KEYS = [
  "sub icb location name","sub icb location code",
  "sub-icb location name","sub-icb location code",
  "sub_icb_location name","sub_icb_location code",
  "sub_icb_location_name","sub_icb_location_code",
  "icb name","icb code"
];
const PCN_KEYS = ["pcn name","pcn code","pcn_name","pcn_code"];
const SUPPLIER_KEYS = ["supplier","supplier name","system supplier","supplier_name"];

// --- inspect mode ---
if (argv[0] === "--inspect") {
  const dir = argVal("--inspect") || argv[1] || process.cwd();
  const rowsStr = argVal("--rows");
  const sampleRows = Math.max(1, Number(rowsStr || 3));
  (async () => {
    const files = fs.readdirSync(dir).filter(f => f.toLowerCase().endsWith(".csv"));
    const out = [];
    for (const f of files) {
      const fp = path.resolve(dir, f);
      try {
        const info = await sampleCsv(fp, sampleRows);
        out.push(info);
      } catch (e) {
        out.push({ file: fp, error: String(e && e.message || e) });
      }
    }
    console.log(JSON.stringify(out, null, 2));
  })()
    .then(() => process.exit(0))
    .catch(e => { console.error(e?.stack || String(e)); process.exit(1); });
} else {
  // --- compare mode ---
  if (argv.length < 2) {
    console.error("usage: node compare-dna.js <csv-file> <ODS_CODE> [--scope subicb|pcn|supplier|all] [--supplier \"Name\"]");
    process.exit(1);
  }
  const filePath = argv[0];
  const TARGET = argv[1].trim().toUpperCase();
  const scopeArg = (argVal("--scope") || "subicb").toLowerCase();
  const supplierOverride = argVal("--supplier");

  streamCompare(filePath, TARGET, scopeArg, supplierOverride).catch(err => {
    console.error(err?.stack || String(err));
    process.exit(1);
  });
}

// --- core: streaming compare ---
async function streamCompare(filePath, TARGET, scopeArg, supplierOverride) {
  const byPractice = new Map();

  let headerMap = null; // Map<lowerHeader, originalHeader>
  let cols = null; // resolved column names
  let statusColumnsWide = null; // array of original header names for wide statuses

  await new Promise((resolve, reject) => {
    const rs = fs.createReadStream(filePath);
    const parser = parse({ columns: true, skip_empty_lines: true, relax_column_count: true });

    rs.on("error", reject);
    parser.on("error", reject);
    parser.on("end", resolve);

    parser.on("readable", () => {
      let row;
      while ((row = parser.read())) {
        if (!headerMap) {
          const headers = Object.keys(row || {});
          headerMap = new Map(headers.map(h => [lc(h), h]));
          const getCol = (cands) => cands.map(c => headerMap.get(c)).find(Boolean);
          cols = {
            PRACTICE_COL: getCol(PRACTICE_CODE_KEYS),
            NAME_COL: getCol(PRACTICE_NAME_KEYS),
            STATUS_COL: getCol(STATUS_KEYS),
            COUNT_COL: getCol(COUNT_KEYS),
            SUBICB_NAME_COL: getCol(SUBICB_KEYS.filter(k => k.includes("name"))),
            SUBICB_CODE_COL: getCol(SUBICB_KEYS.filter(k => k.includes("code"))),
            PCN_NAME_COL: getCol(PCN_KEYS.filter(k => k.includes("name"))),
            PCN_CODE_COL: getCol(PCN_KEYS.filter(k => k.includes("code"))),
            SUPPLIER_COL: getCol(SUPPLIER_KEYS),
          };
          statusColumnsWide = headers.filter(h => ["attended","did not attend","dna","unknown","patient cancelled","practice cancelled"].includes(lc(h)));
        }

        const practice = norm(row[cols.PRACTICE_COL] ?? row["Practice ODS Code"] ?? row["GP Code"]);
        if (!practice) continue;

        const cohortFields = {
          name: norm(row[cols.NAME_COL]),
          subicb_name: norm(row[cols.SUBICB_NAME_COL]),
          subicb_code: norm(row[cols.SUBICB_CODE_COL]),
          pcn_name: norm(row[cols.PCN_NAME_COL]),
          pcn_code: norm(row[cols.PCN_CODE_COL]),
          supplier: supplierOverride ?? norm(row[cols.SUPPLIER_COL]),
        };

        if (statusColumnsWide && statusColumnsWide.length) {
          for (const sc of statusColumnsWide) {
            addCount(byPractice, practice, lc(sc), toNum(row[sc]), cohortFields);
          }
        } else {
          const status = lc(row[cols.STATUS_COL] ?? "");
          addCount(byPractice, practice, status, toNum(row[cols.COUNT_COL]), cohortFields);
        }
      }
    });

    rs.pipe(parser);
  });

  const target = byPractice.get(TARGET);
  if (!target) {
    console.error(`Practice ${TARGET} not found.`);
    process.exit(2);
  }
  if (!(target.total > 0)) {
    console.error(`Practice ${TARGET} has no usable appointment totals.`);
    process.exit(3);
  }

  const makeCohort = () => {
    if (scopeArg === "all") return [...byPractice.entries()];
    if (scopeArg === "pcn" && target.pcn_code) {
      return [...byPractice.entries()].filter(([,v]) => v.pcn_code && v.pcn_code === target.pcn_code);
    }
    if (scopeArg === "supplier" && target.supplier) {
      return [...byPractice.entries()].filter(([,v]) => v.supplier && v.supplier.toLowerCase() === target.supplier.toLowerCase());
    }
    // default: sub-ICB (falls back to ALL if missing)
    if (target.subicb_code) {
      return [...byPractice.entries()].filter(([,v]) => v.subicb_code && v.subicb_code === target.subicb_code);
    }
    return [...byPractice.entries()];
  };

  const cohort = makeCohort()
    .map(([practice, v]) => ({ practice, name: v.name, total: v.total, dna: v.dna, rate: v.total>0 ? v.dna/v.total : 0 }))
    .filter(r => r.total > 0);

  cohort.sort((a,b) => b.rate - a.rate); // worst first
  const index = cohort.findIndex(r => r.practice === TARGET);
  const rank = index + 1;
  const n = cohort.length;

  const higher = cohort.filter(r => r.rate > cohort[index].rate).length;
  const lower  = cohort.filter(r => r.rate < cohort[index].rate).length;
  const equal  = n - higher - lower;

  const pct = x => (x*100).toFixed(2) + "%";
  const fmtRate = r => (r*100).toFixed(2) + "%";
  const money = n => "£" + Math.round(n).toLocaleString();

  const dnaRate = cohort[index].rate;
  const midCost = cohort[index].dna * 30;

  const out = {
    target: {
      ods: TARGET,
      name: target.name || null,
      sub_icb: target.subicb_name || null,
      pcn: target.pcn_name || null,
      supplier: target.supplier || null,
      total_appointments: cohort[index].total,
      dna_appointments: cohort[index].dna,
      dna_rate: fmtRate(dnaRate),
    },
    cohort: {
      scope: scopeArg,
      members: n,
      rank_by_dna_rate_desc: rank,        // 1 = worst DNA rate in cohort
      percentile_worse: pct(higher / n),  // % with higher DNA rate
      percentile_better: pct(lower / n),  // % with lower DNA rate
      ties_same_rate: equal
    },
    estimate: {
      cost_mid_30: money(midCost)
    }
  };

  console.log(JSON.stringify(out, null, 2));
}

function addCount(byPractice, practice, status, count, cohortFields) {
  const key = practice.toUpperCase();
  const s = normalizeStatus(status);
  const rec = byPractice.get(key) || {
    name: cohortFields.name,
    subicb_name: cohortFields.subicb_name, subicb_code: cohortFields.subicb_code,
    pcn_name: cohortFields.pcn_name, pcn_code: cohortFields.pcn_code,
    supplier: cohortFields.supplier,
    total: 0, dna: 0
  };
  rec.total += count;
  if (s === "dna") rec.dna += count;
  if (!rec.name && cohortFields.name) rec.name = cohortFields.name;
  if (!rec.subicb_name && cohortFields.subicb_name) rec.subicb_name = cohortFields.subicb_name;
  if (!rec.subicb_code && cohortFields.subicb_code) rec.subicb_code = cohortFields.subicb_code;
  if (!rec.pcn_name && cohortFields.pcn_name) rec.pcn_name = cohortFields.pcn_name;
  if (!rec.pcn_code && cohortFields.pcn_code) rec.pcn_code = cohortFields.pcn_code;
  if (!rec.supplier && cohortFields.supplier) rec.supplier = cohortFields.supplier;
  byPractice.set(key, rec);
}

function normalizeStatus(s) {
  switch (s) {
    case "did not attend":
    case "dna":
      return "dna";
    case "attended":
      return "attended";
    case "unknown":
      return "unknown";
    case "patient cancelled":
      return "patient cancelled";
    case "practice cancelled":
      return "practice cancelled";
    default:
      return s;
  }
}

// --- sampling helper for inspect mode ---
function sampleCsv(filePath, maxRows) {
  return new Promise((resolve, reject) => {
    const rs = fs.createReadStream(filePath);
    const parser = parse({ columns: true, skip_empty_lines: true, relax_column_count: true });
    const sample = [];
    let headers = null;
    let done = false;

    function finish() {
      if (done) return;
      done = true;
      const stat = fs.statSync(filePath);
      const looksPractice = inferLooksLikePractice(headers);
      resolve({
        file: filePath,
        size_bytes: stat.size,
        headers: headers || [],
        sample_rows: sample,
        looks_like_practice_data: looksPractice
      });
    }

    rs.on("error", err => { done = true; reject(err); });
    parser.on("error", err => { done = true; reject(err); });
    parser.on("end", () => finish());
    parser.on("readable", () => {
      let row;
      while (!done && (row = parser.read())) {
        if (!headers) headers = Object.keys(row);
        sample.push(row);
        if (sample.length >= maxRows) {
          // stop early
          try { parser.destroy(); } catch {}
          try { rs.destroy(); } catch {}
          finish();
          break;
        }
      }
    });

    rs.pipe(parser);
  });
}

function inferLooksLikePractice(headers) {
  if (!headers || !headers.length) return false;
  const L = headers.map(h => lc(h));
  const hasPractice = L.some(h => PRACTICE_CODE_KEYS.includes(h));
  const hasAppt = L.some(h => COUNT_KEYS.includes(h) || ["attended","did not attend","dna","unknown","patient cancelled","practice cancelled"].includes(h));
  return hasPractice && hasAppt;
}
