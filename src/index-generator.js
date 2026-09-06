const fs = require("node:fs");
const path = require("node:path");

const { applyAtomicFileBatch } = require("./fs-ops");

const GENERATED_MARKER = "<!-- GENERATED FILE — DO NOT EDIT MANUALLY. -->";

function compareStrings(left, right) {
  // Purpose: provide deterministic lexical ordering; Input: two strings; Output: negative, zero, or positive comparison result.
  if (left < right) {
    return -1;
  }
  if (left > right) {
    return 1;
  }
  return 0;
}

function compareSpecs(left, right) {
  // Purpose: order Specs for generated navigation; Input: two Spec summaries; Output: lexical comparison result.
  const topicOrder = compareStrings(String(left.topic), String(right.topic));
  if (topicOrder !== 0) {
    return topicOrder;
  }
  const leftNumber = Number(String(left.id).replace(/^SPEC-/, ""));
  const rightNumber = Number(String(right.id).replace(/^SPEC-/, ""));
  if (Number.isFinite(leftNumber) && Number.isFinite(rightNumber) && leftNumber !== rightNumber) {
    return leftNumber - rightNumber;
  }
  return compareStrings(String(left.id), String(right.id));
}

function compareRecords(left, right) {
  // Purpose: order Runs newest-first with stable tie breaks; Input: two Record summaries; Output: comparison result.
  const leftTime = left.started === null ? Number.NEGATIVE_INFINITY : Date.parse(left.started);
  const rightTime = right.started === null ? Number.NEGATIVE_INFINITY : Date.parse(right.started);
  if (leftTime !== rightTime) {
    return rightTime - leftTime;
  }
  return compareStrings(String(right.runId), String(left.runId));
}

function escapeCell(value) {
  // Purpose: escape text for a Markdown table cell; Input: display value; Output: newline- and pipe-safe string.
  return String(value)
    .replace(/\\/g, "\\\\")
    .replace(/\|/g, "\\|")
    .replace(/\r\n|\r|\n/g, "<br>");
}

function relativeLink(indexPath, targetPath) {
  // Purpose: build an encoded relative Markdown destination; Input: Index path and target path; Output: portable relative link.
  return path.posix.relative(path.posix.dirname(indexPath), targetPath)
    .split("/")
    .map((segment) => encodeURIComponent(segment).replace(
      /[!'()*]/g,
      (character) => `%${character.charCodeAt(0).toString(16).toUpperCase()}`
    ))
    .join("/");
}

function markdownLink(label, indexPath, targetPath) {
  // Purpose: render one safe Markdown link; Input: label, Index path, and target path; Output: Markdown link text.
  return `[${escapeCell(label)}](${relativeLink(indexPath, targetPath)})`;
}

function table(header, rows) {
  // Purpose: render a complete deterministic Markdown table; Input: header cells and row cells; Output: Markdown table text.
  const separator = header.map(() => "---");
  return [
    `| ${header.join(" | ")} |`,
    `| ${separator.join(" | ")} |`,
    ...rows.map((row) => `| ${row.join(" | ")} |`),
  ];
}

function renderGlobalIndex(specs) {
  // Purpose: render the repository-wide Spec Index; Input: normalized Specs; Output: generated Markdown bytes.
  const indexPath = "hello-scholar/specs/INDEX.md";
  const rows = specs.map((spec) => [
    escapeCell(spec.topic),
    markdownLink(spec.id, indexPath, spec.relativePath),
    escapeCell(spec.type),
    escapeCell(spec.status),
    escapeCell(spec.revision),
    escapeCell(spec.summary),
  ]);
  return [
    GENERATED_MARKER,
    "# Specs",
    "",
    ...table(
      ["Topic", "Spec", "Type", "Status", "Revision", "Summary"],
      rows
    ),
    "",
  ].join("\n");
}

function relationCell(spec, indexPath, specsById) {
  // Purpose: render linked supersession relations; Input: Spec, Index path, and ID map; Output: relation cell text.
  const relations = [];
  for (const id of spec.supersedes || []) {
    const target = specsById.get(id);
    relations.push(target
      ? `supersedes ${markdownLink(id, indexPath, target.relativePath)}`
      : `supersedes ${escapeCell(id)}`);
  }
  if (spec.supersededBy) {
    const target = specsById.get(spec.supersededBy);
    relations.push(target
      ? `superseded by ${markdownLink(spec.supersededBy, indexPath, target.relativePath)}`
      : `superseded by ${escapeCell(spec.supersededBy)}`);
  }
  return relations.length === 0 ? "-" : relations.join("; ");
}

function renderTopicIndex(topic, specs, specsById) {
  // Purpose: render one Topic-scoped Spec Index; Input: Topic, Specs, and ID map; Output: generated Markdown bytes.
  const indexPath = `hello-scholar/specs/${topic}/INDEX.md`;
  const rows = specs.map((spec) => [
    markdownLink(spec.id, indexPath, spec.relativePath),
    escapeCell(spec.type),
    escapeCell(spec.status),
    escapeCell(spec.revision),
    escapeCell(spec.summary),
    relationCell(spec, indexPath, specsById),
  ]);
  return [
    GENERATED_MARKER,
    `# Topic: ${topic}`,
    "",
    ...table(
      ["Spec", "Type", "Status", "Revision", "Summary", "Relations"],
      rows
    ),
    "",
  ].join("\n");
}

function renderRunIndex(records, specsById) {
  // Purpose: render the root Run Index; Input: normalized Records and Spec map; Output: generated Markdown bytes.
  const indexPath = "runs/INDEX.md";
  const rows = records.map((record) => {
    const spec = record.spec === null ? null : specsById.get(record.spec);
    return [
      escapeCell(record.runId),
      escapeCell(record.status),
      spec ? markdownLink(record.spec, indexPath, spec.relativePath) : "-",
      record.specRevision === null ? "-" : escapeCell(record.specRevision),
      escapeCell(record.decision),
      escapeCell(record.summary),
      markdownLink("record.md", indexPath, record.relativePath),
    ];
  });
  return [
    GENERATED_MARKER,
    "# Runs",
    "",
    ...table(
      ["Run", "Status", "Spec", "Spec Revision", "Decision", "Summary", "Record"],
      rows
    ),
    "",
  ].join("\n");
}

function renderIndexes(validationResult) {
  // Purpose: build every desired generated Index; Input: validated document graph; Output: relative-path to content map.
  if ((validationResult.errors || []).length > 0) {
    return [];
  }
  const specs = [...(validationResult.specs || [])].sort(compareSpecs);
  const records = [...(validationResult.records || [])].sort(compareRecords);
  const specsById = new Map(specs.map((spec) => [spec.id, spec]));
  const files = [];

  if (specs.length > 0) {
    files.push({
      relativePath: "hello-scholar/specs/INDEX.md",
      content: renderGlobalIndex(specs),
    });
    const topics = [...new Set(specs.map((spec) => spec.topic))].sort(compareStrings);
    for (const topic of topics) {
      files.push({
        relativePath: `hello-scholar/specs/${topic}/INDEX.md`,
        content: renderTopicIndex(
          topic,
          specs.filter((spec) => spec.topic === topic).sort(compareSpecs),
          specsById
        ),
      });
    }
  }
  if (records.length > 0) {
    files.push({ relativePath: "runs/INDEX.md", content: renderRunIndex(records, specsById) });
  }
  return files;
}

function lstatIfPresent(targetPath) {
  // Purpose: inspect an optional Index path; Input: absolute path; Output: lstat result or null; Errors: propagates non-ENOENT failures.
  try {
    return fs.lstatSync(targetPath);
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return null;
    }
    throw error;
  }
}

function inspectIndexPath(projectRoot, relativePath) {
  // Purpose: validate an existing or missing Index target without following links; Input: project root and relative path; Output: safe inspection descriptor.
  const segments = relativePath.split("/");
  const rootPath = path.resolve(projectRoot);
  const absolutePath = path.resolve(rootPath, ...segments);
  const lexical = path.relative(rootPath, absolutePath);
  if (
    relativePath.includes("\\")
    || relativePath.split("/").includes("..")
    || lexical === ".."
    || lexical.startsWith(`..${path.sep}`)
    || path.isAbsolute(lexical)
  ) {
    return { error: "path escapes the project root" };
  }

  let current = rootPath;
  try {
    const rootStat = fs.lstatSync(rootPath);
    if (rootStat.isSymbolicLink() || !rootStat.isDirectory()) {
      return { error: "project root is not a regular directory" };
    }
    for (const segment of segments.slice(0, -1)) {
      current = path.join(current, segment);
      const stat = fs.lstatSync(current);
      if (stat.isSymbolicLink() || !stat.isDirectory()) {
        return { error: "parent path is a symbolic link, junction, or non-directory" };
      }
    }
    const stat = lstatIfPresent(absolutePath);
    if (stat && (stat.isSymbolicLink() || !stat.isFile())) {
      return { error: "target is a symbolic link, junction, or non-file" };
    }
    return { absolutePath, stat };
  } catch (error) {
    return { error: `cannot inspect path${error && error.code ? ` (${error.code})` : ""}` };
  }
}

function hasGeneratedMarker(content) {
  // Purpose: recognize hello-scholar-owned Index bytes; Input: file content; Output: true when the generated marker is present.
  const firstLine = content.split("\n", 1)[0].replace(/\r$/, "");
  return firstLine === GENERATED_MARKER;
}

function isGeneratedIndexPath(relativePath) {
  // Purpose: recognize canonical generated Index locations; Input: relative path; Output: true for global, Topic, or Run Index.
  return relativePath === "hello-scholar/specs/INDEX.md"
    || relativePath === "runs/INDEX.md"
    || /^hello-scholar\/specs\/[^/]+\/INDEX\.md$/.test(relativePath);
}

function indexError(code, pathValue, message) {
  // Purpose: create one normalized Index diagnostic; Input: code, path, and message; Output: diagnostic object.
  return { code, path: pathValue, message };
}

function readIndex(inspection, relativePath, errors) {
  // Purpose: read a validated existing Index; Input: inspection, path, and error sink; Output: UTF-8 content or null; Side effects: appends read errors.
  try {
    return fs.readFileSync(inspection.absolutePath, "utf8");
  } catch (error) {
    const suffix = error && error.code ? ` (${error.code})` : "";
    errors.push(indexError(
      "index-read-error",
      relativePath,
      `cannot read Index${suffix}`
    ));
    return null;
  }
}

function sortIndexErrors(errors) {
  // Purpose: order Index diagnostics deterministically; Input: error array; Output: none; Side effects: sorts input in place.
  errors.sort((left, right) =>
    compareStrings(left.path, right.path)
    || compareStrings(left.code, right.code)
    || compareStrings(left.message, right.message)
  );
}

function prepareIndexBatch({ projectRoot, validationResult, indexPaths = [] }) {
  // Purpose: compute an all-or-nothing Index write/delete batch; Input: project root, validation result, and discovered indexes; Output: batch plus diagnostics; Side effects: reads Index files.
  if ((validationResult.errors || []).length > 0) {
    return {
      errors: [...validationResult.errors],
      renderedFiles: [],
      writes: [],
      deletePaths: [],
      indexStates: [],
    };
  }

  const renderedFiles = renderIndexes(validationResult);
  const renderedByPath = new Map(renderedFiles.map((file) => [file.relativePath, file]));
  const errors = [];
  const proposedWrites = [];
  const proposedDeletes = [];
  const indexStates = [];

  for (const file of renderedFiles) {
    const inspection = inspectIndexPath(projectRoot, file.relativePath);
    if (inspection.error) {
      errors.push(indexError("unsafe-index-path", file.relativePath, inspection.error));
      continue;
    }
    if (!inspection.stat) {
      indexStates.push({ path: file.relativePath, state: "Missing" });
      proposedWrites.push(file);
      continue;
    }
    const current = readIndex(inspection, file.relativePath, errors);
    if (current === null) {
      continue;
    }
    if (!hasGeneratedMarker(current)) {
      errors.push(indexError(
        "index-not-generated",
        file.relativePath,
        "existing Index does not have the exact generated marker"
      ));
      continue;
    }
    if (current === file.content) {
      indexStates.push({ path: file.relativePath, state: "Current" });
    } else {
      indexStates.push({ path: file.relativePath, state: "Stale" });
      proposedWrites.push(file);
    }
  }

  for (const relativePath of [...new Set(indexPaths)].sort(compareStrings)) {
    if (renderedByPath.has(relativePath)) {
      continue;
    }
    if (!isGeneratedIndexPath(relativePath)) {
      errors.push(indexError(
        "unrecognized-index-path",
        relativePath,
        "path is not one of the generated Index locations"
      ));
      continue;
    }
    const inspection = inspectIndexPath(projectRoot, relativePath);
    if (inspection.error) {
      errors.push(indexError("unsafe-index-path", relativePath, inspection.error));
      continue;
    }
    if (!inspection.stat) {
      continue;
    }
    const current = readIndex(inspection, relativePath, errors);
    if (current === null) {
      continue;
    }
    if (!hasGeneratedMarker(current)) {
      errors.push(indexError(
        "index-not-generated",
        relativePath,
        "orphan Index does not have the exact generated marker"
      ));
      continue;
    }
    indexStates.push({ path: relativePath, state: "Stale" });
    proposedDeletes.push(relativePath);
  }

  sortIndexErrors(errors);
  indexStates.sort((left, right) => compareStrings(left.path, right.path));
  return {
    errors,
    renderedFiles,
    writes: errors.length === 0 ? proposedWrites : [],
    deletePaths: errors.length === 0 ? proposedDeletes : [],
    indexStates,
  };
}

function syncIndexBatch({ projectRoot, batch, fileSystem, makeToken }) {
  // Purpose: apply a prepared Index batch atomically; Input: project root, batch, filesystem adapter, and token factory; Output: applied batch summary; Side effects: writes and deletes Index files.
  if (batch.errors.length > 0) {
    throw new Error("cannot sync Index files while validation errors exist");
  }
  applyAtomicFileBatch({
    projectRoot,
    writes: batch.writes,
    deletes: batch.deletePaths,
    ...(fileSystem ? { fileSystem } : {}),
    ...(makeToken ? { makeToken } : {}),
  });
  return {
    writtenPaths: batch.writes.map((file) => file.relativePath),
    deletedPaths: [...batch.deletePaths],
  };
}

module.exports = {
  GENERATED_MARKER,
  prepareIndexBatch,
  renderIndexes,
  syncIndexBatch,
};
