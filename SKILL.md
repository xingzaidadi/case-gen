---
name: case-gen
description: Use when the user asks to design, generate, review, or improve test cases, test scenarios, acceptance checks, unit-test matrices, E2E cases, API cases, regression cases, or QA plans. Use this skill even when the user says "生成用例", "测试点", "case", "验收清单", "单测场景", "E2E", "回归用例", or asks whether coverage is complete. Also use it for finance-system cases involving AP, AR, GL, payment, invoice, tax, voucher, ledger, reconciliation, period close, budget, or audit controls. Do not default to VCB-specific rules unless the target system is VCB or a similar Java backend control-plane with auth, approval, scope, idempotency, audit, or metrics risks.
---

# Case Gen

Design professional test cases from requirements, code, API contracts, existing tests, and domain rules. Build the case set from first principles, then render it into Markdown, YAML/JSON, Excel-ready rows, Gherkin, or implementation guidance as requested.

This is not a VCB-only skill. VCB and VAF are reference systems:
- Use VAF as the workflow skeleton: admission, context loading, dual-view test-point design, case construction, self-check, execution feedback.
- Use VCB as a domain adapter only when the target resembles VCB: Java backend control plane, auth/resource/scope/idempotency/approval/audit/metrics.
- Use the finance adapter when the target touches AP/AR/GL, payment, invoice, tax, voucher/journal, subledger/GL, period close, budget, treasury, reconciliation, or financial controls.

## First Move

If the user provides files, paths, requirements, code, API docs, or existing tests, read them first. Do not begin with a long questionnaire.

If critical inputs are missing, ask for the minimum missing item:
- Requirement or PRD for business intent
- Code/API path for implementation details
- Existing test or template if output must match local style
- Target output format if the user needs a file, YAML, Markdown, Excel, or Gherkin

Use sensible defaults when safe:
- Output: `cases.yaml` plus a concise Markdown summary
- Priority: P0/P1/P2
- Case style: Given-When-Then
- Traceability: source file + line when local files are available

## Reference Loading

Load only the references needed for the task:

| Need | Read |
| --- | --- |
| Choose professional case design techniques | `references/industry-methods.md` |
| Apply VAF-style staged case-generation workflow | `references/vaf-case-flow.md` |
| Target is VCB or similar Java backend control-plane | `references/vcb-case-patterns.md` |
| Target is a finance system, accounting flow, payment, invoice, tax, budget, treasury, or financial-control workflow | `references/adapters/finance-system.md`, then load the specific finance adapter files listed there |
| Finance target has company-specific rules, account mappings, tax codes, approval matrices, systems, tables, incidents, or test data | `references/adapters/finance-project-rulepack.md` |
| Need structured output or validation | `references/case-schema.md` |
| Need to control suite size or split smoke/regression/full | `references/case-pruning.md` |
| Have execution results, failed cases, defects, or flaky tests | `references/execution-feedback-loop.md` |

## Workflow

### 1. Test Admission

Decide whether this is a case-generation task, a test-strategy task, or a case-review task.

Classify the target:
- `unit`: method/class/component behavior
- `api`: endpoint, contract, error shape, auth, idempotency
- `integration`: cross-component flow
- `e2e`: user or system workflow
- `regression`: protect existing behavior after a change
- `security/control`: permission, isolation, approval, audit, compliance
- `exploratory`: unknown behavior, risk discovery

State the selected mode briefly in the output.

### 2. Context Loading

Gather evidence before inventing cases:
- Requirements: PRD, acceptance criteria, design docs, user stories, tickets
- Code: controller/service/domain model/schema/enums/validation/exception handling
- API: OpenAPI, routes, request/response samples, error codes
- Existing tests: naming style, fixture style, mock strategy
- Runtime assumptions: environments, test data, identities, feature flags
- Domain rules: auth, roles, state machine, idempotency, audit, metrics, compliance
- Finance rules when applicable: source document, accounting event, voucher/journal, period, currency, tax, subledger/GL, reconciliation, approval matrix, SoD, audit evidence
- Project rulepack when available: legal entity, account policy, tax code, approval/SoD matrix, integration event, observability table, historical incident, reusable test data

Every case must trace to at least one of:
- `REQ-*`: requirement or acceptance criterion
- `CODE-*`: source code behavior
- `API-*`: API contract
- `RULE-*`: domain or regulatory rule
- `RISK-*`: explicit risk or production incident
- `INF-*`: inferred gap, clearly marked as inferred

### 3. Build The Test Model

Create a compact test model before writing cases:

| Model | Purpose |
| --- | --- |
| Business flow model | E2E paths, actors, major outcomes |
| Feature/layer model | UI/API/service/storage/async layers |
| Rule model | validations, permissions, invariants, policies |
| Data model | equivalence classes, boundaries, required fixtures |
| State model | valid transitions, invalid transitions, terminal states |
| Risk model | impact, likelihood, detectability, rollback need |

If there is not enough context for one model, mark it `unknown` and continue with available evidence.

For finance targets, also build the finance model from `references/adapters/finance-system.md`:
- Business flow model
- Accounting event model
- Control model
- Reconciliation model
- Audit evidence model

### 4. Generate Test Points In Two Views

Use two independent views and then cross-check them.

**E2E view:** business flow -> business scenarios -> E2E test points.

**Layered view:** feature point -> UI/API/service/data/security test points.

Cross-check:
- Every critical E2E scenario has supporting layer checks.
- Every critical API/service rule appears in at least one E2E or integration case when it affects user-visible behavior.
- Any unmatched test point is either added, explicitly deferred, or marked out of scope.

### 5. Select Design Techniques

Read `references/industry-methods.md` and apply its Technique Selection Matrix. Use the smallest set of techniques that fits the risk:
- Equivalence partitioning for input classes
- Boundary value analysis for numeric, date, length, count, and time-window rules
- Decision tables for multi-condition business rules
- State transition testing for lifecycle/status workflows
- Pairwise/combinatorial testing when many flags, roles, browsers, devices, or config dimensions interact
- Scenario/use-case testing for user journeys
- BDD/Given-When-Then for executable communication
- Risk-based prioritization for P0/P1/P2
- Error guessing/checklists for historical incidents and domain-specific failure modes

### 6. Create Cases In Structured Form First

Unless the user only asks for a short list, create or propose structured cases first:
- `cases.yaml` or `cases.json`
- `coverage_map` inside the structured file
- Optional rendered `coverage-map.md`
- Optional rendered Markdown table
- Optional Excel-ready rows
- Optional Gherkin `.feature`

Do not write final Markdown as the only source of truth when the user needs maintainable cases. Markdown is a rendering target; structured cases are the source.

Use scripts when a file output is requested:
- `scripts/create_case_skeleton.py` for T04.1 skeleton generation from test points
- `scripts/render_markdown.py` for Markdown delivery
- `scripts/render_gherkin.py` for Gherkin delivery
- `scripts/export_xlsx.py` for Excel delivery

### 7. Self-Check Gates

Before finalizing, run this checklist:
- No case without a source or explicit `inferred` marker.
- No P0 rule without at least one case.
- No case without an observable expected result.
- No happy-path-only set for non-trivial features.
- Boundary values use concrete N-1/N/N+1 or equivalent data.
- Decision-table cases cover each meaningful rule outcome.
- State cases include invalid transitions and terminal states.
- Security/control features include negative authorization cases.
- E2E and layered test points have been cross-checked.
- Generated cases are executable enough for a tester or automation engineer to follow.
- Finance cases assert business document, accounting event, control decision, ledger impact, reconciliation, and audit evidence when applicable.

If structured case files are produced, run `scripts/validate_cases.py` when practical. Run `scripts/coverage_check.py` for suites with `coverage_map`, P0 requirements, security/control cases, state transitions, or boundary-heavy rules.

For finance structured case files, also run `scripts/finance_coverage_check.py` when practical.

When a finance project rulepack is provided, run `scripts/finance_rulepack_check.py` on the rulepack and `scripts/finance_case_rulepack_check.py` on the generated cases plus the rulepack.

When the user provides raw finance materials but no rulepack, use `scripts/extract_finance_rulepack.py` to create a draft rulepack. After generating or reviewing cases, use `scripts/finance_rule_gap_report.py` to summarize missing internal rules and confirmation needs.

### 8. Prune And Layer The Suite

For non-trivial outputs, read `references/case-pruning.md` and assign each case to one or more suite layers:
- smoke
- p0_gate
- regression
- full
- exploratory

Merge duplicate cases only when setup, action, expected result, priority, and failure diagnosis are the same. Split cases when risk, state, boundary, actor, or observable result differs.

### 9. Execution Feedback

When the user provides test results, failed cases, flaky behavior, or defect ids, read `references/execution-feedback-loop.md`. Classify failures before changing cases. Convert fixed defects into regression cases.

Run `scripts/execution_feedback_check.py` when `execution_results` are present.

## Output Contract

For full case generation, produce:

1. **Mode and assumptions**
2. **Test model summary**
3. **Coverage map**
4. **Cases** in the requested format
5. **Open questions and inferred items**
6. **Self-check result**

Default case fields:
- `id`
- `title`
- `priority`
- `level`
- `type`
- `traceability`
- `preconditions`
- `data`
- `steps`
- `expected`
- `automation_candidate`
- `status`

For maintainable outputs, also include:
- `coverage_map`
- `open_questions`
- `quality_gates`
- suite layers or pruning notes when the case set is large
- execution feedback analysis when results are provided

For finance outputs, include adapter-specific finance annotations when the output format allows it:
- `finance.process`
- `finance.business_event`
- `finance.accounting_event`
- `finance.financial_assertions`
- `finance.control_assertions`
- `finance.regulatory_refs`

If a project rulepack is available, P0 finance cases should reference internal rulepack IDs in `traceability.rules`, `traceability.risks`, finance assertions, or notes. Missing internal rules should become `open_questions`.

## Boundaries

Do not:
- Treat VCB-specific auth/scope/approval rules as universal.
- Invent business rules without marking them as inferred.
- Invent accounting entries, tax treatment, or report-line impact without a requirement, accounting policy, or explicit inferred marker.
- Generate only happy paths unless the user explicitly asks for smoke tests.
- Modify production code while designing cases unless the user asks for test implementation.
- Claim coverage is complete without a traceability map.
