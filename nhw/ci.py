#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The GitHub Action's runner: one `check` with a floor, its number as a step output, its detail as the job summary.
Run:  python3 nhw/ci.py --path docs --fail-under 95 --signers .nhw/allowed_signers
The exit code is the checker's: 0 at or above the floor, 1 below it or without a verified score.
"""
import argparse, json, os, subprocess, sys
CLI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nohumanwrites.py")


def append(env_var, text):
    target = os.environ.get(env_var)
    if target:
        with open(target, "a", encoding="utf-8") as f:
            f.write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="."); ap.add_argument("--fail-under", default="90"); ap.add_argument("--signers", default=".nhw/allowed_signers")
    a = ap.parse_args()
    r = subprocess.run([sys.executable, CLI, "check", a.path, "--signers", a.signers, "--fail-under", a.fail_under, "--json"],
                       capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
    except ValueError:
        res = {}
    state = res.get("state", "no-evidence")
    lines, un = res.get("lines", 0), res.get("unattested", 0)
    pct = round(100 * (lines - un) / lines) if state == "scored" and lines else None
    verdict = "pass" if r.returncode == 0 else "FAIL"
    head = (f"NoHumanWrites: {pct}% attested ({lines - un} of {lines} units)" if pct is not None
            else f"NoHumanWrites: no verified score ({state})")
    print(f"{head} · floor {a.fail_under}% · {verdict}")
    if r.stderr.strip():
        print(r.stderr.strip())
    append("GITHUB_OUTPUT", f"attested={'' if pct is None else pct}\nstate={state}\n")
    rows = [f for f in res.get("files", []) if f.get("unattested")]
    md = [f"### {head}", "", f"floor {a.fail_under}% · trust root `{a.signers}` · **{verdict}**", ""]
    if rows:
        md += ["| file | unattested units |", "|---|---|"]
        md += [f"| `{f['file']}` | {len(f['unattested'])} of {f.get('units', f.get('lines', '?'))} |" for f in rows[:20]]
        if len(rows) > 20:
            md.append(f"| … | {len(rows) - 20} more files |")
    elif state == "scored":
        md.append("Every unit sits in a signed, still-matching machine record.")
    else:
        md.append("No ledger verified with the given keys, so there is no score; a floor with no score fails by design.")
    append("GITHUB_STEP_SUMMARY", "\n".join(md) + "\n")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
