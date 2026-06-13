# Finance Period Close Domain Coverage Eval

> Mode: mixed

## Assumptions

- Month-end close may generate closing or adjustment vouchers according to RULE-GL-CLOSE.
- Close prerequisites are represented by deterministic system checks.

## Coverage Map

| Source/Test Point | Priority | Status | Cases |
| --- | --- | --- | --- |
| REQ-CLOSE-001 | P0 | covered | TC-FIN-CLOSE-001, TC-FIN-CLOSE-002 |
| REQ-CLOSE-002 | P0 | covered | TC-FIN-CLOSE-003, TC-FIN-CLOSE-006 |
| REQ-CLOSE-003 | P0 | covered | TC-FIN-CLOSE-005 |
| RULE-GL-CLOSE | P0 | covered | TC-FIN-CLOSE-001, TC-FIN-CLOSE-004, TC-FIN-CLOSE-005 |
| TP-CLOSE-E2E-001 |  | covered | TC-FIN-CLOSE-001 |
| TP-CLOSE-CTRL-001 |  | covered | TC-FIN-CLOSE-002, TC-FIN-CLOSE-005 |
| TP-CLOSE-ACCT-001 |  | covered | TC-FIN-CLOSE-001, TC-FIN-CLOSE-003, TC-FIN-CLOSE-004, TC-FIN-CLOSE-006 |

## Cases

| ID | Priority | Level | Type | Title | Traceability | Expected |
| --- | --- | --- | --- | --- | --- | --- |
| TC-FIN-CLOSE-001 | P0 | e2e | happy_path | Month-end close completes from open to hard_closed with balanced closing voucher and reconciliation | REQ-CLOSE-001, RULE-GL-CLOSE, LAW-ACCOUNTING, CIC-BASIC, TP-CLOSE-E2E-001, TP-CLOSE-ACCT-001 | Period status transitions open -> soft_closed -> hard_closed with terminal hard_closed state. [period_status]<br>Closing journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds: debit equals credit. [journal_voucher]<br>Subledger balances reconcile to GL control accounts after close. [reconciliation_result]<br>Financial report line readiness is published for period 2026-06. [financial_report_line]<br>Audit evidence records prerequisite results, close approval chain, close job id, and terminal state timestamp. [audit_evidence] |
| TC-FIN-CLOSE-002 | P0 | integration | negative | Close is blocked when prerequisite exceptions remain, and retry is idempotent | REQ-CLOSE-001, CIC-BASIC, RISK-CLOSE-001, TP-CLOSE-CTRL-001 | Close is rejected and period status remains open because prerequisite exceptions remain. [period_status]<br>Retry is idempotent and does not create duplicate close tasks or duplicate closing vouchers. [control_evidence]<br>No journal voucher is generated; debit_credit_balance is unchanged. [journal_voucher]<br>Reconciliation result shows prerequisite difference and blocks report-line readiness. [reconciliation_result]<br>Audit evidence records failed prerequisite names and exception counts. [audit_evidence] |
| TC-FIN-CLOSE-003 | P0 | integration | state_transition | Hard-closed period rejects invalid posting, reversal, and sensitive mutation | REQ-CLOSE-002, RULE-GL-CLOSE, LAW-ACCOUNTING, RISK-CLOSE-002, TP-CLOSE-ACCT-001 | Invalid transition from hard_closed to posted/reversed is forbidden and terminal hard_closed state is preserved. [period_status]<br>No journal voucher or reversal voucher is generated in hard_closed period; debit_credit_balance is unchanged. [journal_voucher]<br>GL balance and report line remain unchanged. [general_ledger_balance]<br>Audit evidence records closed-period mutation denial. [audit_evidence] |
| TC-FIN-CLOSE-004 | P0 | integration | decision_table | Soft close blocks normal posting but allows approved adjustment voucher | REQ-CLOSE-002, RULE-GL-CLOSE, RISK-CLOSE-002, TP-CLOSE-ACCT-001 | Normal posting and unapproved adjustment are rejected; approved adjustment is posted. [period_status]<br>Approved adjustment journal voucher is generated exactly once and debit_credit_balance holds. [journal_voucher]<br>Subledger, GL, and report line reconciliation is recalculated after approved adjustment. [reconciliation_result]<br>Approval chain and audit evidence identify adjustment reason and approver. [approval_chain] |
| TC-FIN-CLOSE-005 | P0 | security | security | Privileged reopen requires independent approval and rejects same-operator approval | REQ-CLOSE-003, CIC-BASIC, OWASP-API-2023, RISK-CLOSE-003, TP-CLOSE-CTRL-001, TP-CLOSE-ACCT-001 | Same-operator reopen approval is forbidden with wrong role / segregation of duties denial. [response]<br>Independent approval moves period hard_closed -> reopened -> reclosed with full traceability. [period_status]<br>Adjustment journal voucher is generated once and debit_credit_balance holds for 100.00 CNY. [journal_voucher]<br>Reclosed period recomputes subledger/GL/report reconciliation with zero unexplained difference. [reconciliation_result]<br>Audit evidence records reopen reason, same-operator denial, independent approver, adjustment voucher, and reclose timestamp. [audit_evidence]<br>Security log is emitted for forbidden same-operator approval. [log] |
| TC-FIN-CLOSE-006 | P0 | integration | boundary | Cut-off boundary assigns documents to the correct accounting period | REQ-CLOSE-002, RULE-GL-CLOSE, LAW-ACCOUNTING, RISK-CLOSE-002, TP-CLOSE-ACCT-001 | Documents before and exactly at cut-off are assigned to 2026-06; the document after cut-off is assigned to 2026-07 or rejected by policy. [period_status]<br>Allowed postings generate journal vouchers in the assigned accounting period and debit_credit_balance holds. [journal_voucher]<br>GL and report line impacts appear only in the assigned period. [financial_report_line]<br>Reconciliation result separates 2026-06 and 2026-07 impacts without cross-period leakage. [reconciliation_result]<br>Audit evidence records cut-off decision, source timestamp, assigned period, and rule version. [audit_evidence] |

## Open Questions

| ID | Question | Impact | Owner |
| --- | --- | --- | --- |
| Q-CLOSE-001 | Which prerequisite checks are hard blockers versus warnings for each legal entity? | blocks_p0 | finance |

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
