# Positioning

**Version:** 0.1.0
**Stage:** Pre-validation. No buyer evidence has been collected.
**Folder alignment:** `commercialization/`

## The sellable object

Not the thinking modes. The taxonomy is commodity content — thirteen
well-drawn infographic cards, and any competitor can redraw them in an
afternoon. What is not commodity is a reproducible artifact that shows, for a
consequential decision:

- which analytical perspectives were applied, and which were not;
- what evidence supported each conclusion, and what state that evidence was in;
- what contradicted it, and whether the contradiction was ever dispositioned;
- what was missing;
- and that authorization to act was granted separately from analytical confidence.

The decision receipt is the proof. The outcome the buyer purchases is
**decision assurance**: fewer consequential decisions made on narrow framing,
unsupported assumptions, or unexamined downstream effects, and a defensible
record when someone asks how a decision was reached.

## Ideal buyer

Primary, in order of hypothesized fit:

1. **The accountable owner of AI-assisted decisions in a regulated function.**
   Risk, compliance, internal audit, or a Chief AI Officer who must answer for
   how a recommendation was produced, not merely that a model produced it.
2. **A platform engineering leader shipping agent features** who needs a
   defensible record of why an agent recommended what it did, and who already
   operates change-time controls that a reasoning record would complement.
3. **An operator or founder making high-stakes decisions with AI assistance**
   who has already been burned by a confident recommendation that omitted an
   obvious perspective. Smallest deal, fastest cycle, best source of
   validation evidence.

Not the buyer: anyone who wants better answers from a model. This system does
not make reasoning better. It makes reasoning coverage visible and its gaps
explicit.

## The expensive problem

Decisions get made with narrow framing, and the cost surfaces later as rework,
a reversal, or an incident that a single unasked question would have
prevented. The expense is not the bad decision itself; it is that nobody can
reconstruct why it looked right at the time, so the same gap recurs.

Three concrete forms:

- **Rework.** A direction is chosen, downstream effects surface in the next
  quarter, and the work is redone. The second-order question was never asked
  on the record.
- **Unanswerable audit.** A regulator, board, or customer asks how an
  AI-assisted decision was reached. Model-level observability answers which
  prompt ran and which tokens came back. It does not answer which perspectives
  were applied or what evidence supported the conclusion.
- **Confidence mistaken for permission.** A recommendation reads as certain, so
  it is executed. Analytical confidence and authority to act were never
  separated, structurally or procedurally.

## Existing alternatives

An honest scan, with the caveat that all of the following is category-level
observation. No competitive teardown, pricing analysis, or win/loss data has
been collected.

| Alternative | What it does | Where it stops |
|---|---|---|
| **AI governance platforms** — a Gartner Peer Insights market category ([Gartner](https://www.gartner.com/reviews/market/ai-governance-platforms)), with buyer guides from [Modulos](https://www.modulos.ai/best-ai-governance-platforms/), [Splunk](https://www.splunk.com/en_us/blog/learn/ai-governance-platforms.html), and [Kiteworks](https://www.kiteworks.com/cybersecurity-risk-management/ai-governance-solutions-regulated-industries/) | Model inventory, risk registers, policy management, compliance reporting, audit logs, model cards | Governs the *model lifecycle*. Records that a model was approved and monitored, not which analytical perspectives a specific recommendation applied |
| **Decision intelligence platforms** — also a Gartner Peer Insights category ([Gartner](https://www.gartner.com/reviews/market/decision-intelligence-platforms)), vendors including Rainbird, Dataiku, Aera Technology, eyko ([Dataiku](https://www.dataiku.com/blog/decision-intelligence-platforms), [eyko](https://eyko.ai/blog/decision-intelligence-landscape-2026/)) | Decision modeling, composite AI, decision orchestration, explainability, human-in-the-loop review | Optimized for *recurring, modellable* decisions with defined data pipelines. The novel, one-off, consequential judgment call is the gap |
| **LLM observability and evaluation** | Traces, prompt versions, token costs, eval scores, latency | Answers what the model did. Does not answer whether the reasoning covered the perspectives the decision required |
| **Prompt libraries and "thinking mode" packs** | Reusable prompts, mental-model checklists | No contract, no evidence binding, no failure conditions, no receipt. The closest substitute and the weakest one |
| **Human decision process** — pre-mortems, red teams, decision journals, structured review boards | Genuine coverage when practiced well | Expensive, inconsistently applied, rarely instrumented, and produces prose rather than a queryable record |

The nearest neighbours are decision intelligence platforms. Two authoritative
observations from that space describe requirements this system is built
around: that every automated decision should be traceable to the data that
informed it, the model that scored it, the rule that constrained it, and the
human who reviewed it ([eyko](https://eyko.ai/blog/decision-intelligence-landscape-2026/));
and that buyers should require immutable records showing who changed a
control, when, what evidence was attached, and who approved it — with the
audit trail as a first-class object rather than a log file
([Modulos](https://www.modulos.ai/best-ai-governance-platforms/)).

## Defensible differentiation

Four claims that hold under inspection:

1. **Reasoning-level rather than model-level auditability.** Existing categories
   record which model ran under which policy. This records which analytical
   perspectives were applied to a specific decision, what supported them, and
   what did not. Coverage of *perspective* is the unit.

2. **Contract-enforced operators, not labelled prompts.** Every operator's
   required transformations are mechanically checked. A declared feedback loop
   must be a real cycle in the declared relation graph. Three restated options
   fail a token-distinctness threshold. A hypothesis without a rival and a
   discriminating test fails. Fifteen adversarial tests, one per failure
   condition, prove the checks fire. This is the moat against a prompt pack:
   a competitor can copy the operator names in an afternoon and cannot copy
   the enforcement without rebuilding it.

3. **Structural separation of confidence and authorization.** The authorization
   function takes no confidence argument — there is nothing it could read to
   self-authorize — and a test asserts its exact parameter list. The
   `confidence-does-not-authorize` fixture demonstrates the end state:
   confidence 1.0, audit `PASS`, gate `ALLOW`, execution `NOT_AUTHORIZED`.

4. **Deterministic and reproducible.** Identical normalized intake plus an
   identical policy version yields a byte-identical receipt. Two people
   auditing the same decision see the same artifact. Anything built on a model
   choosing its own thinking style cannot make that claim.

## Claims that can be supported today

Each of these maps to a passing test or an inspectable artifact:

- Every v0.1 operator has an explicit, versioned contract with enumerated
  failure conditions.
- Routing is deterministic and reproducible; identical inputs produce identical
  routes and receipts.
- A caller cannot select its own task class and thereby its own evidence
  threshold.
- Evidence insufficiency, contradictions, and missing evidence are surfaced
  explicitly rather than absorbed into a confidence number.
- The metacognitive audit is mandatory and cannot be waived.
- Analytical confidence cannot authorize action under any combination of gate
  result, evidence sufficiency, and authorization status.
- Spoofed, expired, replayed, mis-bound, and mis-scoped authorizations are
  rejected.
- Completed stages are immutable and hash-verifiable; tampering is detectable.
- Receipts are machine-readable, schema-validated, and integrity-checkable
  after issuance.
- The runtime has no third-party dependencies and performs no network or
  process calls.

## Claims that must not be made

- **Not** that prompting a model with a thinking label proves it reasoned that
  way. The system asserts structural compliance of an artifact, nothing about
  cognition.
- **Not** that confidence values are probabilities of correctness. They are
  uncalibrated decision-support scores, labelled as such in every receipt.
- **Not** that evidence is verified. It is declared, with its verification
  state recorded. Say this in every buyer conversation.
- **Not** that CASA integration is authentic. v0.1 ships an interface and a
  test adapter; the production verifier does not exist and the default fails
  closed.
- **Not** that the system prevents bad decisions. It surfaces coverage gaps
  and evidence weakness. A well-formed shallow analysis passes every check.
- **Not** that this is the first system in the ecosystem to store decisions.
  CASA, the Leverage Engine's DecisionLedger, and Mirdexx already do. The
  accurate claim is narrower: this may be the first component dedicated to
  operator-level reasoning coverage and structured decision receipts.
- **Not** any market size, adoption, revenue, or customer-count figure. None
  has been measured and none appears in this repository.
- **Not** compliance with any named regulation. No mapping to EU AI Act, SOC 2,
  ISO 42001, or any other framework has been performed.

## The load-bearing unvalidated assumption

**That buyers will pay for reasoning-level auditability rather than accepting
model-level observability.** Everything commercial rests on it, and it has not
been tested. The counter-case is credible: enterprises may conclude that
tracing which model ran under which policy is sufficient, and that reasoning
coverage is an internal quality practice rather than a purchased control.

This assumption is the reason the offer ladder starts with an audit rather
than an implementation. The audit is deliverable with today's code, requires
no integration, and doubles as the instrument that tests the assumption. See
`commercialization/offer-ladder.md` for the validation protocol, which is
deliberately designed to be able to fail.
