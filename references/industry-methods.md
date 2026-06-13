# Industry Test Case Design Methods

Use these methods as a toolbox. Select techniques based on risk, input type, and system behavior instead of applying every technique mechanically.

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

