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

    const lines = sanitised.split('\n').map((line) => line.trim());

    const nonEmpty = () => {
      while (lines.length) {
        const line = lines.shift();
        if (line && !TRUSTPILOT_IGNORES.has(line)) return line;
      }
      return null;
    };

    const author = nonEmpty();
    if (!author) {
      logNamespace(label, 'Unable to determine author', { index: idx, raw: segment.slice(0, 120) });
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

    if (!ratingLine) {
      logNamespace(label, 'Missing rating line for review', { author, segment });
      return;
    }

    const ratingMatch = ratingLine.match(/Rated\s+([\d.]+)\s+out\s+of\s+5/i);
    const rating = ratingMatch ? Number.parseFloat(ratingMatch[1]) : null;
    if (rating == null || Number.isNaN(rating)) {
      logNamespace(label, 'Could not parse rating', { author, ratingLine });
    }

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

const bootstrap = () => {
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

  const grid = document.createElement('section');
  grid.className = 'reviews-grid';

  reviews.forEach((review) => {
    const card = renderReviewCard(review);
    grid.append(card);
  });

  target.append(grid);
};

document.addEventListener('DOMContentLoaded', bootstrap);

