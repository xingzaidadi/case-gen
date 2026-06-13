Feature: Finance Expense Reimbursement Domain Coverage Eval

  @p0 @e2e @happy_path
  Scenario: TC-FIN-EXP-001 Approved expense reimbursement consumes budget, pays employee, posts balanced voucher, and reconciles
    Given Accounting period 2026-06 is open.
    And Expense report EXP-001 has valid VAT invoice INV-EXP-001 and available budget.
    When Submit expense report and validate invoice, tax amount, cost center, project, and budget.
    And Approve with department head and finance reviewer, then release employee payment.
    And Receive bank success and run reimbursement posting.
    Then Invoice status is validated and linked to expense report EXP-001.
    And Tax amount is 30.00 CNY and reimbursement amount is 530.00 CNY with configured rounding.
    And Budget occupation is created at submission and consumed after successful payment.
    And Approval chain records department head and finance reviewer before payment release.
    And Payment status reaches paid and bank receipt matches employee, account, amount, currency, and reference.
    And Bank receipt is linked as paid evidence.
    And Journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds: debit equals credit for 530.00 CNY.
    And Employee payable subledger clears and GL balance reflects reimbursement settlement.
    And Expense report, invoice, payment, bank receipt, subledger, GL, and report line reconcile with zero difference.

  @p0 @api @negative
  Scenario: TC-FIN-EXP-002 Duplicate or invalid invoice blocks reimbursement and tax recognition
    Given Invoice INV-DUP-EXP-001 was used by another paid expense report.
    When Submit reimbursement with duplicate invoice and same business key.
    And Retry the same submit request after timeout.
    Then Duplicate invoice is rejected and no expense report payable is created.
    And Invoice status remains used_by_existing_report and is not relinked.
    And No tax amount is recognized for the rejected reimbursement.
    And Retry with same request id is idempotent and does not create a second draft.

  @p0 @integration @boundary
  Scenario: TC-FIN-EXP-003 Approval matrix boundary at 500.00 CNY selects the required approvers
    Given Approval limit is 500.00 CNY.
    When Submit expense reports at 499.99, 500.00, and 500.01 CNY.
    Then 499.99 and 500.00 CNY route to direct manager; 500.01 CNY routes to department head plus finance reviewer.
    And Control evidence records the approval matrix branch and amount used for the decision.

  @p0 @security @security
  Scenario: TC-FIN-EXP-004 Requester self-approval and expired delegation are forbidden with SoD audit evidence
    Given Employee ACT-EMP submitted expense report EXP-SOD-001.
    And Delegation for ACT-MGR-DELEGATE expired yesterday.
    When Attempt approval as requester and as expired delegate.
    Then Approval is forbidden for self-approval and expired delegation; expense status remains submitted.
    And Approval chain contains no invalid approver node.
    And Audit evidence records segregation of duties denial and delegation expiry reason.
    And Security log is emitted for wrong role / SoD denial.

  @p0 @integration @state_transition
  Scenario: TC-FIN-EXP-005 Hard-closed period rejects reimbursement posting and preserves cut-off
    Given Accounting period 2026-05 is hard_closed.
    And Expense report EXP-CLOSE-001 is approved but not posted.
    When Attempt to post reimbursement voucher into hard_closed period 2026-05.
    Then Invalid transition from approved to posted is rejected because period 2026-05 is hard_closed.
    And No journal voucher is created in the closed period; debit_credit_balance is unchanged.
    And Employee payable subledger and GL balances remain unchanged.
    And Audit evidence records closed-period cut-off denial.

  @p0 @integration @negative
  Scenario: TC-FIN-EXP-006 Bank rejection or voided invoice after approval keeps reimbursement unpaid and unreconciled
    Given Expense report EXP-BANK-001 is approved and sent to bank.
    And Invoice INV-EXP-VOID-001 becomes voided before payment confirmation.
    When Receive bank rejection and invoice void status update.
    Then Invoice status becomes voided_exception and blocks payment completion.
    And Payment status becomes bank_rejected and employee payable remains open.
    And Bank statement records rejected instruction and no paid bank receipt is attached.
    And No settlement journal voucher is posted in period 2026-06; debit_credit_balance remains unchanged.
    And Budget occupation follows configured exception policy and reconciliation shows no clearing difference.
    And Audit evidence links bank rejection and voided invoice exception.
