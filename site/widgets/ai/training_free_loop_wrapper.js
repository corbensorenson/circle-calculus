import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0010", "AIM-T0011", "AIM-T0019", "AIM-T0020"];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0054", "COMMON-0067"];

let chartIdCounter = 0;

function range(count) {
  return Array.from({ length: count }, (_, index) => index);
}

function requiredBudget(loopPeriod, sample) {
  return mod(sample, loopPeriod) + 1;
}

function requiredBudgets(loopPeriod, samples) {
  return samples.map((sample) => requiredBudget(loopPeriod, sample));
}

function trainingFreeBudget(loopPeriod, sample, maxLoops) {
  return Math.min(requiredBudget(loopPeriod, sample), maxLoops);
}

function trainingFreeBudgets(loopPeriod, samples, maxLoops) {
  return samples.map((sample) => trainingFreeBudget(loopPeriod, sample, maxLoops));
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

function budgetIsFullDepthPredictions(plannedBudgets, maxLoops) {
  return plannedBudgets.map((budget) => (budget >= maxLoops ? 1 : 0));
}

function nonperiodicThresholdLabel(sample, threshold) {
  return sample >= threshold ? 1 : 0;
}

function accuracy(predictions, labels) {
  let correct = 0;
  for (let index = 0; index < labels.length; index += 1) {
    if (predictions[index] === labels[index]) correct += 1;
  }
  return correct / labels.length;
}

function fitThresholdClassifier(samples, labels) {
  let best = { score: -1, threshold: Math.min(...samples), polarity: 1 };
  for (let threshold = Math.min(...samples); threshold <= Math.max(...samples) + 1; threshold += 1) {
    for (const polarity of [1, -1]) {
      const predictions = samples.map((sample) => (sample >= threshold) === (polarity === 1) ? 1 : 0);
      const score = accuracy(predictions, labels);
      if (score > best.score) best = { score, threshold, polarity };
    }
  }
  return best;
}

function predictThresholdClassifier(samples, threshold, polarity) {
  return samples.map((sample) => (sample >= threshold) === (polarity === 1) ? 1 : 0);
}

function activeCountsByBudget(budgets, maxLoops) {
  return Array.from({ length: maxLoops }, (_, index) => {
    const step = index + 1;
    return budgets.filter((budget) => budget >= step).length;
  });
}

function budgetHistogram(budgets) {
  const uniqueBudgets = Array.from(new Set(budgets)).sort((left, right) => left - right);
  return uniqueBudgets.map((budget) => [budget, budgets.filter((value) => value === budget).length]);
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

function fixture(values) {
  const samples = range(values.sampleCount);
  const required = requiredBudgets(values.loopPeriod, samples);
  const labels = samples.map(() => 1);
  const phaseBudgets = trainingFreeBudgets(values.loopPeriod, samples, values.maxLoops);
  const singlePassBudgets = samples.map(() => 1);
  const fixedBudgets = samples.map(() => values.fixedLoopBudget);
  const wrongPeriodBudgets = trainingFreeBudgets(values.wrongLoopPeriod, samples, values.maxLoops);
  const overBudgets = samples.map(() => values.overLoopBudget);
  const threshold = Math.floor((3 * values.sampleCount) / 4);
  const controlLabels = samples.map((sample) => nonperiodicThresholdLabel(sample, threshold));
  const controlPhasePredictions = budgetIsFullDepthPredictions(phaseBudgets, values.maxLoops);
  const thresholdFit = fitThresholdClassifier(samples, controlLabels);
  const thresholdPredictions = predictThresholdClassifier(samples, thresholdFit.threshold, thresholdFit.polarity);
  const activeCounts = activeCountsByBudget(phaseBudgets, values.maxLoops);

  return {
    requiredBudgets: required,
    phaseBudgets,
    wrongPeriodBudgets,
    activeCounts,
    histogram: budgetHistogram(phaseBudgets),
    averagePhaseBudget: phaseBudgets.reduce((total, budget) => total + budget, 0) / phaseBudgets.length,
    singlePassAccuracy: accuracy(budgetPredictions(required, singlePassBudgets, values.tolerance), labels),
    fixedAccuracy: accuracy(budgetPredictions(required, fixedBudgets, values.tolerance), labels),
    phaseAccuracy: accuracy(budgetPredictions(required, phaseBudgets, values.tolerance), labels),
    wrongAccuracy: accuracy(budgetPredictions(required, wrongPeriodBudgets, values.tolerance), labels),
    overLoopAccuracy: accuracy(budgetPredictions(required, overBudgets, values.tolerance), labels),
    nonperiodicPhaseAccuracy: accuracy(controlPhasePredictions, controlLabels),
    nonperiodicThresholdAccuracy: accuracy(thresholdPredictions, controlLabels),
  };
}

function renderBudgetChart({ values, result }) {
  chartIdCounter += 1;
  const visibleCount = Math.min(values.sampleCount, 32);
  const width = 640;
  const height = 220;
  const left = 38;
  const right = 18;
  const top = 28;
  const rowGap = 18;
  const rowHeight = 70;
  const usableWidth = width - left - right;
  const titleId = `training-free-wrapper-title-${chartIdCounter}`;
  const descId = `training-free-wrapper-desc-${chartIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Training-free loop-wrapper budgets";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Required budgets and capped phase budgets for ${visibleCount} displayed samples.`;
  svg.append(title, desc);

  [
    ["required", result.requiredBudgets, top, "#1357a6"],
    ["phase", result.phaseBudgets, top + rowHeight + rowGap, "#2f855a"],
  ].forEach(([labelText, budgets, rowTop, fill]) => {
    const label = svgElement("text", { class: "node-label", x: 10, y: rowTop + 12 });
    label.textContent = labelText;
    svg.appendChild(label);
    budgets.slice(0, visibleCount).forEach((budget, index) => {
      const x = left + (index * usableWidth) / visibleCount;
      const barWidth = Math.max(4, usableWidth / visibleCount - 3);
      const barHeight = (Math.min(budget, values.maxLoops) * rowHeight) / values.maxLoops;
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

function appendRecord(output, values, result, theoremById) {
  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Training-free loop-wrapper record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `loop period: ${values.loopPeriod}`,
    `sample count: ${values.sampleCount}`,
    `max loops: ${values.maxLoops}`,
    `fixed loop budget: ${values.fixedLoopBudget}`,
    `wrong loop period: ${values.wrongLoopPeriod}`,
    `over-loop budget: ${values.overLoopBudget}`,
    `phase budget sample: ${result.phaseBudgets.slice(0, 12).join(", ")}`,
    `wrong-period budget sample: ${result.wrongPeriodBudgets.slice(0, 12).join(", ")}`,
    `active sample counts: ${result.activeCounts.join(", ")}`,
    `budget histogram: ${result.histogram.map(([budget, count]) => `${budget}:${count}`).join(", ")}`,
    `average phase budget: ${result.averagePhaseBudget.toFixed(2)}`,
    `single-pass accuracy: ${percent(result.singlePassAccuracy)}`,
    `fixed-loop accuracy: ${percent(result.fixedAccuracy)}`,
    `training-free phase-budget accuracy: ${percent(result.phaseAccuracy)}`,
    `wrong-period budget accuracy: ${percent(result.wrongAccuracy)}`,
    `over-loop no-exit accuracy: ${percent(result.overLoopAccuracy)}`,
    `nonperiodic phase-budget accuracy: ${percent(result.nonperiodicPhaseAccuracy)}`,
    `nonperiodic scalar-threshold accuracy: ${percent(result.nonperiodicThresholdAccuracy)}`,
    "boundary: widget output is deterministic training-free loop-wrapper bookkeeping, not learned recurrence, recursive-reasoning, throughput, memory, context-length, or model-quality evidence.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Training-free loop wrapper", "Widget: fixed phase-budget fixture only");
  const loopPeriodInput = addLabeledNumber(panel, "ai-tfl-loop-period", "loop period", 4, 1, 16);
  const sampleCountInput = addLabeledNumber(panel, "ai-tfl-sample-count", "sample count", 32, 1, 96);
  const maxLoopsInput = addLabeledNumber(panel, "ai-tfl-max-loops", "max loops", 4, 1, 16);
  const fixedBudgetInput = addLabeledNumber(panel, "ai-tfl-fixed-budget", "fixed budget", 2, 1, 32);
  const wrongPeriodInput = addLabeledNumber(panel, "ai-tfl-wrong-period", "wrong period", 3, 1, 16);
  const overBudgetInput = addLabeledNumber(panel, "ai-tfl-over-budget", "over budget", 8, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-tfl-tolerance", "tolerance", 0, 0, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const loopPeriod = positiveInt(loopPeriodInput.value, 4, 1, 16);
    let wrongLoopPeriod = positiveInt(wrongPeriodInput.value, 3, 1, 16);
    if (wrongLoopPeriod === loopPeriod) wrongLoopPeriod = loopPeriod === 1 ? 2 : loopPeriod - 1;
    const values = {
      loopPeriod,
      sampleCount: positiveInt(sampleCountInput.value, 32, 1, 96),
      maxLoops: positiveInt(maxLoopsInput.value, 4, 1, 16),
      fixedLoopBudget: positiveInt(fixedBudgetInput.value, 2, 1, 32),
      wrongLoopPeriod,
      overLoopBudget: positiveInt(overBudgetInput.value, 8, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 0, 0, 8),
    };
    const result = fixture(values);
    clear(output);
    output.appendChild(renderBudgetChart({ values, result }));
    appendRecord(output, values, result, theoremById);
  }

  for (const input of [
    loopPeriodInput,
    sampleCountInput,
    maxLoopsInput,
    fixedBudgetInput,
    wrongPeriodInput,
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

mountWidgets("training_free_loop_wrapper", mount);
