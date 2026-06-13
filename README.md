# case-gen

`case-gen` is a Codex skill for professional test case generation.

It is designed as a general case-generation system, not a VCB-only generator:

- VAF provides the workflow skeleton: test admission, context loading, dual-view test-point design, staged case construction, and self-check.
- Industry test design methods provide the technique base: equivalence partitioning, boundary value analysis, decision tables, state transition testing, pairwise/combinatorial testing, risk-based prioritization, and Given-When-Then case expression.
- VCB provides an optional domain adapter for backend control-plane systems with auth, approval, scope, idempotency, audit, and metrics risks.

## Layout

```text
case-gen/
├── SKILL.md
├── references/
│   ├── industry-methods.md
│   ├── vaf-case-flow.md
│   ├── vcb-case-patterns.md
│   ├── case-schema.md
│   ├── case-pruning.md
│   └── execution-feedback-loop.md
├── scripts/
│   ├── validate_cases.py
│   ├── coverage_check.py
│   ├── render_markdown.py
│   └── render_gherkin.py
├── evals/
│   ├── evals.json
│   └── sample_cases.json
├── legacy/
│   └── vcb-case-gen-progress.md
└── SYNC.md
```

## Validate

Validate the skill metadata:

```powershell
$env:PYTHONUTF8='1'
python C:\Users\MI\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\MI\.codex\skills\case-gen
```

Validate structured cases:

```powershell
python C:\Users\MI\.codex\skills\case-gen\scripts\validate_cases.py C:\Users\MI\.codex\skills\case-gen\evals\sample_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\coverage_check.py C:\Users\MI\.codex\skills\case-gen\evals\sample_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\validate_cases.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\coverage_check.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\render_markdown.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json -o C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\rendered.md
python C:\Users\MI\.codex\skills\case-gen\scripts\render_gherkin.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json -o C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\rendered.feature
```

## Current P0 Capability

- Technique Selection Matrix: maps input signals to test design techniques and required case shapes.
- Coverage map schema: connects sources, test points, cross-view links, and cases.
- Quality gates: records whether P0 coverage, traceability, observability, boundary values, state checks, and security negative cases are present.
- `coverage_check.py`: performs coverage-quality checks beyond structural validation.
- `evals/vcb-like-backend`: a realistic VCB-like backend adapter eval with design input, controller input, and expected cases.
- Case pruning and suite layering: smoke, P0 gate, regression, full, exploratory.
- Execution feedback loop: failure classification and defect-to-regression flow.
- Renderers: Markdown and Gherkin output from structured case JSON/YAML.

## Sync Policy

This skill is maintained in three locations:

1. Codex active skill: `C:\Users\MI\.codex\skills\case-gen`
2. Desktop working copy: `C:\Users\MI\Desktop\vcb-case-gen-skill`
3. GitHub repository: `https://github.com/xingzaidadi/case-gen`

See `SYNC.md` before changing files.
