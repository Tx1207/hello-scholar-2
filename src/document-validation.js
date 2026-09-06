const SPEC_ID_PATTERN = /^SPEC-[0-9]{3,}$/;
const TOPIC_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;
const TIMESTAMP_PATTERN = /^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):(\d{2}))$/;

const REQUIRED_FIELDS = {
  spec: [
    "schema", "kind", "id", "title", "topic", "type", "status", "revision",
    "summary", "created", "updated", "supersedes", "superseded_by",
  ],
  record: [
    "schema", "kind", "run_id", "title", "status", "spec", "spec_revision",
    "started", "completed", "decision", "summary",
  ],
  architecture: ["schema", "kind", "status", "applies_to", "updated"],
};

const ENUMS = {
  specType: new Set(["research", "prototype", "capability", "system-design"]),
  specStatus: new Set(["draft", "accepted", "completed", "rejected", "withdrawn", "superseded"]),
  recordStatus: new Set(["planned", "running", "completed", "failed", "interrupted", "cancelled"]),
};

function classifyPath(relativePath) {
  // Purpose: map a canonical project-relative path to its document role; Input: relative path; Output: location metadata or null.
  if (relativePath === "hello-scholar/architecture.md") {
    return { kind: "architecture" };
  }

  let match = relativePath.match(
    /^hello-scholar\/specs\/([^/]+)\/([^/]+)\/(spec)\.md$/
  );
  if (match) {
    return {
      kind: match[3],
      topic: match[1],
      bundleName: match[2],
      bundlePath: `hello-scholar/specs/${match[1]}/${match[2]}`,
    };
  }

  match = relativePath.match(/^runs\/([^/]+)\/record\.md$/);
  if (match) {
    return { kind: "record", runId: match[1] };
  }
  return null;
}

function isNonemptyString(value) {
  // Purpose: test required textual metadata; Input: unknown value; Output: true for a nonblank string.
  return typeof value === "string" && value.trim() !== "";
}

function isPositiveInteger(value) {
  // Purpose: test revision-style integers; Input: unknown value; Output: true for an integer greater than zero.
  return Number.isInteger(value) && value > 0;
}

function isDate(value) {
  // Purpose: validate a real YYYY-MM-DD calendar date; Input: unknown value; Output: true for a valid canonical date.
  if (typeof value !== "string") {
    return false;
  }
  const match = value.match(DATE_PATTERN);
  if (!match) {
    return false;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return parsed.getUTCFullYear() === year
    && parsed.getUTCMonth() === month - 1
    && parsed.getUTCDate() === day;
}

function isTimestamp(value) {
  // Purpose: validate an ISO timestamp with timezone and real date/time fields; Input: unknown value; Output: true for a supported timestamp.
  if (typeof value !== "string") {
    return false;
  }
  const match = value.match(TIMESTAMP_PATTERN);
  if (!match || !isDate(match[1])) {
    return false;
  }
  const hour = Number(match[2]);
  const minute = Number(match[3]);
  const second = Number(match[4]);
  const offsetHour = match[5] === undefined ? 0 : Number(match[5]);
  const offsetMinute = match[6] === undefined ? 0 : Number(match[6]);
  return hour <= 23
    && minute <= 59
    && second <= 59
    && offsetHour <= 23
    && offsetMinute <= 59
    && Number.isFinite(Date.parse(value));
}

function diagnostic(code, path, message) {
  // Purpose: create one normalized validation diagnostic; Input: code, path, and message; Output: diagnostic object.
  return { code, path, message };
}

function sortDiagnostics(values) {
  // Purpose: order diagnostics deterministically; Input: diagnostic array; Output: none; Side effects: sorts the input array in place.
  values.sort((left, right) =>
    left.path.localeCompare(right.path)
    || left.code.localeCompare(right.code)
    || left.message.localeCompare(right.message)
  );
}

function validateDocumentSet(discoveryResult) {
  // Purpose: validate the complete discovered document graph; Input: discovery inventory; Output: errors, notices, normalized Specs, Records, and Architecture.
  const errors = [];
  const notices = [];
  const addError = (code, path, message) => {
    // Purpose: append one validation error; Input: code, path, and message; Output: updated error count; Side effects: mutates the error list.
    return errors.push(diagnostic(code, path, message));
  };
  const addNotice = (code, path, message) => {
    // Purpose: append one validation notice; Input: code, path, and message; Output: updated notice count; Side effects: mutates the notice list.
    return notices.push(diagnostic(code, path, message));
  };

  for (const relativePath of discoveryResult.legacyPaths || []) {
    addNotice("legacy-path", relativePath, "legacy hello-scholar path requires reviewed migration");
  }
  const historicalPaths = new Set(discoveryResult.historicalPaths || []);
  for (const relativePath of historicalPaths) {
    const label = relativePath.endsWith("/plan.md") ? "Plan" : "Tasks";
    addNotice(
      "historical-document",
      relativePath,
      `historical ${label} is not part of the current document model`
    );
  }
  for (const relativePath of discoveryResult.misplacedPaths || []) {
    addError("misplaced-document", relativePath, "core document is outside its required path");
  }
  for (const relativePath of discoveryResult.forbiddenRunDocuments || []) {
    addError("forbidden-run-document", relativePath, "a Run may contain only record.md as its core description");
  }
  for (const unsafe of discoveryResult.unsafePaths || []) {
    const relativePath = typeof unsafe === "string" ? unsafe : unsafe.relativePath;
    const reason = typeof unsafe === "string" ? "unsafe filesystem node" : unsafe.reason;
    addError("unsafe-path", relativePath, reason || "unsafe filesystem node");
  }

  const documents = [...(discoveryResult.documents || [])].sort((left, right) =>
    left.relativePath.localeCompare(right.relativePath)
  );
  const seenPaths = new Set();
  const typed = [];

  for (const current of documents) {
    const relativePath = current.relativePath;
    if (seenPaths.has(relativePath)) {
      addError("duplicate-document-path", relativePath, "document path appears more than once");
    }
    seenPaths.add(relativePath);

    const location = classifyPath(relativePath);
    if (!location) {
      addError("misplaced-document", relativePath, "document path does not identify a core document");
      continue;
    }

    const attributes = current.attributes || {};
    if (attributes.kind !== location.kind) {
      addError(
        "kind-path-mismatch",
        relativePath,
        `path requires kind ${location.kind}, found ${String(attributes.kind)}`
      );
    }
    validateFields(location.kind, attributes, relativePath, addError);
    validatePathIdentity(location, attributes, relativePath, addError);
    typed.push({ document: current, attributes, location });
  }

  const specEntries = typed.filter((entry) => entry.location.kind === "spec");
  const recordEntries = typed.filter((entry) => entry.location.kind === "record");
  const architectureEntries = typed.filter((entry) => entry.location.kind === "architecture");

  const specsById = new Map();
  for (const entry of specEntries) {
    const id = entry.attributes.id;
    if (!isNonemptyString(id)) {
      continue;
    }
    if (specsById.has(id)) {
      addError("duplicate-spec-id", entry.document.relativePath, `Spec ID ${id} is not globally unique`);
    } else {
      specsById.set(id, entry);
    }
  }

  const specs = specEntries.map((specEntry) => {
    const spec = specEntry.attributes;

    return {
      id: spec.id,
      title: spec.title,
      topic: spec.topic,
      type: spec.type,
      status: spec.status,
      revision: spec.revision,
      summary: spec.summary,
      created: spec.created,
      updated: spec.updated,
      supersedes: Array.isArray(spec.supersedes) ? [...spec.supersedes] : [],
      supersededBy: spec.superseded_by,
      relativePath: specEntry.document.relativePath,
      attributes: { ...spec },
      body: specEntry.document.body,
    };
  }).sort(compareSpecs);

  validateSpecRelations(specEntries, specsById, addError);

  const records = recordEntries.map((entry) => {
    validateRecordAssociation(entry, specsById, historicalPaths, addError, addNotice);
    const attributes = entry.attributes;
    return {
      runId: attributes.run_id,
      title: attributes.title,
      status: attributes.status,
      spec: attributes.spec,
      specRevision: attributes.spec_revision,
      ...(attributes.schema === 1 ? { planRevision: attributes.plan_revision } : {}),
      started: attributes.started,
      completed: attributes.completed,
      decision: attributes.decision,
      summary: attributes.summary,
      relativePath: entry.document.relativePath,
      attributes: { ...attributes },
      body: entry.document.body,
    };
  }).sort((left, right) => String(left.runId).localeCompare(String(right.runId)));

  let architecture = null;
  if (architectureEntries.length === 0) {
    addNotice(
      "architecture-missing",
      "hello-scholar/architecture.md",
      "Architecture document is missing"
    );
  } else {
    architecture = copyDocument(architectureEntries[0].document);
    for (const extra of architectureEntries.slice(1)) {
      addError(
        "duplicate-architecture",
        extra.document.relativePath,
        "project may contain at most one Architecture document"
      );
    }
    const architectureDate = architectureEntries[0].attributes.updated;
    for (const entry of specEntries) {
      if (
        entry.attributes.status === "completed"
        && isDate(entry.attributes.updated)
        && isDate(architectureDate)
        && entry.attributes.updated > architectureDate
      ) {
        addNotice(
          "architecture-drift-candidate",
          architectureEntries[0].document.relativePath,
          `Completed ${String(entry.attributes.id)} is newer than Architecture`
        );
      }
    }
  }

  sortDiagnostics(errors);
  sortDiagnostics(notices);
  return { errors, notices, specs, records, architecture };
}

function validateFields(kind, attributes, relativePath, addError) {
  // Purpose: dispatch required and kind-specific metadata checks; Input: document kind, attributes, path, and error sink; Output: none; Side effects: appends errors.
  const requiredFields = kind === "record" && attributes.schema === 1
    ? [...REQUIRED_FIELDS.record, "plan_revision"]
    : REQUIRED_FIELDS[kind];
  for (const field of requiredFields) {
    if (!Object.prototype.hasOwnProperty.call(attributes, field)) {
      addError("missing-field", relativePath, `${kind} requires field ${field}`);
    }
  }

  if (Object.prototype.hasOwnProperty.call(attributes, "schema")) {
    const supported = kind === "record"
      ? attributes.schema === 1 || attributes.schema === 2
      : attributes.schema === 1;
    if (!supported) {
      addError(
        "invalid-schema",
        relativePath,
        kind === "record" ? "Record schema must be integer 1 or 2" : "schema must be integer 1"
      );
    }
  }

  if (kind === "spec") {
    validateSpecFields(attributes, relativePath, addError);
  } else if (kind === "record") {
    validateRecordFields(attributes, relativePath, addError);
  } else {
    validateArchitectureFields(attributes, relativePath, addError);
  }
}

function validateSpecFields(attributes, path, addError) {
  // Purpose: validate Spec metadata types and relations; Input: attributes, path, and error sink; Output: none; Side effects: appends errors.
  validateSpecId(attributes.id, "id", path, addError);
  validateStringFields(attributes, ["title", "topic", "summary"], path, addError);
  if (Object.prototype.hasOwnProperty.call(attributes, "topic")
      && (!isNonemptyString(attributes.topic) || !TOPIC_PATTERN.test(attributes.topic))) {
    addError("invalid-topic", path, "topic must be lowercase kebab-case");
  }
  validateEnum(attributes.type, ENUMS.specType, "type", path, addError);
  validateEnum(attributes.status, ENUMS.specStatus, "status", path, addError);
  validatePositiveInteger(attributes.revision, "revision", path, addError);
  validateDateFields(attributes, ["created", "updated"], path, addError);

  if (Object.prototype.hasOwnProperty.call(attributes, "supersedes")) {
    if (!Array.isArray(attributes.supersedes)
        || attributes.supersedes.some((value) => !SPEC_ID_PATTERN.test(value))) {
      addError("invalid-spec-relations", path, "supersedes must be an array of Spec IDs");
    } else if (new Set(attributes.supersedes).size !== attributes.supersedes.length) {
      addError("duplicate-spec-relation", path, "supersedes may not repeat a Spec ID");
    }
  }
  if (Object.prototype.hasOwnProperty.call(attributes, "superseded_by")
      && attributes.superseded_by !== null
      && (typeof attributes.superseded_by !== "string"
        || !SPEC_ID_PATTERN.test(attributes.superseded_by))) {
    addError("invalid-spec-relations", path, "superseded_by must be a Spec ID or null");
  }
}

function validateRecordFields(attributes, path, addError) {
  // Purpose: validate Run Record associations and lifecycle timestamps; Input: attributes, path, and error sink; Output: none; Side effects: appends errors.
  validateStringFields(attributes, ["run_id", "title", "decision", "summary"], path, addError);
  validateEnum(attributes.status, ENUMS.recordStatus, "status", path, addError);

  if (attributes.schema === 2 && Object.prototype.hasOwnProperty.call(attributes, "plan_revision")) {
    addError("unexpected-record-field", path, "schema 2 Record must not contain plan_revision");
  }

  const association = attributes.schema === 1
    ? [attributes.spec, attributes.spec_revision, attributes.plan_revision]
    : [attributes.spec, attributes.spec_revision];
  const allNull = association.every((value) => value === null);
  const allPresent = association.every((value) => value !== null && value !== undefined);
  if (!allNull && !allPresent) {
    addError(
      "partial-record-association",
      path,
      attributes.schema === 1
        ? "schema 1 Record requires spec, spec_revision, and plan_revision to be all set or all null"
        : "spec and spec_revision must be both set or both null"
    );
  } else if (allPresent) {
    validateSpecId(attributes.spec, "spec", path, addError);
    validatePositiveInteger(attributes.spec_revision, "spec_revision", path, addError);
    if (attributes.schema === 1) {
      validatePositiveInteger(attributes.plan_revision, "plan_revision", path, addError);
    }
  }

  for (const field of ["started", "completed"]) {
    const value = attributes[field];
    if (value !== null && value !== undefined && !isTimestamp(value)) {
      addError("invalid-timestamp", path, `${field} must be a timezone-qualified ISO 8601 timestamp or null`);
    }
  }

  const status = attributes.status;
  const startedValid = isTimestamp(attributes.started);
  const completedValid = isTimestamp(attributes.completed);
  if (status === "planned" && (attributes.started !== null || attributes.completed !== null)) {
    addError("invalid-record-lifecycle", path, "planned Record requires null started and completed");
  } else if (status === "running" && (!startedValid || attributes.completed !== null)) {
    addError("invalid-record-lifecycle", path, "running Record requires started and null completed");
  } else if (status === "cancelled" && attributes.schema === 2) {
    // A planned Run can be cancelled without inventing a process start.
    if ((!startedValid && attributes.started !== null) || !completedValid) {
      addError("invalid-record-lifecycle", path, "cancelled Record requires null or valid started and a valid completed time");
    }
  } else if (["completed", "failed", "interrupted", "cancelled"].includes(status)
      && (!startedValid || !completedValid)) {
    addError("invalid-record-lifecycle", path, `${status} Record requires started and completed`);
  }
  if (startedValid && completedValid && Date.parse(attributes.completed) < Date.parse(attributes.started)) {
    addError("record-time-order", path, "completed may not be earlier than started");
  }
}

function validateArchitectureFields(attributes, path, addError) {
  // Purpose: validate current Architecture metadata; Input: attributes, path, and error sink; Output: none; Side effects: appends errors.
  validateEnum(attributes.status, new Set(["current"]), "status", path, addError);
  validateStringFields(attributes, ["applies_to"], path, addError);
  validateDateFields(attributes, ["updated"], path, addError);
}

function validatePathIdentity(location, attributes, path, addError) {
  // Purpose: enforce agreement between document path and metadata identity; Input: location, attributes, path, and error sink; Output: none; Side effects: appends errors.
  if (location.kind === "spec") {
    if (isNonemptyString(attributes.topic) && attributes.topic !== location.topic) {
      addError(
        "topic-path-mismatch",
        path,
        `Spec topic ${attributes.topic} does not match directory ${location.topic}`
      );
    }
    if (isNonemptyString(attributes.id)
        && location.bundleName !== attributes.id
        && !location.bundleName.startsWith(`${attributes.id}-`)) {
      addError(
        "bundle-id-mismatch",
        path,
        `Bundle directory ${location.bundleName} does not start with ${attributes.id}`
      );
    }
  } else if (location.kind === "record"
      && isNonemptyString(attributes.run_id)
      && attributes.run_id !== location.runId) {
    addError(
      "run-id-path-mismatch",
      path,
      `run_id ${attributes.run_id} does not match directory ${location.runId}`
    );
  }
}

function validateSpecId(value, field, path, addError) {
  // Purpose: validate one stable Spec identifier; Input: value, field, path, and error sink; Output: none; Side effects: appends errors.
  if (value !== undefined
      && (typeof value !== "string" || !SPEC_ID_PATTERN.test(value))) {
    addError("invalid-spec-id", path, `${field} must match SPEC-[0-9]{3,}`);
  }
}

function validateStringFields(attributes, fields, path, addError) {
  // Purpose: validate required nonblank strings; Input: attributes, field names, path, and error sink; Output: none; Side effects: appends errors.
  for (const field of fields) {
    if (Object.prototype.hasOwnProperty.call(attributes, field) && !isNonemptyString(attributes[field])) {
      addError("invalid-string", path, `${field} must be a non-empty string`);
    }
  }
}

function validatePositiveInteger(value, field, path, addError) {
  // Purpose: validate one positive-integer metadata field; Input: value, field, path, and error sink; Output: none; Side effects: appends errors.
  if (value !== undefined && !isPositiveInteger(value)) {
    addError("invalid-positive-integer", path, `${field} must be a positive integer`);
  }
}

function validateEnum(value, allowed, field, path, addError) {
  // Purpose: validate one enumerated metadata field; Input: value, allowed set, field, path, and error sink; Output: none; Side effects: appends errors.
  if (value !== undefined && !allowed.has(value)) {
    addError("invalid-enum", path, `${field} has unsupported value ${String(value)}`);
  }
}

function validateDateFields(attributes, fields, path, addError) {
  // Purpose: validate canonical date fields; Input: attributes, fields, path, and error sink; Output: none; Side effects: appends errors.
  for (const field of fields) {
    if (Object.prototype.hasOwnProperty.call(attributes, field) && !isDate(attributes[field])) {
      addError("invalid-date", path, `${field} must use YYYY-MM-DD`);
    }
  }
}

function validateSpecRelations(specEntries, specsById, addError) {
  // Purpose: validate reciprocal, acyclic Spec supersession links; Input: Spec entries, ID map, and error sink; Output: none; Side effects: appends relation errors.
  for (const entry of specEntries) {
    const sourceId = entry.attributes.id;
    if (!isNonemptyString(sourceId)) {
      continue;
    }
    const supersedes = Array.isArray(entry.attributes.supersedes)
      ? entry.attributes.supersedes
      : [];
    for (const targetId of supersedes) {
      if (targetId === sourceId) {
        addError("spec-self-reference", entry.document.relativePath, `${sourceId} cannot supersede itself`);
        continue;
      }
      const target = specsById.get(targetId);
      if (!target) {
        addError("missing-spec-reference", entry.document.relativePath, `${targetId} does not exist`);
      } else if (target.attributes.superseded_by !== sourceId) {
        addError(
          "inconsistent-spec-relation",
          entry.document.relativePath,
          `${targetId}.superseded_by must point back to ${sourceId}`
        );
      }
    }

    const successorId = entry.attributes.superseded_by;
    if (successorId === null || successorId === undefined) {
      continue;
    }
    if (successorId === sourceId) {
      addError("spec-self-reference", entry.document.relativePath, `${sourceId} cannot supersede itself`);
      continue;
    }
    const successor = specsById.get(successorId);
    if (!successor) {
      addError("missing-spec-reference", entry.document.relativePath, `${successorId} does not exist`);
    } else if (!Array.isArray(successor.attributes.supersedes)
        || !successor.attributes.supersedes.includes(sourceId)) {
      addError(
        "inconsistent-spec-relation",
        entry.document.relativePath,
        `${successorId}.supersedes must include ${sourceId}`
      );
    }
  }

  const state = new Map();
  const reported = new Set();
  function visit(id) {
    // Purpose: detect a supersession cycle with depth-first traversal; Input: current Spec ID; Output: none; Side effects: updates traversal state and appends errors.
    state.set(id, "visiting");
    const entry = specsById.get(id);
    const targets = Array.isArray(entry.attributes.supersedes) ? entry.attributes.supersedes : [];
    for (const targetId of targets) {
      if (!specsById.has(targetId) || targetId === id) {
        continue;
      }
      if (state.get(targetId) === "visiting") {
        const key = [id, targetId].sort().join(":");
        if (!reported.has(key)) {
          addError("spec-relation-cycle", entry.document.relativePath, `replacement relation contains a cycle through ${targetId}`);
          reported.add(key);
        }
      } else if (!state.has(targetId)) {
        visit(targetId);
      }
    }
    state.set(id, "visited");
  }
  for (const id of specsById.keys()) {
    if (!state.has(id)) {
      visit(id);
    }
  }
}

function validateRecordAssociation(entry, specsById, historicalPaths, addError, addNotice) {
  // Purpose: validate a Record's optional Spec association and schema 1 provenance; Input: Record, Spec map, historical paths, and sinks; Output: none; Side effects: appends errors or notices.
  const attributes = entry.attributes;
  const path = entry.document.relativePath;
  const association = attributes.schema === 1
    ? [attributes.spec, attributes.spec_revision, attributes.plan_revision]
    : [attributes.spec, attributes.spec_revision];
  if (association.every((value) => value === null)) {
    addNotice("unassociated-record", path, "Record is not associated with a Spec");
    return;
  }
  if (!association.every((value) => value !== null && value !== undefined)) {
    return;
  }

  const specEntry = specsById.get(attributes.spec);
  if (!specEntry) {
    addError("missing-record-spec", path, `Record references missing ${String(attributes.spec)}`);
    return;
  }
  if (isPositiveInteger(attributes.spec_revision)
      && isPositiveInteger(specEntry.attributes.revision)
      && attributes.spec_revision > specEntry.attributes.revision) {
    addError("future-spec-revision", path, "Record references a future Spec revision");
  }

  if (attributes.schema === 1) {
    const historicalPlanPath = `${specEntry.location.bundlePath}/plan.md`;
    if (!historicalPaths.has(historicalPlanPath)) {
      addNotice(
        "historical-plan-missing",
        path,
        `schema 1 Record references historical Plan revision ${String(attributes.plan_revision)}, but ${historicalPlanPath} is missing`
      );
    }
  }
}

function copyDocument(document) {
  // Purpose: expose stable document facts without parser-only body data; Input: discovered document; Output: normalized document descriptor.
  return {
    kind: document.kind,
    absolutePath: document.absolutePath,
    relativePath: document.relativePath,
    attributes: { ...(document.attributes || {}) },
    body: document.body,
  };
}

function compareSpecs(left, right) {
  // Purpose: order Specs by Topic, ID, and path; Input: two normalized Specs; Output: lexical comparison result.
  const topicOrder = String(left.topic).localeCompare(String(right.topic));
  if (topicOrder !== 0) {
    return topicOrder;
  }
  const leftNumber = Number(String(left.id).replace(/^SPEC-/, ""));
  const rightNumber = Number(String(right.id).replace(/^SPEC-/, ""));
  if (Number.isFinite(leftNumber) && Number.isFinite(rightNumber) && leftNumber !== rightNumber) {
    return leftNumber - rightNumber;
  }
  return String(left.id).localeCompare(String(right.id));
}

module.exports = {
  validateDocumentSet,
};
