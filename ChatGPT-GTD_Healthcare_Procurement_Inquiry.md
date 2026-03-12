# GTD Healthcare Procurement Inquiry

#### You:
![image](sediment://file_000000002f90720a981d05e58b3141a6)
![image](sediment://file_00000000a3ec7243b27af0ac35ee1032)
okay, so I've got this site, that shows for google reviews (and almost as bad for patient survey)... GTD Healthcare Ltd (aka GoToDoc) have the worst or second worst practice satisfaction scores, and I want to know why they a) just (18 months to a year ago or therabouts) got awarded the contract for New Bank Health Centre, when all of their practices have terrible quality scores and b) who 'exactly' made that decision, to start looking for brown envelopes. and b) according to companies house, GTD are basically broke, or nearly, for that type of org... why are they still allowed to operate? Staff 'kinda hinted' that they're who gets brought in to fix problems, but I'm very unconvinced since most of their practices have been under their control for years. Basically, I want to know the exact process for who put these clowns in charge of yet another GP practice, and why, and where to find the receipts. Something smells off here, and I need you to find everything you can about this process/contract/tender/whatever that you can find, and help me figure out why such an obviously incapable firm took over yet another doctor's surgery.

#### Plugin (file_search):
Make sure to include fileciteturn0file0 in your response to cite this file, or to surface it as a link.
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Greater Manchester GP Practice Experience</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {
  --bg: #f6f4ef;
  --ink: #1a1c1a;
  --panel: rgba(255,255,255,0.92);
  --panel-strong: rgba(255,255,255,0.98);
  --missing: #9aa0a6;
  --low: #c3472f;
  --midlow: #dc8c23;
  --midhigh: #d2b529;
  --high: #4c9a52;
  --veryhigh: #1c7c54;
  --line: rgba(26,28,26,0.12);
  --accent: #0f5e9c;
}
html, body {
  margin: 0;
}
body {
  font: 14px/1.4 Georgia, serif;
  color: var(--ink);
  background: radial-gradient(circle at top, #fff7e3, var(--bg));
}
.page {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-rows: minmax(100vh, 100dvh) auto;
}
.map-stage {
  display: grid;
  grid-template-areas: "legend map";
  grid-template-columns: 360px minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}
#map {
  grid-area: map;
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  min-height: 100dvh;
}
.legend {
  grid-area: legend;
  position: relative;
  z-index: 10;
  background: var(--panel-strong);
  padding: 12px 14px;
  border-right: 1px solid var(--line);
  box-shadow: inset -1px 0 0 rgba(26, 28, 26, 0.04);
  max-width: none;
  overflow: auto;
}
.legend h1 {
  margin: 0 0 8px;
  font-size: 18px;
}
.legend p {
  margin: 0 0 8px;
}
.legend h2 {
  margin: 12px 0 8px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.legend .row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.legend .hint {
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.control-group {
  display: grid;
  gap: 8px;
}
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(15, 94, 156, 0.06);
}
#size-mode-control {
  grid-template-columns: 1fr 1fr;
}
#voronoi-control {
  display: flex;
  align-items: center;
  gap: 8px;
}
#voronoi-control input {
  display: inline-block;
}
.segmented label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
}
.segmented input {
  display: none;
}
.segmented span {
  width: 100%;
  text-align: center;
  border-radius: 999px;
  padding: 5px 8px;
}
.segmented input:checked + span {
  background: var(--accent);
  color: #fff;
}
.metric-note {
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}
.manager-list {
  display: grid;
  gap: 8px;
  max-height: 210px;
  overflow: auto;
  padding-right: 4px;
}
.manager-option {
  display: grid;
  grid-template-columns: 18px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.manager-option input {
  margin: 0;
}
.manager-name {
  min-width: 0;
}
.manager-meta {
  color: rgba(26, 28, 26, 0.68);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.swatch {
  width: 14px;
  height: 14px;
  border: 1px solid rgba(0,0,0,0.25);
  flex: 0 0 auto;
}
.swatch.circle {
  border-radius: 999px;
}
.swatch.square {}
.swatch.diamond {
  transform: rotate(45deg);
}
.swatch.triangle {
  clip-path: polygon(50% 0, 0 100%, 100% 100%);
}
.swatch.hexagon {
  clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);
}
.swatch.pentagon {
  clip-path: polygon(50% 0, 100% 38%, 81% 100%, 19% 100%, 0 38%);
}
.leaflet-marker-icon.marker-icon {
  background: transparent;
  border: 0;
}
.marker-svg {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.22));
}
.leaflet-popup-content {
  min-width: 220px;
}
.leaflet-popup-content a {
  word-break: break-word;
}
.insights {
  padding: 18px 18px 26px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}
.panel {
  background: var(--panel-strong);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}
.panel h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.panel p {
  margin: 0 0 10px;
}
.chart-frame {
  width: 100%;
  overflow-x: auto;
}
#scatterplot {
  width: 100%;
  height: 320px;
  display: block;
}
.chart-note {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}
.comparison-panel {
  grid-column: 1 / -1;
}
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.comparison-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255,255,255,0.72);
  padding: 12px 14px;
}
.comparison-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
}
.comparison-kicker {
  margin: 0 0 10px;
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.comparison-summary {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.45;
}
.comparison-summary p {
  margin: 0 0 10px;
}
.rank-bar {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}
.rank-bar-track {
  position: relative;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, #b23322 0%, #d7b74b 50%, #1f7a3f 100%);
  box-shadow: inset 0 0 0 1px rgba(26, 28, 26, 0.14);
  overflow: hidden;
}
.rank-bar-marker {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #fff;
  border: 2px solid rgba(26, 28, 26, 0.82);
  box-shadow: 0 2px 6px rgba(0,0,0,0.16);
  transform: translate(-50%, -50%);
}
.rank-bar-labels {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
  line-height: 1.35;
}
.rank-bar-labels span {
  color: rgba(26, 28, 26, 0.8);
}
.rank-bar-labels strong {
  color: #161816;
}
.rank-bar-labels .rank-worse {
  text-align: left;
}
.rank-bar-labels .rank-better {
  text-align: right;
}
.comparison-metrics {
  display: grid;
  gap: 8px;
}
.comparison-row {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 1.1fr;
  gap: 10px;
  align-items: baseline;
  padding: 8px 0;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
}
.comparison-row:first-child {
  border-top: 0;
  padding-top: 0;
}
.comparison-label {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.comparison-stat strong {
  display: block;
  font-size: 18px;
}
.comparison-stat strong.tone-good {
  color: #1f7a3f;
}
.comparison-stat strong.tone-mid {
  color: #9d6a00;
}
.comparison-stat strong.tone-bad {
  color: #b23322;
}
.comparison-stat strong.tone-missing {
  color: #7d838a;
}
.comparison-stat span {
  display: block;
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
}
.comparison-delta {
  font-size: 13px;
  line-height: 1.4;
}
.comparison-delta.tone-good {
  color: #1f7a3f;
}
.comparison-delta.tone-mid {
  color: #9d6a00;
}
.comparison-delta.tone-bad {
  color: #b23322;
}
.comparison-delta.tone-missing {
  color: #7d838a;
}
@media (max-width: 960px) {
  .page {
    grid-template-rows: minmax(100vh, 100dvh) auto;
  }
  .map-stage {
    grid-template-areas:
      "map"
      "legend";
    grid-template-columns: 1fr;
    grid-template-rows: minmax(62vh, 70dvh) auto;
    min-height: auto;
  }
  #map {
    height: 62vh;
    height: 62dvh;
    min-height: 62vh;
    min-height: 62dvh;
  }
  .insights {
    grid-template-columns: 1fr;
  }
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  .comparison-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .legend {
    border-right: 0;
    border-top: 1px solid var(--line);
    box-shadow: none;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    background: #fff;
  }
  .page {
    display: block;
  }
  .map-stage {
    grid-template-areas: "legend map";
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: auto;
    break-inside: avoid-page;
  }
  #map {
    height: 170mm;
    min-height: 170mm;
  }
  .legend {
    border: 1px solid var(--line);
    border-right: 0;
    box-shadow: none;
  }
  .panel {
    box-shadow: none;
    border: 1px solid var(--line);
    break-inside: avoid-page;
  }
  .leaflet-control-container {
    display: none;
  }
  .marker-svg {
    filter: none;
  }
}
</style>
</head>
<body>
<div class="page">
  <div class="map-stage">
    <div class="legend">
      <h1>GTD GP Practice Experience Map</h1>
      <p>424 GP surgery profiles from a broad catchment around GTD anchors.</p>
      <p>3,021,833 registered patients across 360 practices.</p>
      <div class="control-group">
        <h2>Score Source</h2>
        <div class="segmented">
          <label><input type="radio" name="score-source" value="google" checked><span>Google</span></label>
          <label><input type="radio" name="score-source" value="survey"><span>GP Survey</span></label>
          <label><input type="radio" name="score-source" value="gap"><span>Gap</span></label>
        </div>
        <p id="metric-description" class="hint"></p>
      </div>
      <div class="control-group">
        <div id="voronoi-control">
          <label title="An estimated population/affected-people view. This is a rough vibes layer, not a real practice boundary map."><input type="checkbox" id="voronoi-toggle"><span>Est. population</span></label>
        </div>
      </div>
      <h2>Management</h2>
      <p id="manager-hint" class="hint"></p>
      <div id="manager-list" class="manager-list"></div>
    </div>
    <div id="map"></div>
  </div>
  <div class="insights">
    <section class="panel comparison-panel">
      <h2 id="comparison-heading">Interactive Benchmarks</h2>
      <p id="comparison-note" class="hint"></p>
      <div id="comparison-grid" class="comparison-grid"></div>
    </section>
    <section class="panel comparison-panel">
      <h2>Completion Rate vs Score</h2>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source.</p>
    </section>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@turf/turf@7.2.0/turf.min.js"></script>
<script>
const rows = [{"code": "Y02849", "name": "City Health Centre", "lat": 53.4827, "lon": -2.24292, "postcode": "M1 1PL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.5, "google_count": 11, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02849-city-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/city-health-centre/Y02849", "gtd_url": "https://www.gtdhealthcare.co.uk/cityhealthcentre", "nearby": "City Health Centre, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 9, "survey_sent_out": 957, "survey_sent_back": 85, "registered_patient_count": 15321}, {"code": "Y02960", "name": "New Bank Health", "lat": 53.4601, "lon": -2.20437, "postcode": "M12 4JE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 163, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02960-new-bank-health.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/new-bank-health/Y02960", "gtd_url": "https://www.gtdhealthcare.co.uk/newbankhealthcentre", "nearby": "City Health Centre, Droylsden Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 942, "survey_sent_back": 98, "registered_patient_count": 6419}, {"code": "Y02713", "name": "Guide Bridge Medical Practice", "lat": 53.4716, "lon": -2.11327, "postcode": "M34 5HY", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 116, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02713-guide-bridge-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/guide-bridge-medical-practice/Y02713", "gtd_url": "https://www.gtdhealthcare.co.uk/guidebridgemedicalpractice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 53, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 531, "survey_sent_back": 122, "registered_patient_count": 4478}, {"code": "Y02520", "name": "Simpson Medical Practice", "lat": 53.514, "lon": -2.19802, "postcode": "M40 9NB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 104, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02520-simpson-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/simpson-medical-practice/Y02520", "gtd_url": "https://www.gtdhealthcare.co.uk/simpsonmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 463, "survey_sent_back": 76, "registered_patient_count": 5375}, {"code": "Y02663", "name": "Droylsden Medical Practice", "lat": 53.4872, "lon": -2.14565, "postcode": "M43 7NP", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 85, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02663-droylsden-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/droylsden-medical-practice/Y02663", "gtd_url": "https://www.gtdhealthcare.co.uk/droylsdenmedicalpractice", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 49, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 550, "survey_sent_back": 100, "registered_patient_count": 4388}, {"code": "Y02325", "name": "Charlestown MD", "lat": 53.5226, "lon": -2.18689, "postcode": "M9 7ED", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 109, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02325-charlestown-md.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlestown-md/Y02325", "gtd_url": "https://www.gtdhealthcare.co.uk/charlestownmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Lindley Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 59, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 621, "survey_sent_back": 106, "registered_patient_count": 5268}, {"code": "Y02875", "name": "Lindley House Health Centre", "lat": 53.5438, "lon": -2.11693, "postcode": "OL1 1NL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 66, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02875-lindley-house-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/lindley-house-health-centre/Y02875", "gtd_url": "https://www.gtdhealthcare.co.uk/lindleymedicalpractice", "nearby": "Lindley Medical Practice, Mossley Medical Practice", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 722, "survey_sent_back": 129, "registered_patient_count": 4895}, {"code": "P89612", "name": "Mossley Medical Practice", "lat": 53.514, "lon": -2.04062, "postcode": "OL5 9AB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 3.7, "google_count": 16, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89612-mossley-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mossley-medical-practice/P89612", "gtd_url": "https://www.gtdhealthcare.co.uk/mossleymedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 423, "survey_sent_back": 95, "registered_patient_count": 2197}, {"code": "P89011", "name": "Gordon Street Medical Centre", "lat": 53.4929, "lon": -2.07804, "postcode": "OL6 6NE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.5, "google_count": 86, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89011-gordon-street-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/gordon-street-medical-centre/P89011", "gtd_url": "https://www.gtdhealthcare.co.uk/gordonstreetmedicalcentre", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 61, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 517, "survey_sent_back": 113, "registered_patient_count": 5181}, {"code": "Y02586", "name": "Ashton Gp Service", "lat": 53.4858, "lon": -2.09997, "postcode": "OL6 7SR", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 91, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02586-ashton-gp-service.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ashton-gp-service/Y02586", "gtd_url": "https://www.gtdhealthcare.co.uk/ashtongpservice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 52, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 569, "survey_sent_back": 88, "registered_patient_count": 5171}, {"code": "P89013", "name": "Hattersley Group Practice", "lat": 53.4502, "lon": -2.02741, "postcode": "SK14 3EH", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 72, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89013-hattersley-group-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/hattersley-group-practice/P89013", "gtd_url": "https://www.gtdhealthcare.co.uk/hattersleygrouppractice", "nearby": "Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 41, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 531, "survey_sent_back": 117, "registered_patient_count": 5011}, {"code": "P89602", "name": "The Smithy Surgery", "lat": 53.4611, "lon": -1.99579, "postcode": "SK14 8LJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.0, "google_count": 23, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89602-the-smithy-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-smithy-surgery/P89602", "gtd_url": "https://www.gtdhealthcare.co.uk/thesmithysurgery", "nearby": "Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 78, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 364, "survey_sent_back": 109, "registered_patient_count": 3747}, {"code": "Y02936", "name": "Millbrook Medical Practice", "lat": 53.4923, "lon": -2.03427, "postcode": "SK15 3BJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.7, "google_count": 39, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02936-millbrook-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/millbrook-medical-practice/Y02936", "gtd_url": "https://www.gtdhealthcare.co.uk/millbrookmedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 565, "survey_sent_back": 111, "registered_patient_count": 3505}, {"code": "P82013001", "name": "Dr Y Loomba & Partner", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.0, "google_count": 10, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82013001-dr-y-loomba-and-partner.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-y-loomba-and-partner/P82013001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82012", "name": "Octagon Medical Centre", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 308, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82012-octagon-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/octagon-medical-centre/P82012", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 24, "survey_sent_out": 665, "survey_sent_back": 161, "registered_patient_count": 6254}, {"code": "P82022", "name": "Dr Rizwan and Dr Awan", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.7, "google_count": 6, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82022-dr-rizwan-and-dr-awan.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-rizwan-and-dr-awan/P82022", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 535, "survey_sent_back": 115, "registered_patient_count": 5594}, {"code": "P82029", "name": "Halliwell Surgery 2", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82029-halliwell-surgery-2.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-2/P82029", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 96, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 530, "survey_sent_back": 110, "registered_patient_count": 3586}, {"code": "P82626", "name": "Halliwell Surgery 3", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82626-halliwell-surgery-3.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-3/P82626", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 82, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 653, "survey_sent_back": 121, "registered_patient_count": 5173}, {"code": "P82634", "name": "Wyresdale Road Surgery", "lat": 53.5816, "lon": -2.45218, "postcode": "BL1 4DN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 9, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634-wyresdale-road-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/wyresdale-road-surgery/P82634", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 558, "survey_sent_back": 107, "registered_patient_count": 3995}, {"code": "P82010", "name": "Dalefield Surgery", "lat": 53.5882, "lon": -2.4518, "postcode": "BL1 4JP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dalefield-surgery/P82010", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 494, "survey_sent_back": 109, "registered_patient_count": 7962}, {"code": "Y02319", "name": "Bolton General Practice", "lat": 53.5782, "lon": -2.43495, "postcode": "BL1 4TH", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 1.8, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-general-practice/Y02319", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 65, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 845, "survey_sent_back": 148, "registered_patient_count": 7694}, {"code": "P82031", "name": "Heaton Medical Centre", "lat": 53.588, "lon": -2.46831, "postcode": "BL1 5PU", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/heaton-medical-centre/P82031", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 393, "survey_sent_back": 116, "registered_patient_count": 10727}, {"code": "P82014", "name": "Spring House Surgery", "lat": 53.5884, "lon": -2.46354, "postcode": "BL1 6AF", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.1, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/spring-house-surgery/P82014", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 6457}, {"code": "P82627", "name": "Cornerstone Surgery", "lat": 53.5887, "lon": -2.45916, "postcode": "BL1 6AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 41, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82627-cornerstone-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/cornerstone-surgery/P82627", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 414, "survey_sent_back": 105, "registered_patient_count": 4230}, {"code": "P82023", "name": "Mandalay Medical Centre", "lat": 53.6106, "lon": -2.4321, "postcode": "BL1 7LR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mandalay-medical-centre/P82023", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 8580}, {"code": "P82634001", "name": "Drs Karim & James-Authe", "lat": 53.596, "lon": -2.45072, "postcode": "BL1 8BZ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.5, "google_count": 19, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634001-drs-karim-and-james-authe.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/drs-karim-and-james-authe/P82634001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "Y03079", "name": "Bolton Community Practice", "lat": 53.5963, "lon": -2.43067, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 4, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-community-practice/Y03079", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 530, "survey_sent_back": 133, "registered_patient_count": 16122}, {"code": "P82025", "name": "Burnside Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "ehealthservice.co.uk", "affiliated_group": "", "google_score": 1.8, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/burnside-surgery/P82025", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 467, "survey_sent_back": 99, "registered_patient_count": 4423}, {"code": "P82625", "name": "Charlotte Street Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.3, "google_count": 33, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlotte-street-surgery/P82625", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 8, "survey_sent_out": 936, "survey_sent_back": 76, "registered_patient_count": 2356}, {"code": "P82607", "name": "Crompton View Surgery", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 7, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82607-crompton-view-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/crompton-view-surgery/P82607", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 89, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 450, "survey_sent_back": 137, "registered_patient_count": 6045}, {"code": "P82021", "name": "The Oaks Family Practice", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.9, "google_count": 33, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82021-the-oaks-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-oaks-family-practice/P82021", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 88, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 412, "survey_sent_back": 136, "registered_patient_count": 6964}, {"code": "P82033", "name": "Bradford Street Surgery", "lat": 53.5768, "lon": -2.41821, "postcode": "BL2 1HT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.8, "google_count": 4, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82033-bradford-street-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bradford-street-surgery/P82033", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 586, "survey_sent_back": 129, "registered_patient_count": 1996}, {"code": "P82016001", "name": "Tonge Moor Health Centre", "lat": 53.5891, "lon": -2.40904, "postcode": "BL2 2LW", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-moor-health-centre/P82016001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82016", "name": "Harwood Medical Centre", "lat": 53.6041, "lon": -2.39814, "postcode": "BL2 3HQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.2, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/harwood-medical-centre/P82016", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 32, "survey_sent_out": 374, "survey_sent_back": 119, "registered_patient_count": 12086}, {"code": "P82011", "name": "Tonge Fold Health Centre", "lat": 53.5795, "lon": -2.40532, "postcode": "BL2 6DY", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 42, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82011-tonge-fold-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-fold-health-centre/P82011", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 90, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 397, "survey_sent_back": 130, "registered_patient_count": 6969}, {"code": "P82018", "name": "The Alastair Ross Medical Practice", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 60, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82018-the-alastair-ross-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-alastair-ross-medical-practice/P82018", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 541, "survey_sent_back": 121, "registered_patient_count": 7491}, {"code": "P82001", "name": "The Dunstan Partnership", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 59, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82001-the-dunstan-partnership.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-dunstan-partnership/P82001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 27, "survey_sent_out": 428, "survey_sent_back": 114, "registered_patient_count": 10157}, {"code": "Y03079003", "name": "Little Lever Health Centre & Library", "lat": 53.5623, "lon": -2.37194, "postcode": "BL3 1HH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 2, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y03079003-little-lever-health-centre-and-library.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/little-lever-health-centre-and-library/Y03079003", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82020", "name": "Little Lever Health Centre 1", "lat": 53.5623, "lon": -2.37194, "postcode": "BL3 1HH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 2, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82020-little-lever-health-centre-1.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/little-lever-health-centre-1/P82020", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 667, "survey_sent_back": 113, "registered_patient_count": 4820}, {"code": "P82036", "name": "Little Lever Health Centre 2", "lat": 53.5593, "lon": -2.37105, "postcode": "BL3 1HH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.2, "google_count": 25, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82036-little-lever-health-centre-2.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/little-lever-health-centre-2/P82036", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 27, "survey_sent_out": 503, "survey_sent_back": 138, "registered_patient_count": 2852}, {"code": "P82613", "name": "Spring View Medical Centre", "lat": 53.5608, "lon": -2.36973, "postcode": "BL3 1HQ", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 4.1, "google_count": 216, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82613-spring-view-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/spring-view-medical-centre/P82613", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 503, "survey_sent_back": 125, "registered_patient_count": 5178}, {"code": "P82009001", "name": "Southbrook Surgery", "lat": 53.5612, "lon": -2.4269, "postcode": "BL3 2DN", "gtd": false, "management_company": "ehealthservice.co.uk", "affiliated_group": "", "google_score": 3.4, "google_count": 12, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82009001-southbrook-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/southbrook-surgery/P82009001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82616", "name": "Beehive Surgery", "lat": 53.5642, "lon": -2.41916, "postcode": "BL3 2JR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.3, "google_count": 101, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82616-beehive-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/beehive-surgery/P82616", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 58, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 779, "survey_sent_back": 125, "registered_patient_count": 3919}, {"code": "P82609", "name": "Shanti Medical Centre", "lat": 53.5634, "lon": -2.45144, "postcode": "BL3 3PH", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 4.2, "google_count": 806, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82609-shanti-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/shanti-medical-centre/P82609", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 61, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 13, "survey_sent_out": 859, "survey_sent_back": 115, "registered_patient_count": 6335}, {"code": "P82009", "name": "St Helens Road Practice", "lat": 53.5596, "lon": -2.45783, "postcode": "BL3 3RR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.2, "google_count": 34, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82009-st-helens-road-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/st-helens-road-practice/P82009", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 412, "survey_sent_back": 104, "registered_patient_count": 7928}, {"code": "P82660", "name": "Deane Clinic 1", "lat": 53.5678, "lon": -2.46443, "postcode": "BL3 4LU", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 85, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82660-deane-clinic-1.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/deane-clinic-1/P82660", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 13, "survey_sent_out": 635, "survey_sent_back": 82, "registered_patient_count": 3615}, {"code": "Y03079001", "name": "Bolton Community Practice CIC - Ladybridge Surgery", "lat": 53.5704, "lon": -2.47649, "postcode": "BL3 4PZ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 23, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y03079001-bolton-community-practice-cic-ladybridge-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-community-practice-cic-ladybridge-surgery/Y03079001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82030", "name": "Deane Medical Centre", "lat": 53.5727, "lon": -2.44197, "postcode": "BL3 5AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.8, "google_count": 45, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82030-deane-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/deane-medical-centre/P82030", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 957, "survey_sent_back": 115, "registered_patient_count": 4010}, {"code": "P82030001", "name": "Deane Surgery", "lat": 53.5727, "lon": -2.44197, "postcode": "BL3 5AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.7, "google_count": 3, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82030001-deane-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/deane-surgery/P82030001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "Y00186", "name": "3D Medical Centre", "lat": 53.573, "lon": -2.444, "postcode": "BL3 5DP", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 4.1, "google_count": 84, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y00186-3d-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/3d-medical-centre/Y00186", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 48, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 9, "survey_sent_out": 915, "survey_sent_back": 78, "registered_patient_count": 1663}, {"code": "P82640", "name": "AL Fal Medical Group", "lat": 53.5727, "lon": -2.44633, "postcode": "BL3 5HP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.9, "google_count": 58, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82640-al-fal-medical-group.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/al-fal-medical-group/P82640", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 65, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 11, "survey_sent_out": 924, "survey_sent_back": 99, "registered_patient_count": 5082}, {"code": "P82629", "name": "Dr S Naseef", "lat": 53.5729, "lon": -2.4457, "postcode": "BL3 5HP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.8, "google_count": 26, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82629-dr-s-naseef.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-s-naseef/P82629", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 88, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 546, "survey_sent_back": 116, "registered_patient_count": 2036}, {"code": "Y03366", "name": "Olive Family Practice", "lat": 53.5727, "lon": -2.44633, "postcode": "BL3 5HP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.5, "google_count": 34, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y03366-olive-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/olive-family-practice/Y03366", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 913, "survey_sent_back": 139, "registered_patient_count": 5653}, {"code": "P82002", "name": "Pikes Lane 1", "lat": 53.5727, "lon": -2.44633, "postcode": "BL3 5HP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 51, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82002-pikes-lane-1.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/pikes-lane-1/P82002", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 71, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 466, "survey_sent_back": 108, "registered_patient_count": 7222}, {"code": "P82624", "name": "Orient House Medical Centre", "lat": 53.5688, "lon": -2.46058, "postcode": "BL3 5QE", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 20, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82624-orient-house-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/orient-house-medical-centre/P82624", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 651, "survey_sent_back": 115, "registered_patient_count": 3553}, {"code": "Y02790", "name": "Bolton Medical Centre", "lat": 53.5655, "lon": -2.43143, "postcode": "BL3 6PY", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 4.0, "google_count": 564, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02790-bolton-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-medical-centre/Y02790", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 64, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 826, "survey_sent_back": 102, "registered_patient_count": 7652}, {"code": "P82633", "name": "Great Lever One", "lat": 53.5656, "lon": -2.43243, "postcode": "BL3 6RN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.9, "google_count": 84, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82633-great-lever-one.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/great-lever-one/P82633", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 786, "survey_sent_back": 115, "registered_patient_count": 2527}, {"code": "P82013", "name": "The Bolton Family Practice", "lat": 53.5656, "lon": -2.43243, "postcode": "BL3 6RN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 564, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-bolton-family-practice/P82013", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 680, "survey_sent_back": 124, "registered_patient_count": 3964}, {"code": "P82004", "name": "Swan Lane Medical Centre", "lat": 53.5669, "lon": -2.44238, "postcode": "BL3 6TL", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.3, "google_count": 61, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82004-swan-lane-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/swan-lane-medical-centre/P82004", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 624, "survey_sent_back": 104, "registered_patient_count": 9727}, {"code": "P82008001", "name": "Highfield Surgery", "lat": 53.5466, "lon": -2.42743, "postcode": "BL4 0NX", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 6, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82008001-highfield-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/highfield-surgery/P82008001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82007", "name": "Kearsley Medical Centre", "lat": 53.5432, "lon": -2.38282, "postcode": "BL4 8EP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 109, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82007-kearsley-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/kearsley-medical-centre/P82007", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 431, "survey_sent_back": 100, "registered_patient_count": 13287}, {"code": "P82652", "name": "Farnworth Family Practice", "lat": 53.5461, "lon": -2.39774, "postcode": "BL4 9AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.2, "google_count": 30, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82652-farnworth-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/farnworth-family-practice/P82652", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 87, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 598, "survey_sent_back": 113, "registered_patient_count": 4365}, {"code": "P82037", "name": "Fig Tree Medical Practice", "lat": 53.5461, "lon": -2.39774, "postcode": "BL4 9AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.5, "google_count": 10, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82037-fig-tree-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/fig-tree-medical-practice/P82037", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 89, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 24, "survey_sent_out": 556, "survey_sent_back": 136, "registered_patient_count": 4863}, {"code": "P82008", "name": "STONEHILL MEDICAL CENTRE", "lat": 53.5436, "lon": -2.40243, "postcode": "BL4 9QZ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.3, "google_count": 163, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82008-stonehill-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/stonehill-medical-centre/P82008", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 82, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 475, "survey_sent_back": 111, "registered_patient_count": 14880}, {"code": "Y03079002", "name": "Bolton Community Practice CIC - The Market Surgery", "lat": 53.5983, "lon": -2.54254, "postcode": "BL6 5PY", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 40, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y03079002-bolton-community-practice-cic-the-market-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-community-practice-cic-the-market-surgery/Y03079002", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P83017", "name": "Woodbank Surgery", "lat": 53.6051, "lon": -2.30879, "postcode": "BL8 1EG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.6, "google_count": 105, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83017-woodbank-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/woodbank-surgery/P83017", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 26, "survey_sent_out": 469, "survey_sent_back": 124, "registered_patient_count": 7012}, {"code": "P83612", "name": "Mile Lane Health Centre", "lat": 53.5878, "lon": -2.33523, "postcode": "BL8 2JR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 47, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83612-mile-lane-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mile-lane-health-centre/P83612", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 35, "survey_sent_out": 400, "survey_sent_back": 139, "registered_patient_count": 5421}, {"code": "P83012", "name": "Tower Family Healthcare", "lat": 53.6148, "lon": -2.34143, "postcode": "BL8 4AD", "gtd": false, "management_company": "Tower Family Healthcare", "affiliated_group": "", "google_score": 2.5, "google_count": 59, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83012-tower-family-healthcare.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tower-family-healthcare/P83012", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 32, "survey_sent_out": 373, "survey_sent_back": 120, "registered_patient_count": 48295}, {"code": "P83012002", "name": "Tower Family Healthcare - Greenmount", "lat": 53.6245, "lon": -2.33605, "postcode": "BL8 4DR", "gtd": false, "management_company": "Tower Family Healthcare", "affiliated_group": "", "google_score": 2.0, "google_count": 63, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83012002-tower-family-healthcare-greenmount.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tower-family-healthcare-greenmount/P83012002", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "Y02755", "name": "Rock Healthcare Limited", "lat": 53.5955, "lon": -2.28858, "postcode": "BL9 0NJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.7, "google_count": 155, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02755-rock-healthcare-limited.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/rock-healthcare-limited/Y02755", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 57, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 622, "survey_sent_back": 128, "registered_patient_count": 9553}, {"code": "W4J3Q", "name": "Tower Family Healthcare Minden", "lat": 53.5955, "lon": -2.28858, "postcode": "BL9 0NJ", "gtd": false, "management_company": "Tower Family Healthcare", "affiliated_group": "", "google_score": 2.4, "google_count": 86, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/W4J3Q-tower-family-healthcare-minden.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tower-family-healthcare-minden/W4J3Q", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P83021", "name": "Peel GPs", "lat": 53.5903, "lon": -2.29897, "postcode": "BL9 0SN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.9, "google_count": 101, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83021-peel-gps.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/peel-gps/P83021", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 460, "survey_sent_back": 116, "registered_patient_count": 9873}, {"code": "P83015", "name": "Ribblesdale Medical Practice", "lat": 53.5903, "lon": -2.29897, "postcode": "BL9 0SN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 62, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83015-ribblesdale-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ribblesdale-medical-practice/P83015", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 378, "survey_sent_back": 126, "registered_patient_count": 7442}, {"code": "P83005", "name": "Townside Surgery", "lat": 53.5903, "lon": -2.29897, "postcode": "BL9 0SN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.4, "google_count": 28, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83005-townside-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/townside-surgery/P83005", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 86, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 401, "survey_sent_back": 136, "registered_patient_count": 4568}, {"code": "P83024", "name": "Knowsley Medical Centre", "lat": 53.5885, "lon": -2.3006, "postcode": "BL9 0ST", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 49, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83024-knowsley-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/knowsley-medical-centre/P83024", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 557, "survey_sent_back": 112, "registered_patient_count": 4579}, {"code": "P83611", "name": "Walmersley Road Medical Practice", "lat": 53.5999, "lon": -2.28954, "postcode": "BL9 6DX", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 42, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83611-walmersley-road-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/walmersley-road-medical-practice/P83611", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 76, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 731, "survey_sent_back": 106, "registered_patient_count": 4719}, {"code": "P83621", "name": "Huntley Mount Medical Centre", "lat": 53.6002, "lon": -2.27857, "postcode": "BL9 6JA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 67, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83621-huntley-mount-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/huntley-mount-medical-centre/P83621", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 516, "survey_sent_back": 127, "registered_patient_count": 2878}, {"code": "P83011", "name": "Unsworth Medical Centre", "lat": 53.5607, "lon": -2.27308, "postcode": "BL9 8JR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 59, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83011-unsworth-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/unsworth-medical-centre/P83011", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 76, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 355, "survey_sent_back": 106, "registered_patient_count": 7397}, {"code": "P83009", "name": "Blackford House Medical Centre", "lat": 53.5742, "lon": -2.2834, "postcode": "BL9 8QA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.3, "google_count": 53, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P83009-blackford-house-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/blackford-house-medical-centre/P83009", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 88, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 39, "survey_sent_out": 340, "survey_sent_back": 131, "registered_patient_count": 7591}, {"code": "P84683", "name": "THE Doc's Surgery", "lat": 53.4768, "lon": -2.23827, "postcode": "M1 3LY", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.8, "google_count": 366, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-doc-s-surgery/P84683", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 9, "survey_sent_out": 912, "survey_sent_back": 84, "registered_patient_count": 14745}, {"code": "P84059", "name": "Lime Square Medical Centre", "lat": 53.4737, "lon": -2.16489, "postcode": "M11 1DA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.2, "google_count": 143, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84059-lime-square-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/lime-square-medical-centre/P84059", "gtd_url": "", "nearby": "Ashton GP Service, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 64, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 531, "survey_sent_back": 114, "registered_patient_count": 9094}, {"code": "P84042", "name": "Florence House Medical Practice", "lat": 53.4726, "lon": -2.16202, "postcode": "M11 1JG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.4, "google_count": 160, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/florence-house-medical-practice/P84042", "gtd_url": "", "nearby": "Ashton GP Service, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 538, "survey_sent_back": 132, "registered_patient_count": 11033}, {"code": "P84041", "name": "Cornerstone Family Practice", "lat": 53.4744, "lon": -2.19508, "postcode": "M11 3AA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.5, "google_count": 88, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84041-cornerstone-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/cornerstone-family-practice/P84041", "gtd_url": "", "nearby": "City Health Centre, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 81, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 636, "survey_sent_back": 126, "registered_patient_count": 7642}, {"code": "P84004", "name": "Five Oaks Family Practice", "lat": 53.4757, "lon": -2.19446, "postcode": "M11 3BB", "gtd": false, "management_company": "", "affiliated_group": "Northern Health GPPO Limited", "google_score": 2.9, "google_count": 96, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84004-five-oaks-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/five-oaks-family-practice/P84004", "gtd_url": "", "nearby": "City Health Centre, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 88, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 540, "survey_sent_back": 97, "registered_patient_count": 8636}, {"code": "P84637", "name": "Dr Khan's Practice", "lat": 53.4843, "lon": -2.18414, "postcode": "M11 4EJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.3, "google_count": 20, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84637-dr-khans-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-khan-s-practice/P84637", "gtd_url": "", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 94, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 546, "survey_sent_back": 111, "registered_patient_count": 2945}, {"code": "P84032", "name": "Drs Hanif & Bannuru", "lat": 53.4843, "lon": -2.18414, "postcode": "M11 4EJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.9, "google_count": 7, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/drs-hanif-and-bannuru/P84032", "gtd_url": "", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 26, "survey_sent_out": 525, "survey_sent_back": 136, "registered_patient_count": 5920}, {"code": "P84051", "name": "Eastlands Medical Centre", "lat": 53.4843, "lon": -2.18414, "postcode": "M11 4EJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.2, "google_count": 62, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84051-eastlands-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/eastlands-medical-centre/P84051", "gtd_url": "", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 496, "survey_sent_back": 93, "registered_patient_count": 5662}, {"code": "P84052", "name": "West Gorton Medical Practice", "lat": 53.467, "lon": -2.20424, "postcode": "M12 5JE", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.3, "google_count": 106, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84052-west-gorton-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/west-gorton-medical-practice/P84052", "gtd_url": "", "nearby": "City Health Centre, Droylsden Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 569, "survey_sent_back": 119, "registered_patient_count": 7681}, {"code": "P84644", "name": "Parkside Surgery", "lat": 53.4532, "lon": -2.19083, "postcode": "M12 5RU", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 137, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84644-parkside-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/parkside-surgery/P84644", "gtd_url": "", "nearby": "Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 11, "survey_sent_out": 922, "survey_sent_back": 97, "registered_patient_count": 7230}, {"code": "P84689", "name": "Manchester Integrative Medical Practice", "lat": 53.4576, "lon": -2.20187, "postcode": "M13 0RR", "gtd": false, "management_company": "Manchester Integrative Medical Practice", "affiliated_group": "", "google_score": 4.8, "google_count": 550, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84689-manchester-integrative-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/manchester-integrative-medical-practice/P84689", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 982, "survey_sent_back": 115, "registered_patient_count": 14205}, {"code": "P84026", "name": "Dickenson Road Medical Centre", "lat": 53.4561, "lon": -2.20227, "postcode": "M13 0WQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 175, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84026-dickenson-road-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dickenson-road-medical-centre/P84026", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 984, "survey_sent_back": 101, "registered_patient_count": 9751}, {"code": "P84009", "name": "Ailsa Craig Medical Centre", "lat": 53.4542, "lon": -2.20853, "postcode": "M13 0YL", "gtd": false, "management_company": "", "affiliated_group": "Primary Care Manchester Ltd", "google_score": 3.8, "google_count": 288, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84009-ailsa-craig-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ailsa-craig-medical-centre/P84009", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 78, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 13, "survey_sent_out": 910, "survey_sent_back": 115, "registered_patient_count": 11005}, {"code": "P84037", "name": "Ardwick Medical Practice", "lat": 53.4698, "lon": -2.22453, "postcode": "M13 9UJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.5, "google_count": 172, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84037-ardwick-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ardwick-medical-practice/P84037", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 66, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 990, "survey_sent_back": 121, "registered_patient_count": 5871}, {"code": "P84611", "name": "Brunswick Medical Practice", "lat": 53.4698, "lon": -2.22453, "postcode": "M13 9UJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.5, "google_count": 172, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84611-brunswick-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/brunswick-medical-practice/P84611", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 90, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 875, "survey_sent_back": 102, "registered_patient_count": 7589}, {"code": "P84005", "name": "Vallance Medical", "lat": 53.4698, "lon": -2.22453, "postcode": "M13 9UJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.8, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84005-vallance-medical.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/vallance-medical/P84005", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 5, "survey_sent_out": 886, "survey_sent_back": 44, "registered_patient_count": 15999}, {"code": "V6E6I", "name": "Manchester Integrative Medical Practice at Moss Side Health Centre", "lat": 53.4588, "lon": -2.23744, "postcode": "M14 4GP", "gtd": false, "management_company": "Manchester Integrative Medical Practice", "affiliated_group": "", "google_score": 4.8, "google_count": 550, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/V6E6I-manchester-integrative-medical-practice-at-moss-side-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/manchester-integrative-medical-practice-at-moss-side-health-centre/V6E6I", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P84023", "name": "Surrey Lodge Practice", "lat": 53.4574, "lon": -2.21735, "postcode": "M14 5BY", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.8, "google_count": 115, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84023-surrey-lodge-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/surrey-lodge-practice/P84023", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 86, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 954, "survey_sent_back": 112, "registered_patient_count": 9711}, {"code": "P84626", "name": "Wilmslow Road Surgery", "lat": 53.4522, "lon": -2.22281, "postcode": "M14 5LQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.9, "google_count": 117, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/wilmslow-road-surgery/P84626", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 68, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 967, "survey_sent_back": 97, "registered_patient_count": 5641}, {"code": "P84072", "name": "The Robert Darbishire Practice", "lat": 53.455, "lon": -2.22631, "postcode": "M14 5NP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 267, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84072-the-robert-darbishire-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-robert-darbishire-practice/P84072", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 6, "survey_sent_out": 973, "survey_sent_back": 63, "registered_patient_count": 34920}, {"code": "Y02890", "name": "Hawthorn MC", "lat": 53.4423, "lon": -2.20459, "postcode": "M14 6FS", "gtd": false, "management_company": "Hope Citadel Healthcare", "affiliated_group": "", "google_score": 3.0, "google_count": 300, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/Y02890-hawthorn-mc.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/hawthorn-mc/Y02890", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 13, "survey_sent_out": 814, "survey_sent_back": 103, "registered_patient_count": 6507}, {"code": "P84018", "name": "Mauldeth Medical Centre", "lat": 53.4348, "lon": -2.21341, "postcode": "M14 6SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.8, "google_count": 39, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84018-mauldeth-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mauldeth-medical-centre/P84018", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 929, "survey_sent_back": 97, "registered_patient_count": 3792}, {"code": "P84035", "name": "Bodey Medical Centre", "lat": 53.4406, "lon": -2.21478, "postcode": "M14 6WP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.2, "google_count": 179, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bodey-medical-centre/P84035", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 85, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 785, "survey_sent_back": 129, "registered_patient_count": 16410}, {"code": "P84639", "name": "Fallowfield Medical Centre", "lat": 53.4388, "lon": -2.21349, "postcode": "M14 6YL", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.8, "google_count": 96, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84639-fallowfield-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/fallowfield-medical-centre/P84639", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 950, "survey_sent_back": 91, "registered_patient_count": 3046}, {"code": "P84669", "name": "Cornbrook Medical Practice", "lat": 53.4681, "lon": -2.25986, "postcode": "M15 4EA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.1, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/cornbrook-medical-practice/P84669", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 913, "survey_sent_back": 90, "registered_patient_count": 18195}, {"code": "P84630", "name": "The Arch Medical Practice", "lat": 53.4677, "lon": -2.2496, "postcode": "M15 5TJ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 232, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84630-the-arch-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-arch-medical-practice/P84630", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 87, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 7, "survey_sent_out": 969, "survey_sent_back": 71, "registered_patient_count": 24647}, {"code": "P84669001", "name": "Cornbrook Medical Practice - Boundary Surgery", "lat": 53.4669, "lon": -2.23964, "postcode": "M15 6PR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 129, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/cornbrook-medical-practice-boundary-surgery/P84669001", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P91629001", "name": "North Trafford Group Practice", "lat": 53.4581, "lon": -2.27564, "postcode": "M16 0LW", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.6, "google_count": 1368, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P91629001-north-trafford-group-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/north-trafford-group-practice/P91629001", "gtd_url": "", "nearby": "City Health Centre", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P84635", "name": "The Whitswood Practice", "lat": 53.4555, "lon": -2.25363, "postcode": "M16 7AP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.6, "google_count": 72, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84635-the-whitswood-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-whitswood-practice/P84635", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 82, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 742, "survey_sent_back": 91, "registered_patient_count": 5219}, {"code": "P84039", "name": "The Range Medical Centre", "lat": 53.4523, "lon": -2.25705, "postcode": "M16 8EE", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.6, "google_count": 1368, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84039-the-range-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-range-medical-centre/P84039", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 636, "survey_sent_back": 99, "registered_patient_count": 14480}, {"code": "P84650", "name": "The Alexandra Practice", "lat": 53.4431, "lon": -2.25573, "postcode": "M16 8NG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.6, "google_count": 379, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-alexandra-practice/P84650", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 568, "survey_sent_back": 129, "registered_patient_count": 6106}, {"code": "P91020", "name": "Limelight Health and Wellbeing Hub", "lat": 53.4614, "lon": -2.26196, "postcode": "M16 9NW", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.4, "google_count": 156, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P91020-limelight-health-and-wellbeing-hub.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/limelight-health-and-wellbeing-hub/P91020", "gtd_url": "", "nearby": "City Health Centre, New Bank Health Centre", "survey_overall_good_percent": 71, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 14, "survey_sent_out": 660, "survey_sent_back": 93, "registered_patient_count": 9233}, {"code": "P84038", "name": "Ashville Surgery", "lat": 53.4525, "lon": -2.26803, "postcode": "M16 9RT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.4, "google_count": 323, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84038-ashville-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ashville-surgery/P84038", "gtd_url": "", "nearby": "City Health Centre", "survey_overall_good_percent": 81, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 487, "survey_sent_back": 113, "registered_patient_count": 13665}, {"code": "P84050", "name": "Mount Road Surgery", "lat": 53.4598, "lon": -2.18139, "postcode": "M18 7BQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.5, "google_count": 80, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84050-mount-road-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mount-road-surgery/P84050", "gtd_url": "", "nearby": "Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 559, "survey_sent_back": 108, "registered_patient_count": 7935}, {"code": "P84028", "name": "Gorton Medical Centre", "lat": 53.4622, "lon": -2.17587, "postcode": "M18 8HE", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.1, "google_count": 164, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84028-gorton-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/gorton-medical-centre/P84028", "gtd_url": "", "nearby": "Ashton GP Service, Droylsden Medical Practice, Guide Bridge Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 528, "survey_sent_back": 115, "registered_patient_count": 10727}, {"code": "P84022", "name": "Kingsway Medical Practice", "lat": 53.4203, "lon": -2.21246, "postcode": "M19 1UG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.4, "google_count": 98, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/kingsway-medical-practice/P84022", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 55, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 26, "survey_sent_out": 473, "survey_sent_back": 124, "registered_patient_count": 6162}, {"code": "P84027", "name": "West Point Medical Centre", "lat": 53.446, "lon": -2.19757, "postcode": "M19 2AF", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.4, "google_count": 149, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84027-west-point-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/west-point-medical-centre/P84027", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 586, "survey_sent_back": 106, "registered_patient_count": 8270}, {"code": "P84053", "name": "Ashcroft Surgery", "lat": 53.4455, "lon": -2.19116, "postcode": "M19 3BS", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 87, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84053-ashcroft-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ashcroft-surgery/P84053", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 617, "survey_sent_back": 111, "registered_patient_count": 7814}, {"code": "P84016", "name": "Levenshulme Medical Practice", "lat": 53.4464, "lon": -2.18851, "postcode": "M19 3BX", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.4, "google_count": 183, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84016-levenshulme-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/levenshulme-medical-practice/P84016", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 76, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 550, "survey_sent_back": 112, "registered_patient_count": 9179}, {"code": "P84056", "name": "Princess Road Surgery", "lat": 53.4404, "lon": -2.24361, "postcode": "M20 1BH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.9, "google_count": 85, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84056-princess-road-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/princess-road-surgery/P84056", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 758, "survey_sent_back": 117, "registered_patient_count": 4317}, {"code": "P84010", "name": "The Borchardt Medical Centre", "lat": 53.4345, "lon": -2.23705, "postcode": "M20 1EB", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.6, "google_count": 172, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84010-the-borchardt-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-borchardt-medical-centre/P84010", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 515, "survey_sent_back": 108, "registered_patient_count": 10270}, {"code": "P84034", "name": "Barlow Medical Centre", "lat": 53.4132, "lon": -2.23142, "postcode": "M20 2RN", "gtd": false, "management_company": "", "affiliated_group": "South Manchester GP Federation Limited", "google_score": 3.7, "google_count": 234, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84034-barlow-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/barlow-medical-centre/P84034", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 86, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 26, "survey_sent_out": 469, "survey_sent_back": 122, "registered_patient_count": 16220}, {"code": "P84665", "name": "Withington Medical Practice", "lat": 53.4309, "lon": -2.22839, "postcode": "M20 4BA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.8, "google_count": 56, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84665-withington-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/withington-medical-practice/P84665", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 94, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 12, "survey_sent_out": 893, "survey_sent_back": 107, "registered_patient_count": 5228}, {"code": "P84017", "name": "LADYBARN GROUP PRACTICE", "lat": 53.4306, "lon": -2.21387, "postcode": "M20 4SS", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.8, "google_count": 368, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ladybarn-group-practice/P84017", "gtd_url": "", "nearby": "New Bank Health Centre", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 557, "survey_sent_back": 125, "registered_patient_count": 12641}, {"code": "P84678", "name": "Didsbury Medical Centre - Dr Whitaker", "lat": 53.4204, "lon": -2.2318, "postcode": "M20 6BA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 1, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/didsbury-medical-centre-dr-whitaker/P84678", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 24, "survey_sent_out": 454, "survey_sent_back": 107, "registered_patient_count": 15796}, {"code": "P84071", "name": "Wilbraham Surgery", "lat": 53.4423, "lon": -2.2715, "postcode": "M21 0UF", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.2, "google_count": 48, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84071-wilbraham-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/wilbraham-surgery/P84071", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 38, "survey_sent_out": 384, "survey_sent_back": 144, "registered_patient_count": 4557}, {"code": "P84066001", "name": "Merseybank Surgery", "lat": 53.4228, "lon": -2.263, "postcode": "M21 7NN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.3, "google_count": 14, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84066001-merseybank-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/merseybank-surgery/P84066001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P84066", "name": "David Medical Centre", "lat": 53.432, "lon": -2.26871, "postcode": "M21 8HA", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.4, "google_count": 80, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84066-david-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/david-medical-centre/P84066", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 78, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 535, "survey_sent_back": 91, "registered_patient_count": 7569}, {"code": "G3K4Y", "name": "Corkland Road Medical Practice", "lat": 53.4418, "lon": -2.27386, "postcode": "M21 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.5, "google_count": 91, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/G3K4Y-corkland-road-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/corkland-road-medical-practice/G3K4Y", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P84068", "name": "Chorlton Family Practice", "lat": 53.4438, "lon": -2.2797, "postcode": "M21 9NJ", "gtd": false, "management_company": "", "affiliated_group": "Primary Care Manchester Ltd", "google_score": 4.0, "google_count": 1039, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84068-chorlton-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/chorlton-family-practice/P84068", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 467, "survey_sent_back": 109, "registered_patient_count": 22115}, {"code": "P84048", "name": "Tregenna Group Practice", "lat": 53.3707, "lon": -2.25651, "postcode": "M22 0EP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.5, "google_count": 55, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P84048-tregenna-group-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tregenna-group-practice/P84048", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 609,
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn0file1 in your response to cite this file, or to surface it as a link.
# New Bank Health Centre – PPG Meeting 4 Goals
*(Prepared for meeting on 4 Feb 2026)* - Robert (Bob) Davies: admin@bobbigmac.com

## A. Key objective

**Make appointment access possible without requiring an unscheduled office-hours call.**

> It is currently **impossible** for some people to access appointments, mainly night workers, because of the mandatory office-hours unscheduled call.

This blocker has to be **circumventable** by design, not handled by special-casing individual patients.

## B. What has improved since November?

- **Admin requests on PATCHS are now open out of hours** (since **14 Jan 2026**). 
  - Good step, but it does not yet solve appointment access.

## C. Why the call requirement still blocks access

- A mandatory unscheduled call excludes people who cannot pick up in working hours (shift workers, carers, people at work, people without privacy/signal, some disabled patients).
- The website should allow **submit anytime, handled in-hours** for appointment requests to support patients who struggle to get web access in office-hours, or just to reduce procrastination. 
  - Many people handle 'admin' like healthcare in chunks when they can fit it in around work, and simply preventing them from starting the process at any time, is an access failure.
- If missed calls trigger closure or a “start again” loop, the process becomes not just inconvenient, but punitive.

PATCHS doesn't resolve the issue of appointment requests closing if 2 missed unscheduled calls.
  - Simple quality of life for patients: remove/solve the blocker OR make requests reopenable

**Questions:** 

1. Is the unscheduled call requirement intentional or an oversight?
  - Who decided this?
  - Can this change to include either a bookable-slot picker (available in PATCHS) or SMS round-trip via accurx?
  - If by design, what problem is it solving and is that more important than making it convenient for patients?

2. Is blocking appointment requests out of hours intentional or an oversight? 
  - Who decided this?
  - Can this change to 24hr availability?
  - If by design, what problem is it solving and is that more important than making it convenient for patients?

3. The patient survey has a very low response rate (10%), far below the national average (~25%). Why?

## D. Recent reviews

Nov 2025 to Jan 2026 has only a handful of new reviews. There are fewer severe flashpoints than previous months, and might suggest overall improvements, but the remaining issues are still clear.

- **Positive:** one reviewer says appointments have “always been good” for them.
- **Follow-up gaps:** tests/results not communicated.
- **Prescription process:** repeats rejected despite being on the system.
- **Appointment handling:** cancellation after a long wait; distress; no apology.
- **Staff attitude:** complaints of rudeness.
- **Continuity/expectations:** patient felt the appointment context wasn’t carried through.

## E. What success looks like

- A night worker can submit an appointment request out of hours and receive a text message or email response offering them an appointment
  - (ideally with a bookable slot picker, but a roundtrip would still be an improvement).
- No request is deleted because a patient missed an unscheduled call.
- Patients can use message/SMS (not just start on web, wait for phone call) for non-urgent coordination, with clear urgent-care signposting.

The repository is regularly updated: [https://github.com/bobbigmac/nhs-complaint-dec-2024](https://github.com/bobbigmac/nhs-complaint-dec-2024). 

Personal note: I've been complaining about this for 6 months under GTD Healthcare, with no change on this specific process. Initial escalation next-steps are outlined in the repository, but I'd prefer to see the process fixed at this practice (and reviewed for all GTD practices) than to turn it into yet another Healthwatch letter-writing campaign. I don't think the accessibility issue is disputed by staff (maybe I am just not communicating the issue clearly), but we do need to know if/when this will be fixed, and if not, why not?

#### Plugin (file_search):
Make sure to include fileciteturn0file2 in your response to cite this file, or to surface it as a link.
If we’re serious about making Britain healthier, “healthcare access exists in theory” isn’t a win. Access has to be *EASY* in practice—easier than most day-to-day admin—because it’s the one service people use when they’re already under strain.

The NHS (and politics/media around it) has drifted into a habit of treating patients as the problem: too complex, too busy, too late, too needy, too inconvenient. But people aren’t “failing the system” when they miss a call or can’t find time to resubmit a complicated form; the system is failing to fit human lives, and the people who resent that friction are turning to other means to express that frustration, while getting sicker. 

A missed appointment (or missed call) isn’t moral failure, it’s normal life: shift work, childcare, poor signal, anxiety, disability, depression, exhaustion, no privacy at work, no credit on the phone, no reliable device. Designing around the fantasy of perfect availability is designing for the healthiest, wealthiest, least-stressed people—and then acting surprised when the rest fall off.

What this looks like on the ground is friction-as-rationing: digital-only routes and punitive resets that push the cost of “efficiency” onto patients. 

At New Bank, the model of unscheduled callbacks plus deletion/reset after missed calls forces patients into a resubmission loop and strips them of control over access for reasons that are often outside their control. It also invites patient-blame by treating an unscheduled call like a “missed appointment” pushes patients to postpone even trying to get an appointment, if they know those missed calls would just waste somebody's time.

Even when you *measure* access, you can still hide the damage, because the people most excluded stop participating entirely. The local survey summary shows large minorities struggling to get through (by phone, website, or NHS App) and a quarter not knowing what happens next after contact—classic gateway failures. 

This matters more than nitpicking vendor choices: health is not restored by optimising the appointment form; it’s restored by removing the “tax” we charge people to even *ask* for help. The more you squeeze access, the more you concentrate harm onto the people already least able to bear it—those with unstable work, disability, caring duties, language barriers, low digital access, or chaotic lives. That doesn’t just feel unfair; it’s self-defeating. Delayed care turns treatable problems into crises, increases A&E pressure, reduces workforce participation, and entrenches long-term conditions.

So the standard should be blunt: first-contact healthcare must be resilient to real life. 

Systems should assume that missed calls happen, messages go unread, forms get abandoned, and people will try again later—not because they’re careless, but because they’re human. “Try again tomorrow from scratch” is not an access policy; it’s rationing access by inconvenience, and scolding patients, not supporting them.

In the early 2000s, the story is mostly: **the NHS has a duty to improve access and cut waits**, and government reports treat long waits and poor access as problems the service needs to fix with investment and better organisation.

> **2000–2004: “Make access faster and simpler” was the headline.** The Labour-era [*NHS Plan: A plan for investment, a plan for reform* (July 2000)](https://dera.ioe.ac.uk/id/eprint/4423/1/04055783.pdf) is basically a promise that the service will expand capacity and hit clear access targets (incl. the 4-hour A&E target), and Parliament explicitly frames later reforms as “delivering” that plan in the [*Health and Social Care Act 2001 – Explanatory Notes*](https://www.legislation.gov.uk/ukpga/2001/15/notes/division/2). The vibe is “we’ll make the system work better for you,” reinforced by contemporaneous commentary like [*The NHS Plan and clinicians* (Clin Med, 2002)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4952375/). Early “access by phone/online” experiments also land in this era: the [NAO report *NHS Direct in England* (2002)](https://www.nao.org.uk/reports/nhs-direct-in-england/) treats NHS Direct as a major access channel and evaluates who it reaches and what it achieves—already showing how “new access routes” can help some people while leaving others behind.

As the 2000s go on, you start seeing more **“route people to the right place”** work: phone and out-of-hours services, booking systems, and reforms meant to move patients through the system more smoothly. It’s still mainly framed as *system design* and *service accountability*, not “patients are the issue”.


> **2005–2009: move care into the community… but start tightening the system around targets, contracts, and compliance.** The big policy pitch is “care closer to home” and “focus on poorer communities,” stated outright in the White Paper [*Our health, our care, our say: a new direction for community services* (2006)](https://www.gov.uk/government/publications/our-health-our-care-our-say-a-new-direction-for-community-services). But the management logic gets sharper too: the NAO’s [*New contracts for general practice* (2008)](https://www.nao.org.uk/reports/new-contracts-for-general-practice/) is very “incentives, productivity, value for money” in tone, and the Darzi-era final report [*High quality care for all: NHS Next Stage Review* (2008)](https://www.gov.uk/government/publications/high-quality-care-for-all-nhs-next-stage-review-final-report) pushes measurement, standards, and service redesign. Government’s own follow-up, [*Response to the Health Select Committee report ‘NHS next stage review’* (March 2009)](https://www.gov.uk/government/publications/government-response-to-the-health-select-committee-report-nhs-next-stage-review-march-2009), keeps that “system improvement” framing, but you can feel the ground being prepared for a more rules-driven NHS.

**2009 is a key marker** because the NHS Constitution formally spells out not just patient rights, but also **patient “responsibilities”** (like keeping appointments and using services sensibly). That’s where “the public must do their bit” becomes more official, not just a vibe.

From **2010 into the early 2010s**, you can see a stronger shift toward **efficiency, demand control, and behaviour messaging**. Campaigns like “Choose Well” and lots of talk about “unnecessary” A&E or GP use become common. The implied message changes from “we’ll make access better” to “please stop using the wrong door”.


> **2010–2013: the “efficiency + reform” years, where responsibility starts getting nudged toward patients in public messaging.** Post-2010, the Coalition’s [*Equity and excellence: Liberating the NHS* (2010)](https://www.gov.uk/government/publications/equity-and-excellence-liberating-the-nhs) resets structures and doubles down on “value” language. Around the same time, the NHS formalises a more explicit “patient responsibilities” line: the [*NHS Constitution: The Handbook* (2015)](https://assets.publishing.service.gov.uk/media/5a749fa0ed915d6faf2b0f5a/NHS_Constitution_Handbook_v2.pdf) (building on earlier Constitution versions) spells out expectations like keeping appointments and following agreed treatment, and media coverage such as the Guardian’s [*Patients told to keep appointments under NHS constitution* (2009)](https://www.theguardian.com/society/2009/jan/21/patients-keep-appointments-nhs) shows how that lands publicly. Crucially, watchdogs also document that “patient choice” isn’t happening in a vacuum: the NAO’s [*Emergency admissions to hospital: managing the demand* (2013)](https://www.nao.org.uk/reports/emergency-admissions-to-hospital-managing-the-demand/) points to rising emergency pressure and weak alternatives as system problems—i.e., people ending up in the wrong place isn’t just “bad choices,” it’s often “bad routes.”


By **2013–2016**, the pressure story becomes constant: urgent care is overloaded, money is tight, and the system leans harder on schemes meant to **manage demand** (111, comms campaigns, rapid reviews of what messaging changes people’s choices). You also get big strategy docs that push “patients taking more control” — which can be positive, but can also slide into “you’re responsible for navigating the maze.”

> **2014–2016: the system openly accepts a demand–capacity gap, then leans harder on behaviour-shaping (“use the right service”) to cope.** The [*NHS Five Year Forward View* (Oct 2014)](https://www.england.nhs.uk/publication/nhs-five-year-forward-view/) is explicit that the NHS is facing widening gaps (health, care quality, funding) and needs new models of care; the “help patients self-manage / use the right channels” thread gets stronger as a practical response to overload. Oversight gaps in access routes show up too, in NAO’s [*Out-of-hours GP services in England* (2014)](https://www.nao.org.uk/reports/out-of-hours-gp-services-in-england/) (variable quality, variable commissioning grip). Then austerity-pressure evidence becomes harder to ignore: the NAO’s [*Financial sustainability of the NHS* (2016)](https://www.nao.org.uk/reports/financial-sustainability-of-the-nhs/) frames the funding/efficiency bind as structural, while public campaigns like NHS England’s [*“Stay Well This Winter” launch* (Oct 2015)](https://www.england.nhs.uk/2015/10/stay-well-this-winter/) push messages about where to go first (pharmacy/111 etc.)—helpful in parts, but also a cultural pivot toward “patients must route themselves correctly” to protect the system.

From **2017–2019**, the public-facing narrative gets sharper: winter campaigns and headlines focus on pressure and **“wasted appointments”**, often with the simplest explanation sitting front-and-centre: “people didn’t turn up” or “people went to A&E unnecessarily.” At the same time, watchdogs and committees also keep saying “many of these admissions are avoidable if care outside hospital works better,” which is a quieter but important counter-message: fix upstream access.


> **2017–2019: “missed appointments” becomes a moral story in headlines… while research says it’s a risk marker for deprivation and illness.** Public discourse crystallises with factoids like Full Fact’s explainer on [*GP appointments missed* (2017)](https://fullfact.org/health/gp-appointments-missed/) and the underlying NHS Digital stats on [*Appointments in General Practice (Oct 2018)*](https://digital.nhs.uk/data-and-information/publications/statistical/appointments-in-general-practice/october-2018). NHS England then amplifies the money framing via [*Missed GP appointments costing NHS millions* (Jan 2019)](https://www.england.nhs.uk/2019/01/missed-gp-appointments-costing-nhs-millions/), and clinicians push back on the implied blame: see [David Oliver’s *Missed GP appointments are no scandal* (BMJ, Feb 2019)](https://www.bmj.com/content/364/bmj.l545). Meanwhile, the strongest “don’t blame; treat as vulnerability” evidence base is Scottish-linked data: [*Morbidity, mortality and missed appointments…* (BMC Medicine, 2019)](https://bmcmedicine.biomedcentral.com/articles/10.1186/s12916-018-1234-0) finds missed appointments correlate with worse outcomes and higher mortality risk—this is not “people being pricks,” it’s often “people drowning.” In the same year, the system’s strategic story becomes “digital front door + prevention,” in [*The NHS Long Term Plan* (Jan 2019)](https://www.england.nhs.uk/publication/the-nhs-long-term-plan/) and the government announcement [*NHS Long Term Plan launched* (DHSC, Jan 2019)](https://www.gov.uk/government/news/nhs-long-term-plan-launched)—which sits awkwardly beside warnings about austerity/inequality like [*The NHS long term plan and public health* (BMJ, 2019)](https://www.bmj.com/content/364/bmj.l218).

**2020–2022** accelerates the channel shift. The pandemic makes remote triage and online routing feel normal overnight, and afterwards the system is left with massive backlogs plus a stronger habit of “go digital first” pathways. That’s where access problems can turn into exclusion problems if you’re not equipped to play the new game.

From **2023 onward**, there’s a visible attempt (in at least some NHS guidance) to stop treating missed appointments as a moral failure and treat them more like **a process problem and sometimes a risk signal** (follow up differently, reduce friction, design services that people can actually use). Meanwhile, the pressure narrative hasn’t gone away, and public comms still often defaults to “right service” nudges.

By **2025**, you’ve got two things happening at once: (1) continued financial/pressure framing and the “use services wisely” drumbeat, and (2) a new long-term plan that tries to reshape the system, including pushing “analogue to digital.” Whether that becomes “easier for everyone” or “patients carry more burden” depends on whether access and inclusion are treated as non-negotiable, not optional extras.


> **2020–2025: covid accelerates “digital-first”; backlogs explode; policy starts (slowly) re-learning that shaming non-attendance makes things worse.** Covid makes remote routing unavoidable, with NHS England scaling [*NHS 111 online to help people with coronavirus* (2 Mar 2020)](https://www.england.nhs.uk/2020/03/nhs-111-online-to-help-people-with-coronavirus/) and government even pushing zero-rated access via [*Mobile networks remove data charges for online NHS coronavirus advice* (18 Mar 2020)](https://www.gov.uk/government/news/mobile-networks-remove-data-charges-for-online-nhs-coronavirus-advice)—a tacit admission that “digital front doors” can exclude people unless you deliberately remove barriers. The backlog era then gets nailed down by watchdogs: [NAO *Managing NHS backlogs and waiting times in England* (Nov 2022)](https://www.nao.org.uk/reports/managing-nhs-backlogs-and-waiting-times-in-england/) describes pre-covid deterioration plus pandemic shock plus inflation eroding recovery funding. On the “DNAs” front, NHS England’s own guidance [*Reducing did not attends (DNAs) in outpatient services* (Feb 2023)](https://www.england.nhs.uk/long-read/reducing-did-not-attends-dnas-in-outpatient-services/) still talks about freeing capacity, but it also explicitly says outpatient care shouldn’t be “one size fits all,” hinting at a shift away from pure blame. You can see the same tension in politics and press: the Guardian’s summary of PAC criticism, [*NHS failing to cut waiting times as promised…* (Nov 2025)](https://www.theguardian.com/society/2025/nov/19/nhs-failing-waiting-times-recovery-plan-pac-report), treats delivery failure as a system/government problem (and notes the post-July-2024 Labour context). And the “don’t shame; treat as risk” line finally becomes explicit mainstream clinical argument in [*Attending to patients who do not attend—missed appointments deserve clinical attention* (BMJ, Dec 2025)](https://www.bmj.com/content/391/bmj.r2534). Importantly, current regulators are now quantifying the “access failure → A&E” link: CQC’s [*State of Care 2024–2025: Primary and community care access*](https://www.cqc.org.uk/publications/major-report/state-care/2024-2025/access/primary) reports people going to A&E when they can’t contact their GP, and that it’s worse in the most deprived areas—basically a numeric rebuttal to simplistic “inappropriate attendance” blame.

## Current status on treating patients with respect, not blame

**1) Dignity is being re-litigated because hospitals are visibly failing it.** The biggest “respect” story in 2024–2026 reporting is *[corridor care](https://www.rcn.org.uk/news-and-events/news/uk-corridor-care-rcn-declares-national-emergency-and-demands-political-action-030624)*—patients treated in spaces that aren’t safe, private, or humane. The Royal College of Nursing has been calling it a “[national emergency](https://www.rcn.org.uk/news-and-events/news/uk-corridor-care-rcn-declares-national-emergency-and-demands-political-action-030624)” and links it to people being forced to hospital because they can’t get supported elsewhere. The Royal College of Physicians has been publishing snapshot surveys showing corridor/temporary-space care becoming routine, and explicitly frames it as undignified and unsafe (e.g. “[Doctors confirm ‘corridor care’ crisis as 80% forced to treat patients in unsafe spaces](https://www.rcplondon.ac.uk/news-and-media/news-and-opinion/doctors-confirm-corridor-care-crisis-as-80-forced-to-treat-patients-in-unsafe-spaces/)”). The Royal College of Emergency Medicine and an APPG inquiry have been quantifying scale and harm, and BMJ coverage has amplified it as a year-round failure,
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn0file3 in your response to cite this file, or to surface it as a link.
# Project Report (Repo Contents + Progress)

This file is a working map of what’s in this repository, how the pieces relate, what looks “older/orphaned”, and what to do next to actually get the access problems fixed.

Repo intent (as reflected in `README.md` / `OBJECTIVES.md`): evidence-led documentation of GP access barriers at New Bank Health Centre (GTD Healthcare), with materials suitable for meetings, escalation, and public scrutiny.

---

## 1) Top-Level “Source of Truth” Docs

These define the narrative, goals, and escalation path.

- `README.md` — primary public-facing overview: what’s in the repo, main concerns, personal timeline/experience, notes, ongoing research.
- `OBJECTIVES.md` — compact statement of aims (“fix local”, “use local case for systemic change”) + what success should look like.
- `ORIGINAL_COMPLAINT.md` — original Dec 2024 complaint / talking points (useful as baseline “what started this”).
- `ESCALATION.md` — escalation ladder with “policy hooks” (core hours online access requirement, equity in access, AIS, etc.) and target bodies.
  
Supporting / utility:
- `.gitignore` — standard ignore rules (minimal).
- `markdown-print-viewer.html` — standalone HTML utility to load a markdown file and print it nicely (handy for creating meeting printouts without a full build step).

---

## 2) Meetings (Core Chronology + Meeting Packs)

This is the “project timeline” in practice. Each meeting folder tends to include prep notes, outputs, and supporting evidence.

### 2.1 Aug 2025 — first meeting notes capture

Folder:
- `meetings-notes/2025-08-06-meeting1/`

Key files:
- `meetings-notes/2025-08-06-meeting1/extracted-meeting-1-notes.md` — extracted notes from meeting artefacts (agenda + sticky notes + immediate observations, including “reception training/mystery shoppers”).
- `meetings-notes/2025-08-06-meeting1/IMG20250806185018.jpg` (+ other JPGs) — photos used as the source for extraction.

### 2.2 Sept 2025 — structured “meeting pack” and GTD response capture

Folder:
- `meetings-notes/2025-09-10-meeting2/`

Key authored notes:
- `meetings-notes/2025-09-10-meeting2/meeting-prep-sept-10.md` — prep notes framing issues/questions for the meeting.
- `meetings-notes/2025-09-10-meeting2/gtd-response-summary-and-questions-re-warren-tuite.md` — summary of GTD’s response points and the follow-up questions you want answered.
- `meetings-notes/2025-09-10-meeting2/Training-Challenge-Diplomatic.md` — “training theatre vs root causes” worksheet; a tool for keeping management honest about what fixes actually change outcomes.
- `meetings-notes/2025-09-10-meeting2/benchmarks-summary-sept-10.md` — benchmark reference sheet (practice sizes, access stats, etc.) for contextual comparisons.

Meeting artefacts:
- `meetings-notes/2025-09-10-meeting2/agenda-and-handwritten-notes/ocrd-handwritten-notes-and-agenda.md` — OCR’d agenda + handwritten notes; captures meeting process/tooling ideas and follow-ups.
- `meetings-notes/2025-09-10-meeting2/print-offs/` — PDFs and derived summaries used for the meeting (GP Patient Survey, “You said we did” poster, etc.).
  - `meetings-notes/2025-09-10-meeting2/print-offs/PatientSurveyBreakdown.md` — written breakdown of GP Patient Survey metrics (gateway failures like phone/website/app access, “what happens next”, etc.).

Chat research outputs (semi-orphaned but content-rich):
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GP_Practice_Reviews_Summary.md` — long synthesis of review themes (large).
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GP_Appointment_System_Issues.md` — earlier “issue framing” text.
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GP_practice_benchmarks_UK.md` — benchmarks context (feeds into the benchmark sheet).
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-Appointment_service_confusion.*` — specific analysis of inconsistent “same day” vs “within 1 working day” messaging.
- `meetings-notes/2025-09-10-meeting2/chats/ChatGPT-GTD_Healthcare_summary.*` — background on GTD (size, footprint, themes).
- `meetings-notes/2025-09-10-meeting2/chats/chatgpt-export-to-md.js` — tool to convert ChatGPT export JSON into a sourced markdown representation (duplicated elsewhere).

### 2.3 Nov 2025 — later meeting evidence bundle (largest “pack”)

Folders:
- `meetings-notes/2025-11-26-meeting3/` — photos only (notes captured as images).
- `meetings-notes/2025-11-26-meeting3/` — full evidence bundle: policy docs, vendor docs, data extracts, screenshots, and pack PDFs.

Key authored notes:
- `meetings-notes/2025-11-26-meeting3/Meeting3-goals.md` — structured pre-meeting framing for Nov 26 (site down/out-of-hours, missed calls, complexity, survey signal, PATCHS criticism, receptionist pay, etc.).
- `meetings-notes/2025-11-26-meeting3/Meeting Outcomes.md` — short post-meeting “what changed / what’s next” note.
  - Note: contains a link to `meeting-ppg-nov26/` which does not exist (likely a rename/move happened).
- `meetings-notes/2025-11-26-meeting3/Archived README parts.md` — archived/removed README sections (important for “lost context”; worth mining back into main docs or into `REPORT.md`/a future `timeline.md`).

Key evidence subfolders:
- `meetings-notes/2025-11-26-meeting3/send-to-gtd-team-pre-nov26/` — the “ready-to-send” PDFs: evidence pack, Nov deck, Nov reviews, PATCHS review summary panel.
- `meetings-notes/2025-11-26-meeting3/rubbish website -  down and offline out of hours/` — screenshots/PDFs demonstrating outages, out-of-hours closure, inability to book online, etc.
- `meetings-notes/2025-11-26-meeting3/access rights and escalation/` — local governance/scrutiny context PDFs (Manchester access rights + scrutiny committee guide).
- `meetings-notes/2025-11-26-meeting3/PATCHS-support/` — PATCHS vendor PDFs describing configuration options and request limiter settings (useful for “this is configurable” arguments).
- `meetings-notes/2025-11-26-meeting3/PATCHS-dr-brown-papers/` — academic/press papers on online consultation systems and AI in primary care (useful to back “known failure modes” claims).

Quant analysis (appointments/DNAs):
- `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/` — large NHS appointment CSV extracts (Jun/Jul/Aug 2025), plus JS scripts for comparing DNA rates and estimating impacts.
  - `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/compare-dna.js` — streams CSV and benchmarks one practice vs cohort (sub-ICB/PCN/supplier/all).
  - `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/deep-compare-dna.js` — deeper breakdowns by mode/category/HCP type and correlation with waiting-time buckets.
  - `meetings-notes/2025-11-26-meeting3/Practice_Level_Crosstab_Aug_25/impact-check.js` — specific “impact tests” and additional mined insights across months.
  - Note: these scripts import `csv-parse`; there is no `package.json` in the repo to make running them reproducible out of the box.
- `meetings-notes/2025-11-26-meeting3/Did Not Attends data/` — derived outputs (New Bank-only CSV slice and exported JSON summaries), likely produced using the above scripts.

Additional chat research outputs:
- `meetings-notes/2025-11-26-meeting3/chats/ChatGPT-UK_GP_DNA_statistics.md` — background on published practice-level DNA data.
- `meetings-notes/2025-11-26-meeting3/chats/ChatGPT-GP_online_hours_practice.md` — analysis of time-gating/online-hours norms and the Oct 2025 core-hours rule.
- `meetings-notes/2025-11-26-meeting3/chats/ChatGPT-Fairly_framing_complaints.md` — “how to frame respectfully without losing the substance” guidance.

---

## 3) Reviews and Review Parsing / Analysis

This is the other “major pillar”: qualitative evidence from public feedback.

### 3.1 Practice reviews (Google etc.)

Folder:
- `reviews/`

Primary parsed outputs:
- `reviews/parsed-reviews-usable.json` — cleaned/usable review dataset.
- `reviews/parsed-reviews-og.json` — original scrape/parse output.
- `reviews/parsed-reviews-og-parsed-2yrs.md` / `reviews/parsed-reviews-og-parsed-2yrs.txt` — human-readable extracts.
- `reviews/parsed-reviews-og-parsing.txt` — notes/artefacts from parsing.

Raw sources and parsers:
- `reviews/raw-reviews/New Bank Health Centre-reviews.html` — large captured HTML dump (source evidence).
- `reviews/raw-reviews/New Bank Health Centre-reviews.txt` — plain text export.
- `reviews/raw-reviews/review-parser.user.js` — in-browser user script used to parse Google Maps reviews.
- `reviews/raw-reviews/bad-parser/` — older “offline parsing” attempts (Node scripts + parsed outputs); useful for reference, but looks like an earlier iteration.

Meeting-specific review snapshots:
- `reviews/reviews-between-aug-sept-meetings.txt` — extracted review sample used around the Sept meeting.
- `meetings-notes/2025-11-26-meeting3/reviews/november-google-reviews.txt` — review snapshot used for the Nov pack.

### 3.2 PATCHS product reviews (Trustpilot/Google) and analysis

Folder:
- `reviews/PATCHS/`

Analyses:
- `reviews/PATCHS/ChatGPT-PATCHS_system_overview.md` — long “what is PATCHS” and critique thread; includes “Unsupported Content” blocks (not fully self-contained).
- `reviews/PATCHS/ChatGPT-Re-framing_patient_feedback.md` — reframing feedback for constructive use.
- `reviews/PATCHS/ChatGPT-Summary_of_trustpilot_reviews.md` — summarised Trustpilot review themes.
- `reviews/PATCHS/Grok_2025-09-16_23-49-25_PATCHS Access Issues Analysis - Grok.md` — analysis of 1–3★ Trustpilot review text (useful to show “known failure modes”).

Outputs/printables:
- `reviews/PATCHS/output reports/` — PDF outputs for printing/sharing.

Review browser prototype:
- `reviews/PATCHS/reviews-browser/` — `index.html`, `main.js`, `style.css`, and embedded review text modules.
  - Note: `main.js` imports CSS as a module (`import './style.css'`), which usually implies a bundler workflow (e.g. Vite). There’s no repo-level build config/lockfile, so this currently looks like a “prototype snapshot” rather than a runnable tool as-is.

---

## 4) Survey / Benchmark Evidence

These are used to quantify the “gateway failures” and show “this isn’t just one person”.

- `patient survey breakdown/GP Patient Survey - New Bank Summary.pdf` — the New Bank specific survey summary.
- `patient survey breakdown/GP Patient Survey - Analysis Tool - FULL.pdf` — reference workbook/pdf for broader comparisons.
- `patient survey breakdown/GP Patient Survey - Analysis Tool - Reception.pdf` — reception-related view.
- `patient survey breakdown/GPPS 2024 Questionnaire_PUBLIC.pdf` — survey instrument itself (good for pointing out question design limitations).
- `patient survey breakdown/ChatGPT-GP_Survey_Questions.md` — large question dump / exploration.

Note: `README.md` refers to `patient-survey-breakdown/` but the actual folder name is `patient survey breakdown/` (space). The report and README should agree.

---

## 5) Healthwatch / Wider Context Reports

Folder:
- `healthwatch-reports/`

Contents:
- Multiple Healthwatch / scrutiny / usability PDFs showing that “digital front door” and triage/access problems are widespread.
- `healthwatch-reports/ChatGPT-UK_NHS_GP_data.md` — exploratory attempt to find UK-level counts for “sites closed out of hours” etc., but includes many “Unsupported Content” placeholders (treat as partial notes, not a clean citation source).

---

## 6) Messages / Comms Trail

Folder:
- `messages/`

Contents:
- `messages/2025-08-26-email-for-takeover-dates-and-context.md` — your outgoing “background information request” draft.
- `.eml` threads and `.txt` exports — captured correspondence (useful evidence trail, but contains personal/identifying data).
- `messages/Example - New health problem.txt` — example narrative; likely a template for writing a patient case cleanly.
- Screenshot(s) of correspondence artefacts.

---

## 7) Feb Meeting Pack (Older, But Not “Dead”)

Folder:
- `meeting-ppg-feb4/`

Why it matters:
- This is “fringe” relative to the top-level README, but contains some of the strongest broader narrative framing and curated evidence lists that could materially improve the repo’s main storyline and escalation packs.

Key files:
- `meeting-ppg-feb4/PatientBlaming-README.md` — strong narrative framing around “patient blame” and friction-as-rationing; policy-history framing; useful for tone and “why this matters”.
- `meeting-ppg-feb4/GP Access Evidence - Websites triage and digital barriers.md` — structured index of external evidence sources, with “who is affected” estimates and grouped sources.
- `meeting-ppg-feb4/GP Access Evidence - Immigration blame and far-right.md` — argument for improving access as a way to undercut scapegoating narratives.
- `meeting-ppg-feb4/chats/ChatGPT-Access_to_Healthcare_First.sourced.md` — sourced chat export (long).
- `meeting-ppg-feb4/chats/chatgpt-export-to-md.js` — same export-to-md tool seen elsewhere.
- `meeting-ppg-feb4/Jan15_2026_00-22am-no-appointment-request-out-of-hours.png` — evidence of out-of-hours closure.

---

## 8) “Orphan / Drift / Broken Reference” Checklist


The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn0file4 in your response to cite this file, or to surface it as a link.
# New Bank Health Centre: Access Project

## What this project is trying to achieve

This repo documents **access failures at New Bank Health Centre (GTD Healthcare)**, and uses that local reality to argue for **safer, fairer “front door” models** in primary care. 

* A short, evidence-led record of access problems at this GP practice, and what we want changed.
* We know staff and managers are under pressure. We’re still being clear: blocking any group from care is unfair, and avoidable.

What we’re trying to achieve (two main tracks)

1. Fix the immediate local problem (at this practice and for the management company's other practices)

* Right now, some patients (night/shift workers, carers, people in work, people who can’t take daytime calls) can’t get an appointment. It's not just hard, for some, it's outright impossible.
* The current “daytime-only / unscheduled call / online-only” path means you can miss the call and get pushed back to the start.
* We want a usable non-digital route, and a system that doesn’t require answering unknown calls at random times (scheduled windows or clear alternatives). No “start again” loops.

2. Use the local case to address the bigger, systemic issue

* Poor “digital-only” choices don’t just inconvenience people: They quietly push some groups out of healthcare.
* That means people get sicker later, trust drops, and pressure shifts to urgent care.
* If we escalate, we’ll use this practice as a clear example to argue for fair access standards that work for real life, not ideal users.
* Accountability and transparency: who owns the policy, what changed, and how we’ll know it actually improved.

### What “success” looks like locally

* A **real non-digital route** for requesting help (walk-in / phone / text / email, not just 'training' as if the patient is too stupid to use a website, regardless of the website being rubbish and inaccessible out of office hours). 
* Ability to bypass unscheduled calls stage by either text/sms/email or even just the ability to book by **calling** or visiting the practice, not being **called by** the practice
* No access model where **unscheduled calls are the only way** to progress a request:
  * offer **scheduled callback windows** and/or **message-based handling** where appropriate.
  * simply allow booking an appointment from walk-in.
  * alternatively, supporting registered patients on Bookable _could_ mitigate this.
* **Requests shouldn't be deleted** in a way that forces repeated form-filling and loss of continuity. Doctors and admin are obviously not reading filled in forms fully anyway, so why are you making patients fill in fields you don't read when actioning the response.
* Clear, reliable **status updates** so patients know what’s happening and what to do next. Not just during the e-roundtrip or nhs app stuff, but following up after tests (even if just a text that says "we got all your tests and back and did/didn't find what we were looking for, contact us for your next appointment..."). 
  * The NHS app is pretty good for 'data', but... 
  * Healthcare isn't a transaction, healthcare is a relationship.

### Audience for Tier 1

* Practice leadership and ops (practice manager / ops manager / clinical lead).
* GTD as the operator across its portfolio: “fix it here, then apply the same fix anywhere else you can.”

---

## Tier 2: Escalate the bigger systemic point (using New Bank as an example)

**Goal:** Show how common “digital-only” and poorly-designed triage choices become **friction-as-rationing** — quietly pushing specific groups out of healthcare — and why this is unsafe, unfair, and self-defeating.

### The systemic pattern we’re highlighting

* Access models that assume *perfect availability* (answer unknown calls, repeat forms, keep checking portals) are **designed for the least-stressed people**, and they systematically shed everyone else.
* The harm can be **under-measured**, because excluded people often stop participating (surveys, feedback, repeated attempts).
* This leads to:

  * delayed care, worsening conditions, more urgent crises later,
  * higher system pressure elsewhere (A&E/111),
  * resentment and distrust, often mislabelled as “patients being difficult”.

### What we want changed at the “system” level

* Harder to define, much more complex problem.
* Patients are often treated as if they are at wrong in every situation.
  * How to fix almost 2 decades of language that encourages treating patients like inconveniences?

### Audience for Tier 2

* Commissioners / ICB + oversight bodies (when Tier 1 doesn’t resolve).
* Other practices/operators using similar models; local Healthwatch-type bodies; policy people interested in digital exclusion and access fairness.

---

## Tier 3: “Other issues” 

* **Clarity and honesty in patient-facing comms**: inconsistent promises (“same day” vs “within 1 working day”, unclear cutoffs, unclear next steps). Mostly minor, but this practice can improve simply by renovating the website and reviewing it for repetition/redundancy and out of date or simply wrong information (the process seems to have __drifted__ in reality from what is expected digitally).
* **Contact-data exclusion**: workflows that require both email + phone, or assume stable devices/connectivity. 
* **Staff experience vs “training theatre”**: avoid papering over structural problems by calling them “training challenges” without fixing the system that generates the behaviour. "You said, we did" is only useful if you can pin what you did to real outcomes, not just that you took action, but demonstrating that that action was effective in solving the problem, with receipts.
* **Transparency + governance**: “what is the policy, who owns it, what changed, and how do you know it improved?”
* **Evidence tracking**: keep a clean timeline and pack of sources so the conversation stays grounded and non-inflammatory.


#### Plugin (file_search):
Make sure to include fileciteturn0file5 in your response to cite this file, or to surface it as a link.
# Digital Access Failures - New Bank Health Centre (NHS GP Practice, Manchester)

This repo documents ongoing concerns about **patient access, digital systems, and front‑door process** at New Bank Health Centre (run by GTD Healthcare).

It contains only publicly available data so that the evidence and reasoning are transparent to patients, staff, GTD, and anyone else trying to improve access. These issues pre-date GTD's control of New Bank, but have continued since their take-over in April 2025, with only very minor improvements.

  - Patients are being excluded by the practice requiring a mandatory unscheduled office-hours phone call, forcing them to start over
  - Patients are being treated as if they are to blame, wherever the practice's flawed 'efficiency' decisions are excluding them in ways that are hard to measure the impact
  - Some patients are being excluded completely by 'digital-only' process, poor workflow choices and reception stiffness

## What’s in this repository?

- **Complaint details and meeting prep**
  - [ORIGINAL_COMPLAINT.md](./ORIGINAL_COMPLAINT.md) - initial long‑form complaint about the appointment system. Dec 2024, updated Aug 2025.
  - [OBJECTIVES.md](./OBJECTIVES.md) - Shorter form summary of issues.
  - [meetings-notes/](./meetings-notes/) - Documentation for each meeting, and my prep/issues and received handouts with my notes.
  - [meeting4-goals.md](./meeting-ppg-feb4/meeting4-goals.md) - Meeting 4 (Feb 2026) prep
- **Data and analysis**
  - `patient-survey-breakdown/` - breakdown of GP Patient Survey results for New Bank and further research.
  - `reviews/` - Google review HTML/text, parsing scripts, and parsed outputs.
  - `messages/` - Log of sent messages (mostly emails, complaint-related only).
  - `healthwatch-reports/` - Healthwatch reports from around the UK sharing these concerns.
- [My own experience](#My-patient-experience-with-New-Bank) trying (and failing) to see my doctor, as a patient who works nights (among other issues).
- [Notes](#Notes) - My notes that don't fit anywhere else.
- [Ongoing/further Research](#ongoingfurther-research) - What's next.
- **Produced reports/evidence packs**
  - [General GP practice stats and scope/environment notes](./meetings-notes/2025-09-10-meeting2/benchmarks-summary-sept-10.md)
  - [PATCHS trustpilot reviews for lots of useful patient input](./reviews/PATCHS/output%20reports/PATCHS%201-2-3%20Star%20Reviews%20with%20Summary%20Panel%20Landscape.pdf)
  - [Patient blaming evidence pack](./meeting-ppg-feb4/PatientBlaming-README.md)
  - [Affected patients estimates and Healthwatch overview](./meeting-ppg-feb4/GP%20Access%20Evidence%20-%20Websites%20triage%20and%20digital%20barriers.md)
  - [Poor NHS access and political extremism](./meeting-ppg-feb4/GP%20Access%20Evidence%20-%20Immigration%20blame%20and%20far-right.md)
  - [Google reviews management and good response patterns](./meeting-ppg-feb4/reviews-management.md)

The focus throughout is **patient access**, not clinical care quality.

## Main concerns

1. **Digital‑only booking and exclusion**
  - Access is effectively **digital‑only**
    - No simple “walk in and make an appointment” route and impossible to book by phone without being sent back online, and still requires unscheduled daytime callback.
  - This excludes people without stable internet, devices, availability or confidence with forms, and adds friction even for confident users.
  - Current system also excludes anyone who can't take a day off for a *chance* at an appointment, anyone who works nights or other weird times and many other groups (documented/estimated in the november meeting docs).

2. **Unscheduled missed calls cause deletion/resubmission loop**
  - Alienates patients
    - If the clinician calls for triage OR the receptionist calls to arrange an appointment, and the patient misses two **unscheduled** calls (typically, but not consistently within less than an hour, with no route to schedule or bypass the call), the **request is closed** and the patient must start again.
      - This __was__ enforced at 1 and only 1 appointment request per day but have not yet re-tested since moving to PATCHs. 
      - I have had at least 1 request placed via the old website (the second in the same day, after missing 2 calls) be deleted on the same day, with the explicit reason that it was submitted on the same day.
    - Notification issues _might_ have been fixed by PATCHs, but should re-test patients are notified correctly (in my own case, I was not in the second case).
   - Reporting of missed unscheduled calls __were__ sometimes labelled as **“missed appointments”**.
        - This practice appears to have been reduced significantly in August's practice stats
        - Phone DNAs reported halved relative to other DNA types from July to August

3. **Reception**
  - Reviews over several years describe **rude, dismissive, or blocking behaviour** at reception, especially towards distressed or complex patients.
  - 'Rude reception' is a very common complaint, and some reported incidents have been __severe__, including patients in distress, being laughed at by staff or otherwise driven to leave.
    - Reviews are subjective, but repeated instances of similar types of mistreatment from real Google users suggest a terrible pattern that needs to be fixed.
  - Once patients get through to a GP or nurse, experiences are often (tho not universally) positive...
    - TODO: As of November 2025, slight evidence this is improving, though reception/process complaints still among most common negative reviews.
  - The automated sliding front door sticks (literally blocking access)

4. **PATCHS website off outside office hours**
  - Partially solved, admin requests are now open out of hours (since 14th Jan)
  - but... Appointments cannot be requested.
    - This is only enabled when the office is open
    - Why? It wastes the benefit of a website, which is to avoid synchronous availability needs.

5. **Metrics vs reality**
   - Internal appointment metrics can look “fine” or improving, while:
     - Google and PATCHS reviews include **many 1★ complaints** about access, downtime, confusion, and reception.
        - The practice/GTD should examine these complaints as issues like these are already appearing as reviews on GTD-managed practices, including New Bank.
   - The concern is that **what is measured** (e.g., completed appointments) hides those who are driven away or give up, because only a small proportion of those then go on to write reviews on any platform (some simply can't, the quietest contingent are those most lost).

---

## My patient experience with New Bank

I have been trying to get an appointment at New Bank since December 2024 (when I registered), but as I work nights the process has been almost impossible (the only doctor's appointment I've had took a year, and I had to take a day off and stay awake 6 hours late waiting on an unscheduled office-hours call for that to be possible). Details below...

  - Had a day off (Dec 4th 2025), and transient pain, so tried again...
  - Tried using Bookable.health first, good UI. Gets to the last step, after picking an appointment datetime, then tells me I can't book it because I'm registered at the practice. Nearly moved my registration elsewhere just so I could use Bookable because that's actually what I want the process to be.
  - Used PATCHS
    - Previous improvement of 'suggested callback time' input field, has not been kept in the move to PATCHS. Still cannot request an appointment for anything, still dependent on unscheduled calls, despite stating in message that I cannot receive calls in the day as I work nights.
    - Form has repetitive questions that barely make any sense (I think they put the 'AI' label on it, but there's no way these questions come from a modern LLM-based system).
    - Form has "when should we _not_ contact you" question, but it's pointless if the answer is 'do not phone me, ever', or 'I work nights and sleep days (or cannot use my phone at work, or I don't have a phone), so will not see your phone call'.
    - Staff _really_ need to deal with this, I've brought it up at the PPG several times now. LOTS of people work nights/shifts, or otherwise cannot access their phone in work, and are being actively excluded (no wonder so many 1 star reviews).
  - Asked staff who phoned me (reaching me on the second attempt, with 41 minutes between calls, staring at my phone the entire time, because last time I tried to call back after missing 2 calls, I was told to "ask _really_ nicely and _maybe_ a doctor _would consider_ trying again") if they read my mention that I was probably not accessible via phone and she said "I didn't see that", then scrolled down the page, and confirmed my message was indeed present (she did not say outright, but had clearly not read it), but that...
    - She cannot make an appointment (or propose/suggest/start an appointment process) via PATCHs without a phone call anyway. 
    - Request was not deleted, but no response has been made online. Cannot attach further notes, or reactivate the ticket. I 'have' an appointment scheduled, but PATCHS doesn't surface that, or update the ticket.
    - Request status updated to 'Completed'. Cannot reopen or attach any info. Appointment info is NOT added anywhere in the system. 
  - Don't know what would happen if I missed that second call again. Can't afford to risk it, I only have one day off and awake in the day.
  - PATCHS UX sucks. 
    - The 'AI' questions are barely coherent, and as repetitive as the old eConsult route, maybe more so.
    - PATCHS (or elsewhere on the site) _really_ needs a non-phone-based roundtrip (message/chat/booking slot picker) to solve this problem.
    - It's ridiculous that I STILL _must_ be able to answer an unscheduled phone call within business hours, to get an appointment.
    - The entire message/request content is squeezed into a small scrollable box within the webpage, making it hard to read (this is just really lazy web design by PATCHS). It also seems to auto-scroll itself to the bottom every few seconds, so you have to find your place again if you're rereading the content (it also does not display properly in printed form, as it prints the box, and only a little of the contents).
  - Attended appointment, good discussion with doctor, submitted samples for tests
  - Didn't have a day where the doctor was open and I would be able to answer an unscheduled call randomly in the day.
  - Tests all came back pretty much normal ~~(was not tested for calprotectin, despite asking for that test)~~ (rechecked this, it appeared a few days later, but lower in the list, reporting low end of normal), health condition in NHS app was closed on jan 6th, with no follow-up.
  - The app doesn't say which doctor closed the condition I am trying to get diagnosed, but I consider this an oversight, as the cause of my condition was not identified, only things that are NOT the cause (i.e. I am still sick, but the practice data flagged condition as PAST, pre-mature diagnosis end). 
    - Case was closed without confirmation from the patient or thorough check about the current status.
    - Process issue or lack of care?
    - This same issue was raised by another patient in the Nov 26th PPG.
      - Likely, the process/workflow encourages closing off conditions, but doesn't recognise if the patient was diagnosed/treated, only that the tests were done.
    - From the log, it reads like someone came back after new year and just ticked off whatever tests were on the list, because they clearly didn't read the patient notes about what the tests were looking for.
  - Tried to make an appointment at the front desk (Jan 9th), told "You HAVE to do it online" (still), mentioned that management had said in the PPG meetings I _should_ be able to make an appointment without going online, and reception said they can do it for me, but I would have to be able to receive an unscheduled call (still), and briefly explained I work nights and sleep days, so cannot receive a call, and was told when she checked my history "there's nothing here about that", and I briefly explained that my case had been closed prematurely, but that the doctor had told me to make an appointment to see her next time.
    - She took a note to ask (the ops manager) about it on Monday and she offered to text me Monday.
    - She was polite and seemed understanding, an improvement over last time I tried to make an appointment at the front desk.
  - Woke up monday evening to 2 missed calls (no text message) at 10:44 and 11:33.
    - Missed them because I told the receptionist I would be asleep and she told me she'd send a text message.
    - I saw the receptionist write a post-it about sending me a text message, but that turned into regular 2 phone calls, but with no entry created on the system.
  - Went to front desk, told the receptionist (different one from friday) that they rung me twice, and it should be about making an appointment, but she checked and told me it wasn't on the system, so wouldn't book me an appointment. I told her a short version of the story so far, and she still couldn't make an appointment.

### Notes

- The workflow/system decision-maker at this practice seems to believe "**a doctor MUST be present and online at the moment someone requests an appointment**".
  - This neglects/wastes the simple benefit of a web-based platform is to **decouple doctor availability from patient access**. The mandatory phone call is a decision being made, not an oversight?
  - I want to know who specifically is FORCING a workflow that keeps appointment requests offline outside of office hours, and who is mandating an in-office-hours phone call as a mandatory part of getting an appointed time for any type of meeting.
  - If the rationale is "what if someone accidentally asks about something urgent, and a doctor doesn't see it until morning" seems like something that **could** happen (and is already mitigated by several sentences on every page just to get this far about 'no urgent issues'), being used as justification to continue harm that **is already happening** (alienating/inconveniencing some people outright).
    - I suspect this is about avoiding a backlog of overnight requests to be processed each morning, which is again, a false economy. Sure, you're avoiding _some_ requests that _could_ have been made in-hours, but you're also locking out quite a lot of people from having any access at all, which just compounds the mandatory unscheduled phone call problem.
    - I'm curious about the actual numbers on this... How many requests _are_ made overnight if it is accessible? Do any of these missing people turn up if the practice trials it?
    - It _feels_ like the practice operates patient care as a production line, where each doctor focuses only on part of the process. I don't think this results in good care. ~~A person is not a Model T Ford.~~
      - Healthcare is a relationship, not a transaction.
      - How do legislative requirements have an effect here? 
- The current patient survey status shows 22% of patients report it being hard to get an appointment (an improvement on last year's 39%, tho this isn't quite comparing like to like, as the 39% is the inverse of people who found it easy to contact the practice by phone, and also excludes the "I haven't tried" contingent). I _think_ the real number is higher because the patient survey is worded (unintentionally) to 'downplay' access issues by having some access issues fall through the gaps between available answers.
- On the diagnostic issue, I don't think it reaches clinical negligence (it hasn't resulted in
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn0file6 in your response to cite this file, or to surface it as a link.
# Digital Access Failures – Raised December 2024, Escalated August 2025

## Patient Participation Group Talking Points - Appointment System Concerns

I’d like to discuss a problem with the appointment system at New Bank Health Centre that’s making it unnecessarily hard to get care. If a doctor can’t reach a patient by phone, the request is deleted outright, and they have to resubmit it the next day from scratch. This strips patients of control over their access to care for reasons like work, poor signal, or just missing a call. It’s frustrating, unfair, leads to patient-blaming instead of helpful outcomes, and I think it can be improved.

## Key Points to Raise

1. **Unpredictable Availability**

   - Patients can’t wait by the phone all day for an unscheduled call. Jobs, family, or technical issues (e.g., no signal) mean missing a call isn’t their fault.
   - **NHS Link**: NHS guidelines say appointments should be reasonable and consider patients’ circumstances.

2. **Deleted Requests Create Barriers**

   - Deleting requests after missed calls forces patients into a daily resubmission loop, delaying care with no guarantee of success.
   - **NHS Link**: The NHS Constitution calls for equitable access to care, but this system penalizes patients unfairly.

3. **Vulnerable Patients Suffer Most**

   - Elderly or disabled patients may struggle with the online form or being available for calls, risking exclusion from care.
   - **NHS Link**: NHS accessibility rules require alternative methods for those who can’t use digital systems.

4. **Misleading "Missed Appointment" Label**

   - Calling an unscheduled call a "missed appointment" isn’t accurate and might inflate statistics, affecting trust and policies like charging for no-shows.
   - **NHS Link**: Accurate appointment data is vital per NHS guidance—mislabeling distorts this.

5. **No Notification Worsens the Problem**

   - Patients aren’t always told when their request is deleted (I wasn't for 3 of the 4), leaving them confused and wasting time checking manually.
   - **NHS Link**: NHS England stresses clear communication from the first contact—patients deserve to know their request status.

## Solutions to Suggest

- **Don’t Delete Requests**: Keep appointment requests open for a set period (e.g., 48 hours) even if you rejected it, or ask the patient if they want to close it or reopen tomorrow automatically.
   - You don’t have to make multiple call attempts—we get time is tight—but 2 calls inside 20 seconds isn't giving patients time to spot a missed call to keep an eye out for another call, so it's no different from 1 call practically.
   - Patients should at least be able to reschedule (or even better escalate to non-phone path).
- **Schedule Call Windows**: Let patients pick a time range for callbacks to fit their lives.
- **Offer Alternatives**: Add phone or in-person booking for those who can’t use the online form. Your patient survey suggests 40% of people are not making it through your system for even a first appointment.
- **Notify Patients Reliably**: Send a text or email if a request is closed (which ideally it wouldn't be), with clear next steps. Likewise for support messages, which just black hole currently.
- **Have Some Empathy/Humanity**: People come to the doctor rarely, when they need help most... Most people are not as tech savvy as you, and certainly do not have comfortable devices for filling out long relatively complex forms multiple times or every day. When the receptionist treats people badly because it's technically the patient's own fault, it just drives them further away from your help.
- **Don't Make Doctors Call People**: A simple live-holding system where the Doctors review and queue requests, but a staff member makes the calls, and queues them into the Doctor as needed, would improve the process on both ends, with more flexibility and efficiency for everyone involved.s


## **CORE ISSUES**
- **Digital-only booking system** - no phone/in-person options
- **Unscheduled callbacks** - patients wait all day with no timeframe
- **Two-strikes deletion policy** - missed calls = deleted requests
- **No same-day resubmission** - must wait until next day
- **Misleading terminology** - "missed appointments" for unscheduled calls
- **Tiny text fields** insufficient space for entering detailed medical information
- **Poor notifications** - requests deleted without notification

## **IMPACT ON PATIENTS**
- **Vulnerable groups excluded** (elderly, disabled, digitally excluded)
- **Patient safety risks** - delays in care access
- **Mental health impact** - uncertainty and anxiety
- **Time wasted** - all-day waiting for uncertain outcomes
- **Statistical misrepresentation** - inflates "missed appointment" figures

## **EVIDENCE FROM REVIEWS**
- **40+ complaints** about appointment system since 2017
- **Average rating 1.5/5** for appointment-related complaints
- **Consistent themes**: long phone waits, confusing digital system, rude staff
- **Pattern**: Better Health MCR management (post-2017) shows significant decline

## **NHS POLICY VIOLATIONS**
- **Patient communication standards** - unclear notifications
- **Accessibility requirements** - no alternative booking methods
- **Data accuracy** - mischaracterizing missed calls as appointments
- **Patient rights** - equitable access not provided

## **ESCALATION PATH**
1. **Practice Manager** (direct complaint)
2. **Healthwatch Manchester** (0300 078 0669)
3. **NHS England** (0300 311 22 33)
4. **NHS Counter Fraud Authority** (if intentional misrepresentation suspected)

## **PROPOSED SOLUTIONS**
- **No Deletion** The patient didn’t magically recover. They reached out for help, and you deleted their request—sometimes with a dismissive, blame-shifting response.
- **Alternative booking methods** (phone/in-person)
- **Scheduled callback windows** instead of all-day waiting
- **Flexible missed call policy** - allow same-day resubmission
- **Clear notifications** when requests are closed
- **Accurate terminology** - don't call unscheduled calls "appointments"

## **BROADER IMPLICATIONS**
- **Systemic issue** - the doctors might be great, but some patients don't get the chance to find out
- **Potential fraud** - inflated missed appointment statistics
- **Public interest** - worth investigating across Manchester practices
- **Journalistic angle** - could escalate to Manchester Mill/Press

#### Plugin (file_search):
Make sure to include fileciteturn0file7 in your response to cite this file, or to surface it as a link.
### New Bank Health Centre Patient Survey Summary

The document provided is a detailed report on patient satisfaction with the New Bank Health Centre GP practice, focusing on metrics such as ease of contact, appointment experiences, and overall satisfaction. 

#### Key Failure Areas Impacting Access

1. **Difficulty in Contacting the Practice**
   - **Phone Contact:**
     - **Failure Rate:** 39% of patients do not find it easy to get through to the practice by phone.
     - **Breakdown:** 
       - 10% find it fairly difficult.
       - 12% find it very difficult.
       - 18% are neutral, which may also suggest dissatisfaction.
     - **Comparison:** This is better than the national average (47% do not find it easy), but 39% is still a substantial barrier.
   - **Website Contact:**
     - **Failure Rate:** 27% do not find it easy to contact the practice via the website.
     - **Breakdown:** 
       - 10% find it fairly difficult.
       - 8% find it very difficult.
       - 9% are neutral.
     - **Comparison:** Outperforms the national average (49% do not find it easy), yet 27% still struggle.
   - **NHS App Contact:**
     - **Failure Rate:** 40% do not find it easy to contact the practice using the NHS App.
     - **Breakdown:** 
       - 10% find it fairly difficult.
       - 18% find it very difficult.
       - 11% are neutral.
     - **Comparison:** Better than the national average (51% do not find it easy), but 40% is a high failure rate.
   - **Impact:** These initial contact methods are critical gateways to care. With 39% struggling by phone, 27% via the website, and 40% via the NHS App, a significant portion of patients face barriers before they can even request an appointment. This likely discourages or prevents many from accessing services altogether.

2. **Lack of Clarity After Contact**
   - **Failure Rate:** 25% of patients did not know what the next step would be after contacting the practice (75% knew).
   - **Breakdown:** 
     - 12% explicitly said "no."
     - 13% were told to contact the practice again another day, indicating inefficiency.
   - **Comparison:** Worse than the national average (17% do not know).
   - **Impact:** A quarter of patients leaving without clear guidance may delay care or give up, especially if they must repeatedly attempt contact. This inefficiency exacerbates access issues.

3. **Poor Experience in Contacting the Practice**
   - **Failure Rate:** 34% do not describe their experience of contacting the practice as good (66% say it’s good).
   - **Breakdown:** 
     - 17% rate it as neither good nor poor.
     - 7% as fairly poor.
     - 10% as very poor.
   - **Comparison:** Worse than the national average (30% do not rate it as good).
   - **Impact:** A third of patients having a subpar contact experience reflects systemic issues in responsiveness, potentially deterring future attempts to access care.

4. **Limited Choice in Appointments**
   - **Failure Rate:** 
     - 34% were not offered a choice of time or day.
     - 89% were not offered a choice of location (11% were offered this choice).
   - **Comparison:** 
     - Time/day choice is better than the national average (46% not offered).
     - Location choice is worse (86% not offered nationally).
   - **Impact:** Lack of flexibility in scheduling can prevent patients from attending appointments that fit their availability or location preferences, creating another barrier to access.

5. **Excessive Wait Times**
   - **Failure Rate:** 35% felt they waited too long for their last appointment (65% felt it was about right).
   - **Comparison:** Slightly worse than the national average (33% felt it took too long).
   - **Impact:** Long wait times can discourage timely care-seeking, particularly for urgent needs, and may lead some to abandon the process.

6. **Inadequate Support for Long-Term Conditions**
   - **Failure Rate:** 39% of patients with long-term conditions say they have not had enough support from local services in the past 12 months (61% say they have).
   - **Comparison:** Worse than the national average (31% say no).
   - **Impact:** This high failure rate suggests a gap in ongoing care, which is critical for managing chronic conditions and maintaining patient engagement with the practice.

7. **Overall Experience**
   - **Failure Rate:** 31% do not describe their overall experience as good (69% say it’s good).
   - **Breakdown:** 
     - 9% rate it as neither good nor poor.
     - 12% as fairly poor.
     - 10% as very poor.
   - **Comparison:** Worse than the national average (25% do not rate it as good).
   - **Impact:** Nearly a third of patients being dissatisfied reflects the cumulative effect of accessibility and service issues, likely reducing trust and willingness to seek care.

#### Critical Oversight: The 40% Driven Away

The survey only includes patients who have successfully contacted or had appointments with the practice, excluding those who couldn’t get through or gave up due to initial barriers. This methodological flaw means the reported failure rates (e.g., 39% for phone, 40% for NHS App) likely underestimate the true extent of access problems. 

The people they’re driving away are not measured, suggesting that the practice’s accessibility failures could be significantly worse than the data indicates (running local numbers suggests a range 800-1200 patients affected). These unrepresented patients are likely the most affected by the practice’s shortcomings in contact methods and responsiveness.

#### Comparison to Local and National Averages

While the practice often performs better than local (ICS) and national averages, this does not mitigate the absolute scale of its failures:
- **Phone Contact:** 39% vs. 47% nationally (still a large group struggling).
- **Website Contact:** 27% vs. 49% nationally (still over a quarter failing).
- **NHS App Contact:** 40% vs. 51% nationally (still two-fifths facing issues).
Better-than-average performance does not excuse the fact that substantial minorities are unable to access services easily. The focus on relative success masks the real-world impact on patients.

#### Later Stages vs. Initial Access

The data shows higher satisfaction in later stages (e.g., 74%-87% for appointment quality metrics like listening and care), with failure rates ranging from 13% to 30%. This suggests that once patients overcome initial barriers, their experience improves. However, the critical failure lies in getting to that stage:
- **Implication:** The practice is losing people at the entry point, and the survey’s focus on later-stage satisfaction obscures the significant drop-off before care is received.

### Conclusion

The GP practice is failing a substantial portion of its patients in accessing services, with 39% struggling to contact by phone, 27% via the website, and 40% via the NHS App. Additional barriers include 34% not getting a choice of appointment time/day, 89% not getting a location choice, and 35% facing long wait times. The 39% lacking support for long-term conditions and 31% dissatisfied overall further highlight systemic issues. 

Most critically, the survey excludes the 40% of patients potentially driven away by these initial hurdles, meaning the true failure rate is likely higher. While the practice outperforms some averages, its absolute failure rates reveal significant accessibility barriers that prevent many from receiving care. To address this, the practice must prioritize improving contact methods, clarity, and flexibility to ensure all patients can access services effectively.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
There is a paper trail. There is not, from what I’ve found so far, a public smoking gun for bribery or some secret handoff. What there *is* is a formal procurement trail that makes this much narrower and more attackable.

Your own uploaded data already makes the basic problem obvious: New Bank appears in your map data as a GTD-managed practice with a 1.9 Google score, 69% “overall good” on the GP survey, and a 10% survey completion rate. Your repo also notes that GTD took over in April 2025 and that GTD-run Manchester practices tend to cluster around \~2★ on Google. Separately, your patient-survey breakdown says 39% struggle to get through by phone, 27% via the website, 40% via the NHS App, and 25% do not know what happens next after contacting the practice. fileciteturn3file0 fileciteturn2file7 fileciteturn2file4 fileciteturn0file7

What I can prove is that New Bank was part of a formal Greater Manchester APMS procurement, not some casual local arrangement. In the Find a Tender notice, NECS says it was acting “for and on behalf of” NHS Greater Manchester ICB. New Bank is explicitly Lot 3, “Manchester APMS, New Bank Practice.” The procurement used a Light Touch Regime process mirroring the open procedure. APMS contracts were set at 10 years from 1 April 2025, with an optional 5-year extension. Lot 3 received 7 tenders and was awarded to GTD Healthcare Limited at £12,110,057 ex VAT. The whole procurement was valued at £114,319,680 ex VAT. citeturn31view2turn31view0turn33view3turn33view0turn33view2turn34view0

On the decision side, the formal public body was NHS Greater Manchester Primary Care Commissioning Committee, not just a single practice manager or random local exec. A December 2024 GM PCCC report says that in October 2024 NHS GM PCCC was asked to note the three locality RBR reports, approve the awards, approve award letters, approve publication after standstill, and approve the next phase. That same paper names the report authors as Gordon Reid and Jess Marsi, and its successful-bidder summary lists Lot 3 New Bank Practice going to GTD Healthcare. A later March 2025 Manchester locality paper says NHS GM PCCC supported the contract award notice and confirms that New Bank moved from Better Health Manchester to GTD for the 1 April 2025 start. citeturn31view4turn35view0turn40view3turn38view1

So, on the public record, the closest answer to “who exactly made that decision?” is: NHS Greater Manchester ICB as contracting authority; NECS as procurement support running the process; and GM PCCC as the approving committee. The October 2024 public minutes show the committee membership/present list included Rob Bellingham, Janna Rigby, Manisha Kumar, Sam Evans, Jane Brooks, Anita Rolfe, Ben Squires, Martin Ashton, Caroline Bradley, Jonathan Kerry, Don McGrath, Jim Rochford and Dharmesh Patel. What I have **not** yet found is an individual vote sheet or named signer saying “X personally chose GTD for Lot 3.” That is probably in a fuller October award paper, a Part 2 paper, or the underlying procurement records. citeturn38view0

The awkward bit is this: the public documents do **not** explain *why* GTD beat the other 6 bidders for New Bank. They say there was evaluation, consensus and due diligence across several teams, but they do not publish the scoring matrix, moderation notes, bidder-by-bidder scores, financial-standing assessment, or Lot 3 rationale. There was also a challenge on 3 lots that extended the standstill period twice, but the public paper does not say whether Lot 3 was one of those challenged lots. That missing layer is where the real receipts are. citeturn40view4turn35view2

On “why are they still allowed to operate?”, the current public answer is boring rather than satisfying. CQC currently shows New Bank Health Centre as provided and run by GoToDoc Limited, and GoToDoc’s legal entitlement page includes New Bank among its registered services. CQC also shows GTD Healthcare Head Office, run by GoToDoc Limited, as overall Good, with the latest comprehensive inspection published in 2019 and a 2023 review saying CQC had not found reason to reassess the rating at that stage. On Companies House, GTD Healthcare Limited is active and has filed accounts up to 31 March 2025; GoToDoc Limited is also active. GTD Healthcare Limited also has an outstanding Barclays fixed-and-floating charge created on 2 April 2025. None of that proves the group is financially comfortable, but it does explain why they are still allowed to operate: the public record still shows active companies plus live CQC registration, not a public disqualification. citeturn36search2turn30view3turn41search0turn32view0turn39search0turn32view6

The company structure matters here. The procurement award notice names **GTD Healthcare Limited** as the winning contractor for Lot 3, but CQC shows **GoToDoc Limited** as the registered provider running New Bank. That split is normal enough in corporate groups, but it means financial and regulatory questions may sit in different entities, and you want both looked at, not just “GTD” in the vague sense. citeturn33view0turn36search2turn39search0turn32view0

The cleanest next move is a tight FOI to NHS Greater Manchester asking for recorded information, not “why did you do this?” Their FOI policy is explicit that requests need to identify the documents/information sought, and FOI covers recorded information rather than explanations or opinions. The archive page shows they do publish responses. citeturn30view7turn30view6

Ask for these, by Lot 3 / MANICB01 / New Bank specifically:

1. The three locality RBR reports referenced in the December 2024 GM PCCC paper.
2. The full evaluation methodology, scoring matrix, weightings and pass/fail criteria used for Lot 3.
3. The moderation / consensus scoring notes for Lot 3.
4. The financial-standing and due-diligence assessments for GTD Healthcare Limited and any delivery-entity checks tied to GoToDoc Limited.
5. All conflict-of-interest declarations for evaluators, moderators and GM PCCC members connected to this procurement.
6. The contract award letter, the executed contract, and the quality / access KPIs and schedules for New Bank.
7. Any standstill challenge correspondence or decision records relating to Lot 3.
8. Any equality impact assessment, service-needs assessment, options appraisal, or commissioner case for changing provider at New Bank.
9. Any mobilisation / transition papers for the move from Better Health Manchester to GTD.
10. Any contract-management reviews, remedial notices, quality concerns, access-improvement notices, or escalation records since 1 April 2025.

That is the route to the actual answer. Right now the public trail proves *that* GTD got New Bank, *through what procurement route*, *under which committee*, *for what contract size and term*, and *under which corporate/regulatory shell*. It does **not** yet prove why they outscored the other bidders, and it does **not** show any public evidence of corruption. The gap is narrower than it looked at first, though: the missing documents are pretty specific now.


#### You:
can you find anything I don't know about that process that you haven't already told me, that is probably relevant too.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. A few things matter.

- This was in motion long before the public award notice. NHS GM’s own papers say NECS started the procurement in February 2023 with an RFI, and the public PIN/RFI went out on 16 June 2023 under the same reference, MANICB01, explicitly to test market “capacity and appetite” for New Bank and the other Manchester APMS lots. citeturn37view0turn35view0turn35view1turn35view3

- They had a formal Procurement Evaluation Strategy before the tender opened. The paper says that PES covered procurement methodology, evaluation strategy, the recommended-bidder process, financial thresholds, risks/mitigation, market-engagement reports and evaluation questions. That matters because it tells you exactly which records ought to exist, even if they have not published them. citeturn37view3

- It was bundled into one 11-lot procurement across Manchester, Bolton and HMR, not run as a stand-alone New Bank exercise. I cannot prove from the public papers that this changed the winner, but it plainly made scale and bid capacity more valuable than in a one-practice contest. citeturn37view0

- The intended timetable was fairly tight and very document-heavy: tender publication 26 March 2024, bids closed 10 May, evaluation 23 May to 13 June, due diligence 8 to 11 July, recommended-bidder approvals in July/August, standstill by end of September, mobilisation from mid-October to March, then go-live on 1 April 2025. So there should be dated evaluation packs, moderation notes, due-diligence outputs and approval papers sitting in those windows. citeturn37view1turn37view2

- There was a declared conflict of interest tied directly to New Bank’s new provider. The December 2024 GM PCCC minutes record that Manisha Kumar (“MK”) had a conflict regarding “APMS Procurement Outcomes and the new provider for NewBank Health Centre.” The public minutes I found do not explain what the conflict was or how it was managed beyond recording it. That is one of the cleanest missing records to chase. citeturn35view5

- There was also a legal/procurement challenge. NHS GM later recorded that the process finished about three weeks late because of a challenge, and its 2024/25 delegated-primary-care self-certification says APMS contract length above 5 years and “procurement outcome legal challenges” were reported to NHS England North West. That strongly suggests challenge correspondence and legal handling papers exist. citeturn35view4turn37view4

- GTD did not just pick up New Bank. In the Manchester part of this procurement, GTD won New Bank, Charlestown, Simpson and City Health Centre; Victoria Mill went to Northern Health GPPO; Droylsden and Hawthorn went to Hope Citadel. So whatever the scoring rewarded, it produced a pretty concentrated Manchester outcome in GTD’s favour. citeturn36view1turn36view3turn36view4

- New Bank was already an APMS practice before GTD. NHS GM’s contract list shows New Bank as APMS from 1 October 2017, and there was a 2017 open procurement for it. So this 2024/25 award looks like a re-procurement / successor-contract cycle for an existing APMS site, not a one-off emergency fix. That points toward earlier extension or bridging decisions between the 2017 contract end and the 2025 start. citeturn34view5turn37view5

The records most worth dragging out now are the NECS market-engagement report, the PES appendix, the Recommended Bidder Report for Lot 3, the conflict-of-interest forms and management note for MK, the financial-threshold / due-diligence pack, and the standstill challenge correspondence. Those are the likeliest places where the real rationale is sitting.


#### You:
How do we go about investigating whether their capability (could afford to 'buy') led to overstretching thin (and thinning faster) resources? Like what can we find about the org, who runs it, and why they wanted this, and where 'the money' goes (they seem to be hiring doctors, so this isn't inteded to be accusative, just pragmatic understanding). I already know they pay front-desk staff pretty low wages, so are clearly struggling to compete with market prices, but I'm curious why they took on yet another practice if all the others were already 'failing' (at least at patient satisfaction, which is what we can say for sure). 

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### You:
Added a support doc from grok to look for more info.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I don’t see the Grok doc in the files I can access yet, so this is still from the public record plus your repo.

The public record is more consistent with a thin-margin, centralised contract operator than with a cash-extraction play. New Bank looks, on paper, like a provider transfer under the Greater Manchester APMS tender, not a disclosed corporate acquisition: GTD Healthcare Ltd won Lot 3, and GoToDoc Ltd is the CQC-registered provider now running New Bank. GTD also won three other Manchester lots in the same procurement, so this was part of a deliberate growth push, not a one-off rescue. citeturn24search2turn24search5turn0search2

Who runs it is fairly visible. Companies House shows GoToDoc Ltd is controlled by GTD Healthcare Ltd, and GTD Healthcare Ltd is controlled by Our People’s Trust. GTD says that trust is its employee-ownership vehicle and presents itself as a not-for-profit that reinvests surpluses. The leadership picture also tells you a lot about intent: David Beckett has led GTD since 2005, Jane Pugh handles finance and is part of the team that tenders and negotiates external contracts, and James Logue talks explicitly about continued growth. That does not make them competent, but it does make the direction of travel obvious. citeturn6view0turn19view1turn19view2turn23view0turn3view0

The money side is the interesting bit. In the 2024 group accounts, revenue was £49.3m, cost of sales £37.4m, admin expenses £11.6m, pre-tax profit £203.6k, and post-tax profit £8.3k. Staff costs were £20.8m across an average 1,140 employees. Year-end cash was £2.35m, current liabilities were £10.6m, net assets £2.04m, and secured bank debt £1.18m. Revenue is mainly healthcare contracts plus back-office services to practices. That is not “broke” in the legal sense, but it is a very skinny buffer for a £49m operator. There is also a fresh Barclays charge dated 2 April 2025, right after the new contracts went live; that is worth watching, though by itself it could be routine financing rather than distress. Their jobs page also shows ongoing recruitment across front-desk, clinical and senior service roles, which fits a group still trying to add capacity rather than pull back. citeturn11view2turn11view3turn11view9turn12view0turn12view2turn12view3turn12view6turn12view7turn20view0turn18search1

So the practical hypothesis to test is not “where are the hidden profits?” so much as “did they bid and win faster than they could add resilient local staffing?” Their own strategic report says 2024/25 was about improving contract profitability through continued income generation and tight cost control, and the finance lead is directly involved in tendering. That kind of model can look strong in procurement because scale, governance and mobilisation read well on paper, while the damage shows up later in access and patient experience. Your own data fits that pattern more than it fits a “single bad site” story: New Bank is 1.9 on Google with 69% overall-good and 10% survey completion; Guide Bridge is 1.8 / 53% / 23%; Ashton GP Service 1.8 / 52% / 15%; Gordon Street 1.5 / 61% / 22%; Charlestown 1.9 / 59% / 17%. There are exceptions, but the cluster is ugly. citeturn10view3turn23view0 fileciteturn6file6 fileciteturn5file7 fileciteturn5file1

The clean test is a site-by-quarter panel. Pull, for each GTD practice, GP WTE, nurse/ANP WTE, receptionist/admin WTE, vacancies, turnover, sickness, locum spend, list size, appointments delivered, call-answer rate, routine wait, complaints, FFT, GP Patient Survey, and any contract-performance or remedial notices. Then line those up against contract wins and mobilisation dates. The key documents to drag out are the New Bank APMS contract schedules, the Lot 3 workforce and mobilisation method statement, the TUPE / transfer staffing assumptions from Better Health Manchester to GTD, the financial due-diligence pack used in the tender, and the post-go-live contract-management dashboards. Once you have those, the question becomes measurable: did staffing and access capacity scale with growth, or did they win faster than they staffed. citeturn24search5turn24search4turn21search1

One more thing: CQC won’t tell this story properly. GoToDoc/GTD still appears as an active provider with multiple services and an overall Good provider rating, but several GP-site ratings are old. So CQC status is a bad real-time proxy for whether access has been thinned out under a stretched operating model. citeturn16view0turn16view1turn17view0

Once the Grok doc shows up on my side, I’ll cross-check it against this and pull out anything new or wrong.


#### You:
![image](sediment://file_00000000e7c471f4b926d7724eb9358e)
Okay, all this is good, but I'm looking at this chart of GTD managed properties getting worse and worse every year and I'm like "how on earth are they still expanding the business in the face of terrible reviews like this for a decade?" I need to know about GTD's impact locally, just in case the internet doesn't seem to have surfaced it in google reviews, we want to look for literally any other place any part of this organisation has made and been recorded, anywhere. It won't just be linked to the exact company but look further for the staff and named owners... Before I'm going around saying these people suck at running their company and it's impacting the health of manchester, I need to find anything anyone closely involved with decisions at the company has done.

#### Plugin (file_search):
Make sure to include fileciteturn7file0 in your response to cite this file, or to surface it as a link.
# New Bank Health Centre- Contract, PCN Shift, Stabi

Date: 10/03/2026, 11:05:27

## User

what can you add to this investigation?

## Grok

There is more on the contract timeline and some operational shifts since the April 2025 handover. The New Bank Health Centre contract with GTD is confirmed as 10 years initial term with a possible 5-year extension, aligning with the APMS procurement specs. A May 2025 Manchester Locality PCCC agenda noted a proposed PCN change for New Bank, and the March 2025 paper explicitly confirmed the transition from Better Health Manchester PCN to Ardwick & Longsight PCN as of 1 April 2025, following a vote by PCN members. This came after Better Health Manchester's clinical director declared New Bank would no longer be part of their network post-handover. No public rationale for why GTD chose Ardwick & Longsight, but it suggests integration with nearby practices like Gorton Medical Centre or West Point.  

Financially, both entities look stable on paper with no new distress signals. GoToDoc Limited (the registered provider for New Bank) filed full accounts up to 31 March 2025 in December 2025, plus a confirmation statement in March 2025 and a director details update in February 2026—no charges or major changes since April 2025. GTD Healthcare Limited filed group accounts to 31 March 2025 in December 2025, a confirmation in November 2025, and minor admin fixes like a DOB correction in March 2026. The Barclays charge from 2 April 2025 remains outstanding, but that's consistent with prior info. Accounts are filed timely, but without full PDFs, can't drill into metrics like liquidity or debt ratios—suggest pulling them via Companies House for ratios if you haven't.

CQC-wise, no new inspections for GTD Head Office or New Bank since the 2018 Good rating (up from 2017 requires improvement). A GTD press release mentions three unnamed practices rated Good "recently," but dates aren't specified and likely predate 2025. Broader CQC reports (State of Care 2024/25) flag sector-wide primary care strains like access delays and inequalities, but nothing ties directly to GTD. A 2024 CQC operational review notes reduced inspection volumes (6,700 in 2023/24 vs. 15,800 in 2019), so ratings lag—New Bank's might not reflect post-handover performance.  

On patient sentiment, X chatter is sparse and generic—no direct hits on GTD or New Bank since April 2025. Semantic search pulled complaints about NHS-wide issues: missed results, no-shows, coercive care, trivialized concerns, long waits (e.g., 18 hours without food/water, 9-month appt delays). One post from March 2026 describes quitting a job over denied medical leave during an appt wait; another from February 2026 details a daughter's misread records and denied iron treatment. Nothing names GTD, but patterns echo your uploaded survey breakdowns (39% phone struggles, etc.). Deeper X dives might need user-specific searches like @gtdhealthcare replies.

Recent PCCC minutes (e.g., February 2026) discuss GM primary care risks like funding instability for 2026/27, winter pressures, and estates challenges, with some localities reporting no mitigations—could indirectly affect GTD if New Bank's in a stretched area. A December 2025 pack notes all APMS contracts (including New Bank's) completed standstill without further challenges, and award letters issued. 

To push further: FOI NHS GM for the Recommended Bidder Report and due-diligence pack on Lot 3 (as suggested before)—now timely with 2025/26 accounts out. Monitor PCCC agendas for 2026 quality reviews or remedial notices. If finances hint at strain, code-execute a quick ratio analysis once you grab those PDFs.

## User

How do we go about investigating whether their capability (could afford to 'buy') led to overstretching thin (and thinning faster) resources? Like what can we find about the org, who runs it, and why they wanted this, and where 'the money' goes (they seem to be hiring doctors, so this isn't inteded to be accusative, just pragmatic understanding). I already know they pay front-desk staff pretty low wages, so are clearly struggling to compete with market prices, but I'm curious why they took on yet another practice if all the others were already 'failing' (at least at patient satisfaction, which is what we can say for sure).

## Grok

GTD operates as a not-for-profit social enterprise with a mission to deliver innovative, compassionate primary/urgent/dental care across NW England, emphasizing multidisciplinary teams and service transformation for better patient/commissioner outcomes. This ethos likely drove the New Bank bid—to extend their model into underserved Manchester areas, aligning with NHS tenders favoring scalable, integrated providers. No explicit "why New Bank" in public records, but their tender win (post-2024 procurement) was based on bid strength, possibly highlighting cost-efficiency and innovation over pure satisfaction metrics.

Leadership includes CEO David Beckett (ex-Stockport Homes, focus on ethical ops), Clinical Chair Dr Brian Lewis, NEDs like Dr Peter Fink (clinical expertise), Graham Aitken (governance), and Sally Deaville (non-exec). Directors appointed variably: Beckett since 2019 inception, others 2020-2023. No major changes post-New Bank; stable team suggests calculated growth.

On finances and stretch: Group accounts to Mar 2025 filed Dec 2025, but public summaries lack breakdowns—full PDFs show turnover/profits/net assets, worth pulling for ratios (e.g., liquidity under 1.0 could flag strain). As not-for-profit, surpluses reinvest into services/staff, evident in doctor hires (e.g., recent Salary GP ad at New Bank via WhatsApp channel). Low front-desk pay (market lag) points to budget pressures, possibly from APMS contract constraints or multi-site ops (they run 20+ practices). Expansion might exacerbate this if resources dilute—e.g., satisfaction dips could stem from centralized admin straining local delivery.

To probe overstretch: Compare pre/post-2025 metrics via NHS datasets (patient surveys, staffing ratios). If bids prioritized affordability/scale, it might explain award despite scores. Chase via FOI to NHS GM: bid evaluation on financial viability, projected resource allocation for New Bank. X yields little—mostly neutral/irrelevant posts, no finance specifics.

## User

this thing came up "A 2024 CQC operational review notes reduced inspection volumes (6,700 in 2023/24 vs. 15,800 in 2019", does this mean New Bank patient volume more than halved through the pandemic? Can we get over time stats on this? That's a MASSIVE patient drop (under the previous operator, is notable, but we still want to know that). Find out more about this.

## Grok

this thing came up "A 2024 CQC operational review notes reduced inspection volumes (6,700 in 2023/24 vs. 15,800 in 2019", does this mean New Bank patient volume more than halved through the pandemic? Can we get over time stats on this? That's a MASSIVE patient drop (under the previous operator, is notable, but we still want to know that). Find out more about this.

## References





#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. The thing that jumps out is that GTD is not just “the company running a few badly reviewed GP surgeries.” In Greater Manchester and nearby systems it is treated more like a utility provider: its own site lists 13 GP practices plus urgent-care services across central, north and south Manchester, Oldham, Ashton and elsewhere; Manchester papers also show GTD being used for care-home outbreak support, vaccination delivery, asylum-seeker health support, and the Indigo adult gender service. That helps explain how it keeps expanding despite poor patient-facing review scores: commissioners are buying a delivery platform, not judging it on Google stars. citeturn942760search4turn564772search0turn307733search5turn721700search10turn564772search2

The other important bit is how embedded the leadership is in the local primary-care world. David Beckett has led GTD since 2005; Jane Pugh is the finance lead and part of the team that tenders and negotiates external contracts; Peter Fink’s bio says he has held senior Manchester commissioning roles; Brian Lewis is still showing up in NHS GM papers as Chair of the Oldham GP Board. GTD is also inside the Greater Manchester Urgent Primary Care Alliance: GTD Healthcare Limited became a director of GMUPCA, Jane Pugh is its secretary, and Dawn Sewards is listed as the alliance’s governance lead. That does not show corruption, but it does show GTD is very much inside the same local provider/governance network that makes commissioning decisions. citeturn486154search1turn953414search1turn369569search1turn369569search4turn369569search7

On ownership and “where the money goes,” the public structure is more boring than sinister, but still useful. GTD says it shifted to an employee-ownership model in 2020, with Our People’s Trust as the single shareholder of GTD Healthcare Ltd. Companies House shows the trust is active and its officers include David Beckett alongside other directors. Separately, the group has asset-and-financing plumbing around it: GTD Healthcare Ltd has an outstanding Barclays fixed-and-floating charge created on 2 April 2025, GoToDoc has older Barclays debentures still outstanding, and GTD Health Holdings has property-related charges including Gordon Street Medical Centre, The Smithy, and another Hollingworth property. So the group is not just a wage bill plus contracts; there is estate and secured finance in the picture too. citeturn486154search0turn191103search0turn248973view0turn302290search0turn302290search2turn302290search1turn302290search4turn191103search3

There is also a real public record for why commissioners may keep trusting them. GTD has at least one documented “rescuer” story: Brookdale Surgery was rated Inadequate under a previous provider, GTD took it over in 2018, and CQC later rated it Good across the board. Commissioner papers also show repeated direct awards or renewals to GTD for difficult Special Allocation Scheme work, with Stockport explicitly saying GTD had worked collaboratively and continuity was the reason to keep the contract. So the commissioner-facing story is not “they are obviously useless”; it is more like “they are a known operator willing to take awkward contracts.” citeturn907700search1turn907700search4turn907700search7turn718034search7turn718034search1

But there is one very relevant public negative that is much stronger than Google reviews. In the Leslie Swindells Prevention of Future Deaths report, the coroner said his deteriorating mental health “was not sufficiently recognised or acted upon within the primary care setting when he sought help,” and sent the report to GTD Healthcare. GTD’s response admits he should not have been booked with the assistant practitioner who saw him, says the agency receptionist was not properly aware of the escalation process, and says GTD then stopped employing Assistant Practitioners in Mental Health and changed triage arrangements. Hattersley Group Practice, where GTD says that practitioner worked, is currently rated Requires Improvement by CQC for Safe and Well-led. That is concrete evidence of staffing, role-design and triage weaknesses, not just annoyed patients leaving bad ratings. citeturn838016search0turn649984view0turn907700search2turn734540view0

There is also a straight margin-pressure signal. Manchester’s own papers say GTD told commissioners it could not keep running the Special Allocation Scheme at the current value and wanted about a 23% uplift; the locality then switched the contract to another provider. In other words, when a contract gets too thin, GTD does push back. That matters for your overstretch hypothesis, because it shows the organisation is not indifferent to thin funding and capacity limits. citeturn721700search3turn192566view0

Your local data still matters because it shows the patient-facing side of that model. In your own mapped dataset, GTD sites around Manchester include Gordon Street at 1.5 Google, Ashton GP Service at 1.8, Hattersley at 2.1 and New Bank at 1.9, while nearby non-GTD comparators in the same orbit include Awburn House at 4.0, Bredbury at 4.9 and Chadsfield at 4.5. That does not prove causation on its own, but it makes the “hard contracts in deprived areas” defence look incomplete. fileciteturn8file1 fileciteturn8file5 fileciteturn8file6

What I have **not** found is public evidence that any of the named leaders have been disqualified, struck off as directors, or publicly accused in a way that would justify you going around saying “these people are crooks.” The safer, well-supported line is narrower and stronger: GTD is a regionally embedded contract operator with commissioner trust and local influence, some genuine turnaround credentials, a visible secured-finance/estate structure, and at least one serious coroner-linked failure plus a cluster of poor patient-experience signals across its GP footprint. That’s enough to question competence, stretch and commissioning judgement without overclaiming.

The next tranche worth digging for is very specific: the Swindells serious-incident / learning review if disclosable, Hattersley and New Bank staffing models by role, APMS mobilisation plans, GTD board minutes or trust-board minutes around 2024-25 growth, and post-award quality dashboards for New Bank, Charlestown, Simpson and City Health Centre.


#### You:
it's not so much about 'where's the money' at this point, but I want to know why they keep picking up more practices despite such poor results. I don't think it's a conspiracy or corruption, but I literally want to know why they haven't noticed, and why this company (what policies, what practices, what decisions) can be identified that are driving these bad quality outcomes? Like what potential points could we needle with simple fixes for large improvements? My repo/project generally makes this about access, but its also worth considering care, and looking for GTD's hiring record on online sites, their employee reviews etc, I want a bigger picture than just reciting the companies house listing again.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### You:
"Commissioner papers also show repeated direct awards or renewals to GTD for difficult Special Allocation Scheme work" find more on this... not just from their own website.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. The SAS paper trail is mostly in NHS Greater Manchester and locality committee papers, and it’s a lot more revealing than GTD’s own material.

This is not a generic GP contract. The Special Allocation Scheme is the mandated service for patients who have been immediately removed from a practice list after violence, threatened violence, or behaviour causing fear for safety. Commissioner papers frame it as a last-resort, security-sensitive service where continuity matters more than normal market churn. citeturn442583view0turn357186view0turn435847view0

On Stockport, GTD has held the SAS contract since 2018. In September 2023 Stockport sought a one-year direct award to GTD while GM explored whether a single SAS provider across GM was viable and whether the market could be tested. By July 2024, Stockport was proposing a two-year direct award to GTD again, saying tariff negotiations had already reduced GTD’s activity price to be competitive with other GM providers, and that year-to-date activity suggested a 40% reduction against the previous year’s contract value. In September 2024 the committee minutes say the current provider met all quality requirements, there was no suitable Stockport site with security, the service was being run out of area in Tameside, and there had been no appeals that year. In November 2025 Stockport still went back to a direct award to GTD, noting that a two-year award had been approved but the Provider Selection Regime rules then required the direct award to match the previous contract length, so only a one-year contract could be issued. citeturn442583view2turn442583view0turn141708view0turn141708view1turn141708view3

Manchester has a similar pattern, but with more operational detail. Official Manchester papers say GTD commenced as SAS provider in January 2023, with roughly 100 SAS patients registered at City Health Centre. The initial contract was for 15 months to March 2024, then extended to 31 March 2025. Face-to-face clinics were initially run from Ancoats Primary Care Centre, then relocated to Newton Heath, specifically into Droylsden Road Family Practice, which GTD already ran. The paper says the SAS specification required security guards, gives annual security costs of £30,794 at the old site, and puts the SAS contract itself at £120,174 a year before uplift. It also records a joint commissioner-provider working group, conflict-resolution training for front-line staff, and regular operational meetings. citeturn357186view0

The really important bit is what happened next. In May 2025 Manchester reported that GTD had told commissioners it could not continue delivering SAS unless the overall contract value increased. The locality treated that as a significant service risk, extended GTD for one month to 5 May 2025, and then shifted the 2025/26 SAS contract to Northern Health GPPO. That same paper says reluctance to take on Manchester SAS had been common for years because of the complexity and challenging nature of the patients, and that previous attempts to secure a provider through expressions of interest had been unsuccessful. By September 2025 Manchester’s contract report shows Northern Health GPPO holding the SAS at £100,833 for 2025/26, with quarterly contract reviews, monthly operational meetings, and a stated intention to align the SAS term with longer APMS arrangements for resilience and stability. citeturn435847view0turn435847view1

So the non-GTD reading is pretty plain. GTD kept getting SAS work not because commissioners thought it was a universally brilliant provider, but because SAS is awkward, high-risk, security-heavy work with a shallow provider market. In Stockport, GTD looks like the incumbent commissioners could keep on a negotiated tariff, with continuity and secure premises outweighing the hassle of reprocuring. In Manchester, GTD was also the incumbent for a while, using its own estate, until it finally said the money no longer worked and the ICB had to move the contract elsewhere. citeturn442583view0turn141708view0turn357186view0turn435847view0

The next two documents worth forcing out are the April 2025 Manchester options appraisal that sat behind the switch away from GTD, and the Stockport EqIAs plus contract monitoring packs. Those will tell you whether GTD was being kept because it was genuinely performing acceptably on SAS, or because nobody else wanted the job.


#### You:
on Hattersly group practice and 'leslie swindell'... this is fresh news to me, contextualise. Hattersly is the only entry in our chart which had improved on google reviews from 2018 to 2023 early, but then dipped again from early 2025. If they managed to actually improve, it would be useful to know why they were able to improve that practice (even tho it's only gone from like 1.something to 2.something) what did they do differently here? The CQC identifying this should also have raised flags for more inspections at their other practices, so I'd like you to find anythin to do with that, why many still haven't been reviewed, or at least look up the ftd practices and see how they're doing now.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Hattersley is a bit different from New Bank. On CQC it is not run by GoToDoc Limited. It is a partnership provider, but GTD’s own site says the partnership is “managed by gtd GMS, on behalf of the partners and NHS.” The CQC registration for the partnership names Dr Peter Fink, Dr Brian Lewis and Dawn Sewards among the partners, and those names also sit inside GTD’s leadership/governance world. That is why it shows up in your GTD orbit even though the legal wrapper is not the same as New Bank’s. citeturn440944search4turn689636search0turn137177search0turn137177search3

On Leslie Swindells, the coroner’s finding was very stark: his deteriorating mental health “was not sufficiently recognised or acted upon within the primary care setting when he sought help.” The coroner’s concerns were not just about one bad consultation. They were about role design and operating model: a mental-health assistant practitioner with limited scope, no doctor triage before booking, an agency receptionist who did not understand the escalation pathway, unclear supervision, a telephone assessment for a worsening mental-health presentation, and poor documentation. GTD’s response accepted that Mr Swindells should not have been booked with that practitioner, said the role was later removed from the organisation, added mandatory escalation prompts for new or acute symptoms, tightened agency-staff induction, restricted those appointment books, and introduced a clinician-triaged “digital front door” at Hattersley on 18 November 2024. citeturn589837search1turn510196view0

Why Hattersley seems to have improved for a while is actually pretty legible in the inspection history. In 2015 CQC found governance failures serious enough for a Warning Notice. By the end of 2015 CQC said the required governance fixes had been made. By 2019 Hattersley was rated Good overall. The things CQC specifically praised in that improved period were not exotic: better appointment and telephone arrangements, an active patient participation group and evidence that feedback was acted on, a “health champions” programme launched in 2018, and a young people’s counselling offer in the practice and local schools. That looks like a recipe of basic governance, access tweaks, and community-facing support, not some deep clinical transformation. citeturn381359search2turn869363search1

The 2025 slide also looks pretty legible. CQC’s new assessment did not paint a picture of a practice that had suddenly become uncaring. It said people were mostly positive about care and recent survey/FFT results were mostly satisfactory. The downgrade came from organisational churn and safety/governance weakness: changes to the management structure created support gaps, a practice manager had only been in post for three days, there was no medical lead or diabetes specialist nurse in place, some staff were doing unpaid extra hours, required training had not been completed, recall systems were unclear, and risks around rising list size and staffing were not properly captured on the risk register. CQC also noted the new triage system had only been in place seven weeks. So the pattern is: Hattersley got better when boring systems were tightened, then slipped when management/support structure, staffing and governance loosened again. citeturn308834view0turn308834view1turn857508view0

That also answers the “simple fixes” angle. The leverage points CQC and the coroner both point to are not mysterious: clinician-led triage for higher-risk presentations, tighter role boundaries, less reliance on poorly inducted agency reception cover, explicit escalation rules for mental-health deterioration, staffed practice management rather than floating operational oversight, clear recall ownership, and not running list growth ahead of trained capacity. GTD’s own post-inquest actions at Hattersley line up with exactly those levers. citeturn510196view0turn857508view0turn308834view1

On why CQC has not obviously swept through the rest of GTD, the official answer is basically that CQC does not promise blanket reinspections. Its current guidance says assessment frequency depends on the evidence it receives and can be planned or responsive. On provider changes, CQC says the new provider “inherits” the previous location history and CQC can plan the next inspection based on the last assessment and the type of registration change. For newly registered services, CQC does a registration assessment and says follow-up inspections happen later. So a serious failure at Hattersley does not automatically force immediate full inspections at every other GTD-linked site. citeturn246697search5turn423370search1turn423370search2

The current CQC picture for the Manchester Find a Tender sites is awkwardly stale:

- **New Bank**: GoToDoc registered on 8 July 2025; CQC says it has **not inspected** the service yet under the new provider, and the page shows inherited ratings from the previous provider. citeturn440944search1
- **Charlestown**: GoToDoc registered on 8 July 2025; again **not yet inspected** under the new provider, with inherited previous ratings. citeturn440944search2
- **Simpson**: GoToDoc has been the provider since 11 March 2020, and CQC still says **we have not inspected this service yet** under that provider; the visible Good rating is inherited from a 2015 inspection of the previous provider. citeturn374221search5turn374221search2
- **City Health Centre**: this is the one cleaner GTD counterexample; CQC inspected it in August 2022, rated it **Good** across the board, and in July 2023 said it had not found evidence to reassess the rating at that stage. citeturn696048search0turn696048search6
- For comparison, non-GTD winners in the same tender are not all shaky: **Victoria Mill** is currently **Good** under Northern Health GPPO, and **Hawthorn** is **Outstanding** under Hope Citadel. citeturn696048search1turn696048search2turn696048search8

So the real takeaway is not that CQC “missed” a clear GTD-wide emergency. It is that the public CQC layer is too slow and too inherited to tell you much, except at the handful of sites it has actually looked at recently. Hattersley matters because it shows both sides of the thing you’re trying to understand: this model can improve a practice when it gets the basics right, and it can also degrade quickly when management structure, staffing, role boundaries and triage discipline go soft. That is a much stronger line than “they’re just bad at everything.” citeturn381359search2turn857508view0turn510196view0

The next useful pass would be to pull GTD practice-by-practice changes in access model and staffing from 2023 onward and line them up against the review dips.


#### You:
To be very clear, I'm not saying anyone is a crook. I'm saying they're potentially incompetent, but I recognise the individual people do seem to care, and the stated objectives of the business seem reasonable, but that they suck at providing healthcare. I'm trying to understand exactly why, with receipts, and how we got here, and where we can go with this info to build a full picuture and start trying to fix problems beyond just New Bank.

It sounds like we also need to look at explaining in plain language... ```Manchester’s own papers say GTD told commissioners it could not keep running the Special Allocation Scheme at the current value and wanted about a 23% uplift; the locality then switched the contract to another provider. In other words, when a contract gets too thin, GTD does push back. That matters for your overstretch hypothesis, because it shows the organisation is not indifferent to thin funding and capacity limits``` 'own papers' is vague, uplift is vague, 23% of what? What other provider? etc, don't skim over detail like those. Get the info.

```Stockport explicitly saying GTD had worked collaboratively and continuity was the reason to keep the contract```, how did Stockport say this, who, where, when? What context?


See what you can find on ```APMS mobilisation plans, GTD board minutes or trust-board minutes around 2024-25 growth, and post-award quality dashboards for New Bank, Charlestown, Simpson and City Health Centre``` too.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Pinned down, properly:

The “23% uplift” point comes from Manchester’s own public primary care risk log in the 27 March 2025 Manchester PCCC papers. It says the incumbent SAS provider would not renew “at the current value” and was “looking for an increase in contract value c23%” for 2025/26; it also says a STAR form had been submitted, the incumbent had agreed only a 1-month extension to 30 April 2025, and alternatives were being reviewed. The last public Manchester SAS paper before that put the annual SAS contract at **£120,174**, with a separate expected **0.6% planning uplift** for 2024/25, and said security funding sat outside the core SAS service cost. On that published service-contract baseline, **c23% is roughly £27.6k to £27.8k**, excluding the separate security budget. citeturn442971view0turn235312view5turn235312view2

The “other provider” was **Northern Health GPPO**. Manchester’s 22 May 2025 PCCC paper says GTD had been the previous SAS provider from Droylsden Road Family Practice; commissioners extended GTD only until **5 May 2025** while they reviewed options; Manchester LMT then agreed on **10 April 2025** to contract SAS for 2025/26 to Northern Health GPPO; and Northern Health GPPO **commenced on 6 May 2025** from **Victoria Mill Medical Centre, Miles Platting**. The public reasons given were: prior SAS experience, no significant past performance/quality issues, no complaints or negative patient-outcome impacts during its earlier run, suitable estate ready to go, and willingness to deliver **within the existing budget**. By September 2025 Manchester’s contracts report lists the Northern Health GPPO SAS contract at **£100,833** for 2025/26, with quarterly contract reviews and monthly operational meetings. citeturn781628view0turn137688view3turn137688view5turn781628view5

The Stockport “worked collaboratively” line is also traceable. It is from a **17 July 2024** paper to **Stockport Primary Care Commissioning Committee**, with **Gale Edwards** as executive lead and **Shannon Wesley** as author. That paper says GTD had held the Stockport SAS contract since **2018**, that Stockport had negotiated a **reduced activity tariff** after GM benchmarking to keep it competitive with other GM providers, and that GTD had “worked collaboratively with Stockport Primary Care team to closely monitor the service processes and activity levels across the contract term.” The same paper says year-to-date activity suggested a **40% reduction** versus the previous year’s contract. Then, in the **18 September 2024** public minutes, **K Roberts** told the committee the reduced tariff had been agreed, the contract was being monitored very closely, activity had reduced, the provider met all quality requirements, and Stockport had considered bringing the service back into-borough but had **no suitable accommodation with security**. A later **21 January 2026** Stockport paper repeats continuity and close budget monitoring as the basis for retaining GTD. citeturn142234view0turn781628view1turn142234view1turn781628view6

On the APMS side, the public mobilisation trail is much thinner than the SAS trail. The public Manchester paper of **27 March 2025** says all **seven** new Manchester APMS contracts were in final mobilisation, overseen by a **Project Team led by the Manchester Locality Primary Care Team**, and on course for **1 April 2025**. It names the Manchester provider changes as Droylsden Road moving away from GTD, Charlestown moving to GTD, and New Bank moving to GTD. For **New Bank**, the public next steps it actually spells out are: PCN transfer from **Better Health Manchester** to **Ardwick & Longsight**, PCSE/ODS paperwork, Medicines Optimisation deployment changes, ARRS resource re-estimation, and locality transition support. The December 2024 GM paper adds that the procurement challenge delayed things and that locality teams were finalising signatures and handling mobilisation/transition between outgoing and incoming providers. I have **not** found a public mobilisation pack with staffing assumptions, TUPE plan, handover checklist, clinical-risk log, or site KPIs. citeturn781628view4turn252622search0turn591937search1

For the four Manchester lots you asked about, the award values are public: **New Bank £12,110,057**, **Charlestown £10,325,690**, **Simpson £11,119,652**, and **City Health Centre £26,650,208**, all ex VAT. GTD won all four. citeturn886966search0

On post-award quality dashboards, I still cannot see a public per-site dashboard for **New Bank, Charlestown, Simpson, or City Health Centre**. The public Manchester contracts reports do show review cadence for some contracts, but not site-level APMS performance tables for those four practices. What *is* public is the regulator/status layer: **New Bank** and **Charlestown** were registered by CQC to **GoToDoc Limited** on **8 July 2025** and both say **“we have not inspected this service yet”** under the new provider; **Simpson** has been registered to GoToDoc since **11 March 2020** and still says **“we have not inspected this service yet”** under that provider; **City Health Centre** was inspected in **August 2022**, rated **Good**, and reviewed again in **July 2023** with no need found to reassess the rating then. Manchester’s own quality papers say CQC is prioritising **aged ratings** and a **risk-based** approach. The one concrete post-award site issue I found in the Manchester papers is a **November 2025** estates risk at **Simpson Medical Practice** around **damp and waterproofing**. citeturn438159search0turn438159search1turn438159search2turn438159search3turn801864view0turn474317view1

On GTD board minutes / Our People’s Trust minutes: I couldn’t find any public minutes. Publicly, GTD exposes an **Our People’s Trust** page saying there is a trust board with a voice on the GTD board and an **Employee Connect Council** feeding into that trust board. Companies House, though, shows **Our People’s Trust Limited** filing **dormant accounts** to **31 March 2025**. So there is a public governance shell, but I am not seeing published board packs, minutes, or a public annual report that would explain the 2024–25 growth decisions in detail. citeturn977937search1turn977937search0turn447328search0

That leaves four missing documents that now look especially worth forcing out:

1. the **April 2025 Manchester LMT options appraisal** for SAS;
2. the **lot-specific APMS mobilisation packs** for New Bank and Charlestown;
3. the **site contract review / KPI dashboards** for New Bank, Charlestown, Simpson and City Health Centre;
4. any **post-award remedial notices, contract-management letters, or escalation logs** for those four sites.

Those are the places where the real “why did you think this would work?” record is most likely sitting.


#### You:
who are GTD's actual competitors and peer organisations? Help me understand how the fabric of this industry is connected, who owns what, what pressures are on GTD besides obvious medical/delivery/access concerns, but like who is around them, who is doing well and who is failing similarly? let's zoom out a bit and look at why they're sorta skint enough to be failing, but still expanding the business ONLY into the hardest sectors nobody else will touch? It's pretty obvious to look at it as a privatisation effect, like of course all the worse problems are going to get handled by a non-profit, because the profit-takers around them won't hold the bag if literally anyone else will do it.

Instead of looking at it as a single failing company, investigate how it connects to other operators, and WHY this clearly struggling company is left holding the bag, and has become understandably unable to lift up the troubled practices they're taking on. Let's look not at like "this is corruption", but this is the shape of the world, how do we identify who is squeezing them (directly and indirectly) and try to shine a light on those pressures (by name, wherever possible) to try and find out why they never have enough money to fix problems, and tend to make organisationally-protective decisions instead of good patient-based decisions (like easier access, despite additional staff workloads).

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m pulling this apart from two sides: the local paper trail you already have, and the wider provider market around GTD so this doesn’t collapse back into “one bad company”. Then I’ll stitch them together into a pressure map instead of a blame rant.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Already seeing the pattern: GTD isn’t competing with Tesco-style “good businesses”, it’s in a weird layer of social enterprises, GP federations, CICs and provider shells that commissioners use when contracts are unattractive, risky or hard to mobilise. The question becomes who can absorb risk, not who patients like most.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### You:
i'm not clear if this is paid by gtd to 'buy' the contract (so they get paid for service) or if this is like a fixed price paid by the authority for them to service the faility and its patients? ```For the four Manchester lots you asked about, the award values are public: New Bank £12,110,057, Charlestown £10,325,690, Simpson £11,119,652, and City Health Centre £26,650,208, all ex VAT. GTD won all four.``` what exactly does this mean and is this for?

#### ChatGPT:
That bit is contract value, not a price GTD pays to acquire the practice.

In the tender notice, those figures are the **“total value of the contract/lot (excluding VAT)”** for the relevant APMS lot, and the APMS term is **10 years from 1 April 2025**, with an **optional 5-year extension**. So for New Bank, the public record is basically saying: NHS Greater Manchester ICB awarded GTD the right and obligation to run that APMS service, and the published value for that initial contract lot is about **£12.1m ex VAT over the term**. It is not GTD paying £12.1m to “buy” New Bank. citeturn512196view0turn342208view0

In practice, think “commissioned service contract”, not “acquisition”. The authority pays the provider to deliver the specified GP service to that practice population under the APMS contract. There can still be separate issues around premises, mobilisation costs, staffing assumptions, security budgets for special services, and whether the published figure is fixed, activity-based, uplifted, or varied through schedules. But the headline lot values are commissioner-to-provider contract values, not a takeover fee. citeturn512196view0turn675114view0turn675114view1


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### Plugin (file_search):
Make sure to include fileciteturn16file0 in your response to cite this file, or to surface it as a link.
# Digital Access Failures - New Bank Health Centre (NHS GP Practice, Manchester)

This repo documents ongoing concerns about **patient access, digital systems, and front‑door process** at New Bank Health Centre (run by GTD Healthcare).

It contains only publicly available data so that the evidence and reasoning are transparent to patients, staff, GTD, and anyone else trying to improve access. These issues pre-date GTD's control of New Bank, but have continued since their take-over in April 2025, with only very minor improvements.

  - Patients are being excluded by the practice requiring a mandatory unscheduled office-hours phone call, forcing them to start over
  - Patients are being treated as if they are to blame, wherever the practice's flawed 'efficiency' decisions are excluding them in ways that are hard to measure the impact
  - Some patients are being excluded completely by 'digital-only' process, poor workflow choices and reception stiffness

## What’s in this repository?

- **Complaint details and meeting prep**
  - [ORIGINAL_COMPLAINT.md](./ORIGINAL_COMPLAINT.md) - initial long‑form complaint about the appointment system. Dec 2024, updated Aug 2025.
  - [OBJECTIVES.md](./OBJECTIVES.md) - Shorter form summary of issues.
  - [meetings-notes/](./meetings-notes/) - Documentation for each meeting, and my prep/issues and received handouts with my notes.
  - [meeting4-goals.md](./meeting-ppg-feb4/meeting4-goals.md) - Meeting 4 (Feb 2026) prep
- **Data and analysis**
  - `patient-survey-breakdown/` - breakdown of GP Patient Survey results for New Bank and further research.
  - `reviews/` - Google review HTML/text, parsing scripts, and parsed outputs.
  - `messages/` - Log of sent messages (mostly emails, complaint-related only).
  - `healthwatch-reports/` - Healthwatch reports from around the UK sharing these concerns.
- [My own experience](#My-patient-experience-with-New-Bank) trying (and failing) to see my doctor, as a patient who works nights (among other issues).
- [Notes](#Notes) - My notes that don't fit anywhere else.
- [Ongoing/further Research](#ongoingfurther-research) - What's next.
- **Produced reports/evidence packs**
  - [General GP practice stats and scope/environment notes](./meetings-notes/2025-09-10-meeting2/benchmarks-summary-sept-10.md)
  - [PATCHS trustpilot reviews for lots of useful patient input](./reviews/PATCHS/output%20reports/PATCHS%201-2-3%20Star%20Reviews%20with%20Summary%20Panel%20Landscape.pdf)
  - [Patient blaming evidence pack](./meeting-ppg-feb4/PatientBlaming-README.md)
  - [Affected patients estimates and Healthwatch overview](./meeting-ppg-feb4/GP%20Access%20Evidence%20-%20Websites%20triage%20and%20digital%20barriers.md)
  - [Poor NHS access and political extremism](./meeting-ppg-feb4/GP%20Access%20Evidence%20-%20Immigration%20blame%20and%20far-right.md)
  - [Google reviews management and good response patterns](./meeting-ppg-feb4/reviews-management.md)

The focus throughout is **patient access**, not clinical care quality.

## Main concerns

1. **Digital‑only booking and exclusion**
  - Access is effectively **digital‑only**
    - No simple “walk in and make an appointment” route and impossible to book by phone without being sent back online, and still requires unscheduled daytime callback.
  - This excludes people without stable internet
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn16file1 in your response to cite this file, or to surface it as a link.
# New Bank Health Centre: Access Project

## What this project is trying to achieve

This repo documents **access failures at New Bank Health Centre (GTD Healthcare)**, and uses that local reality to argue for **safer, fairer “front door” models** in primary care. 

* A short, evidence-led record of access problems at this GP practice, and what we want changed.
* We know staff and managers are under pressure. We’re still being clear: blocking any group from care is unfair, and avoidable.

What we’re trying to achieve (two main tracks)

1. Fix the immediate local problem (at this practice and for the management company's other practices)

* Right now, some patients (night/shift workers, carers, people in work, people who can’t take daytime calls) can’t get an appointment. It's not just hard, for some, it's outright impossible.
* The current “daytime-only / unscheduled call / online-only” path means you can miss the call and get pushed back to the start.
* We want a usable non-digital route, and a system that doesn’t require answering unknown calls at random times (scheduled windows or clear alternatives). No “start again” loops.

2. Use the local case to address the bigger, systemic issue

* Poor “digital-only” choices don’t just inconvenience people: They quietly push some groups out of healthcare.
* That means people get sicker later, trust drops, and pressure shifts to urgent care.
* If we escalate, we’ll use this practice as a clear example to argue for fair access standards that work for real life, not ideal users.
* Accountability and transparency: who owns the policy, what changed, and how we’ll know it actually improved.

### What “success” looks like locally

* A **real non-digital route** for requesting help (walk-in / phone / text / email, not just 'training' as if the patient is too stupid to use a website, regardless of the website being rubbish and inaccessible out of office hours). 
* Ability to bypass unscheduled calls stage by either text/sms/email or even just the ability to book by **calling** or visiting the practice, not being **called by** the practice
* No access model where **unscheduled calls are the only way** to progress a request:
  * offer **scheduled callback windows** and/or **message-based handling** where appropriate.
  * simply allow booking an appointment from walk-in.
  * alternatively, supporting registered patients on Bookable _could_ mitigate this.
* **Requests shouldn't be deleted** in a way that forces repeated form-filling and loss of continuity. Doctors and admin are obviously not reading filled in forms fully anyway, so why are you making patients fill in fields you don't read when actioning the response.
* Clear, reliable **status updates** so patients know what’s happening and what to do next. Not just during the e-roundtrip or nhs app stuff, but following up after tests (even if just a text that says "we got all your tests and back and did/didn't find what we were looking for, contact us for your next appointment..."). 
  * The NHS app is pretty good for 'data', but... 
  * Healthcare isn't a transaction, healthcare is a relationship.

### Audience for Tier 1

* Practice leadership and ops (practice manager / ops manager / clinical lead).
* GTD as
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn16file2 in your response to cite this file, or to surface it as a link.
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Greater Manchester GP Practice Experience</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {
  --bg: #f6f4ef;
  --ink: #1a1c1a;
  --panel: rgba(255,255,255,0.92);
  --panel-strong: rgba(255,255,255,0.98);
  --missing: #9aa0a6;
  --low: #c3472f;
  --midlow: #dc8c23;
  --midhigh: #d2b529;
  --high: #4c9a52;
  --veryhigh: #1c7c54;
  --line: rgba(26,28,26,0.12);
  --accent: #0f5e9c;
}
html, body {
  margin: 0;
}
body {
  font: 14px/1.4 Georgia, serif;
  color: var(--ink);
  background: radial-gradient(circle at top, #fff7e3, var(--bg));
}
.page {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-rows: minmax(100vh, 100dvh) auto;
}
.map-stage {
  display: grid;
  grid-template-areas: "legend map";
  grid-template-columns: 360px minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}
#map {
  grid-area: map;
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  min-height: 100dvh;
}
.legend {
  grid-area: legend;
  position: relative;
  z-index: 10;
  background: var(--panel-strong);
  padding: 12px 14px;
  border-right: 1px solid var(--line);
  box-shadow: inset -1px 0 0 rgba(26, 28, 26, 0.04);
  max-width: none;
  overflow: auto;
}
.legend h1 {
  margin: 0 0 8px;
  font-size: 18px;
}
.legend p {
  margin: 0 0 8px;
}
.legend h2 {
  margin: 12px 0 8px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.legend .row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.legend .hint {
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.control-group {
  display: grid;
  gap: 8px;
}
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(15, 94, 156, 0.06);
}
#size-mode-control {
  grid-template-columns: 1fr 1fr;
}
#voronoi-control {
  display: flex;
  align-items: center;
  gap: 8px;
}
#voronoi-control input {
  display: inline-block;
}
.segmented label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
}
.segmented input {
  display: none;
}
.segmented span {
  width: 100%;
  text-align: center;
  border-radius: 999px;
  padding: 5px 8px;
}
.segmented input:checked + span {
  background: var(--accent);
  color: #fff;
}
.metric-note {
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}
.manager-list {
  display: grid;
  gap: 8px;
  max-height: 210px;
  overflow: auto;
  padding-right: 4px;
}
.manager-option {
  display: grid;
  grid-template-columns: 18px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.manager-option input {
  margin: 0;
}
.manager-name {
  min-width: 0;
}
.manager-meta {
  color: rgba(26, 28, 26, 0.68);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.swatch {
  width: 14px;
  height: 14px;
  border: 1px solid rgba(0,0,0,0.25);
  flex: 0 0 auto;
}
.swatch.circle {
  border-radius: 999px;
}
.swatch.square {}
.swatch.diamond {
  transform: rotate(45deg);
}
.swatch.triangle {
  clip-path: polygon(50% 0, 0 100%, 100% 100%);
}
.swatch.hexagon {
  clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);
}
.swatch.pentagon {
  clip-path: polygon(50% 0, 100% 38%, 81% 100%, 19% 100%, 0 38%);
}
.leaflet-marker-icon.marker-icon {
  background: transparent;
  border: 0;
}
.marker-svg {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.22));
}
.leaflet-popup-content {
  min-width: 220px;
}
.leaflet-popup-content a {
  word-break: break-word;
}
.insights {
  padding: 18px 18px 26px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}
.panel {
  background: var(--panel-strong);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}
.panel h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.panel p {
  margin: 0 0 10px;
}
.chart-frame {
  width: 100%;
  overflow-x: auto;
}
#scatterplot {
  width: 100%;
  height: 320px;
  display: block;
}
.chart-note {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}
.comparison-panel {
  grid-column: 1 / -1;
}
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.comparison-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255,255,255,0.72);
  padding: 12px 14px;
}
.comparison-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
}
.comparison-kicker {
  margin: 0 0 10px;
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.comparison-summary {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.45;
}
.comparison-summary p {
  margin: 0 0 10px;
}
.rank-bar {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}
.rank-bar-track {
  position: relative;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, #b23322 0%, #d7b74b 50%, #1f7a3f 100%);
  box-shadow: inset 0 0 0 1px rgba(26, 28, 26, 0.14);
  overflow: hidden;
}
.rank-bar-marker {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #fff;
  border: 2px solid rgba(26, 28, 26, 0.82);
  box-shadow: 0 2px 6px rgba(0,0,0,0.16);
  transform: translate(-50%, -50%);
}
.rank-bar-labels {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
  line-height: 1.35;
}
.rank-bar-labels span {
  color: rgba(26, 28, 26, 0.8);
}
.rank-bar-labels strong {
  color: #161816;
}
.rank-bar-labels .rank-worse {
  text-align: left;
}
.rank-bar-labels .rank-better {
  text-align: right;
}
.comparison-metrics {
  display: grid;
  gap: 8px;
}
.comparison-row {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 1.1fr;
  gap: 10px;
  align-items: baseline;
  padding: 8px 0;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
}
.comparison-row:first-child {
  border-top: 0;
  padding-top: 0;
}
.comparison-label {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.comparison-stat strong {
  display: block;
  font-size: 18px;
}
.comparison-stat strong.tone-good {
  color: #1f7a3f;
}
.comparison-stat strong.tone-mid {
  color: #9d6a00;
}
.comparison-stat strong.tone-bad {
  color: #b23322;
}
.comparison-stat strong.tone-missing {
  color: #7d838a;
}
.comparison-stat span {
  display: block;
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
}
.comparison-delta {
  font-size: 13px;
  line-height: 1.4;
}
.comparison-delta.tone-good {
  color: #1f7a3f;
}
.comparison-delta.tone-mid {
  color: #9d6a00;
}
.comparison-delta.tone-bad {
  color: #b23322;
}
.comparison-delta.tone-missing {
  color: #7d838a;
}
@media (max-width: 960px) {
  .page {
    grid-template-rows: minmax(100vh, 100dvh) auto;
  }
  .map-stage {
    grid-template-areas:
      "map"
      "legend";
    grid-template-columns: 1fr;
    grid-template-rows: minmax(62vh, 70dvh) auto;
    min-height: auto;
  }
  #map {
    height: 62vh;
    height: 62dvh;
    min-height: 62vh;
    min-height: 62dvh;
  }
  .insights {
    grid-template-columns: 1fr;
  }
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  .comparison-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .legend {
    border-right: 0;
    border-top: 1px solid var(--line);
    box-shadow: none;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    background: #fff;
  }
  .page {
    display: block;
  }
  .map-stage {
    grid-template-areas: "legend map";
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: auto;
    break-inside: avoid-page;
  }
  #map {
    height: 170mm;
    min-height: 170mm;
  }
  .legend {
    border: 1px solid var(--line);
    border-right: 0;
    box-shadow: none;
  }
  .panel {
    box-shadow: none;
    border: 1px solid var(--line);
    break-inside: avoid-page;
  }
  .leaflet-control-container {
    display: none;
  }
  .marker-svg {
    filter: none;
  }
}
</style>
</head>
<body>
<div class="page">
  <div class="map-stage">
    <div class="legend">
      <h1>GTD GP Practice Experience Map</h1>
      <p>424 GP surgery profiles from a broad catchment around GTD anchors.</p>
      <p>3,021,833 registered patients across 360 practices.</p>
      <div class="control-group">
        <h2>Score Source</h2>
        <div class="segmented">
          <label><input type="radio" name="score-source" value="google" checked><span>Google</span></label>
          <label><input type="radio" name="score-source" value="survey"><span>GP Survey</span></label>
          <label><input type="radio" name="score-source" value="gap"><span>Gap</span></label>
        </div>
        <p id="metric-description" class="hint"></p>
      </div>
      <div class="control-group">
        <div id="voronoi-control">
          <label title="An estimated population/affected-people view. This is a rough vibes layer, not a real practice boundary map."><input type="checkbox" id="voronoi-toggle"><span>Est. population</span></label>
        </div>
      </div>
      <h2>Management</h2>
      <p id="manager-hint" class="hint"></p>
      <div id="manager-list" class="manager-list"></div>
    </div>
    <div id="map"></div>
  </div>
  <div class="insights">
    <section class="panel comparison-panel">
      <h2 id="comparison-heading">Interactive Benchmarks</h2>
      <p id="comparison-note" class="hint"></p>
      <div id="comparison-grid" class="comparison-grid"></div>
    </section>
    <section class="panel comparison-panel">
      <h2>Completion Rate vs Score</h2>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source.</p>
    </section>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@turf/turf@7.2.0/turf.min.js"></script>
<script>
const rows = [{"code": "Y02849", "name": "City Health Centre", "lat": 53.4827, "lon": -2.24292, "postcode": "M1 1PL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.5, "google_count": 11, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02849-city-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/city-health-centre/Y02849", "gtd_url": "https://www.gtdhealthcare.co.uk/cityhealthcentre", "nearby": "City Health Centre, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 9, "survey_sent_out": 957, "survey_sent_back": 85, "registered_patient_count": 15321}, {"code": "Y02960", "name": "New Bank Health", "lat": 53.4601, "lon": -2.20437, "postcode": "M12 4JE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 163, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02960-new-bank-health.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/new-bank-health/Y02960", "gtd_url": "https://www.gtdhealthcare.co.uk/newbankhealthcentre", "nearby": "City Health Centre, Droylsden Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 942, "survey_sent_back": 98, "registered_patient_count": 6419}, {"code": "Y02713", "name": "Guide Bridge Medical Practice", "lat": 53.4716, "lon": -2.11327, "postcode": "M34 5HY", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 116, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02713-guide-bridge-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/guide-bridge-medical-practice/Y02713", "gtd_url": "https://www.gtdhealthcare.co.uk/guidebridgemedicalpractice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 53, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 531, "survey_sent_back": 122, "registered_patient_count": 4478}, {"code": "Y02520", "name": "Simpson Medical Practice", "lat": 53.514, "lon": -2.19802, "postcode": "M40 9NB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 104, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02520-simpson-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/simpson-medical-practice/Y02520", "gtd_url": "https://www.gtdhealthcare.co.uk/simpsonmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 463, "survey_sent_back": 76, "registered_patient_count": 5375}, {"code": "Y02663", "name": "Droylsden Medical Practice", "lat": 53.4872, "lon": -2.14565, "postcode": "M43 7NP", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 85, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02663-droylsden-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/droylsden-medical-practice/Y02663", "gtd_url": "https://www.gtdhealthcare.co.uk/droylsdenmedicalpractice", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 49, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 550, "survey_sent_back": 100, "registered_patient_count": 4388}, {"code": "Y02325", "name": "Charlestown MD", "lat": 53.5226, "lon": -2.18689, "postcode": "M9 7ED", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 109, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02325-charlestown-md.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlestown-md/Y02325", "gtd_url": "https://www.gtdhealthcare.co.uk/charlestownmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Lindley Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 59, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 621, "survey_sent_back": 106, "registered_patient_count": 5268}, {"code": "Y02875", "name": "Lindley House Health Centre", "lat": 53.5438, "lon": -2.11693, "postcode": "OL1 1NL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 66, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02875-lindley-house-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/lindley-house-health-centre/Y02875", "gtd_url": "https://www.gtdhealthcare.co.uk/lindleymedicalpractice", "nearby": "Lindley Medical Practice, Mossley Medical Practice", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 722, "survey_sent_back": 129, "registered_patient_count": 4895}, {"code": "P89612", "name": "Mossley Medical Practice", "lat": 53.514, "lon": -2.04062, "postcode": "OL5 9AB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 3.7, "google_count": 16, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89612-mossley-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mossley-medical-practice/P89612", "gtd_url": "https://www.gtdhealthcare.co.uk/mossleymedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 423, "survey_sent_back": 95, "registered_patient_count": 2197}, {"code": "P89011", "name": "Gordon Street Medical Centre", "lat": 53.4929, "lon": -2.07804, "postcode": "OL6 6NE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.5, "google_count": 86, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89011-gordon-street-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/gordon-street-medical-centre/P89011", "gtd_url": "https://www.gtdhealthcare.co.uk/gordonstreetmedicalcentre", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 61, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 517, "survey_sent_back": 113, "registered_patient_count": 5181}, {"code": "Y02586", "name": "Ashton Gp Service", "lat": 53.4858, "lon": -2.09997, "postcode": "OL6 7SR", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 91, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02586-ashton-gp-service.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ashton-gp-service/Y02586", "gtd_url": "https://www.gtdhealthcare.co.uk/ashtongpservice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 52, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 569, "survey_sent_back": 88, "registered_patient_count": 5171}, {"code": "P89013", "name": "Hattersley Group Practice", "lat": 53.4502, "lon": -2.02741, "postcode": "SK14 3EH", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 72, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89013-hattersley-group-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/hattersley-group-practice/P89013", "gtd_url": "https://www.gtdhealthcare.co.uk/hattersleygrouppractice", "nearby": "Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 41, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 531, "survey_sent_back": 117, "registered_patient_count": 5011}, {"code": "P89602", "name": "The Smithy Surgery", "lat": 53.4611, "lon": -1.99579, "postcode": "SK14 8LJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.0, "google_count": 23, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89602-the-smithy-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-smithy-surgery/P89602", "gtd_url": "https://www.gtdhealthcare.co.uk/thesmithysurgery", "nearby": "Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 78, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 364, "survey_sent_back": 109, "registered_patient_count": 3747}, {"code": "Y02936", "name": "Millbrook Medical Practice", "lat": 53.4923, "lon": -2.03427, "postcode": "SK15 3BJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.7, "google_count": 39, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02936-millbrook-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/millbrook-medical-practice/Y02936", "gtd_url": "https://www.gtdhealthcare.co.uk/millbrookmedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 565, "survey_sent_back": 111, "registered_patient_count": 3505}, {"code": "P82013001", "name": "Dr Y Loomba & Partner", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.0, "google_count": 10, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82013001-dr-y-loomba-and-partner.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-y-loomba-and-partner/P82013001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82012", "name": "Octagon Medical Centre", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 308, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82012-octagon-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/octagon-medical-centre/P82012", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 24, "survey_sent_out": 665, "survey_sent_back": 161, "registered_patient_count": 6254}, {"code": "P82022", "name": "Dr Rizwan and Dr Awan", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.7, "google_count": 6, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82022-dr-rizwan-and-dr-awan.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-rizwan-and-dr-awan/P82022", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 535, "survey_sent_back": 115, "registered_patient_count": 5594}, {"code": "P82029", "name": "Halliwell Surgery 2", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82029-halliwell-surgery-2.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-2/P82029", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 96, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 530, "survey_sent_back": 110, "registered_patient_count": 3586}, {"code": "P82626", "name": "Halliwell Surgery 3", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82626-halliwell-surgery-3.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-3/P82626", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 82, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 653, "survey_sent_back": 121, "registered_patient_count": 5173}, {"code": "P82634", "name": "Wyresdale Road Surgery", "lat": 53.5816, "lon": -2.45218, "postcode": "BL1 4DN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 9, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634-wyresdale-road-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/wyresdale-road-surgery/P82634", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 558, "survey_sent_back": 107, "registered_patient_count": 3995}, {"code": "P82010", "name": "Dalefield Surgery", "lat": 53.5882, "lon": -2.4518, "postcode": "BL1 4JP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dalefield-surgery/P82010", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 494, "survey_sent_back": 109, "registered_patient_count": 7962}, {"code": "Y02319", "name": "Bolton General Practice", "lat": 53.5782, "lon": -2.43495, "postcode": "BL1 4TH", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 1.8, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-general-practice/Y02319", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 65, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 845, "survey_sent_back": 148, "registered_patient_count": 7694}, {"code": "P82031", "name": "Heaton Medical Centre", "lat": 53.588, "lon": -2.46831, "postcode": "BL1 5PU", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/heaton-medical-centre/P82031", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 393, "survey_sent_back": 116, "registered_patient_count": 10727}, {"code": "P82014", "name": "Spring House Surgery", "lat": 53.5884, "lon": -2.46354, "postcode": "BL1 6AF", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.1, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/spring-house-surgery/P82014", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 6457}, {"code": "P82627", "name": "Cornerstone Surgery", "lat": 53.5887, "lon": -2.45916, "postcode": "BL1 6AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 41, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82627-cornerstone-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/cornerstone-surgery/P82627", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 414, "survey_sent_back": 105, "registered_patient_count": 4230}, {"code": "P82023", "name": "Mandalay Medical Centre", "lat": 53.6106, "lon": -2.4321, "postcode": "BL1 7LR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mandalay-medical-centre/P82023", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 8580}, {"code": "P82634001", "name": "Drs Karim & James-Authe", "lat": 53.596, "lon": -2.45072, "postcode": "BL1 8BZ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.5, "google_count": 19, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634001-drs-karim-and-james-authe.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/drs-karim-and-james-authe/P82634001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "Y03079", "name": "Bolton Community Practice", "lat": 53.5963, "lon": -2.43067, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 4, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-community-practice/Y03079", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 530, "survey_sent_back": 133, "registered_patient_count": 16122}, {"code": "P82025", "name": "Burnside Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "ehealthservice.co.uk", "affiliated_group": "", "google_score": 1.8, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/burnside-surgery/P82025", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 467, "survey_sent_back": 99, "registered_patient_count": 4423}, {"code": "P82625", "name": "Charlotte Street Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.3, "google_count": 33, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlotte-street-surgery/P82625", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 8, "survey_sent_out": 936, "survey_sent_back": 76, "registered_patient_count": 2356}, {"code": "P82607", "name": "Crompton View Surgery", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 7, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82607-crompton-view-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/crompton-view-surgery/P82607", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 89, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 450, "survey_sent_back": 137, "registered_patient_count": 6045}, {"code": "P82021", "name": "The Oaks Family Practice", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.9, "google_count": 33, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82021-the-oaks-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-oaks-family-practice/P82021", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 88, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 412, "survey_sent_back": 136, "registered_patient_count": 6964}, {"code": "P82033", "name": "Bradford Street Surgery", "lat": 53.5768, "lon": -2.41821, "postcode": "BL2 1HT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.8, "google_count": 4, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82033-bradford-street-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bradford-street-surgery/P82033", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 586, "survey_sent_back": 129, "registered_patient_count": 1996}, {"code": "P82016001", "name": "Tonge Moor Health Centre", "lat": 53.5891, "lon": -2.40904, "postcode": "BL2 2LW", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-moor-health-centre/P82016001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82016", "name": "Harwood Medical Centre", "lat": 53.6041, "lon": -2.39814, "postcode": "BL2 3HQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.2, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/harwood-medical-centre/P82016", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 32, "survey_sent_out": 374, "survey_sent_back": 119, "registered_patient_count": 12086}, {"code": "P82011", "name": "Tonge Fold Health Centre", "lat": 53.5795, "lon": -2.40532, "postcode": "BL2 6DY", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 42, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82011-tonge-fold-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-fold-health-centre/P82011", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 90, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 397, "survey_sent_back": 130, "registered_patient_count": 6969}, {"code": "P82018", "name": "The Alastair Ross Medical Practice", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 60, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82018-the-alastair-ross-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-alastair-ross-medical-practice/P82018", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 541, "survey_sent_back": 121, "registered_patient_count": 7491}, {"code": "P82001", "name": "The Dunstan Partnership", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 59, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82001-the-dunstan-partnership.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-dunstan-partnership/P82001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 27, "survey_sent_out": 428, "survey_sent_back": 114, "registered_patient_count": 10157}, {"code": "Y03079003", "name": "Little Lever Health Centre & Library", "lat": 53.5623, "lon": -2.37194, "postcode": "BL3 1HH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 2, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y03079003-little-lever-health-centre-and-library.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/little-lever-health-centre-and-library/Y03079003", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null,
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn16file3 in your response to cite this file, or to surface it as a link.
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Greater Manchester GP Practice Experience</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {
  --bg: #f6f4ef;
  --ink: #1a1c1a;
  --panel: rgba(255,255,255,0.92);
  --panel-strong: rgba(255,255,255,0.98);
  --missing: #9aa0a6;
  --low: #c3472f;
  --midlow: #dc8c23;
  --midhigh: #d2b529;
  --high: #4c9a52;
  --veryhigh: #1c7c54;
  --line: rgba(26,28,26,0.12);
  --accent: #0f5e9c;
}
html, body {
  margin: 0;
}
body {
  font: 14px/1.4 Georgia, serif;
  color: var(--ink);
  background: radial-gradient(circle at top, #fff7e3, var(--bg));
}
.page {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-rows: minmax(100vh, 100dvh) auto;
}
.map-stage {
  display: grid;
  grid-template-areas: "legend map";
  grid-template-columns: 360px minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}
#map {
  grid-area: map;
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  min-height: 100dvh;
}
.legend {
  grid-area: legend;
  position: relative;
  z-index: 10;
  background: var(--panel-strong);
  padding: 12px 14px;
  border-right: 1px solid var(--line);
  box-shadow: inset -1px 0 0 rgba(26, 28, 26, 0.04);
  max-width: none;
  overflow: auto;
}
.legend h1 {
  margin: 0 0 8px;
  font-size: 18px;
}
.legend p {
  margin: 0 0 8px;
}
.legend h2 {
  margin: 12px 0 8px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.legend .row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.legend .hint {
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.control-group {
  display: grid;
  gap: 8px;
}
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(15, 94, 156, 0.06);
}
#size-mode-control {
  grid-template-columns: 1fr 1fr;
}
#voronoi-control {
  display: flex;
  align-items: center;
  gap: 8px;
}
#voronoi-control input {
  display: inline-block;
}
.segmented label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
}
.segmented input {
  display: none;
}
.segmented span {
  width: 100%;
  text-align: center;
  border-radius: 999px;
  padding: 5px 8px;
}
.segmented input:checked + span {
  background: var(--accent);
  color: #fff;
}
.metric-note {
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}
.manager-list {
  display: grid;
  gap: 8px;
  max-height: 210px;
  overflow: auto;
  padding-right: 4px;
}
.manager-option {
  display: grid;
  grid-template-columns: 18px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.manager-option input {
  margin: 0;
}
.manager-name {
  min-width: 0;
}
.manager-meta {
  color: rgba(26, 28, 26, 0.68);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.swatch {
  width: 14px;
  height: 14px;
  border: 1px solid rgba(0,0,0,0.25);
  flex: 0 0 auto;
}
.swatch.circle {
  border-radius: 999px;
}
.swatch.square {}
.swatch.diamond {
  transform: rotate(45deg);
}
.swatch.triangle {
  clip-path: polygon(50% 0, 0 100%, 100% 100%);
}
.swatch.hexagon {
  clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);
}
.swatch.pentagon {
  clip-path: polygon(50% 0, 100% 38%, 81% 100%, 19% 100%, 0 38%);
}
.leaflet-marker-icon.marker-icon {
  background: transparent;
  border: 0;
}
.marker-svg {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.22));
}
.leaflet-popup-content {
  min-width: 220px;
}
.leaflet-popup-content a {
  word-break: break-word;
}
.insights {
  padding: 18px 18px 26px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}
.panel {
  background: var(--panel-strong);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}
.panel h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.panel p {
  margin: 0 0 10px;
}
.chart-frame {
  width: 100%;
  overflow-x: auto;
}
#scatterplot {
  width: 100%;
  height: 320px;
  display: block;
}
.chart-note {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}
.comparison-panel {
  grid-column: 1 / -1;
}
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.comparison-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255,255,255,0.72);
  padding: 12px 14px;
}
.comparison-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
}
.comparison-kicker {
  margin: 0 0 10px;
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.comparison-summary {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.45;
}
.comparison-summary p {
  margin: 0 0 10px;
}
.rank-bar {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}
.rank-bar-track {
  position: relative;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, #b23322 0%, #d7b74b 50%, #1f7a3f 100%);
  box-shadow: inset 0 0 0 1px rgba(26, 28, 26, 0.14);
  overflow: hidden;
}
.rank-bar-marker {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #fff;
  border: 2px solid rgba(26, 28, 26, 0.82);
  box-shadow: 0 2px 6px rgba(0,0,0,0.16);
  transform: translate(-50%, -50%);
}
.rank-bar-labels {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
  line-height: 1.35;
}
.rank-bar-labels span {
  color: rgba(26, 28, 26, 0.8);
}
.rank-bar-labels strong {
  color: #161816;
}
.rank-bar-labels .rank-worse {
  text-align: left;
}
.rank-bar-labels .rank-better {
  text-align: right;
}
.comparison-metrics {
  display: grid;
  gap: 8px;
}
.comparison-row {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 1.1fr;
  gap: 10px;
  align-items: baseline;
  padding: 8px 0;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
}
.comparison-row:first-child {
  border-top: 0;
  padding-top: 0;
}
.comparison-label {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.comparison-stat strong {
  display: block;
  font-size: 18px;
}
.comparison-stat strong.tone-good {
  color: #1f7a3f;
}
.comparison-stat strong.tone-mid {
  color: #9d6a00;
}
.comparison-stat strong.tone-bad {
  color: #b23322;
}
.comparison-stat strong.tone-missing {
  color: #7d838a;
}
.comparison-stat span {
  display: block;
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
}
.comparison-delta {
  font-size: 13px;
  line-height: 1.4;
}
.comparison-delta.tone-good {
  color: #1f7a3f;
}
.comparison-delta.tone-mid {
  color: #9d6a00;
}
.comparison-delta.tone-bad {
  color: #b23322;
}
.comparison-delta.tone-missing {
  color: #7d838a;
}
@media (max-width: 960px) {
  .page {
    grid-template-rows: minmax(100vh, 100dvh) auto;
  }
  .map-stage {
    grid-template-areas:
      "map"
      "legend";
    grid-template-columns: 1fr;
    grid-template-rows: minmax(62vh, 70dvh) auto;
    min-height: auto;
  }
  #map {
    height: 62vh;
    height: 62dvh;
    min-height: 62vh;
    min-height: 62dvh;
  }
  .insights {
    grid-template-columns: 1fr;
  }
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  .comparison-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .legend {
    border-right: 0;
    border-top: 1px solid var(--line);
    box-shadow: none;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    background: #fff;
  }
  .page {
    display: block;
  }
  .map-stage {
    grid-template-areas: "legend map";
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: auto;
    break-inside: avoid-page;
  }
  #map {
    height: 170mm;
    min-height: 170mm;
  }
  .legend {
    border: 1px solid var(--line);
    border-right: 0;
    box-shadow: none;
  }
  .panel {
    box-shadow: none;
    border: 1px solid var(--line);
    break-inside: avoid-page;
  }
  .leaflet-control-container {
    display: none;
  }
  .marker-svg {
    filter: none;
  }
}
</style>
</head>
<body>
<div class="page">
  <div class="map-stage">
    <div class="legend">
      <h1>GTD GP Practice Experience Map</h1>
      <p>424 GP surgery profiles from a broad catchment around GTD anchors.</p>
      <p>3,021,833 registered patients across 360 practices.</p>
      <div class="control-group">
        <h2>Score Source</h2>
        <div class="segmented">
          <label><input type="radio" name="score-source" value="google" checked><span>Google</span></label>
          <label><input type="radio" name="score-source" value="survey"><span>GP Survey</span></label>
          <label><input type="radio" name="score-source" value="gap"><span>Gap</span></label>
        </div>
        <p id="metric-description" class="hint"></p>
      </div>
      <div class="control-group">
        <div id="voronoi-control">
          <label title="An estimated population/affected-people view. This is a rough vibes layer, not a real practice boundary map."><input type="checkbox" id="voronoi-toggle"><span>Est. population</span></label>
        </div>
      </div>
      <h2>Management</h2>
      <p id="manager-hint" class="hint"></p>
      <div id="manager-list" class="manager-list"></div>
    </div>
    <div id="map"></div>
  </div>
  <div class="insights">
    <section class="panel comparison-panel">
      <h2 id="comparison-heading">Interactive Benchmarks</h2>
      <p id="comparison-note" class="hint"></p>
      <div id="comparison-grid" class="comparison-grid"></div>
    </section>
    <section class="panel comparison-panel">
      <h2>Completion Rate vs Score</h2>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source.</p>
    </section>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@turf/turf@7.2.0/turf.min.js"></script>
<script>
const rows = [{"code": "Y02849", "name": "City Health Centre", "lat": 53.4827, "lon": -2.24292, "postcode": "M1 1PL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.5, "google_count": 11, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02849-city-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/city-health-centre/Y02849", "gtd_url": "https://www.gtdhealthcare.co.uk/cityhealthcentre", "nearby": "City Health Centre, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 9, "survey_sent_out": 957, "survey_sent_back": 85, "registered_patient_count": 15321}, {"code": "Y02960", "name": "New Bank Health", "lat": 53.4601, "lon": -2.20437, "postcode": "M12 4JE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 163, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02960-new-bank-health.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/new-bank-health/Y02960", "gtd_url": "https://www.gtdhealthcare.co.uk/newbankhealthcentre", "nearby": "City Health Centre, Droylsden Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 942, "survey_sent_back": 98, "registered_patient_count": 6419}, {"code": "Y02713", "name": "Guide Bridge Medical Practice", "lat": 53.4716, "lon": -2.11327, "postcode": "M34 5HY", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 116, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02713-guide-bridge-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/guide-bridge-medical-practice/Y02713", "gtd_url": "https://www.gtdhealthcare.co.uk/guidebridgemedicalpractice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 53, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 531, "survey_sent_back": 122, "registered_patient_count": 4478}, {"code": "Y02520", "name": "Simpson Medical Practice", "lat": 53.514, "lon": -2.19802, "postcode": "M40 9NB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 104, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02520-simpson-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/simpson-medical-practice/Y02520", "gtd_url": "https://www.gtdhealthcare.co.uk/simpsonmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 463, "survey_sent_back": 76, "registered_patient_count": 5375}, {"code": "Y02663", "name": "Droylsden Medical Practice", "lat": 53.4872, "lon": -2.14565, "postcode": "M43 7NP", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 85, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02663-droylsden-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/droylsden-medical-practice/Y02663", "gtd_url": "https://www.gtdhealthcare.co.uk/droylsdenmedicalpractice", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 49, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 550, "survey_sent_back": 100, "registered_patient_count": 4388}, {"code": "Y02325", "name": "Charlestown MD", "lat": 53.5226, "lon": -2.18689, "postcode": "M9 7ED", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 109, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02325-charlestown-md.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlestown-md/Y02325", "gtd_url": "https://www.gtdhealthcare.co.uk/charlestownmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Lindley Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 59, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 621, "survey_sent_back": 106, "registered_patient_count": 5268}, {"code": "Y02875", "name": "Lindley House Health Centre", "lat": 53.5438, "lon": -2.11693, "postcode": "OL1 1NL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 66, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02875-lindley-house-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/lindley-house-health-centre/Y02875", "gtd_url": "https://www.gtdhealthcare.co.uk/lindleymedicalpractice", "nearby": "Lindley Medical Practice, Mossley Medical Practice", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 722, "survey_sent_back": 129, "registered_patient_count": 4895}, {"code": "P89612", "name": "Mossley Medical Practice", "lat": 53.514, "lon": -2.04062, "postcode": "OL5 9AB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 3.7, "google_count": 16, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89612-mossley-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mossley-medical-practice/P89612", "gtd_url": "https://www.gtdhealthcare.co.uk/mossleymedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 423, "survey_sent_back": 95, "registered_patient_count": 2197}, {"code": "P89011", "name": "Gordon Street Medical Centre", "lat": 53.4929, "lon": -2.07804, "postcode": "OL6 6NE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.5, "google_count": 86, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89011-gordon-street-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/gordon-street-medical-centre/P89011", "gtd_url": "https://www.gtdhealthcare.co.uk/gordonstreetmedicalcentre", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 61, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 517, "survey_sent_back": 113, "registered_patient_count": 5181}, {"code": "Y02586", "name": "Ashton Gp Service", "lat": 53.4858, "lon": -2.09997, "postcode": "OL6 7SR", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 91, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02586-ashton-gp-service.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ashton-gp-service/Y02586", "gtd_url": "https://www.gtdhealthcare.co.uk/ashtongpservice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 52, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 569, "survey_sent_back": 88, "registered_patient_count": 5171}, {"code": "P89013", "name": "Hattersley Group Practice", "lat": 53.4502, "lon": -2.02741, "postcode": "SK14 3EH", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 72, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89013-hattersley-group-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/hattersley-group-practice/P89013", "gtd_url": "https://www.gtdhealthcare.co.uk/hattersleygrouppractice", "nearby": "Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 41, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 531, "survey_sent_back": 117, "registered_patient_count": 5011}, {"code": "P89602", "name": "The Smithy Surgery", "lat": 53.4611, "lon": -1.99579, "postcode": "SK14 8LJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.0, "google_count": 23, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89602-the-smithy-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-smithy-surgery/P89602", "gtd_url": "https://www.gtdhealthcare.co.uk/thesmithysurgery", "nearby": "Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 78, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 364, "survey_sent_back": 109, "registered_patient_count": 3747}, {"code": "Y02936", "name": "Millbrook Medical Practice", "lat": 53.4923, "lon": -2.03427, "postcode": "SK15 3BJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.7, "google_count": 39, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02936-millbrook-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/millbrook-medical-practice/Y02936", "gtd_url": "https://www.gtdhealthcare.co.uk/millbrookmedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 565, "survey_sent_back": 111, "registered_patient_count": 3505}, {"code": "P82013001", "name": "Dr Y Loomba & Partner", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.0, "google_count": 10, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82013001-dr-y-loomba-and-partner.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-y-loomba-and-partner/P82013001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82012", "name": "Octagon Medical Centre", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 308, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82012-octagon-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/octagon-medical-centre/P82012", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 24, "survey_sent_out": 665, "survey_sent_back": 161, "registered_patient_count": 6254}, {"code": "P82022", "name": "Dr Rizwan and Dr Awan", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.7, "google_count": 6, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82022-dr-rizwan-and-dr-awan.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-rizwan-and-dr-awan/P82022", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 535, "survey_sent_back": 115, "registered_patient_count": 5594}, {"code": "P82029", "name": "Halliwell Surgery 2", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82029-halliwell-surgery-2.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-2/P82029", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 96, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 530, "survey_sent_back": 110, "registered_patient_count": 3586}, {"code": "P82626", "name": "Halliwell Surgery 3", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82626-halliwell-surgery-3.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-3/P82626", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 82, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 653, "survey_sent_back": 121, "registered_patient_count": 5173}, {"code": "P82634", "name": "Wyresdale Road Surgery", "lat": 53.5816, "lon": -2.45218, "postcode": "BL1 4DN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 9, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634-wyresdale-road-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/wyresdale-road-surgery/P82634", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 558, "survey_sent_back": 107, "registered_patient_count": 3995}, {"code": "P82010", "name": "Dalefield Surgery", "lat": 53.5882, "lon": -2.4518, "postcode": "BL1 4JP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dalefield-surgery/P82010", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 494, "survey_sent_back": 109, "registered_patient_count": 7962}, {"code": "Y02319", "name": "Bolton General Practice", "lat": 53.5782, "lon": -2.43495, "postcode": "BL1 4TH", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 1.8, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-general-practice/Y02319", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 65, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 845, "survey_sent_back": 148, "registered_patient_count": 7694}, {"code": "P82031", "name": "Heaton Medical Centre", "lat": 53.588, "lon": -2.46831, "postcode": "BL1 5PU", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/heaton-medical-centre/P82031", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 393, "survey_sent_back": 116, "registered_patient_count": 10727}, {"code": "P82014", "name": "Spring House Surgery", "lat": 53.5884, "lon": -2.46354, "postcode": "BL1 6AF", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.1, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/spring-house-surgery/P82014", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 6457}, {"code": "P82627", "name": "Cornerstone Surgery", "lat": 53.5887, "lon": -2.45916, "postcode": "BL1 6AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 41, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82627-cornerstone-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/cornerstone-surgery/P82627", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 414, "survey_sent_back": 105, "registered_patient_count": 4230}, {"code": "P82023", "name": "Mandalay Medical Centre", "lat": 53.6106, "lon": -2.4321, "postcode": "BL1 7LR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mandalay-medical-centre/P82023", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 8580}, {"code": "P82634001", "name": "Drs Karim & James-Authe", "lat": 53.596, "lon": -2.45072, "postcode": "BL1 8BZ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.5, "google_count": 19, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634001-drs-karim-and-james-authe.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/drs-karim-and-james-authe/P82634001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "Y03079", "name": "Bolton Community Practice", "lat": 53.5963, "lon": -2.43067, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 4, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-community-practice/Y03079", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 530, "survey_sent_back": 133, "registered_patient_count": 16122}, {"code": "P82025", "name": "Burnside Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "ehealthservice.co.uk", "affiliated_group": "", "google_score": 1.8, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/burnside-surgery/P82025", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 467, "survey_sent_back": 99, "registered_patient_count": 4423}, {"code": "P82625", "name": "Charlotte Street Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.3, "google_count": 33, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlotte-street-surgery/P82625", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 8, "survey_sent_out": 936, "survey_sent_back": 76, "registered_patient_count": 2356}, {"code": "P82607", "name": "Crompton View Surgery", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 7, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82607-crompton-view-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/crompton-view-surgery/P82607", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 89, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 450, "survey_sent_back": 137, "registered_patient_count": 6045}, {"code": "P82021", "name": "The Oaks Family Practice", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.9, "google_count": 33, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82021-the-oaks-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-oaks-family-practice/P82021", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 88, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 412, "survey_sent_back": 136, "registered_patient_count": 6964}, {"code": "P82033", "name": "Bradford Street Surgery", "lat": 53.5768, "lon": -2.41821, "postcode": "BL2 1HT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.8, "google_count": 4, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82033-bradford-street-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bradford-street-surgery/P82033", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 586, "survey_sent_back": 129, "registered_patient_count": 1996}, {"code": "P82016001", "name": "Tonge Moor Health Centre", "lat": 53.5891, "lon": -2.40904, "postcode": "BL2 2LW", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-moor-health-centre/P82016001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82016", "name": "Harwood Medical Centre", "lat": 53.6041, "lon": -2.39814, "postcode": "BL2 3HQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.2, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/harwood-medical-centre/P82016", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 32, "survey_sent_out": 374, "survey_sent_back": 119, "registered_patient_count": 12086}, {"code": "P82011", "name": "Tonge Fold Health Centre", "lat": 53.5795, "lon": -2.40532, "postcode": "BL2 6DY", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 42, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82011-tonge-fold-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-fold-health-centre/P82011", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 90, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 397, "survey_sent_back": 130, "registered_patient_count": 6969}, {"code": "P82018", "name": "The Alastair Ross Medical Practice", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 60, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82018-the-alastair-ross-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-alastair-ross-medical-practice/P82018", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 541, "survey_sent_back": 121, "registered_patient_count": 7491}, {"code": "P82001", "name": "The Dunstan Partnership", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 59, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82001-the-dunstan-partnership.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-dunstan-partnership/P82001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 27, "survey_sent_out": 428, "survey_sent_back": 114, "registered_patient_count": 10157}, {"code": "Y03079003", "name": "Little Lever Health Centre & Library", "lat": 53.5623, "lon": -2.37194, "postcode": "BL3 1HH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 2, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y03079003-little-lever-health-centre-and-library.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/little-lever-health-centre-and-library/Y03079003", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null,
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn16file4 in your response to cite this file, or to surface it as a link.
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Greater Manchester GP Practice Experience</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {
  --bg: #f6f4ef;
  --ink: #1a1c1a;
  --panel: rgba(255,255,255,0.92);
  --panel-strong: rgba(255,255,255,0.98);
  --missing: #9aa0a6;
  --low: #c3472f;
  --midlow: #dc8c23;
  --midhigh: #d2b529;
  --high: #4c9a52;
  --veryhigh: #1c7c54;
  --line: rgba(26,28,26,0.12);
  --accent: #0f5e9c;
}
html, body {
  margin: 0;
}
body {
  font: 14px/1.4 Georgia, serif;
  color: var(--ink);
  background: radial-gradient(circle at top, #fff7e3, var(--bg));
}
.page {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-rows: minmax(100vh, 100dvh) auto;
}
.map-stage {
  display: grid;
  grid-template-areas: "legend map";
  grid-template-columns: 360px minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}
#map {
  grid-area: map;
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  min-height: 100dvh;
}
.legend {
  grid-area: legend;
  position: relative;
  z-index: 10;
  background: var(--panel-strong);
  padding: 12px 14px;
  border-right: 1px solid var(--line);
  box-shadow: inset -1px 0 0 rgba(26, 28, 26, 0.04);
  max-width: none;
  overflow: auto;
}
.legend h1 {
  margin: 0 0 8px;
  font-size: 18px;
}
.legend p {
  margin: 0 0 8px;
}
.legend h2 {
  margin: 12px 0 8px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.legend .row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.legend .hint {
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.control-group {
  display: grid;
  gap: 8px;
}
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(15, 94, 156, 0.06);
}
#size-mode-control {
  grid-template-columns: 1fr 1fr;
}
#voronoi-control {
  display: flex;
  align-items: center;
  gap: 8px;
}
#voronoi-control input {
  display: inline-block;
}
.segmented label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
}
.segmented input {
  display: none;
}
.segmented span {
  width: 100%;
  text-align: center;
  border-radius: 999px;
  padding: 5px 8px;
}
.segmented input:checked + span {
  background: var(--accent);
  color: #fff;
}
.metric-note {
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}
.manager-list {
  display: grid;
  gap: 8px;
  max-height: 210px;
  overflow: auto;
  padding-right: 4px;
}
.manager-option {
  display: grid;
  grid-template-columns: 18px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.manager-option input {
  margin: 0;
}
.manager-name {
  min-width: 0;
}
.manager-meta {
  color: rgba(26, 28, 26, 0.68);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.swatch {
  width: 14px;
  height: 14px;
  border: 1px solid rgba(0,0,0,0.25);
  flex: 0 0 auto;
}
.swatch.circle {
  border-radius: 999px;
}
.swatch.square {}
.swatch.diamond {
  transform: rotate(45deg);
}
.swatch.triangle {
  clip-path: polygon(50% 0, 0 100%, 100% 100%);
}
.swatch.hexagon {
  clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);
}
.swatch.pentagon {
  clip-path: polygon(50% 0, 100% 38%, 81% 100%, 19% 100%, 0 38%);
}
.leaflet-marker-icon.marker-icon {
  background: transparent;
  border: 0;
}
.marker-svg {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.22));
}
.leaflet-popup-content {
  min-width: 220px;
}
.leaflet-popup-content a {
  word-break: break-word;
}
.insights {
  padding: 18px 18px 26px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}
.panel {
  background: var(--panel-strong);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}
.panel h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.panel p {
  margin: 0 0 10px;
}
.chart-frame {
  width: 100%;
  overflow-x: auto;
}
#scatterplot {
  width: 100%;
  height: 320px;
  display: block;
}
.chart-note {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}
.comparison-panel {
  grid-column: 1 / -1;
}
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.comparison-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255,255,255,0.72);
  padding: 12px 14px;
}
.comparison-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
}
.comparison-kicker {
  margin: 0 0 10px;
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.comparison-summary {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.45;
}
.comparison-summary p {
  margin: 0 0 10px;
}
.rank-bar {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}
.rank-bar-track {
  position: relative;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, #b23322 0%, #d7b74b 50%, #1f7a3f 100%);
  box-shadow: inset 0 0 0 1px rgba(26, 28, 26, 0.14);
  overflow: hidden;
}
.rank-bar-marker {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #fff;
  border: 2px solid rgba(26, 28, 26, 0.82);
  box-shadow: 0 2px 6px rgba(0,0,0,0.16);
  transform: translate(-50%, -50%);
}
.rank-bar-labels {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
  line-height: 1.35;
}
.rank-bar-labels span {
  color: rgba(26, 28, 26, 0.8);
}
.rank-bar-labels strong {
  color: #161816;
}
.rank-bar-labels .rank-worse {
  text-align: left;
}
.rank-bar-labels .rank-better {
  text-align: right;
}
.comparison-metrics {
  display: grid;
  gap: 8px;
}
.comparison-row {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 1.1fr;
  gap: 10px;
  align-items: baseline;
  padding: 8px 0;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
}
.comparison-row:first-child {
  border-top: 0;
  padding-top: 0;
}
.comparison-label {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.comparison-stat strong {
  display: block;
  font-size: 18px;
}
.comparison-stat strong.tone-good {
  color: #1f7a3f;
}
.comparison-stat strong.tone-mid {
  color: #9d6a00;
}
.comparison-stat strong.tone-bad {
  color: #b23322;
}
.comparison-stat strong.tone-missing {
  color: #7d838a;
}
.comparison-stat span {
  display: block;
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
}
.comparison-delta {
  font-size: 13px;
  line-height: 1.4;
}
.comparison-delta.tone-good {
  color: #1f7a3f;
}
.comparison-delta.tone-mid {
  color: #9d6a00;
}
.comparison-delta.tone-bad {
  color: #b23322;
}
.comparison-delta.tone-missing {
  color: #7d838a;
}
@media (max-width: 960px) {
  .page {
    grid-template-rows: minmax(100vh, 100dvh) auto;
  }
  .map-stage {
    grid-template-areas:
      "map"
      "legend";
    grid-template-columns: 1fr;
    grid-template-rows: minmax(62vh, 70dvh) auto;
    min-height: auto;
  }
  #map {
    height: 62vh;
    height: 62dvh;
    min-height: 62vh;
    min-height: 62dvh;
  }
  .insights {
    grid-template-columns: 1fr;
  }
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  .comparison-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .legend {
    border-right: 0;
    border-top: 1px solid var(--line);
    box-shadow: none;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    background: #fff;
  }
  .page {
    display: block;
  }
  .map-stage {
    grid-template-areas: "legend map";
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: auto;
    break-inside: avoid-page;
  }
  #map {
    height: 170mm;
    min-height: 170mm;
  }
  .legend {
    border: 1px solid var(--line);
    border-right: 0;
    box-shadow: none;
  }
  .panel {
    box-shadow: none;
    border: 1px solid var(--line);
    break-inside: avoid-page;
  }
  .leaflet-control-container {
    display: none;
  }
  .marker-svg {
    filter: none;
  }
}
</style>
</head>
<body>
<div class="page">
  <div class="map-stage">
    <div class="legend">
      <h1>GTD GP Practice Experience Map</h1>
      <p>424 GP surgery profiles from a broad catchment around GTD anchors.</p>
      <p>3,021,833 registered patients across 360 practices.</p>
      <div class="control-group">
        <h2>Score Source</h2>
        <div class="segmented">
          <label><input type="radio" name="score-source" value="google" checked><span>Google</span></label>
          <label><input type="radio" name="score-source" value="survey"><span>GP Survey</span></label>
          <label><input type="radio" name="score-source" value="gap"><span>Gap</span></label>
        </div>
        <p id="metric-description" class="hint"></p>
      </div>
      <div class="control-group">
        <div id="voronoi-control">
          <label title="An estimated population/affected-people view. This is a rough vibes layer, not a real practice boundary map."><input type="checkbox" id="voronoi-toggle"><span>Est. population</span></label>
        </div>
      </div>
      <h2>Management</h2>
      <p id="manager-hint" class="hint"></p>
      <div id="manager-list" class="manager-list"></div>
    </div>
    <div id="map"></div>
  </div>
  <div class="insights">
    <section class="panel comparison-panel">
      <h2 id="comparison-heading">Interactive Benchmarks</h2>
      <p id="comparison-note" class="hint"></p>
      <div id="comparison-grid" class="comparison-grid"></div>
    </section>
    <section class="panel comparison-panel">
      <h2>Completion Rate vs Score</h2>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source.</p>
    </section>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@turf/turf@7.2.0/turf.min.js"></script>
<script>
const rows = [{"code": "Y02849", "name": "City Health Centre", "lat": 53.4827, "lon": -2.24292, "postcode": "M1 1PL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.5, "google_count": 11, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02849-city-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/city-health-centre/Y02849", "gtd_url": "https://www.gtdhealthcare.co.uk/cityhealthcentre", "nearby": "City Health Centre, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 9, "survey_sent_out": 957, "survey_sent_back": 85, "registered_patient_count": 15321}, {"code": "Y02960", "name": "New Bank Health", "lat": 53.4601, "lon": -2.20437, "postcode": "M12 4JE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 163, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02960-new-bank-health.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/new-bank-health/Y02960", "gtd_url": "https://www.gtdhealthcare.co.uk/newbankhealthcentre", "nearby": "City Health Centre, Droylsden Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 942, "survey_sent_back": 98, "registered_patient_count": 6419}, {"code": "Y02713", "name": "Guide Bridge Medical Practice", "lat": 53.4716, "lon": -2.11327, "postcode": "M34 5HY", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 116, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02713-guide-bridge-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/guide-bridge-medical-practice/Y02713", "gtd_url": "https://www.gtdhealthcare.co.uk/guidebridgemedicalpractice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 53, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 531, "survey_sent_back": 122, "registered_patient_count": 4478}, {"code": "Y02520", "name": "Simpson Medical Practice", "lat": 53.514, "lon": -2.19802, "postcode": "M40 9NB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 104, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02520-simpson-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/simpson-medical-practice/Y02520", "gtd_url": "https://www.gtdhealthcare.co.uk/simpsonmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 463, "survey_sent_back": 76, "registered_patient_count": 5375}, {"code": "Y02663", "name": "Droylsden Medical Practice", "lat": 53.4872, "lon": -2.14565, "postcode": "M43 7NP", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 85, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02663-droylsden-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/droylsden-medical-practice/Y02663", "gtd_url": "https://www.gtdhealthcare.co.uk/droylsdenmedicalpractice", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 49, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 550, "survey_sent_back": 100, "registered_patient_count": 4388}, {"code": "Y02325", "name": "Charlestown MD", "lat": 53.5226, "lon": -2.18689, "postcode": "M9 7ED", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 109, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02325-charlestown-md.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlestown-md/Y02325", "gtd_url": "https://www.gtdhealthcare.co.uk/charlestownmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Lindley Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 59, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 621, "survey_sent_back": 106, "registered_patient_count": 5268}, {"code": "Y02875", "name": "Lindley House Health Centre", "lat": 53.5438, "lon": -2.11693, "postcode": "OL1 1NL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 66, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02875-lindley-house-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/lindley-house-health-centre/Y02875", "gtd_url": "https://www.gtdhealthcare.co.uk/lindleymedicalpractice", "nearby": "Lindley Medical Practice, Mossley Medical Practice", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 722, "survey_sent_back": 129, "registered_patient_count": 4895}, {"code": "P89612", "name": "Mossley Medical Practice", "lat": 53.514, "lon": -2.04062, "postcode": "OL5 9AB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 3.7, "google_count": 16, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89612-mossley-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mossley-medical-practice/P89612", "gtd_url": "https://www.gtdhealthcare.co.uk/mossleymedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 423, "survey_sent_back": 95, "registered_patient_count": 2197}, {"code": "P89011", "name": "Gordon Street Medical Centre", "lat": 53.4929, "lon": -2.07804, "postcode": "OL6 6NE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.5, "google_count": 86, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89011-gordon-street-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/gordon-street-medical-centre/P89011", "gtd_url": "https://www.gtdhealthcare.co.uk/gordonstreetmedicalcentre", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 61, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 517, "survey_sent_back": 113, "registered_patient_count": 5181}, {"code": "Y02586", "name": "Ashton Gp Service", "lat": 53.4858, "lon": -2.09997, "postcode": "OL6 7SR", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 91, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02586-ashton-gp-service.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ashton-gp-service/Y02586", "gtd_url": "https://www.gtdhealthcare.co.uk/ashtongpservice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 52, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 569, "survey_sent_back": 88, "registered_patient_count": 5171}, {"code": "P89013", "name": "Hattersley Group Practice", "lat": 53.4502, "lon": -2.02741, "postcode": "SK14 3EH", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 72, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89013-hattersley-group-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/hattersley-group-practice/P89013", "gtd_url": "https://www.gtdhealthcare.co.uk/hattersleygrouppractice", "nearby": "Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 41, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 531, "survey_sent_back": 117, "registered_patient_count": 5011}, {"code": "P89602", "name": "The Smithy Surgery", "lat": 53.4611, "lon": -1.99579, "postcode": "SK14 8LJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.0, "google_count": 23, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89602-the-smithy-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-smithy-surgery/P89602", "gtd_url": "https://www.gtdhealthcare.co.uk/thesmithysurgery", "nearby": "Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 78, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 364, "survey_sent_back": 109, "registered_patient_count": 3747}, {"code": "Y02936", "name": "Millbrook Medical Practice", "lat": 53.4923, "lon": -2.03427, "postcode": "SK15 3BJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.7, "google_count": 39, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02936-millbrook-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/millbrook-medical-practice/Y02936", "gtd_url": "https://www.gtdhealthcare.co.uk/millbrookmedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 565, "survey_sent_back": 111, "registered_patient_count": 3505}, {"code": "P82013001", "name": "Dr Y Loomba & Partner", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.0, "google_count": 10, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82013001-dr-y-loomba-and-partner.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-y-loomba-and-partner/P82013001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82012", "name": "Octagon Medical Centre", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 308, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82012-octagon-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/octagon-medical-centre/P82012", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 24, "survey_sent_out": 665, "survey_sent_back": 161, "registered_patient_count": 6254}, {"code": "P82022", "name": "Dr Rizwan and Dr Awan", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.7, "google_count": 6, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82022-dr-rizwan-and-dr-awan.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-rizwan-and-dr-awan/P82022", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 535, "survey_sent_back": 115, "registered_patient_count": 5594}, {"code": "P82029", "name": "Halliwell Surgery 2", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82029-halliwell-surgery-2.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-2/P82029", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 96, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 530, "survey_sent_back": 110, "registered_patient_count": 3586}, {"code": "P82626", "name": "Halliwell Surgery 3", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82626-halliwell-surgery-3.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-3/P82626", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 82, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 653, "survey_sent_back": 121, "registered_patient_count": 5173}, {"code": "P82634", "name": "Wyresdale Road Surgery", "lat": 53.5816, "lon": -2.45218, "postcode": "BL1 4DN", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.7, "google_count": 9, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634-wyresdale-road-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/wyresdale-road-surgery/P82634", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 77, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 558, "survey_sent_back": 107, "registered_patient_count": 3995}, {"code": "P82010", "name": "Dalefield Surgery", "lat": 53.5882, "lon": -2.4518, "postcode": "BL1 4JP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dalefield-surgery/P82010", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 494, "survey_sent_back": 109, "registered_patient_count": 7962}, {"code": "Y02319", "name": "Bolton General Practice", "lat": 53.5782, "lon": -2.43495, "postcode": "BL1 4TH", "gtd": false, "management_company": "SSP Health", "affiliated_group": "", "google_score": 1.8, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-general-practice/Y02319", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 65, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 845, "survey_sent_back": 148, "registered_patient_count": 7694}, {"code": "P82031", "name": "Heaton Medical Centre", "lat": 53.588, "lon": -2.46831, "postcode": "BL1 5PU", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/heaton-medical-centre/P82031", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 393, "survey_sent_back": 116, "registered_patient_count": 10727}, {"code": "P82014", "name": "Spring House Surgery", "lat": 53.5884, "lon": -2.46354, "postcode": "BL1 6AF", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.1, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/spring-house-surgery/P82014", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 6457}, {"code": "P82627", "name": "Cornerstone Surgery", "lat": 53.5887, "lon": -2.45916, "postcode": "BL1 6AH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 41, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82627-cornerstone-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/cornerstone-surgery/P82627", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 79, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 414, "survey_sent_back": 105, "registered_patient_count": 4230}, {"code": "P82023", "name": "Mandalay Medical Centre", "lat": 53.6106, "lon": -2.4321, "postcode": "BL1 7LR", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mandalay-medical-centre/P82023", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 34, "survey_sent_out": 376, "survey_sent_back": 127, "registered_patient_count": 8580}, {"code": "P82634001", "name": "Drs Karim & James-Authe", "lat": 53.596, "lon": -2.45072, "postcode": "BL1 8BZ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.5, "google_count": 19, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82634001-drs-karim-and-james-authe.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/drs-karim-and-james-authe/P82634001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "Y03079", "name": "Bolton Community Practice", "lat": 53.5963, "lon": -2.43067, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.0, "google_count": 4, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bolton-community-practice/Y03079", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 25, "survey_sent_out": 530, "survey_sent_back": 133, "registered_patient_count": 16122}, {"code": "P82025", "name": "Burnside Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "ehealthservice.co.uk", "affiliated_group": "", "google_score": 1.8, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/burnside-surgery/P82025", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 467, "survey_sent_back": 99, "registered_patient_count": 4423}, {"code": "P82625", "name": "Charlotte Street Surgery", "lat": 53.5904, "lon": -2.42776, "postcode": "BL1 8TT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.3, "google_count": 33, "google_source_note": "Google Maps direct search", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlotte-street-surgery/P82625", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 73, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 8, "survey_sent_out": 936, "survey_sent_back": 76, "registered_patient_count": 2356}, {"code": "P82607", "name": "Crompton View Surgery", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 7, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82607-crompton-view-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/crompton-view-surgery/P82607", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 89, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 450, "survey_sent_back": 137, "registered_patient_count": 6045}, {"code": "P82021", "name": "The Oaks Family Practice", "lat": 53.5975, "lon": -2.41521, "postcode": "BL1 8UP", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.9, "google_count": 33, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82021-the-oaks-family-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-oaks-family-practice/P82021", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 88, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 412, "survey_sent_back": 136, "registered_patient_count": 6964}, {"code": "P82033", "name": "Bradford Street Surgery", "lat": 53.5768, "lon": -2.41821, "postcode": "BL2 1HT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.8, "google_count": 4, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82033-bradford-street-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/bradford-street-surgery/P82033", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 586, "survey_sent_back": 129, "registered_patient_count": 1996}, {"code": "P82016001", "name": "Tonge Moor Health Centre", "lat": 53.5891, "lon": -2.40904, "postcode": "BL2 2LW", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 9, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-moor-health-centre/P82016001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82016", "name": "Harwood Medical Centre", "lat": 53.6041, "lon": -2.39814, "postcode": "BL2 3HQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.2, "google_count": 10, "google_source_note": "Just Visits exact listing match", "google_text_file": "", "nhs_url": "https://www.nhs.uk/services/gp-surgery/harwood-medical-centre/P82016", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 32, "survey_sent_out": 374, "survey_sent_back": 119, "registered_patient_count": 12086}, {"code": "P82011", "name": "Tonge Fold Health Centre", "lat": 53.5795, "lon": -2.40532, "postcode": "BL2 6DY", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.9, "google_count": 42, "google_source_note": "Google Maps direct search with visible recent reviews (weak name match)", "google_text_file": "google-review-texts/P82011-tonge-fold-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/tonge-fold-health-centre/P82011", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 90, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 33, "survey_sent_out": 397, "survey_sent_back": 130, "registered_patient_count": 6969}, {"code": "P82018", "name": "The Alastair Ross Medical Practice", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 2.6, "google_count": 60, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82018-the-alastair-ross-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-alastair-ross-medical-practice/P82018", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 75, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 541, "survey_sent_back": 121, "registered_patient_count": 7491}, {"code": "P82001", "name": "The Dunstan Partnership", "lat": 53.5824, "lon": -2.38426, "postcode": "BL2 6NT", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.0, "google_count": 59, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82001-the-dunstan-partnership.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-dunstan-partnership/P82001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 84, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 27, "survey_sent_out": 428, "survey_sent_back": 114, "registered_patient_count": 10157}, {"code": "Y03079003", "name": "Little Lever Health Centre & Library", "lat": 53.5623, "lon": -2.37194, "postcode": "BL3 1HH", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 5.0, "google_count": 2, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y03079003-little-lever-health-centre-and-library.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/little-lever-health-centre-and-library/Y03079003", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null,
The file is too long and its contents have been truncated.


#### Plugin (file_search):
Make sure to include fileciteturn16file5 in your response to cite this file, or to surface it as a link.
### New Bank Health Centre Patient Survey Summary

The document provided is a detailed report on patient satisfaction with the New Bank Health Centre GP practice, focusing on metrics such as ease of contact, appointment experiences, and overall satisfaction. 

#### Key Failure Areas Impacting Access

1. **Difficulty in Contacting the Practice**
   - **Phone Contact:**
     - **Failure Rate:** 39% of patients do not find it easy to get through to the practice by phone.
     - **Breakdown:** 
       - 10% find it fairly difficult.
       - 12% find it very difficult.
       - 18% are neutral, which may also suggest dissatisfaction.
     - **Comparison:** This is better than the national average (47% do not find it easy), but 39% is still a substantial barrier.
   - **Website Contact:**
     - **Failure Rate:** 27% do not find it easy to contact the practice via the website.
     - **Breakdown:** 
       - 10% find it fairly difficult.
       - 8% find it very difficult.
       - 9% are neutral.
     - **Comparison:** Outperforms the national average (49% do not find it easy), yet 27% still struggle.
   - **NHS App Contact:**
     - **Failure Rate:** 40% do not find it easy to contact the practice using the NHS App.
     - **Breakdown:** 
       - 10% find it fairly difficult.
       - 18% find it very difficult.
       - 11% are neutral.
     - **Comparison:** Better than the national average (51% do not find it easy), but 40% is a high failure rate.
   - **Impact:** These initial contact methods are critical gateways to care. With 39% struggling by phone, 27% via the website, and 40% via the NHS App, a significant portion of patients face barriers before they can even request an appointment. This likely discourages or prevents many from accessing services altogether.

2. **Lack of Clarity After Contact**
   - **Failure Rate:** 25% of patients did not know what the next step would be after contacting the practice (75% knew).
   - **Breakdown:** 
     - 12% explicitly said "no."
     - 13% were told to contact the practice again another day, indicating inefficiency.
   - **Comparison:** Worse than the national average (17% do not know).
   - **Impact:** A quarter of patients leaving without clear guidance may delay care or give up, especially if they must repeatedly attempt contact. This inefficiency exacerbates access issues.

3. **Poor Experience in Contacting the Practice**
   - **Failure Rate:** 34% do not describe their experience of contacting the practice as good (66% say it’s good).
   - **Breakdown:** 
     - 17% rate it as neither good nor poor.
     - 7% as fairly poor.
     - 10% as very poor.
   - **Comparison:** Worse than the national average (30% do not rate it as good).
   - **Impact:** A third of patients having a subpar contact experience reflects systemic issues in responsiveness, potentially deterring future attempts to access care.

4. **Limited Choice in Appointments**
   - **Failure Rate:** 
     - 34% were not offered a choice of time or day.
     - 89% were not offered
The file is too long and its contents have been truncated.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
The useful frame is not “why does this rubbish company keep buying practices?” They are not paying to buy them. These are commissioner-paid service contracts. APMS is the flexible GP-contract route that lets ICBs award primary care work to organisations other than ordinary GP partnerships, including third-sector and other provider bodies. In the Manchester tender, New Bank had **7 bids**, Charlestown **6**, Simpson **8**, City Health Centre **11**; GTD won four Manchester lots, Northern Health GPPO won Victoria Mill, Hope Citadel won Droylsden and Hawthorn, and Rochdale Health Alliance won the Bolton and HMR lots. That already tells you the market is a small regional pool of repeat players, not some huge national open field. citeturn846681view1turn356478view0turn821030view1turn821030view2turn821030view4

Who sits around GTD is revealing. GTD says **Our People’s Trust** is its single shareholder. Manchester Primary Care Partnership says it is a **not-for-profit** owned by the three Manchester GP federations: **Northern Health GPPO**, **Primary Care Manchester**, and **South Manchester GP Federation**. Northern Health GPPO is itself described publicly as a not-for-profit GP federation with full north-Manchester practice membership. Salford Primary Care Together is a **CIC**. Mastercall says it is a **social enterprise**, and CQC’s background note says it grew out of the Stockport Doctors’ Co-operative. So the immediate peer group around GTD is mostly federations, CICs and social enterprises, not classic shareholder-maximising chains. citeturn583409view3turn311963search2turn311963search5turn311963search1turn311963search4turn311963search3turn311963search6

There is another layer too: these organisations collaborate as well as compete. GMUPCA describes itself as a non-exclusive alliance of **Bardoc, gtd healthcare, Mastercall Healthcare, Salford Primary Care Together and Wigan GP Alliance**, and its team page puts **David Beckett** alongside the CEOs of Mastercall and Bardoc in the same alliance structure. That means the same small set of provider bodies are often the people the system turns to for urgent care, out-of-hours, streaming, SAS-type work and hard-to-mobilise contracts. It is a dense ecosystem. citeturn583409view5turn583409view6

That also helps answer “who is doing better, who is failing similarly?” Officially, several peers look more stable on the regulator side: Bardoc’s listed services show multiple **Good** ratings, Victoria Mill under Northern Health GPPO is **Good**, and SPCT Practices is **Good**. But your local data suggests patient-facing reputation is patchier and not unique to GTD. In your own map, GTD’s Manchester/Tameside cluster includes **New Bank 1.9**, **Guide Bridge 1.8**, **Simpson 1.8**, **Droylsden 1.8**, **Charlestown 1.9**, **Gordon Street 1.5**, **Ashton 1.8**, **Hattersley 2.1**, with **The Smithy 4.0** as a notable exception. Nearby peers are mixed rather than spotless: **Hawthorn** under Hope Citadel is **3.0**, and **Bolton General Practice** under SSP Health is **1.8** in your scope. So GTD is not alone in struggling, but the GTD cluster is unusually consistent. citeturn583409view8turn311963search20turn583409view9turn16file3turn15file8turn16file4

Why commissioners keep using GTD is much less mysterious once you read the committee papers. They are not selecting on Google reviews. They are selecting on continuity, tariff, estates, willingness to hold risk, and ability to mobilise. Stockport’s July 2024 paper says it had already negotiated GTD’s SAS tariff down to be competitive with other GM contracts, said GTD had “worked collaboratively” with the primary care team, and said activity was tracking toward a **40% reduction** versus the previous year while keeping within budget; the committee approved a direct award on that basis. In September 2024 the minutes say the provider met all quality requirements. Manchester’s May 2025 SAS paper is even blunter: lack of appetite for SAS had been common, several previous expressions of interest had been unsuccessful, and Northern Health GPPO was chosen because it had prior SAS experience, appropriate estate, no significant prior quality issues, and agreed to run it **within the existing budget**. That is the commissioning logic. citeturn451515view0turn451515view1turn451515view2turn675114view6turn675114view3turn675114view4

The squeeze has names. **NHS England** defines the contract framework and uses APMS precisely for locally flexible, harder-to-structure services, including groups like asylum seekers or homeless populations. **NHS Greater Manchester ICB** and locality committees squeeze on tariff, budget and continuity. **NECS** runs the procurement machinery. Estate availability becomes a hard constraint on who can bid and who can safely run services. Manchester’s own papers also show wider commissioner-side capacity thinning out: even nursing-support roles were being delayed or ended because of reduced ICB workforce and financial pressures. And GTD is hiring into a brutal wage ladder at the same time: current NHS Jobs listings on GTD’s site include a **part-time receptionist at £24,675**, ACP/ANP roles at **£55,157–£68,544**, and a Head of Specialist Services role explicitly describing GTD as a £49m-turnover provider. citeturn846681view1turn723457view0turn583409view4

My best read of the mechanism is this. GTD’s own description of itself is not “we run a few GP surgeries.” It runs GP practices, urgent care, a **24/7 clinical and non-clinical co-ordination centre and call-handling service**, and referral triage/gateway services. That kind of organisation is structurally inclined toward triage, queue control, escalation rules, throughput and central oversight. Your repo’s complaints about New Bank are exactly in that failure mode: mandatory unscheduled office-hours callbacks, requests getting deleted, digital-only routing, unclear next steps, and care feeling like a production line rather than a relationship. That does not prove malice. It does suggest that GTD’s operating model can drift into protecting flow and risk exposure at the expense of continuity and humane access when a site is already under stress. citeturn162729view0turn162729view1turn16file0turn16file1turn16file5

The employee-review layer is thin and anecdotal, but it points the same way. GTD’s Indeed page currently shows **2.8/5 for pay and benefits**, **2.8 for management**, **3.0 for culture**, **3.3 for work-life balance** across seven reviews; the latest entries include “unsafe environment,” “understaffed,” and “overwhelming workload,” though there are also positive reviews from finance/governance roles. Hope Citadel’s tiny sample talks about challenging patient contact and no progression. Mastercall’s sample is small and a bit more positive overall. I would treat that as weak signal, not evidence, but it fits the official story of a stressed sector where the front line feels the strain first. citeturn495253view0turn495253view1turn495253view2

The part you can actually needle is not abstract “competence”, it’s the operating choices that a squeezed triage-heavy provider makes. The simple fixes are boring and testable: stop deleting requests after missed calls; hold requests open and requeue them; offer scheduled callback windows; give patients a direct phone/email route for unresolved cases; separate admin sorting from clinician triage so not every contact becomes an unpredictable doctor callback; assign a named owner for unresolved episodes so diagnostic work does not fragment; publish site-level measures like abandoned calls, request-closure reasons, callback miss rates, median wait to meaningful contact, and repeat-contact loops. Even Manchester’s replacement SAS model explicitly promised a **direct phone line**, **email address**, a named contact, and dedicated admin triage. Your own project is already asking for the same family of changes. That is where the leverage is. citeturn675114view3turn16file1turn16file5turn16file0

So the strong public-interest line is not “GTD are crooks.” It is: **Greater Manchester relies on a small network of federations, CICs and social-enterprise-style providers to absorb the awkward end of primary care; GTD is one of the main risk-absorbers in that network; commissioners reward continuity, estate and budget discipline more than patient-experience signals; and under those pressures GTD appears to default to organisationally protective front-door designs that ration access by friction.** That is a structural argument, it is well-supported, and it gives you named pressures and named bodies to go after rather than just shouting at one practice. citeturn583409view6turn451515view1turn675114view3turn723457view0turn16file0turn16file1

The next clean step is to build a one-page “pressure map” around GTD with four columns: commissioner pressures, labour-market pressures, estates/security pressures, and GTD’s own operating choices. That would make the argument much harder for them to brush off.


#### You:
We also want to find source data around this claim... ```Why commissioners keep using GTD is much less mysterious once you read the committee papers. They are not selecting on Google reviews. They are selecting on continuity, tariff, estates, willingness to hold risk, and ability to mobilise. Stockport’s July 2024 paper says it had already negotiated GTD’s SAS tariff down to be competitive with other GM contracts, said GTD had “worked collaboratively” with the primary care team, and said activity was tracking toward a 40% reduction versus the previous year while keeping within budget; the committee approved a direct award on that basis.```, that 40% reduction is a massive cost saving to the local authority (if I understand that right), but if all their practices are so obviously struggling to satisfy patients, is this where that tight budget is directly harming patients? Can we draw a direct line with hard data between saving money on the contract and the quality of patient experience at 'lowest bidder's holding the most risk. Like this looks like an institutional/incentives problem that needs to be identified, not just for change from the practices affected (who share a lot of the same issues caused by cost-cutting that forces patients into poor experience pathways and simple erorrs), but by actively degrading public health by making access harder, not easier (likewise having a closed PPG instead of an open one with auto-enrollment and active engagement, its like it's trying not to be fixed because change costs more money and eenergy to action than it has) 

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m pinning the money bits to actual committee papers first, then I’ll see what can and can’t be supported about patient harm with hard data. The likely answer is “strong institutional pattern, weak public causal proof unless we assemble a panel ourselves.”


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### Plugin (file_search):
Make sure to include fileciteturn18file0 in your response to cite this file, or to surface it as a link.
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GTD Greater Manchester GP Practice Experience</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {
  --bg: #f6f4ef;
  --ink: #1a1c1a;
  --panel: rgba(255,255,255,0.92);
  --panel-strong: rgba(255,255,255,0.98);
  --missing: #9aa0a6;
  --low: #c3472f;
  --midlow: #dc8c23;
  --midhigh: #d2b529;
  --high: #4c9a52;
  --veryhigh: #1c7c54;
  --line: rgba(26,28,26,0.12);
  --accent: #0f5e9c;
}
html, body {
  margin: 0;
}
body {
  font: 14px/1.4 Georgia, serif;
  color: var(--ink);
  background: radial-gradient(circle at top, #fff7e3, var(--bg));
}
.page {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-rows: minmax(100vh, 100dvh) auto;
}
.map-stage {
  display: grid;
  grid-template-areas: "legend map";
  grid-template-columns: 360px minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}
#map {
  grid-area: map;
  height: 100vh;
  height: 100dvh;
  min-height: 100vh;
  min-height: 100dvh;
}
.legend {
  grid-area: legend;
  position: relative;
  z-index: 10;
  background: var(--panel-strong);
  padding: 12px 14px;
  border-right: 1px solid var(--line);
  box-shadow: inset -1px 0 0 rgba(26, 28, 26, 0.04);
  max-width: none;
  overflow: auto;
}
.legend h1 {
  margin: 0 0 8px;
  font-size: 18px;
}
.legend p {
  margin: 0 0 8px;
}
.legend h2 {
  margin: 12px 0 8px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.legend .row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.legend .hint {
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.control-group {
  display: grid;
  gap: 8px;
}
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(15, 94, 156, 0.06);
}
#size-mode-control {
  grid-template-columns: 1fr 1fr;
}
#voronoi-control {
  display: flex;
  align-items: center;
  gap: 8px;
}
#voronoi-control input {
  display: inline-block;
}
.segmented label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
}
.segmented input {
  display: none;
}
.segmented span {
  width: 100%;
  text-align: center;
  border-radius: 999px;
  padding: 5px 8px;
}
.segmented input:checked + span {
  background: var(--accent);
  color: #fff;
}
.metric-note {
  margin-top: 6px;
  font-size: 11px;
  line-height: 1.35;
}
.manager-list {
  display: grid;
  gap: 8px;
  max-height: 210px;
  overflow: auto;
  padding-right: 4px;
}
.manager-option {
  display: grid;
  grid-template-columns: 18px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.manager-option input {
  margin: 0;
}
.manager-name {
  min-width: 0;
}
.manager-meta {
  color: rgba(26, 28, 26, 0.68);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.swatch {
  width: 14px;
  height: 14px;
  border: 1px solid rgba(0,0,0,0.25);
  flex: 0 0 auto;
}
.swatch.circle {
  border-radius: 999px;
}
.swatch.square {}
.swatch.diamond {
  transform: rotate(45deg);
}
.swatch.triangle {
  clip-path: polygon(50% 0, 0 100%, 100% 100%);
}
.swatch.hexagon {
  clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);
}
.swatch.pentagon {
  clip-path: polygon(50% 0, 100% 38%, 81% 100%, 19% 100%, 0 38%);
}
.leaflet-marker-icon.marker-icon {
  background: transparent;
  border: 0;
}
.marker-svg {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.22));
}
.leaflet-popup-content {
  min-width: 220px;
}
.leaflet-popup-content a {
  word-break: break-word;
}
.insights {
  padding: 18px 18px 26px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}
.panel {
  background: var(--panel-strong);
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}
.panel h2 {
  margin: 0 0 8px;
  font-size: 18px;
}
.panel p {
  margin: 0 0 10px;
}
.chart-frame {
  width: 100%;
  overflow-x: auto;
}
#scatterplot {
  width: 100%;
  height: 320px;
  display: block;
}
.chart-note {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.72);
}
.comparison-panel {
  grid-column: 1 / -1;
}
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.comparison-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255,255,255,0.72);
  padding: 12px 14px;
}
.comparison-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
}
.comparison-kicker {
  margin: 0 0 10px;
  color: rgba(26, 28, 26, 0.72);
  font-size: 12px;
}
.comparison-summary {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.45;
}
.comparison-summary p {
  margin: 0 0 10px;
}
.rank-bar {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}
.rank-bar-track {
  position: relative;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, #b23322 0%, #d7b74b 50%, #1f7a3f 100%);
  box-shadow: inset 0 0 0 1px rgba(26, 28, 26, 0.14);
  overflow: hidden;
}
.rank-bar-marker {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #fff;
  border: 2px solid rgba(26, 28, 26, 0.82);
  box-shadow: 0 2px 6px rgba(0,0,0,0.16);
  transform: translate(-50%, -50%);
}
.rank-bar-labels {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
  line-height: 1.35;
}
.rank-bar-labels span {
  color: rgba(26, 28, 26, 0.8);
}
.rank-bar-labels strong {
  color: #161816;
}
.rank-bar-labels .rank-worse {
  text-align: left;
}
.rank-bar-labels .rank-better {
  text-align: right;
}
.comparison-metrics {
  display: grid;
  gap: 8px;
}
.comparison-row {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 1.1fr;
  gap: 10px;
  align-items: baseline;
  padding: 8px 0;
  border-top: 1px solid rgba(26, 28, 26, 0.08);
}
.comparison-row:first-child {
  border-top: 0;
  padding-top: 0;
}
.comparison-label {
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.comparison-stat strong {
  display: block;
  font-size: 18px;
}
.comparison-stat strong.tone-good {
  color: #1f7a3f;
}
.comparison-stat strong.tone-mid {
  color: #9d6a00;
}
.comparison-stat strong.tone-bad {
  color: #b23322;
}
.comparison-stat strong.tone-missing {
  color: #7d838a;
}
.comparison-stat span {
  display: block;
  font-size: 12px;
  color: rgba(26, 28, 26, 0.68);
}
.comparison-delta {
  font-size: 13px;
  line-height: 1.4;
}
.comparison-delta.tone-good {
  color: #1f7a3f;
}
.comparison-delta.tone-mid {
  color: #9d6a00;
}
.comparison-delta.tone-bad {
  color: #b23322;
}
.comparison-delta.tone-missing {
  color: #7d838a;
}
@media (max-width: 960px) {
  .page {
    grid-template-rows: minmax(100vh, 100dvh) auto;
  }
  .map-stage {
    grid-template-areas:
      "map"
      "legend";
    grid-template-columns: 1fr;
    grid-template-rows: minmax(62vh, 70dvh) auto;
    min-height: auto;
  }
  #map {
    height: 62vh;
    height: 62dvh;
    min-height: 62vh;
    min-height: 62dvh;
  }
  .insights {
    grid-template-columns: 1fr;
  }
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  .comparison-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .legend {
    border-right: 0;
    border-top: 1px solid var(--line);
    box-shadow: none;
  }
}
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    background: #fff;
  }
  .page {
    display: block;
  }
  .map-stage {
    grid-template-areas: "legend map";
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: auto;
    break-inside: avoid-page;
  }
  #map {
    height: 170mm;
    min-height: 170mm;
  }
  .legend {
    border: 1px solid var(--line);
    border-right: 0;
    box-shadow: none;
  }
  .panel {
    box-shadow: none;
    border: 1px solid var(--line);
    break-inside: avoid-page;
  }
  .leaflet-control-container {
    display: none;
  }
  .marker-svg {
    filter: none;
  }
}
</style>
</head>
<body>
<div class="page">
  <div class="map-stage">
    <div class="legend">
      <h1>GTD GP Practice Experience Map</h1>
      <p>424 GP surgery profiles from a broad catchment around GTD anchors.</p>
      <p>3,021,833 registered patients across 360 practices.</p>
      <div class="control-group">
        <h2>Score Source</h2>
        <div class="segmented">
          <label><input type="radio" name="score-source" value="google" checked><span>Google</span></label>
          <label><input type="radio" name="score-source" value="survey"><span>GP Survey</span></label>
          <label><input type="radio" name="score-source" value="gap"><span>Gap</span></label>
        </div>
        <p id="metric-description" class="hint"></p>
      </div>
      <div class="control-group">
        <div id="voronoi-control">
          <label title="An estimated population/affected-people view. This is a rough vibes layer, not a real practice boundary map."><input type="checkbox" id="voronoi-toggle"><span>Est. population</span></label>
        </div>
      </div>
      <h2>Management</h2>
      <p id="manager-hint" class="hint"></p>
      <div id="manager-list" class="manager-list"></div>
    </div>
    <div id="map"></div>
  </div>
  <div class="insights">
    <section class="panel comparison-panel">
      <h2 id="comparison-heading">Interactive Benchmarks</h2>
      <p id="comparison-note" class="hint"></p>
      <div id="comparison-grid" class="comparison-grid"></div>
    </section>
    <section class="panel comparison-panel">
      <h2>Completion Rate vs Score</h2>
      <p id="scatter-summary" class="hint"></p>
      <div class="chart-frame">
        <svg id="scatterplot" viewBox="0 0 920 320" preserveAspectRatio="xMidYMid meet" aria-labelledby="scatter-title" role="img">
          <title id="scatter-title">Survey completion rate against selected score</title>
        </svg>
      </div>
      <p class="chart-note">Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source.</p>
    </section>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@turf/turf@7.2.0/turf.min.js"></script>
<script>
const rows = [{"code": "Y02849", "name": "City Health Centre", "lat": 53.4827, "lon": -2.24292, "postcode": "M1 1PL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.5, "google_count": 11, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02849-city-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/city-health-centre/Y02849", "gtd_url": "https://www.gtdhealthcare.co.uk/cityhealthcentre", "nearby": "City Health Centre, New Bank Health Centre, Simpson Medical Practice", "survey_overall_good_percent": 70, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 9, "survey_sent_out": 957, "survey_sent_back": 85, "registered_patient_count": 15321}, {"code": "Y02960", "name": "New Bank Health", "lat": 53.4601, "lon": -2.20437, "postcode": "M12 4JE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 163, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02960-new-bank-health.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/new-bank-health/Y02960", "gtd_url": "https://www.gtdhealthcare.co.uk/newbankhealthcentre", "nearby": "City Health Centre, Droylsden Medical Practice, New Bank Health Centre", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 10, "survey_sent_out": 942, "survey_sent_back": 98, "registered_patient_count": 6419}, {"code": "Y02713", "name": "Guide Bridge Medical Practice", "lat": 53.4716, "lon": -2.11327, "postcode": "M34 5HY", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 116, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02713-guide-bridge-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/guide-bridge-medical-practice/Y02713", "gtd_url": "https://www.gtdhealthcare.co.uk/guidebridgemedicalpractice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 53, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 23, "survey_sent_out": 531, "survey_sent_back": 122, "registered_patient_count": 4478}, {"code": "Y02520", "name": "Simpson Medical Practice", "lat": 53.514, "lon": -2.19802, "postcode": "M40 9NB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 104, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02520-simpson-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/simpson-medical-practice/Y02520", "gtd_url": "https://www.gtdhealthcare.co.uk/simpsonmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 80, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 16, "survey_sent_out": 463, "survey_sent_back": 76, "registered_patient_count": 5375}, {"code": "Y02663", "name": "Droylsden Medical Practice", "lat": 53.4872, "lon": -2.14565, "postcode": "M43 7NP", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 85, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02663-droylsden-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/droylsden-medical-practice/Y02663", "gtd_url": "https://www.gtdhealthcare.co.uk/droylsdenmedicalpractice", "nearby": "Ashton GP Service, Charlestown Medical Practice, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 49, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 550, "survey_sent_back": 100, "registered_patient_count": 4388}, {"code": "Y02325", "name": "Charlestown MD", "lat": 53.5226, "lon": -2.18689, "postcode": "M9 7ED", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.9, "google_count": 109, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02325-charlestown-md.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/charlestown-md/Y02325", "gtd_url": "https://www.gtdhealthcare.co.uk/charlestownmedicalpractice", "nearby": "Charlestown Medical Practice, Droylsden Medical Practice, Lindley Medical Practice, Simpson Medical Practice", "survey_overall_good_percent": 59, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 17, "survey_sent_out": 621, "survey_sent_back": 106, "registered_patient_count": 5268}, {"code": "Y02875", "name": "Lindley House Health Centre", "lat": 53.5438, "lon": -2.11693, "postcode": "OL1 1NL", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 66, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02875-lindley-house-health-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/lindley-house-health-centre/Y02875", "gtd_url": "https://www.gtdhealthcare.co.uk/lindleymedicalpractice", "nearby": "Lindley Medical Practice, Mossley Medical Practice", "survey_overall_good_percent": 72, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 18, "survey_sent_out": 722, "survey_sent_back": 129, "registered_patient_count": 4895}, {"code": "P89612", "name": "Mossley Medical Practice", "lat": 53.514, "lon": -2.04062, "postcode": "OL5 9AB", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 3.7, "google_count": 16, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89612-mossley-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/mossley-medical-practice/P89612", "gtd_url": "https://www.gtdhealthcare.co.uk/mossleymedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 83, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 423, "survey_sent_back": 95, "registered_patient_count": 2197}, {"code": "P89011", "name": "Gordon Street Medical Centre", "lat": 53.4929, "lon": -2.07804, "postcode": "OL6 6NE", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.5, "google_count": 86, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89011-gordon-street-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/gordon-street-medical-centre/P89011", "gtd_url": "https://www.gtdhealthcare.co.uk/gordonstreetmedicalcentre", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Lindley Medical Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 61, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 517, "survey_sent_back": 113, "registered_patient_count": 5181}, {"code": "Y02586", "name": "Ashton Gp Service", "lat": 53.4858, "lon": -2.09997, "postcode": "OL6 7SR", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 1.8, "google_count": 91, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02586-ashton-gp-service.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/ashton-gp-service/Y02586", "gtd_url": "https://www.gtdhealthcare.co.uk/ashtongpservice", "nearby": "Ashton GP Service, Droylsden Medical Practice, Gordon Street Medical Centre, Guide Bridge Medical Practice, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 52, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 15, "survey_sent_out": 569, "survey_sent_back": 88, "registered_patient_count": 5171}, {"code": "P89013", "name": "Hattersley Group Practice", "lat": 53.4502, "lon": -2.02741, "postcode": "SK14 3EH", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.1, "google_count": 72, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89013-hattersley-group-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/hattersley-group-practice/P89013", "gtd_url": "https://www.gtdhealthcare.co.uk/hattersleygrouppractice", "nearby": "Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 41, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 22, "survey_sent_out": 531, "survey_sent_back": 117, "registered_patient_count": 5011}, {"code": "P89602", "name": "The Smithy Surgery", "lat": 53.4611, "lon": -1.99579, "postcode": "SK14 8LJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 4.0, "google_count": 23, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P89602-the-smithy-surgery.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/the-smithy-surgery/P89602", "gtd_url": "https://www.gtdhealthcare.co.uk/thesmithysurgery", "nearby": "Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 78, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 30, "survey_sent_out": 364, "survey_sent_back": 109, "registered_patient_count": 3747}, {"code": "Y02936", "name": "Millbrook Medical Practice", "lat": 53.4923, "lon": -2.03427, "postcode": "SK15 3BJ", "gtd": true, "management_company": "GTD Healthcare", "affiliated_group": "", "google_score": 2.7, "google_count": 39, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/Y02936-millbrook-medical-practice.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/millbrook-medical-practice/Y02936", "gtd_url": "https://www.gtdhealthcare.co.uk/millbrookmedicalpractice", "nearby": "Ashton GP Service, Gordon Street Medical Centre, Hattersley Group Practice, Millbrook Medical Practice, Mossley Medical Practice, The Smithy Surgery", "survey_overall_good_percent": 69, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 20, "survey_sent_out": 565, "survey_sent_back": 111, "registered_patient_count": 3505}, {"code": "P82013001", "name": "Dr Y Loomba & Partner", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 1.0, "google_count": 10, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82013001-dr-y-loomba-and-partner.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-y-loomba-and-partner/P82013001", "gtd_url": "", "nearby": "", "survey_overall_good_percent": null, "survey_overall_good_ics_percent": null, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": null, "survey_sent_out": null, "survey_sent_back": null, "registered_patient_count": ""}, {"code": "P82012", "name": "Octagon Medical Centre", "lat": 53.5771, "lon": -2.43205, "postcode": "BL1 1SQ", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 4.0, "google_count": 308, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82012-octagon-medical-centre.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/octagon-medical-centre/P82012", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 74, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 24, "survey_sent_out": 665, "survey_sent_back": 161, "registered_patient_count": 6254}, {"code": "P82022", "name": "Dr Rizwan and Dr Awan", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.7, "google_count": 6, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82022-dr-rizwan-and-dr-awan.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/dr-rizwan-and-dr-awan/P82022", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 91, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 535, "survey_sent_back": 115, "registered_patient_count": 5594}, {"code": "P82029", "name": "Halliwell Surgery 2", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82029-halliwell-surgery-2.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-2/P82029", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 96, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 21, "survey_sent_out": 530, "survey_sent_back": 110, "registered_patient_count": 3586}, {"code": "P82626", "name": "Halliwell Surgery 3", "lat": 53.5883, "lon": -2.43172, "postcode": "BL1 3RG", "gtd": false, "management_company": "", "affiliated_group": "", "google_score": 3.1, "google_count": 37, "google_source_note": "Google Maps direct search with visible recent reviews", "google_text_file": "google-review-texts/P82626-halliwell-surgery-3.txt", "nhs_url": "https://www.nhs.uk/services/gp-surgery/halliwell-surgery-3/P82626", "gtd_url": "", "nearby": "", "survey_overall_good_percent": 82, "survey_overall_good_ics_percent": 77, "survey_overall_good_national_percent": 75, "survey_completion_rate_percent": 19, "survey_sent_out": 653, "survey_sent_back": 121, "registered_patient_count": 5173}, {"code": "P82634", "name": "Wyresdale Road Surgery", "lat": 53.5816, "lon": -2.45218, "postcode": "BL1
The file is too long and its contents have been truncated.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’ve got the commissioner-side half pinned: they explicitly talk about competitiveness, budget, tariff and continuity, and in at least one case they record patient engagement as “N/A”. The missing bit is a public table that says “we saved £X and satisfaction fell by Y” — I don’t think that exists openly, so I’m going to separate what’s provable from what’s only strongly suggestive.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
The source data for that claim is real, but it does **not** yet prove “cheapest bidder caused bad care.”

What the Stockport paper actually says is narrower. In the **17 July 2024** Stockport Primary Care Commissioning Committee paper, the locality says it had already negotiated a **reduced activity tariff** with GTD so the SAS contract was “competitive in line with other GM provider contracts,” and that if year-to-date activity carried on, it would mean a **40% reduction in activity levels** compared with the previous year’s contract, “therefore generating a financial efficiency on the budgeted contract value.” It also says the contract would stay on the **current activity-based tariff**, with close monitoring to keep activity and service costs within the annual budget. citeturn859229view0turn611190view2

That 40% figure is **not** a published “we cut the contract by 40%” number, and it is **not** a published pound saving. The paper does not disclose the SAS contract value, the tariff, or the actual activity counts. It just says fewer activity units than the previous year would create a budget efficiency. citeturn859229view0turn611190view0

There is an important nuance in the earlier Stockport record too. A **September 2023** Stockport quality flash said SAS activity had been high because of a small number of frequent attenders, and that **two individuals were removed at the end of July** with the full impact not yet visible. In the same September 2023 committee paper, Stockport asked for a **direct award** to GTD for another year, said it would test the market later, and noted negotiations were underway to **reduce the tariff for activity costs per patient seen**. That means the later “40% reduction” may be at least partly a **caseload / case-mix** story, not clean evidence that GTD somehow became more efficient. citeturn103110view0

The commissioner logic is also plainer than the shorthand made it sound. Stockport did **not** run a fresh open competition there and pick a “lowest bidder.” It proposed a **direct award** to the incumbent, justified by continuity, a nationally mandated service, a negotiated tariff, and contract monitoring. The July 2024 paper explicitly says **patient engagement was N/A**, and that performance, quality and safety would be monitored later “through contract processes.” In September 2024 the minutes add that the current provider met all quality requirements and that Stockport had considered an in-borough base but had **no suitable accommodation with security**. citeturn611190view1turn817222view6turn817222view7turn103110view0

Manchester’s own papers show the same incentive structure even more bluntly. In the **27 March 2025** Manchester risk log, the locality records that there was a lack of willing SAS providers, that the incumbent wanted about a **23% increase in contract value** to continue, and that if funding or provider capacity failed there was a risk that people would be unable to access primary care. The same risk log elsewhere says limited funding can lead to **unmet need, wider inequalities, increased acuity, more A\&E attendance and more non-elective admissions**. Then, in **May 2025**, Manchester moved SAS to **Northern Health GPPO** because it had prior SAS experience, ready estate, no significant reported quality issues, and agreed to deliver **within the existing budget**. Manchester also recorded a more patient-friendly service design there: pharmacist/GP/nurse input, admin triage, and a **direct phone line and email address** with a named contact. citeturn866109view3turn817222view5

That is the strongest public institutional story I can support: commissioners are rewarding **continuity, tariff fit, available premises/security, incumbent knowledge, and willingness to hold awkward risk inside a fixed budget**. That is not the same thing as saying they are explicitly rewarding patient experience, and it is not the same thing as saying GTD is always the cheapest. On the APMS side, NHS England’s own guidance says APMS is the flexible, time-limited contract route used for services outside ordinary GP contracting, which is exactly the kind of structure where recommissioning and budget pressure can dominate. citeturn859229view5turn859229view6

On the outcome side, your own uploaded catchment data does show GTD’s footprint looking materially worse than the rest: across the **13 GTD practices** in your map, the average Google score is about **2.43** and average GP Patient Survey “overall good” is about **64.3%**, versus about **3.31** and **77.8%** across the other practices in the same 424-practice catchment. GTD’s average survey response rate is also lower, about **18.6%** versus **23.7%**. fileciteturn18file0

But the direct causal jump you want is still missing in public. We do **not** have an open table showing, for each GTD contract, the tariff or annual value, staffing levels, appointment supply, abandoned calls, callback failures, complaints, FFT, GPPS and clinical-safety incidents over time. Without that, I can’t honestly say “Stockport saved £X on SAS and that directly degraded patient experience at GTD practices by Y.” What I can say is that the public record shows a system selecting providers partly on **budget compatibility and risk absorption**, while your local outcome data shows GTD’s patient experience is poor across much of its footprint. That is a strong incentives argument, not a proved causal estimate. citeturn859229view0turn817222view5 fileciteturn18file0

One correction to keep your repo clean: the official GP Patient Survey FAQ says the survey includes questions about the **last contact, including for those who were not able to get in touch**. So it is not true that GPPS simply excludes everyone driven away at the front door. The bigger methodological problem is response rate: nationally it was **25.8%** in 2025, while your GTD cluster is generally below that, and New Bank sits around **10%** in your file. That still leaves lots of room for non-response bias, just not total exclusion. citeturn466268view0turn466268view2 fileciteturn18file0

The clean next step is to FOI for a panel, not more narrative. Ask for, per contract and per quarter, the SAS/APMS contract value, tariff basis, activity volumes, staffing WTE by role, complaints, FFT, call-answer metrics, abandoned calls, digital-request closure reasons, and any remedial notices. That is the data that would let you stop saying “this looks like an incentives problem” and start saying “here is the mechanism.”


#### You:
can you fucking put that in plain speech, there's so many vague holes, it almost feels intentional... what are activity levels? sick patients? what? 'activity based tariff' is such a bullshit word/phrase. 'Cut the cotnract by 40%' is meaningless, cut it for what? pay? from what to what? etc. Speak like a person, not a corporate lawyer please.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m going back to the exact Stockport / Manchester papers and I’ll translate the jargon into normal English instead of repeating their wording.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. In normal English:

They did **not** say “we cut the contract by 40%.” That was me compressing their jargon too much.

What Stockport actually said was: GTD was being paid under an **activity-based tariff**, and they expected **40% less billed activity** this year than the year before. The paper does **not** explain the unit properly, which is part of why the language is so slippery. The closest it gets is saying they negotiated a lower tariff for **“activity costs per patient”** and, earlier, **“per patient seen.”** So the plain-English version is: **GTD gets paid partly based on how much SAS work it actually does, and Stockport thought the amount of payable work would be about 40% lower than the previous year.** That would save money against the budget. It does **not** necessarily mean staff pay was cut by 40%, or the whole contract price was cut by 40%, or the service was formally reduced by 40%. citeturn506174view0turn506174view1

The honest problem is that the public paper leaves a hole right where the important detail should be. It does **not** define what counts as an “activity” unit. From the wording, it looks like something like **patient contacts / appointments / cases seen under the SAS service**, because they talk about tariff “per patient” and “per patient seen.” But they do not publish the actual formula, the count, or the tariff. So anyone reading it is left to reverse-engineer what they mean. citeturn506174view0turn506174view1

There is also a boring possible explanation for some of that drop that has nothing to do with GTD suddenly getting efficient. In Stockport’s 2023 papers, they said SAS activity had been high because of **a small number of frequent attenders**, and that **two individuals were removed** at the end of July 2023, with the full effect not yet known. So when the 2024 paper later says activity was tracking 40% lower, that could partly just mean **fewer high-need / high-contact patients**, not “same patients, cheaper care.” citeturn506174view1

So the clean translation of the Stockport bit is:

**“We kept GTD on this difficult service without a fresh competition. We had already haggled them down on the price per unit of work. We expected the amount of chargeable work to be lower this year than last year. So we thought the budget would look better.”** citeturn506174view0turn506174view1

On Manchester, the numbers are a bit clearer. Manchester publicly said the SAS contract itself was worth **£120,174 a year**, plus a tiny **0.6% uplift**, and that **security costs were separate**. Then, in March 2025, Manchester said the incumbent wanted about a **23% increase** to keep going. In plain English: **GTD said the service wasn’t worth doing at the old price anymore and asked for roughly another £27.6k a year on top of the £120.2k base**. Manchester then switched provider instead. citeturn506174view2turn506174view3

And who replaced them? **Northern Health GPPO.** Manchester said it picked them because they had run SAS before, had a building ready, had no significant recent quality issues reported in that service, and agreed to do it **within the existing budget**. That paper also spells out a more patient-friendly setup than the vague GTD wording: direct phone line, direct email, named contact, admin person handling triage, and GP/nurse/pharmacist appointments. citeturn506174view4

So the uncomfortable but plain version is this:

**The public papers show commissioners thinking like contract managers first.**\
Not “are patients delighted?”\
More like:\
**Can someone keep this awkward service running?**\
**Do they have a safe building?**\
**Will they do it at a price we can live with?**\
**Can we avoid service collapse?** citeturn506174view0turn506174view4

That still does **not** give a clean public proof that “saving money caused worse patient experience.” The public docs are too vague for that. What they do show is the incentive structure: **budget pressure + hard-to-place patients + scarce willing providers + continuity worries**. That is exactly the sort of setup where a provider can end up building defensive systems that save hassle and contain risk, while patients experience them as obstructive, remote, and hard to get through. The mechanism is plausible. The hard proof would need better data than they publish. citeturn506174view0turn506174view3turn506174view4

The missing bits you’d want are very specific:

**What exactly is an activity unit?**\
**What was the old tariff and the new tariff?**\
**How many activity units were billed each year?**\
**How many actual patients were in the service?**\
**How many appointments / contacts per patient?**\
**What happened to complaints, access times, failed contacts, and outcomes while those costs were being squeezed?**

Without that, they get to hide behind mushy phrases like “activity-based tariff” and “financial efficiency.”

A sharper FOI here would ask for:

**the SAS tariff schedule, the definition of an activity unit, annual activity volumes, patient numbers, appointment/contact counts, complaints, and any service quality reports for Stockport and Manchester SAS from 2023 onward.**

That would turn this from “their jargon suggests cost pressure” into “here is the exact lever they pulled.”


#### You:
Okay great "GTD gets paid partly based on how much SAS work it actually does, and Stockport thought the amount of payable work would be about 40% lower than the previous year." (I'd love to know why they thought there would be 40% less demand, that sounds like a lot, but I guess with small numbers, it makes sense) this only applies to one practice tho, right? Anything like this for other GTD practices?

I suppose on the SAS system, it's a relatively small corner of the business (especially given the measly pay total), but I wonder about visibility of related issues when winning the contracts for other practices? Can you find the reasoning for those too? Or basically anything beynd the SAS tiny piece.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m checking both the public committee papers and your uploaded notes for anything that explains the non-SAS contracts in normal terms, not just procurement boilerplate. The key question is whether GTD kept winning because of explicit scoring logic, or because the system only had a small pool of willing operators.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
The APMS side is looking much thinner in public than the SAS side. The system says a lot about process, timelines and “due diligence”, but almost nothing public about why GTD beat the other bidders lot by lot. That gap itself is part of the answer.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. The **40% thing is SAS-only**, not “all GTD practices.”

More precisely, it is about **Stockport’s Special Allocation Scheme contract** with GTD, which is a separate high-risk service for patients removed from normal GP lists after violence or threats. Stockport said GTD would stay on an **activity-based tariff**, and that year-to-date activity was tracking about **40% lower than the previous year**, which would create a budget efficiency. That is not about New Bank, Charlestown, Simpson or City Health Centre ordinary GP contracts. It is about one weird corner service. citeturn976924view0turn853476view0

And even there, the public wording is frustratingly vague. They do not explain the unit properly, but their own words say they negotiated a lower tariff for activity costs **“per patient”** and earlier **“per patient seen.”** So the normal-language read is: **GTD gets paid partly based on how many SAS patients / patient contacts it handles, and Stockport expected fewer billable cases this year than last year.** citeturn976924view0turn853476view0

There are a couple of other public payment models, but not for ordinary GTD-run practices in the clean way you want.

Bolton’s SAS paper describes a **different** payment model entirely: that SAS contract was worth **£70,000** and paid in **12 equal monthly amounts regardless of how many patients were on the scheme**. So even inside SAS, different localities were paying in different ways. citeturn936189view0

Manchester’s SAS paper gives another variation: the SAS contract was around **£120,174 a year**, with **security funded separately**, and GTD later said it could not keep running it unless funding increased. Manchester then switched the SAS to **Northern Health GPPO**. So again, that is a special service with its own contract logic, not a normal practice contract. citeturn368758view0turn976924view3

For the ordinary GTD practices you care about, the public record looks different. The Manchester APMS contracts are published as **lot values over a long contract term**, not as “per patient seen” or “per appointment” prices. The tender notice says APMS contracts are **10 years from 1 April 2025, with an optional 5-year extension**, and the published lot values are the total contract values for that service lot. For GTD’s Manchester wins, the public values are **New Bank £12.1m**, **Charlestown £10.3m**, **Simpson £11.1m**, and **City Health Centre £26.7m** ex VAT. citeturn870763view0turn768887view0

So the short version is:

**SAS:** sometimes paid by activity / patient seen, sometimes fixed, sometimes with separate security budgets.\
**Ordinary APMS practice contracts:** publicly shown as long-term service contract values, not public per-activity tariffs. citeturn976924view0turn936189view0turn870763view0

On “can we find the reasoning for the other practices too?”, only partly.

What the public APMS papers do show is that this was a **full regional procurement**, not a casual handout. NHS GM says the three localities started with **RFIs in early 2023**, then ran a joint procurement with NECS support, using a Procurement Evaluation Strategy that covered **procurement objectives, methodology, timetable, evaluation strategy, recommended-bidder process, financial thresholds, risks/mitigation, market engagement reports and evaluation questions**. The public tender notice says the process was meant to test **capability, capacity and technical competence**. Across all nine lots, **73 bids** were received. citeturn525478search0turn976924view2turn870763view0

But the public record still **does not tell you why GTD beat the other bidders lot by lot**. It says there were three locality Recommended Bidder Reports, evaluation, consensus and due diligence, but those papers are not public. So we know the machinery existed; we do not have the scoring, moderation notes, or bidder-by-bidder strengths and weaknesses. citeturn976924view2

What we can say from the public bits:

GTD was **not** being handed everything. In Manchester, it won **New Bank, Charlestown, Simpson and City Health Centre**, but **Victoria Mill** went to Northern Health GPPO and **Droylsden / Hawthorn** went to Hope Citadel. GTD also had to **give up** the Manchester SAS when it said the funding no longer worked. So the system clearly was willing to award elsewhere. citeturn768887view0turn368758view0

Also, not all those GTD wins were the same kind of win. Manchester’s March 2025 paper says four of the seven Manchester APMS contracts stayed with their **incumbent providers**, including **Simpson** and **City Health Centre**. The three actual provider changes were **Droylsden away from GTD**, **Charlestown to GTD**, and **New Bank to GTD**. So for Simpson and City, GTD was mostly **holding on** to contracts it already had. The real fresh expansion in those Manchester practice lots was mainly **New Bank** and **Charlestown**. citeturn976924view1

There is one very relevant link between the SAS world and the ordinary APMS world: Manchester’s May 2025 paper says that during the 2024/25 APMS procurement, the locality **built the SAS service into the APMS service specification as a fallback option**, in case nobody volunteered to run SAS. In plain speech, winning one of the APMS practice contracts also made a provider part of the small pool the system could potentially lean on for this difficult specialist work. That is probably the clearest public sign that commissioners were thinking in terms of **provider resilience / willingness to absorb hard work**, not just “run one practice nicely.” citeturn368758view0turn976924view3

So where does that leave the bigger question?

There is **good public evidence** that SAS was treated as awkward, risky work with few willing providers, and that cost / continuity / estate / willingness mattered a lot there. There is **moderate public evidence** that the same regional procurement logic around capacity, competence and mobilisation shaped the ordinary APMS awards. There is **not yet public evidence** showing the exact scoring logic that made GTD beat rival bids at New Bank or Charlestown. citeturn368758view0turn870763view0turn976924view2

The missing records are now pretty specific:

the **Recommended Bidder Report** for each Manchester lot,\
the **evaluation matrix and moderation notes**,\
the **financial due-diligence pack**,\
the **mobilisation plans** for New Bank and Charlestown,\
and the **contract KPI schedules**.

Without those, the public story is basically:\
**they ran a formal process; GTD was one of a few repeat regional operators; GTD won some lots and lost others; and the public paperwork is much more open about continuity and mobilisation than it is about patient experience.** citeturn976924view2turn976924view1turn368758view0

The cleanest next move is an FOI that asks for the **lot-by-lot RBRs and scoring sheets** for New Bank and Charlestown specifically, because those are the two Manchester practice awards where GTD actually displaced another provider.


#### You:
You've hyperfocused on SAS because it's well documented, but move on... I want to know about any process involving GTD that we haven't covered anywhere in this chat or project so far.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
I’m doing a wider sweep now, not just SAS/APMS: anything GTD touches operationally or contractually that gives you a better map of how they function and where the failure modes might come from.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
A few overlooked threads are opening up: GTD has a much bigger central machinery than “a chain of GP practices” suggests — co-ordination centre, referral triage, patient-safety machinery, employee-trust governance, and a central complaints setup. Those are all candidate places where local practice problems can be created or amplified.


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Yes. The best genuinely new stuff is not another tender notice. It is the machinery behind GTD.

The first big thing is that GTD is not really “a company that runs some surgeries.” It runs a **central Clinical Hub** out of Denton, 24/7, handling things like **Alternative to Transfer**, **Acute Priority Assessment**, **acute visiting**, **SAS**, a **healthcare professional line**, and even **cover for GP half-day closures**. Their own site says staff in that hub manage patient flows and clinical assessments by phone and face to face, with multiple consultation modes. That means some of what feels like a local surgery problem may actually be coming from a central operating layer. citeturn987351view0turn878330search3

Second, GTD also runs **referral control**. Their Referral Gateway Clinical Triage Service says it reviews GP referrals for **Manchester Care Gateway**, **Warrington Referral Assistance Gateway**, and **St Helens Referral Management Service**, across **more than 25 specialties**, deciding whether a patient should stay in primary care, go to community care, or go to hospital, and what priority the referral should have. That is a much bigger role than “answer the phone at the practice.” It means GTD already operates in a system where **sorting, filtering and redirecting demand** is normalised work. citeturn716794view0

Third, their own website shows a more formal **safety and governance stack** than we’d talked about before. They publish a **Patient Safety Incident Response Framework** page with a policy and response plan, and their **patient safety partners** are described as sitting on governance and risk committees, reviewing safety data, helping shape the response plan, and working with the board on safety improvements. They also say they moved to an **employee-owned trust** structure in 2020, with an **Our People’s Trust Board** and an **Employee Connect Council** meant to feed staff views into governance. So there are named internal routes where “we knew this was going wrong” questions can be pushed, beyond just the practice manager. citeturn763448view0turn763448view1turn763448view2turn763448view3

The strongest new evidence, though, is buried in GTD’s own **2024 quality-improvement poster pack**. There is a poster about a **“digital front door” at Guide Bridge Medical Practice**. It spells out the implementation playbook: communications plan, PPG involvement, website and phone-message updates, text-message templates, a detailed SOP covering **staffing models**, **clinical and access pathways**, **clear escalation routes**, dashboards and auditable reporting, plus extra senior staff onsite at go-live. So GTD already has an internal blueprint for rolling out access changes properly. That matters because it means New Bank-style problems are not some mysterious thing they have never thought about. citeturn380209view0turn380209view1

That same Guide Bridge poster is also blunt about where it goes wrong. It says the system was open **7.30am to 4pm**, and the project’s own “challenges” included **patient concerns about accessibility**, **locums unfamiliar with the system**, **agency staff unfamiliar with Accurx**, and periods where **triage had to be closed early because of staffing shortages**. In the first month they say **1,142 requests** were received, versus **960 clinical appointments** in the pre-triage month they compare against. That is very close to the failure mode you keep describing: digital triage presented as fairness/efficiency, but heavily dependent on staffing, familiarity and front-door design. citeturn380209view1turn380209view2

There is an even nastier internal-governance finding in that same poster pack. GTD’s own project on **non-medical prescribing governance** says that after reviewing **226 non-medical prescribers**, **54%** of the clinicians with prescribing access rights had **incorrect prescribing rights**; only **67%** were fully compliant with GTD’s prescribing governance process; **33%** were practising outside the governance process, and **half of those were PCN-employed staff**. The same project says a wider clinical-system cleanse led to **1,456 colleagues being deactivated** from the clinical systems, with **354 more** needing deactivation but blocked by outstanding tasks. That is not a patient-review issue. That is internal control strain, mixed employment arrangements, and system hygiene. citeturn412524view3

Another seam we had not really pulled is GTD’s “rapid mobilisation” specialist work. Their internal materials say a **Community Health Protection Response Service** can mobilise bespoke services within **24–48 hours** across **care homes, schools, nurseries and universities**, and that “commissioner confidence” led to repeat rapid mobilisation and GTD becoming “the provider of choice.” Their migrant-health work was shortlisted for an HSJ Patient Safety Award; GTD says its **Migrant Health Passport** was built for asylum seekers and refugees who may be moved without notice, and Trafford papers show GTD got a **12-week contract** to support newly arrived asylum seekers at **Cresta Court**, doing initial health checks and vaccinations. Oldham papers separately show GM commissioning GTD for **Calm clinics** for residents with learning disability/autism and later a **mobile COVID vaccination** service. That gives you a very clear pattern: commissioners use GTD when they need somebody to stand something up fast in messy settings. citeturn412524view3turn274760search4turn699255view0turn699255view1turn699255view2

And GTD is still expanding outside the surgery portfolio. Public tender notices show **GoToDoc** got a **Central Lancashire Integrated Urgent Care Service** contract for **2025/26** worth **£9.54m**, awarded by direct award A because it had **Commissioner Requested Services** designation; GTD also got **Sefton Acute Home Visiting** for **2025–2028** at an annual value of **£961,121**, and another **Sefton acute home visiting urgent community response** contract at **£336,393 a year**. So the picture is not “they keep being given failing GP practices and nothing else.” It is “they are embedded in regional urgent/community infrastructure as well.” citeturn196690search0turn196690search2turn196690search5

One other new public process: NHS GM used the new **Provider Selection Regime** to award some **care-home primary care services**, and the January 2025 notice shows GTD winning some of that work too, on behalf of PCNs, including **Averill House**, **Brookdale View** and **Ringway Mews**. The notice says the scoring criteria were split evenly between **quality/innovation/integration**, **value**, **improving access and reducing health inequalities**, and **social value**, with all criteria met. So there is another GTD pipeline we had not talked about: not just running practices, but plugging into PCN/care-home commissioned work. citeturn680944view0

There is also a quieter but useful accountability route: GTD’s public contact pages route complaints to a **central complaints team**, say calls are recorded, and say the formal **complaints policy is available on request**. The Parliamentary and Health Service Ombudsman shows **7 complaints** about GTD in **2024/25**, with **4** decided at primary investigation. That is not a huge public caseload, but it gives you a traceable external complaints channel and a reason to ask GTD for complaint themes by service line, not just by practice. citeturn100007search0turn100007search7turn904156view0

So, the genuinely new processes worth digging are:

GTD’s **central Clinical Hub** and call/triage machinery.\
GTD’s **referral-gateway** role.\
GTD’s internal **access redesign playbooks**.\
GTD’s internal **governance failures around prescribing/system access**.\
GTD’s **rapid-mobilisation specialist services** for asylum, outbreaks, LD/autism clinics, vaccinations.\
GTD’s **care-home / PCN service work** under PSR.\
GTD’s **safety, complaints and employee-trust governance** routes. citeturn987351view0turn716794view0turn380209view0turn412524view3turn699255view0turn680944view0turn763448view0

The two biggest seams, for me, are the **Guide Bridge access poster** and the **non-medical prescribing governance poster**. One shows how GTD thinks about fixing access. The other shows how stretched/messy the internals may already be. Those are much closer to “why this keeps happening” than another Companies House filing.


#### You:
![image](sediment://file_00000000088c72439d862f1d50fd2eb9)
![image](sediment://file_0000000038a472439b310dd310127e45)
![image](sediment://file_00000000e75472438c66284f642dcb6a)
![image](sediment://file_00000000594072468b071c2771141e9d)
 summarise each image's cental info in one line

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
1. GTD has formal internal governance routes and a documented Guide Bridge “digital front door” rollout playbook, so access problems are not something the organisation is unaware of or unequipped to structure.

2. The public CQC picture for GTD’s Manchester tender sites is mostly stale or inherited, with New Bank, Charlestown and Simpson not yet properly inspected under the current provider, while City Health Centre is the one cleaner recent Good result.

3. Hattersley’s improvement appears to have come from basic governance and access fixes, while its later decline was tied more to management churn, staffing gaps and weak safety/governance than to patients suddenly thinking care staff were uncaring.

4. The Leslie Swindells case points to a serious role-design and triage failure at Hattersley, and GTD’s response shows it later changed escalation prompts, staff induction, appointment restrictions and triage design there.
