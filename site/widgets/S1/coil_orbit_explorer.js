import { gcd, orbit, period, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { mountWidgets } from "../shared/widget_base.js";

function mount(panel) {
  const header = document.createElement("div");
  header.className = "widget-header";
  header.innerHTML = "<strong>Coil orbit explorer</strong><span>Theorem id: CC-T0005</span>";
  panel.appendChild(header);

  const nInput = addLabeledNumber(panel, "coil-n", "n", 12, 1, 64);
  const strideInput = addLabeledNumber(panel, "coil-stride", "stride k", 4, 0, 999);
  const startInput = addLabeledNumber(panel, "coil-start", "start", 0, 0, 999);
  const output = addOutput(panel);

  function render() {
    const n = positiveInt(nInput.value, 12, 1, 64);
    const stride = positiveInt(strideInput.value, 0, 0, 999);
    const start = positiveInt(startInput.value, 0, 0, 999) % n;
    const nodes = orbit(n, stride, start);
    const g = gcd(n, stride);
    const predicted = period(n, stride);
    clear(output);
    output.appendChild(renderCircleSvg({ n, selected: start, visited: nodes, title: "coil orbit" }));
    const data = document.createElement("div");
    data.className = "widget-data";
    data.textContent = [
      `orbit sequence: ${nodes.join(" -> ")} -> ${nodes[0]}`,
      `gcd(${n}, ${stride}) = ${g}`,
      `predicted period n/gcd(n,k) = ${predicted}`,
      `actual orbit length = ${nodes.length}`,
      `closed loop: ${nodes.length === predicted}`,
    ].join("\n");
    output.appendChild(data);
  }

  for (const input of [nInput, strideInput, startInput]) {
    input.addEventListener("input", render);
  }
  render();
}

mountWidgets("coil_orbit_explorer", mount);
