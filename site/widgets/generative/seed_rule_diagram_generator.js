import { addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const EXAMPLES = {
  finite_circle_diagram: {
    label: "Finite circle diagram",
    seed: { n: 8 },
    theoremIds: ["CC-T0001", "CC-T0002", "GEN-T0017", "GEN-T0019"],
    dictionaryIds: ["CC-0001", "CC-0002", "COMMON-0064", "COMMON-0066"],
    rules: [
      { ruleId: "enumerate_nodes", parameters: { start: 0, stop: 8 } },
      { ruleId: "connect_successor_mod_n", parameters: {} },
    ],
    iterationSchedule: "nodes i=0..n-1; edges i -> (i+1) mod n",
    closureCondition: "successor edge from n-1 returns to node 0",
    note: "Generated diagram fixture only; not a formal proof or minimality theorem.",
  },
  physics_loop_diagram: {
    label: "Finite physics-loop diagram",
    seed: { modulus: 7, bottom: 2, right: 3, top: -1, left: 5 },
    theoremIds: ["PHYS-T0005", "PHYS-T0012", "GEN-T0017", "GEN-T0019"],
    dictionaryIds: ["COMMON-0060", "COMMON-0061", "COMMON-0062", "COMMON-0063", "COMMON-0064", "COMMON-0066"],
    rules: [
      { ruleId: "normalize_link_phases_mod_n", parameters: {} },
      { ruleId: "connect_square_plaquette", parameters: {} },
      { ruleId: "sum_closed_loop_holonomy", parameters: {} },
    ],
    iterationSchedule: "v00 -> v10 -> v11 -> v01 -> v00",
    closureCondition: "fourth edge returns to v00, so the finite loop is closed",
    note: "Generated finite physics-loop diagram fixture only; not a formal proof, physics claim, or minimality theorem.",
  },
};

function mod(value, n) {
  return ((value % n) + n) % n;
}

function finiteCircleDiagram(n) {
  return {
    nodes: Array.from({ length: n }, (_, node) => ({ id: node, label: `${node} mod ${n}` })),
    edges: Array.from({ length: n }, (_, node) => ({
      source: node,
      target: (node + 1) % n,
      rule: "successor_mod_n",
    })),
  };
}

function physicsLoopDiagram(seed) {
  const modulus = seed.modulus;
  const phases = [
    ["v00", "v10", seed.bottom],
    ["v10", "v11", seed.right],
    ["v11", "v01", seed.top],
    ["v01", "v00", seed.left],
  ];
  const edges = phases.map(([source, target, phase]) => {
    const normalized = mod(Number(phase), modulus);
    return {
      source,
      target,
      phase: normalized,
      label: `${normalized} mod ${modulus}`,
      rule: "plaquette_edge_phase",
    };
  });
  return {
    modulus,
    vertices: ["v00", "v10", "v11", "v01"].map((id) => ({ id })),
    edges,
    closed: true,
    holonomy: mod(edges.reduce((total, edge) => total + edge.phase, 0), modulus),
  };
}

function generatedObjectFor(exampleId) {
  const example = EXAMPLES[exampleId];
  if (exampleId === "finite_circle_diagram") return finiteCircleDiagram(example.seed.n);
  return physicsLoopDiagram(example.seed);
}

function addLabeledSelect(panel, id, label, options) {
  const wrapper = document.createElement("label");
  wrapper.setAttribute("for", id);
  wrapper.textContent = label;
  const select = document.createElement("select");
  select.id = id;
  select.setAttribute("aria-label", label);
  for (const option of options) {
    const element = document.createElement("option");
    element.value = option.value;
    element.textContent = option.label;
    select.appendChild(element);
  }
  wrapper.appendChild(select);
  panel.appendChild(wrapper);
  return select;
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function renderPhysicsLoopSvg(diagram) {
  const size = 360;
  const titleId = "physics-loop-title";
  const descId = "physics-loop-desc";
  const positions = {
    v00: [80, 260],
    v10: [260, 260],
    v11: [260, 80],
    v01: [80, 80],
  };
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${size} ${size}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Finite plaquette loop diagram";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Closed four-edge loop modulo ${diagram.modulus} with holonomy ${diagram.holonomy}.`;
  svg.append(title, desc);

  const labelOffsets = [[0, 24], [24, 0], [0, -18], [-38, 0]];
  diagram.edges.forEach((edge, index) => {
    const [x1, y1] = positions[edge.source];
    const [x2, y2] = positions[edge.target];
    const line = svgElement("line", {
      x1,
      y1,
      x2,
      y2,
      stroke: "#1357a6",
      "stroke-width": 4,
      "stroke-linecap": "round",
    });
    svg.appendChild(line);
    const [dx, dy] = labelOffsets[index];
    const text = svgElement("text", {
      class: "node-label",
      x: (x1 + x2) / 2 + dx,
      y: (y1 + y2) / 2 + dy,
    });
    text.textContent = edge.label;
    svg.appendChild(text);
  });

  for (const vertex of diagram.vertices) {
    const [x, y] = positions[vertex.id];
    const point = svgElement("circle", {
      class: "node-circle selected",
      cx: x,
      cy: y,
      r: 11,
    });
    const label = svgElement("text", {
      class: "node-label",
      x,
      y: y + 28,
    });
    label.textContent = vertex.id;
    svg.append(point, label);
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

function appendBadgeRow(section, label, ids, theoremById) {
  const row = document.createElement("div");
  row.className = "generator-badge-row";
  const title = document.createElement("strong");
  title.textContent = label;
  row.appendChild(title);
  for (const id of ids) {
    const theorem = theoremById.get(id);
    const badge = makeLink(id, "theorems.html");
    badge.className = theorem ? statusClass(theorem) : "status-badge status-planned";
    badge.textContent = theorem ? `${id}: ${statusLabel(theorem)}` : `${id}: status loading`;
    row.appendChild(badge);
  }
  section.appendChild(row);
}

function appendDictionaryRow(section, ids) {
  const row = document.createElement("div");
  row.className = "generator-badge-row";
  const title = document.createElement("strong");
  title.textContent = "Dictionary";
  row.appendChild(title);
  for (const id of ids) {
    const link = makeLink(id, "dictionary.html");
    link.className = "record-pill";
    row.appendChild(link);
  }
  section.appendChild(row);
}

function appendRecord(output, example, diagram, theoremById) {
  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = example.label;
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `seed: ${JSON.stringify(example.seed)}`,
    `rules: ${example.rules.map((rule) => rule.ruleId).join(", ")}`,
    `schedule: ${example.iterationSchedule}`,
    `closure: ${example.closureCondition}`,
    `generated summary: ${JSON.stringify(diagram)}`,
    `note: ${example.note}`,
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, "Theorems", example.theoremIds, theoremById);
  appendDictionaryRow(record, example.dictionaryIds);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Seed-rule diagram generator", "Widget: generated explanation only");
  const selector = addLabeledSelect(
    panel,
    "seed-rule-example",
    "generated artifact",
    Object.entries(EXAMPLES).map(([value, example]) => ({ value, label: example.label })),
  );
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const exampleId = selector.value;
    const example = EXAMPLES[exampleId];
    const diagram = generatedObjectFor(exampleId);
    clear(output);
    if (exampleId === "finite_circle_diagram") {
      output.appendChild(renderCircleSvg({ n: example.seed.n, title: `Generated C_${example.seed.n} diagram` }));
    } else {
      output.appendChild(renderPhysicsLoopSvg(diagram));
    }
    appendRecord(output, example, diagram, theoremById);
  }

  selector.addEventListener("change", render);
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

mountWidgets("seed_rule_diagram_generator", mount);
