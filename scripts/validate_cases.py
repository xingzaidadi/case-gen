#!/usr/bin/env python3
"""Validate case-gen structured case files.

Accepts JSON by default. YAML is supported when PyYAML is installed.
The validator intentionally checks only structural gates that are useful
before rendering cases into Markdown, Excel, or Gherkin.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_CASE_FIELDS = {"id", "title", "priority", "level", "traceability", "steps", "expected"}
VALID_PRIORITIES = {"P0", "P1", "P2"}


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


def has_traceability(traceability: Any) -> bool:
    if not isinstance(traceability, dict):
        return False
    for key in ("requirements", "code", "api", "rules", "risks", "test_points"):
        if as_list(traceability.get(key)):
            return True
    return bool(traceability.get("inferred"))


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Top-level document must be an object."]

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        return ["Top-level 'cases' must be a non-empty list."]

    p0_with_sources = 0
    for index, case in enumerate(cases, start=1):
        label = f"case[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object.")
            continue

        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            errors.append(f"{label} missing required fields: {', '.join(sorted(missing))}.")

        priority = case.get("priority")
        if priority not in VALID_PRIORITIES:
            errors.append(f"{label} has invalid priority: {priority!r}.")

        if not has_traceability(case.get("traceability")):
            errors.append(f"{label} has no traceability and is not marked inferred.")
        elif priority == "P0":
            p0_with_sources += 1

        steps = as_list(case.get("steps"))
        if not steps:
            errors.append(f"{label} has no steps.")

        expected = as_list(case.get("expected"))
        if not expected:
            errors.append(f"{label} has no expected assertions.")
        for exp_index, expected_item in enumerate(expected, start=1):
            if isinstance(expected_item, dict):
                assertion = str(expected_item.get("assertion", "")).strip()
                observable = str(expected_item.get("observable", "")).strip()
                if not assertion:
                    errors.append(f"{label}.expected[{exp_index}] missing assertion.")
                if not observable:
                    errors.append(f"{label}.expected[{exp_index}] missing observable.")
            elif not str(expected_item).strip():
                errors.append(f"{label}.expected[{exp_index}] is empty.")

    if p0_with_sources == 0:
        errors.append("No P0 case with traceability found.")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_cases.py <cases.json|cases.yaml>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        data = load_data(path)
        errors = validate(data)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("Case validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Case validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

