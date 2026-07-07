const readline = require("node:readline/promises");
const { stdin: defaultStdin, stdout: defaultStdout } = require("node:process");
const { beginMarker, endMarker } = require("./instruction-blocks");
const { hasExistingInstructionBlock, install, uninstall } = require("./install");
const { resolveProjectRoot } = require("./project-root");

function usageText() {
  return [
    "hello-scholar",
    "",
    "Usage:",
    "  hello-scholar help",
    "  hello-scholar install codex|claude [--mode link|copy]",
    "  hello-scholar uninstall codex|claude",
    "",
    "Defaults:",
    "  --mode link",
  ].join("\n");
}

function usageError() {
  return new Error(usageText());
}

function parseArgs(args) {
  const [action, tool, flag, value, extra] = args;
  const tools = new Set(["codex", "claude"]);

  if (action === "help" && args.length === 1) {
    return { action: "help" };
  }

  if (action === "install") {
    if (!tools.has(tool) || extra !== undefined) {
      throw usageError();
    }
    if (flag === undefined) {
      return { action, tool, mode: "link" };
    }
    if (flag === "--mode" && (value === "link" || value === "copy")) {
      return { action, tool, mode: value };
    }
    throw usageError();
  }

  if (action === "uninstall") {
    if (!tools.has(tool) || flag !== undefined) {
      throw usageError();
    }
    return { action, tool };
  }

  throw usageError();
}

function formatSummary(summary) {
  const parts = [];
  for (const key of ["installed", "updated", "removed", "skipped"]) {
    if (summary[key] !== undefined) {
      parts.push(`${key} ${summary[key]}`);
    }
  }
  return `${summary.action} ${summary.tool}: ${parts.join(", ")}`;
}

function reinstallWarning(tool) {
  return [
    `hello-scholar is already installed for ${tool}.`,
    "Reinstalling will replace the content inside:",
    beginMarker(tool),
    "...",
    endMarker(tool),
    "",
    "Back up any manual edits inside that block before continuing.",
  ].join("\n");
}

async function confirmReinstall(tool, stdin, stdout) {
  stdout.write(`${reinstallWarning(tool)}\n`);
  const rl = readline.createInterface({ input: stdin, output: stdout });
  try {
    const answer = await rl.question('Type "yes" to continue: ');
    return answer === "yes";
  } finally {
    rl.close();
  }
}

async function main(args, options = {}) {
  const command = parseArgs(args);
  const stdin = options.stdin || defaultStdin;
  const stdout = options.stdout || defaultStdout;

  if (command.action === "help") {
    stdout.write(`${usageText()}\n`);
    return;
  }

  const projectRoot = options.projectRoot || resolveProjectRoot();
  const repoRoot = options.repoRoot;

  if (
    command.action === "install" &&
    hasExistingInstructionBlock(projectRoot, command.tool) &&
    !(await confirmReinstall(command.tool, stdin, stdout))
  ) {
    stdout.write(`install ${command.tool} cancelled\n`);
    return;
  }

  const summary =
    command.action === "install"
      ? install({ tool: command.tool, mode: command.mode, projectRoot, repoRoot })
      : uninstall({ tool: command.tool, projectRoot, repoRoot });
  stdout.write(`${formatSummary(summary)}\n`);
}

module.exports = {
  formatSummary,
  main,
  parseArgs,
  usageText,
};
