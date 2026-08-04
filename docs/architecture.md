# Architecture

**Version:** 0.1.0
**Stage:** v0.1 locked
**Folder alignment:** `docs/`

## The pipeline

```text
problem intake                 enforced schema, normalized, hashed
  ↓
task and signal classification computed from normalized intake, never caller-declared
  ↓
reasoning-mode selection       deterministic route from a versioned policy
  ↓
operator execution             contract enforcement per operator, sealed per stage
  ↓
evidence and contradiction gate ceilings, sufficiency thresholds, structural contradiction detection
  ↓
option convergence             deterministic aggregation, or NO_RECOMMENDATION
  ↓
metacognitive audit            mandatory, four phases, cannot be waived
  ↓
recommendation                 with gate result ALLOW / REVIEW / HALT
  ↓
authorization gate             only when an action was requested; separate control
  ↓
decision receipt               machine-readable, schema-validated, hash-linked
```

## Two decisions that shape everything else

### The router is deterministic; only operator content is generative

No model call participates in classification, route selection, convergence, or
the audit. Given normalized intake and a policy version, the route and its
rationale are a pure function. Operator *content* arrives through an adapter,
so a model can supply it later without moving any routing logic into the
model. v0.1 ships a fixture adapter, which is why every run replays
byte-identically.

What the engine executes in either case is the operator *contract*: input
validation, required transformations, evidence binding, confidence ceilings,
prohibited-behavior checks. That is the governable part, and it is enforced
identically whether the payload came from a fixture or a model.

### Confidence and authorization are structurally separate

The separation is not a policy statement that could be forgotten in a later
refactor. It is enforced by the interface:

```python
def evaluate(requested_action, authorization, verifier,
             run_timestamp, receipt_binding, seen_nonces) -> dict
```

There is no confidence, coverage, score, or gate argument. There is nothing
the authorization gate could read to let a well-supported recommendation
authorize itself.
`tests/test_acceptance.py::test_the_authorization_gate_cannot_read_confidence`
asserts the exact parameter set, so adding one would fail the suite.

## Task classification

Computed by ordered first-match over `classification_rules`, with every
non-winning match recorded as a rejected classification.

| Rule | Class | Predicate |
|---|---|---|
| CL-1 | `CHANGE_RISK` | `artifact_kind == code_change` |
| CL-2 | `GOVERNANCE_EVALUATION` | `artifact_kind` in proposal, policy, control_design |
| CL-3 | `DIAGNOSTIC` | at least one unexplained observation and at most one option |
| CL-4 | `PRIORITIZATION` | `decision_kind == select_next_action` and two or more options |
| CL-5 | `DESIGN` | `artifact_kind == system_design` |
| CL-6 | `STRATEGY` | horizon is quarters or years |
| — | `UNSUPPORTED` | nothing matched: declare a coverage gap and route to REVIEW |

A caller may submit `proposed_classification`. It is recorded, compared, and
never honored. A caller that picks its own task class picks its own evidence
thresholds — `CHANGE_RISK` demands three distinct records across two
independent sources with at least one verified, while `PRIORITIZATION` demands
two records from one source. That gap is exactly what a mislabelled intake
would buy.

## Signals

Twelve signals are extracted deterministically from normalized intake:
`contested_options`, `unexplained_observation`, `irreversibility`,
`sensitive_data_scope`, `permission_change`, `external_impact`,
`declared_evidence_gap`, `time_bound`, `novel_domain`, `stakeholder_conflict`,
`systemic_coupling`, `precedent_setting`.

Signals do two things: activate conditional operators, and set the confidence
threshold. Four of them — irreversibility, sensitive data scope, permission
change, external impact — mark a route high-impact and raise the
recommendation floor from 0.50 to 0.75.

## Stages and routes

Stage order is `FRAME → EXPLORE → EXPLAIN → CHALLENGE → FORECAST → DECIDE → AUDIT`.

`CHALLENGE` precedes `DECIDE` so that challenge operators cannot be produced as
justification for a decision already made. Ordering alone would be a
convention, so stage records are append-only and hash-linked; a later stage
that edits an earlier one breaks the chain and the audit reports it.

Operators within a stage share inputs and never read each other's output, so
they are parallel-eligible. The engine serializes them in policy-declared
order so a run is byte-reproducible regardless of scheduling.

| Task class | Required | Conditional (activating signals) |
|---|---|---|
| `PRIORITIZATION` | first-principles, divergent, critical, second-order, convergent, metacognitive | systemic, inverted, abductive |
| `GOVERNANCE_EVALUATION` | first-principles, systemic, critical, inverted, second-order, convergent, metacognitive | divergent, abductive |
| `CHANGE_RISK` | first-principles, systemic, inverted, critical, second-order, convergent, metacognitive | divergent, abductive |
| `DIAGNOSTIC` | first-principles, abductive, systemic, critical, convergent, metacognitive | divergent, second-order, inverted |
| `DESIGN` | first-principles, divergent, systemic, inverted, critical, second-order, convergent, metacognitive | abductive |
| `STRATEGY` | first-principles, systemic, divergent, second-order, critical, convergent, metacognitive | inverted, abductive |

Route depth is bounded at 4 minimum and 9 maximum. The minimum guarantees at
least one FRAME operator, at least one CHALLENGE operator, convergent, and the
audit; anything shallower cannot produce a defensible receipt. The
`governance-decision` fixture runs at exactly 9 and exercises the ceiling.

## Where options come from

The option set grows during the run. Options supplied at intake start it, and
an EXPLORE operator that generates options adds to it. Generated options are
then challenged, forecast, ranked, and rejected on the record like any other.

This matters more than it sounds. If convergence only ranked intake options,
divergent would be decorative — it would produce a list nothing consumed,
which is precisely the failure this system exists to prevent. In the
`governance-decision` receipt, `OPT-PILOT` carries
`"origin": "generated_by:divergent"` and appears in the ranking, rejected for
having no evidence attached.

## Convergence

Deterministic. For each option:

```text
support     = Σ effective_confidence of supporting claims from contributing operators
opposition  = Σ effective_confidence of opposing claims
penalty     = 0.25 × distinct opposing claims in unresolved material contradictions
net         = support − opposition − penalty
```

The penalty counts distinct opposing claims rather than contradiction pairs.
One objection contested by three supporting claims is one disagreement;
charging it three times would scale the penalty by how many supports happened
to be written, which is an artifact of drafting rather than a fact about the
evidence.

Selection happens only among options that clear the task-class evidence
threshold. If none do, the result is `NO_RECOMMENDATION` and `REVIEW`. Ties
within tolerance route to `REVIEW` rather than breaking arbitrarily.

## Conflict resolution

Ordered precedence, first match wins:

| Order | Condition | Result |
|---|---|---|
| 1 | Boundary flag raised | `HALT` |
| 2 | Metacognitive audit failed | `REVIEW` |
| 3 | Required operator missing or in violation | `REVIEW` |
| 4 | No option is evidence-sufficient | `REVIEW` |
| 5 | Unresolved material contradiction | `REVIEW` |
| 6 | Decision confidence below threshold | `REVIEW` |
| 7 | Material tie | `REVIEW` |
| 8 | Otherwise | `ALLOW` |

`ALLOW` means the recommendation is eligible for human review. It is not
permission to act, and it never has been. The vocabulary is deliberately
identical to CASA, DiffWall, and the Leverage Engine so a route result is
legible across the ecosystem without translation. Boundary flags reuse the
Leverage Engine `G4_*` names for the same reason.

## Execution composition

The evidence gate and the authorization gate are independent functions that
compose into one outcome:

| Recommendation eligible | Authorization | Outcome |
|---|---|---|
| yes | `AUTHORIZED` | `MAY_PROCEED` |
| yes | anything else | `NOT_AUTHORIZED` |
| no | `AUTHORIZED` | `REVIEW` |
| no | anything else | `REVIEW` or `HALT` |

Confidence never grants permission, and authorization never cures insufficient
evidence. Proceeding requires both.

## The CASA verifier boundary

A field reading `source: CASA` proves only that a string was typed. An
authorization is accepted only when a configured verifier confirms the
signature, the action hash matches the recommended action, the principal and
resource match the intake, the authorization is bound to this run's
recommendation hash, the window is open, and the nonce is unused.

**v0.1 ships no authentic CASA verifier.** The default returns
`VERIFICATION_UNAVAILABLE` and routes to `REVIEW`. `TestAdapterVerifier` exists
for fixtures, uses an HMAC over the canonical authorization body, and reports
`verifier_is_authentic: false` in every receipt it touches. It must never be
described as a CASA integration.

## Module map

| Module | Responsibility |
|---|---|
| `intake.py` | Schema-enforced intake, normalization, hashing |
| `classify.py` | Signal extraction and computed classification with provenance |
| `router.py` | Deterministic route selection and per-operator rationale |
| `contracts.py` | Required-transformation enforcement per operator |
| `evidence.py` | Evidence resolution, ceilings, sufficiency thresholds |
| `normalize.py` | Untrusted-content handling and injection containment |
| `contradiction.py` | Structural contradiction detection |
| `converge.py` | The convergent operator, computed |
| `audit.py` | The metacognitive audit, computed |
| `authorization.py` | Verifier interface, binding checks, execution composition |
| `stages.py` | Append-only hash-linked stage chain |
| `ledger.py` | Idempotent receipt append, nonce history, tamper detection |
| `receipt` (in `runner.py`) | Receipt assembly |
| `policy.py` | Control-file loading, validation, checksums |
| `cli.py` | Entry point |

Runtime dependencies: none. The engine uses the standard library only and
performs no network or process calls, asserted by
`test_the_runtime_performs_no_network_or_process_execution`.

## Repository placement decision

**Decision: standalone repository. The initial placement hypothesis is rejected.**

The hypothesis was a Leverage Engine module inside the Operator Intelligence
repository. Inspection of `dburt-proex/operator-intelligence` shows why that
would be wrong:

1. **The Leverage Engine already exists and is complete** at v0.1.0 as an
   advisory MVP with its own schemas, policies, fixtures, and passing tests.
2. **Its own boundary contract forbids this.** `leverage-engine/architecture/system-boundaries.md`
   assigns it "candidate generation, ranking, selection, directive draft, queue
   state" and states the acceptance criterion "each system has one explicit
   responsibility." Reasoning-coverage governance is not in that list, and
   adding it would breach the document's own rule.
3. **The dependency runs the wrong way.** The Leverage Engine is a *consumer*
   of reasoning coverage, not its host. A ranking subsystem that must import
   routing logic to explain its own output has the coupling inverted.
4. **The ecosystem convention is one system, one repository.** CASA, DiffWall,
   Mirdexx, VIL, and PromptBP are each separate.

Considered and rejected:

| Option | Verdict |
|---|---|
| Module inside Operator Intelligence | Rejected: breaches the Leverage Engine's stated single responsibility and inverts the dependency |
| Versioned package consumed by the Leverage Engine | Viable later; premature now, because the receipt schema has not survived a real consumer |
| Standalone repository | **Selected.** No cross-imports, independent release cadence, own audit boundary |

The Cognitive Routing Layer imports nothing from any sibling repository. It
reuses their *vocabulary* — `ALLOW/REVIEW/HALT`, `G4_*` flags, confidence
factors — so integration is a data contract rather than a code dependency.
Migration to a published package, if it happens, is a separate decision behind
its own approval gate.
