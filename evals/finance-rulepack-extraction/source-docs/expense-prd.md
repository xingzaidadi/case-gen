# Expense Reimbursement PRD Fragment

Legal entity: XM-CN-01, base currency CNY, monthly period calendar.

Expense reimbursement approval:

- <= 500.00 CNY: direct manager approval.
- > 500.00 CNY: department head plus finance reviewer approval.
- Requester cannot approve the same reimbursement. This is a SoD rule.

Tax:

- Input VAT tax code TAX-VAT-IN-06 uses 6% rate for eligible travel service invoices.
- Red-letter invoice must trace to original invoice and reverse tax amount.

Controls:

- Hard closed period rejects posting and reversal.
- Duplicate invoice must not create duplicate reimbursement.
- Budget cancellation releases budget exactly once and retry is idempotent.

Integration:

- Bank payment callback includes payment status, bank reference, amount, currency, and failure reason.
- Tax invoice status API returns invoice status, tax amount, and red-letter status.

Incident:

- 2025 duplicate payment production defect: retried payment callback created a second settlement voucher.

