const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { discoverDocuments } = require("../src/document-discovery");

function makeTempDirectory(prefix) {
  // Purpose: create an isolated discovery fixture root; Input: temporary-directory prefix; Output: absolute directory path; Side effects: creates the directory.
  return fs.mkdtempSync(path.join(os.tmpdir(), prefix));
}

function writeFile(root, relativePath, content) {
  // Purpose: populate one discovery fixture file; Input: fixture root, POSIX-style relative path, and UTF-8 content; Output: absolute file path; Side effects: creates parents and writes the file.
  const targetPath = path.join(root, ...relativePath.split("/"));
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
  fs.writeFileSync(targetPath, content, "utf8");
  return targetPath;
}

function writeDocument(root, relativePath, kind, body = "# Body\n") {
  // Purpose: write a minimal core document fixture; Input: root, relative path, kind, and optional body; Output: absolute file path; Side effects: writes the document.
  return writeFile(root, relativePath, `---\nschema: 1\nkind: ${kind}\n---\n${body}`);
}

function makeDirectory(root, relativePath) {
  // Purpose: create one fixture directory; Input: root and POSIX-style relative path; Output: absolute directory path; Side effects: creates the directory tree.
  const targetPath = path.join(root, ...relativePath.split("/"));
  fs.mkdirSync(targetPath, { recursive: true });
  return targetPath;
}

function makeDirectoryLink(targetPath, linkPath) {
  // Purpose: create a portable directory-link fixture; Input: link target and link path; Output: none; Side effects: creates parent directories and a symlink or junction.
  fs.mkdirSync(path.dirname(linkPath), { recursive: true });
  fs.symlinkSync(targetPath, linkPath, process.platform === "win32" ? "junction" : "dir");
}

function makeFileLink(targetPath, linkPath) {
  // Purpose: create a file-link fixture; Input: link target and link path; Output: none; Side effects: creates parent directories and a symlink.
  fs.mkdirSync(path.dirname(linkPath), { recursive: true });
  fs.symlinkSync(targetPath, linkPath, "file");
}

function removeDirectories(...directories) {
  // Purpose: clean isolated discovery fixtures; Input: directory paths; Output: none; Side effects: recursively removes those directories.
  for (const directory of directories) {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

function relativeDocumentPaths(result) {
  // Purpose: project discovery results to comparable paths; Input: discovery result; Output: ordered relative document paths.
  return result.documents.map((document) => document.relativePath);
}

test("discovers only legal documents and reports non-core paths deterministically", () => {
  const projectRoot = makeTempDirectory("hello-scholar-discovery-");
  try {
    writeDocument(projectRoot, "hello-scholar/architecture.md", "architecture", "# Architecture\n");
    writeDocument(
      projectRoot,
      "hello-scholar/specs/zeta/SPEC-010-later/spec.md",
      "spec",
      "# Later\n"
    );
    writeDocument(
      projectRoot,
      "hello-scholar/specs/alpha/SPEC-002-first/spec.md",
      "spec",
      "# First\n"
    );
    writeDocument(
      projectRoot,
      "hello-scholar/specs/alpha/SPEC-002-first/plan.md",
      "plan"
    );
    writeDocument(
      projectRoot,
      "hello-scholar/specs/alpha/SPEC-002-first/tasks.md",
      "tasks"
    );
    writeDocument(projectRoot, "runs/20260801-1200-eval/record.md", "record", "# Run\n");

    writeFile(projectRoot, "hello-scholar/specs/INDEX.md", "generated global index\n");
    writeFile(projectRoot, "hello-scholar/specs/alpha/INDEX.md", "generated topic index\n");
    writeFile(projectRoot, "hello-scholar/specs/zeta/INDEX.md", "generated topic index\n");
    writeFile(projectRoot, "runs/INDEX.md", "generated run index\n");

    writeFile(projectRoot, "hello-scholar/memory/specs/2025-legacy.md", "not front matter\n");
    writeFile(projectRoot, "hello-scholar/memory/cache/data.json", "{}\n");
    writeFile(projectRoot, "hello-scholar/specs/alpha/orphan/plan.md", "not front matter\n");
    writeFile(projectRoot, "hello-scholar/specs/tasks.md", "not front matter\n");
    writeFile(projectRoot, "hello-scholar/runs/old-place/record.md", "not front matter\n");
    writeFile(projectRoot, "runs/20260801-1200-eval/nested/record.md", "not front matter\n");

    for (const fileName of [
      "run.json",
      "README.md",
      "report.md",
      "summary.md",
      "final-report.md",
    ]) {
      writeFile(projectRoot, `runs/20260801-1200-eval/${fileName}`, "not a core document\n");
    }

    for (const directoryName of ["outputs", "results", "logs", "checkpoints"]) {
      writeFile(
        projectRoot,
        `runs/20260801-1200-eval/${directoryName}/deep/record.md`,
        "not front matter\n"
      );
      writeFile(
        projectRoot,
        `runs/20260801-1200-eval/${directoryName}/README.md`,
        "ignored\n"
      );
    }

    const first = discoverDocuments(projectRoot);
    const second = discoverDocuments(projectRoot);
    const expectedDocumentPaths = [
      "hello-scholar/architecture.md",
      "hello-scholar/specs/alpha/SPEC-002-first/spec.md",
      "hello-scholar/specs/zeta/SPEC-010-later/spec.md",
      "runs/20260801-1200-eval/record.md",
    ];

    assert.deepEqual(first, second);
    assert.deepEqual(relativeDocumentPaths(first), expectedDocumentPaths);
    assert.deepEqual(first.documents.map((document) => document.kind), [
      "architecture",
      "spec",
      "spec",
      "record",
    ]);
    assert.equal(first.documents[0].body, "# Architecture\n");
    for (const document of first.documents) {
      assert.equal(document.absolutePath, path.join(projectRoot, ...document.relativePath.split("/")));
      assert.equal(document.attributes.kind, document.kind);
    }

    assert.deepEqual(first.legacyPaths, ["hello-scholar/memory/specs/2025-legacy.md"]);
    assert.deepEqual(first.historicalPaths, [
      "hello-scholar/specs/alpha/SPEC-002-first/plan.md",
      "hello-scholar/specs/alpha/SPEC-002-first/tasks.md",
      "hello-scholar/specs/alpha/orphan/plan.md",
      "hello-scholar/specs/tasks.md",
    ]);
    assert.deepEqual(first.misplacedPaths, [
      "hello-scholar/runs/old-place/record.md",
      "runs/20260801-1200-eval/nested/record.md",
    ]);
    assert.deepEqual(first.forbiddenRunDocuments, [
      "runs/20260801-1200-eval/README.md",
      "runs/20260801-1200-eval/final-report.md",
      "runs/20260801-1200-eval/report.md",
      "runs/20260801-1200-eval/run.json",
      "runs/20260801-1200-eval/summary.md",
    ]);
    assert.deepEqual(first.indexPaths, [
      "hello-scholar/specs/INDEX.md",
      "hello-scholar/specs/alpha/INDEX.md",
      "hello-scholar/specs/zeta/INDEX.md",
      "runs/INDEX.md",
    ]);
    assert.deepEqual(first.unsafePaths, []);
  } finally {
    removeDirectories(projectRoot);
  }
});

test("reports linked parents, core files, indexes, dangling links, and loops without reading them", () => {
  const projectRoot = makeTempDirectory("hello-scholar-links-");
  const externalRoot = makeTempDirectory("hello-scholar-external-");
  try {
    const internalTarget = writeFile(projectRoot, "private-architecture.md", "INTERNAL SENTINEL\n");
    const externalPlan = writeFile(externalRoot, "plan.md", "EXTERNAL PLAN SENTINEL\n");
    const externalRecord = writeFile(externalRoot, "record.md", "EXTERNAL RECORD SENTINEL\n");
    const externalIndex = writeFile(externalRoot, "INDEX.md", "EXTERNAL INDEX SENTINEL\n");
    const externalTopicSpec = writeFile(
      externalRoot,
      "topic/SPEC-999-external/spec.md",
      "---\nkind: spec\n---\nEXTERNAL TOPIC SENTINEL\n"
    );
    const externalRunRecord = writeFile(
      externalRoot,
      "run/record.md",
      "---\nkind: record\n---\nEXTERNAL RUN SENTINEL\n"
    );
    const before = new Map(
      [
        internalTarget,
        externalPlan,
        externalRecord,
        externalIndex,
        externalTopicSpec,
        externalRunRecord,
      ].map((filePath) => [filePath, fs.readFileSync(filePath)])
    );

    makeFileLink(internalTarget, path.join(projectRoot, "hello-scholar", "architecture.md"));
    makeFileLink(externalIndex, path.join(projectRoot, "hello-scholar", "specs", "INDEX.md"));
    makeDirectoryLink(
      path.join(externalRoot, "topic"),
      path.join(projectRoot, "hello-scholar", "specs", "linked-topic")
    );
    writeDocument(projectRoot, "hello-scholar/specs/safe/SPEC-002-safe/spec.md", "spec");
    makeFileLink(
      externalPlan,
      path.join(projectRoot, "hello-scholar", "specs", "safe", "SPEC-002-safe", "plan.md")
    );
    makeFileLink(
      path.join(externalRoot, "missing-tasks.md"),
      path.join(projectRoot, "hello-scholar", "specs", "safe", "SPEC-002-safe", "tasks.md")
    );

    makeFileLink(externalRecord, path.join(projectRoot, "runs", "safe-run", "record.md"));
    makeDirectoryLink(path.join(externalRoot, "run"), path.join(projectRoot, "runs", "linked-run"));
    makeDirectoryLink("loop-run", path.join(projectRoot, "runs", "loop-run"));

    const result = discoverDocuments(projectRoot);

    assert.deepEqual(relativeDocumentPaths(result), [
      "hello-scholar/specs/safe/SPEC-002-safe/spec.md",
    ]);
    assert.deepEqual(
      result.unsafePaths.map((entry) => entry.relativePath),
      [
        "hello-scholar/architecture.md",
        "hello-scholar/specs/INDEX.md",
        "hello-scholar/specs/linked-topic",
        "hello-scholar/specs/safe/SPEC-002-safe/plan.md",
        "hello-scholar/specs/safe/SPEC-002-safe/tasks.md",
        "runs/linked-run",
        "runs/loop-run",
        "runs/safe-run/record.md",
      ]
    );
    for (const unsafePath of result.unsafePaths) {
      assert.match(unsafePath.reason, /symbolic link|junction/i);
      assert.equal(unsafePath.reason.includes(projectRoot), false);
      assert.equal(unsafePath.reason.includes(externalRoot), false);
    }
    for (const [filePath, contents] of before) {
      assert.deepEqual(fs.readFileSync(filePath), contents);
    }
  } finally {
    removeDirectories(projectRoot, externalRoot);
  }
});

test("prunes external artifact links but rejects linked runs roots and run directories", () => {
  const projectRoot = makeTempDirectory("hello-scholar-pruned-");
  const linkedRootProject = makeTempDirectory("hello-scholar-linked-root-");
  const linkedRunProject = makeTempDirectory("hello-scholar-linked-run-");
  const externalRoot = makeTempDirectory("hello-scholar-artifacts-");
  try {
    writeDocument(projectRoot, "runs/local-run/record.md", "record");
    const externalFiles = [];
    for (const directoryName of ["outputs", "results", "logs", "checkpoints"]) {
      const externalDirectory = makeDirectory(externalRoot, directoryName);
      externalFiles.push(
        writeFile(externalRoot, `${directoryName}/record.md`, "EXTERNAL ARTIFACT SENTINEL\n"),
        writeFile(externalRoot, `${directoryName}/README.md`, "EXTERNAL README SENTINEL\n")
      );
      makeDirectoryLink(
        externalDirectory,
        path.join(projectRoot, "runs", "local-run", directoryName)
      );
    }
    const before = new Map(
      externalFiles.map((filePath) => [filePath, fs.readFileSync(filePath)])
    );

    const prunedResult = discoverDocuments(projectRoot);
    assert.deepEqual(relativeDocumentPaths(prunedResult), ["runs/local-run/record.md"]);
    assert.deepEqual(prunedResult.misplacedPaths, []);
    assert.deepEqual(prunedResult.historicalPaths, []);
    assert.deepEqual(prunedResult.forbiddenRunDocuments, []);
    assert.deepEqual(prunedResult.unsafePaths, []);

    makeDirectoryLink(externalRoot, path.join(linkedRootProject, "runs"));
    const linkedRootResult = discoverDocuments(linkedRootProject);
    assert.deepEqual(relativeDocumentPaths(linkedRootResult), []);
    assert.deepEqual(linkedRootResult.unsafePaths.map((entry) => entry.relativePath), ["runs"]);

    makeDirectoryLink(externalRoot, path.join(linkedRunProject, "runs", "external-run"));
    const linkedRunResult = discoverDocuments(linkedRunProject);
    assert.deepEqual(relativeDocumentPaths(linkedRunResult), []);
    assert.deepEqual(linkedRunResult.unsafePaths.map((entry) => entry.relativePath), [
      "runs/external-run",
    ]);
    for (const [filePath, contents] of before) {
      assert.deepEqual(fs.readFileSync(filePath), contents);
    }
  } finally {
    removeDirectories(projectRoot, linkedRootProject, linkedRunProject, externalRoot);
  }
});

test("reports wrong node types without creating or replacing paths", () => {
  const projectRoot = makeTempDirectory("hello-scholar-node-types-");
  try {
    makeDirectory(projectRoot, "hello-scholar/architecture.md");
    writeFile(projectRoot, "hello-scholar/specs", "not a directory\n");
    writeFile(projectRoot, "runs", "not a directory\n");

    const result = discoverDocuments(projectRoot);

    assert.deepEqual(relativeDocumentPaths(result), []);
    assert.deepEqual(
      result.unsafePaths.map((entry) => entry.relativePath),
      ["hello-scholar/architecture.md", "hello-scholar/specs", "runs"]
    );
    assert.equal(fs.lstatSync(path.join(projectRoot, "hello-scholar", "architecture.md")).isDirectory(), true);
    assert.equal(fs.readFileSync(path.join(projectRoot, "hello-scholar", "specs"), "utf8"), "not a directory\n");
    assert.equal(fs.readFileSync(path.join(projectRoot, "runs"), "utf8"), "not a directory\n");
  } finally {
    removeDirectories(projectRoot);
  }
});

test("an empty project remains empty", () => {
  const projectRoot = makeTempDirectory("hello-scholar-empty-");
  try {
    assert.deepEqual(fs.readdirSync(projectRoot), []);

    assert.deepEqual(discoverDocuments(projectRoot), {
      documents: [],
      legacyPaths: [],
      historicalPaths: [],
      misplacedPaths: [],
      forbiddenRunDocuments: [],
      unsafePaths: [],
      indexPaths: [],
    });
    assert.deepEqual(fs.readdirSync(projectRoot), []);
  } finally {
    removeDirectories(projectRoot);
  }
});

test("discovers malformed Plan and Tasks files as unread historical material", () => {
  const projectRoot = makeTempDirectory("hello-scholar-history-");
  try {
    const planPath = writeFile(
      projectRoot,
      "hello-scholar/specs/topic/SPEC-001-example/plan.md",
      "malformed historical plan\n"
    );
    const tasksPath = writeFile(
      projectRoot,
      "hello-scholar/specs/topic/SPEC-001-example/tasks.md",
      "---\ninvalid: [\n"
    );
    const before = new Map([
      [planPath, fs.readFileSync(planPath)],
      [tasksPath, fs.readFileSync(tasksPath)],
    ]);

    const result = discoverDocuments(projectRoot);

    assert.deepEqual(result.documents, []);
    assert.deepEqual(result.historicalPaths, [
      "hello-scholar/specs/topic/SPEC-001-example/plan.md",
      "hello-scholar/specs/topic/SPEC-001-example/tasks.md",
    ]);
    assert.deepEqual(result.misplacedPaths, []);
    for (const [filePath, bytes] of before) {
      assert.deepEqual(fs.readFileSync(filePath), bytes);
    }
  } finally {
    removeDirectories(projectRoot);
  }
});

test("reports front matter errors with a relative source path", () => {
  const projectRoot = makeTempDirectory("hello-scholar-invalid-frontmatter-");
  try {
    writeFile(projectRoot, "hello-scholar/architecture.md", "not front matter\n");

    assert.throws(
      () => discoverDocuments(projectRoot),
      (error) => {
        assert.match(error.message, /^hello-scholar\/architecture\.md:1:/);
        assert.equal(error.message.includes(projectRoot), false);
        return true;
      }
    );
  } finally {
    removeDirectories(projectRoot);
  }
});
