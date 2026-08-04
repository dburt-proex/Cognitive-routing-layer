"""Treat supplied content as untrusted data, never as instructions.

Evidence excerpts and operator payloads arrive from outside the trust
boundary. Text that looks like an instruction to the reader is flagged and the
carrying record is downgraded so it can never satisfy a verified-evidence
threshold. The engine never executes text found in a record.
"""
import re
from typing import Any

_INJECTION_PATTERNS = (
    r"ignore (all |the |previous |prior )*instructions",
    r"disregard (all |the |previous |prior )*(instructions|rules|policy)",
    r"you are now",
    r"system prompt",
    r"reveal (the )?(secret|token|key|password)",
    r"act as (an? )?(admin|root|developer mode)",
    r"override (the )?(policy|gate|authorization)",
    r"mark this as (verified|authorized|approved)",
)

_COMPILED = tuple(re.compile(pattern, re.IGNORECASE) for pattern in _INJECTION_PATTERNS)


def detect_untrusted_instruction(text: str) -> bool:
    return any(pattern.search(text) for pattern in _COMPILED)


def normalize_evidence_record(record: dict[str, Any]) -> dict[str, Any]:
    """Flag instruction-like evidence text and downgrade its verification state."""
    normalized = dict(record)
    inspected = " ".join(
        str(normalized.get(field, "")) for field in ("excerpt", "claim_supported", "locator", "source_id")
    )
    detected = detect_untrusted_instruction(inspected)
    normalized["untrusted_instruction_detected"] = detected
    if detected:
        normalized["verification_state"] = "UNVERIFIED"
        normalized["quality"] = 0
    return normalized
