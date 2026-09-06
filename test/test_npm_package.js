const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const test = require("node:test");
const { discoverSkills } = require("../src/skill-discovery");

const ROOT = path.resolve(__dirname, "..");
const MARKER = ".hello-scholar-install.json";

// Keep paths and bytes, including empty directories, independent of the source lifetime.
function readTree(root, omitMarker = false, relative = "") {
  const entries = {};
  for (const name of fs.readdirSync(path.join(root, relative)).sort()) {
    if (omitMarker && relative === "" && name === MARKER) continue;
    const key = path.posix.join(relative, name);
    const absolute = path.join(root, key);
    const stat = fs.lstatSync(absolute);
    if (stat.isDirectory()) {
      entries[`${key}/`] = null;
      Object.assign(entries, readTree(root, false, key));
    } else {
      assert.ok(stat.isFile(), `expected regular resource: ${absolute}`);
      entries[key] = fs.readFileSync(absolute);
    }
  }
  return entries;
}

function run(command, args, cwd, env, shell = false) {
  const result = spawnSync(command, args, {
    cwd, env, shell, encoding: "utf8", timeout: 120000, maxBuffer: 16 * 1024 * 1024,
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, `${command} ${args.join(" ")}\n${result.stdout}\n${result.stderr}`);
  return result.stdout;
}

test("local npm tarball installs independently with complete rules and resources", (t) => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "hello-scholar-package-"));
  const snapshot = path.join(temp, "source");
  const consumer = path.join(temp, "consumer");
  const env = { ...process.env, npm_config_cache: path.join(temp, "cache") };
  // npm's Windows entrypoint is a cmd shim. Quote each controlled argument for paths with spaces.
  const npm = (args, cwd) => run("npm", process.platform === "win32"
    ? args.map((arg) => `"${arg}"`) : args, cwd, env, process.platform === "win32");
  try {
    const rules = fs.readFileSync(path.join(ROOT, "AGENTS.md"), "utf8").trimEnd();
    const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8"));
    const skills = discoverSkills(ROOT).map(({ name, sourceDir }) => ({
      name, directory: path.basename(sourceDir), contents: readTree(sourceDir),
    }));
    const runtime = new Map(["bin", "src", "skills"].map((name) => [name, readTree(path.join(ROOT, name))]));

    // Exercise the real manifest against excluded sentinels without copying local runs or data.
    fs.mkdirSync(snapshot);
    for (const entry of ["package.json", "AGENTS.md", "README.md", "LICENSE", "bin", "src", "skills"]) {
      fs.cpSync(path.join(ROOT, entry), path.join(snapshot, entry), { recursive: true });
    }
    for (const ignore of [".gitignore", ".npmignore"]) {
      if (fs.existsSync(path.join(ROOT, ignore))) fs.copyFileSync(path.join(ROOT, ignore), path.join(snapshot, ignore));
    }
    for (const directory of [".git", "node_modules", "test", "docs", "runs", "hello-scholar", ".agents", ".claude", ".worktrees", ".cache", "references"]) {
      fs.mkdirSync(path.join(snapshot, directory), { recursive: true });
      fs.writeFileSync(path.join(snapshot, directory, "package-exclusion-sentinel.txt"), "excluded\n");
    }
    fs.writeFileSync(path.join(snapshot, "package-exclusion-sentinel.tgz"), "excluded\n");
    for (const filename of ["CONTRIBUTING.md", "AGENTS-zh.md"]) {
      fs.writeFileSync(path.join(snapshot, filename), "excluded\n");
    }
    const npmVersion = npm(["--version"], temp).trim();
    const [packed] = JSON.parse(npm(["pack", "--json", "--pack-destination", temp], snapshot));
    const expectedPaths = ["package.json", "README.md", "LICENSE", "AGENTS.md"];
    for (const [directory, tree] of runtime) {
      expectedPaths.push(...Object.keys(tree).filter((key) => !key.endsWith("/")).map((key) => `${directory}/${key}`));
    }
    assert.deepEqual(packed.files.map((entry) => entry.path).sort(), expectedPaths.sort());
    npm(["install", "--prefix", consumer, "--no-save", "--package-lock=false", "--ignore-scripts",
      "--offline", "--no-audit", "--no-fund", path.join(temp, packed.filename)], temp);
    const packageRoot = path.join(consumer, "node_modules", manifest.name);
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(packageRoot, "package.json"), "utf8")), manifest);
    for (const [directory, tree] of runtime) assert.deepEqual(readTree(path.join(packageRoot, directory)), tree);
    for (const file of ["README.md", "LICENSE", "AGENTS.md"]) {
      assert.deepEqual(fs.readFileSync(path.join(packageRoot, file)), fs.readFileSync(path.join(snapshot, file)));
    }
    assert.equal(fs.existsSync(path.join(packageRoot, "CLAUDE.md")), false);
    fs.rmSync(snapshot, { recursive: true, force: true });
    assert.equal(fs.existsSync(snapshot), false);
    const bin = path.join(packageRoot, manifest.bin["hello-scholar"]);
    const shim = path.join(consumer, "node_modules", ".bin", "hello-scholar");
    assert.match(process.platform === "win32"
      ? run(`"${shim}.cmd"`, ["help"], temp, env, true)
      : run(shim, ["help"], temp, env), /Usage:/);
    const cli = (args, cwd) => run(process.execPath, [bin, ...args], cwd, env);
    const targets = [];
    function verifyTarget(target, tool, mode) {
      const filename = tool === "codex" ? "AGENTS.md" : "CLAUDE.md";
      const toolRoot = tool === "codex" ? ".agents" : ".claude";
      assert.equal(fs.existsSync(path.join(target, toolRoot, MARKER)), false);
      const rulePath = path.join(target, filename);
      assert.ok(fs.lstatSync(rulePath).isFile());
      assert.equal(fs.readFileSync(rulePath, "utf8"),
        `<!-- HELLO-SCHOLAR:BEGIN ${tool} -->\n${rules}\n<!-- HELLO-SCHOLAR:END ${tool} -->\n\n`);
      const skillRoot = path.join(target, toolRoot, "skills");
      assert.deepEqual(fs.readdirSync(skillRoot).sort(), skills.map((skill) => skill.name).sort());
      for (const skill of skills) {
        const installed = path.join(skillRoot, skill.name);
        assert.equal(fs.lstatSync(installed).isSymbolicLink(), mode === "link");
        if (mode === "link") {
          assert.equal(fs.realpathSync(installed), fs.realpathSync(path.join(packageRoot, "skills", skill.directory)));
        }
        assert.deepEqual(readTree(installed, mode === "copy"), skill.contents);
      }
    }
    for (const tool of ["codex", "claude"]) {
      for (const mode of ["link", "copy"]) {
        const target = path.join(temp, `${tool}-${mode}`);
        fs.mkdirSync(target);
        const output = cli(["install", tool, "--mode", mode], target);
        assert.match(output, new RegExp(`installed ${skills.length}, updated 0, removed 0, skipped 0`));
        verifyTarget(target, tool, mode);
        cli(["install", tool, "--mode", mode], target);
        verifyTarget(target, tool, mode);
        targets.push({ target, tool, mode });
        t.diagnostic(`${tool}/${mode}: exit 0, ${skills.length} complete Skills, reinstall passed after source deletion`);
      }
    }
    const shared = path.join(temp, "shared");
    fs.mkdirSync(shared);
    for (const mode of ["link", "copy", "link"]) {
      for (const tool of ["codex", "claude"]) cli(["install", tool, "--mode", mode], shared);
      for (const tool of ["codex", "claude"]) verifyTarget(shared, tool, mode);
    }
    for (const tool of ["codex", "claude"]) {
      cli(["uninstall", tool], shared);
      const toolRoot = tool === "codex" ? ".agents" : ".claude";
      assert.deepEqual(fs.readdirSync(path.join(shared, toolRoot, "skills")), []);
      assert.equal(fs.existsSync(path.join(shared, toolRoot, MARKER)), false);
      assert.equal(fs.readFileSync(path.join(shared, tool === "codex" ? "AGENTS.md" : "CLAUDE.md"), "utf8"), "\n\n");
      if (tool === "codex") verifyTarget(shared, "claude", "link");
    }
    fs.renameSync(packageRoot, path.join(temp, "removed-package"));
    for (const { target, tool, mode } of targets) {
      if (mode === "copy") verifyTarget(target, tool, mode);
    }
    t.diagnostic(`Node ${process.version}, npm ${npmVersion}, ${os.platform()} ${os.arch()}; ${packed.files.length} files, ${packed.size} packed bytes, ${packed.unpackedSize} unpacked bytes; copy readable after package removal`);
  } finally {
    fs.rmSync(temp, { recursive: true, force: true });
  }
});
