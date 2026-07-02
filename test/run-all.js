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

run(process.execPath, ["--test", "test/test_*.js"]);

if (!run("python3", ["-m", "unittest", "discover", "-s", "test"])) {
  if (!run("python", ["-m", "unittest", "discover", "-s", "test"])) {
    console.error("Could not find python3 or python to run Python tests.");
    process.exit(1);
  }
}
