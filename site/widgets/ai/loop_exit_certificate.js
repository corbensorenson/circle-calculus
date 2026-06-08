import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = [
  "AIM-T0012",
  "AIM-T0013",
  "AIM-T0014",
  "AIM-T0015",
  "AIM-T0016",
  "AIM-T0017",
  "AIM-T0024",
  "AIM-T0029",
  "AIM-T0030",
  "AIM-T0031",
  "AIM-T0032",
  "AIM-T0033",
  "AIM-T0034",
];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0054", "COMMON-0059", "COMMON-0067"];

let traceIdCounter = 0;

function loopRequiredSteps(loopPeriod, sampleIndex) {
  return mod(sampleIndex, loopPeriod) + 1;
}

function trainingFreeLoopBudget(loopPeriod, sampleIndex, maxLoops) {
  return Math.min(loopRequiredSteps(loopPeriod, sampleIndex), maxLoops);
}

function loopScoreTrace(requiredSteps, maxLoops, tolerance) {
  return Array.from({ length: maxLoops }, (_, index) => {
    const step = index + 1;
    return requiredSteps <= step && step <= requiredSteps + tolerance ? 1 : 0;
  });
}

function loopExitStep(requiredSteps, maxLoops, tolerance) {
  const trace = loopScoreTrace(requiredSteps, maxLoops, tolerance);
  const index = trace.findIndex((score) => score === 1);
  return index === -1 ? null : index + 1;
}

function loopExitCertificate(loopPeriod, sampleIndex, maxLoops, tolerance) {
  const requiredSteps = loopRequiredSteps(loopPeriod, sampleIndex);
  const overthinkingBoundary = requiredSteps + tolerance;
  const scoreTrace = loopScoreTrace(requiredSteps, maxLoops, tolerance);
  const exitStep = loopExitStep(requiredSteps, maxLoops, tolerance);
  return {
    loopPeriod,
    sampleIndex,
    maxLoops,
    tolerance,
    requiredSteps,
    overthinkingBoundary,
    scoreTrace,
    exitStep,
    exitAvailable: exitStep !== null,
    withinBudget: exitStep !== null && exitStep <= maxLoops,
    withinGuardrail: exitStep !== null && exitStep <= overthinkingBoundary,
  };
}

function yesNo(value) {
  return value ? "yes" : "no";
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function renderTrace(certificate, label) {
  traceIdCounter += 1;
  const limit = Math.max(certificate.maxLoops, certificate.overthinkingBoundary);
  const width = 620;
  const height = 174;
  const left = 46;
  const right = 36;
  const usable = width - left - right;
  const titleId = `loop-exit-title-${traceIdCounter}`;
  const descId = `loop-exit-desc-${traceIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });

  const title = svgElement("title", { id: titleId });
  title.textContent = `${label} loop-exit score trace`;
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Required step ${certificate.requiredSteps}, max loops ${certificate.maxLoops}, overthinking boundary ${certificate.overthinkingBoundary}, exit step ${certificate.exitStep ?? "none"}.`;
  svg.append(title, desc);

  const axis = svgElement("line", {
    x1: left,
    y1: 82,
    x2: width - right,
    y2: 82,
    stroke: "#cbd5df",
    "stroke-width": 2,
  });
  svg.appendChild(axis);

  for (let step = 1; step <= limit; step += 1) {
    const x = left + ((step - 1) * usable) / Math.max(1, limit - 1);
    const score = certificate.scoreTrace[step - 1] ?? 0;
    const classes = [
      "node-circle",
      score === 1 ? "visited" : "",
      step === certificate.requiredSteps ? "selected" : "",
    ].filter(Boolean).join(" ");
    const point = svgElement("circle", {
      class: classes,
      cx: x,
      cy: 82,
      r: 10,
    });
    const stepLabel = svgElement("text", {
      class: "node-label",
      x,
      y: 116,
    });
    stepLabel.textContent = String(step);
    const scoreLabel = svgElement("text", {
      class: "node-label",
      x,
      y: score === 1 ? 56 : 45,
    });
    scoreLabel.textContent = step <= certificate.maxLoops ? `s=${score}` : "guard";
    svg.append(point, scoreLabel, stepLabel);
  }

  const markers = [
    ["required", certificate.requiredSteps, "R", 22],
    ["exit", certificate.exitStep, "E", 146],
    ["guard", certificate.overthinkingBoundary, "G", 164],
  ];
  for (const [name, step, short, y] of markers) {
    if (step === null) continue;
    const x = left + ((step - 1) * usable) / Math.max(1, limit - 1);
    const marker = svgElement("text", {
      class: "node-label",
      x,
      y,
    });
    marker.textContent = `${short}: ${name}`;
    svg.appendChild(marker);
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
  title.textContent = "Certificate theorems";
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

function appendCertificateTable(section, primary, control) {
  const rows = [
    ["required steps", primary.requiredSteps, control.requiredSteps],
    ["score trace", primary.scoreTrace.join(", "), control.scoreTrace.join(", ")],
    ["exit step", primary.exitStep ?? "none", control.exitStep ?? "none"],
    ["exit available", yesNo(primary.exitAvailable), yesNo(control.exitAvailable)],
    ["within budget", yesNo(primary.withinBudget), yesNo(control.withinBudget)],
    ["within guardrail", yesNo(primary.withinGuardrail), yesNo(control.withinGuardrail)],
    ["guardrail boundary", primary.overthinkingBoundary, control.overthinkingBoundary],
  ];
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["field", "primary certificate", "fixed-budget control"]) {
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
    row.forEach((value) => {
      const td = document.createElement("td");
      td.textContent = String(value);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  section.appendChild(table);
}

function appendRecord(output, values, theoremById) {
  const primary = loopExitCertificate(
    values.loopPeriod,
    values.sampleIndex,
    values.maxLoops,
    values.tolerance,
  );
  const control = loopExitCertificate(
    values.loopPeriod,
    values.controlSampleIndex,
    values.controlMaxLoops,
    values.tolerance,
  );
  const shifted = loopExitCertificate(
    values.loopPeriod,
    values.sampleIndex + values.loopPeriod,
    values.maxLoops,
    values.tolerance,
  );
  const multiPass = loopExitCertificate(
    values.loopPeriod,
    values.sampleIndex + 3 * values.loopPeriod,
    values.maxLoops,
    values.tolerance,
  );
  const primaryBudget = trainingFreeLoopBudget(values.loopPeriod, values.sampleIndex, values.maxLoops);

  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Loop-exit certificate record";
  section.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    "fixture id: AIM-B0011",
    `loop period: ${values.loopPeriod}`,
    `primary sample: ${values.sampleIndex}`,
    `primary phase: ${mod(values.sampleIndex, values.loopPeriod)}`,
    `primary max loops: ${values.maxLoops}`,
    `fixed-budget control sample: ${values.controlSampleIndex}`,
    `fixed-budget control max loops: ${values.controlMaxLoops}`,
    `overthinking tolerance: ${values.tolerance}`,
    `primary selected wrapper budget: ${primaryBudget}`,
    `certified budget equals exit step: ${primary.exitStep !== null && primaryBudget === primary.exitStep}`,
    `one-period shifted sample: ${values.sampleIndex + values.loopPeriod}`,
    `shifted required steps: ${shifted.requiredSteps}`,
    `shifted exit available: ${yesNo(shifted.exitAvailable)}`,
    `periodic exit availability check: ${primary.exitAvailable === shifted.exitAvailable}`,
    `three-pass shifted sample: ${values.sampleIndex + 3 * values.loopPeriod}`,
    `three-pass required steps: ${multiPass.requiredSteps}`,
    `three-pass exit-step check: ${primary.exitStep === multiPass.exitStep}`,
    `three-pass exit available: ${yesNo(multiPass.exitAvailable)}`,
    `multi-pass boundary check: ${primary.overthinkingBoundary === multiPass.overthinkingBoundary}`,
    `multi-pass exit availability check: ${primary.exitAvailable === multiPass.exitAvailable}`,
  ].join("\n");
  section.appendChild(data);
  section.appendChild(renderTrace(primary, "Primary"));
  section.appendChild(renderTrace(control, "Control"));
  appendCertificateTable(section, primary, control);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this is a deterministic finite loop-schedule certificate. It is not a trained early-exit model, recursive-reasoning evidence, speed evidence, or an overthinking result for real transformers.";
  section.appendChild(warning);

  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Loop-exit certificate", "Widget: finite exit trace and guardrail certificate");
  const periodInput = addLabeledNumber(panel, "ai-exit-period", "loop period", 4, 1, 32);
  const sampleInput = addLabeledNumber(panel, "ai-exit-sample", "primary sample", 6, 0, 999);
  const maxLoopsInput = addLabeledNumber(panel, "ai-exit-max", "primary max loops", 4, 1, 64);
  const controlSampleInput = addLabeledNumber(panel, "ai-exit-control-sample", "control sample", 3, 0, 999);
  const controlMaxLoopsInput = addLabeledNumber(panel, "ai-exit-control-max", "control max loops", 2, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-exit-tolerance", "tolerance", 1, 0, 32);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      loopPeriod: positiveInt(periodInput.value, 4, 1, 32),
      sampleIndex: positiveInt(sampleInput.value, 6, 0, 999),
      maxLoops: positiveInt(maxLoopsInput.value, 4, 1, 64),
      controlSampleIndex: positiveInt(controlSampleInput.value, 3, 0, 999),
      controlMaxLoops: positiveInt(controlMaxLoopsInput.value, 2, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 1, 0, 32),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [
    periodInput,
    sampleInput,
    maxLoopsInput,
    controlSampleInput,
    controlMaxLoopsInput,
    toleranceInput,
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

mountWidgets("loop_exit_certificate", mount);
