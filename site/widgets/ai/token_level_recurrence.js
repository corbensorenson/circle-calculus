import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018", "AIM-T0022", "AIM-T0026", "AIM-T0027", "AIM-T0035", "AIM-T0036", "AIM-T0037", "AIM-T0038"];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0059", "COMMON-0068", "COMMON-0069"];

let stripIdCounter = 0;

function tokenBudget(loopPeriod, token) {
  return mod(token, loopPeriod) + 1;
}

function tokenBudgets(loopPeriod, tokenCount) {
  return Array.from({ length: tokenCount }, (_, token) => tokenBudget(loopPeriod, token));
}

function activeTokenCountsByBudget(budgets, maxBudget) {
  return Array.from({ length: maxBudget }, (_, index) => {
    const step = index + 1;
    return budgets.filter((budget) => budget >= step).length;
  });
}

function recurrenceResolutionLevels(maxBudget) {
  return Array.from({ length: maxBudget }, (_, index) => ((index + 1) % 2 === 1 ? "coarse" : "fine"));
}

function shiftedBudgets(budgets, maxBudget, shift) {
  return budgets.map((budget) => mod(budget - 1 + shift, maxBudget) + 1);
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

function majorityLabel(labels) {
  const positives = labels.filter((label) => label === 1).length;
  const negatives = labels.length - positives;
  return positives >= negatives ? 1 : 0;
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

function renderBudgetStrip({ loopPeriod, tokenCount, maxBudget }) {
  stripIdCounter += 1;
  const budgets = tokenBudgets(loopPeriod, tokenCount);
  const visibleCount = Math.min(tokenCount, 32);
  const visibleBudgets = budgets.slice(0, visibleCount);
  const width = 640;
  const height = 190;
  const left = 36;
  const right = 18;
  const bottom = 42;
  const top = 24;
  const usableWidth = width - left - right;
  const usableHeight = height - top - bottom;
  const titleId = `token-recurrence-title-${stripIdCounter}`;
  const descId = `token-recurrence-desc-${stripIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });

  const title = svgElement("title", { id: titleId });
  title.textContent = "Token-level recurrence budget strip";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `First ${visibleCount} of ${tokenCount} tokens, with budgets repeating modulo loop period ${loopPeriod}.`;
  svg.append(title, desc);

  for (let step = 1; step <= maxBudget; step += 1) {
    const y = top + usableHeight - (step * usableHeight) / maxBudget;
    const label = svgElement("text", { class: "node-label", x: 16, y: y + 4 });
    label.textContent = String(step);
    svg.appendChild(label);
  }

  visibleBudgets.forEach((budget, token) => {
    const x = left + (token * usableWidth) / visibleCount;
    const barWidth = Math.max(4, usableWidth / visibleCount - 3);
    const capped = Math.min(budget, maxBudget);
    const barHeight = (capped * usableHeight) / maxBudget;
    const rect = svgElement("rect", {
      x,
      y: top + usableHeight - barHeight,
      width: barWidth,
      height: barHeight,
      fill: token % 2 === 0 ? "#1357a6" : "#2f855a",
      rx: 2,
    });
    const label = svgElement("text", {
      class: "node-label",
      x: x + barWidth / 2,
      y: height - 18,
    });
    label.textContent = String(token);
    svg.append(rect, label);
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

function appendRecord(output, values, theoremById) {
  const tokens = Array.from({ length: values.tokenCount }, (_, token) => token);
  const budgets = tokenBudgets(values.loopPeriod, values.tokenCount);
  const routedBudgets = budgets.map((budget) => Math.min(budget, values.maxBudget));
  const fixedBudgets = tokens.map(() => values.fixedGlobalBudget);
  const wrongBudgets = shiftedBudgets(budgets, values.maxBudget, values.wrongBudgetShift);
  const overBudgets = tokens.map(() => values.overLoopBudget);
  const labels = tokens.map(() => 1);
  const activeCounts = activeTokenCountsByBudget(budgets, values.maxBudget);
  const tokenPredictions = recurrenceBudgetPredictions(budgets, routedBudgets, values.tolerance);
  const fixedPredictions = recurrenceBudgetPredictions(budgets, fixedBudgets, values.tolerance);
  const wrongPredictions = recurrenceBudgetPredictions(budgets, wrongBudgets, values.tolerance);
  const overPredictions = recurrenceBudgetPredictions(budgets, overBudgets, values.tolerance);
  const threshold = Math.floor((3 * values.tokenCount) / 4);
  const controlLabels = tokens.map((token) => nonperiodicThresholdLabel(token, threshold));
  const controlLookup = fitPhaseLookup(values.loopPeriod, tokens, controlLabels);
  const controlLoopPredictions = predictPhaseLookup(values.loopPeriod, controlLookup, tokens);
  const thresholdFit = fitThresholdClassifier(tokens, controlLabels);
  const thresholdPredictions = predictThresholdClassifier(tokens, thresholdFit.threshold, thresholdFit.polarity);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Token-level recurrence record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `loop period: ${values.loopPeriod}`,
    `token count: ${values.tokenCount}`,
    `max budget: ${values.maxBudget}`,
    `selected middle block: [2, 5)`,
    `resolution levels: ${recurrenceResolutionLevels(values.maxBudget).join(", ")}`,
    `token budgets sample: ${budgets.slice(0, Math.min(16, budgets.length)).join(", ")}`,
    `active token counts by loop step: ${activeCounts.join(", ")}`,
    `active-step boundary: step 1 active for every token; steps > loop period inactive`,
    `average active tokens: ${(activeCounts.reduce((total, count) => total + count, 0) / activeCounts.length).toFixed(2)}`,
    `fixed global budget: ${values.fixedGlobalBudget}`,
    `wrong budget shift: ${values.wrongBudgetShift}`,
    `over-loop budget: ${values.overLoopBudget}`,
    `token-level accuracy: ${percent(accuracy(tokenPredictions, labels))}`,
    `fixed-budget accuracy: ${percent(accuracy(fixedPredictions, labels))}`,
    `wrong-budget accuracy: ${percent(accuracy(wrongPredictions, labels))}`,
    `over-loop accuracy: ${percent(accuracy(overPredictions, labels))}`,
    `nonperiodic phase-lookup accuracy: ${percent(accuracy(controlLoopPredictions, controlLabels))}`,
    `nonperiodic scalar-threshold accuracy: ${percent(accuracy(thresholdPredictions, controlLabels))}`,
    "boundary: widget output is deterministic token-level schedule bookkeeping, not a learned-router or model-quality claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Token-level recurrence routing", "Widget: per-token schedule bookkeeping only");
  const periodInput = addLabeledNumber(panel, "ai-token-loop-period", "loop period", 4, 1, 16);
  const tokenCountInput = addLabeledNumber(panel, "ai-token-count", "token count", 32, 1, 96);
  const maxBudgetInput = addLabeledNumber(panel, "ai-token-max-budget", "max budget", 4, 1, 16);
  const fixedBudgetInput = addLabeledNumber(panel, "ai-token-fixed-budget", "fixed budget", 4, 1, 32);
  const wrongShiftInput = addLabeledNumber(panel, "ai-token-wrong-shift", "wrong shift", 1, 1, 15);
  const overBudgetInput = addLabeledNumber(panel, "ai-token-over-budget", "over budget", 8, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-token-tolerance", "tolerance", 0, 0, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      loopPeriod: positiveInt(periodInput.value, 4, 1, 16),
      tokenCount: positiveInt(tokenCountInput.value, 32, 1, 96),
      maxBudget: positiveInt(maxBudgetInput.value, 4, 1, 16),
      fixedGlobalBudget: positiveInt(fixedBudgetInput.value, 4, 1, 32),
      wrongBudgetShift: positiveInt(wrongShiftInput.value, 1, 1, 15),
      overLoopBudget: positiveInt(overBudgetInput.value, 8, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 0, 0, 8),
    };
    clear(output);
    output.appendChild(renderBudgetStrip(values));
    appendRecord(output, values, theoremById);
  }

  for (const input of [
    periodInput,
    tokenCountInput,
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

mountWidgets("token_level_recurrence", mount);
