export function clear(element) {
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}

let svgIdCounter = 0;

function svgElement(name, attrs = {}) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) {
    el.setAttribute(key, String(value));
  }
  return el;
}

export function renderCircleSvg({ n, selected = null, visited = [], title = "finite circle" }) {
  svgIdCounter += 1;
  const titleId = `circle-svg-title-${svgIdCounter}`;
  const descId = `circle-svg-desc-${svgIdCounter}`;
  const size = 360;
  const cx = size / 2;
  const cy = size / 2;
  const radius = 130;
  const visitedSet = new Set(visited);
  const svg = svgElement("svg", {
    class: "widget-svg",
    viewBox: `0 0 ${size} ${size}`,
    role: "img",
    "aria-labelledby": `${titleId} ${descId}`,
  });

  const titleNode = svgElement("title", { id: titleId });
  titleNode.textContent = `${title} with ${n} nodes`;
  svg.appendChild(titleNode);

  const descNode = svgElement("desc", { id: descId });
  const selectedText = selected === null ? "No selected node." : `Selected node: ${selected}.`;
  const visitedText = visited.length === 0
    ? "No highlighted orbit nodes."
    : `Highlighted orbit nodes: ${visited.join(", ")}.`;
  descNode.textContent = `${selectedText} ${visitedText} Node labels are printed next to each finite-circle point.`;
  svg.appendChild(descNode);

  svg.appendChild(svgElement("circle", {
    cx,
    cy,
    r: radius,
    fill: "none",
    stroke: "#cbd5df",
    "stroke-width": 2,
  }));

  for (let i = 0; i < n; i += 1) {
    const theta = -Math.PI / 2 + (2 * Math.PI * i) / n;
    const x = cx + radius * Math.cos(theta);
    const y = cy + radius * Math.sin(theta);
    const circle = svgElement("circle", {
      class: [
        "node-circle",
        visitedSet.has(i) ? "visited" : "",
        selected === i ? "selected" : "",
      ].filter(Boolean).join(" "),
      cx: x,
      cy: y,
      r: n > 36 ? 6 : 10,
    });
    const titleNode = svgElement("title");
    titleNode.textContent = `node ${i}`;
    circle.appendChild(titleNode);
    svg.appendChild(circle);

    const label = svgElement("text", {
      class: "node-label",
      x,
      y: y + (n > 36 ? 18 : 23),
    });
    label.textContent = String(i);
    svg.appendChild(label);
  }

  return svg;
}

export function addLabeledNumber(panel, id, label, value, min, max) {
  const wrapper = document.createElement("label");
  wrapper.setAttribute("for", id);
  wrapper.textContent = label;
  const input = document.createElement("input");
  input.id = id;
  input.type = "number";
  input.value = String(value);
  input.min = String(min);
  input.max = String(max);
  input.step = "1";
  input.inputMode = "numeric";
  input.setAttribute("aria-label", label);
  wrapper.appendChild(input);
  panel.appendChild(wrapper);
  return input;
}

export function addWidgetHeader(panel, title, subtitle) {
  const header = document.createElement("div");
  header.className = "widget-header";
  const heading = document.createElement("strong");
  heading.textContent = title;
  const meta = document.createElement("span");
  meta.textContent = subtitle;
  header.append(heading, meta);
  panel.appendChild(header);
  return header;
}

export function addOutput(panel) {
  const output = document.createElement("div");
  output.className = "widget-output";
  output.setAttribute("role", "region");
  output.setAttribute("aria-live", "polite");
  output.setAttribute("aria-atomic", "true");
  output.setAttribute("aria-label", "Widget output");
  panel.appendChild(output);
  return output;
}
