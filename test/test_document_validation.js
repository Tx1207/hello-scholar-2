const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { discoverDocuments } = require("../src/document-discovery");
const { validateDocumentSet } = require("../src/document-validation");

function document(relativePath, attributes, body = "# Document\n") {
  // Purpose: build one discovered-document fixture; Input: path, metadata, and body; Output: validation input document.
  return {
    kind: attributes.kind,
    absolutePath: `/fixture/${relativePath}`,
    relativePath,
    attributes,
    body,
  };
}

function discovery(documents, overrides = {}) {
  // Purpose: build a complete discovery fixture; Input: documents and collection overrides; Output: validation input inventory.
  return {
    documents,
    legacyPaths: [],
    historicalPaths: [],
    misplacedPaths: [],
    forbiddenRunDocuments: [],
    unsafePaths: [],
    indexPaths: [],
    ...overrides,
  };
}

function specAttributes(overrides = {}) {
  // Purpose: build valid schema 1 Spec metadata; Input: optional overrides; Output: attributes.
  return {
    schema: 1,
    kind: "spec",
    id: "SPEC-001",
    title: "Paged Cache",
    topic: "kv-cache",
    type: "research",
    status: "accepted",
    revision: 3,
    summary: "Remove fragmentation failures",
    created: "2026-07-20",
    updated: "2026-08-01",
    supersedes: [],
    superseded_by: null,
    ...overrides,
  };
}

function recordV1Attributes(overrides = {}) {
  // Purpose: build a valid historical schema 1 Record; Input: optional overrides; Output: attributes.
  return {
    schema: 1,
    kind: "record",
    run_id: "20260801-1430-paged-cache",
    title: "Block Size Comparison",
    status: "completed",
    spec: "SPEC-001",
    spec_revision: 2,
    plan_revision: 1,
    started: "2026-08-01T14:30:00+08:00",
    completed: "2026-08-01T16:42:00+08:00",
    decision: "adopt",
    summary: "Block size 16 wins",
    ...overrides,
  };
}

function recordV2Attributes(overrides = {}) {
  // Purpose: build a valid current schema 2 Record; Input: optional overrides; Output: attributes.
  return {
    schema: 2,
    kind: "record",
    run_id: "20260801-1430-paged-cache",
    title: "Block Size Comparison",
    status: "completed",
    spec: "SPEC-001",
    spec_revision: 2,
    started: "2026-08-01T14:30:00+08:00",
    completed: "2026-08-01T16:42:00+08:00",
    decision: "adopt",
    summary: "Block size 16 wins",
    ...overrides,
  };
}

function architectureAttributes(overrides = {}) {
  // Purpose: build valid schema 1 Architecture metadata; Input: optional overrides; Output: attributes.
  return {
    schema: 1,
    kind: "architecture",
    status: "current",
    applies_to: "main",
    updated: "2026-08-03",
    ...overrides,
  };
}

const bundle = "hello-scholar/specs/kv-cache/SPEC-001-paged-cache";

function errorCodes(result) {
  // Purpose: compare validation errors by stable code; Input: validation result; Output: set of codes.
  return new Set(result.errors.map((diagnostic) => diagnostic.code));
}

function noticeCodes(result) {
  // Purpose: compare validation notices by stable code; Input: validation result; Output: set of codes.
  return new Set(result.notices.map((diagnostic) => diagnostic.code));
}

test("accepts a Spec-only project without Plan or Tasks diagnostics", () => {
  const input = discovery([
    document(`${bundle}/spec.md`, specAttributes()),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ]);
  const before = structuredClone(input);

  const result = validateDocumentSet(input);

  assert.deepEqual(result.errors, []);
  assert.deepEqual(result.notices, []);
  assert.equal(result.specs.length, 1);
  assert.equal(result.specs[0].id, "SPEC-001");
  for (const obsoleteField of [
    "plan", "tasks", "planState", "tasksState", "completion", "approvalState", "tasksStatus",
  ]) {
    assert.equal(Object.hasOwn(result.specs[0], obsoleteField), false);
  }
  assert.equal(result.architecture.relativePath, "hello-scholar/architecture.md");
  assert.deepEqual(input, before, "validation must not mutate discovery results");
});

test("reports historical Plan and Tasks as notices without parsing them as core documents", () => {
  const result = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, specAttributes()),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ], {
    historicalPaths: [`${bundle}/tasks.md`, `${bundle}/plan.md`],
  }));

  assert.deepEqual(result.errors, []);
  assert.deepEqual(result.notices, [
    {
      code: "historical-document",
      path: `${bundle}/plan.md`,
      message: "historical Plan is not part of the current document model",
    },
    {
      code: "historical-document",
      path: `${bundle}/tasks.md`,
      message: "historical Tasks is not part of the current document model",
    },
  ]);
});

test("checks required fields, supported schemas, and fixed scalar types", () => {
  const missingSpec = specAttributes();
  delete missingSpec.title;
  const missingV1Record = recordV1Attributes();
  delete missingV1Record.plan_revision;
  const missingV2Record = recordV2Attributes();
  delete missingV2Record.summary;
  const result = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, missingSpec),
    document("runs/v1/record.md", { ...missingV1Record, run_id: "v1" }),
    document("runs/v2/record.md", { ...missingV2Record, run_id: "v2" }),
    document("hello-scholar/architecture.md", architectureAttributes({ status: "draft" })),
  ]));

  assert.ok(result.errors.some((error) => error.code === "missing-field" && error.message.includes("title")));
  assert.ok(result.errors.some((error) => error.code === "missing-field" && error.message.includes("plan_revision")));
  assert.ok(result.errors.some((error) => error.code === "missing-field" && error.message.includes("summary")));
  assert.ok(errorCodes(result).has("invalid-enum"));

  const schemas = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, specAttributes({ schema: 2 })),
    document("hello-scholar/architecture.md", architectureAttributes({ schema: 2 })),
    document("runs/unsupported/record.md", recordV2Attributes({ schema: 3, run_id: "unsupported" })),
    document("runs/obsolete/record.md", recordV2Attributes({ run_id: "obsolete", plan_revision: 1 })),
  ]));
  assert.ok(schemas.errors.filter((error) => error.code === "invalid-schema").length >= 3);
  assert.ok(errorCodes(schemas).has("unexpected-record-field"));
});

test("checks path identity, globally unique Spec IDs, and three-or-more digit IDs", () => {
  const result = validateDocumentSet(discovery([
    document("hello-scholar/specs/search/SPEC-999-search/spec.md", specAttributes({ id: "SPEC-999", topic: "search" })),
    document("hello-scholar/specs/search/SPEC-1000-search/spec.md", specAttributes({ id: "SPEC-1000", topic: "search" })),
    document("hello-scholar/specs/wrong-topic/SPEC-002-other/spec.md", specAttributes({ topic: "right-topic" })),
    document("hello-scholar/specs/duplicate/SPEC-001-duplicate/spec.md", specAttributes({ topic: "duplicate" })),
  ]));

  const codes = errorCodes(result);
  assert.ok(codes.has("duplicate-spec-id"));
  assert.ok(codes.has("topic-path-mismatch"));
  assert.ok(codes.has("bundle-id-mismatch"));
  assert.equal(result.errors.some((error) => error.message.includes("SPEC-999") && error.code === "invalid-spec-id"), false);
  assert.equal(result.errors.some((error) => error.message.includes("SPEC-1000") && error.code === "invalid-spec-id"), false);
});

test("validates Spec replacement references, reciprocity, missing IDs, and cycles", () => {
  const makeSpec = (id, topic, relations) => {
    // Purpose: build a related Spec fixture; Input: ID, topic, and relation overrides; Output: document.
    return document(
      `hello-scholar/specs/${topic}/${id}-${topic}/spec.md`,
      specAttributes({ id, topic, ...relations })
    );
  };
  const result = validateDocumentSet(discovery([
    makeSpec("SPEC-010", "alpha", { supersedes: ["SPEC-011"], superseded_by: "SPEC-011" }),
    makeSpec("SPEC-011", "beta", { supersedes: ["SPEC-010"], superseded_by: "SPEC-010" }),
    makeSpec("SPEC-012", "self", { supersedes: ["SPEC-012"] }),
    makeSpec("SPEC-013", "missing", { supersedes: ["SPEC-999"] }),
    makeSpec("SPEC-014", "one-way", { supersedes: ["SPEC-015"] }),
    makeSpec("SPEC-015", "target", {}),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ]));

  const codes = errorCodes(result);
  assert.ok(codes.has("spec-relation-cycle"));
  assert.ok(codes.has("spec-self-reference"));
  assert.ok(codes.has("missing-spec-reference"));
  assert.ok(codes.has("inconsistent-spec-relation"));
});

test("schema 2 Records use a paired optional Spec association without Plan metadata", () => {
  const associated = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, specAttributes()),
    document("runs/current/record.md", recordV2Attributes({ run_id: "current" })),
    document("runs/independent/record.md", recordV2Attributes({
      run_id: "independent", status: "planned", spec: null, spec_revision: null,
      started: null, completed: null, decision: "pending",
    })),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ]));

  assert.deepEqual(associated.errors, []);
  assert.ok(noticeCodes(associated).has("unassociated-record"));
  assert.equal(Object.hasOwn(associated.records[0], "planRevision"), false);

  const invalid = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, specAttributes()),
    document("runs/partial/record.md", recordV2Attributes({ run_id: "partial", spec_revision: null })),
    document("runs/future/record.md", recordV2Attributes({ run_id: "future", spec_revision: 4 })),
    document("runs/missing/record.md", recordV2Attributes({ run_id: "missing", spec: "SPEC-999" })),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ]));
  assert.ok(errorCodes(invalid).has("partial-record-association"));
  assert.ok(errorCodes(invalid).has("future-spec-revision"));
  assert.ok(errorCodes(invalid).has("missing-record-spec"));
});

test("schema 1 Records preserve Plan field validation but missing historical Plans are notices", () => {
  const recordPath = "runs/history/record.md";
  const withoutPlan = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, specAttributes()),
    document(recordPath, recordV1Attributes({ run_id: "history" })),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ]));
  assert.deepEqual(withoutPlan.errors, []);
  assert.ok(noticeCodes(withoutPlan).has("historical-plan-missing"));

  const withPlan = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, specAttributes()),
    document(recordPath, recordV1Attributes({ run_id: "history" })),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ], { historicalPaths: [`${bundle}/plan.md`] }));
  assert.deepEqual(withPlan.errors, []);
  assert.equal(noticeCodes(withPlan).has("historical-plan-missing"), false);
  assert.ok(noticeCodes(withPlan).has("historical-document"));
  assert.equal(withPlan.records[0].planRevision, 1);

  const invalidPlanRevision = validateDocumentSet(discovery([
    document(recordPath, recordV1Attributes({ run_id: "history", plan_revision: 0 })),
  ]));
  assert.ok(errorCodes(invalidPlanRevision).has("invalid-positive-integer"));
});

test("Record body organization does not change metadata validation or source text", () => {
  const attributes = recordV2Attributes({ decision: "do-not-adopt", summary: "81.2 below 82.0" });
  const bodies = [
    "## Execution Information\n\npython3 benchmark.py; exit 0.\n\n## Key Results\n\n81.2 below 82.0; do not adopt.\n",
    "## 运行与结论\n\npython3 benchmark.py; exit 0.\n\n81.2 below 82.0; do not adopt.\n",
  ];
  const results = bodies.map((body) => {
    const input = discovery([
      document(`${bundle}/spec.md`, specAttributes()),
      document(`runs/${attributes.run_id}/record.md`, attributes, body),
      document("hello-scholar/architecture.md", architectureAttributes()),
    ]);
    const before = structuredClone(input);
    const result = validateDocumentSet(input);
    assert.deepEqual(result.errors, []);
    assert.deepEqual(input, before);
    assert.equal(result.records[0].body, body);
    return result.records.map(({ body: recordBody, ...metadata }) => metadata);
  });
  assert.deepEqual(results[0], results[1]);

  const invalid = { ...attributes };
  delete invalid.started;
  const result = validateDocumentSet(discovery([
    document(`runs/${attributes.run_id}/record.md`, invalid, bodies[1]),
  ]));
  assert.ok(errorCodes(result).has("missing-field"));
  assert.ok(errorCodes(result).has("invalid-record-lifecycle"));
});

test("keeps stale Spec references and rejects invalid Record times", () => {
  const result = validateDocumentSet(discovery([
    document(`${bundle}/spec.md`, specAttributes()),
    document("runs/stale/record.md", recordV2Attributes({ run_id: "stale", spec_revision: 1 })),
    document("runs/backwards/record.md", recordV2Attributes({ run_id: "backwards", completed: "2026-08-01T13:30:00+08:00" })),
    document("runs/invalid-time/record.md", recordV2Attributes({ run_id: "invalid-time", started: "2026-02-30T14:30:00+08:00" })),
    document("runs/running/record.md", recordV2Attributes({ run_id: "running", status: "running", started: null, completed: null })),
    document("hello-scholar/architecture.md", architectureAttributes()),
  ]));

  assert.deepEqual(result.errors.filter((error) => error.path === "runs/stale/record.md"), []);
  assert.ok(errorCodes(result).has("invalid-record-lifecycle"));
  assert.ok(errorCodes(result).has("invalid-timestamp"));
  assert.ok(errorCodes(result).has("record-time-order"));
});

test("schema 2 supports cancellation before launch without weakening other terminal states", () => {
  const validate = (overrides = {}) => {
    const attributes = recordV2Attributes({
      status: "cancelled", started: null, spec: null, spec_revision: null,
      decision: "do-not-run", summary: "Cancelled before launch", ...overrides,
    });
    const input = discovery([document(`runs/${attributes.run_id}/record.md`, attributes)]);
    const before = structuredClone(input);
    const result = validateDocumentSet(input);
    assert.deepEqual(input, before);
    return result;
  };

  assert.deepEqual(validate().errors, []);
  assert.deepEqual(validate({ started: "2026-08-01T14:30:00+08:00" }).errors, []);
  for (const completed of [null, undefined, "not-a-time"]) {
    assert.ok(errorCodes(validate({ completed })).has("invalid-record-lifecycle"));
  }
  for (const started of [undefined, "not-a-time"]) {
    assert.ok(errorCodes(validate({ started })).has("invalid-record-lifecycle"));
  }
  for (const status of ["completed", "failed", "interrupted", "running"]) {
    assert.ok(errorCodes(validate({ status })).has("invalid-record-lifecycle"), status);
  }
  assert.ok(errorCodes(validate({
    started: "2026-08-01T18:00:00+08:00",
  })).has("record-time-order"));
  assert.ok(errorCodes(validate({
    schema: 1, plan_revision: null,
  })).has("invalid-record-lifecycle"));
});

test("validates discovered files without changing source or historical bytes", () => {
  const projectRoot = fs.mkdtempSync(path.join(os.tmpdir(), "hello-scholar-validation-"));
  const specPath = path.join(projectRoot, ...`${bundle}/spec.md`.split("/"));
  const planPath = path.join(projectRoot, ...`${bundle}/plan.md`.split("/"));
  try {
    fs.mkdirSync(path.dirname(specPath), { recursive: true });
    fs.writeFileSync(specPath, [
      "---", "schema: 1", "kind: spec", "id: SPEC-001", "title: Paged Cache",
      "topic: kv-cache", "type: research", "status: accepted", "revision: 3",
      "summary: Remove fragmentation failures", "created: 2026-07-20", "updated: 2026-08-01",
      "supersedes: []", "superseded_by: null", "---", "# Paged Cache", "",
    ].join("\n"), "utf8");
    fs.writeFileSync(planPath, "malformed historical Plan\n", "utf8");
    const before = new Map([[specPath, fs.readFileSync(specPath)], [planPath, fs.readFileSync(planPath)]]);

    const result = validateDocumentSet(discoverDocuments(projectRoot));

    assert.deepEqual(result.errors, []);
    assert.ok(noticeCodes(result).has("historical-document"));
    for (const [filePath, bytes] of before) {
      assert.deepEqual(fs.readFileSync(filePath), bytes);
    }
  } finally {
    fs.rmSync(projectRoot, { recursive: true, force: true });
  }
});

test("converts discovery safety, legacy, and misplaced findings into sorted diagnostics", () => {
  const result = validateDocumentSet(discovery([], {
    legacyPaths: ["hello-scholar/memory/specs/old.md"],
    historicalPaths: ["hello-scholar/specs/orphan/tasks.md"],
    misplacedPaths: ["hello-scholar/specs/orphan/spec.md"],
    forbiddenRunDocuments: ["runs/demo/README.md"],
    unsafePaths: [{ relativePath: "runs/linked", reason: "symbolic link or junction" }],
  }));

  assert.deepEqual(errorCodes(result), new Set(["forbidden-run-document", "misplaced-document", "unsafe-path"]));
  assert.deepEqual(noticeCodes(result), new Set(["architecture-missing", "historical-document", "legacy-path"]));
  assert.deepEqual(result.errors.map((diagnostic) => diagnostic.path), [
    "hello-scholar/specs/orphan/spec.md", "runs/demo/README.md", "runs/linked",
  ]);
});
