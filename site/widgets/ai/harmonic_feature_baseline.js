import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIA-T0005"];
const DICTIONARY_IDS = ["COMMON-0026", "COMMON-0027", "COMMON-0046"];

function phaseChannel(period, position) {
  return mod(position, period);
}

function defaultPositivePhases(period) {
  return Array.from({ length: period }, (_, phase) => phase).filter((phase) => phase % 3 === 1);
}

function periodicPhaseLabel(period, position, positivePhases) {
  return positivePhases.includes(phaseChannel(period, position)) ? 1 : 0;
}

function round12(value) {
  const rounded = Math.round(value * 1e12) / 1e12;
  return Object.is(rounded, -0) ? 0 : rounded;
}

function harmonicFeature(period, position, harmonic = 1) {
  const angle = (2 * Math.PI * harmonic * phaseChannel(period, position)) / period;
  return [round12(Math.cos(angle)), round12(Math.sin(angle))];
}

function featureKey(feature) {
  return `${feature[0].toFixed(12)},${feature[1].toFixed(12)}`;
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
    counts[phaseChannel(period, position)][labels[index]] += 1;
  });
  return counts.map(([zeroCount, oneCount]) => {
    if (zeroCount + oneCount === 0) return fallback;
    return oneCount >= zeroCount ? 1 : 0;
  });
}

function predictPhaseLookup(period, lookup, positions) {
  return positions.map((position) => lookup[phaseChannel(period, position)]);
}

function fitHarmonicFeatureLookup(period, positions, labels) {
  const counts = new Map();
  positions.forEach((position, index) => {
    const feature = harmonicFeature(period, position);
    const key = featureKey(feature);
    if (!counts.has(key)) {
      counts.set(key, { feature, zero: 0, one: 0 });
    }
    if (labels[index] === 1) counts.get(key).one += 1;
    else counts.get(key).zero += 1;
  });
  return Array.from(counts.values())
    .map((entry) => ({
      feature: entry.feature,
      label: entry.one >= entry.zero ? 1 : 0,
    }))
    .sort((left, right) => featureKey(left.feature).localeCompare(featureKey(right.feature)));
}

function predictHarmonicFeatureLookup(period, lookup, positions) {
  const lookupMap = new Map(lookup.map((entry) => [featureKey(entry.feature), entry.label]));
  const fallback = majorityLabel(lookup.map((entry) => entry.label));
  return positions.map((position) => {
    const key = featureKey(harmonicFeature(period, position));
    return lookupMap.has(key) ? lookupMap.get(key) : fallback;
  });
}

function fitPositionLookup(positions, labels) {
  const fallback = majorityLabel(labels);
  const counts = new Map();
  positions.forEach((position, index) => {
    if (!counts.has(position)) counts.set(position, [0, 0]);
    counts.get(position)[labels[index]] += 1;
  });
  const entries = Array.from(counts.entries())
    .map(([position, [zeroCount, oneCount]]) => [position, oneCount >= zeroCount ? 1 : 0])
    .sort((left, right) => left[0] - right[0]);
  return { fallback, entries };
}

function predictPositionLookup(lookup, positions) {
  const lookupMap = new Map(lookup.entries);
  return positions.map((position) => (lookupMap.has(position) ? lookupMap.get(position) : lookup.fallback));
}

function nonperiodicThresholdLabel(position, threshold) {
  return position >= threshold ? 1 : 0;
}

function accuracy(predictions, labels) {
  let correct = 0;
  predictions.forEach((prediction, index) => {
    if (prediction === labels[index]) correct += 1;
  });
  return correct / labels.length;
}

function fitThresholdClassifier(positions, labels) {
  let best = { score: -1, threshold: Math.min(...positions), polarity: 1 };
  for (let threshold = Math.min(...positions); threshold <= Math.max(...positions) + 1; threshold += 1) {
    for (const polarity of [1, -1]) {
      const predictions = positions.map((position) =>
        (position >= threshold) === (polarity === 1) ? 1 : 0
      );
      const score = accuracy(predictions, labels);
      if (score > best.score) best = { score, threshold, polarity };
    }
  }
  return best;
}

function predictThresholdClassifier(positions, threshold, polarity) {
  return positions.map((position) => (position >= threshold) === (polarity === 1) ? 1 : 0);
}

function formatNumber(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

function benchmark(values) {
  const positivePhases = defaultPositivePhases(values.period);
  const trainPositions = Array.from({ length: values.trainLength }, (_, index) => index);
  const testPositions = Array.from({ length: values.testLength }, (_, index) => values.trainLength + index);
  const trainLabels = trainPositions.map((position) =>
    periodicPhaseLabel(values.period, position, positivePhases)
  );
  const testLabels = testPositions.map((position) =>
    periodicPhaseLabel(values.period, position, positivePhases)
  );

  const phaseLookup = fitPhaseLookup(values.period, trainPositions, trainLabels);
  const phasePredictions = predictPhaseLookup(values.period, phaseLookup, testPositions);
  const harmonicLookup = fitHarmonicFeatureLookup(values.period, trainPositions, trainLabels);
  const harmonicPredictions = predictHarmonicFeatureLookup(values.period, harmonicLookup, testPositions);
  const wrongLookup = fitHarmonicFeatureLookup(values.wrongPeriod, trainPositions, trainLabels);
  const wrongPredictions = predictHarmonicFeatureLookup(values.wrongPeriod, wrongLookup, testPositions);
  const threshold = fitThresholdClassifier(trainPositions, trainLabels);
  const thresholdPredictions = predictThresholdClassifier(testPositions, threshold.threshold, threshold.polarity);
  const positionLookup = fitPositionLookup(trainPositions, trainLabels);
  const positionPredictions = predictPositionLookup(positionLookup, testPositions);

  const controlThreshold = Math.floor((3 * values.trainLength) / 4);
  const controlTrainLabels = trainPositions.map((position) => nonperiodicThresholdLabel(position, controlThreshold));
  const controlTestLabels = testPositions.map((position) => nonperiodicThresholdLabel(position, controlThreshold));
  const controlHarmonicLookup = fitHarmonicFeatureLookup(values.period, trainPositions, controlTrainLabels);
  const controlHarmonicPredictions = predictHarmonicFeatureLookup(
    values.period,
    controlHarmonicLookup,
    testPositions,
  );
  const controlThresholdFit = fitThresholdClassifier(trainPositions, controlTrainLabels);
  const controlThresholdPredictions = predictThresholdClassifier(
    testPositions,
    controlThresholdFit.threshold,
    controlThresholdFit.polarity,
  );

  return {
    positivePhases,
    phaseLookup,
    harmonicLookup,
    sampleFeature: harmonicFeature(values.period, 1),
    controlThreshold,
    cyclicPhaseAccuracy: accuracy(phasePredictions, testLabels),
    harmonicFeatureAccuracy: accuracy(harmonicPredictions, testLabels),
    wrongHarmonicAccuracy: accuracy(wrongPredictions, testLabels),
    scalarThresholdAccuracy: accuracy(thresholdPredictions, testLabels),
    learnedPositionAccuracy: accuracy(positionPredictions, testLabels),
    nonperiodicHarmonicAccuracy: accuracy(controlHarmonicPredictions, controlTestLabels),
    nonperiodicScalarThresholdAccuracy: accuracy(controlThresholdPredictions, controlTestLabels),
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
  title.textContent = "Finite phase theorems";
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

function appendMetricsTable(section, result) {
  const rows = [
    ["cyclic phase lookup", result.cyclicPhaseAccuracy, "same finite phase, integer key"],
    ["correct sine/cosine lookup", result.harmonicFeatureAccuracy, "same phase as Fourier-style feature"],
    ["wrong-frequency sine/cosine", result.wrongHarmonicAccuracy, "frequency-control baseline"],
    ["scalar threshold", result.scalarThresholdAccuracy, "ordinary position-threshold control"],
    ["learned absolute position", result.learnedPositionAccuracy, "memorization control"],
    ["nonperiodic sine/cosine", result.nonperiodicHarmonicAccuracy, "wrong inductive bias control"],
    ["nonperiodic scalar threshold", result.nonperiodicScalarThresholdAccuracy, "ordinary control should win"],
  ];
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["fixture", "accuracy", "role"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    row.forEach((value) => {
      const td = document.createElement("td");
      td.textContent = typeof value === "number" ? formatNumber(value) : value;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  section.appendChild(table);
}

function appendRecord(output, values, theoremById) {
  const result = benchmark(values);
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Harmonic/Fourier feature baseline record";
  section.appendChild(title);
  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    "fixture id: AIA-B0005",
    `period / wrong period: ${values.period} / ${values.wrongPeriod}`,
    `train/test length: ${values.trainLength}/${values.testLength}`,
    `positive phases: ${result.positivePhases.join(", ")}`,
    `phase lookup: ${result.phaseLookup.join(", ")}`,
    `observed harmonic features: ${result.harmonicLookup.length}`,
    `sample feature for position 1: (${result.sampleFeature.map(formatNumber).join(", ")})`,
    `nonperiodic scalar threshold: ${result.controlThreshold}`,
    "boundary: Lean certifies finite phase indexing; this fixture is executable benchmark scaffolding.",
  ].join("\n");
  section.appendChild(data);
  appendMetricsTable(section, result);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this is a deterministic synthetic Fourier-style feature-control fixture. It is not RoPE evidence, a language-model benchmark, a speed claim, or proof that harmonic features help real AI workloads.";
  section.appendChild(warning);
  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Harmonic/Fourier feature baseline", "Widget: sine/cosine phase-control fixture");
  const periodInput = addLabeledNumber(panel, "ai-harmonic-period", "period", 8, 2, 32);
  const wrongPeriodInput = addLabeledNumber(panel, "ai-harmonic-wrong-period", "wrong period", 7, 2, 32);
  const trainInput = addLabeledNumber(panel, "ai-harmonic-train", "train length", 64, 1, 256);
  const testInput = addLabeledNumber(panel, "ai-harmonic-test", "test length", 32, 1, 256);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      period: positiveInt(periodInput.value, 8, 2, 32),
      wrongPeriod: positiveInt(wrongPeriodInput.value, 7, 2, 32),
      trainLength: positiveInt(trainInput.value, 64, 1, 256),
      testLength: positiveInt(testInput.value, 32, 1, 256),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [periodInput, wrongPeriodInput, trainInput, testInput]) {
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

mountWidgets("harmonic_feature_baseline", mount);
