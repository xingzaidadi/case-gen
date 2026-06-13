# Finance Core Processes Requirement Sample

The system supports additional Xiaomi finance shared-services core processes:

1. Supplier master data and supplier bank account changes require independent approval before any payment can be released.
2. VAT invoice red-letter processing must validate invoice status, tax amount, original invoice traceability, and accounting reversal.
3. AR receipt matching clears customer open items, links bank statement lines, posts settlement voucher, and reconciles AR subledger to GL.
4. GL manual journal entry requires debit-credit balance, approval matrix, SoD control, closed-period control, and report-line traceability.
5. Fixed asset capitalization, depreciation, transfer, and disposal must post correct vouchers and reconcile asset subledger to GL.
6. Budget control must occupy budget, block over-budget requests, release on cancellation/failure, and prevent double release.
7. All high-risk mutation commands require idempotency, audit evidence, and negative authorization checks.
8. Cross-period cut-off must assign accounting impact to the correct period and reject hard-closed period mutation.

Output needed:

- Structured P0/P1 cases.
- Finance-domain assertions for voucher/journal, debit-credit balance, invoice/tax, payment/bank, budget, period cut-off, reconciliation, SoD, and audit evidence.

