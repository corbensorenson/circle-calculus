import { gcd, isPrime, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { mountWidgets } from "../shared/widget_base.js";

function mount(panel) {
  addWidgetHeader(panel, "Prime full-coil explorer", "Theorem id: CC-T0007");

  const nInput = addLabeledNumber(panel, "prime-n", "n", 13, 2, 64);
  const output = addOutput(panel);

  function render() {
    const n = positiveInt(nInput.value, 13, 2, 64);
    const full = [];
    const partial = [];
    for (let k = 1; k < n; k += 1) {
      if (gcd(n, k) === 1) full.push(k);
      else partial.push(k);
    }
    clear(output);
    output.appendChild(renderCircleSvg({ n, visited: full, title: "prime full coil explorer" }));
    const data = document.createElement("div");
    data.className = "widget-data";
    data.textContent = [
      `n = ${n}`,
      `prime by trial division: ${isPrime(n)}`,
      `full-coil strides 1 <= k < n: ${full.join(", ") || "(none)"}`,
      `non-full strides: ${partial.join(", ") || "(none)"}`,
      "This widget computes examples; theorem status comes from the theorem card.",
    ].join("\n");
    output.appendChild(data);
  }

  nInput.addEventListener("input", render);
  render();
}

mountWidgets("prime_full_coil_explorer", mount);
