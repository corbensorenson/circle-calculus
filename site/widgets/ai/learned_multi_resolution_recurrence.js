import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018"];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0059", "COMMON-0069", "COMMON-0070"];

let chartIdCounter = 0;

function range(start, count) {
  return Array.from({ length: count }, (_, index) => start + index);
}

function tokenBudget(loopPeriod, sample) {
  return mod(sample, loopPeriod) + 1;
}

function tokenBudgets(loopPeriod, samples) {
  return samples.map((sample) => tokenBudget(loopPeriod, sample));
}

function recurrenceResolutionLevels(maxBudget) {
  return range(1, maxBudget).map((step) => (step % 2 === 1 ? "coarse" : "fine"));
}

function requiredResolutions(maxBudget, budgets) {
  const levels = recurrenceResolutionLevels(maxBudget);
  return budgets.map((budget) => levels[budget - 1]);
}

function majority(values) {
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
  return Array.from(counts.entries())
    .sort(([leftValue, leftCount], [rightValue, rightCount]) => (
      rightCount - leftCount || String(leftValue).localeCompare(String(rightValue))
    ))[0][0];
}

function fitLookup(period, positions, values) {
  const fallback = majority(values);
  const buckets = Array.from({ length: period }, () => []);
  positions.forEach((position, index) => {
    buckets[mod(position, period)].push(values[index]);
  });
  return buckets.map((bucket) => (bucket.length === 0 ? fallback : majority(bucket)));
}

function predictLookup(period, lookup, positions) {
  return positions.map((position) => lookup[mod(position, period)]);
}

function activeCountsByBudget(budgets, maxBudget) {
  return range(1, maxBudget).map((step) => budgets.filter((budget) => budget >= step).length);
}

function multiResolutionPredictions(requiredBudgets, requiredResolutionLabels, plannedBudgets, plannedResolutions, tolerance) {
  return requiredBudgets.map((requiredBudget, index) => {
    const plannedBudget = plannedBudgets[index];
    return requiredResolutionLabels[index] === plannedResolutions[index]
      && requiredBudget <= plannedBudget
      && plannedBudget <= requiredBudget + tolerance
      ? 1
      : 0;
  });
}

function accuracy(predictions) {
  return predictions.filter((prediction) => prediction === 1).length / predictions.length;
}

function percent(value) {
  return `${(100 * value).toFixed(1)}%`;
}

function svgElement(name, attrs = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function learnedFixture(values) {
  const trainSamples = range(0, values.trainLength);
  const testSamples = range(values.trainLength, values.testLength);
  const trainBudgets = tokenBudgets(values.loopPeriod, trainSamples);
  const trainResolutions = requiredResolutions(values.maxBudget, trainBudgets);
  const requiredBudgets = tokenBudgets(values.loopPeriod, testSamples);
  const requiredResolutionLabels = requiredResolutions(values.maxBudget, requiredBudgets);
  const learnedBudgetLookup = fitLookup(values.loopPeriod, trainSamples, trainBudgets);
  const learnedBudgets = predictLookup(values.loopPeriod, learnedBudgetLookup, testSamples)
    .map((budget) => Math.min(budget, values.maxBudget));
  const learnedResolutionLookup = fitLookup(values.loopPeriod, trainSamples, trainResolutions);
  const learnedResolutions = predictLookup(values.loopPeriod, learnedResolutionLookup, testSamples);
  const wrongBudgetLookup = fitLookup(values.wrongBudgetPeriod, trainSamples, trainBudgets);
  const wrongBudgets = predictLookup(values.wrongBudgetPeriod, wrongBudgetLookup, testSamples)
    .map((budget) => Math.min(budget, values.maxBudget));
  const wrongResolutionLookup = fitLookup(values.wrongResolutionPeriod, trainSamples, trainResolutions);
  const wrongResolutions = predictLookup(values.wrongResolutionPeriod, wrongResolutionLookup, testSamples);
  const fixedBudgets = testSamples.map(() => values.fixedLoopBudget);
  const overBudgets = testSamples.map(() => values.overLoopBudget);
  const coarseResolutions = testSamples.map(() => "coarse");
  const fineResolutions = testSamples.map(() => "fine");
  const activeCounts = activeCountsByBudget(learnedBudgets, values.maxBudget);

  return {
    resolutionLevels: recurrenceResolutionLevels(values.maxBudget),
    learnedBudgetLookup,
    learnedResolutionLookup,
    wrongBudgetLookup,
    wrongResolutionLookup,
    requiredBudgets,
    learnedBudgets,
    wrongBudgets,
    requiredResolutions: requiredResolutionLabels,
    learnedResolutions,
    wrongResolutions,
    activeCounts,
    learnedAccuracy: accuracy(multiResolutionPredictions(
      requiredBudgets,
      requiredResolutionLabels,
      learnedBudgets,
      learnedResolutions,
      values.tolerance,
    )),
    coarseAccuracy: accuracy(multiResolutionPredictions(
      requiredBudgets,
      requiredResolutionLabels,
      learnedBudgets,
      coarseResolutions,
      values.tolerance,
    )),
    fineAccuracy: accuracy(multiResolutionPredictions(
      requiredBudgets,
      requiredResolutionLabels,
      learnedBudgets,
      fineResolutions,
      values.tolerance,
    )),
    fixedAccuracy: accuracy(multiResolutionPredictions(
      requiredBudgets,
      requiredResolutionLabels,
      fixedBudgets,
      learnedResolutions,
      values.tolerance,
    )),
    wrongBudgetAccuracy: accuracy(multiResolutionPredictions(
      requiredBudgets,
      requiredResolutionLabels,
      wrongBudgets,
      learnedResolutions,
      values.tolerance,
    )),
    wrongResolutionAccuracy: accuracy(multiResolutionPredictions(
      requiredBudgets,
      requiredResolutionLabels,
      learnedBudgets,
      wrongResolutions,
      values.tolerance,
    )),
    overLoopAccuracy: accuracy(multiResolutionPredictions(
      requiredBudgets,
      requiredResolutionLabels,
      overBudgets,
      learnedResolutions,
      values.tolerance,
    )),
    averageActiveSamples: activeCounts.reduce((total, count) => total + count, 0) / activeCounts.length,
  };
}

function renderResolutionChart({ values, fixture }) {
  chartIdCounter += 1;
  const visibleCount = Math.min(values.testLength, 32);
  const width = 660;
  const height = 230;
  const left = 48;
  const right = 22;
  const top = 28;
  const rowHeight = 72;
  const rowGap = 22;
  const usableWidth = width - left - right;
  const titleId = `learned-multi-resolution-title-${chartIdCounter}`;
  const descId = `learned-multi-resolution-desc-${chartIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Learned multi-resolution recurrence route";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `First ${visibleCount} held-out samples, showing required and learned budget-resolution routes.`;
  svg.append(title, desc);

  [
    ["required", fixture.requiredBudgets, fixture.requiredResolutions, top],
    ["learned", fixture.learnedBudgets, fixture.learnedResolutions, top + rowHeight + rowGap],
  ].forEach(([labelText, budgets, resolutions, rowTop]) => {
    const rowLabel = svgElement("text", { class: "node-label", x: 8, y: rowTop + 12 });
    rowLabel.textContent = labelText;
    svg.appendChild(rowLabel);
    budgets.slice(0, visibleCount).forEach((budget, index) => {
      const resolution = resolutions[index];
      const x = left + (index * usableWidth) / visibleCount;
      const cellWidth = Math.max(7, usableWidth / visibleCount - 3);
      const cellHeight = Math.max(14, (Math.min(budget, values.maxBudget) * rowHeight) / values.maxBudget);
      const rect = svgElement("rect", {
        x,
        y: rowTop + rowHeight - cellHeight,
        width: cellWidth,
        height: cellHeight,
        fill: resolution === "coarse" ? "#1357a6" : "#2f855a",
        rx: 2,
      });
      const label = svgElement("text", {
        class: "node-label",
        x: x + cellWidth / 2,
        y: rowTop + rowHeight + 16,
      });
      label.textContent = resolution === "coarse" ? "C" : "F";
      svg.append(rect, label);
    });
  });
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

function appendRecord(output, values, fixture, theoremById) {
  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Learned multi-resolution recurrence record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `loop period: ${values.loopPeriod}`,
    `wrong budget period: ${values.wrongBudgetPeriod}`,
    `wrong resolution period: ${values.wrongResolutionPeriod}`,
    `train samples: ${values.trainLength}`,
    `held-out test samples: ${values.testLength}`,
    `max budget: ${values.maxBudget}`,
    `resolution levels: ${fixture.resolutionLevels.join(", ")}`,
    `learned budget lookup: ${fixture.learnedBudgetLookup.join(", ")}`,
    `learned resolution lookup: ${fixture.learnedResolutionLookup.join(", ")}`,
    `wrong budget-period lookup: ${fixture.wrongBudgetLookup.join(", ")}`,
    `wrong resolution-period lookup: ${fixture.wrongResolutionLookup.join(", ")}`,
    `required budget sample: ${fixture.requiredBudgets.slice(0, 12).join(", ")}`,
    `learned budget sample: ${fixture.learnedBudgets.slice(0, 12).join(", ")}`,
    `wrong budget sample: ${fixture.wrongBudgets.slice(0, 12).join(", ")}`,
    `required resolution sample: ${fixture.requiredResolutions.slice(0, 12).join(", ")}`,
    `learned resolution sample: ${fixture.learnedResolutions.slice(0, 12).join(", ")}`,
    `wrong resolution sample: ${fixture.wrongResolutions.slice(0, 12).join(", ")}`,
    `active sample counts by loop step: ${fixture.activeCounts.join(", ")}`,
    `average active samples: ${fixture.averageActiveSamples.toFixed(2)}`,
    `learned multi-resolution router accuracy: ${percent(fixture.learnedAccuracy)}`,
    `single-resolution coarse accuracy: ${percent(fixture.coarseAccuracy)}`,
    `single-resolution fine accuracy: ${percent(fixture.fineAccuracy)}`,
    `fixed-budget accuracy: ${percent(fixture.fixedAccuracy)}`,
    `wrong budget-period accuracy: ${percent(fixture.wrongBudgetAccuracy)}`,
    `wrong resolution-period accuracy: ${percent(fixture.wrongResolutionAccuracy)}`,
    `over-loop accuracy: ${percent(fixture.overLoopAccuracy)}`,
    "boundary: widget output is learned multi-resolution schedule bookkeeping for a constructed finite fixture, not a neural router, recursive-reasoning, throughput, memory, context-length, or model-quality claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Learned multi-resolution recurrence", "Widget: coarse/fine route bookkeeping only");
  const loopPeriodInput = addLabeledNumber(panel, "ai-multi-loop-period", "loop period", 4, 1, 16);
  const wrongBudgetPeriodInput = addLabeledNumber(panel, "ai-multi-wrong-budget-period", "wrong budget period", 3, 1, 16);
  const wrongResolutionPeriodInput = addLabeledNumber(panel, "ai-multi-wrong-resolution-period", "wrong resolution period", 3, 1, 16);
  const trainLengthInput = addLabeledNumber(panel, "ai-multi-train-length", "train samples", 64, 4, 256);
  const testLengthInput = addLabeledNumber(panel, "ai-multi-test-length", "test samples", 32, 1, 96);
  const maxBudgetInput = addLabeledNumber(panel, "ai-multi-max-budget", "max budget", 4, 1, 16);
  const fixedBudgetInput = addLabeledNumber(panel, "ai-multi-fixed-budget", "fixed budget", 4, 1, 32);
  const overBudgetInput = addLabeledNumber(panel, "ai-multi-over-budget", "over budget", 8, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-multi-tolerance", "tolerance", 0, 0, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const loopPeriod = positiveInt(loopPeriodInput.value, 4, 1, 16);
    const maxBudget = Math.max(positiveInt(maxBudgetInput.value, 4, 1, 16), loopPeriod);
    let wrongBudgetPeriod = positiveInt(wrongBudgetPeriodInput.value, 3, 1, 16);
    if (wrongBudgetPeriod === loopPeriod) wrongBudgetPeriod = loopPeriod === 1 ? 2 : loopPeriod - 1;
    let wrongResolutionPeriod = positiveInt(wrongResolutionPeriodInput.value, 3, 1, 16);
    if (wrongResolutionPeriod === loopPeriod) wrongResolutionPeriod = loopPeriod === 1 ? 2 : loopPeriod - 1;
    const values = {
      loopPeriod,
      wrongBudgetPeriod,
      wrongResolutionPeriod,
      trainLength: positiveInt(trainLengthInput.value, 64, 4, 256),
      testLength: positiveInt(testLengthInput.value, 32, 1, 96),
      maxBudget,
      fixedLoopBudget: positiveInt(fixedBudgetInput.value, 4, 1, 32),
      overLoopBudget: positiveInt(overBudgetInput.value, 8, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 0, 0, 8),
    };
    const fixture = learnedFixture(values);
    clear(output);
    output.appendChild(renderResolutionChart({ values, fixture }));
    appendRecord(output, values, fixture, theoremById);
  }

  for (const input of [
    loopPeriodInput,
    wrongBudgetPeriodInput,
    wrongResolutionPeriodInput,
    trainLengthInput,
    testLengthInput,
    maxBudgetInput,
    fixedBudgetInput,
    overBudgetInput,
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

mountWidgets("learned_multi_resolution_recurrence", mount);
