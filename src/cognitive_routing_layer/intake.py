"""Intake validation and normalization.

Determinism has to begin at the boundary. If two callers can express the same
problem in two shapes, or can declare their own task class, the router's
determinism is decorative. Every executable entry point passes through
`normalize_intake`, which validates against the intake schema, canonicalizes
the representation, and produces the hash that the whole run is keyed on.
"""
from typing import Any

from .io import digest
from .paths import SCHEMA_DIR
from .schema_validation import SchemaValidationError, load_and_validate

INTAKE_SCHEMA = SCHEMA_DIR / "problem-intake.schema.json"

_SCALAR_LIST_FIELDS = (
    "constraints",
    "data_scope",
    "permission_delta",
    "external_parties",
    "affected_systems",
    "known_evidence_gaps",
)

_DEFAULTS: dict[str, Any] = {
    "constraints": [],
    "options": [],
    "observations": [],
    "data_scope": [],
    "permission_delta": [],
    "external_parties": [],
    "affected_systems": [],
    "stakeholder_positions": [],
    "known_evidence_gaps": [],
    "deadline": None,
    "precedent_exists": True,
    "precedent_setting": False,
    "proposed_classification": None,
    "requested_action": None,
}


class IntakeError(ValueError):
    """Raised when intake cannot be trusted enough to classify."""


def normalize_intake(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise IntakeError("intake must be an object")

    intake = {**_DEFAULTS, **{key: value for key, value in raw.items() if value is not None or key in raw}}
    for key, default in _DEFAULTS.items():
        if intake.get(key) is None and default is not None:
            intake[key] = default

    try:
        load_and_validate(intake, INTAKE_SCHEMA)
    except SchemaValidationError as exc:
        raise IntakeError(f"intake failed schema validation: {exc}") from exc

    statement = intake["problem_statement"].strip()
    if len(statement.split()) < 5:
        raise IntakeError("problem_statement must contain at least five words to be classifiable")

    normalized: dict[str, Any] = {
        "problem_statement": statement,
        "artifact_kind": intake["artifact_kind"].strip().lower(),
        "decision_kind": intake["decision_kind"].strip().lower(),
        "decision_horizon": intake["decision_horizon"].strip().lower(),
        "precedent_exists": bool(intake["precedent_exists"]),
        "precedent_setting": bool(intake["precedent_setting"]),
        "deadline": intake["deadline"],
        "proposed_classification": intake["proposed_classification"],
        "requested_action": intake["requested_action"],
    }
    for field in _SCALAR_LIST_FIELDS:
        normalized[field] = sorted({str(item).strip().lower() for item in intake[field]})

    normalized["options"] = sorted(
        (
            {
                "option_id": option["option_id"].strip(),
                "label": option["label"].strip(),
                "mechanism": option["mechanism"].strip(),
                "tradeoff": option["tradeoff"].strip(),
                "reversible": bool(option["reversible"]),
            }
            for option in intake["options"]
        ),
        key=lambda item: item["option_id"],
    )
    normalized["observations"] = sorted(
        (
            {
                "observation_id": observation["observation_id"].strip(),
                "statement": observation["statement"].strip(),
                "explained": bool(observation["explained"]),
            }
            for observation in intake["observations"]
        ),
        key=lambda item: item["observation_id"],
    )
    normalized["stakeholder_positions"] = sorted(
        (
            {"party": position["party"].strip(), "position": position["position"].strip().lower()}
            for position in intake["stakeholder_positions"]
        ),
        key=lambda item: (item["party"], item["position"]),
    )

    option_ids = [option["option_id"] for option in normalized["options"]]
    if len(set(option_ids)) != len(option_ids):
        raise IntakeError("duplicate option_id in intake")
    observation_ids = [item["observation_id"] for item in normalized["observations"]]
    if len(set(observation_ids)) != len(observation_ids):
        raise IntakeError("duplicate observation_id in intake")

    return normalized


def intake_hash(normalized: dict[str, Any]) -> str:
    return digest(normalized)
