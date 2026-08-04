"""Operator contract enforcement.

This module is the reason the system is not a prompt library. An operator's
declared thinking mode buys it nothing; what it must do is produce a payload
whose required transformations are mechanically checkable, and every check
below either passes or produces a violation that forces REVIEW.

Nothing here claims the model reasoned in a particular way. The checks assert
only that the emitted artifact has the structure the operator's contract
requires, which is an observable property of the output.
"""
import re
from typing import Any

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is", "it",
    "of", "on", "or", "that", "the", "then", "this", "to", "with", "we", "our", "its", "will",
}

CHAIN_OF_THOUGHT_FIELDS = {"chain_of_thought", "reasoning_trace", "scratchpad", "internal_monologue", "thinking"}


class ContractViolation(dict):
    """A structured, reportable contract failure."""

    def __init__(self, operator_id: str, code: str, detail: str) -> None:
        super().__init__(operator_id=operator_id, code=code, detail=detail)


def _tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in _STOPWORDS}


def _jaccard(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


# --------------------------------------------------------------------------
# Per-operator transformation checks
# --------------------------------------------------------------------------

def _check_first_principles(payload: dict, ctx: dict) -> list[ContractViolation]:
    out: list[ContractViolation] = []
    primitives = payload.get("primitives", [])
    if len(primitives) < 3:
        out.append(ContractViolation("first-principles", "FP-F1", f"requires 3 primitives, found {len(primitives)}"))
    valid_status = {"verified_fact", "assumption", "unknown"}
    ids = set()
    for primitive in primitives:
        ids.add(primitive.get("primitive_id"))
        if primitive.get("status") not in valid_status:
            out.append(
                ContractViolation("first-principles", "FP-F2", f"{primitive.get('primitive_id')} has status {primitive.get('status')!r}")
            )
        if primitive.get("status") == "verified_fact" and not primitive.get("evidence_refs"):
            out.append(
                ContractViolation("first-principles", "FP-F4", f"{primitive.get('primitive_id')} is a verified_fact with no evidence")
            )
    for claim in payload.get("claims", []):
        derived = claim.get("derived_from", [])
        if not derived or not set(derived) <= ids:
            out.append(
                ContractViolation("first-principles", "FP-F3", f"{claim.get('claim_id')} derives from {derived}, which is not a declared primitive set")
            )
    return out


def _check_systemic(payload: dict, ctx: dict) -> list[ContractViolation]:
    out: list[ContractViolation] = []
    components = payload.get("components", [])
    if len(components) < 3:
        out.append(ContractViolation("systemic", "SY-F1", f"requires 3 components, found {len(components)}"))
    component_ids = {component.get("component_id") for component in components}
    edges: set[tuple[str, str]] = set()
    for relation in payload.get("relations", []):
        source, target = relation.get("from"), relation.get("to")
        if source not in component_ids or target not in component_ids:
            out.append(ContractViolation("systemic", "SY-F2", f"relation {source}->{target} references an undeclared component"))
        else:
            edges.add((source, target))
    loops = payload.get("feedback_loops", [])
    if not loops:
        out.append(ContractViolation("systemic", "SY-F3", "no feedback loop declared"))
    for loop in loops:
        path = loop.get("path", [])
        if len(path) < 2:
            out.append(ContractViolation("systemic", "SY-F4", f"{loop.get('loop_id')} declares a path shorter than two components"))
            continue
        closed = list(path) + [path[0]]
        broken = [
            f"{closed[index]}->{closed[index + 1]}"
            for index in range(len(closed) - 1)
            if (closed[index], closed[index + 1]) not in edges
        ]
        if broken:
            out.append(
                ContractViolation("systemic", "SY-F4", f"{loop.get('loop_id')} is not a closed cycle; missing relations {broken}")
            )
    return out


def _check_divergent(payload: dict, ctx: dict) -> list[ContractViolation]:
    out: list[ContractViolation] = []
    options = payload.get("options", [])
    if len(options) < 3:
        out.append(ContractViolation("divergent", "DV-F1", f"requires 3 options, found {len(options)}"))
    threshold = ctx["policy"]["option_distinctness_jaccard_max"]
    for i in range(len(options)):
        for j in range(i + 1, len(options)):
            similarity = _jaccard(options[i].get("mechanism", ""), options[j].get("mechanism", ""))
            if similarity > threshold:
                out.append(
                    ContractViolation(
                        "divergent",
                        "DV-F2",
                        f"{options[i].get('option_id')} and {options[j].get('option_id')} have mechanism similarity "
                        f"{round(similarity, 3)} above the {threshold} distinctness threshold",
                    )
                )
    for option in options:
        if not _nonempty(option.get("tradeoff")):
            out.append(ContractViolation("divergent", "DV-F3", f"{option.get('option_id')} declares no tradeoff"))
    if payload.get("declared_confidence") == "high":
        out.append(ContractViolation("divergent", "DV-F4", "declared_confidence above the contract maximum of medium"))
    for claim in payload.get("claims", []):
        if claim.get("polarity") != "neutral":
            out.append(
                ContractViolation(
                    "divergent",
                    "DV-F5",
                    f"{claim.get('claim_id')} takes polarity {claim.get('polarity')!r}; divergent is prohibited from ranking or recommending an option",
                )
            )
    return out


def _check_abductive(payload: dict, ctx: dict) -> list[ContractViolation]:
    out: list[ContractViolation] = []
    hypotheses = payload.get("hypotheses", [])
    if len(hypotheses) < 2:
        out.append(ContractViolation("abductive", "AB-F1", f"requires a leading hypothesis and at least one rival, found {len(hypotheses)}"))
    leading = [item for item in hypotheses if item.get("rank") == 1]
    if len(leading) != 1:
        out.append(ContractViolation("abductive", "AB-F2", f"requires exactly one rank 1 hypothesis, found {len(leading)}"))
    known = ctx["observation_ids"]
    for hypothesis in hypotheses:
        explains = set(hypothesis.get("explains", []))
        unknown = sorted(explains - known)
        if unknown:
            out.append(ContractViolation("abductive", "AB-F3", f"{hypothesis.get('hypothesis_id')} explains unsupplied observations {unknown}"))
        if not _nonempty(hypothesis.get("discriminating_test")):
            out.append(ContractViolation("abductive", "AB-F4", f"{hypothesis.get('hypothesis_id')} declares no discriminating test"))
    if leading:
        expected = sorted(known - set(leading[0].get("explains", [])))
        declared = sorted(payload.get("unexplained_observations", []))
        if declared != expected:
            out.append(
                ContractViolation("abductive", "AB-F3", f"unexplained_observations {declared} does not match the computed remainder {expected}")
            )
    return out


def _check_critical(payload: dict, ctx: dict) -> list[ContractViolation]:
    out: list[ContractViolation] = []
    defects = payload.get("defects", [])
    vocabulary = set(ctx["policy"]["defect_vocabulary"])
    targets = ctx["claim_ids"] | ctx["evidence_ids"] | ctx["option_ids"] | {"evidence_register"}
    if not defects and not _nonempty(payload.get("no_defects_found_justification")):
        out.append(ContractViolation("critical", "CR-F4", "no defects and no explicit no_defects_found justification"))
    for defect in defects:
        if defect.get("defect_type") not in vocabulary:
            out.append(ContractViolation("critical", "CR-F1", f"{defect.get('defect_id')} uses type {defect.get('defect_type')!r}, outside the closed vocabulary"))
        if defect.get("target_ref") not in targets:
            out.append(ContractViolation("critical", "CR-F2", f"{defect.get('defect_id')} targets {defect.get('target_ref')!r}, which does not exist in the run"))
        if not _nonempty(defect.get("remediation")):
            out.append(ContractViolation("critical", "CR-F3", f"{defect.get('defect_id')} declares no remediation"))
        if defect.get("severity") not in {"material", "minor"}:
            out.append(ContractViolation("critical", "CR-F1", f"{defect.get('defect_id')} has severity {defect.get('severity')!r}"))
    return out


def _check_inverted(payload: dict, ctx: dict) -> list[ContractViolation]:
    out: list[ContractViolation] = []
    modes = payload.get("failure_modes", [])
    if len(modes) < 2:
        out.append(ContractViolation("inverted", "IN-F1", f"requires 2 failure modes, found {len(modes)}"))
    for mode in modes:
        if mode.get("option_ref") not in ctx["option_ids"]:
            out.append(ContractViolation("inverted", "IN-F2", f"{mode.get('failure_mode_id')} binds to unknown option {mode.get('option_ref')!r}"))
        if not _nonempty(mode.get("precondition")):
            out.append(ContractViolation("inverted", "IN-F3", f"{mode.get('failure_mode_id')} declares no precondition"))
        if not _nonempty(mode.get("detection_signal")):
            out.append(ContractViolation("inverted", "IN-F4", f"{mode.get('failure_mode_id')} declares no detection signal"))
        if not isinstance(mode.get("reversible"), bool):
            out.append(ContractViolation("inverted", "IN-F3", f"{mode.get('failure_mode_id')} does not declare reversibility"))
        candidate = mode.get("boundary_flag_candidate")
        if mode.get("reversible") is False and not candidate:
            out.append(
                ContractViolation("inverted", "IN-F5", f"{mode.get('failure_mode_id')} is irreversible but names no boundary_flag_candidate")
            )
        if candidate and candidate not in set(ctx["policy"]["boundary_flags"]):
            out.append(
                ContractViolation("inverted", "IN-F5", f"{mode.get('failure_mode_id')} names boundary_flag_candidate {candidate!r}, which is outside the policy vocabulary")
            )
    return out


def _check_second_order(payload: dict, ctx: dict) -> list[ContractViolation]:
    out: list[ContractViolation] = []
    horizons = set(ctx["policy"]["horizon_vocabulary"])
    effects = payload.get("effects", [])
    if not effects:
        out.append(ContractViolation("second-order", "SO-F2", "no downstream effects declared"))
    for effect in effects:
        order = effect.get("order")
        if not isinstance(order, int) or order < 2:
            out.append(ContractViolation("second-order", "SO-F1", f"{effect.get('effect_id')} declares order {order!r}, which is not second order or later"))
        if not _nonempty(effect.get("follows_from")):
            out.append(ContractViolation("second-order", "SO-F2", f"{effect.get('effect_id')} names no first-order antecedent"))
        if effect.get("horizon") not in horizons:
            out.append(ContractViolation("second-order", "SO-F2", f"{effect.get('effect_id')} has horizon {effect.get('horizon')!r}"))
        if not _nonempty(effect.get("affected_party")):
            out.append(ContractViolation("second-order", "SO-F2", f"{effect.get('effect_id')} names no affected party"))
        if effect.get("option_ref") not in ctx["option_ids"]:
            out.append(ContractViolation("second-order", "SO-F3", f"{effect.get('effect_id')} binds to unknown option {effect.get('option_ref')!r}"))
    if payload.get("declared_confidence") == "high":
        out.append(ContractViolation("second-order", "SO-F4", "declared_confidence above the contract maximum of medium"))
    return out


_TRANSFORMATION_CHECKS = {
    "first-principles": _check_first_principles,
    "systemic": _check_systemic,
    "divergent": _check_divergent,
    "abductive": _check_abductive,
    "critical": _check_critical,
    "inverted": _check_inverted,
    "second-order": _check_second_order,
}


# --------------------------------------------------------------------------
# Generic contract enforcement
# --------------------------------------------------------------------------

def enforce(operator_id: str, contract: dict, payload: dict, ctx: dict) -> list[ContractViolation]:
    """Validate one operator payload against its versioned contract."""
    violations: list[ContractViolation] = []

    leaked = sorted(CHAIN_OF_THOUGHT_FIELDS & set(payload))
    if leaked:
        violations.append(
            ContractViolation(operator_id, "GLOBAL-COT", f"payload carries private-reasoning fields {leaked}; only structured conclusions are retained")
        )
        for field in leaked:
            payload.pop(field, None)

    output_contract = contract["output_contract"]
    missing = [field for field in output_contract["required_fields"] if field not in payload]
    if missing:
        violations.append(ContractViolation(operator_id, "GLOBAL-OUTPUT", f"payload is missing required fields {missing}"))

    claims = payload.get("claims", [])
    if len(claims) < output_contract["min_claims"]:
        violations.append(ContractViolation(operator_id, "GLOBAL-CLAIMS", f"requires {output_contract['min_claims']} claims, found {len(claims)}"))
    if len(claims) > output_contract["max_claims"]:
        violations.append(ContractViolation(operator_id, "GLOBAL-CLAIMS", f"exceeds the contract maximum of {output_contract['max_claims']} claims"))

    allowed = set(contract["confidence_rules"]["declared_confidence_allowed"])
    declared = payload.get("declared_confidence")
    if declared is not None and declared not in allowed:
        violations.append(ContractViolation(operator_id, "GLOBAL-CONFIDENCE", f"declared_confidence {declared!r} is outside the contract-allowed set {sorted(allowed)}"))

    minimum_refs = contract["evidence_requirements"]["min_evidence_refs_per_claim"]
    for claim in claims:
        refs = claim.get("evidence_refs", [])
        if len(refs) < minimum_refs:
            violations.append(ContractViolation(operator_id, "GLOBAL-EVIDENCE", f"{claim.get('claim_id')} carries {len(refs)} evidence refs, contract requires {minimum_refs}"))
        fabricated = sorted(set(refs) - ctx["evidence_ids"])
        if fabricated:
            violations.append(ContractViolation(operator_id, "GLOBAL-FABRICATION", f"{claim.get('claim_id')} references evidence that does not exist: {fabricated}"))
        if claim.get("subject_ref") and claim["subject_ref"] not in ctx["option_ids"] | ctx["subject_ids"]:
            violations.append(ContractViolation(operator_id, "GLOBAL-SUBJECT", f"{claim.get('claim_id')} has subject_ref {claim['subject_ref']!r}, which is not a known option or subject"))

    if contract["assumption_handling"]["must_declare_assumptions"] and "assumptions" not in payload:
        violations.append(ContractViolation(operator_id, "GLOBAL-ASSUMPTIONS", "contract requires an explicit assumptions list, even when empty"))

    unknown_flags = sorted(set(payload.get("boundary_flags", [])) - set(ctx["policy"]["boundary_flags"]))
    if unknown_flags:
        violations.append(ContractViolation(operator_id, "GLOBAL-BOUNDARY", f"raises boundary flags outside the policy vocabulary: {unknown_flags}"))

    check = _TRANSFORMATION_CHECKS.get(operator_id)
    if check:
        violations.extend(check(payload, ctx))

    return violations
