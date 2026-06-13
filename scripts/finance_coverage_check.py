#!/usr/bin/env python3
"""Finance-domain coverage checks for case-gen structured case files."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


POSTING_EVENTS = {"voucher_required", "reversal", "accrual", "settlement", "adjustment", "revaluation"}
FINANCE_SIGNALS = {
    "finance",
    "invoice",
    "payment",
    "voucher",
    "journal",
    "ledger",
    "subledger",
    "reconciliation",
    "period",
    "tax",
    "budget",
    "treasury",
    "ap",
    "ar",
    "gl",
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


def lower_text(value: Any) -> str:
    return text_of(value).lower()


def expected_observables(case: dict[str, Any]) -> set[str]:
    observables: set[str] = set()
    for expected in as_list(case.get("expected")):
        if isinstance(expected, dict):
            observable = str(expected.get("observable", "")).strip().lower()
            if observable:
                observables.add(observable)
    return observables


def has_observable(case: dict[str, Any], *observables: str) -> bool:
    actual = expected_observables(case)
    return any(observable in actual for observable in observables)


def has_words(value: Any, *tokens: str) -> bool:
    haystack = lower_text(value)
    return any(token.lower() in haystack for token in tokens)


def looks_finance_suite(data: dict[str, Any], cases: list[dict[str, Any]]) -> bool:
    if any(isinstance(case.get("finance"), dict) for case in cases):
        return True
    return any(token in lower_text(data) for token in FINANCE_SIGNALS)


def case_accounting_event(case: dict[str, Any]) -> str:
    finance = case.get("finance")
    if isinstance(finance, dict):
        return str(finance.get("accounting_event", "")).strip().lower()
    return ""


def has_debit_credit_assertion(case: dict[str, Any]) -> bool:
    return has_words(case, "debit_credit_balance", "debit equals credit", "debits equal credits", "借贷平衡")


def validate_posting_case(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_id = str(case.get("id", "<missing-id>"))
    event = case_accounting_event(case)
    if event == "no_posting":
        return errors
    text = lower_text(case)
    looks_posting = event in POSTING_EVENTS or any(token in text for token in ("voucher", "journal", "posting"))
    if not looks_posting:
        return errors

    if not has_observable(case, "journal_voucher", "ledger_entry"):
        errors.append(f"{case_id} has accounting/posting signals but no journal_voucher or ledger_entry observable.")
    if not has_debit_credit_assertion(case):
        errors.append(f"{case_id} has accounting/posting signals but no debit-credit balance assertion.")
    if "period" not in text and not has_observable(case, "period_status"):
        errors.append(f"{case_id} has accounting/posting signals but no accounting period assertion.")
    return errors


def validate_control_case(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_id = str(case.get("id", "<missing-id>"))
    text = lower_text(case)
    looks_control = any(token in text for token in ("approval", "approver", "segregation", "sod", "self-approval", "control"))
    if looks_control and not has_observable(case, "approval_chain", "audit_evidence", "control_evidence", "log"):
        errors.append(f"{case_id} has control signals but no approval_chain/audit_evidence/control_evidence observable.")
    return errors


def validate_suite_level(data: dict[str, Any], cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    suite_text = lower_text(data)
    p0_cases = [case for case in cases if case.get("priority") == "P0"]

    if not p0_cases:
        errors.append("Finance suite has no P0 cases.")
    if not any(isinstance(case.get("finance"), dict) for case in cases):
        errors.append("Finance suite has no adapter-specific finance block on any case.")
    if not any(has_debit_credit_assertion(case) for case in cases):
        errors.append("Finance suite has no debit-credit balance assertion.")
    if not any(has_observable(case, "journal_voucher", "ledger_entry") for case in cases):
        errors.append("Finance suite has no voucher/journal or ledger observable.")
    if not any(has_observable(case, "reconciliation_result") for case in cases):
        errors.append("Finance suite has no reconciliation_result observable.")
    if not any(has_words(case, "closed period", "cut-off", "cutoff", "hard_closed", "period_status") for case in cases):
        errors.append("Finance suite has no period close/cut-off case.")
    if not any(has_words(case, "duplicate invoice", "duplicate payment", "idempot") for case in cases):
        errors.append("Finance suite has no duplicate invoice/payment or idempotency case.")
    if not any(has_words(case, "segregation of duties", "sod", "self-approval") for case in cases):
        errors.append("Finance suite has no segregation-of-duties case.")
    if not any(has_observable(case, "audit_evidence", "control_evidence", "approval_chain", "log") for case in cases):
        errors.append("Finance suite has no audit/control evidence observable.")

    if any(token in suite_text for token in ("invoice", "tax", "vat", "fapiao", "red-letter")):
        if not any(has_observable(case, "invoice_status") for case in cases):
            errors.append("Invoice/tax signals found but no invoice_status observable.")
        if not any(has_observable(case, "tax_amount") or has_words(case, "tax amount") for case in cases):
            errors.append("Invoice/tax signals found but no tax_amount assertion.")

    if any(token in suite_text for token in ("payment", "bank", "treasury")):
        if not any(has_observable(case, "payment_status") for case in cases):
            errors.append("Payment signals found but no payment_status observable.")
        if not any(has_observable(case, "bank_receipt", "bank_statement") for case in cases):
            errors.append("Payment/bank signals found but no bank_receipt or bank_statement observable.")

    if "budget" in suite_text and not any(has_observable(case, "budget_occupation") for case in cases):
        errors.append("Budget signals found but no budget_occupation observable.")

    if any(token in suite_text for token in ("foreign currency", "exchange rate", "multi-currency", "fx")):
        if not any(has_observable(case, "exchange_rate") for case in cases):
            errors.append("Currency/exchange signals found but no exchange_rate observable.")

    return errors


def validate_finance(data: dict[str, Any]) -> list[str]:
    cases = [case for case in as_list(data.get("cases")) if isinstance(case, dict)]
    if not cases:
        return ["Top-level 'cases' must be a non-empty list."]

    if not looks_finance_suite(data, cases):
        return ["No finance suite signals found. This checker is intended for finance-domain suites."]

    errors: list[str] = []
    errors.extend(validate_suite_level(data, cases))

    for case in cases:
        errors.extend(validate_posting_case(case))
        errors.extend(validate_control_case(case))

    for case in cases:
        case_id = str(case.get("id", "<missing-id>"))
        if case.get("priority") == "P0" and not isinstance(case.get("finance"), dict):
            errors.append(f"{case_id} is P0 but has no finance block.")

    gates = data.get("quality_gates")
    if isinstance(gates, dict):
        for gate, value in gates.items():
            if gate.startswith("finance_") and value is False:
                errors.append(f"Finance quality gate is false: {gate}.")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: finance_coverage_check.py <cases.json|cases.yaml>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    try:
        data = load_data(path)
        if not isinstance(data, dict):
            raise RuntimeError("Top-level document must be an object.")
        errors = validate_finance(data)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("Finance coverage check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Finance coverage check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
