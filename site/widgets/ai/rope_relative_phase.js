import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIA-T0005"];
const DICTIONARY_IDS = ["COMMON-0051", "COMMON-0050", "COMMON-0026"];

function ropeRelativeFeature(period, queryPosition, keyPosition) {
  const lag = mod(queryPosition - keyPosition, period);
  const angle = (2 * Math.PI * lag) / period;
  return {
    lag,
    cos: Number(Math.cos(angle).toFixed(12)),
    sin: Number(Math.sin(angle).toFixed(12)),
  };
}

function defaultPositiveLags(period) {
  return Array.from({ length: period }, (_, lag) => lag).filter((lag) => lag % 3 === 1);
}

function relativeLabel(period, queryPosition, keyPosition) {
  const feature = ropeRelativeFeature(period, queryPosition, keyPosition);
  return defaultPositiveLags(period).includes(feature.lag) ? 1 : 0;
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
  title.textContent = "Finite phase-channel theorems";
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

function appendFeatureTable(record, rows) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["case", "period", "lag", "cos", "sin", "label"]) {
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
      String(row.period),
      String(row.feature.lag),
      String(row.feature.cos),
      String(row.feature.sin),
      String(row.syntheticLabel),
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
  const correct = ropeRelativeFeature(values.period, values.query, values.key);
  const wrong = ropeRelativeFeature(values.wrongPeriod, values.query, values.key);
  const shiftedQuery = ropeRelativeFeature(values.period, values.query + values.period, values.key);
  const shiftedKey = ropeRelativeFeature(values.period, values.query, values.key + values.period);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "RoPE-style relative phase record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIRA-B0003`,
    `query position: ${values.query}`,
    `key position: ${values.key}`,
    `correct period: ${values.period}`,
    `wrong period: ${values.wrongPeriod}`,
    `positive lags for correct period: ${defaultPositiveLags(values.period).join(", ")}`,
    `correct-period lag: ${correct.lag}`,
    `correct-period feature: (${correct.cos}, ${correct.sin})`,
    `query + period feature closes: ${JSON.stringify(correct) === JSON.stringify(shiftedQuery)}`,
    `key + period feature closes: ${JSON.stringify(correct) === JSON.stringify(shiftedKey)}`,
  ].join("\n");
  record.appendChild(data);

  appendFeatureTable(record, [
    {
      label: "correct period",
      period: values.period,
      feature: correct,
      syntheticLabel: relativeLabel(values.period, values.query, values.key),
    },
    {
      label: "wrong period",
      period: values.wrongPeriod,
      feature: wrong,
      syntheticLabel: relativeLabel(values.wrongPeriod, values.query, values.key),
    },
    {
      label: "query shifted by period",
      period: values.period,
      feature: shiftedQuery,
      syntheticLabel: relativeLabel(values.period, values.query + values.period, values.key),
    },
    {
      label: "key shifted by period",
      period: values.period,
      feature: shiftedKey,
      syntheticLabel: relativeLabel(values.period, values.query, values.key + values.period),
    },
  ]);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget is a relative phase fixture only. It is not a standard RoPE benchmark, attention-quality result, context-length result, perplexity result, or runtime claim.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "RoPE relative phase", "Widget: query/key lag phase only");
  const periodInput = addLabeledNumber(panel, "ai-rope-period", "period", 8, 2, 64);
  const wrongPeriodInput = addLabeledNumber(panel, "ai-rope-wrong-period", "wrong period", 7, 2, 64);
  const queryInput = addLabeledNumber(panel, "ai-rope-query", "query", 19, 0, 999);
  const keyInput = addLabeledNumber(panel, "ai-rope-key", "key", 11, -999, 999);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      period: positiveInt(periodInput.value, 8, 2, 64),
      wrongPeriod: positiveInt(wrongPeriodInput.value, 7, 2, 64),
      query: positiveInt(queryInput.value, 19, 0, 999),
      key: positiveInt(keyInput.value, 11, -999, 999),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [periodInput, wrongPeriodInput, queryInput, keyInput]) {
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

mountWidgets("rope_relative_phase", mount);
