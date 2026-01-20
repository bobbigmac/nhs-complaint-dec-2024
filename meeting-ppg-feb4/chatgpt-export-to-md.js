#!/usr/bin/env node

/*
  Scans the repository for ChatGPT/OpenAI conversation export JSON files,
  pretty-prints them to .indented.json, and renders a .sourced.md that mirrors
  the default export markdown style but adds inline source links (if present in
  the message metadata).
*/

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

/**
 * Determine whether a parsed JSON value looks like a ChatGPT conversation export.
 * Supports both array-wrapped exports and single-object exports.
 */
function isChatGPTExportJson(parsed) {
  try {
    const convo = Array.isArray(parsed) ? parsed[0] : parsed;
    if (!convo || typeof convo !== 'object') return false;

    // Heuristics: ChatGPT exports include a mapping of nodes with messages
    // whose author has a role (user/assistant/system), and often include title/create_time.
    if (!convo.mapping || typeof convo.mapping !== 'object') return false;

    const mappingValues = Object.values(convo.mapping);
    if (mappingValues.length === 0) return false;

    // Find at least one node with a message including an author role
    const hasMessageWithRole = mappingValues.some((node) => {
      if (!node || typeof node !== 'object') return false;
      const msg = node.message;
      return (
        msg &&
        typeof msg === 'object' &&
        msg.author &&
        typeof msg.author === 'object' &&
        typeof msg.author.role === 'string'
      );
    });

    return hasMessageWithRole;
  } catch {
    return false;
  }
}

/**
 * Extract visible, user/assistant messages in chronological order.
 */
function extractOrderedMessages(convo) {
  const nodes = Object.values(convo.mapping || {});

  // Filter only visible messages that have textual content and known roles
  const messages = nodes
    .map((node) => node && node.message)
    .filter(Boolean)
    .filter((msg) => {
      // Skip system/hidden messages
      const isHidden = msg.metadata && msg.metadata.is_visually_hidden_from_conversation === true;
      if (isHidden) return false;
      if (!msg.author || typeof msg.author.role !== 'string') return false;
      const role = msg.author.role;
      if (role !== 'user' && role !== 'assistant') return false;
      // Prefer textual content
      if (!msg.content || typeof msg.content !== 'object') return false;
      const ct = msg.content.content_type;
      if (ct && ct !== 'text') return false;
      const parts = Array.isArray(msg.content.parts) ? msg.content.parts : [];
      if (parts.length === 0) return false;
      return true;
    })
    .map((msg) => ({
      role: msg.author.role,
      createTime: msg.create_time || 0,
      text: (Array.isArray(msg.content.parts) ? msg.content.parts : []).join('\n\n'),
      metadata: msg.metadata || {},
    }))
    .sort((a, b) => (a.createTime || 0) - (b.createTime || 0));

  return messages;
}

/**
 * Collect references (links) from a message metadata payload.
 * We walk known fields and also do a shallow scan for any object with a string 'url'.
 */
function collectReferencesFromMetadata(metadata) {
  if (!metadata || typeof metadata !== 'object') return [];

  const references = [];
  const idToRef = new Map();

  // Helper to add a ref if it has a usable URL
  const addRef = (obj) => {
    if (!obj || typeof obj !== 'object') return;
    const url = obj.url || obj.link || obj.source_url || obj.href;
    if (typeof url === 'string' && /^https?:\/\//i.test(url)) {
      const title = obj.title || obj.name || obj.text || url;
      const normalizedUrl = normalizeUrlForDedupe(url);
      const ref = { title: String(title).trim() || normalizedUrl, url: normalizedUrl };
      if (typeof obj.id === 'string') {
        idToRef.set(obj.id, ref);
      }
      references.push(ref);
    }
  };

  // Deep scan any nested objects/arrays to find url-bearing refs
  const visited = new Set();
  const stack = [metadata];
  while (stack.length) {
    const node = stack.pop();
    if (!node || typeof node !== 'object') continue;
    if (visited.has(node)) continue;
    visited.add(node);
    // If this node looks like a reference (has url), capture it
    if (typeof node.url === 'string' && /^https?:\/\//i.test(node.url)) {
      addRef(node);
    }
    // Recurse into arrays/objects
    if (Array.isArray(node)) {
      for (const item of node) stack.push(item);
    } else {
      for (const k of Object.keys(node)) {
        const val = node[k];
        if (val && typeof val === 'object') stack.push(val);
      }
    }
  }

  // Dedupe by URL
  const seen = new Set();
  const deduped = [];
  for (const ref of references) {
    const key = normalizeUrlForDedupe(ref.url);
    if (!seen.has(key)) {
      seen.add(key);
      deduped.push(ref);
    }
  }

  // Attach idToRef on the array for later lookup
  deduped.idToRef = idToRef;
  return deduped;
}

/**
 * Render a markdown document similar to ChatGPT markdown export, with inline sources.
 */
function renderMarkdown(convo, orderedMessages) {
  const lines = [];
  const title = typeof convo.title === 'string' && convo.title.trim().length > 0 ? convo.title.trim() : 'Conversation';
  lines.push(`# ${title}`);
  lines.push('');

  // We group consecutive messages by role with headers like in the default export
  let lastSourcesSignature = null;
  for (const msg of orderedMessages) {
    if (msg.role === 'user') {
      lines.push('#### You:');
    } else if (msg.role === 'assistant') {
      lines.push('#### ChatGPT:');
    } else {
      continue;
    }
    const { text: transformed, usedByUrl } = transformInlineCitations(msg.text, msg.metadata);
    lines.push(transformed);

    const refs = collectReferencesFromMetadata(msg.metadata);
    // Exclude inlined
    let remaining = refs.filter((r) => !usedByUrl.has(r.url));
    // Dedupe by URL for the Sources block
    const seenUrls = new Set();
    remaining = remaining.filter((r) => {
      if (seenUrls.has(r.url)) return false;
      seenUrls.add(r.url);
      return true;
    });
    if (remaining.length > 0) {
      const sig = remaining.map((r) => r.url).slice().sort().join('|');
      const isDuplicate = sig === lastSourcesSignature;
      if (!isDuplicate) {
      const refsText = remaining
        .map((r) => `[${escapeMd(r.title)}](${r.url})`)
        .join(' ');
      lines.push('');
      lines.push(remaining.length === 1 ? `Source: ${refsText}` : `Sources: ${refsText}`);
        lastSourcesSignature = sig;
      }
    }

    lines.push('');
  }

  return lines.join('\n');
}

function escapeMd(text) {
  return String(text).replace(/([\\`*_{}\[\]()#+\-.!])/g, '\\$1');
}

async function ensureFileWritten(filePath, contents) {
  await fs.promises.mkdir(path.dirname(filePath), { recursive: true });
  await fs.promises.writeFile(filePath, contents, 'utf8');
}

/**
 * Replace inline citation markers with markdown links using metadata or trailing sources.
 * Supported markers:
 *  - Perplexity-style:  → uses nth link from trailing Sources: list
 *  - ChatGPT internal: citeturn15search0turn15search1 → replaced with links by id from metadata
 */
function transformInlineCitations(text, metadata) {
  if (typeof text !== 'string' || text.length === 0) return text;

  const refs = collectReferencesFromMetadata(metadata);
  const idToRef = refs.idToRef || new Map();
  const usedByUrl = new Set();

  // Some assistant messages are wrapped as JSON with a `response` string. Extract it.
  const extracted = extractResponseFromStructuredJson(text);
  if (extracted.extracted) {
    text = extracted.text;
  }

  // Parse trailing Sources block (if present) to map indices → links
  let numberToRef = new Map();
  try {
    const sourcesMatch = text.match(/(?:^|\n)\*{0,3}\s*Sources\s*:\s*[\s\S]*$/i);
    if (sourcesMatch) {
      const sourcesBlock = sourcesMatch[0];
      const linkRegex = /\[([^\]]+)\]\((https?:[^)\s]+)\)/g;
      let idx = 1;
      let m;
      while ((m = linkRegex.exec(sourcesBlock)) !== null) {
        const title = m[1];
        const url = normalizeUrlForDedupe(m[2]);
        numberToRef.set(idx, { title, url });
        idx += 1;
      }
    }
  } catch {}

  // Replace ChatGPT internal cite markers. Support both separators:  and 
  const citeMarkerRegex = /cite([\s\S]*?)/g;
  text = text.replace(citeMarkerRegex, (_full, innerRaw) => {
    const inner = String(innerRaw).trim();
    const parts = inner.split(/[,]+/).map((s) => s.trim()).filter(Boolean);
    const links = [];
    for (const id of parts) {
      const ref = idToRef.get(id);
      if (ref && ref.url) {
        const title = ref.title || ref.url;
        links.push(`[${escapeMd(title)}](${ref.url})`);
        usedByUrl.add(normalizeUrlForDedupe(ref.url));
      }
    }
    // Fallback: if we couldn't resolve by IDs, include all refs inline (best effort)
    if (links.length === 0 && Array.isArray(refs) && refs.length > 0) {
      for (const ref of refs) {
        if (ref && ref.url) {
          const title = ref.title || ref.url;
          links.push(`[${escapeMd(title)}](${ref.url})`);
          usedByUrl.add(normalizeUrlForDedupe(ref.url));
        }
      }
    }
    return links.length > 0 ? links.join(' ') : '';
  });

  // Replace navlist markers into a simple See also line
  const navlistRegex = /navlist([\s\S]*?)/g;
  text = text.replace(navlistRegex, (_full, innerRaw) => {
    const inner = String(innerRaw);
    const segments = inner.split(//);
    const title = (segments[0] || '').trim() || 'See also';
    const idsCsv = (segments[1] || '').trim();
    const ids = idsCsv.split(/[,\s]+/).map((s) => s.trim()).filter(Boolean);
    const links = [];
    for (const id of ids) {
      const ref = idToRef.get(id);
      if (ref && ref.url) {
        links.push(`[${escapeMd(ref.title || ref.url)}](${ref.url})`);
        usedByUrl.add(normalizeUrlForDedupe(ref.url));
      }
    }
    return links.length ? `${escapeMd(title)}: ${links.join(' ')}` : '';
  });

  // Replace Perplexity-style numbered markers
  const numMarkerRegex = /【(\d+)†[^】]*】/g;
  text = text.replace(numMarkerRegex, (_full, numStr) => {
    const n = parseInt(numStr, 10);
    const ref = numberToRef.get(n) || refs[n - 1];
    if (ref && ref.url) {
      const title = ref.title || ref.url;
      usedByUrl.add(normalizeUrlForDedupe(ref.url));
      return `[${escapeMd(title)}](${ref.url})`;
    }
    return '';
  });

  // Optionally dedupe within paragraphs without collapsing whitespace
  text = dedupeLinksPerParagraph(text);

  return { text, usedByUrl };
}

function dedupeLinksPerParagraph(text) {
  const paragraphs = text.split(/\n{2,}/);
  const processed = paragraphs.map((para) => {
    const seen = new Set();
    // Replace duplicate links with empty string
    const replaced = para.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, (full, label, url) => {
      const key = normalizeUrlForDedupe(url);
      if (seen.has(key)) return '';
      seen.add(key);
      // Also normalize the output link to the top page (strip #fragment)
      const normalized = key;
      return `[${label}](${normalized})`;
    });
    return replaced;
  });
  return processed.join('\n\n');
}

function normalizeUrlForDedupe(url) {
  try {
    // Strip hash fragment first
    let base = url;
    const hashIndex = base.indexOf('#');
    if (hashIndex >= 0) base = base.slice(0, hashIndex);

    // Remove utm_source=chatgpt.com query param; drop trailing ? if empty
    try {
      const u = new URL(base);
      if (u.searchParams.get('utm_source') === 'chatgpt.com') {
        u.searchParams.delete('utm_source');
      }
      const search = u.searchParams.toString();
      const rebuilt = `${u.origin}${u.pathname}${search ? `?${search}` : ''}`;
      return rebuilt;
    } catch {
      return base;
    }
  } catch {
    return url;
  }
}

function extractResponseFromStructuredJson(text) {
  const out = { extracted: false, text };
  const trimmed = String(text).trim();
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed && typeof parsed === 'object' && typeof parsed.response === 'string') {
        out.extracted = true;
        out.text = parsed.response;
      }
    } catch {
      // leave as-is
    }
  }
  return out;
}

// Removed formatBulletRuns: avoid modifying whitespace structure globally

async function* walk(dir, excludeDirs = new Set(['node_modules', '.git'])) {
  const entries = await fs.promises.readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (excludeDirs.has(entry.name)) continue;
      yield* walk(full, excludeDirs);
    } else if (entry.isFile()) {
      yield full;
    }
  }
}

async function processFile(filePath, options) {
  if (!filePath.endsWith('.json')) return false;
  // Skip derived pretty-printed files
  if (/\.indented\.json$/i.test(filePath)) return false;

  let raw;
  try {
    raw = await fs.promises.readFile(filePath, 'utf8');
  } catch {
    return false;
  }

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return false;
  }

  if (!isChatGPTExportJson(parsed)) return false;

  const convo = Array.isArray(parsed) ? parsed[0] : parsed;

  // Optionally write indented JSON when requested
  if (options.writeIndented === true) {
    const indentedPath = filePath.replace(/\.json$/i, '.indented.json');
    const pretty = JSON.stringify(parsed, null, 2);
    await ensureFileWritten(indentedPath, pretty);
  }

  // Render markdown
  const orderedMessages = extractOrderedMessages(convo);
  const md = renderMarkdown(convo, orderedMessages);
  const sourcedMdPath = filePath.replace(/\.json$/i, '.sourced.md');
  await ensureFileWritten(sourcedMdPath, md);

  return true;
}

async function main() {
  const repoRoot = process.cwd();
  const argv = new Set(process.argv.slice(2));
  const options = { writeIndented: argv.has('--write-indented') || argv.has('--indented') };
  let processedCount = 0;
  for await (const file of walk(repoRoot)) {
    try {
      const did = await processFile(file, options);
      if (did) processedCount += 1;
    } catch (err) {
      // Continue scanning other files; optionally log
      // console.error(`Failed processing ${file}:`, err);
    }
  }
  console.log(`Processed ${processedCount} ChatGPT export JSON file(s).`);
}

// ESM main check
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const invokedPath = path.resolve(process.argv[1] || '');
const thisPath = path.resolve(__filename);
if (invokedPath === thisPath) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}


