import { positiveInt, rot } from "../shared/circle_math_core.js";
import { addLabeledNumber, addOutput, addWidgetHeader, clear, renderCircleSvg } from "../shared/svg_helpers.js";
import { mountWidgets } from "../shared/widget_base.js";

function mount(panel) {
  addWidgetHeader(panel, "Rotation composition", "Theorem id: CC-T0002");

  const nInput = addLabeledNumber(panel, "rotation-n", "n", 12, 1, 48);
  const startInput = addLabeledNumber(panel, "rotation-start", "start x", 8, 0, 999);
  const aInput = addLabeledNumber(panel, "rotation-a", "stride a", 5, 0, 999);
  const bInput = addLabeledNumber(panel, "rotation-b", "stride b", 7, 0, 999);
  const output = addOutput(panel);

  function render() {
    const n = positiveInt(nInput.value, 12, 1, 48);
    const start = positiveInt(startInput.value, 0, 0, 999) % n;
    const a = positiveInt(aInput.value, 0, 0, 999);
    const b = positiveInt(bInput.value, 0, 0, 999);
    const afterB = rot(n, b, start);
    const afterAB = rot(n, a, afterB);
    const direct = rot(n, a + b, start);
    clear(output);
    output.appendChild(renderCircleSvg({ n, selected: direct, visited: [start, afterB, afterAB], title: "rotation composition" }));
    const data = document.createElement("div");
    data.className = "widget-data";
    data.textContent = [
      `rot(${n}, ${b})(${start}) = ${afterB}`,
      `rot(${n}, ${a})(rot(${n}, ${b})(${start})) = ${afterAB}`,
      `rot(${n}, ${a + b})(${start}) = ${direct}`,
      `composition agrees: ${afterAB === direct}`,
    ].join("\n");
    output.appendChild(data);
  }

  for (const input of [nInput, startInput, aInput, bInput]) {
    input.addEventListener("input", render);
  }
  render();
}

mountWidgets("rotation_composition", mount);
