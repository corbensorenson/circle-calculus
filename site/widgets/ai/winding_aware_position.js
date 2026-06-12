import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIRA-T0006", "AIRA-T0007", "AIRA-T0008", "AIRA-T0009", "AIRA-T0010"];
const DICTIONARY_IDS = ["COMMON-0072", "COMMON-0026", "COMMON-0046"];

function windingPosition(period, position) {
  const winding = Math.floor(position / period);
  const residue = mod(position, period);
  return { winding, residue, reconstructed: winding * period + residue };
}

function windingFeature(period, windingPeriod, position) {
  const pos = windingPosition(period, position);
  return { windingPhase: mod(pos.winding, windingPeriod), residue: pos.residue };
}

function windingLabel(period, windingPeriod, position) {
  const feature = windingFeature(period, windingPeriod, position);
  const score = feature.residue + 2 * feature.windingPhase;
  return [1, 3].includes(mod(score, 5)) ? 1 : 0;
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
  title.textContent = "Residue/winding theorems";
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

function appendAliasTable(record, values) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["position", "residue", "winding", "winding phase", "synthetic label"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  const baseResidue = mod(values.position, values.period);
  for (let winding = 0; winding < values.windingPeriod; winding += 1) {
    const position = winding * values.period + baseResidue;
    const feature = windingFeature(values.period, values.windingPeriod, position);
    const tr = document.createElement("tr");
    for (const cell of [
      String(position),
      String(feature.residue),
      String(windingPosition(values.period, position).winding),
      String(feature.windingPhase),
      String(windingLabel(values.period, values.windingPeriod, position)),
    ]) {
      const td = document.createElement("td");
      td.textContent = cell;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  record.appendChild(table);
}

function appendRecord(output, values, theoremById) {
  const position = windingPosition(values.period, values.position);
  const feature = windingFeature(values.period, values.windingPeriod, values.position);
  const shifted = windingPosition(values.period, values.position + values.period);
  const cycle = values.period * values.windingPeriod;
  const cycleFeature = windingFeature(values.period, values.windingPeriod, values.position + cycle);
  const wrongFeature = windingFeature(values.wrongPeriod, values.windingPeriod, values.position);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Winding-aware position record";
  record.appendChild(title);
  record.appendChild(renderCircleSvg({
    n: values.period,
    selected: position.residue,
    visited: [position.residue],
    title: "residue component",
  }));

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIRA-B0006`,
    `position: ${values.position}`,
    `period: ${values.period}`,
    `residue: ${position.residue}`,
    `winding: ${position.winding}`,
    `reconstructed: ${position.reconstructed}`,
    `reconstruction holds: ${position.reconstructed === values.position}`,
    `after +period residue: ${shifted.residue}`,
    `after +period winding: ${shifted.winding}`,
    `finite winding period: ${values.windingPeriod}`,
    `finite feature: (${feature.windingPhase}, ${feature.residue})`,
    `feature after full finite cycle: (${cycleFeature.windingPhase}, ${cycleFeature.residue})`,
    `feature closes after period*winding_period: ${JSON.stringify(feature) === JSON.stringify(cycleFeature)}`,
    `wrong-period feature: (${wrongFeature.windingPhase}, ${wrongFeature.residue})`,
    `constructed synthetic label: ${windingLabel(values.period, values.windingPeriod, values.position)}`,
  ].join("\n");
  record.appendChild(data);
  appendAliasTable(record, values);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget visualizes finite residue and winding bookkeeping. It is not a RoPE benchmark, long-context result, perplexity result, runtime claim, or proof by diagram.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Winding-aware position", "Widget: residue plus winding bookkeeping only");
  const periodInput = addLabeledNumber(panel, "ai-winding-period", "period", 8, 2, 64);
  const windingPeriodInput = addLabeledNumber(panel, "ai-winding-winding-period", "winding period", 4, 1, 32);
  const wrongPeriodInput = addLabeledNumber(panel, "ai-winding-wrong-period", "wrong period", 7, 2, 64);
  const positionInput = addLabeledNumber(panel, "ai-winding-position", "position", 37, 0, 999);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      period: positiveInt(periodInput.value, 8, 2, 64),
      windingPeriod: positiveInt(windingPeriodInput.value, 4, 1, 32),
      wrongPeriod: positiveInt(wrongPeriodInput.value, 7, 2, 64),
      position: positiveInt(positionInput.value, 37, 0, 999),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [periodInput, windingPeriodInput, wrongPeriodInput, positionInput]) {
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

mountWidgets("winding_aware_position", mount);
