"""Deterministic route selection.

No model call participates in routing. Given a classification and the fired
signals, the route and its per-operator rationale are a pure function of the
versioned policy.
"""
from typing import Any


class RoutingError(ValueError):
    pass


def select_route(classification: dict[str, Any], signals: list[str], controls: dict[str, Any]) -> dict[str, Any]:
    policy = controls["policy"]
    operators_by_id = controls["operators_by_id"]
    task_class = classification["task_class"]

    if task_class == "UNSUPPORTED":
        unsupported = policy["unsupported_classification_behavior"]
        return {
            "task_class": task_class,
            "operators": [],
            "stage_sequence": [],
            "route_depth": 0,
            "route_supported": False,
            "coverage_gap_reason": unsupported["reason_code"],
            "coverage_gap_statement": unsupported["statement"],
        }

    route_policy = next((item for item in policy["routes"] if item["task_class"] == task_class), None)
    if route_policy is None:
        raise RoutingError(f"no route defined for classification {task_class}")

    fired = set(signals)
    selected: list[dict[str, Any]] = []

    for operator_id in route_policy["required_operators"]:
        contract = operators_by_id[operator_id]
        selected.append(
            {
                "operator_id": operator_id,
                "operator_version": contract["version"],
                "stage": contract["stage"],
                "selection_basis": "required",
                "activated_by": [],
                "selection_rationale": (
                    f"{operator_id} is required for every {task_class} route by policy "
                    f"{policy['policy_id']}. Purpose: {contract['purpose'].split('.')[0]}."
                ),
            }
        )

    for conditional in route_policy["conditional_operators"]:
        activating = sorted(fired & set(conditional["activated_by"]))
        contract = operators_by_id[conditional["operator_id"]]
        if activating:
            selected.append(
                {
                    "operator_id": conditional["operator_id"],
                    "operator_version": contract["version"],
                    "stage": contract["stage"],
                    "selection_basis": "conditional",
                    "activated_by": activating,
                    "selection_rationale": (
                        f"{conditional['operator_id']} was activated for this {task_class} route by "
                        f"signal(s) {', '.join(activating)}."
                    ),
                }
            )

    not_selected = [
        {
            "operator_id": conditional["operator_id"],
            "reason": "no activating signal fired",
            "would_activate_on": sorted(conditional["activated_by"]),
        }
        for conditional in route_policy["conditional_operators"]
        if not (fired & set(conditional["activated_by"]))
    ]
    deferred = [
        {"operator_id": item["operator_id"], "reason": "deferred to v0.2", "detail": item["deferral_reason"]}
        for item in controls["registry"]["deferred_operators"]
    ]

    stage_order = policy["stage_order"]
    selected.sort(key=lambda item: (stage_order.index(item["stage"]), item["operator_id"]))

    execution = policy["execution_model"]
    depth = len(selected)
    if depth < execution["min_route_depth"]:
        raise RoutingError(f"route depth {depth} is below the policy minimum {execution['min_route_depth']}")
    if depth > execution["max_route_depth"]:
        raise RoutingError(f"route depth {depth} exceeds the policy maximum {execution['max_route_depth']}")

    stage_sequence: list[dict[str, Any]] = []
    for stage in stage_order:
        members = [item["operator_id"] for item in selected if item["stage"] == stage]
        if members:
            stage_sequence.append(
                {
                    "stage": stage,
                    "operators": members,
                    "execution": "parallel_eligible" if len(members) > 1 else "single",
                    "serialized_order": members,
                }
            )

    return {
        "task_class": task_class,
        "operators": selected,
        "stage_sequence": stage_sequence,
        "route_depth": depth,
        "route_supported": True,
        "operators_not_selected": not_selected,
        "operators_deferred": deferred,
    }
