# Metacognitive Audit

**Version:** 0.1.0
**Stage:** v0.1 locked, mandatory
**Folder alignment:** `spec/`

## What it audits

The audit examines the run, not the problem. Every other operator produces a
view of the question; this one produces a verdict on whether the process that
answered the question met its own contract. It is the control that makes the
rest of the receipt worth reading.

It is mandatory on every route. `policy.py` rejects any routing policy in
which a task class does not require it, and it may not appear as a conditional
operator. `tests/test_acceptance.py::test_the_metacognitive_audit_is_required_on_every_route`
enforces this.

## Four phases

The phase structure follows the PLAN / MONITOR / EVALUATE / REFLECT model of
metacognition. Each phase here is a set of deterministic checks over a sealed
run record rather than a reflective prompt.

### PLAN — did the run do what the policy selected?

| Check | Finding |
|---|---|
| Executed operators equal planned operators | `MC-F1` |
| No operator executed outside the selected route | `MC-F1` |
| Route depth is at or above the policy minimum | `MC-F1` |

A required operator that did not execute is a material finding. There is no
path in which a route silently runs short.

### MONITOR — did each operator meet its contract?

| Check | Finding |
|---|---|
| No unresolved contract violation on any operator | `MC-F2` |
| Stage chain links are intact | `MC-CHAIN-LINK-BROKEN` |
| Sealed stage content still hashes to its recorded value | `MC-CHAIN-CONTENT-MUTATED` |
| Each stage record body still hashes to its record hash | `MC-CHAIN-RECORD-MUTATED` |

The chain checks are what make stage ordering a structural guarantee rather
than a convention. `CHALLENGE` running before `DECIDE` prevents challenge
operators from being written as post-hoc justification, but only if a later
stage cannot go back and edit an earlier one. Each stage record carries the
hash of its content and the hash of its predecessor, so a removed
contradiction, a softened assumption, or a deleted evidence reference breaks
the chain and surfaces here.

### EVALUATE — is confidence supported?

| Check | Finding |
|---|---|
| No claim's effective confidence exceeds its evidence ceiling | `MC-F3` |
| An evidence sufficiency threshold was applied at convergence | `MC-F3` |

### REFLECT — what is unresolved, and was the boundary respected?

| Check | Finding |
|---|---|
| Every contradiction carries a disposition | `MC-F4` |
| No material contradiction is left `unresolved` | `MC-F4` |
| No contradiction was self-assigned `accepted_tension` without a human owner | `MC-F4` |
| Authorization status was not derived from a confidence value | `MC-F5` |
| Missing evidence is enumerated | `MC-EVIDENCE-GAP` (minor) |

`accepted_tension` is the disposition that would let a run proceed with a
known contradiction on the record. The engine may never assign it in v0.1;
only a human with a recorded identity can. This is the specific hole through
which "we considered the objection and moved on" would otherwise become
automatic.

## Result and consequence

`audit_result` is `PASS` or `FAIL`. Any material finding produces `FAIL`.
Minor findings — currently the missing-evidence enumeration — are recorded and
do not fail the run.

A `FAIL` forces `REVIEW` at conflict-resolution precedence 2, above evidence
sufficiency, contradiction, and confidence. It cannot be waived, and there is
no code path that downgrades a material finding to make a run pass.

Only a boundary flag outranks the audit. A run that raises one `HALT`s at
precedence 1 whether the audit passed or not, which is why the `boundary-halt`
fixture shows `HALT` alongside `audit_result: PASS` and a decision confidence
of 0.75. The analysis was sound; the action is still prohibited.

## Coverage is not confidence

The audit reports coverage separately from confidence, and the receipt keeps
them in different fields:

```json
"coverage": {
  "planned_operators": [...],
  "executed_operators": [...],
  "missing_operators": [],
  "stages_covered": [...],
  "route_depth": 7,
  "claims_evaluated": 6,
  "contradictions_detected": 3,
  "missing_evidence_items": 5,
  "contradiction_detection_method": "structural: same subject_ref, opposing polarity",
  "coverage_is_not_confidence": true
}
```

A run can have complete coverage and low confidence: every operator ran and
none of them found much support. It can also have high confidence and
incomplete coverage, which the audit fails. Reporting one number for both
would hide exactly the case worth surfacing.

## Stated limits of the audit

Honesty about what these checks do not establish:

- **Contradiction detection is structural, not semantic.** Two claims are
  contradictory when they address the same `subject_ref` with opposing
  polarity. Two claims that disagree in different vocabulary, about subjects
  the operators labelled differently, are not detected. The receipt records
  the detection method so a reader knows the boundary.
- **The audit cannot verify evidence.** It confirms that a claim's confidence
  is consistent with the declared strength and verification state of the
  evidence it cites. It does not confirm the evidence is true.
- **The audit cannot judge whether the reasoning was good.** It confirms the
  process met its contract. A run in which every operator satisfied every
  transformation can still reach a poor conclusion from sound-looking inputs.
- **Confidence is uncalibrated.** No study relates these values to outcome
  correctness. They are decision-support scores and are labelled as such in
  every receipt.
