import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0018", "AIM-T0019", "AIM-T0020", "AIM-T0021"];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0054", "COMMON-0059", "COMMON-0067"];

let timelineIdCounter = 0;

function loopRequiredSteps(loopPeriod, sample) {
  return mod(sample, loopPeriod) + 1;
}

function tokenRecurrenceBudget(loopPeriod, token) {
  return loopRequiredSteps(loopPeriod, token);
}

function trainingFreeLoopBudget(loopPeriod, sample, maxLoops) {
  return Math.min(loopRequiredSteps(loopPeriod, sample), maxLoops);
}

function loopExitAvailable(loopPeriod, sample, maxLoops) {
  return loopRequiredSteps(loopPeriod, sample) <= maxLoops;
}

function loopOverthinkingBoundary(loopPeriod, sample, tolerance) {
  return loopRequiredSteps(loopPeriod, sample) + tolerance;
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function renderTimeline({ loopPeriod, sample, maxLoops, tolerance }) {
  timelineIdCounter += 1;
  const required = loopRequiredSteps(loopPeriod, sample);
  const budget = trainingFreeLoopBudget(loopPeriod, sample, maxLoops);
  const boundary = loopOverthinkingBoundary(loopPeriod, sample, tolerance);
  const limit = Math.max(loopPeriod, maxLoops, boundary);
  const width = 520;
  const height = 150;
  const left = 42;
  const right = 32;
  const usable = width - left - right;
  const titleId = `loop-budget-title-${timelineIdCounter}`;
  const descId = `loop-budget-desc-${timelineIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });

  const title = svgElement("title", { id: titleId });
  title.textContent = "Loop recurrence budget timeline";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Required loop ${required}, capped budget ${budget}, overthinking boundary ${boundary}, across ${limit} displayed steps.`;
  svg.append(title, desc);

  const axis = svgElement("line", {
    x1: left,
    y1: 72,
    x2: width - right,
    y2: 72,
    stroke: "#cbd5df",
    "stroke-width": 2,
  });
  svg.appendChild(axis);

  for (let step = 1; step <= limit; step += 1) {
    const x = left + ((step - 1) * usable) / Math.max(1, limit - 1);
    const classes = [
      "node-circle",
      step === required ? "selected" : "",
      step <= budget ? "visited" : "",
    ].filter(Boolean).join(" ");
    const point = svgElement("circle", {
      class: classes,
      cx: x,
      cy: 72,
      r: 9,
    });
    const label = svgElement("text", {
      class: "node-label",
      x,
      y: 104,
    });
    label.textContent = String(step);
    svg.append(point, label);
  }

  const markers = [
    ["required", required, "R", 22],
    ["budget", budget, "B", 38],
    ["boundary", boundary, "G", 134],
  ];
  for (const [name, step, label, y] of markers) {
    const x = left + ((step - 1) * usable) / Math.max(1, limit - 1);
    const text = svgElement("text", {
      class: "node-label",
      x,
      y,
    });
    text.textContent = `${label}: ${name}`;
    svg.appendChild(text);
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

function appendRecord(output, values, theoremById) {
  const shiftedSample = values.sample + values.loopPeriod;
  const required = loopRequiredSteps(values.loopPeriod, values.sample);
  const shiftedRequired = loopRequiredSteps(values.loopPeriod, shiftedSample);
  const tokenBudget = tokenRecurrenceBudget(values.loopPeriod, values.sample);
  const trainingBudget = trainingFreeLoopBudget(values.loopPeriod, values.sample, values.maxLoops);
  const shiftedTrainingBudget = trainingFreeLoopBudget(values.loopPeriod, shiftedSample, values.maxLoops);
  const exitAvailable = loopExitAvailable(values.loopPeriod, values.sample, values.maxLoops);
  const boundary = loopOverthinkingBoundary(values.loopPeriod, values.sample, values.tolerance);
  const shiftedBoundary = loopOverthinkingBoundary(values.loopPeriod, shiftedSample, values.tolerance);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Schedule record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `loop period: ${values.loopPeriod}`,
    `sample/token index: ${values.sample}`,
    `loop phase: ${mod(values.sample, values.loopPeriod)}`,
    `required loops = phase + 1: ${required}`,
    `token recurrence budget: ${tokenBudget}`,
    `training-free budget min(required, maxLoops): ${trainingBudget}`,
    `loop exit available: ${exitAvailable ? "yes" : "no"}`,
    `overthinking boundary required + tolerance: ${boundary}`,
    `one-period shift sample + loopPeriod: ${shiftedSample}`,
    `shifted required loops: ${shiftedRequired}`,
    `shifted training-free budget: ${shiftedTrainingBudget}`,
    `shifted boundary: ${shiftedBoundary}`,
    `periodic checks: required=${required === shiftedRequired}, training=${trainingBudget === shiftedTrainingBudget}, boundary=${boundary === shiftedBoundary}`,
    "boundary: widget output is executable schedule intuition, not a proof or model-quality claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Loop recurrence budget", "Widget: finite schedule bookkeeping only");
  const periodInput = addLabeledNumber(panel, "ai-loop-period", "loop period", 4, 1, 32);
  const sampleInput = addLabeledNumber(panel, "ai-loop-sample", "sample/token", 11, 0, 999);
  const maxLoopsInput = addLabeledNumber(panel, "ai-loop-max", "max loops", 3, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-loop-tolerance", "tolerance", 1, 0, 32);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      loopPeriod: positiveInt(periodInput.value, 4, 1, 32),
      sample: positiveInt(sampleInput.value, 11, 0, 999),
      maxLoops: positiveInt(maxLoopsInput.value, 3, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 1, 0, 32),
    };
    clear(output);
    output.appendChild(renderTimeline(values));
    appendRecord(output, values, theoremById);
  }

  for (const input of [periodInput, sampleInput, maxLoopsInput, toleranceInput]) {
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

mountWidgets("loop_recurrence_budget", mount);
