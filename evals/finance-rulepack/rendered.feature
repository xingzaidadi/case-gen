Feature: Finance Rulepack Reference Eval

  @p0 @security @security
  Scenario: TC-RULEPACK-001 Supplier bank account change uses internal SoD, duplicate payment, bank callback, and audit observability rules
    Given Supplier S001 belongs to LE-XM-CN-01 and has pending bank account change.
    And Payment request uses duplicate payment key from CTRL-DUPLICATE-PAYMENT.
    When Attempt same-maintainer approval and payment release.
    Then Same-maintainer approval is denied by SOD-SUPPLIER-BANK-PAYMENT.
    And Duplicate payment prevention uses CTRL-DUPLICATE-PAYMENT and payment status remains not released.
    And Bank gateway receives no outgoing instruction for this denied release.
    And Audit evidence follows OBS-AUDIT-LOG with actor, timestamp, old/new value, and denied rule id.
    And Security log records wrong role / SoD denial.

  @p0 @integration @state_transition
  Scenario: TC-RULEPACK-002 Closed-period posting uses internal period, voucher, account, and tax rulepack ids
    Given Period 2026-05 is hard_closed by POLICY-PERIOD-CUTOFF.
    And Voucher observability uses OBS-VOUCHER-TABLE.
    When Attempt AP posting with input VAT into hard_closed period.
    Then Invalid posting transition is rejected by CTRL-CLOSED-PERIOD-NO-POST and period remains terminal hard_closed.
    And Invoice status remains validated_not_posted and is not moved to posted in the closed period.
    And No voucher row is created in OBS-VOUCHER-TABLE; debit_credit_balance is unchanged.
    And No tax amount is recognized for TAX-VAT-IN-06 in the closed period.
    And AP payable account ACC-AP-PAYABLE and GL balance remain unchanged.
    And Invoice, AP subledger, tax amount, and GL reconciliation remain unchanged with zero unauthorized difference.
    And Audit evidence records closed-period denial and rulepack ids.
