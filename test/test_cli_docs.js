const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { Readable, Writable } = require("node:stream");
const test = require("node:test");

const { main, parseArgs, usageText } = require("../src/cli");
const { checkDocs, syncDocs } = require("../src/docs");
const { GENERATED_MARKER } = require("../src/index-generator");

const REPO_ROOT = path.resolve(__dirname, "..");

function makeTempProject() {
  // Purpose: create an isolated docs CLI project; Input: none; Output: temporary project path; Side effects: creates a directory under the system temp root.
  return fs.mkdtempSync(path.join(os.tmpdir(), "hello-scholar-docs-"));
}

function writeFile(projectRoot, relativePath, content) {
  // Purpose: populate one test project file; Input: project root, POSIX-style relative path, and UTF-8 content; Output: absolute target path; Side effects: creates parent directories and writes the file.
  const target = path.join(projectRoot, ...relativePath.split("/"));
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content, "utf8");
  return target;
}

function readFile(projectRoot, relativePath) {
  // Purpose: read one test project file; Input: project root and POSIX-style relative path; Output: UTF-8 file content.
  return fs.readFileSync(path.join(projectRoot, ...relativePath.split("/")), "utf8");
}

function specText(overrides = {}) {
  // Purpose: build a valid Spec fixture document; Input: optional revision and date overrides; Output: Markdown text with restricted Front Matter.
  const values = {
    revision: 1,
    updated: "2026-08-01",
    ...overrides,
  };
  return [
    "---",
    "schema: 1",
    "kind: spec",
    "id: SPEC-001",
    "title: Paged Cache",
    "topic: kv-cache",
    "type: research",
    "status: accepted",
    `revision: ${values.revision}`,
    "summary: Remove fragmentation failures",
    "created: 2026-07-20",
    `updated: ${values.updated}`,
    "supersedes: []",
    "superseded_by: null",
    "---",
    "# Paged Cache",
    "",
  ].join("\n");
}

function architectureText() {
  // Purpose: build a valid Architecture fixture document; Input: none; Output: Markdown text with restricted Front Matter.
  return [
    "---",
    "schema: 1",
    "kind: architecture",
    "status: current",
    "applies_to: main",
    "updated: 2026-08-01",
    "---",
    "# Current Architecture",
    "",
  ].join("\n");
}

function createSpecProject(projectRoot) {
  // Purpose: seed the minimum current Spec project; Input: project root; Output: relative Bundle path; Side effects: writes Spec and Architecture documents.
  const bundle = "hello-scholar/specs/kv-cache/SPEC-001-paged-cache";
  writeFile(projectRoot, `${bundle}/spec.md`, specText());
  writeFile(projectRoot, "hello-scholar/architecture.md", architectureText());
  return bundle;
}

function makeCliIo(inputText = "") {
  // Purpose: capture CLI input and output without a process; Input: optional stdin text; Output: stdin, stdout, and captured-output accessor.
  let output = "";
  const stdin = Readable.from([inputText]);
  const stdout = new Writable({
    write(chunk, encoding, callback) {
      // Purpose: capture one stdout write; Input: stream chunk, encoding, and completion callback; Output: none; Side effects: appends captured text and completes the write.
      output += chunk.toString();
      callback();
    },
  });
  return { stdin, stdout, getOutput: () => output };
}

test("parseArgs and usage expose only docs check and docs sync", () => {
  assert.deepEqual(parseArgs(["docs", "check"]), { action: "docs", operation: "check" });
  assert.deepEqual(parseArgs(["docs", "sync"]), { action: "docs", operation: "sync" });
  for (const args of [
    ["docs"],
    ["docs", "repair"],
    ["docs", "check", "extra"],
    ["docs", "sync", "--mode", "copy"],
  ]) {
    assert.throws(() => parseArgs(args), /Usage:/);
  }
  const usage = usageText();
  assert.match(usage, /hello-scholar docs check/);
  assert.match(usage, /hello-scholar docs sync/);
  assert.match(usage, /hello-scholar install codex\|claude/);
});

test("empty project check and sync are successful and create nothing", () => {
  const projectRoot = makeTempProject();
  try {
    const checked = checkDocs({ projectRoot });
    assert.deepEqual(checked.errors, []);
    assert.deepEqual(checked.indexStates, []);
    assert.deepEqual(checked.counts, { specs: 0, records: 0, indexes: 0 });
    assert.ok(checked.notices.some((notice) => notice.code === "architecture-missing"));

    const synced = syncDocs({ projectRoot });
    assert.deepEqual(synced.errors, []);
    assert.deepEqual(synced.writtenPaths, []);
    assert.deepEqual(synced.deletedPaths, []);
    assert.deepEqual(fs.readdirSync(projectRoot), []);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("check reports Missing, Current, and Stale generated Index states without writing", () => {
  const projectRoot = makeTempProject();
  try {
    const bundle = createSpecProject(projectRoot);
    const before = checkDocs({ projectRoot });
    assert.deepEqual(before.errors, []);
    assert.deepEqual(before.indexStates, [
      { path: "hello-scholar/specs/INDEX.md", state: "Missing" },
      { path: "hello-scholar/specs/kv-cache/INDEX.md", state: "Missing" },
    ]);
    assert.equal(fs.existsSync(path.join(projectRoot, "hello-scholar", "specs", "INDEX.md")), false);

    const synced = syncDocs({ projectRoot });
    assert.deepEqual(synced.writtenPaths, [
      "hello-scholar/specs/INDEX.md",
      "hello-scholar/specs/kv-cache/INDEX.md",
    ]);
    assert.deepEqual(checkDocs({ projectRoot }).indexStates, [
      { path: "hello-scholar/specs/INDEX.md", state: "Current" },
      { path: "hello-scholar/specs/kv-cache/INDEX.md", state: "Current" },
    ]);

    writeFile(projectRoot, `${bundle}/plan.md`, "malformed historical Plan\n");
    writeFile(projectRoot, `${bundle}/tasks.md`, "---\ninvalid: [\n");
    const withHistory = checkDocs({ projectRoot });
    assert.deepEqual(withHistory.errors, []);
    assert.ok(withHistory.notices.every((notice) => notice.code === "historical-document"));
    assert.ok(withHistory.indexStates.every((entry) => entry.state === "Current"));
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("historical Plan and Tasks remain notices and do not block or change sync", () => {
  const projectRoot = makeTempProject();
  try {
    const bundle = createSpecProject(projectRoot);
    const planPath = writeFile(projectRoot, `${bundle}/plan.md`, "historical Plan without Front Matter\n");
    const tasksPath = writeFile(projectRoot, `${bundle}/tasks.md`, "historical Tasks without Front Matter\n");
    syncDocs({ projectRoot });
    writeFile(projectRoot, `${bundle}/spec.md`, specText({ revision: 2, updated: "2026-08-02" }));
    writeFile(projectRoot, "hello-scholar/memory/specs/old.md", "# Legacy\n");
    const historicalBefore = new Map([
      [planPath, fs.readFileSync(planPath)],
      [tasksPath, fs.readFileSync(tasksPath)],
    ]);

    const checked = checkDocs({ projectRoot });
    assert.deepEqual(checked.errors, []);
    assert.equal(checked.notices.filter((notice) => notice.code === "historical-document").length, 2);
    assert.ok(checked.notices.some((notice) => notice.code === "legacy-path"));
    assert.ok(checked.indexStates.every((entry) => entry.state === "Stale"));

    const synced = syncDocs({ projectRoot });
    assert.deepEqual(synced.errors, []);
    assert.equal(synced.writtenPaths.length, 2);
    assert.equal(readFile(projectRoot, "hello-scholar/memory/specs/old.md"), "# Legacy\n");
    for (const [filePath, bytes] of historicalBefore) {
      assert.deepEqual(fs.readFileSync(filePath), bytes);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("front matter errors block sync and preserve every existing Index byte", () => {
  const projectRoot = makeTempProject();
  try {
    writeFile(projectRoot, "hello-scholar/architecture.md", "not front matter\n");
    const indexPath = "hello-scholar/specs/INDEX.md";
    const original = `${GENERATED_MARKER}\nold\n`;
    writeFile(projectRoot, indexPath, original);

    const checked = checkDocs({ projectRoot });
    assert.ok(checked.errors.some((error) => error.code === "frontmatter-error"));
    assert.equal(checked.errors[0].message.includes(projectRoot), false);
    const synced = syncDocs({ projectRoot });
    assert.ok(synced.errors.length > 0);
    assert.deepEqual(synced.writtenPaths, []);
    assert.deepEqual(synced.deletedPaths, []);
    assert.equal(readFile(projectRoot, indexPath), original);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("handwritten and linked Index targets are errors, never Stale overwrite candidates", () => {
  for (const linked of [false, true]) {
    const projectRoot = makeTempProject();
    const externalRoot = makeTempProject();
    try {
      createSpecProject(projectRoot);
      const target = path.join(projectRoot, "hello-scholar", "specs", "INDEX.md");
      const external = writeFile(externalRoot, "INDEX.md", "EXTERNAL\n");
      if (linked) {
        fs.symlinkSync(external, target, "file");
      } else {
        fs.writeFileSync(target, "# User Index\n", "utf8");
      }

      const checked = checkDocs({ projectRoot });
      assert.ok(checked.errors.length > 0);
      assert.equal(
        checked.indexStates.some((entry) =>
          entry.path === "hello-scholar/specs/INDEX.md" && entry.state === "Stale"
        ),
        false
      );
      const synced = syncDocs({ projectRoot });
      assert.deepEqual(synced.writtenPaths, []);
      assert.equal(fs.readFileSync(external, "utf8"), "EXTERNAL\n");
      if (!linked) {
        assert.equal(fs.readFileSync(target, "utf8"), "# User Index\n");
      }
    } finally {
      fs.rmSync(projectRoot, { recursive: true, force: true });
      fs.rmSync(externalRoot, { recursive: true, force: true });
    }
  }
});

test("sync removes proven generated orphan indexes after all sources disappear", () => {
  const projectRoot = makeTempProject();
  try {
    for (const relativePath of [
      "hello-scholar/specs/INDEX.md",
      "hello-scholar/specs/retired/INDEX.md",
      "runs/INDEX.md",
    ]) {
      writeFile(projectRoot, relativePath, `${GENERATED_MARKER}\nold\n`);
    }

    const synced = syncDocs({ projectRoot });

    assert.deepEqual(synced.errors, []);
    assert.deepEqual(synced.writtenPaths, []);
    assert.deepEqual(synced.deletedPaths, [
      "hello-scholar/specs/INDEX.md",
      "hello-scholar/specs/retired/INDEX.md",
      "runs/INDEX.md",
    ]);
    assert.equal(fs.existsSync(path.join(projectRoot, "hello-scholar", "specs", "INDEX.md")), false);
    assert.equal(fs.existsSync(path.join(projectRoot, "runs", "INDEX.md")), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("sync propagates atomic failure after restoring all old Index bytes", () => {
  const projectRoot = makeTempProject();
  try {
    createSpecProject(projectRoot);
    const globalPath = "hello-scholar/specs/INDEX.md";
    const topicPath = "hello-scholar/specs/kv-cache/INDEX.md";
    writeFile(projectRoot, globalPath, `${GENERATED_MARKER}\nold global\n`);
    writeFile(projectRoot, topicPath, `${GENERATED_MARKER}\nold topic\n`);
    const failingFs = Object.create(fs);
    let renameCount = 0;
    failingFs.renameSync = (...args) => {
      renameCount += 1;
      if (renameCount === 2) {
        throw new Error("injected sync replacement failure");
      }
      return fs.renameSync(...args);
    };

    assert.throws(
      () => syncDocs({ projectRoot, fileSystem: failingFs }),
      /injected sync replacement failure/
    );
    assert.equal(readFile(projectRoot, globalPath), `${GENERATED_MARKER}\nold global\n`);
    assert.equal(readFile(projectRoot, topicPath), `${GENERATED_MARKER}\nold topic\n`);
    assert.deepEqual(
      fs.readdirSync(path.join(projectRoot, "hello-scholar", "specs")).sort(),
      ["INDEX.md", "kv-cache"]
    );
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("main prints stable docs summaries without entering reinstall confirmation", async () => {
  const projectRoot = makeTempProject();
  try {
    const checkIo = makeCliIo();
    await main(["docs", "check"], { projectRoot, ...checkIo });
    assert.match(checkIo.getOutput(), /^docs check: specs 0, records 0, indexes 0, errors 0, notices 1\n/);
    assert.match(checkIo.getOutput(), /notice architecture-missing hello-scholar\/architecture\.md:/);

    const syncIo = makeCliIo();
    await main(["docs", "sync"], { projectRoot, ...syncIo });
    assert.match(syncIo.getOutput(), /^docs sync: written 0, deleted 0, errors 0, notices 1\n/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("main prints relative docs errors and rejects for a nonzero real CLI exit", async () => {
  const projectRoot = makeTempProject();
  try {
    writeFile(projectRoot, "hello-scholar/architecture.md", "not front matter\n");
    const io = makeCliIo();

    await assert.rejects(
      main(["docs", "check"], { projectRoot, ...io }),
      /docs check failed with 1 error/
    );

    const output = io.getOutput();
    assert.match(output, /^docs check: specs 0, records 0, indexes 0, errors 1, notices 0\n/);
    assert.match(output, /error frontmatter-error hello-scholar\/architecture\.md:/);
    assert.equal(output.includes(projectRoot), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("real CLI entry checks and syncs from the current project directory", () => {
  const projectRoot = makeTempProject();
  try {
    createSpecProject(projectRoot);
    const cli = path.join(REPO_ROOT, "bin", "hello-scholar.js");
    const checkBefore = spawnSync(process.execPath, [cli, "docs", "check"], {
      cwd: projectRoot,
      encoding: "utf8",
    });
    assert.equal(checkBefore.status, 0, checkBefore.stderr);
    assert.match(checkBefore.stdout, /index Missing hello-scholar\/specs\/INDEX\.md/);

    const sync = spawnSync(process.execPath, [cli, "docs", "sync"], {
      cwd: projectRoot,
      encoding: "utf8",
    });
    assert.equal(sync.status, 0, sync.stderr);
    assert.match(sync.stdout, /written hello-scholar\/specs\/INDEX\.md/);

    const checkAfter = spawnSync(process.execPath, [cli, "docs", "check"], {
      cwd: projectRoot,
      encoding: "utf8",
    });
    assert.equal(checkAfter.status, 0, checkAfter.stderr);
    assert.match(checkAfter.stdout, /index Current hello-scholar\/specs\/INDEX\.md/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});
