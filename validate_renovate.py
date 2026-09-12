#!/usr/bin/env python3
"""Validate .github/dependabot.yml and renovate.json.

Checks:
  - renovate.json is valid JSON and parses against the documented schema
    (best-effort: we don't have network access to the live schema, so we
    validate structure + known-good field names locally).
  - .github/dependabot.yml is valid YAML and has the required fields.
  - The two configs don't fight each other (only ONE owns github-actions).
"""
import json
import os
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)")
    sys.exit(2)

WKSP = os.path.dirname(os.path.abspath(__file__))
DEP = os.path.join(WKSP, ".github", "dependabot.yml")
REN = os.path.join(WKSP, "renovate.json")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    errors = []

    # ---- renovate.json -------------------------------------------------
    with open(REN, encoding="utf-8") as f:
        raw = f.read()
    # Reject tab characters (JSON is fine with them, but Renovate's parser has
    # historically been strict and they're invisible in diffs anyway).
    if "\t" in raw:
        errors.append("renovate.json contains a tab character")

    data = load_json(REN)
    if not isinstance(data, dict):
        errors.append("renovate.json root must be an object")
    else:
        if "extends" not in data and "packageRules" not in data:
            errors.append("renovate.json should have `extends` or `packageRules`")
        rules = data.get("packageRules", [])
        if not isinstance(rules, list):
            errors.append("renovate.json `packageRules` must be a list")
        else:
            # Confirm the github-actions rule exists and is disabled (no duplicate-PR fight).
            ga_rules = [r for r in rules if r.get("matchManagers") == ["github-actions"]]
            if not ga_rules:
                errors.append(
                    "renovate.json has no rule disabling `github-actions` -- "
                    "it will compete with Dependabot for the same PRs"
                )
            elif ga_rules[0].get("enabled") is not False:
                errors.append(
                    "renovate.json github-actions rule must set `enabled: false` "
                    "(Dependabot owns that ecosystem)"
                )

    # ---- .github/dependabot.yml ---------------------------------------
    dep = load_yaml(DEP)
    if not isinstance(dep, dict) or "updates" not in dep:
        errors.append(".github/dependabot.yml missing top-level `updates:` list")
    else:
        updates = dep["updates"]
        if not isinstance(updates, list) or not updates:
            errors.append("`updates:` must be a non-empty list")
        else:
            ga = [u for u in updates if u.get("package-ecosystem") == "github-actions"]
            if not ga:
                errors.append(
                    "dependabot.yml has no `github-actions` ecosystem entry"
                )
            else:
                g = ga[0]
                for field in ("directory", "schedule"):
                    if field not in g:
                        errors.append(f"github-actions entry missing `{field}`")
                sched = g.get("schedule", {})
                if not isinstance(sched, dict) or "interval" not in sched:
                    errors.append("github-actions schedule missing `interval`")
                if g.get("directory") != "/":
                    errors.append(
                        "github-actions `directory` should be `/` for workflow files"
                    )

    # ---- cross-config consistency --------------------------------------
    if "packageRules" in (data if isinstance(data, dict) else {}) and isinstance(dep, dict):
        # Both must agree that github-actions is Dependabot's responsibility.
        ga_enabled_in_renovate = any(
            r.get("matchManagers") == ["github-actions"] and r.get("enabled") is not False
            for r in data.get("packageRules", [])
        )
        ga_in_dependabot = any(
            u.get("package-ecosystem") == "github-actions" for u in dep.get("updates", [])
        )
        if ga_enabled_in_renovate and ga_in_dependabot:
            errors.append(
                "CONFLICT: both Renovate and Dependabot are enabled for "
                "github-actions -- this produces duplicate PRs"
            )

    if errors:
        print(f"{len(errors)} issue(s):")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    print("OK  Both configs validated successfully")
    print("    .github/dependabot.yml")
    for u in dep["updates"]:
        print(f"      - {u['package-ecosystem']:<18} dir={u.get('directory')} "
              f"schedule={u.get('schedule', {}).get('interval')}")
    print("    renovate.json")
    print(f"      enabled={data.get('enabled')}  dashboard={data.get('dependencyDashboard')}")
    for r in data.get("packageRules", []):
        print(f"      rule: managers={r.get('matchManagers')} enabled={r.get('enabled')}")
    print("")
    print("    Division of labour: Dependabot -> github-actions, Renovate -> disabled")
    print("    (Renovate stays out of the github-actions ecosystem to avoid duplicate PRs.)")


if __name__ == "__main__":
    main()
