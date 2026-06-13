#!/usr/bin/env python3
"""Merge modular finance rulepacks into one project rulepack."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


SECTIONS = [
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
]


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object.")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def source_label(path: Path) -> str:
    """Return a stable source path for generated eval artifacts."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return str(resolved)


def normalized_item(item: dict[str, Any]) -> str:
    return json.dumps(item, ensure_ascii=False, sort_keys=True)


def merge_rulepacks(paths: list[Path], rulepack_id: str, owner: str, prefer: str) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "metadata": {
            "rulepack_id": rulepack_id,
            "version": "0.1.0-merged",
            "owner": owner,
            "updated_at": date.today().isoformat(),
            "status": "draft",
            "source_rulepacks": [source_label(path) for path in paths],
        }
    }
    for section in SECTIONS:
        merged[section] = []

    seen: dict[str, tuple[str, dict[str, Any]]] = {}
    conflicts: list[str] = []

    for path in paths:
        data = load_json(path)
        source = source_label(path)
        for section in SECTIONS:
            for item in as_list(data.get(section)):
                if not isinstance(item, dict):
                    continue
                item_id = str(item.get("id", "")).strip()
                if not item_id:
                    continue
                item = dict(item)
                sources = as_list(item.get("sources"))
                if source not in sources:
                    sources.append(source)
                item["sources"] = sources

                if item_id not in seen:
                    seen[item_id] = (section, item)
                    merged[section].append(item)
                    continue

                previous_section, previous_item = seen[item_id]
                if previous_section != section:
                    conflicts.append(f"{item_id} appears in both {previous_section} and {section}.")
                    continue
                previous_without_sources = dict(previous_item)
                item_without_sources = dict(item)
                previous_without_sources.pop("sources", None)
                item_without_sources.pop("sources", None)
                if normalized_item(previous_without_sources) == normalized_item(item_without_sources):
                    previous_item["sources"] = sorted(set(as_list(previous_item.get("sources")) + sources))
                    continue
                if prefer == "error":
                    conflicts.append(f"{item_id} has conflicting definitions in {section}.")
                    continue
                if prefer == "last":
                    previous_item.clear()
                    previous_item.update(item)

    if conflicts:
        raise RuntimeError("Rulepack merge conflicts:\n- " + "\n- ".join(conflicts))

    merged["metadata"]["merge_summary"] = {section: len(as_list(merged.get(section))) for section in SECTIONS}
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge finance project rulepacks.")
    parser.add_argument("rulepacks", nargs="+", help="Input rulepack JSON files.")
    parser.add_argument("-o", "--output", required=True, help="Output merged rulepack JSON path.")
    parser.add_argument("--rulepack-id", default="finance-merged-rulepack", help="Merged rulepack id.")
    parser.add_argument("--owner", default="finance-system-team", help="Merged rulepack owner.")
    parser.add_argument("--prefer", choices=["error", "first", "last"], default="error", help="Duplicate id handling.")
    args = parser.parse_args()

    paths = [Path(value) for value in args.rulepacks]
    merged = merge_rulepacks(paths, args.rulepack_id, args.owner, args.prefer)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Merged finance rulepack written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
