const fs = require("node:fs");
const path = require("node:path");

function ensureParent(targetPath) {
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
}

function sameRealPath(left, right) {
  try {
    return fs.realpathSync(left) === fs.realpathSync(right);
  } catch {
    return false;
  }
}

function installSkillLink(sourceDir, targetDir) {
  ensureParent(targetDir);
  if (fs.existsSync(targetDir)) {
    if (fs.lstatSync(targetDir).isSymbolicLink() && sameRealPath(targetDir, sourceDir)) {
      return "updated";
    }
    return "skipped";
  }
  const type = process.platform === "win32" ? "junction" : "dir";
  fs.symlinkSync(sourceDir, targetDir, type);
  return "installed";
}

function copyDir(sourceDir, targetDir) {
  fs.cpSync(sourceDir, targetDir, {
    recursive: true,
    dereference: false,
    errorOnExist: false,
  });
}

function readOwnershipMarker(markerPath) {
  try {
    return JSON.parse(fs.readFileSync(markerPath, "utf8"));
  } catch {
    return null;
  }
}

function installSkillCopy(sourceDir, targetDir, metadata) {
  if (fs.existsSync(targetDir)) {
    const marker = path.join(targetDir, ".hello-scholar-install.json");
    if (!fs.existsSync(marker)) {
      return "skipped";
    }
    const existingMetadata = readOwnershipMarker(marker);
    if (!existingMetadata || existingMetadata.tool !== metadata.tool) {
      return "skipped";
    }
    fs.rmSync(targetDir, { recursive: true, force: true });
  }
  fs.mkdirSync(path.dirname(targetDir), { recursive: true });
  copyDir(sourceDir, targetDir);
  fs.writeFileSync(
    path.join(targetDir, ".hello-scholar-install.json"),
    `${JSON.stringify(metadata, null, 2)}\n`,
    "utf8"
  );
  return "installed";
}

function uninstallSkillTarget(targetDir, sourceDir, tool) {
  if (!fs.existsSync(targetDir)) {
    return "skipped";
  }

  const stat = fs.lstatSync(targetDir);
  if (stat.isSymbolicLink()) {
    if (sameRealPath(targetDir, sourceDir)) {
      fs.rmSync(targetDir, { recursive: true, force: true });
      return "removed";
    }
    return "skipped";
  }

  const marker = path.join(targetDir, ".hello-scholar-install.json");
  if (!fs.existsSync(marker)) {
    return "skipped";
  }
  const metadata = readOwnershipMarker(marker);
  if (metadata && metadata.tool === tool) {
    fs.rmSync(targetDir, { recursive: true, force: true });
    return "removed";
  }
  return "skipped";
}

module.exports = {
  installSkillCopy,
  installSkillLink,
  uninstallSkillTarget,
};
