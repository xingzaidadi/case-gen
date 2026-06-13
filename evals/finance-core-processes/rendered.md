# Finance Core Processes Domain Coverage Eval

> Mode: mixed

## Assumptions

- Exact account codes and tax policy are project-specific and represented by RULE-* labels.
- The suite intentionally covers multiple finance domains to validate adapter breadth.

## Coverage Map

| Source/Test Point | Priority | Status | Cases |
| --- | --- | --- | --- |
| REQ-CORE-001 | P0 | covered | TC-FIN-CORE-001 |
| REQ-CORE-002 | P0 | covered | TC-FIN-CORE-002 |
| REQ-CORE-003 | P0 | covered | TC-FIN-CORE-003 |
| REQ-CORE-004 | P0 | covered | TC-FIN-CORE-004 |
| REQ-CORE-005 | P0 | covered | TC-FIN-CORE-005 |
| REQ-CORE-006 | P0 | covered | TC-FIN-CORE-006 |
| REQ-CORE-007 | P0 | covered | TC-FIN-CORE-007 |
| TP-CORE-001 |  | covered | TC-FIN-CORE-001 |
| TP-CORE-002 |  | covered | TC-FIN-CORE-002 |
| TP-CORE-003 |  | covered | TC-FIN-CORE-003, TC-FIN-CORE-004, TC-FIN-CORE-005, TC-FIN-CORE-006, TC-FIN-CORE-007 |

## Cases

| ID | Priority | Level | Type | Title | Traceability | Expected |
| --- | --- | --- | --- | --- | --- | --- |
| TC-FIN-CORE-001 | P0 | security | security | Supplier bank account change blocks payment until independent approval and SoD pass | REQ-CORE-001, CIC-BASIC, OWASP-API-2023, RISK-CORE-001, TP-CORE-001 | Same-maintainer approval is forbidden with wrong role / segregation of duties denial. [response]<br>Approval chain contains no approval from ACT-MDM and requires ACT-FIN-APPROVER. [approval_chain]<br>Payment status remains approved_not_released and duplicate payment is blocked until bank-account approval completes. [payment_status]<br>Bank statement has no outgoing payment instruction for PAY-MDM-001. [bank_statement]<br>Control evidence records sensitive master-data dependency, idempotency key, duplicate payment key, and SoD rule. [control_evidence]<br>Audit evidence records old/new bank account, actor, timestamp, approval requirement, and release denial. [audit_evidence]<br>Security log is emitted for forbidden self-approval. [log] |
| TC-FIN-CORE-002 | P0 | integration | state_transition | VAT red-letter invoice reverses original tax and accounting impact exactly once | REQ-CORE-002, STA-INVOICE, RULE-TAX-REDLETTER, LAW-ACCOUNTING, RISK-CORE-002, TP-CORE-002 | Invoice status follows valid transition posted -> red_lettered terminal state; invalid duplicate invoice red-letter is idempotent and returns RL-001. [invoice_status]<br>Tax amount reverses exactly 60.00 CNY and cannot exceed original tax amount. [tax_amount]<br>Reversal journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds. [journal_voucher]<br>Original invoice, red-letter invoice, tax reversal, subledger, GL, and report line reconcile to expected net impact. [reconciliation_result]<br>Audit evidence links red-letter invoice to original invoice, request id, actor, and rule version. [audit_evidence] |
| TC-FIN-CORE-003 | P0 | e2e | happy_path | AR receipt matches bank statement, clears customer open item, and reconciles AR to GL | REQ-CORE-003, RULE-AR-SETTLEMENT, LAW-ACCOUNTING, TP-CORE-003 | Bank statement line is linked to receipt and customer invoice. [bank_statement]<br>Payment status reaches received and AR open item is cleared. [payment_status]<br>Settlement journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds for 2000.00 CNY. [journal_voucher]<br>AR subledger balance equals GL control account after receipt settlement. [subledger_balance]<br>Customer invoice, bank statement, AR subledger, GL, and report line reconcile with zero difference. [reconciliation_result]<br>Audit evidence records matcher, posting actor, bank reference, and settlement voucher id. [audit_evidence] |
| TC-FIN-CORE-004 | P0 | integration | decision_table | GL manual journal enforces balance, approval matrix, SoD, and closed-period control | REQ-CORE-004, RULE-GL-JOURNAL, CIC-BASIC, LAW-ACCOUNTING, RISK-CORE-003, TP-CORE-003 | Balanced open-period journal is approved and posted; imbalanced, hard_closed, and self-approval rows are forbidden. [response]<br>Approval chain records independent approver and excludes creator self-approval. [approval_chain]<br>Posted journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds. [journal_voucher]<br>Hard-closed period 2026-05 remains terminal hard_closed with no ledger mutation. [period_status]<br>GL balance and financial report line update only for the allowed open-period journal. [financial_report_line]<br>Audit evidence records denied wrong role / self-approval and closed-period attempts. [audit_evidence] |
| TC-FIN-CORE-005 | P0 | integration | state_transition | Fixed asset capitalization and depreciation post balanced vouchers and reconcile asset subledger to GL | REQ-CORE-005, RULE-FA-LIFECYCLE, LAW-ACCOUNTING, TP-CORE-003 | Asset status follows valid transition acquired -> capitalized -> depreciating; invalid disposal before capitalization is rejected. [source_document]<br>Capitalization and depreciation journal vouchers are generated once and debit_credit_balance holds for each voucher. [journal_voucher]<br>Asset subledger carrying amount is 11000.00 CNY after first depreciation. [subledger_balance]<br>Asset subledger reconciles to fixed-asset GL and depreciation expense report line. [reconciliation_result]<br>Audit evidence records asset card, useful life, capitalization date, depreciation run id, and invalid transition denial. [audit_evidence] |
| TC-FIN-CORE-006 | P0 | integration | boundary | Budget occupation blocks over-budget request and releases exactly once on cancellation | REQ-CORE-006, RULE-BUDGET-CONTROL, CIC-BASIC, RISK-CORE-004, TP-CORE-003 | 999.99 and 1000.00 CNY occupy budget; 1000.01 CNY is blocked as over-budget. [budget_occupation]<br>Cancellation releases occupied budget exactly once; retry is idempotent and does not double release. [control_evidence]<br>No payment status is created for over-budget blocked request. [payment_status]<br>Budget occupation, source document, subledger/GL placeholder, and report impact reconcile to configured rule. [reconciliation_result]<br>Audit evidence records occupation, over-budget denial, cancellation, and idempotent retry. [audit_evidence] |
| TC-FIN-CORE-007 | P0 | integration | boundary | Cross-period cut-off assigns impact to correct period and rejects hard-closed mutation | REQ-CORE-007, RULE-PERIOD-CUTOFF, LAW-ACCOUNTING, RISK-CORE-003, TP-CORE-003 | Before and exactly at cut-off are assigned to 2026-06; after cut-off is assigned to 2026-07 or rejected by policy. [period_status]<br>Backdated mutation into hard_closed 2026-05 is forbidden and terminal hard_closed state is preserved. [period_status]<br>Allowed journal vouchers are posted only in assigned periods and debit_credit_balance holds. [journal_voucher]<br>Financial report line impact appears only in the assigned period. [financial_report_line]<br>Reconciliation separates 2026-06 and 2026-07 impact without cross-period leakage. [reconciliation_result]<br>Audit evidence records cut-off decision, rejected hard_closed mutation, actor, and rule version. [audit_evidence] |

## Open Questions

| ID | Question | Impact | Owner |
| --- | --- | --- | --- |
| Q-CORE-001 | Which internal account codes, tax codes, asset classes, and budget dimensions apply for each Xiaomi legal entity? | blocks_p0 | finance |

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
