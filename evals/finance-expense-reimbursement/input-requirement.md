# Finance Expense Reimbursement Requirement Sample

The system supports employee expense reimbursement for Xiaomi finance shared services.

Flow:

1. Employee submits an expense report with one or more VAT invoices.
2. The system validates invoice uniqueness, invoice status, tax amount, reimbursement amount, cost center, project, and budget availability.
3. Approval follows a matrix:
   - `<= 500.00 CNY`: direct manager approval.
   - `> 500.00 CNY`: department head plus finance reviewer approval.
4. The requester cannot approve the same reimbursement. A delegate approver must have active delegation.
5. Budget is occupied after submission and released on rejection or cancellation before payment.
6. After approval, finance releases payment to the employee bank account.
7. Successful payment generates a reimbursement voucher in the selected accounting period and clears employee payable.
8. Bank rejection keeps the reimbursement unpaid and must not create a settlement voucher.
9. A red-letter or voided invoice after approval must block payment or route to exception.
10. Hard-closed accounting periods reject posting and reversal unless a privileged reopen flow is completed.

Output needed:

- Structured P0/P1 cases.
- Finance-domain assertions for invoice, tax, budget, payment, voucher, debit-credit balance, reconciliation, SoD, and audit evidence.

