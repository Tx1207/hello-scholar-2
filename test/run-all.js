const { spawnSync } = require("node:child_process");

function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.error && result.error.code === "ENOENT") {
    return false;
  }
  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
  return true;
}

function commandRuns(command, args) {
  const result = spawnSync(command, args, { stdio: "ignore" });
  return !result.error && result.status === 0;
}

run(process.execPath, ["--test", "test/test_*.js"]);

const pythonCommand = ["python3", "python"].find((command) => commandRuns(command, ["--version"]));

if (!pythonCommand) {
  console.error("Could not find python3 or python to run Python tests.");
  process.exit(1);
}

run(pythonCommand, ["-m", "unittest", "discover", "-s", "test"]);
