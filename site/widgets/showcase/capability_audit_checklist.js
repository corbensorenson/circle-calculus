import { githubSourceLink, loadJson, mountWidgets } from "../shared/widget_base.js";

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

function fallbackClaimContract(capability) {
  const counts = evidenceCounts(capability);
  const roles = new Set(capability.portfolio_roles || []);
  const gates = [
    ["role_contract", "standard parity or Circle-native role", roles.has("standard_math_parity") || roles.has("circle_native_value")],
    ["standard_anchor", "standard math anchor", Boolean(capability.standard_math_anchor)],
    ["circle_expression", "Circle Math expression", Boolean(capability.circle_math_expression)],
    ["circle_native_value", "Circle-native value", Boolean(capability.circle_native_value)],
    ["advertised_claim", "advertised claim", Boolean(capability.advertised_claim)],
    ["proof_scope", "proof scope", Boolean(capability.proof_scope)],
    ["proof_provenance_kind", "proof provenance kind", Boolean(capability.proof_provenance_kind)],
    ["proof_provenance", "proof provenance text", Boolean(capability.proof_provenance)],
    ["paper_backing", "paper backing", counts.paper_count > 0],
    ["proved_theorem_ids", "proved theorem ids", counts.theorem_count > 0],
    ["dictionary_backing", "dictionary backing", counts.dictionary_count > 0],
    ["source_trail", "source trail", counts.source_count > 0],
    ["executable_reference", "executable pytest reference", counts.executable_count > 0],
    ["verification_recipe", "reproducible verification recipe", counts.executable_count > 0],
    ["living_book_presentation", "Living Book presentation", counts.living_book_page_count > 0],
    ["claim_boundary", "not-claimed boundary", Boolean(capability.not_claimed)],
  ].map(([id, label, passed]) => ({ id, label, passed }));
  const passed = gates.filter((gate) => gate.passed).length;
  return {
    status: passed === gates.length ? "ready" : "incomplete",
    ready_to_advertise: passed === gates.length,
    passed_gate_count: passed,
    total_gate_count: gates.length,
    gates,
  };
}

function claimContract(capability) {
  return capability.claim_contract || fallbackClaimContract(capability);
}

function failedGateLabels(contract) {
  return (contract.gates || [])
    .filter((gate) => !gate.passed)
    .map((gate) => gate.label || gate.id)
    .filter(Boolean);
}

function verificationRecipe(capability) {
  return capability.verification_recipe || {
    lean_command: "lake build",
    pytest_command: `python -m pytest ${(capability.executable_refs || []).join(" ")}`.trim(),
    capability_contract_command: "python scripts/check_capability_showcase.py && python scripts/site/check_capability_contracts.py",
    site_command: "make sitecheck",
  };
}

function renderCommand(command) {
  const code = document.createElement("code");
  code.textContent = command || "";
  return code;
}

function renderVerificationRecipe(capability) {
  const recipe = verificationRecipe(capability);
  const dl = document.createElement("dl");
  dl.className = "capability-recipe";
  for (const [label, command] of [
    ["Lean", recipe.lean_command],
    ["Examples", recipe.pytest_command],
    ["Contracts", recipe.capability_contract_command],
    ["Site", recipe.site_command],
  ]) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.appendChild(renderCommand(command));
    dl.append(dt, dd);
  }
  return dl;
}

function renderClaimContract(capability) {
  const contract = claimContract(capability);
  const node = document.createElement("div");
  node.className = "capability-contract";

  const badge = document.createElement("span");
  badge.className = `status-badge ${contract.ready_to_advertise ? "status-proved" : "status-blocked"}`;
  badge.textContent = contract.ready_to_advertise ? "ready to advertise" : "incomplete";

  const detail = document.createElement("p");
  detail.className = "capability-contract-detail";
  detail.textContent = `gates passed: ${contract.passed_gate_count || 0}/${contract.total_gate_count || 0}`;
  node.append(badge, detail);

  const failures = failedGateLabels(contract);
  if (failures.length > 0) {
    const list = document.createElement("ul");
    list.className = "capability-contract-failures";
    for (const failure of failures) {
      const item = document.createElement("li");
      item.textContent = failure;
      list.appendChild(item);
    }
    node.appendChild(list);
  }
  return node;
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

function appendSeparated(fragment, nodes) {
  nodes.forEach((node, index) => {
    if (index > 0) fragment.appendChild(document.createTextNode(", "));
    fragment.appendChild(node);
  });
}

function siteIndexHref(page, id) {
  const url = new URL(`../../${page}`, import.meta.url);
  if (id) url.hash = id;
  return url.toString();
}

function linkedIds(ids, page) {
  const values = Array.isArray(ids) ? ids.filter(Boolean) : [];
  if (values.length === 0) return "";
  const fragment = document.createDocumentFragment();
  appendSeparated(fragment, values.map((id) => makeLink(id, siteIndexHref(page, id))));
  return fragment;
}

function sourcePathFrom(ref) {
  if (!ref) return "";
  if (typeof ref === "string") return ref;
  return ref.path || ref.page || ref.source || "";
}

function linkedRepoPaths(refs) {
  const values = Array.isArray(refs) ? refs.map(sourcePathFrom).filter(Boolean) : [];
  if (values.length === 0) return "";
  const fragment = document.createDocumentFragment();
  appendSeparated(
    fragment,
    values.map((path) => {
      const href = githubSourceLink(path);
      return href ? makeLink(path, href) : document.createTextNode(path);
    }),
  );
  return fragment;
}

function livingBookWidgetIds(refs) {
  const ids = (Array.isArray(refs) ? refs : []).flatMap((ref) => ref.widget_ids || []).filter(Boolean);
  if (ids.length === 0) return "";
  const fragment = document.createDocumentFragment();
  appendSeparated(fragment, ids.map((id) => document.createTextNode(id)));
  return fragment;
}

function auditItem(label, value, details) {
  const item = document.createElement("li");
  item.append(`${label}: ${value}`);
  if (details) {
    item.append(" (");
    if (details instanceof Node) {
      item.appendChild(details);
    } else {
      item.append(String(details));
    }
    item.append(")");
  }
  return item;
}

function checklist(capability) {
  const counts = evidenceCounts(capability);
  const contract = claimContract(capability);
  const failures = failedGateLabels(contract);
  const list = document.createElement("ul");
  list.className = "capability-audit-list";
  const items = [
    auditItem(
      "claim contract gates",
      `${contract.passed_gate_count || 0}/${contract.total_gate_count || 0}`,
      failures.length > 0 ? failures.join(", ") : "all pass",
    ),
    auditItem("papers", counts.paper_count, linkedIds(capability.paper_ids, "papers.html")),
    auditItem("proved theorem ids", counts.theorem_count, linkedIds(capability.theorem_ids, "theorems.html")),
    auditItem("dictionary ids", counts.dictionary_count, linkedIds(capability.dictionary_ids, "dictionary.html")),
    auditItem("pytest executable refs", counts.executable_count, linkedRepoPaths(capability.executable_refs)),
    auditItem("source refs", counts.source_count, linkedRepoPaths(capability.source_refs)),
    auditItem("verification recipe", "present", renderCommand(verificationRecipe(capability).pytest_command)),
    auditItem("Living Book pages", counts.living_book_page_count, linkedRepoPaths(capability.living_book_refs)),
    auditItem("Living Book widgets", counts.living_book_widget_count, livingBookWidgetIds(capability.living_book_refs)),
  ];
  for (const item of items) {
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
  for (const label of ["Capability", "Claim contract", "Proof provenance", "Advertised claim", "Audit checklist", "Reproduce", "Boundary"]) {
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
    appendCell(row, renderClaimContract(capability));
    appendCell(row, `${provenanceLabel(capability.proof_provenance_kind)}: ${capability.proof_provenance || ""}`);
    appendCell(row, capability.advertised_claim || "");
    appendCell(row, checklist(capability));
    appendCell(row, renderVerificationRecipe(capability));
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
  const contracts = summary?.claim_contract_summary || {};
  const node = document.createElement("p");
  node.className = "widget-data";
  node.textContent = [
    `capability lanes: ${summary?.capability_count ?? capabilities.length}`,
    `claim contracts: ready ${contracts.ready_count ?? 0}; incomplete ${contracts.incomplete_count ?? 0}`,
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
