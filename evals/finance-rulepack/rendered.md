# Finance Rulepack Reference Eval

> Mode: mixed

## Assumptions

- Rulepack contains placeholder internal rules for validation only.

## Coverage Map

| Source/Test Point | Priority | Status | Cases |
| --- | --- | --- | --- |
| SOD-SUPPLIER-BANK-PAYMENT | P0 | covered | TC-RULEPACK-001 |
| CTRL-CLOSED-PERIOD-NO-POST | P0 | covered | TC-RULEPACK-002 |
| TP-RULEPACK-001 |  | covered | TC-RULEPACK-001, TC-RULEPACK-002 |

## Cases

| ID | Priority | Level | Type | Title | Traceability | Expected |
| --- | --- | --- | --- | --- | --- | --- |
| TC-RULEPACK-001 | P0 | security | security | Supplier bank account change uses internal SoD, duplicate payment, bank callback, and audit observability rules | LE-XM-CN-01, SOD-SUPPLIER-BANK-PAYMENT, CTRL-DUPLICATE-PAYMENT, INT-BANK-PAYMENT-CALLBACK, OBS-AUDIT-LOG, INC-DUP-PAYMENT-PLACEHOLDER, TP-RULEPACK-001 | Same-maintainer approval is denied by SOD-SUPPLIER-BANK-PAYMENT. [response]<br>Duplicate payment prevention uses CTRL-DUPLICATE-PAYMENT and payment status remains not released. [payment_status]<br>Bank gateway receives no outgoing instruction for this denied release. [bank_statement]<br>Audit evidence follows OBS-AUDIT-LOG with actor, timestamp, old/new value, and denied rule id. [audit_evidence]<br>Security log records wrong role / SoD denial. [log] |
| TC-RULEPACK-002 | P0 | integration | state_transition | Closed-period posting uses internal period, voucher, account, and tax rulepack ids | LE-XM-CN-01, POLICY-PERIOD-CUTOFF, CTRL-CLOSED-PERIOD-NO-POST, OBS-VOUCHER-TABLE, ACC-AP-PAYABLE, TAX-VAT-IN-06, TP-RULEPACK-001 | Invalid posting transition is rejected by CTRL-CLOSED-PERIOD-NO-POST and period remains terminal hard_closed. [period_status]<br>Invoice status remains validated_not_posted and is not moved to posted in the closed period. [invoice_status]<br>No voucher row is created in OBS-VOUCHER-TABLE; debit_credit_balance is unchanged. [journal_voucher]<br>No tax amount is recognized for TAX-VAT-IN-06 in the closed period. [tax_amount]<br>AP payable account ACC-AP-PAYABLE and GL balance remain unchanged. [general_ledger_balance]<br>Invoice, AP subledger, tax amount, and GL reconciliation remain unchanged with zero unauthorized difference. [reconciliation_result]<br>Audit evidence records closed-period denial and rulepack ids. [audit_evidence] |

## Open Questions

| ID | Question | Impact | Owner |
| --- | --- | --- | --- |
| Q-RULEPACK-001 | Replace placeholder rulepack ids with approved Xiaomi internal ids before production use. | blocks_p0 | finance |

## Quality Gates

| Gate | Status |
| --- | --- |
| p0_sources_covered | True |
| no_happy_path_only | True |
| all_cases_have_traceability | True |
| all_cases_have_observable_expected | True |
| boundary_cases_have_concrete_values | True |
| state_cases_include_invalid_transitions | True |
| security_cases_include_negative_authorization | True |
| e2e_layer_cross_check_complete | True |
| finance_voucher_or_ledger_asserted | True |
| finance_debit_credit_balance_asserted | True |
| finance_period_cutoff_asserted | True |
| finance_reconciliation_asserted | True |
| finance_control_evidence_asserted | True |
