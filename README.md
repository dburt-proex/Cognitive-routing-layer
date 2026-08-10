# Reasoning Control Plane

**Governs which analytical perspectives are applied before a recommendation, and proves it afterwards.**

The **Cognitive Routing Layer** is the executable component in this
repository: a deterministic router that selects, sequences, executes, and
audits versioned reasoning operators, then emits a machine-readable decision
receipt.

**Version:** 0.1.0 · **Stage:** v0.1 locked, pre-commercial-validation · **Runtime dependencies:** none

---

## What this is

A decision is made. Later, someone asks how. Model-level observability answers
which prompt ran and which tokens came back. It does not answer which
analytical perspectives were applied, what evidence supported them, what
contradicted them, or what was missing.

This system answers that, as a reproducible artifact.

Thirteen thinking modes — first-principles, systemic, divergent, abductive,
critical, inverted, second-order, convergent, metacognitive, and four deferred
— become versioned operators with enforced contracts. Not labels on prompts:
each operator declares required transformations that the engine mechanically
checks. A declared feedback loop must be an actual cycle in the declared
relation graph. Three "distinct" options must clear a token-similarity
threshold. A hypothesis must have a rival and a discriminating test.

**This system does not claim that prompting a model with a thinking label
makes it reason that way.** It asserts something narrower and checkable: the
artifact an operator produced has the structure its contract requires, or the
violation is on the record.

## Quickstart

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m cognitive_routing_layer.cli --run leverage-prioritization
```

Any fixture name, path, or directory works:

```bash
PYTHONPATH=src python -m cognitive_routing_layer.cli \
  --run confidence-does-not-authorize \
  --ledger /tmp/rcp-ledger.jsonl \
  --output /tmp/receipt.json \
  --verify-determinism
```

Exit codes: `0` for ALLOW or REVIEW, `1` for HALT, `2` for a run error.

Python 3.11+, standard library only. `jsonschema` is optional and used by one
cross-check test.

## The pipeline

```text
problem intake                  enforced schema, normalized, hashed
  ↓
task and signal classification  computed, never caller-declared
  ↓
reasoning-mode selection        deterministic, from a versioned policy
  ↓
operator execution              contract-enforced, sealed per stage
  ↓
evidence and contradiction gate ceilings, thresholds, structural detection
  ↓
option convergence              deterministic, or NO_RECOMMENDATION
  ↓
metacognitive audit             mandatory, four phases, cannot be waived
  ↓
recommendation                  ALLOW / REVIEW / HALT
  ↓
authorization gate              separate control, only when action is requested
  ↓
decision receipt                schema-validated, hash-linked
```

**Confidence never grants permission.** The authorization function accepts no
confidence, coverage, score, or gate argument — there is nothing it could read
to self-authorize. A test asserts its exact parameter list.

## Fixture outcomes

| Fixture | Class | Gate | Audit | Confidence | Execution |
|---|---|---|---|---:|---|
| `leverage-prioritization` | PRIORITIZATION | ALLOW | PASS | 0.75 | NOT_AUTHORIZED |
| `governance-decision` | GOVERNANCE_EVALUATION | REVIEW | PASS | 0.0 | REVIEW |
| `high-risk-code-change` | CHANGE_RISK | REVIEW | FAIL | 0.583 | REVIEW |
| `evidence-starved-convergence` | PRIORITIZATION | REVIEW | FAIL | 0.0 | REVIEW |
| `generated-option-wins` | PRIORITIZATION | ALLOW | PASS | 0.875 | NOT_AUTHORIZED |
| `confidence-does-not-authorize` | PRIORITIZATION | ALLOW | PASS | **1.0** | **NOT_AUTHORIZED** |
| `unsupported-classification` | UNSUPPORTED | REVIEW | FAIL | 0.0 | REVIEW |
| `boundary-halt` | PRIORITIZATION | HALT | PASS | 0.75 | HALT |

Row 5 proves exploration is load-bearing: a divergent-generated option is
evidence-sufficient and selected. Row 6 is the point: maximum confidence, clean
audit, `ALLOW` gate, irreversible action requested — still not authorized. Row 8
is its mirror: a clean audit and a well-evidenced option, and the run halts
anyway because a boundary flag outranks every score.

## The v0.1 operators

| Operator | Stage | Class | Required for |
|---|---|---|---|
| first-principles | FRAME | analysis | every class |
| systemic | FRAME | analysis | all but PRIORITIZATION |
| divergent | EXPLORE | analysis | PRIORITIZATION, DESIGN, STRATEGY |
| abductive | EXPLAIN | analysis | DIAGNOSTIC; elsewhere on `unexplained_observation` |
| critical | CHALLENGE | analysis | every class |
| inverted | CHALLENGE | analysis | GOVERNANCE_EVALUATION, CHANGE_RISK, DESIGN |
| second-order | FORECAST | analysis | all but DIAGNOSTIC |
| convergent | DECIDE | deterministic | every class |
| metacognitive | AUDIT | meta | **every class, mandatory** |

Deferred to v0.2: analogical, lateral, associative, Janusian — each with a
specific technical prerequisite recorded in `spec/operators.yaml`, not a vague
"later."

Convergence and the audit are computed, not generated. Those are the two places
where a persuasive narrative could quietly become a decision.

## Repository

```text
├── README.md
├── pyproject.toml
├── docs/
│   ├── opportunity-brief.md            verdict, challenged premise, locked boundary
│   ├── architecture.md                 pipeline, routing, placement decision
│   ├── integration-boundaries.md       the eight systems and their interfaces
│   ├── threat-and-failure-model.md     twelve threats, controls, recovery
│   └── product-interface.md            future UI spec; core stays independent
├── spec/
│   ├── operator-contract.md            what an operator is and how to add one
│   ├── operators.yaml                  nine contracts, eleven elements each
│   ├── routing-policy.yaml             classification, signals, routes, thresholds
│   └── metacognitive-audit.md          the mandatory audit
├── schemas/                            six JSON Schema documents
├── src/cognitive_routing_layer/        the engine
├── examples/                           three end-to-end receipts
├── tests/
│   ├── fixtures/                       eight runs
│   ├── test_acceptance.py              81 tests
│   └── acceptance-tests.md             results and criteria mapping
├── commercialization/
│   ├── positioning.md
│   └── offer-ladder.md
└── roadmap/
    └── v0.1-build-plan.md
```

Control files are JSON-compatible YAML, matching the
`operator-intelligence/leverage-engine` convention so a standard-library
runtime parses them without a YAML dependency.

## Ecosystem boundaries

This repository imports nothing from any sibling system. It reuses their
*vocabulary* — `ALLOW/REVIEW/HALT`, the `G4_*` boundary flags, the confidence
factors — so integration is a data contract, not a code dependency.

| System | Relationship |
|---|---|
| Operator Intelligence | Consumes receipts as evidence of reasoning coverage |
| PromptBP | Owns the instruction layer that will generate operator payloads |
| VIL | Supplies scored signals into the evidence register |
| Leverage Engine | Primary consumer: attaches a receipt to a directive |
| CASA | Authority for the authorization gate |
| DiffWall | Supplies change-risk evidence; may invoke RCP on high-risk changes |
| Mirdexx / Shared Decision Ledger | Durable retention of emitted receipts |

Full interface contracts in `docs/integration-boundaries.md`.

**This is not the ecosystem's decision store.** CASA, the Leverage Engine's
DecisionLedger, and Mirdexx already retain decisions. The local JSONL ledger
here exists for run-local receipt integrity and authorization replay
detection. The accurate claim is narrower: this may be the first component
dedicated to operator-level reasoning coverage and structured decision
receipts.

## Known limitations

Stated plainly, because a governance system that overstates itself is worse
than none:

1. **No authentic CASA verification.** The interface and all seven binding
   checks exist; the production verifier does not. The default returns
   `VERIFICATION_UNAVAILABLE` and routes to REVIEW.
2. **Evidence is declared, not verified.** Each record carries a
   `verification_state` that the engine records and never upgrades.
3. **Confidence is uncalibrated.** Labelled
   `uncalibrated_decision_support_score` in every receipt. No study relates
   these values to correctness.
4. **Contradiction detection is structural.** Same subject, opposing polarity.
   Semantic disagreement in different vocabulary is not detected, and the
   receipt says so.
5. **Intake field content is unattested.** Classification is computed honestly
   from the fields; the fields themselves are caller-supplied.
6. **Content quality is not assessed.** A well-formed shallow analysis passes
   every check.
7. **Commercially unvalidated.** No buyer has used this. The load-bearing
   assumption — that buyers pay for reasoning-level auditability rather than
   accepting model-level observability — is named and untested in
   `commercialization/positioning.md`.

## Privacy

Receipts contain structured conclusions, evidence references, assumptions,
contradictions, and rationale. They contain **no private chain-of-thought**.
Payload fields named `chain_of_thought`, `reasoning_trace`, `scratchpad`,
`internal_monologue`, or `thinking` are stripped and reported as a contract
violation.
