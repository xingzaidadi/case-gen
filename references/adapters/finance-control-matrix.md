# Finance Control Matrix

Use this matrix to convert control requirements into test cases.

## Core Controls

| Control | Required test points |
| --- | --- |
| Authorization | missing identity, wrong role, wrong organization, wrong legal entity, wrong cost center |
| Approval matrix | amount boundary, department/project boundary, legal entity boundary, substitute approver |
| Segregation of duties | requester cannot approve own request, master-data maintainer cannot release payment alone |
| Duplicate prevention | duplicate invoice, duplicate payment, duplicate voucher, replayed request, retried bank callback |
| Sensitive master data | supplier bank account change, tax number change, payment term change, approval and audit evidence |
| Period control | open, soft closed, hard closed, reopen, reclose, backdated posting |
| Posting control | voucher generated once, balanced journal, correct accounts, no orphan subledger item |
| Reconciliation | source-to-invoice, invoice-to-payment, payment-to-bank, subledger-to-GL, GL-to-report |
| Exception handling | bank rejection, invoice validation failure, posting failure, partial success rollback |
| Audit trail | actor, timestamp, before/after value, approval chain, posting id, external reference |

## P0 Control Rules

Classify as P0 by default:

- Any direct or indirect money movement.
- Any accounting posting, reversal, write-off, or adjustment.
- Any closed-period mutation.
- Any supplier/customer bank account mutation.
- Any payment approval or bank release.
- Any tax deduction, red-letter invoice, or tax report impact.
- Any financial report line mutation.
- Any SoD conflict that could allow fraud or concealment.

## Approval Matrix Cases

For approval limits, use boundary analysis:

- amount = limit - 0.01
- amount = limit
- amount = limit + 0.01
- currency conversion around limit
- split requests that attempt to bypass limit

For approver rules, include:

- correct approver
- wrong department approver
- wrong legal entity approver
- requester self-approval
- substitute approver without delegation
- expired delegation

## SoD Cases

Common conflicts:

- create supplier and approve payment to that supplier
- change supplier bank account and release payment
- request reimbursement and approve the same reimbursement
- create manual journal and approve/post it
- reopen closed period and post adjustment without independent approval
- maintain chart of accounts and post manual journals

## Evidence Expectations

Expected results for control cases should include evidence:

- response or UI message
- persisted status
- audit log entry
- approval record
- immutable external reference
- metric or alert for denied high-risk action

