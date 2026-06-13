# Finance AP Payment Requirement Sample

The system supports supplier invoice payment for Xiaomi finance shared services.

Flow:

1. A finance user creates a supplier payment request from a validated supplier invoice.
2. The system checks duplicate invoice and duplicate payment business keys.
3. The request follows an approval matrix:
   - `<= 1000.00 CNY`: finance reviewer approval.
   - `> 1000.00 CNY`: finance manager approval.
4. If budget control is enabled, the request occupies budget before bank release.
5. After approval, a treasury user releases the payment to the bank.
6. The bank may accept or reject the instruction.
7. Accepted bank payment settles the AP open item and generates accounting posting in the selected accounting period.
8. The system reconciles supplier invoice, payment request, bank receipt, AP subledger, GL control account, and report line.
9. Hard-closed accounting periods must reject posting and reversal unless a privileged reopen flow is completed.
10. Requester cannot approve the same payment request. Supplier bank account changes require independent approval before payment.

Output needed:

- P0/P1 structured cases.
- Finance-domain assertions, not only API response assertions.
- Traceability and coverage map.

