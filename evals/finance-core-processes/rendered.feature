Feature: Finance Core Processes Domain Coverage Eval

  @p0 @security @security
  Scenario: TC-FIN-CORE-001 Supplier bank account change blocks payment until independent approval and SoD pass
    Given Supplier S001 bank account was changed by ACT-MDM and is pending independent approval.
    And Payment request PAY-MDM-001 references supplier S001.
    When Attempt to approve the bank account change as the same maintainer.
    And Attempt to release duplicate payment before independent approval.
    Then Same-maintainer approval is forbidden with wrong role / segregation of duties denial.
    And Approval chain contains no approval from ACT-MDM and requires ACT-FIN-APPROVER.
    And Payment status remains approved_not_released and duplicate payment is blocked until bank-account approval completes.
    And Bank statement has no outgoing payment instruction for PAY-MDM-001.
    And Control evidence records sensitive master-data dependency, idempotency key, duplicate payment key, and SoD rule.
    And Audit evidence records old/new bank account, actor, timestamp, approval requirement, and release denial.
    And Security log is emitted for forbidden self-approval.

  @p0 @integration @state_transition
  Scenario: TC-FIN-CORE-002 VAT red-letter invoice reverses original tax and accounting impact exactly once
    Given Original VAT invoice INV-TAX-001 is posted in open period 2026-06.
    And No prior red-letter invoice exists for INV-TAX-001.
    When Create red-letter invoice for original invoice INV-TAX-001.
    And Retry red-letter creation with the same request id.
    Then Invoice status follows valid transition posted -> red_lettered terminal state; invalid duplicate invoice red-letter is idempotent and returns RL-001.
    And Tax amount reverses exactly 60.00 CNY and cannot exceed original tax amount.
    And Reversal journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds.
    And Original invoice, red-letter invoice, tax reversal, subledger, GL, and report line reconcile to expected net impact.
    And Audit evidence links red-letter invoice to original invoice, request id, actor, and rule version.

  @p0 @e2e @happy_path
  Scenario: TC-FIN-CORE-003 AR receipt matches bank statement, clears customer open item, and reconciles AR to GL
    Given Customer invoice AR-INV-001 is open for 2000.00 CNY in period 2026-06.
    And Bank statement line BNK-AR-001 is available for 2000.00 CNY.
    When Match bank statement line to customer invoice AR-INV-001.
    And Post AR receipt settlement.
    Then Bank statement line is linked to receipt and customer invoice.
    And Payment status reaches received and AR open item is cleared.
    And Settlement journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds for 2000.00 CNY.
    And AR subledger balance equals GL control account after receipt settlement.
    And Customer invoice, bank statement, AR subledger, GL, and report line reconcile with zero difference.
    And Audit evidence records matcher, posting actor, bank reference, and settlement voucher id.

  @p0 @integration @decision_table
  Scenario: TC-FIN-CORE-004 GL manual journal enforces balance, approval matrix, SoD, and closed-period control
    Given Period 2026-06 is open and period 2026-05 is hard_closed.
    When Submit balanced journal, imbalanced journal, hard-closed-period journal, and self-approved journal.
    Then Balanced open-period journal is approved and posted; imbalanced, hard_closed, and self-approval rows are forbidden.
    And Approval chain records independent approver and excludes creator self-approval.
    And Posted journal voucher is generated exactly once in period 2026-06 and debit_credit_balance holds.
    And Hard-closed period 2026-05 remains terminal hard_closed with no ledger mutation.
    And GL balance and financial report line update only for the allowed open-period journal.
    And Audit evidence records denied wrong role / self-approval and closed-period attempts.

  @p0 @integration @state_transition
  Scenario: TC-FIN-CORE-005 Fixed asset capitalization and depreciation post balanced vouchers and reconcile asset subledger to GL
    Given Asset FA-001 is acquired for 12000.00 CNY and period 2026-06 is open.
    And Useful life is 12 months and residual value is 0.00 CNY.
    When Capitalize asset FA-001.
    And Run first depreciation and attempt invalid disposal before capitalization is complete.
    Then Asset status follows valid transition acquired -> capitalized -> depreciating; invalid disposal before capitalization is rejected.
    And Capitalization and depreciation journal vouchers are generated once and debit_credit_balance holds for each voucher.
    And Asset subledger carrying amount is 11000.00 CNY after first depreciation.
    And Asset subledger reconciles to fixed-asset GL and depreciation expense report line.
    And Audit evidence records asset card, useful life, capitalization date, depreciation run id, and invalid transition denial.

  @p0 @integration @boundary
  Scenario: TC-FIN-CORE-006 Budget occupation blocks over-budget request and releases exactly once on cancellation
    Given Budget center BUD-001 has available amount 1000.00 CNY.
    When Submit budget occupation requests at 999.99, 1000.00, and 1000.01 CNY.
    And Cancel an occupied request twice with the same idempotency key.
    Then 999.99 and 1000.00 CNY occupy budget; 1000.01 CNY is blocked as over-budget.
    And Cancellation releases occupied budget exactly once; retry is idempotent and does not double release.
    And No payment status is created for over-budget blocked request.
    And Budget occupation, source document, subledger/GL placeholder, and report impact reconcile to configured rule.
    And Audit evidence records occupation, over-budget denial, cancellation, and idempotent retry.

  @p0 @integration @boundary
  Scenario: TC-FIN-CORE-007 Cross-period cut-off assigns impact to correct period and rejects hard-closed mutation
    Given Period 2026-06 closes at 2026-06-30T23:59:59 and period 2026-05 is hard_closed.
    When Submit accounting-impacting documents around cut-off and attempt backdated mutation in hard_closed period.
    Then Before and exactly at cut-off are assigned to 2026-06; after cut-off is assigned to 2026-07 or rejected by policy.
    And Backdated mutation into hard_closed 2026-05 is forbidden and terminal hard_closed state is preserved.
    And Allowed journal vouchers are posted only in assigned periods and debit_credit_balance holds.
    And Financial report line impact appears only in the assigned period.
    And Reconciliation separates 2026-06 and 2026-07 impact without cross-period leakage.
    And Audit evidence records cut-off decision, rejected hard_closed mutation, actor, and rule version.
