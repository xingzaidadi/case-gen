# Finance Process Patterns

Use these patterns to seed E2E and integration cases.

## AP Payment

Flow:

```text
supplier invoice/payment request
-> validation and matching
-> approval
-> budget occupation if configured
-> bank payment instruction
-> bank accepted/rejected
-> AP settlement
-> voucher/journal posting
-> bank/AP/GL reconciliation
```

Required variants:

- happy path payment and reconciliation
- duplicate invoice and duplicate payment
- amount approval boundary
- supplier bank account changed before payment
- bank rejection after payment instruction
- closed-period posting or reversal attempt
- SoD conflict between requester, approver, and payment releaser

## Expense Reimbursement

Flow:

```text
expense report
-> invoice attachment and validation
-> manager/finance approval
-> budget occupation
-> payment
-> voucher posting
-> reimbursement settlement
```

Required variants:

- missing or duplicate invoice
- self-approval attempt
- over-budget and exactly-at-budget
- personal bank account change
- red-letter/voided invoice after approval
- cancellation after payment vs before payment

## AR Receipt

Flow:

```text
customer invoice
-> receipt or bank statement
-> matching
-> clearing
-> voucher posting
-> AR/GL reconciliation
```

Required variants:

- partial receipt
- overpayment
- wrong customer receipt
- duplicate bank statement line
- write-off approval

## GL Manual Journal

Flow:

```text
journal draft
-> validation
-> approval
-> posting
-> reversal or adjustment
-> report impact
```

Required variants:

- debit/credit imbalance
- closed-period posting
- restricted account
- high amount approval
- create-and-approve SoD conflict
- reversal in later period

## Fixed Assets

Flow:

```text
asset acquisition
-> capitalization
-> depreciation
-> transfer
-> disposal
-> GL reconciliation
```

Required variants:

- capitalization date cut-off
- depreciation start period
- useful-life boundary
- residual value boundary
- disposal gain/loss
- asset transfer approval

## Tax Invoice / Red-Letter

Flow:

```text
invoice issuance or receipt
-> status validation
-> deduction/use confirmation
-> red-letter or void
-> tax and accounting reversal
```

Required variants:

- duplicate invoice
- invalid invoice status
- tax amount rounding
- red-letter amount greater than original
- red-letter after deduction/payment
- audit trace to original invoice

