from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = ROOT / "spec"
SCHEMA_DIR = ROOT / "schemas"
FIXTURE_DIR = ROOT / "tests" / "fixtures"
EXAMPLE_DIR = ROOT / "examples"

OPERATOR_REGISTRY = SPEC_DIR / "operators.yaml"
ROUTING_POLICY = SPEC_DIR / "routing-policy.yaml"


def resolve_run(value: str) -> Path:
    """Accept a fixture directory, an explicit file, or a bare fixture name."""
    candidate = Path(value)
    if candidate.is_dir():
        return candidate / "run.json"
    if candidate.is_file():
        return candidate
    named = FIXTURE_DIR / value / "run.json"
    if named.is_file():
        return named
    raise FileNotFoundError(f"Run input not found: {value}")
