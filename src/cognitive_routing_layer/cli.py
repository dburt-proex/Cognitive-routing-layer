import argparse
import json
import sys
from pathlib import Path

from .authorization import TestAdapterVerifier, UnavailableVerifier
from .io import canonical_json, write_json
from .paths import resolve_run
from .runner import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cognitive-routing-layer",
        description="Run the deterministic Cognitive Routing Layer over a structured problem statement.",
    )
    parser.add_argument("--run", required=True, help="Run directory, run.json path, or fixture name")
    parser.add_argument("--ledger", help="Optional append-only JSONL receipt ledger path")
    parser.add_argument("--output", help="Optional JSON output path")
    parser.add_argument(
        "--casa-test-adapter-secret",
        help=(
            "Fixture-only CASA verifier secret. This is a test adapter, not a CASA integration; "
            "the receipt records verifier_is_authentic=false whenever it is used."
        ),
    )
    parser.add_argument("--verify-determinism", action="store_true", help="Replay the run and fail if the receipts differ")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run_path = resolve_run(args.run)
        ledger = Path(args.ledger) if args.ledger else None
        verifier = (
            TestAdapterVerifier(args.casa_test_adapter_secret.encode("utf-8"))
            if args.casa_test_adapter_secret
            else UnavailableVerifier()
        )
        receipt = run(run_path, ledger, verifier)

        if args.verify_determinism:
            replay = run(run_path, ledger, verifier)
            first = {**receipt, "ledger_receipt": {**receipt["ledger_receipt"], "appended": False}}
            second = {**replay, "ledger_receipt": {**replay["ledger_receipt"], "appended": False}}
            if canonical_json(first) != canonical_json(second):
                raise RuntimeError("determinism verification failed: replay produced a different receipt")

        if args.output:
            write_json(Path(args.output), receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if receipt["gate"]["gate_result"] != "HALT" else 1
    except Exception as exc:
        print(json.dumps({"gate_result": "HALT", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
