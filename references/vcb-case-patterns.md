# VCB Case Patterns

Use this reference only when the target is VCB or a similar backend/control-plane system involving AI job control, auth, approval, scope, idempotency, audit, metrics, or cross-user isolation.

Do not apply these rules to unrelated domains by default.

## VCB-Like Risk Model

High-risk areas:
- Identity extraction and authentication
- Resource ownership and reviewer authorization
- Action scope and scene binding
- Request idempotency and replay safety
- Approval workflows and decision actions
- Cross-user data isolation
- Audit log completeness
- Metrics and alerting for denied actions
- Fail-safe behavior on unknown risk

## Rule Families

| Family | Typical P0 Cases |
| --- | --- |
| Authn | Missing identity, invalid identity, unsupported auth header |
| Resource isolation | A reads B resource, A writes B resource, list leaks B resource |
| Scope | scene type mismatch, scene id mismatch, expired timestamp, invalid signature |
| Idempotency | repeated request id returns previous result, concurrent same request id only applies once |
| Approval | unauthorized actor cannot approve/reject/defer/need_info, list filters by actor |
| State | invalid status transition, terminal state cannot mutate |
| Audit | denial and success logs include actor/resource/action/result/request_id |
| Metrics | denial counters increase for owner forbidden, approval forbidden, cross-scene reject, idempotent drop |
| Compatibility | old clients missing new fields fail safely or follow documented migration behavior |

## VCB-Inspired Output Sections

For backend control-plane cases, Markdown renderings can include:

1. Goal
2. Scope under test
3. Scenario matrix
4. Mock and fixtures
5. Coverage target
6. Exit criteria
7. Risks and compensations
8. E2E acceptance checklist
9. Observability and evidence collection
10. Rollback triggers

## Case Patterns

### Cross-User Read

Given user A and user B own separate resources.

When A reads B's resource by ID.

Then the system returns 403 or the documented safe error, the response contains no B data, audit records the denial, and denial metrics increment.

### Cross-User Write

Given user B owns a mutable resource.

When user A attempts a write action on B's resource.

Then the write is rejected, B's resource remains unchanged, audit records actor/resource/action/result/request_id, and metrics increment.

### Scope Mismatch

Given a request with valid identity but mismatched scene fields.

When the protected action is called.

Then the request is rejected before business mutation and the relevant cross-scene metric increments.

### Idempotent Replay

Given a successful request with request_id X.

When the same request_id X is submitted again in the idempotency window.

Then the system returns the prior result or documented duplicate behavior and does not repeat the mutation.

### Approval Four Actions

For approval workflows, cover approve, reject, need_info, and defer independently. Do not collapse them into one case if they have different validation, data, or side effects.

## Domain Adapter Rule

When using VCB patterns, keep both:
- Generic method: industry and VAF flow
- Domain overlay: VCB-specific risks

The output should say which cases came from VCB-like domain rules and which came from requirements or code.

