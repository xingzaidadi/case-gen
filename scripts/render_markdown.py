#!/usr/bin/env python3
"""Render case-gen structured cases to Markdown."""

from __future__ import annotations

import argparse
import json
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


def cell(value: Any) -> str:
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    elif isinstance(value, dict):
        value = ", ".join(f"{k}={v}" for k, v in value.items() if v)
    text = str(value or "")
    return text.replace("\n", "<br>").replace("|", "\\|")


def trace_summary(case: dict[str, Any]) -> str:
    trace = case.get("traceability")
    if not isinstance(trace, dict):
        return ""
    refs: list[str] = []
    for key in ("requirements", "code", "api", "rules", "risks", "test_points"):
        refs.extend(str(item) for item in as_list(trace.get(key)))
    if trace.get("inferred"):
        refs.append("inferred")
    return ", ".join(refs)


def expected_summary(case: dict[str, Any]) -> str:
    items: list[str] = []
    for expected in as_list(case.get("expected")):
        if isinstance(expected, dict):
            assertion = expected.get("assertion", "")
            observable = expected.get("observable", "")
            items.append(f"{assertion} [{observable}]")
        else:
            items.append(str(expected))
    return "<br>".join(items)


def render(data: dict[str, Any]) -> str:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    title = metadata.get("title") or "Test Cases"
    mode = metadata.get("mode") or "unknown"
    assumptions = as_list(metadata.get("assumptions"))

    lines: list[str] = [f"# {title}", "", f"> Mode: {mode}", ""]

    if assumptions:
        lines.append("## Assumptions")
        lines.append("")
        for item in assumptions:
            lines.append(f"- {item}")
        lines.append("")

    coverage_map = data.get("coverage_map")
    if isinstance(coverage_map, dict):
        lines.append("## Coverage Map")
        lines.append("")
        lines.append("| Source/Test Point | Priority | Status | Cases |")
        lines.append("| --- | --- | --- | --- |")
        for section in ("sources", "test_points"):
            for item in as_list(coverage_map.get(section)):
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"| {cell(item.get('id'))} | {cell(item.get('priority'))} | "
                    f"{cell(item.get('status'))} | {cell(as_list(item.get('cases')))} |"
                )
        lines.append("")

    lines.append("## Cases")
    lines.append("")
    lines.append("| ID | Priority | Level | Type | Title | Traceability | Expected |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for case in as_list(data.get("cases")):
        if not isinstance(case, dict):
            continue
        lines.append(
            f"| {cell(case.get('id'))} | {cell(case.get('priority'))} | {cell(case.get('level'))} | "
            f"{cell(case.get('type'))} | {cell(case.get('title'))} | "
            f"{cell(trace_summary(case))} | {cell(expected_summary(case))} |"
        )
    lines.append("")

    open_questions = as_list(data.get("open_questions"))
    if open_questions:
        lines.append("## Open Questions")
        lines.append("")
        lines.append("| ID | Question | Impact | Owner |")
        lines.append("| --- | --- | --- | --- |")
        for q in open_questions:
            if isinstance(q, dict):
                lines.append(f"| {cell(q.get('id'))} | {cell(q.get('question'))} | {cell(q.get('impact'))} | {cell(q.get('owner'))} |")
        lines.append("")

    gates = data.get("quality_gates")
    if isinstance(gates, dict):
        lines.append("## Quality Gates")
        lines.append("")
        lines.append("| Gate | Status |")
        lines.append("| --- | --- |")
        for key, value in gates.items():
            lines.append(f"| {cell(key)} | {cell(value)} |")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render case-gen cases to Markdown.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    data = load_data(args.input)
    if not isinstance(data, dict):
        raise RuntimeError("Top-level document must be an object.")

    output = render(data)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8", newline="\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

