Feature: Finance Period Close Domain Coverage Eval

  @p0 @e2e @happy_path
  Scenario: TC-FIN-CLOSE-001 Month-end close completes from open to hard_closed with balanced closing voucher and reconciliation
    Given Legal entity XM-CN-01 period 2026-06 is open.
    And All prerequisite close checks are passed with zero exception count.
    When Run prerequisite checks for period 2026-06.
    And Submit close approval and execute soft close then hard close.
    Then Period status transitions open -> soft_closed -> hard_closed with terminal hard_closed state.
    And Closing journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds: debit equals credit.
    And Subledger balances reconcile to GL control accounts after close.
    And Financial report line readiness is published for period 2026-06.
    And Audit evidence records prerequisite results, close approval chain, close job id, and terminal state timestamp.

  @p0 @integration @negative
  Scenario: TC-FIN-CLOSE-002 Close is blocked when prerequisite exceptions remain, and retry is idempotent
    Given Period 2026-06 is open.
    And Prerequisite check has one unreconciled subledger difference and one unposted voucher.
    When Attempt to hard close period while prerequisite exceptions remain.
    And Retry the same close request after timeout.
    Then Close is rejected and period status remains open because prerequisite exceptions remain.
    And Retry is idempotent and does not create duplicate close tasks or duplicate closing vouchers.
    And No journal voucher is generated; debit_credit_balance is unchanged.
    And Reconciliation result shows prerequisite difference and blocks report-line readiness.
    And Audit evidence records failed prerequisite names and exception counts.

  @p0 @integration @state_transition
  Scenario: TC-FIN-CLOSE-003 Hard-closed period rejects invalid posting, reversal, and sensitive mutation
    Given Period 2026-06 is hard_closed.
    When Attempt manual posting, reversal, and backdated document mutation in hard_closed period.
    Then Invalid transition from hard_closed to posted/reversed is forbidden and terminal hard_closed state is preserved.
    And No journal voucher or reversal voucher is generated in hard_closed period; debit_credit_balance is unchanged.
    And GL balance and report line remain unchanged.
    And Audit evidence records closed-period mutation denial.

  @p0 @integration @decision_table
  Scenario: TC-FIN-CLOSE-004 Soft close blocks normal posting but allows approved adjustment voucher
    Given Period 2026-06 is soft_closed.
    When Submit normal business posting, approved adjustment, and unapproved adjustment in soft_closed period.
    Then Normal posting and unapproved adjustment are rejected; approved adjustment is posted.
    And Approved adjustment journal voucher is generated exactly once and debit_credit_balance holds.
    And Subledger, GL, and report line reconciliation is recalculated after approved adjustment.
    And Approval chain and audit evidence identify adjustment reason and approver.

  @p0 @security @security
  Scenario: TC-FIN-CLOSE-005 Privileged reopen requires independent approval and rejects same-operator approval
    Given Period 2026-06 is hard_closed.
    And ACT-CLOSE-OP created reopen request REOPEN-202606-001.
    When Attempt reopen approval as same operator, then as independent approver.
    And Post approved adjustment and reclose the period.
    Then Same-operator reopen approval is forbidden with wrong role / segregation of duties denial.
    And Independent approval moves period hard_closed -> reopened -> reclosed with full traceability.
    And Adjustment journal voucher is generated once and debit_credit_balance holds for 100.00 CNY.
    And Reclosed period recomputes subledger/GL/report reconciliation with zero unexplained difference.
    And Audit evidence records reopen reason, same-operator denial, independent approver, adjustment voucher, and reclose timestamp.
    And Security log is emitted for forbidden same-operator approval.

  @p0 @integration @boundary
  Scenario: TC-FIN-CLOSE-006 Cut-off boundary assigns documents to the correct accounting period
    Given Period 2026-06 closes at 2026-06-30T23:59:59.
    When Submit three documents around the cut-off boundary.
    Then Documents before and exactly at cut-off are assigned to 2026-06; the document after cut-off is assigned to 2026-07 or rejected by policy.
    And Allowed postings generate journal vouchers in the assigned accounting period and debit_credit_balance holds.
    And GL and report line impacts appear only in the assigned period.
    And Reconciliation result separates 2026-06 and 2026-07 impacts without cross-period leakage.
    And Audit evidence records cut-off decision, source timestamp, assigned period, and rule version.
