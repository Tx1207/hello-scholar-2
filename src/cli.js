const { install, uninstall } = require("./install");

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

async function main(args) {
  const command = parseArgs(args);
  if (command.action === "help") {
    console.log(usageText());
    return;
  }
  const summary =
    command.action === "install"
      ? install({ tool: command.tool, mode: command.mode })
      : uninstall({ tool: command.tool });
  console.log(formatSummary(summary));
}

module.exports = {
  formatSummary,
  main,
  parseArgs,
  usageText,
};
