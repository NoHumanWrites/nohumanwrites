#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The commit guard: staged files under the guarded paths stay attested above the floor, and the ledger is staged with them.
Installed as .git/hooks/pre-commit by `python3 nohumanwrites.py setup --guard`; shared by every worktree of the clone.
Skip once with `git commit --no-verify`. The floor and scope match .github/workflows/test.yml.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(HERE, "nohumanwrites.py")
FLOOR, SCOPE, SIGNERS = "95", ("docs/",), ".nhw/allowed_signers"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


def main():
    top = git("rev-parse", "--show-toplevel").strip()
    if not top:
        return 0
    os.chdir(top)
    staged = [l for l in git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines() if l]
    scope = [f for f in staged if f.startswith(SCOPE) and os.path.isfile(f)]
    if not scope:
        return 0
    r = subprocess.run([sys.executable, CLI, "check", *scope, "--signers", SIGNERS, "--fail-under", FLOOR, "--json"],
                       capture_output=True, text=True)
    if r.returncode:
        try:
            files = json.loads(r.stdout).get("files", [])
        except ValueError:
            files = []
        bad = [f["file"] for f in files if f.get("unattested") or f.get("state") == "unverifiable"] or scope
        print(f"NoHumanWrites guard: the staged {', '.join(scope)} would land below {FLOOR}% attested.")
        print("  " + r.stderr.strip())
        print("  Sign what the machine wrote, then stage the ledger:")
        print(f"    python3 nohumanwrites.py import {' '.join(bad)} --from <harness>")
        print("    git add .nhw/attest.jsonl")
        print("  Skip once: git commit --no-verify")
        return 1
    status = git("status", "--porcelain", "--", ".nhw/attest.jsonl")
    if status.startswith("??") or (len(status) > 1 and status[1] == "M"):
        print("NoHumanWrites guard: .nhw/attest.jsonl has unstaged records; the signed pages need them in the same commit.")
        print("    git add .nhw/attest.jsonl")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
