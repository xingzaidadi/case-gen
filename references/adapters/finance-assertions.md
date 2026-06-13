# Finance Assertions

Use these assertions in `expected` blocks. Prefer concrete observables.

## Finance Observables

Allowed finance-specific observable names:

- `source_document`
- `invoice_status`
- `payment_status`
- `bank_receipt`
- `bank_statement`
- `journal_voucher`
- `ledger_entry`
- `subledger_balance`
- `general_ledger_balance`
- `reconciliation_result`
- `tax_amount`
- `budget_occupation`
- `period_status`
- `exchange_rate`
- `financial_report_line`
- `approval_chain`
- `audit_evidence`
- `control_evidence`

These can be used in addition to generic observables such as `response`, `db`,
`event`, `log`, `metric`, `ui`, and `file`.

## Required Assertion Patterns

### Accounting Posting

- Voucher exists exactly once for the source document.
- Voucher lines use expected account, cost center, project, legal entity, and period.
- Total debit equals total credit.
- Subledger open item state matches the source document.
- GL balance reflects the posted voucher.
- Posting failure leaves no partial voucher or orphan subledger item.

### Payment

- Payment request status moves through approved, sent, accepted/failed, paid, reconciled.
- Duplicate payment request is rejected or idempotently returns the existing payment.
- Payee name, bank account, currency, and amount match approved data.
- Bank receipt or bank statement reference is linked.
- AP open item is cleared only after successful payment according to the business rule.

### Invoice And Tax

- Invoice uniqueness is enforced by supplier, invoice number, invoice code/type, and legal entity.
- Tax-inclusive, tax-exclusive, and tax amount are calculated with defined precision.
- Invoice status gates payment, posting, deduction, and red-letter operations.
- Red-letter or void operation reverses accounting and tax impact without corrupting audit history.

### Period And Cut-Off

- Posting date maps to the correct accounting period.
- Closed period rejects new posting, reversal, and master-data-sensitive mutation.
- Reopen requires permission, reason, and audit evidence.
- Backdated documents use the configured cut-off rule.

### Reconciliation

- Source document total equals invoice/payment/voucher total where required.
- Subledger balance equals GL control account balance.
- Bank statement amount and bank receipt match payment instruction.
- Report line impact can be traced back to GL/voucher/source document.

### Budget

- Budget occupation happens at the configured step.
- Over-budget request is blocked or routed to exception.
- Failed approval/payment/posting releases or preserves budget according to rule.
- Cancellation or reversal releases budget without double release.

### Multi-Currency

- Exchange rate source and date are recorded.
- Transaction currency, functional currency, and reporting currency amounts are correct.
- Rounding differences are posted to configured accounts.
- Revaluation and exchange gain/loss are calculated for open items when required.

