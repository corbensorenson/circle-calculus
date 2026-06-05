import { gcd, orbitDecomposition, period, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { mountWidgets } from "../shared/widget_base.js";

function mount(panel) {
  const header = document.createElement("div");
  header.className = "widget-header";
  header.innerHTML = "<strong>Period/GCD visualizer</strong><span>Theorem id: CC-T0006</span>";
  panel.appendChild(header);

  const nInput = addLabeledNumber(panel, "period-n", "n", 12, 1, 64);
  const strideInput = addLabeledNumber(panel, "period-stride", "stride k", 4, 0, 999);
  const output = addOutput(panel);

  function render() {
    const n = positiveInt(nInput.value, 12, 1, 64);
    const stride = positiveInt(strideInput.value, 0, 0, 999);
    const cycles = orbitDecomposition(n, stride);
    const g = gcd(n, stride);
    clear(output);
    output.appendChild(renderCircleSvg({ n, visited: cycles[0] || [], title: "period gcd decomposition" }));
    const data = document.createElement("div");
    data.className = "widget-data";
    data.textContent = [
      `gcd(${n}, ${stride}) = ${g}`,
      `number of cycles = ${cycles.length}`,
      `cycle length = ${period(n, stride)}`,
      `cycles: ${cycles.map((cycle) => `[${cycle.join(", ")}]`).join("  ")}`,
    ].join("\n");
    output.appendChild(data);
  }

  for (const input of [nInput, strideInput]) {
    input.addEventListener("input", render);
  }
  render();
}

mountWidgets("period_gcd_visualizer", mount);
