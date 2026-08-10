# Calibration Run — August 2026

**Version:** 0.1.0
**Stage:** Instrument calibration. **Not** the validation protocol.
**Folder alignment:** `audit/calibration-2026-08/`

## What this is

Two real decisions taken during the v0.1 build, reconstructed as structured
intake and run through the Cognitive Routing Layer. The purpose was to measure
whether the operator contracts bind on real material and how long
reconstruction takes — not to validate the commercial assumption.

These runs are **not** part of the acceptance suite. They live outside
`tests/fixtures/` deliberately: they are evidence about the instrument, not
tests of it.

```bash
PYTHONPATH=src python -m cognitive_routing_layer.cli \
  --run audit/calibration-2026-08/a2-contradiction-penalty
PYTHONPATH=src python -m cognitive_routing_layer.cli \
  --run audit/calibration-2026-08/a3-generated-options
```

## Method

Each decision was reconstructed from what was knowable **at the decision
point**. No evidence describing the outcome was included, and the option
actually chosen was not marked. The receipts were produced before the
selections were compared against what was actually done.

## Results

| Run | Class | Depth | Gate | Audit | Selected | Confidence | Matched actual choice |
|---|---|---:|---|---|---|---:|---|
| `a2-contradiction-penalty` | DESIGN | 9 | ALLOW | PASS | `OPT-OBJECTIONS` | 0.75 | Yes |
| `a3-generated-options` | DESIGN | 9 | REVIEW | FAIL | `OPT-MERGE` | 0.50 | Yes |

Both runs selected the option that was actually chosen. A2 cleared every gate.
A3 selected the same option but refused to clear, on three unresolved material
contradictions that all trace to one objection:

> `CR-C1` — Admitting generated options is argued from a case in which the
> generated option had no evidence and could not have won, so the mechanism is
> untested where it would matter.

## The material finding, verified

At the time, that objection was correct, and it was verified against the
shipped suite rather than accepted on its own authority.

| Fixture | Generated option | Evidence-sufficient |
|---|---|---|
| `governance-decision` | `OPT-PILOT` | False |
| `high-risk-code-change` | `OPT-SPLIT` | False |
| `confidence-does-not-authorize` | `OPT-RESTRICT` | False |
| `boundary-halt` | `OPT-ONSITE` | False |

Across all seven acceptance fixtures at the time, a generated option cleared the
evidence threshold in **zero** cases. The shipped test asserted only that a
generated option appeared in the ranking — not that it could pass the threshold
or be selected.

**At calibration time, the branch in which a generated option wins was
implemented and unexercised.** The `a2-contradiction-penalty` run was the first
case anywhere in this repository where a generated option cleared the threshold,
and it still lost on net score.

Remediated by `tests/fixtures/generated-option-wins/`: `OPT-PROVE` is generated
by divergent, supported by downstream evidence, selected, evidence-sufficient,
and asserted under an `ALLOW` gate.

## Measurements

| Measure | Result |
|---|---|
| Material findings | 1, verified |
| Non-obvious findings | 1 |
| False critical findings | 0 |
| Decision changes | 0 — both selections stand; the gap was in evidence, not choice |
| Reconstruction time | ~95 seconds per decision |

The timing figure is a **floor, not an estimate**. Every evidence locator was
already in working context. Reconstructing an older decision, or one belonging
to someone else, requires evidence retrieval and interviews that this run did
not have to perform.

## Why this is not validation

Three reasons, all disqualifying:

1. **Not blinded.** The same author wrote the decisions and their intakes.
   Outcome evidence was withheld and no option was marked as chosen, but the
   author knew the answer while writing the operator payloads. The
   verification of `CR-C1` is independent; the finding's origin is not.
2. **No observed outcomes.** Both decisions are hours old. Success is asserted.
3. **Self-selected.** Choosing which of one's own decisions to submit is the
   selection bias the validation protocol exists to defeat.

The validation protocol in `commercialization/offer-ladder.md` requires six
decisions including a control group of two considered successful, with
retrospectives reconstructed blind. That set must come from decisions with
outcomes months old that the reconstructor did not make — the sibling
repositories are the available source.

No commercial claim follows from this run.
