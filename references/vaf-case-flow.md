# VAF-Inspired Case Generation Flow

This reference adapts VAF testing ideas into a general case-generation workflow. It is a workflow skeleton, not a domain rule set.

## Core Ideas To Preserve

1. Split case design into stages instead of asking the model to produce final cases in one step.
2. Use machine-checkable gates where possible.
3. Anchor every case to a source or explicitly mark it as inferred.
4. Avoid happy-path-only case sets.
5. Maintain state across outputs: test points -> cases -> execution results -> defects -> regression.

## T01: Test Admission

Goal: decide whether the target is ready to test and what should be tested.

Outputs:
- Test scope
- Out-of-scope items
- Actors and systems
- Risk list
- Required input gaps

Key pattern: dual-view test point design.

E2E view:
```
business flow -> business scenario -> E2E test point
```

Layered view:
```
feature point -> UI/API/service/data/security test point
```

Cross-validation:
- E2E points not covered by layers become missing technical checks.
- Layer points not covered by E2E become isolated API/service cases or out-of-scope notes.

## T02: Context Loading

Goal: gather enough technical detail to avoid vague or unexecutable cases.

Collect:
- UI surfaces or API endpoints
- Request/response fields
- State model
- Data dependencies
- Environment and account requirements
- Existing tests and fixtures
- Known incidents and defects

Revise T01 test points after this step:
- Merge duplicate points that hit the same interface and assertion.
- Split one broad point when it maps to multiple interfaces, roles, states, or data boundaries.
- Add technical points missed by PRD-only analysis, such as idempotency, permission, pagination, async retry, and parameter boundaries.

## T03: Test Plan / Coverage Matrix

Goal: turn test points into an explicit coverage plan.

Coverage dimensions:
- Business flow
- Feature/layer
- Risk
- Priority
- Data class
- State transition
- Automation target
- Evidence source

Output a coverage matrix before detailed cases when the target is complex.

## T04: Test Case Design

Design cases in five passes:

| Pass | Focus | Should not decide |
| --- | --- | --- |
| T04.1 Case frame | metadata, traceability, priority, preconditions | detailed assertion values |
| T04.2 Data setup | users, fixtures, variables, boundary values | final pass/fail analysis |
| T04.3 Steps | actions, API calls, UI operations, sequence | assertion completeness |
| T04.4 Assertions | exact expected values, side effects, logs, metrics | new scope |
| T04.5 Self-check | coverage report and execution strategy | silently editing scope |

Use this staged approach when the requested output is important, large, or likely to be automated.

## S04 Unit-Test Principles

For unit or component tests:
- Use AAA: Arrange, Act, Assert.
- Every test must assert something observable.
- Do not call real DB/network unless the user explicitly asks for integration tests.
- Prefer local fixtures or in-memory stores when they match existing project style.
- Include exception and boundary cases, not only happy paths.
- Use naming that communicates behavior, such as `should_return_403_when_actor_reads_other_users_job`.
- Existing tests from implementation stages should be reviewed for four gaps: correctness, completeness, maintainability, and regression value.

## T06/T07 Feedback Loop

If execution results exist:
- Classify failures as product bug, test data issue, environment issue, flaky case, or obsolete expectation.
- Convert fixed defects into regression cases.
- Keep failed P0 cases visible until resolved.

