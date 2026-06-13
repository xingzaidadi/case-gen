# Finance Project Rulepack

Use a project rulepack when a finance team has internal rules that should shape
case generation. The finance adapter gives the professional model; the rulepack
supplies company-specific facts.

The rulepack is intentionally explicit. Do not infer account codes, tax codes,
approval thresholds, integration events, or table names when they are missing.
Mark missing rules as open questions instead.

## When To Use

Load or create a rulepack when the user provides any of these:

- accounting policy, chart of accounts, account mapping, tax-code mapping
- approval matrix, SoD matrix, role list, delegation policy
- legal entity, company code,账套, cost center, project, department dimension
- system interface spec, event topic, callback, database table, reconciliation table
- historical incidents, defect list, production support cases
- finance test data, UAT checklist, regression suite, release checklist

## File Shape

Use JSON for deterministic validation:

```json
{
  "metadata": {
    "rulepack_id": "xiaomi-finance-placeholder",
    "version": "0.1.0",
    "owner": "finance-system-team",
    "updated_at": "2026-06-13",
    "status": "draft"
  },
  "legal_entities": [],
  "accounting_policies": [],
  "chart_of_accounts": [],
  "tax_codes": [],
  "approval_matrices": [],
  "segregation_of_duties": [],
  "finance_controls": [],
  "integration_points": [],
  "data_observability": [],
  "historical_incidents": [],
  "test_data_profiles": []
}
```

Each item must have an `id`, `name`, and `description`. IDs should be stable and
domain-prefixed, for example:

- `LE-XM-CN-01`
- `ACC-AP-PAYABLE`
- `TAX-VAT-IN-06`
- `APPROVAL-EXP-500`
- `SOD-SUPPLIER-BANK-PAYMENT`
- `CTRL-CLOSED-PERIOD-NO-POST`
- `INT-BANK-PAYMENT-CALLBACK`
- `OBS-VOUCHER-TABLE`
- `INC-DUP-PAYMENT-2025-001`
- `DATA-AP-HAPPY-PATH`

## Required Sections

| Section | Purpose |
| --- | --- |
| `legal_entities` | Legal entity, company code,账套, base currency, timezone, period calendar |
| `accounting_policies` | Posting timing, reversal behavior, cut-off policy, rounding policy |
| `chart_of_accounts` | Account id, account name, account type, allowed process, report line |
| `tax_codes` | Tax code, rate, direction, deduction/use rules, red-letter behavior |
| `approval_matrices` | Process, amount boundaries, org boundaries, approver roles |
| `segregation_of_duties` | Conflicting role/action combinations and required independent approval |
| `finance_controls` | Closed period, duplicate payment, duplicate invoice, budget, master data |
| `integration_points` | ERP, tax, bank, approval, MDM, budget, report, and event contracts |
| `data_observability` | Tables, events, logs, metrics, reports, and evidence locations |
| `historical_incidents` | Known defects or production risks that should become regression cases |
| `test_data_profiles` | Reusable legal entity, supplier, invoice, bank, currency, tax, budget data |

## Case Generation Rules

When a rulepack is available:

- Use rulepack IDs in `traceability.rules`, `traceability.risks`, or case notes.
- Prefer rulepack account/tax/control IDs over generic `RULE-*` placeholders.
- Every P0 finance case should reference at least one project-specific rulepack
  ID unless the case is explicitly exploratory or inferred.
- If a required rule is missing, add an `open_questions` item instead of
  inventing the rule.
- Historical incidents should become regression cases or explicit risk-derived
  test points.

## Quality Gates

A project-specific finance suite should pass these gates:

- P0 cases reference internal controls, policies, or observability rules.
- Posting cases reference account policy or chart-of-account mapping.
- Tax cases reference tax-code rules.
- Approval/SoD cases reference approval or SoD matrix rules.
- Integration cases reference event/API/table observability rules.
- Historical incidents are mapped to regression cases or consciously deferred.

