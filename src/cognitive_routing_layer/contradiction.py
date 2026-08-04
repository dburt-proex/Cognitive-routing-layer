"""Structural contradiction detection between operator conclusions.

Detection is structural rather than semantic: two claims contradict when they
address the same subject with opposing polarity. That is deterministic and
reproducible. It will miss contradictions expressed in different vocabulary,
which is a stated limitation rather than a hidden one, and the audit reports
the detection method used so a reader knows what was and was not checked.
"""
from typing import Any


def detect(claims: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    rules = policy["contradiction_rules"]
    by_subject: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        subject = claim.get("subject_ref")
        if subject and claim.get("polarity") in {"supports", "opposes"}:
            by_subject.setdefault(subject, []).append(claim)

    contradictions: list[dict[str, Any]] = []
    for subject in sorted(by_subject):
        supporting = sorted(
            (item for item in by_subject[subject] if item["polarity"] == "supports"),
            key=lambda item: item["claim_id"],
        )
        opposing = sorted(
            (item for item in by_subject[subject] if item["polarity"] == "opposes"),
            key=lambda item: item["claim_id"],
        )
        for left in supporting:
            for right in opposing:
                severity = (
                    "material"
                    if left["effective_confidence"] >= 0.5 and right["effective_confidence"] >= 0.5
                    else "minor"
                )
                contradictions.append(
                    {
                        "contradiction_id": f"RCP-CON-{left['claim_id']}-{right['claim_id']}",
                        "subject_ref": subject,
                        "supporting_claim_id": left["claim_id"],
                        "supporting_operator": left["operator_id"],
                        "supporting_confidence": left["effective_confidence"],
                        "opposing_claim_id": right["claim_id"],
                        "opposing_operator": right["operator_id"],
                        "opposing_confidence": right["effective_confidence"],
                        "severity": severity,
                        "disposition": "unresolved",
                        "disposition_owner": None,
                        "detection_method": rules["detection"],
                    }
                )
    return contradictions


def unresolved_material(contradictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in contradictions
        if item["severity"] == "material" and item["disposition"] == "unresolved"
    ]
