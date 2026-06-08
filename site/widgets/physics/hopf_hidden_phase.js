import { positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["S3H-T0001", "S3H-T0002", "S3H-T0003", "S3H-T0004", "S3H-T0005", "S3H-T0006"];
const DICTIONARY_IDS = ["S3H-0001", "S3H-0002", "S3H-W0001"];
const TOLERANCE = 1e-10;

let hopfSvgIdCounter = 0;

function roundCoord(value) {
  return Math.abs(value) < TOLERANCE ? 0 : Math.round(value * 1e12) / 1e12;
}

function complex(re, im) {
  return { re, im };
}

function complexMul(left, right) {
  return complex(left.re * right.re - left.im * right.im, left.re * right.im + left.im * right.re);
}

function complexConj(value) {
  return complex(value.re, -value.im);
}

function complexAbsSq(value) {
  return value.re * value.re + value.im * value.im;
}

function pairNormSq(pair) {
  return complexAbsSq(pair.z0) + complexAbsSq(pair.z1);
}

function normalizePair(pair) {
  const normSq = pairNormSq(pair);
  if (normSq === 0) return null;
  const scale = Math.sqrt(normSq);
  return {
    z0: complex(pair.z0.re / scale, pair.z0.im / scale),
    z1: complex(pair.z1.re / scale, pair.z1.im / scale),
  };
}

function unitPhase(period, step) {
  const angle = (2 * Math.PI * (((step % period) + period) % period)) / period;
  return complex(Math.cos(angle), Math.sin(angle));
}

function phaseRotate(pair, phase) {
  return {
    z0: complexMul(phase, pair.z0),
    z1: complexMul(phase, pair.z1),
  };
}

function hopfMap(pair) {
  const product = complexMul(pair.z0, complexConj(pair.z1));
  return {
    x: 2 * product.re,
    y: 2 * product.im,
    z: complexAbsSq(pair.z0) - complexAbsSq(pair.z1),
  };
}

function sphereNormSq(point) {
  return point.x * point.x + point.y * point.y + point.z * point.z;
}

function pointClose(left, right) {
  return ["x", "y", "z"].every((axis) => Math.abs(left[axis] - right[axis]) <= TOLERANCE);
}

function formatComplex(value) {
  return `(${roundCoord(value.re)}, ${roundCoord(value.im)})`;
}

function formatPoint(point) {
  return `(${roundCoord(point.x)}, ${roundCoord(point.y)}, ${roundCoord(point.z)})`;
}

function hopfRecord(values) {
  const normalized = normalizePair({
    z0: complex(values.z0re, values.z0im),
    z1: complex(values.z1re, values.z1im),
  });
  if (!normalized) return null;
  const phase = unitPhase(values.period, values.step);
  const rotated = phaseRotate(normalized, phase);
  const base = hopfMap(normalized);
  const rotatedBase = hopfMap(rotated);
  return {
    phase,
    normalized,
    rotated,
    base,
    rotatedBase,
    pairNormSq: pairNormSq(normalized),
    rotatedPairNormSq: pairNormSq(rotated),
    baseNormSq: sphereNormSq(base),
    rotatedBaseNormSq: sphereNormSq(rotatedBase),
    basePointsMatch: pointClose(base, rotatedBase),
  };
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function addText(svg, text, x, y, className = "node-label") {
  const label = svgElement("text", { class: className, x, y });
  label.textContent = text;
  svg.appendChild(label);
}

function renderHopfSvg(record) {
  hopfSvgIdCounter += 1;
  const titleId = `hopf-phase-title-${hopfSvgIdCounter}`;
  const descId = `hopf-phase-desc-${hopfSvgIdCounter}`;
  const markerId = `hopf-phase-arrow-${hopfSvgIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: "0 0 640 240",
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Hopf hidden phase preserves the visible base point";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `A normalized S3 pair and its shared phase rotation map to matching visible base points: ${record.basePointsMatch}.`;
  svg.append(title, desc);

  const defs = svgElement("defs");
  const marker = svgElement("marker", {
    id: markerId,
    viewBox: "0 0 10 10",
    refX: 9,
    refY: 5,
    markerWidth: 6,
    markerHeight: 6,
    orient: "auto-start-reverse",
  });
  marker.appendChild(svgElement("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "#64748b" }));
  defs.appendChild(marker);
  svg.appendChild(defs);

  const rows = [
    {
      y: 80,
      label: "pair",
      pairText: "normalized S3 pair",
      baseText: "visible base",
    },
    {
      y: 165,
      label: "phase pair",
      pairText: "phase-rotated pair",
      baseText: "same base",
    },
  ];
  for (const row of rows) {
    svg.appendChild(svgElement("circle", { class: "node-circle selected", cx: 86, cy: row.y, r: 16 }));
    addText(svg, row.label, 86, row.y + 5);
    addText(svg, row.pairText, 230, row.y + 5);
    svg.appendChild(svgElement("line", {
      x1: 335,
      y1: row.y,
      x2: 420,
      y2: row.y,
      stroke: "#64748b",
      "stroke-width": 3,
      "marker-end": `url(#${markerId})`,
    }));
    addText(svg, "Hopf map", 377, row.y - 15);
    svg.appendChild(svgElement("circle", { class: "node-circle visited", cx: 505, cy: row.y, r: 16 }));
    addText(svg, record.basePointsMatch ? "same" : "diff", 505, row.y + 5);
    addText(svg, row.baseText, 585, row.y + 5);
  }
  addText(svg, `phase = ${formatComplex(record.phase)}`, 320, 220);
  return svg;
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
  title.textContent = "Hopf phase theorems";
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

function appendTable(section, record) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["object", "norm", "visible base"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  for (const row of [
    ["normalized pair", roundCoord(record.pairNormSq), formatPoint(record.base)],
    ["phase-rotated pair", roundCoord(record.rotatedPairNormSq), formatPoint(record.rotatedBase)],
    ["base norm", roundCoord(record.baseNormSq), `rotated base norm ${roundCoord(record.rotatedBaseNormSq)}`],
  ]) {
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

function appendRecord(output, values, theoremById) {
  const record = hopfRecord(values);
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Hopf hidden phase record";
  section.appendChild(title);
  if (!record) {
    const warning = document.createElement("p");
    warning.className = "warning-box";
    warning.textContent = "The zero complex pair cannot be normalized. Choose at least one nonzero input coordinate.";
    section.appendChild(warning);
    output.appendChild(section);
    return;
  }

  section.appendChild(renderHopfSvg(record));
  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `phase sample: step ${values.step % values.period} of C_${values.period}`,
    `unit phase: ${formatComplex(record.phase)}`,
    `normalized pair: ${formatComplex(record.normalized.z0)}, ${formatComplex(record.normalized.z1)}`,
    `phase-rotated pair: ${formatComplex(record.rotated.z0)}, ${formatComplex(record.rotated.z1)}`,
    `base point: ${formatPoint(record.base)}`,
    `rotated base point: ${formatPoint(record.rotatedBase)}`,
    `base points match: ${record.basePointsMatch}`,
  ].join("\n");
  section.appendChild(data);
  appendTable(section, record);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this is a bounded coordinate Hopf phase fixture. It is not Berry phase, a full fiber-bundle formalization, or a physics prediction.";
  section.appendChild(warning);

  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Hopf hidden phase", "Widget: shared phase changes fiber coordinates while preserving the visible base");
  const periodInput = addLabeledNumber(panel, "hopf-period", "phase period", 12, 1, 64);
  const stepInput = addLabeledNumber(panel, "hopf-step", "phase step", 2, 0, 64);
  const z0reInput = addLabeledNumber(panel, "hopf-z0-re", "z0 real", 1, -8, 8);
  const z0imInput = addLabeledNumber(panel, "hopf-z0-im", "z0 imag", -1, -8, 8);
  const z1reInput = addLabeledNumber(panel, "hopf-z1-re", "z1 real", 2, -8, 8);
  const z1imInput = addLabeledNumber(panel, "hopf-z1-im", "z1 imag", 1, -8, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const period = positiveInt(periodInput.value, 12, 1, 64);
    const values = {
      period,
      step: positiveInt(stepInput.value, 2, 0, 64) % period,
      z0re: positiveInt(z0reInput.value, 1, -8, 8),
      z0im: positiveInt(z0imInput.value, -1, -8, 8),
      z1re: positiveInt(z1reInput.value, 2, -8, 8),
      z1im: positiveInt(z1imInput.value, 1, -8, 8),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [periodInput, stepInput, z0reInput, z0imInput, z1reInput, z1imInput]) {
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

mountWidgets("hopf_hidden_phase", mount);
