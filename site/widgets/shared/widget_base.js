const dataCache = new Map();
const REPOSITORY_URL = "https://github.com/corbensorenson/circle-calculus";

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
    if (typeof value === "object" && value.href) {
      const link = document.createElement("a");
      link.href = value.href;
      link.textContent = value.text;
      dd.appendChild(link);
    } else if (typeof value === "object" && value.text) {
      dd.textContent = value.text;
    } else {
      dd.textContent = value;
    }
    dl.append(dt, dd);
  }
  return dl;
}

function githubSourceLink(path, line) {
  if (!path) return "";
  const anchor = line ? `#L${line}` : "";
  return `${REPOSITORY_URL}/blob/main/${path}${anchor}`;
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
      ["Lean", theorem.lean_name ? {
        text: theorem.lean_name,
        href: githubSourceLink(theorem.lean_source, theorem.lean_source_line),
      } : ""],
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

async function hydrateDictionaryIndexes() {
  const data = await loadJson("../../data/generated/dictionary.json");
  for (const target of document.querySelectorAll(".dictionary-index[data-dictionary-index]")) {
    const table = document.createElement("table");
    table.className = "dictionary-index-table";
    const thead = document.createElement("thead");
    thead.innerHTML = "<tr><th>Id</th><th>Term</th><th>Kind</th><th>Source</th></tr>";
    const tbody = document.createElement("tbody");
    for (const entry of data.entries) {
      const tr = document.createElement("tr");
      for (const value of [
        entry.id,
        entry.name || "",
        entry.kind || "",
        entry.source_dictionary || "",
      ]) {
        const td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.append(thead, tbody);
    target.replaceChildren(table);
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
  hydrateDictionaryIndexes().catch((error) => console.error(error));
});
