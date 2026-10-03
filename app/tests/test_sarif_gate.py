"""The CodeQL fail-on-high helper used by the workflow."""

import importlib.util
import json
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "fail_on_sarif.py"
_SPEC = importlib.util.spec_from_file_location("fail_on_sarif", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
fail_on_sarif = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(fail_on_sarif)


def _write_sarif(path: Path, results: list[dict], rules: list[dict]) -> None:
    document = {
        "runs": [
            {
                "tool": {"driver": {"rules": rules}},
                "results": results,
            }
        ]
    }
    path.write_text(json.dumps(document), encoding="utf-8")


def test_high_severity_fails(tmp_path):
    sarif = tmp_path / "python.sarif"
    _write_sarif(
        sarif,
        results=[{"ruleId": "py/sql-injection", "level": "error"}],
        rules=[{"id": "py/sql-injection", "properties": {"security-severity": "9.0"}}],
    )
    assert fail_on_sarif.main(sarif) == 1


def test_medium_severity_passes(tmp_path):
    sarif = tmp_path / "python.sarif"
    _write_sarif(
        sarif,
        results=[{"ruleId": "py/log-injection", "level": "warning"}],
        rules=[{"id": "py/log-injection", "properties": {"security-severity": "5.0"}}],
    )
    assert fail_on_sarif.main(sarif) == 0


def test_clean_sarif_passes(tmp_path):
    sarif = tmp_path / "python.sarif"
    _write_sarif(sarif, results=[], rules=[])
    assert fail_on_sarif.main(sarif) == 0
