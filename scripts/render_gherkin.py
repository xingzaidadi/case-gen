#!/usr/bin/env python3
"""Render case-gen structured cases to a Gherkin feature file."""

from __future__ import annotations

import argparse
import json
import re
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


def clean(text: Any) -> str:
    text = str(text or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.replace("\n", " ")


def render_step(prefix: str, text: str) -> str:
    text = clean(text)
    if not text:
        text = "the condition is satisfied"
    return f"    {prefix} {text}"


def render(data: dict[str, Any]) -> str:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    feature_name = clean(metadata.get("title") or "Generated test cases")
    lines: list[str] = [f"Feature: {feature_name}", ""]

    for case in as_list(data.get("cases")):
        if not isinstance(case, dict):
            continue
        case_id = clean(case.get("id"))
        title = clean(case.get("title"))
        tags = [f"@{clean(case.get('priority')).lower()}", f"@{clean(case.get('level')).lower()}", f"@{clean(case.get('type')).lower()}"]
        tags = [tag for tag in tags if tag != "@"]
        lines.append("  " + " ".join(tags))
        lines.append(f"  Scenario: {case_id} {title}".rstrip())

        preconditions = as_list(case.get("preconditions"))
        if preconditions:
            lines.append(render_step("Given", str(preconditions[0])))
            for item in preconditions[1:]:
                lines.append(render_step("And", str(item)))
        else:
            lines.append(render_step("Given", "the required preconditions are met"))

        steps = as_list(case.get("steps"))
        if steps:
            first = steps[0]
            action = first.get("action") if isinstance(first, dict) else first
            lines.append(render_step("When", str(action)))
            for item in steps[1:]:
                action = item.get("action") if isinstance(item, dict) else item
                lines.append(render_step("And", str(action)))
        else:
            lines.append(render_step("When", "the user performs the action"))

        expected = as_list(case.get("expected"))
        if expected:
            first = expected[0]
            assertion = first.get("assertion") if isinstance(first, dict) else first
            lines.append(render_step("Then", str(assertion)))
            for item in expected[1:]:
                assertion = item.get("assertion") if isinstance(item, dict) else item
                lines.append(render_step("And", str(assertion)))
        else:
            lines.append(render_step("Then", "the expected result is observed"))
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render case-gen cases to Gherkin.")
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
