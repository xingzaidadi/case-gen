#!/usr/bin/env python3
"""Coverage-quality checks for case-gen structured case files.

This complements validate_cases.py. The validator checks shape; this script
checks whether the suite looks like a useful professional test set.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


HIGH_RISK_RULE_WORDS = {
    "auth",
    "authorization",
    "permission",
    "identity",
    "role",
    "owner",
    "tenant",
    "scope",
    "idempot",
    "replay",
    "approval",
    "audit",
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


def text_of(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(text_of(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(text_of(v) for v in value)
    return str(value or "")


def case_refs(case: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    trace = case.get("traceability")
    if isinstance(trace, dict):
        for value in trace.values():
            if isinstance(value, list):
                refs.update(str(item) for item in value)
    return refs


def has_observable(case: dict[str, Any], observable: str) -> bool:
    for expected in as_list(case.get("expected")):
        if isinstance(expected, dict) and str(expected.get("observable", "")).lower() == observable:
            return True
    return False


def is_negative_security(case: dict[str, Any]) -> bool:
    haystack = text_of(case).lower()
    return any(
        token in haystack
        for token in (
            "missing identity",
            "invalid identity",
            "wrong identity",
            "wrong role",
            "cross-user",
            "cross tenant",
            "cross-tenant",
            "forbidden",
            "unauthorized",
            "越权",
            "跨用户",
            "无身份",
            "错误身份",
        )
    )


def has_concrete_boundary(case: dict[str, Any]) -> bool:
    haystack = text_of(case)
    patterns = [
        r"\b\d+\s*/\s*\d+\s*/\s*\d+\b",
        r"\bN-1\s*/\s*N\s*/\s*N\+1\b",
        r"\bmin-1\b|\bmin\+1\b|\bmax-1\b|\bmax\+1\b",
        r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}",
        r"\b\d+\s*(ms|s|min|minutes|seconds|hours)\b",
    ]
    return any(re.search(pattern, haystack, re.IGNORECASE) for pattern in patterns)


def validate_coverage_map(data: dict[str, Any], cases_by_id: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    coverage_map = data.get("coverage_map")
    if not isinstance(coverage_map, dict):
        errors.append("Missing coverage_map for coverage-quality checks.")
        return errors

    for section in ("sources", "test_points"):
        for item in as_list(coverage_map.get(section)):
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "<missing-id>"))
            priority = item.get("priority")
            status = item.get("status")
            mapped_cases = [str(case_id) for case_id in as_list(item.get("cases"))]
            if priority == "P0" and status not in {"covered", "deferred"}:
                errors.append(f"P0 {section[:-1]} {item_id} is not covered or deferred.")
            if status == "covered" and not mapped_cases:
                errors.append(f"Covered {section[:-1]} {item_id} has no cases.")
            for case_id in mapped_cases:
                if case_id not in cases_by_id:
                    errors.append(f"{section[:-1]} {item_id} references unknown case {case_id}.")

    for link in as_list(coverage_map.get("cross_view")):
        if not isinstance(link, dict):
            continue
        if link.get("status") == "linked" and not as_list(link.get("layered")):
            errors.append(f"Cross-view link for {link.get('e2e')} is linked but has no layered test points.")

    return errors


def validate_quality(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = [case for case in as_list(data.get("cases")) if isinstance(case, dict)]
    cases_by_id = {str(case.get("id")): case for case in cases}

    errors.extend(validate_coverage_map(data, cases_by_id))

    p0_cases = [case for case in cases if case.get("priority") == "P0"]
    if not p0_cases:
        errors.append("No P0 cases found.")

    for case in cases:
        case_id = case.get("id", "<missing-id>")
        refs = case_refs(case)
        if not refs and not (case.get("traceability") or {}).get("inferred"):
            errors.append(f"{case_id} has no traceability and is not inferred.")

    by_level: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        by_level.setdefault(str(case.get("level", "unknown")), []).append(case)
    for level, group in by_level.items():
        if len(group) >= 3 and all(str(case.get("type")) == "happy_path" for case in group):
            errors.append(f"Level {level} has only happy_path cases.")

    for case in cases:
        case_id = str(case.get("id"))
        case_type = str(case.get("type", ""))
        if case_type == "boundary" and not has_concrete_boundary(case):
            errors.append(f"{case_id} is boundary type but has no concrete boundary values.")
        if case_type == "state_transition":
            haystack = text_of(case).lower()
            if "invalid" not in haystack and "非法" not in haystack and "terminal" not in haystack and "终态" not in haystack:
                errors.append(f"{case_id} is state_transition type but does not mention invalid or terminal-state behavior.")

    suite_text = text_of(data).lower()
    looks_security_control = any(word in suite_text for word in HIGH_RISK_RULE_WORDS)
    if looks_security_control:
        if not any(is_negative_security(case) for case in cases):
            errors.append("Security/control signals found but no negative authorization case detected.")
        if not any(has_observable(case, "log") or has_observable(case, "metric") for case in cases):
            errors.append("Security/control signals found but no log or metric observability case detected.")

    gates = data.get("quality_gates")
    if isinstance(gates, dict):
        for gate, value in gates.items():
            if value is False:
                errors.append(f"Quality gate is false: {gate}.")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: coverage_check.py <cases.json|cases.yaml>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        data = load_data(path)
        if not isinstance(data, dict):
            raise RuntimeError("Top-level document must be an object.")
        errors = validate_quality(data)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("Coverage-quality check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Coverage-quality check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
