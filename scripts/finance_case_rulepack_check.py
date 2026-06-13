#!/usr/bin/env python3
"""Check that finance cases reference a project rulepack."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


RULEPACK_SECTIONS = {
    "legal_entities",
    "accounting_policies",
    "chart_of_accounts",
    "tax_codes",
    "approval_matrices",
    "segregation_of_duties",
    "finance_controls",
    "integration_points",
    "data_observability",
    "historical_incidents",
    "test_data_profiles",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def text_of(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(text_of(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(text_of(v) for v in value)
    return str(value or "")


def collect_rule_ids(rulepack: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for section in RULEPACK_SECTIONS:
        for item in as_list(rulepack.get(section)):
            if isinstance(item, dict) and str(item.get("id", "")).strip():
                ids.add(str(item["id"]).strip())
    return ids


def case_rule_refs(case: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    trace = case.get("traceability")
    if isinstance(trace, dict):
        for key in ("rules", "risks", "requirements", "test_points"):
            for item in as_list(trace.get(key)):
                refs.add(str(item))
    finance = case.get("finance")
    if isinstance(finance, dict):
        for item in as_list(finance.get("regulatory_refs")):
            refs.add(str(item))
        for item in as_list(finance.get("financial_assertions")):
            refs.add(str(item))
        for item in as_list(finance.get("control_assertions")):
            refs.add(str(item))
    haystack = text_of(case)
    for token in haystack.replace(",", " ").replace(";", " ").split():
        if "-" in token:
            refs.add(token.strip("[](){}.:"))
    return refs


def validate_cases_against_rulepack(cases_data: Any, rulepack_data: Any) -> list[str]:
    if not isinstance(cases_data, dict):
        return ["Cases document must be an object."]
    if not isinstance(rulepack_data, dict):
        return ["Rulepack document must be an object."]

    rule_ids = collect_rule_ids(rulepack_data)
    if not rule_ids:
        return ["Rulepack has no rule ids."]

    errors: list[str] = []
    cases = [case for case in as_list(cases_data.get("cases")) if isinstance(case, dict)]
    if not cases:
        return ["Cases document has no cases."]

    referenced_any = False
    for case in cases:
        case_id = str(case.get("id", "<missing-id>"))
        priority = case.get("priority")
        finance = case.get("finance")
        is_finance = isinstance(finance, dict)
        refs = case_rule_refs(case)
        matched = refs & rule_ids
        if matched:
            referenced_any = True
        if priority == "P0" and is_finance and not matched:
            errors.append(f"{case_id} is P0 finance case but references no rulepack id.")

    if not referenced_any:
        errors.append("No case references any rulepack id.")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: finance_case_rulepack_check.py <cases.json> <rulepack.json>", file=sys.stderr)
        return 2

    try:
        cases_data = load_json(Path(argv[1]))
        rulepack_data = load_json(Path(argv[2]))
        errors = validate_cases_against_rulepack(cases_data, rulepack_data)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("Finance case rulepack check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Finance case rulepack check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

