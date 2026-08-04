# Integration Boundaries

**Version:** 0.1.0
**Stage:** v0.1 locked
**Folder alignment:** `docs/`

## Purpose

Prevent ownership collision. Each system in this ecosystem has one
responsibility, and the Reasoning Control Plane must not absorb any of them.
This document states what the Cognitive Routing Layer consumes, what it emits,
and what it is explicitly prohibited from doing on another system's behalf.

The format follows `operator-intelligence/leverage-engine/architecture/system-boundaries.md`
so the two documents can be read side by side.

## Responsibility table

| System | Owns | Interface with the Cognitive Routing Layer | Prohibited transfer of authority |
|---|---|---|---|
| **Operator Intelligence** | Organizational and agentic readiness assessment, findings, Operator Score | Consumes RCP receipts as evidence of reasoning coverage in an assessed organization | RCP cannot modify Operator Score, findings, or assessment records |
| **PromptBP** | Instruction contracts, versioning, capability registry | Owns the instruction layer that generates operator payloads once a model adapter replaces the fixture adapter | RCP cannot version instructions; PromptBP cannot alter routing policy or evidence thresholds |
| **VIL** | Signal relevance, evidence strength, verifiability scoring | Supplies scored signals that populate the evidence register with `quality` and `verification_state` | RCP cannot redefine VIL scoring semantics; VIL cannot select operators |
| **Leverage Engine** | Candidate generation, ranking, directive drafting, queue state | **Primary consumer.** Attaches an RCP receipt to a directive so the ranking can cite reasoning coverage rather than assert it | RCP cannot rank opportunities or draft directives; the Leverage Engine cannot bypass the metacognitive audit |
| **Reasoning Control Plane** | Which analytical perspectives are applied before a recommendation, and the evidence, contradictions, and coverage behind it | Emits a decision receipt | Cannot execute, authorize, rank, persist durably, or claim realized value |
| **CASA** | Runtime permissions, tools, actions, approval gates | **Authority for the authorization gate.** Issues the authorization object RCP verifies and binds to a receipt | RCP cannot authorize anything; CASA cannot substitute for evidence sufficiency |
| **DiffWall** | Code-change risk at change time | Supplies scan results as evidence records for `CHANGE_RISK` runs; may invoke RCP for inverted, second-order, and systemic analysis on high-risk changes | RCP cannot gate a merge; DiffWall cannot choose the reasoning route |
| **Mirdexx / Shared Decision Ledger** | Durable retention of evidence, decisions, changes, audit records | **Persistence authority.** Receives the emitted receipt for durable storage | RCP cannot become a second durable decision store; the ledger cannot alter a receipt |

## What the Cognitive Routing Layer is not

Three claims worth stating explicitly, because each is easy to drift into:

**It is not the ecosystem's decision store.** CASA already maintains an
immutable ledger, the Leverage Engine already appends DecisionLedger records,
and Mirdexx already owns durable artifact retention. The local JSONL ledger in
this repository exists for run-local receipt integrity and authorization
replay detection, not as a competing system of record. The accurate claim is
narrower: this may be the first component dedicated to **operator-level
reasoning coverage and structured decision receipts**.

**It is not a governance gate.** `ALLOW` means eligible for human review.
DiffWall gates merges. CASA gates actions. RCP gates neither.

**It is not an evidence verifier.** It records the declared strength and
verification state of evidence and reports which state each record was in when
it was used. It does not retrieve, authenticate, or corroborate anything.

## Interface contracts

### Inbound: VIL → RCP

VIL scores populate evidence records. The mapping is direct:

| VIL concept | Evidence record field |
|---|---|
| verifiability score | `quality` (0–100) |
| source classification | `source_type`, `authority` |
| independence | `independence_group` |
| validation state | `verification_state` |

RCP's invariant is the same one VIL applies to signals, one layer up. VIL
holds `vil_score = min(weighted_signal_score, verifiability_score)`; RCP holds
`effective_confidence = min(declared_confidence, evidence_ceiling)`. Neither a
signal nor a conclusion may outrank its evidence.

### Inbound: DiffWall → RCP

DiffWall scan results enter as evidence records with
`source_type: repository` and `authority: authoritative`. A DiffWall `HALT`
does not force an RCP `HALT`: DiffWall governs whether the change may merge,
RCP governs whether the reasoning about the change was adequate. The
`high-risk-code-change` fixture shows a DiffWall `HALT` present as evidence
`EV-D2` while the RCP gate result is `REVIEW` on contradiction grounds.

### Inbound: CASA → RCP

The authorization object CASA issues, and every field RCP checks:

```json
{
  "authorization_id": "CASA-AUTH-0001",
  "issuer": "casa",
  "principal": "platform-operator",
  "resource": "identity-provider:svc-deployer",
  "action_hash": "<sha256 of kind|target|principal|resource|data_scope>",
  "bound_receipt_hash": "<sha256 of run_id|recommendation|option_id>",
  "policy_version": "0.1.0",
  "issued_at": "2026-08-04T18:55:00Z",
  "expires_at": "2026-08-04T19:30:00Z",
  "nonce": "nonce-0001",
  "signature": "<verifier-checked>"
}
```

All seven conditions must hold: verifier confirms the signature, action hash
matches, principal matches, resource matches, receipt binding matches, the
window is open, the nonce is unused. Any failure yields `DENIED`. No verifier
yields `VERIFICATION_UNAVAILABLE`.

**v0.1 has no authentic CASA verifier.** Integration requires implementing
`CasaVerifier` against CASA's real issuance mechanism. Until then the default
`UnavailableVerifier` is the only production-safe configuration, and any
receipt produced with `TestAdapterVerifier` carries
`verifier_is_authentic: false`.

### Outbound: RCP → Leverage Engine

The Leverage Engine attaches a receipt to a directive:

| Receipt field | Leverage Engine use |
|---|---|
| `recommendation.option_id` | The reasoning-supported candidate |
| `convergence.decision_confidence` | Feeds the confidence factor, still capped by the engine's own rules |
| `gate.gate_result` | `ALLOW` is a precondition for directive eligibility, never a substitute for the engine's gates |
| `metacognitive_audit.coverage` | Which perspectives were applied |
| `missing_evidence` | Directive completion contract |
| `contradictions` | Reviewer briefing |
| `record_id`, `stage_chain_head` | Cross-reference into the ledger |

Vocabulary is shared deliberately: `ALLOW/REVIEW/HALT` and the `G4_*` boundary
flags mean the same thing in both systems, so no translation layer is needed
and no meaning is lost at the seam.

### Outbound: RCP → Shared Decision Ledger / Mirdexx

The full receipt, validated against `schemas/decision-receipt.schema.json`,
with `record_id` as the idempotency key and `stage_chain_head` as the
integrity anchor. RCP writes a local JSONL copy when a ledger path is
supplied; durable retention, indexing, and cross-run history belong to
Mirdexx.

Corrections create a superseding run that references the prior `run_id`. A
receipt is never mutated. This matches the Leverage Engine's correction model.

### Outbound: RCP → Operator Intelligence

An assessment can ask a new question with these receipts: not "does this
organization have an AI policy" but "when this organization made consequential
decisions, which analytical perspectives were actually applied, what evidence
supported them, and what contradictions were left unresolved." That is the
Cognitive Coverage Audit, and it is the entry offer in
`commercialization/offer-ladder.md`.

## Boundary tests

| Boundary | Test |
|---|---|
| RCP never authorizes | `test_no_receipt_in_any_scenario_authorizes_execution` |
| Confidence cannot become permission | `test_confidence_cannot_grant_permission` (exhaustive over gate × sufficiency × status) |
| Authorization cannot cure evidence | `test_authorization_cannot_cure_insufficient_evidence` |
| The gate cannot read confidence | `test_the_authorization_gate_cannot_read_confidence` |
| A test adapter is never called authentic | `test_a_valid_test_adapter_authorization_proceeds_but_is_never_called_authentic` |
| No external action at runtime | `test_the_runtime_performs_no_network_or_process_execution` |
| Control files are versioned and checksummed | every receipt carries `versions.*_sha256` |
