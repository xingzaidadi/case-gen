---
name: case-gen
description: Use when the user asks to design, generate, review, or improve test cases, test scenarios, acceptance checks, unit-test matrices, E2E cases, API cases, regression cases, or QA plans. Use this skill even when the user says "生成用例", "测试点", "case", "验收清单", "单测场景", "E2E", "回归用例", or asks whether coverage is complete. Do not default to VCB-specific rules unless the target system is VCB or a similar Java backend control-plane with auth, approval, scope, idempotency, audit, or metrics risks.
---

# Case Gen

Design professional test cases from requirements, code, API contracts, existing tests, and domain rules. Build the case set from first principles, then render it into Markdown, YAML/JSON, Excel-ready rows, Gherkin, or implementation guidance as requested.

This is not a VCB-only skill. VCB and VAF are reference systems:
- Use VAF as the workflow skeleton: admission, context loading, dual-view test-point design, case construction, self-check, execution feedback.
- Use VCB as a domain adapter only when the target resembles VCB: Java backend control plane, auth/resource/scope/idempotency/approval/audit/metrics.

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
| Need structured output or validation | `references/case-schema.md` |

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

### 4. Generate Test Points In Two Views

Use two independent views and then cross-check them.

**E2E view:** business flow -> business scenarios -> E2E test points.

**Layered view:** feature point -> UI/API/service/data/security test points.

Cross-check:
- Every critical E2E scenario has supporting layer checks.
- Every critical API/service rule appears in at least one E2E or integration case when it affects user-visible behavior.
- Any unmatched test point is either added, explicitly deferred, or marked out of scope.

### 5. Select Design Techniques

Use the smallest set of techniques that fits the risk:
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
- Optional `coverage-map.md`
- Optional rendered Markdown table
- Optional Excel-ready rows
- Optional Gherkin `.feature`

Do not write final Markdown as the only source of truth when the user needs maintainable cases. Markdown is a rendering target; structured cases are the source.

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

If structured case files are produced, run `scripts/validate_cases.py` when practical.

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

## Boundaries

Do not:
- Treat VCB-specific auth/scope/approval rules as universal.
- Invent business rules without marking them as inferred.
- Generate only happy paths unless the user explicitly asks for smoke tests.
- Modify production code while designing cases unless the user asks for test implementation.
- Claim coverage is complete without a traceability map.

