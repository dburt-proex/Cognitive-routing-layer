"""The convergent operator: deterministic option reduction.

This operator computes; it does not generate. It aggregates evidence-weighted
supporting and opposing claims into a per-option net score, applies the
task-class evidence threshold, and either selects one option or returns
NO_RECOMMENDATION. It can never invent an option, and it can never select an
option that failed the evidence threshold.
"""
from typing import Any

from . import evidence as evidence_module


def _round(value: float) -> float:
    return round(value + 0.0, 6)


def converge(
    options: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    register: dict[str, dict[str, Any]],
    contradictions: list[dict[str, Any]],
    policy: dict[str, Any],
    task_class: str,
) -> dict[str, Any]:
    model = policy["confidence_model"]
    contributors = set(model["decision_confidence_contributors"])
    weighted = [claim for claim in claims if claim["operator_id"] in contributors]

    # Penalty counts distinct opposing claims, not pairwise combinations. One
    # objection contested by three supporting claims is one disagreement, and
    # charging it three times would understate confidence by an artefact of
    # how many supports happened to be written.
    opposing_by_subject: dict[str, set[str]] = {}
    for contradiction in contradictions:
        if contradiction["severity"] == "material" and contradiction["disposition"] == "unresolved":
            opposing_by_subject.setdefault(contradiction["subject_ref"], set()).add(contradiction["opposing_claim_id"])
    material_by_subject = {subject: len(claim_ids) for subject, claim_ids in opposing_by_subject.items()}

    ranking: list[dict[str, Any]] = []
    for option in options:
        option_id = option["option_id"]
        about = [claim for claim in weighted if claim.get("subject_ref") == option_id]
        support = _round(sum(claim["effective_confidence"] for claim in about if claim["polarity"] == "supports"))
        opposition = _round(sum(claim["effective_confidence"] for claim in about if claim["polarity"] == "opposes"))

        refs: list[str] = []
        for claim in about:
            refs.extend(claim.get("evidence_refs", []))
        sufficiency = evidence_module.option_sufficiency(refs, register, policy, task_class)

        penalty = _round(material_by_subject.get(option_id, 0) * model["contradiction_penalty_per_material_contradiction"])
        net = _round(support - opposition - penalty)

        ranking.append(
            {
                "option_id": option_id,
                "label": option["label"],
                "support": support,
                "opposition": opposition,
                "contradiction_penalty": penalty,
                "net": net,
                "supporting_claims": sorted(claim["claim_id"] for claim in about if claim["polarity"] == "supports"),
                "opposing_claims": sorted(claim["claim_id"] for claim in about if claim["polarity"] == "opposes"),
                "evidence_refs": sorted(set(refs)),
                "evidence_sufficient": sufficiency["evidence_sufficient"],
                "unmet_thresholds": sufficiency["unmet_thresholds"],
                "distinct_evidence": sufficiency["distinct_evidence"],
                "independent_groups": sufficiency["independent_groups"],
                "mean_evidence_quality": sufficiency["mean_quality"],
                "verified_evidence": sufficiency["verified_evidence"],
            }
        )

    ranking.sort(key=lambda item: (not item["evidence_sufficient"], -item["net"], item["option_id"]))
    eligible = [item for item in ranking if item["evidence_sufficient"]]

    tie_candidates: list[str] = []
    selected_id = None
    reason = ""
    if not eligible:
        reason = "no option cleared the task-class evidence threshold"
    else:
        if len(eligible) > 1 and abs(eligible[0]["net"] - eligible[1]["net"]) <= policy["tie_tolerance"]:
            tie_candidates = sorted(
                item["option_id"] for item in eligible if abs(item["net"] - eligible[0]["net"]) <= policy["tie_tolerance"]
            )
            reason = f"options {', '.join(tie_candidates)} are tied within the policy tie tolerance"
        else:
            selected_id = eligible[0]["option_id"]
            reason = (
                f"{selected_id} carries the highest evidence-weighted net score {eligible[0]['net']} "
                f"among options meeting the {task_class} evidence threshold"
            )

    thresholds = policy["evidence_thresholds"]["by_task_class"].get(task_class, policy["evidence_thresholds"]["default"])
    decision_confidence = 0.0
    confidence_basis = "no option was selected"
    if selected_id:
        chosen = next(item for item in ranking if item["option_id"] == selected_id)
        ceiling = evidence_module.ceiling(chosen["evidence_refs"], register, policy, task_class)
        supporting = [claim for claim in weighted if claim.get("subject_ref") == selected_id and claim["polarity"] == "supports"]
        mean_claim_confidence = (
            _round(sum(claim["effective_confidence"] for claim in supporting) / len(supporting)) if supporting else 0.0
        )
        raw = min(mean_claim_confidence, ceiling["ceiling"])
        decision_confidence = _round(max(0.0, raw - chosen["contradiction_penalty"]))
        confidence_basis = (
            f"min(mean supporting claim confidence {mean_claim_confidence}, evidence ceiling {ceiling['ceiling']}) "
            f"less contradiction penalty {chosen['contradiction_penalty']}"
        )

    return {
        "operator_id": "convergent",
        "ranking": ranking,
        "selected_option_id": selected_id,
        "tie_candidates": tie_candidates,
        "rejected_alternatives": [
            {
                "option_id": item["option_id"],
                "reason": (
                    "; ".join(item["unmet_thresholds"])
                    if not item["evidence_sufficient"]
                    else f"lower evidence-weighted net score ({item['net']}) than the selection"
                ),
            }
            for item in ranking
            if item["option_id"] != selected_id
        ],
        "selection_reason": reason,
        "decision_confidence": decision_confidence,
        "decision_confidence_basis": confidence_basis,
        "decision_confidence_label": model["label"],
        "thresholds_applied": thresholds,
        "declared_confidence": "derived",
        "claims": [
            {
                "claim_id": "CV-CLAIM-1",
                "operator_id": "convergent",
                "statement": reason,
                "polarity": "neutral",
                "subject_ref": selected_id,
                "evidence_refs": [],
                "declared_confidence": "unknown",
                "effective_confidence": decision_confidence,
            }
        ],
    }
