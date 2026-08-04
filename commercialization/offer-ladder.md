# Offer Ladder

**Version:** 0.1.0
**Stage:** Pre-validation. No offer here has been sold or priced against a real buyer.
**Folder alignment:** `commercialization/`

## Evaluation of the proposed ladder

The proposed four rungs were: Cognitive Coverage Audit → Governed Decision
Design Sprint → Reasoning Control Plane implementation → Enterprise API and
governance integration.

The sequence is sound. Each rung produces the input the next one needs, and
the ladder tests demand before creating integration obligations. Two changes:

**Rename rung 1.** "Cognitive Coverage Audit" describes the mechanism. Buyers
purchase outcomes, not mechanisms. **Decision Assurance Audit** names what
they get: identification of missing perspectives, unsupported assumptions,
unresolved contradictions, and evidence gaps in consequential AI-assisted
decisions. The coverage analysis is how it works; the receipt is the proof
artifact; assurance is the outcome.

**Add an explicit gate between rungs 2 and 3.** Selling an implementation
before a policy has survived real decisions sells a configuration exercise.
Rung 3 should not open until at least two design sprints have produced a
routing policy that held up against decisions the buyer actually made.

## Rung 1 — Decision Assurance Audit

**Outcome.** A written finding for each reviewed decision: which analytical
perspectives were applied and which were not, which conclusions rested on
unsupported assumptions, which contradictions were never dispositioned, and
where evidence was insufficient for the conclusion drawn.

**Mechanism.** Reconstruct each decision as a structured intake, run it through
the Cognitive Routing Layer, and deliver the receipts plus a synthesis.

**Why this is the entry point.** Zero integration. Deliverable with today's
code. Requires no access to production systems. And it is simultaneously the
instrument that tests whether the core commercial assumption holds.

**Deliverables.** One decision receipt per decision, a coverage synthesis
across the set, and a prioritized gap list.

**Effort.** Days, not weeks, once intake reconstruction is practiced.

**Pricing.** Not established. Do not quote a figure until three of these have
been delivered and the effort is measured rather than estimated.

## Rung 2 — Governed Decision Design Sprint

**Outcome.** A routing policy fitted to the buyer's decision types: their task
classifications, their evidence thresholds, their boundary conditions, their
human-review gates.

**Mechanism.** A working session that produces a versioned
`routing-policy.yaml` and any operator contract adjustments, validated against
real historical decisions from the audit in rung 1.

**Precondition.** A completed Decision Assurance Audit. Without it the sprint
designs policy against imagined decisions.

**Deliverables.** A versioned routing policy, fixtures drawn from the buyer's
own decisions, and acceptance tests that fail when the policy is violated.

## Gate — policy survival

Rung 3 does not open until two sprints have produced a policy that survived
contact with real decisions: the thresholds were not immediately overridden,
the classifications matched how the organization actually frames problems, and
the review gates fired on the right decisions rather than on everything.

A policy that has not survived this is a configuration nobody will maintain.

## Rung 3 — Reasoning Control Plane implementation

**Outcome.** The buyer runs governed decisions themselves, producing receipts
as a normal part of their decision process.

**Mechanism.** Deploy the Cognitive Routing Layer against the buyer's policy,
connect a model adapter for operator generation, wire receipt persistence into
their existing decision store.

**Deliverables.** Running deployment, operations runbook, policy change
process, and calibration baseline.

**What this rung requires that v0.1 does not yet have.** A model adapter
(v0.2), and a decision on receipt persistence that does not create a second
system of record.

## Rung 4 — Enterprise API and governance integration

**Outcome.** Reasoning coverage becomes a control other systems consume:
change management, agent runtimes, approval workflows.

**Mechanism.** The API, an authentic CASA verifier against the buyer's
authorization authority, and receipt handoff into their audit infrastructure.

**What this rung requires that v0.1 does not have.** An authentic CASA
verifier. v0.1 ships the interface, the seven binding checks, and a test
adapter that reports itself as inauthentic. Selling rung 4 before that exists
would be selling a control that fails closed by design.

## Flagship demonstration

The `confidence-does-not-authorize` fixture, run live.

The system reaches maximum decision confidence — 1.0 — on a credential-rotation
decision. The metacognitive audit passes with zero material findings. The gate
returns `ALLOW`. An irreversible action was requested. Execution outcome:
`NOT_AUTHORIZED`.

Then present a signed authorization and watch it flip to `MAY_PROCEED`. Then
present the same authorization a second time and watch replay protection deny
it. Then present one bound to a different action and watch the action-binding
check deny it.

The demonstration works because it inverts the expected story. Every AI demo
shows the system being confident. This one shows the system being maximally
confident and still not permitted to act — and then shows exactly what it
takes to grant permission, and how many ways that grant can be refused.

## Validation protocol

Six decisions, deliberately structured to be able to fail.

| Set | Count | Why |
|---|---|---|
| Decisions that caused rework | 2 | The cases where a missing perspective is most likely |
| Decisions considered successful | 2 | **The control group.** Without it the protocol only proves the system generates findings, not that findings track outcomes |
| Upcoming live decisions | 2 | Tests prospective usefulness, not just retrospective critique |

Selecting only decisions that caused rework is a selection-bias trap: a system
that generates plausible findings will always find something in a decision
already known to have gone wrong. The successful decisions are what make the
result interpretable.

**Blinding.** Retrospective cases are reconstructed as intake without revealing
the outcome. The reconstructor should not know which set a decision belongs
to. Compare findings against known outcomes only after all receipts are
produced.

**Measurements.**

| Measure | Definition |
|---|---|
| Material findings | Findings the decision owner agrees are real |
| Non-obvious findings | Material findings the owner had not already identified |
| False critical findings | Findings raised as material that the owner rejects |
| Reviewer agreement | Two reviewers, independently, on the same receipt |
| Decision changes | Live decisions where the receipt changed the outcome |
| Time per audit | Reconstruction plus review, measured not estimated |
| Perceived usefulness | The owner's own rating |
| Willingness to pay | Asked directly, after delivery |

**The falsification condition.** If the rework decisions produce no
non-obvious material findings, and the successful decisions produce
false criticals at a similar rate, the core assumption is wrong. That is the
signal to stop rather than build v0.2.

Write this condition down before running the protocol. A validation exercise
that cannot fail has not validated anything.

## What must not be claimed until the protocol runs

No market validation. No customer count. No revenue. No "proven" anything. The
only supportable commercial statement today is that the system does what
`tests/acceptance-tests.md` says it does, and that nobody has yet paid for it.
