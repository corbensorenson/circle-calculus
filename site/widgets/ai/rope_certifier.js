import { positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_GROUPS = [
  {
    title: "Exact certifier theorems",
    ids: [
      "AIRA-T0021",
      "AIRA-T0022",
      "AIRA-T0023",
      "AIRA-T0024",
      "AIRA-T0025",
      "AIRA-T0026",
    ],
  },
  {
    title: "Collision-count theorems",
    ids: [
      "AIRA-T0027",
      "AIRA-T0028",
      "AIRA-T0034",
      "AIRA-T0035",
      "AIRA-T0036",
      "AIRA-T0046",
      "AIRA-T0048",
      "AIRA-T0049",
      "AIRA-T0051",
      "AIRA-T0052",
    ],
  },
  {
    title: "Real-phase precursor theorems",
    ids: [
      "AIRA-T0029",
      "AIRA-T0030",
      "AIRA-T0031",
      "AIRA-T0032",
      "AIRA-T0033",
      "AIRA-T0037",
      "AIRA-T0038",
      "AIRA-T0039",
      "AIRA-T0040",
      "AIRA-T0041",
      "AIRA-T0042",
      "AIRA-T0043",
      "AIRA-T0044",
      "AIRA-T0045",
      "AIRA-T0047",
      "AIRA-T0050",
      "AIRA-T0053",
      "AIRA-T0054",
      "AIRA-T0055",
      "AIRA-T0056",
      "AIRA-T0057",
      "AIRA-T0058",
      "AIRA-T0059",
    ],
  },
];
const DICTIONARY_IDS = [
  "COMMON-0076",
  "COMMON-0077",
  "COMMON-0078",
  "COMMON-0083",
  "COMMON-0084",
  "COMMON-0080",
  "COMMON-0082",
  "COMMON-0085",
  "COMMON-0086",
];
const TWO_PI = 2 * Math.PI;

function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y !== 0) {
    const next = x % y;
    x = y;
    y = next;
  }
  return x;
}

function lcm(a, b) {
  return (a / gcd(a, b)) * b;
}

function cappedLcm(values, cap) {
  let current = 1;
  for (const value of values) {
    current = lcm(current, value);
    if (current >= cap) return { value: current, reachesContext: true };
  }
  return { value: current, reachesContext: current >= cap };
}

function collisionPairCountAtGapMultiples(context, gap) {
  if (gap <= 0 || gap >= context) return 0;
  let total = 0;
  for (let multiple = 1; multiple * gap < context; multiple += 1) {
    total += context - multiple * gap;
  }
  return total;
}

function phaseBankPrefixReports(context, periods, limit = 8) {
  const reports = [];
  const prefixLimit = Math.min(periods.length, limit);
  for (let prefixLength = 1; prefixLength <= prefixLimit; prefixLength += 1) {
    const prefix = periods.slice(0, prefixLength);
    const exact = cappedLcm(prefix, context);
    reports.push({
      prefixLength,
      reachesContext: exact.reachesContext,
      gap: exact.reachesContext ? null : exact.value,
      totalPairs: exact.reachesContext ? 0 : collisionPairCountAtGapMultiples(context, exact.value),
    });
  }
  return reports;
}

function angularFrequencies(headDim, base) {
  const out = [];
  for (let index = 0; index < headDim / 2; index += 1) {
    out.push(base ** (-(2 * index) / headDim));
  }
  return out;
}

function periodEstimates(headDim, base) {
  return angularFrequencies(headDim, base).map((frequency) => TWO_PI / frequency);
}

function discretize(periods, policy) {
  return periods.map((period) => {
    if (policy === "floor") return Math.max(1, Math.floor(period));
    if (policy === "ceil") return Math.max(1, Math.ceil(period));
    return Math.max(1, Math.round(period));
  });
}

function circularPhaseDistance(angle) {
  return Math.abs(((angle + Math.PI) % TWO_PI + TWO_PI) % TWO_PI - Math.PI);
}

function realMargin(headDim, base, context, tolerance) {
  if (context <= 1) {
    return {
      pass: true,
      worstMargin: Infinity,
      worstGap: null,
      scanned: 0,
      near: [],
    };
  }
  const frequencies = angularFrequencies(headDim, base);
  let worstMargin = Infinity;
  let worstGap = null;
  const near = [];
  for (let gap = 1; gap < context; gap += 1) {
    let best = -1;
    for (const frequency of frequencies) {
      best = Math.max(best, circularPhaseDistance(gap * frequency));
    }
    if (best < worstMargin) {
      worstMargin = best;
      worstGap = gap;
    }
    if (best <= tolerance && near.length < 5) {
      near.push({ gap, margin: best });
    }
  }
  return {
    pass: worstMargin > tolerance,
    worstMargin,
    worstGap,
    scanned: context - 1,
    near,
  };
}

function makeLink(id, page) {
  const href = new URL(`../../${page}#${encodeURIComponent(id)}`, import.meta.url).toString();
  const link = document.createElement("a");
  link.href = href;
  link.textContent = id;
  return link;
}

function appendBadgeRow(section, theoremById, titleText, theoremIds) {
  const row = document.createElement("div");
  row.className = "generator-badge-row";
  const title = document.createElement("strong");
  title.textContent = titleText;
  row.appendChild(title);
  for (const id of theoremIds) {
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

function appendPeriodTable(record, periods) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["channel", "integer period"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  periods.slice(0, 12).forEach((period, index) => {
    const tr = document.createElement("tr");
    for (const value of [String(index), String(period)]) {
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
  const estimates = periodEstimates(values.headDim, values.base);
  const periods = discretize(estimates, values.policy);
  const exact = cappedLcm(periods, values.context);
  const samplePairs = exact.reachesContext
    ? []
    : Array.from({ length: Math.min(5, values.context - exact.value) }, (_, start) => [start, start + exact.value]);
  const guaranteedPairCount = exact.reachesContext ? 0 : Math.max(0, values.context - exact.value);
  const guaranteedMultiplePairCount = exact.reachesContext
    ? 0
    : collisionPairCountAtGapMultiples(values.context, exact.value);
  const prefixReports = phaseBankPrefixReports(values.context, periods);
  const firstPassPrefix = prefixReports.find((report) => report.reachesContext);
  const margin = realMargin(values.headDim, values.base, values.context, values.tolerance);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "RoPE position certificate";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIRA-B0009`,
    `head dimension: ${values.headDim}`,
    `base: ${values.base}`,
    `context length: ${values.context}`,
    `discretization: ${values.policy}`,
    `tolerance: ${values.tolerance}`,
    `exact discrete contract: ${exact.reachesContext ? "PASS" : "FAIL"}`,
    `common collision gap: ${exact.reachesContext ? ">= context" : exact.value}`,
    `guaranteed common-gap collision pairs: ${guaranteedPairCount}`,
    `guaranteed common-gap multiple pairs: ${guaranteedMultiplePairCount}`,
    `bounded prefix reports: ${prefixReports.length}`,
    `first exact pass prefix length: ${firstPassPrefix ? firstPassPrefix.prefixLength : "none"}`,
    `real-phase margin: ${margin.pass ? "PASS" : "WARN"}`,
    `worst margin radians: ${Number.isFinite(margin.worstMargin) ? margin.worstMargin.toPrecision(6) : "inf"}`,
    `worst gap: ${margin.worstGap === null ? "none" : margin.worstGap}`,
  ].join("\n");
  record.appendChild(data);

  for (const group of THEOREM_GROUPS) {
    appendBadgeRow(record, theoremById, group.title, group.ids);
  }
  appendDictionaryRow(record);
  appendPeriodTable(record, periods);

  if (prefixReports.length > 0) {
    const prefixes = document.createElement("p");
    prefixes.textContent = `Prefix reports: ${prefixReports
      .map((report) => {
        const gap = report.reachesContext ? ">= context" : report.gap;
        return `first ${report.prefixLength}: gap ${gap}, pairs ${report.totalPairs}`;
      })
      .join("; ")}.`;
    record.appendChild(prefixes);
  }

  if (samplePairs.length > 0) {
    const pairs = document.createElement("p");
    pairs.textContent = `Sample exact discrete collisions: ${samplePairs.map((pair) => `(${pair[0]}, ${pair[1]})`).join(", ")}.`;
    record.appendChild(pairs);
  }

  const warning = document.createElement("p");
  warning.className = "widget-warning";
  warning.textContent = "Boundary: exact pass/fail is for the integer-period discretized model. The real-phase margin is numerical evidence only, not a Lean proof and not a model-quality or context-length claim.";
  record.appendChild(warning);

  output.appendChild(record);
}

async function mount(target) {
  const [theoremData] = await Promise.all([
    loadJson("../../data/generated/theorem_manifest.json"),
  ]);
  const theoremById = new Map((theoremData.theorems || []).map((item) => [item.id, item]));

  const panel = document.createElement("div");
  panel.className = "widget-controls";
  addWidgetHeader(panel, "RoPE Position Certifier", "Exact discrete collision contract plus numerical margin scan");
  const headInput = addLabeledNumber(panel, "rope-cert-head-dim", "head dim", 128, 2, 256);
  const baseInput = addLabeledNumber(panel, "rope-cert-base", "base", 10000, 2, 500000);
  const contextInput = addLabeledNumber(panel, "rope-cert-context", "context", 4096, 1, 131072);
  const toleranceInput = addLabeledNumber(panel, "rope-cert-tolerance", "tolerance x 1e-6", 1, 0, 1000);

  const policyLabel = document.createElement("label");
  policyLabel.textContent = "discretization";
  const policyInput = document.createElement("select");
  for (const policy of ["round", "floor", "ceil"]) {
    const option = document.createElement("option");
    option.value = policy;
    option.textContent = policy;
    policyInput.appendChild(option);
  }
  policyLabel.appendChild(policyInput);
  panel.appendChild(policyLabel);

  const output = addOutput(panel);
  const render = () => {
    clear(output);
    const rawHead = positiveInt(headInput.value, 128, 2, 256);
    const headDim = rawHead % 2 === 0 ? rawHead : rawHead + 1;
    const values = {
      headDim,
      base: positiveInt(baseInput.value, 10000, 2, 500000),
      context: positiveInt(contextInput.value, 4096, 1, 131072),
      tolerance: positiveInt(toleranceInput.value, 1, 0, 1000) / 1000000,
      policy: policyInput.value,
    };
    appendRecord(output, values, theoremById);
  };
  for (const input of [headInput, baseInput, contextInput, toleranceInput, policyInput]) {
    input.addEventListener("input", render);
    input.addEventListener("change", render);
  }
  target.appendChild(panel);
  render();
}

mountWidgets("rope_certifier", mount);
