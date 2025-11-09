import './style.css';
import { trustpilotReviewsText as trustpilotOneStar } from './patchs-1star-reviews.js';
import { trustpilotReviewsText as trustpilotMixed } from './patchs-2-3star-reviews.js';
import { googleReviewsText } from './PATCHS-google-reviews.js';

const APP_SELECTOR = '#app';

/**
 * Helpers
 */
const TP_SEGMENT_DELIMITER = /\n\s*Useful\s*\n/;
const TRUSTPILOT_IGNORES = new Set([
  'Share',
  'Useful',
  '•',
  'See if a website is trustworthy without leaving the page',
  '',
]);
const GOOGLE_IGNORES = new Set([
  'Like',
  'Share',
  '',
  '',
  '',
]);

const logNamespace = (source, message, payload) => {
  // eslint-disable-next-line no-console
  console.warn(`[${source}] ${message}`, payload ?? '');
};

const normaliseWhitespace = (value) =>
  value
    .replace(/\s+/g, ' ')
    .replace(/\s([?.!,;:])/g, '$1')
    .trim();

const toParagraphs = (lines) => {
  const joined = lines.join('\n').replace(/\n{3,}/g, '\n\n');
  return joined
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
};

const looksLikeTrustpilotTitle = (line) => Boolean(line && !/^Rated\s/i.test(line));

const looksLikeGoogleMeta = (line) =>
  /^Local Guide/i.test(line) ||
  /^[0-9]+\s+reviews/i.test(line) ||
  /^[0-9]+\s+photos/i.test(line) ||
  /^[A-Z][^]*\breviews\b/i.test(line) && line.includes('·') ||
  /(?:Edited\s+)?(?:[A-Z][a-z]+\s)?\d+\s+(?:day|days|week|weeks|month|months|year|years)\s+ago/i.test(line) ||
  /^(?:a|an)\s+(?:day|week|month|year)\s+ago/i.test(line) ||
  /^New$/i.test(line);

const looksLikeNewReviewer = (line) =>
  Boolean(
    line &&
      !GOOGLE_IGNORES.has(line) &&
      !/^Edited\s+/i.test(line) &&
      !/ago$/i.test(line) &&
      !/^Local Guide/i.test(line) &&
      !/^\d+\s+(?:reviews|photos)/i.test(line) &&
      !/^New$/i.test(line),
  );

/**
 * Parsing
 */
const parseTrustpilot = (raw, label) => {
  const segments = raw.split(TP_SEGMENT_DELIMITER).map((segment) => segment.trim());
  const parsed = [];

  segments.forEach((segment, idx) => {
    if (!segment) return;
    const sanitised = segment
      .replace(/\n\s*Share\s*/gi, '\n')
      .replace(/\n\s*See if a website is trustworthy without leaving the page.*$/i, '')
      .trim();

    if (!sanitised) return;
    // Skip trivial or numeric-only artifacts
    if (/^(?:share|\d+)$/.test(sanitised.toLowerCase())) return;
    if (sanitised.length < 3) return;

    const lines = sanitised.split('\n').map((line) => line.trim());

    // Pull the next meaningful line (skip ignores and digit-only fragments from "Useful" counters)
    const nextMeaningful = () => {
      while (lines.length) {
        const line = lines.shift();
        if (!line) continue;
        if (TRUSTPILOT_IGNORES.has(line)) continue;
        if (/^\d+$/.test(line)) continue;
        return line;
      }
      return null;
    };

    const author = nextMeaningful();
    if (!author || /^(?:share|\d+)$/.test(String(author).toLowerCase())) {
      // Skip noise-only segments
      return;
    }

    const meta = [];
    let ratingLine = null;
    while (lines.length) {
      const candidate = lines.shift();
      if (TRUSTPILOT_IGNORES.has(candidate)) continue;
      if (!candidate) continue;
      if (/^Rated\s+/i.test(candidate)) {
        ratingLine = candidate;
        break;
      }
      meta.push(candidate);
    }

    // ratingLine optional in messy input

    const ratingMatch = ratingLine ? ratingLine.match(/Rated\s+([\d.]+)\s+out\s+of\s+5/i) : null;
    const rating = ratingMatch ? Number.parseFloat(ratingMatch[1]) : null;
    // Do not log: rating often absent in scraped text

    let title = null;
    while (lines.length) {
      const candidate = lines.shift();
      if (!candidate || TRUSTPILOT_IGNORES.has(candidate)) continue;
      if (looksLikeTrustpilotTitle(candidate)) {
        title = candidate;
      } else {
        lines.unshift(candidate);
      }
      break;
    }

    const bodyLines = [];
    lines.forEach((line) => {
      if (TRUSTPILOT_IGNORES.has(line)) return;
      bodyLines.push(line);
    });
    const bodyParagraphs = toParagraphs(bodyLines);

    if (!bodyParagraphs.length && title) {
      bodyParagraphs.push(title);
      title = null;
    }

    parsed.push({
      source: label,
      author,
      meta,
      rating,
      title,
      body: bodyParagraphs,
    });
  });

  return parsed;
};

const parseGoogle = (raw, label) => {
  const lines = raw.split('\n').map((line) => line.trim());
  const parsed = [];
  let idx = 0;

  const getNextMeaningful = () => {
    while (idx < lines.length) {
      const line = lines[idx].trim();
      idx += 1;
      if (!line || GOOGLE_IGNORES.has(line)) continue;
      return line;
    }
    return null;
  };

  while (idx < lines.length) {
    const nameLine = getNextMeaningful();
    if (!nameLine) break;
    const author = nameLine;

    const meta = [];
    let checkpoint = idx;
    while (checkpoint < lines.length) {
      const current = lines[checkpoint];
      const trimmed = current.trim();
      if (!trimmed) {
        checkpoint += 1;
        continue;
      }
      if (GOOGLE_IGNORES.has(trimmed)) {
        checkpoint += 1;
        continue;
      }
      if (looksLikeGoogleMeta(trimmed)) {
        meta.push(trimmed);
        checkpoint += 1;
        idx = checkpoint;
        continue;
      }
      break;
    }
    idx = checkpoint;

    const bodyLines = [];
    let lookaheadIndex = idx;
    while (lookaheadIndex < lines.length) {
      const current = lines[lookaheadIndex];
      const trimmed = current.trim();
      if (GOOGLE_IGNORES.has(trimmed)) {
        lookaheadIndex += 1;
        continue;
      }
      if (!trimmed) {
        if (bodyLines.length) bodyLines.push('');
        lookaheadIndex += 1;
        continue;
      }
      const nextLine = lines[lookaheadIndex + 1]?.trim() ?? '';
      if (bodyLines.length && looksLikeNewReviewer(trimmed) && looksLikeGoogleMeta(nextLine)) {
        break;
      }
      if (!looksLikeGoogleMeta(trimmed) || bodyLines.length) {
        bodyLines.push(trimmed);
        lookaheadIndex += 1;
        continue;
      }
      break;
    }

    idx = lookaheadIndex;

    const body = toParagraphs(bodyLines);
    if (!body.length) {
      logNamespace(label, 'Review body is empty', { author, meta });
    }

    parsed.push({
      source: label,
      author,
      meta,
      rating: null,
      title: null,
      body,
    });
  }

  return parsed;
};

/**
 * Classification (theme extraction)
 */
const THEMES = [
  {
    id: 'capacity_closed',
    label: 'System closed / capacity reached / limited hours',
    patterns: [
      /full\s*capacity|reached\s*capacity|quota\s*(for|forth?)\s*day\s*is\s*full/i,
      /always full (?:up)?|always full\b/i,
      /\b(unavailable|closed)\b.*(today|now|for (?:requests|submissions|health problems))/i,
      /\b(only )?(open|available)\b.*\b(7:?30|8:?00)\b/i,
      /\btry again (tomorrow|at|later|monday)\b/i,
      /\bslots? (?:are )?(?:full|gone|unavailable)\b/i,
      /\b(always|never)\s+(available|open)\b/i,
    ],
  },
  {
    id: 'digital_only_access',
    label: 'Digital-only access / cannot book by phone/in-person',
    patterns: [
      /digital[- ]first|digital[- ]only|online[- ]only/i,
      /(?:must|have to|made me|forced to)\s+(?:use|go|book|register)\s+(?:on|via)\s+(?:patchs|online|website|app)/i,
      /surgery (?:wouldn'?t|won'?t|doesn'?t)\s+(?:book|take)\s+(?:by )?(?:phone|telephone|walk[- ]?in|in person)/i,
      /no (?:in[- ]person|face[- ]to[- ]face) (?:appointments?|booking)/i,
      /\bforced to create an account\b/i,
      /cannot (?:email|ring|phone|call) (?:the )?surgery/i,
      /gp (?:insists|forces) (?:on )?patchs/i,
      /reception (?:just|only) (?:says|tells) (?:use|go) (?:to )?patchs/i,
      /use the link.*patchs/i,
      /\bonline form (?:only|required)/i,
    ],
  },
  {
    id: 'phone_access',
    label: 'Phone access difficult / long waits / IVR',
    patterns: [
      /phone (queue|system) (is )?(full|busy|a joke)/i,
      /wait(ed)? (on|on the) line (for|over) \d+ (minutes|hrs?)/i,
      /automated (ivr|phone) (loop|menu|system)/i,
      /cut (off|out)|kept getting cut off/i,
      /press (?:\d|one|two|three) (?:for|to)/i,
    ],
  },
  {
    id: 'timeout_long_form',
    label: 'Long forms / timeouts / session expired',
    patterns: [
      /time(d)?\s*out|session timed out|been online for 30 minutes/i,
      /too many questions|endless (questions|forms)|long[- ]winded/i,
      /lost all.*(entered|writing|typing|information)/i,
      /verify (you'?re|you are) not a bot.*again/i,
      /\bminimum of 5 characters\b/i,
    ],
  },
  {
    id: 'login_account',
    label: 'Login/account issues (NHS login, linking, registration)',
    patterns: [
      /password (not|no longer) (works|recognised)/i,
      /(can'?t|cannot) log ?in/i,
      /merged patients cannot log/i,
      /not registered with my doctor/i,
      /NHS (?:app|login).*(loop|doesn'?t work|not working)/i,
      /remember this number.*never does/i,
      /\bsecurity code\b.*(not|never) received/i,
      /geo-?block|outside the uk/i,
    ],
  },
  {
    id: 'usability_ui',
    label: 'Poor UI/UX / confusing navigation / bad design',
    patterns: [
      /\bpatchs\b/i,
      /user interface (?:is )?(?:terrible|awful|bad)/i,
      /unintuitive|not user[- ]?friendly|badly (designed|written)/i,
      /go(es)? round in circles|circular|maze/i,
      /hard(er)? to (use|navigate|set ?up)|complicated|confusing|messy/i,
      /(not|no) (?:clear|obvious) (?:how|where|what)/i,
      /1990 style|student project/i,
    ],
  },
  {
    id: 'crash_bug_attachment',
    label: 'Crashes / bugs / attachments fail',
    patterns: [
      /crash(es|ed)|freez(es|e[ds])/i,
      /attachment(s)? (?:not )?supported|problem uploading|jpg|pdf|undefined files are not supported/i,
      /system (?:is )?down|not working/i,
      /disappear(ed|s) (?:and|then) never creates a message/i,
    ],
  },
  {
    id: 'only_open_short_window',
    label: 'Short submission windows / 1–2 minute rush',
    patterns: [
      /only (open|available) (?:for )?\d+ (minutes?|mins?)/i,
      /open between 7:?30 and 7:?3[12]/i,
      /by 8:?0?\d (am)? there'?s (?:nothing|no appointments?)/i,
      /\b1-?2 minutes?\b|\bfirst minute\b/i,
      /we have now reached full capacity/i,
      /Group Practice is currently unavailable for .* on PATCHS/i,
      /will next be available (?:today at|tomorrow at|\d{1,2}:\d{2})/i,
      /out of hours|not 24\/?7|cannot submit (?:out of|outside) hours/i,
    ],
  },
  {
    id: 'response_delay_no_reply',
    label: 'No response / slow response / requests closed',
    patterns: [
      /no (reply|response)/i,
      /still (?:haven'?t|have not) heard/i,
      /request (?:has )?been closed/i,
      /disappeared from (?:my )?messages|vanish(?:ed)? into cyberspace/i,
      /cannot reply to.*thread|no option to respond/i,
      /marked (?:as )?complete.*but/i,
      /surgery (?:just )?ignores (?:them|me|it)|ignore[sd] (?:by )?the surgery/i,
      /(?:two|2)\s*hours later.*need more info.*no one replied/i,
    ],
  },
  {
    id: 'mis_triage',
    label: 'Mis-triage (sent to wrong service / unsafe triage)',
    patterns: [
      /mis-?triage|triage.*(wrong|unsafe)/i,
      /misclassified|classified.*incorrect/i,
      /told.*\b(dentist|pharmacy|chemist|a\s*&\s*e|a\s*e|walk-?in)\b.*(when|but).*(?:not|no)/i,
      /\bsend(ing)? me to (?:pharmacy|A&E|the dentist|walk-?in)\b/i,
      /referred to (?:pharmacy|dentist) incorrectly/i,
    ],
  },
  {
    id: 'ai_automation_concern',
    label: 'AI/bot/automation concerns',
    patterns: [
      /\bAI\b|artificial intelligence|machine learning/i,
      /\b(bot|chat)\b.*(?:useless|wrong|nightmare|barrier)/i,
      /automated triage|automation|algorithm/i,
      /pretend(s)? to be human|as dumb as a rock/i,
      /chat box layout/i,
    ],
  },
  {
    id: 'accessibility_exclusion',
    label: 'Accessibility / elderly / digital exclusion',
    patterns: [
      /\b(elderly|older|over 7[05])\b/i,
      /not (?:tech|app|it) literate|not tech savvy|don'?t have (?:smart)?phone/i,
      /assumes (?:I|you) have (?:a )?smart phone|mandatory mobile/i,
      /poor mobile reception|no mobile (?:signal|reception)/i,
      /parkinson'?s|carer|power of attorney|dementia/i,
    ],
  },
  {
    id: 'callback_scheduling',
    label: 'Unscheduled callbacks / missed-call penalties',
    patterns: [
      /(unscheduled|no time).*(call|callback)/i,
      /only call once|miss(ed)? the call/i,
      /have to re[- ]?submit.*next day/i,
      /\bno (?:time )?slot\b|\bno slot given\b/i,
    ],
  },
  {
    id: 'repeat_prescription',
    label: 'Repeat prescriptions / medication ordering issues',
    patterns: [
      /repeat (?:prescriptions?|medication)/i,
      /order (?:script|prescription) (?:refused|rejected|late)/i,
      /antipsychotic|alzheimer/i,
      /deliver(?:y)? of medication|collection.*pharmacy/i,
    ],
  },
  {
    id: 'rude_staff',
    label: 'Rude/unhelpful reception or admin',
    patterns: [
      /rude (?:staff|reception)/i,
      /unhelpful (?:staff|reception)/i,
      /dismissive|arrogant|don'?t care/i,
      /couldn'?t care less|overbearing/i,
    ],
  },
  {
    id: 'privacy_gdpr',
    label: 'Privacy / data handling / GDPR concerns',
    patterns: [
      /gdpr|data (?:farming|privacy)/i,
      /shared my (?:details|records) without consent/i,
      /opt(?:-| )?out.*impossible|spam text messages/i,
      /\bSAR\b|subject access request/i,
    ],
  },
  {
    id: 'generic_access_difficulty',
    label: 'General difficulty accessing care / impossible to get appointment',
    patterns: [
      /impossible to get (?:an )?appointment/i,
      /hard(er)? to get (?:an )?appointment/i,
      /worst (?:gp|system) (?:ever|in (?:manchester|the country))/i,
      /not fit for purpose|absolute (?:garbage|rubbish)/i,
      /waste of (?:time|money|taxpayers' money)/i,
      /barrier (?:between|to) (?:patients?|healthcare)/i,
      /keep patients from (?:their )?gps?/i,
    ],
  },
];

// Higher-level groups for report sections
const THEME_GROUPS = [
  {
    id: 'access_capacity',
    title: 'Access & Capacity',
    includes: [
      'digital_only_access',
      'capacity_closed',
      'only_open_short_window',
      'phone_access',
      'callback_scheduling',
      'generic_access_difficulty',
    ],
  },
  {
    id: 'platform_ux',
    title: 'Platform & UX',
    includes: [
      'usability_ui',
      'timeout_long_form',
      'crash_bug_attachment',
      'login_account',
    ],
  },
  {
    id: 'process_comms',
    title: 'Process & Communication',
    includes: ['response_delay_no_reply'],
  },
  {
    id: 'clinical_safety',
    title: 'Clinical Safety',
    includes: ['mis_triage'],
  },
  {
    id: 'automation',
    title: 'AI & Automation',
    includes: ['ai_automation_concern'],
  },
  {
    id: 'equity_inclusion',
    title: 'Equity & Inclusion',
    includes: ['accessibility_exclusion'],
  },
  {
    id: 'meds',
    title: 'Medication & Prescriptions',
    includes: ['repeat_prescription'],
  },
  {
    id: 'staff_conduct',
    title: 'Staff Conduct',
    includes: ['rude_staff'],
  },
  {
    id: 'data_privacy',
    title: 'Data & Privacy',
    includes: ['privacy_gdpr'],
  },
];

const classifyText = (text) => {
  const found = new Set();
  THEMES.forEach((theme) => {
    if (theme.patterns.some((re) => re.test(text))) {
      found.add(theme.id);
    }
  });
  return found;
};

const summariseThemes = (reviews) => {
  const counts = new Map(THEMES.map((t) => [t.id, 0]));
  const perReview = [];
  let unallocated = 0;
  reviews.forEach((r) => {
    const hay = [r.title || '', ...(r.body || []), ...(r.meta || [])]
      .join('\n')
      .toLowerCase();
    let matched = classifyText(hay);

    // Fallback assignment to reduce unallocated (and log)
    if (matched.size === 0) {
      const fallback = [];
      if (/\bpatchs\b|website|site|app\b/.test(hay)) {
        fallback.push('usability_ui');
      }
      if (/\bphone|ring|queue|call\b/.test(hay)) {
        fallback.push('phone_access');
      }
      if (/\bappointment|contact|speak|see (?:a )?doctor|get through\b/.test(hay)) {
        fallback.push('generic_access_difficulty');
      }
      if (fallback.length) {
        // eslint-disable-next-line no-console
        console.info('Fallback-categorised', {
          source: r.source,
          author: r.author,
          assigned: fallback,
          snippet: hay.slice(0, 240),
        });
        fallback.forEach((id) => matched.add(id));
      } else {
        unallocated += 1;
        // eslint-disable-next-line no-console
        console.warn('Unallocated review', {
          source: r.source,
          author: r.author,
          snippet: hay.slice(0, 500),
        });
      }
    }

    matched.forEach((id) => counts.set(id, (counts.get(id) || 0) + 1));
    perReview.push({ review: r, matched: Array.from(matched) });
  });
  const results = THEMES.map((t) => ({
    id: t.id,
    label: t.label,
    count: counts.get(t.id) || 0,
  }))
    .filter((x) => x.count > 0)
    .sort((a, b) => b.count - a.count);
  // Grouping
  const grouped = THEME_GROUPS.map((g) => {
    const items = results
      .filter((r) => g.includes.includes(r.id))
      .sort((a, b) => b.count - a.count);
    const total = items.reduce((acc, it) => acc + it.count, 0);
    return { id: g.id, title: g.title, total, items };
  }).filter((g) => g.total > 0);
  return { results, grouped, unallocated, total: reviews.length, perReview };
};

/**
 * Rendering
 */
const renderReviewCard = (review) => {
  const card = document.createElement('article');
  card.className = 'review-card';
  if (review.rating != null) {
    card.dataset.rating = review.rating.toString();
  }
  card.dataset.source = review.source;

  const header = document.createElement('header');
  header.className = 'review-card__header';

  const author = document.createElement('div');
  author.className = 'review-card__author';
  author.textContent = review.author;

  const source = document.createElement('span');
  source.className = 'review-card__source';
  source.textContent = review.source;

  header.append(author, source);

  const meta = document.createElement('div');
  meta.className = 'review-card__meta';
  if (review.rating != null && Number.isFinite(review.rating)) {
    const rounded = Math.round(review.rating * 10) / 10;
    const starsFloor = Math.max(1, Math.min(5, Math.round(rounded)));
    const stars = `${'★'.repeat(starsFloor)}${'☆'.repeat(5 - starsFloor)}`;
    meta.innerHTML = `<span class="review-card__rating" title="Rated ${rounded} out of 5">${stars}<span class="sr-only">Rated ${rounded} out of 5</span></span>`;
  }
  if (review.meta.length) {
    const metaText = document.createElement('span');
    metaText.className = 'review-card__meta-text';
    metaText.textContent = review.meta.join(' • ');
    meta.append(metaText);
  }

  const content = document.createElement('div');
  content.className = 'review-card__content';

  if (review.title) {
    const title = document.createElement('h3');
    title.className = 'review-card__title';
    title.textContent = review.title;
    content.append(title);
  }

  if (review.body.length) {
    review.body.forEach((paragraph) => {
      const p = document.createElement('p');
      p.textContent = paragraph;
      content.append(p);
    });
  }

  card.append(header);
  if (meta.childNodes.length) card.append(meta);
  card.append(content);

  return card;
};

const renderSummaryCard = (summary) => {
  const card = document.createElement('section');
  card.className = 'review-card summary-card';

  const header = document.createElement('header');
  header.className = 'review-card__header';

  const h = document.createElement('h2');
  h.className = 'review-card__title';
  h.textContent = 'Detected Issues Summary';

  const meta = document.createElement('div');
  meta.className = 'review-card__meta';
  const totals = document.createElement('span');
  totals.className = 'review-card__meta-text';
  totals.textContent = `Total reviews: ${summary.total} • Unallocated: ${summary.unallocated}`;
  meta.append(totals);

  const content = document.createElement('div');
  content.className = 'review-card__content';

  const grid = document.createElement('div');
  grid.className = 'summary-grid';

  if (summary.grouped.length) {
    summary.grouped.forEach((group) => {
      const box = document.createElement('div');
      box.className = 'summary-box';
      const boxTitle = document.createElement('h3');
      boxTitle.textContent = `${group.title} — ${group.total}`;
      const list = document.createElement('div');
      list.className = 'summary-rows';
      group.items.forEach((r) => {
        const row = document.createElement('div');
        row.className = 'summary-row';
        const name = document.createElement('span');
        name.className = 'summary-name';
        name.textContent = r.label;
        const count = document.createElement('span');
        count.className = 'summary-count';
        count.textContent = r.count.toString();
        row.append(name, count);
        list.append(row);
      });
      box.append(boxTitle, list);
      grid.append(box);
    });
  } else {
    const p = document.createElement('p');
    p.textContent = 'No themes detected.';
    grid.append(p);
  }

  const totalsBox = document.createElement('div');
  totalsBox.className = 'summary-box';
  const tTitle = document.createElement('h3');
  tTitle.textContent = 'Totals';
  const tList = document.createElement('ul');
  tList.className = 'summary-list';
  const li1 = document.createElement('li');
  li1.textContent = `Total reviews: ${summary.total}`;
  const li2 = document.createElement('li');
  li2.textContent = `Unallocated (no theme matched): ${summary.unallocated}`;
  tList.append(li1, li2);
  totalsBox.append(tTitle, tList);
  grid.append(totalsBox);

  const foot = document.createElement('p');
  foot.className = 'summary-note';
  foot.textContent =
    'Non-LLM, rules-based classification using keyword/phrase detection; reviews may match multiple themes.';

  content.append(grid);
  card.append(header, h, meta, content, foot);
  return card;
};

const bootstrap = async () => {
  const target = document.querySelector(APP_SELECTOR);
  if (!target) {
    // eslint-disable-next-line no-console
    console.error(`Unable to find mount point "${APP_SELECTOR}".`);
    return;
  }

  target.innerHTML = '';

  const heading = document.createElement('h1');
  heading.textContent = 'PATCHS Reviews Browser - New Bank PPG 12 Nov 2025';
  heading.className = 'page-title';
  target.append(heading);

  const reviews = [
    ...parseTrustpilot(trustpilotOneStar, 'Trustpilot (1★)'),
    ...parseTrustpilot(trustpilotMixed, 'Trustpilot (2-3★)'),
    ...parseGoogle(googleReviewsText, 'Google Reviews'),
  ];

  // eslint-disable-next-line no-console
  console.info('Loaded reviews', {
    total: reviews.length,
    bySource: reviews.reduce((acc, review) => {
      acc[review.source] = (acc[review.source] ?? 0) + 1;
      return acc;
    }, {}),
  });

  // Theme summary (rules-based NLP-lite)
  const summary = summariseThemes(reviews);
  // eslint-disable-next-line no-console
  console.info('Theme summary', summary);

  const grid = document.createElement('section');
  grid.className = 'reviews-grid';

  // Summary card first, spanning all columns
  const summaryCard = renderSummaryCard(summary);
  grid.append(summaryCard);

  reviews.forEach((review) => {
    const card = renderReviewCard(review);
    grid.append(card);
  });

  target.append(grid);
};

document.addEventListener('DOMContentLoaded', () => {
  bootstrap().catch((err) => {
    // eslint-disable-next-line no-console
    console.error('Bootstrap failed', err);
  });
});

