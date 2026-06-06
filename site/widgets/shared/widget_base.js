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
    if (value instanceof Node) {
      dd.appendChild(value);
    } else if (typeof value === "object" && value.href) {
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
  const mode = !line && !/\.[^/]+$/.test(path) ? "tree" : "blob";
  return `${REPOSITORY_URL}/${mode}/main/${path}${anchor}`;
}

function makeLink(text, href) {
  if (!href) return text || "";
  const link = document.createElement("a");
  link.href = href;
  link.textContent = text || href;
  return link;
}

function sitePageLink(page, filter) {
  const url = new URL(`../../${page}`, import.meta.url);
  if (filter) url.hash = filter;
  return url.toString();
}

function makeIndexLink(text, page, filter) {
  return makeLink(text, sitePageLink(page, filter || text));
}

function idsFrom(items) {
  if (!items) return [];
  const values = Array.isArray(items) ? items : [items];
  return values
    .map((item) => typeof item === "object" ? item.id : item)
    .filter(Boolean);
}

function sourcePathFrom(item) {
  if (!item) return "";
  if (typeof item === "string") return item;
  return item.path || item.source_manifest || item.lean_source || item.source || "";
}

function appendSeparatedLinks(fragment, nodes) {
  nodes.forEach((node, index) => {
    if (index > 0) fragment.appendChild(document.createTextNode(", "));
    fragment.appendChild(node);
  });
}

function linkedCompactIds(items, page, limit = 6) {
  const ids = idsFrom(items);
  if (ids.length === 0) return "";
  const fragment = document.createDocumentFragment();
  appendSeparatedLinks(
    fragment,
    ids.slice(0, limit).map((id) => makeIndexLink(id, page, id)),
  );
  if (ids.length > limit) {
    fragment.appendChild(document.createTextNode(` + ${ids.length - limit} more`));
  }
  return fragment;
}

function linkedRepoPaths(items, limit = 4) {
  if (!items || items.length === 0) return "";
  const values = Array.isArray(items) ? items : [items];
  const links = [];
  for (const item of values.slice(0, limit)) {
    const path = sourcePathFrom(item);
    if (!path) continue;
    const text = typeof item === "object" ? item.id || path : path;
    links.push(makeLink(text, githubSourceLink(path)));
  }
  if (links.length === 0) return "";
  const fragment = document.createDocumentFragment();
  appendSeparatedLinks(fragment, links);
  if (values.length > limit) {
    fragment.appendChild(document.createTextNode(` + ${values.length - limit} more`));
  }
  return fragment;
}

function appendCell(tr, value) {
  const td = document.createElement("td");
  if (value instanceof Node) {
    td.appendChild(value);
  } else {
    td.textContent = value || "";
  }
  tr.appendChild(td);
}

function compactIds(items, limit = 6) {
  if (!items || items.length === 0) return "";
  const ids = items.map((item) => item.id).filter(Boolean);
  if (ids.length <= limit) return ids.join(", ");
  return `${ids.slice(0, limit).join(", ")} + ${ids.length - limit} more`;
}

function filterText(item) {
  return JSON.stringify(item).toLowerCase();
}

function renderFilterableIndex(target, items, columns, options = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = "filterable-index";

  const tools = document.createElement("div");
  tools.className = "index-tools";

  const label = document.createElement("label");
  label.textContent = options.label || "Filter";

  const input = document.createElement("input");
  input.type = "search";
  input.placeholder = options.placeholder || "Filter entries";
  input.setAttribute("aria-label", options.placeholder || "Filter entries");
  if (options.hashFilter) {
    input.value = readHashFilter();
  }
  label.appendChild(input);

  const count = document.createElement("span");
  count.className = "index-count";
  tools.append(label, count);

  const tableWrap = document.createElement("div");
  tableWrap.className = "index-table-wrap";

  function renderTable() {
    const needle = input.value.trim().toLowerCase();
    let rows = items;
    if (needle) {
      const primaryKey = options.primaryKey || "id";
      const exactRows = items.filter((item) => String(item[primaryKey] || "").toLowerCase() === needle);
      rows = exactRows.length > 0
        ? exactRows
        : items.filter((item) => filterText(item).includes(needle));
    }

    const table = document.createElement("table");
    table.className = options.tableClass || "generated-index-table";
    const thead = document.createElement("thead");
    const header = document.createElement("tr");
    for (const column of columns) {
      const th = document.createElement("th");
      th.textContent = column.label;
      header.appendChild(th);
    }
    thead.appendChild(header);

    const tbody = document.createElement("tbody");
    for (const item of rows) {
      const tr = document.createElement("tr");
      for (const column of columns) {
        appendCell(tr, column.render(item));
      }
      tbody.appendChild(tr);
    }

    table.append(thead, tbody);
    tableWrap.replaceChildren(table);
    count.textContent = `${rows.length} of ${items.length}`;
  }

  input.addEventListener("input", () => {
    if (options.hashFilter) updateHashFilter(input.value);
    renderTable();
  });
  if (options.hashFilter) {
    window.addEventListener("hashchange", () => {
      input.value = readHashFilter();
      renderTable();
    });
  }
  wrapper.append(tools, tableWrap);
  target.replaceChildren(wrapper);
  renderTable();
}

function readHashFilter() {
  const raw = window.location.hash.slice(1);
  if (!raw) return "";
  try {
    return decodeURIComponent(raw).trim();
  } catch {
    return raw.trim();
  }
}

function updateHashFilter(value) {
  const url = new URL(window.location.href);
  const needle = value.trim();
  url.hash = needle || "";
  history.replaceState(null, "", url);
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
      ["Used by papers", linkedCompactIds(theorem.used_by_papers, "papers.html", 4)],
      ["Paper refs", linkedRepoPaths(theorem.paper_refs)],
      ["Dictionary", linkedCompactIds(theorem.dictionary_dependencies, "dictionary.html")],
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
    const meta = renderMeta([
      ["Source", {
        text: entry.source_dictionary,
        href: githubSourceLink(entry.source_dictionary),
      }],
      ["Lean", joinList(entry.lean_declarations)],
      ["Python", joinList(entry.python_objects)],
      ["Used by theorems", linkedCompactIds(entry.used_by_theorems, "theorems.html")],
      ["Used by papers", linkedCompactIds(entry.used_by_papers, "papers.html", 4)],
      ["Used by widgets", linkedRepoPaths(entry.used_by_widgets)],
      ["Used by glyphs", linkedCompactIds(entry.used_by_glyphs, "chapters/phase2/proof_carrying_glyphs.html")],
    ]);

    target.replaceChildren(header, definition, intuition, forbidden, meta);
  }
}

async function hydrateDictionaryIndexes() {
  const data = await loadJson("../../data/generated/dictionary.json");
  for (const target of document.querySelectorAll(".dictionary-index[data-dictionary-index]")) {
    renderFilterableIndex(
      target,
      data.entries,
      [
        { label: "Id", render: (entry) => makeIndexLink(entry.id, "dictionary.html", entry.id) },
        { label: "Term", render: (entry) => entry.name || "" },
        { label: "Kind", render: (entry) => entry.kind || "" },
        { label: "Source", render: (entry) => makeLink(entry.source_dictionary, githubSourceLink(entry.source_dictionary)) },
        { label: "Theorems", render: (entry) => linkedCompactIds(entry.used_by_theorems, "theorems.html") },
        { label: "Papers", render: (entry) => linkedCompactIds(entry.used_by_papers, "papers.html", 4) },
        { label: "Widgets", render: (entry) => linkedRepoPaths(entry.used_by_widgets) },
      ],
      {
        placeholder: "Filter by id, term, kind, theorem, paper, widget, or source",
        tableClass: "dictionary-index-table",
        hashFilter: true,
        primaryKey: "id",
      },
    );
  }
}

async function hydrateTheoremIndexes() {
  const data = await loadJson("../../data/generated/theorem_manifest.json");
  for (const target of document.querySelectorAll(".theorem-index[data-theorem-index]")) {
    renderFilterableIndex(
      target,
      data.theorems,
      [
        { label: "Id", render: (theorem) => makeIndexLink(theorem.id, "theorems.html", theorem.id) },
        {
          label: "Status",
          render: (theorem) => {
            const badge = document.createElement("span");
            badge.className = statusClass(theorem);
            badge.textContent = statusLabel(theorem);
            return badge;
          },
        },
        { label: "Name", render: (theorem) => theorem.name || theorem.informal_statement || "" },
        {
          label: "Lean",
          render: (theorem) => theorem.lean_name
            ? makeLink(theorem.lean_name, githubSourceLink(theorem.lean_source, theorem.lean_source_line))
            : "",
        },
        { label: "Dictionary", render: (theorem) => linkedCompactIds(theorem.dictionary_dependencies, "dictionary.html") },
        { label: "Papers", render: (theorem) => linkedCompactIds(theorem.used_by_papers, "papers.html", 4) },
        { label: "Refs", render: (theorem) => linkedRepoPaths(theorem.paper_refs, 2) },
        { label: "Source", render: (theorem) => makeLink(theorem.source_manifest, githubSourceLink(theorem.source_manifest)) },
      ],
      {
        placeholder: "Filter by theorem id, status, Lean name, dictionary id, or source",
        tableClass: "theorem-index-table",
        hashFilter: true,
        primaryKey: "id",
      },
    );
  }
}

async function hydratePaperIndexes() {
  const data = await loadJson("../../data/generated/paper_index.json");
  for (const target of document.querySelectorAll(".paper-index[data-paper-index]")) {
    renderFilterableIndex(
      target,
      data.papers,
      [
        { label: "Id", render: (paper) => makeIndexLink(paper.id || "", "papers.html", paper.id || "") },
        { label: "Status", render: (paper) => paper.status || "" },
        { label: "Title", render: (paper) => paper.title || "" },
        { label: "Paper", render: (paper) => makeLink(paper.path, githubSourceLink(paper.path)) },
        { label: "Sidecar", render: (paper) => makeLink(paper.sidecar, githubSourceLink(paper.sidecar)) },
        { label: "Theorems", render: (paper) => linkedCompactIds(paper.theorem_ids, "theorems.html") },
        { label: "Dictionary", render: (paper) => linkedCompactIds(paper.dictionary_ids, "dictionary.html") },
      ],
      {
        placeholder: "Filter by paper id, title, theorem id, dictionary id, or sidecar",
        tableClass: "paper-index-table",
        hashFilter: true,
        primaryKey: "id",
      },
    );
  }
}

async function hydrateTargetIndexes() {
  const indexFiles = {
    phase4: "../../data/generated/phase4_targets.json",
    phase5: "../../data/generated/phase5_targets.json",
    phase6: "../../data/generated/phase6_targets.json",
  };
  for (const target of document.querySelectorAll(".target-index[data-target-index]")) {
    const indexName = target.dataset.targetIndex || "phase4";
    const data = await loadJson(indexFiles[indexName] || indexFiles.phase4);
    renderFilterableIndex(
      target,
      data.targets,
      [
        { label: "Id", render: (item) => makeIndexLink(item.id || "", "targets.html", item.id || "") },
        { label: "Layer/Area", render: (item) => item.layer || item.area || "" },
        { label: "Status", render: (item) => item.status || "" },
        { label: "Priority", render: (item) => item.priority || "" },
        { label: "Title", render: (item) => item.title || item.objective || "" },
        { label: "Theorem", render: (item) => linkedCompactIds(item.promoted_theorem_id, "theorems.html") },
        { label: "Dictionary", render: (item) => linkedCompactIds(item.dictionary_dependencies, "dictionary.html", 4) },
        { label: "Refs", render: (item) => linkedRepoPaths(item.paper_refs || item.artifact_refs, 3) },
        { label: "Next Action", render: (item) => item.next_action || "" },
      ],
      {
        placeholder: "Filter by target id, area, status, title, or next action",
        tableClass: "target-index-table",
        hashFilter: true,
        primaryKey: "id",
      },
    );
  }
}

async function hydrateGlyphIndexes() {
  const data = await loadJson("../../data/generated/glyph_index.json");
  for (const target of document.querySelectorAll(".glyph-index")) {
    renderFilterableIndex(
      target,
      data.glyphs,
      [
        { label: "Glyph", render: (item) => makeIndexLink(item.id || "", "chapters/phase2/proof_carrying_glyphs.html", item.id || "") },
        { label: "Theorem", render: (item) => linkedCompactIds(item.theorem_id, "theorems.html") },
        { label: "Status", render: (item) => item.status_label || "" },
        {
          label: "Lean",
          render: (item) => makeLink(item.lean_name, githubSourceLink(item.lean_source, item.lean_source_line)),
        },
        { label: "Dictionary", render: (item) => linkedCompactIds(item.dictionary_ids, "dictionary.html") },
        { label: "Papers", render: (item) => linkedRepoPaths(item.paper_refs, 3) },
        { label: "Caption", render: (item) => item.caption || "" },
      ],
      {
        placeholder: "Filter by glyph id, theorem id, status, Lean name, or dictionary id",
        tableClass: "glyph-index-table",
        hashFilter: true,
        primaryKey: "id",
      },
    );
  }
}

export function mountWidgets(name, mount) {
  for (const target of document.querySelectorAll(`[data-widget="${name}"]`)) {
    target.setAttribute("role", "region");
    target.setAttribute("aria-label", `${name.replaceAll("_", " ")} widget`);
    mount(target);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  hydrateTheorems().catch((error) => console.error(error));
  hydrateDictionary().catch((error) => console.error(error));
  hydrateDictionaryIndexes().catch((error) => console.error(error));
  hydrateTheoremIndexes().catch((error) => console.error(error));
  hydratePaperIndexes().catch((error) => console.error(error));
  hydrateTargetIndexes().catch((error) => console.error(error));
  hydrateGlyphIndexes().catch((error) => console.error(error));
});
