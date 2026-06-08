import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["PHYS-T0004", "PHYS-T0005", "PHYS-T0012", "PHYS-T0045", "PHYS-T0047"];
const DICTIONARY_IDS = ["COMMON-0060", "COMMON-0061", "COMMON-0062", "COMMON-0063"];

let svgIdCounter = 0;

function signedInt(value, fallback, min = -99, max = 99) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, parsed));
}

function plaquetteEdges(seed) {
  return [
    { id: "bottom", source: "v00", target: "v10", phase: seed.bottom },
    { id: "right", source: "v10", target: "v11", phase: seed.right },
    { id: "top", source: "v11", target: "v01", phase: seed.top },
    { id: "left", source: "v01", target: "v00", phase: seed.left },
  ];
}

function gaugeValue(seed, vertex) {
  return mod(seed.gauge[vertex] || 0, seed.modulus);
}

function normalizedEdges(seed) {
  return plaquetteEdges(seed).map((edge) => ({
    ...edge,
    phase: mod(edge.phase, seed.modulus),
  }));
}

function transformedEdges(seed) {
  return plaquetteEdges(seed).map((edge) => {
    const transformed = edge.phase + gaugeValue(seed, edge.source) - gaugeValue(seed, edge.target);
    return {
      ...edge,
      phase: mod(transformed, seed.modulus),
    };
  });
}

function pathHolonomy(edges, modulus) {
  return mod(edges.reduce((total, edge) => total + edge.phase, 0), modulus);
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function renderPlaquetteSvg(seed, transformed) {
  svgIdCounter += 1;
  const titleId = `finite-gauge-loop-title-${svgIdCounter}`;
  const descId = `finite-gauge-loop-desc-${svgIdCounter}`;
  const size = 380;
  const positions = {
    v00: [78, 284],
    v10: [284, 284],
    v11: [284, 78],
    v01: [78, 78],
  };
  const originalEdges = normalizedEdges(seed);
  const shiftedEdges = transformedEdges(seed);
  const displayEdges = transformed ? shiftedEdges : originalEdges;
  const label = transformed ? "transformed" : "original";
  const holonomy = pathHolonomy(displayEdges, seed.modulus);
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${size} ${size}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = `${label} finite plaquette loop`;
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `${label} edge phases around a closed square plaquette modulo ${seed.modulus}; holonomy ${holonomy}.`;
  svg.append(title, desc);

  const labelOffsets = {
    bottom: [0, 28],
    right: [36, 0],
    top: [0, -18],
    left: [-42, 0],
  };
  for (const edge of displayEdges) {
    const [x1, y1] = positions[edge.source];
    const [x2, y2] = positions[edge.target];
    const line = svgElement("line", {
      x1,
      y1,
      x2,
      y2,
      stroke: transformed ? "#8a4d00" : "#1357a6",
      "stroke-width": 4,
      "stroke-linecap": "round",
    });
    const [dx, dy] = labelOffsets[edge.id];
    const text = svgElement("text", {
      class: "node-label",
      x: (x1 + x2) / 2 + dx,
      y: (y1 + y2) / 2 + dy,
    });
    text.textContent = `${edge.id}: ${edge.phase}`;
    svg.append(line, text);
  }

  for (const [vertex, [x, y]] of Object.entries(positions)) {
    const point = svgElement("circle", {
      class: "node-circle selected",
      cx: x,
      cy: y,
      r: 11,
    });
    const text = svgElement("text", {
      class: "node-label",
      x,
      y: y + 29,
    });
    text.textContent = `${vertex} g=${gaugeValue(seed, vertex)}`;
    svg.append(point, text);
  }
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
  title.textContent = "Theorems";
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

function appendRecord(output, seed, theoremById) {
  const original = normalizedEdges(seed);
  const transformed = transformedEdges(seed);
  const originalHolonomy = pathHolonomy(original, seed.modulus);
  const transformedHolonomy = pathHolonomy(transformed, seed.modulus);
  const endpointShift = mod(gaugeValue(seed, "v00") - gaugeValue(seed, "v00"), seed.modulus);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Finite Wilson-loop record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `modulus: ${seed.modulus}`,
    `original normalized phases: ${original.map((edge) => `${edge.id}=${edge.phase}`).join(", ")}`,
    `original holonomy: ${originalHolonomy}`,
    `vertex gauge values: v00=${gaugeValue(seed, "v00")}, v10=${gaugeValue(seed, "v10")}, v11=${gaugeValue(seed, "v11")}, v01=${gaugeValue(seed, "v01")}`,
    `transformed phases: ${transformed.map((edge) => `${edge.id}=${edge.phase}`).join(", ")}`,
    `transformed holonomy: ${transformedHolonomy}`,
    `closed path: yes, v00 -> v10 -> v11 -> v01 -> v00`,
    `endpoint shift g(source)-g(target): ${endpointShift}`,
    `gauge-invariant finite holonomy: ${originalHolonomy === transformedHolonomy}`,
    "boundary: widget output is finite bookkeeping intuition, not a proof artifact or physics prediction.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Finite gauge-loop holonomy", "Widget: finite plaquette bookkeeping only");
  const modulusInput = addLabeledNumber(panel, "phys-modulus", "modulus", 23, 1, 97);
  const bottomInput = addLabeledNumber(panel, "phys-bottom", "bottom phase", 2, -99, 99);
  const rightInput = addLabeledNumber(panel, "phys-right", "right phase", 5, -99, 99);
  const topInput = addLabeledNumber(panel, "phys-top", "top phase", -7, -99, 99);
  const leftInput = addLabeledNumber(panel, "phys-left", "left phase", 4, -99, 99);
  const g00Input = addLabeledNumber(panel, "phys-g00", "g(v00)", 3, -99, 99);
  const g10Input = addLabeledNumber(panel, "phys-g10", "g(v10)", 9, -99, 99);
  const g11Input = addLabeledNumber(panel, "phys-g11", "g(v11)", 1, -99, 99);
  const g01Input = addLabeledNumber(panel, "phys-g01", "g(v01)", 17, -99, 99);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const seed = {
      modulus: positiveInt(modulusInput.value, 23, 1, 97),
      bottom: signedInt(bottomInput.value, 2),
      right: signedInt(rightInput.value, 5),
      top: signedInt(topInput.value, -7),
      left: signedInt(leftInput.value, 4),
      gauge: {
        v00: signedInt(g00Input.value, 3),
        v10: signedInt(g10Input.value, 9),
        v11: signedInt(g11Input.value, 1),
        v01: signedInt(g01Input.value, 17),
      },
    };
    clear(output);
    output.appendChild(renderPlaquetteSvg(seed, false));
    output.appendChild(renderPlaquetteSvg(seed, true));
    appendRecord(output, seed, theoremById);
  }

  for (const input of [
    modulusInput,
    bottomInput,
    rightInput,
    topInput,
    leftInput,
    g00Input,
    g10Input,
    g11Input,
    g01Input,
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

mountWidgets("finite_gauge_loop_holonomy", mount);
