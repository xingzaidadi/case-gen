# Finance AP Payment Domain Coverage Eval

> Mode: mixed

## Assumptions

- Accounting policy and exact account codes are project-specific and represented as RULE-AP-POSTING.
- Budget control is enabled for this eval.

## Coverage Map

| Source/Test Point | Priority | Status | Cases |
| --- | --- | --- | --- |
| REQ-AP-001 | P0 | covered | TC-FIN-AP-001, TC-FIN-AP-006 |
| REQ-AP-002 | P0 | covered | TC-FIN-AP-003 |
| REQ-AP-003 | P0 | covered | TC-FIN-AP-005 |
| RULE-CIC-BASIC | P0 | covered | TC-FIN-AP-004, TC-FIN-AP-008 |
| RULE-AP-POSTING | P0 | covered | TC-FIN-AP-001, TC-FIN-AP-005, TC-FIN-AP-006 |
| TP-E2E-AP-001 |  | covered | TC-FIN-AP-001 |
| TP-CTRL-AP-001 |  | covered | TC-FIN-AP-002 |
| TP-CTRL-AP-002 |  | covered | TC-FIN-AP-003, TC-FIN-AP-004, TC-FIN-AP-008 |
| TP-ACCT-AP-001 |  | covered | TC-FIN-AP-001, TC-FIN-AP-005, TC-FIN-AP-006 |

## Cases

| ID | Priority | Level | Type | Title | Traceability | Expected |
| --- | --- | --- | --- | --- | --- | --- |
| TC-FIN-AP-001 | P0 | e2e | happy_path | Approved supplier payment posts balanced AP settlement and reconciles bank/AP/GL | REQ-AP-001, RULE-AP-POSTING, LAW-ACCOUNTING, CIC-BASIC, TP-E2E-AP-001, TP-ACCT-AP-001 | Invoice status becomes paid and remains linked to payment request PAY-AP-001. [invoice_status]<br>Approval chain records requester, finance manager, treasury releaser, timestamps, and no self-approval. [approval_chain]<br>Budget occupation is created before bank release and consumed after successful settlement. [budget_occupation]<br>Payment status reaches paid with bank reference BNK-AP-001. [payment_status]<br>Bank receipt amount, payee, bank account, currency, and external reference match the approved request. [bank_receipt]<br>Journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds: debit equals credit for 1060.00 CNY. [journal_voucher]<br>AP subledger open item is cleared and GL control account balance reflects the settlement. [subledger_balance]<br>Invoice, payment, bank receipt, AP subledger, GL, and report line reconcile with zero difference. [reconciliation_result] |
| TC-FIN-AP-002 | P0 | api | negative | Duplicate invoice and duplicate payment keys prevent overpayment | REQ-AP-001, CIC-BASIC, RISK-001, TP-CTRL-AP-001 | Second business-key duplicate is rejected with a safe duplicate-payment error and no new payment is created. [response]<br>Retry with same request id is idempotent and returns existing payment PAY-DUP-001. [payment_status]<br>Invoice status remains paid and no duplicate invoice settlement is created. [invoice_status]<br>Control evidence records duplicate invoice/payment prevention decision. [control_evidence] |
| TC-FIN-AP-003 | P0 | integration | boundary | Approval matrix boundary at 1000.00 CNY selects correct approver | REQ-AP-002, CIC-BASIC, TP-CTRL-AP-002 | 999.99 and 1000.00 CNY route to finance reviewer; 1000.01 CNY routes to finance manager. [approval_chain]<br>Control evidence records the limit rule, selected branch, and amount used for the decision. [control_evidence] |
| TC-FIN-AP-004 | P0 | security | security | Requester self-approval is forbidden and recorded as SoD control denial | REQ-AP-001, CIC-BASIC, OWASP-API-2023, RISK-003, TP-CTRL-AP-002 | Approval is forbidden with wrong role / self-approval error; payment status remains submitted. [response]<br>Approval chain has no approval node from ACT-REQUESTER. [approval_chain]<br>Audit evidence records segregation of duties denial with actor, payment id, timestamp, and reason. [audit_evidence]<br>Security metric/log is emitted for SoD denial. [log] |
| TC-FIN-AP-005 | P0 | integration | state_transition | Hard-closed period rejects invalid posting transition and preserves cut-off | REQ-AP-003, RULE-AP-POSTING, LAW-ACCOUNTING, RISK-002, TP-ACCT-AP-001 | Invalid transition from approved to posted is rejected because period 2026-05 is hard_closed. [period_status]<br>No journal voucher is generated in the closed period; debit_credit_balance is not affected. [journal_voucher]<br>AP subledger and GL balances remain unchanged for period 2026-05. [general_ledger_balance]<br>Audit evidence records closed-period posting denial and required reopen workflow. [audit_evidence] |
| TC-FIN-AP-006 | P0 | integration | negative | Bank rejection does not clear AP or create settlement voucher | REQ-AP-001, RULE-AP-POSTING, TP-E2E-AP-001, TP-ACCT-AP-001 | Payment status becomes bank_rejected and AP open item remains unpaid. [payment_status]<br>Bank statement records rejected instruction and no bank receipt is attached as paid evidence. [bank_statement]<br>No settlement journal voucher is posted in period 2026-06; debit_credit_balance remains unchanged. [journal_voucher]<br>Subledger and GL reconciliation shows no clearing difference and no orphan settlement item. [reconciliation_result]<br>Audit evidence links bank rejection to payment request and exception workflow. [audit_evidence] |
| TC-FIN-AP-007 | P1 | integration | state_transition | Red-letter supplier invoice reverses tax and accounting impact with traceability | REQ-AP-001, STA-INVOICE, RULE-AP-POSTING, TP-ACCT-AP-001, inferred | Invoice status moves through valid reversal transition and terminal red_lettered state; invalid over-red-letter amount is rejected. [invoice_status]<br>Tax amount is reversed for 60.00 CNY with traceability to original invoice. [tax_amount]<br>Reversal journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds. [journal_voucher]<br>Original and reversal documents reconcile to zero net payable and zero net tax impact. [reconciliation_result] |
| TC-FIN-AP-008 | P0 | security | security | Supplier bank account change blocks payment until independent approval | REQ-AP-001, CIC-BASIC, OWASP-API-2023, RISK-003, TP-CTRL-AP-002, inferred | Payment release is forbidden until independent supplier bank account approval is complete. [response]<br>Payment status remains approved_not_released and no bank instruction is sent. [payment_status]<br>Control evidence records sensitive master-data approval dependency and segregation of duties rule. [control_evidence]<br>Audit evidence links supplier bank account change, approver requirement, and payment release denial. [audit_evidence] |

## Open Questions

| ID | Question | Impact | Owner |
| --- | --- | --- | --- |
| Q-001 | What are the exact AP account codes, tax accounts, and bank clearing accounts for each legal entity? | affects_p1 | finance |
| Q-002 | Should AP settlement voucher be posted at bank acceptance or bank reconciliation? | blocks_p0 | product |

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
