#!/usr/bin/env python3
"""Create draft case skeletons from test points."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


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


def test_points(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        if isinstance(data.get("test_model"), dict):
            points = data["test_model"].get("test_points")
            if isinstance(points, list):
                return [p for p in points if isinstance(p, dict)]
        points = data.get("test_points")
        if isinstance(points, list):
            return [p for p in points if isinstance(p, dict)]
    if isinstance(data, list):
        return [p for p in data if isinstance(p, dict)]
    return []


def priority_of(point: dict[str, Any]) -> str:
    priority = str(point.get("priority") or "P1").upper()
    return priority if priority in {"P0", "P1", "P2"} else "P1"


def source_refs(point: dict[str, Any]) -> dict[str, list[str]]:
    refs = {"requirements": [], "code": [], "api": [], "rules": [], "risks": [], "test_points": []}
    point_id = str(point.get("id") or "")
    if point_id:
        refs["test_points"].append(point_id)
    for source in as_list(point.get("source")):
        if not isinstance(source, dict):
            continue
        ref = str(source.get("ref") or "")
        source_type = str(source.get("type") or "")
        if not ref:
            continue
        if source_type == "requirement":
            refs["requirements"].append(ref)
        elif source_type == "code":
            refs["code"].append(ref)
        elif source_type == "api":
            refs["api"].append(ref)
        elif source_type == "rule":
            refs["rules"].append(ref)
        elif source_type == "risk":
            refs["risks"].append(ref)
    return refs


def build_cases(points: list[dict[str, Any]], suite_id: str) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    coverage_points: list[dict[str, Any]] = []
    for index, point in enumerate(points, start=1):
        point_id = str(point.get("id") or f"TP-{index:03d}")
        case_id = f"TC-{index:03d}"
        priority = priority_of(point)
        level = "e2e" if str(point.get("view")) == "e2e" else "api"
        case_type = "happy_path" if priority != "P0" else "negative"
        cases.append(
            {
                "id": case_id,
                "title": str(point.get("title") or point_id),
                "priority": priority,
                "level": level,
                "type": case_type,
                "traceability": {**source_refs(point), "inferred": False},
                "preconditions": ["TODO: fill concrete preconditions"],
                "data": [],
                "steps": [{"action": "TODO: fill action", "input": ""}],
                "expected": [{"assertion": "TODO: fill observable assertion", "observable": "response"}],
                "automation_candidate": "medium",
                "status": "draft",
            }
        )
        coverage_points.append({"id": point_id, "cases": [case_id], "status": "covered"})

    p0_case_ids = [case["id"] for case in cases if case["priority"] == "P0"]
    all_case_ids = [case["id"] for case in cases]
    return {
        "metadata": {
            "suite_id": suite_id,
            "title": f"{suite_id} case skeleton",
            "generated_at": date.today().isoformat(),
            "mode": "mixed",
            "assumptions": ["Generated as a skeleton from test points; fill TODO fields before use."],
        },
        "coverage_map": {"sources": [], "test_points": coverage_points, "cross_view": []},
        "cases": cases,
        "suite_layers": {
            "smoke": p0_case_ids[:5],
            "p0_gate": p0_case_ids,
            "regression": all_case_ids,
            "full": all_case_ids,
            "exploratory": [],
        },
        "quality_gates": {
            "p0_sources_covered": bool(p0_case_ids) or True,
            "no_happy_path_only": True,
            "all_cases_have_traceability": True,
            "all_cases_have_observable_expected": True,
            "boundary_cases_have_concrete_values": True,
            "state_cases_include_invalid_transitions": True,
            "security_cases_include_negative_authorization": True,
            "e2e_layer_cross_check_complete": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create case skeletons from test points.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--suite-id", default="generated-suite")
    args = parser.parse_args()

    points = test_points(load_data(args.input))
    if not points:
        raise RuntimeError("No test points found.")

    data = build_cases(points, args.suite_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(data['cases'])} case skeletons: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

