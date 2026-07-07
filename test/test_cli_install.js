const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { Readable, Writable } = require("node:stream");
const test = require("node:test");

const { main, parseArgs, usageText } = require("../src/cli");
const { formatSummary } = require("../src/cli");
const {
  hasInstructionBlock,
  removeInstructionBlock,
  upsertInstructionBlock,
} = require("../src/instruction-blocks");
const { discoverSkills, parseSkillName } = require("../src/skill-discovery");
const { install, uninstall } = require("../src/install");

const REPO_ROOT = path.resolve(__dirname, "..");

function makeTempProject() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "hello-scholar-cli-"));
}

function listSkillNames() {
  return discoverSkills(REPO_ROOT).map((skill) => skill.name).sort();
}

function countMatches(text, pattern) {
  return (text.match(pattern) || []).length;
}

function makeCliIo(inputText = "") {
  let output = "";
  const stdin = Readable.from([inputText]);
  const stdout = new Writable({
    write(chunk, encoding, callback) {
      output += chunk.toString();
      callback();
    },
  });
  return { stdin, stdout, getOutput: () => output };
}

test("parseArgs accepts supported commands", () => {
  assert.deepEqual(parseArgs(["help"]), { action: "help" });
  assert.deepEqual(parseArgs(["install", "codex"]), {
    action: "install",
    tool: "codex",
    mode: "link",
  });
  assert.deepEqual(parseArgs(["install", "claude"]), {
    action: "install",
    tool: "claude",
    mode: "link",
  });
  assert.deepEqual(parseArgs(["install", "codex", "--mode", "link"]), {
    action: "install",
    tool: "codex",
    mode: "link",
  });
  assert.deepEqual(parseArgs(["install", "codex", "--mode", "copy"]), {
    action: "install",
    tool: "codex",
    mode: "copy",
  });
  assert.deepEqual(parseArgs(["uninstall", "codex"]), {
    action: "uninstall",
    tool: "codex",
  });
});

test("parseArgs rejects invalid commands", () => {
  assert.throws(() => parseArgs(["install", "gemini"]), /Usage:/);
  assert.throws(() => parseArgs(["install", "codex", "--mode", "bad"]), /Usage:/);
  assert.throws(() => parseArgs(["run", "codex"]), /Usage:/);
  assert.throws(() => parseArgs(["install", "codex", "--unknown"]), /Usage:/);
});

test("usageText includes help and supported install commands", () => {
  const text = usageText();
  assert.match(text, /hello-scholar help/);
  assert.match(text, /hello-scholar install codex\|claude \[--mode link\|copy\]/);
  assert.match(text, /hello-scholar uninstall codex\|claude/);
});

test("formatSummary reports installed updated removed and skipped counts explicitly", () => {
  assert.equal(
    formatSummary({ action: "install", tool: "codex", installed: 2, updated: 1, skipped: 3 }),
    "install codex: installed 2, updated 1, skipped 3"
  );
  assert.equal(
    formatSummary({ action: "uninstall", tool: "claude", removed: 4, skipped: 1 }),
    "uninstall claude: removed 4, skipped 1"
  );
});

test("instruction blocks insert, replace, and remove by tool", () => {
  const userText = "# Project Rules\n\nKeep this.";
  const inserted = upsertInstructionBlock(userText, "codex", "hello rules");
  assert.ok(inserted.startsWith("<!-- HELLO-SCHOLAR:BEGIN codex -->"));
  assert.match(inserted, /hello rules/);
  assert.match(inserted, /# Project Rules/);

  const replaced = upsertInstructionBlock(inserted, "codex", "new rules");
  assert.match(replaced, /new rules/);
  assert.doesNotMatch(replaced, /hello rules/);
  assert.match(replaced, /# Project Rules/);

  const mixed = upsertInstructionBlock(replaced, "claude", "claude rules");
  const removedCodex = removeInstructionBlock(mixed, "codex");
  assert.doesNotMatch(removedCodex, /HELLO-SCHOLAR:BEGIN codex/);
  assert.match(removedCodex, /HELLO-SCHOLAR:BEGIN claude/);
  assert.match(removedCodex, /# Project Rules/);
});

test("instruction blocks detect and replace Windows CRLF managed blocks", () => {
  const existingText = [
    "<!-- HELLO-SCHOLAR:BEGIN codex -->",
    "manual edit inside managed block",
    "<!-- HELLO-SCHOLAR:END codex -->",
    "# Project Rules",
    "",
  ].join("\r\n");

  assert.equal(hasInstructionBlock(existingText, "codex"), true);

  const replaced = upsertInstructionBlock(existingText, "codex", "new rules");
  assert.equal(countMatches(replaced, /HELLO-SCHOLAR:BEGIN codex/g), 1);
  assert.match(replaced, /new rules/);
  assert.doesNotMatch(replaced, /manual edit inside managed block/);
  assert.match(replaced, /# Project Rules/);
});

test("discoverSkills returns unique skill names from repository skills", () => {
  const names = listSkillNames();
  assert.ok(names.includes("using-helloscholar"));
  assert.ok(names.includes("writing-plans"));
  assert.ok(names.includes("record-experiment"));
  assert.equal(new Set(names).size, names.length);
});

test("parseSkillName accepts LF and CRLF frontmatter line endings", () => {
  assert.equal(parseSkillName("---\nname: lf-skill\n---\n", "lf/SKILL.md"), "lf-skill");
  assert.equal(parseSkillName("---\r\nname: crlf-skill\r\n---\r\n", "crlf/SKILL.md"), "crlf-skill");
});

test("install codex in link mode creates AGENTS block and linked skills", () => {
  const projectRoot = makeTempProject();
  try {
    const summary = install({ tool: "codex", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT });
    assert.equal(summary.tool, "codex");
    assert.equal(summary.mode, "link");

    const agentsText = fs.readFileSync(path.join(projectRoot, "AGENTS.md"), "utf8");
    assert.match(agentsText, /HELLO-SCHOLAR:BEGIN codex/);
    assert.match(agentsText, /hello-scholar Guide/);

    for (const name of listSkillNames()) {
      const target = path.join(projectRoot, ".agents", "skills", name);
      assert.ok(fs.lstatSync(target).isSymbolicLink(), `${name} should be a symlink`);
      assert.ok(fs.existsSync(path.join(target, "SKILL.md")), `${name} should expose SKILL.md`);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("install claude in copy mode creates CLAUDE block and copied skills", () => {
  const projectRoot = makeTempProject();
  try {
    const summary = install({ tool: "claude", mode: "copy", projectRoot: projectRoot, repoRoot: REPO_ROOT });
    assert.equal(summary.tool, "claude");
    assert.equal(summary.mode, "copy");

    const claudeText = fs.readFileSync(path.join(projectRoot, "CLAUDE.md"), "utf8");
    assert.match(claudeText, /HELLO-SCHOLAR:BEGIN claude/);
    assert.match(claudeText, /hello-scholar Guide/);

    for (const name of listSkillNames()) {
      const target = path.join(projectRoot, ".claude", "skills", name);
      assert.equal(fs.lstatSync(target).isSymbolicLink(), false, `${name} should be copied`);
      assert.ok(fs.existsSync(path.join(target, "SKILL.md")), `${name} should contain SKILL.md`);
      assert.ok(fs.existsSync(path.join(target, ".hello-scholar-install.json")), `${name} should contain ownership metadata`);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("uninstall removes owned artifacts and preserves user content", () => {
  const projectRoot = makeTempProject();
  try {
    fs.writeFileSync(path.join(projectRoot, "AGENTS.md"), "# User Rules\n\nKeep me.\n", "utf8");
    install({ tool: "codex", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    const conflictDir = path.join(projectRoot, ".agents", "skills", "custom-skill");
    fs.mkdirSync(conflictDir, { recursive: true });
    fs.writeFileSync(path.join(conflictDir, "SKILL.md"), "---\nname: custom-skill\n---\n", "utf8");

    const summary = uninstall({ tool: "codex", projectRoot: projectRoot, repoRoot: REPO_ROOT });
    assert.equal(summary.tool, "codex");

    const agentsText = fs.readFileSync(path.join(projectRoot, "AGENTS.md"), "utf8");
    assert.doesNotMatch(agentsText, /HELLO-SCHOLAR:BEGIN codex/);
    assert.match(agentsText, /# User Rules/);
    assert.ok(fs.existsSync(conflictDir), "unowned skill directory should remain");

    for (const name of listSkillNames()) {
      assert.equal(fs.existsSync(path.join(projectRoot, ".agents", "skills", name)), false);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("uninstall removes copy-mode skills with ownership metadata", () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "claude", mode: "copy", projectRoot: projectRoot, repoRoot: REPO_ROOT });
    const skillRoot = path.join(projectRoot, ".claude", "skills");

    for (const name of listSkillNames()) {
      assert.ok(fs.existsSync(path.join(skillRoot, name, ".hello-scholar-install.json")));
    }

    uninstall({ tool: "claude", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    for (const name of listSkillNames()) {
      assert.equal(fs.existsSync(path.join(skillRoot, name)), false, `${name} should be removed`);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("uninstall preserves copy-mode skills owned by another tool", () => {
  const projectRoot = makeTempProject();
  try {
    const skillRoot = path.join(projectRoot, ".agents", "skills");
    const skillDir = path.join(skillRoot, "writing-plans");
    fs.mkdirSync(skillDir, { recursive: true });
    fs.writeFileSync(path.join(skillDir, "SKILL.md"), "---\nname: writing-plans\n---\n", "utf8");
    fs.writeFileSync(
      path.join(skillDir, ".hello-scholar-install.json"),
      JSON.stringify({ source: "/tmp/example", mode: "copy", tool: "claude" }, null, 2),
      "utf8"
    );

    uninstall({ tool: "codex", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    assert.ok(fs.existsSync(skillDir), "skill owned by another tool should remain");
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("repeated install replaces instruction block instead of duplicating it", () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "codex", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT });
    install({ tool: "codex", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    const agentsText = fs.readFileSync(path.join(projectRoot, "AGENTS.md"), "utf8");
    assert.equal(countMatches(agentsText, /HELLO-SCHOLAR:BEGIN codex/g), 1);
    assert.equal(countMatches(agentsText, /HELLO-SCHOLAR:END codex/g), 1);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("cli install prompts before replacing an existing codex instruction block", async () => {
  const projectRoot = makeTempProject();
  try {
    const agentsPath = path.join(projectRoot, "AGENTS.md");
    const originalText = upsertInstructionBlock("", "codex", "manual edit inside managed block");
    fs.writeFileSync(agentsPath, originalText, "utf8");

    const io = makeCliIo("no\n");
    await main(["install", "codex"], {
      projectRoot,
      repoRoot: REPO_ROOT,
      stdin: io.stdin,
      stdout: io.stdout,
    });

    const output = io.getOutput();
    assert.match(output, /hello-scholar is already installed for codex/);
    assert.match(output, /HELLO-SCHOLAR:BEGIN codex/);
    assert.match(output, /Type "yes" to continue:/);
    assert.match(output, /install codex cancelled/);
    assert.equal(fs.readFileSync(agentsPath, "utf8"), originalText);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("cli install continues after yes when replacing an existing codex instruction block", async () => {
  const projectRoot = makeTempProject();
  try {
    const agentsPath = path.join(projectRoot, "AGENTS.md");
    fs.writeFileSync(
      agentsPath,
      upsertInstructionBlock("", "codex", "manual edit inside managed block"),
      "utf8"
    );

    const io = makeCliIo("yes\n");
    await main(["install", "codex"], {
      projectRoot,
      repoRoot: REPO_ROOT,
      stdin: io.stdin,
      stdout: io.stdout,
    });

    const agentsText = fs.readFileSync(agentsPath, "utf8");
    assert.match(io.getOutput(), /install codex: installed/);
    assert.match(agentsText, /hello-scholar Guide/);
    assert.doesNotMatch(agentsText, /manual edit inside managed block/);
    assert.equal(countMatches(agentsText, /HELLO-SCHOLAR:BEGIN codex/g), 1);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("cli install does not prompt on first install", async () => {
  const projectRoot = makeTempProject();
  try {
    const io = makeCliIo("");
    await main(["install", "codex"], {
      projectRoot,
      repoRoot: REPO_ROOT,
      stdin: io.stdin,
      stdout: io.stdout,
    });

    const output = io.getOutput();
    assert.doesNotMatch(output, /Type "yes" to continue:/);
    assert.match(output, /install codex: installed/);
    assert.match(
      fs.readFileSync(path.join(projectRoot, "AGENTS.md"), "utf8"),
      /HELLO-SCHOLAR:BEGIN codex/
    );
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("cli install prompts for claude using claude markers", async () => {
  const projectRoot = makeTempProject();
  try {
    const claudePath = path.join(projectRoot, "CLAUDE.md");
    const originalText = upsertInstructionBlock("", "claude", "manual claude edit");
    fs.writeFileSync(claudePath, originalText, "utf8");

    const io = makeCliIo("no\n");
    await main(["install", "claude"], {
      projectRoot,
      repoRoot: REPO_ROOT,
      stdin: io.stdin,
      stdout: io.stdout,
    });

    const output = io.getOutput();
    assert.match(output, /hello-scholar is already installed for claude/);
    assert.match(output, /HELLO-SCHOLAR:BEGIN claude/);
    assert.match(output, /HELLO-SCHOLAR:END claude/);
    assert.equal(fs.readFileSync(claudePath, "utf8"), originalText);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("install skips existing unowned skill directories", () => {
  const projectRoot = makeTempProject();
  try {
    const target = path.join(projectRoot, ".agents", "skills", "writing-plans");
    fs.mkdirSync(target, { recursive: true });
    fs.writeFileSync(path.join(target, "SKILL.md"), "---\nname: writing-plans\n---\ncustom\n", "utf8");

    const summary = install({ tool: "codex", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    assert.ok(summary.skipped >= 1);
    assert.equal(fs.lstatSync(target).isSymbolicLink(), false);
    assert.match(fs.readFileSync(path.join(target, "SKILL.md"), "utf8"), /custom/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("copy install skips skill directories owned by another tool", () => {
  const projectRoot = makeTempProject();
  try {
    const target = path.join(projectRoot, ".agents", "skills", "writing-plans");
    fs.mkdirSync(target, { recursive: true });
    fs.writeFileSync(path.join(target, "SKILL.md"), "---\nname: writing-plans\n---\ncustom\n", "utf8");
    fs.writeFileSync(
      path.join(target, ".hello-scholar-install.json"),
      JSON.stringify({ source: "/tmp/example", mode: "copy", tool: "claude" }, null, 2),
      "utf8"
    );

    const summary = install({ tool: "codex", mode: "copy", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    assert.ok(summary.skipped >= 1);
    assert.match(fs.readFileSync(path.join(target, "SKILL.md"), "utf8"), /custom/);
    const metadata = JSON.parse(fs.readFileSync(path.join(target, ".hello-scholar-install.json"), "utf8"));
    assert.equal(metadata.tool, "claude");
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("copy install skips skill directories with invalid ownership metadata", () => {
  const projectRoot = makeTempProject();
  try {
    const target = path.join(projectRoot, ".agents", "skills", "writing-plans");
    fs.mkdirSync(target, { recursive: true });
    fs.writeFileSync(path.join(target, "SKILL.md"), "---\nname: writing-plans\n---\ncustom\n", "utf8");
    fs.writeFileSync(path.join(target, ".hello-scholar-install.json"), "{not json", "utf8");

    const summary = install({ tool: "codex", mode: "copy", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    assert.ok(summary.skipped >= 1);
    assert.match(fs.readFileSync(path.join(target, "SKILL.md"), "utf8"), /custom/);
    assert.equal(fs.readFileSync(path.join(target, ".hello-scholar-install.json"), "utf8"), "{not json");
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("install does not write instruction block when skill install fails", () => {
  const projectRoot = makeTempProject();
  try {
    const blockingFile = path.join(projectRoot, ".agents");
    fs.writeFileSync(blockingFile, "not a directory", "utf8");

    assert.throws(
      () => install({ tool: "codex", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT }),
      /ENOTDIR|EEXIST|not a directory/i
    );

    assert.equal(fs.existsSync(path.join(projectRoot, "AGENTS.md")), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("claude install falls back to AGENTS content when CLAUDE.md source is absent", () => {
  const projectRoot = makeTempProject();
  try {
    assert.equal(fs.existsSync(path.join(REPO_ROOT, "CLAUDE.md")), false);
    assert.equal(fs.existsSync(path.join(REPO_ROOT, "CLAUDE.MD")), false);

    install({ tool: "claude", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    const claudeText = fs.readFileSync(path.join(projectRoot, "CLAUDE.md"), "utf8");
    assert.match(claudeText, /HELLO-SCHOLAR:BEGIN claude/);
    assert.match(claudeText, /hello-scholar Guide/);
    assert.match(claudeText, /Read Before You Write/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("file-level uninstall removes only the requested tool block", () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "codex", mode: "link", projectRoot: projectRoot, repoRoot: REPO_ROOT });
    const agentsPath = path.join(projectRoot, "AGENTS.md");
    const withClaudeBlock = upsertInstructionBlock(
      fs.readFileSync(agentsPath, "utf8"),
      "claude",
      "claude rules"
    );
    fs.writeFileSync(agentsPath, withClaudeBlock, "utf8");

    uninstall({ tool: "codex", projectRoot: projectRoot, repoRoot: REPO_ROOT });

    const agentsText = fs.readFileSync(agentsPath, "utf8");
    assert.doesNotMatch(agentsText, /HELLO-SCHOLAR:BEGIN codex/);
    assert.match(agentsText, /HELLO-SCHOLAR:BEGIN claude/);
    assert.match(agentsText, /claude rules/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});
