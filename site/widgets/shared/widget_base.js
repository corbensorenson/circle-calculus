const dataCache = new Map();

function dataUrl(relativePath) {
  const currentScript = document.currentScript;
  const scriptUrl = currentScript ? currentScript.src : import.meta.url;
  return new URL(relativePath, scriptUrl).toString();
}

async function loadJson(relativePath) {
  const url = dataUrl(relativePath);
  if (!dataCache.has(url)) {
    dataCache.set(url, fetch(url).then((response) => {
      if (!response.ok) {
        throw new Error(`failed to load ${url}`);
      }
      return response.json();
    }));
  }
  return dataCache.get(url);
}

function statusLabel(item) {
  const status = item.canonical_status || item.status || "planned";
  if (status === "proved") return "Lean-proved";
  if (status === "exploratory") return "Exploratory";
  if (status === "blocked") return "Blocked";
  if (status === "deferred") return "Deferred";
  if (status === "draft") return "Draft";
  return "Planned theorem";
}

function statusClass(item) {
  const status = item.canonical_status || item.status || "planned";
  return `status-badge status-${status}`;
}

function joinList(value) {
  if (!value || value.length === 0) return "";
  return Array.isArray(value) ? value.join(", ") : String(value);
}

function renderMeta(meta) {
  const dl = document.createElement("dl");
  dl.className = "theorem-meta";
  for (const [label, value] of meta) {
    if (!value) continue;
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    dl.append(dt, dd);
  }
  return dl;
}

async function hydrateTheorems() {
  const data = await loadJson("../../data/generated/theorem_manifest.json");
  const byId = new Map(data.theorems.map((item) => [item.id, item]));
  for (const target of document.querySelectorAll(".theorem-box[data-theorem-id]")) {
    const id = target.dataset.theoremId;
    const theorem = byId.get(id);
    target.classList.add("theorem-card");
    if (!theorem) {
      target.textContent = `Unknown theorem id: ${id}`;
      continue;
    }

    const header = document.createElement("header");
    const title = document.createElement("strong");
    title.textContent = `${theorem.id}: ${theorem.name || theorem.lean_name || "Theorem"}`;
    const badge = document.createElement("span");
    badge.className = statusClass(theorem);
    badge.textContent = statusLabel(theorem);
    header.append(title, badge);

    const statement = document.createElement("p");
    statement.textContent = theorem.informal_statement || theorem.formal_statement || "";

    const meta = renderMeta([
      ["Lean", theorem.lean_name],
      ["Source", theorem.source_manifest],
      ["Paper refs", joinList(theorem.paper_refs)],
      ["Dictionary", joinList(theorem.dictionary_dependencies)],
    ]);

    target.replaceChildren(header, statement, meta);
  }
}

async function hydrateDictionary() {
  const data = await loadJson("../../data/generated/dictionary.json");
  const byId = new Map(data.entries.map((item) => [item.id, item]));
  for (const target of document.querySelectorAll(".dictionary-box[data-dictionary-id]")) {
    const id = target.dataset.dictionaryId;
    const entry = byId.get(id);
    target.classList.add("dictionary-card");
    if (!entry) {
      target.textContent = `Unknown dictionary id: ${id}`;
      continue;
    }

    const header = document.createElement("header");
    const title = document.createElement("strong");
    title.textContent = `${entry.id}: ${entry.name}`;
    header.appendChild(title);

    const definition = document.createElement("p");
    definition.textContent = entry.formal_definition || "";
    const intuition = document.createElement("p");
    intuition.textContent = entry.intuition || "";
    const forbidden = document.createElement("p");
    forbidden.className = "dictionary-meta";
    forbidden.textContent = entry.forbidden_meanings && entry.forbidden_meanings.length
      ? `Forbidden meanings: ${entry.forbidden_meanings.join("; ")}`
      : "";

    target.replaceChildren(header, definition, intuition, forbidden);
  }
}

export function mountWidgets(name, mount) {
  for (const target of document.querySelectorAll(`[data-widget="${name}"]`)) {
    mount(target);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  hydrateTheorems().catch((error) => console.error(error));
  hydrateDictionary().catch((error) => console.error(error));
});
