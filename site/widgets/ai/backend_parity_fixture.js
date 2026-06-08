import { mod } from "../shared/circle_math_core.js";
import { addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIA-T0001", "AIM-T0001", "AIM-T0015", "AIRA-T0001"];
const DICTIONARY_IDS = [
  "COMMON-0026",
  "COMMON-0028",
  "COMMON-0030",
  "COMMON-0046",
  "COMMON-0047",
  "COMMON-0051",
  "COMMON-0052",
];

function phaseChannel(period, position) {
  return mod(position, period);
}

function majorityLabel(labels) {
  const positives = labels.filter((label) => label === 1).length;
  const negatives = labels.length - positives;
  return positives >= negatives ? 1 : 0;
}

function accuracy(predictions, labels) {
  let correct = 0;
  predictions.forEach((prediction, index) => {
    if (prediction === labels[index]) correct += 1;
  });
  return correct / labels.length;
}

function fitLookup(period, positions, labels, indexer = phaseChannel) {
  const fallback = majorityLabel(labels);
  const counts = Array.from({ length: period }, () => [0, 0]);
  positions.forEach((position, index) => {
    counts[indexer(period, position)][labels[index]] += 1;
  });
  return counts.map(([zeroCount, oneCount]) => {
    if (zeroCount + oneCount === 0) return fallback;
    return oneCount >= zeroCount ? 1 : 0;
  });
}

function predictLookup(period, lookup, positions, indexer = phaseChannel) {
  return positions.map((position) => lookup[indexer(period, position)]);
}

function defaultPositivePhases(period) {
  return Array.from({ length: period }, (_, phase) => phase).filter((phase) => phase % 3 === 1);
}

function syntheticPhaseDataset(period, length, start = 0) {
  const phases = defaultPositivePhases(period);
  const positions = Array.from({ length }, (_, index) => start + index);
  return {
    positions,
    labels: positions.map((position) => phases.includes(phaseChannel(period, position)) ? 1 : 0),
  };
}

function defaultSlotValues(size) {
  return Array.from({ length: size }, (_, index) => index % 3 === 1 ? 1 : 0);
}

function syntheticSlotDataset(size, length, start = 0) {
  const values = defaultSlotValues(size);
  const positions = Array.from({ length }, (_, index) => start + index);
  return {
    positions,
    labels: positions.map((position) => values[mod(position, size)]),
  };
}

function multicoilPhase(periods, position) {
  return periods.map((period) => mod(position, period));
}

function multicoilPhaseLabel(periods, position) {
  const phase = multicoilPhase(periods, position);
  const score = phase.reduce((total, residue, index) => total + (index + 1) * residue, 0);
  return score % 4 === 1 ? 1 : 0;
}

function fitMapLookup(items, labels, keyFn) {
  const counts = new Map();
  items.forEach((item, index) => {
    const key = keyFn(item);
    if (!counts.has(key)) counts.set(key, { item, zero: 0, one: 0 });
    if (labels[index] === 1) counts.get(key).one += 1;
    else counts.get(key).zero += 1;
  });
  return Array.from(counts.entries()).map(([key, entry]) => [key, entry.one >= entry.zero ? 1 : 0]);
}

function predictMapLookup(lookup, items, keyFn) {
  const map = new Map(lookup);
  const fallback = majorityLabel(lookup.map((entry) => entry[1]));
  return items.map((item) => {
    const key = keyFn(item);
    return map.has(key) ? map.get(key) : fallback;
  });
}

function round12(value) {
  const rounded = Math.round(value * 1e12) / 1e12;
  return Object.is(rounded, -0) ? 0 : rounded;
}

function harmonicFeature(period, position) {
  const angle = (2 * Math.PI * phaseChannel(period, position)) / period;
  return [round12(Math.cos(angle)), round12(Math.sin(angle))];
}

function ropeRelativeFeature(period, [queryPosition, keyPosition]) {
  const lag = mod(queryPosition - keyPosition, period);
  const angle = (2 * Math.PI * lag) / period;
  return [round12(Math.cos(angle)), round12(Math.sin(angle))];
}

function featureKey(feature) {
  return feature.map((value) => value.toFixed(12)).join(",");
}

function syntheticRopeRelativeDataset(period, length, start = 0) {
  const positiveLags = defaultPositivePhases(period);
  const pairs = [];
  const labels = [];
  for (let sampleIndex = start; sampleIndex < start + length; sampleIndex += 1) {
    const queryPosition = Math.floor(sampleIndex / period);
    const lag = sampleIndex % period;
    const keyPosition = queryPosition - lag;
    pairs.push([queryPosition, keyPosition]);
    labels.push(positiveLags.includes(lag) ? 1 : 0);
  }
  return { pairs, labels };
}

function coilAttentionPath(sequenceLength, queryIndex, stride, pathLength) {
  return Array.from({ length: pathLength }, (_, index) => mod(queryIndex - (index + 1) * stride, sequenceLength));
}

function localWindowIndices(sequenceLength, queryIndex, window) {
  return Array.from({ length: window }, (_, index) => mod(queryIndex - (index + 1), sequenceLength));
}

function retrievalTargetIndex(sequenceLength, queryIndex, targetLag) {
  return mod(queryIndex - targetLag, sequenceLength);
}

function retrievalIndicators(sequenceLength, queryIndices, targetLags, candidateSets) {
  return queryIndices.map((queryIndex, index) => {
    const targetLag = Array.isArray(targetLags) ? targetLags[index] : targetLags;
    const target = retrievalTargetIndex(sequenceLength, queryIndex, targetLag);
    return new Set(candidateSets[index]).has(target) ? 1 : 0;
  });
}

function loopRequiredSteps(loopPeriod, sampleIndex) {
  return mod(sampleIndex, loopPeriod) + 1;
}

function loopAdaptiveExitPredictions(loopPeriod, sampleIndices, budget) {
  return sampleIndices.map((sampleIndex) => loopRequiredSteps(loopPeriod, sampleIndex) <= budget ? 1 : 0);
}

function computeCases() {
  const phaseTrain = syntheticPhaseDataset(8, 64);
  const phaseTest = syntheticPhaseDataset(8, 32, 64);
  const phaseLookup = fitLookup(8, phaseTrain.positions, phaseTrain.labels);
  const phasePredictions = predictLookup(8, phaseLookup, phaseTest.positions);
  const phaseConstant = majorityLabel(phaseTrain.labels);

  const memoryTrain = syntheticSlotDataset(8, 64);
  const memoryTest = syntheticSlotDataset(8, 32, 64);
  const memoryLookup = fitLookup(8, memoryTrain.positions, memoryTrain.labels);
  const memoryPredictions = predictLookup(8, memoryLookup, memoryTest.positions);

  const adapterTrain = syntheticSlotDataset(8, 64);
  const adapterTest = syntheticSlotDataset(8, 32, 64);
  const adapterLookup = fitLookup(8, adapterTrain.positions, adapterTrain.labels);
  const adapterPredictions = predictLookup(8, adapterLookup, adapterTest.positions);

  const multicoilPeriods = [5, 7];
  const multicoilTrainPositions = Array.from({ length: 140 }, (_, index) => index);
  const multicoilTestPositions = Array.from({ length: 70 }, (_, index) => 140 + index);
  const multicoilTrainLabels = multicoilTrainPositions.map((position) =>
    multicoilPhaseLabel(multicoilPeriods, position)
  );
  const multicoilTestLabels = multicoilTestPositions.map((position) =>
    multicoilPhaseLabel(multicoilPeriods, position)
  );
  const multicoilLookup = fitMapLookup(
    multicoilTrainPositions,
    multicoilTrainLabels,
    (position) => multicoilPhase(multicoilPeriods, position).join(","),
  );
  const multicoilPredictions = predictMapLookup(
    multicoilLookup,
    multicoilTestPositions,
    (position) => multicoilPhase(multicoilPeriods, position).join(","),
  );

  const retrievalQueries = Array.from({ length: 64 }, (_, index) => index);
  const retrievalCandidates = retrievalQueries.map((queryIndex) => coilAttentionPath(64, queryIndex, 7, 3));
  const retrievalPredictions = retrievalIndicators(64, retrievalQueries, 21, retrievalCandidates);
  const retrievalLabels = retrievalQueries.map(() => 1);

  const learnedTrain = syntheticPhaseDataset(8, 64);
  const learnedTest = syntheticPhaseDataset(8, 32, 64);
  const learnedLookup = fitLookup(8, learnedTrain.positions, learnedTrain.labels);
  const learnedPredictions = predictLookup(8, learnedLookup, learnedTest.positions);
  const learnedControlThreshold = Math.floor((3 * 64) / 4);
  const learnedControlTrainLabels = learnedTrain.positions.map((position) =>
    position >= learnedControlThreshold ? 1 : 0
  );
  const learnedControlTestLabels = learnedTest.positions.map((position) =>
    position >= learnedControlThreshold ? 1 : 0
  );
  const learnedControlPredictions = learnedTest.positions.map((position) =>
    position >= learnedControlThreshold ? 1 : 0
  );

  const harmonicTrain = syntheticPhaseDataset(8, 64);
  const harmonicTest = syntheticPhaseDataset(8, 32, 64);
  const harmonicLookup = fitMapLookup(
    harmonicTrain.positions,
    harmonicTrain.labels,
    (position) => featureKey(harmonicFeature(8, position)),
  );
  const harmonicPredictions = predictMapLookup(
    harmonicLookup,
    harmonicTest.positions,
    (position) => featureKey(harmonicFeature(8, position)),
  );

  const ropeTrain = syntheticRopeRelativeDataset(8, 64);
  const ropeTest = syntheticRopeRelativeDataset(8, 32, 64);
  const ropeLookup = fitMapLookup(
    ropeTrain.pairs,
    ropeTrain.labels,
    (pair) => featureKey(ropeRelativeFeature(8, pair)),
  );
  const ropePredictions = predictMapLookup(
    ropeLookup,
    ropeTest.pairs,
    (pair) => featureKey(ropeRelativeFeature(8, pair)),
  );

  const nearLocalCandidates = retrievalQueries.map((queryIndex) => localWindowIndices(64, queryIndex, 8));
  const nearLocalPredictions = retrievalIndicators(64, retrievalQueries, 3, nearLocalCandidates);
  const nearLocalLabels = retrievalQueries.map(() => 1);

  const gatedTargetLags = retrievalQueries.map((queryIndex) => queryIndex % 2 === 0 ? 21 : 3);
  const gatedCoilCandidates = retrievalQueries.map((queryIndex) => coilAttentionPath(64, queryIndex, 7, 3));
  const gatedLocalCandidates = retrievalQueries.map((queryIndex) => localWindowIndices(64, queryIndex, 8));
  const gatedCandidates = retrievalQueries.map((queryIndex, index) =>
    queryIndex % 2 === 0 ? gatedCoilCandidates[index] : gatedLocalCandidates[index]
  );
  const gatedPredictions = retrievalIndicators(64, retrievalQueries, gatedTargetLags, gatedCandidates);
  const gatedLabels = retrievalQueries.map(() => 1);

  const loopedTestIndices = Array.from({ length: 32 }, (_, index) => 64 + index);
  const loopedPredictions = loopAdaptiveExitPredictions(4, loopedTestIndices, 4);
  const loopedLabels = loopedTestIndices.map(() => 1);

  return [
    ["phase_lookup", phasePredictions, phaseTest.labels],
    ["phase_constant_baseline", phaseTest.positions.map(() => phaseConstant), phaseTest.labels],
    ["memory_lookup", memoryPredictions, memoryTest.labels],
    ["adapter_lookup", adapterPredictions, adapterTest.labels],
    ["multicoil_lookup", multicoilPredictions, multicoilTestLabels],
    ["retrieval_coil_path", retrievalPredictions, retrievalLabels],
    ["retrieval_near_local_window", nearLocalPredictions, nearLocalLabels],
    ["retrieval_content_gated", gatedPredictions, gatedLabels],
    ["learned_feature_cyclic", learnedPredictions, learnedTest.labels],
    ["harmonic_feature_lookup", harmonicPredictions, harmonicTest.labels],
    ["rope_relative_phase", ropePredictions, ropeTest.labels],
    ["looped_recurrence_adaptive_exit", loopedPredictions, loopedLabels],
    ["learned_feature_nonperiodic_dense_scalar", learnedControlPredictions, learnedControlTestLabels],
  ];
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
  title.textContent = "Formal boundary";
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

function appendTable(section, scores) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["case", "CPU score", "role"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  scores.forEach(([name, score]) => {
    const tr = document.createElement("tr");
    const role = name.includes("baseline") || name.includes("near") || name.includes("nonperiodic")
      ? "control or baseline"
      : "positive deterministic fixture";
    for (const value of [name, score.toFixed(3).replace(/0+$/, "").replace(/\.$/, ""), role]) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  section.appendChild(table);
}

function appendRecord(output, theoremById) {
  const cases = computeCases();
  const scores = cases.map(([name, predictions, labels]) => [name, accuracy(predictions, labels)]);
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Backend parity fixture record";
  section.appendChild(title);
  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    "fixture id: AIA-B0003",
    `fixture count: ${cases.length}`,
    "browser backend: deterministic JavaScript CPU formulas",
    "Python backend: run_ai_backend_parity_check() compares CPU with optional MLX when MLX is installed",
    "boundary: parity scores are executable consistency checks, not speed or model-quality claims.",
  ].join("\n");
  section.appendChild(data);
  appendTable(section, scores);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this static widget cannot import MLX and does not measure acceleration. It mirrors the CPU scoring cases so the Living Book explains what the local Python/optional-MLX parity fixture checks.";
  section.appendChild(warning);
  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Backend parity fixture", "Widget: deterministic CPU scores for the optional MLX parity harness");
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    clear(output);
    appendRecord(output, theoremById);
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

mountWidgets("backend_parity_fixture", mount);
