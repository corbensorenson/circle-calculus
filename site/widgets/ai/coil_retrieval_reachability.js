import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["CC-T0002", "CC-T0005"];
const DICTIONARY_IDS = ["COMMON-0047", "COMMON-0028", "COMMON-0029"];

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

function fullAttentionIndices(sequenceLength) {
  return Array.from({ length: sequenceLength }, (_, index) => index);
}

function hit(candidates, target) {
  return new Set(candidates).has(target);
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

function appendCandidateTable(record, rows) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["candidate set", "target", "hit", "candidate count", "indices"]) {
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
      String(row.target),
      row.hit ? "hit" : "miss",
      String(new Set(row.candidates).size),
      formatCandidates(row.candidates),
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
  const longTarget = retrievalTargetIndex(values.sequenceLength, values.queryIndex, values.targetLag);
  const nearTarget = retrievalTargetIndex(values.sequenceLength, values.queryIndex, values.nearControlLag);
  const coilCandidates = coilAttentionPath(
    values.sequenceLength,
    values.queryIndex,
    values.stride,
    values.pathLength,
  );
  const localCandidates = localWindowIndices(values.sequenceLength, values.queryIndex, values.localWindow);
  const wrongCandidates = coilAttentionPath(
    values.sequenceLength,
    values.queryIndex,
    values.wrongStride,
    values.pathLength,
  );
  const fullCandidates = fullAttentionIndices(values.sequenceLength);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Coil retrieval reachability record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIM-B0002`,
    `sequence length: ${values.sequenceLength}`,
    `query index: ${values.queryIndex}`,
    `target lag: ${values.targetLag}`,
    `target index query - lag mod length: ${longTarget}`,
    `stride: ${values.stride}`,
    `path length: ${values.pathLength}`,
    `local window: ${values.localWindow}`,
    `wrong stride: ${values.wrongStride}`,
    `near-control lag: ${values.nearControlLag}`,
    `near-control target: ${nearTarget}`,
  ].join("\n");
  record.appendChild(data);

  appendCandidateTable(record, [
    {
      label: "selected coil path",
      target: longTarget,
      candidates: coilCandidates,
      hit: hit(coilCandidates, longTarget),
    },
    {
      label: "local window",
      target: longTarget,
      candidates: localCandidates,
      hit: hit(localCandidates, longTarget),
    },
    {
      label: "wrong stride",
      target: longTarget,
      candidates: wrongCandidates,
      hit: hit(wrongCandidates, longTarget),
    },
    {
      label: "full-attention oracle",
      target: longTarget,
      candidates: fullCandidates,
      hit: hit(fullCandidates, longTarget),
    },
    {
      label: "near-control local window",
      target: nearTarget,
      candidates: localCandidates,
      hit: hit(localCandidates, nearTarget),
    },
    {
      label: "near-control coil path",
      target: nearTarget,
      candidates: coilCandidates,
      hit: hit(coilCandidates, nearTarget),
    },
  ]);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget checks finite candidate-set reachability only. It is not a neural retrieval-quality, context-length, runtime, memory-scaling, or attention-replacement claim.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Coil retrieval reachability", "Widget: candidate-set arithmetic only");
  const lengthInput = addLabeledNumber(panel, "ai-coil-sequence-length", "sequence length", 64, 2, 128);
  const queryInput = addLabeledNumber(panel, "ai-coil-query-index", "query", 42, 0, 999);
  const targetLagInput = addLabeledNumber(panel, "ai-coil-target-lag", "target lag", 21, 0, 127);
  const strideInput = addLabeledNumber(panel, "ai-coil-stride", "stride", 7, 0, 127);
  const pathLengthInput = addLabeledNumber(panel, "ai-coil-path-length", "path length", 3, 1, 32);
  const localWindowInput = addLabeledNumber(panel, "ai-coil-local-window", "local window", 8, 1, 64);
  const wrongStrideInput = addLabeledNumber(panel, "ai-coil-wrong-stride", "wrong stride", 5, 0, 127);
  const nearLagInput = addLabeledNumber(panel, "ai-coil-near-lag", "near-control lag", 3, 0, 127);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const sequenceLength = positiveInt(lengthInput.value, 64, 2, 128);
    const values = {
      sequenceLength,
      queryIndex: positiveInt(queryInput.value, 42, 0, 999),
      targetLag: positiveInt(targetLagInput.value, 21, 0, sequenceLength - 1),
      stride: positiveInt(strideInput.value, 7, 0, sequenceLength - 1),
      pathLength: positiveInt(pathLengthInput.value, 3, 1, 32),
      localWindow: positiveInt(localWindowInput.value, 8, 1, Math.min(64, sequenceLength)),
      wrongStride: positiveInt(wrongStrideInput.value, 5, 0, sequenceLength - 1),
      nearControlLag: positiveInt(nearLagInput.value, 3, 0, sequenceLength - 1),
    };
    const queryNode = mod(values.queryIndex, values.sequenceLength);
    const longTarget = retrievalTargetIndex(values.sequenceLength, values.queryIndex, values.targetLag);
    const visited = [
      queryNode,
      longTarget,
      ...coilAttentionPath(values.sequenceLength, values.queryIndex, values.stride, values.pathLength),
    ];
    clear(output);
    output.appendChild(renderCircleSvg({
      n: values.sequenceLength,
      selected: queryNode,
      visited,
      title: "Coil retrieval candidate path",
    }));
    appendRecord(output, values, theoremById);
  }

  for (const input of [
    lengthInput,
    queryInput,
    targetLagInput,
    strideInput,
    pathLengthInput,
    localWindowInput,
    wrongStrideInput,
    nearLagInput,
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

mountWidgets("coil_retrieval_reachability", mount);
