import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIRA-T0001", "AIRA-T0002", "AIRA-T0004", "AIRA-T0005"];
const DICTIONARY_IDS = ["COMMON-0056", "COMMON-0030", "COMMON-0031"];

function denseAdapterParameters(channelCount, parametersPerChannel) {
  return channelCount * parametersPerChannel;
}

function loraAdapterParameters(channelCount, parametersPerChannel, rank) {
  return rank * (channelCount + parametersPerChannel);
}

function blockCyclicAdapterParameters(blockSize, parametersPerBlock) {
  return blockSize * parametersPerBlock;
}

function adapterBlockLoads(blockSize, channelCount) {
  const loads = Array.from({ length: blockSize }, () => 0);
  for (let channel = 0; channel < channelCount; channel += 1) {
    loads[mod(channel, blockSize)] += 1;
  }
  return loads;
}

function adapterBlockCollisionCount(loads) {
  return loads.reduce((total, load) => total + Math.max(0, load - 1), 0);
}

function formatRatio(value) {
  return value.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
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
  title.textContent = "Adapter-block indexing theorems";
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

function appendBudgetTable(record, rows) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["scheme", "parameters", "ratio to dense", "role"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const row of rows) {
    const tr = document.createElement("tr");
    for (const value of [
      row.scheme,
      String(row.parameters),
      formatRatio(row.ratio),
      row.role,
    ]) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  record.appendChild(table);
}

function appendLoadTable(record, loads) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["block", "channel load", "extra collisions"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  loads.forEach((load, block) => {
    const tr = document.createElement("tr");
    for (const value of [String(block), String(load), String(Math.max(0, load - 1))]) {
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
  const dense = denseAdapterParameters(values.channelCount, values.parametersPerChannel);
  const lora = loraAdapterParameters(values.channelCount, values.parametersPerChannel, values.rank);
  const block = blockCyclicAdapterParameters(values.blockSize, values.parametersPerChannel);
  const loads = adapterBlockLoads(values.blockSize, values.channelCount);
  const collisionCount = adapterBlockCollisionCount(loads);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Adapter parameter-budget record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIRA-B0004`,
    `channels: ${values.channelCount}`,
    `block size: ${values.blockSize}`,
    `LoRA-style rank: ${values.rank}`,
    `parameters per channel/block: ${values.parametersPerChannel}`,
    `dense parameters: ${dense}`,
    `LoRA-style parameters: ${lora}`,
    `block-cyclic parameters: ${block}`,
    `block-cyclic / dense ratio: ${formatRatio(block / dense)}`,
    `channel collision count: ${collisionCount}`,
    `max block load: ${Math.max(...loads)}`,
  ].join("\n");
  record.appendChild(data);

  appendBudgetTable(record, [
    {
      scheme: "dense per-channel",
      parameters: dense,
      ratio: 1,
      role: "ordinary unshared adapter table",
    },
    {
      scheme: "LoRA-style low rank",
      parameters: lora,
      ratio: lora / dense,
      role: "ordinary low-rank baseline count",
    },
    {
      scheme: "block-cyclic shared table",
      parameters: block,
      ratio: block / dense,
      role: "channels share by channel mod block_size",
    },
  ]);
  appendLoadTable(record, loads);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget counts parameters and alias/load pressure only. It is not evidence about fine-tuning quality, runtime, memory, training stability, or hardware efficiency.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Adapter parameter budget", "Widget: count and alias pressure only");
  const channelInput = addLabeledNumber(panel, "ai-adapter-channel-count", "channels", 128, 1, 512);
  const blockInput = addLabeledNumber(panel, "ai-adapter-block-size", "block size", 8, 1, 64);
  const rankInput = addLabeledNumber(panel, "ai-adapter-rank", "rank", 4, 1, 64);
  const paramInput = addLabeledNumber(panel, "ai-adapter-params", "params per channel", 16, 1, 256);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      channelCount: positiveInt(channelInput.value, 128, 1, 512),
      blockSize: positiveInt(blockInput.value, 8, 1, 64),
      rank: positiveInt(rankInput.value, 4, 1, 64),
      parametersPerChannel: positiveInt(paramInput.value, 16, 1, 256),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [channelInput, blockInput, rankInput, paramInput]) {
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

mountWidgets("adapter_parameter_budget", mount);
