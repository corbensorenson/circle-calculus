import { addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const GENERATOR_INDEX_URL = "../../data/generated/generator_index.json";

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

function setSelectOptions(select, generators) {
  while (select.firstChild) {
    select.removeChild(select.firstChild);
  }
  for (const generator of generators) {
    const element = document.createElement("option");
    element.value = generator.id;
    element.textContent = generator.label;
    select.appendChild(element);
  }
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

function renderProofGlyphPanel(glyph) {
  const panel = document.createElement("div");
  panel.className = "widget-data";
  panel.setAttribute("role", "img");
  panel.setAttribute("aria-label", `Proof glyph ${glyph.glyph_id} links theorem ${glyph.theorem_id} to Lean declaration ${glyph.lean_name}.`);
  panel.textContent = [
    "proof glyph",
    `glyph id: ${glyph.glyph_id}`,
    `theorem id: ${glyph.theorem_id}`,
    `Lean name: ${glyph.lean_name}`,
  ].join("\n");
  return panel;
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
  addWidgetHeader(panel, "Seed-rule diagram generator", "Widget: generated explanation only; not a formal proof");
  const selector = addLabeledSelect(
    panel,
    "seed-rule-example",
    "generated artifact",
    [{ value: "", label: "loading generated records" }],
  );
  const output = addOutput(panel);
  let theoremById = new Map();
  let generators = [];

  function render() {
    clear(output);
    if (generators.length === 0) {
      const loading = document.createElement("p");
      loading.textContent = "Loading generated seed-rule records.";
      output.appendChild(loading);
      return;
    }
    const example = generators.find((item) => item.id === selector.value) || generators[0];
    selector.value = example.id;
    const diagram = example.generatedObject;
    if (example.id === "finite_circle_diagram") {
      output.appendChild(renderCircleSvg({ n: example.seed.n, title: `Generated C_${example.seed.n} diagram` }));
    } else if (example.id === "physics_loop_diagram") {
      output.appendChild(renderPhysicsLoopSvg(diagram));
    } else if (example.id === "coil_orbit") {
      output.appendChild(renderCircleSvg({
        n: example.seed.n,
        selected: example.seed.start,
        visited: diagram,
        title: "Generated coil orbit",
      }));
    } else if (example.id === "orbit_decomposition") {
      output.appendChild(renderCircleSvg({
        n: example.seed.n,
        selected: 0,
        visited: diagram.flat(),
        title: `Generated ${diagram.length}-orbit family`,
      }));
    } else {
      output.appendChild(renderProofGlyphPanel(diagram));
    }
    appendRecord(output, example, diagram, theoremById);
  }

  selector.addEventListener("change", render);
  Promise.all([
    loadJson("../../data/generated/theorem_manifest.json"),
    loadJson(GENERATOR_INDEX_URL),
  ])
    .then(([theoremData, generatorData]) => {
      theoremById = new Map(theoremData.theorems.map((theorem) => [theorem.id, theorem]));
      generators = generatorData.generators || [];
      setSelectOptions(selector, generators);
      render();
    })
    .catch((error) => {
      console.error(error);
      render();
    });
  render();
}

mountWidgets("seed_rule_diagram_generator", mount);
