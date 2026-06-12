import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { loadJson, mountWidgets, statusClass, statusLabel } from "../shared/widget_base.js";

const THEOREM_IDS = ["AIRA-T0011", "AIRA-T0012", "AIRA-T0013", "AIRA-T0014", "AIRA-T0015"];
const DICTIONARY_IDS = ["COMMON-0073", "COMMON-0058", "COMMON-0056"];

function defaultInput(channelCount) {
  return Array.from({ length: channelCount }, (_, index) => ((index * index + 5 * index + 2) % 11) - 5);
}

function defaultKernel(blockSize) {
  return Array.from({ length: blockSize }, (_, row) =>
    Array.from({ length: blockSize }, (_, column) => ((3 * row - 2 * column + row * column + 1) % 9) - 4),
  );
}

function blockCyclicCell(blockSize, row, column) {
  return [mod(row, blockSize), mod(column, blockSize)];
}

function blockCyclicMixerOutput(values, kernel) {
  const blockSize = kernel.length;
  return values.map((_, row) =>
    values.reduce((total, value, column) => total + kernel[mod(row, blockSize)][mod(column, blockSize)] * value, 0),
  );
}

function denseBlockCyclicMatrix(channelCount, kernel) {
  const blockSize = kernel.length;
  return Array.from({ length: channelCount }, (_, row) =>
    Array.from({ length: channelCount }, (_, column) => kernel[mod(row, blockSize)][mod(column, blockSize)]),
  );
}

function denseMatrixVectorProduct(matrix, values) {
  return matrix.map((row) => row.reduce((total, entry, index) => total + entry * values[index], 0));
}

function rotateBlockCyclicKernelRows(kernel, shift) {
  const blockSize = kernel.length;
  return kernel.map((_, row) => kernel[mod(row - shift, blockSize)]);
}

function cellLoads(blockSize, channelCount) {
  const loads = Array.from({ length: blockSize }, () => Array.from({ length: blockSize }, () => 0));
  for (let row = 0; row < channelCount; row += 1) {
    for (let column = 0; column < channelCount; column += 1) {
      const [blockRow, blockColumn] = blockCyclicCell(blockSize, row, column);
      loads[blockRow][blockColumn] += 1;
    }
  }
  return loads;
}

function collisionCount(loads) {
  return loads.reduce(
    (outerTotal, row) => outerTotal + row.reduce((innerTotal, load) => innerTotal + Math.max(0, load - 1), 0),
    0,
  );
}

function maxLoad(loads) {
  return Math.max(...loads.flat());
}

function formatVector(values) {
  return `[${values.join(", ")}]`;
}

function formatMatrix(rows) {
  return rows.map((row) => `[${row.join(", ")}]`).join("\n");
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
  title.textContent = "Block-cyclic cell theorems";
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

function appendOutputTable(record, rows) {
  const table = document.createElement("table");
  table.className = "widget-table";
  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const label of ["channel", "input", "block row", "block output", "dense output", "wrong row shift"]) {
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
      String(row.channel),
      String(row.input),
      String(row.blockRow),
      String(row.block),
      String(row.dense),
      String(row.wrong),
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
  for (const label of ["block row", "cell loads by block column"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = label;
    header.appendChild(th);
  }
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  loads.forEach((row, blockRow) => {
    const tr = document.createElement("tr");
    for (const value of [String(blockRow), formatVector(row)]) {
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
  const input = defaultInput(values.channelCount);
  const kernel = defaultKernel(values.blockSize);
  const denseMatrix = denseBlockCyclicMatrix(values.channelCount, kernel);
  const blockOutput = blockCyclicMixerOutput(input, kernel);
  const denseOutput = denseMatrixVectorProduct(denseMatrix, input);
  const wrongOutput = blockCyclicMixerOutput(input, rotateBlockCyclicKernelRows(kernel, values.wrongRowShift));
  const deltas = blockOutput.map((value, index) => Math.abs(value - denseOutput[index]));
  const mismatchCount = blockOutput.filter((value, index) => value !== wrongOutput[index]).length;
  const denseParameters = values.channelCount * values.channelCount;
  const blockParameters = values.blockSize * values.blockSize;
  const loads = cellLoads(values.blockSize, values.channelCount);

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Block-cyclic mixer validation record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIRA-B0007`,
    `channels: ${values.channelCount}`,
    `block size: ${values.blockSize}`,
    `input: ${formatVector(input)}`,
    `block kernel:\n${formatMatrix(kernel)}`,
    `wrong row shift: ${values.wrongRowShift}`,
    `dense parameters: ${denseParameters}`,
    `block-cyclic parameters: ${blockParameters}`,
    `block-cyclic / dense parameter ratio: ${(blockParameters / denseParameters).toFixed(4)}`,
    `max |block-cyclic - dense|: ${Math.max(...deltas)}`,
    `wrong-row-shift mismatch count: ${mismatchCount}`,
    `cell collision count: ${collisionCount(loads)}`,
    `max cell load: ${maxLoad(loads)}`,
  ].join("\n");
  record.appendChild(data);

  appendOutputTable(
    record,
    input.map((value, channel) => ({
      channel,
      input: value,
      blockRow: mod(channel, values.blockSize),
      block: blockOutput[channel],
      dense: denseOutput[channel],
      wrong: wrongOutput[channel],
    })),
  );
  appendLoadTable(record, loads);

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget validates block-cyclic matrix bookkeeping against a dense matrix and a wrong-row-shift control. It is not a neural-layer quality, runtime, memory, training-stability, or hardware-efficiency claim.";
  record.appendChild(warning);

  appendBadgeRow(record, theoremById);
  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Block-cyclic mixer validation", "Widget: dense parity and alias pressure only");
  const channelInput = addLabeledNumber(panel, "ai-block-cyclic-channels", "channels", 16, 2, 32);
  const blockInput = addLabeledNumber(panel, "ai-block-cyclic-block-size", "block size", 4, 1, 16);
  const wrongShiftInput = addLabeledNumber(panel, "ai-block-cyclic-wrong-shift", "wrong row shift", 1, 0, 15);
  const output = addOutput(panel);
  let theoremById = new Map();

  function render() {
    const blockSize = positiveInt(blockInput.value, 4, 1, 16);
    const values = {
      channelCount: positiveInt(channelInput.value, 16, 2, 32),
      blockSize,
      wrongRowShift: positiveInt(wrongShiftInput.value, 1, 0, blockSize - 1),
    };
    clear(output);
    appendRecord(output, values, theoremById);
  }

  for (const input of [channelInput, blockInput, wrongShiftInput]) {
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

mountWidgets("block_cyclic_mixer_validation", mount);
