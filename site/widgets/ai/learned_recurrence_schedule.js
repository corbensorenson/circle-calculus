import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009"];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0070"];

let chartIdCounter = 0;

function range(start, count) {
  return Array.from({ length: count }, (_, index) => start + index);
}

function requiredBudget(loopPeriod, sample) {
  return mod(sample, loopPeriod) + 1;
}

function requiredBudgets(loopPeriod, samples) {
  return samples.map((sample) => requiredBudget(loopPeriod, sample));
}

function majorityInt(values) {
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
  return Array.from(counts.entries())
    .sort(([leftValue, leftCount], [rightValue, rightCount]) => (
      rightCount - leftCount || leftValue - rightValue
    ))[0][0];
}

function fitBudgetLookup(period, positions, budgets) {
  const fallback = majorityInt(budgets);
  const buckets = Array.from({ length: period }, () => []);
  positions.forEach((position, index) => {
    buckets[mod(position, period)].push(budgets[index]);
  });
  return buckets.map((bucket) => (bucket.length === 0 ? fallback : majorityInt(bucket)));
}

function predictBudgetLookup(period, lookup, positions) {
  return positions.map((position) => lookup[mod(position, period)]);
}

function budgetPredictions(required, planned, tolerance) {
  return required.map((requiredBudgetValue, index) => {
    const plannedBudget = planned[index];
    return requiredBudgetValue <= plannedBudget
      && plannedBudget <= requiredBudgetValue + tolerance
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
  const trainBudgets = requiredBudgets(values.loopPeriod, trainSamples);
  const testSamples = range(values.trainLength, values.testLength);
  const required = requiredBudgets(values.loopPeriod, testSamples);
  const learnedLookup = fitBudgetLookup(values.loopPeriod, trainSamples, trainBudgets);
  const learnedBudgets = predictBudgetLookup(values.loopPeriod, learnedLookup, testSamples);
  const wrongLookup = fitBudgetLookup(values.wrongPeriod, trainSamples, trainBudgets);
  const wrongBudgets = predictBudgetLookup(values.wrongPeriod, wrongLookup, testSamples);
  const fixedBudgets = testSamples.map(() => values.fixedLoopBudget);
  const overBudgets = testSamples.map(() => values.overLoopBudget);

  return {
    learnedLookup,
    wrongLookup,
    requiredBudgets: required,
    learnedBudgets,
    wrongBudgets,
    learnedAccuracy: accuracy(budgetPredictions(required, learnedBudgets, values.tolerance)),
    fixedAccuracy: accuracy(budgetPredictions(required, fixedBudgets, values.tolerance)),
    wrongAccuracy: accuracy(budgetPredictions(required, wrongBudgets, values.tolerance)),
    overLoopAccuracy: accuracy(budgetPredictions(required, overBudgets, values.tolerance)),
  };
}

function renderBudgetChart({ values, fixture }) {
  chartIdCounter += 1;
  const visibleCount = Math.min(values.testLength, 32);
  const width = 640;
  const height = 220;
  const left = 38;
  const right = 18;
  const top = 28;
  const rowGap = 18;
  const rowHeight = 70;
  const usableWidth = width - left - right;
  const titleId = `learned-schedule-title-${chartIdCounter}`;
  const descId = `learned-schedule-desc-${chartIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Learned recurrence schedule budgets";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Required and learned held-out budgets repeat modulo loop period ${values.loopPeriod}.`;
  svg.append(title, desc);

  [
    ["required", fixture.requiredBudgets, top, "#1357a6"],
    ["learned", fixture.learnedBudgets, top + rowHeight + rowGap, "#2f855a"],
  ].forEach(([labelText, budgets, rowTop, fill]) => {
    const label = svgElement("text", { class: "node-label", x: 10, y: rowTop + 12 });
    label.textContent = labelText;
    svg.appendChild(label);
    budgets.slice(0, visibleCount).forEach((budget, index) => {
      const x = left + (index * usableWidth) / visibleCount;
      const barWidth = Math.max(4, usableWidth / visibleCount - 3);
      const barHeight = (budget * rowHeight) / values.loopPeriod;
      const rect = svgElement("rect", {
        x,
        y: rowTop + rowHeight - barHeight,
        width: barWidth,
        height: barHeight,
        fill,
        rx: 2,
      });
      svg.appendChild(rect);
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
  title.textContent = "Learned recurrence-schedule record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `loop period: ${values.loopPeriod}`,
    `wrong/control period: ${values.wrongPeriod}`,
    `train samples: ${values.trainLength}`,
    `held-out test samples: ${values.testLength}`,
    `learned budget lookup: ${fixture.learnedLookup.join(", ")}`,
    `wrong-period lookup: ${fixture.wrongLookup.join(", ")}`,
    `required budget sample: ${fixture.requiredBudgets.slice(0, 12).join(", ")}`,
    `learned budget sample: ${fixture.learnedBudgets.slice(0, 12).join(", ")}`,
    `wrong-period budget sample: ${fixture.wrongBudgets.slice(0, 12).join(", ")}`,
    `fixed loop budget: ${values.fixedLoopBudget}`,
    `over-loop budget: ${values.overLoopBudget}`,
    `learned phase-router accuracy: ${percent(fixture.learnedAccuracy)}`,
    `fixed-budget accuracy: ${percent(fixture.fixedAccuracy)}`,
    `wrong-period accuracy: ${percent(fixture.wrongAccuracy)}`,
    `over-loop accuracy: ${percent(fixture.overLoopAccuracy)}`,
    "boundary: widget output is learned recurrence-schedule bookkeeping for a constructed finite fixture, not a neural router, recursive-reasoning, throughput, memory, context-length, or model-quality claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Learned recurrence schedule", "Widget: phase-to-budget lookup only");
  const loopPeriodInput = addLabeledNumber(panel, "ai-learned-schedule-loop-period", "loop period", 4, 1, 16);
  const wrongPeriodInput = addLabeledNumber(panel, "ai-learned-schedule-wrong-period", "wrong period", 3, 1, 16);
  const trainLengthInput = addLabeledNumber(panel, "ai-learned-schedule-train-length", "train samples", 64, 4, 256);
  const testLengthInput = addLabeledNumber(panel, "ai-learned-schedule-test-length", "test samples", 32, 1, 96);
  const fixedBudgetInput = addLabeledNumber(panel, "ai-learned-schedule-fixed-budget", "fixed budget", 4, 1, 32);
  const overBudgetInput = addLabeledNumber(panel, "ai-learned-schedule-over-budget", "over budget", 8, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-learned-schedule-tolerance", "tolerance", 0, 0, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const loopPeriod = positiveInt(loopPeriodInput.value, 4, 1, 16);
    let wrongPeriod = positiveInt(wrongPeriodInput.value, 3, 1, 16);
    if (wrongPeriod === loopPeriod) wrongPeriod = loopPeriod === 1 ? 2 : loopPeriod - 1;
    const values = {
      loopPeriod,
      wrongPeriod,
      trainLength: positiveInt(trainLengthInput.value, 64, 4, 256),
      testLength: positiveInt(testLengthInput.value, 32, 1, 96),
      fixedLoopBudget: positiveInt(fixedBudgetInput.value, 4, 1, 32),
      overLoopBudget: positiveInt(overBudgetInput.value, 8, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 0, 0, 8),
    };
    const fixture = learnedFixture(values);
    clear(output);
    output.appendChild(renderBudgetChart({ values, fixture }));
    appendRecord(output, values, fixture, theoremById);
  }

  for (const input of [
    loopPeriodInput,
    wrongPeriodInput,
    trainLengthInput,
    testLengthInput,
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

mountWidgets("learned_recurrence_schedule", mount);
