Feature: Finance AP Payment Domain Coverage Eval

  @p0 @e2e @happy_path
  Scenario: TC-FIN-AP-001 Approved supplier payment posts balanced AP settlement and reconciles bank/AP/GL
    Given Accounting period 2026-06 is open.
    And Supplier invoice INV-AP-001 is validated, not paid, and has tax amount 60.00 CNY.
    And Budget center BUD-AP-001 has available budget above 1060.00 CNY.
    When Create AP payment request from validated supplier invoice INV-AP-001.
    And Approve the request with finance manager and release payment to bank.
    And Receive bank accepted result and run AP settlement posting.
    Then Invoice status becomes paid and remains linked to payment request PAY-AP-001.
    And Approval chain records requester, finance manager, treasury releaser, timestamps, and no self-approval.
    And Budget occupation is created before bank release and consumed after successful settlement.
    And Payment status reaches paid with bank reference BNK-AP-001.
    And Bank receipt amount, payee, bank account, currency, and external reference match the approved request.
    And Journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds: debit equals credit for 1060.00 CNY.
    And AP subledger open item is cleared and GL control account balance reflects the settlement.
    And Invoice, payment, bank receipt, AP subledger, GL, and report line reconcile with zero difference.

  @p0 @api @negative
  Scenario: TC-FIN-AP-002 Duplicate invoice and duplicate payment keys prevent overpayment
    Given Supplier invoice INV-DUP-001 already has paid payment request PAY-DUP-001.
    When Submit a second payment request for the same supplier invoice.
    And Retry the first request id after timeout.
    Then Second business-key duplicate is rejected with a safe duplicate-payment error and no new payment is created.
    And Retry with same request id is idempotent and returns existing payment PAY-DUP-001.
    And Invoice status remains paid and no duplicate invoice settlement is created.
    And Control evidence records duplicate invoice/payment prevention decision.

  @p0 @integration @boundary
  Scenario: TC-FIN-AP-003 Approval matrix boundary at 1000.00 CNY selects correct approver
    Given Approval limit is 1000.00 CNY.
    When Create payment requests at 999.99, 1000.00, and 1000.01 CNY.
    And Inspect assigned approver role for each request.
    Then 999.99 and 1000.00 CNY route to finance reviewer; 1000.01 CNY routes to finance manager.
    And Control evidence records the limit rule, selected branch, and amount used for the decision.

  @p0 @security @security
  Scenario: TC-FIN-AP-004 Requester self-approval is forbidden and recorded as SoD control denial
    Given Requester ACT-REQUESTER created payment request PAY-SOD-001.
    When Call approve payment as the same requester.
    Then Approval is forbidden with wrong role / self-approval error; payment status remains submitted.
    And Approval chain has no approval node from ACT-REQUESTER.
    And Audit evidence records segregation of duties denial with actor, payment id, timestamp, and reason.
    And Security metric/log is emitted for SoD denial.

  @p0 @integration @state_transition
  Scenario: TC-FIN-AP-005 Hard-closed period rejects invalid posting transition and preserves cut-off
    Given Accounting period 2026-05 is hard_closed.
    And Payment request PAY-CLOSE-001 is approved but not posted.
    When Attempt to post AP settlement into hard_closed period 2026-05.
    Then Invalid transition from approved to posted is rejected because period 2026-05 is hard_closed.
    And No journal voucher is generated in the closed period; debit_credit_balance is not affected.
    And AP subledger and GL balances remain unchanged for period 2026-05.
    And Audit evidence records closed-period posting denial and required reopen workflow.

  @p0 @integration @negative
  Scenario: TC-FIN-AP-006 Bank rejection does not clear AP or create settlement voucher
    Given Payment request PAY-BANK-REJ-001 is approved and sent to bank in open period 2026-06.
    When Receive bank rejection callback.
    Then Payment status becomes bank_rejected and AP open item remains unpaid.
    And Bank statement records rejected instruction and no bank receipt is attached as paid evidence.
    And No settlement journal voucher is posted in period 2026-06; debit_credit_balance remains unchanged.
    And Subledger and GL reconciliation shows no clearing difference and no orphan settlement item.
    And Audit evidence links bank rejection to payment request and exception workflow.

  @p1 @integration @state_transition
  Scenario: TC-FIN-AP-007 Red-letter supplier invoice reverses tax and accounting impact with traceability
    Given Original supplier invoice INV-RED-001 is paid and posted in open period 2026-06.
    When Create red-letter invoice for the original paid supplier invoice.
    Then Invoice status moves through valid reversal transition and terminal red_lettered state; invalid over-red-letter amount is rejected.
    And Tax amount is reversed for 60.00 CNY with traceability to original invoice.
    And Reversal journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds.
    And Original and reversal documents reconcile to zero net payable and zero net tax impact.

  @p0 @security @security
  Scenario: TC-FIN-AP-008 Supplier bank account change blocks payment until independent approval
    Given Supplier S001 bank account was changed by ACT-REQUESTER and is pending independent approval.
    And Payment PAY-BANK-CHANGE-001 references supplier S001.
    When Attempt to release payment to bank before independent approval of supplier bank account change.
    Then Payment release is forbidden until independent supplier bank account approval is complete.
    And Payment status remains approved_not_released and no bank instruction is sent.
    And Control evidence records sensitive master-data approval dependency and segregation of duties rule.
    And Audit evidence links supplier bank account change, approver requirement, and payment release denial.
