"""The mandatory metacognitive audit.

This operator audits the run, not the problem. Its four phases follow the
PLAN / MONITOR / EVALUATE / REFLECT structure of the source metacognition
model, but each phase here is a deterministic check over the run record
rather than a prompt. A FAIL cannot be waived: the conflict-resolution
precedence routes an audited-failed run to REVIEW no matter how strong the
recommendation looked.
"""
from typing import Any

from .stages import StageChain


def _finding(finding_id: str, phase: str, severity: str, detail: str) -> dict[str, Any]:
    return {"finding_id": finding_id, "phase": phase, "severity": severity, "detail": detail}


def run_audit(
    planned_operators: list[str],
    executed_operators: list[str],
    violations: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    convergence: dict[str, Any],
    authorization: dict[str, Any],
    missing_evidence: list[dict[str, Any]],
    chain: StageChain,
    stage_contents: dict[int, dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    # PLAN -------------------------------------------------------------
    missing_operators = sorted(set(planned_operators) - set(executed_operators))
    extra_operators = sorted(set(executed_operators) - set(planned_operators))
    for operator_id in missing_operators:
        findings.append(_finding("MC-F1", "PLAN", "material", f"required operator {operator_id} did not execute"))
    for operator_id in extra_operators:
        findings.append(_finding("MC-F1", "PLAN", "material", f"operator {operator_id} executed but was not in the selected route"))

    depth = len(executed_operators)
    execution = policy["execution_model"]
    if depth < execution["min_route_depth"]:
        findings.append(_finding("MC-F1", "PLAN", "material", f"route depth {depth} is below the policy minimum"))

    # MONITOR ----------------------------------------------------------
    for violation in violations:
        findings.append(
            _finding("MC-F2", "MONITOR", "material", f"{violation['operator_id']} violated {violation['code']}: {violation['detail']}")
        )
    for chain_finding in chain.verify(stage_contents):
        findings.append(
            _finding(chain_finding["finding_id"], "MONITOR", "material", f"stage {chain_finding['stage']}: {chain_finding['detail']}")
        )

    # EVALUATE ---------------------------------------------------------
    for claim in claims:
        if claim["effective_confidence"] > claim["evidence_ceiling"] + 1e-9:
            findings.append(
                _finding(
                    "MC-F3",
                    "EVALUATE",
                    "material",
                    f"{claim['claim_id']} has effective confidence {claim['effective_confidence']} above its evidence ceiling {claim['evidence_ceiling']}",
                )
            )
    if not convergence.get("thresholds_applied"):
        findings.append(_finding("MC-F3", "EVALUATE", "material", "no evidence sufficiency threshold was applied at convergence"))

    # REFLECT ----------------------------------------------------------
    for contradiction in contradictions:
        if not contradiction.get("disposition"):
            findings.append(_finding("MC-F4", "REFLECT", "material", f"{contradiction['contradiction_id']} has no disposition"))
        elif contradiction["severity"] == "material" and contradiction["disposition"] == "unresolved":
            findings.append(
                _finding("MC-F4", "REFLECT", "material", f"{contradiction['contradiction_id']} is a material contradiction left unresolved")
            )
    if contradiction_self_assigned := [
        item for item in contradictions if item["disposition"] == "accepted_tension" and not item.get("disposition_owner")
    ]:
        for item in contradiction_self_assigned:
            findings.append(
                _finding("MC-F4", "REFLECT", "material", f"{item['contradiction_id']} was self-assigned accepted_tension without a human owner")
            )
    if authorization.get("derived_from_confidence"):
        findings.append(_finding("MC-F5", "REFLECT", "material", "authorization status was derived from a confidence value"))
    for gap in missing_evidence:
        findings.append(_finding("MC-EVIDENCE-GAP", "REFLECT", "minor", gap["detail"]))

    material = [item for item in findings if item["severity"] == "material"]
    stages_covered = sorted({record["stage"] for record in chain.records})

    return {
        "operator_id": "metacognitive",
        "audit_result": "FAIL" if material else "PASS",
        "findings": findings,
        "material_finding_count": len(material),
        "phases": [
            {"phase": "PLAN", "checked": "the executed route matches the route the policy selected"},
            {"phase": "MONITOR", "checked": "operator contracts were satisfied and the stage chain is intact"},
            {"phase": "EVALUATE", "checked": "no claim outranks its evidence and thresholds were applied"},
            {"phase": "REFLECT", "checked": "contradictions are dispositioned, gaps enumerated, authorization not derived from confidence"},
        ],
        "coverage": {
            "planned_operators": sorted(planned_operators),
            "executed_operators": sorted(executed_operators),
            "missing_operators": missing_operators,
            "stages_covered": stages_covered,
            "route_depth": depth,
            "claims_evaluated": len(claims),
            "contradictions_detected": len(contradictions),
            "missing_evidence_items": len(missing_evidence),
            "contradiction_detection_method": "structural: same subject_ref, opposing polarity",
            "coverage_is_not_confidence": True,
        },
        "declared_confidence": "high",
        "stage_chain_head": chain.head,
    }
