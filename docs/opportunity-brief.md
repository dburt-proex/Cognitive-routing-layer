# Opportunity Brief

**Version:** 0.1.0
**Stage:** Pre-validation
**Folder alignment:** `docs/`

## Verdict

Build it. The premise that this is a real opportunity survives challenge, but
one substitution is required to make it true: **the thinking modes are not the
product.** They are the internal machinery. The product is a reproducible
record proving how a consequential decision was reached, and whether the
reasoning behind it covered what the decision required.

That distinction determines everything downstream — what to build first, what
to demonstrate, what to sell, and what would falsify the whole thesis.

## The premise, challenged

**"Thirteen thinking-mode diagrams form an executable reasoning architecture."**

Half right. The taxonomy is genuine and the stage grouping is sound, but the
diagrams themselves are educational infographics, and educational infographics
have no commercial defensibility. Anyone can redraw them. A prompt pack
wrapping them is a weekend of work for a competitor.

What survives the challenge is narrower and stronger: the modes are a useful
*vocabulary for coverage*. Once "which perspectives were applied to this
decision" is a question with a structured answer, it becomes auditable — and
auditability is the thing nobody currently sells at the reasoning level.

**"Each mode becomes a versioned reasoning operator."**

This is the load-bearing claim, and it is only true if an operator is
enforceable. An operator whose contract cannot be violated by a bad payload is
a label. Every operator here declares required transformations with
mechanically checkable predicates: a declared feedback loop must be a real
cycle in the declared relation graph, three "distinct" options must clear a
token-similarity threshold, a hypothesis must have a rival and a discriminating
test. Fifteen adversarial tests prove the checks fire.

That is the difference between infrastructure and a prompt library, and it is
the only thing here a competitor cannot copy in an afternoon.

## The v0.1 boundary, challenged once, then locked

The proposed v0.1 was nine operators: first-principles, divergent, abductive,
systemic, inverted, critical, second-order, convergent, and a mandatory
metacognitive audit.

**The challenge.** Nine operators is a lot of contract surface for a first
version. The strongest cut is **abductive**: it is a diagnostic operator, and
none of the five required test scenarios is a diagnosis task. Including an
operator that no fixture exercises adds a surface that cannot fail — precisely
the reasoning-theatre failure mode this system exists to prevent.

**The answer, and the decision.** The challenge identifies a real risk and
prescribes the wrong remedy. An operator that cannot fail is a contract
problem, not a membership problem. Abductive's contract gives it four
mechanically checkable transformations: at least two hypotheses with exactly
one ranked leading, every `explains` reference resolving to a supplied
observation, a discriminating test on every hypothesis, and a declared
unexplained-observation set that must equal the computed remainder.
`ContractTests` includes three adversarial tests that break it in three ways.
It can fail.

Cutting it costs something real: `DIAGNOSTIC` becomes an unsupported
classification, so any problem that is "explain this anomaly" routes to REVIEW
as an admitted coverage gap. That is honest, but it is a capability forfeited
to solve a problem that a contract already solved.

**Resolution: keep abductive, make it conditional.** It is required only for
`DIAGNOSTIC` and activates elsewhere on the `unexplained_observation` signal.
In the `leverage-prioritization` fixture it does not run, and the receipt
records why. In `governance-decision` it does, because two anomalies were
supplied unexplained. Membership is not the same as always-on.

**Locked v0.1: nine operators.** The four deferred — analogical, lateral,
associative, Janusian — each carry a specific technical reason in
`spec/operators.yaml`, not a vague "later." Janusian is the most interesting:
it deliberately holds opposed propositions simultaneously, which the v0.1
contradiction gate is built to flag and route to REVIEW. Admitting it requires
a taxonomy distinguishing productive tension from unresolved conflict, and
that taxonomy is its prerequisite.

## Where the value concentrates

Not evenly across the pipeline. Three places:

1. **The evidence gate.** Most decision tooling reports confidence. This
   reports the ceiling that available evidence can support, and refuses to
   converge above it. The `evidence-starved-convergence` fixture is the
   demonstration: three well-formed, materially distinct options, all leaning
   on one internally authored note, and `NO_RECOMMENDATION`. A system that
   answered anyway would be more satisfying and less useful.

2. **The contradiction panel.** Operator disagreement is normally averaged into
   a summary and disappears. Here it is a structured object with a severity, a
   named pair of claims, and a required disposition. The
   `high-risk-code-change` fixture surfaces a genuine one: CI evidence supports
   a scoped credential while the security review's own limited examination
   undercuts it.

3. **The authorization separation.** The single most demonstrable property. Not
   a policy statement but an interface constraint — the authorization function
   takes no confidence argument, and a test asserts its exact parameter list.

## What would falsify this

**That buyers accept model-level observability as sufficient.** If tracing
which model ran under which policy satisfies the audit question in practice,
reasoning-level coverage is an internal quality practice, not a purchased
control, and the commercial thesis fails while the engineering remains sound.

This is untested. It is why the entry offer is an audit deliverable with
today's code rather than an implementation, and why the validation protocol in
`commercialization/offer-ladder.md` includes a control group and a written
falsification condition.

## What is already true

Independent of any commercial outcome:

- Nine operators with complete, versioned, enforceable contracts.
- 81 passing tests, including 15 operator-contract adversarial cases and 12
  authorization-boundary cases.
- Seven fixtures covering all five required scenarios plus unsupported
  classification and boundary HALT.
- Byte-identical replay across every fixture.
- Documented boundaries with all eight ecosystem systems, no cross-imports.
- Zero runtime dependencies.

The engineering claim stands on its own. The commercial claim does not yet.
