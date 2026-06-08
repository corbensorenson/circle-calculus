import { addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const GENERATOR_INDEX_URL = "../../data/generated/generator_index.json";
const THEOREM_IDS = ["P2G-T0001", "P2G-T0002", "P2G-T0003", "CC-T0005"];
const DICTIONARY_IDS = ["COMMON-0033", "COMMON-0064", "COMMON-0066"];

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
  title.textContent = "Proof glyph theorems";
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

function appendFieldTable(section, rows) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["field", "generated glyph", "manifest", "match"]) {
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
    for (const value of row) {
      const td = document.createElement("td");
      td.textContent = String(value);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  section.appendChild(table);
}

function appendRecord(output, glyphRecord, theoremById) {
  const generated = glyphRecord.generatedObject;
  const theorem = theoremById.get(generated.theorem_id);
  const leanName = theorem ? theorem.lean_name || "" : "";
  const rows = [
    ["theorem id", generated.theorem_id, theorem ? theorem.id : "missing", theorem ? "yes" : "no"],
    ["Lean name", generated.lean_name, leanName || "missing", leanName === generated.lean_name ? "yes" : "no"],
    ["glyph id", generated.glyph_id, generated.glyph_id, "self"],
  ];
  const allResolved = theorem && leanName === generated.lean_name;

  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Proof glyph certificate record";
  section.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `glyph id: ${generated.glyph_id}`,
    `generated theorem id: ${generated.theorem_id}`,
    `generated Lean name: ${generated.lean_name}`,
    `manifest status: ${theorem ? statusLabel(theorem) : "missing"}`,
    `manifest source: ${theorem ? theorem.lean_source || "missing source" : "missing theorem"}`,
    `certificate resolves: ${allResolved ? "yes" : "no"}`,
    `generator note: ${glyphRecord.note}`,
  ].join("\n");
  section.appendChild(data);
  appendFieldTable(section, rows);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this generated glyph is a proof-navigation certificate. It does not prove the theorem; proof status still comes from the manifest and local Lean build.";
  section.appendChild(warning);

  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Proof glyph certificate", "Widget: generated theorem/Lean declaration linkage");
  const output = addOutput(panel);
  let theoremById = new Map();
  let glyphRecord = null;

  function render() {
    clear(output);
    if (!glyphRecord) {
      const loading = document.createElement("p");
      loading.textContent = "Loading proof glyph record.";
      output.appendChild(loading);
      return;
    }
    appendRecord(output, glyphRecord, theoremById);
  }

  Promise.all([
    loadJson("../../data/generated/theorem_manifest.json"),
    loadJson(GENERATOR_INDEX_URL),
  ])
    .then(([theoremData, generatorData]) => {
      theoremById = new Map(theoremData.theorems.map((theorem) => [theorem.id, theorem]));
      glyphRecord = (generatorData.generators || []).find((item) => item.id === "proof_glyph") || null;
      render();
    })
    .catch((error) => {
      console.error(error);
      render();
    });
  render();
}

mountWidgets("proof_glyph_certificate", mount);
