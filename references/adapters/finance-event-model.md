# Finance Event Model

Use this model to convert requirements into finance test points.

## Event Chain

Finance workflows usually follow this chain:

```text
business trigger
-> source document
-> approval/control decision
-> accounting event
-> voucher/journal
-> subledger update
-> general ledger update
-> payment/receipt or settlement
-> reconciliation
-> financial report impact
-> audit evidence
```

Not every feature reaches every step. Mark skipped steps explicitly.

## Common Source Documents

| Domain | Source document examples |
| --- | --- |
| AP | purchase order, goods receipt, supplier invoice, payment request |
| Expense | expense report, travel request, reimbursement claim, invoice |
| AR | sales order, delivery, customer invoice, receipt, write-off |
| GL | manual journal, accrual, adjustment, reversal, allocation |
| FA | asset card, capitalization document, depreciation run, disposal |
| Tax | VAT invoice, deduction confirmation, tax filing, red-letter invoice |
| Treasury | payment instruction, bank statement, bank receipt, cash forecast |
| Budget | budget request, occupation, release, adjustment, transfer |

## Accounting Event Types

| Event type | Test focus |
| --- | --- |
| `voucher_required` | Voucher generated once, correct lines, debit equals credit, correct period |
| `no_posting` | No voucher or ledger mutation is created for non-accounting change |
| `settlement` | Open item cleared, payment/receipt linked, residual amount correct |
| `reversal` | Original posting reversed or red-lettered without mutating closed-period history |
| `accrual` | Accrual amount, period, reversal schedule, and report impact are correct |
| `adjustment` | Adjustment reason, approval, audit evidence, and report impact are correct |
| `revaluation` | Exchange rate, valuation date, gain/loss account, and precision are correct |

## State Models

### Document Status

`draft -> submitted -> approved -> posted -> settled -> closed`

Required cases:

- valid forward transition
- reject invalid transition, such as `draft -> posted`
- terminal-state behavior after `closed`
- repeated command does not duplicate posting
- concurrent approval/posting does not create duplicate voucher or payment

### Period Status

`open -> soft_closed -> hard_closed -> reopened -> reclosed`

Required cases:

- posting allowed in open period
- restricted behavior in soft close
- mutation rejected in hard close
- reopen requires permission and audit evidence
- reposting after reopen preserves traceability

### Invoice Status

`received -> validated -> matched -> deducted_or_used -> paid -> red_lettered_or_voided`

Required cases:

- duplicate invoice number for same supplier is rejected or routed to exception
- status mismatch blocks deduction/payment/posting
- red-letter or voided invoice reverses accounting impact correctly

### Payment Status

`requested -> approved -> sent_to_bank -> bank_accepted -> paid -> reconciled`

Required cases:

- duplicate payment request is idempotent or rejected
- bank rejection rolls back or marks exception without clearing payable
- bank receipt reconciles to payment and ledger

## Precision And Amount Rules

Always identify:

- transaction currency and functional currency
- tax-inclusive or tax-exclusive amount
- tax rate and tax amount
- rounding mode and precision
- exchange rate source and valuation date
- zero, negative, maximum, and high-precision amount boundaries

