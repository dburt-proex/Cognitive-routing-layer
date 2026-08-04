# Acceptance Tests

**Version:** 0.1.0
**Stage:** v0.1 acceptance gate
**Folder alignment:** `tests/`

## Running

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Zero exit code plus the fixture outcomes in the table below are the completion
evidence. Passing tests do not authorize a model adapter, a CASA integration,
or any commercial claim.

## Actual result

```text
Ran 81 tests in 0.776s

OK
```

Python 3.11.15, standard library only at runtime. `jsonschema` is used by one
cross-check test and skipped when absent.

| Suite | Tests | Covers |
|---|---:|---|
| `SpecificationTests` | 6 | Schema well-formedness, reference-implementation agreement, control-file format, contract completeness, locked operator set, mandatory audit |
| `ScenarioTests` | 8 | The five required scenarios plus unsupported classification, boundary HALT, and a no-private-reasoning sweep |
| `DeterminismTests` | 6 | Byte-identical replay, route reproducibility, selection rationale, ledger idempotency, receipt tamper detection, version pinning |
| `IntakeTests` | 5 | Malformed intake, unknown fields, thin statements, duplicate IDs, caller-supplied classification |
| `ContractTests` | 21 | One adversarial case per operator failure condition, plus schema and private-reasoning handling |
| `EvidenceTests` | 10 | Ceilings, independence caps, injection containment, contradiction detection and severity, missing-evidence enumeration, verification state, confidence labelling, generated-option ranking |
| `StageChainTests` | 4 | Chain integrity, content mutation, relinking, stage ordering |
| `AuthorizationTests` | 12 | The full authorization boundary |
| `RuntimeBoundaryTests` | 4 | No network or process execution, no dependencies, CLI exit codes, fixture references resolve |

## Fixture outcomes

| Fixture | Class | Depth | Gate | Audit | Selected | Confidence | Authorization | Execution |
|---|---|---:|---|---|---|---:|---|---|
| `leverage-prioritization` | PRIORITIZATION | 7 | ALLOW | PASS | OPT-A | 0.75 | NOT_REQUESTED | NOT_AUTHORIZED |
| `governance-decision` | GOVERNANCE_EVALUATION | 9 | REVIEW | PASS | none | 0.0 | NOT_REQUESTED | REVIEW |
| `high-risk-code-change` | CHANGE_RISK | 8 | REVIEW | FAIL | OPT-SCOPED | 0.583 | PENDING_CASA | REVIEW |
| `evidence-starved-convergence` | PRIORITIZATION | 6 | REVIEW | FAIL | none | 0.0 | NOT_REQUESTED | REVIEW |
| `confidence-does-not-authorize` | PRIORITIZATION | 8 | ALLOW | PASS | OPT-ROTATE | **1.0** | PENDING_CASA | **NOT_AUTHORIZED** |
| `unsupported-classification` | UNSUPPORTED | 0 | REVIEW | FAIL | none | 0.0 | NOT_REQUESTED | REVIEW |
| `boundary-halt` | PRIORITIZATION | 8 | HALT | PASS | OPT-AGGREGATE | 0.75 | NOT_REQUESTED | HALT |

Two rows carry most of the argument.

**`confidence-does-not-authorize`** is the authorization proof. Maximum
decision confidence, a clean audit, an `ALLOW` gate, and an irreversible action
requested. Execution is still `NOT_AUTHORIZED`. It flips to `MAY_PROCEED` only
when a verified authorization arrives bound to this exact recommendation, and
`AuthorizationTests` proves six separate ways that grant can be refused.

**`boundary-halt`** is the inverse. The audit passes, confidence reaches the
0.75 high-impact threshold, and a well-evidenced option is selected — and the
run still `HALT`s, because a boundary flag outranks every score at
conflict-resolution precedence 1. Sound analysis does not make a prohibited
action permissible.

## Required scenario coverage

| Required scenario | Fixture | Test |
|---|---|---|
| 1. Highest-leverage action from competing priorities | `leverage-prioritization` | `test_scenario_1_prioritization_produces_a_recommendation` |
| 2. Agent-governance proposal with incomplete evidence | `governance-decision` | `test_scenario_2_incomplete_evidence_blocks_convergence` |
| 3. High-risk change involving permissions and sensitive data | `high-risk-code-change` | `test_scenario_3_high_risk_change_surfaces_contradiction_and_pends_authorization` |
| 4. Divergent produces options, evidence cannot support convergence | `evidence-starved-convergence` | `test_scenario_4_options_without_evidence_cannot_converge` |
| 5. High confidence does not bypass authorization | `confidence-does-not-authorize` | `test_scenario_5_high_confidence_does_not_authorize` |

## Acceptance criteria

| Criterion | Status | Evidence |
|---|---|---|
| Every v0.1 operator has an explicit contract | Met | `test_every_v01_operator_carries_a_complete_contract` — all eleven elements, all transformations carry `verifiable_as` |
| Routing behavior is versioned and testable | Met | `spec/routing-policy.yaml` v0.1.0, checksummed into every receipt; `test_unknown_policy_version_halts_the_run` |
| Identical classification inputs produce a reproducible route | Met | `test_identical_classification_inputs_produce_the_same_route`, `test_identical_inputs_produce_byte_identical_receipts` across all seven fixtures |
| Evidence insufficiency and contradictions are surfaced | Met | `test_scenario_4_options_without_evidence_cannot_converge`, `test_contradictions_are_detected_and_severity_ranked`, `test_missing_evidence_is_enumerated_rather_than_absorbed` |
| Metacognitive audit is mandatory | Met | `test_the_metacognitive_audit_is_required_on_every_route`; `policy.py` rejects any route lacking it |
| Confidence cannot override authorization | Met | `test_confidence_cannot_grant_permission` exhausts gate × sufficiency × non-authorized status; `test_the_authorization_gate_cannot_read_confidence` asserts the exact parameter set |
| Three end-to-end fixtures produce decision receipts | Met | `examples/*.json`, three receipts, schema-validated, determinism-verified |
| System boundaries documented | Met | `docs/integration-boundaries.md`, all eight systems; no cross-repository imports |
| Commercial positioning is specific and defensible | Met | `commercialization/positioning.md` with supportable and prohibited claims separated, and the load-bearing assumption named as unvalidated |
| A new engineer can run the slice without clarification | Met | `README.md` quickstart; `docs/architecture.md` module map |

## Adversarial cases

Each mutates a known-good fixture to break exactly one control.

**Operator contracts (`ContractTests`)**

| Attack | Fires |
|---|---|
| Three restatements presented as distinct options | `DV-F2` |
| Divergent ranks an option | `DV-F5` |
| A feedback loop that is not a cycle in the declared graph | `SY-F4` |
| A relation referencing an undeclared component | `SY-F2` |
| Fewer than three primitives | `FP-F1` |
| A claim derived from a nonexistent primitive | `FP-F3` |
| An assumption relabelled `verified_fact` | `FP-F4` |
| A single hypothesis with no rival | `AB-F1` |
| Explaining an observation never supplied | `AB-F3` |
| A hypothesis with no discriminating test | `AB-F4` |
| A defect bound to a nonexistent target | `CR-F2` |
| A defect type outside the closed vocabulary | `GLOBAL-SCHEMA` + `CR-F1` |
| A failure mode with no detection signal | `IN-F4` |
| An irreversible failure mode with no boundary flag | `IN-F5` |
| A first-order effect relabelled second-order | `SO-F1` |
| A forecast bound to a nonexistent option | `SO-F3` |
| A forecast declaring high confidence | `GLOBAL-CONFIDENCE` |
| A fabricated evidence reference | `GLOBAL-FABRICATION` |
| A private reasoning field in the payload | `GLOBAL-COT`, content stripped |
| A required operator omitted | `MC-F1`, REVIEW, `partial_execution` |

**Authorization (`AuthorizationTests`)**

| Attack | Result |
|---|---|
| A field reading `issuer: casa` with a forged signature | `DENIED` |
| An expired authorization | `DENIED` on `expiry` |
| An authorization for a different action | `DENIED` on `action_binding` |
| An authorization for a different principal | `DENIED` on `principal_binding` |
| An authorization bound to a different receipt | `DENIED` on `receipt_binding` |
| A replayed nonce, correctly re-signed for a second run | `DENIED` on `replay` |
| A valid authorization with the default verifier | `VERIFICATION_UNAVAILABLE` |
| A valid test-adapter authorization | `AUTHORIZED`, `verifier_is_authentic: false` |
| Valid authorization, insufficient evidence | `REVIEW`, not `MAY_PROCEED` |
| Any non-`AUTHORIZED` status, any gate, any sufficiency | never authorized |

**Intake, evidence, and integrity**

| Attack | Result |
|---|---|
| Caller declares `PRIORITIZATION` on a code change | Computed `CHANGE_RISK`, mismatch recorded, stricter thresholds applied |
| Unknown intake field | `IntakeError` |
| Problem statement too thin to classify | `IntakeError` |
| Duplicate option IDs | `IntakeError` |
| Instruction text inside evidence | Flagged, downgraded to `UNVERIFIED`, quality 0 |
| Mutating sealed stage content | `MC-CHAIN-CONTENT-MUTATED` |
| Relinking the stage chain | `MC-CHAIN-LINK-BROKEN` + `MC-CHAIN-RECORD-MUTATED` |
| Editing a stored receipt | `verify_receipt` reports `intact: false` |
| Removing an operator from the registry | `PolicyError` |
| Running against a different policy version | `RunError` |

## What these tests do not prove

- That evidence cited by a claim is true. Only that it was declared and its
  verification state recorded.
- That confidence values predict correctness. No calibration study has run.
- That a CASA integration works. No authentic verifier exists; the default
  fails closed.
- That the reasoning was good. The checks confirm structural compliance. A
  well-formed shallow analysis passes.
- That the system is commercially validated. No buyer has used it.
