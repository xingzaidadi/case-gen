# Finance Expense Reimbursement Domain Coverage Eval

> Mode: mixed

## Assumptions

- Budget control is enabled.
- Employee payable voucher rules are represented as RULE-EXP-POSTING.

## Coverage Map

| Source/Test Point | Priority | Status | Cases |
| --- | --- | --- | --- |
| REQ-EXP-001 | P0 | covered | TC-FIN-EXP-001, TC-FIN-EXP-006 |
| REQ-EXP-002 | P0 | covered | TC-FIN-EXP-003 |
| REQ-EXP-003 | P0 | covered | TC-FIN-EXP-005 |
| RULE-EXP-POSTING | P0 | covered | TC-FIN-EXP-001, TC-FIN-EXP-005, TC-FIN-EXP-006 |
| TP-EXP-E2E-001 |  | covered | TC-FIN-EXP-001 |
| TP-EXP-CTRL-001 |  | covered | TC-FIN-EXP-002, TC-FIN-EXP-003, TC-FIN-EXP-004 |
| TP-EXP-ACCT-001 |  | covered | TC-FIN-EXP-001, TC-FIN-EXP-005, TC-FIN-EXP-006 |

## Cases

| ID | Priority | Level | Type | Title | Traceability | Expected |
| --- | --- | --- | --- | --- | --- | --- |
| TC-FIN-EXP-001 | P0 | e2e | happy_path | Approved expense reimbursement consumes budget, pays employee, posts balanced voucher, and reconciles | REQ-EXP-001, RULE-EXP-POSTING, LAW-ACCOUNTING, CIC-BASIC, TP-EXP-E2E-001, TP-EXP-ACCT-001 | Invoice status is validated and linked to expense report EXP-001. [invoice_status]<br>Tax amount is 30.00 CNY and reimbursement amount is 530.00 CNY with configured rounding. [tax_amount]<br>Budget occupation is created at submission and consumed after successful payment. [budget_occupation]<br>Approval chain records department head and finance reviewer before payment release. [approval_chain]<br>Payment status reaches paid and bank receipt matches employee, account, amount, currency, and reference. [payment_status]<br>Bank receipt is linked as paid evidence. [bank_receipt]<br>Journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds: debit equals credit for 530.00 CNY. [journal_voucher]<br>Employee payable subledger clears and GL balance reflects reimbursement settlement. [subledger_balance]<br>Expense report, invoice, payment, bank receipt, subledger, GL, and report line reconcile with zero difference. [reconciliation_result] |
| TC-FIN-EXP-002 | P0 | api | negative | Duplicate or invalid invoice blocks reimbursement and tax recognition | REQ-EXP-001, STA-INVOICE, CIC-BASIC, RISK-EXP-001, TP-EXP-CTRL-001 | Duplicate invoice is rejected and no expense report payable is created. [response]<br>Invoice status remains used_by_existing_report and is not relinked. [invoice_status]<br>No tax amount is recognized for the rejected reimbursement. [tax_amount]<br>Retry with same request id is idempotent and does not create a second draft. [control_evidence] |
| TC-FIN-EXP-003 | P0 | integration | boundary | Approval matrix boundary at 500.00 CNY selects the required approvers | REQ-EXP-002, CIC-BASIC, TP-EXP-CTRL-001 | 499.99 and 500.00 CNY route to direct manager; 500.01 CNY routes to department head plus finance reviewer. [approval_chain]<br>Control evidence records the approval matrix branch and amount used for the decision. [control_evidence] |
| TC-FIN-EXP-004 | P0 | security | security | Requester self-approval and expired delegation are forbidden with SoD audit evidence | REQ-EXP-001, CIC-BASIC, OWASP-API-2023, RISK-EXP-002, TP-EXP-CTRL-001 | Approval is forbidden for self-approval and expired delegation; expense status remains submitted. [response]<br>Approval chain contains no invalid approver node. [approval_chain]<br>Audit evidence records segregation of duties denial and delegation expiry reason. [audit_evidence]<br>Security log is emitted for wrong role / SoD denial. [log] |
| TC-FIN-EXP-005 | P0 | integration | state_transition | Hard-closed period rejects reimbursement posting and preserves cut-off | REQ-EXP-003, RULE-EXP-POSTING, LAW-ACCOUNTING, RISK-EXP-003, TP-EXP-ACCT-001 | Invalid transition from approved to posted is rejected because period 2026-05 is hard_closed. [period_status]<br>No journal voucher is created in the closed period; debit_credit_balance is unchanged. [journal_voucher]<br>Employee payable subledger and GL balances remain unchanged. [general_ledger_balance]<br>Audit evidence records closed-period cut-off denial. [audit_evidence] |
| TC-FIN-EXP-006 | P0 | integration | negative | Bank rejection or voided invoice after approval keeps reimbursement unpaid and unreconciled | REQ-EXP-001, RULE-EXP-POSTING, STA-INVOICE, RISK-EXP-001, TP-EXP-E2E-001, TP-EXP-ACCT-001 | Invoice status becomes voided_exception and blocks payment completion. [invoice_status]<br>Payment status becomes bank_rejected and employee payable remains open. [payment_status]<br>Bank statement records rejected instruction and no paid bank receipt is attached. [bank_statement]<br>No settlement journal voucher is posted in period 2026-06; debit_credit_balance remains unchanged. [journal_voucher]<br>Budget occupation follows configured exception policy and reconciliation shows no clearing difference. [reconciliation_result]<br>Audit evidence links bank rejection and voided invoice exception. [audit_evidence] |

## Open Questions

| ID | Question | Impact | Owner |
| --- | --- | --- | --- |
| Q-EXP-001 | Which reimbursement categories are VAT deductible and which require tax transfer-out? | affects_p1 | finance |

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
