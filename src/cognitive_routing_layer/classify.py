"""Deterministic signal extraction and task classification.

Classification is computed from normalized intake. A caller-supplied
`proposed_classification` is recorded and compared, never trusted: a caller
that picks its own task class picks its own level of scrutiny.
"""
from typing import Any


def extract_signals(intake: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    sensitive = set(policy["sensitive_data_kinds"])
    positions = {item["position"] for item in intake["stakeholder_positions"]}
    action = intake.get("requested_action") or {}

    fired: list[str] = []
    if len(intake["options"]) >= 2:
        fired.append("contested_options")
    if any(not item["explained"] for item in intake["observations"]):
        fired.append("unexplained_observation")
    if action.get("reversible") is False or any(not option["reversible"] for option in intake["options"]):
        fired.append("irreversibility")
    if sensitive & set(intake["data_scope"]):
        fired.append("sensitive_data_scope")
    if intake["permission_delta"]:
        fired.append("permission_change")
    if intake["external_parties"]:
        fired.append("external_impact")
    if intake["known_evidence_gaps"]:
        fired.append("declared_evidence_gap")
    if intake["deadline"]:
        fired.append("time_bound")
    if not intake["precedent_exists"]:
        fired.append("novel_domain")
    if len(intake["stakeholder_positions"]) >= 2 and len(positions) >= 2:
        fired.append("stakeholder_conflict")
    if len(intake["affected_systems"]) >= 2:
        fired.append("systemic_coupling")
    if intake["precedent_setting"]:
        fired.append("precedent_setting")
    return sorted(fired)


def _rule_matches(rule_id: str, intake: dict[str, Any]) -> bool:
    unexplained = [item for item in intake["observations"] if not item["explained"]]
    return {
        "CL-1": intake["artifact_kind"] == "code_change",
        "CL-2": intake["artifact_kind"] in {"proposal", "policy", "control_design"},
        "CL-3": len(unexplained) >= 1 and len(intake["options"]) <= 1,
        "CL-4": intake["decision_kind"] == "select_next_action" and len(intake["options"]) >= 2,
        "CL-5": intake["artifact_kind"] == "system_design",
        "CL-6": intake["decision_horizon"] in {"quarters", "years"},
    }[rule_id]


def classify(intake: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Return the computed classification with full provenance."""
    rules = sorted(policy["classification_rules"], key=lambda item: item["precedence"])
    matched = [rule for rule in rules if _rule_matches(rule["rule_id"], intake)]

    if matched:
        winner = matched[0]
        task_class = winner["task_class"]
        activated = winner["rule_id"]
        rejected = [
            {"task_class": rule["task_class"], "rule_id": rule["rule_id"], "reason": "lower precedence than the activated rule"}
            for rule in matched[1:]
        ]
    else:
        unsupported = policy["unsupported_classification_behavior"]
        task_class = unsupported["task_class"]
        activated = None
        rejected = [
            {"task_class": rule["task_class"], "rule_id": rule["rule_id"], "reason": "predicate did not match normalized intake"}
            for rule in rules
        ]

    proposed = intake.get("proposed_classification")
    mismatch = bool(proposed) and proposed != task_class

    return {
        "task_class": task_class,
        "classification_source": "computed",
        "classification_policy_id": policy["policy_id"],
        "classification_policy_version": policy["version"],
        "activated_rule_id": activated,
        "rejected_classifications": rejected,
        "deterministic_basis": "ordered first-match over classification_rules against normalized intake",
        "caller_proposed_classification": proposed,
        "caller_proposal_honored": False,
        "caller_proposal_mismatch": mismatch,
        "manual_override": None,
        "manual_override_owner": None,
        "manual_override_reason": None,
    }
