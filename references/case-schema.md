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
        observable: response|db|event|log|metric|ui|file
    automation_candidate: high|medium|low
    status: draft|ready|blocked
    notes:
      - string
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

## Traceability Rules

Use source references:
- Requirement: `REQ:file.md:42`
- Code: `CODE:Controller.java:88`
- API: `API:openapi.yaml:/paths/~1orders/get`
- Rule: `RULE:AUTH-01`
- Risk: `RISK:production-incident-2026-05-01`
- Inferred: `INF:missing explicit rule; derived from security checklist`

If local line numbers are unavailable, use the closest section title and mark the source as approximate.

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

