import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = [
  "PHYS-T0001",
  "PHYS-T0002",
  "PHYS-T0003",
  "PHYS-T0006",
  "PHYS-T0007",
  "PHYS-T0039",
  "PHYS-T0050",
  "PHYS-T0051",
];
const DICTIONARY_IDS = ["COMMON-0060", "COMMON-0061", "COMMON-0063"];

let pathSvgIdCounter = 0;

function normalizePhase(phase, modulus) {
  return mod(phase, modulus);
}

function edge(source, target, phase, modulus) {
  return {
    source,
    target,
    phase: normalizePhase(phase, modulus),
  };
}

function pathHolonomy(edges, modulus) {
  return mod(edges.reduce((total, item) => total + item.phase, 0), modulus);
}

function reversePath(edges, modulus) {
  return edges
    .slice()
    .reverse()
    .map((item) => edge(item.target, item.source, -item.phase, modulus));
}

function gaugeValue(gauge, vertex, modulus) {
  return normalizePhase(gauge[vertex] || 0, modulus);
}

function gaugeTransformEdge(item, gauge, modulus) {
  return edge(
    item.source,
    item.target,
    item.phase + gaugeValue(gauge, item.source, modulus) - gaugeValue(gauge, item.target, modulus),
    modulus,
  );
}

function formatEdges(edges) {
  return edges.map((item) => `${item.source}->${item.target}:${item.phase}`).join(", ");
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function renderPathSvg({ edges, modulus, title }) {
  pathSvgIdCounter += 1;
  const titleId = `path-algebra-title-${pathSvgIdCounter}`;
  const descId = `path-algebra-desc-${pathSvgIdCounter}`;
  const width = 560;
  const height = 160;
  const y = 70;
  const nodeXs = new Map([
    ["a", 54],
    ["b", 204],
    ["c", 354],
    ["d", 504],
  ]);
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const titleNode = svgElement("title", { id: titleId });
  titleNode.textContent = title;
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Finite path with edges ${formatEdges(edges)} modulo ${modulus}.`;
  svg.append(titleNode, desc);

  for (const item of edges) {
    const x1 = nodeXs.get(item.source);
    const x2 = nodeXs.get(item.target);
    if (x1 === undefined || x2 === undefined) continue;
    svg.appendChild(svgElement("line", {
      x1,
      y1: y,
      x2,
      y2: y,
      stroke: "#64748b",
      "stroke-width": 3,
      "marker-end": "url(#path-arrow)",
    }));
    const label = svgElement("text", {
      class: "node-label",
      x: (x1 + x2) / 2,
      y: y - 20,
    });
    label.textContent = `${item.phase} mod ${modulus}`;
    svg.appendChild(label);
  }

  const defs = svgElement("defs");
  const marker = svgElement("marker", {
    id: "path-arrow",
    viewBox: "0 0 10 10",
    refX: 9,
    refY: 5,
    markerWidth: 6,
    markerHeight: 6,
    orient: "auto-start-reverse",
  });
  marker.appendChild(svgElement("path", {
    d: "M 0 0 L 10 5 L 0 10 z",
    fill: "#64748b",
  }));
  defs.appendChild(marker);
  svg.insertBefore(defs, svg.firstChild);

  for (const [vertex, x] of nodeXs.entries()) {
    svg.appendChild(svgElement("circle", {
      class: "node-circle selected",
      cx: x,
      cy: y,
      r: 11,
    }));
    const label = svgElement("text", {
      class: "node-label",
      x,
      y: y + 34,
    });
    label.textContent = vertex;
    svg.appendChild(label);
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
  title.textContent = "Finite path theorems";
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

function appendRecord(output, values, theoremById) {
  const left = [
    edge("a", "b", values.ab, values.modulus),
    edge("b", "c", values.bc, values.modulus),
  ];
  const right = [edge("c", "d", values.cd, values.modulus)];
  const combined = [...left, ...right];
  const reversed = reversePath(combined, values.modulus);
  const closed = [...combined, ...reversed];
  const gauge = {
    a: values.ga,
    b: values.gb,
    c: values.gc,
    d: values.gd,
  };
  const transformed = combined.map((item) => gaugeTransformEdge(item, gauge, values.modulus));

  const leftHolonomy = pathHolonomy(left, values.modulus);
  const rightHolonomy = pathHolonomy(right, values.modulus);
  const combinedHolonomy = pathHolonomy(combined, values.modulus);
  const reversedHolonomy = pathHolonomy(reversed, values.modulus);
  const closedHolonomy = pathHolonomy(closed, values.modulus);
  const transformedHolonomy = pathHolonomy(transformed, values.modulus);
  const endpointPrediction = mod(
    combinedHolonomy + gaugeValue(gauge, "a", values.modulus) - gaugeValue(gauge, "d", values.modulus),
    values.modulus,
  );

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Finite path algebra record";
  record.appendChild(title);
  record.appendChild(renderPathSvg({
    edges: combined,
    modulus: values.modulus,
    title: "Finite composable gauge path",
  }));

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `left path: ${formatEdges(left)}`,
    `right path: ${formatEdges(right)}`,
    `concat path: ${formatEdges(combined)}`,
    `left holonomy: ${leftHolonomy}`,
    `right holonomy: ${rightHolonomy}`,
    `concat holonomy: ${combinedHolonomy}`,
    `concat check left + right mod n: ${mod(leftHolonomy + rightHolonomy, values.modulus)}`,
    `reverse path: ${formatEdges(reversed)}`,
    `reverse holonomy: ${reversedHolonomy}`,
    `reverse check -concat mod n: ${mod(-combinedHolonomy, values.modulus)}`,
    `concat with reverse closed: yes`,
    `closed holonomy: ${closedHolonomy}`,
    `gauge values: a=${gaugeValue(gauge, "a", values.modulus)}, b=${gaugeValue(gauge, "b", values.modulus)}, c=${gaugeValue(gauge, "c", values.modulus)}, d=${gaugeValue(gauge, "d", values.modulus)}`,
    `transformed path: ${formatEdges(transformed)}`,
    `transformed holonomy: ${transformedHolonomy}`,
    `endpoint prediction holonomy + g(a) - g(d): ${endpointPrediction}`,
    `endpoint check: ${transformedHolonomy === endpointPrediction}`,
  ].join("\n");
  record.appendChild(data);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget is finite path algebra over modular phases. It is not continuum electromagnetism, QFT, Yang-Mills theory, Berry phase, or a physics prediction.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Finite path algebra", "Widget: path concatenation, reversal, and endpoint gauge shift");
  const modulusInput = addLabeledNumber(panel, "phys-path-modulus", "modulus", 17, 1, 97);
  const abInput = addLabeledNumber(panel, "phys-path-ab", "phase a->b", 6, -200, 200);
  const bcInput = addLabeledNumber(panel, "phys-path-bc", "phase b->c", 2, -200, 200);
  const cdInput = addLabeledNumber(panel, "phys-path-cd", "phase c->d", 9, -200, 200);
  const gaInput = addLabeledNumber(panel, "phys-path-ga", "gauge a", 4, -200, 200);
  const gbInput = addLabeledNumber(panel, "phys-path-gb", "gauge b", 9, -200, 200);
  const gcInput = addLabeledNumber(panel, "phys-path-gc", "gauge c", 12, -200, 200);
  const gdInput = addLabeledNumber(panel, "phys-path-gd", "gauge d", 3, -200, 200);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      modulus: positiveInt(modulusInput.value, 17, 1, 97),
      ab: positiveInt(abInput.value, 6, -200, 200),
      bc: positiveInt(bcInput.value, 2, -200, 200),
      cd: positiveInt(cdInput.value, 9, -200, 200),
      ga: positiveInt(gaInput.value, 4, -200, 200),
      gb: positiveInt(gbInput.value, 9, -200, 200),
      gc: positiveInt(gcInput.value, 12, -200, 200),
      gd: positiveInt(gdInput.value, 3, -200, 200),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [modulusInput, abInput, bcInput, cdInput, gaInput, gbInput, gcInput, gdInput]) {
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

mountWidgets("finite_path_algebra", mount);
