import {
  githubSourceLink,
  looksLikeRepoPath,
} from "../../site/widgets/shared/widget_base.js";

const REPOSITORY_URL = "https://github.com/corbensorenson/circle-calculus";
const failures = [];

function expectEqual(label, actual, expected) {
  if (actual !== expected) {
    failures.push(`${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

function expectTruthy(label, value) {
  if (!value) failures.push(`${label}: expected truthy value`);
}

function expectFalsy(label, value) {
  if (value) failures.push(`${label}: expected falsy value, got ${JSON.stringify(value)}`);
}

expectTruthy("Lean path is a repo path", looksLikeRepoPath("Circle/Core/Rotation.lean"));
expectEqual(
  "Lean source line link",
  githubSourceLink("Circle/Core/Rotation.lean", 9),
  `${REPOSITORY_URL}/blob/main/Circle/Core/Rotation.lean#L9`,
);

expectTruthy("paper path with anchor is a repo path", looksLikeRepoPath("papers/PAPER_01_FINITE_CIRCLES.md#theorem-spine"));
expectEqual(
  "paper anchor link",
  githubSourceLink("papers/PAPER_01_FINITE_CIRCLES.md#theorem-spine"),
  `${REPOSITORY_URL}/blob/main/papers/PAPER_01_FINITE_CIRCLES.md#theorem-spine`,
);

expectTruthy("root README is a repo path", looksLikeRepoPath("README.md"));
expectEqual(
  "root README link",
  githubSourceLink("README.md"),
  `${REPOSITORY_URL}/blob/main/README.md`,
);

expectFalsy("symbolic paper section is not a repo path", looksLikeRepoPath("PAPER_01_FINITE_CIRCLES.section.rotation"));
expectEqual(
  "symbolic paper section does not become a broken GitHub link",
  githubSourceLink("PAPER_01_FINITE_CIRCLES.section.rotation"),
  "",
);

expectFalsy("absolute URL is not re-linked", looksLikeRepoPath("https://example.com/paper.md"));
expectEqual("absolute URL is not re-linked", githubSourceLink("https://example.com/paper.md"), "");

expectFalsy("unsafe parent path is not a repo path", looksLikeRepoPath("../README.md"));
expectEqual("unsafe parent path is not linked", githubSourceLink("../README.md"), "");

if (failures.length > 0) {
  console.error("widget runtime link failures:");
  for (const failure of failures) console.error(failure);
  process.exit(1);
}

console.log("widget runtime links ok");
