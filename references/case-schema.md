# Case Schema

Use this schema for maintainable case output. YAML is preferred for human editing; JSON is acceptable for tooling.

## Top-Level Shape

```yaml
metadata:
  suite_id: string
  title: string
  source_files:
    - path: string
      lines: string
  generated_at: YYYY-MM-DD
  mode: unit|api|integration|e2e|regression|security-control|mixed
  assumptions:
    - string

test_model:
  actors:
    - id: string
      role: string
  risks:
    - id: RISK-001
      description: string
      priority: P0|P1|P2
  test_points:
    - id: TP-001
      view: e2e|layered
      title: string
      source:
        - type: requirement|code|api|rule|risk|inferred
          ref: string
      priority: P0|P1|P2

coverage_map:
  sources:
    - id: REQ-001
      title: string
      priority: P0|P1|P2
      cases:
        - TC-001
      status: covered|partial|missing|deferred
  test_points:
    - id: TP-001
      cases:
        - TC-001
      status: covered|partial|missing|deferred
  cross_view:
    - e2e: TP-E2E-001
      layered:
        - TP-API-001
        - TP-SVC-001
      status: linked|missing-layer|missing-e2e|deferred

cases:
  - id: TC-001
    title: string
    priority: P0|P1|P2
    level: unit|api|integration|e2e|security|manual
    type: happy_path|negative|boundary|decision_table|state_transition|pairwise|regression|security|observability
    traceability:
      requirements: []
      code: []
      api: []
      rules: []
      risks: []
      test_points: []
      inferred: false
    preconditions:
      - string
    data:
      - name: string
        value: string
        source: string
    steps:
      - action: string
        input: string
    expected:
      - assertion: string
        observable: response|db|event|log|metric|ui|file|source_document|invoice_status|payment_status|bank_receipt|bank_statement|journal_voucher|ledger_entry|subledger_balance|general_ledger_balance|reconciliation_result|tax_amount|budget_occupation|period_status|exchange_rate|financial_report_line|approval_chain|audit_evidence|control_evidence
    finance:
      process: ap_payment|expense_reimbursement|ar_receipt|gl_journal|fixed_asset|tax|treasury|budget|consolidation|other
      business_event: string
      accounting_event: voucher_required|no_posting|reversal|accrual|settlement|adjustment|revaluation|unknown
      financial_assertions: []
      control_assertions: []
      regulatory_refs: []
    automation_candidate: high|medium|low
    status: draft|ready|blocked
    notes:
      - string

open_questions:
  - id: Q-001
    question: string
    impact: blocks_p0|affects_p1|nice_to_have
    owner: user|dev|qa|product|unknown

suite_layers:
  smoke:
    - TC-001
  p0_gate:
    - TC-001
  regression:
    - TC-001
  full:
    - TC-001
  exploratory:
    - CHARTER-001

pruning_notes:
  generated: 0
  smoke: 0
  p0_gate: 0
  regression: 0
  full: 0
  pruned_or_merged: 0
  deferred: 0
  rationale:
    - string

execution_results:
  run_id: string
  environment: string
  started_at: string
  cases:
    - case_id: TC-001
      result: pass|fail|blocked|skipped|flaky
      failure_class: product_bug|test_case_bug|test_data_issue|environment_issue|flaky_test|obsolete_expectation|null
      evidence:
        - type: response|log|metric|screenshot|trace|db
          ref: string
      defect_id: string|null
      notes: string

quality_gates:
  p0_sources_covered: true|false
  no_happy_path_only: true|false
  all_cases_have_traceability: true|false
  all_cases_have_observable_expected: true|false
  boundary_cases_have_concrete_values: true|false
  state_cases_include_invalid_transitions: true|false
  security_cases_include_negative_authorization: true|false
  e2e_layer_cross_check_complete: true|false
```

## Minimal Required Fields

Every case must have:
- `id`
- `title`
- `priority`
- `level`
- `traceability`
- `steps`
- `expected`

Every `expected` item must be observable. Avoid expectations like "works correctly".

## Coverage Map Rules

Use `coverage_map` whenever the output has more than a short ad hoc list.

Required behavior:
- Every P0 source or test point must be `covered` or explicitly `deferred` with an open question.
- `missing` P0 coverage is a blocker and must be called out before finalizing.
- Cross-view links should connect E2E test points to supporting layered test points.
- Cases not referenced by any source or test point are suspect; keep them only when explicitly marked `inferred`.

Example:

```yaml
coverage_map:
  sources:
    - id: REQ-AUTH-001
      title: Missing actor is rejected
      priority: P0
      cases: [TC-AUTH-001]
      status: covered
  test_points:
    - id: TP-API-001
      cases: [TC-AUTH-001]
      status: covered
  cross_view:
    - e2e: TP-E2E-LOGIN-001
      layered: [TP-API-001]
      status: linked
```

## Traceability Rules

Use source references:
- Requirement: `REQ:file.md:42`
- Code: `CODE:Controller.java:88`
- API: `API:openapi.yaml:/paths/~1orders/get`
- Rule: `RULE:AUTH-01`
- Risk: `RISK:production-incident-2026-05-01`
- Inferred: `INF:missing explicit rule; derived from security checklist`

If local line numbers are unavailable, use the closest section title and mark the source as approximate.

## Quality Gate Rules

Set `quality_gates` after case generation. A gate can be `false`, but the output must explain why.

Recommended blocker behavior:
- `p0_sources_covered = false` blocks final approval.
- `all_cases_have_observable_expected = false` blocks final approval.
- `all_cases_have_traceability = false` blocks final approval unless all orphan cases are explicitly inferred.
- `no_happy_path_only = false` blocks non-trivial suites.

Technique-specific gates:
- Boundary cases must contain concrete values such as `9/10/11`, `2026-06-13T10:00:00Z`, or `N-1/N/N+1`.
- State transition cases must include at least one invalid transition and terminal-state behavior when a state model exists.
- Security/control suites must include missing identity, wrong identity/role, and cross-resource or cross-tenant access where applicable.

## Suite Layer Rules

Use `suite_layers` when the case set is intended to be run repeatedly.

Rules:
- Every P0 case should be in `p0_gate`.
- Smoke should be small and should not include broad P2 compatibility cases.
- Regression should include fixed defect cases and high-value P1 cases.
- Full should include all non-deferred executable cases.
- Cases in no layer need a pruning reason or should be removed.

## Execution Result Rules

Use `execution_results` when the user provides run results.

Rules:
- Failed P0 cases must remain visible.
- A failure must be classified before changing the case.
- Fixed defects should add or update regression cases.
- Flaky cases need stabilization notes, not silent pass/fail rewriting.

## Markdown Rendering Template

```markdown
# Test Cases: {title}

> Mode: {mode}
> Sources: {source summary}
> Assumptions: {assumptions}

## Coverage Map

| Source/Test Point | P0 | P1 | P2 | Cases |
| --- | --- | --- | --- | --- |

## Cases

| ID | Priority | Level | Type | Title | Traceability | Expected |
| --- | --- | --- | --- | --- | --- | --- |

## Open Questions

## Self-Check
```

## Gherkin Rendering Template

```gherkin
Feature: {feature name}

  Scenario: {case title}
    Given {precondition}
    When {action}
    Then {observable assertion}
```
