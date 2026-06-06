import { mod, positiveInt } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { mountWidgets } from "../shared/widget_base.js";

function mount(panel) {
  addWidgetHeader(panel, "Finite circle rotator", "Widget: intuition only");

  const nInput = addLabeledNumber(panel, "finite-circle-n", "n", 12, 1, 48);
  const nodeInput = addLabeledNumber(panel, "finite-circle-node", "selected node i", 14, 0, 999);
  const output = addOutput(panel);

  function render() {
    const n = positiveInt(nInput.value, 12, 1, 48);
    const selected = mod(positiveInt(nodeInput.value, 0, 0, 999), n);
    clear(output);
    output.appendChild(renderCircleSvg({ n, selected, title: `C_${n}` }));
    const data = document.createElement("div");
    data.className = "widget-data";
    data.textContent = `C_${n}\nnode(${n}, ${nodeInput.value}) = ${selected} mod ${n}\ndictionary: CC-0001, CC-0002`;
    output.appendChild(data);
  }

  nInput.addEventListener("input", render);
  nodeInput.addEventListener("input", render);
  render();
}

mountWidgets("finite_circle_rotator", mount);
