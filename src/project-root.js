const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");

function resolveProjectRoot(cwd = process.cwd()) {
  try {
    return execFileSync("git", ["rev-parse", "--show-toplevel"], {
      cwd,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return cwd;
  }
}

function resolveHelloScholarRoot(startDir = __dirname) {
  let current = startDir;
  while (true) {
    if (
      fs.existsSync(path.join(current, "skills")) &&
      fs.existsSync(path.join(current, "AGENTS.md"))
    ) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      throw new Error("Could not find hello-scholar repository root");
    }
    current = parent;
  }
}

module.exports = {
  resolveHelloScholarRoot,
  resolveProjectRoot,
};
