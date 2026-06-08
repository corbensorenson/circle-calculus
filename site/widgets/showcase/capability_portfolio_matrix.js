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

function provenanceLabel(kind) {
  if (kind === "mathlib_bridge") return "mathlib bridge";
  if (kind === "project_native") return "project-native";
  if (kind === "mixed") return "mixed";
  return String(kind || "unspecified").replaceAll("_", " ");
}

function capabilityIdLink(capabilityId) {
  const link = document.createElement("a");
  link.href = `#${encodeURIComponent(capabilityId)}`;
  link.textContent = capabilityId;
  link.addEventListener("click", (event) => {
    const target = document.querySelector(`[data-capability-id="${capabilityId}"]`);
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    history.replaceState(null, "", `#${encodeURIComponent(capabilityId)}`);
  });
  return link;
}

function capabilityLink(capability) {
  return capabilityIdLink(capability.id);
}

function appendSeparated(fragment, nodes, separator = ", ") {
  nodes.forEach((node, index) => {
    if (index > 0) fragment.append(separator);
    fragment.append(node);
  });
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

function valuePropositionText(capability) {
  const checks = capability.value_proposition_contract?.role_checks || {};
  const parts = Object.entries(checks)
    .filter(([, check]) => check?.required)
    .map(([role, check]) => `${roleLabel(role)}: ${check.ready ? "ready" : "incomplete"}`);
  return parts.length > 0 ? parts.join("; ") : "no required roles";
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
    "Role backing",
    "Proof provenance",
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
    appendCell(row, valuePropositionText(capability));
    appendCell(row, provenanceLabel(capability.proof_provenance_kind));
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

function routeCapabilityLinks(route) {
  const fragment = document.createDocumentFragment();
  appendSeparated(fragment, (route.capability_ids || []).map((id) => capabilityIdLink(id)));
  return fragment;
}

function routeBackingText(route) {
  const contract = route.route_contract || {};
  const theoremRefs = contract.theorem_refs || {};
  const sourceRefs = contract.source_refs || {};
  const livingRefs = contract.living_book_refs || {};
  const reviewPackets = contract.review_packets || {};
  const language = contract.claim_language_contract || {};
  return [
    contract.ready_to_advertise ? "ready" : "incomplete",
    `capabilities ${contract.ready_capability_count ?? 0}/${contract.capability_count ?? 0}`,
    `theorems ${theoremRefs.proved_and_paper_backed_count ?? 0}/${theoremRefs.total_count ?? 0}`,
    `sources ${sourceRefs.backed_count ?? 0}/${sourceRefs.total_count ?? 0}`,
    `Living Book pages ${livingRefs.backed_page_count ?? 0}/${livingRefs.total_page_count ?? 0}`,
    `widgets ${livingRefs.backed_widget_count ?? 0}/${livingRefs.total_widget_count ?? 0}`,
    `review packets ${reviewPackets.ready_count ?? 0}/${reviewPackets.total_count ?? 0}`,
    `language ${language.ready_to_advertise ? "pass" : "fail"}`,
  ].join("; ");
}

function routeDossierText(route) {
  const dossier = route.route_review_dossier_contract || {};
  const sections = Array.isArray(dossier.sections) ? dossier.sections : [];
  const sectionText = sections
    .map((section) => `${section.label || section.id}: ${section.ready ? "ready" : "incomplete"}`)
    .join("; ");
  return [
    dossier.ready_to_review ? "ready" : "incomplete",
    `sections ${dossier.ready_section_count ?? 0}/${dossier.total_section_count ?? 0}`,
    sectionText,
  ].filter(Boolean).join("; ");
}

function routeImpactText(route) {
  const impact = route.route_impact_summary_contract || {};
  const lines = Array.isArray(impact.summary_lines) ? impact.summary_lines : [];
  const sections = Array.isArray(impact.sections) ? impact.sections : [];
  const sectionText = sections
    .map((section) => `${section.label || section.id}: ${section.ready ? "ready" : "incomplete"}`)
    .join("; ");
  return [
    impact.ready_to_review ? "ready" : "incomplete",
    `sections ${impact.ready_section_count ?? 0}/${impact.total_section_count ?? 0}`,
    ...lines,
    sectionText,
  ].filter(Boolean).join("\n");
}

function renderRouteTable(routes) {
  if (!Array.isArray(routes) || routes.length === 0) return "";
  const wrap = document.createElement("div");
  wrap.className = "index-table-wrap";
  const table = document.createElement("table");
  table.className = "capability-route-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["Route", "Audience", "Why this route matters", "Route claim", "Capabilities", "Backing", "Reviewer dossier", "Boundary"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const route of routes) {
    const row = document.createElement("tr");
    appendCell(row, `${route.id || ""} ${route.title || ""}`);
    appendCell(row, route.audience || "");
    appendCell(row, routeImpactText(route));
    appendCell(row, route.route_claim || "");
    appendCell(row, routeCapabilityLinks(route));
    appendCell(row, routeBackingText(route));
    appendCell(row, routeDossierText(route));
    appendCell(row, route.not_claimed || "");
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

function provenanceCoverageLine(summary) {
  const counts = summary?.proof_provenance_counts || {};
  const parts = [];
  for (const kind of ["mathlib_bridge", "project_native", "mixed"]) {
    if (counts[kind]) parts.push(`${provenanceLabel(kind)} lanes: ${counts[kind]}`);
  }
  return parts.join("\n");
}

function renderManifestSummary(capabilities, summary) {
  if (!summary || !summary.unique_evidence_counts) return renderSummary(capabilities);
  const unique = summary.unique_evidence_counts;
  const totals = summary.evidence_totals || {};
  const provenanceCoverage = provenanceCoverageLine(summary);
  const backing = summary.backing_contract_summary || {};
  const routeSummary = summary.route_summary || {};
  const theoremRefs = backing.theorem_refs || {};
  const sourceRefs = backing.source_refs || {};
  const livingRefs = backing.living_book_refs || {};
  const reviewPackets = backing.review_packets || {};
  const lines = [
    `capability lanes: ${summary.capability_count ?? capabilities.length}`,
    `portfolio routes: ready ${routeSummary.ready_count ?? 0}/${routeSummary.route_count ?? 0}`,
    `route reviewer dossiers: ready ${routeSummary.ready_dossier_count ?? 0}/${routeSummary.route_count ?? 0}`,
    `route impact summaries: ready ${routeSummary.ready_impact_summary_count ?? 0}/${routeSummary.route_count ?? 0}`,
    `role coverage:\n${roleCoverageLine(summary)}`,
    provenanceCoverage ? `proof provenance:\n${provenanceCoverage}` : "",
    `portfolio backing: ${backing.ready_to_advertise ? "ready" : "incomplete"}`,
    `backed theorem refs: ${theoremRefs.proved_and_paper_backed_count ?? 0}/${theoremRefs.total_count ?? 0}`,
    `backed source refs: ${sourceRefs.backed_count ?? 0}/${sourceRefs.total_count ?? 0}`,
    `backed Living Book refs: pages ${livingRefs.backed_page_count ?? 0}/${livingRefs.total_page_count ?? 0}; widgets ${livingRefs.backed_widget_count ?? 0}/${livingRefs.total_widget_count ?? 0}`,
    `review packets: ready ${reviewPackets.ready_count ?? 0}/${reviewPackets.total_count ?? 0}`,
    `unique paper ids: ${unique.paper_count}`,
    `unique proved theorem ids advertised: ${unique.theorem_count}`,
    `unique pytest executable refs: ${unique.executable_count}`,
    `unique source refs: ${unique.source_count}`,
    `unique Living Book page refs: ${unique.living_book_page_count}`,
    `unique Living Book widget refs: ${unique.living_book_widget_count}`,
    `total evidence links: papers ${totals.paper_count ?? 0}; theorems ${totals.theorem_count ?? 0}; sources ${totals.source_count ?? 0}; executables ${totals.executable_count ?? 0}; pages ${totals.living_book_page_count ?? 0}; widgets ${totals.living_book_widget_count ?? 0}`,
  ];
  const node = document.createElement("p");
  node.className = "widget-data";
  node.textContent = lines.filter(Boolean).join("\n");
  return node;
}

function render(panel, data) {
  const capabilities = data.capabilities || [];
  const routes = data.portfolio_routes || [];
  const section = document.createElement("section");
  section.className = "seed-rule-record";

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this matrix summarizes manifest-backed evidence only. It does not turn imported theorem bridges, executable examples, widgets, or benchmarks into new mathematical proofs.";

  section.append(
    renderManifestSummary(capabilities, data.portfolio_summary),
    renderRouteTable(routes),
    renderTable(capabilities),
    warning,
  );
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
