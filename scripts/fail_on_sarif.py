#!/usr/bin/env python3
"""Exit 1 when a CodeQL SARIF file contains a high or critical finding.

GitHub's analyze action uploads results and still exits 0. This gate is what
makes high and critical CodeQL alerts fail the pull request.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# CodeQL security-severity: 7.0 high, 9.0 critical.
HIGH_THRESHOLD = 7.0


def finding_is_blocking(result: dict, rules: dict[str, dict]) -> tuple[bool, str]:
    rule = rules.get(result.get("ruleId", ""), {})
    raw = rule.get("properties", {}).get("security-severity")
    score: float | None
    try:
        score = float(raw) if raw is not None else None
    except (TypeError, ValueError):
        score = None
    level = result.get("level", "")
    blocking = (score is not None and score >= HIGH_THRESHOLD) or level == "error"
    detail = f"{result.get('ruleId')} level={level or 'unset'} security-severity={raw}"
    return blocking, detail


def main(path: Path) -> int:
    files = sorted(path.rglob("*.sarif")) if path.is_dir() else [path]
    files = [item for item in files if item.is_file()]
    if not files:
        print(f"No SARIF files found under {path}", file=sys.stderr)
        return 1

    blocking: list[str] = []
    for sarif_file in files:
        data = json.loads(sarif_file.read_text(encoding="utf-8"))
        for run in data.get("runs", []):
            driver = run.get("tool", {}).get("driver", {})
            rules = {rule.get("id"): rule for rule in driver.get("rules", [])}
            for result in run.get("results", []):
                is_blocking, detail = finding_is_blocking(result, rules)
                if is_blocking:
                    blocking.append(f"{sarif_file.name}: {detail}")

    if blocking:
        print("High or critical CodeQL findings:")
        for line in blocking:
            print(f"  {line}")
        return 1

    print("No high or critical CodeQL findings.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} SARIF_FILE_OR_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
