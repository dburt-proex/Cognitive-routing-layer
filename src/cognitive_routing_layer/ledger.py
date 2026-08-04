"""Idempotent append-only receipt ledger.

This is a local handoff record, not a durable decision store. The Shared
Decision Ledger and Mirdexx own durable retention; this file exists so a run
has a verifiable local receipt and so replayed authorization nonces are
detectable. Matches the leverage-engine ledger contract.
"""
import json
from pathlib import Path
from typing import Any

from .io import canonical_json, digest


class LedgerError(RuntimeError):
    pass


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def seen_nonces(path: Path | None) -> set[str]:
    if path is None:
        return set()
    nonces: set[str] = set()
    for record in _read(path):
        nonce = (record.get("authorization") or {}).get("nonce")
        if nonce:
            nonces.add(nonce)
    return nonces


def append_idempotent(path: Path | None, record: dict[str, Any]) -> dict[str, Any]:
    receipt_digest = digest(record)
    receipt = {
        "record_id": record["record_id"],
        "sha256": receipt_digest,
        "appended": False,
        "persisted": path is not None,
    }
    if path is None:
        return receipt

    path.parent.mkdir(parents=True, exist_ok=True)
    for existing in _read(path):
        if existing.get("record_id") == record["record_id"]:
            if digest(existing) != receipt_digest:
                raise LedgerError(f"record ID {record['record_id']} already exists with different content")
            return receipt

    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(record) + "\n")
    receipt["appended"] = True
    return receipt


def verify_receipt(path: Path, record_id: str, expected_sha256: str) -> dict[str, Any]:
    """Detect tampering with a receipt after issuance."""
    for existing in _read(path):
        if existing.get("record_id") == record_id:
            actual = digest(existing)
            return {
                "found": True,
                "intact": actual == expected_sha256,
                "expected_sha256": expected_sha256,
                "actual_sha256": actual,
            }
    return {"found": False, "intact": False, "expected_sha256": expected_sha256, "actual_sha256": None}
