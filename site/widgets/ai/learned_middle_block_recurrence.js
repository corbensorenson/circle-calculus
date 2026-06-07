import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018"];
const DICTIONARY_IDS = ["COMMON-0052", "COMMON-0053", "COMMON-0059", "COMMON-0068", "COMMON-0070"];

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

function loopBlockIndices(blockCount, selectedBlock) {
  const [start, stop] = selectedBlock;
  const boundedStop = Math.min(stop, blockCount);
  return range(start, Math.max(1, boundedStop - start));
}

function middleBlockRequiredBlocks(blockCount, selectedBlock, samples) {
  const selected = loopBlockIndices(blockCount, selectedBlock);
  return samples.map((sample) => selected[mod(sample, selected.length)]);
}

function majorityInt(values) {
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
  return Array.from(counts.entries())
    .sort(([leftValue, leftCount], [rightValue, rightCount]) => (
      rightCount - leftCount || leftValue - rightValue
    ))[0][0];
}

function fitLookup(period, positions, values) {
  const fallback = majorityInt(values);
  const buckets = Array.from({ length: period }, () => []);
  positions.forEach((position, index) => {
    buckets[mod(position, period)].push(values[index]);
  });
  return buckets.map((bucket) => (bucket.length === 0 ? fallback : majorityInt(bucket)));
}

function predictLookup(period, lookup, positions) {
  return positions.map((position) => lookup[mod(position, period)]);
}

function activeCountsByBudget(budgets, maxBudget) {
  return Array.from({ length: maxBudget }, (_, index) => {
    const step = index + 1;
    return budgets.filter((budget) => budget >= step).length;
  });
}

function middleBlockPredictions(requiredBlocks, requiredBudgets, candidateBlocks, plannedBudgets, tolerance) {
  const candidateSet = new Set(candidateBlocks);
  return requiredBlocks.map((requiredBlock, index) => {
    const requiredBudget = requiredBudgets[index];
    const plannedBudget = plannedBudgets[index];
    return candidateSet.has(requiredBlock)
      && requiredBudget <= plannedBudget
      && plannedBudget <= requiredBudget + tolerance
      ? 1
      : 0;
  });
}

function sampledMiddleBlockPredictions(requiredBlocks, requiredBudgets, plannedBlocks, plannedBudgets, tolerance) {
  return requiredBlocks.map((requiredBlock, index) => {
    const requiredBudget = requiredBudgets[index];
    const plannedBlock = plannedBlocks[index];
    const plannedBudget = plannedBudgets[index];
    return requiredBlock === plannedBlock
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
  const selectedBlocks = loopBlockIndices(values.blockCount, values.selectedLoopBlock);
  const wrongBlocks = loopBlockIndices(values.blockCount, values.wrongLoopBlock);
  const fullBlocks = range(0, values.blockCount);
  const blockPeriod = selectedBlocks.length;
  const trainRequiredBlocks = middleBlockRequiredBlocks(values.blockCount, values.selectedLoopBlock, trainSamples);
  const trainBudgets = tokenBudgets(values.loopPeriod, trainSamples);
  const requiredBlocks = middleBlockRequiredBlocks(values.blockCount, values.selectedLoopBlock, testSamples);
  const requiredBudgets = tokenBudgets(values.loopPeriod, testSamples);
  const learnedBlockLookup = fitLookup(blockPeriod, trainSamples, trainRequiredBlocks);
  const learnedBlocks = predictLookup(blockPeriod, learnedBlockLookup, testSamples);
  const learnedBudgetLookup = fitLookup(values.loopPeriod, trainSamples, trainBudgets);
  const learnedBudgets = predictLookup(values.loopPeriod, learnedBudgetLookup, testSamples)
    .map((budget) => Math.min(budget, values.maxBudget));
  const wrongBlockLookup = fitLookup(values.wrongBlockPeriod, trainSamples, trainRequiredBlocks);
  const wrongPeriodBlocks = predictLookup(values.wrongBlockPeriod, wrongBlockLookup, testSamples);
  const wrongBudgetLookup = fitLookup(values.wrongBudgetPeriod, trainSamples, trainBudgets);
  const wrongPeriodBudgets = predictLookup(values.wrongBudgetPeriod, wrongBudgetLookup, testSamples)
    .map((budget) => Math.min(budget, values.maxBudget));
  const fixedBudgets = testSamples.map(() => values.fixedLoopBudget);
  const overBudgets = testSamples.map(() => values.overLoopBudget);
  const activeCounts = activeCountsByBudget(learnedBudgets, values.maxBudget);
  const averageBudget = learnedBudgets.reduce((total, budget) => total + budget, 0) / learnedBudgets.length;

  return {
    selectedBlocks,
    wrongBlocks,
    blockPeriod,
    learnedBlockLookup,
    learnedBudgetLookup,
    wrongBlockLookup,
    wrongBudgetLookup,
    requiredBlocks,
    learnedBlocks,
    wrongPeriodBlocks,
    requiredBudgets,
    learnedBudgets,
    wrongPeriodBudgets,
    activeCounts,
    learnedAccuracy: accuracy(sampledMiddleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      learnedBlocks,
      learnedBudgets,
      values.tolerance,
    )),
    selectedBandAccuracy: accuracy(middleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      selectedBlocks,
      learnedBudgets,
      values.tolerance,
    )),
    fullBlockAccuracy: accuracy(middleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      fullBlocks,
      learnedBudgets,
      values.tolerance,
    )),
    fixedBudgetAccuracy: accuracy(sampledMiddleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      learnedBlocks,
      fixedBudgets,
      values.tolerance,
    )),
    wrongBlockPeriodAccuracy: accuracy(sampledMiddleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      wrongPeriodBlocks,
      learnedBudgets,
      values.tolerance,
    )),
    wrongBudgetPeriodAccuracy: accuracy(sampledMiddleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      learnedBlocks,
      wrongPeriodBudgets,
      values.tolerance,
    )),
    wrongLoopBlockAccuracy: accuracy(middleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      wrongBlocks,
      learnedBudgets,
      values.tolerance,
    )),
    overLoopAccuracy: accuracy(sampledMiddleBlockPredictions(
      requiredBlocks,
      requiredBudgets,
      learnedBlocks,
      overBudgets,
      values.tolerance,
    )),
    averageLearnedBlockPasses: averageBudget,
    averageSelectedBandPasses: averageBudget * selectedBlocks.length,
    averageFullBlockPasses: averageBudget * fullBlocks.length,
  };
}

function renderBlockBudgetChart({ values, fixture }) {
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
  const titleId = `learned-middle-block-title-${chartIdCounter}`;
  const descId = `learned-middle-block-desc-${chartIdCounter}`;
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });
  const title = svgElement("title", { id: titleId });
  title.textContent = "Learned middle-block recurrence route";
  const desc = svgElement("desc", { id: descId });
  desc.textContent = `First ${visibleCount} held-out samples, showing required and learned block-budget routes.`;
  svg.append(title, desc);

  [
    ["required", fixture.requiredBlocks, fixture.requiredBudgets, top, "#1357a6"],
    ["learned", fixture.learnedBlocks, fixture.learnedBudgets, top + rowHeight + rowGap, "#2f855a"],
  ].forEach(([labelText, blocks, budgets, rowTop, fill]) => {
    const rowLabel = svgElement("text", { class: "node-label", x: 8, y: rowTop + 12 });
    rowLabel.textContent = labelText;
    svg.appendChild(rowLabel);
    blocks.slice(0, visibleCount).forEach((block, index) => {
      const budget = budgets[index];
      const x = left + (index * usableWidth) / visibleCount;
      const cellWidth = Math.max(7, usableWidth / visibleCount - 3);
      const cellHeight = Math.max(14, (Math.min(budget, values.maxBudget) * rowHeight) / values.maxBudget);
      const rect = svgElement("rect", {
        x,
        y: rowTop + rowHeight - cellHeight,
        width: cellWidth,
        height: cellHeight,
        fill,
        rx: 2,
      });
      const label = svgElement("text", {
        class: "node-label",
        x: x + cellWidth / 2,
        y: rowTop + rowHeight + 16,
      });
      label.textContent = String(block);
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
  title.textContent = "Learned middle-block recurrence record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `block count: ${values.blockCount}`,
    `selected loop block: [${values.selectedLoopBlock[0]}, ${values.selectedLoopBlock[1]})`,
    `selected block indices: ${fixture.selectedBlocks.join(", ")}`,
    `loop period: ${values.loopPeriod}`,
    `block period: ${fixture.blockPeriod}`,
    `wrong block period: ${values.wrongBlockPeriod}`,
    `wrong budget period: ${values.wrongBudgetPeriod}`,
    `train samples: ${values.trainLength}`,
    `held-out test samples: ${values.testLength}`,
    `learned block lookup: ${fixture.learnedBlockLookup.join(", ")}`,
    `learned budget lookup: ${fixture.learnedBudgetLookup.join(", ")}`,
    `wrong block-period lookup: ${fixture.wrongBlockLookup.join(", ")}`,
    `wrong budget-period lookup: ${fixture.wrongBudgetLookup.join(", ")}`,
    `required block sample: ${fixture.requiredBlocks.slice(0, 12).join(", ")}`,
    `learned block sample: ${fixture.learnedBlocks.slice(0, 12).join(", ")}`,
    `wrong block sample: ${fixture.wrongPeriodBlocks.slice(0, 12).join(", ")}`,
    `required budget sample: ${fixture.requiredBudgets.slice(0, 12).join(", ")}`,
    `learned budget sample: ${fixture.learnedBudgets.slice(0, 12).join(", ")}`,
    `wrong budget sample: ${fixture.wrongPeriodBudgets.slice(0, 12).join(", ")}`,
    `active sample counts by loop step: ${fixture.activeCounts.join(", ")}`,
    `learned middle-block router accuracy: ${percent(fixture.learnedAccuracy)}`,
    `selected-band phase-budget accuracy: ${percent(fixture.selectedBandAccuracy)}`,
    `full-block phase-budget accuracy: ${percent(fixture.fullBlockAccuracy)}`,
    `fixed-budget accuracy: ${percent(fixture.fixedBudgetAccuracy)}`,
    `wrong block-period accuracy: ${percent(fixture.wrongBlockPeriodAccuracy)}`,
    `wrong budget-period accuracy: ${percent(fixture.wrongBudgetPeriodAccuracy)}`,
    `wrong loop-block accuracy: ${percent(fixture.wrongLoopBlockAccuracy)}`,
    `over-loop accuracy: ${percent(fixture.overLoopAccuracy)}`,
    `average learned block passes: ${fixture.averageLearnedBlockPasses.toFixed(2)}`,
    `average selected-band passes: ${fixture.averageSelectedBandPasses.toFixed(2)}`,
    `average full-block passes: ${fixture.averageFullBlockPasses.toFixed(2)}`,
    "boundary: widget output is learned middle-block schedule bookkeeping for a constructed finite fixture, not a neural router, recursive-reasoning, throughput, memory, context-length, or model-quality claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Learned middle-block recurrence", "Widget: block and loop-budget bookkeeping only");
  const blockCountInput = addLabeledNumber(panel, "ai-middle-block-count", "block count", 8, 6, 24);
  const selectedStartInput = addLabeledNumber(panel, "ai-middle-selected-start", "selected start", 2, 0, 20);
  const selectedStopInput = addLabeledNumber(panel, "ai-middle-selected-stop", "selected stop", 5, 1, 24);
  const wrongStartInput = addLabeledNumber(panel, "ai-middle-wrong-start", "wrong start", 0, 0, 20);
  const wrongStopInput = addLabeledNumber(panel, "ai-middle-wrong-stop", "wrong stop", 2, 1, 24);
  const loopPeriodInput = addLabeledNumber(panel, "ai-middle-loop-period", "loop period", 4, 1, 16);
  const wrongBlockPeriodInput = addLabeledNumber(panel, "ai-middle-wrong-block-period", "wrong block period", 2, 1, 16);
  const wrongBudgetPeriodInput = addLabeledNumber(panel, "ai-middle-wrong-budget-period", "wrong budget period", 3, 1, 16);
  const trainLengthInput = addLabeledNumber(panel, "ai-middle-train-length", "train samples", 64, 4, 256);
  const testLengthInput = addLabeledNumber(panel, "ai-middle-test-length", "test samples", 32, 1, 96);
  const maxBudgetInput = addLabeledNumber(panel, "ai-middle-max-budget", "max budget", 4, 1, 16);
  const fixedBudgetInput = addLabeledNumber(panel, "ai-middle-fixed-budget", "fixed budget", 4, 1, 32);
  const overBudgetInput = addLabeledNumber(panel, "ai-middle-over-budget", "over budget", 8, 1, 64);
  const toleranceInput = addLabeledNumber(panel, "ai-middle-tolerance", "tolerance", 0, 0, 8);
  const output = addOutput(panel);
  let theoremById = new Map();

  function normalizedBlockRange(startInput, stopInput, blockCount) {
    const start = positiveInt(startInput.value, 0, 0, blockCount - 1);
    const stop = positiveInt(stopInput.value, start + 1, start + 1, blockCount);
    return [start, stop];
  }

  function render() {
    const blockCount = positiveInt(blockCountInput.value, 8, 6, 24);
    const selectedLoopBlock = normalizedBlockRange(selectedStartInput, selectedStopInput, blockCount);
    const wrongLoopBlock = normalizedBlockRange(wrongStartInput, wrongStopInput, blockCount);
    const loopPeriod = positiveInt(loopPeriodInput.value, 4, 1, 16);
    const maxBudget = Math.max(positiveInt(maxBudgetInput.value, 4, 1, 16), loopPeriod);
    const blockPeriod = selectedLoopBlock[1] - selectedLoopBlock[0];
    let wrongBlockPeriod = positiveInt(wrongBlockPeriodInput.value, 2, 1, 16);
    if (wrongBlockPeriod === blockPeriod) wrongBlockPeriod = blockPeriod === 1 ? 2 : blockPeriod - 1;
    let wrongBudgetPeriod = positiveInt(wrongBudgetPeriodInput.value, 3, 1, 16);
    if (wrongBudgetPeriod === loopPeriod) wrongBudgetPeriod = loopPeriod === 1 ? 2 : loopPeriod - 1;
    const values = {
      blockCount,
      selectedLoopBlock,
      wrongLoopBlock,
      loopPeriod,
      wrongBlockPeriod,
      wrongBudgetPeriod,
      trainLength: positiveInt(trainLengthInput.value, 64, 4, 256),
      testLength: positiveInt(testLengthInput.value, 32, 1, 96),
      maxBudget,
      fixedLoopBudget: positiveInt(fixedBudgetInput.value, 4, 1, 32),
      overLoopBudget: positiveInt(overBudgetInput.value, 8, 1, 64),
      tolerance: positiveInt(toleranceInput.value, 0, 0, 8),
    };
    const fixture = learnedFixture(values);
    clear(output);
    output.appendChild(renderBlockBudgetChart({ values, fixture }));
    appendRecord(output, values, fixture, theoremById);
  }

  for (const input of [
    blockCountInput,
    selectedStartInput,
    selectedStopInput,
    wrongStartInput,
    wrongStopInput,
    loopPeriodInput,
    wrongBlockPeriodInput,
    wrongBudgetPeriodInput,
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

mountWidgets("learned_middle_block_recurrence", mount);
