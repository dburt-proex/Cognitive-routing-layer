"""The authorization boundary.

Analytical confidence and action authorization are separate controls. The
structural guarantee is enforced by this module's interface: `evaluate` never
receives a confidence value, a coverage value, or a gate result. There is no
argument it could read to let a well-supported recommendation authorize
itself. `tests/test_acceptance.py` asserts this by inspecting the signature.

A field reading `source: CASA` proves nothing. An authorization is accepted
only when a configured verifier confirms it, the binding matches the
recommended action, the window is open, and the nonce is unused. v0.1 ships
no authentic CASA verifier: the default returns VERIFICATION_UNAVAILABLE and
routes to REVIEW. `TestAdapterVerifier` exists for fixtures, announces itself
in the receipt, and must never be presented as a CASA integration.
"""
import hmac
from datetime import datetime
from hashlib import sha256
from typing import Any, Protocol

from .io import canonical_json, digest

NOT_REQUESTED = "NOT_REQUESTED"
PENDING_CASA = "PENDING_CASA"
VERIFICATION_UNAVAILABLE = "VERIFICATION_UNAVAILABLE"
AUTHORIZED = "AUTHORIZED"
DENIED = "DENIED"


def action_hash(requested_action: dict[str, Any]) -> str:
    return digest(
        {
            "kind": requested_action["kind"],
            "target": requested_action["target"],
            "principal": requested_action["principal"],
            "resource": requested_action["resource"],
            "data_scope": sorted(requested_action.get("data_scope", [])),
        }
    )


class CasaVerifier(Protocol):
    name: str
    is_authentic: bool

    def verify(self, authorization: dict[str, Any]) -> dict[str, Any]:
        ...


class UnavailableVerifier:
    """The default. v0.1 cannot authenticate a real CASA authorization."""

    name = "unavailable"
    is_authentic = False

    def verify(self, authorization: dict[str, Any]) -> dict[str, Any]:
        return {
            "verified": False,
            "reason": "no CASA verifier is configured; v0.1 cannot authenticate an authorization object",
            "terminal": True,
        }


class TestAdapterVerifier:
    """Fixture-only verifier. Never a production integration."""

    name = "test_adapter"
    is_authentic = False

    def __init__(self, shared_secret: bytes) -> None:
        self._secret = shared_secret

    def _expected(self, authorization: dict[str, Any]) -> str:
        signed = {key: authorization[key] for key in sorted(authorization) if key != "signature"}
        return hmac.new(self._secret, canonical_json(signed).encode("utf-8"), sha256).hexdigest()

    def verify(self, authorization: dict[str, Any]) -> dict[str, Any]:
        signature = authorization.get("signature", "")
        if not hmac.compare_digest(signature, self._expected(authorization)):
            return {"verified": False, "reason": "signature does not match the authorization body", "terminal": False}
        return {"verified": True, "reason": "test adapter signature matched", "terminal": False}


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate(
    requested_action: dict[str, Any] | None,
    authorization: dict[str, Any] | None,
    verifier: CasaVerifier,
    run_timestamp: str,
    receipt_binding: str,
    seen_nonces: set[str],
) -> dict[str, Any]:
    """Decide the authorization status.

    Deliberately takes no confidence, coverage, or gate argument.
    """
    base = {
        "verifier": verifier.name,
        "verifier_is_authentic": verifier.is_authentic,
        "checks": [],
        "authorization_id": None,
        "issuer": None,
        # The nonce is carried into the receipt so the ledger can detect a
        # replay on a later run. Without it there is nothing to compare against.
        "nonce": None,
        "derived_from_confidence": False,
    }

    if not requested_action:
        return {**base, "status": NOT_REQUESTED, "reason": "the intake requested no external action"}

    if not authorization:
        return {
            **base,
            "status": PENDING_CASA,
            "reason": "an action was requested and no CASA authorization object was supplied",
        }

    base["authorization_id"] = authorization.get("authorization_id")
    base["issuer"] = authorization.get("issuer")
    base["nonce"] = authorization.get("nonce")

    result = verifier.verify(authorization)
    checks: list[dict[str, Any]] = [
        {"check": "verifier_signature", "passed": bool(result["verified"]), "detail": result["reason"]}
    ]
    if not result["verified"]:
        status = VERIFICATION_UNAVAILABLE if result.get("terminal") else DENIED
        return {**base, "status": status, "reason": result["reason"], "checks": checks}

    expected_action = action_hash(requested_action)
    checks.append(
        {
            "check": "action_binding",
            "passed": authorization.get("action_hash") == expected_action,
            "detail": "authorization action_hash must equal the hash of the requested action",
        }
    )
    checks.append(
        {
            "check": "principal_binding",
            "passed": authorization.get("principal") == requested_action.get("principal"),
            "detail": "authorization principal must equal the acting principal",
        }
    )
    checks.append(
        {
            "check": "resource_binding",
            "passed": authorization.get("resource") == requested_action.get("resource"),
            "detail": "authorization resource must equal the target resource",
        }
    )
    checks.append(
        {
            "check": "receipt_binding",
            "passed": authorization.get("bound_receipt_hash") == receipt_binding,
            "detail": "authorization must be bound to this run's recommendation",
        }
    )
    try:
        expired = _parse(authorization["expires_at"]) <= _parse(run_timestamp)
        detail = "authorization must not be expired at run time"
    except (KeyError, ValueError):
        expired = True
        detail = "authorization carries no parseable expires_at"
    checks.append({"check": "expiry", "passed": not expired, "detail": detail})

    nonce = authorization.get("nonce")
    checks.append(
        {
            "check": "replay",
            "passed": bool(nonce) and nonce not in seen_nonces,
            "detail": "authorization nonce must be unused in this ledger",
        }
    )

    failed = [item["check"] for item in checks if not item["passed"]]
    if failed:
        return {
            **base,
            "status": DENIED,
            "reason": f"authorization failed binding checks: {', '.join(failed)}",
            "checks": checks,
        }

    return {**base, "status": AUTHORIZED, "reason": "all authorization binding checks passed", "checks": checks}


def compose_execution(gate_result: str, evidence_sufficient: bool, authorization_status: str) -> dict[str, Any]:
    """Compose the evidence gate and the authorization gate into one outcome.

    Confidence never grants permission; authorization never cures insufficient
    evidence. Proceeding requires both.
    """
    authorized = authorization_status == AUTHORIZED
    eligible = gate_result == "ALLOW" and evidence_sufficient

    if eligible and authorized:
        outcome = "MAY_PROCEED"
    elif eligible and not authorized:
        outcome = "NOT_AUTHORIZED"
    elif not eligible and authorized:
        outcome = "REVIEW"
    else:
        outcome = "REVIEW" if gate_result != "HALT" else "HALT"

    return {
        "execution_outcome": outcome,
        "execution_authorized": outcome == "MAY_PROCEED",
        "recommendation_eligible": eligible,
        "authorization_status": authorization_status,
        "composition_rule": "confidence never grants permission; authorization never cures insufficient evidence",
    }
