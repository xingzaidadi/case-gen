#!/usr/bin/env python3
"""Validate a finance project rulepack."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_SECTIONS = {
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

REQUIRED_ITEM_FIELDS = {"id", "name", "description"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_rulepack(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["Top-level rulepack must be an object."]

    errors: list[str] = []
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("Missing metadata object.")
    else:
        for field in ("rulepack_id", "version", "owner", "updated_at", "status"):
            if not str(metadata.get(field, "")).strip():
                errors.append(f"metadata.{field} is required.")

    ids: dict[str, str] = {}
    for section in sorted(REQUIRED_SECTIONS):
        value = data.get(section)
        if not isinstance(value, list):
            errors.append(f"{section} must be a list.")
            continue
        if not value:
            errors.append(f"{section} must not be empty.")
            continue
        for index, item in enumerate(value, start=1):
            label = f"{section}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object.")
                continue
            missing = [field for field in sorted(REQUIRED_ITEM_FIELDS) if not str(item.get(field, "")).strip()]
            if missing:
                errors.append(f"{label} missing required fields: {', '.join(missing)}.")
                continue
            item_id = str(item["id"]).strip()
            if item_id in ids:
                errors.append(f"Duplicate rule id {item_id} in {section}; first seen in {ids[item_id]}.")
            ids[item_id] = section

    if "CTRL-CLOSED-PERIOD-NO-POST" not in ids:
        errors.append("Missing closed-period control id CTRL-CLOSED-PERIOD-NO-POST.")
    if not any(rule_id.startswith("SOD-") for rule_id in ids):
        errors.append("No segregation-of-duties rule id found.")
    if not any(rule_id.startswith("APPROVAL-") for rule_id in ids):
        errors.append("No approval matrix rule id found.")
    if not any(rule_id.startswith("OBS-") for rule_id in ids):
        errors.append("No observability rule id found.")

    return errors


def collect_rule_ids(data: dict[str, Any]) -> list[str]:
    rule_ids: list[str] = []
    for section in REQUIRED_SECTIONS:
        for item in as_list(data.get(section)):
            if isinstance(item, dict) and str(item.get("id", "")).strip():
                rule_ids.append(str(item["id"]).strip())
    return sorted(rule_ids)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: finance_rulepack_check.py <rulepack.json>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        data = load_json(path)
        errors = validate_rulepack(data)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("Finance rulepack validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    ids = collect_rule_ids(data)
    print(f"Finance rulepack validation passed. {len(ids)} rule ids loaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

