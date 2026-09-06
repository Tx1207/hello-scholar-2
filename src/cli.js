const readline = require("node:readline/promises");
const { stdin: defaultStdin, stdout: defaultStdout } = require("node:process");
const { checkDocs, syncDocs } = require("./docs");
const {
  InstallConflictError,
  inspectInstall,
  install,
  uninstall,
} = require("./install");
const { resolveProjectRoot } = require("./project-root");

function usageText() {
  // Purpose: render canonical CLI help; Input: none; Output: usage text.
  return [
    "hello-scholar",
    "",
    "Usage:",
    "  hello-scholar help",
    "  hello-scholar install codex|claude [--mode link|copy]",
    "  hello-scholar uninstall codex|claude",
    "  hello-scholar docs check",
    "  hello-scholar docs sync",
    "",
    "Defaults:",
    "  --mode link",
  ].join("\n");
}

function usageError() {
  // Purpose: create a consistent invalid-command error; Input: none; Output: Error carrying usage text.
  return new Error(usageText());
}

function parseArgs(args) {
  // Purpose: parse supported CLI actions and flags; Input: argv tokens after the executable; Output: normalized command; Errors: invalid combinations throw usage error.
  const [action, tool, flag, value, extra] = args;
  const tools = new Set(["codex", "claude"]);

  if (action === "help" && args.length === 1) {
    return { action: "help" };
  }

  if (action === "docs"
      && (tool === "check" || tool === "sync")
      && flag === undefined) {
    return { action, operation: tool };
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
  // Purpose: render install/uninstall counts; Input: operation summary; Output: one human-readable line.
  const parts = [];
  for (const key of ["installed", "updated", "removed", "skipped"]) {
    if (summary[key] !== undefined) {
      parts.push(`${key} ${summary[key]}`);
    }
  }
  return `${summary.action} ${summary.tool}: ${parts.join(", ")}`;
}

function compareStrings(left, right) {
  // Purpose: provide deterministic lexical ordering; Input: two strings; Output: negative, zero, or positive comparison result.
  if (left < right) {
    return -1;
  }
  if (left > right) {
    return 1;
  }
  return 0;
}

function sortedDiagnostics(values) {
  // Purpose: order CLI diagnostics without mutating callers; Input: diagnostic array; Output: sorted copy.
  return [...values].sort((left, right) =>
    compareStrings(left.path, right.path)
    || compareStrings(left.code, right.code)
    || compareStrings(left.message, right.message)
  );
}

function writeDocsResult(command, result, stdout) {
  // Purpose: print deterministic docs check/sync output; Input: parsed command, docs result, and output stream; Output: none; Side effects: writes to stdout.
  if (command.operation === "check") {
    stdout.write([
      "docs check:",
      `specs ${result.counts.specs},`,
      `records ${result.counts.records},`,
      `indexes ${result.counts.indexes},`,
      `errors ${result.errors.length},`,
      `notices ${result.notices.length}`,
    ].join(" ") + "\n");
    for (const entry of [...result.indexStates].sort((left, right) =>
      compareStrings(left.path, right.path) || compareStrings(left.state, right.state)
    )) {
      stdout.write(`index ${entry.state} ${entry.path}\n`);
    }
  } else {
    stdout.write([
      "docs sync:",
      `written ${result.writtenPaths.length},`,
      `deleted ${result.deletedPaths.length},`,
      `errors ${result.errors.length},`,
      `notices ${result.notices.length}`,
    ].join(" ") + "\n");
    for (const relativePath of [...result.writtenPaths].sort(compareStrings)) {
      stdout.write(`written ${relativePath}\n`);
    }
    for (const relativePath of [...result.deletedPaths].sort(compareStrings)) {
      stdout.write(`deleted ${relativePath}\n`);
    }
  }
  for (const notice of sortedDiagnostics(result.notices)) {
    stdout.write(`notice ${notice.code} ${notice.path}: ${notice.message}\n`);
  }
  for (const error of sortedDiagnostics(result.errors)) {
    stdout.write(`error ${error.code} ${error.path}: ${error.message}\n`);
  }
}

function writeInstallConflicts(conflicts, stdout) {
  // Purpose: print the complete deterministic preflight conflict set before any mutation; Side effects: writes to stdout.
  for (const conflict of [...conflicts].sort((left, right) => compareStrings(left.path, right.path))) {
    stdout.write(`conflict ${conflict.code} ${conflict.path}: ${conflict.message}\n`);
  }
}

async function confirmConflicts(conflicts, stdin, stdout) {
  // Purpose: obtain one explicit approval for the exact managed targets already listed; Output: true only for exact yes.
  stdout.write(`The ${conflicts.length} managed target${conflicts.length === 1 ? "" : "s"} listed above will be replaced.\n`);
  const rl = readline.createInterface({ input: stdin, output: stdout });
  try {
    const answer = await rl.question('Type "yes" to continue: ');
    return answer === "yes";
  } finally {
    rl.close();
  }
}

async function main(args, options = {}) {
  // Purpose: execute one hello-scholar CLI request; Input: argv tokens and optional adapters; Output: Promise<void>; Side effects: prints, reads confirmation, or mutates managed files and Indexes.
  const command = parseArgs(args);
  const stdin = options.stdin || defaultStdin;
  const stdout = options.stdout || defaultStdout;

  if (command.action === "help") {
    stdout.write(`${usageText()}\n`);
    return;
  }

  const projectRoot = options.projectRoot || resolveProjectRoot();
  const repoRoot = options.repoRoot;

  if (command.action === "docs") {
    const result = command.operation === "check"
      ? checkDocs({ projectRoot })
      : syncDocs({ projectRoot });
    writeDocsResult(command, result, stdout);
    if (result.errors.length > 0) {
      const noun = result.errors.length === 1 ? "error" : "errors";
      throw new Error(`docs ${command.operation} failed with ${result.errors.length} ${noun}`);
    }
    return;
  }

  let summary;
  if (command.action === "install") {
    const plan = inspectInstall({
      tool: command.tool,
      mode: command.mode,
      projectRoot,
      repoRoot,
    });
    if (plan.conflicts.length > 0) {
      writeInstallConflicts(plan.conflicts, stdout);
      const unowned = plan.conflicts.filter((conflict) => !conflict.approvable);
      if (unowned.length > 0) {
        throw new InstallConflictError(plan.conflicts);
      }
      if (!(await confirmConflicts(plan.conflicts, stdin, stdout))) {
        stdout.write(`install ${command.tool} cancelled\n`);
        return;
      }
    }
    summary = install({
      tool: command.tool,
      mode: command.mode,
      projectRoot,
      repoRoot,
      approvedConflicts: plan.conflicts.map((conflict) => ({
        targetPath: conflict.targetPath,
        digest: conflict.digest,
      })),
    });
  } else {
    summary = uninstall({ tool: command.tool, projectRoot, repoRoot });
  }
  stdout.write(`${formatSummary(summary)}\n`);
}

module.exports = {
  formatSummary,
  main,
  parseArgs,
  usageText,
};
