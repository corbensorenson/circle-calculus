import { positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["S3S-T0001", "S3S-T0002", "S3S-T0003", "S3S-T0004"];
const DICTIONARY_IDS = ["S3S-0001", "S3S-0002", "S3Q-0001", "S3Q-0002"];
const TOLERANCE = 1e-10;

let spinSvgIdCounter = 0;

function roundCoord(value) {
  return Math.abs(value) < TOLERANCE ? 0 : Math.round(value * 1e12) / 1e12;
}

function quat(r, i, j, k) {
  return { r, i, j, k };
}

function quatNeg(q) {
  return quat(-q.r, -q.i, -q.j, -q.k);
}

function quatConj(q) {
  return quat(q.r, -q.i, -q.j, -q.k);
}

function quatMul(left, right) {
  return quat(
    left.r * right.r - left.i * right.i - left.j * right.j - left.k * right.k,
    left.r * right.i + left.i * right.r + left.j * right.k - left.k * right.j,
    left.r * right.j - left.i * right.k + left.j * right.r + left.k * right.i,
    left.r * right.k + left.i * right.j - left.j * right.i + left.k * right.r,
  );
}

function conjugationAction(q, v) {
  return quatMul(quatMul(q, v), quatConj(q));
}

function coords(q) {
  return [roundCoord(q.r), roundCoord(q.i), roundCoord(q.j), roundCoord(q.k)];
}

function quatClose(left, right) {
  return coords(left).every((value, index) => Math.abs(value - coords(right)[index]) <= TOLERANCE);
}

function formatQuat(q) {
  const [r, i, j, k] = coords(q);
  return `(${r}, ${i}, ${j}, ${k})`;
}

function unitIPhase(period, step) {
  const normalizedStep = ((step % period) + period) % period;
  const angle = (2 * Math.PI * normalizedStep) / period;
  return quat(Math.cos(angle), Math.sin(angle), 0, 0);
}

function orientationDebugRecord(period, step, vector) {
  const q = unitIPhase(period, step);
  const negQ = quatNeg(q);
  const qAction = conjugationAction(q, vector);
  const negAction = conjugationAction(negQ, vector);
  return {
    q,
    negQ,
    vector,
    qAction,
    negAction,
    representativesAreDistinct: !quatClose(q, negQ),
    actionsMatch: quatClose(qAction, negAction),
    spinSignRelated: quatClose(negQ, q) || quatClose(negQ, quatNeg(q)),
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

function renderSpinSvg(record) {
  spinSvgIdCounter += 1;
  const titleId = `spin-sign-title-${spinSvgIdCounter}`;
  const descId = `spin-sign-desc-${spinSvgIdCounter}`;
  const markerId = `spin-sign-arrow-${spinSvgIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: "0 0 620 220",
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Quaternion sign representatives share one conjugation action";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Representative q ${formatQuat(record.q)} and representative -q ${formatQuat(record.negQ)} act on v ${formatQuat(record.vector)} with matching outputs ${record.actionsMatch}.`;
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
    { y: 70, source: "q", value: formatQuat(record.q), output: formatQuat(record.qAction) },
    { y: 150, source: "-q", value: formatQuat(record.negQ), output: formatQuat(record.negAction) },
  ];
  for (const row of rows) {
    svg.appendChild(svgElement("circle", { class: "node-circle selected", cx: 90, cy: row.y, r: 16 }));
    addText(svg, row.source, 90, row.y + 5);
    addText(svg, row.value, 200, row.y + 5);
    svg.appendChild(svgElement("line", {
      x1: 300,
      y1: row.y,
      x2: 390,
      y2: row.y,
      stroke: "#64748b",
      "stroke-width": 3,
      "marker-end": `url(#${markerId})`,
    }));
    addText(svg, "q*v*conj(q)", 345, row.y - 15);
    svg.appendChild(svgElement("circle", { class: "node-circle visited", cx: 480, cy: row.y, r: 16 }));
    addText(svg, record.actionsMatch ? "same" : "diff", 480, row.y + 5);
    addText(svg, row.output, 560, row.y + 5);
  }
  addText(svg, `v = ${formatQuat(record.vector)}`, 310, 205);
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
  title.textContent = "Spin sign theorems";
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

function appendComparisonTable(section, record) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["representative", "raw coordinates", "conjugation output"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const row of [
    ["q", formatQuat(record.q), formatQuat(record.qAction)],
    ["-q", formatQuat(record.negQ), formatQuat(record.negAction)],
  ]) {
    const tr = document.createElement("tr");
    for (const value of row) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  section.appendChild(table);
}

function appendRecord(output, values, theoremById) {
  const vector = quat(0, values.vi, values.vj, values.vk);
  const record = orientationDebugRecord(values.period, values.step, vector);
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Quaternion sign ambiguity record";
  section.appendChild(title);
  section.appendChild(renderSpinSvg(record));

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `phase sample: step ${values.step % values.period} of C_${values.period}`,
    `q: ${formatQuat(record.q)}`,
    `-q: ${formatQuat(record.negQ)}`,
    `vector v: ${formatQuat(record.vector)}`,
    `representatives distinct: ${record.representativesAreDistinct}`,
    `spin sign related: ${record.spinSignRelated}`,
    `conjugation actions match: ${record.actionsMatch}`,
  ].join("\n");
  section.appendChild(data);
  appendComparisonTable(section, record);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this is a bounded quaternion conjugation-action fixture. It is not a complete SO(3), robotics, spinor, or physics verification result.";
  section.appendChild(warning);

  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Quaternion spin sign ambiguity", "Widget: q and -q as action-equivalent representatives");
  const periodInput = addLabeledNumber(panel, "spin-period", "phase period", 8, 1, 64);
  const stepInput = addLabeledNumber(panel, "spin-step", "phase step", 1, 0, 64);
  const viInput = addLabeledNumber(panel, "spin-vector-i", "vector i", 1, -8, 8);
  const vjInput = addLabeledNumber(panel, "spin-vector-j", "vector j", 2, -8, 8);
  const vkInput = addLabeledNumber(panel, "spin-vector-k", "vector k", -1, -8, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const period = positiveInt(periodInput.value, 8, 1, 64);
    const values = {
      period,
      step: positiveInt(stepInput.value, 1, 0, 64) % period,
      vi: positiveInt(viInput.value, 1, -8, 8),
      vj: positiveInt(vjInput.value, 2, -8, 8),
      vk: positiveInt(vkInput.value, -1, -8, 8),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [periodInput, stepInput, viInput, vjInput, vkInput]) {
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

mountWidgets("spin_sign_ambiguity", mount);
