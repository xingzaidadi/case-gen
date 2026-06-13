#!/usr/bin/env python3
"""Generate a finance rule gap report for cases and an optional rulepack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RULEPACK_SECTIONS = [
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

DOMAIN_RULE_PREFIXES = {
    "posting/accounting": ("ACC-", "POLICY-", "OBS-"),
    "tax/invoice": ("TAX-", "INT-TAX", "OBS-"),
    "approval": ("APPROVAL-",),
    "segregation_of_duties": ("SOD-",),
    "closed_period": ("CTRL-CLOSED-PERIOD", "POLICY-PERIOD"),
    "budget": ("CTRL-BUDGET",),
    "integration/observability": ("INT-", "OBS-"),
    "historical_regression": ("INC-",),
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


def placeholder_items(rulepack: dict[str, Any]) -> list[tuple[str, str]]:
    placeholders: list[tuple[str, str]] = []
    for section in RULEPACK_SECTIONS:
        for item in as_list(rulepack.get(section)):
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", ""))
            if item.get("needs_confirmation") or "PLACEHOLDER" in item_id:
                placeholders.append((section, item_id))
    return placeholders


def case_refs(case: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    trace = case.get("traceability")
    if isinstance(trace, dict):
        for value in trace.values():
            for item in as_list(value):
                refs.add(str(item))
    finance = case.get("finance")
    if isinstance(finance, dict):
        for value in finance.values():
            for item in as_list(value):
                refs.add(str(item))
    for token in text_of(case).replace(",", " ").replace(";", " ").split():
        if "-" in token:
            refs.add(token.strip("[](){}.:"))
    return refs


def inferred_domains(case: dict[str, Any]) -> set[str]:
    haystack = text_of(case).lower()
    domains: set[str] = set()
    if any(token in haystack for token in ("voucher", "journal", "ledger", "posting", "debit_credit")):
        domains.add("posting/accounting")
    if any(token in haystack for token in ("tax", "invoice", "vat", "red-letter")):
        domains.add("tax/invoice")
    if any(token in haystack for token in ("approval", "approver")):
        domains.add("approval")
    if any(token in haystack for token in ("sod", "segregation", "self-approval", "same-maintainer")):
        domains.add("segregation_of_duties")
    if any(token in haystack for token in ("closed period", "hard_closed", "cut-off", "cutoff")):
        domains.add("closed_period")
    if "budget" in haystack:
        domains.add("budget")
    if any(token in haystack for token in ("api", "event", "callback", "table", "log", "audit", "metric", "observable")):
        domains.add("integration/observability")
    if any(token in haystack for token in ("incident", "defect", "bug", "regression")):
        domains.add("historical_regression")
    return domains


def has_prefix(refs: set[str], prefixes: tuple[str, ...]) -> bool:
    return any(ref.startswith(prefix) for ref in refs for prefix in prefixes)


def generate_report(cases_data: dict[str, Any], rulepack: dict[str, Any] | None) -> str:
    cases = [case for case in as_list(cases_data.get("cases")) if isinstance(case, dict)]
    rule_ids = collect_rule_ids(rulepack) if rulepack else set()
    placeholders = placeholder_items(rulepack) if rulepack else []

    lines: list[str] = []
    lines.append("# Finance Rule Gap Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Cases: {len(cases)}")
    lines.append(f"- P0 finance cases: {sum(1 for case in cases if case.get('priority') == 'P0' and isinstance(case.get('finance'), dict))}")
    lines.append(f"- Rulepack loaded: {'yes' if rulepack else 'no'}")
    lines.append(f"- Rule ids: {len(rule_ids)}")
    lines.append(f"- Placeholder / needs-confirmation rules: {len(placeholders)}")
    lines.append("")

    if rulepack:
        lines.append("## Rulepack Section Coverage")
        lines.append("")
        for section in RULEPACK_SECTIONS:
            count = len(as_list(rulepack.get(section)))
            marker = "OK" if count else "MISSING"
            lines.append(f"- {marker}: `{section}` has {count} item(s)")
        lines.append("")

    if placeholders:
        lines.append("## Rules Needing Confirmation")
        lines.append("")
        for section, item_id in placeholders:
            lines.append(f"- `{section}`: `{item_id}`")
        lines.append("")

    lines.append("## Case Gaps")
    lines.append("")
    any_gap = False
    for case in cases:
        case_id = str(case.get("id", "<missing-id>"))
        if case.get("priority") != "P0" or not isinstance(case.get("finance"), dict):
            continue
        refs = case_refs(case)
        matched_rulepack = refs & rule_ids
        domains = inferred_domains(case)
        gaps: list[str] = []
        if rulepack and not matched_rulepack:
            gaps.append("does not reference any rulepack id")
        for domain in sorted(domains):
            prefixes = DOMAIN_RULE_PREFIXES[domain]
            if rulepack and not has_prefix(refs, prefixes):
                gaps.append(f"missing `{domain}` rule id prefix {', '.join(prefixes)}")
        if gaps:
            any_gap = True
            lines.append(f"### {case_id}")
            lines.append("")
            lines.append(f"- Title: {case.get('title', '')}")
            lines.append(f"- Referenced rulepack ids: {', '.join(sorted(matched_rulepack)) if matched_rulepack else 'none'}")
            for gap in gaps:
                lines.append(f"- Gap: {gap}")
            lines.append("")

    if not any_gap:
        lines.append("No blocking P0 finance rule gaps detected.")
        lines.append("")

    lines.append("## Recommended Next Actions")
    lines.append("")
    if not rulepack:
        lines.append("- Provide or extract a finance project rulepack, then rerun this report.")
    if placeholders:
        lines.append("- Replace placeholder / needs-confirmation rulepack items with approved internal rules.")
    if any_gap:
        lines.append("- Add missing rulepack ids to case traceability or mark the rule as an open question.")
    if not placeholders and not any_gap:
        lines.append("- Keep the rulepack and cases under CI using finance rulepack checks.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a finance rule gap report.")
    parser.add_argument("cases", help="Cases JSON file.")
    parser.add_argument("--rulepack", help="Optional finance rulepack JSON file.")
    parser.add_argument("-o", "--output", help="Output Markdown path. Prints to stdout when omitted.")
    args = parser.parse_args()

    cases_data = load_json(Path(args.cases))
    rulepack = load_json(Path(args.rulepack)) if args.rulepack else None
    report = generate_report(cases_data, rulepack)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report + "\n", encoding="utf-8")
        print(f"Finance rule gap report written: {output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

