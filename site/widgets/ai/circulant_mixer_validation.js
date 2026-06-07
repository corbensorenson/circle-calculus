import { positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear } from "../shared/svg_helpers.js";
import { mountWidgets } from "../shared/widget_base.js";

const DICTIONARY_IDS = ["COMMON-0058", "COMMON-0056", "COMMON-0046"];

function defaultInput(period) {
  return Array.from({ length: period }, (_, index) => ((index * index + 3 * index + 1) % 7) - 3);
}

function defaultKernel(period) {
  const kernel = Array.from({ length: period }, () => 0);
  kernel[0] = 2;
  if (period > 1) kernel[1] = -1;
  if (period > 2) kernel[2] = 1;
  if (period > 4) kernel[4] = -2;
  return kernel;
}

function circularConvolution(values, kernel) {
  const period = values.length;
  return values.map((_, index) =>
    kernel.reduce((total, weight, offset) => total + weight * values[(index - offset + period) % period], 0),
  );
}

function denseCirculantMatrix(kernel) {
  const period = kernel.length;
  return Array.from({ length: period }, (_, row) =>
    Array.from({ length: period }, (_, column) => kernel[(row - column + period) % period]),
  );
}

function denseMatrixVectorProduct(matrix, values) {
  return matrix.map((row) => row.reduce((total, entry, index) => total + entry * values[index], 0));
}

function rotateKernel(kernel, shift) {
  const period = kernel.length;
  return kernel.map((_, index) => kernel[(index - shift + period) % period]);
}

function formatVector(values) {
  return `[${values.join(", ")}]`;
}

function makeLink(id, page) {
  const href = new URL(`../../${page}#${encodeURIComponent(id)}`, import.meta.url).toString();
  const link = document.createElement("a");
  link.href = href;
  link.textContent = id;
  return link;
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
  for (const label of ["index", "input", "kernel", "circulant", "dense", "wrong shift"]) {
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
      String(row.index),
      String(row.input),
      String(row.kernel),
      String(row.circulant),
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

function appendRecord(output, values) {
  const input = defaultInput(values.period);
  const kernel = defaultKernel(values.period);
  const denseMatrix = denseCirculantMatrix(kernel);
  const circulant = circularConvolution(input, kernel);
  const dense = denseMatrixVectorProduct(denseMatrix, input);
  const wrong = circularConvolution(input, rotateKernel(kernel, values.wrongShift));
  const deltas = circulant.map((value, index) => Math.abs(value - dense[index]));
  const mismatchCount = circulant.filter((value, index) => value !== wrong[index]).length;
  const denseParameters = values.period * values.period;
  const circulantParameters = values.period;

  const record = document.createElement("section");
  record.className = "seed-rule-record";
  const title = document.createElement("h3");
  title.textContent = "Circulant mixer validation record";
  record.appendChild(title);

  const data = document.createElement("div");
  data.className = "widget-data";
  data.textContent = [
    `fixture id: AIRA-B0005`,
    `period: ${values.period}`,
    `input: ${formatVector(input)}`,
    `kernel: ${formatVector(kernel)}`,
    `wrong shift: ${values.wrongShift}`,
    `dense parameters: ${denseParameters}`,
    `circulant parameters: ${circulantParameters}`,
    `circulant / dense parameter ratio: ${(circulantParameters / denseParameters).toFixed(4)}`,
    `max |circulant - dense|: ${Math.max(...deltas)}`,
    `wrong-shift mismatch count: ${mismatchCount}`,
  ].join("\n");
  record.appendChild(data);

  appendOutputTable(
    record,
    input.map((value, index) => ({
      index,
      input: value,
      kernel: kernel[index],
      circulant: circulant[index],
      dense: dense[index],
      wrong: wrong[index],
    })),
  );

  const warning = document.createElement("p");
  warning.className = "warning-box";
  warning.textContent = "Boundary: this widget validates exact circular-convolution bookkeeping against a dense circulant matrix and a wrong-shift control. It is not a neural-layer quality, runtime, memory, training-stability, or hardware-efficiency claim.";
  record.appendChild(warning);

  appendDictionaryRow(record);
  output.appendChild(record);
}

function mount(panel) {
  addWidgetHeader(panel, "Circulant mixer validation", "Widget: circular convolution parity only");
  const periodInput = addLabeledNumber(panel, "ai-circulant-period", "period", 8, 2, 16);
  const wrongShiftInput = addLabeledNumber(panel, "ai-circulant-wrong-shift", "wrong shift", 1, 0, 15);
  const output = addOutput(panel);

  function render() {
    const period = positiveInt(periodInput.value, 8, 2, 16);
    const values = {
      period,
      wrongShift: positiveInt(wrongShiftInput.value, 1, 0, period - 1),
    };
    clear(output);
    appendRecord(output, values);
  }

  for (const input of [periodInput, wrongShiftInput]) {
    input.addEventListener("input", render);
  }
  render();
}

mountWidgets("circulant_mixer_validation", mount);
