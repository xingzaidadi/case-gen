# Finance Test Data

Use this file when choosing data classes and boundary values.

## Core Dimensions

| Dimension | Values to cover |
| --- | --- |
| Legal entity | same entity, cross entity, inactive entity, entity without permission |
| Accounting period | open, soft closed, hard closed, reopened, future period |
| Currency | CNY, foreign currency, missing rate, stale rate, high precision rate |
| Amount | 0, 0.01, limit - 0.01, limit, limit + 0.01, maximum, negative |
| Tax | tax exempt, 0%, standard VAT, reduced rate, mixed tax rates, rounding |
| Supplier/customer | active, frozen, blacklisted, changed bank account, duplicate tax id |
| Invoice | unique, duplicate, invalid status, red-lettered, voided, partially matched |
| Bank | valid account, changed account pending approval, rejected by bank, duplicate callback |
| Budget | enough, exactly enough, over by 0.01, frozen budget, released after rollback |
| Approval | requester, direct manager, wrong org approver, expired delegate, SoD conflict |

## Boundary Examples

- Approval limit: `999.99/1000.00/1000.01`
- Tax rounding: `0.01`, `0.005`, `99999999.99`
- Period cut-off: last second before close, exact close time, first second after close
- Retry/idempotency: first submit, same request id retry, different request id same business key
- Exchange rate: missing, zero, stale, current, high precision, weekend/holiday fallback

## Data Quality Rules

- Do not use vague amounts such as "large amount"; choose concrete values.
- Include legal entity and accounting period in P0 finance cases.
- Include currency and tax fields when amount is present.
- Include source document id, external reference id, and idempotency key for mutation cases.
- Include actor identities for control and SoD cases.

