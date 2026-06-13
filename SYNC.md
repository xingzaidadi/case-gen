# Sync Policy

Maintain `case-gen` in three synchronized locations:

| Role | Path |
| --- | --- |
| Codex active skill | `C:\Users\MI\.codex\skills\case-gen` |
| Desktop working copy | `C:\Users\MI\Desktop\vcb-case-gen-skill` |
| GitHub remote | `https://github.com/xingzaidadi/case-gen` |

## Source Of Truth

During Codex work, edit the Codex active skill first:

```text
C:\Users\MI\.codex\skills\case-gen
```

After edits:

1. Validate `SKILL.md`.
2. Validate any generated sample cases.
3. Copy the same files to the desktop working copy.
4. Commit and push the desktop working copy to GitHub.

## Required Checks

```powershell
$env:PYTHONUTF8='1'
python C:\Users\MI\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\MI\.codex\skills\case-gen
python C:\Users\MI\.codex\skills\case-gen\scripts\validate_cases.py C:\Users\MI\.codex\skills\case-gen\evals\sample_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\coverage_check.py C:\Users\MI\.codex\skills\case-gen\evals\sample_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\validate_cases.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\coverage_check.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json
python C:\Users\MI\.codex\skills\case-gen\scripts\render_markdown.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json -o C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\rendered.md
python C:\Users\MI\.codex\skills\case-gen\scripts\render_gherkin.py C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\expected_cases.json -o C:\Users\MI\.codex\skills\case-gen\evals\vcb-like-backend\rendered.feature
```

## Notes

- Do not make future updates only in GitHub or only on the desktop.
- Do not turn `case-gen` back into a VCB-only skill. Keep VCB in `references/vcb-case-patterns.md` as a domain adapter.
- Keep `SKILL.md` concise. Move detailed methods and templates into `references/`.
