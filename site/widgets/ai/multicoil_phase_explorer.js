import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIA-T0005"];
const DICTIONARY_IDS = ["COMMON-0046", "COMMON-0026", "COMMON-0027"];

function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y !== 0) {
    const next = x % y;
    x = y;
    y = next;
  }
  return x;
}

function lcm(a, b) {
  return Math.abs(a * b) / gcd(a, b);
}

function multicoilPhase(periods, position) {
  return periods.map((period) => mod(position, period));
}

function multicoilCycleLength(periods) {
  return periods.reduce((cycle, period) => lcm(cycle, period), 1);
}

function multicoilPhaseLabel(periods, position) {
  const phase = multicoilPhase(periods, position);
  const score = phase.reduce((total, residue, index) => total + (index + 1) * residue, 0);
  return score % 4 === 1 ? 1 : 0;
}

function formatTuple(values) {
  return `(${values.join(", ")})`;
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

function appendPhaseTable(record, periods, position, cycle) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["period", "phase(position)", "phase(position + cycle)", "same"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const period of periods) {
    const phase = mod(position, period);
    const shifted = mod(position + cycle, period);
    const tr = document.createElement("tr");
    for (const value of [String(period), String(phase), String(shifted), phase === shifted ? "yes" : "no"]) {
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
  const periods = [values.periodA, values.periodB, values.periodC].filter((period) => period > 1);
  const cycle = multicoilCycleLength(periods);
  const phase = multicoilPhase(periods, values.position);
  const shiftedPhase = multicoilPhase(periods, values.position + cycle);
  const label = multicoilPhaseLabel(periods, values.position);
  const shiftedLabel = multicoilPhaseLabel(periods, values.position + cycle);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "MultiCoil phase record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIRA-B0002`,
    `periods: ${formatTuple(periods)}`,
    `position: ${values.position}`,
    `combined phase tuple: ${formatTuple(phase)}`,
    `joint repeat horizon lcm(periods): ${cycle}`,
    `position + cycle: ${values.position + cycle}`,
    `shifted phase tuple: ${formatTuple(shiftedPhase)}`,
    `phase tuple closes after one joint cycle: ${JSON.stringify(phase) === JSON.stringify(shiftedPhase)}`,
    `constructed synthetic label: ${label}`,
    `shifted synthetic label: ${shiftedLabel}`,
    `label closes after one joint cycle: ${label === shiftedLabel}`,
  ].join("\n");
  record.appendChild(data);
  appendPhaseTable(record, periods, values.position, cycle);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget is positional phase bookkeeping for a synthetic fixture. It is not a RoPE improvement, language-model result, attention replacement, or model-quality claim.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "MultiCoil phase explorer", "Widget: combined positional phases only");
  const periodAInput = addLabeledNumber(panel, "ai-multicoil-period-a", "period A", 5, 2, 64);
  const periodBInput = addLabeledNumber(panel, "ai-multicoil-period-b", "period B", 7, 2, 64);
  const periodCInput = addLabeledNumber(panel, "ai-multicoil-period-c", "period C", 1, 1, 64);
  const positionInput = addLabeledNumber(panel, "ai-multicoil-position", "position", 42, 0, 999);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      periodA: positiveInt(periodAInput.value, 5, 2, 64),
      periodB: positiveInt(periodBInput.value, 7, 2, 64),
      periodC: positiveInt(periodCInput.value, 1, 1, 64),
      position: positiveInt(positionInput.value, 42, 0, 999),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [periodAInput, periodBInput, periodCInput, positionInput]) {
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

mountWidgets("multicoil_phase_explorer", mount);
