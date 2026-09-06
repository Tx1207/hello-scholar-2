const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const {
  GENERATED_MARKER,
  prepareIndexBatch,
  renderIndexes,
  syncIndexBatch,
} = require("../src/index-generator");
const { applyAtomicFileBatch } = require("../src/fs-ops");

function makeTempProject() {
  // Purpose: create an isolated Index fixture project; Input: none; Output: temporary project path; Side effects: creates a directory under the system temp root.
  return fs.mkdtempSync(path.join(os.tmpdir(), "hello-scholar-index-"));
}

function writeFile(projectRoot, relativePath, content) {
  // Purpose: populate one Index fixture file; Input: project root, POSIX-style relative path, and UTF-8 content; Output: absolute target path; Side effects: creates parents and writes the file.
  const target = path.join(projectRoot, ...relativePath.split("/"));
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content, "utf8");
  return target;
}

function readFile(projectRoot, relativePath) {
  // Purpose: read one Index fixture file; Input: project root and POSIX-style relative path; Output: UTF-8 file content.
  return fs.readFileSync(path.join(projectRoot, ...relativePath.split("/")), "utf8");
}

function generated(content = "old\n") {
  // Purpose: mark fixture content as hello-scholar generated; Input: optional Index body; Output: marker-prefixed Index text.
  return `${GENERATED_MARKER}\n${content}`;
}

function sampleValidation() {
  // Purpose: provide a representative validated document set; Input: none; Output: validation result spanning topics and Runs.
  return {
    errors: [],
    notices: [],
    specs: [
      {
        id: "SPEC-010",
        title: "Later Alpha",
        topic: "alpha",
        type: "prototype",
        status: "accepted",
        revision: 2,
        summary: "Pipe | line\nnext",
        supersedes: ["SPEC-002"],
        supersededBy: null,
        relativePath: "hello-scholar/specs/alpha/SPEC-010-later/spec.md",
      },
      {
        id: "SPEC-002",
        title: "First Alpha",
        topic: "alpha",
        type: "research",
        status: "completed",
        revision: 10,
        summary: "First summary",
        supersedes: [],
        supersededBy: "SPEC-010",
        relativePath: "hello-scholar/specs/alpha/SPEC-002-first/spec.md",
      },
      {
        id: "SPEC-001",
        title: "Zeta",
        topic: "zeta",
        type: "capability",
        status: "draft",
        revision: 1,
        summary: "Zeta summary",
        supersedes: [],
        supersededBy: null,
        relativePath: "hello-scholar/specs/zeta/SPEC-001-zeta/spec.md",
      },
    ],
    records: [
      {
        runId: "20260801-0900-alpha",
        status: "completed",
        spec: "SPEC-010",
        specRevision: 2,
        started: "2026-08-01T09:00:00Z",
        decision: "adopt",
        summary: "Alpha | result",
        relativePath: "runs/20260801-0900-alpha/record.md",
      },
      {
        runId: "20260801-1000-zeta",
        status: "failed",
        spec: null,
        specRevision: null,
        started: "2026-08-01T09:00:00Z",
        decision: "reject",
        summary: "Zeta result",
        relativePath: "runs/20260801-1000-zeta/record.md",
      },
      {
        runId: "planned",
        status: "planned",
        spec: null,
        specRevision: null,
        started: null,
        decision: "pending",
        summary: "Planned",
        relativePath: "runs/planned/record.md",
      },
    ],
    architecture: null,
  };
}

function fileMap(files) {
  // Purpose: index rendered files by repository path; Input: rendered file objects; Output: relative-path to content map.
  return new Map(files.map((file) => [file.relativePath, file.content]));
}

test("renders global, Topic, and Run indexes with exact stable bytes", () => {
  const first = renderIndexes(sampleValidation());
  const second = renderIndexes(sampleValidation());
  assert.deepEqual(first, second);
  const files = fileMap(first);

  assert.deepEqual([...files.keys()], [
    "hello-scholar/specs/INDEX.md",
    "hello-scholar/specs/alpha/INDEX.md",
    "hello-scholar/specs/zeta/INDEX.md",
    "runs/INDEX.md",
  ]);
  assert.equal(files.get("hello-scholar/specs/INDEX.md"), [
    GENERATED_MARKER,
    "# Specs",
    "",
    "| Topic | Spec | Type | Status | Revision | Summary |",
    "| --- | --- | --- | --- | --- | --- |",
    "| alpha | [SPEC-002](alpha/SPEC-002-first/spec.md) | research | completed | 10 | First summary |",
    "| alpha | [SPEC-010](alpha/SPEC-010-later/spec.md) | prototype | accepted | 2 | Pipe \\| line<br>next |",
    "| zeta | [SPEC-001](zeta/SPEC-001-zeta/spec.md) | capability | draft | 1 | Zeta summary |",
    "",
  ].join("\n"));
  assert.equal(files.get("hello-scholar/specs/alpha/INDEX.md"), [
    GENERATED_MARKER,
    "# Topic: alpha",
    "",
    "| Spec | Type | Status | Revision | Summary | Relations |",
    "| --- | --- | --- | --- | --- | --- |",
    "| [SPEC-002](SPEC-002-first/spec.md) | research | completed | 10 | First summary | superseded by [SPEC-010](SPEC-010-later/spec.md) |",
    "| [SPEC-010](SPEC-010-later/spec.md) | prototype | accepted | 2 | Pipe \\| line<br>next | supersedes [SPEC-002](SPEC-002-first/spec.md) |",
    "",
  ].join("\n"));
  assert.equal(files.get("runs/INDEX.md"), [
    GENERATED_MARKER,
    "# Runs",
    "",
    "| Run | Status | Spec | Spec Revision | Decision | Summary | Record |",
    "| --- | --- | --- | --- | --- | --- | --- |",
    "| 20260801-1000-zeta | failed | - | - | reject | Zeta result | [record.md](20260801-1000-zeta/record.md) |",
    "| 20260801-0900-alpha | completed | [SPEC-010](../hello-scholar/specs/alpha/SPEC-010-later/spec.md) | 2 | adopt | Alpha \\| result | [record.md](20260801-0900-alpha/record.md) |",
    "| planned | planned | - | - | pending | Planned | [record.md](planned/record.md) |",
    "",
  ].join("\n"));
  for (const content of files.values()) {
    assert.equal(content.includes("\r"), false);
    assert.equal(content.endsWith("\n"), true);
  }
});

test("percent-encodes filesystem characters in Markdown link destinations", () => {
  const validation = sampleValidation();
  validation.specs[0].relativePath = "hello-scholar/specs/alpha/SPEC-002 hash#(draft)/spec.md";
  validation.records[0].relativePath = "runs/20260801-0900 alpha#(draft)/record.md";

  const files = fileMap(renderIndexes(validation));

  assert.match(
    files.get("hello-scholar/specs/INDEX.md"),
    /alpha\/SPEC-002%20hash%23%28draft%29\/spec\.md/
  );
  assert.match(
    files.get("runs/INDEX.md"),
    /20260801-0900%20alpha%23%28draft%29\/record\.md/
  );
});

test("prepares only Missing and Stale writes and preserves Current indexes", () => {
  const projectRoot = makeTempProject();
  try {
    const rendered = fileMap(renderIndexes(sampleValidation()));
    writeFile(projectRoot, "hello-scholar/specs/INDEX.md", generated("stale\n"));
    writeFile(
      projectRoot,
      "hello-scholar/specs/alpha/INDEX.md",
      rendered.get("hello-scholar/specs/alpha/INDEX.md")
    );
    fs.mkdirSync(path.join(projectRoot, "hello-scholar", "specs", "zeta"), { recursive: true });
    fs.mkdirSync(path.join(projectRoot, "runs"), { recursive: true });

    const batch = prepareIndexBatch({
      projectRoot,
      validationResult: sampleValidation(),
      indexPaths: [
        "hello-scholar/specs/INDEX.md",
        "hello-scholar/specs/alpha/INDEX.md",
      ],
    });

    assert.deepEqual(batch.errors, []);
    assert.deepEqual(batch.indexStates, [
      { path: "hello-scholar/specs/INDEX.md", state: "Stale" },
      { path: "hello-scholar/specs/alpha/INDEX.md", state: "Current" },
      { path: "hello-scholar/specs/zeta/INDEX.md", state: "Missing" },
      { path: "runs/INDEX.md", state: "Missing" },
    ]);
    assert.deepEqual(batch.writes.map((file) => file.relativePath), [
      "hello-scholar/specs/INDEX.md",
      "hello-scholar/specs/zeta/INDEX.md",
      "runs/INDEX.md",
    ]);
    assert.deepEqual(batch.deletePaths, []);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("validation errors suppress every planned write and deletion", () => {
  const projectRoot = makeTempProject();
  try {
    const globalIndex = "hello-scholar/specs/INDEX.md";
    const original = generated("old\n");
    writeFile(projectRoot, globalIndex, original);
    const validationResult = sampleValidation();
    validationResult.errors = [{
      code: "invalid-document",
      path: "hello-scholar/specs/alpha/SPEC-002-first/spec.md",
      message: "injected validation error",
    }];

    const batch = prepareIndexBatch({
      projectRoot,
      validationResult,
      indexPaths: [globalIndex],
    });

    assert.deepEqual(batch.errors, validationResult.errors);
    assert.deepEqual(batch.renderedFiles, []);
    assert.deepEqual(batch.writes, []);
    assert.deepEqual(batch.deletePaths, []);
    assert.equal(readFile(projectRoot, globalIndex), original);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("an empty source set creates no Index directories", () => {
  const projectRoot = makeTempProject();
  try {
    const batch = prepareIndexBatch({
      projectRoot,
      validationResult: { errors: [], notices: [], specs: [], records: [], architecture: null },
      indexPaths: [],
    });

    assert.deepEqual(batch.errors, []);
    assert.deepEqual(batch.renderedFiles, []);
    assert.deepEqual(batch.writes, []);
    assert.deepEqual(batch.deletePaths, []);
    assert.deepEqual(fs.readdirSync(projectRoot), []);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("refuses handwritten, damaged-marker, linked, and linked-parent indexes", () => {
  const cases = ["handwritten", "damaged", "target-link", "parent-link"];
  for (const kind of cases) {
    const projectRoot = makeTempProject();
    const externalRoot = fs.mkdtempSync(path.join(os.tmpdir(), "hello-scholar-index-external-"));
    try {
      const targetRelative = "hello-scholar/specs/INDEX.md";
      const target = path.join(projectRoot, ...targetRelative.split("/"));
      const sentinel = writeFile(externalRoot, "sentinel.md", "EXTERNAL SENTINEL\n");
      if (kind === "handwritten") {
        writeFile(projectRoot, targetRelative, "# User Index\n");
      } else if (kind === "damaged") {
        writeFile(projectRoot, targetRelative, ` ${GENERATED_MARKER}\nold\n`);
      } else if (kind === "target-link") {
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.symlinkSync(sentinel, target, "file");
      } else {
        fs.mkdirSync(path.join(projectRoot, "hello-scholar"), { recursive: true });
        fs.mkdirSync(path.join(externalRoot, "specs"), { recursive: true });
        fs.symlinkSync(
          path.join(externalRoot, "specs"),
          path.join(projectRoot, "hello-scholar", "specs"),
          process.platform === "win32" ? "junction" : "dir"
        );
      }
      fs.mkdirSync(path.join(projectRoot, "runs"), { recursive: true });
      const before = fs.readFileSync(sentinel);

      const batch = prepareIndexBatch({
        projectRoot,
        validationResult: { ...sampleValidation(), specs: sampleValidation().specs.slice(0, 2), records: [] },
        indexPaths: kind === "target-link" || kind === "parent-link" ? [] : [targetRelative],
      });

      assert.ok(batch.errors.length > 0, kind);
      assert.deepEqual(batch.writes, []);
      assert.deepEqual(batch.deletePaths, []);
      assert.deepEqual(fs.readFileSync(sentinel), before);
      if (kind === "handwritten" || kind === "damaged") {
        assert.equal(readFile(projectRoot, targetRelative), kind === "handwritten"
          ? "# User Index\n"
          : ` ${GENERATED_MARKER}\nold\n`);
      }
    } finally {
      fs.rmSync(projectRoot, { recursive: true, force: true });
      fs.rmSync(externalRoot, { recursive: true, force: true });
    }
  }
});

test("deletes only proven generated orphan indexes", () => {
  for (const owned of [true, false]) {
    const projectRoot = makeTempProject();
    try {
      const orphan = "hello-scholar/specs/retired/INDEX.md";
      const original = owned ? generated("retired\n") : "# User Retired Index\n";
      writeFile(projectRoot, orphan, original);

      const batch = prepareIndexBatch({
        projectRoot,
        validationResult: { errors: [], notices: [], specs: [], records: [], architecture: null },
        indexPaths: [orphan],
      });

      if (owned) {
        assert.deepEqual(batch.errors, []);
        assert.deepEqual(batch.deletePaths, [orphan]);
        assert.deepEqual(batch.indexStates, [{ path: orphan, state: "Stale" }]);
      } else {
        assert.ok(batch.errors.some((error) => error.code === "index-not-generated"));
        assert.deepEqual(batch.deletePaths, []);
        assert.equal(readFile(projectRoot, orphan), original);
      }
    } finally {
      fs.rmSync(projectRoot, { recursive: true, force: true });
    }
  }
});

test("never treats an arbitrary generated-looking path as an orphan Index", () => {
  const projectRoot = makeTempProject();
  try {
    const userPath = "notes/INDEX.md";
    writeFile(projectRoot, userPath, generated("user-owned location\n"));

    const batch = prepareIndexBatch({
      projectRoot,
      validationResult: { errors: [], notices: [], specs: [], records: [], architecture: null },
      indexPaths: [userPath],
    });

    assert.ok(batch.errors.some((error) => error.code === "unrecognized-index-path"));
    assert.deepEqual(batch.deletePaths, []);
    assert.equal(readFile(projectRoot, userPath), generated("user-owned location\n"));
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("sync writes and deletes one prepared batch", () => {
  const projectRoot = makeTempProject();
  try {
    const orphan = "hello-scholar/specs/retired/INDEX.md";
    writeFile(projectRoot, orphan, generated("retired\n"));
    fs.mkdirSync(path.join(projectRoot, "hello-scholar", "specs", "alpha"), { recursive: true });
    fs.mkdirSync(path.join(projectRoot, "hello-scholar", "specs", "zeta"), { recursive: true });
    fs.mkdirSync(path.join(projectRoot, "runs"), { recursive: true });
    const batch = prepareIndexBatch({
      projectRoot,
      validationResult: sampleValidation(),
      indexPaths: [orphan],
    });

    const summary = syncIndexBatch({ projectRoot, batch });

    assert.deepEqual(summary.writtenPaths, [
      "hello-scholar/specs/INDEX.md",
      "hello-scholar/specs/alpha/INDEX.md",
      "hello-scholar/specs/zeta/INDEX.md",
      "runs/INDEX.md",
    ]);
    assert.deepEqual(summary.deletedPaths, [orphan]);
    assert.equal(fs.existsSync(path.join(projectRoot, ...orphan.split("/"))), false);
    assert.equal(readFile(projectRoot, "runs/INDEX.md"), fileMap(renderIndexes(sampleValidation())).get("runs/INDEX.md"));
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("atomic batch rolls back replacements, creations, and deletions on a mid-batch error", () => {
  const projectRoot = makeTempProject();
  try {
    writeFile(projectRoot, "indexes/a.md", "old a\n");
    writeFile(projectRoot, "indexes/delete.md", "old delete\n");
    const failingFs = Object.create(fs);
    let renameCount = 0;
    failingFs.renameSync = (...args) => {
      renameCount += 1;
      if (renameCount === 2) {
        const error = new Error("injected replace failure");
        error.code = "EIO";
        throw error;
      }
      return fs.renameSync(...args);
    };

    assert.throws(() => applyAtomicFileBatch({
      projectRoot,
      writes: [
        { relativePath: "indexes/a.md", content: "new a\n" },
        { relativePath: "indexes/new.md", content: "new file\n" },
      ],
      deletes: ["indexes/delete.md"],
      fileSystem: failingFs,
    }), /indexes\/new\.md.*injected replace failure/);

    assert.equal(readFile(projectRoot, "indexes/a.md"), "old a\n");
    assert.equal(readFile(projectRoot, "indexes/delete.md"), "old delete\n");
    assert.equal(fs.existsSync(path.join(projectRoot, "indexes", "new.md")), false);
    assert.deepEqual(
      fs.readdirSync(path.join(projectRoot, "indexes")).sort(),
      ["a.md", "delete.md"]
    );
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("atomic batch restores prior writes and deletions when a later deletion fails", () => {
  const projectRoot = makeTempProject();
  try {
    writeFile(projectRoot, "indexes/a.md", "old a\n");
    writeFile(projectRoot, "indexes/delete-a.md", "old delete a\n");
    writeFile(projectRoot, "indexes/delete-b.md", "old delete b\n");
    const failingFs = Object.create(fs);
    let injected = false;
    failingFs.unlinkSync = (targetPath) => {
      if (!injected && targetPath.endsWith(`${path.sep}delete-b.md`)) {
        injected = true;
        const error = new Error("injected delete failure");
        error.code = "EIO";
        throw error;
      }
      return fs.unlinkSync(targetPath);
    };

    assert.throws(() => applyAtomicFileBatch({
      projectRoot,
      writes: [{ relativePath: "indexes/a.md", content: "new a\n" }],
      deletes: ["indexes/delete-a.md", "indexes/delete-b.md"],
      fileSystem: failingFs,
    }), /indexes\/delete-b\.md.*injected delete failure/);

    assert.equal(readFile(projectRoot, "indexes/a.md"), "old a\n");
    assert.equal(readFile(projectRoot, "indexes/delete-a.md"), "old delete a\n");
    assert.equal(readFile(projectRoot, "indexes/delete-b.md"), "old delete b\n");
    assert.deepEqual(
      fs.readdirSync(path.join(projectRoot, "indexes")).sort(),
      ["a.md", "delete-a.md", "delete-b.md"]
    );
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("atomic batch leaves old files intact after temporary-write failure", () => {
  const projectRoot = makeTempProject();
  try {
    writeFile(projectRoot, "indexes/a.md", "old a\n");
    const failingFs = Object.create(fs);
    failingFs.writeFileSync = (target, ...args) => {
      if (typeof target === "number") {
        const error = new Error("injected temp write failure");
        error.code = "ENOSPC";
        throw error;
      }
      return fs.writeFileSync(target, ...args);
    };

    assert.throws(() => applyAtomicFileBatch({
      projectRoot,
      writes: [{ relativePath: "indexes/a.md", content: "new a\n" }],
      deletes: [],
      fileSystem: failingFs,
    }), /indexes\/a\.md.*injected temp write failure/);

    assert.equal(readFile(projectRoot, "indexes/a.md"), "old a\n");
    assert.deepEqual(fs.readdirSync(path.join(projectRoot, "indexes")), ["a.md"]);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("atomic batch rolls back when committed-backup cleanup fails", () => {
  const projectRoot = makeTempProject();
  try {
    writeFile(projectRoot, "indexes/a.md", "old a\n");
    writeFile(projectRoot, "indexes/b.md", "old b\n");
    const failingFs = Object.create(fs);
    let backupCleanupCount = 0;
    failingFs.unlinkSync = (targetPath) => {
      if (targetPath.endsWith(".bak")) {
        backupCleanupCount += 1;
      }
      if (backupCleanupCount === 2) {
        backupCleanupCount += 1;
        const error = new Error("injected backup cleanup failure");
        error.code = "EIO";
        throw error;
      }
      return fs.unlinkSync(targetPath);
    };

    assert.throws(() => applyAtomicFileBatch({
      projectRoot,
      writes: [
        { relativePath: "indexes/a.md", content: "new a\n" },
        { relativePath: "indexes/b.md", content: "new b\n" },
      ],
      deletes: [],
      fileSystem: failingFs,
    }), /injected backup cleanup failure/);

    assert.equal(readFile(projectRoot, "indexes/a.md"), "old a\n");
    assert.equal(readFile(projectRoot, "indexes/b.md"), "old b\n");
    assert.deepEqual(fs.readdirSync(path.join(projectRoot, "indexes")).sort(), ["a.md", "b.md"]);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("exclusive temporary-name collisions are retried without touching the collision", () => {
  const projectRoot = makeTempProject();
  try {
    fs.mkdirSync(path.join(projectRoot, "indexes"), { recursive: true });
    const collision = path.join(projectRoot, "indexes", ".hello-scholar-index-collision.tmp");
    fs.writeFileSync(collision, "user collision\n", "utf8");
    const tokens = ["collision", "success", "backup"];

    applyAtomicFileBatch({
      projectRoot,
      writes: [{ relativePath: "indexes/a.md", content: "new a\n" }],
      deletes: [],
      makeToken: () => tokens.shift() || "fallback",
    });

    assert.equal(readFile(projectRoot, "indexes/a.md"), "new a\n");
    assert.equal(fs.readFileSync(collision, "utf8"), "user collision\n");
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});
