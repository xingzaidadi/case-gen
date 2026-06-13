# Industry Test Case Design Methods

Use these methods as a toolbox. Select techniques based on risk, input type, and system behavior instead of applying every technique mechanically.

## Technique Selection Matrix

Use this matrix before generating detailed cases. It prevents "method drift", where the model lists good techniques but does not apply the right one to the input.

| Input signal | Primary technique | Required case shape | Quality gate |
| --- | --- | --- | --- |
| Field has numeric, length, count, money, date, timeout, quota, or retention limits | Boundary value analysis | Concrete `min-1/min/min+1` and `max-1/max/max+1`, or `N-1/N/N+1` | No vague "boundary value" labels without concrete data |
| Field or request has valid/invalid classes | Equivalence partitioning | One representative per meaningful valid, invalid, missing, null, malformed, and unsupported class | Each class maps to at least one expected result |
| Multiple conditions decide one outcome | Decision table | Conditions, actions, selected rows, impossible rows, and expected result per row | Every meaningful outcome has at least one row |
| Object has lifecycle/status/workflow | State transition testing | Valid transition, invalid transition, terminal state, repeated command, concurrent transition when risky | At least one invalid transition and one terminal-state case |
| Many dimensions interact, full Cartesian set is too large | Pairwise/combinatorial testing | Pairwise set plus explicit P0 high-risk full combinations | Pairwise is not used to skip known high-risk interactions |
| User or system journey matters | Scenario/use-case testing | Main path, alternate path, failure path, observable business result | E2E cases cross-link to layered checks |
| API contract exists | Contract/API testing | Required/optional fields, types, error shape, compatibility, pagination, auth, idempotency | Every documented error class has a case or deferral |
| Role, tenant, owner, reviewer, scope, policy, or permission appears | Security/control negative testing | Missing identity, invalid identity, wrong role, cross-resource, replay/duplicate, fail-safe | Negative cases are P0 unless impact is explicitly low |
| Existing tests are mostly success paths | S04-style legacy test review | Add exception, boundary, invalid state, duplicate submit, and permission cases | No non-trivial method/interface remains happy-path only |
| Production incident, bug, or support complaint exists | Regression/error guessing | Reproduce bug, fixed behavior, adjacent negative case, regression marker | Fixed defects become regression cases |
| Async, retry, queue, event, webhook, or batch behavior appears | Reliability/resilience testing | Duplicate event, out-of-order event, retry exhaustion, partial failure, idempotent consumer | Expected observability is defined: event/log/metric/state |
| Data mutation is important | Data-integrity testing | Before/after state, rollback, concurrent write, partial write, audit evidence | Expected result includes persistent state assertion |

When multiple signals apply, combine techniques. Example: an API endpoint with role checks and a time window needs contract testing, security/control negative testing, and boundary value analysis.

## Priority Assignment Rules

Use these defaults unless project policy overrides them:

| Risk | Default priority |
| --- | --- |
| Data leak, unauthorized write, money movement, destructive operation, irreversible state mutation | P0 |
| Authn/authz missing, cross-user/tenant access, replay causing duplicate mutation | P0 |
| Critical business flow broken for primary users | P0 |
| Error path returns 500 instead of documented safe error | P1, or P0 if it leaks data or blocks release |
| Audit/metric missing for high-risk denial | P1, or P0 in regulated/control-plane systems |
| Compatibility for old clients | P1/P2 depending on traffic and rollout plan |
| Cosmetic issue, wording, low-frequency optional path | P2 |

## Case Count Control

Professional case generation is not "more is better". Control suite size:

- For each P0 rule, include at least one direct case and one negative case when applicable.
- For broad input domains, use equivalence classes plus boundaries instead of enumerating every value.
- For many dimensions, use pairwise plus explicit high-risk combinations.
- Split cases only when setup, action, assertion, priority, or failure diagnosis differs.
- Merge cases when they share the same setup, action, and expected result and only differ by unimportant labels.

## Risk-Based Testing

Prioritize cases by business impact, user impact, security exposure, likelihood of failure, change size, and observability.

Priority convention:
- `P0`: release blocker or high-impact safety/security/data-integrity risk
- `P1`: important regression or likely defect path; should pass before release
- `P2`: compatibility, low-frequency, or nice-to-have validation

Use risk-based design whenever time is limited.

## Equivalence Partitioning

Split inputs into classes expected to behave the same. Choose representative values from each class.

Example:
- Valid username length: 1..64
- Invalid: empty, >64, unsupported characters
- Unknown: null or omitted if API allows absence

Use for fields, roles, statuses, request shapes, permissions, config values, and feature flags.

## Boundary Value Analysis

For ordered or numeric domains, test edges and values adjacent to edges.

Pattern:
- Minimum: `min-1`, `min`, `min+1`
- Maximum: `max-1`, `max`, `max+1`
- Time window: just before, exactly at, just after expiry
- Count limit: `N-1`, `N`, `N+1`

Use concrete values, not vague labels like "boundary".

## Decision Tables

Use when multiple conditions determine outcomes.

Best for:
- Eligibility rules
- Permission rules
- Pricing/discounts
- Workflow routing
- Error-code selection

Build a table with conditions, actions, expected results, and selected cases. Collapse impossible or duplicate rows, but keep every meaningful outcome.

## State Transition Testing

Use when objects move through statuses.

Cover:
- Valid transition
- Invalid transition
- Terminal state behavior
- Repeated command
- Concurrent transition
- Recovery or rollback state

Examples: order lifecycle, approval status, job execution, ticket workflow, payment status.

## Pairwise And Combinatorial Testing

Use when many dimensions interact and full Cartesian coverage is too expensive.

Dimensions can include:
- Role
- Platform
- Browser
- Feature flag
- Region
- Payment type
- Data size
- Permission scope

Prefer pairwise for broad compatibility coverage, then add explicit high-risk triples or full combinations for P0 rules.

## Scenario And Use-Case Testing

Use business flows to cover realistic user/system journeys.

Each scenario should include:
- Actor
- Goal
- Trigger
- Main path
- Alternate path
- Failure path
- Observable result

Scenario testing is stronger when paired with layered API/service checks.

## BDD / Given-When-Then

Use Given-When-Then to make cases readable and automation-friendly:
- Given: preconditions and data
- When: action
- Then: observable assertions

Use BDD for cross-functional communication, acceptance tests, and high-level regression suites.

## Error Guessing And Checklists

Use historical bugs, production incidents, and domain checklists to find cases formal techniques miss.

Common checklist lenses:
- Auth missing or wrong user
- Data not found
- Duplicate submit
- Timeout/retry
- Race condition
- Partial failure
- Backward compatibility
- Error body leaks implementation details
- Audit/metric missing

Mark checklist-derived cases as `RISK-*` or `INF-*` if no explicit requirement exists.

## Contract And API Testing

For APIs, cover:
- Required/optional fields
- Type validation
- Error codes and error body shape
- Idempotency
- Backward compatibility
- Pagination/filtering/sorting
- Authn/authz
- Rate limit and retry semantics

Use API contracts as traceability sources.

## Security And Control Testing

For systems that make decisions, isolate users, approve actions, or mutate important data, include:
- Missing identity
- Invalid identity
- Cross-user access
- Role/scope mismatch
- Replay or duplicate request
- Audit trail
- Metrics/alerting
- Fail-safe behavior

These often become P0 even if the happy path is simple.
