# Finance Period Close Requirement Sample

The system supports month-end close for Xiaomi finance shared services.

Flow:

1. Finance starts the close process for a legal entity and accounting period.
2. The system checks prerequisite tasks: AP/AR subledger close, bank reconciliation, unposted voucher queue, failed interface events, and tax invoice exceptions.
3. The period moves from `open` to `soft_closed` and then `hard_closed` after approvals.
4. During soft close, normal business posting is blocked except configured adjustment journals.
5. During hard close, posting, reversal, master-data-sensitive financial mutation, and backdated documents are rejected.
6. Close job can be retried after timeout without duplicate close tasks or duplicate closing vouchers.
7. A privileged reopen flow requires reason, independent approval, SoD check, and audit evidence.
8. Reopen allows approved adjustment posting, then reclose recomputes subledger/GL/report reconciliation.
9. Cross-period cut-off must assign documents to the correct accounting period based on posting date and cut-off time.
10. Close completion publishes report-line readiness and immutable evidence for audit.

Output needed:

- Structured P0/P1 cases.
- Finance-domain assertions for period status, cut-off, closing voucher, debit-credit balance, subledger/GL reconciliation, report-line readiness, reopen SoD, idempotent close retry, and audit evidence.

