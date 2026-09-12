#!/usr/bin/env python3
"""Validate .github/workflows/ci.yml against GitHub Actions requirements.

Parses the YAML properly (via PyYAML, with a clear error if absent) and checks
the structural rules that matter for the workflow to actually run:

  - `on` is a mapping with push/pull_request/workflow_dispatch triggers
  - `jobs` has at least one job
  - every job has `runs-on` and at least one step
  - every step has `run` or `uses` (and `run` is not empty)
  - required secrets referenced: NETLIFY_AUTH_TOKEN, NETLIFY_SITE_ID
"""
import sys
import os

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(2)

WKSP = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(WKSP, ".github", "workflows", "ci.yml")


def main():
    print(f"Validating {os.path.relpath(PATH, WKSP)}")
    with open(PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    errors = []

    # --- `on` ---------------------------------------------------------------
    on = data.get("on")
    if not isinstance(on, dict):
        errors.append("`on:` must be a mapping (push/pull_request/workflow_dispatch)")
    else:
        triggers = list(on.keys())
        for required in ("push", "pull_request", "workflow_dispatch"):
            if required not in triggers:
                errors.append(f"`on:` is missing trigger `{required}`")
        if "push" in on and not on["push"].get("branches"):
            errors.append("`on.push` should specify `branches:` (e.g. [main, master])")

    # --- `jobs` -------------------------------------------------------------
    jobs = data.get("jobs") or {}
    if not isinstance(jobs, dict) or not jobs:
        errors.append("`jobs:` must contain at least one job")

    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            errors.append(f"job `{job_name}` is not a mapping")
            continue
        if "runs-on" not in job:
            errors.append(f"job `{job_name}` missing `runs-on:`")
        steps = job.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"job `{job_name}` has no steps")
            continue
        for idx, step in enumerate(steps, 1):
            if not isinstance(step, dict):
                errors.append(f"job `{job_name}` step {idx} is not a mapping")
                continue
            if "run" not in step and "uses" not in step:
                errors.append(
                    f"job `{job_name}` step {idx} has neither `run:` nor `uses:`"
                )
            if step.get("run") == "":
                errors.append(f"job `{job_name}` step {idx} has empty `run:`")

    # --- secrets ------------------------------------------------------------
    text = open(PATH, encoding="utf-8").read()
    for secret in ("NETLIFY_AUTH_TOKEN", "NETLIFY_SITE_ID"):
        if secret not in text:
            errors.append(f"secret `{secret}` is not referenced")

    if errors:
        print(f"\n{len(errors)} issue(s):")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    # --- success ------------------------------------------------------------
    print("Workflow structure is valid")
    print(f"   triggers: {list(on.keys())}")
    print(f"   jobs: {list(jobs.keys())}")
    for job_name, job in jobs.items():
        print(f"     - {job_name}: runs-on={job.get('runs-on')}, {len(job['steps'])} steps")
    print()
    print("(Structure only. Exact action versions and secret availability are")
    print(" verified when the workflow actually runs on GitHub Actions.)")


if __name__ == "__main__":
    main()
