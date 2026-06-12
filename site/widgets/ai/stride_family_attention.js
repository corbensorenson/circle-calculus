import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = [
  "AIT-T0015",
  "AIT-T0016",
  "AIT-T0017",
  "AIT-T0018",
  "AIT-T0019",
  "AIT-T0020",
  "AIT-T0021",
  "AIT-T0028",
  "AIT-T0033",
  "AIT-T0034",
  "AIT-T0035",
  "AIT-T0036",
  "AIT-T0037",
  "AIT-T0038",
];
const DICTIONARY_IDS = ["COMMON-0075", "COMMON-0079", "COMMON-0047", "COMMON-0029"];

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

function uniquePreservingOrder(values) {
  const seen = new Set();
  const result = [];
  for (const value of values) {
    if (!seen.has(value)) {
      seen.add(value);
      result.push(value);
    }
  }
  return result;
}

function strideFamilyCandidates(sequenceLength, queryIndex, strides, pathLength, localWindow) {
  const candidates = [...localWindowIndices(sequenceLength, queryIndex, localWindow)];
  for (const stride of strides) {
    candidates.push(...coilAttentionPath(sequenceLength, queryIndex, stride, pathLength));
  }
  return uniquePreservingOrder(candidates);
}

function strideFamilyCoveredLags(sequenceLength, strides, pathLength, localWindow) {
  const covered = Array.from(
    { length: Math.min(localWindow, sequenceLength - 1) },
    (_, index) => index + 1,
  );
  for (const stride of strides) {
    for (let step = 1; step <= pathLength; step += 1) {
      const lag = mod(step * stride, sequenceLength);
      if (lag !== 0) covered.push(lag);
    }
  }
  return uniquePreservingOrder(covered);
}

function strideFamilyCoverageCertificate(sequenceLength, strides, pathLength, localWindow) {
  const coveredLags = strideFamilyCoveredLags(sequenceLength, strides, pathLength, localWindow);
  const covered = new Set(coveredLags);
  const uncoveredLags = [];
  for (let lag = 1; lag < sequenceLength; lag += 1) {
    if (!covered.has(lag)) uncoveredLags.push(lag);
  }
  const candidateBudget = strideFamilyCandidates(sequenceLength, 0, strides, pathLength, localWindow).length;
  const rawCandidateBudgetUpperBound = localWindow + pathLength * strides.length;
  return {
    coveredLags,
    uncoveredLags,
    coveredLagCount: coveredLags.length,
    uncoveredLagCount: uncoveredLags.length,
    candidateBudgetPerQuery: candidateBudget,
    rawCandidateBudgetUpperBound,
    fullAttentionBudget: sequenceLength,
    coverageComplete: uncoveredLags.length === 0,
    coverageRatio: sequenceLength <= 1 ? 1 : coveredLags.length / (sequenceLength - 1),
  };
}

function fullAttentionIndices(sequenceLength) {
  return Array.from({ length: sequenceLength }, (_, index) => index);
}

function retrievalTargetIndex(sequenceLength, queryIndex, targetLag) {
  return mod(queryIndex - targetLag, sequenceLength);
}

function structuredLag(index, strides, pathLength, localWindow) {
  const nearLag = Math.min(3, localWindow);
  const lagCycle = [nearLag, ...strides.map((stride) => stride * Math.min(2, pathLength))];
  lagCycle.push(strides[strides.length - 1] * pathLength);
  return lagCycle[index % lagCycle.length];
}

function nonstructuredLag(queryIndex, sequenceLength) {
  return mod(11 * queryIndex + 17, sequenceLength - 1) + 1;
}

function hit(candidates, target) {
  return new Set(candidates).has(target);
}

function hitRate(values, candidatesForQuery, lagForQuery) {
  let hits = 0;
  for (let query = 0; query < values.queryCount; query += 1) {
    const target = retrievalTargetIndex(values.sequenceLength, query, lagForQuery(query));
    if (hit(candidatesForQuery(query), target)) hits += 1;
  }
  return hits / values.queryCount;
}

function averageCandidateCount(values, candidatesForQuery) {
  let total = 0;
  for (let query = 0; query < values.queryCount; query += 1) {
    total += new Set(candidatesForQuery(query)).size;
  }
  return total / values.queryCount;
}

function formatNumber(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

function formatCandidates(candidates, limit = 18) {
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
  title.textContent = "Stride-family theorems";
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
  for (const label of ["strategy", "structured hit rate", "control hit rate", "avg candidates", "role"]) {
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
      formatNumber(row.structuredHitRate),
      formatNumber(row.controlHitRate),
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
  const strides = [values.strideA, values.strideB];
  const wrongStrides = [values.wrongStrideA, values.wrongStrideB];
  const structuredLagForQuery = (query) => structuredLag(query, strides, values.pathLength, values.localWindow);
  const controlLagForQuery = (query) => nonstructuredLag(query, values.sequenceLength);
  const localForQuery = (query) => localWindowIndices(values.sequenceLength, query, values.localWindow);
  const singleForQuery = (query) => strideFamilyCandidates(
    values.sequenceLength,
    query,
    [values.strideA],
    values.pathLength,
    values.localWindow,
  );
  const familyForQuery = (query) => strideFamilyCandidates(
    values.sequenceLength,
    query,
    strides,
    values.pathLength,
    values.localWindow,
  );
  const wrongFamilyForQuery = (query) => strideFamilyCandidates(
    values.sequenceLength,
    query,
    wrongStrides,
    values.pathLength,
    values.localWindow,
  );
  const fullForQuery = () => fullAttentionIndices(values.sequenceLength);

  const strategies = [
    ["stride family", familyForQuery, "local plus two admitted coil strides"],
    ["single stride", singleForQuery, "local plus first admitted stride only"],
    ["local window", localForQuery, "ordinary local sparse baseline"],
    ["wrong family", wrongFamilyForQuery, "wrong-stride sparse control"],
    ["full-attention oracle", fullForQuery, "every sequence index"],
  ].map(([label, candidatesForQuery, role]) => ({
    label,
    structuredHitRate: hitRate(values, candidatesForQuery, structuredLagForQuery),
    controlHitRate: hitRate(values, candidatesForQuery, controlLagForQuery),
    averageCandidates: averageCandidateCount(values, candidatesForQuery),
    role,
  }));

  const inspectedQuery = mod(values.inspectQuery, values.queryCount);
  const inspectedLag = structuredLagForQuery(inspectedQuery);
  const inspectedTarget = retrievalTargetIndex(values.sequenceLength, inspectedQuery, inspectedLag);
  const inspectedCandidates = familyForQuery(inspectedQuery);
  const coverage = strideFamilyCoverageCertificate(
    values.sequenceLength,
    strides,
    values.pathLength,
    values.localWindow,
  );

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Stride-family sparse-attention record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIM-B0017`,
    `sequence length: ${values.sequenceLength}`,
    `query count: ${values.queryCount}`,
    `strides: (${strides.join(", ")})`,
    `wrong strides: (${wrongStrides.join(", ")})`,
    `path length: ${values.pathLength}`,
    `local window: ${values.localWindow}`,
    `structured lag sample: ${Array.from({ length: 8 }, (_, index) => structuredLagForQuery(index)).join(", ")}`,
    `control lag sample: ${Array.from({ length: 8 }, (_, index) => controlLagForQuery(index)).join(", ")}`,
    `covered positive lags: ${formatCandidates(coverage.coveredLags, 18)}`,
    `uncovered lag sample: ${formatCandidates(coverage.uncoveredLags, 18)}`,
    `covered lag count: ${coverage.coveredLagCount}`,
    `uncovered lag count: ${coverage.uncoveredLagCount}`,
    `coverage complete: ${coverage.coverageComplete}`,
    `coverage ratio: ${formatNumber(coverage.coverageRatio)}`,
    `deduplicated candidate budget per query: ${coverage.candidateBudgetPerQuery}`,
    `raw candidate-budget upper bound: ${coverage.rawCandidateBudgetUpperBound}`,
    `full-attention budget: ${coverage.fullAttentionBudget}`,
    `inspected query: ${inspectedQuery}`,
    `inspected structured lag: ${inspectedLag}`,
    `inspected target: ${inspectedTarget}`,
    `inspected family candidates: ${formatCandidates(inspectedCandidates)}`,
    `inspected hit: ${hit(inspectedCandidates, inspectedTarget) ? "hit" : "miss"}`,
  ].join("\n");
  record.appendChild(data);

  appendStrategyTable(record, strategies);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget checks finite stride-family candidate-set reachability and gap certificates only. It is not a sparse-attention quality, context-length, runtime, memory-scaling, throughput, or attention-replacement claim.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Stride-family sparse attention", "Widget: multi-stride candidate reachability only");
  const lengthInput = addLabeledNumber(panel, "ai-stride-family-sequence-length", "sequence length", 120, 2, 180);
  const queryCountInput = addLabeledNumber(panel, "ai-stride-family-query-count", "query count", 120, 1, 180);
  const inspectQueryInput = addLabeledNumber(panel, "ai-stride-family-inspect-query", "inspect query", 50, 0, 179);
  const strideAInput = addLabeledNumber(panel, "ai-stride-family-stride-a", "stride A", 7, 1, 179);
  const strideBInput = addLabeledNumber(panel, "ai-stride-family-stride-b", "stride B", 13, 1, 179);
  const wrongStrideAInput = addLabeledNumber(panel, "ai-stride-family-wrong-a", "wrong stride A", 5, 1, 179);
  const wrongStrideBInput = addLabeledNumber(panel, "ai-stride-family-wrong-b", "wrong stride B", 9, 1, 179);
  const pathLengthInput = addLabeledNumber(panel, "ai-stride-family-path-length", "path length", 3, 1, 32);
  const localWindowInput = addLabeledNumber(panel, "ai-stride-family-local-window", "local window", 4, 1, 64);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const sequenceLength = positiveInt(lengthInput.value, 120, 2, 180);
    const queryCount = positiveInt(queryCountInput.value, 120, 1, 180);
    const values = {
      sequenceLength,
      queryCount,
      inspectQuery: positiveInt(inspectQueryInput.value, 50, 0, queryCount - 1),
      strideA: positiveInt(strideAInput.value, 7, 1, sequenceLength - 1),
      strideB: positiveInt(strideBInput.value, 13, 1, sequenceLength - 1),
      wrongStrideA: positiveInt(wrongStrideAInput.value, 5, 1, sequenceLength - 1),
      wrongStrideB: positiveInt(wrongStrideBInput.value, 9, 1, sequenceLength - 1),
      pathLength: positiveInt(pathLengthInput.value, 3, 1, 32),
      localWindow: positiveInt(localWindowInput.value, 4, 1, Math.min(64, sequenceLength)),
    };
    const inspectedQuery = mod(values.inspectQuery, values.queryCount);
    const inspectedLag = structuredLag(inspectedQuery, [values.strideA, values.strideB], values.pathLength, values.localWindow);
    const inspectedTarget = retrievalTargetIndex(values.sequenceLength, inspectedQuery, inspectedLag);
    const visited = [
      mod(inspectedQuery, values.sequenceLength),
      inspectedTarget,
      ...strideFamilyCandidates(
        values.sequenceLength,
        inspectedQuery,
        [values.strideA, values.strideB],
        values.pathLength,
        values.localWindow,
      ),
    ];
    clear(output);
    output.appendChild(renderCircleSvg({
      n: values.sequenceLength,
      selected: mod(inspectedQuery, values.sequenceLength),
      visited,
      title: "Stride-family sparse-attention candidates",
    }));
    appendRecord(output, values, theoremById);
  }

  for (const input of panel.querySelectorAll("input")) {
    input.addEventListener("input", render);
  }

  Promise.all([
    loadJson("../../data/generated/theorem_manifest.json"),
  ]).then(([theoremData]) => {
    theoremById = new Map((theoremData.theorems || []).map((entry) => [entry.id, entry]));
    render();
  }).catch(() => render());
}

mountWidgets("stride_family_attention", mount);
