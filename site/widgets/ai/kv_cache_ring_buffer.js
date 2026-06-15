import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = [
  "AIM-T0059",
  "AIM-T0060",
  "AIM-T0061",
  "AIM-T0062",
  "AIM-T0063",
  "AIM-T0064",
  "AIM-T0065",
  "AIM-T0066",
  "AIM-T0067",
  "AIM-T0068",
  "AIM-T0069",
  "AIM-T0070",
  "AIM-T0071",
  "AIM-T0072",
  "AIM-T0073",
  "AIM-T0074",
  "AIM-T0075",
  "AIM-T0076",
  "AIM-T0077",
  "AIM-T0078",
  "AIM-T0079",
  "AIM-T0080",
  "AIM-T0081",
  "AIM-T0082",
  "AIM-T0083",
  "AIM-T0086",
  "AIM-T0087",
  "AIM-T0088",
  "AIM-T0089",
  "AIM-T0091",
  "AIM-T0092",
  "AIM-T0093",
  "AIM-T0094",
  "AIM-T0095",
  "AIM-T0096",
];
const DICTIONARY_IDS = ["COMMON-0028", "COMMON-0081"];

function kvSlot(cacheSize, token) {
  return mod(token, cacheSize);
}

function retained(cacheSize, current, token) {
  return token <= current && current < token + cacheSize;
}

function liveTokens(cacheSize, current) {
  const start = Math.max(0, current - cacheSize + 1);
  return Array.from({ length: current - start + 1 }, (_, index) => start + index);
}

function allDistinct(values) {
  return new Set(values).size === values.length;
}

function isOrderedSubsequence(needle, haystack) {
  let haystackIndex = 0;
  for (const value of needle) {
    while (haystackIndex < haystack.length && haystack[haystackIndex] !== value) {
      haystackIndex += 1;
    }
    if (haystackIndex === haystack.length) {
      return false;
    }
    haystackIndex += 1;
  }
  return true;
}

function coversSlotRange(slots, cacheSize) {
  const seen = new Set(slots);
  return seen.size === cacheSize
    && Array.from({ length: cacheSize }, (_, index) => index).every((slot) => seen.has(slot));
}

function noSameSlotOverwriteBeforeCurrent(cacheSize, current, token) {
  if (token > current) {
    return false;
  }
  const slot = kvSlot(cacheSize, token);
  return Array.from(
    { length: Math.max(0, current - token) },
    (_, index) => token + index + 1,
  ).every((overwrite) => kvSlot(cacheSize, overwrite) !== slot);
}

function readBatch(cacheSize, current, token) {
  const candidates = [
    token,
    Math.min(current, token + Math.max(1, Math.floor(cacheSize / 4))),
    Math.max(0, current - 2),
    current,
  ];
  return Array.from(new Set(candidates.filter((candidate) => candidate <= current)))
    .sort((left, right) => left - right);
}

function traceFreshBatchSlotsDistinct(cacheSize, current, tokens) {
  if (!allDistinct(tokens)) {
    return false;
  }
  if (!tokens.every((token) => token <= current)) {
    return false;
  }
  if (!tokens.every((token) => noSameSlotOverwriteBeforeCurrent(cacheSize, current, token))) {
    return false;
  }
  return allDistinct(tokens.map((token) => kvSlot(cacheSize, token)));
}

function makeLink(id, page) {
  const href = new URL(`../../${page}#${encodeURIComponent(id)}`, import.meta.url).toString();
  const link = document.createElement("a");
  link.href = href;
  link.textContent = id;
  return link;
}

function appendBadgeRow(section, theoremById) {
  const row = document.createElement("div");
  row.className = "generator-badge-row";
  const title = document.createElement("strong");
  title.textContent = "Theorems";
  row.appendChild(title);
  for (const id of THEOREM_IDS) {
    const theorem = theoremById.get(id);
    const badge = makeLink(id, "theorems.html");
    badge.className = theorem ? statusClass(theorem) : "status-badge status-planned";
    badge.textContent = theorem ? `${id}: ${statusLabel(theorem)}` : `${id}: status loading`;
    row.appendChild(badge);
  }
  section.appendChild(row);
}

function appendDictionaryRow(section) {
  const row = document.createElement("div");
  row.className = "generator-badge-row";
  const title = document.createElement("strong");
  title.textContent = "Dictionary";
  row.appendChild(title);
  for (const id of DICTIONARY_IDS) {
    const link = makeLink(id, "dictionary.html");
    link.className = "record-pill";
    row.appendChild(link);
  }
  section.appendChild(row);
}

function appendRecord(output, values, theoremById) {
  const slot = kvSlot(values.cacheSize, values.token);
  const currentSlot = kvSlot(values.cacheSize, values.current);
  const isFuture = values.token > values.current;
  const lag = isFuture ? null : values.current - values.token;
  const isRetained = retained(values.cacheSize, values.current, values.token);
  const nextOverwrite = values.token + values.cacheSize;
  const overwriteAfterCurrent = values.current < nextOverwrite;
  const staleByOverwriteBoundary = !isFuture && !isRetained && nextOverwrite <= values.current;
  const staleOverwriteWitness = staleByOverwriteBoundary && values.token < nextOverwrite && nextOverwrite <= values.current && slot === kvSlot(values.cacheSize, nextOverwrite);
  const noSameSlotOverwrite = noSameSlotOverwriteBeforeCurrent(values.cacheSize, values.current, values.token);
  const retainedIffNoSameSlotOverwrite = !isFuture && isRetained === noSameSlotOverwrite;
  const traceFreshIffNextOverwriteBoundary = !isFuture && noSameSlotOverwrite === overwriteAfterCurrent;
  const collisionWithCurrent = slot === currentSlot;
  const distinctFromCurrent = isRetained && values.token < values.current && !collisionWithCurrent;
  const batchTokens = readBatch(values.cacheSize, values.current, values.token);
  const batchSlots = batchTokens.map((token) => kvSlot(values.cacheSize, token));
  const batchAllNonFuture = batchTokens.every((token) => token <= values.current);
  const batchAllRetained = batchTokens.every((token) => retained(values.cacheSize, values.current, token));
  const batchTokensDistinct = allDistinct(batchTokens);
  const batchSlotsDistinct = allDistinct(batchSlots);
  const batchNextOverwritesAfterCurrent = batchTokens.every(
    (token) => values.current < token + values.cacheSize,
  );
  const batchTraceFresh = batchTokens.every(
    (token) => noSameSlotOverwriteBeforeCurrent(values.cacheSize, values.current, token),
  );
  const batchTraceFreshIffBoundary = batchAllNonFuture
    && batchTraceFresh === batchNextOverwritesAfterCurrent;
  const traceFreshSlotsDistinct = traceFreshBatchSlotsDistinct(
    values.cacheSize,
    values.current,
    batchTokens,
  );
  const adapterRequestPass = (
    batchAllNonFuture
    && batchAllRetained
    && batchTokensDistinct
    && batchSlotsDistinct
    && traceFreshSlotsDistinct
  );
  const adapterRequestBoundaryPass = (
    batchAllNonFuture
    && batchTokensDistinct
    && batchNextOverwritesAfterCurrent
  );
  const adapterRequestPassIffBoundary = adapterRequestPass === adapterRequestBoundaryPass;
  const tokens = liveTokens(values.cacheSize, values.current);
  const slots = tokens.map((token) => kvSlot(values.cacheSize, token));
  const orderedLiveWindowSubrequest = isOrderedSubsequence(batchTokens, tokens);
  const duplicateFreeLiveWindowSubrequest = orderedLiveWindowSubrequest && batchTokensDistinct;
  const liveWindowSubrequestPassContract = duplicateFreeLiveWindowSubrequest && adapterRequestPass;
  const fullWindow = values.cacheSize <= values.current + 1;
  const slotsDistinct = allDistinct(slots);
  const slotsWithinCache = slots.every((slot) => 0 <= slot && slot < values.cacheSize);
  const slotCountMatchesCacheSize = slots.length === values.cacheSize;
  const slotCountMatchesFullWindow = slotCountMatchesCacheSize === fullWindow;
  const slotRangeCovered = coversSlotRange(slots, values.cacheSize);
  const fullCoverageContract =
    fullWindow && slotsDistinct && slotCountMatchesCacheSize && slotsWithinCache;
  const fullCoverageContractMatchesFullWindow = fullCoverageContract === fullWindow;

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "KV-cache ring-buffer certificate";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `cache size: ${values.cacheSize}`,
    `current token: ${values.current}`,
    `inspected token: ${values.token}`,
    `token slot token % cache_size: ${slot}`,
    `current slot current % cache_size: ${currentSlot}`,
    `lag current - token: ${lag === null ? "future token" : lag}`,
    `retained window token <= current < token + cache_size: ${isRetained}`,
    `next same-slot overwrite token + cache_size: ${nextOverwrite}`,
    `overwrite after current: ${overwriteAfterCurrent}`,
    `stale by overwrite boundary: ${staleByOverwriteBoundary}`,
    `no later same-slot write up to current: ${noSameSlotOverwrite}`,
    `stale same-slot overwrite witness token + cache_size: ${staleOverwriteWitness}`,
    `retained iff no later same-slot write trace: ${retainedIffNoSameSlotOverwrite}`,
    `trace fresh iff next overwrite boundary: ${traceFreshIffNextOverwriteBoundary}`,
    `read batch tokens: ${batchTokens.join(", ")}`,
    `read batch slots: ${batchSlots.join(", ")}`,
    `batch next overwrites after current: ${batchNextOverwritesAfterCurrent}`,
    `batch trace fresh iff boundary: ${batchTraceFreshIffBoundary}`,
    `trace-fresh read-batch slots distinct: ${traceFreshSlotsDistinct}`,
    `ordered live-window subrequest: ${orderedLiveWindowSubrequest}`,
    `duplicate-free live-window subrequest: ${duplicateFreeLiveWindowSubrequest}`,
    `live-window subrequest pass contract: ${liveWindowSubrequestPassContract}`,
    `adapter request trace pass: ${adapterRequestPass}`,
    `adapter request pass iff boundary: ${adapterRequestPassIffBoundary}`,
    `collision with current slot: ${collisionWithCurrent}`,
    `retained older token distinct from current slot: ${distinctFromCurrent}`,
    `live window tokens: ${tokens.join(", ")}`,
    `live window slots: ${slots.join(", ")}`,
    `live tokens distinct: ${allDistinct(tokens)}`,
    `live slots distinct: ${slotsDistinct}`,
    `live window full: ${fullWindow}`,
    `live slots within cache: ${slotsWithinCache}`,
    `live slot count equals cache size: ${slotCountMatchesCacheSize}`,
    `slot count iff full window: ${slotCountMatchesFullWindow}`,
    `slot range covered: ${slotRangeCovered}`,
    `full coverage contract: ${fullCoverageContract}`,
    `full coverage iff full window: ${fullCoverageContractMatchesFullWindow}`,
    "boundary: widget output is finite indexing and overwrite-window bookkeeping, not a paging-policy, throughput, memory-saving, retrieval-quality, or deployment-safety claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "KV-cache ring buffer", "Widget: finite slot and retention-window bookkeeping only");
  const cacheInput = addLabeledNumber(panel, "kv-cache-size", "cache size", 16, 1, 64);
  const currentInput = addLabeledNumber(panel, "kv-current-token", "current token", 31, 0, 512);
  const tokenInput = addLabeledNumber(panel, "kv-inspected-token", "inspected token", 20, 0, 512);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      cacheSize: positiveInt(cacheInput.value, 16, 1, 64),
      current: positiveInt(currentInput.value, 31, 0, 512),
      token: positiveInt(tokenInput.value, 20, 0, 512),
    };
    const tokens = liveTokens(values.cacheSize, values.current);
    const visitedSlots = Array.from(new Set(tokens.map((token) => kvSlot(values.cacheSize, token))));
    clear(output);
    output.appendChild(renderCircleSvg({
      n: values.cacheSize,
      selected: kvSlot(values.cacheSize, values.token),
      visited: visitedSlots,
      title: "KV-cache ring-buffer slots",
    }));
    appendRecord(output, values, theoremById);
  }

  for (const input of [cacheInput, currentInput, tokenInput]) {
    input.addEventListener("input", render);
  }
  loadJson("../../data/generated/theorem_manifest.json")
    .then((data) => {
      theoremById = new Map(data.theorems.map((theorem) => [theorem.id, theorem]));
      render();
    })
    .catch((error) => {
      console.error(error);
      render();
    });
  render();
}

mountWidgets("kv_cache_ring_buffer", mount);
