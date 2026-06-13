#!/usr/bin/env python3
"""Validate execution feedback blocks in case-gen files."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


RESULTS_REQUIRING_CLASS = {"fail", "blocked", "flaky"}
VALID_CLASSES = {
    "product_bug",
    "test_case_bug",
    "test_data_issue",
    "environment_issue",
    "flaky_test",
    "obsolete_expectation",
}


def load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("YAML input requires PyYAML. Use JSON or install PyYAML.") from exc
        return yaml.safe_load(text)
    return json.loads(text)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = {str(case.get("id")): case for case in as_list(data.get("cases")) if isinstance(case, dict)}
    results = data.get("execution_results")
    if not isinstance(results, dict):
        return ["Missing execution_results."]

    seen: set[str] = set()
    for item in as_list(results.get("cases")):
        if not isinstance(item, dict):
            continue
        case_id = str(item.get("case_id") or "")
        result = str(item.get("result") or "")
        failure_class = item.get("failure_class")
        if case_id not in cases:
            errors.append(f"Execution result references unknown case {case_id}.")
        seen.add(case_id)
        if result in RESULTS_REQUIRING_CLASS:
            if failure_class not in VALID_CLASSES:
                errors.append(f"{case_id} result={result} requires valid failure_class.")
            if not as_list(item.get("evidence")):
                errors.append(f"{case_id} result={result} requires evidence.")
        if result == "fail" and cases.get(case_id, {}).get("priority") == "P0" and not item.get("defect_id"):
            errors.append(f"P0 failed case {case_id} needs defect_id or explicit triage note.")

    p0_cases = {case_id for case_id, case in cases.items() if case.get("priority") == "P0"}
    missing_p0 = sorted(p0_cases - seen)
    if missing_p0:
        errors.append(f"Execution results missing P0 cases: {', '.join(missing_p0)}.")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: execution_feedback_check.py <cases-with-results.json|yaml>", file=sys.stderr)
        return 2
    try:
        data = load_data(Path(argv[1]))
        if not isinstance(data, dict):
            raise RuntimeError("Top-level document must be an object.")
        errors = validate(data)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("Execution feedback check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Execution feedback check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
