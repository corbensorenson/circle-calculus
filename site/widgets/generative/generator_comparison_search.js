import { positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = [
  "GEN-T0001",
  "GEN-T0005",
  "GEN-T0017",
  "GEN-T0018",
  "GEN-T0019",
  "GEN-T0020",
  "GEN-T0022",
  "GEN-T0023",
  "GEN-T0024",
  "GEN-T0025",
  "GEN-T0026",
  "GEN-T0027",
  "GEN-T0028",
  "GEN-T0029",
  "GEN-T0030",
  "GEN-T0031",
  "GEN-T0032",
  "GEN-T0033",
  "GEN-T0034",
];
const DICTIONARY_IDS = ["COMMON-0064", "COMMON-0065", "COMMON-0066"];

function sortedPairs(object) {
  return Object.entries(object).sort(([left], [right]) => left.localeCompare(right));
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function jsonLength(value) {
  return stableStringify(value).length;
}

function finiteCircleGenerator(n) {
  const generated = Array.from({ length: n }, (_, index) => index);
  return {
    artifact_id: "finite_circle",
    seed: sortedPairs({ n }),
    rules: [
      ["enumerate_nodes", sortedPairs({ start: 0, stop: n })],
    ],
    iteration_schedule: "i = 0..n-1",
    closure_condition: "stop before node n, since nodes are residues modulo n",
    generated_object: generated,
    theorem_ids: ["GEN-T0001", "GEN-T0020", "CC-T0001"],
    dictionary_ids: ["CC-0001", "CC-0002", "COMMON-0064", "COMMON-0066"],
  };
}

function brokenFiniteCircleGenerator(n) {
  const record = finiteCircleGenerator(n);
  return {
    ...record,
    generated_object: [0, 1],
  };
}

function regenerate(record) {
  const seed = Object.fromEntries(record.seed);
  if (record.artifact_id === "finite_circle") {
    return Array.from({ length: Number(seed.n) }, (_, index) => index);
  }
  throw new Error(`unknown artifact id: ${record.artifact_id}`);
}

function recordDescription(record) {
  return {
    artifact_id: record.artifact_id,
    seed: record.seed,
    rules: record.rules,
    iteration_schedule: record.iteration_schedule,
    closure_condition: record.closure_condition,
    theorem_ids: record.theorem_ids,
    dictionary_ids: record.dictionary_ids,
  };
}

function compareGeneratorToExplicit(record) {
  const regenerated = regenerate(record);
  const explicit = {
    artifact_id: record.artifact_id,
    generated_object: record.generated_object,
  };
  const generator = recordDescription(record);
  const exact = stableStringify(regenerated) === stableStringify(record.generated_object);
  const explicitLength = jsonLength(explicit);
  const generatorLength = jsonLength(generator);
  return {
    artifact_id: record.artifact_id,
    exact_regeneration: exact,
    explicit_length: explicitLength,
    generator_length: generatorLength,
    generator_shorter: generatorLength < explicitLength,
    note: "Description-length fixture only; not universal compression.",
  };
}

function boundedSearch(records) {
  const comparisons = records.map(compareGeneratorToExplicit);
  const exact = comparisons.filter((comparison) => comparison.exact_regeneration);
  const shorter = exact.filter((comparison) => comparison.generator_shorter);
  const compareKey = (left, right) => {
    if (left.generator_length !== right.generator_length) {
      return left.generator_length - right.generator_length;
    }
    if (left.explicit_length !== right.explicit_length) {
      return left.explicit_length - right.explicit_length;
    }
    return left.artifact_id.localeCompare(right.artifact_id);
  };
  return {
    search_id: "finite_circle_node_generators",
    candidate_count: comparisons.length,
    exact_candidate_count: exact.length,
    best_exact: exact.slice().sort(compareKey)[0] || null,
    best_shorter: shorter.slice().sort(compareKey)[0] || null,
    finite_search_space: true,
    theorem_ids: [
      "GEN-T0022",
      "GEN-T0023",
      "GEN-T0024",
      "GEN-T0025",
      "GEN-T0026",
      "GEN-T0027",
      "GEN-T0028",
      "GEN-T0029",
      "GEN-T0030",
      "GEN-T0031",
      "GEN-T0032",
      "GEN-T0033",
      "GEN-T0034",
    ],
    note: "Bounded finite search only; not an optimality theorem.",
    comparisons,
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
  title.textContent = "Generator comparison theorems";
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

function appendComparisonTable(record, rows) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["candidate", "exact", "explicit length", "generator length", "shorter"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  rows.forEach((row, index) => {
    const tr = document.createElement("tr");
    for (const value of [
      `candidate ${index + 1}: ${row.artifact_id}`,
      row.exact_regeneration ? "yes" : "no",
      String(row.explicit_length),
      String(row.generator_length),
      row.generator_shorter ? "yes" : "no",
    ]) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  record.appendChild(table);
}

function appendRecord(output, values, theoremById) {
  const records = [
    finiteCircleGenerator(1),
    finiteCircleGenerator(values.n),
    brokenFiniteCircleGenerator(values.n),
  ];
  const search = boundedSearch(records);
  const emptySearch = boundedSearch([]);
  const singletonSearch = boundedSearch([finiteCircleGenerator(values.n)]);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Bounded generator comparison record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `search id: ${search.search_id}`,
    `finite search space: ${search.finite_search_space}`,
    `candidate count: ${search.candidate_count}`,
    `exact candidate count: ${search.exact_candidate_count}`,
    `best exact generator length: ${search.best_exact ? search.best_exact.generator_length : "none"}`,
    `best shorter generator length: ${search.best_shorter ? search.best_shorter.generator_length : "none"}`,
    `best-exact presence implies positive exact count: ${search.best_exact !== null ? search.exact_candidate_count > 0 : "not applicable"}`,
    `singleton exact boundary: candidate_count=${singletonSearch.candidate_count}, exact_candidate_count=${singletonSearch.exact_candidate_count}, best_exact=${singletonSearch.best_exact === null ? "none" : "present"}`,
    `singleton best exact is exact: ${singletonSearch.best_exact !== null && singletonSearch.best_exact.exact_regeneration}`,
    `empty search boundary: candidate_count=${emptySearch.candidate_count}, exact_candidate_count=${emptySearch.exact_candidate_count}, best_exact=${emptySearch.best_exact === null ? "none" : "present"}`,
    `empty search no-best iff exact count zero: ${(emptySearch.best_exact === null) === (emptySearch.exact_candidate_count === 0)}`,
    `positive case n=${values.n}: ${search.comparisons[1].generator_shorter ? "generator shorter than explicit" : "explicit not beaten by generator"}`,
    `negative/broken case exact: ${search.comparisons[2].exact_regeneration}`,
  ].join("\n");
  record.appendChild(data);
  appendComparisonTable(record, search.comparisons);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this is a bounded declared-candidate search. It is not an optimal-compression theorem, not Kolmogorov complexity, and not evidence that smaller descriptions are always better.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Generator comparison search", "Widget: exact regeneration and bounded description length");
  const nInput = addLabeledNumber(panel, "gen-search-n", "finite circle n", 128, 1, 512);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      n: positiveInt(nInput.value, 128, 1, 512),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  nInput.addEventListener("input", render);
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

mountWidgets("generator_comparison_search", mount);
