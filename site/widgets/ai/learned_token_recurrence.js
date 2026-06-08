import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018", "AIM-T0022", "AIM-T0057"];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0059", "COMMON-0068", "COMMON-0069"];

let chartIdCounter = 0;

function range(start, count) {
  return Array.from({ length: count }, (_, index) => start + index);
}

function tokenBudget(loopPeriod, token) {
  return mod(token, loopPeriod) + 1;
}

function tokenBudgets(loopPeriod, tokens) {
  return tokens.map((token) => tokenBudget(loopPeriod, token));
}

function majorityInt(values) {
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
  return Array.from(counts.entries())
    .sort(([leftValue, leftCount], [rightValue, rightCount]) => (
      rightCount - leftCount || leftValue - rightValue
    ))[0][0];
}

function majorityLabel(labels) {
  const positives = labels.filter((label) => label === 1).length;
  const negatives = labels.length - positives;
  return positives >= negatives ? 1 : 0;
}

function fitLoopBudgetLookup(period, positions, budgets) {
  const fallback = majorityInt(budgets);
  const buckets = Array.from({ length: period }, () => []);
  positions.forEach((position, index) => {
    buckets[mod(position, period)].push(budgets[index]);
  });
  return buckets.map((bucket) => (bucket.length === 0 ? fallback : majorityInt(bucket)));
}

function predictLoopBudgetLookup(period, lookup, positions) {
  return positions.map((position) => lookup[mod(position, period)]);
}

function shiftedBudgets(budgets, maxBudget, shift) {
  return budgets.map((budget) => mod(budget - 1 + shift, maxBudget) + 1);
}

function activeTokenCountsByBudget(budgets, maxBudget) {
  return Array.from({ length: maxBudget }, (_, index) => {
    const step = index + 1;
    return budgets.filter((budget) => budget >= step).length;
  });
}

function recurrenceBudgetPredictions(requiredBudgets, plannedBudgets, tolerance) {
  return requiredBudgets.map((required, index) => {
    const planned = plannedBudgets[index];
    return required <= planned && planned <= required + tolerance ? 1 : 0;
  });
}

function accuracy(predictions, labels) {
  let correct = 0;
  for (let index = 0; index < labels.length; index += 1) {
    if (predictions[index] === labels[index]) correct += 1;
  }
  return correct / labels.length;
}

function fitPhaseLookup(period, positions, labels) {
  const fallback = majorityLabel(labels);
  const counts = Array.from({ length: period }, () => [0, 0]);
  positions.forEach((position, index) => {
    counts[mod(position, period)][labels[index]] += 1;
  });
  return counts.map(([zeroCount, oneCount]) => {
    if (zeroCount + oneCount === 0) return fallback;
    return oneCount >= zeroCount ? 1 : 0;
  });
}

function predictPhaseLookup(period, lookup, positions) {
  return positions.map((position) => lookup[mod(position, period)]);
}

function nonperiodicThresholdLabel(position, threshold) {
  return position >= threshold ? 1 : 0;
}

function fitThresholdClassifier(positions, labels) {
  const start = Math.min(...positions);
  const stop = Math.max(...positions) + 1;
  let best = { score: -1, threshold: start, polarity: 1 };
  for (let threshold = start; threshold <= stop; threshold += 1) {
    for (const polarity of [1, -1]) {
      const predictions = positions.map((position) => (position >= threshold) === (polarity === 1) ? 1 : 0);
      const score = accuracy(predictions, labels);
      if (score > best.score) best = { score, threshold, polarity };
    }
  }
  return best;
}

function predictThresholdClassifier(positions, threshold, polarity) {
  return positions.map((position) => (position >= threshold) === (polarity === 1) ? 1 : 0);
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

function renderBudgetComparison({ loopPeriod, testTokenCount, maxBudget, requiredBudgets, learnedBudgets }) {
  chartIdCounter += 1;
  const visibleCount = Math.min(testTokenCount, 32);
  const width = 640;
  const height = 220;
  const left = 38;
  const right = 18;
  const top = 28;
  const rowGap = 18;
  const rowHeight = 70;
  const usableWidth = width - left - right;
  const titleId = `learned-token-title-${chartIdCounter}`;
  const descId = `learned-token-desc-${chartIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Learned token-level recurrence budgets";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `Required and learned held-out budgets repeat modulo loop period ${loopPeriod}.`;
  svg.append(title, desc);

  [
    ["required", requiredBudgets.slice(0, visibleCount), top, "#1357a6"],
    ["learned", learnedBudgets.slice(0, visibleCount), top + rowHeight + rowGap, "#2f855a"],
  ].forEach(([labelText, budgets, rowTop, fill]) => {
    const label = svgElement("text", { class: "node-label", x: 10, y: rowTop + 12 });
    label.textContent = labelText;
    svg.appendChild(label);
    budgets.forEach((budget, index) => {
      const x = left + (index * usableWidth) / visibleCount;
      const barWidth = Math.max(4, usableWidth / visibleCount - 3);
      const barHeight = (Math.min(budget, maxBudget) * rowHeight) / maxBudget;
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

function learnedFixture(values) {
  const trainTokens = range(0, values.trainTokenCount);
  const trainBudgets = tokenBudgets(values.loopPeriod, trainTokens);
  const testTokens = range(values.trainTokenCount, values.testTokenCount);
  const requiredBudgets = tokenBudgets(values.loopPeriod, testTokens);
  const labels = testTokens.map(() => 1);
  const learnedLookup = fitLoopBudgetLookup(values.loopPeriod, trainTokens, trainBudgets);
  const learnedBudgets = predictLoopBudgetLookup(values.loopPeriod, learnedLookup, testTokens)
    .map((budget) => Math.min(budget, values.maxBudget));
  const wrongLookup = fitLoopBudgetLookup(values.wrongPeriod, trainTokens, trainBudgets);
  const wrongPeriodBudgets = predictLoopBudgetLookup(values.wrongPeriod, wrongLookup, testTokens)
    .map((budget) => Math.min(budget, values.maxBudget));
  const fixedBudgets = testTokens.map(() => values.fixedGlobalBudget);
  const wrongShiftBudgets = shiftedBudgets(requiredBudgets, values.maxBudget, values.wrongBudgetShift);
  const overBudgets = testTokens.map(() => values.overLoopBudget);

  const controlThreshold = Math.floor((3 * values.trainTokenCount) / 4);
  const controlTrainLabels = trainTokens.map((token) => nonperiodicThresholdLabel(token, controlThreshold));
  const controlTestLabels = testTokens.map((token) => nonperiodicThresholdLabel(token, controlThreshold));
  const controlPhaseLookup = fitPhaseLookup(values.loopPeriod, trainTokens, controlTrainLabels);
  const controlPhasePredictions = predictPhaseLookup(values.loopPeriod, controlPhaseLookup, testTokens);
  const thresholdFit = fitThresholdClassifier(trainTokens, controlTrainLabels);
  const thresholdPredictions = predictThresholdClassifier(testTokens, thresholdFit.threshold, thresholdFit.polarity);
  const activeCounts = activeTokenCountsByBudget(learnedBudgets, values.maxBudget);

  return {
    learnedLookup,
    wrongLookup,
    requiredBudgets,
    learnedBudgets,
    wrongShiftBudgets,
    activeCounts,
    learnedAccuracy: accuracy(
      recurrenceBudgetPredictions(requiredBudgets, learnedBudgets, values.tolerance),
      labels,
    ),
    fixedAccuracy: accuracy(
      recurrenceBudgetPredictions(requiredBudgets, fixedBudgets, values.tolerance),
      labels,
    ),
    wrongPeriodAccuracy: accuracy(
      recurrenceBudgetPredictions(requiredBudgets, wrongPeriodBudgets, values.tolerance),
      labels,
    ),
    wrongShiftAccuracy: accuracy(
      recurrenceBudgetPredictions(requiredBudgets, wrongShiftBudgets, values.tolerance),
      labels,
    ),
    overLoopAccuracy: accuracy(
      recurrenceBudgetPredictions(requiredBudgets, overBudgets, values.tolerance),
      labels,
    ),
    nonperiodicPhaseAccuracy: accuracy(controlPhasePredictions, controlTestLabels),
    nonperiodicThresholdAccuracy: accuracy(thresholdPredictions, controlTestLabels),
  };
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
  title.textContent = "Learned token-level recurrence record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `loop period: ${values.loopPeriod}`,
    `wrong/control period: ${values.wrongPeriod}`,
    `train tokens: ${values.trainTokenCount}`,
    `held-out test tokens: ${values.testTokenCount}`,
    `max budget: ${values.maxBudget}`,
    `learned budget lookup: ${fixture.learnedLookup.join(", ")}`,
    `wrong-period lookup: ${fixture.wrongLookup.join(", ")}`,
    `required budget sample: ${fixture.requiredBudgets.slice(0, 12).join(", ")}`,
    `learned budget sample: ${fixture.learnedBudgets.slice(0, 12).join(", ")}`,
    `token budget at sample zero: ${tokenBudget(values.loopPeriod, 0)}`,
    `wrong-shift sample: ${fixture.wrongShiftBudgets.slice(0, 12).join(", ")}`,
    `active token counts by loop step: ${fixture.activeCounts.join(", ")}`,
    `average active tokens: ${(fixture.activeCounts.reduce((total, count) => total + count, 0) / fixture.activeCounts.length).toFixed(2)}`,
    `learned token-router accuracy: ${percent(fixture.learnedAccuracy)}`,
    `fixed-budget accuracy: ${percent(fixture.fixedAccuracy)}`,
    `wrong-period router accuracy: ${percent(fixture.wrongPeriodAccuracy)}`,
    `wrong-shift accuracy: ${percent(fixture.wrongShiftAccuracy)}`,
    `over-loop accuracy: ${percent(fixture.overLoopAccuracy)}`,
    `nonperiodic phase-lookup accuracy: ${percent(fixture.nonperiodicPhaseAccuracy)}`,
    `nonperiodic scalar-threshold accuracy: ${percent(fixture.nonperiodicThresholdAccuracy)}`,
    "boundary: widget output is learned lookup-table bookkeeping for a constructed finite fixture, not a neural router, recursive-reasoning, throughput, memory, context-length, or model-quality claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Learned token-level recurrence", "Widget: learned lookup-table bookkeeping only");
  const periodInput = addLabeledNumber(panel, "ai-learned-token-loop-period", "loop period", 4, 1, 16);
  const wrongPeriodInput = addLabeledNumber(panel, "ai-learned-token-wrong-period", "wrong period", 3, 1, 16);
  const trainInput = addLabeledNumber(panel, "ai-learned-token-train-count", "train tokens", 64, 4, 256);
  const testInput = addLabeledNumber(panel, "ai-learned-token-test-count", "test tokens", 32, 1, 96);
  const maxBudgetInput = addLabeledNumber(panel, "ai-learned-token-max-budget", "max budget", 4, 1, 16);
  const fixedBudgetInput = addLabeledNumber(panel, "ai-learned-token-fixed-budget", "fixed budget", 4, 1, 32);
  const wrongShiftInput = addLabeledNumber(panel, "ai-learned-token-wrong-shift", "wrong shift", 1, 1, 15);
  const overBudgetInput = addLabeledNumber(panel, "ai-learned-token-over-budget", "over budget", 8, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-learned-token-tolerance", "tolerance", 0, 0, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const loopPeriod = positiveInt(periodInput.value, 4, 1, 16);
    let wrongPeriod = positiveInt(wrongPeriodInput.value, 3, 1, 16);
    if (wrongPeriod === loopPeriod) wrongPeriod = loopPeriod === 1 ? 2 : loopPeriod - 1;
    const values = {
      loopPeriod,
      wrongPeriod,
      trainTokenCount: positiveInt(trainInput.value, 64, 4, 256),
      testTokenCount: positiveInt(testInput.value, 32, 1, 96),
      maxBudget: Math.max(positiveInt(maxBudgetInput.value, 4, 1, 16), loopPeriod),
      fixedGlobalBudget: positiveInt(fixedBudgetInput.value, 4, 1, 32),
      wrongBudgetShift: positiveInt(wrongShiftInput.value, 1, 1, 15),
      overLoopBudget: positiveInt(overBudgetInput.value, 8, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 0, 0, 8),
    };
    const fixture = learnedFixture(values);
    clear(output);
    output.appendChild(renderBudgetComparison({
      loopPeriod: values.loopPeriod,
      testTokenCount: values.testTokenCount,
      maxBudget: values.maxBudget,
      requiredBudgets: fixture.requiredBudgets,
      learnedBudgets: fixture.learnedBudgets,
    }));
    appendRecord(output, values, fixture, theoremById);
  }

  for (const input of [
    periodInput,
    wrongPeriodInput,
    trainInput,
    testInput,
    maxBudgetInput,
    fixedBudgetInput,
    wrongShiftInput,
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

mountWidgets("learned_token_recurrence", mount);
