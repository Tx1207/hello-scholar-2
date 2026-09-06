const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { Readable, Writable } = require("node:stream");
const test = require("node:test");

const { formatSummary, main, parseArgs, usageText } = require("../src/cli");
const { directoryDigest } = require("../src/fs-ops");
const {
  hasInstructionBlock,
  removeInstructionBlock,
  upsertInstructionBlock,
  wrapBlock,
} = require("../src/instruction-blocks");
const {
  InstallConflictError,
  RETIRED_SKILLS,
  inspectInstall,
  install,
  uninstall,
} = require("../src/install");
const { discoverSkills, parseSkillName } = require("../src/skill-discovery");

const REPO_ROOT = path.resolve(__dirname, "..");
const CURRENT_SKILLS = [
  "converge-to-spec",
  "crash-audit",
  "docs-maintenance",
  "grilling",
  "handoff",
  "landing",
  "manage-specs",
  "record-experiment",
  "takeoff",
];

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

function makeMutatingCliIo(mutate) {
  let output = "";
  let sent = false;
  const stdin = new Readable({
    read() {
      if (!sent) {
        sent = true;
        mutate();
        this.push("yes\n");
        this.push(null);
      }
    },
  });
  const stdout = new Writable({
    write(chunk, encoding, callback) {
      output += chunk.toString();
      callback();
    },
  });
  return { stdin, stdout, getOutput: () => output };
}

function approvalsFor(plan) {
  return plan.conflicts.map((conflict) => ({
    targetPath: conflict.targetPath,
    digest: conflict.digest,
  }));
}

function markerPath(target) {
  return path.join(target, ".hello-scholar-install.json");
}

function writeCopyMarker(target, metadata) {
  fs.writeFileSync(markerPath(target), `${JSON.stringify(metadata, null, 2)}\n`, "utf8");
}

test("parseArgs accepts only the existing complete-set install commands", () => {
  assert.deepEqual(parseArgs(["help"]), { action: "help" });
  assert.deepEqual(parseArgs(["install", "codex"]), {
    action: "install", tool: "codex", mode: "link",
  });
  assert.deepEqual(parseArgs(["install", "claude", "--mode", "copy"]), {
    action: "install", tool: "claude", mode: "copy",
  });
  assert.deepEqual(parseArgs(["uninstall", "codex"]), { action: "uninstall", tool: "codex" });
  assert.throws(() => parseArgs(["install", "codex", "--with", "handoff"]), /Usage:/);
  assert.throws(() => parseArgs(["install", "gemini"]), /Usage:/);
  assert.throws(() => parseArgs(["install", "codex", "--mode", "bad"]), /Usage:/);
});

test("usage and summary expose the retained command contract", () => {
  const text = usageText();
  assert.match(text, /hello-scholar install codex\|claude \[--mode link\|copy\]/);
  assert.doesNotMatch(text, /--with/);
  assert.equal(
    formatSummary({ action: "install", tool: "codex", installed: 2, updated: 1, removed: 3, skipped: 0 }),
    "install codex: installed 2, updated 1, removed 3, skipped 0"
  );
});

test("instruction blocks insert, replace, remove, and recognize CRLF", () => {
  const userText = "# Project Rules\n\nKeep this.";
  const inserted = upsertInstructionBlock(userText, "codex", "hello rules");
  assert.equal(hasInstructionBlock(inserted, "codex"), true);
  const replaced = upsertInstructionBlock(inserted.replace(/\n/g, "\r\n"), "codex", "new rules");
  assert.match(replaced, /new rules/);
  assert.doesNotMatch(replaced, /hello rules/);
  assert.match(removeInstructionBlock(replaced, "codex"), /# Project Rules/);
});

test("instruction replacement and removal preserve LF and CRLF outside the block", () => {
  const lfBlock = wrapBlock("codex", "owned");
  const lfOutside = "\n\n\nUSER\n";
  assert.equal(
    upsertInstructionBlock(`${lfBlock}${lfOutside}`, "codex", "new"),
    `${wrapBlock("codex", "new")}${lfOutside}`
  );
  assert.equal(removeInstructionBlock(`${lfBlock}${lfOutside}`, "codex"), lfOutside);

  const crlfBlock = lfBlock.replace(/\n/g, "\r\n");
  const crlfPrefix = "HEAD\r\n\r\n";
  const crlfSuffix = "\r\n\r\n\r\nUSER\r\n";
  assert.equal(
    upsertInstructionBlock(`${crlfPrefix}${crlfBlock}${crlfSuffix}`, "codex", "new"),
    `${crlfPrefix}${wrapBlock("codex", "new")}${crlfSuffix}`
  );
  assert.equal(
    removeInstructionBlock(`${crlfPrefix}${crlfBlock}${crlfSuffix}`, "codex"),
    `${crlfPrefix}${crlfSuffix}`
  );
});

test("instruction replacement and removal preserve text beside blocks at file boundaries", () => {
  const oldBlock = wrapBlock("codex", "owned");
  const newBlock = wrapBlock("codex", "new");
  const cases = [
    { current: oldBlock, replaced: newBlock, removed: "" },
    { current: `${oldBlock}TAIL`, replaced: `${newBlock}TAIL`, removed: "TAIL" },
    { current: `HEAD${oldBlock}`, replaced: `HEAD${newBlock}`, removed: "HEAD" },
    { current: `HEAD${oldBlock}TAIL`, replaced: `HEAD${newBlock}TAIL`, removed: "HEADTAIL" },
  ];
  for (const fixture of cases) {
    assert.equal(upsertInstructionBlock(fixture.current, "codex", "new"), fixture.replaced);
    assert.equal(removeInstructionBlock(fixture.current, "codex"), fixture.removed);
  }
});

test("discovery returns exactly the nine retained Skills and no retired name", () => {
  const names = listSkillNames();
  assert.deepEqual(names, CURRENT_SKILLS);
  assert.deepEqual(names.filter((name) => RETIRED_SKILLS.includes(name)), []);
  assert.equal(new Set(names).size, names.length);
});

test("parseSkillName accepts LF and CRLF frontmatter", () => {
  assert.equal(parseSkillName("---\nname: lf-skill\n---\n", "lf/SKILL.md"), "lf-skill");
  assert.equal(parseSkillName("---\r\nname: crlf-skill\r\n---\r\n", "crlf/SKILL.md"), "crlf-skill");
});

test("fresh link install uses root AGENTS.md and installs all current Skills", () => {
  const projectRoot = makeTempProject();
  try {
    fs.writeFileSync(path.join(projectRoot, "AGENTS.md"), "# User Rules\n\nKeep me.\n", "utf8");
    const summary = install({ tool: "codex", mode: "link", projectRoot, repoRoot: REPO_ROOT });
    assert.equal(summary.installed, CURRENT_SKILLS.length);
    assert.equal(summary.removed, 0);

    const agentsText = fs.readFileSync(path.join(projectRoot, "AGENTS.md"), "utf8");
    const portableText = fs.readFileSync(path.join(REPO_ROOT, "AGENTS.md"), "utf8").trimEnd();
    assert.match(agentsText, /HELLO-SCHOLAR:BEGIN codex/);
    assert.ok(agentsText.includes(portableText));
    assert.match(agentsText, /# User Rules/);
    assert.match(agentsText, /Write code that will not need to be rewritten/);
    assert.doesNotMatch(agentsText, /npm test|Current repository language: Chinese|hello-scholar Repository Guide/);
    assert.equal(fs.existsSync(path.join(projectRoot, ".agents", ".hello-scholar-install.json")), false);

    for (const name of CURRENT_SKILLS) {
      const target = path.join(projectRoot, ".agents", "skills", name);
      assert.equal(fs.lstatSync(target).isSymbolicLink(), true);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("fresh copy install records a content baseline for every Skill", () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT });
    assert.equal(fs.existsSync(path.join(projectRoot, ".claude", ".hello-scholar-install.json")), false);
    assert.equal(fs.lstatSync(path.join(projectRoot, "CLAUDE.md")).isSymbolicLink(), false);
    assert.equal(
      fs.readFileSync(path.join(projectRoot, "CLAUDE.md"), "utf8").trim(),
      wrapBlock("claude", fs.readFileSync(path.join(REPO_ROOT, "AGENTS.md"), "utf8"))
    );
    for (const name of CURRENT_SKILLS) {
      const target = path.join(projectRoot, ".claude", "skills", name);
      const marker = JSON.parse(fs.readFileSync(markerPath(target), "utf8"));
      assert.equal(fs.lstatSync(target).isSymbolicLink(), false);
      assert.equal(marker.tool, "claude");
      assert.equal(marker.mode, "copy");
      assert.equal(marker.baselineDigest, directoryDigest(target));
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("both tools use only AGENTS in both modes and upgrade without touching outside bytes", () => {
  const repoRoot = makeTempProject();
  const projectRoot = makeTempProject();
  try {
    fs.mkdirSync(path.join(repoRoot, "skills"));
    fs.writeFileSync(path.join(repoRoot, "CONTRIBUTING.md"), "repository-only sentinel\n");
    for (const [tool, filename, mode] of [
      ["codex", "AGENTS.md", "link"], ["codex", "AGENTS.md", "copy"],
      ["claude", "CLAUDE.md", "link"], ["claude", "CLAUDE.md", "copy"],
    ]) {
      const sourcePath = path.join(repoRoot, "AGENTS.md");
      const targetPath = path.join(projectRoot, filename);
      const prefix = "USER HEAD\r\n\r\n";
      const suffix = "\n\nUSER TAIL\n";
      fs.writeFileSync(sourcePath, `${tool} version one\n`);
      install({ tool, mode, projectRoot, repoRoot });
      fs.writeFileSync(targetPath, `${prefix}${wrapBlock(tool, `${tool} version one`)}${suffix}`);
      fs.writeFileSync(sourcePath, `${tool} version two\n`);
      const plan = inspectInstall({ tool, mode, projectRoot, repoRoot });
      assert.equal(plan.conflicts.length, 1);
      assert.throws(() => install({ tool, mode, projectRoot, repoRoot }), InstallConflictError);
      uninstall({ tool, projectRoot, repoRoot });
      assert.equal(fs.readFileSync(targetPath, "utf8"), `${prefix}${wrapBlock(tool, `${tool} version one`)}${suffix}`);
      install({ tool, mode, projectRoot, repoRoot, approvedConflicts: approvalsFor(plan) });
      const expected = `${prefix}${wrapBlock(tool, `${tool} version two`)}${suffix}`;
      assert.equal(fs.readFileSync(targetPath, "utf8"), expected);
      install({ tool, mode, projectRoot, repoRoot });
      assert.equal(fs.readFileSync(targetPath, "utf8"), expected);
      uninstall({ tool, projectRoot, repoRoot });
      assert.equal(fs.readFileSync(targetPath, "utf8"), `${prefix}${suffix}`);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
    fs.rmSync(repoRoot, { recursive: true, force: true });
  }
});

test("missing AGENTS fails before any target writes for both tools and modes", () => {
  const repoRoot = makeTempProject();
  try {
    fs.mkdirSync(path.join(repoRoot, "skills", "example"), { recursive: true });
    fs.writeFileSync(path.join(repoRoot, "skills", "example", "SKILL.md"), "---\nname: example\n---\n");
    fs.writeFileSync(path.join(repoRoot, "CLAUDE.md"), "not the rule source\n");
    for (const tool of ["codex", "claude"]) {
      for (const mode of ["link", "copy"]) {
        const projectRoot = makeTempProject();
        try {
          assert.throws(() => install({ tool, mode, projectRoot, repoRoot }), /ENOENT.*AGENTS\.md/);
          assert.deepEqual(fs.readdirSync(projectRoot), []);
        } finally {
          fs.rmSync(projectRoot, { recursive: true, force: true });
        }
      }
    }
  } finally {
    fs.rmSync(repoRoot, { recursive: true, force: true });
  }
});

test("unchanged CLI reinstall is automatic and does not duplicate instructions", async () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "codex", mode: "link", projectRoot, repoRoot: REPO_ROOT });
    const io = makeCliIo("");
    await main(["install", "codex"], {
      projectRoot, repoRoot: REPO_ROOT, stdin: io.stdin, stdout: io.stdout,
    });
    assert.doesNotMatch(io.getOutput(), /Type "yes"/);
    assert.match(io.getOutput(), /updated 9/);
    const agentsText = fs.readFileSync(path.join(projectRoot, "AGENTS.md"), "utf8");
    assert.equal(countMatches(agentsText, /HELLO-SCHOLAR:BEGIN codex/g), 1);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("modified instruction block is reported before mutation and needs one exact approval", async () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "codex", mode: "link", projectRoot, repoRoot: REPO_ROOT });
    const agentsPath = path.join(projectRoot, "AGENTS.md");
    const editedText = upsertInstructionBlock(
      fs.readFileSync(agentsPath, "utf8"), "codex", "user changed the managed block"
    );
    fs.writeFileSync(agentsPath, editedText, "utf8");

    const declined = makeCliIo("no\n");
    await main(["install", "codex"], {
      projectRoot, repoRoot: REPO_ROOT, stdin: declined.stdin, stdout: declined.stdout,
    });
    assert.match(declined.getOutput(), /conflict managed-content-conflict AGENTS\.md/);
    assert.match(declined.getOutput(), /Type "yes" to continue/);
    assert.equal(fs.readFileSync(agentsPath, "utf8"), editedText);

    const approved = makeCliIo("yes\n");
    await main(["install", "codex"], {
      projectRoot, repoRoot: REPO_ROOT, stdin: approved.stdin, stdout: approved.stdout,
    });
    assert.doesNotMatch(fs.readFileSync(agentsPath, "utf8"), /user changed/);

    const unchanged = makeCliIo("");
    await main(["install", "codex"], {
      projectRoot, repoRoot: REPO_ROOT, stdin: unchanged.stdin, stdout: unchanged.stdout,
    });
    assert.doesNotMatch(unchanged.getOutput(), /Type "yes"/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("instruction approval cannot overwrite a newer edit made while the CLI waits", async () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "codex", mode: "link", projectRoot, repoRoot: REPO_ROOT });
    const agentsPath = path.join(projectRoot, "AGENTS.md");
    fs.writeFileSync(
      agentsPath,
      upsertInstructionBlock(fs.readFileSync(agentsPath, "utf8"), "codex", "first edit"),
      "utf8"
    );
    let textAfterPrompt;
    const io = makeMutatingCliIo(() => {
      textAfterPrompt = upsertInstructionBlock(
        fs.readFileSync(agentsPath, "utf8"),
        "codex",
        "newer edit while waiting"
      );
      fs.writeFileSync(agentsPath, textAfterPrompt, "utf8");
    });

    await assert.rejects(
      main(["install", "codex"], {
        projectRoot, repoRoot: REPO_ROOT, stdin: io.stdin, stdout: io.stdout,
      }),
      InstallConflictError
    );

    assert.match(io.getOutput(), /Type "yes" to continue/);
    assert.equal(fs.readFileSync(agentsPath, "utf8"), textAfterPrompt);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("modified and unknown-baseline managed copies are preserved until approved", () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT });
    const modifiedTarget = path.join(projectRoot, ".claude", "skills", "handoff");
    const modifiedSkill = path.join(modifiedTarget, "SKILL.md");
    fs.appendFileSync(modifiedSkill, "\nuser edit\n", "utf8");
    const legacyTarget = path.join(projectRoot, ".claude", "skills", "landing");
    const legacyMarker = JSON.parse(fs.readFileSync(markerPath(legacyTarget), "utf8"));
    delete legacyMarker.baselineDigest;
    writeCopyMarker(legacyTarget, legacyMarker);

    assert.throws(
      () => install({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT }),
      (error) => error instanceof InstallConflictError && error.conflicts.length === 2
    );
    assert.match(fs.readFileSync(modifiedSkill, "utf8"), /user edit/);
    assert.equal(JSON.parse(fs.readFileSync(markerPath(legacyTarget), "utf8")).baselineDigest, undefined);

    const plan = inspectInstall({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT });
    install({
      tool: "claude",
      mode: "copy",
      projectRoot,
      repoRoot: REPO_ROOT,
      approvedConflicts: approvalsFor(plan),
    });
    assert.doesNotMatch(fs.readFileSync(modifiedSkill, "utf8"), /user edit/);
    assert.equal(typeof JSON.parse(fs.readFileSync(markerPath(legacyTarget), "utf8")).baselineDigest, "string");
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("copy approval cannot overwrite a newer edit made while the CLI waits", async () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT });
    const skillPath = path.join(projectRoot, ".claude", "skills", "handoff", "SKILL.md");
    fs.appendFileSync(skillPath, "\nfirst edit\n", "utf8");
    const io = makeMutatingCliIo(() => {
      fs.appendFileSync(skillPath, "newer edit while waiting\n", "utf8");
    });

    await assert.rejects(
      main(["install", "claude", "--mode", "copy"], {
        projectRoot, repoRoot: REPO_ROOT, stdin: io.stdin, stdout: io.stdout,
      }),
      InstallConflictError
    );

    assert.match(io.getOutput(), /Type "yes" to continue/);
    assert.match(fs.readFileSync(skillPath, "utf8"), /newer edit while waiting/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("an unowned current target blocks the whole install and is never approvable", () => {
  const projectRoot = makeTempProject();
  try {
    const target = path.join(projectRoot, ".agents", "skills", "handoff");
    fs.mkdirSync(target, { recursive: true });
    fs.writeFileSync(path.join(target, "SKILL.md"), "custom\n", "utf8");

    assert.throws(
      () => install({
        tool: "codex",
        mode: "link",
        projectRoot,
        repoRoot: REPO_ROOT,
        approvedConflicts: [{ targetPath: target, digest: "not-applicable" }],
      }),
      (error) => error instanceof InstallConflictError
        && error.conflicts[0].code === "unowned-target"
    );
    assert.equal(fs.readFileSync(path.join(target, "SKILL.md"), "utf8"), "custom\n");
    assert.equal(fs.existsSync(path.join(projectRoot, "AGENTS.md")), false);
    assert.equal(fs.existsSync(path.join(projectRoot, ".agents", "skills", "landing")), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("install removes an owned dangling retired link discovered with lstat", () => {
  const projectRoot = makeTempProject();
  try {
    const retiredName = "writing-plans";
    const target = path.join(projectRoot, ".agents", "skills", retiredName);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.symlinkSync(path.join(REPO_ROOT, "skills", retiredName), target, "dir");
    assert.equal(fs.existsSync(target), false, "fixture must be a dangling link");
    assert.equal(fs.lstatSync(target).isSymbolicLink(), true);

    const summary = install({ tool: "codex", mode: "link", projectRoot, repoRoot: REPO_ROOT });
    assert.equal(summary.removed, 1);
    assert.equal(fs.existsSync(target), false);
    assert.throws(() => fs.lstatSync(target), /ENOENT/);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("retired clean copies are removed but modified retired copies require approval", () => {
  const projectRoot = makeTempProject();
  try {
    const skillRoot = path.join(projectRoot, ".claude", "skills");
    const cleanTarget = path.join(skillRoot, "writing-plans");
    const modifiedTarget = path.join(skillRoot, "generating-tasks");
    for (const [name, target] of [["writing-plans", cleanTarget], ["generating-tasks", modifiedTarget]]) {
      fs.mkdirSync(target, { recursive: true });
      fs.writeFileSync(path.join(target, "SKILL.md"), `---\nname: ${name}\n---\n`, "utf8");
      writeCopyMarker(target, {
        source: path.join(REPO_ROOT, "skills", name),
        mode: "copy",
        tool: "claude",
        baselineDigest: directoryDigest(target),
      });
    }
    fs.appendFileSync(path.join(modifiedTarget, "SKILL.md"), "user edit\n", "utf8");

    assert.throws(
      () => install({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT }),
      InstallConflictError
    );
    assert.ok(fs.existsSync(cleanTarget), "preflight conflict prevents partial retirement");
    assert.ok(fs.existsSync(modifiedTarget));

    const plan = inspectInstall({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT });
    install({
      tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT,
      approvedConflicts: approvalsFor(plan),
    });
    assert.equal(fs.existsSync(cleanTarget), false);
    assert.equal(fs.existsSync(modifiedTarget), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("other-source retired links are preserved and block mutation", async () => {
  const projectRoot = makeTempProject();
  const otherSource = makeTempProject();
  try {
    const target = path.join(projectRoot, ".agents", "skills", "writing-plans");
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.symlinkSync(otherSource, target, "dir");
    const io = makeCliIo("yes\n");
    await assert.rejects(
      main(["install", "codex"], {
        projectRoot, repoRoot: REPO_ROOT, stdin: io.stdin, stdout: io.stdout,
      }),
      InstallConflictError
    );
    assert.match(io.getOutput(), /conflict unowned-target \.agents\/skills\/writing-plans/);
    assert.doesNotMatch(io.getOutput(), /Type "yes"/);
    assert.equal(fs.realpathSync(target), fs.realpathSync(otherSource));
    assert.equal(fs.existsSync(path.join(projectRoot, "AGENTS.md")), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
    fs.rmSync(otherSource, { recursive: true, force: true });
  }
});

test("uninstall removes unchanged owned assets and preserves modified user content", () => {
  const projectRoot = makeTempProject();
  try {
    fs.writeFileSync(path.join(projectRoot, "CLAUDE.md"), "# User Rules\n", "utf8");
    install({ tool: "claude", mode: "copy", projectRoot, repoRoot: REPO_ROOT });
    const modifiedTarget = path.join(projectRoot, ".claude", "skills", "handoff");
    fs.appendFileSync(path.join(modifiedTarget, "SKILL.md"), "user edit\n", "utf8");
    const claudePath = path.join(projectRoot, "CLAUDE.md");
    fs.writeFileSync(
      claudePath,
      upsertInstructionBlock(fs.readFileSync(claudePath, "utf8"), "claude", "user block edit"),
      "utf8"
    );

    uninstall({ tool: "claude", projectRoot, repoRoot: REPO_ROOT });
    assert.ok(fs.existsSync(modifiedTarget));
    assert.match(fs.readFileSync(claudePath, "utf8"), /user block edit/);
    assert.match(fs.readFileSync(claudePath, "utf8"), /# User Rules/);
    assert.equal(fs.existsSync(path.join(projectRoot, ".claude", "skills", "landing")), false);
    assert.equal(fs.existsSync(path.join(projectRoot, ".claude", ".hello-scholar-install.json")), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("uninstall preserves exact whitespace outside an unchanged managed block", () => {
  const projectRoot = makeTempProject();
  try {
    install({ tool: "codex", mode: "link", projectRoot, repoRoot: REPO_ROOT });
    const agentsPath = path.join(projectRoot, "AGENTS.md");
    const sourceText = fs.readFileSync(
      path.join(REPO_ROOT, "AGENTS.md"),
      "utf8"
    );
    const outsideText = "\n\n\nUSER\n";
    fs.writeFileSync(agentsPath, `${wrapBlock("codex", sourceText)}${outsideText}`, "utf8");

    uninstall({ tool: "codex", projectRoot, repoRoot: REPO_ROOT });

    assert.equal(fs.readFileSync(agentsPath, "utf8"), outsideText);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("uninstall preserves instructions with duplicate or misordered markers", () => {
  const duplicateProject = makeTempProject();
  const misorderedProject = makeTempProject();
  try {
    install({ tool: "codex", mode: "link", projectRoot: duplicateProject, repoRoot: REPO_ROOT });
    const duplicatePath = path.join(duplicateProject, "AGENTS.md");
    const duplicateText = `${fs.readFileSync(duplicatePath, "utf8")}\n`
      + "<!-- HELLO-SCHOLAR:BEGIN codex -->\nuser duplicate\n"
      + "<!-- HELLO-SCHOLAR:END codex -->\n";
    fs.writeFileSync(duplicatePath, duplicateText, "utf8");
    uninstall({ tool: "codex", projectRoot: duplicateProject, repoRoot: REPO_ROOT });
    assert.equal(fs.readFileSync(duplicatePath, "utf8"), duplicateText);

    install({ tool: "codex", mode: "link", projectRoot: misorderedProject, repoRoot: REPO_ROOT });
    const misorderedPath = path.join(misorderedProject, "AGENTS.md");
    const misorderedText = "<!-- HELLO-SCHOLAR:END codex -->\n"
      + `${fs.readFileSync(misorderedPath, "utf8")}`;
    fs.writeFileSync(misorderedPath, misorderedText, "utf8");
    uninstall({ tool: "codex", projectRoot: misorderedProject, repoRoot: REPO_ROOT });
    assert.equal(fs.readFileSync(misorderedPath, "utf8"), misorderedText);
  } finally {
    fs.rmSync(duplicateProject, { recursive: true, force: true });
    fs.rmSync(misorderedProject, { recursive: true, force: true });
  }
});

test("install failure before Skill writes does not create instructions", () => {
  const projectRoot = makeTempProject();
  try {
    fs.writeFileSync(path.join(projectRoot, ".agents"), "not a directory", "utf8");
    assert.throws(
      () => install({ tool: "codex", mode: "link", projectRoot, repoRoot: REPO_ROOT }),
      InstallConflictError
    );
    assert.equal(fs.existsSync(path.join(projectRoot, "AGENTS.md")), false);
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("linked managed parents block installation and obsolete state files are untouched", () => {
  const linkedParentProject = makeTempProject();
  const linkedStateProject = makeTempProject();
  const externalRoot = makeTempProject();
  const externalState = path.join(externalRoot, "state.json");
  try {
    fs.symlinkSync(externalRoot, path.join(linkedParentProject, ".agents"), "dir");
    assert.throws(
      () => install({ tool: "codex", mode: "link", projectRoot: linkedParentProject, repoRoot: REPO_ROOT }),
      InstallConflictError
    );
    assert.deepEqual(fs.readdirSync(externalRoot), []);
    assert.equal(fs.existsSync(path.join(linkedParentProject, "AGENTS.md")), false);

    fs.mkdirSync(path.join(linkedStateProject, ".agents"), { recursive: true });
    fs.writeFileSync(externalState, JSON.stringify({ schema: 1, tool: "codex" }), "utf8");
    fs.symlinkSync(externalState, path.join(linkedStateProject, ".agents", ".hello-scholar-install.json"));
    install({ tool: "codex", mode: "link", projectRoot: linkedStateProject, repoRoot: REPO_ROOT });
    uninstall({ tool: "codex", projectRoot: linkedStateProject, repoRoot: REPO_ROOT });
    assert.equal(fs.readFileSync(externalState, "utf8"), JSON.stringify({ schema: 1, tool: "codex" }));
    assert.equal(fs.lstatSync(path.join(linkedStateProject, ".agents", ".hello-scholar-install.json")).isSymbolicLink(), true);
    assert.equal(fs.readFileSync(path.join(linkedStateProject, "AGENTS.md"), "utf8"), "\n\n");
  } finally {
    fs.rmSync(linkedParentProject, { recursive: true, force: true });
    fs.rmSync(linkedStateProject, { recursive: true, force: true });
    fs.rmSync(externalRoot, { recursive: true, force: true });
  }
});
