const embed = window.__MAP_EMBED__;
const nationalSupplementals = Array.isArray(window.NATIONAL_PRACTICE_SUPPLEMENTALS)
  ? window.NATIONAL_PRACTICE_SUPPLEMENTALS
  : [];
const rows = embed.rows;
const nationOrder = embed.nationOrder;
const cityCatchments = embed.cityCatchments;
const compositeRegionDefinitions = embed.compositeRegionDefinitions;
const PUBLISHED_CATCHMENT_INDEX_REL_PATH = embed.publishedCatchmentIndexRelPath;
const MANCHESTER_CATCHMENT_MIN_ZOOM = 12;
const northSouthDivide = embed.northSouthDivide;
const gtdGoogleTimeseries = embed.gtdGoogleTimeseries;
const gtdSurveyTimeseries = embed.gtdSurveyTimeseries;
const patientCountsByYear = embed.patientCountsByYear;
const patientChangeAnalysis = embed.patientChangeAnalysis;
const knownManagementCompanies = embed.knownManagementCompanies;
const deprivationGeojson = embed.deprivationGeojson;
const healthcareTerrainOverlays = Array.isArray(embed.healthcareTerrainOverlays)
  ? embed.healthcareTerrainOverlays
  : (embed.healthcareTerrainOverlay ? [embed.healthcareTerrainOverlay] : []);
const TERRAIN_OVERLAY_ORDER = ['england_catchment', 'england_out_of_area', 'scotland', 'wales', 'northern_ireland'];
const TERRAIN_OVERLAY_CONTROL_IDS = {
  england_catchment: 'healthcare-terrain-england-catchment-toggle',
  england_out_of_area: 'healthcare-terrain-england-out-of-area-toggle',
  scotland: 'healthcare-terrain-scotland-toggle',
  wales: 'healthcare-terrain-wales-toggle',
  northern_ireland: 'healthcare-terrain-northern-ireland-toggle',
};
const practiceDeprivationLookup = embed.practiceDeprivationLookup;
const allPracticeDeprivationLookup = embed.allPracticeDeprivationLookup;
const rowsByCode = new Map(rows.map((row) => [row.code, row]));
const NEW_BANK_CODE = 'Y02960';
const BASELINE_MANAGEMENT_COMPANY = 'GTD Healthcare';
const TREND_DEFAULT_CONTEXT_CODE = '__gtd_mean_with_new_bank__';
const LOCAL_RADIUS_MILES = 2.5;
const COMPOSITE_REGION_RADIUS_MILES = Number(embed.compositeRegionRadiusMiles ?? 5.0);
const SIDEBAR_COLLAPSE_KEY = 'mapSidebarCollapsed';
const LOW_ZOOM_MARKER_POOL_MAX_ZOOM = 10;
const LOW_ZOOM_MARKER_POOL_BASE_PRACTICES = 50;
const LOW_ZOOM_MARKER_POOL_CLOSE_ZOOM_PRACTICES = 100;
const LOW_ZOOM_MARKER_POOL_MOVE_THRESHOLD_PX = 24;
const LOW_ZOOM_MARKER_POOL_RERENDER_DELAY_MS = 70;
const LOW_ZOOM_MARKER_POOL_MAX_AGE_MS = 16000;
const selectedHealthcareTerrainOverlayIds = (() => {
  const availableOverlayIds = new Set(
    healthcareTerrainOverlays
      .map((overlay) => String(overlay?.overlayId || overlay?.nation || '').trim().toLowerCase())
      .filter(Boolean)
  );
  if (!availableOverlayIds.size) return new Set();
  return new Set();
})();
const dataBbox = (() => {
  const lons = rows.map(r => Number(r.lon));
  const lats = rows.map(r => Number(r.lat));
  const pad = 0.12;
  return [
    Math.min(...lons) - pad,
    Math.min(...lats) - pad,
    Math.max(...lons) + pad,
    Math.max(...lats) + pad
  ];
})();
const map = L.map('map').setView([embed.centerLat, embed.centerLon], embed.mapZoom ?? 11);
const markerLayer = L.layerGroup().addTo(map);
const nationalMarkerLayer = L.layerGroup().addTo(map);
const cityCircleLayer = L.layerGroup().addTo(map);
const sampleCircleLayer = L.layerGroup().addTo(map);
const catchmentOutlineLayer = L.layerGroup().addTo(map);
const serviceFinderPointLayer = L.layerGroup().addTo(map);
let voronoiLayer = null;
let deprivationLayer = null;
let healthcareTerrainLayers = [];
const nationalPane = map.createPane('nationalSupplementals');
nationalPane.style.zIndex = '350';
const healthcareTerrainPane = map.createPane('healthcareTerrain');
healthcareTerrainPane.style.zIndex = '240';
healthcareTerrainPane.style.pointerEvents = 'none';
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
const managementShapePool = ['triangle', 'square', 'diamond', 'hexagon', 'pentagon'];
const selectedManagementCompanies = new Set([BASELINE_MANAGEMENT_COMPANY]);
let activeMetric = 'google';
let activeGapMode = 'normalized';
let activeAreaOverlay = selectedHealthcareTerrainOverlayIds.size ? 'terrain' : null;
let focusedPracticeCode = NEW_BANK_CODE;
let pinnedTrendPracticeCode = TREND_DEFAULT_CONTEXT_CODE;
let hoveredTrendPracticeCode = null;
let trendLegendHoverSuppressed = false;
let sidebarCollapsed = false;
let patientTreemapYearIndex = null;
let patientTreemapPlaying = false;
let hoveredCatchmentCode = null;
const persistentCatchmentCodes = new Set();
let manchesterCatchmentIndex = null;
let manchesterCatchmentLoadPromise = null;
let manchesterCatchmentIndexMeta = null;
let manchesterCatchmentBundleLoadPromises = new Map();
let manchesterCatchmentLoadedBundleIds = new Set();
let manchesterCatchmentLoadError = '';
let serviceFinderArmed = false;
let serviceFinderPoint = null;
let serviceFinderLocationLabel = '';
let serviceFinderExtraArmed = false;
let serviceFinderExtraPoint = null;
let serviceFinderExtraLocationLabel = '';
let serviceFinderEmptyMessage = '';
let serviceFinderMatchedRows = null;
let serviceFinderHomeCodeSet = new Set();
let serviceFinderExtraCodeSet = new Set();
let serviceFinderMatchedCodeSet = new Set();
let serviceFinderOutOfAreaCodeSet = new Set();
let serviceFinderDistanceFallbackCodeSet = new Set();
let serviceFinderHomeDistanceFallbackCodeSet = new Set();
let serviceFinderExtraDistanceFallbackCodeSet = new Set();
let serviceFinderNationalDistanceFallbackCodeSet = new Set();
let serviceFinderEnglishMissingCatchmentCodeSet = new Set();
let serviceFinderMatchedStateKey = '';
let serviceFinderMatchLoadPromise = null;
let serviceFinderShowAllOutOfArea = false;
let serviceFinderOutOfAreaEligibleCount = 0;
let serviceFinderOutOfAreaVisibleCount = 0;
let serviceFinderDistanceFallbackVisibleCount = 0;
let serviceFinderButtonFlash = '';
let serviceFinderButtonFlashTimer = null;
let serviceFinderDragActive = false;
let serviceFinderDragGhost = null;
let serviceFinderSortKey = 'google';
let serviceFinderSortDirection = 'desc';
let serviceFinderOutOfAreaMiles = 5;
let serviceFinderOutOfAreaApplyTimer = null;
let patientTreemapTimer = null;
let patientTreemapNormalizeForChange = true;
let nationalDeprivationUsePopulation = false;
let completionScatterScope = 'regional';
const completionScatterNationOrder = (() => {
  const preferredOrder = ['england', 'scotland', 'wales', 'northern_ireland'];
  const allRows = rows.concat(nationalSupplementals);
  return preferredOrder.filter((nation) => allRows.some((row) => {
    if (String(row?.nation || '').trim().toLowerCase() !== nation) return false;
    return numericOrNull(row.survey_completion_rate_percent) !== null;
  }));
})();
let completionScatterNationIndex = 0;
let ratingSurveyMode = 'regions';
let showCityCircles = true;
let sampleCircleArmed = false;
let sampleCircleRadiusMiles = 6;
let sampleCircleCenter = null;
let lowZoomMarkerInterestLatLng = null;
let lowZoomMarkerInterestUpdatedAt = 0;
let lowZoomMarkerInterestRerenderTimer = null;
let lowZoomMarkerNearestPracticeCacheKey = '';
let lowZoomMarkerNearestPracticeCache = null;
const GTD_MEAN_COLOR = '#b23322';

const metricConfigs = {
  google: {
    title: 'Google rating',
    description: "Google data here is from this repo's merged review collection.",
    value(row) {
      return numericOrNull(row.google_score);
    },
    compareValue(_row) {
      return null;
    },
    markerLabel(row) {
      const value = this.value(row);
      return value === null ? '?' : value.toFixed(1);
    },
    markerColor(row) {
      const value = this.value(row);
      if (value === null) return '#9aa0a6';
      if (value < 2) return '#c3472f';
      if (value < 3) return '#dc8c23';
      if (value < 4) return '#d2b529';
      if (value < 4.5) return '#4c9a52';
      return '#1c7c54';
    },
    scaleCount(row) {
      const count = numericOrNull(row.google_count);
      return count !== null && count > 0 ? count : 0;
    },
    averageLabel(value) {
      return value === null ? '?' : value.toFixed(2);
    },
    axisLabel: 'Google rating',
    axisMin: 0,
    axisMax: 5
  },
  survey: {
    title: 'GP survey overall good %',
    description: 'GP Survey uses the official overall-experience-as-good percentage.',
    value(row) {
      return numericOrNull(row.survey_overall_good_percent);
    },
    compareValue(row) {
      return numericOrNull(row.survey_overall_good_ics_percent);
    },
    markerLabel(row) {
      const value = this.value(row);
      return value === null ? '?' : String(Math.round(value));
    },
    markerColor(row) {
      const value = this.value(row);
      if (value === null) return '#9aa0a6';
      if (value < 50) return '#c3472f';
      if (value < 60) return '#dc8c23';
      if (value < 70) return '#d2b529';
      if (value < 80) return '#4c9a52';
      return '#1c7c54';
    },
    scaleCount(row) {
      const count = surveyParticipationCount(row);
      return count !== null && count > 0 ? count : 0;
    },
    averageLabel(value) {
      return value === null ? '?' : `${value.toFixed(0)}%`;
    },
    axisLabel: 'GP survey overall-good %',
    axisMin: 0,
    axisMax: 100
  },
  gap: {
    title: 'Survey/Google gap',
    value(row) {
      return gapValue(row, { suppressSmall: true });
    },
    compareValue(_row) {
      return null;
    },
    markerLabel(row) {
      const value = this.value(row);
      return value === null ? '?' : value.toFixed(1);
    },
    markerColor(row) {
      const value = this.value(row);
      if (value === null) return '#9aa0a6';
      if (activeGapMode === 'normalized') {
        if (value >= 0.75) return '#1c7c54';
        if (value >= 0.25) return '#4c9a52';
        if (value > -0.25) return '#d2b529';
        if (value > -0.75) return '#dc8c23';
        return '#c3472f';
      }
      if (value >= 1.0) return '#1c7c54';
      if (value >= 0.5) return '#4c9a52';
      if (value > -0.5) return '#d2b529';
      if (value > -1.0) return '#dc8c23';
      return '#c3472f';
    },
    scaleCount(row) {
      const google = numericOrNull(row.google_count);
      const survey = surveyParticipationCount(row);
      const googleValid = google !== null && google > 0;
      const surveyValid = survey !== null && survey > 0;
      if (googleValid && surveyValid) return Math.min(google, survey);
      if (googleValid) return google;
      if (surveyValid) return survey;
      return 0;
    },
    averageLabel(value) {
      return value === null ? '?' : value.toFixed(2);
    },
    axisLabel: '',
    axisMin: -2.5,
    axisMax: 2.5
  }
};

function numericOrNull(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'string' && value.trim() === '') return null;
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function roundApproxPatientsPerYear(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return null;
  const magnitude = Math.abs(numeric);
  if (magnitude >= 2000) return Math.round(numeric / 100) * 100;
  if (magnitude >= 500) return Math.round(numeric / 50) * 50;
  if (magnitude >= 100) return Math.round(numeric / 25) * 25;
  return Math.round(numeric / 10) * 10;
}

function surveyParticipationCount(row) {
  const surveySentBack = numericOrNull(row.survey_sent_back);
  if (surveySentBack !== null && surveySentBack > 0) return surveySentBack;
  const overallResponses = numericOrNull(row.responses_for_overall_question);
  if (overallResponses !== null && overallResponses > 0) return overallResponses;
  const responseCount = numericOrNull(row.number_of_responses);
  if (responseCount !== null && responseCount > 0) return responseCount;
  return null;
}

function metricColorForValue(metricName, value) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return '#9aa0a6';
  const numeric = Number(value);
  if (metricName === 'google') {
    if (numeric < 2) return '#c3472f';
    if (numeric < 3) return '#dc8c23';
    if (numeric < 4) return '#d2b529';
    if (numeric < 4.5) return '#4c9a52';
    return '#1c7c54';
  }
  if (metricName === 'survey') {
    if (numeric < 50) return '#c3472f';
    if (numeric < 60) return '#dc8c23';
    if (numeric < 70) return '#d2b529';
    if (numeric < 80) return '#4c9a52';
    return '#1c7c54';
  }
  if (activeGapMode === 'normalized') {
    if (numeric >= 0.75) return '#1c7c54';
    if (numeric >= 0.25) return '#4c9a52';
    if (numeric > -0.25) return '#d2b529';
    if (numeric > -0.75) return '#dc8c23';
    return '#c3472f';
  }
  if (numeric >= 1.0) return '#1c7c54';
  if (numeric >= 0.5) return '#4c9a52';
  if (numeric > -0.5) return '#d2b529';
  if (numeric > -1.0) return '#dc8c23';
  return '#c3472f';
}

function standardDeviation(values) {
  if (!values.length) return null;
  const average = mean(values);
  if (average === null) return null;
  const variance = values.reduce((sum, value) => sum + ((value - average) ** 2), 0) / values.length;
  return variance > 0 ? Math.sqrt(variance) : 0;
}

function gapInputs(row) {
  const google = numericOrNull(row.google_score);
  const googleCount = numericOrNull(row.google_count);
  const surveyPercent = numericOrNull(row.survey_overall_good_percent);
  const surveyResponses = surveyParticipationCount(row);
  if (google === null || surveyPercent === null) return null;
  if (googleCount === null || googleCount <= 0) return null;
  if (surveyResponses === null || surveyResponses <= 0) return null;
  return {
    google,
    surveyPercent,
    surveyStars: surveyPercent / 20,
  };
}

function gapNormalisationCohortKey(row) {
  const nation = String(row?.nation || '').trim().toLowerCase();
  return nation || 'all';
}

const gapNormalisationStatsByCohort = (() => {
  const buckets = new Map();
  for (const row of rows.concat(nationalSupplementals)) {
    const inputs = gapInputs(row);
    if (!inputs) continue;
    const key = gapNormalisationCohortKey(row);
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(inputs.google - inputs.surveyStars);
  }
  const stats = new Map();
  for (const [key, values] of buckets.entries()) {
    stats.set(key, {
      rawGapMean: mean(values),
      rawGapStd: standardDeviation(values),
      sampleSize: values.length,
    });
  }
  const allValues = Array.from(buckets.values()).flat();
  stats.set('all', {
    rawGapMean: mean(allValues),
    rawGapStd: standardDeviation(allValues),
    sampleSize: allValues.length,
  });
  return stats;
})();

function absoluteGapValue(row, suppressSmall = true) {
  const inputs = gapInputs(row);
  if (!inputs) return null;
  const gap = inputs.google - inputs.surveyStars;
  return suppressSmall && Math.abs(gap) < 1 ? null : gap;
}

function normalizedGapValue(row, suppressSmall = true) {
  const inputs = gapInputs(row);
  if (!inputs) return null;
  const cohortKey = gapNormalisationCohortKey(row);
  const cohortStats = gapNormalisationStatsByCohort.get(cohortKey) || gapNormalisationStatsByCohort.get('all');
  if (!cohortStats) return null;
  const rawGapStd = cohortStats.rawGapStd;
  if (!rawGapStd) return null;
  const rawGap = inputs.google - inputs.surveyStars;
  const gap = (rawGap - cohortStats.rawGapMean) / rawGapStd;
  return suppressSmall && Math.abs(gap) < 1 ? null : gap;
}

function gapValue(row, options = {}) {
  const suppressSmall = options.suppressSmall !== false;
  return activeGapMode === 'normalized'
    ? normalizedGapValue(row, suppressSmall)
    : absoluteGapValue(row, suppressSmall);
}

function gapAxisInfo() {
  if (activeGapMode !== 'normalized') {
    return {
      label: 'Google minus survey-equivalent stars (positive = Google higher)',
      min: -2.5,
      max: 2.5,
      magnitudeLabel: 'Survey/Google gap magnitude (abs, stars)',
      magnitudeTicks: [0, 0.5, 1.0, 1.5, 2.0, 2.5],
    };
  }
  const values = rows
    .map((row) => gapValue(row, { suppressSmall: false }))
    .filter((value) => value !== null && Number.isFinite(value));
  const maxAbs = values.length ? Math.max(...values.map((value) => Math.abs(value))) : 1;
  const roundedMax = Math.max(1, Math.ceil(maxAbs * 2) / 2);
  const ticks = [];
  const step = roundedMax <= 2 ? 0.5 : 1;
  for (let tick = 0; tick <= roundedMax + 0.001; tick += step) {
    ticks.push(Number(tick.toFixed(2)));
  }
  return {
    label: 'Normalised Google-minus-survey gap (within-nation z-score, positive = Google higher)',
    min: -roundedMax,
    max: roundedMax,
    magnitudeLabel: 'Survey/Google gap magnitude (abs, normalised z-score)',
    magnitudeTicks: ticks,
  };
}

function gapDescription() {
  if (activeGapMode === 'normalized') {
    return 'Normalised mode: the raw Google-minus-survey gap is converted to a within-nation z-score. Positive means Google reviews sit above the survey-equivalent score for that nation-relative cohort; negative means the survey-equivalent score sits above Google, which this view treats as worse.';
  }
  return 'Indicator only: survey overall-good % is scaled to 0-5 and compared with Google. Positive means Google reviews are higher than the survey-equivalent score; negative means the survey-equivalent score is higher than Google, which this view treats as worse.';
}

const gtdAveragePatientCountByYear = Object.fromEntries(
  Object.entries(patientCountsByYear || {}).map(([year, counts]) => {
    const values = Object.values(counts || {})
      .map((value) => numericOrNull(value))
      .filter((value) => value !== null && value > 0);
    return [year, values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null];
  })
);

function maxRegisteredPatientCount() {
  return Math.max(0, ...rows.map((row) => numericOrNull(row.registered_patient_count) || 0));
}

function sizeValueForRow(row) {
  const count = numericOrNull(row.registered_patient_count);
  return count !== null && count > 0 ? count : 0;
}

function averageMetric(rowsForCompany, metricName) {
  const metric = metricConfigs[metricName];
  const values = rowsForCompany
    .map((row) => metric.value(row))
    .filter((value) => value !== null);
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

const managementCompanies = knownManagementCompanies.map((name) => {
  const companyRows = rows.filter((row) => row.management_company === name);
  return {
    name,
    count: companyRows.length,
    rows: companyRows
  };
});

function patientScaleForRow(row) {
  const count = numericOrNull(row.registered_patient_count);
  const maxCount = maxRegisteredPatientCount();
  if (!Number.isFinite(count) || count <= 0) return 0.7;
  if (maxCount <= 0) return 0.7;
  const normalized = Math.log1p(count) / Math.log1p(maxCount);
  return 0.5 + (normalized ** 0.7) * 0.7;
}

function markerPresentationForZoom() {
  const zoom = map.getZoom();
  if (zoom <= 6) {
    return { scaleMultiplier: 0.26, showLabel: false, simplifiedShape: true, shadowMode: 'none' };
  }
  if (zoom === 7) {
    return { scaleMultiplier: 0.34, showLabel: false, simplifiedShape: true, shadowMode: 'none' };
  }
  if (zoom === 8) {
    return { scaleMultiplier: 0.46, showLabel: false, simplifiedShape: true, shadowMode: 'none' };
  }
  if (zoom === 9) {
    return { scaleMultiplier: 0.68, showLabel: true, simplifiedShape: true, shadowMode: 'none' };
  }
  if (zoom === 10) {
    return { scaleMultiplier: 0.86, showLabel: true, simplifiedShape: true, shadowMode: 'none' };
  }
  if (zoom === 11) {
    return { scaleMultiplier: 1, showLabel: true, simplifiedShape: false, shadowMode: 'light' };
  }
  return { scaleMultiplier: 1, showLabel: true, simplifiedShape: false, shadowMode: 'full' };
}

function mapRowsForOverlays() {
  return rows.filter((row) => Number.isFinite(Number(row.lat)) && Number.isFinite(Number(row.lon)));
}

function shapeAssignment() {
  const selected = managementCompanies
    .filter((company) => selectedManagementCompanies.has(company.name))
    .slice(0, managementShapePool.length);
  const assignments = new Map();
  selected.forEach((company, index) => assignments.set(company.name, managementShapePool[index]));
  return assignments;
}

function baseShapeMetrics(shape) {
  if (shape === 'triangle') return { width: 42, height: 36, anchorX: 21, anchorY: 30, popupY: -14 };
  if (shape === 'square') return { width: 34, height: 34, anchorX: 17, anchorY: 17, popupY: -14 };
  if (shape === 'diamond') return { width: 34, height: 34, anchorX: 17, anchorY: 17, popupY: -14 };
  if (shape === 'hexagon') return { width: 38, height: 34, anchorX: 19, anchorY: 17, popupY: -14 };
  if (shape === 'pentagon') return { width: 38, height: 36, anchorX: 19, anchorY: 18, popupY: -14 };
  return { width: 34, height: 34, anchorX: 17, anchorY: 17, popupY: -14 };
}

function markerSvg(shape, color, label, fontSize, missing, highlighted = false, options = {}) {
  const showLabel = options.showLabel !== false;
  const shadowMode = options.shadowMode || 'full';
  const svgClass = `marker-svg marker-svg--shadow-${shadowMode}`;
  const stroke = highlighted ? '#111111' : 'rgba(0,0,0,0.28)';
  const strokeWidth = highlighted ? '2.8' : '1.2';
  const textColor = missing ? '#f4f4f4' : '#ffffff';
  const textMarkup = (x, y) => showLabel
    ? `<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="middle" fill="${textColor}" font-size="${fontSize}" font-weight="700" font-family="ui-sans-serif, system-ui, sans-serif">${label}</text>`
    : '';
  if (shape === 'triangle') {
    return `
      <svg class="${svgClass}" width="100%" height="100%" viewBox="0 0 42 36" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="21,1 41,35 1,35" fill="${color}" stroke="${stroke}" stroke-width="${strokeWidth}" />
        ${textMarkup(21, 24)}
      </svg>
    `;
  }
  if (shape === 'square') {
    return `
      <svg class="${svgClass}" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect x="1" y="1" width="32" height="32" fill="${color}" stroke="${stroke}" stroke-width="${strokeWidth}" />
        ${textMarkup(17, 18)}
      </svg>
    `;
  }
  if (shape === 'diamond') {
    return `
      <svg class="${svgClass}" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="17,1 33,17 17,33 1,17" fill="${color}" stroke="${stroke}" stroke-width="${strokeWidth}" />
        ${textMarkup(17, 18)}
      </svg>
    `;
  }
  if (shape === 'hexagon') {
    return `
      <svg class="${svgClass}" width="100%" height="100%" viewBox="0 0 38 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="10,1 28,1 37,17 28,33 10,33 1,17" fill="${color}" stroke="${stroke}" stroke-width="${strokeWidth}" />
        ${textMarkup(19, 18)}
      </svg>
    `;
  }
  if (shape === 'pentagon') {
    return `
      <svg class="${svgClass}" width="100%" height="100%" viewBox="0 0 38 36" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <polygon points="19,1 37,14 31,35 7,35 1,14" fill="${color}" stroke="${stroke}" stroke-width="${strokeWidth}" />
        ${textMarkup(19, 20)}
      </svg>
    `;
  }
  return `
    <svg class="${svgClass}" width="100%" height="100%" viewBox="0 0 34 34" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="17" cy="17" r="16" fill="${color}" stroke="${stroke}" stroke-width="${strokeWidth}" />
      ${textMarkup(17, 18)}
    </svg>
  `;
}

function renderMetricLegend() {
  const metric = metricConfigs[activeMetric];
  document.getElementById('metric-description').textContent =
    activeMetric === 'gap' ? gapDescription() : metric.description;
  document.getElementById('metric-description').className = 'hint metric-note';
  const gapModeControl = document.getElementById('gap-mode-control');
  const normalizeToggle = document.getElementById('normalize-gap-toggle');
  const gapModeNote = document.getElementById('gap-mode-note');
  const gapModeActive = activeMetric === 'gap';
  gapModeControl.hidden = !gapModeActive;
  normalizeToggle.checked = activeGapMode === 'normalized';
  gapModeControl.querySelector('label').classList.toggle('is-active', gapModeActive && activeGapMode === 'normalized');
  gapModeNote.textContent = activeGapMode === 'normalized'
    ? "Converts the raw Google-vs-survey gap into a cohort z-score, showing how unusual each practice's gap is on this map."
    : 'Compares Google stars directly with survey-equivalent stars (survey overall-good % mapped to 0-5).';
}

function updateSidebarState() {
  const stage = document.querySelector('.map-stage');
  const button = document.getElementById('legend-collapse');
  stage.classList.toggle('is-collapsed', sidebarCollapsed);
  button.setAttribute('aria-pressed', sidebarCollapsed ? 'true' : 'false');
  button.setAttribute('title', sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar');
  button.textContent = sidebarCollapsed ? '>' : '<';
}

function clearOverlayLayers() {
  markerLayer.clearLayers();
  if (voronoiLayer) {
    map.removeLayer(voronoiLayer);
    voronoiLayer = null;
  }
  if (deprivationLayer) {
    map.removeLayer(deprivationLayer);
    deprivationLayer = null;
  }
  healthcareTerrainLayers.forEach((layer) => {
    if (layer) map.removeLayer(layer);
  });
  healthcareTerrainLayers = [];
}

function availableHealthcareTerrainOverlays() {
  return healthcareTerrainOverlays
    .filter((overlay) => overlay && overlay.tileUrl)
    .sort((left, right) => {
      const leftId = String(left?.overlayId || left?.nation || '').trim().toLowerCase();
      const rightId = String(right?.overlayId || right?.nation || '').trim().toLowerCase();
      return TERRAIN_OVERLAY_ORDER.indexOf(leftId) - TERRAIN_OVERLAY_ORDER.indexOf(rightId);
    });
}

function selectedHealthcareTerrainOverlays() {
  return availableHealthcareTerrainOverlays().filter((overlay) => selectedHealthcareTerrainOverlayIds.has(String(overlay?.overlayId || overlay?.nation || '').trim().toLowerCase()));
}

function fallbackAreaOverlay() {
  return selectedHealthcareTerrainOverlays().length ? 'terrain' : null;
}

function healthcareTerrainSummaryText(overlays = selectedHealthcareTerrainOverlays()) {
  if (!overlays.length) return '';
  const englandCatchment = overlays.find((overlay) => String(overlay?.overlayId || '') === 'england_catchment');
  const englandOutOfArea = overlays.find((overlay) => String(overlay?.overlayId || '') === 'england_out_of_area');
  const distanceNations = overlays
    .filter((overlay) => overlay.mode === 'distance_strength' && String(overlay?.overlayId || '') !== 'england_out_of_area')
    .map((overlay) => overlay.label.replace(/\s+distance terrain$/i, ''))
    .filter(Boolean);
  if (englandCatchment && englandOutOfArea && distanceNations.length) {
    return `England catchments show published hard boundaries. England out-of-area adds soft halos for practices logged as accepting out-of-area registrations. ${distanceNations.join(', ')} use softer distance-strength tiles around practice locations instead of hard boundaries.`;
  }
  if (englandCatchment && englandOutOfArea) {
    return 'England catchments show published hard boundaries, while England out-of-area adds soft halos for practices logged as accepting out-of-area registrations.';
  }
  if (englandCatchment && distanceNations.length) {
    return `England uses published catchment-overlap tiles. ${distanceNations.join(', ')} use softer distance-strength tiles around practice locations instead of hard boundaries.`;
  }
  if (englandCatchment) return 'England uses published catchment-overlap tiles based on actual practice polygons.';
  if (englandOutOfArea) return 'England out-of-area shows soft distance halos around practices logged as accepting out-of-area registrations.';
  return 'This terrain uses distance-strength tiles around practice locations rather than hard catchment boundaries.';
}

function updateAreaOverlayControls() {
  const populationChecked = activeAreaOverlay === 'population';
  const deprivationChecked = activeAreaOverlay === 'deprivation';
  const terrainAvailable = availableHealthcareTerrainOverlays().length > 0;
  const selectedTerrainOverlays = selectedHealthcareTerrainOverlays();
  const terrainChecked = terrainAvailable && activeAreaOverlay === 'terrain' && selectedTerrainOverlays.length > 0;
  const populationToggle = document.getElementById('voronoi-toggle');
  const deprivationToggle = document.getElementById('deprivation-toggle');
  const availableTerrainOverlayIds = new Set(availableHealthcareTerrainOverlays().map((overlay) => String(overlay?.overlayId || overlay?.nation || '').trim().toLowerCase()));
  const tip = document.getElementById('area-overlay-tip');
  populationToggle.checked = populationChecked;
  deprivationToggle.checked = deprivationChecked;
  document.getElementById('population-overlay-control').classList.toggle('is-active', populationChecked);
  document.getElementById('deprivation-overlay-control').classList.toggle('is-active', deprivationChecked);
  const terrainControl = document.getElementById('healthcare-terrain-overlay-control');
  terrainControl.classList.toggle('is-disabled', !terrainAvailable);
  TERRAIN_OVERLAY_ORDER.forEach((overlayId) => {
    const toggle = document.getElementById(TERRAIN_OVERLAY_CONTROL_IDS[overlayId]);
    const control = document.getElementById(`${TERRAIN_OVERLAY_CONTROL_IDS[overlayId].replace(/-toggle$/, '-control')}`);
    if (!toggle || !control) return;
    const available = availableTerrainOverlayIds.has(overlayId);
    toggle.checked = available && selectedHealthcareTerrainOverlayIds.has(overlayId);
    toggle.disabled = !available;
    control.classList.toggle('is-active', terrainChecked && toggle.checked);
    control.classList.toggle('is-disabled', !available);
  });
  if (populationChecked) {
    tip.textContent = 'Approximate catchment cells built from practice locations and coloured by the active score metric. This is a rough vibes layer, not a real practice-boundary map.';
  } else if (deprivationChecked) {
    tip.textContent = 'Official 2025 IMD deciles for the current map catchment, shown by small-area LSOA polygon. This is area deprivation, not a practice-performance score.';
  } else if (terrainChecked) {
    const selectedLabels = selectedTerrainOverlays.map((overlay) => overlay.label.replace(/\s+(distance terrain|catchment terrain)$/i, '')).join(', ');
    tip.textContent = `${healthcareTerrainSummaryText(selectedTerrainOverlays)} Showing ${selectedLabels}.`;
  } else if (!terrainAvailable) {
    tip.textContent = '';
  } else {
    tip.textContent = 'Select one or more terrain layers to show the raster overlay. England catchments starts on by default; England out-of-area and the devolved-nation layers are available separately.';
  }
}

function voronoiGhostPoints() {
  const [minLon, minLat, maxLon, maxLat] = dataBbox;
  const width = maxLon - minLon;
  const height = maxLat - minLat;
  const lonInset = width * 0.035;
  const latInset = height * 0.035;
  const sideSteps = 6;
  const points = [];
  let ghostIndex = 0;

  for (let step = 0; step <= sideSteps; step += 1) {
    const t = step / sideSteps;
    const lon = minLon + width * t;
    const lat = minLat + height * t;
    points.push(turf.point([lon, minLat + latInset], { code: `__ghost_top_${ghostIndex++}` }));
    points.push(turf.point([lon, maxLat - latInset], { code: `__ghost_bottom_${ghostIndex++}` }));
    points.push(turf.point([minLon + lonInset, lat], { code: `__ghost_left_${ghostIndex++}` }));
    points.push(turf.point([maxLon - lonInset, lat], { code: `__ghost_right_${ghostIndex++}` }));
  }

  return points;
}

function voronoiPoints() {
  const rowsForMap = mapRowsForOverlays();
  const duplicateCounts = new Map();
  const realPoints = rowsForMap.map((row) => {
    const key = `${Number(row.lat).toFixed(6)},${Number(row.lon).toFixed(6)}`;
    const duplicateIndex = duplicateCounts.get(key) || 0;
    duplicateCounts.set(key, duplicateIndex + 1);
    const angle = duplicateIndex * 2.399963229728653;
    const offset = duplicateIndex === 0 ? 0 : 0.00018 * Math.ceil(duplicateIndex / 2);
    const lon = Number(row.lon) + Math.cos(angle) * offset;
    const lat = Number(row.lat) + Math.sin(angle) * offset;
    return turf.point([lon, lat], { code: row.code });
  });
  return realPoints.concat(voronoiGhostPoints());
}

function voronoiCentroidByCode() {
  const points = voronoiPoints();
  if (!points.length) return new Map();
  const fc = turf.featureCollection(points);
  const polygons = turf.voronoi(fc, { bbox: dataBbox });
  const rowByCode = new Map(rows.map((row) => [row.code, row]));
  const centroidByCode = new Map();
  (polygons?.features || []).forEach((feature) => {
    const code = feature?.properties?.code;
    if (code && rowByCode.has(code)) {
      const centroid = turf.centroid(feature);
      const [lon, lat] = centroid.geometry.coordinates;
      centroidByCode.set(code, [lat, lon]);
    }
  });
  return centroidByCode;
}

function renderVoronoi() {
  const points = voronoiPoints();
  if (!points.length) return;
  const fc = turf.featureCollection(points);
  const polygons = turf.voronoi(fc, { bbox: dataBbox });
  const rowByCode = new Map(rows.map((row) => [row.code, row]));
  const features = (polygons && polygons.features ? polygons.features : [])
    .filter((feature) => feature && feature.properties && feature.properties.code && rowByCode.has(feature.properties.code))
    .map((feature) => {
      const row = rowByCode.get(feature.properties.code);
      feature.properties.popupMarkup = popupMarkup(row);
      feature.properties.code = row.code;
      feature.properties.color = metricConfigs[activeMetric].markerColor(row);
      return feature;
    });
  if (!features.length) return;
  voronoiLayer = L.geoJSON({ type: 'FeatureCollection', features }, {
    style: (feature) => {
      return {
        color: 'rgba(26,28,26,0.26)',
        weight: 1,
        fillColor: feature.properties.color || '#9aa0a6',
        fillOpacity: 0.42
      };
    },
    onEachFeature: (feature, layer) => {
      const row = rowByCode.get(feature.properties.code);
      layer.bindPopup(feature.properties.popupMarkup || '');
      layer.on('click', () => {
        if (row) focusRow(row);
      });
    }
  });
  voronoiLayer.addTo(map);
  voronoiLayer.bringToBack();
}

function deprivationFillColor(decile) {
  if (decile === null) return '#9aa0a6';
  if (decile <= 1) return '#8e1f1b';
  if (decile <= 2) return '#b93522';
  if (decile <= 4) return '#d86a1b';
  if (decile <= 6) return '#d2b529';
  if (decile <= 8) return '#72a847';
  return '#1c7c54';
}

function deprivationPopupMarkup(properties) {
  const decile = numericOrNull(properties.imd_decile);
  const rank = numericOrNull(properties.imd_rank);
  const score = numericOrNull(properties.imd_score);
  const healthDecile = numericOrNull(properties.health_decile);
  const population = numericOrNull(properties.population_2022);
  return [
    `<strong>${properties.lsoa21nm || properties.lsoa21cd || 'LSOA'}</strong>`,
    `<div>IMD 2025 decile: ${decile === null ? '?' : decile} / 10 (1 = most deprived)</div>`,
    `<div>IMD rank: ${rank === null ? '?' : rank.toLocaleString('en-GB')}</div>`,
    `<div>IMD score: ${score === null ? '?' : score.toFixed(3)}</div>`,
    `<div>Health deprivation decile: ${healthDecile === null ? '?' : healthDecile} / 10</div>`,
    `<div>Population (mid-2022): ${population === null ? '?' : population.toLocaleString('en-GB')}</div>`,
  ].join('');
}

function renderDeprivation() {
  const features = (deprivationGeojson && deprivationGeojson.features ? deprivationGeojson.features : []).map((feature) => {
    const nextFeature = {
      ...feature,
      properties: {
        ...(feature.properties || {}),
        popupMarkup: deprivationPopupMarkup(feature.properties || {})
      }
    };
    return nextFeature;
  });
  if (!features.length) return;
  deprivationLayer = L.geoJSON({ type: 'FeatureCollection', features }, {
    style: (feature) => {
      const decile = numericOrNull(feature?.properties?.imd_decile);
      return {
        color: 'rgba(26,28,26,0.18)',
        weight: 0.8,
        fillColor: deprivationFillColor(decile),
        fillOpacity: 0.5
      };
    },
    onEachFeature: (feature, layer) => {
      layer.bindPopup(feature?.properties?.popupMarkup || '');
    }
  });
  deprivationLayer.addTo(map);
  deprivationLayer.bringToBack();
}

function renderHealthcareTerrain() {
  healthcareTerrainLayers = selectedHealthcareTerrainOverlays().map((overlay) => {
    const layer = L.tileLayer(overlay.tileUrl, {
      pane: 'healthcareTerrain',
      bounds: overlay.bounds,
      noWrap: true,
      opacity: overlay.opacity ?? 0.58,
      tileSize: overlay.tileSize ?? 256,
      minZoom: overlay.minZoom ?? 0,
      maxNativeZoom: overlay.maxNativeZoom ?? 9,
      maxZoom: 18,
      attribution: 'NHS GP terrain overlays'
    });
    layer.addTo(map);
    return layer;
  });
  healthcareTerrainLayers.forEach((layer) => layer.bringToFront());
}

function renderManagementList() {
  const container = document.getElementById('manager-list');
  container.innerHTML = '';
  const assignments = shapeAssignment();
  const metric = metricConfigs[activeMetric];
  document.getElementById('manager-hint').textContent = `GTD stays on as the baseline. Add up to ${managementShapePool.length - 1} more management companies to compare their average ${metric.title.toLowerCase()} with GTD.`;
  for (const company of managementCompanies) {
    const checked = selectedManagementCompanies.has(company.name);
    const isBaselineCompany = company.name === BASELINE_MANAGEMENT_COMPANY;
    const shape = assignments.get(company.name) || 'circle';
    const average = metric.averageLabel(averageMetric(company.rows, activeMetric));
    const row = document.createElement('label');
    row.className = 'manager-option';
    row.title = isBaselineCompany
      ? `${company.name} · baseline company · ${average} avg · ${company.count} practices`
      : `${company.name} · ${average} avg · ${company.count} practices`;
    row.innerHTML = `
      <input type="checkbox" ${checked ? 'checked' : ''} ${isBaselineCompany ? 'disabled' : ''} data-company="${company.name}">
      <span class="manager-name"><span class="swatch ${shape}" style="background:${checked ? 'var(--midhigh)' : 'var(--missing)'}; display:inline-block; margin-right:8px;"></span><span class="manager-name-text">${company.name}</span></span>
      <span class="manager-meta">${average} avg · ${company.count}</span>
    `;
    if (isBaselineCompany) {
      container.appendChild(row);
      continue;
    }
    row.querySelector('input').addEventListener('change', (event) => {
      if (event.target.checked) {
        if (selectedManagementCompanies.size >= managementShapePool.length) {
          event.target.checked = false;
          return;
        }
        selectedManagementCompanies.add(company.name);
      } else {
        selectedManagementCompanies.delete(company.name);
      }
      rerenderAll();
    });
    container.appendChild(row);
  }
}

function formatGoogle(row) {
  const value = numericOrNull(row.google_score);
  if (value === null) return row.google_missing_text || 'Google: ?';
  const count = numericOrNull(row.google_count);
  return `Google: ${value.toFixed(1)}${count === null ? '' : ` (${Math.round(count)} reviews)`}`;
}

function formatSurvey(row) {
  const surveyLabel = row.survey_label || 'GPPS';
  const overall = numericOrNull(row.survey_overall_good_percent);
  const completion = numericOrNull(row.survey_completion_rate_percent);
  const sentBack = numericOrNull(row.survey_sent_back);
  const sentOut = numericOrNull(row.survey_sent_out);
  if (overall === null && completion === null) {
    return row.survey_missing_text || `${surveyLabel}: ?`;
  }
  const parts = [];
  if (overall !== null) parts.push(`${Math.round(overall)}%`);
  if (completion !== null) parts.push(`${Math.round(completion)}% completion`);
  if (sentBack !== null && sentOut !== null) parts.push(`${Math.round(sentBack)}/${Math.round(sentOut)} returned`);
  return `${surveyLabel} ${parts.join(' / ')}`;
}

function formatGap(row) {
  const inputs = gapInputs(row);
  const gap = gapValue(row, { suppressSmall: false });
  if (!inputs || gap === null) return 'Survey/Google gap: ?';
  const magnitude = Math.abs(gap);
  if (magnitude < 0.01) {
    return activeGapMode === 'normalized'
      ? `Survey/Google gap: typical for this nation-relative cohort · Google ${inputs.google.toFixed(1)} vs survey-equivalent ${inputs.surveyStars.toFixed(2)}`
      : `Survey/Google gap: aligned · Google ${inputs.google.toFixed(1)} vs survey-equivalent ${inputs.surveyStars.toFixed(2)}`;
  }
  const direction = gap > 0 ? 'higher' : 'lower';
  return activeGapMode === 'normalized'
    ? `Survey/Google gap: ${magnitude.toFixed(2)} within-nation z-score (${direction}) · Google ${inputs.google.toFixed(1)} vs survey-equivalent ${inputs.surveyStars.toFixed(2)}`
    : `Survey/Google gap: ${magnitude.toFixed(2)} stars (${direction}) · Google ${inputs.google.toFixed(1)} vs survey-equivalent ${inputs.surveyStars.toFixed(2)}`;
}

function firstUsableUrl(...values) {
  for (const value of values) {
    const normalized = String(value || '').trim();
    if (normalized) return normalized;
  }
  return '';
}

function practiceWebsiteUrl(row) {
  return firstUsableUrl(row?.website_url, row?.cqc_service_website);
}

function practiceProfileUrl(row) {
  return firstUsableUrl(row?.nhs_url, practiceWebsiteUrl(row), row?.google_maps_url, row?.ods_org_link);
}

function practiceActionLink(row) {
  const registerUrl = firstUsableUrl(row?.nhs_register_url);
  if (registerUrl) return { url: registerUrl, label: 'Register' };
  const websiteUrl = practiceWebsiteUrl(row);
  if (websiteUrl) return { url: websiteUrl, label: 'Website' };
  const mapsUrl = firstUsableUrl(row?.google_maps_url);
  if (mapsUrl) return { url: mapsUrl, label: 'Map' };
  const profileUrl = firstUsableUrl(row?.nhs_url);
  if (profileUrl) return { url: profileUrl, label: 'Profile' };
  const odsUrl = firstUsableUrl(row?.ods_org_link);
  if (odsUrl) return { url: odsUrl, label: 'ODS' };
  return null;
}

function popupMarkup(row) {
  const google = `<div>${formatGoogle(row)}</div>`;
  const googleText = row.google_text_url ? `<div><a href="${row.google_text_url}" target="_blank" rel="noreferrer">Review text</a></div>` : '';
  const cqcRating = row.cqc_overall_rating
    ? `<div>CQC: ${row.cqc_overall_rating}${row.cqc_inherited_rating === 'Y' ? ' (inherited)' : ''}${row.cqc_publication_date ? ` · ${row.cqc_publication_date}` : ''}</div>`
    : '';
  const cqcLink = row.cqc_location_url ? `<div><a href="${row.cqc_location_url}" target="_blank" rel="noreferrer">CQC page</a></div>` : '';
  const profileUrl = firstUsableUrl(row.nhs_url);
  const profileLabel = row.nhs_url ? 'NHS page' : '';
  const profileLink = profileUrl ? `<div><a href="${profileUrl}" target="_blank" rel="noreferrer">${profileLabel}</a></div>` : '';
  const websiteUrl = practiceWebsiteUrl(row);
  const practiceWebsite = websiteUrl && websiteUrl !== profileUrl ? `<div><a href="${websiteUrl}" target="_blank" rel="noreferrer">Practice website</a></div>` : '';
  const odsLink = !profileUrl && !websiteUrl && row.ods_org_link ? `<div><a href="${row.ods_org_link}" target="_blank" rel="noreferrer">ODS record</a></div>` : '';
  const management = row.management_company ? `<div>Management: ${row.management_company}</div>` : '<div>Management: unknown</div>';
  const affiliatedGroup = row.affiliated_group ? `<div>Affiliated group: ${row.affiliated_group}</div>` : '';
  const takeoverDate = formatTakeoverDate(row.gtd_takeover_date, row.gtd_takeover_precision);
  const takeoverLine = takeoverDate ? `<div>GTD takeover: ${takeoverDate}</div>` : '';
  const takeoverNote = row.gtd_takeover_note ? `<div>${row.gtd_takeover_note}</div>` : '';
  const takeoverSource = row.gtd_takeover_source_url
    ? `<div><a href="${row.gtd_takeover_source_url}" target="_blank" rel="noreferrer">${row.gtd_takeover_source_label || 'Takeover source'}</a></div>`
    : '';
  const registeredPatients = numericOrNull(row.registered_patient_count_effective ?? row.registered_patient_count);
  const registeredPatientsSource = String(row.registered_patient_count_effective_source || row.registered_patient_count_source || '').trim();
  const registeredPatientsLine = `<div>Registered patients: ${registeredPatients === null ? '?' : registeredPatients.toLocaleString('en-GB')}</div>`;
  const registeredPatientsNote = registeredPatients !== null && registeredPatientsSource === 'nhs_monthly_parent_ods_fallback'
    ? '<div class="popup-note">Count shown via parent practice ODS code.</div>'
    : '';
  const outOfAreaLine = row.accepts_out_of_area_registrations ? '<div>Accepts out-of-area registrations</div>' : '';
  const survey = `<div>${formatSurvey(row)}</div>`;
  const surveyCompareValue = numericOrNull(row.survey_overall_good_ics_percent);
  const surveyCompare = surveyCompareValue === null ? '' : `<div>GP survey ICS overall-good: ${Math.round(surveyCompareValue)}%</div>`;
  const surveyResolution = row.survey_resolution_note ? `<div>${row.survey_resolution_note}</div>` : '';
  const surveySourceNote = row.survey_note ? `<div>${row.survey_note}</div>` : '';
  const surveyUrl = row.survey_link_url || '';
  const surveyLinkLabel = row.survey_link_label || 'Survey source';
  const surveyLink = surveyUrl ? `<div><a href="${surveyUrl}" target="_blank" rel="noreferrer">${surveyLinkLabel}</a></div>` : '';
  const gap = `<div>${formatGap(row)}</div>`;
  const gtd = row.gtd_url ? `<div><a href="${row.gtd_url}" target="_blank" rel="noreferrer">GTD page</a></div>` : '';
  return `
    <strong>${row.name}</strong><br>
    ${row.postcode}<br>
    <div>Code: ${row.code}</div>
    ${management}
    ${affiliatedGroup}
    ${takeoverLine}
    ${takeoverNote}
    ${registeredPatientsLine}
    ${registeredPatientsNote}
    ${outOfAreaLine}
    ${google}
    ${survey}
    ${cqcRating}
    ${surveyCompare}
    ${surveyResolution}
    ${surveySourceNote}
    ${gap}
    ${googleText}
    ${profileLink}
    ${cqcLink}
    ${practiceWebsite}
    ${odsLink}
    ${surveyLink}
    ${gtd}
    ${takeoverSource}
  `;
}

function nationalPopupMarkup(row) {
  const google = `<div>${formatGoogle(row)}</div>`;
  const survey = `<div>${formatSurvey(row)}</div>`;
  const gap = `<div>${formatGap(row)}</div>`;
  const cqcRating = row.cqc_overall_rating
    ? `<div>CQC: ${row.cqc_overall_rating}${row.cqc_inherited_rating === 'Y' ? ' (inherited)' : ''}${row.cqc_publication_date ? ` · ${row.cqc_publication_date}` : ''}</div>`
    : '';
  const registeredPatients = numericOrNull(row.registered_patient_count_effective ?? row.registered_patient_count);
  const registeredPatientsSource = String(row.registered_patient_count_effective_source || row.registered_patient_count_source || '').trim();
  const patientsLine = registeredPatients === null ? '' : `<div>Registered patients: ${registeredPatients.toLocaleString('en-GB')}</div>`;
  const patientsNote = registeredPatients !== null && registeredPatientsSource === 'nhs_monthly_parent_ods_fallback'
    ? '<div class="popup-note">Count shown via parent practice ODS code.</div>'
    : '';
  const surveyResolution = row.survey_resolution_note ? `<div>${row.survey_resolution_note}</div>` : '';
  const surveySourceNote = row.survey_note ? `<div>${row.survey_note}</div>` : '';
  const surveyUrl = row.survey_link_url || '';
  const surveyLinkLabel = row.survey_link_label || 'Survey source';
  const surveyLink = surveyUrl ? `<div><a href="${surveyUrl}" target="_blank" rel="noreferrer">${surveyLinkLabel}</a></div>` : '';
  const googleLink = row.google_maps_url ? `<div><a href="${row.google_maps_url}" target="_blank" rel="noreferrer">Google Maps page</a></div>` : '';
  const cqcLink = row.cqc_location_url ? `<div><a href="${row.cqc_location_url}" target="_blank" rel="noreferrer">CQC page</a></div>` : '';
  const profileUrl = firstUsableUrl(row.nhs_url);
  const profileLabel = row.nhs_url ? 'NHS page' : '';
  const profileLink = profileUrl ? `<div><a href="${profileUrl}" target="_blank" rel="noreferrer">${profileLabel}</a></div>` : '';
  const websiteUrl = practiceWebsiteUrl(row);
  const practiceWebsite = websiteUrl && websiteUrl !== profileUrl ? `<div><a href="${websiteUrl}" target="_blank" rel="noreferrer">Practice website</a></div>` : '';
  const odsLink = !profileUrl && !websiteUrl && !row.google_maps_url && row.ods_org_link ? `<div><a href="${row.ods_org_link}" target="_blank" rel="noreferrer">ODS record</a></div>` : '';
  return `
    <strong>${row.name}</strong><br>
    ${row.postcode || ''}<br>
    <div>Code: ${row.code}</div>
    <div>Nation: ${row.nation || '?'}</div>
    ${patientsLine}
    ${patientsNote}
    ${google}
    ${survey}
    ${cqcRating}
    ${surveyResolution}
    ${surveySourceNote}
    ${gap}
    ${surveyLink}
    ${googleLink}
    ${profileLink}
    ${cqcLink}
    ${practiceWebsite}
    ${odsLink}
  `;
}

function focusRow(row) {
  focusedPracticeCode = row.code;
  renderComparisons();
}

function focusPracticeByCode(code) {
  const row = rowsByCode.get(code);
  if (row) {
    focusRow(row);
  }
}

function isTrendSpecialCode(code) {
  return code === TREND_DEFAULT_CONTEXT_CODE;
}

function validTrendCode(code, availableCodes) {
  return isTrendSpecialCode(code) || availableCodes.has(code);
}

function defaultTrendReferenceEntry(practiceEntries) {
  return practiceEntries.find((entry) => entry.series.code === NEW_BANK_CODE) || practiceEntries[0] || null;
}

function patientVsAveragePoint(yearKey, code, index) {
  const raw = numericOrNull(patientCountsByYear?.[yearKey]?.[code]);
  const average = numericOrNull(gtdAveragePatientCountByYear?.[yearKey]);
  if (raw === null || average === null || average <= 0) return null;
  return {
    i: index,
    v: (raw / average) * 100,
    raw,
    average,
  };
}

function overlayAxisMax(values) {
  const usable = (values || []).filter((value) => value !== null && Number.isFinite(value));
  const maxValue = usable.length ? Math.max(100, ...usable) : 100;
  return maxValue <= 100 ? 100 : Math.ceil(maxValue / 25) * 25;
}

function overlayAxisTicks(maxValue) {
  const step = maxValue <= 100 ? 25 : maxValue <= 200 ? 50 : 100;
  const ticks = [];
  for (let tick = 0; tick <= maxValue; tick += step) {
    ticks.push(tick);
  }
  if (ticks[ticks.length - 1] !== maxValue) {
    ticks.push(maxValue);
  }
  return ticks;
}

function bindTrendLegendInteractions(legend) {
  legend.querySelectorAll('[data-practice-code]').forEach((button) => {
    const code = button.getAttribute('data-practice-code');
    button.addEventListener('mouseenter', () => {
      if (trendLegendHoverSuppressed) return;
      if (hoveredTrendPracticeCode === code) return;
      hoveredTrendPracticeCode = code;
      renderGtdScoreTrendChart();
    });
    button.addEventListener('mouseleave', () => {
      if (trendLegendHoverSuppressed) return;
      if (hoveredTrendPracticeCode !== code) return;
      hoveredTrendPracticeCode = null;
      renderGtdScoreTrendChart();
    });
    button.addEventListener('focus', () => {
      if (trendLegendHoverSuppressed) return;
      hoveredTrendPracticeCode = code;
      renderGtdScoreTrendChart();
    });
    button.addEventListener('blur', () => {
      if (trendLegendHoverSuppressed) return;
      if (hoveredTrendPracticeCode !== code) return;
      hoveredTrendPracticeCode = null;
      renderGtdScoreTrendChart();
    });
    button.addEventListener('mousedown', (event) => {
      event.preventDefault();
      const nextCode = code || TREND_DEFAULT_CONTEXT_CODE;
      trendLegendHoverSuppressed = true;
      hoveredTrendPracticeCode = null;
      pinnedTrendPracticeCode = nextCode;
      renderGtdScoreTrendChart();
    });
    button.addEventListener('click', (event) => {
      event.preventDefault();
      const nextCode = code || TREND_DEFAULT_CONTEXT_CODE;
      trendLegendHoverSuppressed = true;
      hoveredTrendPracticeCode = null;
      pinnedTrendPracticeCode = nextCode;
      renderGtdScoreTrendChart();
    });
  });
}

function renderTrendOverlayLegend(container, items) {
  if (!container) return;
  const activeItems = (items || []).filter((item) => item && item.label);
  container.innerHTML = activeItems.length
    ? activeItems.map((item) => `
        <span class="trend-overlay-key">
          <span class="trend-overlay-swatch" style="--swatch-color:${item.color}"></span>
          <span>${item.label}</span>
        </span>
      `).join('')
    : '';
}

function buildManchesterCatchmentIndex(featureCollection, existingIndex = null) {
  const index = existingIndex instanceof Map ? existingIndex : new Map();
  const features = Array.isArray(featureCollection?.features) ? featureCollection.features : [];
  features.forEach((feature) => {
    const codes = Array.isArray(feature?.properties?.codes) ? feature.properties.codes : [];
    codes.forEach((code) => {
      const normalized = String(code || '').trim();
      if (!normalized) return;
      if (!index.has(normalized)) index.set(normalized, []);
      index.get(normalized).push(feature);
    });
  });
  return index;
}

function pointInCatchmentBundleBbox(lat, lon, bbox) {
  if (!Array.isArray(bbox) || bbox.length !== 4) return false;
  const [minLon, minLat, maxLon, maxLat] = bbox.map((value) => Number(value));
  if (![minLon, minLat, maxLon, maxLat].every((value) => Number.isFinite(value))) return false;
  return lon >= minLon && lon <= maxLon && lat >= minLat && lat <= maxLat;
}

function boundsIntersectCatchmentBundleBbox(bounds, bbox) {
  if (!bounds || !Array.isArray(bbox) || bbox.length !== 4) return false;
  const [minLon, minLat, maxLon, maxLat] = bbox.map((value) => Number(value));
  if (![minLon, minLat, maxLon, maxLat].every((value) => Number.isFinite(value))) return false;
  return !(
    maxLon < bounds.getWest()
    || minLon > bounds.getEast()
    || maxLat < bounds.getSouth()
    || minLat > bounds.getNorth()
  );
}

function catchmentBundleMetaById(bundleId) {
  const normalized = String(bundleId || '').trim();
  if (!normalized || !manchesterCatchmentIndexMeta?._bundleById) return null;
  return manchesterCatchmentIndexMeta._bundleById.get(normalized) || null;
}

function catchmentBundleMetaForCode(code) {
  const normalized = String(code || '').trim();
  if (!normalized || !manchesterCatchmentIndexMeta) return null;
  const bundleId = manchesterCatchmentIndexMeta.code_to_bundle?.[normalized];
  return bundleId ? catchmentBundleMetaById(bundleId) : null;
}

function loadManchesterCatchmentIndex() {
  if (manchesterCatchmentIndexMeta) return Promise.resolve(manchesterCatchmentIndexMeta);
  if (manchesterCatchmentLoadPromise) return manchesterCatchmentLoadPromise;
  manchesterCatchmentLoadError = '';
  manchesterCatchmentLoadPromise = fetch(`./${PUBLISHED_CATCHMENT_INDEX_REL_PATH}`)
    .then((response) => {
      if (!response.ok) throw new Error(`catchment index fetch failed: ${response.status}`);
      return response.json();
    })
    .then((payload) => {
      manchesterCatchmentIndexMeta = payload && typeof payload === 'object' ? payload : null;
      if (manchesterCatchmentIndexMeta) {
        const bundles = Array.isArray(manchesterCatchmentIndexMeta.bundles) ? manchesterCatchmentIndexMeta.bundles : [];
        manchesterCatchmentIndexMeta._bundleById = new Map(
          bundles
            .filter((bundle) => bundle?.id)
            .map((bundle) => [String(bundle.id), bundle])
        );
      }
      manchesterCatchmentLoadError = manchesterCatchmentIndexMeta ? '' : 'Invalid catchment index payload';
      return manchesterCatchmentIndexMeta;
    })
    .catch((error) => {
      manchesterCatchmentIndexMeta = null;
      manchesterCatchmentLoadError = error instanceof Error ? error.message : String(error || 'Unknown catchment index load error');
      console.error('Catchment index load failed:', error);
      return null;
    })
    .finally(() => {
      manchesterCatchmentLoadPromise = null;
    });
  return manchesterCatchmentLoadPromise;
}

function loadManchesterCatchmentBundle(bundleMeta) {
  if (!bundleMeta?.id || !bundleMeta?.file) return Promise.resolve(null);
  if (manchesterCatchmentLoadedBundleIds.has(bundleMeta.id)) return Promise.resolve(bundleMeta.id);
  if (manchesterCatchmentBundleLoadPromises.has(bundleMeta.id)) return manchesterCatchmentBundleLoadPromises.get(bundleMeta.id);
  const promise = fetch(`./catchments/${bundleMeta.file}`)
    .then((response) => {
      if (!response.ok) throw new Error(`catchment bundle fetch failed for ${bundleMeta.id}: ${response.status}`);
      return response.json();
    })
    .then((payload) => {
      manchesterCatchmentIndex = buildManchesterCatchmentIndex(payload, manchesterCatchmentIndex);
      manchesterCatchmentLoadedBundleIds.add(bundleMeta.id);
      manchesterCatchmentLoadError = '';
      return bundleMeta.id;
    })
    .catch((error) => {
      manchesterCatchmentLoadError = error instanceof Error ? error.message : String(error || `Unknown catchment bundle load error (${bundleMeta.id})`);
      console.error('Catchment bundle load failed:', bundleMeta?.id, error);
      return null;
    })
    .finally(() => {
      manchesterCatchmentBundleLoadPromises.delete(bundleMeta.id);
    });
  manchesterCatchmentBundleLoadPromises.set(bundleMeta.id, promise);
  return promise;
}

function loadManchesterCatchmentBundles(bundleMetas) {
  const deduped = [];
  const seen = new Set();
  (bundleMetas || []).forEach((bundleMeta) => {
    const id = String(bundleMeta?.id || '').trim();
    if (!id || seen.has(id)) return;
    seen.add(id);
    deduped.push(bundleMeta);
  });
  return Promise.all(deduped.map((bundleMeta) => loadManchesterCatchmentBundle(bundleMeta)));
}

function neighboringCatchmentBundleMetas(bundleMeta) {
  if (!bundleMeta || !Array.isArray(bundleMeta.neighbor_bundle_ids)) return [];
  return bundleMeta.neighbor_bundle_ids
    .map((bundleId) => catchmentBundleMetaById(bundleId))
    .filter((bundle) => !!bundle);
}

function ensureCatchmentBundleForCode(code) {
  return loadManchesterCatchmentIndex().then((indexMeta) => {
    if (!indexMeta) return null;
    const bundleMeta = catchmentBundleMetaForCode(code);
    if (!bundleMeta) return null;
    return loadManchesterCatchmentBundles([bundleMeta].concat(neighboringCatchmentBundleMetas(bundleMeta)));
  });
}

function bundleMetasForPoint(lat, lon) {
  if (!manchesterCatchmentIndexMeta) return [];
  const directBundles = (manchesterCatchmentIndexMeta.bundles || []).filter((bundle) => pointInCatchmentBundleBbox(lat, lon, bundle?.bbox));
  const withNeighbors = [];
  const seen = new Set();
  directBundles.forEach((bundleMeta) => {
    [bundleMeta].concat(neighboringCatchmentBundleMetas(bundleMeta)).forEach((candidate) => {
      const id = String(candidate?.id || '').trim();
      if (!id || seen.has(id)) return;
      seen.add(id);
      withNeighbors.push(candidate);
    });
  });
  return withNeighbors;
}

function ensureCatchmentBundlesForPoint(lat, lon) {
  return loadManchesterCatchmentIndex().then((indexMeta) => {
    if (!indexMeta) return [];
    return loadManchesterCatchmentBundles(bundleMetasForPoint(lat, lon));
  });
}

function bundleMetasForBounds(bounds) {
  if (!bounds || !manchesterCatchmentIndexMeta) return [];
  const directBundles = (manchesterCatchmentIndexMeta.bundles || []).filter((bundle) => {
    const bbox = Array.isArray(bundle?.expanded_bbox) ? bundle.expanded_bbox : bundle?.bbox;
    return boundsIntersectCatchmentBundleBbox(bounds, bbox);
  });
  const withNeighbors = [];
  const seen = new Set();
  directBundles.forEach((bundleMeta) => {
    [bundleMeta].concat(neighboringCatchmentBundleMetas(bundleMeta)).forEach((candidate) => {
      const id = String(candidate?.id || '').trim();
      if (!id || seen.has(id)) return;
      seen.add(id);
      withNeighbors.push(candidate);
    });
  });
  return withNeighbors;
}

function ensureCatchmentBundlesForBounds(bounds) {
  return loadManchesterCatchmentIndex().then((indexMeta) => {
    if (!indexMeta) return [];
    return loadManchesterCatchmentBundles(bundleMetasForBounds(bounds));
  });
}

function preloadManchesterCatchments() {
  window.setTimeout(() => {
    loadManchesterCatchmentIndex().then(() => {
      const preloadPromise = shouldPreloadVisibleCatchmentBundles()
        ? ensureCatchmentBundlesForBounds(map.getBounds().pad(0.08))
        : Promise.resolve([]);
      preloadPromise.then(() => {
        renderMarkers();
        updateHoveredCatchmentOutline();
        renderServiceFinderMarker();
        renderServiceFinder();
      });
    });
  }, 0);
}

function clearHoveredCatchmentOutline() {
  catchmentOutlineLayer.clearLayers();
}

function updateHoveredCatchmentOutline() {
  clearHoveredCatchmentOutline();
  if (map.getZoom() < MANCHESTER_CATCHMENT_MIN_ZOOM) return;
  if (!manchesterCatchmentIndex) return;
  const codes = Array.from(persistentCatchmentCodes);
  if (hoveredCatchmentCode && !persistentCatchmentCodes.has(hoveredCatchmentCode)) {
    codes.push(hoveredCatchmentCode);
  }
  if (!codes.length) return;
  codes.forEach((activeCode) => {
    const features = manchesterCatchmentIndex.get(activeCode) || [];
    if (!features.length) return;
    const layer = L.geoJSON({ type: 'FeatureCollection', features }, {
      style: () => ({
        color: '#7a7a7a',
        weight: 2.4,
        opacity: 0.9,
        fillOpacity: 0,
        dashArray: '6 4',
        interactive: false,
      }),
    });
    layer.addTo(catchmentOutlineLayer);
  });
}

function setHoveredCatchmentOutline(code) {
  hoveredCatchmentCode = String(code || '').trim() || null;
  if (!hoveredCatchmentCode) {
    updateHoveredCatchmentOutline();
    return;
  }
  ensureCatchmentBundleForCode(hoveredCatchmentCode).then(() => {
    updateHoveredCatchmentOutline();
  });
}

function clearHoveredCatchment(code = '') {
  const normalized = String(code || '').trim();
  if (normalized && hoveredCatchmentCode && hoveredCatchmentCode !== normalized) return;
  hoveredCatchmentCode = null;
  updateHoveredCatchmentOutline();
}

function togglePersistentCatchment(code) {
  const normalized = String(code || '').trim();
  if (!normalized) return;
  ensureCatchmentBundleForCode(normalized).then(() => {
    if (persistentCatchmentCodes.has(normalized)) {
      persistentCatchmentCodes.delete(normalized);
    } else {
      persistentCatchmentCodes.add(normalized);
    }
    updateHoveredCatchmentOutline();
  });
}

function serviceFinderDefaultDirection(sortKey) {
  return sortKey === 'practice' || sortKey === 'distance' ? 'asc' : 'desc';
}

function serviceFinderAccentColor(row) {
  const google = numericOrNull(row?.google_score);
  if (google !== null) return metricColorForValue('google', google);
  const survey = numericOrNull(row?.survey_overall_good_percent);
  if (survey !== null) return metricColorForValue('survey', survey);
  return '#9aa0a6';
}

function serviceFinderColumnValue(entry, sortKey) {
  const row = entry.row || entry;
  if (sortKey === 'practice') return String(row?.name || '').trim().toLowerCase();
  if (sortKey === 'distance') return Number.isFinite(entry.distance) ? entry.distance : null;
  if (sortKey === 'google') return numericOrNull(row?.google_score);
  if (sortKey === 'reviews') return numericOrNull(row?.google_count);
  if (sortKey === 'survey') return numericOrNull(row?.survey_overall_good_percent);
  if (sortKey === 'patients') return numericOrNull(row?.registered_patient_count_effective ?? row?.registered_patient_count);
  return null;
}

function updateServiceFinderSortButtons() {
  document.querySelectorAll('[data-service-finder-sort]').forEach((button) => {
    const key = button.getAttribute('data-service-finder-sort');
    const indicator = button.querySelector('.service-finder-sort-indicator');
    const isActive = key === serviceFinderSortKey;
    button.classList.toggle('is-active', isActive);
    if (indicator) indicator.textContent = isActive ? (serviceFinderSortDirection === 'asc' ? '▲' : '▼') : '';
  });
}

function clearServiceFinderButtonFlash() {
  if (serviceFinderButtonFlashTimer) {
    window.clearTimeout(serviceFinderButtonFlashTimer);
    serviceFinderButtonFlashTimer = null;
  }
  serviceFinderButtonFlash = '';
}

function flashServiceFinderButton(label, duration = 2600) {
  clearServiceFinderButtonFlash();
  serviceFinderButtonFlash = label;
  renderServiceFinder();
  serviceFinderButtonFlashTimer = window.setTimeout(() => {
    serviceFinderButtonFlash = '';
    serviceFinderButtonFlashTimer = null;
    renderServiceFinder();
  }, duration);
}

function serviceFinderButtonText() {
  if (serviceFinderButtonFlash) return serviceFinderButtonFlash;
  if (serviceFinderDragActive || serviceFinderArmed) return serviceFinderPoint ? '📍 Pick Home' : '📍 Pick a Location';
  if (serviceFinderPoint) return '📍 Move Home';
  return '📍 Find Practices';
}

function serviceFinderExtraButtonText() {
  if (!serviceFinderPoint) return 'Add place';
  return serviceFinderExtraPoint ? 'Move place' : 'Add place';
}

function serviceFinderActiveDragLabel() {
  if (serviceFinderExtraArmed) return '📍 Add a Place';
  return '📍 Pick Home';
}

function clearServiceFinderMatches() {
  serviceFinderMatchedRows = null;
  serviceFinderHomeCodeSet = new Set();
  serviceFinderExtraCodeSet = new Set();
  serviceFinderMatchedCodeSet = new Set();
  serviceFinderOutOfAreaCodeSet = new Set();
  serviceFinderDistanceFallbackCodeSet = new Set();
  serviceFinderHomeDistanceFallbackCodeSet = new Set();
  serviceFinderExtraDistanceFallbackCodeSet = new Set();
  serviceFinderNationalDistanceFallbackCodeSet = new Set();
  serviceFinderEnglishMissingCatchmentCodeSet = new Set();
  serviceFinderMatchedStateKey = '';
  serviceFinderMatchLoadPromise = null;
  serviceFinderOutOfAreaEligibleCount = 0;
  serviceFinderOutOfAreaVisibleCount = 0;
  serviceFinderDistanceFallbackVisibleCount = 0;
}

function normalizeServiceFinderOutOfAreaMiles(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 5;
  return Math.max(0, Math.min(30, Math.round(numeric)));
}

function serviceFinderSearchLog(label, payload) {
  try {
    console.info(`[service-finder] ${label}`, payload);
  } catch (_error) {
    return;
  }
}

function removeServiceFinderDragGhost() {
  if (serviceFinderDragGhost?.parentNode) {
    serviceFinderDragGhost.parentNode.removeChild(serviceFinderDragGhost);
  }
  serviceFinderDragGhost = null;
}

function updateServiceFinderDragGhost(clientX, clientY) {
  if (!serviceFinderDragGhost) {
    serviceFinderDragGhost = document.createElement('div');
    serviceFinderDragGhost.className = 'service-finder-drag-ghost';
    document.body.appendChild(serviceFinderDragGhost);
  }
  serviceFinderDragGhost.textContent = serviceFinderActiveDragLabel();
  serviceFinderDragGhost.style.left = `${clientX}px`;
  serviceFinderDragGhost.style.top = `${clientY}px`;
}

function mapLatLngFromClientPoint(clientX, clientY) {
  const container = map.getContainer();
  if (!container) return null;
  const rect = container.getBoundingClientRect();
  if (clientX < rect.left || clientX > rect.right || clientY < rect.top || clientY > rect.bottom) {
    return null;
  }
  const point = L.point(clientX - rect.left, clientY - rect.top);
  return map.containerPointToLatLng(point);
}

function updateServiceFinderButtons() {
  const text = serviceFinderButtonText();
  const title = serviceFinderPoint
    ? (serviceFinderArmed
      ? 'Click the map to move your home pin. Use Add place for another regular location.'
      : 'Click to move your home pin. You can also add another regular location.')
    : (serviceFinderArmed
      ? 'Click the map to place a practice lookup pin.'
      : 'Click, then click the map to place a practice lookup pin.');
  ['service-finder-place-button', 'service-finder-map-button'].forEach((id) => {
    const button = document.getElementById(id);
    if (!button) return;
    button.classList.toggle('is-active', serviceFinderArmed);
    button.title = title;
    const label = button.querySelector('span');
    if (label) label.textContent = text;
  });
  ['service-finder-extra-place-button', 'service-finder-map-extra-button'].forEach((id) => {
    const extraButton = document.getElementById(id);
    if (!extraButton) return;
    extraButton.disabled = !serviceFinderPoint;
    extraButton.hidden = !serviceFinderPoint;
    extraButton.classList.toggle('is-active', serviceFinderExtraArmed);
    extraButton.title = !serviceFinderPoint
      ? 'Add a home pin first, then you can add another place.'
      : 'Add another place you often go to, such as work or the school run.';
    const label = extraButton.querySelector('span');
    if (label) label.textContent = id === 'service-finder-map-extra-button' ? '+ Add' : serviceFinderExtraButtonText();
  });
}

function scrollToServiceFinder() {
  const heading = document.getElementById('service-finder-heading');
  if (!heading) return;
  heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderServiceFinderMarker() {
  serviceFinderPointLayer.clearLayers();
  if (!serviceFinderPoint) return;
  if (!manchesterCatchmentIndexMeta && !manchesterCatchmentLoadPromise) {
    loadManchesterCatchmentIndex().then(() => {
      clearServiceFinderMatches();
      renderMarkers();
      renderNationalSupplementals();
      renderServiceFinderMarker();
      renderServiceFinder();
    });
  }
  if (!serviceFinderMatchedRows && !serviceFinderMatchLoadPromise && !manchesterCatchmentLoadError) {
    loadServiceFinderMatchesForPoint(serviceFinderPoint.lat, serviceFinderPoint.lon).then(() => {
      renderMarkers();
      renderNationalSupplementals();
      renderServiceFinderMarker();
      renderServiceFinder();
    });
  }
  const matches = serviceFinderRowsForPoint(serviceFinderPoint.lat, serviceFinderPoint.lon);
  const homeMaybeCount = matches ? serviceFinderHomeDistanceFallbackCodeSet.size : null;
  const homeCatchmentCount = matches ? serviceFinderHomeCodeSet.size : null;
  const homeCount = matches ? serviceFinderHomeCodeSet.size + serviceFinderHomeDistanceFallbackCodeSet.size : null;
  const countText = manchesterCatchmentLoadError ? '!' : homeCount === null ? '…' : String(homeCount);
  const homeIsHouse = Boolean(serviceFinderExtraPoint);
  const icon = L.divIcon({
    className: 'service-finder-pin-icon',
    html: homeIsHouse
      ? `<div class="service-finder-home-pin-wrap"><svg class="service-finder-home-pin" viewBox="0 0 48 48" aria-hidden="true"><path d="M8 21.5 24 8l16 13.5V39a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2Z" fill="#161816" stroke="#fff" stroke-width="2.6" stroke-linejoin="round"/></svg><span class="service-finder-home-pin-count">${escapeHtml(countText)}</span></div>`
      : `<div class="service-finder-pin${homeCount !== null && homeCount >= 100 ? ' is-large' : ''}">${escapeHtml(countText)}</div>`,
    iconSize: homeIsHouse ? [42, 42] : (homeCount !== null && homeCount >= 100 ? [44, 44] : [38, 38]),
    iconAnchor: homeIsHouse ? [21, 21] : (homeCount !== null && homeCount >= 100 ? [22, 22] : [19, 19]),
  });
  const tooltip = manchesterCatchmentLoadError
    ? `${serviceFinderExtraPoint ? 'Home' : (serviceFinderLocationLabel || 'Selected location')} · catchments failed to load`
    : homeCount === null
      ? `${serviceFinderExtraPoint ? 'Home' : (serviceFinderLocationLabel || 'Selected location')} · waiting for catchments`
      : homeMaybeCount
        ? `${serviceFinderExtraPoint ? 'Home' : (serviceFinderLocationLabel || 'Selected location')} · ${homeCount.toLocaleString('en-GB')} possible match${homeCount === 1 ? '' : 'es'} (${homeCatchmentCount.toLocaleString('en-GB')} catchment, ${homeMaybeCount.toLocaleString('en-GB')} maybe)`
        : `${serviceFinderExtraPoint ? 'Home' : (serviceFinderLocationLabel || 'Selected location')} · ${homeCount.toLocaleString('en-GB')} matching catchment${homeCount === 1 ? '' : 's'}`;
  const marker = L.marker([serviceFinderPoint.lat, serviceFinderPoint.lon], { icon, draggable: true });
  marker.on('click', () => {
    scrollToServiceFinder();
  });
  marker.on('dragend', () => {
    const latlng = marker.getLatLng();
    setServiceFinderPoint(latlng.lat, latlng.lng, 'Selected location');
  });
  marker
    .bindTooltip(tooltip, { sticky: false, opacity: 0.94 })
    .addTo(serviceFinderPointLayer);
  if (!serviceFinderExtraPoint) return;
  const extraMaybeCount = matches ? serviceFinderExtraDistanceFallbackCodeSet.size : null;
  const extraCatchmentCount = matches ? serviceFinderExtraCodeSet.size : null;
  const extraCount = matches ? serviceFinderExtraCodeSet.size + serviceFinderExtraDistanceFallbackCodeSet.size : null;
  const extraCountText = manchesterCatchmentLoadError ? '!' : extraCount === null ? '…' : String(extraCount);
  const extraIcon = L.divIcon({
    className: 'service-finder-pin-icon',
    html: `<div class="service-finder-place-pin${extraCount !== null && extraCount >= 100 ? ' is-large' : ''}">${escapeHtml(extraCountText)}</div>`,
    iconSize: extraCount !== null && extraCount >= 100 ? [38, 38] : [34, 34],
    iconAnchor: extraCount !== null && extraCount >= 100 ? [19, 19] : [17, 17],
  });
  const extraMarker = L.marker([serviceFinderExtraPoint.lat, serviceFinderExtraPoint.lon], { icon: extraIcon, draggable: true });
  extraMarker.on('click', () => {
    scrollToServiceFinder();
  });
  extraMarker.on('dragend', () => {
    const latlng = extraMarker.getLatLng();
    setServiceFinderExtraPoint(latlng.lat, latlng.lng, 'Extra place');
  });
  extraMarker.on('contextmenu', () => {
    clearServiceFinderExtraPoint();
  });
  extraMarker
    .bindTooltip(
      manchesterCatchmentLoadError
        ? `${serviceFinderExtraLocationLabel || 'Extra place'} · catchments failed to load`
        : extraCount === null
          ? `${serviceFinderExtraLocationLabel || 'Extra place'} · waiting for catchments`
          : extraMaybeCount
            ? `${serviceFinderExtraLocationLabel || 'Extra place'} · ${extraCount.toLocaleString('en-GB')} possible match${extraCount === 1 ? '' : 'es'} (${extraCatchmentCount.toLocaleString('en-GB')} catchment, ${extraMaybeCount.toLocaleString('en-GB')} maybe)`
            : `${serviceFinderExtraLocationLabel || 'Extra place'} · ${extraCount.toLocaleString('en-GB')} matching catchment${extraCount === 1 ? '' : 's'}`,
      { sticky: false, opacity: 0.94 }
    )
    .addTo(serviceFinderPointLayer);
}

function clearServiceFinderPoint() {
  serviceFinderArmed = false;
  serviceFinderExtraArmed = false;
  serviceFinderPoint = null;
  serviceFinderLocationLabel = '';
  serviceFinderExtraPoint = null;
  serviceFinderExtraLocationLabel = '';
  serviceFinderEmptyMessage = '';
  serviceFinderShowAllOutOfArea = false;
  clearServiceFinderMatches();
  clearServiceFinderButtonFlash();
  renderMarkers();
  renderServiceFinderMarker();
  renderServiceFinder();
}

function clearServiceFinderExtraPoint() {
  if (!serviceFinderExtraPoint) return;
  serviceFinderExtraArmed = false;
  serviceFinderExtraPoint = null;
  serviceFinderExtraLocationLabel = '';
  serviceFinderShowAllOutOfArea = false;
  clearServiceFinderMatches();
  clearServiceFinderButtonFlash();
  renderMarkers();
  renderServiceFinderMarker();
  renderServiceFinder();
}

function setServiceFinderPoint(lat, lon, label = 'Selected location') {
  serviceFinderArmed = false;
  serviceFinderExtraArmed = false;
  serviceFinderPoint = {
    lat: Number(lat),
    lon: Number(lon),
  };
  serviceFinderLocationLabel = label;
  serviceFinderEmptyMessage = '';
  serviceFinderShowAllOutOfArea = false;
  clearServiceFinderMatches();
  renderMarkers();
  renderServiceFinderMarker();
  renderServiceFinder();
  flashServiceFinderButton('✅ List Updated');
}

function setServiceFinderExtraPoint(lat, lon, label = 'Extra place') {
  if (!serviceFinderPoint) return;
  serviceFinderArmed = false;
  serviceFinderExtraArmed = false;
  serviceFinderExtraPoint = {
    lat: Number(lat),
    lon: Number(lon),
  };
  serviceFinderExtraLocationLabel = label;
  serviceFinderShowAllOutOfArea = false;
  clearServiceFinderMatches();
  renderMarkers();
  renderServiceFinderMarker();
  renderServiceFinder();
}

function computeServiceFinderMatchesForRows(rowsToTry, lat, lon) {
  if (!Array.isArray(rowsToTry) || !rowsToTry.length || !manchesterCatchmentIndex) {
    return { catchmentMatches: [], catchmentCodeSet: new Set() };
  }
  const point = turf.point([Number(lon), Number(lat)]);
  const catchmentMatches = [];
  const catchmentCodeSet = new Set();
  rowsToTry.forEach((row) => {
    const code = String(row?.code || '').trim();
    if (!code) return;
    const features = manchesterCatchmentIndex.get(code) || [];
    if (!features.length) return;
    const isMatch = features.some((feature) => {
      try {
        return turf.booleanPointInPolygon(point, feature);
      } catch (_error) {
        return false;
      }
    });
    if (!isMatch) return;
    catchmentMatches.push(row);
    catchmentCodeSet.add(code);
  });
  return { catchmentMatches, catchmentCodeSet };
}

function serviceFinderCandidateEntries(lat, lon) {
  return allKnownRows
    .map((row) => ({
      row,
      homeDistance: distanceMiles(lat, lon, Number(row?.lat), Number(row?.lon)),
      extraDistance: serviceFinderExtraPoint
        ? distanceMiles(serviceFinderExtraPoint.lat, serviceFinderExtraPoint.lon, Number(row?.lat), Number(row?.lon))
        : null,
    }))
    .map((entry) => ({
      ...entry,
      distance: [entry.homeDistance, entry.extraDistance].filter((value) => Number.isFinite(value)).reduce((best, value) => Math.min(best, value), Number.POSITIVE_INFINITY),
    }))
    .filter((entry) => Number.isFinite(entry.distance))
    .sort((left, right) => left.distance - right.distance || String(left.row?.name || '').localeCompare(String(right.row?.name || ''), 'en'));
}

function serviceFinderCandidateRowsForStage(entries, minCount, maxDistanceMiles) {
  return entries
    .filter((entry, index) => index < minCount || entry.distance <= maxDistanceMiles)
    .map((entry) => entry.row);
}

function serviceFinderUsesDistanceFallback(row) {
  const code = String(row?.code || '').trim();
  if (!code) return false;
  const nation = String(row?.nation || '').trim().toLowerCase();
  if (nation === 'scotland' || nation === 'wales' || nation === 'northern_ireland') return true;
  return nation === 'england' && !catchmentBundleMetaForCode(code);
}

function serviceFinderDistanceFallbackExtras(entries, excludedCodes) {
  const radiusMiles = normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMiles);
  const debug = {
    radiusMiles,
    totalCandidates: Array.isArray(entries) ? entries.length : 0,
    excludedByCatchment: 0,
    notUsingDistanceFallback: 0,
    notAcceptingNewPatients: 0,
    beyondRadius: 0,
    selectedCount: 0,
    selected: [],
  };
  if (radiusMiles <= 0) {
    return { rows: [], debug: { ...debug, disabled: true } };
  }
  const selectedEntries = entries
    .filter((entry) => {
      const code = String(entry?.row?.code || '').trim();
      if (!code) {
        debug.notUsingDistanceFallback += 1;
        return false;
      }
      if (excludedCodes.has(code)) {
        debug.excludedByCatchment += 1;
        return false;
      }
      if (!serviceFinderUsesDistanceFallback(entry?.row)) {
        debug.notUsingDistanceFallback += 1;
        return false;
      }
      if (entry?.row?.accepting_new_patients === false) {
        debug.notAcceptingNewPatients += 1;
        return false;
      }
      if (entry.distance > radiusMiles) {
        debug.beyondRadius += 1;
        return false;
      }
      return true;
    });
  debug.selectedCount = selectedEntries.length;
  debug.selected = selectedEntries.map((entry) => ({
    code: String(entry?.row?.code || '').trim(),
    name: String(entry?.row?.name || '').trim(),
    distanceMiles: Number.isFinite(entry?.distance) ? Number(entry.distance.toFixed(2)) : null,
    nation: String(entry?.row?.nation || '').trim().toLowerCase(),
  }));
  return {
    rows: selectedEntries.map((entry) => entry.row),
    debug,
  };
}

function serviceFinderOutOfAreaExtras(entries, excludedCodes) {
  const radiusMiles = normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMiles);
  const selectionLimit = serviceFinderShowAllOutOfArea ? Number.MAX_SAFE_INTEGER : 3;
  const debug = {
    radiusMiles,
    showAll: serviceFinderShowAllOutOfArea,
    selectionLimit,
    totalCandidates: Array.isArray(entries) ? entries.length : 0,
    excludedByCatchment: 0,
    excludedByDistanceFallback: 0,
    missingOutOfAreaFlag: 0,
    notAcceptingNewPatients: 0,
    beyondRadius: 0,
    eligibleCount: 0,
    selectedCount: 0,
    overflowCount: 0,
    selected: [],
  };
  if (radiusMiles <= 0) {
    return { rows: [], debug: { ...debug, disabled: true } };
  }
  const eligibleEntries = entries
    .filter((entry) => {
      const code = String(entry?.row?.code || '').trim();
      if (!code) {
        debug.missingOutOfAreaFlag += 1;
        return false;
      }
      if (excludedCodes.has(code)) {
        debug.excludedByCatchment += 1;
        return false;
      }
      if (serviceFinderUsesDistanceFallback(entry?.row)) {
        debug.excludedByDistanceFallback += 1;
        return false;
      }
      if (!entry?.row?.accepts_out_of_area_registrations) {
        debug.missingOutOfAreaFlag += 1;
        return false;
      }
      if (entry?.row?.accepting_new_patients === false) {
        debug.notAcceptingNewPatients += 1;
        return false;
      }
      if (entry.distance > radiusMiles) {
        debug.beyondRadius += 1;
        return false;
      }
      return true;
    });
  debug.eligibleCount = eligibleEntries.length;
  const selectedEntries = eligibleEntries
    .sort((left, right) => {
      const leftGoogle = numericOrNull(left.row.google_score);
      const rightGoogle = numericOrNull(right.row.google_score);
      if (leftGoogle === null && rightGoogle !== null) return 1;
      if (leftGoogle !== null && rightGoogle === null) return -1;
      if (leftGoogle !== null && rightGoogle !== null && leftGoogle !== rightGoogle) return rightGoogle - leftGoogle;
      const leftSurvey = numericOrNull(left.row.survey_overall_good_percent);
      const rightSurvey = numericOrNull(right.row.survey_overall_good_percent);
      if (leftSurvey === null && rightSurvey !== null) return 1;
      if (leftSurvey !== null && rightSurvey === null) return -1;
      if (leftSurvey !== null && rightSurvey !== null && leftSurvey !== rightSurvey) return rightSurvey - leftSurvey;
      const leftReviews = numericOrNull(left.row.google_count);
      const rightReviews = numericOrNull(right.row.google_count);
      if (leftReviews === null && rightReviews !== null) return 1;
      if (leftReviews !== null && rightReviews === null) return -1;
      if (leftReviews !== null && rightReviews !== null && leftReviews !== rightReviews) return rightReviews - leftReviews;
      if (left.distance !== right.distance) return left.distance - right.distance;
      return String(left.row?.name || '').localeCompare(String(right.row?.name || ''), 'en');
    })
    .slice(0, selectionLimit);
  debug.selectedCount = selectedEntries.length;
  debug.overflowCount = Math.max(0, debug.eligibleCount - debug.selectedCount);
  debug.selected = selectedEntries.map((entry) => ({
    code: String(entry?.row?.code || '').trim(),
    name: String(entry?.row?.name || '').trim(),
    distanceMiles: Number.isFinite(entry?.distance) ? Number(entry.distance.toFixed(2)) : null,
  }));
  return {
    rows: selectedEntries.map((entry) => entry.row),
    debug,
  };
}

function loadServiceFinderMatchesForPoint(lat, lon) {
  if (!serviceFinderPoint) return Promise.resolve([]);
  const extraPointKey = serviceFinderExtraPoint
    ? `${Number(serviceFinderExtraPoint.lat).toFixed(6)},${Number(serviceFinderExtraPoint.lon).toFixed(6)}`
    : 'none';
  const pointKey = `${Number(lat).toFixed(6)},${Number(lon).toFixed(6)}|extra=${extraPointKey}|out=${normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMiles)}|showall=${serviceFinderShowAllOutOfArea ? 1 : 0}`;
  if (serviceFinderMatchLoadPromise && serviceFinderMatchedStateKey === pointKey) return serviceFinderMatchLoadPromise;
  serviceFinderMatchedStateKey = pointKey;
  serviceFinderSearchLog('search-start', {
    pointKey,
    home: {
      lat: Number(lat.toFixed(6)),
      lon: Number(lon.toFixed(6)),
    },
    extra: serviceFinderExtraPoint ? {
      lat: Number(serviceFinderExtraPoint.lat.toFixed(6)),
      lon: Number(serviceFinderExtraPoint.lon.toFixed(6)),
    } : null,
    outOfAreaMiles: normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMiles),
    showAllOutOfArea: serviceFinderShowAllOutOfArea,
  });
  serviceFinderMatchLoadPromise = loadManchesterCatchmentIndex().then((indexMeta) => {
    if (!indexMeta) return [];
    const entries = serviceFinderCandidateEntries(lat, lon);
    const stages = [
      { minCount: 40, maxDistanceMiles: 20, minMatches: 6, minTried: 40 },
      { minCount: 80, maxDistanceMiles: 35, minMatches: 8, minTried: 80 },
      { minCount: 140, maxDistanceMiles: 55, minMatches: 10, minTried: 120 },
    ];
    const runStage = (stageIndex) => {
      const stage = stages[Math.min(stageIndex, stages.length - 1)];
      const rowsToTry = serviceFinderCandidateRowsForStage(entries, stage.minCount, stage.maxDistanceMiles);
      const bundleMetas = rowsToTry
        .map((row) => catchmentBundleMetaForCode(row.code))
        .filter((bundleMeta, index, array) => bundleMeta && array.findIndex((candidate) => candidate?.id === bundleMeta.id) === index);
      return loadManchesterCatchmentBundles(bundleMetas).then(() => {
        if (!serviceFinderPoint || serviceFinderMatchedStateKey !== pointKey) return [];
        const homeMatchResult = computeServiceFinderMatchesForRows(rowsToTry, lat, lon);
        const extraMatchResult = serviceFinderExtraPoint
          ? computeServiceFinderMatchesForRows(rowsToTry, serviceFinderExtraPoint.lat, serviceFinderExtraPoint.lon)
          : { catchmentMatches: [], catchmentCodeSet: new Set() };
        const homeCatchmentMatches = homeMatchResult.catchmentMatches;
        const homeCatchmentCodeSet = homeMatchResult.catchmentCodeSet;
        const extraCatchmentMatches = extraMatchResult.catchmentMatches.filter((row) => !homeCatchmentCodeSet.has(String(row?.code || '').trim()));
        const extraCatchmentCodeSet = extraMatchResult.catchmentCodeSet;
        const excludedOutOfAreaCodes = new Set(homeCatchmentCodeSet);
        extraCatchmentCodeSet.forEach((code) => excludedOutOfAreaCodes.add(code));
        const distanceFallbackResult = serviceFinderDistanceFallbackExtras(entries, excludedOutOfAreaCodes);
        const distanceFallbackExtras = distanceFallbackResult.rows;
        const distanceFallbackCodeSet = new Set(distanceFallbackExtras.map((row) => String(row?.code || '').trim()).filter(Boolean));
        const homeDistanceFallbackCodeSet = new Set();
        const extraDistanceFallbackCodeSet = new Set();
        const nationalDistanceFallbackCodeSet = new Set();
        const englishMissingCatchmentCodeSet = new Set();
        const fallbackRadiusMiles = normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMiles);
        distanceFallbackExtras.forEach((row) => {
          const code = String(row?.code || '').trim();
          if (!code) return;
          const nation = String(row?.nation || '').trim().toLowerCase();
          if (nation && nation !== 'england') {
            nationalDistanceFallbackCodeSet.add(code);
          } else {
            englishMissingCatchmentCodeSet.add(code);
          }
          const homeDistance = distanceMiles(lat, lon, Number(row?.lat), Number(row?.lon));
          if (Number.isFinite(homeDistance) && homeDistance <= fallbackRadiusMiles) {
            homeDistanceFallbackCodeSet.add(code);
          }
          if (!serviceFinderExtraPoint) return;
          const extraDistance = distanceMiles(serviceFinderExtraPoint.lat, serviceFinderExtraPoint.lon, Number(row?.lat), Number(row?.lon));
          if (Number.isFinite(extraDistance) && extraDistance <= fallbackRadiusMiles) {
            extraDistanceFallbackCodeSet.add(code);
          }
        });
        const outOfAreaResult = serviceFinderOutOfAreaExtras(entries, excludedOutOfAreaCodes);
        const outOfAreaExtras = outOfAreaResult.rows;
        const outOfAreaCodeSet = new Set(outOfAreaExtras.map((row) => String(row?.code || '').trim()).filter(Boolean));
        const matchesByCode = new Map();
        homeCatchmentMatches.concat(extraCatchmentMatches, distanceFallbackExtras, outOfAreaExtras).forEach((row) => {
          const code = String(row?.code || '').trim();
          if (!code || matchesByCode.has(code)) return;
          matchesByCode.set(code, row);
        });
        const matches = Array.from(matchesByCode.values());
        const matchedCodeSet = new Set(homeCatchmentCodeSet);
        extraCatchmentCodeSet.forEach((code) => matchedCodeSet.add(code));
        distanceFallbackCodeSet.forEach((code) => matchedCodeSet.add(code));
        outOfAreaCodeSet.forEach((code) => matchedCodeSet.add(code));
        serviceFinderMatchedRows = matches;
        serviceFinderHomeCodeSet = new Set(homeCatchmentCodeSet);
        serviceFinderExtraCodeSet = new Set(extraCatchmentCodeSet);
        serviceFinderMatchedCodeSet = matchedCodeSet;
        serviceFinderOutOfAreaCodeSet = outOfAreaCodeSet;
        serviceFinderDistanceFallbackCodeSet = distanceFallbackCodeSet;
        serviceFinderHomeDistanceFallbackCodeSet = homeDistanceFallbackCodeSet;
        serviceFinderExtraDistanceFallbackCodeSet = extraDistanceFallbackCodeSet;
        serviceFinderNationalDistanceFallbackCodeSet = nationalDistanceFallbackCodeSet;
        serviceFinderEnglishMissingCatchmentCodeSet = englishMissingCatchmentCodeSet;
        serviceFinderOutOfAreaEligibleCount = Number(outOfAreaResult.debug?.eligibleCount || 0);
        serviceFinderOutOfAreaVisibleCount = Number(outOfAreaResult.debug?.selectedCount || 0);
        serviceFinderDistanceFallbackVisibleCount = Number(distanceFallbackResult.debug?.selectedCount || 0);
        serviceFinderSearchLog('stage-result', {
          pointKey,
          stageIndex,
          rowsTried: rowsToTry.length,
          bundleCount: bundleMetas.length,
          homeCatchmentMatches: homeCatchmentMatches.length,
          homeCatchmentCodes: homeCatchmentCodeSet.size,
          extraCatchmentMatches: extraCatchmentMatches.length,
          extraCatchmentCodes: extraCatchmentCodeSet.size,
          homeDistanceFallbackCodes: homeDistanceFallbackCodeSet.size,
          extraDistanceFallbackCodes: extraDistanceFallbackCodeSet.size,
          distanceFallback: distanceFallbackResult.debug,
          outOfArea: outOfAreaResult.debug,
          combinedMatches: matches.length,
        });
        if (stageIndex >= stages.length - 1) {
          serviceFinderSearchLog('search-complete', {
            pointKey,
            reason: 'max-stage',
            matchCount: matches.length,
            outOfAreaMatchCount: outOfAreaCodeSet.size,
          });
          return matches;
        }
        if (matches.length >= stage.minMatches && rowsToTry.length >= stage.minTried) {
          serviceFinderSearchLog('search-complete', {
            pointKey,
            reason: 'stage-threshold-met',
            matchCount: matches.length,
            outOfAreaMatchCount: outOfAreaCodeSet.size,
          });
          return matches;
        }
        serviceFinderSearchLog('search-expand', {
          pointKey,
          nextStageIndex: stageIndex + 1,
          currentMatchCount: matches.length,
          requiredMinMatches: stage.minMatches,
          rowsTried: rowsToTry.length,
          requiredMinTried: stage.minTried,
        });
        return runStage(stageIndex + 1);
      });
    };
    return runStage(0);
  }).finally(() => {
    if (serviceFinderMatchedStateKey === pointKey) {
      serviceFinderMatchLoadPromise = null;
    }
  });
  return serviceFinderMatchLoadPromise;
}

function serviceFinderRowsForPoint(lat, lon) {
  if (!serviceFinderPoint) return null;
  if (Math.abs(Number(lat) - Number(serviceFinderPoint.lat)) > 0.0000005) return null;
  if (Math.abs(Number(lon) - Number(serviceFinderPoint.lon)) > 0.0000005) return null;
  return serviceFinderMatchedRows;
}

function serviceFinderResultRows(matches) {
  const entries = matches.map((row) => ({
    row,
    homeDistance: distanceMiles(serviceFinderPoint.lat, serviceFinderPoint.lon, Number(row.lat), Number(row.lon)),
    extraDistance: serviceFinderExtraPoint
      ? distanceMiles(serviceFinderExtraPoint.lat, serviceFinderExtraPoint.lon, Number(row.lat), Number(row.lon))
      : null,
  })).map((entry) => ({
    ...entry,
    distance: [entry.homeDistance, entry.extraDistance].filter((value) => Number.isFinite(value)).reduce((best, value) => Math.min(best, value), Number.POSITIVE_INFINITY),
  }));
  return entries.sort((left, right) => {
    const leftValue = serviceFinderColumnValue(left, serviceFinderSortKey);
    const rightValue = serviceFinderColumnValue(right, serviceFinderSortKey);
    if (leftValue === null && rightValue !== null) return 1;
    if (leftValue !== null && rightValue === null) return -1;
    if (leftValue !== null && rightValue !== null && leftValue !== rightValue) {
      if (typeof leftValue === 'string' || typeof rightValue === 'string') {
        return serviceFinderSortDirection === 'asc'
          ? String(leftValue).localeCompare(String(rightValue), 'en')
          : String(rightValue).localeCompare(String(leftValue), 'en');
      }
      return serviceFinderSortDirection === 'asc' ? leftValue - rightValue : rightValue - leftValue;
    }
    const leftGoogle = numericOrNull(left.row.google_score);
    const rightGoogle = numericOrNull(right.row.google_score);
    if (leftGoogle === null && rightGoogle !== null) return 1;
    if (leftGoogle !== null && rightGoogle === null) return -1;
    if (leftGoogle !== null && rightGoogle !== null && leftGoogle !== rightGoogle) return rightGoogle - leftGoogle;
    return String(left.row.name || '').localeCompare(String(right.row.name || ''), 'en');
  });
}

function renderServiceFinder() {
  const tbody = document.getElementById('service-finder-results');
  const clearButton = document.getElementById('service-finder-clear-button');
  const footnote = document.getElementById('service-finder-footnote');
  if (!tbody) return;
  if (footnote) {
    footnote.hidden = true;
    footnote.textContent = '';
  }
  updateServiceFinderSortButtons();
  updateServiceFinderButtons();
  if (clearButton) clearButton.disabled = !serviceFinderPoint;

  if (!serviceFinderPoint) {
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">${escapeHtml(serviceFinderEmptyMessage || 'Drop a pin or use your location.')}</td></tr>`;
    return;
  }

  if (!manchesterCatchmentIndexMeta && !manchesterCatchmentLoadPromise) {
    loadManchesterCatchmentIndex().then(() => {
      clearServiceFinderMatches();
      renderMarkers();
      renderNationalSupplementals();
      renderServiceFinderMarker();
      renderServiceFinder();
    });
  }

  if (manchesterCatchmentLoadError) {
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">Catchments failed to load: ${escapeHtml(manchesterCatchmentLoadError)}</td></tr>`;
    return;
  }

  if (!manchesterCatchmentIndexMeta) {
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">Loading catchment index...</td></tr>`;
    return;
  }

  if (!serviceFinderMatchedRows) {
    if (!serviceFinderMatchLoadPromise) {
      loadServiceFinderMatchesForPoint(serviceFinderPoint.lat, serviceFinderPoint.lon).then(() => {
        renderMarkers();
        renderNationalSupplementals();
        renderServiceFinderMarker();
        renderServiceFinder();
      });
    }
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">Loading nearby catchments...</td></tr>`;
    return;
  }

  const matches = serviceFinderRowsForPoint(serviceFinderPoint.lat, serviceFinderPoint.lon) || [];
  const ranked = serviceFinderResultRows(matches);
  const hiddenOutOfAreaCount = Math.max(0, serviceFinderOutOfAreaEligibleCount - serviceFinderOutOfAreaVisibleCount);
  const outOfAreaToggleMarkup = (serviceFinderOutOfAreaEligibleCount > 3 || serviceFinderShowAllOutOfArea) ? `
    <tr class="service-finder-more-row">
      <td colspan="6">
        <label class="service-finder-more-toggle">
          <input type="checkbox" data-service-finder-show-all-out-of-area ${serviceFinderShowAllOutOfArea ? 'checked' : ''}>
          <span>${serviceFinderShowAllOutOfArea ? `Showing all ${serviceFinderOutOfAreaEligibleCount} out-of-area options` : `Show ${hiddenOutOfAreaCount} more out-of-area options`}</span>
          <span class="service-finder-more-note">within ${normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMiles)} miles</span>
        </label>
      </td>
    </tr>
  ` : serviceFinderOutOfAreaEligibleCount > 0 ? `
    <tr class="service-finder-more-row">
      <td colspan="6">
        <span class="service-finder-more-note">Including ${serviceFinderOutOfAreaVisibleCount} out-of-area option${serviceFinderOutOfAreaVisibleCount === 1 ? '' : 's'} within ${normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMiles)} miles.</span>
      </td>
    </tr>
  ` : '';

  if (!ranked.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="service-finder-empty">No suggested practices matched this point within the current distance limit.</td></tr>`;
    return;
  }

  if (footnote && (serviceFinderNationalDistanceFallbackCodeSet.size > 0 || serviceFinderEnglishMissingCatchmentCodeSet.size > 0)) {
    footnote.hidden = false;
    const footnoteBits = [];
    if (serviceFinderNationalDistanceFallbackCodeSet.size > 0) {
      footnoteBits.push('Scottish, Welsh and Northern Irish practices do not publish catchments centrally, so nearer practices may still not accept your registration.');
    }
    if (serviceFinderEnglishMissingCatchmentCodeSet.size > 0) {
      footnoteBits.push(`Some nearby English practices also have no published catchment lookup, so they are shown as maybes.`);
    }
    footnote.textContent = footnoteBits.join(' ');
  }

  tbody.innerHTML = ranked.map((entry, index) => {
    const row = entry.row;
    const google = numericOrNull(row.google_score);
    const survey = numericOrNull(row.survey_overall_good_percent);
    const reviews = numericOrNull(row.google_count);
    const reviewsPerYear = numericOrNull(row.google_reviews_per_year);
    const patients = numericOrNull(row.registered_patient_count_effective ?? row.registered_patient_count);
    const patientChangePerYear = numericOrNull(row.patient_change_per_year);
    const distance = entry.distance;
    const code = String(row.code || '').trim();
    const accentColor = serviceFinderAccentColor(row);
    const primaryProfileUrl = practiceProfileUrl(row);
    const actionLink = practiceActionLink(row);
    const googleMapsUrl = String(row.google_maps_url || '').trim();
    const surveyUrl = String(row.survey_link_url || '').trim();
    const shortAddress = String(row.short_address || '').trim();
    const patientLabel = patients === null ? '?' : patients.toLocaleString('en-GB');
    const googleLabel = google === null ? '?' : google.toFixed(1);
    const reviewRateLabel = reviewsPerYear === null ? '' : `${reviewsPerYear < 10 ? reviewsPerYear.toFixed(1) : Math.round(reviewsPerYear)}/yr`;
    const reviewMainLabel = reviews === null ? '?' : Math.round(reviews).toLocaleString('en-GB');
    const reviewDetailMarkup = reviewRateLabel ? `<span class="service-finder-secondary-detail"> (${reviewRateLabel})</span>` : '';
    const reviewClass = reviews === null ? 'service-finder-secondary-value is-missing' : 'service-finder-secondary-value';
    const patientClass = patients === null ? 'service-finder-secondary-value is-missing' : 'service-finder-secondary-value';
    const roundedPatientChange = patientChangePerYear === null ? null : roundApproxPatientsPerYear(patientChangePerYear);
    const patientTrendClass = roundedPatientChange === null
      ? ''
      : roundedPatientChange > 0
        ? 'service-finder-secondary-trend is-positive'
        : roundedPatientChange < 0
          ? 'service-finder-secondary-trend is-negative'
          : 'service-finder-secondary-trend is-flat';
    const patientTrendLabel = roundedPatientChange === null
      ? ''
      : `(${roundedPatientChange > 0 ? '+' : roundedPatientChange < 0 ? '-' : ''}~${Math.abs(roundedPatientChange).toLocaleString('en-GB')}/yr)`;
    const surveyLabel = survey === null ? '?' : `${Math.round(survey)}%`;
    const googleClass = google === null ? 'service-finder-primary-value is-missing' : 'service-finder-primary-value';
    const surveyClass = survey === null ? 'service-finder-primary-value is-missing' : 'service-finder-primary-value';
    const googleStyle = google === null ? '' : ` style="color:${metricColorForValue('google', google)}"`;
    const surveyStyle = survey === null ? '' : ` style="color:${metricColorForValue('survey', survey)}"`;
    const distanceLabel = Number.isFinite(distance) ? `${distance.toFixed(distance < 10 ? 1 : 0)} mi` : '?';
    const scopeTags = [];
    const isHomeMatch = serviceFinderHomeCodeSet.has(code);
    const isExtraMatch = serviceFinderExtraCodeSet.has(code);
    const isOutOfAreaMatch = serviceFinderOutOfAreaCodeSet.has(code);
    const isDistanceFallbackMatch = serviceFinderDistanceFallbackCodeSet.has(code);
    const isNationalDistanceFallbackMatch = serviceFinderNationalDistanceFallbackCodeSet.has(code);
    const isEnglishDistanceFallbackMatch = isDistanceFallbackMatch && !isNationalDistanceFallbackMatch;
    const isMaybe = (!isHomeMatch && isExtraMatch) || isOutOfAreaMatch || isEnglishDistanceFallbackMatch;
    if (row.gtd) scopeTags.push('<span class="service-finder-tag">GTD</span>');
    if (isMaybe) scopeTags.push('<span class="service-finder-tag is-warning">Maybe</span>');
    if (isExtraMatch && !isHomeMatch) {
      scopeTags.push('<span class="service-finder-tag">Near place</span>');
    }
    if (isOutOfAreaMatch) {
      scopeTags.push('<span class="service-finder-tag">Out-of-area</span>');
    }
    const scopeTag = scopeTags.join('');
    const cqcRating = String(row.cqc_overall_rating || '').trim();
    const cqcUrl = String(row.cqc_location_url || '').trim();
    const cqcBadgeConfig = (() => {
      if (!cqcRating || !cqcUrl) return null;
      if (cqcRating === 'Outstanding') return { icon: '⭐', className: 'is-outstanding', title: 'CQC: Outstanding' };
      if (cqcRating === 'Good') return { icon: '✓', className: 'is-good', title: 'CQC: Good' };
      if (cqcRating === 'Requires improvement') return { icon: '⚠', className: 'is-requires-improvement', title: 'CQC: Requires improvement' };
      if (cqcRating === 'Inadequate') return { icon: '⛔', className: 'is-inadequate', title: 'CQC: Inadequate' };
      if (cqcRating === 'Insufficient evidence to rate') return { icon: '❔', className: 'is-insufficient-evidence', title: 'CQC: Insufficient evidence to rate' };
      return { icon: '❔', className: 'is-insufficient-evidence', title: `CQC: ${cqcRating}` };
    })();
    const cqcBadgeMarkup = cqcBadgeConfig
      ? `<a class="service-finder-cqc-badge ${cqcBadgeConfig.className}" href="${escapeHtml(cqcUrl)}" target="_blank" rel="noreferrer" title="${escapeHtml(cqcBadgeConfig.title)}">${cqcBadgeConfig.icon}</a>`
      : '';
    const titleMarkup = primaryProfileUrl
      ? `<a class="service-finder-practice-name" href="${escapeHtml(primaryProfileUrl)}" target="_blank" rel="noreferrer">${escapeHtml(row.name || row.code)}</a>`
      : `<button type="button" class="service-finder-practice-name" data-service-finder-code="${escapeHtml(row.code)}">${escapeHtml(row.name || row.code)}</button>`;
    const addressBits = [
      shortAddress ? `<span class="service-finder-subtle">${escapeHtml(shortAddress)}</span>` : '',
      row.postcode ? `<span class="service-finder-subtle">${escapeHtml(row.postcode)}</span>` : '',
    ].filter(Boolean);
    const acceptsOutOfAreaBadge = row.accepts_out_of_area_registrations
      ? '<span class="service-finder-address-badge" title="This practice says it accepts out-of-area registrations">Out-of-area OK</span>'
      : '';
    const addressLineMarkup = addressBits.length
      ? `<span class="service-finder-address-line">${addressBits.join('<span class="service-finder-address-separator">·</span>')}${acceptsOutOfAreaBadge}</span>`
      : '';
    const addressLinkUrl = googleMapsUrl || primaryProfileUrl;
    const addressMarkup = addressLinkUrl
      ? (addressLineMarkup ? `<a class="service-finder-address-link" href="${escapeHtml(addressLinkUrl)}" target="_blank" rel="noreferrer">${addressLineMarkup}</a>` : '')
      : addressLineMarkup;
    const googleValueMarkup = googleMapsUrl && google !== null
      ? `<a class="service-finder-primary-value-link" href="${escapeHtml(googleMapsUrl)}" target="_blank" rel="noreferrer"><span class="${googleClass}"${googleStyle}>${googleLabel}</span></a>`
      : `<span class="${googleClass}"${googleStyle}>${googleLabel}</span>`;
    const surveyValueMarkup = surveyUrl && survey !== null
      ? `<a class="service-finder-primary-value-link" href="${escapeHtml(surveyUrl)}" target="_blank" rel="noreferrer"><span class="${surveyClass}"${surveyStyle}>${surveyLabel}</span></a>`
      : `<span class="${surveyClass}"${surveyStyle}>${surveyLabel}</span>`;
    return `
      <tr class="service-finder-row" style="--service-finder-accent:${accentColor}">
        <td class="service-finder-practice">
          <div class="service-finder-practice-layout">
            <div class="service-finder-practice-main">
              <div class="service-finder-title-line">
                ${cqcBadgeMarkup}${titleMarkup}${scopeTag}
              </div>
              ${addressMarkup}
            </div>
            ${actionLink ? `<a class="service-finder-register-link" href="${escapeHtml(actionLink.url)}" target="_blank" rel="noreferrer">${escapeHtml(actionLink.label)}</a>` : ''}
          </div>
        </td>
        <td class="service-finder-distance-cell"><span class="service-finder-distance-value">${distanceLabel}</span></td>
        <td class="service-finder-primary-metric service-finder-primary-metric-google">
          ${googleValueMarkup}
          <span class="service-finder-primary-label">Google</span>
        </td>
        <td class="service-finder-primary-metric service-finder-primary-metric-survey">
          ${surveyValueMarkup}
          <span class="service-finder-primary-label">Survey</span>
        </td>
        <td class="service-finder-secondary-metric service-finder-secondary-metric-reviews">
          <span class="${reviewClass}">${reviewMainLabel}${reviewDetailMarkup}</span>
          <span class="service-finder-secondary-label">Review Count</span>
        </td>
        <td class="service-finder-secondary-metric service-finder-secondary-metric-patients">
          <span class="${patientClass}">${patientLabel}</span>
          ${patientTrendLabel ? `<span class="${patientTrendClass}">${patientTrendLabel}</span>` : ''}
          <span class="service-finder-secondary-label">Patients</span>
        </td>
      </tr>
    `;
  }).join('') + outOfAreaToggleMarkup;

  tbody.querySelectorAll('[data-service-finder-code]').forEach((button) => {
    button.addEventListener('click', () => {
      const code = button.getAttribute('data-service-finder-code');
      const row = rowsByCode.get(code);
      if (!row) return;
      focusRow(row);
      map.flyTo([Number(row.lat), Number(row.lon)], Math.max(map.getZoom(), 12), { duration: 0.65 });
      persistentCatchmentCodes.add(row.code);
      updateHoveredCatchmentOutline();
    });
  });
  tbody.querySelectorAll('[data-service-finder-show-all-out-of-area]').forEach((input) => {
    input.addEventListener('change', (event) => {
      serviceFinderShowAllOutOfArea = Boolean(event.target.checked);
      serviceFinderSearchLog('out-of-area-show-all-updated', {
        showAllOutOfArea: serviceFinderShowAllOutOfArea,
        eligibleCount: serviceFinderOutOfAreaEligibleCount,
        visibleCount: serviceFinderOutOfAreaVisibleCount,
      });
      clearServiceFinderMatches();
      renderMarkers();
      renderNationalSupplementals();
      renderServiceFinderMarker();
      renderServiceFinder();
    });
  });
}

function renderMarkers() {
  markerLayer.clearLayers();
  const assignments = shapeAssignment();
  const metric = metricConfigs[activeMetric];
  const markerPresentation = markerPresentationForZoom();
  const centroidByCode = activeAreaOverlay === 'population' ? voronoiCentroidByCode() : null;
  const visibleLocalRows = rowsVisibleForCurrentMap(rows, { requireBoundsAtHighZoom: false }).rows;
  const serviceFinderMatchedCodes = new Set(
    serviceFinderPoint && manchesterCatchmentIndex
      ? Array.from(serviceFinderMatchedCodeSet)
      : []
  );
  for (const row of visibleLocalRows) {
    const metricValue = metric.value(row);
    if (metricValue === null && activeMetric === 'google') {
      continue;
    }
    if (metricValue === null && activeMetric === 'gap') {
      continue;
    }
    if (activeMetric === 'gap' && activeGapMode === 'normalized' && metricValue > 0) {
      continue;
    }
    const color = metric.markerColor(row);
    const label = metric.markerLabel(row);
    const shapeName = assignments.get(row.management_company) || 'circle';
    const renderedShape = markerPresentation.simplifiedShape ? 'circle' : shapeName;
    const scale = markerPresentation.scaleMultiplier;
    const metrics = baseShapeMetrics(renderedShape);
    const fontSize = markerPresentation.showLabel
      ? Math.max(8, Math.min(13, Math.round(9 + scale * 4)))
      : 0;
    const baseZIndex = assignments.has(row.management_company) ? 1000 : 0;
    const scaledWidth = Math.round(metrics.width * scale);
    const scaledHeight = Math.round(metrics.height * scale);
    const icon = L.divIcon({
      className: 'marker-icon',
      html: markerSvg(renderedShape, color, label, fontSize, label === '?', serviceFinderMatchedCodes.has(row.code), {
        showLabel: markerPresentation.showLabel,
        shadowMode: markerPresentation.shadowMode,
      }),
      iconSize: [scaledWidth, scaledHeight],
      iconAnchor: [Math.round(metrics.anchorX * scale), Math.round(metrics.anchorY * scale)],
      popupAnchor: [0, Math.round(metrics.popupY * Math.max(scale, 0.75))]
    });
    const pos = centroidByCode && centroidByCode.has(row.code) ? centroidByCode.get(row.code) : [row.lat, row.lon];
    const marker = L.marker(pos, { icon, zIndexOffset: baseZIndex });
    marker.bindPopup(popupMarkup(row));
    marker.on('click', () => {
      togglePersistentCatchment(row.code);
      focusRow(row);
    });
    marker.on('mouseover', () => {
      marker.setZIndexOffset(baseZIndex + 2000);
      setHoveredCatchmentOutline(row.code);
    });
    marker.on('mouseout', () => {
      marker.setZIndexOffset(baseZIndex);
      clearHoveredCatchment(row.code);
    });
    marker.addTo(markerLayer);
  }
}

function renderNationalSupplementals() {
  nationalMarkerLayer.clearLayers();
  const note = document.getElementById('national-supplemental-note');
  const markerPresentation = markerPresentationForZoom();
  const notePrefix = (() => {
    if (!note) return '';
    const totalPatients = Number(note.dataset.totalPatients || 0).toLocaleString('en-GB');
    const totalPractices = Number(note.dataset.totalPractices || 0).toLocaleString('en-GB');
    return `🏴 National: ${totalPatients} 👥 · ${totalPractices} 🏥`;
  })();
  if (!nationalSupplementals.length) {
    if (note) note.textContent = '🏴 National: no supplementals built yet';
    return;
  }
  const metric = metricConfigs[activeMetric];
  const visibleResult = rowsVisibleForCurrentMap(nationalSupplementals, { requireBoundsAtHighZoom: true });
  const visibleRows = visibleResult.rows;
  const serviceFinderMatchedCodes = new Set(
    serviceFinderPoint && manchesterCatchmentIndex
      ? Array.from(serviceFinderMatchedCodeSet)
      : []
  );
  for (const row of visibleRows) {
    const metricValue = metric.value(row);
    if (metricValue === null && activeMetric === 'google') {
      continue;
    }
    if (metricValue === null && activeMetric === 'gap') {
      continue;
    }
    if (activeMetric === 'gap' && activeGapMode === 'normalized' && metricValue > 0) {
      continue;
    }
    const color = metric.markerColor(row);
    const label = metric.markerLabel(row);
    const scale = markerPresentation.scaleMultiplier;
    const metrics = baseShapeMetrics('circle');
    const fontSize = markerPresentation.showLabel
      ? Math.max(8, Math.min(12, Math.round(8 + scale * 4)))
      : 0;
    const scaledWidth = Math.round(metrics.width * scale);
    const scaledHeight = Math.round(metrics.height * scale);
    const icon = L.divIcon({
      className: 'marker-icon marker-icon-national',
      html: markerSvg('circle', color, label, fontSize, label === '?', serviceFinderMatchedCodes.has(row.code), {
        showLabel: markerPresentation.showLabel,
        shadowMode: markerPresentation.shadowMode,
      }),
      iconSize: [scaledWidth, scaledHeight],
      iconAnchor: [Math.round(metrics.anchorX * scale), Math.round(metrics.anchorY * scale)],
      popupAnchor: [0, Math.round(metrics.popupY * Math.max(scale, 0.75))]
    });
    const marker = L.marker([row.lat, row.lon], {
      pane: 'nationalSupplementals',
      icon,
      zIndexOffset: -300,
    });
    marker.bindPopup(nationalPopupMarkup(row));
    marker.on('click', () => {
      togglePersistentCatchment(row.code);
    });
    marker.on('mouseover', () => {
      marker.setZIndexOffset(1200);
      setHoveredCatchmentOutline(row.code);
    });
    marker.on('mouseout', () => {
      marker.setZIndexOffset(-300);
      clearHoveredCatchment(row.code);
    });
    marker.addTo(nationalMarkerLayer);
  }

  if (note) {
    const visibleText = `${visibleRows.length.toLocaleString('en-GB')} visible`;
    if (visibleResult.mode === 'interest' && Number.isFinite(visibleResult.practiceCount)) {
      note.textContent = `${notePrefix} · ${visibleText} from nearest ${visibleResult.practiceCount.toLocaleString('en-GB')} to current focus`;
    } else {
      note.textContent = `${notePrefix} · ${visibleText}`;
    }
  }
}

function correlation(points) {
  if (points.length < 2) return null;
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  const meanX = xs.reduce((sum, value) => sum + value, 0) / xs.length;
  const meanY = ys.reduce((sum, value) => sum + value, 0) / ys.length;
  let numerator = 0;
  let sumSqX = 0;
  let sumSqY = 0;
  for (let index = 0; index < points.length; index += 1) {
    const dx = xs[index] - meanX;
    const dy = ys[index] - meanY;
    numerator += dx * dy;
    sumSqX += dx * dx;
    sumSqY += dy * dy;
  }
  if (sumSqX === 0 || sumSqY === 0) return null;
  return numerator / Math.sqrt(sumSqX * sumSqY);
}

function linearRegression(points) {
  if (points.length < 2) return null;
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  const meanX = xs.reduce((sum, value) => sum + value, 0) / xs.length;
  const meanY = ys.reduce((sum, value) => sum + value, 0) / ys.length;
  let numerator = 0;
  let denominator = 0;
  for (let index = 0; index < points.length; index += 1) {
    const dx = xs[index] - meanX;
    numerator += dx * (ys[index] - meanY);
    denominator += dx * dx;
  }
  if (denominator === 0) return null;
  const slope = numerator / denominator;
  const intercept = meanY - (slope * meanX);
  return { slope, intercept };
}

function quadraticRegression(points) {
  if (points.length < 3) return null;
  let n = 0;
  let sx = 0;
  let sx2 = 0;
  let sx3 = 0;
  let sx4 = 0;
  let sy = 0;
  let sxy = 0;
  let sx2y = 0;
  points.forEach((point) => {
    const x = Number(point.x);
    const y = Number(point.y);
    if (!Number.isFinite(x) || !Number.isFinite(y)) return;
    const x2 = x * x;
    n += 1;
    sx += x;
    sx2 += x2;
    sx3 += x2 * x;
    sx4 += x2 * x2;
    sy += y;
    sxy += x * y;
    sx2y += x2 * y;
  });
  if (n < 3) return null;
  const matrix = [
    [sx4, sx3, sx2, sx2y],
    [sx3, sx2, sx, sxy],
    [sx2, sx, n, sy],
  ];
  for (let pivot = 0; pivot < 3; pivot += 1) {
    let bestRow = pivot;
    for (let row = pivot + 1; row < 3; row += 1) {
      if (Math.abs(matrix[row][pivot]) > Math.abs(matrix[bestRow][pivot])) bestRow = row;
    }
    if (Math.abs(matrix[bestRow][pivot]) < 1e-9) return null;
    if (bestRow !== pivot) [matrix[pivot], matrix[bestRow]] = [matrix[bestRow], matrix[pivot]];
    const pivotValue = matrix[pivot][pivot];
    for (let col = pivot; col < 4; col += 1) matrix[pivot][col] /= pivotValue;
    for (let row = 0; row < 3; row += 1) {
      if (row === pivot) continue;
      const factor = matrix[row][pivot];
      for (let col = pivot; col < 4; col += 1) matrix[row][col] -= factor * matrix[pivot][col];
    }
  }
  const [a, b, c] = matrix.map((row) => row[3]);
  if (![a, b, c].every((value) => Number.isFinite(value))) return null;
  return { a, b, c };
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}

function normalizedCounts(counts) {
  const safe = (counts || []).map((value) => Number(value) || 0);
  const total = safe.reduce((sum, value) => sum + value, 0);
  if (total <= 0) return safe.map(() => 0);
  return safe.map((value) => value / total);
}

function jensenShannonDivergence(leftCounts, rightCounts) {
  const left = normalizedCounts(leftCounts);
  const right = normalizedCounts(rightCounts);
  if (!left.length || left.length !== right.length) return 0;
  const midpoint = left.map((value, index) => (value + right[index]) / 2);
  const kl = (source, target) => source.reduce((sum, value, index) => {
    if (value <= 0 || target[index] <= 0) return sum;
    return sum + (value * Math.log2(value / target[index]));
  }, 0);
  return (kl(left, midpoint) + kl(right, midpoint)) / 2;
}

function percentile(sortedValues, value) {
  if (!sortedValues.length) return null;
  let lessOrEqual = 0;
  sortedValues.forEach((candidate) => {
    if (candidate <= value) lessOrEqual += 1;
  });
  return (lessOrEqual / sortedValues.length) * 100;
}

function mean(values) {
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function median(values) {
  if (!values.length) return null;
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) return sorted[middle];
  return (sorted[middle - 1] + sorted[middle]) / 2;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function distanceMiles(lat1, lon1, lat2, lon2) {
  const toRadians = (degrees) => (degrees * Math.PI) / 180;
  const earthRadiusMiles = 3958.8;
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * earthRadiusMiles * Math.asin(Math.sqrt(a));
}

function displayNationName(nation) {
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return 'England';
  if (normalized === 'scotland') return 'Scotland';
  if (normalized === 'wales') return 'Wales';
  if (normalized === 'northern_ireland') return 'Northern Ireland';
  return normalized ? normalized.replace(/_/g, ' ').replace(/\\b\\w/g, (match) => match.toUpperCase()) : 'Unknown';
}

function activeCompletionNation() {
  return completionScatterNationOrder[completionScatterNationIndex] || 'england';
}

function completionNationShortLabel(nation) {
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return 'E';
  if (normalized === 'scotland') return 'S';
  if (normalized === 'wales') return 'W';
  if (normalized === 'northern_ireland') return 'NI';
  return 'N';
}

function updateCompletionScopeControl() {
  const option = document.getElementById('completion-scope-national-option');
  const text = document.getElementById('completion-scope-national-label');
  const short = document.getElementById('completion-scope-national-short');
  if (completionScatterScope !== 'national') {
    if (option) option.title = 'Nation scope';
    if (text) text.textContent = 'Nations';
    if (short) short.textContent = 'N';
    return;
  }
  const nation = activeCompletionNation();
  const label = displayNationName(nation);
  if (option) option.title = `${label} scope`;
  if (text) text.textContent = label;
  if (short) short.textContent = completionNationShortLabel(nation);
}

function cityCatchmentForRow(row) {
  const lat = Number(row?.lat);
  const lon = Number(row?.lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
  let best = null;
  cityCatchments.forEach((city) => {
    const distance = distanceMiles(lat, lon, Number(city.lat), Number(city.lon));
    if (distance > Number(city.radius_miles)) return;
    if (!best || distance < best.distance) {
      best = { city, distance };
    }
  });
  return best ? best.city : null;
}

function rowsWithinCircle(rowsSubset, lat, lon, radiusMiles) {
  return rowsSubset.filter((row) => {
    const rowLat = Number(row?.lat);
    const rowLon = Number(row?.lon);
    if (!Number.isFinite(rowLat) || !Number.isFinite(rowLon)) return false;
    return distanceMiles(lat, lon, rowLat, rowLon) <= radiusMiles;
  });
}

function northSouthBucketForRow(row) {
  const lat = Number(row?.lat);
  const lon = Number(row?.lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
  const lonSpan = northSouthDivide.east.lon - northSouthDivide.west.lon;
  if (!Number.isFinite(lonSpan) || lonSpan === 0) return null;
  const t = (lon - northSouthDivide.west.lon) / lonSpan;
  const boundaryLat = northSouthDivide.west.lat + (t * (northSouthDivide.east.lat - northSouthDivide.west.lat));
  return lat >= boundaryLat ? 'North' : 'South';
}

const allKnownRows = rows.concat(nationalSupplementals);
const allKnownRowsByCode = (() => {
  const grouped = new Map();
  allKnownRows.forEach((row) => {
    const code = String(row?.code || '').trim();
    if (code && !grouped.has(code)) grouped.set(code, row);
  });
  return grouped;
})();
const totalKnownGoogleReviews = allKnownRows.reduce((sum, row) => {
  const count = numericOrNull(row?.google_count);
  return sum + (count !== null && count > 0 ? count : 0);
}, 0);
const cityRowsByCatchment = (() => {
  const grouped = new Map(cityCatchments.map((city) => [city.name, []]));
  allKnownRows.forEach((row) => {
    const city = cityCatchmentForRow(row);
    if (city && grouped.has(city.name)) {
      grouped.get(city.name).push(row);
    }
  });
  return grouped;
})();
const northSouthRows = (() => {
  const grouped = new Map([['North', []], ['South', []]]);
  allKnownRows.forEach((row) => {
    const bucket = northSouthBucketForRow(row);
    if (bucket && grouped.has(bucket)) {
      grouped.get(bucket).push(row);
    }
  });
  return grouped;
})();
const compositeRegionRowsByLabel = (() => {
  const grouped = new Map();
  compositeRegionDefinitions.forEach((definition) => {
    const subset = (definition?.codes || [])
      .map((code) => allKnownRowsByCode.get(String(code || '').trim()))
      .filter(Boolean);
    grouped.set(definition.label, subset);
  });
  return grouped;
})();
const regionGoogleSortedValues = allKnownRows
  .map((row) => numericOrNull(row.google_score))
  .filter((value) => value !== null && Number.isFinite(value))
  .sort((left, right) => left - right);
const regionSurveySortedValues = allKnownRows
  .map((row) => numericOrNull(row.survey_overall_good_percent))
  .filter((value) => value !== null && Number.isFinite(value))
  .sort((left, right) => left - right);
const globalGoogleAverage = mean(regionGoogleSortedValues);
const globalSurveyAverage = mean(regionSurveySortedValues);

function lowZoomMarkerPoolActive() {
  return map.getZoom() <= LOW_ZOOM_MARKER_POOL_MAX_ZOOM;
}

function lowZoomMarkerPoolPracticeLimit() {
  return map.getZoom() >= LOW_ZOOM_MARKER_POOL_MAX_ZOOM
    ? LOW_ZOOM_MARKER_POOL_CLOSE_ZOOM_PRACTICES
    : LOW_ZOOM_MARKER_POOL_BASE_PRACTICES;
}

function shouldPreloadVisibleCatchmentBundles() {
  return map.getZoom() >= MANCHESTER_CATCHMENT_MIN_ZOOM;
}

function validPracticeLatLng(row) {
  const lat = Number(row?.lat);
  const lon = Number(row?.lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
  return { lat, lon };
}

function focusedPracticeLatLng() {
  const focused = allKnownRowsByCode.get(String(focusedPracticeCode || '').trim());
  return focused ? validPracticeLatLng(focused) : null;
}

function fallbackLowZoomMarkerInterestLatLng() {
  const homePoint = validPracticeLatLng(serviceFinderPoint);
  if (homePoint) return homePoint;
  const extraPoint = validPracticeLatLng(serviceFinderExtraPoint);
  if (extraPoint) return extraPoint;
  const samplePoint = validPracticeLatLng(sampleCircleCenter);
  if (samplePoint) return samplePoint;
  const focusedPoint = focusedPracticeLatLng();
  if (focusedPoint) return focusedPoint;
  const center = map.getCenter();
  return center ? { lat: Number(center.lat), lon: Number(center.lng) } : null;
}

function currentLowZoomMarkerInterestLatLng() {
  const now = Date.now();
  if (
    lowZoomMarkerInterestLatLng &&
    Number.isFinite(lowZoomMarkerInterestLatLng.lat) &&
    Number.isFinite(lowZoomMarkerInterestLatLng.lon) &&
    (now - lowZoomMarkerInterestUpdatedAt) <= LOW_ZOOM_MARKER_POOL_MAX_AGE_MS
  ) {
    return lowZoomMarkerInterestLatLng;
  }
  return fallbackLowZoomMarkerInterestLatLng();
}

function lowZoomMarkerContext() {
  if (!lowZoomMarkerPoolActive()) return null;
  const interestPoint = currentLowZoomMarkerInterestLatLng();
  if (!interestPoint) return null;
  const practiceLimit = lowZoomMarkerPoolPracticeLimit();
  const cacheKey = `${map.getZoom()}:${practiceLimit}:${interestPoint.lat.toFixed(5)},${interestPoint.lon.toFixed(5)}`;
  if (lowZoomMarkerNearestPracticeCache && lowZoomMarkerNearestPracticeCacheKey === cacheKey) {
    return lowZoomMarkerNearestPracticeCache;
  }
  const nearest = Array.from(allKnownRowsByCode.values())
    .map((row) => {
      const point = validPracticeLatLng(row);
      const code = String(row?.code || '').trim();
      if (!point || !code) return null;
      return {
        code,
        distance: distanceMiles(interestPoint.lat, interestPoint.lon, point.lat, point.lon),
      };
    })
    .filter(Boolean)
    .sort((left, right) => left.distance - right.distance || left.code.localeCompare(right.code, 'en'))
    .slice(0, practiceLimit);
  const context = {
    interestPoint,
    practiceCount: nearest.length,
    codeSet: new Set(nearest.map((entry) => entry.code)),
  };
  lowZoomMarkerNearestPracticeCacheKey = cacheKey;
  lowZoomMarkerNearestPracticeCache = context;
  return context;
}

function rowsVisibleForCurrentMap(rowsToFilter, options = {}) {
  const requireBoundsAtHighZoom = options.requireBoundsAtHighZoom !== false;
  const validRows = rowsToFilter.filter((row) => validPracticeLatLng(row));
  const lowZoomContext = lowZoomMarkerContext();
  if (lowZoomContext) {
    return {
      rows: validRows.filter((row) => lowZoomContext.codeSet.has(String(row?.code || '').trim())),
      mode: 'interest',
      practiceCount: lowZoomContext.practiceCount,
      interestPoint: lowZoomContext.interestPoint,
    };
  }
  if (!requireBoundsAtHighZoom) {
    return {
      rows: validRows,
      mode: 'all',
      practiceCount: null,
      interestPoint: null,
    };
  }
  const bounds = map.getBounds().pad(0.04);
  return {
    rows: validRows.filter((row) => {
      const point = validPracticeLatLng(row);
      return point ? bounds.contains([point.lat, point.lon]) : false;
    }),
    mode: 'bounds',
    practiceCount: null,
    interestPoint: null,
  };
}

function scheduleLowZoomMarkerPoolRerender() {
  if (!lowZoomMarkerPoolActive()) return;
  if (lowZoomMarkerInterestRerenderTimer) return;
  lowZoomMarkerInterestRerenderTimer = window.setTimeout(() => {
    lowZoomMarkerInterestRerenderTimer = null;
    renderMarkers();
    renderNationalSupplementals();
  }, LOW_ZOOM_MARKER_POOL_RERENDER_DELAY_MS);
}

function updateLowZoomMarkerInterest(latlng) {
  if (!latlng) return;
  const lat = Number(latlng.lat);
  const lon = Number(latlng.lng);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
  const nextPoint = { lat, lon };
  if (lowZoomMarkerInterestLatLng) {
    const previousContainerPoint = map.latLngToContainerPoint([lowZoomMarkerInterestLatLng.lat, lowZoomMarkerInterestLatLng.lon]);
    const nextContainerPoint = map.latLngToContainerPoint([nextPoint.lat, nextPoint.lon]);
    if (Math.hypot(nextContainerPoint.x - previousContainerPoint.x, nextContainerPoint.y - previousContainerPoint.y) < LOW_ZOOM_MARKER_POOL_MOVE_THRESHOLD_PX) {
      lowZoomMarkerInterestUpdatedAt = Date.now();
      return;
    }
  }
  lowZoomMarkerInterestLatLng = nextPoint;
  lowZoomMarkerInterestUpdatedAt = Date.now();
  scheduleLowZoomMarkerPoolRerender();
}

function positivePatientCount(row) {
  const patients = numericOrNull(row?.registered_patient_count);
  return patients !== null && patients > 0 ? patients : null;
}

function regionAverage(rowsSubset, extractor) {
  const values = rowsSubset
    .map((row) => extractor(row))
    .filter((value) => value !== null && Number.isFinite(value));
  return {
    value: values.length ? mean(values) : null,
    count: values.length,
  };
}

function formatPatientTotal(value) {
  if (value === null || !Number.isFinite(value) || value <= 0) return '?';
  if (value >= 1000000) {
    const millions = value / 1000000;
    return `${millions >= 10 ? millions.toFixed(0) : millions.toFixed(1)}m`;
  }
  if (value >= 1000) {
    const thousands = value / 1000;
    return `${thousands >= 100 ? thousands.toFixed(0) : thousands.toFixed(1)}k`;
  }
  return Math.round(value).toLocaleString('en-GB');
}

function formatAverageDelta(metricName, value) {
  if (value === null || !Number.isFinite(value)) return null;
  const globalAverage = metricName === 'google' ? globalGoogleAverage : globalSurveyAverage;
  if (globalAverage === null || !Number.isFinite(globalAverage)) return null;
  const delta = value - globalAverage;
  const tolerance = metricName === 'google' ? 0.04 : 1.5;
  if (Math.abs(delta) <= tolerance) return 'around dataset avg';
  if (metricName === 'google') {
    return `${Math.abs(delta).toFixed(2)} ${delta > 0 ? 'above' : 'below'} dataset avg`;
  }
  return `${Math.abs(delta).toFixed(1)}pp ${delta > 0 ? 'above' : 'below'} dataset avg`;
}

function datasetToneForAverage(metricName, value) {
  if (value === null || !Number.isFinite(value)) return 'tone-missing';
  const globalAverage = metricName === 'google' ? globalGoogleAverage : globalSurveyAverage;
  if (globalAverage === null || !Number.isFinite(globalAverage)) return 'tone-missing';
  const delta = value - globalAverage;
  const tolerance = metricName === 'google' ? 0.04 : 1.5;
  if (Math.abs(delta) <= tolerance) return 'tone-mid';
  return delta > 0 ? 'tone-good' : 'tone-bad';
}

function globalGapAverage() {
  const values = allKnownRows
    .map((row) => gapValue(row, { suppressSmall: false }))
    .filter((value) => value !== null && Number.isFinite(value));
  return values.length ? mean(values) : null;
}

function formatGapDeltaFromAverage(value) {
  if (value === null || !Number.isFinite(value)) return '?';
  return activeGapMode === 'normalized'
    ? `${value >= 0 ? '+' : ''}${value.toFixed(2)}z`
    : `${value >= 0 ? '+' : ''}${value.toFixed(2)}`;
}

function gapDeltaTone(delta) {
  if (delta === null || !Number.isFinite(delta)) return 'tone-missing';
  const tolerance = activeGapMode === 'normalized' ? 0.08 : 0.05;
  if (Math.abs(delta) <= tolerance) return 'tone-mid';
  return delta > 0 ? 'tone-good' : 'tone-bad';
}

function regionCardStats(rowsSubset) {
  const google = regionAverage(rowsSubset, (row) => numericOrNull(row.google_score));
  const survey = regionAverage(rowsSubset, (row) => numericOrNull(row.survey_overall_good_percent));
  const gap = regionAverage(rowsSubset, (row) => gapValue(row, { suppressSmall: false }));
  const patientTotal = rowsSubset.reduce((sum, row) => sum + (positivePatientCount(row) || 0), 0);
  return {
    practiceCount: rowsSubset.length,
    patientTotal: patientTotal > 0 ? patientTotal : null,
    google,
    survey,
    gap,
  };
}

function regionCountsMarkup(stats) {
  return `
    <div class="place-benchmark-counts">
      <span>${formatPatientTotal(stats.patientTotal)} <small>&#128101;</small></span>
      <span class="place-benchmark-count-divider">/</span>
      <span>${stats.practiceCount.toLocaleString('en-GB')} <small>&#127973;</small></span>
    </div>
  `;
}

function regionStatBoxMarkup(label, value, subtle, isActive, toneClass, extraClass = '') {
  const title = subtle ? ` title="${escapeHtml(String(subtle))}"` : '';
  return `
    <div class="place-benchmark-stat${isActive ? ' is-active' : ''}${extraClass ? ` ${extraClass}` : ''}"${title}>
      <span class="place-benchmark-stat-label">${label}</span>
      <span class="place-benchmark-stat-value ${toneClass || 'tone-missing'}">${value}</span>
    </div>
  `;
}

function surveyWarningForSubset(title, rowsSubset) {
  const nations = Array.from(
    new Set(
      rowsSubset
        .map((row) => String(row?.nation || '').trim().toLowerCase())
        .filter(Boolean)
    )
  );
  if (!nations.length) return null;
  const onlyNation = nations.length === 1 ? nations[0] : null;
  if (onlyNation === 'wales' || title === 'Cardiff') {
    return 'Wales does not currently have a standardized national practice-level survey feed here. Some Welsh practices appear to publish local survey results, but there is no comparable national dashboard, and mixing those local returns into this view would add noise.';
  }
  if (onlyNation === 'northern_ireland' || title === 'Belfast') {
    return 'Northern Ireland does not currently have a live standardized national practice-level survey feed here, so survey comparisons for this panel are incomplete.';
  }
  return null;
}

function regionCardMarkup(title, rowsSubset, accent) {
  const stats = regionCardStats(rowsSubset);
  const googleValue = stats.google.value === null ? '?' : stats.google.value.toFixed(2);
  const surveyValue = stats.survey.value === null ? '?' : `${stats.survey.value.toFixed(0)}%`;
  const googleTone = datasetToneForAverage('google', stats.google.value);
  const surveyTone = datasetToneForAverage('survey', stats.survey.value);
  const googleDelta = formatAverageDelta('google', stats.google.value);
  const surveyDelta = formatAverageDelta('survey', stats.survey.value);
  const googleSubtle = stats.google.count
    ? `${googleDelta || 'dataset avg unavailable'} · ${stats.google.count.toLocaleString('en-GB')} scored`
    : 'Google score not yet present';
  const surveySubtle = stats.survey.count
    ? `${surveyDelta || 'dataset avg unavailable'} · ${stats.survey.count.toLocaleString('en-GB')} scored`
    : 'Survey score not yet present';
  const isGoogleActive = activeMetric === 'google';
  const isSurveyActive = activeMetric === 'survey';
  const surveyWarning = surveyWarningForSubset(title, rowsSubset);
  const surveyLabel = surveyWarning ? 'Survey <span class="place-benchmark-stat-label-warning" aria-hidden="true">!</span>' : 'Survey';
  const surveyTitle = surveyWarning
    ? `${surveySubtle} · ${surveyWarning}`
    : surveySubtle;
  const surveyExtraClass = surveyWarning ? 'is-warning' : '';
  if (activeMetric === 'gap') {
    const overallGapAverage = globalGapAverage();
    const gapDelta = stats.gap.value === null || overallGapAverage === null ? null : stats.gap.value - overallGapAverage;
    const gapSubtle = stats.gap.count
      ? `Region avg: ${metricConfigs.gap.averageLabel(stats.gap.value)} · overall avg: ${metricConfigs.gap.averageLabel(overallGapAverage)} · ${stats.gap.count.toLocaleString('en-GB')} scored`
      : 'Gap score not yet present';
    return `
      <article class="comparison-card place-benchmark-card" style="border-top-color:${accent};">
        <div class="place-benchmark-header">
          <h3>${title}</h3>
          ${regionCountsMarkup(stats)}
        </div>
        <div class="place-benchmark-stats">
          ${regionStatBoxMarkup('Gap vs avg', formatGapDeltaFromAverage(gapDelta), gapSubtle, true, gapDeltaTone(gapDelta), 'is-wide')}
        </div>
      </article>
    `;
  }
  return `
    <article class="comparison-card place-benchmark-card" style="border-top-color:${accent};">
      <div class="place-benchmark-header">
        <h3>${title}</h3>
        ${regionCountsMarkup(stats)}
      </div>
      <div class="place-benchmark-stats">
        ${regionStatBoxMarkup('Google', googleValue, googleSubtle, isGoogleActive, googleTone)}
        ${regionStatBoxMarkup(surveyLabel, surveyValue, surveyTitle, isSurveyActive, surveyTone, surveyExtraClass)}
      </div>
    </article>
  `;
}

function renderCityCircles() {
  cityCircleLayer.clearLayers();
  if (!showCityCircles) return;
  cityCatchments.forEach((city) => {
    const subset = cityRowsByCatchment.get(city.name) || [];
    if (!subset.length) return;
    const circle = L.circle([city.lat, city.lon], {
      radius: Number(city.radius_miles) * 1609.344,
      color: city.accent,
      weight: 2,
      opacity: 0.65,
      fillColor: city.accent,
      fillOpacity: 0.04,
      dashArray: '6 6',
      interactive: false,
    });
    circle.bindTooltip(`${city.name} · ${subset.length} practices`, { sticky: false, opacity: 0.92 });
    circle.addTo(cityCircleLayer);
  });
}

function renderSampleCircle() {
  sampleCircleLayer.clearLayers();
  if (!sampleCircleCenter) return;
  const circle = L.circle([sampleCircleCenter.lat, sampleCircleCenter.lon], {
    radius: Number(sampleCircleRadiusMiles) * 1609.344,
    color: '#161816',
    weight: 2.2,
    opacity: 0.9,
    fillColor: '#161816',
    fillOpacity: 0.05,
    dashArray: '10 6',
  });
  circle.bindTooltip(`Custom sample · ${sampleCircleRadiusMiles.toFixed(1)} miles`, { sticky: false, opacity: 0.95 });
  circle.addTo(sampleCircleLayer);
}

function updateSampleCircleControls() {
  const sampleButton = document.getElementById('sample-circle-button');
  const clearButton = document.getElementById('clear-sample-circle-button');
  const note = document.getElementById('sample-circle-note');
  const radiusLabel = document.getElementById('sample-circle-radius-label');
  const radiusControl = document.querySelector('.circle-radius-control');
  const cityToggleLabel = document.getElementById('city-circles-control');
  if (sampleButton) sampleButton.classList.toggle('is-active', sampleCircleArmed);
  if (clearButton) clearButton.disabled = !sampleCircleCenter;
  if (radiusControl) radiusControl.hidden = !sampleCircleCenter;
  if (radiusLabel) radiusLabel.textContent = `${sampleCircleRadiusMiles.toFixed(sampleCircleRadiusMiles % 1 === 0 ? 0 : 1)} miles`;
  if (cityToggleLabel) cityToggleLabel.classList.toggle('is-active', showCityCircles);
  if (note) {
    note.textContent = sampleCircleArmed
      ? 'Click on the map to place the sample.'
      : sampleCircleCenter
        ? 'Drag the radius slider to resize the current sample.'
        : '';
  }
}

function googleCoverageRatio(rowsSubset) {
  if (!rowsSubset.length) return 0;
  const covered = rowsSubset.filter((row) => numericOrNull(row.google_score) !== null).length;
  return covered / rowsSubset.length;
}

function renderPlaceBenchmarks() {
  const heading = document.getElementById('place-benchmark-heading');
  const note = document.getElementById('place-benchmark-note');
  const nationHeading = document.getElementById('nation-benchmark-heading');
  const cityHeading = document.getElementById('city-benchmark-heading');
  const nationGrid = document.getElementById('nation-benchmark-grid');
  const cityGrid = document.getElementById('city-benchmark-grid');
  if (!heading || !note || !nationGrid || !cityGrid) return;

  heading.textContent = 'Nation and City Benchmarks';
  if (nationHeading) nationHeading.textContent = 'Nations';
  if (cityHeading) cityHeading.textContent = 'Cities and composites';
  const sampleRows = sampleCircleCenter
    ? rowsWithinCircle(allKnownRows, sampleCircleCenter.lat, sampleCircleCenter.lon, sampleCircleRadiusMiles)
    : [];

  const nationCards = nationOrder
    .map((nation) => {
      const subset = allKnownRows.filter((row) => String(row?.nation || '').trim().toLowerCase() === nation);
      if (!subset.length) return '';
      return regionCardMarkup(
        displayNationName(nation),
        subset,
        nation === 'england' ? '#8d3c17' : nation === 'scotland' ? '#2f6fa5' : nation === 'wales' ? '#3f7d4c' : '#6b4f9d'
      );
    })
    .filter(Boolean)
    .join('');

  const cityCards = cityCatchments
    .map((city) => {
      const subset = cityRowsByCatchment.get(city.name) || [];
      if (!subset.length) return '';
      return regionCardMarkup(city.name, subset, city.accent);
    })
    .concat(
      [
        ['North', '#315f8f'],
        ['South', '#8c5a2a'],
      ].map(([label, accent]) => {
        const subset = northSouthRows.get(label) || [];
        if (!subset.length) return '';
        return regionCardMarkup(label, subset, accent);
      })
    )
    .concat(
      compositeRegionDefinitions.map((definition) => {
        const subset = compositeRegionRowsByLabel.get(definition.label) || [];
        if (!subset.length) return '';
        return regionCardMarkup(definition.label, subset, definition.accent);
      })
    )
    .filter(Boolean)
    .join('');

  const sampleCard = sampleRows.length
    ? regionCardMarkup(
        `Custom sample · ${sampleCircleRadiusMiles.toFixed(sampleCircleRadiusMiles % 1 === 0 ? 0 : 1)} mile radius`,
        sampleRows,
        '#161816'
      )
    : '';

  nationGrid.innerHTML = nationCards || '<p class="hint">No nation summaries are available yet.</p>';
  cityGrid.innerHTML = (sampleCard + cityCards) || '<p class="hint">No city-circle summaries are available yet.</p>';
  note.innerHTML = `${allKnownRows.length.toLocaleString('en-GB')} practices · ${totalKnownGoogleReviews.toLocaleString('en-GB')} Google reviews loaded overall.${sampleRows.length ? ` Custom sample: ${sampleRows.length.toLocaleString('en-GB')} practices.` : ''} Sparse/dense composites use bottom/top fifths by nearby-practice count within ${COMPOSITE_REGION_RADIUS_MILES.toFixed(COMPOSITE_REGION_RADIUS_MILES % 1 === 0 ? 0 : 1)} miles, leaving the middle three-fifths neutral. List-size composites are separate: they use bottom/top fifths by registered patient count per practice, not local area population density, and rows without a patient count are excluded. <span class="hint">Footnote: Wales and Northern Ireland do not currently have comparable national practice-level survey feeds here. Some Welsh practices appear to publish local survey results, but there is no standardized national dashboard, and forcing those into the same pool would be easy to misread, especially given the limits of England's own standard survey.</span>`;
}

function metricValues(rowsSubset, metricName, extractor = null) {
  const metric = metricConfigs[metricName];
  return rowsSubset
    .map((row) => extractor ? extractor(row) : metric.value(row))
    .filter((value) => value !== null && Number.isFinite(value));
}

function formatMetricValue(value, metricName) {
  if (value === null) return '?';
  if (metricName === 'survey') return `${Math.round(value)}%`;
  return value.toFixed(metricName === 'gap' ? 2 : 1);
}

function currentMetricValueForRow(row, options = {}) {
  if (!row) return null;
  if (activeMetric === 'gap') {
    return gapValue(row, { suppressSmall: options.suppressSmall === true });
  }
  return metricConfigs[activeMetric].value(row);
}

function colorForCurrentMetric(row, options = {}) {
  if (!row) return '#9aa0a6';
  if (activeMetric !== 'gap') return metricConfigs[activeMetric].markerColor(row);
  const value = gapValue(row, { suppressSmall: options.suppressSmall === true });
  if (value === null) return '#9aa0a6';
  if (activeGapMode === 'normalized') {
    if (value >= 0.75) return '#1c7c54';
    if (value >= 0.25) return '#4c9a52';
    if (value > -0.25) return '#d2b529';
    if (value > -0.75) return '#dc8c23';
    return '#c3472f';
  }
  if (value >= 1.0) return '#1c7c54';
  if (value >= 0.5) return '#4c9a52';
  if (value > -0.5) return '#d2b529';
  if (value > -1.0) return '#dc8c23';
  return '#c3472f';
}

function compactMetricValue(value, metricName) {
  if (value === null) return '?';
  if (metricName === 'survey') return `${Math.round(value)}%`;
  if (metricName === 'google') return value.toFixed(1);
  return activeGapMode === 'normalized'
    ? `${value >= 0 ? '+' : ''}${value.toFixed(1)}z`
    : `${value >= 0 ? '+' : ''}${value.toFixed(1)}`;
}

function compactPatientCount(value) {
  if (!Number.isFinite(value)) return '?';
  if (value >= 100000) return `${Math.round(value / 1000)}k`;
  if (value >= 10000) return `${(value / 1000).toFixed(1)}k`;
  return Math.round(value).toLocaleString('en-GB');
}

function ellipsize(text, maxChars) {
  if (!text) return '';
  if (text.length <= maxChars) return text;
  return maxChars <= 3 ? text.slice(0, maxChars) : `${text.slice(0, Math.max(0, maxChars - 3))}...`;
}

function metricToneClass(metricName, value) {
  if (value === null) return 'tone-missing';
  if (metricName === 'google') {
    if (value < 3) return 'tone-bad';
    if (value < 4) return 'tone-mid';
    return 'tone-good';
  }
  if (metricName === 'survey') {
    if (value < 60) return 'tone-bad';
    if (value < 75) return 'tone-mid';
    return 'tone-good';
  }
  if (metricName === 'gap') {
    if (activeGapMode === 'normalized') {
      if (value <= -0.75) return 'tone-bad';
      if (value <= -0.25) return 'tone-mid';
      return 'tone-good';
    }
    if (value <= -1) return 'tone-bad';
    if (value <= -0.5) return 'tone-mid';
    return 'tone-good';
  }
  return 'tone-missing';
}

function comparisonSense(metricName) {
  return metricName === 'gap' ? 'higher' : 'higher';
}

function deltaSentence(subjectValue, benchmarkValue, metricName) {
  if (subjectValue === null || benchmarkValue === null) return 'insufficient data';
  const delta = subjectValue - benchmarkValue;
  if (Math.abs(delta) < (metricName === 'survey' ? 1 : 0.1)) return 'roughly in line';
  if (comparisonSense(metricName) === 'higher') {
    return delta > 0
      ? `${formatMetricValue(Math.abs(delta), metricName)} above`
      : `${formatMetricValue(Math.abs(delta), metricName)} below`;
  }
  return delta < 0
    ? `${formatMetricValue(Math.abs(delta), metricName)} lower gap`
    : `${formatMetricValue(Math.abs(delta), metricName)} higher gap`;
}

function benchmarkPhrase(subjectValue, benchmarkValue, metricName, label) {
  if (benchmarkValue === null) return `no ${label} comparison yet`;
  const delta = deltaSentence(subjectValue, benchmarkValue, metricName);
  if (delta === 'roughly in line') return `about the same as the ${label} typical score`;
  if (delta === 'insufficient data') return `not enough data for the ${label} comparison`;
  return `${delta} than the ${label} typical score`;
}

function performancePercentile(values, subjectValue, metricName) {
  if (!values.length || subjectValue === null) return null;
  if (comparisonSense(metricName) === 'higher') {
    return percentile(values.slice().sort((left, right) => left - right), subjectValue);
  }
  const reversed = values.map((value) => -value).sort((left, right) => left - right);
  return percentile(reversed, -subjectValue);
}

function performanceCounts(values, subjectValue, metricName) {
  if (!values.length || subjectValue === null) return { better: 0, worse: 0 };
  if (comparisonSense(metricName) === 'higher') {
    return {
      better: values.filter((value) => subjectValue > value).length,
      worse: values.filter((value) => subjectValue < value).length
    };
  }
  return {
    better: values.filter((value) => subjectValue < value).length,
    worse: values.filter((value) => subjectValue > value).length
  };
}

function benchmarkStats(subjectRows, localRows, regionalRows, metricName, subjectMode) {
  const subjectValues = metricValues(
    subjectRows,
    metricName,
    metricName === 'gap' && subjectMode === 'single'
      ? (row) => gapValue(row, { suppressSmall: false })
      : null
  );
  const localValues = metricValues(localRows, metricName);
  const regionalValues = metricValues(regionalRows, metricName);
  const completionSubjectValues = metricValues(subjectRows, metricName, (row) => numericOrNull(row.survey_completion_rate_percent));
  const completionLocalValues = metricValues(localRows, metricName, (row) => numericOrNull(row.survey_completion_rate_percent));
  const completionRegionalValues = metricValues(regionalRows, metricName, (row) => numericOrNull(row.survey_completion_rate_percent));
  const subjectValue = subjectMode === 'single'
    ? (subjectValues.length ? subjectValues[0] : null)
    : mean(subjectValues);
  const completionValue = subjectMode === 'single'
    ? (completionSubjectValues.length ? completionSubjectValues[0] : null)
    : mean(completionSubjectValues);
  return {
    subjectValue,
    subjectCount: subjectValues.length,
    localMedian: median(localValues),
    localCount: localValues.length,
    regionalMedian: median(regionalValues),
    regionalCount: regionalValues.length,
    regionalPercentile: performancePercentile(regionalValues, subjectValue, metricName),
    regionalPerformanceCounts: performanceCounts(regionalValues, subjectValue, metricName),
    completionValue,
    completionLocalMedian: median(completionLocalValues),
    completionLocalCount: completionLocalValues.length,
    completionRegionalMedian: median(completionRegionalValues),
    completionRegionalCount: completionRegionalValues.length,
    completionRegionalPercentile: performancePercentile(completionRegionalValues, completionValue, 'survey')
  };
}

function comparisonCardMarkup(title, kicker, summary, rowsMarkup, variant = '') {
  const cardClass = ['comparison-card', variant].filter(Boolean).join(' ');
  return `
    <article class="${cardClass}">
      <h3>${title}</h3>
      <p class="comparison-kicker">${kicker}</p>
      <div class="comparison-summary">${summary}</div>
      <div class="comparison-metrics">${rowsMarkup}</div>
    </article>
  `;
}

function comparisonRowMarkup(label, subjectLabel, subjectValue, subjectMeta, subjectTone, localLabel, localValue, localMeta, localTone, regionalLabel, regionalValue, regionalMeta, regionalTone, deltaText, deltaTone) {
  return `
    <div class="comparison-row">
      <div class="comparison-label">${label}</div>
      <div class="comparison-stat">
        <strong class="${subjectTone}">${subjectValue}</strong>
        <span>${subjectLabel}${subjectMeta ? ` · ${subjectMeta}` : ''}</span>
      </div>
      <div class="comparison-stat">
        <strong class="${localTone}">${localValue}</strong>
        <span>${localLabel}${localMeta ? ` · ${localMeta}` : ''}</span>
      </div>
      <div class="comparison-stat">
        <strong class="${regionalTone}">${regionalValue}</strong>
        <span>${regionalLabel}${regionalMeta ? ` · ${regionalMeta}` : ''}</span>
      </div>
      <div class="comparison-delta ${deltaTone}">${deltaText}</div>
    </div>
  `;
}

function deltaToneClass(subjectValue, benchmarkValue, metricName) {
  if (subjectValue === null || benchmarkValue === null) return 'tone-missing';
  const delta = subjectValue - benchmarkValue;
  if (Math.abs(delta) < (metricName === 'survey' ? 1 : 0.1)) return 'tone-mid';
  if (comparisonSense(metricName) === 'higher') return delta > 0 ? 'tone-good' : 'tone-bad';
  return delta < 0 ? 'tone-good' : 'tone-bad';
}

function countUnitLabel(count, pluralUnit) {
  if (pluralUnit === 'practices') return count === 1 ? 'practice' : 'practices';
  if (pluralUnit === 'management companies') return count === 1 ? 'management company' : 'management companies';
  return pluralUnit;
}

function metricScopeLabel(metricName) {
  if (metricName === 'google') return 'Google rating';
  if (metricName === 'survey') return 'patient survey overall good %';
  return activeGapMode === 'normalized' ? 'normalised survey/Google gap' : 'survey/Google gap';
}

function metricDisplayLabel(metricName) {
  if (metricName === 'google') return 'Reviews';
  if (metricName === 'survey') return 'Patient Survey';
  return activeGapMode === 'normalized' ? 'Normalised Gap' : 'Gap';
}

function nearbyLabelForMode(subjectMode) {
  return subjectMode === 'group' ? 'nearby non-company average' : 'nearby average';
}

function widerLabel() {
  return 'the wider map average';
}

function rankBarMarkup(countStats, pluralUnit) {
  if (!countStats) return '';
  const better = Number(countStats.better || 0);
  const worse = Number(countStats.worse || 0);
  const total = better + worse;
  if (total <= 0) return '';
  const position = (better / total) * 100;
  return `
    <div class="rank-bar" aria-label="Relative performance bar">
      <div class="rank-bar-track">
        <span class="rank-bar-marker" style="left:${position.toFixed(1)}%"></span>
      </div>
      <div class="rank-bar-labels">
        <span class="rank-worse">Worse than <strong>${worse}</strong> ${countUnitLabel(worse, pluralUnit)}</span>
        <span class="rank-better">Better than <strong>${better}</strong> ${countUnitLabel(better, pluralUnit)}</span>
      </div>
    </div>
  `;
}

function practiceComparisonCard(row, title, kicker, variant = '') {
  const metric = metricConfigs[activeMetric];
  const localRows = rows.filter((candidate) =>
    candidate.code !== row.code &&
    distanceMiles(row.lat, row.lon, candidate.lat, candidate.lon) <= LOCAL_RADIUS_MILES
  );
  const regionalRows = rows.filter((candidate) => candidate.code !== row.code);
  const stats = benchmarkStats([row], localRows, regionalRows, activeMetric, 'single');
  const summary = stats.subjectValue === null
    ? `<p>${title} does not have enough ${metric.title.toLowerCase()} data yet.</p>`
    : (() => {
        const localPhrase = benchmarkPhrase(stats.subjectValue, stats.localMedian, activeMetric, nearbyLabelForMode('single'));
        const regionalPhrase = benchmarkPhrase(stats.subjectValue, stats.regionalMedian, activeMetric, widerLabel());
        const percentilePhrase = stats.regionalPercentile === null
          ? ''
          : ` It sits around the ${Math.round(stats.regionalPercentile)}th percentile on this map.`;
        return `<p>On ${metricScopeLabel(activeMetric)}, ${title} is ${localPhrase} and ${regionalPhrase}.${percentilePhrase}</p>${rankBarMarkup(stats.regionalPerformanceCounts, 'practices')}`;
      })();
  return comparisonCardMarkup(
    title,
    kicker,
    summary,
    [
      comparisonRowMarkup(
        'Current score',
        'This practice',
        formatMetricValue(stats.subjectValue, activeMetric),
        stats.subjectCount ? `${stats.subjectCount} usable value` : '',
        metricToneClass(activeMetric, stats.subjectValue),
        'Nearby average',
        formatMetricValue(stats.localMedian, activeMetric),
        `${stats.localCount} peers`,
        metricToneClass(activeMetric, stats.localMedian),
        'Wider map average',
        formatMetricValue(stats.regionalMedian, activeMetric),
        `${stats.regionalCount} peers`,
        metricToneClass(activeMetric, stats.regionalMedian),
        stats.localMedian === null && stats.regionalMedian === null
          ? 'No comparison available yet'
          : `Nearby: ${deltaSentence(stats.subjectValue, stats.localMedian, activeMetric)}. Wider map: ${deltaSentence(stats.subjectValue, stats.regionalMedian, activeMetric)}.`,
        deltaToneClass(stats.subjectValue, stats.regionalMedian ?? stats.localMedian, activeMetric)
      ),
      comparisonRowMarkup(
        'Survey reply rate',
        'This practice',
        formatMetricValue(stats.completionValue, 'survey'),
        '',
        metricToneClass('survey', stats.completionValue),
        'Nearby average',
        formatMetricValue(stats.completionLocalMedian, 'survey'),
        `${stats.completionLocalCount} peers`,
        metricToneClass('survey', stats.completionLocalMedian),
        'Wider map average',
        formatMetricValue(stats.completionRegionalMedian, 'survey'),
        `${stats.completionRegionalCount} peers`,
        metricToneClass('survey', stats.completionRegionalMedian),
        stats.completionRegionalPercentile === null
          ? 'Reply-rate comparison unavailable'
          : `Reply rate sits around the ${Math.round(stats.completionRegionalPercentile)}th percentile on this map.`,
        deltaToneClass(stats.completionValue, stats.completionRegionalMedian ?? stats.completionLocalMedian, 'survey')
      )
    ].join(''),
    variant
  );
}

function managementCompanyComparisonCard(company, title, kicker, variant = '') {
  const metric = metricConfigs[activeMetric];
  const companyRows = company.rows;
  const companyOtherRows = rows.filter((row) => row.management_company !== company.name);
  const companyLocalRows = companyOtherRows.filter((row) =>
    companyRows.some((companyRow) => distanceMiles(companyRow.lat, companyRow.lon, row.lat, row.lon) <= LOCAL_RADIUS_MILES)
  );
  const stats = benchmarkStats(companyRows, companyLocalRows, companyOtherRows, activeMetric, 'group');
  const otherManagementCompanyValues = managementCompanies
    .filter((candidate) => candidate.name !== company.name)
    .map((candidate) => averageMetric(candidate.rows, activeMetric))
    .filter((value) => value !== null);
  const companyManagementPercentile = performancePercentile(otherManagementCompanyValues, stats.subjectValue, activeMetric);
  const companyManagementCounts = performanceCounts(otherManagementCompanyValues, stats.subjectValue, activeMetric);
  const summary = stats.subjectValue === null
    ? `<p>${title} does not have enough ${metric.title.toLowerCase()} data yet.</p>`
    : (() => {
        const localPhrase = benchmarkPhrase(stats.subjectValue, stats.localMedian, activeMetric, nearbyLabelForMode('group'));
        const regionalPhrase = benchmarkPhrase(stats.subjectValue, stats.regionalMedian, activeMetric, widerLabel());
        const percentilePhrase = companyManagementPercentile === null
          ? ''
          : ` It sits around the ${Math.round(companyManagementPercentile)}th percentile against the other management companies on this map.`;
        return `<p>On ${metricScopeLabel(activeMetric)}, ${title} is ${localPhrase} and ${regionalPhrase}.${percentilePhrase}</p>${rankBarMarkup(companyManagementCounts, 'management companies')}`;
      })();
  return comparisonCardMarkup(
    title,
    kicker,
    summary,
    [
      comparisonRowMarkup(
        'Current average',
        'Company average',
        formatMetricValue(stats.subjectValue, activeMetric),
        `${stats.subjectCount} practices with data`,
        metricToneClass(activeMetric, stats.subjectValue),
        'Nearby others',
        formatMetricValue(stats.localMedian, activeMetric),
        `${stats.localCount} peers`,
        metricToneClass(activeMetric, stats.localMedian),
        'Wider map average',
        formatMetricValue(stats.regionalMedian, activeMetric),
        `${stats.regionalCount} peers`,
        metricToneClass(activeMetric, stats.regionalMedian),
        stats.localMedian === null && stats.regionalMedian === null
          ? 'No comparison available yet'
          : `Nearby others: ${deltaSentence(stats.subjectValue, stats.localMedian, activeMetric)}. Wider map: ${deltaSentence(stats.subjectValue, stats.regionalMedian, activeMetric)}.`,
        deltaToneClass(stats.subjectValue, stats.regionalMedian ?? stats.localMedian, activeMetric)
      ),
      comparisonRowMarkup(
        'Survey reply rate',
        'Company average',
        formatMetricValue(stats.completionValue, 'survey'),
        `${metricValues(companyRows, 'survey', (row) => numericOrNull(row.survey_completion_rate_percent)).length} practices with data`,
        metricToneClass('survey', stats.completionValue),
        'Nearby others',
        formatMetricValue(stats.completionLocalMedian, 'survey'),
        `${stats.completionLocalCount} peers`,
        metricToneClass('survey', stats.completionLocalMedian),
        'Wider map average',
        formatMetricValue(stats.completionRegionalMedian, 'survey'),
        `${stats.completionRegionalCount} peers`,
        metricToneClass('survey', stats.completionRegionalMedian),
        stats.completionRegionalPercentile === null
          ? 'Reply-rate comparison unavailable'
          : `Reply rate sits around the ${Math.round(stats.completionRegionalPercentile)}th percentile on this map.`,
        deltaToneClass(stats.completionValue, stats.completionRegionalMedian ?? stats.completionLocalMedian, 'survey')
      )
    ].join(''),
    variant
  );
}

function renderComparisons() {
  const grid = document.getElementById('comparison-grid');
  const note = document.getElementById('comparison-note');
  const heading = document.getElementById('comparison-heading');
  const baselinePractice = rows.find((row) => row.code === NEW_BANK_CODE) || rows[0];
  const focusedPractice = rows.find((row) => row.code === focusedPracticeCode) || baselinePractice;
  const baselineCompany = managementCompanies.find((company) => company.name === BASELINE_MANAGEMENT_COMPANY) || null;
  const selectedCompanies = managementCompanies.filter((company) =>
    selectedManagementCompanies.has(company.name) && company.name !== BASELINE_MANAGEMENT_COMPANY
  );
  heading.textContent = `Quick comparisons - Showing ${metricDisplayLabel(activeMetric)}`;
  note.textContent = `New Bank and GTD always stay visible here. Click a practice on the map to compare it with New Bank. Use the management tickboxes to compare other companies with GTD. “Nearby” means within ${LOCAL_RADIUS_MILES.toFixed(1)} miles.`;

  const cards = [
    practiceComparisonCard(
      baselinePractice,
      baselinePractice.name,
      `Baseline practice${baselinePractice.postcode ? ` · ${baselinePractice.postcode}` : ''}`,
      'is-baseline'
    )
  ];

  if (focusedPractice && focusedPractice.code !== baselinePractice.code) {
    cards.push(
      practiceComparisonCard(
        focusedPractice,
        focusedPractice.name,
        `Selected practice${focusedPractice.postcode ? ` · ${focusedPractice.postcode}` : ''}`,
        'is-selected'
      )
    );
  }

  if (baselineCompany) {
    cards.push(
      managementCompanyComparisonCard(
        baselineCompany,
        baselineCompany.name,
        `Baseline management company · ${baselineCompany.count} practices`,
        'is-baseline'
      )
    );
  }

  selectedCompanies.forEach((company) => {
    cards.push(
      managementCompanyComparisonCard(
        company,
        company.name,
        `Selected management company · ${company.count} practices`,
        'is-selected'
      )
    );
  });

  grid.innerHTML = cards.join('');
}

function renderScatterplot() {
  const metric = metricConfigs[activeMetric];
  updateCompletionScopeControl();
  document.getElementById('scatter-heading').textContent = `Completion Rate vs Score - Showing ${metricDisplayLabel(activeMetric)}`;
  const scatterAxis = (() => {
    if (activeMetric !== 'gap') {
      return { min: metric.axisMin, max: metric.axisMax, label: metric.axisLabel, ticks: null };
    }
    const gapAxis = gapAxisInfo();
    return {
      min: 0,
      max: Math.max(0.5, gapAxis.max),
      label: gapAxis.magnitudeLabel,
      ticks: gapAxis.magnitudeTicks,
    };
  })();
  const completionNation = activeCompletionNation();
  const completionNationLabel = displayNationName(completionNation);
  const sourceRows = completionScatterScope === 'national'
    ? rows.concat(nationalSupplementals).filter((row) => String(row?.nation || '').trim().toLowerCase() === completionNation)
    : rows;
  const points = sourceRows
    .map((row) => {
      const signed = activeMetric === 'gap'
        ? gapValue(row, { suppressSmall: false })
        : metric.value(row);
      const x = signed === null ? null : (activeMetric === 'gap' ? Math.abs(signed) : signed);
      const y = numericOrNull(row.survey_completion_rate_percent);
      if (x === null || y === null) return null;
      return { row, x, y, signed };
    })
    .filter(Boolean);
  const svg = document.getElementById('scatterplot');
  const summary = document.getElementById('scatter-summary');
  const note = document.getElementById('scatter-note');
  const width = 920;
  const height = 320;
  const margin = { top: 34, right: 18, bottom: 42, left: 52 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const completionMax = Math.max(10, ...points.map((point) => point.y), 50);
  const xScale = (value) => margin.left + ((value - scatterAxis.min) / (scatterAxis.max - scatterAxis.min)) * plotWidth;
  const yScale = (value) => margin.top + plotHeight - (value / completionMax) * plotHeight;
  const gridY = [];
  for (let tick = 0; tick <= completionMax; tick += 10) {
    gridY.push(tick);
  }
  const gridX = scatterAxis.ticks || (
    activeMetric === 'google'
      ? [0, 1, 2, 3, 4, 5]
      : activeMetric === 'survey'
      ? [0, 20, 40, 60, 80, 100]
      : [0, 0.5, 1.0, 1.5, 2.0, 2.5]
  );
  const renderTrendLine = (linePoints, color, titleLabel, dash = '8 6') => {
    const trend = linearRegression(linePoints);
    if (!trend) return '';
    const candidates = [];
    const yAtMinX = (trend.slope * scatterAxis.min) + trend.intercept;
    const yAtMaxX = (trend.slope * scatterAxis.max) + trend.intercept;
    if (yAtMinX >= 0 && yAtMinX <= completionMax) candidates.push({ x: scatterAxis.min, y: yAtMinX });
    if (yAtMaxX >= 0 && yAtMaxX <= completionMax) candidates.push({ x: scatterAxis.max, y: yAtMaxX });
    if (Math.abs(trend.slope) > 1e-9) {
      const xAtZero = (0 - trend.intercept) / trend.slope;
      const xAtMaxY = (completionMax - trend.intercept) / trend.slope;
      if (xAtZero >= scatterAxis.min && xAtZero <= scatterAxis.max) candidates.push({ x: xAtZero, y: 0 });
      if (xAtMaxY >= scatterAxis.min && xAtMaxY <= scatterAxis.max) candidates.push({ x: xAtMaxY, y: completionMax });
    }
    const unique = [];
    candidates.forEach((candidate) => {
      const alreadyPresent = unique.some((entry) => Math.abs(entry.x - candidate.x) < 0.0001 && Math.abs(entry.y - candidate.y) < 0.0001);
      if (!alreadyPresent) unique.push(candidate);
    });
    if (unique.length < 2) return '';
    unique.sort((left, right) => (left.x === right.x ? left.y - right.y : left.x - right.x));
    const segment = [unique[0], unique[unique.length - 1]];
    return `
      <line x1="${xScale(segment[0].x).toFixed(2)}" y1="${yScale(segment[0].y).toFixed(2)}" x2="${xScale(segment[1].x).toFixed(2)}" y2="${yScale(segment[1].y).toFixed(2)}" stroke="${color}" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="${dash}">
        <title>${titleLabel} fitted trend line. Slope ${trend.slope.toFixed(2)} completion points per ${metric.title.toLowerCase()} unit.</title>
      </line>
    `;
  };
  const axisMarkup = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${gridY.map((tick) => `
      <line x1="${margin.left}" y1="${yScale(tick)}" x2="${width - margin.right}" y2="${yScale(tick)}" stroke="rgba(26,28,26,0.10)" />
      <text x="${margin.left - 8}" y="${yScale(tick) + 4}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${tick}%</text>
    `).join('')}
    ${gridX.map((tick) => `
      <line x1="${xScale(tick)}" y1="${margin.top}" x2="${xScale(tick)}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.08)" />
      <text x="${xScale(tick)}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${activeMetric === 'google' ? tick.toFixed(1) : activeMetric === 'survey' ? `${tick}%` : tick.toFixed(1)}</text>
    `).join('')}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">${scatterAxis.label}</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${height / 2})">${completionScatterScope === 'regional' ? 'GP survey completion rate' : 'Survey participation rate'}</text>
  `;
  if (completionScatterScope === 'regional') {
    const assignments = shapeAssignment();
    const pointMarkup = points.map((point) => {
      const companyShape = assignments.get(point.row.management_company);
      const radius = Math.max(4, Math.min(9, patientScaleForRow(point.row) * 6));
      const stroke = companyShape ? '#1a1c1a' : 'rgba(26,28,26,0.25)';
      const label = activeMetric === 'google'
        ? point.x.toFixed(1)
        : activeMetric === 'survey'
          ? `${Math.round(point.x)}%`
          : `${point.signed >= 0 ? '+' : ''}${point.signed.toFixed(2)} (|${point.x.toFixed(2)}|)`;
      return `
        <circle cx="${xScale(point.x).toFixed(2)}" cy="${yScale(point.y).toFixed(2)}" r="${radius.toFixed(2)}" fill="${metric.markerColor(point.row)}" stroke="${stroke}" stroke-width="${companyShape ? 1.8 : 1}">
          <title>${point.row.name} · ${metric.title}: ${label} · Completion: ${Math.round(point.y)}%</title>
        </circle>
      `;
    }).join('');
    const gtdPoints = points.filter((point) => point.row.gtd || point.row.management_company === BASELINE_MANAGEMENT_COMPANY);
    const gtdMeanPoint = gtdPoints.length
      ? {
          x: mean(gtdPoints.map((point) => point.x)),
          y: mean(gtdPoints.map((point) => point.y)),
        }
      : null;
    const newBankPoint = points.find((point) => point.row.code === NEW_BANK_CODE) || null;
    const regionalTrendMarkup = renderTrendLine(points, 'rgba(26,28,26,0.88)', 'Manchester');
    const focusMarkup = [
      gtdMeanPoint
        ? `
          <g>
            <circle cx="${xScale(gtdMeanPoint.x).toFixed(2)}" cy="${yScale(gtdMeanPoint.y).toFixed(2)}" r="6.5" fill="${GTD_MEAN_COLOR}" stroke="#ffffff" stroke-width="2">
              <title>GTD · ${metric.title} mean: ${activeMetric === 'google' ? gtdMeanPoint.x.toFixed(2) : activeMetric === 'survey' ? `${Math.round(gtdMeanPoint.x)}%` : gtdMeanPoint.x.toFixed(2)} · Completion mean: ${gtdMeanPoint.y.toFixed(1)}%</title>
            </circle>
            <text x="${(xScale(gtdMeanPoint.x) + 10).toFixed(2)}" y="${(yScale(gtdMeanPoint.y) - 2).toFixed(2)}" font-size="11" font-weight="700" fill="${GTD_MEAN_COLOR}">GTD</text>
          </g>
        `
        : '',
      newBankPoint
        ? `
          <g>
            <circle cx="${xScale(newBankPoint.x).toFixed(2)}" cy="${yScale(newBankPoint.y).toFixed(2)}" r="6.5" fill="#7b3fb2" stroke="#ffffff" stroke-width="2">
              <title>New Bank · ${metric.title}: ${activeMetric === 'google' ? newBankPoint.x.toFixed(2) : activeMetric === 'survey' ? `${Math.round(newBankPoint.x)}%` : newBankPoint.x.toFixed(2)} · Completion: ${newBankPoint.y.toFixed(1)}%</title>
            </circle>
            <text x="${(xScale(newBankPoint.x) + 10).toFixed(2)}" y="${(yScale(newBankPoint.y) - 18).toFixed(2)}" font-size="11" font-weight="700" fill="#7b3fb2">New Bank</text>
          </g>
        `
        : '',
    ].join('');
    svg.innerHTML = `${axisMarkup}${regionalTrendMarkup}${pointMarkup}${focusMarkup}`;
  } else {
    const showNationalOverlaySeries = completionNation === 'england';
    const xBinCount = activeMetric === 'google' ? 20 : 20;
    const yBinSize = 5;
    const yBinCount = Math.max(1, Math.ceil(completionMax / yBinSize));
    const cells = new Map();
    points.forEach((point) => {
      const xRatio = (point.x - scatterAxis.min) / (scatterAxis.max - scatterAxis.min || 1);
      const yRatio = point.y / completionMax;
      const xBin = Math.max(0, Math.min(xBinCount - 1, Math.floor(xRatio * xBinCount)));
      const yBin = Math.max(0, Math.min(yBinCount - 1, Math.floor(yRatio * yBinCount)));
      const key = `${xBin}-${yBin}`;
      cells.set(key, (cells.get(key) || 0) + 1);
    });
    const maxCellCount = Math.max(0, ...Array.from(cells.values()));
    const cellMarkup = [];
    for (let xBin = 0; xBin < xBinCount; xBin += 1) {
      const x0Value = scatterAxis.min + ((xBin / xBinCount) * (scatterAxis.max - scatterAxis.min));
      const x1Value = scatterAxis.min + (((xBin + 1) / xBinCount) * (scatterAxis.max - scatterAxis.min));
      const xMidValue = (x0Value + x1Value) / 2;
      for (let yBin = 0; yBin < yBinCount; yBin += 1) {
        const count = cells.get(`${xBin}-${yBin}`) || 0;
        const y0Value = (yBin / yBinCount) * completionMax;
        const y1Value = ((yBin + 1) / yBinCount) * completionMax;
        const x = xScale(x0Value);
        const y = yScale(y1Value);
        const widthPx = Math.max(0, xScale(x1Value) - xScale(x0Value));
        const heightPx = Math.max(0, yScale(y0Value) - yScale(y1Value));
        const fill = metricColorForValue(activeMetric, xMidValue);
        const opacity = count <= 0 || maxCellCount <= 0 ? 0.04 : 0.12 + (count / maxCellCount) * 0.74;
        cellMarkup.push(`
          <rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${widthPx.toFixed(2)}" height="${heightPx.toFixed(2)}" fill="${fill}" opacity="${opacity.toFixed(2)}" stroke="rgba(255,255,255,0.38)" stroke-width="0.5">
            <title>${count > 0 ? `${count.toLocaleString('en-GB')} practices` : 'No practices'} · ${metric.title} ${activeMetric === 'google' ? `${x0Value.toFixed(1)} to ${x1Value.toFixed(1)}` : activeMetric === 'survey' ? `${Math.round(x0Value)}% to ${Math.round(x1Value)}%` : `${x0Value.toFixed(2)} to ${x1Value.toFixed(2)}`} · Completion ${Math.round(y0Value)}% to ${Math.round(y1Value)}%</title>
          </rect>
        `);
      }
    }
    const overlaySeries = showNationalOverlaySeries ? [
      {
        label: 'Manchester',
        color: '#1f5f8b',
        rows: rows,
      },
      {
        label: 'GTD',
        color: GTD_MEAN_COLOR,
        rows: rows.filter((row) => row.gtd || row.management_company === BASELINE_MANAGEMENT_COMPANY),
      },
      {
        label: 'New Bank',
        color: '#7b3fb2',
        rows: rows.filter((row) => row.code === NEW_BANK_CODE),
      },
    ].map((series) => {
      const seriesPoints = series.rows
        .map((row) => {
          const signed = activeMetric === 'gap'
            ? gapValue(row, { suppressSmall: false })
            : metric.value(row);
          const x = signed === null ? null : (activeMetric === 'gap' ? Math.abs(signed) : signed);
          const y = numericOrNull(row.survey_completion_rate_percent);
          if (x === null || y === null) return null;
          return { x, y, signed };
        })
        .filter(Boolean);
      return {
        ...series,
        x: seriesPoints.length ? mean(seriesPoints.map((point) => point.x)) : null,
        y: seriesPoints.length ? mean(seriesPoints.map((point) => point.y)) : null,
        count: seriesPoints.length,
      };
    }).filter((series) => series.x !== null && series.y !== null) : [];
    const overlayMarkup = overlaySeries.map((series, index) => `
      <g>
        <circle cx="${xScale(series.x).toFixed(2)}" cy="${yScale(series.y).toFixed(2)}" r="6.5" fill="${series.color}" stroke="#ffffff" stroke-width="2">
          <title>${series.label} · ${series.count} practices · ${metric.title} mean: ${activeMetric === 'google' ? series.x.toFixed(2) : activeMetric === 'survey' ? `${Math.round(series.x)}%` : series.x.toFixed(2)} · Completion mean: ${series.y.toFixed(1)}%</title>
        </circle>
        <text x="${(xScale(series.x) + 10).toFixed(2)}" y="${(yScale(series.y) - (index * 16)).toFixed(2)}" font-size="11" font-weight="700" fill="${series.color}">${series.label}</text>
      </g>
    `).join('');
    const nationalTrendMarkup = renderTrendLine(points, 'rgba(26,28,26,0.88)', completionNationLabel);
    svg.innerHTML = `${axisMarkup}${cellMarkup.join('')}${nationalTrendMarkup}${overlayMarkup}`;
  }
  const completionValues = points.map((point) => point.y).sort((left, right) => left - right);
  const completionMedian = completionValues.length ? completionValues[Math.floor(completionValues.length / 2)] : null;
  const rValue = correlation(points);
  const newBank = points.find((point) => point.row.code === 'Y02960');
  const newBankSummary = completionScatterScope !== 'regional' || !newBank
    ? ''
    : ` New Bank Health is at ${Math.round(newBank.y)}% completion and sits around the ${percentile(completionValues, newBank.y).toFixed(0)}th percentile for completion in this set.`;
  if (completionScatterScope === 'regional') {
    summary.textContent =
      `${points.length} practices have both GP survey completion data and a usable ${metric.title.toLowerCase()} value. Median completion is ${completionMedian === null ? '?' : `${Math.round(completionMedian)}%`}. Pearson r is ${rValue === null ? '?' : rValue.toFixed(2)}.${newBankSummary}`;
    if (note) note.textContent = 'Y-axis is GP Patient Survey completion rate. X-axis changes with the selected score source. The GP survey score itself is heavily bunched near the top end, mostly around or just below 80%, while Google reviews look much more organically spread. At these demarcations that suggests either practices dropping below roughly 70% overall-good are corrected fairly quickly before they persist in the survey, or the patient survey is not really capturing the lower half of possible experience that clearly exists in review text.';
  } else {
    const regionalPoints = rows
      .map((row) => {
        const signed = activeMetric === 'gap'
          ? gapValue(row, { suppressSmall: false })
          : metric.value(row);
        const x = signed === null ? null : (activeMetric === 'gap' ? Math.abs(signed) : signed);
        const y = numericOrNull(row.survey_completion_rate_percent);
        if (x === null || y === null) return null;
        return { x, y, row };
      })
      .filter(Boolean);
    const gtdRegionalPoints = regionalPoints.filter((point) => point.row.gtd || point.row.management_company === BASELINE_MANAGEMENT_COMPANY);
    const newBankRegionalPoint = regionalPoints.find((point) => point.row.code === NEW_BANK_CODE) || null;
    const gmMeanX = regionalPoints.length ? mean(regionalPoints.map((point) => point.x)) : null;
    const gmMeanY = regionalPoints.length ? mean(regionalPoints.map((point) => point.y)) : null;
    const gtdMeanX = gtdRegionalPoints.length ? mean(gtdRegionalPoints.map((point) => point.x)) : null;
    const gtdMeanY = gtdRegionalPoints.length ? mean(gtdRegionalPoints.map((point) => point.y)) : null;
    summary.textContent = showNationalOverlaySeries
      ? `${points.length.toLocaleString('en-GB')} practices currently have both survey participation data and a usable ${metric.title.toLowerCase()} value in ${completionNationLabel}. Median participation is ${completionMedian === null ? '?' : `${Math.round(completionMedian)}%`}. Pearson r is ${rValue === null ? '?' : rValue.toFixed(2)}. Manchester is ${gmMeanY === null ? '?' : `${gmMeanY.toFixed(1)}% participation`} at ${gmMeanX === null ? '?' : activeMetric === 'google' ? gmMeanX.toFixed(2) : activeMetric === 'survey' ? `${Math.round(gmMeanX)}%` : gmMeanX.toFixed(2)}; GTD is ${gtdMeanY === null ? '?' : `${gtdMeanY.toFixed(1)}% participation`} at ${gtdMeanX === null ? '?' : activeMetric === 'google' ? gtdMeanX.toFixed(2) : activeMetric === 'survey' ? `${Math.round(gtdMeanX)}%` : gtdMeanX.toFixed(2)}; New Bank is ${newBankRegionalPoint === null ? '?' : `${newBankRegionalPoint.y.toFixed(1)}% participation`} at ${newBankRegionalPoint === null ? '?' : activeMetric === 'google' ? newBankRegionalPoint.x.toFixed(2) : activeMetric === 'survey' ? `${Math.round(newBankRegionalPoint.x)}%` : newBankRegionalPoint.x.toFixed(2)}.`
      : `${points.length.toLocaleString('en-GB')} practices currently have both survey participation data and a usable ${metric.title.toLowerCase()} value in ${completionNationLabel}. Median participation is ${completionMedian === null ? '?' : `${Math.round(completionMedian)}%`}. Pearson r is ${rValue === null ? '?' : rValue.toFixed(2)}.`;
    if (note) note.textContent = showNationalOverlaySeries
      ? 'Nation mode bins practices into density cells for speed and cycles England, Scotland, Wales, then Northern Ireland. Overlay dots keep Manchester, GTD, and New Bank visible as the local reference set. England currently uses GP Patient Survey completion rate; Scotland uses HACE response rate; Wales and Northern Ireland will show once equivalent practice-level rates are wired.'
      : 'Nation mode bins practices into density cells for speed and cycles England, Scotland, Wales, then Northern Ireland. For Scotland and other non-England nations, the local Manchester/GTD/New Bank overlays are hidden because the participation metric is not directly comparable enough. England currently uses GP Patient Survey completion rate; Scotland uses HACE response rate; Wales and Northern Ireland will show once equivalent practice-level rates are wired.';
  }
}

function renderDeprivationChart() {
  const metric = metricConfigs[activeMetric];
  document.getElementById('deprivation-heading').textContent = `Manchester Score vs Deprivation - Showing ${metricDisplayLabel(activeMetric)}`;
  const svg = document.getElementById('deprivation-chart');
  if (!svg) return;
  const gapAxis = gapAxisInfo();

  const points = rows
    .map((row) => {
      const dep = practiceDeprivationLookup[row.code];
      if (!dep) return null;
      const x = dep.imd_decile;
      const y = activeMetric === 'gap'
        ? gapValue(row, { suppressSmall: false })
        : metric.value(row);
      if (x === null || x === undefined || y === null) return null;
      return { row, x, y };
    })
    .filter(Boolean);

  const width = 920;
  const height = 320;
  const margin = { top: 34, right: 18, bottom: 42, left: 52 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const headerBandY = 4;
  const headerBandHeight = 17;
  const headerTextY = 16;

  const xMin = 1;
  const xMax = 10;
  const yMin = activeMetric === 'gap' ? gapAxis.min : metric.axisMin;
  const yMax = activeMetric === 'gap' ? gapAxis.max : metric.axisMax;

  const xBins = xMax - xMin + 1;
  const xCenter = (decile) => margin.left + ((decile - xMin + 0.5) / xBins) * plotWidth;
  const xBoundary = (boundaryIndex) => margin.left + (boundaryIndex / xBins) * plotWidth;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;

  const gridX = [];
  for (let tick = xMin; tick <= xMax; tick += 1) {
    gridX.push(tick);
  }

  const bucketCount = activeMetric === 'survey' ? 10 : 8;
  const gridY = [];
  const bucketHeight = (yMax - yMin) / bucketCount;
  for (let index = 0; index <= bucketCount; index += 1) {
    gridY.push(yMin + bucketHeight * index);
  }

  // Group points into (decile, value bucket) cells
  const cells = new Map();
  const overallBucketCounts = Array.from({ length: bucketCount }, () => 0);
  const columnBucketCounts = new Map(gridX.map((decile) => [decile, Array.from({ length: bucketCount }, () => 0)]));
  const columnPointMap = new Map(gridX.map((decile) => [decile, []]));
  points.forEach((point) => {
    const decile = Math.max(xMin, Math.min(xMax, Math.round(point.x)));
    const clampedY = Math.max(yMin, Math.min(yMax, point.y));
    const bucketIndex = Math.min(
      bucketCount - 1,
      Math.max(0, Math.floor(((clampedY - yMin) / (yMax - yMin)) * bucketCount))
    );
    const key = `${decile}-${bucketIndex}`;
    if (!cells.has(key)) cells.set(key, []);
    cells.get(key).push(point);
    overallBucketCounts[bucketIndex] += 1;
    columnBucketCounts.get(decile)[bucketIndex] += 1;
    columnPointMap.get(decile).push(point);
  });

  const assignments = shapeAssignment();
  const cellMarkup = [];
  const cellWidth = plotWidth / (xMax - xMin + 1);
  const cellInnerWidth = cellWidth * 0.92;
  const yPixelBucketHeight = plotHeight / bucketCount;
  const cellInnerHeight = yPixelBucketHeight * 0.92;

  // Fixed square size across the chart: pick the largest size that still fits the densest cell.
  const maxCellCount = Math.max(0, ...Array.from(cells.values(), (cellPoints) => cellPoints.length));
  function bestSquareSizeForCount(count) {
    if (!count) return 0;
    let best = 0;
    for (let cols = 1; cols <= count; cols += 1) {
      const rows = Math.ceil(count / cols);
      const size = Math.min(cellInnerWidth / cols, cellInnerHeight / rows);
      if (size > best) best = size;
    }
    return best;
  }
  const minSquareSize = 2.8;
  const maxSquareSize = 14;
  const fixedSquareSize = Math.max(minSquareSize, Math.min(maxSquareSize, bestSquareSizeForCount(maxCellCount)));
  const overallMeanValue = mean(points.map((point) => point.y));

  function bestCellLayout(count) {
    if (!count) return { cols: 1, rows: 1 };
    const targetAspect = cellInnerWidth / cellInnerHeight;
    let bestLayout = null;
    let bestScore = Infinity;
    for (let cols = 1; cols <= count; cols += 1) {
      const rows = Math.ceil(count / cols);
      const totalWidth = cols * fixedSquareSize;
      const totalHeight = rows * fixedSquareSize;
      if (totalWidth > cellInnerWidth + 0.001 || totalHeight > cellInnerHeight + 0.001) continue;
      const aspect = cols / rows;
      const aspectPenalty = Math.abs(aspect - targetAspect);
      const widthSlack = (cellInnerWidth - totalWidth) / cellInnerWidth;
      const heightSlack = (cellInnerHeight - totalHeight) / cellInnerHeight;
      const score = aspectPenalty + (widthSlack * 0.08) + (heightSlack * 0.03);
      if (score < bestScore || (Math.abs(score - bestScore) < 0.0001 && bestLayout && cols > bestLayout.cols)) {
        bestScore = score;
        bestLayout = { cols, rows };
      }
    }
    if (bestLayout) return bestLayout;
    const cols = Math.ceil(Math.sqrt(count));
    return { cols, rows: Math.ceil(count / cols) };
  }

  const distributionMarkup = gridX.map((decile) => {
    const columnPoints = columnPointMap.get(decile) || [];
    const counts = columnBucketCounts.get(decile) || Array.from({ length: bucketCount }, () => 0);
    const columnMean = columnPoints.length ? mean(columnPoints.map((point) => point.y)) : null;
    const shift = columnMean === null || overallMeanValue === null ? 0 : columnMean - overallMeanValue;
    const jsd = columnPoints.length ? jensenShannonDivergence(counts, overallBucketCounts) : 0;
    const shiftScale = Math.max(0.0001, (yMax - yMin) / 4);
    const shiftStrength = clamp01(Math.abs(shift) / shiftScale);
    const diffStrength = clamp01(jsd / 0.35);
    const isNeutral = shiftStrength < 0.12;
    const fill = isNeutral
      ? `hsl(215 12% ${(95 - diffStrength * 10).toFixed(1)}%)`
      : shift >= 0
        ? `hsl(151 40% ${(92 - ((diffStrength * 14) + (shiftStrength * 8))).toFixed(1)}%)`
        : `hsl(12 62% ${(92 - ((diffStrength * 14) + (shiftStrength * 8))).toFixed(1)}%)`;
    const bandFill = isNeutral
      ? `hsl(215 12% ${(82 - diffStrength * 14).toFixed(1)}%)`
      : shift >= 0
        ? `hsl(151 58% ${(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}%)`
        : `hsl(12 64% ${(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}%)`;
    const bandText = isNeutral ? 'rgba(26,28,26,0.82)' : '#ffffff';
    const x0 = xBoundary(decile - xMin);
    const x1 = xBoundary(decile - xMin + 1);
    const meanLabel = columnMean === null
      ? 'n/a'
      : activeMetric === 'survey'
        ? `${Math.round(columnMean)}%`
        : columnMean.toFixed(activeMetric === 'gap' ? 2 : 1);
    const title = !columnPoints.length
      ? `IMD decile ${decile}: no practices with usable data`
      : `IMD decile ${decile}: mean ${meanLabel}. Distribution is ${isNeutral ? 'similar to' : shift >= 0 ? 'better than' : 'worse than'} the overall pattern. Jensen-Shannon divergence ${jsd.toFixed(2)}.`;
    return `
      <g>
        <rect x="${x0.toFixed(2)}" y="${margin.top.toFixed(2)}" width="${(x1 - x0).toFixed(2)}" height="${plotHeight.toFixed(2)}" fill="${fill}">
          <title>${title}</title>
        </rect>
        <rect x="${(x0 + 2).toFixed(2)}" y="${headerBandY.toFixed(2)}" width="${Math.max(0, x1 - x0 - 4).toFixed(2)}" height="${headerBandHeight}" rx="6" fill="${bandFill}">
          <title>${title}</title>
        </rect>
        <text x="${((x0 + x1) / 2).toFixed(2)}" y="${headerTextY.toFixed(2)}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${bandText}">${meanLabel}</text>
      </g>
    `;
  }).join('');

  cells.forEach((cellPoints, key) => {
    const [decileStr, bucketStr] = key.split('-');
    const decile = Number(decileStr);
    const bucketIndex = Number(bucketStr);
    const centerX = xCenter(decile);
    const bucketYMin = yMin + bucketHeight * bucketIndex;
    const bucketYMax = bucketYMin + bucketHeight;
    const centerYValue = (bucketYMin + bucketYMax) / 2;
    const centerY = yScale(centerYValue);

    const count = cellPoints.length;
    const { cols, rows } = bestCellLayout(count);
    const totalWidth = cols * fixedSquareSize;
    const totalHeight = rows * fixedSquareSize;
    const startX = centerX - totalWidth / 2 + fixedSquareSize / 2;
    const startY = centerY - totalHeight / 2 + fixedSquareSize / 2;

    cellPoints.forEach((point, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      const cx = startX + col * fixedSquareSize;
      const cy = startY + row * fixedSquareSize;
      const companyShape = assignments.get(point.row.management_company);
      const stroke = companyShape ? '#1a1c1a' : 'rgba(26,28,26,0.25)';
      const label = activeMetric === 'google'
        ? point.y.toFixed(1)
        : activeMetric === 'survey'
          ? `${Math.round(point.y)}%`
          : point.y.toFixed(2);
      cellMarkup.push(`
        <rect x="${(cx - fixedSquareSize / 2).toFixed(2)}" y="${(cy - fixedSquareSize / 2).toFixed(2)}" width="${fixedSquareSize.toFixed(2)}" height="${fixedSquareSize.toFixed(2)}" rx="1.2" fill="${metric.markerColor(point.row)}" stroke="${stroke}" stroke-width="${companyShape ? 1 : 0.5}">
          <title>${point.row.name} · ${metric.title}: ${label} · IMD decile: ${decile}</title>
        </rect>
      `);
    });
  });

  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${distributionMarkup}
    ${gridY.map((tick) => `
      <line x1="${margin.left}" y1="${yScale(tick)}" x2="${width - margin.right}" y2="${yScale(tick)}" stroke="rgba(26,28,26,0.10)" />
    `).join('')}
    ${Array.from({ length: xBins + 1 }, (_, idx) => idx).map((boundaryIndex) => `
      <line x1="${xBoundary(boundaryIndex)}" y1="${margin.top}" x2="${xBoundary(boundaryIndex)}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.08)" />
    `).join('')}
    ${Array.from({ length: bucketCount }, (_, idx) => idx).map((bucketIndex) => {
      const bucketMid = yMin + bucketHeight * (bucketIndex + 0.5);
      const label = activeMetric === 'survey'
        ? `${Math.round(bucketMid)}%`
        : bucketMid.toFixed(activeMetric === 'gap' ? 2 : 1);
      return `
        <text x="${margin.left - 8}" y="${(yScale(bucketMid) + 4).toFixed(2)}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${label}</text>
      `;
    }).join('')}
    ${gridX.map((tick) => `
      <text x="${xCenter(tick)}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${tick}</text>
    `).join('')}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    ${cellMarkup.join('')}
    <text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">IMD 2025 decile (1 = most deprived)</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${height / 2})">${activeMetric === 'gap' ? gapAxis.label : metric.axisLabel}</text>
  `;

  const depValues = points.map((point) => point.x).sort((l, r) => l - r);
  const yValues = points.map((point) => point.y).sort((l, r) => l - r);
  const depMedian = depValues.length ? depValues[Math.floor(depValues.length / 2)] : null;
  const yMedian = yValues.length ? yValues[Math.floor(yValues.length / 2)] : null;
  const rValue = correlation(points.map((p) => ({ x: p.x, y: p.y })));
  const strongestDecile = gridX
    .map((decile) => {
      const counts = columnBucketCounts.get(decile) || [];
      const pointCount = (columnPointMap.get(decile) || []).length;
      return {
        decile,
        pointCount,
        jsd: pointCount ? jensenShannonDivergence(counts, overallBucketCounts) : 0,
      };
    })
    .sort((left, right) => right.jsd - left.jsd)[0];

  document.getElementById('deprivation-summary').textContent =
    `${points.length} practices have both a usable ${metric.title.toLowerCase()} value and mapped IMD 2025 decile. Median decile is ${depMedian === null ? '?' : depMedian} and median ${metric.title.toLowerCase()} is ${yMedian === null ? '?' : (activeMetric === 'survey' ? `${Math.round(yMedian)}%` : yMedian.toFixed(activeMetric === 'gap' ? 2 : 1))}. Pearson r for score vs decile is ${rValue === null ? '?' : rValue.toFixed(2)}. Column tint shows whether each decile skews better (green), worse (red), or similar (grey) versus the overall distribution, with stronger colour meaning a more different distribution. Strongest departure is decile ${strongestDecile && strongestDecile.pointCount ? strongestDecile.decile : '?'}.`;
}

function renderNationalDeprivationChart() {
  const metric = metricConfigs[activeMetric];
  const heading = document.getElementById('national-deprivation-heading');
  const summary = document.getElementById('national-deprivation-summary');
  const svg = document.getElementById('national-deprivation-chart');
  const populationToggle = document.getElementById('national-deprivation-population-toggle');
  if (!heading || !summary || !svg) return;
  if (populationToggle) {
    populationToggle.checked = nationalDeprivationUsePopulation;
  }
  heading.textContent = `National Score vs Deprivation - Showing ${metricDisplayLabel(activeMetric)}`;

  const combinedRows = rows.concat(nationalSupplementals);
  const gapAxis = gapAxisInfo();
  const points = combinedRows
    .map((row) => {
      const dep = allPracticeDeprivationLookup[row.code];
      if (!dep) return null;
      const decile = numericOrNull(dep.imd_decile);
      if (decile === null) return null;
      const y = activeMetric === 'gap'
        ? gapValue(row, { suppressSmall: false })
        : metric.value(row);
      if (y === null) return null;
      return { row, decile, y };
    })
    .filter(Boolean);

  const width = 920;
  const height = 320;
  const margin = { top: 28, right: 18, bottom: 42, left: 52 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const headerBandY = 4;
  const headerBandHeight = 17;
  const headerTextY = 16;
  const xMin = 1;
  const xMax = 10;
  const yMin = activeMetric === 'gap' ? gapAxis.min : metric.axisMin;
  const yMax = activeMetric === 'gap' ? gapAxis.max : metric.axisMax;
  const bucketCount = activeMetric === 'survey' ? 10 : activeMetric === 'gap' ? 10 : 10;
  const bucketHeight = (yMax - yMin) / bucketCount;
  const xBins = xMax - xMin + 1;
  const cellWidth = plotWidth / xBins;
  const cellHeight = plotHeight / bucketCount;

  const xCenter = (decile) => margin.left + ((decile - xMin + 0.5) / xBins) * plotWidth;
  const xBoundary = (boundaryIndex) => margin.left + (boundaryIndex / xBins) * plotWidth;
  const yBoundary = (boundaryIndex) => margin.top + plotHeight - (boundaryIndex / bucketCount) * plotHeight;
  const bucketMidValue = (bucketIndex) => yMin + bucketHeight * (bucketIndex + 0.5);
  const aggregateValueForRow = (row) => {
    if (!nationalDeprivationUsePopulation) return 1;
    const patients = numericOrNull(row.registered_patient_count);
    return patients !== null && patients > 0 ? patients : 0;
  };
  const formatCellValue = (value) => {
    if (value <= 0) return '';
    if (!nationalDeprivationUsePopulation) return String(Math.round(value));
    if (value >= 1000000) return `${(value / 1000000).toFixed(value >= 10000000 ? 0 : 1)}m`;
    if (value >= 1000) return `${(value / 1000).toFixed(value >= 100000 ? 0 : 1)}k`;
    return String(Math.round(value));
  };
  const formatAggregateLong = (value) => {
    if (!nationalDeprivationUsePopulation) {
      const rounded = Math.round(value);
      return `${rounded.toLocaleString('en-GB')} practice${rounded === 1 ? '' : 's'}`;
    }
    return `${Math.round(value).toLocaleString('en-GB')} registered patients`;
  };

  const cells = new Map();
  const columnCounts = new Map(Array.from({ length: xBins }, (_, index) => [index + 1, 0]));
  const columnPoints = new Map(Array.from({ length: xBins }, (_, index) => [index + 1, []]));
  const columnBucketCounts = new Map(Array.from({ length: xBins }, (_, index) => [index + 1, Array.from({ length: bucketCount }, () => 0)]));
  const overallBucketCounts = Array.from({ length: bucketCount }, () => 0);
  points.forEach((point) => {
    const decile = Math.max(xMin, Math.min(xMax, Math.round(point.decile)));
    const bucketIndex = Math.min(
      bucketCount - 1,
      Math.max(0, Math.floor(((Math.max(yMin, Math.min(yMax, point.y)) - yMin) / (yMax - yMin)) * bucketCount))
    );
    const key = `${decile}-${bucketIndex}`;
    const aggregate = aggregateValueForRow(point.row);
    cells.set(key, (cells.get(key) || 0) + aggregate);
    columnCounts.set(decile, (columnCounts.get(decile) || 0) + aggregate);
    columnPoints.get(decile).push(point);
    columnBucketCounts.get(decile)[bucketIndex] += 1;
    overallBucketCounts[bucketIndex] += 1;
  });

  const maxCellCount = Math.max(0, ...Array.from(cells.values()));
  const allLookupRows = combinedRows.filter((row) => allPracticeDeprivationLookup[row.code]);
  const matchedRows = combinedRows.filter((row) => numericOrNull(allPracticeDeprivationLookup[row.code]?.imd_decile) !== null);
  const overallMeanValue = mean(points.map((point) => point.y));
  const cellMarkup = [];
  const headerMarkup = [];
  for (let decile = xMin; decile <= xMax; decile += 1) {
    const columnTotal = columnCounts.get(decile) || 0;
    const decilePoints = columnPoints.get(decile) || [];
    const columnMean = decilePoints.length ? mean(decilePoints.map((point) => point.y)) : null;
    const counts = columnBucketCounts.get(decile) || Array.from({ length: bucketCount }, () => 0);
    const shift = columnMean === null || overallMeanValue === null ? 0 : columnMean - overallMeanValue;
    const jsd = decilePoints.length ? jensenShannonDivergence(counts, overallBucketCounts) : 0;
    const shiftScale = Math.max(0.0001, (yMax - yMin) / 4);
    const shiftStrength = clamp01(Math.abs(shift) / shiftScale);
    const diffStrength = clamp01(jsd / 0.35);
    const isNeutral = shiftStrength < 0.12;
    const x0 = xBoundary(decile - xMin);
    const x1 = xBoundary(decile - xMin + 1);
    const headerLabel = columnMean === null
      ? ''
      : activeMetric === 'survey'
        ? `${Math.round(columnMean)}%`
        : columnMean.toFixed(activeMetric === 'gap' ? 2 : 1);
    const headerFill = columnMean === null
      ? 'rgba(26,28,26,0.14)'
      : isNeutral
        ? `hsl(215 12% ${(82 - diffStrength * 14).toFixed(1)}%)`
        : shift >= 0
          ? `hsl(151 58% ${(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}%)`
          : `hsl(12 64% ${(58 - ((diffStrength * 10) + (shiftStrength * 6))).toFixed(1)}%)`;
    headerMarkup.push(`
      <g>
        <rect x="${(x0 + 2).toFixed(2)}" y="${headerBandY.toFixed(2)}" width="${Math.max(0, x1 - x0 - 4).toFixed(2)}" height="${headerBandHeight}" rx="6" fill="${headerFill}">
          <title>IMD decile ${decile} average ${metric.title.toLowerCase()}: ${headerLabel || 'n/a'}. Column body is showing ${formatAggregateLong(columnTotal)}.</title>
        </rect>
        ${headerLabel ? `<text x="${((x0 + x1) / 2).toFixed(2)}" y="${headerTextY.toFixed(2)}" text-anchor="middle" font-size="10.5" font-weight="700" fill="rgba(26,28,26,0.88)">${headerLabel}</text>` : ''}
      </g>
    `);
    for (let bucketIndex = 0; bucketIndex < bucketCount; bucketIndex += 1) {
      const key = `${decile}-${bucketIndex}`;
      const count = cells.get(key) || 0;
      const x = xBoundary(decile - xMin);
      const y = yBoundary(bucketIndex + 1);
      const bucketMid = bucketMidValue(bucketIndex);
      const fill = metricColorForValue(activeMetric, bucketMid);
      const opacity = count <= 0 || maxCellCount <= 0 ? 0.08 : 0.16 + (count / maxCellCount) * 0.72;
      const label = formatCellValue(count);
      const tooltipValue = activeMetric === 'survey'
        ? `${Math.round(bucketMid)}%`
        : bucketMid.toFixed(activeMetric === 'gap' ? 2 : 1);
      cellMarkup.push(`
        <g>
          <rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${cellWidth.toFixed(2)}" height="${cellHeight.toFixed(2)}" fill="${fill}" fill-opacity="${opacity.toFixed(3)}" stroke="rgba(26,28,26,0.14)" stroke-width="1">
            <title>IMD decile ${decile}, score bucket around ${tooltipValue}: ${formatAggregateLong(count)}</title>
          </rect>
          ${label ? `<text x="${(x + cellWidth / 2).toFixed(2)}" y="${(y + cellHeight / 2 + 4).toFixed(2)}" text-anchor="middle" font-size="11" font-weight="700" fill="rgba(26,28,26,0.84)">${label}</text>` : ''}
        </g>
      `);
    }
  }

  const yTicks = Array.from({ length: bucketCount + 1 }, (_, index) => yMin + bucketHeight * index);
  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${headerMarkup.join('')}
    ${Array.from({ length: xBins + 1 }, (_, idx) => idx).map((boundaryIndex) => `
      <line x1="${xBoundary(boundaryIndex)}" y1="${margin.top}" x2="${xBoundary(boundaryIndex)}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.10)" />
    `).join('')}
    ${Array.from({ length: bucketCount + 1 }, (_, idx) => idx).map((boundaryIndex) => `
      <line x1="${margin.left}" y1="${yBoundary(boundaryIndex)}" x2="${width - margin.right}" y2="${yBoundary(boundaryIndex)}" stroke="rgba(26,28,26,0.10)" />
    `).join('')}
    ${cellMarkup.join('')}
    ${yTicks.slice(0, -1).map((tick, index) => {
      const bucketMid = tick + bucketHeight / 2;
      const label = activeMetric === 'survey'
        ? `${Math.round(bucketMid)}%`
        : bucketMid.toFixed(activeMetric === 'gap' ? 2 : 1);
      return `<text x="${margin.left - 8}" y="${(yBoundary(index + 1) + cellHeight / 2 + 4).toFixed(2)}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${label}</text>`;
    }).join('')}
    ${Array.from({ length: xBins }, (_, idx) => idx + 1).map((tick) => `
      <text x="${xCenter(tick)}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${tick}</text>
    `).join('')}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">IMD 2025 decile (1 = most deprived)</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${height / 2})">${activeMetric === 'gap' ? gapAxis.label : metric.axisLabel}</text>
  `;

  const unsupportedCount = combinedRows.filter((row) => {
    const dep = allPracticeDeprivationLookup[row.code];
    return dep && dep.lookup_status === 'unsupported_nation';
  }).length;
  const polygonOnlyCount = combinedRows.filter((row) => {
    const dep = allPracticeDeprivationLookup[row.code];
    return dep && dep.lookup_status === 'matched_polygon_no_deprivation_index';
  }).length;
  const topColumn = Array.from(columnCounts.entries()).sort((left, right) => right[1] - left[1])[0];
  const totalAggregate = Array.from(cells.values()).reduce((sum, value) => sum + value, 0);
  summary.textContent =
    `${points.length} practices currently contribute to this national contrast panel. Cells are showing ${nationalDeprivationUsePopulation ? 'summed registered patients' : 'practice counts'} across a total of ${formatAggregateLong(totalAggregate)}. ${allLookupRows.length} loaded rows have some cached deprivation lookup state, and ${matchedRows.length} have numeric IMD deciles. The densest deprivation column is decile ${topColumn ? topColumn[0] : '?'} with ${topColumn ? formatAggregateLong(topColumn[1]) : '0 practices'}. ${polygonOnlyCount} rows currently only have polygon identity without a joined deprivation index, and ${unsupportedCount} are in nations not yet wired into this lookup.`;
}

function nationScatterColor(nation) {
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return '#1f5f8b';
  if (normalized === 'scotland') return '#0c8b68';
  if (normalized === 'wales') return '#b14d5c';
  if (normalized === 'northern_ireland') return '#7b5ea7';
  return '#6b7280';
}

function nationBenchmarkAccent(nation) {
  const normalized = String(nation || '').trim().toLowerCase();
  if (normalized === 'england') return '#8d3c17';
  if (normalized === 'scotland') return '#2f6fa5';
  if (normalized === 'wales') return '#3f7d4c';
  if (normalized === 'northern_ireland') return '#6b4f9d';
  return '#4b5563';
}

function renderRatingVsSurveyChart() {
  const heading = document.getElementById('rating-survey-heading');
  const summary = document.getElementById('rating-survey-summary');
  const note = document.getElementById('rating-survey-note');
  const svg = document.getElementById('rating-survey-chart');
  if (!heading || !summary || !note || !svg) return;

  heading.textContent = 'Google Rating vs Patient Survey';
  const combinedRows = rows.concat(nationalSupplementals);
  const practicePoints = combinedRows
    .map((row) => {
      const google = numericOrNull(row.google_score);
      const survey = numericOrNull(row.survey_overall_good_percent);
      if (google === null || survey === null) return null;
      return { row, x: google, y: survey };
    })
    .filter(Boolean);

  const allBenchmarkEntries = [
    ...nationOrder
      .map((nation) => {
        const subset = allKnownRows.filter((row) => String(row?.nation || '').trim().toLowerCase() === nation);
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {
          label: displayNationName(nation),
          kind: 'nation',
          x: stats.google.value,
          y: stats.survey.value,
          color: nationBenchmarkAccent(nation),
          practiceCount: stats.practiceCount,
        };
      })
      .filter(Boolean),
    ...cityCatchments
      .map((city) => {
        const subset = cityRowsByCatchment.get(city.name) || [];
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {
          label: city.name,
          kind: 'city',
          x: stats.google.value,
          y: stats.survey.value,
          color: city.accent,
          practiceCount: stats.practiceCount,
        };
      })
      .filter(Boolean),
    ...['North', 'South']
      .map((label) => {
        const subset = northSouthRows.get(label) || [];
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {
          label,
          kind: 'region',
          x: stats.google.value,
          y: stats.survey.value,
          color: label === 'North' ? '#315f8f' : '#8c5a2a',
          practiceCount: stats.practiceCount,
        };
      })
      .filter(Boolean),
    ...compositeRegionDefinitions
      .map((definition) => {
        const subset = compositeRegionRowsByLabel.get(definition.label) || [];
        if (!subset.length) return null;
        const stats = regionCardStats(subset);
        return {
          label: definition.label,
          kind: definition.kind || 'region',
          x: stats.google.value,
          y: stats.survey.value,
          color: definition.accent || '#4b5563',
          practiceCount: stats.practiceCount,
        };
      })
      .filter(Boolean),
    ...(sampleCircleCenter
      ? (() => {
          const subset = rowsWithinCircle(allKnownRows, sampleCircleCenter.lat, sampleCircleCenter.lon, sampleCircleRadiusMiles);
          if (!subset.length) return [];
          const stats = regionCardStats(subset);
          return [{
            label: `Custom sample (${sampleCircleRadiusMiles.toFixed(sampleCircleRadiusMiles % 1 === 0 ? 0 : 1)}mi)`,
            kind: 'sample',
            x: stats.google.value,
            y: stats.survey.value,
            color: '#161816',
            practiceCount: stats.practiceCount,
          }];
        })()
      : []),
  ].filter(Boolean);
  const benchmarkPoints = allBenchmarkEntries.filter((point) => point.x !== null && point.y !== null);
  const omittedBenchmarkEntries = allBenchmarkEntries.filter((point) => point.x === null || point.y === null);

  const showPractices = ratingSurveyMode === 'practices';
  const displayPoints = showPractices ? practicePoints : benchmarkPoints;

  if (!practicePoints.length && !benchmarkPoints.length) {
    svg.innerHTML = '';
    summary.textContent = 'No loaded rows currently have both a usable Google rating and a survey/equivalent overall-good score.';
    return;
  }
  if (!displayPoints.length) {
    svg.innerHTML = '';
    summary.textContent = showPractices
      ? 'No loaded practice rows currently have both a usable Google rating and a survey/equivalent overall-good score.'
      : 'No benchmark regions currently have both a usable Google rating and a survey/equivalent overall-good score.';
    return;
  }

  const width = 920;
  const height = 320;
  const margin = { top: 28, right: 18, bottom: 42, left: 52 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const googleValues = displayPoints.map((point) => point.x);
  const surveyValues = displayPoints.map((point) => point.y);
  const rawXMin = Math.min(...googleValues);
  const rawXMax = Math.max(...googleValues);
  const rawYMin = Math.min(...surveyValues);
  const rawYMax = Math.max(...surveyValues);
  const xPad = Math.max(0.1, (rawXMax - rawXMin) * 0.08);
  const yPad = Math.max(2, (rawYMax - rawYMin) * 0.08);
  const xMin = showPractices ? 0 : Math.max(0, rawXMin - xPad);
  const xMax = showPractices ? 5 : Math.min(5, rawXMax + xPad);
  const yMin = showPractices ? 0 : Math.max(0, rawYMin - yPad);
  const yMax = showPractices ? 100 : Math.min(100, rawYMax + yPad);
  const xScale = (value) => margin.left + ((value - xMin) / (xMax - xMin)) * plotWidth;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;
  const xTicks = showPractices ? [0, 1, 2, 3, 4, 5] : (() => {
    const step = (xMax - xMin) <= 1.5 ? 0.25 : (xMax - xMin) <= 3 ? 0.5 : 1;
    const ticks = [];
    for (let tick = Math.ceil(xMin / step) * step; tick <= xMax + 0.0001; tick += step) {
      ticks.push(Number(tick.toFixed(2)));
    }
    return ticks;
  })();
  const yTicks = showPractices ? [0, 20, 40, 60, 80, 100] : (() => {
    const step = (yMax - yMin) <= 20 ? 5 : (yMax - yMin) <= 50 ? 10 : 20;
    const ticks = [];
    for (let tick = Math.ceil(yMin / step) * step; tick <= yMax + 0.0001; tick += step) {
      ticks.push(Number(tick.toFixed(2)));
    }
    return ticks;
  })();
  const trend = showPractices ? quadraticRegression(displayPoints) : null;
  const trendMarkup = trend
    ? (() => {
        const steps = 48;
        const pathParts = [];
        for (let index = 0; index <= steps; index += 1) {
          const xValue = xMin + ((index / steps) * (xMax - xMin));
          const yValue = (trend.a * xValue * xValue) + (trend.b * xValue) + trend.c;
          const clampedY = Math.max(yMin, Math.min(yMax, yValue));
          const command = index === 0 ? 'M' : 'L';
          pathParts.push(`${command}${xScale(xValue).toFixed(2)} ${yScale(clampedY).toFixed(2)}`);
        }
        return `
          <path d="${pathParts.join(' ')}" fill="none" stroke="rgba(26,28,26,0.78)" stroke-width="2.6" stroke-dasharray="8 6" stroke-linecap="round" stroke-linejoin="round">
            <title>Overall fitted quadratic trend curve</title>
          </path>
        `;
      })()
    : '';
  const benchmarkLayoutPoints = benchmarkPoints
    .map((point) => ({
      ...point,
      plotX: xScale(point.x),
      plotY: yScale(point.y),
    }))
    .sort((left, right) => (left.plotX - right.plotX) || (left.plotY - right.plotY))
    .map((point, index, plotted) => {
      const stackIndex = plotted
        .slice(0, index)
        .filter((other) => Math.abs(other.plotX - point.plotX) < 44 && Math.abs(other.plotY - point.plotY) < 24)
        .length % 5;
      return {
        ...point,
        stackIndex,
      };
    });
  const pointMarkup = showPractices ? practicePoints.map((point) => {
    const nation = String(point.row.nation || '').trim().toLowerCase();
    const isHighlighted = point.row.code === NEW_BANK_CODE || point.row.gtd || point.row.management_company === BASELINE_MANAGEMENT_COMPANY;
    const radius = point.row.code === NEW_BANK_CODE ? 5.8 : isHighlighted ? 4.1 : 2.8;
    const fill = nationScatterColor(nation);
    const stroke = point.row.code === NEW_BANK_CODE ? '#7b3fb2' : isHighlighted ? '#1a1c1a' : 'rgba(26,28,26,0.14)';
    const strokeWidth = point.row.code === NEW_BANK_CODE ? 2.1 : isHighlighted ? 1.2 : 0.6;
    const opacity = isHighlighted ? 0.9 : 0.28;
    return `
      <circle cx="${xScale(point.x).toFixed(2)}" cy="${yScale(point.y).toFixed(2)}" r="${radius.toFixed(2)}" fill="${fill}" fill-opacity="${opacity.toFixed(2)}" stroke="${stroke}" stroke-width="${strokeWidth}">
        <title>${point.row.name} · ${displayNationName(point.row.nation)} · Google ${point.x.toFixed(1)} · Survey ${Math.round(point.y)}%</title>
      </circle>
    `;
  }).join('') : '';
  const benchmarkMarkup = benchmarkLayoutPoints.map((point) => {
    const size = point.kind === 'nation' ? 14 : point.kind === 'city' ? 12 : 12.5;
    const labelY = point.plotY - (size / 2) - 8 - (point.stackIndex * 12);
    return `
      <rect x="${(point.plotX - size / 2).toFixed(2)}" y="${(point.plotY - size / 2).toFixed(2)}" width="${size.toFixed(2)}" height="${size.toFixed(2)}" rx="1.4" fill="${point.color}" fill-opacity="0.96" stroke="#ffffff" stroke-width="1.6">
        <title>${escapeHtml(point.label)} benchmark · Google ${point.x.toFixed(2)} · Survey ${Math.round(point.y)}% · ${point.practiceCount.toLocaleString('en-GB')} practices</title>
      </rect>
      ${
        showPractices
          ? ''
          : `
            <line x1="${point.plotX.toFixed(2)}" y1="${(point.plotY - size / 2).toFixed(2)}" x2="${point.plotX.toFixed(2)}" y2="${(labelY + 3).toFixed(2)}" stroke="${point.color}" stroke-opacity="0.42" stroke-width="1.1"></line>
            <text x="${point.plotX.toFixed(2)}" y="${labelY.toFixed(2)}" text-anchor="middle" font-size="${point.kind === 'nation' ? '11.5' : '10.5'}" font-weight="700" fill="${point.color}" stroke="rgba(255,255,255,0.92)" stroke-width="3" paint-order="stroke fill">${escapeHtml(point.label)}</text>
          `
      }
    `;
  }).join('');

  const nationCounts = ['england', 'scotland', 'wales', 'northern_ireland']
    .map((nation) => {
      const count = practicePoints.filter((point) => String(point.row.nation || '').trim().toLowerCase() === nation).length;
      return count > 0 ? `${displayNationName(nation)} ${count.toLocaleString('en-GB')}` : '';
    })
    .filter(Boolean)
    .join(' · ');
  const rValue = correlation(displayPoints.map((point) => ({ x: point.x, y: point.y })));
  const formula = trend
    ? `survey ≈ ${trend.a >= 0 ? '' : '-'}${Math.abs(trend.a).toFixed(2)}·rating² ${trend.b >= 0 ? '+ ' : '- '}${Math.abs(trend.b).toFixed(2)}·rating ${trend.c >= 0 ? '+ ' : '- '}${Math.abs(trend.c).toFixed(2)}`
    : 'no curve fit in region mode';
  summary.textContent =
    showPractices
      ? `${practicePoints.length.toLocaleString('en-GB')} practice entries currently have both a usable Google rating and a survey/equivalent overall-good score. Pearson r is ${rValue === null ? '?' : rValue.toFixed(2)}. ${nationCounts}. ${benchmarkPoints.length} region overlays are drawn as larger squares.`
      : `${benchmarkPoints.length} benchmark regions are currently shown from ${allBenchmarkEntries.length} listed entries. Pearson r between those aggregate points is ${rValue === null ? '?' : rValue.toFixed(2)}.`;
  note.textContent = showPractices
    ? `Practice mode shows all loaded rows on the full Google 0-5 and survey 0-100 scales, with larger squares for nation, city, North/South, and custom-sample aggregates. Quadratic fit: ${formula}.`
    : `Region mode shows only the benchmark aggregates from the Nation and City panel plus North/South and any custom sample, with axes fitted around their local spread. No curve fit is drawn in this mode.${omittedBenchmarkEntries.length ? ` ${omittedBenchmarkEntries.length} listed entries are currently unplottable because one of the two scores is missing: ${omittedBenchmarkEntries.map((entry) => entry.label).join(', ')}.` : ''}`;

  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${yTicks.map((tick) => `
      <line x1="${margin.left}" y1="${yScale(tick)}" x2="${width - margin.right}" y2="${yScale(tick)}" stroke="rgba(26,28,26,0.10)" />
      <text x="${margin.left - 8}" y="${yScale(tick) + 4}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${tick}%</text>
    `).join('')}
    ${xTicks.map((tick) => `
      <line x1="${xScale(tick)}" y1="${margin.top}" x2="${xScale(tick)}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.08)" />
      <text x="${xScale(tick)}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${tick.toFixed(1)}</text>
    `).join('')}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    ${trendMarkup}
    ${pointMarkup}
    ${benchmarkMarkup}
    <text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Google rating</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${height / 2})">Patient survey overall good</text>
  `;
}

function renderPatientChangeChart() {
  const svg = document.getElementById('patient-change-chart');
  const summary = document.getElementById('patient-change-summary');
  const heading = document.getElementById('patient-change-heading');
  const footnote = document.getElementById('patient-change-footnote');
  if (!svg || !summary || !heading || !footnote) return;
  heading.textContent = `Registered Patients Over Time - Coloured by ${metricDisplayLabel(activeMetric)}`;

  const years = patientChangeAnalysis?.years || [];
  const series = (patientChangeAnalysis?.practice_series || []).filter((entry) =>
    (entry.points || []).filter((value) => value !== null && Number.isFinite(Number(value))).length >= 2
  );
  if (!years.length || !series.length) {
    svg.innerHTML = '';
    summary.textContent = 'No practices currently have enough multi-year registered patient counts to plot.';
    footnote.hidden = true;
    footnote.textContent = '';
    return;
  }

  const width = 920;
  const height = 320;
  const margin = { top: 18, right: 18, bottom: 42, left: 56 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xScale = (index) => margin.left + (years.length <= 1 ? plotWidth / 2 : (index / Math.max(1, years.length - 1)) * plotWidth);
  const xTickIndexes = years.map((_, index) => index);

  function bucketInfo(value) {
    if (value === null || !Number.isFinite(value)) return null;
    if (activeMetric === 'google') {
      const bucketValue = Math.round(value * 2) / 2;
      return { key: bucketValue.toFixed(1), label: bucketValue.toFixed(1), value: bucketValue };
    }
    if (activeMetric === 'survey') {
      const bucketValue = Math.round(value / 10) * 10;
      return { key: String(bucketValue), label: `${bucketValue}%`, value: bucketValue };
    }
    if (activeGapMode === 'normalized') {
      const bucketValue = Math.round(value);
      return { key: `${bucketValue}z`, label: `${bucketValue > 0 ? '+' : ''}${bucketValue}z`, value: bucketValue };
    }
    const bucketValue = Math.round(value * 2) / 2;
    return { key: bucketValue.toFixed(1), label: `${bucketValue > 0 ? '+' : ''}${bucketValue.toFixed(1)}`, value: bucketValue };
  }

  const bucketMap = new Map();
  series.forEach((entry) => {
    const row = rowsByCode.get(entry.code) || null;
    const currentValue = currentMetricValueForRow(row, { suppressSmall: false });
    const bucket = bucketInfo(currentValue);
    if (!bucket) return;
    if (!bucketMap.has(bucket.key)) {
      bucketMap.set(bucket.key, { ...bucket, series: [] });
    }
    bucketMap.get(bucket.key).series.push(entry);
  });

  const sortedBuckets = Array.from(bucketMap.values()).sort((left, right) => left.value - right.value);
  const overallSeriesRaw = patientChangeAnalysis?.average_series || [];
  const flattenGlobal = patientTreemapNormalizeForChange;
  const bucketLineEntries = sortedBuckets.map((bucket) => {
    const averagePointsRaw = years.map((_, index) => {
      const values = bucket.series
        .map((entry) => entry.points?.[index])
        .filter((value) => value !== null && Number.isFinite(Number(value)))
        .map(Number);
      return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
    });
    const averagePoints = averagePointsRaw.map((value, index) => {
      if (value === null || !Number.isFinite(Number(value))) return null;
      if (!flattenGlobal) return value;
      const meanValue = Number(overallSeriesRaw[index]);
      if (!Number.isFinite(meanValue) || meanValue <= 0) return null;
      return ((value / meanValue) - 1) * 100;
    });
    const representative = bucket.series
      .map((entry) => rowsByCode.get(entry.code))
      .find(Boolean);
    const color = representative ? colorForCurrentMetric(representative, { suppressSmall: false }) : '#9aa0a6';
    const lastIndex = averagePoints.reduce((acc, value, index) => (value !== null && Number.isFinite(value) ? index : acc), -1);
    const lastValue = lastIndex >= 0 ? averagePoints[lastIndex] : null;
    return {
      averagePoints,
      color,
      label: `${bucket.label} · n=${bucket.series.length}`,
      lastIndex,
      lastValue,
    };
  }).filter((entry) => entry.averagePoints.some((value) => value !== null && Number.isFinite(value)));

  const overallSeries = flattenGlobal
    ? overallSeriesRaw.map((value) => (value !== null && Number.isFinite(Number(value)) ? 0 : null))
    : overallSeriesRaw;
  const displayedValues = [
    ...overallSeries.filter((value) => value !== null && Number.isFinite(Number(value))).map(Number),
    ...bucketLineEntries.flatMap((entry) => entry.averagePoints.filter((value) => value !== null && Number.isFinite(Number(value))).map(Number)),
  ].sort((a, b) => a - b);
  let yMin = 0;
  let yMax = 1000;
  const yTicks = [];
  if (flattenGlobal) {
    const maxAbs = displayedValues.length ? Math.max(...displayedValues.map((value) => Math.abs(value))) : 10;
    const roundedAbs = Math.max(10, Math.ceil(maxAbs / 5) * 5);
    yMin = -roundedAbs;
    yMax = roundedAbs;
    const yStep = roundedAbs <= 20 ? 5 : roundedAbs <= 50 ? 10 : 20;
    for (let tick = yMin; tick <= yMax + 0.001; tick += yStep) {
      yTicks.push(Number(tick.toFixed(2)));
    }
  } else {
    const scopedMax = displayedValues.length ? displayedValues[displayedValues.length - 1] : 0;
    yMax = Math.max(1000, Math.ceil((scopedMax || 1000) / 1000) * 1000);
    const yStep = yMax <= 5000 ? 1000 : yMax <= 15000 ? 2500 : 5000;
    for (let tick = 0; tick <= yMax; tick += yStep) {
      yTicks.push(tick);
    }
  }
  const yScale = (value) => {
    const clamped = Math.min(yMax, Math.max(yMin, value));
    return margin.top + plotHeight - ((clamped - yMin) / Math.max(1, (yMax - yMin))) * plotHeight;
  };
  const bucketLines = bucketLineEntries.map((entry) => {
    const path = linePath(entry.averagePoints, xScale, yScale);
    if (!path) return '';
    return `
      <path d="${path}" fill="none" stroke="${entry.color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"></path>
      ${entry.lastValue === null ? '' : `<circle cx="${xScale(entry.lastIndex).toFixed(2)}" cy="${yScale(entry.lastValue).toFixed(2)}" r="4.2" fill="${entry.color}"></circle>
      <text x="${Math.min(width - margin.right, xScale(entry.lastIndex) + 8).toFixed(2)}" y="${(yScale(entry.lastValue) - 7).toFixed(2)}" font-size="10.5" font-weight="700" fill="${entry.color}">${entry.label}</text>`}
    `;
  }).join('');

  const overallPath = linePath(overallSeries, xScale, yScale);

  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${yTicks.map((tick) => `
      <line x1="${margin.left}" y1="${yScale(tick)}" x2="${width - margin.right}" y2="${yScale(tick)}" stroke="${flattenGlobal && tick === 0 ? 'rgba(26,28,26,0.28)' : 'rgba(26,28,26,0.10)'}" />
      <text x="${margin.left - 8}" y="${yScale(tick) + 4}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${flattenGlobal ? `${tick > 0 ? '+' : ''}${tick.toFixed(0)}%` : tick.toLocaleString('en-GB')}</text>
    `).join('')}
    ${xTickIndexes.map((index) => `
      <line x1="${xScale(index)}" y1="${margin.top}" x2="${xScale(index)}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.08)" />
      <text x="${xScale(index)}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${years[index]}</text>
    `).join('')}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    ${overallPath ? `<path d="${overallPath}" fill="none" stroke="rgba(26,28,26,0.55)" stroke-width="2.2" stroke-dasharray="6 4" stroke-linecap="round" stroke-linejoin="round"></path>` : ''}
    ${bucketLines}
    <text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Year</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${height / 2})">${flattenGlobal ? 'Variance from Manchester mean practice count (%)' : 'Registered patients'}</text>
  `;

  const newBank = series.find((entry) => entry.code === NEW_BANK_CODE);
  const newBankStart = newBank ? newBank.points.find((value) => value !== null) : null;
  const newBankEnd = newBank ? [...newBank.points].reverse().find((value) => value !== null) : null;
  const newBankSummary = !newBank || newBankStart === null || newBankEnd === null
    ? ''
    : flattenGlobal
      ? (() => {
          const startMean = Number(overallSeriesRaw[newBank.points.findIndex((value) => value !== null)]);
          const endMean = Number(overallSeriesRaw[newBank.points.length - 1 - [...newBank.points].reverse().findIndex((value) => value !== null)]);
          const startDelta = Number.isFinite(startMean) && startMean > 0 ? ((Number(newBankStart) / startMean) - 1) * 100 : null;
          const endDelta = Number.isFinite(endMean) && endMean > 0 ? ((Number(newBankEnd) / endMean) - 1) * 100 : null;
          return ` New Bank shifts from ${startDelta === null ? '?' : `${startDelta > 0 ? '+' : ''}${startDelta.toFixed(1)}%`} to ${endDelta === null ? '?' : `${endDelta > 0 ? '+' : ''}${endDelta.toFixed(1)}%`} versus the Manchester mean practice count.`;
        })()
      : ` New Bank runs from ${Number(newBankStart).toLocaleString('en-GB')} to ${Number(newBankEnd).toLocaleString('en-GB')} patients across the available series.`;
  summary.textContent =
    `${series.length} practices have multi-year patient-count histories in this chart. Coloured lines show the average trajectory for each current ${metricDisplayLabel(activeMetric).toLowerCase()} band, and the dashed grey line is the Manchester average practice count for each year.${flattenGlobal ? ' With Flatten Global on, the left y-axis shows deviation from that yearly Manchester mean, so the chart shows which score bands are gaining or losing relative share rather than absolute patient volume.' : ' The left y-axis is scoped to those displayed patient averages rather than every individual practice line.'}${newBankSummary}`;
  
    footnote.hidden = false;
    footnote.textContent = 'Patient growth footnote: both stronger and weaker score bands show only VERY slight divergence from the mean, with better-rated / better-surveyed practices gaining patients a little faster and worse-performing GPs gaining a little more slowly. That suggests patients ARE moving toward better doctors, but INCREDIBLY slowly. One possible reading is that poor access can still trap patients who need more access, convenience, or support most, while others who have a choice (and know it) are more able to switch. This is however in a context of relative to growth, where population pressure is present, but seemingly not a large driver of experience. This suggests policy drives experience more than population pressure, though further investigation might help here.';
}

function stopPatientTreemapPlayback() {
  if (patientTreemapTimer) {
    clearInterval(patientTreemapTimer);
    patientTreemapTimer = null;
  }
  patientTreemapPlaying = false;
}

function startPatientTreemapPlayback() {
  const years = patientChangeAnalysis?.years || [];
  if (years.length < 2) return;
  if (patientTreemapYearIndex === null || patientTreemapYearIndex >= years.length - 1) {
    patientTreemapYearIndex = 0;
  }
  stopPatientTreemapPlayback();
  patientTreemapPlaying = true;
  patientTreemapTimer = setInterval(() => {
    patientTreemapYearIndex = ((patientTreemapYearIndex ?? 0) + 1) % years.length;
    renderPatientTreemap();
  }, 1100);
}

function renderPatientTotalChart(years, activeYearIndex) {
  const svg = document.getElementById('patient-total-chart');
  if (!svg) return;
  if (!years.length) {
    svg.innerHTML = '';
    return;
  }
  const totals = years.map((year) => {
    const counts = patientCountsByYear?.[year] || {};
    return Object.values(counts).reduce((sum, value) => {
      const numeric = numericOrNull(value);
      return numeric !== null && numeric > 0 ? sum + numeric : sum;
    }, 0);
  });
  const usableTotals = totals.filter((value) => Number.isFinite(value) && value > 0);
  if (!usableTotals.length) {
    svg.innerHTML = '';
    return;
  }

  const width = 920;
  const height = 118;
  const margin = { top: 8, right: 12, bottom: 22, left: 54 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const reviewLineColor = '#d26a1b';
  const minTotal = Math.min(...usableTotals);
  const maxTotal = Math.max(...usableTotals);
  const paddedMin = minTotal * 0.99;
  const paddedMax = maxTotal * 1.01;
  const yRange = Math.max(1, paddedMax - paddedMin);
  const xScale = (index) => margin.left + (years.length <= 1 ? plotWidth / 2 : (index / Math.max(1, years.length - 1)) * plotWidth);
  const yScale = (value) => margin.top + plotHeight - ((value - paddedMin) / yRange) * plotHeight;
  const path = totals.map((value, index) => `${index === 0 ? 'M' : 'L'}${xScale(index).toFixed(2)} ${yScale(value).toFixed(2)}`).join(' ');
  const reviewSeriesRaw = patientChangeAnalysis?.dataset_review_average_series || [];
  const reviewCounts = patientChangeAnalysis?.dataset_review_average_practice_counts || [];
  const reviewSeries = years.map((_year, index) => {
    const value = reviewSeriesRaw[index];
    return value !== null && Number.isFinite(Number(value)) ? Number(value) : null;
  });
  const reviewYMin = 1;
  const reviewYMax = 5;
  const reviewYScale = (value) => margin.top + plotHeight - ((Math.min(reviewYMax, Math.max(reviewYMin, value)) - reviewYMin) / Math.max(1, (reviewYMax - reviewYMin))) * plotHeight;
  const reviewPath = linePath(reviewSeries, xScale, reviewYScale);
  const reviewActiveValue = reviewSeries[activeYearIndex] ?? null;
  const activeTotal = totals[activeYearIndex];
  const firstTotal = totals[0];
  const lastTotal = totals[totals.length - 1];
  const changePct = firstTotal > 0 ? ((lastTotal / firstTotal) - 1) * 100 : null;
  const labelStep = Math.max(1, Math.ceil(years.length / 6));
  const tickIndexes = years
    .map((_year, index) => index)
    .filter((index) => index % labelStep === 0 || index === years.length - 1);

  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    <rect x="${margin.left}" y="${margin.top}" width="${plotWidth}" height="${plotHeight}" fill="rgba(26,28,26,0.03)" rx="6"></rect>
    <path d="${path} L${xScale(years.length - 1).toFixed(2)} ${(margin.top + plotHeight).toFixed(2)} L${xScale(0).toFixed(2)} ${(margin.top + plotHeight).toFixed(2)} Z" fill="rgba(15,94,156,0.10)"></path>
    <path d="${path}" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"></path>
    ${reviewPath ? `<path d="${reviewPath}" fill="none" stroke="${reviewLineColor}" stroke-width="2.8" stroke-dasharray="5 4" stroke-linecap="round" stroke-linejoin="round"></path>` : ''}
    ${reviewSeries.map((value, index) => value === null ? '' : `<circle cx="${xScale(index).toFixed(2)}" cy="${reviewYScale(value).toFixed(2)}" r="2.9" fill="${reviewLineColor}" stroke="white" stroke-width="0.9"></circle>`).join('')}
    ${tickIndexes.map((index) => `
      <text x="${xScale(index).toFixed(2)}" y="${height - 6}" text-anchor="middle" font-size="10.5" fill="rgba(26,28,26,0.68)">${years[index]}</text>
    `).join('')}
    ${[1, 2, 3, 4, 5].map((tick) => `
      <text x="${margin.left - 8}" y="${reviewYScale(tick) + 4}" text-anchor="end" font-size="10" font-weight="700" fill="${reviewLineColor}">${tick.toFixed(1)}</text>
    `).join('')}
    <circle cx="${xScale(activeYearIndex).toFixed(2)}" cy="${yScale(activeTotal).toFixed(2)}" r="4.2" fill="var(--accent)" stroke="white" stroke-width="1.2"></circle>
    ${reviewActiveValue === null ? '' : `<circle cx="${xScale(activeYearIndex).toFixed(2)}" cy="${reviewYScale(reviewActiveValue).toFixed(2)}" r="3.4" fill="${reviewLineColor}" stroke="white" stroke-width="1.1"></circle>`}
    <text x="${Math.min(width - margin.right, xScale(activeYearIndex) + 8).toFixed(2)}" y="${Math.max(18, yScale(activeTotal) - 8).toFixed(2)}" font-size="11" font-weight="700" fill="var(--accent)">${years[activeYearIndex]} · ${activeTotal.toLocaleString('en-GB')}</text>
    ${reviewActiveValue === null ? '' : `<text x="${Math.min(width - margin.right - 6, xScale(activeYearIndex) + 8).toFixed(2)}" y="${Math.min(height - margin.bottom - 6, reviewYScale(reviewActiveValue) + 14).toFixed(2)}" font-size="10.5" font-weight="700" fill="${reviewLineColor}">${reviewActiveValue.toFixed(2)} ★ · n=${Number(reviewCounts[activeYearIndex] || 0)}</text>`}
    <text x="${margin.left + 6}" y="${margin.top + 14}" font-size="10.5" fill="rgba(26,28,26,0.72)">Whole dataset total: ${firstTotal.toLocaleString('en-GB')} -> ${lastTotal.toLocaleString('en-GB')} (${changePct === null ? '?' : `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%`})</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${reviewLineColor}" transform="rotate(-90 14 ${height / 2})">Average Google review score</text>
  `;
}

function renderPatientTreemap() {
  const svg = document.getElementById('patient-treemap-chart');
  const summary = document.getElementById('patient-treemap-summary');
  const heading = document.getElementById('patient-treemap-heading');
  const playButton = document.getElementById('patient-treemap-play');
  const slider = document.getElementById('patient-treemap-year');
  const yearLabel = document.getElementById('patient-treemap-year-label');
  const normalizeToggle = document.getElementById('normalize-patient-change-toggle');
  if (!svg || !summary || !heading || !playButton || !slider || !yearLabel || !normalizeToggle) return;

  const years = patientChangeAnalysis?.years || [];
  const sourceSeries = (patientChangeAnalysis?.practice_series || []).filter((entry) =>
    (entry.points || []).some((value) => value !== null && Number.isFinite(Number(value)) && Number(value) > 0)
  );
  if (!years.length || !sourceSeries.length) {
    svg.innerHTML = '';
    renderPatientTotalChart([], 0);
    summary.textContent = 'No patient-count treemap data is available.';
    playButton.textContent = 'Play';
    yearLabel.textContent = 'Year';
    return;
  }

  if (patientTreemapYearIndex === null || patientTreemapYearIndex >= years.length) {
    patientTreemapYearIndex = years.length - 1;
  }
  const latestIndex = years.length - 1;
  const yearIndex = Math.max(0, Math.min(years.length - 1, patientTreemapYearIndex));
  const year = years[yearIndex];
  slider.max = String(Math.max(0, years.length - 1));
  slider.value = String(yearIndex);
  playButton.textContent = patientTreemapPlaying ? 'Pause' : 'Play';
  playButton.setAttribute('aria-pressed', patientTreemapPlaying ? 'true' : 'false');
  yearLabel.textContent = year;
  normalizeToggle.checked = patientTreemapNormalizeForChange;
  heading.textContent = `Patient Count Treemap - Coloured by ${metricDisplayLabel(activeMetric)}`;

  const yearTotals = years.map((yearKey) => {
    const counts = patientCountsByYear?.[yearKey] || {};
    return Object.values(counts).reduce((sum, value) => {
      const numeric = numericOrNull(value);
      return numeric !== null && numeric > 0 ? sum + numeric : sum;
    }, 0);
  });
  const referenceTotal = yearTotals[latestIndex] || yearTotals[yearIndex] || 0;
  const scaledValueForYear = (rawValue, index) => {
    const absolute = Math.max(0, Number(rawValue || 0));
    if (!patientTreemapNormalizeForChange) return absolute;
    const total = yearTotals[index] || 0;
    if (!(absolute > 0) || !(total > 0) || !(referenceTotal > 0)) return 0;
    return (absolute / total) * referenceTotal;
  };

  function googleReviewBandInfo(row) {
    const google = numericOrNull(row?.google_score);
    if (google === null) return { key: 'unknown', label: 'review unknown', shortLabel: 'Ind ?' , order: 4 };
    if (google < 3) return { key: 'lt3', label: 'review <3.0', shortLabel: 'Ind <3.0', order: 0 };
    if (google < 4) return { key: '3to4', label: 'review 3.0-3.9', shortLabel: 'Ind 3-3.9', order: 1 };
    if (google < 4.5) return { key: '4to45', label: 'review 4.0-4.4', shortLabel: 'Ind 4-4.4', order: 2 };
    return { key: 'gte45', label: 'review 4.5+', shortLabel: 'Ind 4.5+', order: 3 };
  }

  const latestTotalsByNamedGroup = new Map();
  sourceSeries.forEach((entry) => {
    const row = rowsByCode.get(entry.code) || null;
    const rawGroup = entry.management_company || row?.management_company || '';
    if (!rawGroup) return;
    const latestValue = scaledValueForYear(entry.points?.[latestIndex], latestIndex);
    latestTotalsByNamedGroup.set(rawGroup, (latestTotalsByNamedGroup.get(rawGroup) || 0) + latestValue);
  });

  const sortedNamedGroups = Array.from(latestTotalsByNamedGroup.entries())
    .sort((left, right) => {
      if (left[0] === BASELINE_MANAGEMENT_COMPANY) return -1;
      if (right[0] === BASELINE_MANAGEMENT_COMPANY) return 1;
      return right[1] - left[1];
    })
    .map(([name]) => name);
  const retainedNamedGroups = new Set([
    ...sortedNamedGroups.filter((name) => name === BASELINE_MANAGEMENT_COMPANY),
    ...sortedNamedGroups.filter((name) => name !== BASELINE_MANAGEMENT_COMPANY).slice(0, 4),
  ]);

  const grouped = new Map();
  sourceSeries.forEach((entry) => {
    const row = rowsByCode.get(entry.code) || null;
    const rawGroup = entry.management_company || row?.management_company || '';
    const band = googleReviewBandInfo(row);
    const display = rawGroup && retainedNamedGroups.has(rawGroup)
      ? {
          key: `named:${rawGroup}`,
          name: rawGroup,
          shortLabel: rawGroup,
          sortBucket: rawGroup === BASELINE_MANAGEMENT_COMPANY ? 0 : 1,
          sortValue: -(latestTotalsByNamedGroup.get(rawGroup) || 0),
        }
      : {
          key: `independent:${band.key}`,
          name: `Independent / other · ${band.label}`,
          shortLabel: band.shortLabel,
          sortBucket: 2,
          sortValue: band.order,
        };
    if (!grouped.has(display.key)) {
      grouped.set(display.key, { ...display, series: [] });
    }
    grouped.get(display.key).series.push(entry);
  });

  const groups = Array.from(grouped.values())
    .map((group) => {
      const orderedSeries = [...group.series].sort((left, right) => {
        const leftLatest = scaledValueForYear(left.points?.[latestIndex], latestIndex);
        const rightLatest = scaledValueForYear(right.points?.[latestIndex], latestIndex);
        if (rightLatest !== leftLatest) return rightLatest - leftLatest;
        return String(left.name || '').localeCompare(String(right.name || ''));
      });
      const totalsByYear = years.map((_year, index) =>
        orderedSeries.reduce((sum, entry) => sum + scaledValueForYear(entry.points?.[index], index), 0)
      );
      const peakTotal = Math.max(0, ...totalsByYear);
      const currentTotal = totalsByYear[yearIndex] || 0;
      return {
        ...group,
        series: orderedSeries,
        totalsByYear,
        peakTotal,
        currentTotal,
      };
    })
    .filter((group) => group.peakTotal > 0)
    .sort((left, right) => (
      left.sortBucket - right.sortBucket ||
      left.sortValue - right.sortValue ||
      right.peakTotal - left.peakTotal ||
      left.name.localeCompare(right.name)
    ));

  if (!groups.length) {
    svg.innerHTML = '';
    renderPatientTotalChart(years, yearIndex);
    summary.textContent = `No practices have a registered-patient value for ${year}.`;
    return;
  }

  const width = 920;
  const height = 420;
  const margin = { top: 6, right: 6, bottom: 6, left: 6 };
  const groupGap = 6;
  const headerHeight = 22;
  const innerPad = 2;
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const stackHeight = plotHeight - headerHeight - innerPad;
  const totalPeakPatients = groups.reduce((sum, group) => sum + group.peakTotal, 0);
  const pixelsPerPatient = totalPeakPatients > 0
    ? ((plotWidth - (groupGap * Math.max(0, groups.length - 1))) * stackHeight) / totalPeakPatients
    : 0;
  const patientsPerPixel = pixelsPerPatient > 0 ? 1 / pixelsPerPatient : null;

  function layoutAreaRects(entries, x, y, width, height, total) {
    if (!entries.length || total <= 0 || width <= 0 || height <= 0) return [];
    if (entries.length === 1) {
      return [{ entry: entries[0], x, y, width, height }];
    }
    const horizontalSplit = width >= height;
    let splitIndex = 1;
    let firstTotal = scaledValueForYear(entries[0].points?.[yearIndex], yearIndex);
    while (splitIndex < entries.length - 1 && firstTotal < total / 2) {
      splitIndex += 1;
      firstTotal += scaledValueForYear(entries[splitIndex - 1].points?.[yearIndex], yearIndex);
    }
    const secondTotal = Math.max(0, total - firstTotal);
    const firstEntries = entries.slice(0, splitIndex);
    const secondEntries = entries.slice(splitIndex);
    if (!secondEntries.length || secondTotal <= 0) {
      return [{ entry: entries[0], x, y, width, height }];
    }
    if (horizontalSplit) {
      const firstWidth = width * (firstTotal / total);
      return [
        ...layoutAreaRects(firstEntries, x, y, firstWidth, height, firstTotal),
        ...layoutAreaRects(secondEntries, x + firstWidth, y, width - firstWidth, height, secondTotal),
      ];
    }
    const firstHeight = height * (firstTotal / total);
    return [
      ...layoutAreaRects(firstEntries, x, y, width, firstHeight, firstTotal),
      ...layoutAreaRects(secondEntries, x, y + firstHeight, width, height - firstHeight, secondTotal),
    ];
  }

  let cursorX = margin.left;
  const groupMarkup = groups.map((group) => {
    const groupWidth = group.peakTotal > 0 && pixelsPerPatient > 0
      ? (group.peakTotal * pixelsPerPatient) / stackHeight
      : 0;
    const x = cursorX;
    cursorX += groupWidth + groupGap;
    const usedHeight = group.peakTotal > 0 ? stackHeight * (group.currentTotal / group.peakTotal) : 0;
    const headerTitle = `${group.name} · ${group.currentTotal.toLocaleString('en-GB')} patients in ${year} · peak ${group.peakTotal.toLocaleString('en-GB')} across ${group.series.length} practices`;
    const headerText = groupWidth > 96
      ? `${ellipsize(group.shortLabel, Math.max(8, Math.floor((groupWidth - 18) / 7)))} · ${compactPatientCount(group.currentTotal)}`
      : '';
    let cursorY = margin.top + headerHeight + innerPad;
    const visibleSeries = group.series.filter((entry) => Number(entry.points?.[yearIndex] || 0) > 0);
    const rectFrames = group.sortBucket === 2
      ? layoutAreaRects(
          visibleSeries,
          x + innerPad,
          margin.top + headerHeight + innerPad,
          Math.max(0, groupWidth - innerPad * 2),
          Math.max(0, usedHeight),
          group.currentTotal
        )
      : visibleSeries.map((entry, index) => {
          const patientCount = scaledValueForYear(entry.points?.[yearIndex], yearIndex);
          const remainingHeight = (margin.top + headerHeight + innerPad + usedHeight) - cursorY;
          const rectHeight = index === visibleSeries.length - 1
            ? remainingHeight
            : Math.max(1.5, usedHeight * (patientCount / group.currentTotal));
          const y = cursorY;
          cursorY += rectHeight;
          return {
            entry,
            x: x + innerPad,
            y,
            width: Math.max(0, groupWidth - innerPad * 2),
            height: Math.max(0, rectHeight),
          };
        });
    const rectMarkup = rectFrames.map((frame) => {
      const entry = frame.entry;
      const row = rowsByCode.get(entry.code) || null;
      const rawPatientCount = Math.max(0, Number(entry.points?.[yearIndex] || 0));
      const patientCount = scaledValueForYear(rawPatientCount, yearIndex);
      const fill = colorForCurrentMetric(row, { suppressSmall: false });
      const metricValue = currentMetricValueForRow(row, { suppressSmall: false });
      const badge = patientTreemapNormalizeForChange
        ? `${compactMetricValue(metricValue, activeMetric)} / ${(yearTotals[yearIndex] > 0 ? ((rawPatientCount / yearTotals[yearIndex]) * 100) : 0).toFixed(1)}%`
        : `${compactMetricValue(metricValue, activeMetric)} / ${compactPatientCount(patientCount)}`;
      const rectWidth = Math.max(0, frame.width);
      const rectHeight = Math.max(0, frame.height);
      const textPad = Math.max(3, Math.min(7, Math.floor(Math.min(rectWidth, rectHeight) * 0.08)));
      const nameFontSize = Math.max(7.5, Math.min(11, Math.min(rectWidth / 10.5, rectHeight / 3.1)));
      const badgeFontSize = Math.max(6.8, Math.min(10.5, Math.min(rectWidth / 9.5, rectHeight / 3.4)));
      const textWidthChars = Math.max(5, Math.floor((rectWidth - (textPad * 2)) / Math.max(5.6, badgeFontSize * 0.58)));
      const showName = rectWidth >= 70 && rectHeight >= 24;
      const showBadge = rectWidth >= 38 && rectHeight >= 12;
      const nameText = ellipsize(entry.name || entry.code, textWidthChars);
      const strokeWidth = row?.gtd ? 1.2 : 0.8;
      const title = patientTreemapNormalizeForChange
        ? `${entry.name} · ${group.name} · ${year} patients: ${rawPatientCount.toLocaleString('en-GB')} (${yearTotals[yearIndex] > 0 ? ((rawPatientCount / yearTotals[yearIndex]) * 100).toFixed(2) : '0.00'}% of dataset, scaled to constant pool) · Current ${metricScopeLabel(activeMetric)}: ${compactMetricValue(metricValue, activeMetric)}`
        : `${entry.name} · ${group.name} · ${year} patients: ${patientCount.toLocaleString('en-GB')} · Current ${metricScopeLabel(activeMetric)}: ${compactMetricValue(metricValue, activeMetric)}`;
      const nameY = frame.y + textPad + nameFontSize;
      const badgeY = frame.y + textPad + (showName ? nameFontSize + Math.max(2, badgeFontSize * 1.15) : badgeFontSize);
      return `
        <g>
          <rect x="${frame.x.toFixed(2)}" y="${frame.y.toFixed(2)}" width="${rectWidth.toFixed(2)}" height="${Math.max(0, rectHeight - 1).toFixed(2)}" rx="2.5" fill="${fill}" stroke="rgba(26,28,26,0.28)" stroke-width="${strokeWidth}">
            <title>${title}</title>
          </rect>
          ${showName ? `<text x="${(frame.x + textPad).toFixed(2)}" y="${nameY.toFixed(2)}" font-size="${nameFontSize.toFixed(1)}" font-weight="700" fill="rgba(255,255,255,0.94)">${nameText}</text>` : ''}
          ${showBadge ? `<text x="${(frame.x + textPad).toFixed(2)}" y="${badgeY.toFixed(2)}" font-size="${badgeFontSize.toFixed(1)}" fill="rgba(255,255,255,0.94)">${ellipsize(badge, Math.max(5, textWidthChars + (showName ? 0 : 2)))}</text>` : ''}
        </g>
      `;
    }).join('');
    return `
      <g>
        <rect x="${x.toFixed(2)}" y="${margin.top.toFixed(2)}" width="${groupWidth.toFixed(2)}" height="${plotHeight.toFixed(2)}" fill="rgba(26,28,26,0.03)" rx="5"></rect>
        <rect x="${x.toFixed(2)}" y="${margin.top.toFixed(2)}" width="${groupWidth.toFixed(2)}" height="${headerHeight.toFixed(2)}" fill="rgba(26,28,26,0.08)" rx="5"></rect>
        <rect x="${(x + innerPad).toFixed(2)}" y="${(margin.top + headerHeight + innerPad).toFixed(2)}" width="${Math.max(0, groupWidth - innerPad * 2).toFixed(2)}" height="${Math.max(0, stackHeight).toFixed(2)}" fill="rgba(26,28,26,0.025)" rx="3"></rect>
        ${headerText ? `<text x="${(x + 7).toFixed(2)}" y="${(margin.top + 14).toFixed(2)}" font-size="11" font-weight="700" fill="rgba(26,28,26,0.82)">${headerText}</text>` : ''}
        <title>${headerTitle}</title>
        ${rectMarkup}
      </g>
    `;
  }).join('');

  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${groupMarkup}
  `;
  renderPatientTotalChart(years, yearIndex);

  const largestGroup = groups[0] || null;
  const visiblePracticeCount = groups.reduce((sum, group) => sum + group.series.filter((entry) => Number(entry.points?.[yearIndex] || 0) > 0).length, 0);
  const largestCurrentGroup = [...groups].sort((left, right) => right.currentTotal - left.currentTotal)[0] || null;
  const totalFirst = yearTotals[0] || 0;
  const totalLast = yearTotals[yearTotals.length - 1] || 0;
  const totalChangePct = totalFirst > 0 ? ((totalLast / totalFirst) - 1) * 100 : null;
  const referenceYear = years[latestIndex] || year;
  summary.textContent =
    `${visiblePracticeCount} practices are shown for ${year} across ${groups.length} treemap columns. Rectangle area uses a fixed scale of ${patientsPerPixel === null ? '?' : patientsPerPixel.toFixed(2)} ${patientTreemapNormalizeForChange ? 'normalised patients' : 'patients'} per pixel, so the same area basis is used across all years and groups. Named operator columns stay separate, while independent/other practices are split by Google review band. Colour shows current ${metricDisplayLabel(activeMetric).toLowerCase()}, and labels use ${patientTreemapNormalizeForChange ? 'score / dataset share' : 'score / patients'}. Largest live block this year is ${largestCurrentGroup ? `${largestCurrentGroup.name} with ${patientTreemapNormalizeForChange ? `${largestCurrentGroup.currentTotal.toFixed(0)} normalised patients` : `${largestCurrentGroup.currentTotal.toLocaleString('en-GB')} patients`}` : '?'}, while the widest reserved column is ${largestGroup ? `${largestGroup.name} at peak ${patientTreemapNormalizeForChange ? `${largestGroup.peakTotal.toFixed(0)} normalised patients` : `${largestGroup.peakTotal.toLocaleString('en-GB')}`}` : '?'}. Whole-dataset registered patients move from ${totalFirst.toLocaleString('en-GB')} to ${totalLast.toLocaleString('en-GB')} across this series (${totalChangePct === null ? '?' : `${totalChangePct >= 0 ? '+' : ''}${totalChangePct.toFixed(1)}%`}).${patientTreemapNormalizeForChange ? ` In this mode each year is rescaled to the ${referenceYear} total, so box changes reflect redistribution within the pool rather than overall pool growth.` : ''}`;
}

function formatMonthLabel(monthIso) {
  const value = new Date(`${monthIso}T00:00:00`);
  return value.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
}

function formatTakeoverDate(dateIso, precision = '') {
  if (!dateIso) return '';
  const value = new Date(`${dateIso}T00:00:00`);
  if (Number.isNaN(value.getTime())) return dateIso;
  const options = precision === 'month'
    ? { month: 'long', year: 'numeric' }
    : { day: 'numeric', month: 'long', year: 'numeric' };
  return value.toLocaleDateString('en-GB', options);
}

function linePath(points, xScale, yScale) {
  let path = '';
  points.forEach((value, index) => {
    if (value === null || !Number.isFinite(value)) return;
    const command = path ? 'L' : 'M';
    path += `${command}${xScale(index).toFixed(2)} ${yScale(value).toFixed(2)} `;
  });
  return path.trim();
}

function fractionalYearIndex(dateIso, years) {
  if (!dateIso || !years.length) return null;
  const target = new Date(`${dateIso}T00:00:00`);
  if (Number.isNaN(target.getTime())) return null;
  const targetYear = target.getUTCFullYear();
  const firstYear = parseInt(years[0], 10);
  const lastYear = parseInt(years[years.length - 1], 10);
  if (targetYear < firstYear) return -1;
  if (targetYear > lastYear) return years.length;
  const idx = years.indexOf(String(targetYear));
  return idx >= 0 ? idx : null;
}

function renderGtdSurveyTrendChart(svg, summary, legend, overlayLegend, heading, note) {
  const years = gtdSurveyTimeseries.years || [];
  const practiceSeries = gtdSurveyTimeseries.practice_series || [];
  const averageSeries = gtdSurveyTimeseries.average_series || [];
  if (heading) heading.textContent = `GTD Score Over Time - Showing ${metricDisplayLabel(activeMetric)}`;
  if (note) note.textContent = "Thin lines show each GTD practice's GP Patient Survey overall-experience-as-good percentage by year. Faint dashed vertical lines mark the documented GTD takeover date. Only the first legend entry shows the GTD mean; selecting any named practice hides it. The green dashed line shows registered patients as a percentage of the GTD-wide average patient count for that year, with raw patient counts kept in the point labels. Data from gp-patient.co.uk practice-level CSV.";
  const width = 920;
  const height = 360;
  const margin = { top: 18, right: 22, bottom: 56, left: 46 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xScale = (index) => margin.left + (years.length <= 1 ? plotWidth / 2 : (index / Math.max(1, years.length - 1)) * plotWidth);
  const yMin = 0;
  const yMax = 100;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;
  const yTicks = [0, 25, 50, 75, 100];
  const palette = [
    '#6c8ebf', '#b67b4d', '#5f9b6b', '#9d6aa8', '#b35656', '#4f8f95', '#8c7a52',
    '#9070b2', '#4f7f5b', '#bf6f91', '#7d8ab5', '#6d8f43', '#af7b52'
  ];
  const practiceEntries = practiceSeries.map((series, index) => {
    const points = series.points || [];
    const path = linePath(points, xScale, yScale);
    const lastIndex = points.reduce((memo, value, pointIndex) => (value !== null && Number.isFinite(value) ? pointIndex : memo), -1);
    const lastValue = lastIndex >= 0 ? points[lastIndex] : null;
    const rawTakeoverIndex = fractionalYearIndex(series.takeover_date, years);
    const takeoverIndex = rawTakeoverIndex === null ? null : Math.max(0, Math.min(years.length - 1, rawTakeoverIndex));
    return { series, color: palette[index % palette.length], path, lastIndex, lastValue, rawTakeoverIndex, takeoverIndex };
  }).filter((entry) => entry.path);
  const availableCodes = new Set(practiceEntries.map((e) => e.series.code));
  if (hoveredTrendPracticeCode && !validTrendCode(hoveredTrendPracticeCode, availableCodes)) hoveredTrendPracticeCode = null;
  if (pinnedTrendPracticeCode && !validTrendCode(pinnedTrendPracticeCode, availableCodes)) pinnedTrendPracticeCode = TREND_DEFAULT_CONTEXT_CODE;
  const activeCode = hoveredTrendPracticeCode || pinnedTrendPracticeCode || TREND_DEFAULT_CONTEXT_CODE;
  const isMeanContext = activeCode === TREND_DEFAULT_CONTEXT_CODE;
  const defaultEntry = defaultTrendReferenceEntry(practiceEntries);
  const displayEntry = isMeanContext
    ? defaultEntry
    : practiceEntries.find((e) => e.series.code === activeCode) || null;
  const emphasisCode = displayEntry?.series.code || null;
  const showAverage = isMeanContext;
  const dimInactive = Boolean(displayEntry);
  const patientOverlay = displayEntry
    ? years
        .map((year, index) => patientVsAveragePoint(year, displayEntry.series.code, index))
        .filter(Boolean)
    : null;
  const overlayValues = patientOverlay ? patientOverlay.map((point) => point.v) : [];
  const overlayMax = overlayAxisMax(overlayValues);
  const overlayTicks = overlayAxisTicks(overlayMax);
  const yScaleRight = patientOverlay?.length
    ? (value) => margin.top + plotHeight - (value / overlayMax) * plotHeight
    : null;
  const patientPoints = patientOverlay ? years.map((_, i) => { const p = patientOverlay.find((o) => o.i === i); return p ? p.v : null; }) : [];
  const patientPath = patientPoints.length && yScaleRight ? linePath(patientPoints, xScale, yScaleRight) : '';
  const pathOpacity = (e) => !dimInactive ? 0.46 : e.series.code === emphasisCode ? 0.96 : 0.12;
  const markerOpacity = (e) => !dimInactive ? 0.26 : e.series.code === emphasisCode ? 0.9 : 0.12;
  const strokeWidth = (e) => e.series.code === emphasisCode ? 2.8 : 1.35;
  const pointRadius = (e) => e.series.code === emphasisCode ? 4.8 : 3.1;
  const practicePaths = practiceEntries.map((entry) => {
    const finalText = entry.lastValue === null ? '?' : Math.round(entry.lastValue) + '%';
    const titleSuffix = entry.series.takeover_date ? ` Takeover: ${formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}.` : '';
    return `<path d="${entry.path}" fill="none" stroke="${entry.color}" stroke-width="${strokeWidth(entry)}" stroke-linecap="round" stroke-linejoin="round" opacity="${pathOpacity(entry).toFixed(2)}"><title>${entry.series.name} · latest ${finalText}${titleSuffix}</title></path>`;
  }).join('');
  const endMarkers = practiceEntries.filter((e) => e.lastIndex >= 0 && e.lastValue !== null).map((entry) =>
    `<circle cx="${xScale(entry.lastIndex).toFixed(2)}" cy="${yScale(entry.lastValue).toFixed(2)}" r="${pointRadius(entry).toFixed(2)}" fill="${entry.color}" opacity="${Math.max(pathOpacity(entry), 0.24).toFixed(2)}" stroke="rgba(255,255,255,0.92)" stroke-width="${entry.series.code === emphasisCode ? '1.8' : '1.1'}"><title>${entry.series.name} latest ${Math.round(entry.lastValue)}%</title></circle>`
  ).join('');
  const takeoverMarkers = practiceEntries.map((entry) => {
    if (entry.takeoverIndex === null) return '';
    const markerX = xScale(entry.takeoverIndex);
    return `<line x1="${markerX.toFixed(2)}" y1="${margin.top}" x2="${markerX.toFixed(2)}" y2="${height - margin.bottom}" stroke="${entry.color}" stroke-width="${entry.series.code === emphasisCode ? '2.2' : '1.2'}" stroke-dasharray="4 4" opacity="${markerOpacity(entry).toFixed(2)}"><title>${entry.series.name} takeover: ${formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}</title></line>`;
  }).join('');
  const averagePath = linePath(averageSeries, xScale, yScale);
  const averageFinal = [...averageSeries].reverse().find((v) => v !== null && Number.isFinite(v));
  const averageFinalIndex = averageSeries.reduce((memo, v, i) => (v !== null && Number.isFinite(v) ? i : memo), -1);
  const averageMarker = showAverage && averageFinalIndex >= 0 && averageFinal !== undefined
    ? `<circle cx="${xScale(averageFinalIndex).toFixed(2)}" cy="${yScale(averageFinal).toFixed(2)}" r="4.5" fill="${GTD_MEAN_COLOR}" opacity="${dimInactive ? '0.74' : '1'}"></circle><text x="${Math.min(width - margin.right, xScale(averageFinalIndex) + 8).toFixed(2)}" y="${(yScale(averageFinal) - 8).toFixed(2)}" font-size="11" fill="${GTD_MEAN_COLOR}" fill-opacity="${dimInactive ? '0.74' : '1'}" font-weight="700">GTD mean ${Math.round(averageFinal)}%</text>`
    : '';
  const surveyPatientOverlay = patientPath ? `
    <path d="${patientPath}" fill="none" stroke="#4c9a52" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 4" opacity="0.88"></path>
    ${patientOverlay.map((p) => `<circle cx="${xScale(p.i).toFixed(2)}" cy="${yScaleRight(p.v).toFixed(2)}" r="3.5" fill="#4c9a52" opacity="0.9"><title>Patients: ${p.raw.toLocaleString()} (${p.v.toFixed(0)}% of GTD yearly average ${Math.round(p.average).toLocaleString()})</title></circle>`).join('')}
    <line x1="${width - margin.right}" y1="${margin.top}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.25)" />
    ${overlayTicks.map((tick) => `<text x="${width - margin.right + 6}" y="${yScaleRight(tick) + 4}" text-anchor="start" font-size="10" fill="rgba(26,28,26,0.6)">${tick}%</text>`).join('')}
  ` : '';
  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${yTicks.map((tick) => `<line x1="${margin.left}" y1="${yScale(tick)}" x2="${width - margin.right}" y2="${yScale(tick)}" stroke="rgba(26,28,26,0.10)" /><text x="${margin.left - 8}" y="${yScale(tick) + 4}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${tick}%</text>`).join('')}
    ${years.map((y, i) => `<line x1="${xScale(i)}" y1="${margin.top}" x2="${xScale(i)}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.08)" /><text x="${xScale(i)}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${y}</text>`).join('')}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    ${takeoverMarkers}
    ${practicePaths}
    ${showAverage ? `<path d="${averagePath}" fill="none" stroke="${GTD_MEAN_COLOR}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity="${dimInactive ? '0.78' : '1'}"></path>` : ''}
    ${averageMarker}
    ${endMarkers}
    ${surveyPatientOverlay}
    <text x="${width / 2}" y="${height - 10}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Survey year</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${height / 2})">Overall experience good %</text>
    ${patientOverlay?.length ? `<text x="${width - 14}" y="${height / 2}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.6)" transform="rotate(90 ${width - 14} ${height / 2})">Patients vs GTD avg (%)</text>` : ''}
  `;
  const defaultLabel = defaultEntry ? `GTD mean + ${defaultEntry.series.name}` : 'GTD mean';
  legend.innerHTML = [
    `<button type="button" class="trend-legend-item${isMeanContext ? ' is-active' : ''}" data-practice-code="${TREND_DEFAULT_CONTEXT_CODE}" aria-pressed="${isMeanContext ? 'true' : 'false'}" title="${defaultLabel}"><span class="trend-legend-swatch" style="background:${GTD_MEAN_COLOR}"></span><span class="trend-legend-body"><span class="trend-legend-name">${defaultLabel}</span></span></button>`,
    ...practiceEntries.map((entry) => {
    const isActive = !isMeanContext && entry.series.code === activeCode;
    return `<button type="button" class="trend-legend-item${isActive ? ' is-active' : ''}" data-practice-code="${entry.series.code}" aria-pressed="${isActive}" title="${entry.series.name}"><span class="trend-legend-swatch" style="background:${entry.color}"></span><span class="trend-legend-body"><span class="trend-legend-name">${entry.series.name}</span></span></button>`;
  })
  ].join('');
  bindTrendLegendInteractions(legend);
  renderTrendOverlayLegend(overlayLegend, patientPath ? [
    { color: '#4c9a52', label: 'Patients vs GTD avg (%)' },
  ] : []);
  const overlaySummary = patientPath ? ' Green dashed: registered patients as a share of the GTD yearly average, with raw patient counts left in the point labels.' : '';
  const activeSummary = !displayEntry
    ? ' Hover or click a practice in the legend to isolate its track.'
    : isMeanContext
      ? ` Default view shows the GTD mean with ${displayEntry.series.name} as the reference track.${overlaySummary}`
      : ` Highlighted: ${displayEntry.series.name}. Latest ${displayEntry.lastValue === null ? '?' : Math.round(displayEntry.lastValue) + '%'}.${overlaySummary}`;
  summary.textContent = `${gtdSurveyTimeseries.practices_with_survey_history} of ${gtdSurveyTimeseries.gtd_practice_count} GTD practices, ${years.length} survey years. Thin lines are practice-level overall-good %, dashed lines mark GTD takeover.${activeSummary}`;
}

function renderGtdScoreTrendChart() {
  const svg = document.getElementById('gtd-score-trend-chart');
  const summary = document.getElementById('gtd-score-trend-summary');
  const legend = document.getElementById('gtd-score-trend-legend');
  const overlayLegend = document.getElementById('gtd-score-trend-overlay-legend');
  const heading = document.getElementById('gtd-trend-heading');
  const note = document.getElementById('gtd-trend-note');
  const useSurvey = activeMetric === 'survey' && gtdSurveyTimeseries.years?.length && gtdSurveyTimeseries.practice_series?.length;
  if (useSurvey) {
    renderGtdSurveyTrendChart(svg, summary, legend, overlayLegend, heading, note);
    return;
  }
  if (heading) heading.textContent = `GTD Score Over Time - Showing ${metricDisplayLabel(activeMetric)}`;
  if (note) note.textContent = "Thin lines show each GTD practice's reconstructed cumulative Google rating by month. Faint dashed vertical lines mark the documented GTD takeover date for each practice. Only the first legend entry shows the GTD mean; selecting any named practice hides it. The green dashed line shows registered patients as a percentage of the GTD-wide average patient count for that year, with raw patient counts kept in the point labels, and the orange dashed line shows GP Survey overall-good %. Review dates are approximate month buckets inferred from Google relative-date labels at scrape time.";
  const months = gtdGoogleTimeseries.months || [];
  const practiceSeries = gtdGoogleTimeseries.practice_series || [];
  const averageSeries = gtdGoogleTimeseries.average_series || [];
  if (!months.length || !practiceSeries.length) {
    svg.innerHTML = '';
    legend.innerHTML = '';
    renderTrendOverlayLegend(overlayLegend, []);
    summary.textContent = `No GTD Google review history is available yet in the current scrape output.`;
    return;
  }

  const width = 920;
  const height = 360;
  const margin = { top: 18, right: 22, bottom: 56, left: 46 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const xScale = (index) => margin.left + (months.length <= 1 ? plotWidth / 2 : (index / (months.length - 1)) * plotWidth);
  const yMin = 1;
  const yMax = 5;
  const yScale = (value) => margin.top + plotHeight - ((value - yMin) / (yMax - yMin)) * plotHeight;
  const yTicks = [1, 2, 3, 4, 5];
  const labelStep = Math.max(1, Math.ceil(months.length / 8));
  const xTickIndexes = months
    .map((_month, index) => index)
    .filter((index) => index % labelStep === 0 || index === months.length - 1);
  const palette = [
    '#6c8ebf', '#b67b4d', '#5f9b6b', '#9d6aa8', '#b35656', '#4f8f95', '#8c7a52',
    '#9070b2', '#4f7f5b', '#bf6f91', '#7d8ab5', '#6d8f43', '#af7b52'
  ];
  const fractionalMonthIndex = (dateIso) => {
    if (!dateIso) return null;
    const target = new Date(`${dateIso}T00:00:00`);
    const first = new Date(`${months[0]}T00:00:00`);
    if (Number.isNaN(target.getTime()) || Number.isNaN(first.getTime())) return null;
    const monthDelta = (target.getUTCFullYear() - first.getUTCFullYear()) * 12 + (target.getUTCMonth() - first.getUTCMonth());
    const daysInMonth = new Date(Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0)).getUTCDate() || 31;
    const dayFraction = Math.max(0, Math.min(0.999, ((target.getUTCDate() || 1) - 1) / daysInMonth));
    return monthDelta + dayFraction;
  };
  const practiceEntries = practiceSeries.map((series, index) => {
    const points = series.points || [];
    const lastIndex = points.reduce((memo, value, pointIndex) => (
      value !== null && Number.isFinite(value) ? pointIndex : memo
    ), -1);
    const lastValue = lastIndex >= 0 ? points[lastIndex] : null;
    const rawTakeoverIndex = fractionalMonthIndex(series.takeover_date);
    const takeoverIndex = rawTakeoverIndex === null
      ? null
      : Math.max(0, Math.min(months.length - 1, rawTakeoverIndex));
    return {
      series,
      color: palette[index % palette.length],
      path: linePath(points, xScale, yScale),
      lastIndex,
      lastValue,
      rawTakeoverIndex,
      takeoverIndex,
    };
  }).filter((entry) => entry.path);
  const availableCodes = new Set(practiceEntries.map((entry) => entry.series.code));
  if (hoveredTrendPracticeCode && !validTrendCode(hoveredTrendPracticeCode, availableCodes)) {
    hoveredTrendPracticeCode = null;
  }
  if (pinnedTrendPracticeCode && !validTrendCode(pinnedTrendPracticeCode, availableCodes)) {
    pinnedTrendPracticeCode = TREND_DEFAULT_CONTEXT_CODE;
  }
  const activeCode = hoveredTrendPracticeCode || pinnedTrendPracticeCode || TREND_DEFAULT_CONTEXT_CODE;
  const isMeanContext = activeCode === TREND_DEFAULT_CONTEXT_CODE;
  const defaultEntry = defaultTrendReferenceEntry(practiceEntries);
  const activeEntry = isMeanContext
    ? defaultEntry
    : practiceEntries.find((entry) => entry.series.code === activeCode) || null;
  const emphasisCode = activeEntry?.series.code || null;
  const showAverage = isMeanContext;
  const dimInactive = Boolean(activeEntry);

  const monthIndexForYear = (year) => {
    const prefix = `${year}-01`;
    const idx = months.findIndex((m) => String(m).startsWith(prefix));
    return idx >= 0 ? idx : null;
  };
  const buildOverlaySeries = (code) => {
    const overlay = { google: null, patient: null, survey: null };
    const surveySeries = (gtdSurveyTimeseries.practice_series || []).find((s) => s.code === code);
    const surveyYears = gtdSurveyTimeseries.years || [];
    const patientByYear = patientCountsByYear || {};
    const patientYears = Object.keys(patientByYear).filter((y) => patientByYear[y] && typeof patientByYear[y][code] === 'number').sort((a, b) => a - b);
    overlay.google = practiceSeries.find((s) => s.code === code)?.points || null;
    overlay.patient = patientYears.length
      ? patientYears
          .map((y) => {
            const i = monthIndexForYear(parseInt(y, 10));
            return i !== null ? patientVsAveragePoint(y, code, i) : null;
          })
          .filter(Boolean)
      : null;
    overlay.survey = surveySeries && surveyYears.length ? surveyYears.map((y, idx) => { const i = monthIndexForYear(parseInt(y, 10)); const v = surveySeries.points?.[idx]; return i !== null && v !== null && Number.isFinite(v) ? { i, v, raw: v } : null; }).filter(Boolean) : null;
    return overlay;
  };
  const overlay = activeEntry ? buildOverlaySeries(activeEntry.series.code) : null;
  const hasOverlay = overlay && (overlay.patient?.length || overlay.survey?.length);
  const overlayValues = hasOverlay
    ? [
        ...(overlay.patient || []).map((point) => point.v),
        ...(overlay.survey || []).map((point) => point.v),
      ]
    : [];
  const overlayMax = overlayAxisMax(overlayValues);
  const overlayTicks = overlayAxisTicks(overlayMax);
  const yScaleRight = hasOverlay ? (v) => margin.top + plotHeight - (v / overlayMax) * plotHeight : null;
  const pathOpacity = (entry) => !dimInactive ? 0.46 : entry.series.code === activeEntry?.series.code ? 0.96 : 0.12;
  const markerOpacity = (entry) => !dimInactive ? 0.26 : entry.series.code === activeEntry?.series.code ? 0.9 : 0.12;
  const strokeWidth = (entry) => entry.series.code === emphasisCode ? 2.8 : 1.35;
  const pointRadius = (entry) => entry.series.code === emphasisCode ? 4.8 : 3.1;
  const overlayPath = (points, yS) => {
    if (!points?.length || !yS) return '';
    let path = '';
    points.forEach(({ i, v }) => {
      const cmd = path ? 'L' : 'M';
      path += `${cmd}${xScale(i).toFixed(2)} ${yS(v).toFixed(2)} `;
    });
    return path.trim();
  };
  const practicePaths = practiceEntries.map((entry) => {
    const finalText = entry.lastValue === null ? '?' : entry.lastValue.toFixed(2);
    const titleSuffix = entry.series.takeover_date
      ? ` Takeover: ${formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}.`
      : '';
    return `
      <path d="${entry.path}" fill="none" stroke="${entry.color}" stroke-width="${strokeWidth(entry)}" stroke-linecap="round" stroke-linejoin="round" opacity="${pathOpacity(entry).toFixed(2)}">
        <title>${entry.series.name} · latest reconstructed average ${finalText} from ${entry.series.parsed_review_count || 0} parsed reviews.${titleSuffix}</title>
      </path>
    `;
  }).join('');
  const endMarkers = practiceEntries
    .filter((entry) => entry.lastIndex >= 0 && entry.lastValue !== null)
    .map((entry) => `
      <circle cx="${xScale(entry.lastIndex).toFixed(2)}" cy="${yScale(entry.lastValue).toFixed(2)}" r="${pointRadius(entry).toFixed(2)}" fill="${entry.color}" opacity="${Math.max(pathOpacity(entry), 0.24).toFixed(2)}" stroke="rgba(255,255,255,0.92)" stroke-width="${entry.series.code === emphasisCode ? '1.8' : '1.1'}">
        <title>${entry.series.name} latest reconstructed rating: ${entry.lastValue.toFixed(2)}</title>
      </circle>
    `).join('');
  const takeoverMarkers = practiceEntries.map((entry) => {
    if (entry.takeoverIndex === null) return '';
    const markerX = xScale(entry.takeoverIndex);
    const timingNote = entry.rawTakeoverIndex < 0
      ? 'Takeover predates the visible review timeline'
      : entry.rawTakeoverIndex > months.length - 1
        ? 'Takeover is after the visible review timeline'
        : 'Takeover within the visible review timeline';
    return `
      <line x1="${markerX.toFixed(2)}" y1="${margin.top}" x2="${markerX.toFixed(2)}" y2="${height - margin.bottom}" stroke="${entry.color}" stroke-width="${entry.series.code === emphasisCode ? '2.2' : '1.2'}" stroke-dasharray="4 4" opacity="${markerOpacity(entry).toFixed(2)}">
        <title>${entry.series.name} takeover: ${formatTakeoverDate(entry.series.takeover_date, entry.series.takeover_precision)}. ${timingNote}. ${entry.series.takeover_note || entry.series.takeover_source_label || 'Official GTD takeover source'}</title>
      </line>
    `;
  }).join('');
  const activeTakeoverMarkup = activeEntry && activeEntry.takeoverIndex !== null
    ? (() => {
        const label = `Takeover ${formatTakeoverDate(activeEntry.series.takeover_date, activeEntry.series.takeover_precision)}`;
        const markerX = xScale(activeEntry.takeoverIndex);
        const labelX = Math.max(margin.left + 78, Math.min(width - margin.right - 78, markerX));
        return `
          <rect x="${(labelX - 78).toFixed(2)}" y="${(margin.top + 6).toFixed(2)}" width="156" height="22" rx="11" fill="rgba(255,255,255,0.90)" stroke="${activeEntry.color}" stroke-opacity="0.45"></rect>
          <text x="${labelX.toFixed(2)}" y="${(margin.top + 21).toFixed(2)}" text-anchor="middle" font-size="11" font-weight="700" fill="${activeEntry.color}">${label}</text>
        `;
      })()
    : '';

  const averagePath = linePath(averageSeries, xScale, yScale);
  const averageFinal = [...averageSeries].reverse().find((value) => value !== null && Number.isFinite(value));
  const averageFinalIndex = averageSeries.reduce((lastIndex, value, index) => (value !== null && Number.isFinite(value) ? index : lastIndex), -1);
  const averageMarker = showAverage && averageFinalIndex >= 0 && averageFinal !== undefined
    ? `
      <circle cx="${xScale(averageFinalIndex).toFixed(2)}" cy="${yScale(averageFinal).toFixed(2)}" r="4.5" fill="${GTD_MEAN_COLOR}" opacity="${dimInactive ? '0.74' : '1'}"></circle>
      <text x="${Math.min(width - margin.right, xScale(averageFinalIndex) + 8).toFixed(2)}" y="${(yScale(averageFinal) - 8).toFixed(2)}" font-size="11" fill="${GTD_MEAN_COLOR}" fill-opacity="${dimInactive ? '0.74' : '1'}" font-weight="700">GTD mean ${averageFinal.toFixed(2)}</text>
    `
    : '';

  const overlayMarkup = hasOverlay && yScaleRight ? `
    ${overlay.patient?.length ? `<path d="${overlayPath(overlay.patient, yScaleRight)}" fill="none" stroke="#4c9a52" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 4" opacity="0.88"></path>${overlay.patient.map((p) => `<circle cx="${xScale(p.i).toFixed(2)}" cy="${yScaleRight(p.v).toFixed(2)}" r="3.5" fill="#4c9a52" opacity="0.9"><title>Patients: ${p.raw.toLocaleString()} (${p.v.toFixed(0)}% of GTD yearly average ${Math.round(p.average).toLocaleString()})</title></circle>`).join('')}` : ''}
    ${overlay.survey?.length ? `<path d="${overlayPath(overlay.survey, yScaleRight)}" fill="none" stroke="#b67b4d" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2 4" opacity="0.88"></path>${overlay.survey.map((p) => `<circle cx="${xScale(p.i).toFixed(2)}" cy="${yScaleRight(p.v).toFixed(2)}" r="3.5" fill="#b67b4d" opacity="0.9"><title>Survey good: ${Math.round(p.raw)}%</title></circle>`).join('')}` : ''}
    <line x1="${width - margin.right}" y1="${margin.top}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.25)" />
    ${overlayTicks.map((t) => `<text x="${width - margin.right + 6}" y="${yScaleRight(t) + 4}" text-anchor="start" font-size="10" fill="rgba(26,28,26,0.6)">${t}%</text>`).join('')}
  ` : '';
  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${yTicks.map((tick) => `
      <line x1="${margin.left}" y1="${yScale(tick)}" x2="${width - margin.right}" y2="${yScale(tick)}" stroke="rgba(26,28,26,0.10)" />
      <text x="${margin.left - 8}" y="${yScale(tick) + 4}" text-anchor="end" font-size="11" fill="rgba(26,28,26,0.72)">${tick.toFixed(1)}</text>
    `).join('')}
    ${xTickIndexes.map((index) => `
      <line x1="${xScale(index)}" y1="${margin.top}" x2="${xScale(index)}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.08)" />
      <text x="${xScale(index)}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.72)">${formatMonthLabel(months[index])}</text>
    `).join('')}
    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    <line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(26,28,26,0.35)" />
    ${takeoverMarkers}
    ${practicePaths}
    ${showAverage ? `<path d="${averagePath}" fill="none" stroke="${GTD_MEAN_COLOR}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity="${dimInactive ? '0.78' : '1'}"></path>` : ''}
    ${averageMarker}
    ${endMarkers}
    ${activeTakeoverMarkup}
    ${overlayMarkup}
    <text x="${width / 2}" y="${height - 10}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)">Approximate review month</text>
    <text x="14" y="${height / 2}" text-anchor="middle" font-size="12" fill="rgba(26,28,26,0.78)" transform="rotate(-90 14 ${height / 2})">Reconstructed cumulative Google rating</text>
    ${hasOverlay ? `<text x="${width - 14}" y="${height / 2}" text-anchor="middle" font-size="11" fill="rgba(26,28,26,0.6)" transform="rotate(90 ${width - 14} ${height / 2})">Patients vs GTD avg (%) · Survey %</text>` : ''}
  `;
  const defaultLabel = defaultEntry ? `GTD mean + ${defaultEntry.series.name}` : 'GTD mean';
  legend.innerHTML = [
    `
      <button
        type="button"
        class="trend-legend-item${isMeanContext ? ' is-active' : ''}"
        data-practice-code="${TREND_DEFAULT_CONTEXT_CODE}"
        aria-pressed="${isMeanContext ? 'true' : 'false'}"
        title="${defaultLabel}"
      >
        <span class="trend-legend-swatch" style="background:${GTD_MEAN_COLOR}"></span>
        <span class="trend-legend-body">
          <span class="trend-legend-name">${defaultLabel}</span>
        </span>
      </button>
    `,
    ...practiceEntries.map((entry) => {
    const isActive = !isMeanContext && entry.series.code === activeCode;
    return `
      <button
        type="button"
        class="trend-legend-item${isActive ? ' is-active' : ''}"
        data-practice-code="${entry.series.code}"
        aria-pressed="${isActive ? 'true' : 'false'}"
        title="${entry.series.name}"
      >
        <span class="trend-legend-swatch" style="background:${entry.color}"></span>
        <span class="trend-legend-body">
          <span class="trend-legend-name">${entry.series.name}</span>
        </span>
      </button>
    `;
  })
  ].join('');
  bindTrendLegendInteractions(legend);
  renderTrendOverlayLegend(overlayLegend, hasOverlay ? [
    ...(overlay.patient?.length ? [{ color: '#4c9a52', label: 'Patients vs GTD avg (%)' }] : []),
    ...(overlay.survey?.length ? [{ color: '#b67b4d', label: 'GP Survey good %' }] : []),
  ] : []);

  const missingPractices = (gtdGoogleTimeseries.missing_practices || []).map((item) => item.name).filter(Boolean);
  const missingSuffix = missingPractices.length
    ? ` ${missingPractices.length} GTD practice${missingPractices.length === 1 ? '' : 's'} still have no usable dated review history in the scrape: ${missingPractices.join(', ')}.`
    : '';
  const overlaySummary = hasOverlay
    ? ' Green dashed: registered patients as a share of the GTD yearly average, with raw patient counts left in the point labels. Orange dashed: GP Survey good %.'
    : '';
  const activeSummary = !activeEntry
    ? ' Hover or click a practice in the side legend to isolate its track and takeover marker.'
    : isMeanContext
      ? ` Default view shows the GTD mean with ${activeEntry.series.name} as the reference track.${overlaySummary}`
      : ` Highlighted: ${activeEntry.series.name}. Latest reconstructed score is ${activeEntry.lastValue === null ? '?' : activeEntry.lastValue.toFixed(2)}${activeEntry.series.takeover_date ? `, with GTD takeover on ${formatTakeoverDate(activeEntry.series.takeover_date, activeEntry.series.takeover_precision)}.` : '.'}${overlaySummary}`;
  summary.textContent =
    `${gtdGoogleTimeseries.practices_with_review_history} of ${gtdGoogleTimeseries.gtd_practice_count} GTD practices contribute to this chart, based on ${gtdGoogleTimeseries.parsed_review_count} parsed Google review dates and ratings. Thin lines are practice-level reconstructed cumulative averages, dashed vertical lines mark documented GTD takeover dates, and the bold line is the mean of available practice trajectories. Relative dates are anchored to the scrape file timestamp ${gtdGoogleTimeseries.anchor_date}.${activeSummary}${missingSuffix}`;
}

function rerenderAll() {
  renderMetricLegend();
  updateAreaOverlayControls();
  renderManagementList();
  clearOverlayLayers();
  renderMarkers();
  renderNationalSupplementals();
  renderCityCircles();
  renderSampleCircle();
  updateSampleCircleControls();
  if (activeAreaOverlay === 'population') {
    renderVoronoi();
  } else if (activeAreaOverlay === 'deprivation') {
    renderDeprivation();
  } else if (activeAreaOverlay === 'terrain') {
    renderHealthcareTerrain();
  }
  renderGtdScoreTrendChart();
  renderScatterplot();
  renderDeprivationChart();
  renderNationalDeprivationChart();
  renderPatientChangeChart();
  renderPatientTreemap();
  renderPlaceBenchmarks();
  renderServiceFinder();
  renderRatingVsSurveyChart();
  renderComparisons();
}

document.querySelectorAll('input[name="score-source"]').forEach((input) => {
  input.addEventListener('change', (event) => {
    activeMetric = event.target.value;
    rerenderAll();
  });
});

document.getElementById('normalize-gap-toggle').addEventListener('change', (event) => {
  activeGapMode = event.target.checked ? 'normalized' : 'absolute';
  rerenderAll();
});

document.querySelectorAll('input[name="completion-scope"]').forEach((input) => {
  input.addEventListener('click', (event) => {
    if (event.target.value !== 'national') return;
    if (completionScatterScope !== 'national') return;
    completionScatterNationIndex = (completionScatterNationIndex + 1) % completionScatterNationOrder.length;
    updateCompletionScopeControl();
    renderScatterplot();
  });
  input.addEventListener('change', (event) => {
    const previousScope = completionScatterScope;
    completionScatterScope = event.target.value;
    if (completionScatterScope === 'national') {
      if (previousScope !== 'national') completionScatterNationIndex = 0;
      updateCompletionScopeControl();
    }
    renderScatterplot();
  });
});

document.querySelectorAll('input[name="rating-survey-mode"]').forEach((input) => {
  input.addEventListener('change', (event) => {
    ratingSurveyMode = event.target.value;
    renderRatingVsSurveyChart();
  });
});

document.getElementById('voronoi-toggle').addEventListener('change', (event) => {
  activeAreaOverlay = event.target.checked ? 'population' : fallbackAreaOverlay();
  rerenderAll();
});

document.getElementById('deprivation-toggle').addEventListener('change', (event) => {
  activeAreaOverlay = event.target.checked ? 'deprivation' : fallbackAreaOverlay();
  rerenderAll();
});

TERRAIN_OVERLAY_ORDER.forEach((overlayId) => {
  const toggle = document.getElementById(TERRAIN_OVERLAY_CONTROL_IDS[overlayId]);
  if (!toggle) return;
  toggle.addEventListener('change', (event) => {
    const available = availableHealthcareTerrainOverlays().some((overlay) => String(overlay?.overlayId || overlay?.nation || '').trim().toLowerCase() === overlayId);
    if (!available) {
      event.target.checked = false;
      return;
    }
    if (event.target.checked) {
      selectedHealthcareTerrainOverlayIds.add(overlayId);
      activeAreaOverlay = 'terrain';
    } else {
      selectedHealthcareTerrainOverlayIds.delete(overlayId);
      if (activeAreaOverlay === 'terrain' && !selectedHealthcareTerrainOverlays().length) {
        activeAreaOverlay = null;
      }
    }
    rerenderAll();
  });
});

let resizeTimer = null;
window.addEventListener('resize', () => {
  if (resizeTimer) clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    updateStickyScoreControl();
    renderScatterplot();
    renderDeprivationChart();
    renderNationalDeprivationChart();
    renderPatientChangeChart();
    renderPatientTreemap();
    renderRatingVsSurveyChart();
  }, 120);
});

document.getElementById('patient-treemap-play').addEventListener('click', () => {
  if (patientTreemapPlaying) {
    stopPatientTreemapPlayback();
  } else {
    startPatientTreemapPlayback();
  }
  renderPatientTreemap();
});

document.getElementById('patient-treemap-year').addEventListener('input', (event) => {
  stopPatientTreemapPlayback();
  patientTreemapYearIndex = Number(event.target.value);
  renderPatientTreemap();
});

document.getElementById('normalize-patient-change-toggle').addEventListener('change', (event) => {
  patientTreemapNormalizeForChange = event.target.checked;
  renderPatientChangeChart();
  renderPatientTreemap();
});

document.getElementById('national-deprivation-population-toggle').addEventListener('change', (event) => {
  nationalDeprivationUsePopulation = event.target.checked;
  renderNationalDeprivationChart();
});

document.getElementById('city-circles-toggle').addEventListener('change', (event) => {
  showCityCircles = event.target.checked;
  renderCityCircles();
  updateSampleCircleControls();
});

document.getElementById('sample-circle-button').addEventListener('click', () => {
  serviceFinderArmed = false;
  serviceFinderExtraArmed = false;
  sampleCircleArmed = !sampleCircleArmed;
  renderServiceFinder();
  updateSampleCircleControls();
});

document.getElementById('clear-sample-circle-button').addEventListener('click', () => {
  sampleCircleCenter = null;
  sampleCircleArmed = false;
  renderSampleCircle();
  renderPlaceBenchmarks();
  updateSampleCircleControls();
});

document.getElementById('sample-circle-radius').addEventListener('input', (event) => {
  sampleCircleRadiusMiles = Number(event.target.value);
  renderSampleCircle();
  renderPlaceBenchmarks();
  updateSampleCircleControls();
});

function toggleServiceFinderArmed() {
  sampleCircleArmed = false;
  serviceFinderExtraArmed = false;
  serviceFinderArmed = !serviceFinderArmed;
  clearServiceFinderButtonFlash();
  updateSampleCircleControls();
  renderServiceFinder();
}

function toggleServiceFinderExtraArmed() {
  if (!serviceFinderPoint) return;
  sampleCircleArmed = false;
  serviceFinderArmed = false;
  serviceFinderExtraArmed = !serviceFinderExtraArmed;
  clearServiceFinderButtonFlash();
  updateSampleCircleControls();
  renderServiceFinder();
}

function bindServiceFinderDrag(buttonId) {
  const button = document.getElementById(buttonId);
  if (!button) return;
  //TODO: Extra button should be hidden until a home has been placed
  const isExtraButton = buttonId === 'service-finder-extra-place-button' || buttonId === 'service-finder-map-extra-button';
  button.addEventListener('dragstart', (event) => {
    event.preventDefault();
  });
  button.addEventListener('pointerdown', (event) => {
    if (isExtraButton && !serviceFinderPoint) return;
    if (event.button !== undefined && event.button !== 0) return;
    const startX = Number(event.clientX);
    const startY = Number(event.clientY);
    let dragging = false;
    const pointerId = event.pointerId;

    const cleanup = () => {
      window.removeEventListener('pointermove', handleMove, true);
      window.removeEventListener('pointerup', handleUp, true);
      window.removeEventListener('pointercancel', handleCancel, true);
      serviceFinderDragActive = false;
      removeServiceFinderDragGhost();
      renderServiceFinder();
    };

    const handleMove = (moveEvent) => {
      if (moveEvent.pointerId !== pointerId) return;
      const distance = Math.hypot(Number(moveEvent.clientX) - startX, Number(moveEvent.clientY) - startY);
      if (!dragging && distance < 8) return;
      if (!dragging) {
        dragging = true;
        sampleCircleArmed = false;
        serviceFinderArmed = !isExtraButton;
        serviceFinderExtraArmed = isExtraButton;
        clearServiceFinderButtonFlash();
        serviceFinderDragActive = true;
      }
      updateServiceFinderDragGhost(Number(moveEvent.clientX), Number(moveEvent.clientY));
      renderServiceFinder();
      moveEvent.preventDefault();
    };

    const handleUp = (upEvent) => {
      if (upEvent.pointerId !== pointerId) return;
      if (!dragging) {
        cleanup();
        if (isExtraButton) {
          toggleServiceFinderExtraArmed();
        } else {
          toggleServiceFinderArmed();
        }
        return;
      }
      const latlng = mapLatLngFromClientPoint(Number(upEvent.clientX), Number(upEvent.clientY));
      cleanup();
      if (latlng) {
        if (isExtraButton) {
          setServiceFinderExtraPoint(latlng.lat, latlng.lng, 'Extra place');
        } else {
          setServiceFinderPoint(latlng.lat, latlng.lng, 'Dropped pin');
        }
      }
    };

    const handleCancel = (cancelEvent) => {
      if (cancelEvent.pointerId !== pointerId) return;
      cleanup();
    };

    window.addEventListener('pointermove', handleMove, true);
    window.addEventListener('pointerup', handleUp, true);
    window.addEventListener('pointercancel', handleCancel, true);
  });
}

bindServiceFinderDrag('service-finder-place-button');
bindServiceFinderDrag('service-finder-map-button');
bindServiceFinderDrag('service-finder-map-extra-button');

const serviceFinderOutOfAreaMilesInput = document.getElementById('service-finder-out-of-area-miles');
const serviceFinderOutOfAreaDecreaseButton = document.getElementById('service-finder-out-of-area-decrease');
const serviceFinderOutOfAreaIncreaseButton = document.getElementById('service-finder-out-of-area-increase');
if (serviceFinderOutOfAreaMilesInput) {
  const syncServiceFinderOutOfAreaControls = (value) => {
    const normalized = normalizeServiceFinderOutOfAreaMiles(value);
    serviceFinderOutOfAreaMilesInput.value = String(normalized);
    if (serviceFinderOutOfAreaDecreaseButton) serviceFinderOutOfAreaDecreaseButton.disabled = normalized <= 0;
    if (serviceFinderOutOfAreaIncreaseButton) serviceFinderOutOfAreaIncreaseButton.disabled = normalized >= 30;
  };
  const applyServiceFinderOutOfAreaMiles = (rawValue) => {
    if (serviceFinderOutOfAreaApplyTimer) {
      window.clearTimeout(serviceFinderOutOfAreaApplyTimer);
      serviceFinderOutOfAreaApplyTimer = null;
    }
    const nextMiles = normalizeServiceFinderOutOfAreaMiles(rawValue);
    serviceFinderOutOfAreaMiles = nextMiles;
    serviceFinderShowAllOutOfArea = false;
    syncServiceFinderOutOfAreaControls(nextMiles);
    serviceFinderSearchLog('out-of-area-radius-updated', { miles: nextMiles });
    clearServiceFinderMatches();
    renderMarkers();
    renderNationalSupplementals();
    renderServiceFinderMarker();
    renderServiceFinder();
  };
  const queueServiceFinderOutOfAreaMiles = (rawValue, delay = 260) => {
    if (serviceFinderOutOfAreaApplyTimer) window.clearTimeout(serviceFinderOutOfAreaApplyTimer);
    serviceFinderOutOfAreaApplyTimer = window.setTimeout(() => {
      serviceFinderOutOfAreaApplyTimer = null;
      applyServiceFinderOutOfAreaMiles(rawValue);
    }, delay);
  };
  const stepServiceFinderOutOfAreaMiles = (delta) => {
    const currentValue = normalizeServiceFinderOutOfAreaMiles(serviceFinderOutOfAreaMilesInput.value || serviceFinderOutOfAreaMiles);
    const nextValue = Math.max(0, Math.min(30, currentValue + delta));
    syncServiceFinderOutOfAreaControls(nextValue);
    queueServiceFinderOutOfAreaMiles(nextValue, 180);
  };
  syncServiceFinderOutOfAreaControls(serviceFinderOutOfAreaMiles);
  serviceFinderOutOfAreaMilesInput.addEventListener('input', (event) => {
    queueServiceFinderOutOfAreaMiles(event.target.value);
  });
  serviceFinderOutOfAreaMilesInput.addEventListener('change', (event) => {
    applyServiceFinderOutOfAreaMiles(event.target.value);
  });
  if (serviceFinderOutOfAreaDecreaseButton) {
    serviceFinderOutOfAreaDecreaseButton.addEventListener('click', () => {
      stepServiceFinderOutOfAreaMiles(-1);
    });
  }
  if (serviceFinderOutOfAreaIncreaseButton) {
    serviceFinderOutOfAreaIncreaseButton.addEventListener('click', () => {
      stepServiceFinderOutOfAreaMiles(1);
    });
  }
}

document.querySelectorAll('[data-service-finder-sort]').forEach((button) => {
  button.addEventListener('click', () => {
    const sortKey = String(button.getAttribute('data-service-finder-sort') || '').trim();
    if (!sortKey) return;
    if (serviceFinderSortKey === sortKey) {
      serviceFinderSortDirection = serviceFinderSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      serviceFinderSortKey = sortKey;
      serviceFinderSortDirection = serviceFinderDefaultDirection(sortKey);
    }
    renderServiceFinder();
  });
});

document.getElementById('service-finder-clear-button').addEventListener('click', () => {
  clearServiceFinderPoint();
});

const serviceFinderExtraPlaceButton = document.getElementById('service-finder-extra-place-button');
if (serviceFinderExtraPlaceButton) {
  serviceFinderExtraPlaceButton.addEventListener('click', () => {
    toggleServiceFinderExtraArmed();
  });
}

document.getElementById('service-finder-locate-button').addEventListener('click', () => {
  if (!navigator.geolocation) {
    serviceFinderArmed = false;
    serviceFinderExtraArmed = false;
    serviceFinderEmptyMessage = 'Browser geolocation is not available here.';
    renderServiceFinder();
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = Number(position.coords.latitude);
      const lon = Number(position.coords.longitude);
      setServiceFinderPoint(lat, lon, 'Browser location');
      map.flyTo([lat, lon], Math.max(map.getZoom(), 12), { duration: 0.65 });
    },
    () => {
      serviceFinderArmed = false;
      serviceFinderExtraArmed = false;
      serviceFinderEmptyMessage = 'Browser geolocation was unavailable or permission was denied.';
      renderServiceFinder();
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000,
    }
  );
});

const scoreSourceControl = document.getElementById('score-source-control');
const scoreSourceSpacer = document.getElementById('score-source-control-spacer');
const legendContainer = document.querySelector('.legend');

function updateStickyScoreControl() {
  if (!scoreSourceControl || !scoreSourceSpacer) return;
  const isPrint = window.matchMedia && window.matchMedia('print').matches;
  if (isPrint) {
    scoreSourceControl.classList.remove('is-fixed');
    scoreSourceSpacer.hidden = true;
    scoreSourceSpacer.style.height = '';
    scoreSourceControl.style.removeProperty('--sticky-left');
    scoreSourceControl.style.removeProperty('--sticky-width');
    return;
  }

  const anchorRect = (scoreSourceControl.classList.contains('is-fixed') ? scoreSourceSpacer : scoreSourceControl).getBoundingClientRect();
  const rect = scoreSourceControl.getBoundingClientRect();
  const shouldFix = anchorRect.top < 0;

  if (!shouldFix) {
    scoreSourceControl.classList.remove('is-fixed');
    scoreSourceSpacer.hidden = true;
    scoreSourceSpacer.style.height = '';
    scoreSourceControl.style.removeProperty('--sticky-left');
    scoreSourceControl.style.removeProperty('--sticky-width');
    return;
  }

  const spacerHeight = scoreSourceControl.offsetHeight;
  scoreSourceSpacer.hidden = false;
  scoreSourceSpacer.style.height = `${spacerHeight}px`;
  scoreSourceControl.style.setProperty('--sticky-left', `${rect.left}px`);
  scoreSourceControl.style.setProperty('--sticky-width', `${rect.width}px`);
  scoreSourceControl.classList.add('is-fixed');
}

window.addEventListener('scroll', updateStickyScoreControl, { passive: true });
legendContainer?.addEventListener('scroll', updateStickyScoreControl, { passive: true });

document.getElementById('legend-collapse').addEventListener('click', () => {
  sidebarCollapsed = !sidebarCollapsed;
  updateSidebarState();
  updateStickyScoreControl();
  try {
    localStorage.setItem(SIDEBAR_COLLAPSE_KEY, sidebarCollapsed ? '1' : '0');
  } catch (_error) {
  }
});

map.on('moveend', () => {
  renderMarkers();
  if (shouldPreloadVisibleCatchmentBundles()) {
    ensureCatchmentBundlesForBounds(map.getBounds().pad(0.08)).then(() => {
      renderMarkers();
      renderNationalSupplementals();
      renderServiceFinderMarker();
      renderServiceFinder();
    });
  }
  renderNationalSupplementals();
  updateHoveredCatchmentOutline();
  if (activeAreaOverlay === 'population') {
    if (voronoiLayer) {
      map.removeLayer(voronoiLayer);
      voronoiLayer = null;
    }
    renderVoronoi();
  }
});

map.on('zoomend', () => {
  renderMarkers();
  renderNationalSupplementals();
  if (shouldPreloadVisibleCatchmentBundles()) {
    ensureCatchmentBundlesForBounds(map.getBounds().pad(0.08)).then(() => {
      renderMarkers();
      renderNationalSupplementals();
      renderServiceFinderMarker();
      renderServiceFinder();
    });
  }
  updateHoveredCatchmentOutline();
});

map.on('mousemove', (event) => {
  updateLowZoomMarkerInterest(event.latlng);
});

map.on('touchstart', (event) => {
  const latlng = event.latlng || event?.originalEvent?.latlng;
  if (latlng) updateLowZoomMarkerInterest(latlng);
});

map.on('touchmove', (event) => {
  const latlng = event.latlng || event?.originalEvent?.latlng;
  if (latlng) updateLowZoomMarkerInterest(latlng);
});

map.on('click', (event) => {
  updateLowZoomMarkerInterest(event.latlng);
  if (serviceFinderArmed) {
    setServiceFinderPoint(event.latlng.lat, event.latlng.lng, 'Dropped pin');
    return;
  }
  if (serviceFinderExtraArmed) {
    setServiceFinderExtraPoint(event.latlng.lat, event.latlng.lng, 'Extra place');
    return;
  }
  if (!sampleCircleArmed) return;
  sampleCircleCenter = {
    lat: Number(event.latlng.lat),
    lon: Number(event.latlng.lng),
  };
  sampleCircleArmed = false;
  renderSampleCircle();
  renderPlaceBenchmarks();
  updateSampleCircleControls();
});

try {
  sidebarCollapsed = localStorage.getItem(SIDEBAR_COLLAPSE_KEY) === '1';
} catch (_error) {
  sidebarCollapsed = false;
}
updateSidebarState();
if (document.readyState === 'complete') {
  preloadManchesterCatchments();
} else {
  window.addEventListener('load', preloadManchesterCatchments, { once: true });
}
rerenderAll();
updateStickyScoreControl();
