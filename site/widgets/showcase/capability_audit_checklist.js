import { loadJson, mountWidgets } from "../shared/widget_base.js";

function count(value) {
  return Array.isArray(value) ? value.length : 0;
}

function evidenceCounts(capability) {
  return capability.evidence_counts || {
    paper_count: count(capability.paper_ids),
    theorem_count: count(capability.theorem_ids),
    dictionary_count: count(capability.dictionary_ids),
    executable_count: count(capability.executable_refs),
    source_count: count(capability.source_refs),
    living_book_page_count: count(capability.living_book_refs),
    living_book_widget_count: 0,
  };
}

function provenanceLabel(kind) {
  if (kind === "mathlib_bridge") return "mathlib bridge";
  if (kind === "project_native") return "project-native";
  if (kind === "mixed") return "mixed";
  return String(kind || "unspecified").replaceAll("_", " ");
}

function appendCell(row, value) {
  const td = document.createElement("td");
  if (value instanceof Node) {
    td.appendChild(value);
  } else {
    td.textContent = String(value || "");
  }
  row.appendChild(td);
}

function makeLink(text, href) {
  const link = document.createElement("a");
  link.href = href;
  link.textContent = text;
  return link;
}

function idList(ids) {
  const values = Array.isArray(ids) ? ids.filter(Boolean) : [];
  if (values.length === 0) return "";
  return values.join(", ");
}

function checklist(capability) {
  const counts = evidenceCounts(capability);
  const list = document.createElement("ul");
  list.className = "capability-audit-list";
  const items = [
    `papers: ${counts.paper_count} (${idList(capability.paper_ids)})`,
    `proved theorem ids: ${counts.theorem_count} (${idList(capability.theorem_ids)})`,
    `dictionary ids: ${counts.dictionary_count} (${idList(capability.dictionary_ids)})`,
    `pytest executable refs: ${counts.executable_count}`,
    `source refs: ${counts.source_count}`,
    `Living Book pages: ${counts.living_book_page_count}`,
    `Living Book widgets: ${counts.living_book_widget_count}`,
  ];
  for (const text of items) {
    const item = document.createElement("li");
    item.textContent = text;
    list.appendChild(item);
  }
  return list;
}

function renderTable(capabilities) {
  const wrap = document.createElement("div");
  wrap.className = "index-table-wrap";

  const table = document.createElement("table");
  table.className = "capability-audit-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["Capability", "Proof provenance", "Advertised claim", "Audit checklist", "Boundary"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const capability of capabilities) {
    const row = document.createElement("tr");
    const href = new URL(`../../showcase.html#${encodeURIComponent(capability.id)}`, import.meta.url).toString();
    appendCell(row, makeLink(`${capability.id} ${capability.title || ""}`, href));
    appendCell(row, `${provenanceLabel(capability.proof_provenance_kind)}: ${capability.proof_provenance || ""}`);
    appendCell(row, capability.advertised_claim || "");
    appendCell(row, checklist(capability));
    appendCell(row, capability.not_claimed || "");
    tbody.appendChild(row);
  }
  table.appendChild(tbody);
  wrap.appendChild(table);
  return wrap;
}

function renderSummary(capabilities, summary) {
  const unique = summary?.unique_evidence_counts || {};
  const provenance = summary?.proof_provenance_counts || {};
  const node = document.createElement("p");
  node.className = "widget-data";
  node.textContent = [
    `capability lanes: ${summary?.capability_count ?? capabilities.length}`,
    `proof provenance: mathlib bridge ${provenance.mathlib_bridge || 0}; project-native ${provenance.project_native || 0}; mixed ${provenance.mixed || 0}`,
    `unique evidence: papers ${unique.paper_count || 0}; theorem ids ${unique.theorem_count || 0}; executables ${unique.executable_count || 0}; Living Book pages ${unique.living_book_page_count || 0}; widgets ${unique.living_book_widget_count || 0}`,
  ].join("\n");
  return node;
}

function render(panel, data) {
  const capabilities = data.capabilities || [];
  const section = document.createElement("section");
  section.className = "seed-rule-record";
  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: an audit checklist verifies traceability only. It does not turn standard theorem bridges, Python examples, widgets, or paper prose into new proofs.";
  section.append(renderSummary(capabilities, data.portfolio_summary), renderTable(capabilities), warning);
  panel.replaceChildren(section);
}

function mount(panel) {
  panel.textContent = "Loading capability audit checklist...";
  loadJson("../../data/generated/capability_showcase.json")
    .then((data) => render(panel, data))
    .catch((error) => {
      console.error(error);
      panel.textContent = "Capability audit checklist could not load.";
    });
}

mountWidgets("capability_audit_checklist", mount);
