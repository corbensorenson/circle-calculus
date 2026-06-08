import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["CC-T0002", "CC-T0005"];
const DICTIONARY_IDS = ["COMMON-0057", "COMMON-0047", "COMMON-0028"];

function contentRouteLabel(queryIndex) {
  return queryIndex % 2 === 0 ? 1 : 0;
}

function routeName(route) {
  return route === 1 ? "coil" : "local";
}

function majorityInt(values) {
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
  return Array.from(counts.keys()).sort((left, right) => {
    const countDelta = counts.get(right) - counts.get(left);
    return countDelta || left - right;
  })[0];
}

function fitContentRouteLookup(routePeriod, queryIndices, routeLabels) {
  const fallback = majorityInt(routeLabels);
  const buckets = Array.from({ length: routePeriod }, () => []);
  queryIndices.forEach((query, index) => {
    buckets[mod(query, routePeriod)].push(routeLabels[index]);
  });
  return buckets.map((bucket) => (bucket.length === 0 ? fallback : majorityInt(bucket)));
}

function predictContentRouteLookup(routePeriod, lookup, queryIndices) {
  return queryIndices.map((query) => lookup[mod(query, routePeriod)]);
}

function coilAttentionPath(sequenceLength, queryIndex, stride, pathLength) {
  return Array.from(
    { length: pathLength },
    (_, index) => mod(queryIndex - (index + 1) * stride, sequenceLength),
  );
}

function localWindowIndices(sequenceLength, queryIndex, window) {
  return Array.from(
    { length: window },
    (_, index) => mod(queryIndex - (index + 1), sequenceLength),
  );
}

function retrievalTargetIndex(sequenceLength, queryIndex, targetLag) {
  return mod(queryIndex - targetLag, sequenceLength);
}

function mixedTargetLag(queryIndex, longTargetLag, nearTargetLag) {
  return queryIndex % 2 === 0 ? longTargetLag : nearTargetLag;
}

function candidateSetsForRoutes(routes, coilCandidates, localCandidates) {
  return routes.map((route, index) => (route === 1 ? coilCandidates[index] : localCandidates[index]));
}

function uniqueSorted(values) {
  return Array.from(new Set(values)).sort((a, b) => a - b);
}

function fullAttentionIndices(sequenceLength) {
  return Array.from({ length: sequenceLength }, (_, index) => index);
}

function hitRateByLag(sequenceLength, queryIndices, targetLags, candidateSets) {
  let hits = 0;
  queryIndices.forEach((query, index) => {
    const target = retrievalTargetIndex(sequenceLength, query, targetLags[index]);
    if (new Set(candidateSets[index]).has(target)) hits += 1;
  });
  return hits / queryIndices.length;
}

function accuracy(predicted, required) {
  let hits = 0;
  predicted.forEach((value, index) => {
    if (value === required[index]) hits += 1;
  });
  return hits / required.length;
}

function averageCandidateCount(candidateSets) {
  return candidateSets.reduce((total, candidates) => total + new Set(candidates).size, 0) / candidateSets.length;
}

function formatNumber(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

function formatRoutes(routes, limit = 12) {
  return routes.slice(0, limit).map(routeName).join(", ");
}

function benchmark(values) {
  const trainQueries = Array.from({ length: values.trainLength }, (_, index) => index);
  const trainRoutes = trainQueries.map(contentRouteLabel);
  const testQueries = Array.from({ length: values.testLength }, (_, index) => values.trainLength + index);
  const requiredRoutes = testQueries.map(contentRouteLabel);
  const targetLags = testQueries.map((query) => mixedTargetLag(query, values.longTargetLag, values.nearTargetLag));
  const learnedLookup = fitContentRouteLookup(values.routePeriod, trainQueries, trainRoutes);
  const wrongLookup = fitContentRouteLookup(values.wrongRoutePeriod, trainQueries, trainRoutes);
  const learnedRoutes = predictContentRouteLookup(values.routePeriod, learnedLookup, testQueries);
  const wrongRoutes = predictContentRouteLookup(values.wrongRoutePeriod, wrongLookup, testQueries);
  const flippedRoutes = requiredRoutes.map((route) => 1 - route);
  const coilCandidates = testQueries.map((query) =>
    coilAttentionPath(values.sequenceLength, query, values.stride, values.pathLength)
  );
  const localCandidates = testQueries.map((query) =>
    localWindowIndices(values.sequenceLength, query, values.localWindow)
  );
  const learnedCandidates = candidateSetsForRoutes(learnedRoutes, coilCandidates, localCandidates);
  const wrongCandidates = candidateSetsForRoutes(wrongRoutes, coilCandidates, localCandidates);
  const flippedCandidates = candidateSetsForRoutes(flippedRoutes, coilCandidates, localCandidates);
  const unionCandidates = coilCandidates.map((coil, index) => uniqueSorted([...coil, ...localCandidates[index]]));
  const fullCandidates = testQueries.map(() => fullAttentionIndices(values.sequenceLength));
  return {
    trainQueries,
    testQueries,
    requiredRoutes,
    learnedLookup,
    wrongLookup,
    learnedRoutes,
    wrongRoutes,
    learnedRouteAccuracy: accuracy(learnedRoutes, requiredRoutes),
    wrongPeriodRouteAccuracy: accuracy(wrongRoutes, requiredRoutes),
    learnedGateAccuracy: hitRateByLag(values.sequenceLength, testQueries, targetLags, learnedCandidates),
    staticCoilAccuracy: hitRateByLag(values.sequenceLength, testQueries, targetLags, coilCandidates),
    staticLocalAccuracy: hitRateByLag(values.sequenceLength, testQueries, targetLags, localCandidates),
    wrongPeriodGateAccuracy: hitRateByLag(values.sequenceLength, testQueries, targetLags, wrongCandidates),
    flippedGateAccuracy: hitRateByLag(values.sequenceLength, testQueries, targetLags, flippedCandidates),
    unionCandidateAccuracy: hitRateByLag(values.sequenceLength, testQueries, targetLags, unionCandidates),
    fullAttentionAccuracy: hitRateByLag(values.sequenceLength, testQueries, targetLags, fullCandidates),
    averageLearnedCandidateCount: averageCandidateCount(learnedCandidates),
    averageStaticCoilCandidateCount: averageCandidateCount(coilCandidates),
    averageStaticLocalCandidateCount: averageCandidateCount(localCandidates),
    averageWrongPeriodCandidateCount: averageCandidateCount(wrongCandidates),
    averageFlippedCandidateCount: averageCandidateCount(flippedCandidates),
    averageUnionCandidateCount: averageCandidateCount(unionCandidates),
    averageFullCandidateCount: averageCandidateCount(fullCandidates),
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
  title.textContent = "Finite primitive theorems";
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
    ["learned gate", result.learnedGateAccuracy, result.averageLearnedCandidateCount, "phase-to-route lookup"],
    ["static coil", result.staticCoilAccuracy, result.averageStaticCoilCandidateCount, "coil route for every query"],
    ["static local", result.staticLocalAccuracy, result.averageStaticLocalCandidateCount, "local route for every query"],
    ["wrong-period gate", result.wrongPeriodGateAccuracy, result.averageWrongPeriodCandidateCount, "lookup fit with wrong period"],
    ["flipped gate", result.flippedGateAccuracy, result.averageFlippedCandidateCount, "opposite of required route"],
    ["union", result.unionCandidateAccuracy, result.averageUnionCandidateCount, "coil plus local candidates"],
    ["full-attention oracle", result.fullAttentionAccuracy, result.averageFullCandidateCount, "all indices"],
  ];
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["strategy", "hit rate", "avg candidates", "role"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  for (const [label, hitRate, averageCandidates, role] of rows) {
    const tr = document.createElement("tr");
    for (const value of [
      label,
      formatNumber(hitRate),
      formatNumber(averageCandidates),
      role,
    ]) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  section.appendChild(table);
}

function appendRecord(output, values, theoremById) {
  const result = benchmark(values);
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Learned content-gate retrieval record";
  section.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    "fixture id: AIM-B0010",
    `sequence length: ${values.sequenceLength}`,
    `train/test length: ${values.trainLength}/${values.testLength}`,
    `route period: ${values.routePeriod}`,
    `wrong route period: ${values.wrongRoutePeriod}`,
    `learned lookup: ${result.learnedLookup.map(routeName).join(", ")}`,
    `wrong-period lookup: ${result.wrongLookup.map(routeName).join(", ")}`,
    `required route sample: ${formatRoutes(result.requiredRoutes)}`,
    `learned route sample: ${formatRoutes(result.learnedRoutes)}`,
    `learned route accuracy: ${formatNumber(result.learnedRouteAccuracy)}`,
    `wrong-period route accuracy: ${formatNumber(result.wrongPeriodRouteAccuracy)}`,
  ].join("\n");
  section.appendChild(data);
  appendMetricsTable(section, result);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this is a tiny deterministic phase-to-route lookup fixture with controls. It is not retrieval quality, attention replacement, learned model, speed, memory, or context-length evidence.";
  section.appendChild(warning);

  appendBadgeRow(section, theoremById);
  appendDictionaryRow(section);
  output.appendChild(section);
}

function mount(panel) {
  addWidgetHeader(panel, "Learned content-gate retrieval", "Widget: phase-to-route lookup with controls");
  const sequenceLengthInput = addLabeledNumber(panel, "ai-learned-gate-sequence-length", "sequence length", 64, 2, 128);
  const trainLengthInput = addLabeledNumber(panel, "ai-learned-gate-train-length", "train length", 64, 1, 128);
  const testLengthInput = addLabeledNumber(panel, "ai-learned-gate-test-length", "test length", 32, 1, 128);
  const routePeriodInput = addLabeledNumber(panel, "ai-learned-gate-route-period", "route period", 2, 1, 16);
  const wrongRoutePeriodInput = addLabeledNumber(panel, "ai-learned-gate-wrong-period", "wrong route period", 3, 1, 16);
  const longLagInput = addLabeledNumber(panel, "ai-learned-gate-long-lag", "long lag", 21, 0, 127);
  const nearLagInput = addLabeledNumber(panel, "ai-learned-gate-near-lag", "near lag", 3, 0, 127);
  const strideInput = addLabeledNumber(panel, "ai-learned-gate-stride", "stride", 7, 0, 127);
  const pathLengthInput = addLabeledNumber(panel, "ai-learned-gate-path-length", "path length", 3, 1, 32);
  const localWindowInput = addLabeledNumber(panel, "ai-learned-gate-local-window", "local window", 8, 1, 64);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      sequenceLength: positiveInt(sequenceLengthInput.value, 64, 2, 128),
      trainLength: positiveInt(trainLengthInput.value, 64, 1, 128),
      testLength: positiveInt(testLengthInput.value, 32, 1, 128),
      routePeriod: positiveInt(routePeriodInput.value, 2, 1, 16),
      wrongRoutePeriod: positiveInt(wrongRoutePeriodInput.value, 3, 1, 16),
      longTargetLag: positiveInt(longLagInput.value, 21, 0, 127),
      nearTargetLag: positiveInt(nearLagInput.value, 3, 0, 127),
      stride: positiveInt(strideInput.value, 7, 0, 127),
      pathLength: positiveInt(pathLengthInput.value, 3, 1, 32),
      localWindow: positiveInt(localWindowInput.value, 8, 1, 64),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [
    sequenceLengthInput,
    trainLengthInput,
    testLengthInput,
    routePeriodInput,
    wrongRoutePeriodInput,
    longLagInput,
    nearLagInput,
    strideInput,
    pathLengthInput,
    localWindowInput,
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

mountWidgets("learned_content_gate_retrieval", mount);
