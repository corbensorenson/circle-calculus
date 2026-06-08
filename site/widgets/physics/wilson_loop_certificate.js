import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["PHYS-T0004", "PHYS-T0005", "PHYS-T0046", "PHYS-T0047", "PHYS-T0049", "PHYS-T0052", "PHYS-T0053"];
const DICTIONARY_IDS = ["COMMON-0060", "COMMON-0061", "COMMON-0062", "COMMON-0063"];

function signedInt(value, fallback, min = -99, max = 99) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, parsed));
}

function loopEdges(seed) {
  return [
    { source: "a", target: "b", phase: mod(seed.ab, seed.modulus) },
    { source: "b", target: "c", phase: mod(seed.bc, seed.modulus) },
    { source: "c", target: "a", phase: mod(seed.ca, seed.modulus) },
  ];
}

function sampleGauges(seed) {
  return [
    { a: 0, b: 0, c: 0 },
    { a: 5, b: 13, c: 2 },
    { a: seed.gaugeA, b: seed.gaugeB, c: seed.gaugeC },
  ];
}

function gaugeValue(gauge, vertex, modulus) {
  return mod(gauge[vertex] || 0, modulus);
}

function pathHolonomy(edges, modulus) {
  return mod(edges.reduce((total, edge) => total + edge.phase, 0), modulus);
}

function transformedEdges(edges, gauge, modulus) {
  return edges.map((edge) => ({
    ...edge,
    phase: mod(edge.phase + gaugeValue(gauge, edge.source, modulus) - gaugeValue(gauge, edge.target, modulus), modulus),
  }));
}

function formatEdges(edges) {
  return edges.map((edge) => `${edge.source}->${edge.target}:${edge.phase}`).join(", ");
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
  title.textContent = "Closed-loop theorems";
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

function appendGaugeTable(record, rows, titleText) {
  const title = document.createElement("h4");
  title.textContent = titleText;
  record.appendChild(title);

  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["sample", "gauge values", "transformed edges", "holonomy", "invariant"]) {
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
      row.sample,
      row.gauge,
      row.edges,
      String(row.holonomy),
      row.invariant ? "yes" : "no",
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

function appendRecord(output, seed, theoremById) {
  const edges = loopEdges(seed);
  const holonomy = pathHolonomy(edges, seed.modulus);
  const gaugeSamples = sampleGauges(seed);
  const identityRows = gaugeSamples.map((gauge, index) => ({
    sample: `identity gauge:${index}`,
    gauge: `a=${gaugeValue(gauge, "a", seed.modulus)}, b=${gaugeValue(gauge, "b", seed.modulus)}, c=${gaugeValue(gauge, "c", seed.modulus)}`,
    edges: "(identity loop)",
    holonomy: 0,
    invariant: true,
  }));
  const cycleRows = gaugeSamples.map((gauge, index) => {
    const shifted = transformedEdges(edges, gauge, seed.modulus);
    const shiftedHolonomy = pathHolonomy(shifted, seed.modulus);
    return {
      sample: `cycle gauge:${index}`,
      gauge: `a=${gaugeValue(gauge, "a", seed.modulus)}, b=${gaugeValue(gauge, "b", seed.modulus)}, c=${gaugeValue(gauge, "c", seed.modulus)}`,
      edges: formatEdges(shifted),
      holonomy: shiftedHolonomy,
      invariant: shiftedHolonomy === holonomy,
    };
  });

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Wilson-loop certificate record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `modulus: ${seed.modulus}`,
    `closed loop: a -> b -> c -> a`,
    `normalized edges: ${formatEdges(edges)}`,
    `original holonomy: ${holonomy}`,
    `identity gauge-shifted holonomy: 0`,
    `cycle gauge-invariant under all sampled gauges: ${cycleRows.every((row) => row.invariant)}`,
    `certificate theorem ids: ${THEOREM_IDS.join(", ")}`,
  ].join("\n");
  record.appendChild(data);

  appendGaugeTable(record, identityRows, "Identity-loop samples (PHYS-T0052)");
  appendGaugeTable(record, cycleRows, "Two-path cycle samples (PHYS-T0053)");

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget checks finite identity-loop and two-path-cycle certificates across sampled vertex gauges. It is not continuum gauge theory, electromagnetism, quantum field theory, Berry phase, or a physics prediction.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Wilson-loop certificate", "Widget: sampled finite gauge invariance only");
  const modulusInput = addLabeledNumber(panel, "phys-wilson-modulus", "modulus", 19, 1, 97);
  const abInput = addLabeledNumber(panel, "phys-wilson-ab", "a->b phase", 3, -99, 99);
  const bcInput = addLabeledNumber(panel, "phys-wilson-bc", "b->c phase", 7, -99, 99);
  const caInput = addLabeledNumber(panel, "phys-wilson-ca", "c->a phase", 11, -99, 99);
  const gaugeAInput = addLabeledNumber(panel, "phys-wilson-ga", "sample g(a)", 21, -99, 99);
  const gaugeBInput = addLabeledNumber(panel, "phys-wilson-gb", "sample g(b)", -4, -99, 99);
  const gaugeCInput = addLabeledNumber(panel, "phys-wilson-gc", "sample g(c)", 8, -99, 99);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const seed = {
      modulus: positiveInt(modulusInput.value, 19, 1, 97),
      ab: signedInt(abInput.value, 3),
      bc: signedInt(bcInput.value, 7),
      ca: signedInt(caInput.value, 11),
      gaugeA: signedInt(gaugeAInput.value, 21),
      gaugeB: signedInt(gaugeBInput.value, -4),
      gaugeC: signedInt(gaugeCInput.value, 8),
    };
    clear(output);
    appendRecord(output, seed, theoremById);
  }

  for (const input of [modulusInput, abInput, bcInput, caInput, gaugeAInput, gaugeBInput, gaugeCInput]) {
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

mountWidgets("wilson_loop_certificate", mount);
