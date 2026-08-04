"""Evidence resolution, ceilings, and sufficiency.

Two ideas carry most of the weight here.

First, a claim cannot outrank its evidence. The declared confidence of any
claim is capped by a ceiling computed from how much evidence it resolves to,
how good that evidence is, and whether the evidence is independent. This
mirrors the VIL invariant `vil_score = min(weighted_signal_score,
verifiability_score)` so the two systems agree about what evidence buys.

Second, declared evidence is not verified evidence. Every record carries a
verification_state, and the engine reports which state each piece of evidence
was in when it was used.
"""
from typing import Any


class EvidenceError(ValueError):
    pass


def build_register(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    register: dict[str, dict[str, Any]] = {}
    for record in records:
        evidence_id = record["evidence_id"]
        if evidence_id in register:
            raise EvidenceError(f"duplicate evidence_id {evidence_id}")
        register[evidence_id] = record
    return register


def resolve(refs: list[str], register: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Split references into resolved records and unresolvable (fabricated) ids."""
    resolved = [register[ref] for ref in refs if ref in register]
    unresolved = sorted({ref for ref in refs if ref not in register})
    return resolved, unresolved


def ceiling(refs: list[str], register: dict[str, dict[str, Any]], policy: dict[str, Any], task_class: str) -> dict[str, Any]:
    """Compute the confidence ceiling that this evidence set can support."""
    model = policy["confidence_model"]
    bands = model["evidence_ceiling_bands"]
    thresholds = policy["evidence_thresholds"]["by_task_class"].get(task_class, policy["evidence_thresholds"]["default"])

    resolved, unresolved = resolve(refs, register)
    distinct = len({record["evidence_id"] for record in resolved})

    band_index = 0
    for index, band in enumerate(bands):
        if distinct >= band["min_distinct_evidence"]:
            band_index = index

    quality_values = [record["quality"] for record in resolved]
    mean_quality = round(sum(quality_values) / len(quality_values), 4) if quality_values else 0.0
    quality_penalty_applied = False
    if resolved and mean_quality < thresholds["minimum_evidence_quality"]:
        band_index = max(0, band_index - 1)
        quality_penalty_applied = True

    value = bands[band_index]["ceiling"]

    groups = {record["independence_group"] for record in resolved}
    independence_cap_applied = False
    if resolved and len(groups) < 2 and value > 0.75:
        value = 0.75
        independence_cap_applied = True

    verified_states = set(policy["verified_states"])
    verified_count = sum(1 for record in resolved if record["verification_state"] in verified_states)

    return {
        "ceiling": value,
        "distinct_evidence": distinct,
        "independent_groups": len(groups),
        "mean_quality": mean_quality,
        "verified_evidence": verified_count,
        "unverified_evidence": len(resolved) - verified_count,
        "unresolved_refs": unresolved,
        "quality_penalty_applied": quality_penalty_applied,
        "independence_cap_applied": independence_cap_applied,
    }


def option_sufficiency(
    refs: list[str],
    register: dict[str, dict[str, Any]],
    policy: dict[str, Any],
    task_class: str,
) -> dict[str, Any]:
    """Decide whether an option's evidence clears the task-class threshold."""
    thresholds = policy["evidence_thresholds"]["by_task_class"].get(task_class, policy["evidence_thresholds"]["default"])
    resolved, unresolved = resolve(refs, register)
    distinct = len({record["evidence_id"] for record in resolved})
    groups = {record["independence_group"] for record in resolved}
    quality_values = [record["quality"] for record in resolved]
    mean_quality = round(sum(quality_values) / len(quality_values), 4) if quality_values else 0.0
    verified_states = set(policy["verified_states"])
    verified = [record for record in resolved if record["verification_state"] in verified_states]

    unmet: list[str] = []
    if distinct < thresholds["min_distinct_evidence_per_option"]:
        unmet.append(
            f"requires {thresholds['min_distinct_evidence_per_option']} distinct evidence records, resolved {distinct}"
        )
    if len(groups) < thresholds["min_independent_sources_per_option"]:
        unmet.append(
            f"requires {thresholds['min_independent_sources_per_option']} independent sources, resolved {len(groups)}"
        )
    if resolved and mean_quality < thresholds["minimum_evidence_quality"]:
        unmet.append(f"requires mean quality {thresholds['minimum_evidence_quality']}, resolved {mean_quality}")
    if not resolved:
        unmet.append("no evidence resolved for this option")
    if thresholds["require_verified_evidence"] and not verified:
        unmet.append("task class requires at least one INTEGRITY_CHECKED or AUTHORITATIVE evidence record")
    if unresolved:
        unmet.append(f"unresolvable evidence references {unresolved}")

    return {
        "evidence_sufficient": not unmet,
        "unmet_thresholds": unmet,
        "thresholds_applied": thresholds,
        "distinct_evidence": distinct,
        "independent_groups": len(groups),
        "mean_quality": mean_quality,
        "verified_evidence": len(verified),
        "unresolved_refs": unresolved,
    }
