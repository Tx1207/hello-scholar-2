const fs = require("node:fs");
const path = require("node:path");
const { createHash, randomUUID } = require("node:crypto");

const INSTALL_MARKER = ".hello-scholar-install.json";

function ensureParent(targetPath) {
  // Purpose: ensure a target's parent directory exists; Input: target path; Output: none; Side effects: creates directories recursively.
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
}

function lstatPath(targetPath) {
  // Purpose: inspect a path without following its final link; Output: lstat or null for an absent node, including a dangling link's destination.
  try {
    return fs.lstatSync(targetPath);
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return null;
    }
    throw error;
  }
}

function resolvedLinkTarget(targetPath) {
  // Purpose: resolve link text lexically so dangling managed links remain identifiable; Output: absolute normalized destination.
  const linkText = fs.readlinkSync(targetPath);
  return path.resolve(path.dirname(targetPath), linkText);
}

function hashValue(value) {
  return createHash("sha256").update(value).digest("hex");
}

function directoryDigest(rootDir) {
  // Purpose: fingerprint installed Skill content independently of its ownership marker; Output: deterministic SHA-256 digest; Errors: propagates unreadable or unsupported nodes.
  const hash = createHash("sha256");

  function visit(directory, relativeDirectory) {
    for (const name of fs.readdirSync(directory).sort()) {
      if (relativeDirectory === "" && name === INSTALL_MARKER) {
        continue;
      }
      const absolutePath = path.join(directory, name);
      const relativePath = path.posix.join(relativeDirectory, name);
      const stat = fs.lstatSync(absolutePath);
      if (stat.isDirectory()) {
        hash.update(`directory\0${relativePath}\0`);
        visit(absolutePath, relativePath);
      } else if (stat.isFile()) {
        hash.update(`file\0${relativePath}\0`);
        hash.update(fs.readFileSync(absolutePath));
        hash.update("\0");
      } else if (stat.isSymbolicLink()) {
        hash.update(`link\0${relativePath}\0${fs.readlinkSync(absolutePath)}\0`);
      } else {
        throw new Error(`unsupported Skill entry: ${absolutePath}`);
      }
    }
  }

  visit(rootDir, "");
  return hash.digest("hex");
}

function installSkillLink(sourceDir, targetDir) {
  // Purpose: install one preflight-approved Skill symlink; Input: source and target directories; Output: install status; Side effects: replaces an existing approved target.
  ensureParent(targetDir);
  const stat = lstatPath(targetDir);
  if (stat) {
    if (stat.isSymbolicLink() && resolvedLinkTarget(targetDir) === path.resolve(sourceDir)) {
      return "updated";
    }
    if (stat.isSymbolicLink()) {
      fs.unlinkSync(targetDir);
    } else {
      fs.rmSync(targetDir, { recursive: true, force: true });
    }
  }
  const type = process.platform === "win32" ? "junction" : "dir";
  fs.symlinkSync(sourceDir, targetDir, type);
  return stat ? "updated" : "installed";
}

function copyDir(sourceDir, targetDir) {
  // Purpose: copy a Skill directory recursively; Input: source and target directories; Output: none; Side effects: creates target files.
  fs.cpSync(sourceDir, targetDir, {
    recursive: true,
    dereference: false,
    errorOnExist: false,
  });
}

function readOwnershipMarker(markerPath) {
  // Purpose: read a managed-target ownership marker when valid; Input: marker path; Output: parsed metadata or null; Side effects: reads filesystem.
  try {
    return JSON.parse(fs.readFileSync(markerPath, "utf8"));
  } catch {
    return null;
  }
}

function installSkillCopy(sourceDir, targetDir, metadata) {
  // Purpose: install one preflight-approved Skill copy and its baseline; Input: source, target, and ownership metadata; Output: install status; Side effects: replaces an existing approved target.
  const stat = lstatPath(targetDir);
  if (stat) {
    if (stat.isSymbolicLink()) {
      fs.unlinkSync(targetDir);
    } else {
      fs.rmSync(targetDir, { recursive: true, force: true });
    }
  }
  fs.mkdirSync(path.dirname(targetDir), { recursive: true });
  copyDir(sourceDir, targetDir);
  const baselineDigest = directoryDigest(sourceDir);
  fs.writeFileSync(
    path.join(targetDir, INSTALL_MARKER),
    `${JSON.stringify({ ...metadata, baselineDigest }, null, 2)}\n`,
    "utf8"
  );
  return stat ? "updated" : "installed";
}

function inspectSkillTarget(targetDir, sourceDir, tool) {
  // Purpose: classify one Skill target before any install mutation; Output: absent, managed-current, managed-clean, managed-conflict, or unowned with a concrete reason.
  const stat = lstatPath(targetDir);
  if (!stat) {
    return { state: "absent" };
  }
  const expectedSource = path.resolve(sourceDir);
  if (stat.isSymbolicLink()) {
    const actualSource = resolvedLinkTarget(targetDir);
    return actualSource === expectedSource
      ? { state: "managed-current", kind: "link" }
      : { state: "unowned", reason: `link points to ${actualSource}` };
  }
  if (!stat.isDirectory()) {
    return { state: "unowned", reason: "target is not a directory or symbolic link" };
  }

  const markerPath = path.join(targetDir, INSTALL_MARKER);
  const metadata = readOwnershipMarker(markerPath);
  if (
    !metadata
    || metadata.tool !== tool
    || metadata.mode !== "copy"
    || typeof metadata.source !== "string"
    || path.resolve(metadata.source) !== expectedSource
  ) {
    return { state: "unowned", reason: "copy ownership marker does not match this tool and source" };
  }
  const actualDigest = directoryDigest(targetDir);
  if (typeof metadata.baselineDigest !== "string") {
    return {
      state: "managed-conflict",
      kind: "copy",
      actualDigest,
      reason: "copy has no installation baseline",
    };
  }
  if (actualDigest !== metadata.baselineDigest) {
    return {
      state: "managed-conflict",
      kind: "copy",
      actualDigest,
      reason: "copy differs from its installation baseline",
    };
  }
  return { state: "managed-clean", kind: "copy", actualDigest };
}

function uninstallSkillTarget(targetDir, sourceDir, tool) {
  // Purpose: remove only a provably owned Skill target; Input: target, expected source, and tool; Output: removal status; Side effects: may delete owned link or copy.
  const inspected = inspectSkillTarget(targetDir, sourceDir, tool);
  if (inspected.state === "absent") {
    return "skipped";
  }
  if (inspected.state === "unowned" || inspected.state === "managed-conflict") {
    return "skipped";
  }
  const stat = fs.lstatSync(targetDir);
  if (stat.isSymbolicLink()) {
    fs.unlinkSync(targetDir);
  } else {
    fs.rmSync(targetDir, { recursive: true, force: true });
  }
  return "removed";
}

function lstatIfPresent(fileSystem, targetPath) {
  // Purpose: inspect an optional filesystem node without following links; Input: filesystem adapter and path; Output: lstat or null; Errors: propagates non-ENOENT failures.
  try {
    return fileSystem.lstatSync(targetPath);
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return null;
    }
    throw error;
  }
}

function resolveBatchTarget(projectRoot, relativePath) {
  // Purpose: resolve a validated batch-relative path inside a project; Input: project root and relative path; Output: absolute path; Errors: rejects absolute or escaping paths.
  if (
    typeof relativePath !== "string"
    || relativePath === ""
    || relativePath.includes("\\")
    || path.posix.isAbsolute(relativePath)
    || relativePath.split("/").includes("..")
  ) {
    throw new Error(`invalid batch path: ${String(relativePath)}`);
  }
  const absolutePath = path.resolve(projectRoot, ...relativePath.split("/"));
  const relative = path.relative(projectRoot, absolutePath);
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error(`batch path escapes project root: ${relativePath}`);
  }
  return absolutePath;
}

function inspectBatchTarget(fileSystem, projectRoot, relativePath) {
  // Purpose: validate an atomic-batch target and its ancestors; Input: adapter, root, and relative path; Output: absolute path and optional stat; Errors: rejects links and non-files.
  try {
    const absolutePath = resolveBatchTarget(projectRoot, relativePath);
    const segments = relativePath.split("/");
    let current = projectRoot;
    const rootStat = fileSystem.lstatSync(projectRoot);
    if (rootStat.isSymbolicLink() || !rootStat.isDirectory()) {
      throw new Error("unsafe batch root");
    }
    for (const segment of segments.slice(0, -1)) {
      current = path.join(current, segment);
      const stat = fileSystem.lstatSync(current);
      if (stat.isSymbolicLink() || !stat.isDirectory()) {
        throw new Error("unsafe parent path");
      }
    }
    const stat = lstatIfPresent(fileSystem, absolutePath);
    if (stat && (stat.isSymbolicLink() || !stat.isFile())) {
      throw new Error("unsafe target path");
    }
    return { absolutePath, stat };
  } catch (error) {
    const suffix = error && error.code ? ` (${error.code})` : "";
    throw new Error(`${relativePath}: cannot prepare batch target${suffix}`);
  }
}

function createExclusiveFile(fileSystem, directory, suffix, makeToken) {
  // Purpose: reserve a collision-free temporary or backup file; Input: adapter, directory, suffix, and token factory; Output: path and descriptor; Side effects: creates an exclusive file.
  for (let attempt = 0; attempt < 100; attempt += 1) {
    const candidate = path.join(
      directory,
      `.hello-scholar-index-${makeToken()}.${suffix}`
    );
    try {
      const descriptor = fileSystem.openSync(candidate, "wx", 0o666);
      return { path: candidate, descriptor };
    } catch (error) {
      if (error && error.code === "EEXIST") {
        continue;
      }
      throw error;
    }
  }
  throw new Error("could not allocate an exclusive batch file name");
}

function closeQuietly(fileSystem, descriptor) {
  // Purpose: close a best-effort descriptor during cleanup; Input: adapter and optional descriptor; Output: none; Side effects: closes descriptor and suppresses cleanup errors.
  if (descriptor === null || descriptor === undefined) {
    return;
  }
  try {
    fileSystem.closeSync(descriptor);
  } catch {
    // The original operation error remains the useful failure.
  }
}

function unlinkQuietly(fileSystem, targetPath) {
  // Purpose: remove an optional cleanup file; Input: adapter and optional path; Output: none; Side effects: unlinks file and suppresses cleanup errors.
  if (!targetPath) {
    return;
  }
  try {
    fileSystem.unlinkSync(targetPath);
  } catch (error) {
    if (!error || error.code !== "ENOENT") {
      throw error;
    }
  }
}

function applyAtomicFileBatch({
  projectRoot,
  writes,
  deletes,
  fileSystem = fs,
  makeToken = randomUUID,
}) {
  // Purpose: commit multiple file replacements/deletions with rollback; Input: root, write/delete sets, and adapters; Output: none; Side effects: atomically mutates target files; Errors: restores old bytes then rethrows.
  const rootPath = path.resolve(projectRoot);
  const writePaths = writes.map((item) => item.relativePath);
  const allPaths = [...writePaths, ...deletes];
  if (new Set(allPaths).size !== allPaths.length) {
    throw new Error("batch paths must be unique across writes and deletes");
  }

  const preparedWrites = writes.map((item) => ({
    ...item,
    ...inspectBatchTarget(fileSystem, rootPath, item.relativePath),
    tempPath: null,
    backupPath: null,
    originalContent: null,
  }));
  const preparedDeletes = deletes.map((relativePath) => ({
    relativePath,
    ...inspectBatchTarget(fileSystem, rootPath, relativePath),
    backupPath: null,
    originalContent: null,
  }));
  const applied = [];
  let currentPath = allPaths[0] || "<empty>";

  try {
    for (const item of preparedWrites) {
      currentPath = item.relativePath;
      const temporary = createExclusiveFile(
        fileSystem,
        path.dirname(item.absolutePath),
        "tmp",
        makeToken
      );
      item.tempPath = temporary.path;
      try {
        fileSystem.writeFileSync(temporary.descriptor, item.content, "utf8");
        fileSystem.fsyncSync(temporary.descriptor);
      } finally {
        closeQuietly(fileSystem, temporary.descriptor);
      }
    }

    for (const item of [...preparedWrites, ...preparedDeletes]) {
      if (!item.stat) {
        continue;
      }
      currentPath = item.relativePath;
      const backup = createExclusiveFile(
        fileSystem,
        path.dirname(item.absolutePath),
        "bak",
        makeToken
      );
      item.backupPath = backup.path;
      try {
        item.originalContent = fileSystem.readFileSync(item.absolutePath);
        fileSystem.writeFileSync(
          backup.descriptor,
          item.originalContent
        );
        if (typeof fileSystem.fchmodSync === "function") {
          fileSystem.fchmodSync(backup.descriptor, item.stat.mode & 0o777);
        }
        fileSystem.fsyncSync(backup.descriptor);
      } finally {
        closeQuietly(fileSystem, backup.descriptor);
      }
    }

    for (const item of preparedWrites) {
      currentPath = item.relativePath;
      fileSystem.renameSync(item.tempPath, item.absolutePath);
      item.tempPath = null;
      applied.push({ type: "write", item });
    }
    for (const item of preparedDeletes) {
      currentPath = item.relativePath;
      if (item.stat) {
        fileSystem.unlinkSync(item.absolutePath);
        applied.push({ type: "delete", item });
      }
    }
    for (const item of [...preparedWrites, ...preparedDeletes]) {
      currentPath = item.relativePath;
      unlinkQuietly(fileSystem, item.tempPath);
      item.tempPath = null;
      unlinkQuietly(fileSystem, item.backupPath);
      item.backupPath = null;
    }
  } catch (error) {
    const rollbackErrors = [];
    for (const operation of [...applied].reverse()) {
      const { item } = operation;
      try {
        const current = lstatIfPresent(fileSystem, item.absolutePath);
        if (current) {
          fileSystem.unlinkSync(item.absolutePath);
        }
        if (item.backupPath && lstatIfPresent(fileSystem, item.backupPath)) {
          fileSystem.renameSync(item.backupPath, item.absolutePath);
          item.backupPath = null;
        } else if (item.stat) {
          fileSystem.writeFileSync(item.absolutePath, item.originalContent, {
            flag: "wx",
            mode: item.stat.mode & 0o777,
          });
        }
      } catch (rollbackError) {
        rollbackErrors.push(`${item.relativePath}: ${rollbackError.message}`);
      }
    }
    for (const item of [...preparedWrites, ...preparedDeletes]) {
      try {
        unlinkQuietly(fileSystem, item.tempPath);
        unlinkQuietly(fileSystem, item.backupPath);
      } catch (cleanupError) {
        rollbackErrors.push(`${item.relativePath}: ${cleanupError.message}`);
      }
    }
    const rollbackSuffix = rollbackErrors.length === 0
      ? ""
      : `; rollback errors: ${rollbackErrors.join("; ")}`;
    throw new Error(`${currentPath}: ${error.message}${rollbackSuffix}`, { cause: error });
  }
}

module.exports = {
  applyAtomicFileBatch,
  directoryDigest,
  hashValue,
  inspectSkillTarget,
  installSkillCopy,
  installSkillLink,
  lstatPath,
  readOwnershipMarker,
  resolvedLinkTarget,
  uninstallSkillTarget,
};
