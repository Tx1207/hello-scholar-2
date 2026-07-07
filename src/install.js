const fs = require("node:fs");
const path = require("node:path");
const { installSkillCopy, installSkillLink, uninstallSkillTarget } = require("./fs-ops");
const {
  hasInstructionBlock,
  removeInstructionBlock,
  upsertInstructionBlock,
} = require("./instruction-blocks");
const { resolveHelloScholarRoot, resolveProjectRoot } = require("./project-root");
const { discoverSkills } = require("./skill-discovery");

const TOOL_CONFIG = {
  codex: {
    instructionFile: "AGENTS.md",
    skillRoot: path.join(".agents", "skills"),
    sourceInstructionFile: "AGENTS.md",
  },
  claude: {
    instructionFile: "CLAUDE.md",
    skillRoot: path.join(".claude", "skills"),
    sourceInstructionFile: "CLAUDE.md",
  },
};

function readInstructionSource(repoRoot, tool) {
  const preferred = path.join(repoRoot, TOOL_CONFIG[tool].sourceInstructionFile);
  const fallback = path.join(repoRoot, "AGENTS.md");
  return fs.readFileSync(fs.existsSync(preferred) ? preferred : fallback, "utf8");
}

function readFileIfExists(filePath) {
  return fs.existsSync(filePath) ? fs.readFileSync(filePath, "utf8") : "";
}

function instructionPath(projectRoot, tool) {
  return path.join(projectRoot, TOOL_CONFIG[tool].instructionFile);
}

function hasExistingInstructionBlock(projectRoot, tool) {
  return hasInstructionBlock(readFileIfExists(instructionPath(projectRoot, tool)), tool);
}

function writeInstructionBlock(projectRoot, repoRoot, tool) {
  const targetPath = instructionPath(projectRoot, tool);
  const nextText = upsertInstructionBlock(
    readFileIfExists(targetPath),
    tool,
    readInstructionSource(repoRoot, tool)
  );
  fs.writeFileSync(targetPath, nextText, "utf8");
}

function removeInstruction(projectRoot, tool) {
  const targetPath = instructionPath(projectRoot, tool);
  if (!fs.existsSync(targetPath)) {
    return;
  }
  const nextText = removeInstructionBlock(fs.readFileSync(targetPath, "utf8"), tool);
  fs.writeFileSync(targetPath, nextText, "utf8");
}

function install(options) {
  const tool = options.tool;
  const mode = options.mode || "link";
  const projectRoot = options.projectRoot || resolveProjectRoot();
  const repoRoot = options.repoRoot || resolveHelloScholarRoot();
  const skills = discoverSkills(repoRoot);
  const config = TOOL_CONFIG[tool];

  const summary = { action: "install", tool, mode, installed: 0, updated: 0, skipped: 0 };
  for (const skill of skills) {
    const targetDir = path.join(projectRoot, config.skillRoot, skill.name);
    const result =
      mode === "copy"
        ? installSkillCopy(skill.sourceDir, targetDir, {
            source: skill.sourceDir,
            mode,
            tool,
          })
        : installSkillLink(skill.sourceDir, targetDir);
    summary[result] += 1;
  }
  writeInstructionBlock(projectRoot, repoRoot, tool);
  return summary;
}

function uninstall(options) {
  const tool = options.tool;
  const projectRoot = options.projectRoot || resolveProjectRoot();
  const repoRoot = options.repoRoot || resolveHelloScholarRoot();
  const skills = discoverSkills(repoRoot);
  const config = TOOL_CONFIG[tool];

  removeInstruction(projectRoot, tool);

  const summary = { action: "uninstall", tool, removed: 0, skipped: 0 };
  for (const skill of skills) {
    const targetDir = path.join(projectRoot, config.skillRoot, skill.name);
    const result = uninstallSkillTarget(targetDir, skill.sourceDir, tool);
    summary[result] += 1;
  }
  return summary;
}

module.exports = {
  hasExistingInstructionBlock,
  install,
  uninstall,
};
