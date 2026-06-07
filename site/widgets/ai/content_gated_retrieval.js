import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["CC-T0002", "CC-T0005"];
const DICTIONARY_IDS = ["COMMON-0057", "COMMON-0047", "COMMON-0028"];

function coilAttentionPath(sequenceLength, queryIndex, stride, pathLength) {
  return Array.from(
    { length: pathLength },
    (_, index) => mod(queryIndex - (index + 1) * stride, sequenceLength),
  );
}

function localWindowIndices(sequenceLength, queryIndex, window) {
  return Array.from(
    { length: window },
    (_, index) => mod(queryIndex - (index + 1), sequenceLength),
  );
}

function retrievalTargetIndex(sequenceLength, queryIndex, targetLag) {
  return mod(queryIndex - targetLag, sequenceLength);
}

function mixedTargetLag(queryIndex, longTargetLag, nearTargetLag) {
  return queryIndex % 2 === 0 ? longTargetLag : nearTargetLag;
}

function routeLabel(queryIndex) {
  return queryIndex % 2 === 0 ? "coil" : "local";
}

function routeCandidates(route, coilCandidates, localCandidates) {
  return route === "coil" ? coilCandidates : localCandidates;
}

function uniqueSorted(values) {
  return Array.from(new Set(values)).sort((a, b) => a - b);
}

function fullAttentionIndices(sequenceLength) {
  return Array.from({ length: sequenceLength }, (_, index) => index);
}

function hit(candidates, target) {
  return new Set(candidates).has(target);
}

function candidateSets(values, strategy) {
  const sets = [];
  for (let query = 0; query < values.queryCount; query += 1) {
    const coil = coilAttentionPath(values.sequenceLength, query, values.stride, values.pathLength);
    const local = localWindowIndices(values.sequenceLength, query, values.localWindow);
    if (strategy === "gated") sets.push(routeCandidates(routeLabel(query), coil, local));
    if (strategy === "static_coil") sets.push(coil);
    if (strategy === "static_local") sets.push(local);
    if (strategy === "wrong_gate") {
      sets.push(routeCandidates(routeLabel(query) === "coil" ? "local" : "coil", coil, local));
    }
    if (strategy === "union") sets.push(uniqueSorted([...coil, ...local]));
    if (strategy === "full") sets.push(fullAttentionIndices(values.sequenceLength));
  }
  return sets;
}

function hitRate(values, sets) {
  let hits = 0;
  for (let query = 0; query < values.queryCount; query += 1) {
    const lag = mixedTargetLag(query, values.longTargetLag, values.nearTargetLag);
    const target = retrievalTargetIndex(values.sequenceLength, query, lag);
    if (hit(sets[query], target)) hits += 1;
  }
  return hits / values.queryCount;
}

function averageCandidateCount(sets) {
  return sets.reduce((total, candidates) => total + new Set(candidates).size, 0) / sets.length;
}

function formatNumber(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

function formatCandidates(candidates, limit = 16) {
  const shown = candidates.slice(0, limit).join(", ");
  return candidates.length > limit ? `${shown}, +${candidates.length - limit} more` : shown;
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
  title.textContent = "Finite primitive theorems";
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

function appendStrategyTable(record, rows) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["strategy", "hit rate", "avg candidates", "role"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const row of rows) {
    const tr = document.createElement("tr");
    for (const value of [
      row.label,
      formatNumber(row.hitRate),
      formatNumber(row.averageCandidates),
      row.role,
    ]) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  record.appendChild(table);
}

function appendRecord(output, values, theoremById) {
  const strategies = [
    ["content-gated", "gated", "chooses coil for long even queries and local for near odd queries"],
    ["static coil", "static_coil", "uses the selected coil path for every query"],
    ["static local", "static_local", "uses local candidates for every query"],
    ["wrong gate", "wrong_gate", "swaps the intended coil/local route"],
    ["union", "union", "keeps both coil and local candidates"],
    ["full-attention oracle", "full", "keeps every sequence index"],
  ].map(([label, key, role]) => {
    const sets = candidateSets(values, key);
    return {
      label,
      hitRate: hitRate(values, sets),
      averageCandidates: averageCandidateCount(sets),
      role,
    };
  });

  const inspectedQuery = mod(values.inspectQuery, values.queryCount);
  const route = routeLabel(inspectedQuery);
  const targetLag = mixedTargetLag(inspectedQuery, values.longTargetLag, values.nearTargetLag);
  const target = retrievalTargetIndex(values.sequenceLength, inspectedQuery, targetLag);
  const coil = coilAttentionPath(values.sequenceLength, inspectedQuery, values.stride, values.pathLength);
  const local = localWindowIndices(values.sequenceLength, inspectedQuery, values.localWindow);
  const gated = routeCandidates(route, coil, local);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Content-gated routing record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIM-B0004`,
    `sequence length: ${values.sequenceLength}`,
    `query count: ${values.queryCount}`,
    `long target lag: ${values.longTargetLag}`,
    `near target lag: ${values.nearTargetLag}`,
    `stride: ${values.stride}`,
    `path length: ${values.pathLength}`,
    `local window: ${values.localWindow}`,
    `inspected query: ${inspectedQuery}`,
    `inspected route: ${route}`,
    `inspected target: ${target}`,
    `inspected gated candidates: ${formatCandidates(gated)}`,
    `inspected hit: ${hit(gated, target) ? "hit" : "miss"}`,
  ].join("\n");
  record.appendChild(data);

  appendStrategyTable(record, strategies);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget checks deterministic route bookkeeping and candidate budgets only. It is not a learned-gate, retrieval-quality, context-length, runtime, memory-scaling, or attention-replacement claim.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Content-gated retrieval", "Widget: coil/local route bookkeeping only");
  const lengthInput = addLabeledNumber(panel, "ai-gate-sequence-length", "sequence length", 64, 2, 128);
  const queryCountInput = addLabeledNumber(panel, "ai-gate-query-count", "query count", 64, 1, 128);
  const inspectQueryInput = addLabeledNumber(panel, "ai-gate-inspect-query", "inspect query", 10, 0, 127);
  const longLagInput = addLabeledNumber(panel, "ai-gate-long-lag", "long lag", 21, 0, 127);
  const nearLagInput = addLabeledNumber(panel, "ai-gate-near-lag", "near lag", 3, 0, 127);
  const strideInput = addLabeledNumber(panel, "ai-gate-stride", "stride", 7, 0, 127);
  const pathLengthInput = addLabeledNumber(panel, "ai-gate-path-length", "path length", 3, 1, 32);
  const localWindowInput = addLabeledNumber(panel, "ai-gate-local-window", "local window", 8, 1, 64);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const sequenceLength = positiveInt(lengthInput.value, 64, 2, 128);
    const queryCount = positiveInt(queryCountInput.value, 64, 1, 128);
    const values = {
      sequenceLength,
      queryCount,
      inspectQuery: positiveInt(inspectQueryInput.value, 10, 0, queryCount - 1),
      longTargetLag: positiveInt(longLagInput.value, 21, 0, sequenceLength - 1),
      nearTargetLag: positiveInt(nearLagInput.value, 3, 0, sequenceLength - 1),
      stride: positiveInt(strideInput.value, 7, 0, sequenceLength - 1),
      pathLength: positiveInt(pathLengthInput.value, 3, 1, 32),
      localWindow: positiveInt(localWindowInput.value, 8, 1, Math.min(64, sequenceLength)),
    };
    const inspectedQuery = mod(values.inspectQuery, values.queryCount);
    const targetLag = mixedTargetLag(inspectedQuery, values.longTargetLag, values.nearTargetLag);
    const target = retrievalTargetIndex(values.sequenceLength, inspectedQuery, targetLag);
    const coil = coilAttentionPath(values.sequenceLength, inspectedQuery, values.stride, values.pathLength);
    const local = localWindowIndices(values.sequenceLength, inspectedQuery, values.localWindow);
    const gated = routeCandidates(routeLabel(inspectedQuery), coil, local);
    clear(output);
    output.appendChild(renderCircleSvg({
      n: values.sequenceLength,
      selected: mod(inspectedQuery, values.sequenceLength),
      visited: [target, ...gated],
      title: "Content-gated retrieval candidates",
    }));
    appendRecord(output, values, theoremById);
  }

  for (const input of [
    lengthInput,
    queryCountInput,
    inspectQueryInput,
    longLagInput,
    nearLagInput,
    strideInput,
    pathLengthInput,
    localWindowInput,
  ]) {
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

mountWidgets("content_gated_retrieval", mount);
