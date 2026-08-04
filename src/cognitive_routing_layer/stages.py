"""Append-only, hash-linked stage records.

Stage ordering stops post-hoc justification only if a later stage cannot
rewrite an earlier one. Each completed stage record carries the hash of its
own content and the hash of the previous record, so any later mutation of a
prior stage breaks the chain and the metacognitive audit detects it. The
ledger stores the chain head, which makes receipt tampering detectable after
issuance as well.
"""
from typing import Any

from .io import digest

GENESIS = "0" * 64


class StageChainError(RuntimeError):
    pass


class StageChain:
    """Ordered, append-only sequence of stage records."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def append(
        self,
        stage: str,
        operator_id: str,
        operator_version: str,
        status: str,
        content: dict[str, Any],
        recorded_at: str,
    ) -> dict[str, Any]:
        previous_hash = self._records[-1]["record_hash"] if self._records else GENESIS
        body = {
            "sequence": len(self._records),
            "stage": stage,
            "operator_id": operator_id,
            "operator_version": operator_version,
            "status": status,
            "recorded_at": recorded_at,
            "content_hash": digest(content),
            "previous_hash": previous_hash,
        }
        record = {**body, "record_hash": digest(body)}
        self._records.append(record)
        return record

    @property
    def records(self) -> list[dict[str, Any]]:
        return [dict(record) for record in self._records]

    @property
    def head(self) -> str:
        return self._records[-1]["record_hash"] if self._records else GENESIS

    def verify(self, contents: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
        """Re-derive every hash from the supplied content and report breaks."""
        findings: list[dict[str, Any]] = []
        previous_hash = GENESIS
        for record in self._records:
            sequence = record["sequence"]
            if record["previous_hash"] != previous_hash:
                findings.append(
                    {
                        "finding_id": "MC-CHAIN-LINK-BROKEN",
                        "sequence": sequence,
                        "stage": record["stage"],
                        "detail": "previous_hash does not match the preceding record",
                    }
                )
            if sequence in contents:
                recomputed = digest(contents[sequence])
                if recomputed != record["content_hash"]:
                    findings.append(
                        {
                            "finding_id": "MC-CHAIN-CONTENT-MUTATED",
                            "sequence": sequence,
                            "stage": record["stage"],
                            "detail": "stage content changed after the record was sealed",
                        }
                    )
            body = {key: value for key, value in record.items() if key != "record_hash"}
            if digest(body) != record["record_hash"]:
                findings.append(
                    {
                        "finding_id": "MC-CHAIN-RECORD-MUTATED",
                        "sequence": sequence,
                        "stage": record["stage"],
                        "detail": "record_hash does not match the record body",
                    }
                )
            previous_hash = record["record_hash"]
        return findings
