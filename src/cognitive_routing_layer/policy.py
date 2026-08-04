"""Load and validate the versioned control files.

Both control files are JSON-compatible YAML so the standard-library runtime
can read them, matching the leverage-engine convention.
"""
from typing import Any

from .io import digest, load_json
from .paths import OPERATOR_REGISTRY, ROUTING_POLICY


class PolicyError(ValueError):
    pass


V01_OPERATORS = {
    "first-principles",
    "systemic",
    "divergent",
    "abductive",
    "critical",
    "inverted",
    "second-order",
    "convergent",
    "metacognitive",
}


def validate_operator_registry(registry: dict[str, Any]) -> None:
    if registry.get("version") != "0.1.0":
        raise PolicyError("unknown operator registry version")
    ids = {item["operator_id"] for item in registry.get("operators", [])}
    if ids != V01_OPERATORS:
        raise PolicyError(f"operator registry does not match the locked v0.1 set: {sorted(ids ^ V01_OPERATORS)}")
    if registry.get("confidence_factors") != {"high": 1.0, "medium": 0.75, "low": 0.5, "unknown": 0.0}:
        raise PolicyError("confidence factors do not match the approved ecosystem baseline")
    for operator in registry["operators"]:
        for field in (
            "purpose",
            "selection_conditions",
            "input_contract",
            "required_transformations",
            "output_contract",
            "evidence_requirements",
            "assumption_handling",
            "confidence_rules",
            "failure_conditions",
            "prohibited_behaviors",
            "evaluation_fixtures",
        ):
            if not operator.get(field):
                raise PolicyError(f"{operator['operator_id']}: contract is missing {field}")
    audit = next(item for item in registry["operators"] if item["operator_id"] == "metacognitive")
    if audit["selection_conditions"].get("mandatory") is not True:
        raise PolicyError("the metacognitive audit must be mandatory")


def validate_routing_policy(policy: dict[str, Any]) -> None:
    if policy.get("version") != "0.1.0":
        raise PolicyError("unknown routing policy version")
    if policy.get("operator_registry_version") != "0.1.0":
        raise PolicyError("routing policy targets a different operator registry version")
    determinism = policy.get("determinism_contract", {})
    if determinism.get("classification_is_computed") is not True:
        raise PolicyError("classification must be computed by the engine")
    authorization = policy.get("authorization_model", {})
    if authorization.get("default_verifier") != "unavailable":
        raise PolicyError("the default CASA verifier must be unavailable in v0.1")
    required_auth_conditions = 7
    if len(authorization.get("authorized_requires_all", [])) < required_auth_conditions:
        raise PolicyError("the authorization model is missing required conditions")
    for route in policy.get("routes", []):
        required = set(route["required_operators"])
        if "metacognitive" not in required:
            raise PolicyError(f"{route['task_class']}: the metacognitive audit is not required")
        if "convergent" not in required:
            raise PolicyError(f"{route['task_class']}: convergent is not required")
        unknown = required - V01_OPERATORS
        if unknown:
            raise PolicyError(f"{route['task_class']}: unknown operators {sorted(unknown)}")
    precedence = [item["order"] for item in policy.get("conflict_resolution_precedence", [])]
    if precedence != sorted(precedence) or not precedence:
        raise PolicyError("conflict resolution precedence must be ordered")


def load_controls() -> dict[str, Any]:
    registry = load_json(OPERATOR_REGISTRY)
    policy = load_json(ROUTING_POLICY)
    validate_operator_registry(registry)
    validate_routing_policy(policy)
    return {
        "registry": registry,
        "policy": policy,
        "operators_by_id": {item["operator_id"]: item for item in registry["operators"]},
        "checksums": {
            "operator_registry_sha256": digest(registry),
            "routing_policy_sha256": digest(policy),
        },
    }
