import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIM-T0001", "AIM-T0002", "AIM-T0003", "AIM-T0004", "AIM-T0005"];
const DICTIONARY_IDS = ["COMMON-0028", "COMMON-0029"];

function memorySlot(bankSize, token) {
  return mod(token, bankSize);
}

function tokenWindow(length) {
  return Array.from({ length }, (_, token) => token);
}

function memorySlotLoads(bankSize, tokens) {
  const loads = Array.from({ length: bankSize }, () => 0);
  for (const token of tokens) loads[memorySlot(bankSize, token)] += 1;
  return loads;
}

function memorySlotCollisionCount(bankSize, tokens) {
  return memorySlotLoads(bankSize, tokens)
    .reduce((total, load) => total + Math.max(0, load - 1), 0);
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
  title.textContent = "Theorems";
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

function appendRecord(output, values, theoremById) {
  const tokens = tokenWindow(values.windowLength);
  const loads = memorySlotLoads(values.bankSize, tokens);
  const slot = memorySlot(values.bankSize, values.token);
  const shifted = memorySlot(values.bankSize, values.token + values.bankSize);
  const multiShifted = memorySlot(values.bankSize, values.token + values.passes * values.bankSize);
  const normalizedTwice = memorySlot(values.bankSize, slot);
  const collisions = memorySlotCollisionCount(values.bankSize, tokens);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Cyclic memory-slot record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `bank size: ${values.bankSize}`,
    `token: ${values.token}`,
    `slot token % bank_size: ${slot}`,
    `slot(token + bank_size): ${shifted}`,
    `slot(token + passes * bank_size), passes=${values.passes}: ${multiShifted}`,
    `slot(slot(token)): ${normalizedTwice}`,
    `slot(0): ${memorySlot(values.bankSize, 0)}`,
    `token window: 0..${values.windowLength - 1}`,
    `slot loads: ${loads.map((load, index) => `${index}:${load}`).join(", ")}`,
    `collision count beyond first occupant per used slot: ${collisions}`,
    `closure checks: one_pass=${slot === shifted}, multi_pass=${slot === multiShifted}, idempotent=${slot === normalizedTwice}`,
    "boundary: widget output is finite indexing and collision bookkeeping, not a retrieval-quality or model-improvement claim.",
  ].join("\n");
  record.appendChild(data);
  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Cyclic memory slots", "Widget: finite indexing and alias diagnostics only");
  const bankInput = addLabeledNumber(panel, "ai-memory-bank", "bank size", 8, 1, 64);
  const tokenInput = addLabeledNumber(panel, "ai-memory-token", "token", 19, 0, 999);
  const passesInput = addLabeledNumber(panel, "ai-memory-passes", "passes", 3, 0, 32);
  const windowInput = addLabeledNumber(panel, "ai-memory-window", "token window", 20, 1, 128);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const values = {
      bankSize: positiveInt(bankInput.value, 8, 1, 64),
      token: positiveInt(tokenInput.value, 19, 0, 999),
      passes: positiveInt(passesInput.value, 3, 0, 32),
      windowLength: positiveInt(windowInput.value, 20, 1, 128),
    };
    const tokens = tokenWindow(values.windowLength);
    const visitedSlots = Array.from(new Set(tokens.map((token) => memorySlot(values.bankSize, token))));
    clear(output);
    output.appendChild(renderCircleSvg({
      n: values.bankSize,
      selected: memorySlot(values.bankSize, values.token),
      visited: visitedSlots,
      title: "Cyclic memory bank",
    }));
    appendRecord(output, values, theoremById);
  }

  for (const input of [bankInput, tokenInput, passesInput, windowInput]) {
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

mountWidgets("cyclic_memory_slots", mount);
