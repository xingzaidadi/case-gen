# Execution Feedback Loop

Use this reference when the user has test execution results, failed cases, flaky tests, defects, or wants to turn execution into regression assets.

## Failure Classification

Classify every failed case before changing cases or product code.

| Class | Meaning | Next action |
| --- | --- | --- |
| product_bug | Product behavior violates requirement or accepted rule | Create/attach defect; keep case failing until fixed |
| test_case_bug | Expected result or steps are wrong | Fix case; do not count as product failure |
| test_data_issue | Fixture/account/environment data is invalid | Repair data setup and rerun |
| environment_issue | Service, dependency, network, or config problem | Mark blocked; rerun after environment recovery |
| flaky_test | Non-deterministic timing/order/dependency problem | Stabilize wait/assertion/isolation; keep risk visible |
| obsolete_expectation | Requirement changed and case no longer applies | Update traceability or deprecate case |

Do not silently delete failed P0 cases.

## Defect To Regression

When a defect is fixed:

1. Keep the original failing case.
2. Mark it as regression.
3. Add the defect id to traceability.
4. Add one adjacent negative or boundary case if the bug suggests a family of failures.
5. Move it into the regression layer.

## Result Schema

When results are available, use this shape:

```yaml
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
```

## Report Sections

For execution analysis, output:

1. Summary: pass/fail/blocked/flaky counts by priority
2. P0 status: every failed or blocked P0 first
3. Failure classification table
4. Defects to create or update
5. Cases to fix
6. Regression additions
7. Rerun strategy

## Rerun Strategy

Use selective reruns:
- Rerun product bug fixes with the original case plus adjacent regression.
- Rerun flaky cases at least 3 times after stabilization.
- Rerun environment failures only after a concrete environment recovery signal.
- Rerun P0 gate before release even if full suite is deferred.

