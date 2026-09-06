const fs = require("node:fs");
const path = require("node:path");

const { parseFrontMatter } = require("./frontmatter");

const FORBIDDEN_RUN_DOCUMENTS = new Set([
  "run.json",
  "README.md",
  "report.md",
  "summary.md",
  "final-report.md",
]);
const PRUNED_RUN_DIRECTORIES = new Set([
  "outputs",
  "results",
  "logs",
  "checkpoints",
]);

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

function isOutsideRoot(rootPath, targetPath) {
  // Purpose: detect lexical path escape; Input: trusted root and candidate path; Output: true when candidate is outside root.
  const relativePath = path.relative(rootPath, targetPath);
  return (
    relativePath === ".." ||
    relativePath.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relativePath)
  );
}

function errorCode(error) {
  // Purpose: format an optional filesystem error code; Input: caught value; Output: parenthesized code or empty string.
  return error && typeof error.code === "string" ? ` (${error.code})` : "";
}

function discoverDocuments(projectRoot) {
  // Purpose: discover core, historical, and legacy documents inside one safe project root; Input: project root path; Output: sorted document/path inventory; Side effects: reads filesystem metadata and core files.
  const rootPath = path.resolve(projectRoot);
  const documentsByPath = new Map();
  const legacyPaths = new Set();
  const historicalPaths = new Set();
  const misplacedPaths = new Set();
  const forbiddenRunDocuments = new Set();
  const indexPaths = new Set();
  const unsafePaths = new Map();

  function relativePathFor(segments) {
    // Purpose: render validated path segments for diagnostics; Input: relative path segments; Output: POSIX-style relative path label.
    return segments.length === 0 ? "." : segments.join("/");
  }

  function addUnsafe(segments, reason) {
    // Purpose: record the first unsafe-path diagnosis; Input: path segments and reason; Output: none; Side effects: updates unsafe-path inventory.
    const relativePath = relativePathFor(segments);
    if (!unsafePaths.has(relativePath)) {
      unsafePaths.set(relativePath, { relativePath, reason });
    }
  }

  function result() {
    // Purpose: materialize deterministic discovery output; Input: current discovery accumulators; Output: sorted immutable-facing result object.
    return {
      documents: [...documentsByPath.values()].sort((left, right) =>
        compareStrings(left.relativePath, right.relativePath)
      ),
      legacyPaths: [...legacyPaths].sort(compareStrings),
      historicalPaths: [...historicalPaths].sort(compareStrings),
      misplacedPaths: [...misplacedPaths].sort(compareStrings),
      forbiddenRunDocuments: [...forbiddenRunDocuments].sort(compareStrings),
      unsafePaths: [...unsafePaths.values()].sort((left, right) =>
        compareStrings(left.relativePath, right.relativePath)
      ),
      indexPaths: [...indexPaths].sort(compareStrings),
    };
  }

  let rootRealPath;
  try {
    const rootStat = fs.lstatSync(rootPath);
    if (rootStat.isSymbolicLink()) {
      addUnsafe([], "path is a symbolic link or junction");
      return result();
    }
    if (!rootStat.isDirectory()) {
      addUnsafe([], "expected a directory");
      return result();
    }
    rootRealPath = fs.realpathSync(rootPath);
  } catch (error) {
    addUnsafe([], `cannot inspect project root${errorCode(error)}`);
    return result();
  }

  function inspectPath(segments, expectedType = "any") {
    // Purpose: validate every path component and realpath boundary; Input: segments and expected node type; Output: safe/missing/unsafe inspection; Side effects: records unsafe diagnoses.
    const absolutePath = path.resolve(rootPath, ...segments);
    if (isOutsideRoot(rootPath, absolutePath)) {
      addUnsafe(segments, "path escapes the project root lexically");
      return { status: "unsafe" };
    }

    let currentPath = rootPath;
    for (let index = 0; index < segments.length; index += 1) {
      currentPath = path.join(currentPath, segments[index]);
      const currentSegments = segments.slice(0, index + 1);
      let stat;
      try {
        stat = fs.lstatSync(currentPath);
      } catch (error) {
        if (error && error.code === "ENOENT") {
          return { status: "missing" };
        }
        addUnsafe(currentSegments, `cannot inspect path${errorCode(error)}`);
        return { status: "unsafe" };
      }

      if (stat.isSymbolicLink()) {
        addUnsafe(currentSegments, "path is a symbolic link or junction");
        return { status: "unsafe" };
      }

      const isFinalSegment = index === segments.length - 1;
      if (!isFinalSegment && !stat.isDirectory()) {
        addUnsafe(currentSegments, "expected a directory");
        return { status: "unsafe" };
      }
      if (isFinalSegment && expectedType === "directory" && !stat.isDirectory()) {
        addUnsafe(currentSegments, "expected a directory");
        return { status: "unsafe" };
      }
      if (isFinalSegment && expectedType === "file" && !stat.isFile()) {
        addUnsafe(currentSegments, "expected a regular file");
        return { status: "unsafe" };
      }
      if (isFinalSegment && expectedType === "any" && !stat.isDirectory() && !stat.isFile()) {
        addUnsafe(currentSegments, "expected a regular file or directory");
        return { status: "unsafe" };
      }

      let realPath;
      try {
        realPath = fs.realpathSync(currentPath);
      } catch (error) {
        addUnsafe(currentSegments, `cannot resolve path${errorCode(error)}`);
        return { status: "unsafe" };
      }
      if (isOutsideRoot(rootRealPath, realPath)) {
        addUnsafe(currentSegments, "path resolves outside the project root");
        return { status: "unsafe" };
      }

      if (isFinalSegment) {
        return { status: "safe", absolutePath, stat };
      }
    }

    return {
      status: "safe",
      absolutePath: rootPath,
      stat: fs.lstatSync(rootPath),
    };
  }

  function readDirectory(segments) {
    // Purpose: list one safe directory deterministically; Input: directory segments; Output: sorted names or null; Side effects: records inspection failures.
    const inspection = inspectPath(segments, "directory");
    if (inspection.status !== "safe") {
      return null;
    }
    try {
      return fs.readdirSync(inspection.absolutePath).sort(compareStrings);
    } catch (error) {
      addUnsafe(segments, `cannot list directory${errorCode(error)}`);
      return null;
    }
  }

  function addDocument(segments) {
    // Purpose: parse and register one safe core document; Input: document path segments; Output: none; Side effects: reads file and updates document inventory; Errors: invalid Front Matter propagates.
    const relativePath = relativePathFor(segments);
    if (documentsByPath.has(relativePath)) {
      return;
    }
    const inspection = inspectPath(segments, "file");
    if (inspection.status !== "safe") {
      return;
    }

    let text;
    try {
      text = fs.readFileSync(inspection.absolutePath, "utf8");
    } catch (error) {
      addUnsafe(segments, `cannot read regular file${errorCode(error)}`);
      return;
    }

    const parsed = parseFrontMatter(text, relativePath);
    documentsByPath.set(relativePath, {
      kind: parsed.attributes.kind,
      absolutePath: inspection.absolutePath,
      relativePath,
      attributes: parsed.attributes,
      body: parsed.body,
    });
  }

  function addIndex(segments) {
    // Purpose: register an existing safe generated Index; Input: Index path segments; Output: none; Side effects: updates Index inventory.
    const inspection = inspectPath(segments, "file");
    if (inspection.status === "safe") {
      indexPaths.add(relativePathFor(segments));
    }
  }

  function addHistorical(segments) {
    // Purpose: inventory a retired Plan or Tasks file without parsing its contents; Input: path segments; Output: none; Side effects: checks path safety and updates historical inventory.
    const inspection = inspectPath(segments, "file");
    if (inspection.status === "safe") {
      historicalPaths.add(relativePathFor(segments));
    }
  }

  function inspectMisplacedFile(segments) {
    // Purpose: record and inspect a core document at an invalid path; Input: file segments; Output: none; Side effects: updates misplaced and unsafe inventories.
    misplacedPaths.add(relativePathFor(segments));
    inspectPath(segments, "file");
  }

  function isLegalSpecBundle(segments) {
    // Purpose: recognize the canonical Spec Bundle directory shape; Input: path segments; Output: true for hello-scholar/specs/topic/SPEC-*.
    return (
      segments.length === 4 &&
      segments[0] === "hello-scholar" &&
      segments[1] === "specs" &&
      segments[3].startsWith("SPEC-")
    );
  }

  function scanSpecsDirectory(segments) {
    // Purpose: recursively discover canonical Spec Bundle documents and indexes; Input: directory segments; Output: none; Side effects: reads tree and updates inventories.
    const entries = readDirectory(segments);
    if (entries === null) {
      return;
    }

    const depthBelowSpecs = segments.length - 2;
    if (depthBelowSpecs === 0 || depthBelowSpecs === 1) {
      addIndex([...segments, "INDEX.md"]);
    }
    const legalBundle = isLegalSpecBundle(segments);

    for (const name of entries) {
      if (name === "INDEX.md" && (depthBelowSpecs === 0 || depthBelowSpecs === 1)) {
        continue;
      }

      const childSegments = [...segments, name];
      if (name === "plan.md" || name === "tasks.md") {
        addHistorical(childSegments);
        continue;
      }
      if (name === "spec.md" && legalBundle) {
        addDocument(childSegments);
        continue;
      }

      const expectedType = depthBelowSpecs === 1 && name.startsWith("SPEC-")
        ? "directory"
        : "any";
      const inspection = inspectPath(childSegments, expectedType);
      if (inspection.status === "safe" && inspection.stat.isDirectory()) {
        scanSpecsDirectory(childSegments);
      }
    }
  }

  function scanLegacyDirectory(segments) {
    // Purpose: recursively inventory legacy Markdown documents; Input: legacy directory segments; Output: none; Side effects: reads tree and updates legacy inventory.
    const entries = readDirectory(segments);
    if (entries === null) {
      return;
    }

    for (const name of entries) {
      const childSegments = [...segments, name];
      const inspection = inspectPath(childSegments, "any");
      if (inspection.status !== "safe") {
        continue;
      }
      if (inspection.stat.isDirectory()) {
        scanLegacyDirectory(childSegments);
      } else if (name.endsWith(".md") && name !== "INDEX.md") {
        legacyPaths.add(relativePathFor(childSegments));
      }
    }
  }

  function scanRunDirectory(segments, legalRun, depthBelowRun = 0) {
    // Purpose: inspect one Run while pruning artifact subtrees; Input: Run segments, legality flag, and depth; Output: none; Side effects: updates core, historical, and forbidden-path inventories.
    const entries = readDirectory(segments);
    if (entries === null) {
      return;
    }

    for (const name of entries) {
      // Artifact nodes are name-pruned before inspection so external links remain untouched.
      if (PRUNED_RUN_DIRECTORIES.has(name)) {
        continue;
      }

      const childSegments = [...segments, name];
      if (depthBelowRun === 0 && FORBIDDEN_RUN_DOCUMENTS.has(name)) {
        forbiddenRunDocuments.add(relativePathFor(childSegments));
        inspectPath(childSegments, "file");
        continue;
      }
      if (name === "record.md") {
        if (legalRun && depthBelowRun === 0) {
          addDocument(childSegments);
        } else {
          inspectMisplacedFile(childSegments);
        }
        continue;
      }
      if (name === "plan.md" || name === "tasks.md") {
        addHistorical(childSegments);
        continue;
      }

      const inspection = inspectPath(childSegments, "any");
      if (inspection.status === "safe" && inspection.stat.isDirectory()) {
        scanRunDirectory(childSegments, legalRun, depthBelowRun + 1);
      }
    }
  }

  function scanRunsRoot(segments, legalRoot) {
    // Purpose: discover Run records below a legal or legacy root; Input: root segments and legality flag; Output: none; Side effects: reads tree and updates Run inventories.
    const entries = readDirectory(segments);
    if (entries === null) {
      return;
    }

    if (legalRoot) {
      addIndex([...segments, "INDEX.md"]);
    }

    for (const name of entries) {
      if (legalRoot && name === "INDEX.md") {
        continue;
      }
      const childSegments = [...segments, name];
      if (name === "plan.md" || name === "tasks.md") {
        addHistorical(childSegments);
        continue;
      }
      if (name === "record.md") {
        inspectMisplacedFile(childSegments);
        continue;
      }

      const inspection = inspectPath(childSegments, "any");
      if (inspection.status === "safe" && inspection.stat.isDirectory()) {
        scanRunDirectory(childSegments, legalRoot);
      }
    }
  }

  const helloScholar = inspectPath(["hello-scholar"], "directory");
  if (helloScholar.status === "safe") {
    addDocument(["hello-scholar", "architecture.md"]);
    scanSpecsDirectory(["hello-scholar", "specs"]);
    scanLegacyDirectory(["hello-scholar", "memory"]);
    scanRunsRoot(["hello-scholar", "runs"], false);
  }
  scanRunsRoot(["runs"], true);

  return result();
}

module.exports = {
  discoverDocuments,
};
