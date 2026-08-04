# Threat and Failure Model

**Version:** 0.1.0
**Stage:** v0.1 locked
**Folder alignment:** `docs/`

## What this system is defending

Not confidentiality, and not availability. The asset is **the trustworthiness
of the decision record**. Every threat below is a way of making a receipt say
something the run did not earn: that a perspective was applied when it was
not, that evidence supported a claim when it did not, that a contradiction was
absent when it was raised, or that an action was authorized when it was not.

## Threat model

### T1 — Classification downgrade

*An intake is labelled as a lower-scrutiny task class to obtain weaker
evidence thresholds.* `CHANGE_RISK` requires three distinct records across two
independent sources with at least one verified; `PRIORITIZATION` requires two
records from one source and no verification. Mislabelling buys that gap.

**Control.** Classification is computed from normalized intake. A caller's
`proposed_classification` is recorded, compared, and never honored. The
receipt carries `caller_proposal_mismatch` and the activated rule.
**Test.** `test_a_caller_cannot_choose_its_own_task_class`
**Residual.** The *content* of intake fields is caller-supplied. Declaring
`artifact_kind: none` for what is really a code change routes it as
prioritization. Field-level attestation is out of scope for v0.1 and is
recorded as an open risk.

### T2 — Evidence fabrication

*A claim cites evidence that does not exist, inheriting the confidence that
evidence would have bought.*

**Control.** Every `evidence_refs` entry is resolved against the run's evidence
register. Unresolvable references produce `GLOBAL-FABRICATION` and count as
unmet thresholds at convergence.
**Test.** `test_fabricated_evidence_references_are_caught`

### T3 — Confidence inflation

*An operator declares high confidence on thin evidence.*

**Control.** `effective_confidence = min(declared, evidence_ceiling)`. The
ceiling comes from distinct evidence count, mean quality against the
task-class minimum, and independence-group diversity. Declaring `high` on one
record yields 0.5.
**Test.** `test_declaring_high_confidence_on_thin_evidence_does_not_raise_it`,
`test_evidence_from_a_single_source_group_is_capped`

### T4 — Post-hoc justification

*Challenge operators are written after a decision to support it.*

**Control.** Stage order places `CHALLENGE` before `DECIDE`, and stage records
are append-only and hash-linked, so a later stage cannot edit an earlier one
without breaking the chain. The audit re-derives every hash.
**Test.** `test_the_audit_runs_last_and_challenge_precedes_decide`,
`test_mutating_a_sealed_stage_breaks_the_chain`, `test_a_relinked_chain_is_detected`

### T5 — Contradiction suppression

*An inconvenient opposing claim is removed before the audit.*

**Control.** Removing a claim changes sealed stage content; the recomputed
hash no longer matches and the audit reports `MC-CHAIN-CONTENT-MUTATED`.
Unresolved material contradictions force `REVIEW`. The `accepted_tension`
disposition requires a recorded human owner and can never be self-assigned.
**Test.** `test_a_contradiction_cannot_be_silently_removed`,
`test_contradictions_are_detected_and_severity_ranked`
**Residual.** Detection is structural. Two claims that disagree in different
vocabulary about differently-labelled subjects are not detected. The receipt
states the detection method so the boundary is visible.

### T6 — Authorization spoofing

*A forged, expired, replayed, or mis-scoped authorization is presented.*

**Control.** Seven binding checks: verifier signature, action hash, principal,
resource, receipt binding, expiry window, nonce freshness. Any failure is
`DENIED`. No verifier is `VERIFICATION_UNAVAILABLE`, never a silent pass.
**Tests.** `test_a_fabricated_casa_source_field_is_not_an_authorization`,
`test_an_expired_authorization_is_denied`,
`test_an_authorization_for_a_different_action_is_denied`,
`test_an_authorization_for_a_different_principal_is_denied`,
`test_an_authorization_bound_to_a_different_receipt_is_denied`,
`test_a_replayed_authorization_is_denied`
**Residual.** v0.1 has no authentic CASA verifier. The production default
fails closed. This is a stated gap, not a solved problem.

### T7 — Confidence used as permission

*A high-confidence recommendation is treated as authorization.*

**Control.** `evaluate` accepts no confidence, coverage, score, or gate
argument — there is nothing it could read. Execution composition requires both
an eligible recommendation and a verified authorization.
**Tests.** `test_the_authorization_gate_cannot_read_confidence`,
`test_confidence_cannot_grant_permission` (exhaustive over every gate result ×
sufficiency × non-authorized status), `test_scenario_5_high_confidence_does_not_authorize`

### T8 — Prompt injection through evidence

*Evidence text contains instructions aimed at the reader.*

**Control.** Evidence content is data, never instruction. Instruction-like text
is detected, flagged as `untrusted_instruction_detected`, and the record is
downgraded to `UNVERIFIED` with quality 0 — so it cannot satisfy a
verified-evidence threshold or contribute to a ceiling.
**Test.** `test_prompt_injection_inside_evidence_is_neutralised`
**Residual.** Pattern-based detection catches known phrasings, not novel ones.
The structural defence is stronger than the pattern list: the engine never
executes text found in a record, and no code path lets evidence content change
policy, routing, or authorization.

### T9 — Receipt tampering after issuance

*A stored receipt is edited to change what was recommended.*

**Control.** Every receipt is hashed on append. `verify_receipt` re-derives the
hash and reports a mismatch. The stage chain head anchors the run's internal
integrity independently.
**Test.** `test_receipt_tampering_after_issuance_is_detectable`

### T10 — Policy substitution

*A run executes against modified thresholds or an altered operator set.*

**Control.** Control files are validated on load and their SHA-256 checksums
are recorded in every receipt. The v0.1 operator set is locked in code:
removing or adding an operator fails registry validation. Version mismatch
between run input and policy halts the run.
**Tests.** `test_the_v01_operator_set_is_locked`,
`test_unknown_policy_version_halts_the_run`

### T11 — Silent route shortening

*A required operator is skipped and the run still produces a recommendation.*

**Control.** The audit's PLAN phase compares executed against planned
operators. A missing operator is a material finding, forces `REVIEW`, and
appears in `partial_execution`.
**Test.** `test_a_missing_required_operator_forces_review`

### T12 — Reasoning-theatre output

*An operator emits its thinking-mode label and generic prose that satisfies no
transformation.*

**Control.** Each operator's required transformations are mechanically checked:
feedback loops must be real cycles in the declared relation graph, options must
be distinct by token similarity, hypotheses must have rivals and discriminating
tests, effects must be second order or later with named antecedents, failure
modes must have preconditions and detection signals, defects must bind to
existing targets. There are fifteen adversarial tests in `ContractTests`, one
per failure condition.

## Failure and recovery

| Failure | Behavior | Recovery |
|---|---|---|
| Malformed intake | `IntakeError` before classification. No partial run record. | Correct the intake and resubmit |
| Unknown intake field | `IntakeError`. Unknown fields are never ignored. | Remove or add to the schema through a versioned change |
| Unknown policy or operator version | `RunError: RCP-FAIL-VERSION-UNKNOWN` | Pin the run to a published version |
| Operator payload fails schema | `GLOBAL-SCHEMA` violation; route continues; gate forces `REVIEW` | Fix the payload; the violation is on the record |
| Operator contract violation | Violation recorded on the stage record; route continues; `REVIEW` | Never silently dropped |
| Operator not supplied | `partial_execution` entry, `NOT_EXECUTED` stage record, audit material finding, `REVIEW` | Supply the operator and re-run |
| Malformed claim | `GLOBAL-CLAIM-MALFORMED`; the claim is not admitted to the run | Fix the claim |
| Stage hash mismatch | Audit material finding, `REVIEW`; the run is not trustworthy | Supersede with a new run |
| Ledger write failure | Receipt still returned, marked `persisted: false`; not eligible for downstream handoff | Retry the append |
| Ledger record-ID collision with different content | `LedgerError` | Investigate; two runs claimed one identity |
| Boundary flag | `HALT` at precedence 1, above everything | Human escalation |
| Unsupported classification | `REVIEW` with an explicit coverage gap; no route runs | Restate within a supported class, or extend the policy |

The engine's default direction under uncertainty is toward `REVIEW`, never
toward `ALLOW`. Every failure path above either stops the run or routes it to a
human.

## Known limitations

Stated plainly because a governance system that overstates itself is worse
than none:

1. **No authentic CASA verification.** The interface and binding checks exist;
   the production verifier does not. Default fails closed.
2. **Evidence is declared, not verified.** RCP records what a record claims
   about itself. It does not retrieve or authenticate sources.
3. **Confidence is uncalibrated.** No study relates these values to outcome
   correctness. They are labelled `uncalibrated_decision_support_score` in
   every receipt.
4. **Contradiction detection is structural.** Semantic disagreement in
   different vocabulary is not detected.
5. **Intake field content is caller-supplied.** Classification is computed
   from those fields honestly, but the fields themselves are unattested.
6. **Operator content quality is not assessed.** The engine checks that a
   payload has the required structure, not that its statements are insightful
   or correct. A well-formed shallow analysis passes.
7. **No timeout enforcement in v0.1.** The policy declares
   `operator_timeout_seconds` and the failure path, but the fixture adapter is
   synchronous and cannot time out. This activates with the model adapter.
