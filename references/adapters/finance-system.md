# Finance System Adapter

Use this adapter when the target system touches accounting, payment, invoice,
tax, treasury, budget, reimbursement, procurement-to-pay, order-to-cash,
fixed assets, period close, consolidation, or financial reporting.

The adapter exists because finance cases fail when they only assert API
responses. A good finance case asserts the business document, accounting
event, control result, ledger impact, reconciliation result, and audit evidence.

## Trigger Signals

Load this adapter when the input mentions any of these signals:

- AP, AR, GL, FA, tax, treasury, budget, consolidation, expense, reimbursement
- invoice, fapiao, VAT, red-letter, deduction, tax rate, tax amount
- payment, bank receipt, bank statement, cash, fund, settlement, supplier
- voucher, journal, posting, reversal, adjustment, write-off, accrual
- period close, reopen, cut-off, month-end, year-end
- subledger, general ledger, reconciliation, report line
- cost center, department, project, legal entity, company code, chart of accounts
- approval matrix, segregation of duties, audit trail, control evidence

## Required Model

Before writing cases, build a compact finance test model:

| Model | Required content |
| --- | --- |
| Business flow | Actors, source document, approval, posting, payment/receipt, reconciliation |
| Accounting event | Whether the event creates voucher/journal entries, reversal, accrual, or settlement |
| Data model | Legal entity, accounting period, currency, tax, amount precision, supplier/customer, bank account |
| State model | Document status, invoice status, payment status, voucher status, period status |
| Control model | Approval, SoD, duplicate prevention, limit checks, sensitive-field changes |
| Reconciliation model | Source document, invoice, payment, bank statement, subledger, GL, report line |
| Audit model | Who did what, when, before/after value, approval evidence, posting evidence |

If one model is unknown, mark it unknown and continue. Do not invent accounting
entries without an explicit rule or an inferred marker.

## Finance Case Shape

Add these fields when producing structured finance cases:

```yaml
finance:
  process: ap_payment|expense_reimbursement|ar_receipt|gl_journal|fixed_asset|tax|treasury|budget|consolidation|other
  business_event: string
  accounting_event: voucher_required|no_posting|reversal|accrual|settlement|adjustment|unknown
  financial_assertions:
    - debit_credit_balance
    - voucher_generated
    - subledger_gl_reconciled
  control_assertions:
    - approval_matrix
    - segregation_of_duties
  regulatory_refs:
    - LAW-ACCOUNTING
```

Use normal case fields as the source of truth. The `finance` block is an
adapter-specific annotation for generation and coverage checks.

## Case Design Rules

- Treat money movement, accounting posting, tax deduction, period close, and
  financial report impact as P0 unless the requirement explicitly scopes them
  out.
- For accounting-impacting events, include a voucher/journal assertion and a
  debit-credit balance assertion.
- For cross-document flows, include reconciliation assertions across source
  document, invoice, payment, bank statement, subledger, GL, and report line.
- For period-sensitive flows, include cut-off cases: open period, closed period,
  just before close, exactly at close, just after close, and reopen behavior.
- For payment and invoice flows, include duplicate prevention and idempotency.
- For approvals, include approval matrix, limit boundary, wrong approver,
  self-approval, and SoD conflict cases.
- For tax and invoice flows, include tax rate, tax amount, invoice status,
  red-letter/reversal behavior, and deduction/use confirmation where applicable.
- For multi-currency flows, include exchange rate source, precision, posting
  currency, functional currency, and exchange gain/loss or revaluation behavior.
- For budget flows, include occupation, release, over-budget blocking, and
  rollback after failure.
- For high-risk negative cases, assert audit logs and control evidence, not
  just an error response.

## Output Expectations

A finance suite is not acceptable if it contains only:

- UI/API success response checks
- Generic permission cases with no financial object scope
- Happy-path posting without reversal, failure, and reconciliation
- Voucher existence without debit/credit, period, and report-impact assertions
- Approval cases without SoD and audit evidence

