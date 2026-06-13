#!/usr/bin/env python3
"""Extract a draft finance project rulepack from local source files.

This is a conservative extractor. It turns obvious facts from PRDs, DDL,
CSV/Excel sheets, JSON, and Markdown into a rulepack draft and marks fallback
items with needs_confirmation=true. It should not be treated as finance policy
until product, finance, or engineering owners confirm the extracted rules.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Iterable


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


def iter_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in {".md", ".txt", ".sql", ".json", ".csv", ".xlsx"}:
                    files.append(child)
        elif path.is_file():
            files.append(path)
    return sorted(files)


def read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".csv":
        rows: list[str] = []
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            for row in csv.reader(handle):
                rows.append(" | ".join(row))
        return "\n".join(rows)
    if suffix == ".xlsx":
        try:
            import openpyxl  # type: ignore
        except ImportError:
            return ""
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        rows: list[str] = []
        for sheet in workbook.worksheets:
            rows.append(f"# sheet: {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                values = [str(cell) for cell in row if cell is not None and str(cell).strip()]
                if values:
                    rows.append(" | ".join(values))
        return "\n".join(rows)
    return path.read_text(encoding="utf-8", errors="replace")


def source_label(path: Path) -> str:
    """Return a stable source path for generated eval artifacts."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return str(resolved)


def slug(value: str, prefix: str, max_len: int = 48) -> str:
    text = value.strip().upper()
    text = re.sub(r"[^A-Z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    if not text:
        text = "PLACEHOLDER"
    return f"{prefix}-{text[:max_len].strip('-')}"


def add_item(section: list[dict[str, Any]], seen: set[str], item: dict[str, Any]) -> None:
    item_id = str(item.get("id", "")).strip()
    if not item_id or item_id in seen:
        return
    seen.add(item_id)
    section.append(item)


def matching_lines(text: str, *patterns: str) -> list[str]:
    result: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns):
            result.append(line)
    return result


def extract_account(line: str, source: str) -> dict[str, Any]:
    code_match = re.search(r"\b([1-9]\d{3,9})\b", line)
    code = code_match.group(1) if code_match else slug(line, "ACC").replace("ACC-", "")
    return {
        "id": f"ACC-{code}",
        "name": line[:80],
        "description": f"Extracted account mapping from {source}: {line}",
        "source": source,
        "needs_confirmation": True,
    }


def extract_tax(line: str, source: str) -> dict[str, Any]:
    rate_match = re.search(r"(\d+(?:\.\d+)?)\s*%", line)
    rate = str(float(rate_match.group(1)) / 100) if rate_match else "unknown"
    return {
        "id": slug(line, "TAX"),
        "name": line[:80],
        "description": f"Extracted tax rule from {source}: {line}",
        "rate": rate,
        "source": source,
        "needs_confirmation": True,
    }


def extract_rulepack(paths: list[Path], rulepack_id: str, owner: str) -> dict[str, Any]:
    docs = [(path, read_file(path)) for path in iter_files(paths)]
    combined = "\n".join(text for _, text in docs)
    rulepack: dict[str, Any] = {
        "metadata": {
            "rulepack_id": rulepack_id,
            "version": "0.1.0-draft",
            "owner": owner,
            "updated_at": date.today().isoformat(),
            "status": "draft",
            "source_files": [source_label(path) for path, _ in docs],
        }
    }
    for section in SECTIONS:
        rulepack[section] = []

    seen_by_section = {section: set() for section in SECTIONS}

    for path, text in docs:
        source = source_label(path)
        for line in matching_lines(text, r"legal entity|company code|法人|公司代码|账套"):
            add_item(
                rulepack["legal_entities"],
                seen_by_section["legal_entities"],
                {
                    "id": slug(line, "LE"),
                    "name": line[:80],
                    "description": f"Extracted legal-entity signal from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

        for line in matching_lines(text, r"cut-?off|closed period|hard_closed|关账|月结|期间|posting timing|rounding|舍入|入账"):
            add_item(
                rulepack["accounting_policies"],
                seen_by_section["accounting_policies"],
                {
                    "id": slug(line, "POLICY"),
                    "name": line[:80],
                    "description": f"Extracted accounting policy from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

        for line in matching_lines(text, r"account|科目|\bGL\b|\bAP\b|\bAR\b|AP payable|fixed asset|应付|应收|固定资产|银行存款"):
            add_item(rulepack["chart_of_accounts"], seen_by_section["chart_of_accounts"], extract_account(line, source))

        for line in matching_lines(text, r"tax|VAT|税码|税率|发票|红冲|red-letter"):
            add_item(rulepack["tax_codes"], seen_by_section["tax_codes"], extract_tax(line, source))

        for line in matching_lines(text, r"approval|approver|审批|<=|>=|>|<|amount boundary|金额"):
            if any(token in line.lower() for token in ("approval", "approver", "审批", "<=", ">=", "amount", "金额")):
                add_item(
                    rulepack["approval_matrices"],
                    seen_by_section["approval_matrices"],
                    {
                        "id": slug(line, "APPROVAL"),
                        "name": line[:80],
                        "description": f"Extracted approval rule from {source}: {line}",
                        "source": source,
                        "needs_confirmation": True,
                    },
                )

        for line in matching_lines(text, r"SoD|segregation|self-approval|same.*approve|不能.*审批|职责分离|同人"):
            add_item(
                rulepack["segregation_of_duties"],
                seen_by_section["segregation_of_duties"],
                {
                    "id": slug(line, "SOD"),
                    "name": line[:80],
                    "description": f"Extracted SoD rule from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

        for line in matching_lines(text, r"duplicate|idempot|closed period|budget|control|重复|幂等|预算|控制|关账"):
            prefix = "CTRL-CLOSED-PERIOD-NO-POST" if re.search(r"closed period|hard_closed|关账", line, re.IGNORECASE) else slug(line, "CTRL")
            add_item(
                rulepack["finance_controls"],
                seen_by_section["finance_controls"],
                {
                    "id": prefix,
                    "name": line[:80],
                    "description": f"Extracted finance control from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

        for line in matching_lines(text, r"API|endpoint|topic|event|callback|MQ|interface|接口|事件|回调|银行|ERP|tax platform"):
            add_item(
                rulepack["integration_points"],
                seen_by_section["integration_points"],
                {
                    "id": slug(line, "INT"),
                    "name": line[:80],
                    "description": f"Extracted integration point from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

        for line in matching_lines(text, r"CREATE TABLE|table|log|metric|audit|voucher|ledger|表|日志|指标|审计|凭证"):
            add_item(
                rulepack["data_observability"],
                seen_by_section["data_observability"],
                {
                    "id": slug(line, "OBS"),
                    "name": line[:80],
                    "description": f"Extracted observability signal from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

        for line in matching_lines(text, r"incident|bug|defect|production|线上|事故|缺陷|重复付款|漏测"):
            add_item(
                rulepack["historical_incidents"],
                seen_by_section["historical_incidents"],
                {
                    "id": slug(line, "INC"),
                    "name": line[:80],
                    "description": f"Extracted incident signal from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

        for line in matching_lines(text, r"supplier|invoice|bank account|currency|budget|test data|供应商|发票|银行账号|币种|预算|测试数据"):
            add_item(
                rulepack["test_data_profiles"],
                seen_by_section["test_data_profiles"],
                {
                    "id": slug(line, "DATA"),
                    "name": line[:80],
                    "description": f"Extracted test-data signal from {source}: {line}",
                    "source": source,
                    "needs_confirmation": True,
                },
            )

    ensure_minimum_rulepack(rulepack, combined)
    return rulepack


def fallback_item(prefix: str, name: str, description: str) -> dict[str, Any]:
    return {
        "id": prefix,
        "name": name,
        "description": description,
        "source": "extractor-fallback",
        "needs_confirmation": True,
    }


def ensure_minimum_rulepack(rulepack: dict[str, Any], combined: str) -> None:
    defaults = {
        "legal_entities": fallback_item("LE-PLACEHOLDER", "Placeholder legal entity", "No legal entity was extracted."),
        "accounting_policies": fallback_item("POLICY-PERIOD-CUTOFF", "Placeholder period cut-off policy", "No accounting policy was extracted."),
        "chart_of_accounts": fallback_item("ACC-PLACEHOLDER", "Placeholder account", "No account mapping was extracted."),
        "tax_codes": fallback_item("TAX-PLACEHOLDER", "Placeholder tax code", "No tax code was extracted."),
        "approval_matrices": fallback_item("APPROVAL-PLACEHOLDER", "Placeholder approval matrix", "No approval matrix was extracted."),
        "segregation_of_duties": fallback_item("SOD-PLACEHOLDER", "Placeholder SoD rule", "No SoD rule was extracted."),
        "finance_controls": fallback_item("CTRL-CLOSED-PERIOD-NO-POST", "Placeholder closed-period control", "No closed-period control was extracted."),
        "integration_points": fallback_item("INT-PLACEHOLDER", "Placeholder integration point", "No integration point was extracted."),
        "data_observability": fallback_item("OBS-PLACEHOLDER", "Placeholder observability rule", "No observability rule was extracted."),
        "historical_incidents": fallback_item("INC-PLACEHOLDER", "Placeholder incident", "No historical incident was extracted."),
        "test_data_profiles": fallback_item("DATA-PLACEHOLDER", "Placeholder test data", "No test data profile was extracted."),
    }
    for section, item in defaults.items():
        if not rulepack.get(section):
            rulepack[section].append(item)

    controls = {item.get("id") for item in rulepack["finance_controls"] if isinstance(item, dict)}
    if "CTRL-CLOSED-PERIOD-NO-POST" not in controls:
        rulepack["finance_controls"].append(defaults["finance_controls"])

    rulepack["metadata"]["extraction_summary"] = {
        section: len(rulepack.get(section, [])) for section in SECTIONS
    }
    rulepack["metadata"]["confidence"] = "draft-needs-review" if combined.strip() else "empty-input"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a draft finance rulepack from source files.")
    parser.add_argument("inputs", nargs="+", help="Input files or directories.")
    parser.add_argument("-o", "--output", required=True, help="Output rulepack JSON path.")
    parser.add_argument("--rulepack-id", default="finance-draft-rulepack", help="Rulepack id.")
    parser.add_argument("--owner", default="finance-system-team", help="Rulepack owner.")
    args = parser.parse_args()

    paths = [Path(value) for value in args.inputs]
    rulepack = extract_rulepack(paths, args.rulepack_id, args.owner)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rulepack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Draft finance rulepack written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
