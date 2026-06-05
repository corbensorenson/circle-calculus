import { mountWidgets } from "../shared/widget_base.js";

function mount(panel) {
  panel.innerHTML = [
    "<div class=\"widget-header\"><strong>Hopf placeholder</strong><span>Scaffold only</span></div>",
    "<p>This placeholder reserves space for bounded Hopf coordinate exploration. Full fibration topology remains future work.</p>",
  ].join("");
}

mountWidgets("hopf_placeholder", mount);
