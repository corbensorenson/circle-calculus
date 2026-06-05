import { positiveInt, windingLift } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { mountWidgets } from "../shared/widget_base.js";

function mount(panel) {
  const header = document.createElement("div");
  header.className = "widget-header";
  header.innerHTML = "<strong>Winding lift explorer</strong><span>Residue plus full turns</span>";
  panel.appendChild(header);

  const nInput = addLabeledNumber(panel, "winding-n", "base n", 5, 1, 48);
  const stepsInput = addLabeledNumber(panel, "winding-steps", "step count t", 17, 0, 999);
  const output = addOutput(panel);

  function render() {
    const n = positiveInt(nInput.value, 5, 1, 48);
    const steps = positiveInt(stepsInput.value, 17, 0, 999);
    const lifted = windingLift(n, steps);
    clear(output);
    output.appendChild(renderCircleSvg({ n, selected: lifted.r, title: "winding lift residue" }));
    const data = document.createElement("div");
    data.className = "widget-data";
    data.textContent = [
      `t = ${steps}`,
      `q = t div n = ${lifted.q}`,
      `r = t mod n = ${lifted.r}`,
      `lifted coordinate = (${lifted.q}, ${lifted.r})`,
      `reconstructed value = ${lifted.value}`,
    ].join("\n");
    output.appendChild(data);
  }

  for (const input of [nInput, stepsInput]) {
    input.addEventListener("input", render);
  }
  render();
}

mountWidgets("winding_lift_explorer", mount);
