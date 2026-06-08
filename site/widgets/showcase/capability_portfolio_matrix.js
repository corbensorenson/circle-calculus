import { loadJson, mountWidgets } from "../shared/widget_base.js";

function count(value) {
  return Array.isArray(value) ? value.length : 0;
}

function livingPageCount(capability) {
  return count(capability.living_book_refs);
}

function livingWidgetCount(capability) {
  const ids = new Set();
  for (const ref of capability.living_book_refs || []) {
    for (const widgetId of ref.widget_ids || []) ids.add(widgetId);
  }
  return ids.size;
}

function evidenceCounts(capability) {
  return capability.evidence_counts || {
    paper_count: count(capability.paper_ids),
    theorem_count: count(capability.theorem_ids),
    dictionary_count: count(capability.dictionary_ids),
    executable_count: count(capability.executable_refs),
    source_count: count(capability.source_refs),
    living_book_page_count: livingPageCount(capability),
    living_book_widget_count: livingWidgetCount(capability),
  };
}

function roleLabel(role) {
  if (role === "standard_math_parity") return "standard parity";
  if (role === "circle_native_value") return "Circle-native";
  if (role === "application_guardrail") return "guardrail";
  return role.replaceAll("_", " ");
}

function capabilityLink(capability) {
  const link = document.createElement("a");
  link.href = `#${encodeURIComponent(capability.id)}`;
  link.textContent = capability.id;
  link.addEventListener("click", (event) => {
    const target = document.querySelector(`[data-capability-id="${capability.id}"]`);
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    history.replaceState(null, "", `#${encodeURIComponent(capability.id)}`);
  });
  return link;
}

function appendCell(row, value) {
  const td = document.createElement("td");
  if (value instanceof Node) {
    td.appendChild(value);
  } else {
    td.textContent = String(value);
  }
  row.appendChild(td);
}

function appendCountCell(row, value, label) {
  const span = document.createElement("span");
  span.className = "capability-count";
  span.textContent = String(value);
  span.setAttribute("aria-label", `${value} ${label}`);
  appendCell(row, span);
}

function roleBadges(capability) {
  const fragment = document.createDocumentFragment();
  for (const role of capability.portfolio_roles || []) {
    const badge = document.createElement("span");
    badge.className = "record-pill";
    badge.textContent = roleLabel(role);
    fragment.appendChild(badge);
  }
  return fragment;
}

function renderTable(capabilities) {
  const wrap = document.createElement("div");
  wrap.className = "index-table-wrap";

  const table = document.createElement("table");
  table.className = "capability-matrix-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of [
    "Capability",
    "Area",
    "Roles",
    "Papers",
    "Theorems",
    "Executables",
    "Living pages",
    "Widgets",
    "Claim boundary",
  ]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const capability of capabilities) {
    const counts = evidenceCounts(capability);
    const row = document.createElement("tr");

    const title = document.createElement("div");
    title.className = "capability-title-cell";
    title.append(capabilityLink(capability), document.createTextNode(` ${capability.title || ""}`));
    appendCell(row, title);
    appendCell(row, capability.area || "");
    appendCell(row, roleBadges(capability));
    appendCountCell(row, counts.paper_count, "papers");
    appendCountCell(row, counts.theorem_count, "theorems");
    appendCountCell(row, counts.executable_count, "executable examples");
    appendCountCell(row, counts.living_book_page_count, "Living Book pages");
    appendCountCell(row, counts.living_book_widget_count, "Living Book widgets");
    appendCell(row, capability.not_claimed || "");
    tbody.appendChild(row);
  }
  table.appendChild(tbody);
  wrap.appendChild(table);
  return wrap;
}

function renderSummary(capabilities) {
  const totals = capabilities.reduce((acc, capability) => {
    const counts = evidenceCounts(capability);
    acc.papers += counts.paper_count;
    acc.theorems += counts.theorem_count;
    acc.executables += counts.executable_count;
    acc.pages += counts.living_book_page_count;
    acc.widgets += counts.living_book_widget_count;
    return acc;
  }, { papers: 0, theorems: 0, executables: 0, pages: 0, widgets: 0 });

  const summary = document.createElement("p");
  summary.className = "widget-data";
  summary.textContent = [
    `capability lanes: ${capabilities.length}`,
    `paper links: ${totals.papers}`,
    `proved theorem ids advertised: ${totals.theorems}`,
    `pytest executable refs: ${totals.executables}`,
    `Living Book page refs: ${totals.pages}`,
    `Living Book widget refs: ${totals.widgets}`,
  ].join("\n");
  return summary;
}

function roleCoverageLine(summary) {
  const roleCounts = summary?.role_counts || {};
  const parts = [];
  for (const role of ["standard_math_parity", "circle_native_value", "application_guardrail"]) {
    if (roleCounts[role]) parts.push(`${roleLabel(role)} lanes: ${roleCounts[role]}`);
  }
  return parts.join("\n");
}

function renderManifestSummary(capabilities, summary) {
  if (!summary || !summary.unique_evidence_counts) return renderSummary(capabilities);
  const unique = summary.unique_evidence_counts;
  const totals = summary.evidence_totals || {};
  const lines = [
    `capability lanes: ${summary.capability_count ?? capabilities.length}`,
    `role coverage:\n${roleCoverageLine(summary)}`,
    `unique paper ids: ${unique.paper_count}`,
    `unique proved theorem ids advertised: ${unique.theorem_count}`,
    `unique pytest executable refs: ${unique.executable_count}`,
    `unique Living Book page refs: ${unique.living_book_page_count}`,
    `unique Living Book widget refs: ${unique.living_book_widget_count}`,
    `total evidence links: papers ${totals.paper_count ?? 0}; theorems ${totals.theorem_count ?? 0}; executables ${totals.executable_count ?? 0}; pages ${totals.living_book_page_count ?? 0}; widgets ${totals.living_book_widget_count ?? 0}`,
  ];
  const node = document.createElement("p");
  node.className = "widget-data";
  node.textContent = lines.filter(Boolean).join("\n");
  return node;
}

function render(panel, data) {
  const capabilities = data.capabilities || [];
  const section = document.createElement("section");
  section.className = "seed-rule-record";

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this matrix summarizes manifest-backed evidence only. It does not turn imported theorem bridges, executable examples, widgets, or benchmarks into new mathematical proofs.";

  section.append(renderManifestSummary(capabilities, data.portfolio_summary), renderTable(capabilities), warning);
  panel.replaceChildren(section);
}

function mount(panel) {
  panel.textContent = "Loading capability portfolio matrix...";
  loadJson("../../data/generated/capability_showcase.json")
    .then((data) => render(panel, data))
    .catch((error) => {
      console.error(error);
      panel.textContent = "Capability portfolio matrix could not load.";
    });
}

mountWidgets("capability_portfolio_matrix", mount);
