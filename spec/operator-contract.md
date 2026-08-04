# Operator Contract

**Version:** 0.1.0
**Stage:** v0.1 locked
**Folder alignment:** `spec/`

## What an operator is

A reasoning operator is a versioned unit with an enforced contract. It is not
a prompt, a persona, or a label. Attaching the name of a thinking mode to a
model call proves nothing about how the model reasoned, and this system makes
no such claim. What it asserts is narrower and checkable: the artifact an
operator produced has the structure its contract requires, and every check
below either passed or produced a violation on the record.

Every operator declares eleven things. All eleven are machine-readable in
`spec/operators.yaml`, and `tests/test_acceptance.py` fails if any operator is
missing one.

| Element | What it fixes |
|---|---|
| Purpose | What this operator is for, in one paragraph, without restating the thinking-mode name as an explanation |
| Selection conditions | Which task classes require it, which signals activate it, which suppress it |
| Input contract | Required, optional, and **forbidden** fields the engine may hand it |
| Required transformations | The observable work, each with a `verifiable_as` predicate |
| Output contract | Required fields, claim bounds, whether it may produce options |
| Evidence requirements | Minimum references per claim, minimum quality, whether unverified evidence counts |
| Assumption handling | Whether assumptions must be declared and how they are carried forward |
| Confidence rules | Which declared values are permitted and how the evidence ceiling applies |
| Failure conditions | Enumerated, coded, individually testable |
| Prohibited behaviors | What the operator must never do, beyond the global set |
| Evaluation fixtures | Named fixtures that exercise it |

## The required-transformation rule

This is the element that separates this system from a prompt library. Every
transformation carries a `verifiable_as` clause that the engine can evaluate
against the emitted payload. If a transformation cannot be expressed that way,
it does not belong in a contract.

Worked examples of what "checkable" means here:

- **Systemic** must declare at least one feedback loop, and the engine walks
  the declared relation graph to confirm the loop's path is an actual closed
  cycle. A loop asserted without a traversable path is `SY-F4`.
- **Divergent** must produce materially distinct options, and distinctness is
  computed as the Jaccard similarity of normalized mechanism tokens against
  the policy threshold. Three restatements of one idea are `DV-F2`.
- **Abductive** must name a leading hypothesis and at least one rival, every
  `explains` reference must resolve to a supplied observation, and the
  declared `unexplained_observations` set must equal the computed remainder.
  A single unfalsifiable hypothesis is `AB-F1` and `AB-F4`.
- **Second-order** must declare `order >= 2` and name the first-order effect
  each consequence follows from. A first-order effect relabelled as
  second-order is `SO-F1`.
- **Inverted** must bind every failure mode to a real option and declare a
  precondition, an observable detection signal, and reversibility. A generic
  risk list is `IN-F3` and `IN-F4`.
- **Critical** must bind every defect to a target that exists in the run and
  name a remediation. General caution instead of a typed defect is `CR-F4`.
- **First-principles** must decompose into at least three labelled primitives,
  and every claim must derive from a declared primitive. An assumption
  labelled `verified_fact` without evidence is `FP-F4`.

## Operator classes

| Class | Members | Content source |
|---|---|---|
| `analysis` | first-principles, systemic, divergent, abductive, critical, inverted, second-order | Adapter-supplied payload, contract-enforced by the engine |
| `deterministic` | convergent | Computed by the engine; no generation |
| `meta` | metacognitive | Computed by the engine over the run record, not the problem |

The split matters. Convergence and the audit are the two places where a
generated narrative could quietly become a decision, so neither is generated.
Convergent aggregates evidence-weighted claims arithmetically. The audit runs
deterministic checks over a sealed run record.

## The claim: the common currency

Every operator, whatever its structured payload, emits claims in one shape.

```json
{
  "claim_id": "FP-C1",
  "statement": "...",
  "polarity": "supports | opposes | neutral",
  "subject_ref": "OPT-A",
  "evidence_refs": ["EV-1", "EV-2"],
  "declared_confidence": "high | medium | low | unknown"
}
```

Claims are what convergence aggregates and what contradiction detection
compares. An operator that produces a rich structured payload but no claims
has contributed nothing to the decision, which is deliberate: analysis that
does not resolve into a positioned, evidence-bearing statement should not move
a recommendation.

## Confidence: declared, then capped

```text
effective_confidence = min(declared_confidence_factor, evidence_ceiling)
```

Factors are `high 1.0`, `medium 0.75`, `low 0.5`, `unknown 0.0`, matching the
Leverage Engine baseline exactly so the two systems mean the same thing by the
same word. The ceiling comes from the resolved evidence:

| Distinct evidence records | Ceiling |
|---|---|
| 0 | 0.00 |
| 1 | 0.50 |
| 2 | 0.75 |
| 3 or more | 1.00 |

Two modifiers apply. Mean quality below the task-class minimum drops the
ceiling one band. Evidence drawn entirely from one `independence_group` caps
the ceiling at 0.75 regardless of volume, because ten records from one source
are one source.

The rule this enforces: **a conclusion cannot outrank its evidence.** It is
the same invariant VIL applies to signals (`vil_score = min(weighted_signal_score,
verifiability_score)`), applied one layer up.

Two operators carry a hard cap below `high` in their contracts:

- **Divergent** is capped at `medium` and its claims must be `neutral`.
  Generating an option is not evidence about that option.
- **Second-order** is capped at `medium`. A projection is not an observation.

Divergent is additionally excluded from decision-confidence aggregation. This
is worth stating plainly because it is a real trap: if exploratory output
counts toward decision confidence, a contract-mandated low value on the
generation operator drags every run below the recommendation floor, and the
system looks uncertain about decisions it is not actually uncertain about. The
fix belongs in the contract, not in the aggregation step. Divergent's claims
carry no evidence weight and take no position, so they neither raise nor lower
the decision. Coverage and confidence are reported separately throughout.

## Prohibited behaviors

Global, applying to every operator:

- `emit_private_chain_of_thought` — payload fields named `chain_of_thought`,
  `reasoning_trace`, `scratchpad`, `internal_monologue`, or `thinking` are
  stripped and reported as `GLOBAL-COT`. Structured conclusions are retained;
  private reasoning is not stored.
- `invent_evidence_reference` — any `evidence_refs` entry that does not resolve
  to the run's evidence register is `GLOBAL-FABRICATION`.
- `assert_authorization` — no operator may set or influence authorization
  status. The authorization function does not accept a confidence argument.
- `modify_policy_or_operator_registry` — control files are read-only at run time
  and their checksums are recorded in every receipt.
- `execute_external_action` — the runtime performs no network or process calls,
  asserted by test.
- `claim_human_like_cognition` — the system claims structural compliance, never
  that a thinking label produced human-like reasoning.
- `restate_another_operator_conclusion_as_new_evidence` — evidence comes from
  the register, not from a peer operator's output.

## Adding an operator

Adding an operator is a data change plus a check function:

1. Add the entry to `spec/operators.yaml` with all eleven elements.
2. Add it to `V01_OPERATORS` in `policy.py` (the locked-set guard) and to the
   relevant routes in `spec/routing-policy.yaml`.
3. Add a `_check_<operator>` function in `contracts.py` implementing each
   `verifiable_as` predicate, and register it in `_TRANSFORMATION_CHECKS`.
4. Add a fixture that exercises it and an adversarial test per failure
   condition.

The locked-set guard means step 2 cannot be skipped silently: the registry
fails validation until the operator is explicitly admitted.
