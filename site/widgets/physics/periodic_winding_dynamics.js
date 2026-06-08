import { gcd, mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["CC-T0005", "CC-T0009", "CC-T0011"];
const DICTIONARY_IDS = ["COMMON-0060", "COMMON-0063", "COMMON-0036", "COMMON-0038", "CC-0301"];

let diagramIdCounter = 0;

function finitePeriodicDynamics(modulus, stride, steps) {
  const normalizedStride = mod(stride, modulus);
  const closurePeriod = modulus / gcd(modulus, normalizedStride);
  const totalMotion = stride * steps;
  const phase = mod(totalMotion, modulus);
  const winding = Math.floor(totalMotion / modulus);
  const residue = mod(totalMotion, modulus);
  const phaseSequence = Array.from({ length: steps + 1 }, (_, step) => mod(stride * step, modulus));
  return {
    modulus,
    stride,
    steps,
    phase,
    winding,
    residue,
    closurePeriod,
    closed: steps % closurePeriod === 0,
    phaseSequence,
  };
}

function finiteDefectWinding(sectors, turns, orientation) {
  const totalSteps = turns * sectors;
  const phasePath = Array.from(
    { length: totalSteps + 1 },
    (_, step) => mod(orientation * step, sectors),
  );
  const netSteps = orientation * totalSteps;
  return {
    sectors,
    turns,
    orientation,
    phasePath,
    netSteps,
    winding: netSteps / sectors,
    closed: phasePath[0] === phasePath[phasePath.length - 1],
  };
}

function addLabeledSelect(parent, id, labelText, options) {
  const wrapper = document.createElement("label");
  wrapper.className = "widget-control";
  wrapper.htmlFor = id;
  const label = document.createElement("span");
  label.textContent = labelText;
  const select = document.createElement("select");
  select.id = id;
  for (const option of options) {
    const node = document.createElement("option");
    node.value = option.value;
    node.textContent = option.label;
    if (option.selected) node.selected = true;
    select.appendChild(node);
  }
  wrapper.append(label, select);
  parent.appendChild(wrapper);
  return select;
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function renderPhaseClock(record) {
  diagramIdCounter += 1;
  const width = 420;
  const height = 320;
  const cx = 210;
  const cy = 155;
  const radius = 105;
  const titleId = `periodic-dynamics-title-${diagramIdCounter}`;
  const descId = `periodic-dynamics-desc-${diagramIdCounter}`;
  const visited = new Set(record.phaseSequence);
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Finite stroboscopic phase clock";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `A C_${record.modulus} phase clock after ${record.steps} steps of stride ${record.stride}; current phase ${record.phase}.`;
  svg.append(title, desc);

  for (let index = 0; index < record.modulus; index += 1) {
    const angle = -Math.PI / 2 + (2 * Math.PI * index) / record.modulus;
    const x = cx + radius * Math.cos(angle);
    const y = cy + radius * Math.sin(angle);
    const classes = [
      "node-circle",
      visited.has(index) ? "visited" : "",
      index === record.phase ? "selected" : "",
    ].filter(Boolean).join(" ");
    const point = svgElement("circle", { class: classes, cx: x, cy: y, r: 11 });
    const label = svgElement("text", { class: "node-label", x, y: y + 4 });
    label.textContent = String(index);
    svg.append(point, label);
  }
  const center = svgElement("text", { class: "node-label", x: cx, y: cy });
  center.textContent = record.closed ? "closed" : "open";
  svg.appendChild(center);
  return svg;
}

function renderDefectClock(record) {
  diagramIdCounter += 1;
  const width = 420;
  const height = 300;
  const cx = 210;
  const cy = 145;
  const radius = 96;
  const titleId = `defect-winding-title-${diagramIdCounter}`;
  const descId = `defect-winding-desc-${diagramIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Finite marked-defect winding toy";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `A ${record.sectors}-sector phase path with winding ${record.winding}.`;
  svg.append(title, desc);

  const defect = svgElement("circle", { cx, cy, r: 16, fill: "#fff4d6", stroke: "#b45309", "stroke-width": 2 });
  const defectLabel = svgElement("text", { class: "node-label", x: cx, y: cy + 4 });
  defectLabel.textContent = "mark";
  svg.append(defect, defectLabel);

  for (let index = 0; index < record.sectors; index += 1) {
    const angle = -Math.PI / 2 + (2 * Math.PI * index) / record.sectors;
    const x = cx + radius * Math.cos(angle);
    const y = cy + radius * Math.sin(angle);
    const point = svgElement("circle", { class: "node-circle visited", cx: x, cy: y, r: 11 });
    const label = svgElement("text", { class: "node-label", x, y: y + 4 });
    label.textContent = String(index);
    svg.append(point, label);
  }
  const orientation = svgElement("text", { class: "node-label", x: cx, y: height - 28 });
  orientation.textContent = record.orientation === 1 ? "orientation: +1" : "orientation: -1";
  svg.appendChild(orientation);
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
  title.textContent = "Finite support theorems";
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

function formatSequence(values, limit = 20) {
  const shown = values.slice(0, limit).join(", ");
  return values.length > limit ? `${shown}, ...` : shown;
}

function appendRecord(output, dynamics, defect, theoremById) {
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Finite periodic dynamics and winding record";
  section.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    "target id: P7-PHYS-004",
    `modulus: ${dynamics.modulus}`,
    `stride: ${dynamics.stride}`,
    `steps: ${dynamics.steps}`,
    `total motion: ${dynamics.stride * dynamics.steps}`,
    `lifted winding/residue: (${dynamics.winding}, ${dynamics.residue})`,
    `closure period n/gcd(n,k): ${dynamics.closurePeriod}`,
    `closed at chosen step count: ${dynamics.closed ? "yes" : "no"}`,
    `phase sequence: ${formatSequence(dynamics.phaseSequence)}`,
    `defect sectors/turns: ${defect.sectors}/${defect.turns}`,
    `defect phase path: ${formatSequence(defect.phasePath)}`,
    `defect net steps: ${defect.netSteps}`,
    `defect winding: ${defect.winding}`,
    `defect loop closed: ${defect.closed ? "yes" : "no"}`,
  ].join("\n");
  section.appendChild(data);
  section.appendChild(renderPhaseClock(dynamics));
  section.appendChild(renderDefectClock(defect));

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this is finite phase, winding, residue, and closure bookkeeping. It is not Floquet theory, action-angle mechanics, a continuum vortex, Kosterlitz-Thouless physics, or a material prediction.";
  section.appendChild(warning);

  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Periodic winding dynamics", "Widget: finite stroboscopic phase and defect-winding toy");
  const modulusInput = addLabeledNumber(panel, "physics-periodic-modulus", "phase modulus", 12, 1, 32);
  const strideInput = addLabeledNumber(panel, "physics-periodic-stride", "stride", 5, 0, 64);
  const stepsInput = addLabeledNumber(panel, "physics-periodic-steps", "steps", 7, 0, 64);
  const sectorsInput = addLabeledNumber(panel, "physics-defect-sectors", "defect sectors", 4, 1, 16);
  const turnsInput = addLabeledNumber(panel, "physics-defect-turns", "defect turns", 2, 0, 8);
  const orientationInput = addLabeledSelect(panel, "physics-defect-orientation", "orientation", [
    { value: "1", label: "+1", selected: true },
    { value: "-1", label: "-1" },
  ]);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const dynamics = finitePeriodicDynamics(
      positiveInt(modulusInput.value, 12, 1, 32),
      positiveInt(strideInput.value, 5, 0, 64),
      positiveInt(stepsInput.value, 7, 0, 64),
    );
    const defect = finiteDefectWinding(
      positiveInt(sectorsInput.value, 4, 1, 16),
      positiveInt(turnsInput.value, 2, 0, 8),
      Number.parseInt(orientationInput.value, 10) === -1 ? -1 : 1,
    );
    clear(output);
    appendRecord(output, dynamics, defect, theoremById);
  }

  for (const input of [modulusInput, strideInput, stepsInput, sectorsInput, turnsInput, orientationInput]) {
    input.addEventListener("input", render);
    input.addEventListener("change", render);
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

mountWidgets("periodic_winding_dynamics", mount);
