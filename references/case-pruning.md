# Case Pruning And Suite Layering

Professional case generation must balance coverage and execution cost. Use this reference after initial case generation and before final delivery.

## Suite Layers

| Layer | Purpose | Typical size | Must include |
| --- | --- | --- | --- |
| Smoke | Fast release sanity | 5-15 cases | Primary happy paths and one critical negative for each major control |
| P0 Gate | Release blockers | All P0 cases | Security, data integrity, money/destructive actions, critical workflows |
| Regression | Protect existing behavior | P0 + important P1 | Historical defects, high-risk boundaries, core compatibility |
| Full | Complete planned coverage | All non-deferred cases | P0/P1/P2, long-tail compatibility, broader pairwise |
| Exploratory Charter | Human-guided risk discovery | Time-boxed | Areas where rules are uncertain or defect density is high |

Every generated case should belong to at least one layer. If it belongs to no layer, it is likely noise.

## Pruning Rules

Merge cases when all of these are true:
- Same setup
- Same action
- Same expected result
- Same priority
- Same failure diagnosis

Split cases when any of these differ:
- Different risk or priority
- Different actor/permission model
- Different state transition
- Different boundary value
- Different observable result
- Different automation target
- Different failure owner

## Pairwise Control

Use pairwise or reduced combinatorial sets when:
- There are 4+ independent dimensions.
- Full Cartesian coverage is too expensive.
- P0 combinations are separately covered.

Do not hide critical combinations inside pairwise:
- Admin + destructive action + production-like data
- Old client + new required field
- Cross-tenant + write operation
- Retry + timeout + mutation

## Automation Candidate Rules

| Candidate | Use when |
| --- | --- |
| high | Deterministic setup, stable assertion, important regression value |
| medium | Requires environment orchestration or timing but still repeatable |
| low | Manual judgment, visual nuance, unstable external dependency, one-off migration |

Prefer automation for P0 and high-frequency P1 cases.

## Cost/Risk Review

Before final output, include a short pruning note:

```text
Generated: 42 cases
Smoke: 8
P0 Gate: 14
Regression: 27
Full: 42
Pruned/Merged: 11
Deferred: 3
Reason: pairwise used for browser/device/role dimensions; P0 security combinations kept explicit.
```

## Anti-Patterns

- Generating one case per field when equivalence classes cover the same behavior.
- Generating all combinations without risk prioritization.
- Merging cases that fail for different reasons.
- Treating E2E cases as a replacement for API/service-layer assertions.
- Keeping P2 compatibility cases in the smoke suite.

