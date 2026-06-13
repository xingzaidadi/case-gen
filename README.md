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
│   └── case-schema.md
├── scripts/
│   └── validate_cases.py
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
```

## Sync Policy

This skill is maintained in three locations:

1. Codex active skill: `C:\Users\MI\.codex\skills\case-gen`
2. Desktop working copy: `C:\Users\MI\Desktop\vcb-case-gen-skill`
3. GitHub repository: `https://github.com/xingzaidadi/case-gen`

See `SYNC.md` before changing files.

