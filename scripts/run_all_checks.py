#!/usr/bin/env python3
"""Run the full case-gen validation suite."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(label: str, command: list[str], cwd: Path) -> bool:
    print(f"\n== {label} ==")
    print(" ".join(command))
    result = subprocess.run(command, cwd=str(cwd), text=True)  # noqa: S603
    if result.returncode == 0:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label} ({result.returncode})")
    return False


def existing(path: Path) -> bool:
    return path.exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all case-gen checks.")
    parser.add_argument(
        "--skill-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Skill root directory. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--quick-validate",
        help="Optional quick_validate.py path. Defaults to sibling .system skill-creator when present.",
    )
    args = parser.parse_args()

    root = Path(args.skill_root).resolve()
    scripts = root / "scripts"
    evals = root / "evals"
    python = sys.executable

    quick_validate = Path(args.quick_validate).resolve() if args.quick_validate else root.parent / ".system" / "skill-creator" / "scripts" / "quick_validate.py"

    checks: list[tuple[str, list[str]]] = []
    if existing(quick_validate):
        checks.append(("skill metadata", [python, str(quick_validate), str(root)]))
    else:
        print(f"SKIP: quick_validate.py not found at {quick_validate}")

    standard_cases = [
        evals / "sample_cases.json",
        evals / "vcb-like-backend" / "expected_cases.json",
    ]
    for path in standard_cases:
        if existing(path):
            checks.append((f"validate {path.relative_to(root)}", [python, str(scripts / "validate_cases.py"), str(path)]))
            checks.append((f"coverage {path.relative_to(root)}", [python, str(scripts / "coverage_check.py"), str(path)]))

    for name in ("finance-ap-payment", "finance-expense-reimbursement", "finance-period-close", "finance-core-processes"):
        path = evals / name / "expected_cases.json"
        if existing(path):
            checks.append((f"validate {name}", [python, str(scripts / "validate_cases.py"), str(path)]))
            checks.append((f"coverage {name}", [python, str(scripts / "coverage_check.py"), str(path)]))
            checks.append((f"finance coverage {name}", [python, str(scripts / "finance_coverage_check.py"), str(path)]))

    rulepack = evals / "finance-rulepack" / "sample_rulepack.json"
    rulepack_cases = evals / "finance-rulepack" / "rulepack_cases.json"
    if existing(rulepack):
        checks.append(("finance rulepack", [python, str(scripts / "finance_rulepack_check.py"), str(rulepack)]))
    if existing(rulepack_cases):
        checks.append(("validate finance rulepack cases", [python, str(scripts / "validate_cases.py"), str(rulepack_cases)]))
        checks.append(("coverage finance rulepack cases", [python, str(scripts / "coverage_check.py"), str(rulepack_cases)]))
        checks.append(("finance coverage rulepack cases", [python, str(scripts / "finance_coverage_check.py"), str(rulepack_cases)]))
    if existing(rulepack) and existing(rulepack_cases):
        checks.append(("case rulepack refs", [python, str(scripts / "finance_case_rulepack_check.py"), str(rulepack_cases), str(rulepack)]))
        checks.append(
            (
                "finance rule gap report",
                [
                    python,
                    str(scripts / "finance_rule_gap_report.py"),
                    str(rulepack_cases),
                    "--rulepack",
                    str(rulepack),
                    "-o",
                    str(evals / "finance-rulepack" / "gap_report.md"),
                ],
            )
        )

    extraction_sources = evals / "finance-rulepack-extraction" / "source-docs"
    extracted_rulepack = evals / "finance-rulepack-extraction" / "draft_rulepack.json"
    if existing(extraction_sources):
        checks.append(
            (
                "extract finance rulepack",
                [
                    python,
                    str(scripts / "extract_finance_rulepack.py"),
                    str(extraction_sources),
                    "-o",
                    str(extracted_rulepack),
                    "--rulepack-id",
                    "xiaomi-finance-extracted-sample",
                    "--owner",
                    "finance-system-team",
                ],
            )
        )
        checks.append(("validate extracted rulepack", [python, str(scripts / "finance_rulepack_check.py"), str(extracted_rulepack)]))

    merged_rulepack = evals / "finance-rulepack-merge" / "merged_rulepack.json"
    merge_inputs = [evals / "finance-rulepack-merge" / "ap_module_rulepack.json", evals / "finance-rulepack-merge" / "tax_module_rulepack.json"]
    if all(existing(path) for path in merge_inputs):
        checks.append(
            (
                "merge finance rulepacks",
                [
                    python,
                    str(scripts / "merge_finance_rulepacks.py"),
                    *[str(path) for path in merge_inputs],
                    "-o",
                    str(merged_rulepack),
                    "--rulepack-id",
                    "xiaomi-finance-merged-sample",
                ],
            )
        )
        checks.append(("validate merged rulepack", [python, str(scripts / "finance_rulepack_check.py"), str(merged_rulepack)]))

    feedback = evals / "execution-feedback" / "results_sample.json"
    if existing(feedback):
        checks.append(("execution feedback", [python, str(scripts / "execution_feedback_check.py"), str(feedback)]))

    failures: list[str] = []
    for label, command in checks:
        if not run(label, command, root):
            failures.append(label)

    print("\n== Summary ==")
    print(f"Checks: {len(checks)}")
    print(f"Failures: {len(failures)}")
    for failure in failures:
        print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

