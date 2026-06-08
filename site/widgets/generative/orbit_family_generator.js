import { gcd, orbitDecomposition, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = [
  "GEN-T0003",
  "GEN-T0006",
  "GEN-T0007",
  "GEN-T0008",
  "GEN-T0009",
  "GEN-T0010",
  "GEN-T0011",
  "GEN-T0012",
  "GEN-T0013",
];
const DICTIONARY_IDS = ["CC-0205", "CC-0208", "COMMON-0064", "COMMON-0066"];

function orbitFamilyRecord(n, stride) {
  const orbits = orbitDecomposition(n, stride);
  const flattened = orbits.flat();
  const unique = new Set(flattened);
  const expected = new Set(Array.from({ length: n }, (_, index) => index));
  const coverageComplete = unique.size === expected.size && [...expected].every((node) => unique.has(node));
  const disjoint = flattened.length === unique.size;
  const orbitCount = orbits.length;
  const gcdCount = gcd(n, stride);
  return {
    n,
    stride,
    orbits,
    flattened,
    period: n / gcdCount,
    orbitCount,
    gcdCount,
    coverageComplete,
    disjoint,
    countMatchesGcd: orbitCount === gcdCount,
  };
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
  title.textContent = "Orbit-family theorems";
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

function appendOrbitTable(section, record) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["representative", "generated orbit", "length"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  record.orbits.forEach((orbit) => {
    const tr = document.createElement("tr");
    const cells = [orbit[0], orbit.join(" -> "), orbit.length];
    cells.forEach((value) => {
      const td = document.createElement("td");
      td.textContent = String(value);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  section.appendChild(table);
}

function appendRecord(output, record, theoremById) {
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Orbit-family generator record";
  section.appendChild(title);
  section.appendChild(renderCircleSvg({
    n: record.n,
    selected: 0,
    visited: record.flattened,
    title: `Generated orbit family for C_${record.n}`,
  }));
  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    "artifact id: orbit_decomposition",
    `seed: {"n":${record.n},"stride":${record.stride}}`,
    "rules: repeat_rotation, restart_at_smallest_unvisited",
    "schedule: generate one closed orbit, then restart at the smallest unvisited node",
    "closure: stop when every node in C_n has appeared exactly once",
    `period n/gcd(n,k): ${record.period}`,
    `orbit count: ${record.orbitCount}`,
    `gcd(n,k): ${record.gcdCount}`,
    `count matches gcd: ${record.countMatchesGcd}`,
    `coverage complete: ${record.coverageComplete}`,
    `orbits disjoint: ${record.disjoint}`,
  ].join("\n");
  section.appendChild(data);
  appendOrbitTable(section, record);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget shows exact finite orbit-family regeneration and theorem-linked coverage checks. It does not prove generator minimality, global compression optimality, or theorem discovery power.";
  section.appendChild(warning);

  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Orbit-family generator", "Widget: finite seed/rule orbit decomposition");
  const nInput = addLabeledNumber(panel, "gen-orbit-family-n", "circle size n", 12, 1, 48);
  const strideInput = addLabeledNumber(panel, "gen-orbit-family-stride", "stride", 8, 0, 96);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const record = orbitFamilyRecord(
      positiveInt(nInput.value, 12, 1, 48),
      positiveInt(strideInput.value, 8, 0, 96),
    );
    clear(output);
    appendRecord(output, record, theoremById);
  }

  for (const input of [nInput, strideInput]) {
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

mountWidgets("orbit_family_generator", mount);
