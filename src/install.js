const fs = require("node:fs");
const path = require("node:path");
const {
  hashValue,
  inspectSkillTarget,
  installSkillCopy,
  installSkillLink,
  lstatPath,
  uninstallSkillTarget,
} = require("./fs-ops");
const {
  beginMarker,
  endMarker,
  hasInstructionBlock,
  removeInstructionBlock,
  upsertInstructionBlock,
  wrapBlock,
} = require("./instruction-blocks");
const { resolveHelloScholarRoot, resolveProjectRoot } = require("./project-root");
const { discoverSkills } = require("./skill-discovery");

const RETIRED_SKILLS = [
  "brainstorming",
  "generating-tasks",
  "test-driven-development",
  "using-git-worktrees",
  "using-helloscholar",
  "writing-great-skills",
  "writing-plans",
];

const TOOL_CONFIG = {
  codex: {
    instructionFile: "AGENTS.md",
    skillRoot: path.join(".agents", "skills"),
  },
  claude: {
    instructionFile: "CLAUDE.md",
    skillRoot: path.join(".claude", "skills"),
  },
};

class InstallConflictError extends Error {
  constructor(conflicts) {
    super(`installation has ${conflicts.length} unresolved conflict${conflicts.length === 1 ? "" : "s"}`);
    this.name = "InstallConflictError";
    this.conflicts = conflicts;
  }
}

function readInstructionSource(repoRoot) {
  // Both tools share AGENTS.md; npm packages do not retain the source CLAUDE.md symlink.
  return fs.readFileSync(path.join(repoRoot, "AGENTS.md"), "utf8");
}

function readFileIfExists(filePath) {
  const stat = lstatPath(filePath);
  return stat && stat.isFile() ? fs.readFileSync(filePath, "utf8") : "";
}

function instructionPath(projectRoot, tool) {
  return path.join(projectRoot, TOOL_CONFIG[tool].instructionFile);
}

function inspectInstallParents(projectRoot, tool) {
  const config = TOOL_CONFIG[tool];
  const toolRoot = path.join(projectRoot, path.dirname(config.skillRoot));
  const skillRoot = path.join(projectRoot, config.skillRoot);
  const results = [];
  for (const targetPath of [toolRoot, skillRoot]) {
    const stat = lstatPath(targetPath);
    if (stat && (!stat.isDirectory() || stat.isSymbolicLink())) {
      results.push({
        state: "unowned",
        targetPath,
        reason: "managed parent is not a regular project directory",
      });
      break;
    }
  }
  return results;
}

function relativeDisplayPath(projectRoot, targetPath) {
  return path.relative(projectRoot, targetPath).split(path.sep).join("/") || ".";
}

function instructionBlock(existingText, tool) {
  const begin = beginMarker(tool);
  const end = endMarker(tool);
  const beginIndex = existingText.indexOf(begin);
  const endIndex = existingText.indexOf(end, beginIndex + begin.length);
  if (beginIndex === -1 || endIndex === -1) {
    return null;
  }
  return existingText.slice(beginIndex, endIndex + end.length);
}

function hasUniqueInstructionBlock(existingText, tool) {
  const beginCount = existingText.split(beginMarker(tool)).length - 1;
  const endCount = existingText.split(endMarker(tool)).length - 1;
  return beginCount === 1 && endCount === 1 && hasInstructionBlock(existingText, tool);
}

function inspectInstruction(projectRoot, repoRoot, tool) {
  const targetPath = instructionPath(projectRoot, tool);
  const targetStat = lstatPath(targetPath);
  const sourceText = readInstructionSource(repoRoot);
  if (!targetStat) {
    return { state: "absent", targetPath, sourceText };
  }
  if (!targetStat.isFile() || targetStat.isSymbolicLink()) {
    return {
      state: "unowned",
      targetPath,
      sourceText,
      reason: "instruction target is not a regular file",
    };
  }

  const existingText = fs.readFileSync(targetPath, "utf8");
  const beginCount = existingText.split(beginMarker(tool)).length - 1;
  const endCount = existingText.split(endMarker(tool)).length - 1;
  if (beginCount === 0 && endCount === 0) {
    return { state: "absent", targetPath, sourceText, existingText };
  }
  if (!hasUniqueInstructionBlock(existingText, tool)) {
    return {
      state: "unowned",
      targetPath,
      sourceText,
      existingText,
      reason: "instruction markers are incomplete or malformed",
    };
  }

  const actualBlock = instructionBlock(existingText, tool);
  if (actualBlock === wrapBlock(tool, sourceText)) {
    return {
      state: "managed-clean",
      targetPath,
      sourceText,
      existingText,
    };
  }
  return {
    state: "managed-conflict",
    targetPath,
    sourceText,
    actualDigest: hashValue(actualBlock),
    existingText,
    reason: "instruction block differs from the current template",
  };
}

function conflictFor(projectRoot, targetPath, inspected) {
  const approvable = inspected.state === "managed-conflict";
  return {
    path: relativeDisplayPath(projectRoot, targetPath),
    targetPath,
    code: approvable ? "managed-content-conflict" : "unowned-target",
    message: inspected.reason,
    approvable,
    digest: approvable ? inspected.actualDigest : null,
  };
}

function inspectInstall(options) {
  // Purpose: build a complete, read-only installation plan; Output: current Skills, retired targets, instruction state, and every conflict found before mutation.
  const tool = options.tool;
  const mode = options.mode || "link";
  const projectRoot = options.projectRoot || resolveProjectRoot();
  const repoRoot = options.repoRoot || resolveHelloScholarRoot();
  const config = TOOL_CONFIG[tool];
  const skills = discoverSkills(repoRoot);
  const activeNames = new Set(skills.map((skill) => skill.name));
  const overlap = RETIRED_SKILLS.filter((name) => activeNames.has(name));
  if (overlap.length > 0) {
    throw new Error(`retired Skills are still discoverable: ${overlap.join(", ")}`);
  }

  const parentConflicts = inspectInstallParents(projectRoot, tool);
  const parentsSafe = parentConflicts.length === 0;
  const skillTargets = skills.map((skill) => {
    const targetPath = path.join(projectRoot, config.skillRoot, skill.name);
    return {
      name: skill.name,
      sourceDir: skill.sourceDir,
      targetPath,
      inspected: parentsSafe
        ? inspectSkillTarget(targetPath, skill.sourceDir, tool)
        : { state: "blocked" },
    };
  });
  const retiredTargets = RETIRED_SKILLS.map((name) => {
    const sourceDir = path.join(repoRoot, "skills", name);
    const targetPath = path.join(projectRoot, config.skillRoot, name);
    return {
      name,
      sourceDir,
      targetPath,
      inspected: parentsSafe
        ? inspectSkillTarget(targetPath, sourceDir, tool)
        : { state: "blocked" },
    };
  });
  const instruction = inspectInstruction(projectRoot, repoRoot, tool);
  const conflicts = parentConflicts.map((inspected) =>
    conflictFor(projectRoot, inspected.targetPath, inspected)
  );
  for (const target of [...skillTargets, ...retiredTargets]) {
    if (target.inspected.state === "managed-conflict" || target.inspected.state === "unowned") {
      conflicts.push(conflictFor(projectRoot, target.targetPath, target.inspected));
    }
  }
  if (instruction.state === "managed-conflict" || instruction.state === "unowned") {
    conflicts.push(conflictFor(projectRoot, instruction.targetPath, instruction));
  }

  return {
    tool,
    mode,
    projectRoot,
    repoRoot,
    config,
    skillTargets,
    retiredTargets,
    instruction,
    conflicts,
  };
}

function approvedMap(approvedConflicts = []) {
  const approved = new Map();
  for (const conflict of approvedConflicts) {
    if (
      conflict
      && typeof conflict.targetPath === "string"
      && typeof conflict.digest === "string"
    ) {
      approved.set(path.resolve(conflict.targetPath), conflict.digest);
    }
  }
  return approved;
}

function assertPlanApproved(plan, approvedConflicts) {
  const approved = approvedMap(approvedConflicts);
  const unresolved = plan.conflicts.filter((conflict) =>
    !conflict.approvable
    || approved.get(path.resolve(conflict.targetPath)) !== conflict.digest
  );
  if (unresolved.length > 0) {
    throw new InstallConflictError(unresolved);
  }
}

function writeInstruction(plan) {
  const { tool, instruction } = plan;
  const targetPath = instruction.targetPath;
  const nextText = upsertInstructionBlock(
    instruction.existingText || readFileIfExists(targetPath),
    tool,
    instruction.sourceText
  );
  fs.writeFileSync(targetPath, nextText, "utf8");
}

function install(options) {
  // Purpose: install the complete current Skill set after a fresh preflight; Side effects: updates approved targets, removes owned retired targets, and writes the portable instruction block.
  const plan = inspectInstall(options);
  assertPlanApproved(plan, options.approvedConflicts || []);
  const summary = {
    action: "install",
    tool: plan.tool,
    mode: plan.mode,
    installed: 0,
    updated: 0,
    removed: 0,
    skipped: 0,
  };

  for (const target of plan.retiredTargets) {
    if (target.inspected.state === "absent") {
      continue;
    }
    const result = uninstallSkillTarget(target.targetPath, target.sourceDir, plan.tool);
    if (result === "skipped" && target.inspected.state === "managed-conflict") {
      const stat = fs.lstatSync(target.targetPath);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(target.targetPath);
      } else {
        fs.rmSync(target.targetPath, { recursive: true, force: true });
      }
      summary.removed += 1;
    } else {
      summary[result] += 1;
    }
  }
  for (const target of plan.skillTargets) {
    const result = plan.mode === "copy"
      ? installSkillCopy(target.sourceDir, target.targetPath, {
          source: target.sourceDir,
          mode: "copy",
          tool: plan.tool,
        })
      : installSkillLink(target.sourceDir, target.targetPath);
    summary[result] += 1;
  }
  writeInstruction(plan);
  return summary;
}

function removeInstruction(projectRoot, repoRoot, tool) {
  const targetPath = instructionPath(projectRoot, tool);
  const stat = lstatPath(targetPath);
  if (!stat || !stat.isFile() || stat.isSymbolicLink()) {
    return "skipped";
  }
  const existingText = fs.readFileSync(targetPath, "utf8");
  const block = hasUniqueInstructionBlock(existingText, tool)
    ? instructionBlock(existingText, tool)
    : null;
  if (!block || block !== wrapBlock(tool, readInstructionSource(repoRoot))) {
    return "skipped";
  }
  fs.writeFileSync(targetPath, removeInstructionBlock(existingText, tool), "utf8");
  return "removed";
}

function uninstall(options) {
  // Purpose: uninstall only unchanged, provably owned current and retired assets; modified copies, instruction blocks, and foreign targets remain untouched.
  const tool = options.tool;
  const projectRoot = options.projectRoot || resolveProjectRoot();
  const repoRoot = options.repoRoot || resolveHelloScholarRoot();
  const skills = discoverSkills(repoRoot);
  const config = TOOL_CONFIG[tool];
  const names = [...new Set([...skills.map((skill) => skill.name), ...RETIRED_SKILLS])];
  const sources = new Map(skills.map((skill) => [skill.name, skill.sourceDir]));

  const summary = { action: "uninstall", tool, removed: 0, skipped: 0 };
  if (inspectInstallParents(projectRoot, tool).length > 0) {
    summary.skipped = names.length + 1;
    return summary;
  }
  const instructionResult = removeInstruction(projectRoot, repoRoot, tool);
  summary[instructionResult] += 1;
  for (const name of names) {
    const targetDir = path.join(projectRoot, config.skillRoot, name);
    const sourceDir = sources.get(name) || path.join(repoRoot, "skills", name);
    const result = uninstallSkillTarget(targetDir, sourceDir, tool);
    summary[result] += 1;
  }
  return summary;
}

module.exports = {
  InstallConflictError,
  RETIRED_SKILLS,
  inspectInstall,
  install,
  uninstall,
};
