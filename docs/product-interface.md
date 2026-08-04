# Product Interface

**Version:** 0.1.0
**Stage:** Specification only. Nothing here is built.
**Folder alignment:** `docs/`

## The constraint that comes first

**The executable core is independent of any interface.** The Cognitive Routing
Layer is a library and a CLI that reads JSON and writes a schema-validated
receipt. It has no view layer, no server, no session state, and no third-party
dependencies. Every panel below is a rendering of fields that already exist in
`schemas/decision-receipt.schema.json`.

This is a hard boundary, not a preference. If a panel needs data the receipt
does not contain, the change belongs in the receipt schema and its tests
first, and in the interface second. Any interface that computes its own
version of a value the receipt already carries has forked the truth.

## Panels

### 1. Problem intake

Structured entry against `schemas/problem-intake.schema.json`, not a chat box.
The field structure is the point: options with explicit mechanisms and
tradeoffs, observations flagged explained or not, data scope, permission
delta, affected systems, and whether the decision is precedent-setting.

Filling this in is itself an intervention. Most of the framing failures this
system detects are visible at intake, before any operator runs.

The interface must show the computed classification and its activated rule
**before** the run, alongside the signals that fired. A user should see "this
will be classified `CHANGE_RISK` by rule CL-1, requiring three distinct
evidence records across two independent sources" while they can still respond
to it.

*Fields:* `problem_statement`, `classification.*`, `signals`,
`convergence.thresholds_applied`.

### 2. Selected reasoning route

The route as a stage sequence, each operator showing whether it was required
or conditional, and for conditional operators which signals activated it.

Equally important: the operators **not** selected, with what would have
activated them, and the deferred v0.2 operators with their deferral reasons.
The absence of an operator is as informative as its presence, and an interface
that only shows what ran hides half the coverage picture.

*Fields:* `route.stage_sequence`, `route.operators[].selection_basis`,
`route.operators[].activated_by`, `route.operators[].selection_rationale`,
`route.operators_not_selected`, `route.operators_deferred`.

### 3. Interactive operator graph

Nodes are operators, grouped by stage, ordered left to right in stage
sequence. Edges are claim relationships: an operator's claim to the option it
addresses, and a critical defect to the claim it targets.

Node colour encodes contract status — complete, contract violation, not
executed. Node size encodes claim count. Edge style encodes polarity:
supporting, opposing, neutral.

Selecting a node opens its structured payload in its native shape: primitives
with status labels for first-principles, a component-and-relation diagram for
systemic, a hypothesis table for abductive, a failure-mode table for inverted.
Each operator's payload has a natural form and the interface should use it
rather than flattening everything to prose.

The graph must never render a private reasoning trace. It renders structured
conclusions, which are the only thing the receipt contains.

*Fields:* `operator_conclusions[]`, `option_set`, `contradictions[]`.

### 4. Evidence panel

Every record with its verification state shown prominently — `UNVERIFIED`
through `AUTHORITATIVE` — and its independence group, quality, and which
claims cite it.

Two things need visual weight because they are the panel's reason to exist:

- **Declared is not verified.** A record at `UNVERIFIED` or
  `SOURCE_IDENTIFIED` should look different from one at `INTEGRITY_CHECKED` or
  `AUTHORITATIVE`, at a glance.
- **Independence.** Grouping by `independence_group` makes single-source
  evidence bases visible immediately. In the `governance-decision` receipt,
  three of four records share one buyer-supplied group, which is why no option
  clears the threshold. A flat list would hide that; a grouped view makes it
  the first thing seen.

Records with `untrusted_instruction_detected` carry an explicit marker and
their downgrade is shown, not silently applied.

*Fields:* `evidence_used[]`, `convergence.ranking[].evidence_refs`,
`convergence.ranking[].independent_groups`, `missing_evidence[]`.

### 5. Contradiction panel

Each contradiction as a two-sided card: the supporting claim with its operator
and effective confidence, the opposing claim with the same, severity, and the
disposition control.

The disposition control is the one place in the interface where a human
changes the run's outcome, so it needs care:

- `resolved_by_evidence` and `resolved_by_precedence` require a written reason.
- `accepted_tension` requires a written justification **and** records the
  reviewer's identity. The engine may never self-assign it.
- `unresolved` is the default and blocks `ALLOW` when the severity is material.

The panel must also show what detection did not cover. Detection is structural
— same subject, opposing polarity — and the interface should state that so a
reader knows an empty panel is not proof of agreement.

*Fields:* `contradictions[]`, `contradiction_rules.disposition_vocabulary`.

### 6. Confidence and coverage indicators

**Two separate indicators. Never one composite score.**

*Coverage* is categorical: which stages ran, which operators executed, which
were skipped and why, route depth against the policy bounds. It answers
"was this looked at from enough angles."

*Confidence* is a number with its derivation shown inline —
`min(mean supporting claim confidence, evidence ceiling) − contradiction penalty`
— and the label `uncalibrated decision-support score` attached wherever the
number appears. Not a tooltip. Adjacent text.

The interface should show the applicable threshold next to the value, and
whether the route is high-impact, so 0.58 against a 0.75 high-impact floor
reads as "below the bar for this kind of decision" rather than as a bare
number.

Complete coverage with low confidence and high confidence with incomplete
coverage are different situations, and one merged gauge would make them look
identical.

*Fields:* `convergence.decision_confidence`, `decision_confidence_basis`,
`decision_confidence_label`, `gate.confidence_threshold_applied`,
`gate.high_impact_route`, `metacognitive_audit.coverage`,
`confidence_by_operator[]`.

### 7. Human-review controls

Active where the gate result is `REVIEW` or `HALT`:

- Disposition each contradiction.
- Record a classification override with owner and reason. Overriding is
  permitted; overriding silently is not.
- Supply missing evidence and re-run, producing a superseding run that
  references the prior `run_id`. Never an edit of the original.
- Approve the recommendation for human action — which is not an authorization
  and must not be presented as one.
- Request authorization, which routes to CASA and returns a verified object or
  does not.

Every control writes an attributable record. The interface should make it
impossible to change a run's outcome anonymously.

*Fields:* `gate.gate_reasons[]`, `review_requirements[]`,
`human_review_gates` from the policy, `classification.manual_override*`.

### 8. Final decision receipt

The full receipt, readable and exportable. Three affordances:

- **Integrity.** Show `stage_chain_head` and a verify action that re-derives
  every stage hash. A receipt that cannot prove its own integrity is a
  document, not a record.
- **Export.** Raw JSON for the Shared Decision Ledger, and a rendered summary
  for humans. Both, from the same source.
- **Diff against the ungoverned answer.** Given the same problem answered
  without the routing layer, show what changed: assumptions surfaced, evidence
  introduced, options rejected and why, contradictions found, confidence
  moved, recommendation altered.

That last one is the demonstration artifact. It is also the only panel here
that needs data the receipt does not yet carry — the ungoverned baseline —
which makes it a v0.2 schema change first and an interface feature second.

*Fields:* the whole receipt, `stage_chain[]`, `stage_chain_head`, `record_id`.

## What the interface must never do

- Render or store private chain-of-thought. The receipt contains none, and no
  panel may reintroduce it.
- Merge coverage and confidence into one score.
- Show an authorization status derived from anything but a verifier result.
- Present a `TestAdapterVerifier` result without its `verifier_is_authentic:
  false` marker.
- Let a user edit a completed run. Corrections supersede; they do not mutate.
- Compute a value the receipt already carries.
