#!/usr/bin/env python3
"""nohumanwrites — check how much of what you use was written through an attested machine channel.

  python3 nohumanwrites.py check <path>...        score files or a directory (git diff aware)
  python3 nohumanwrites.py check <path> --json    machine-readable
  python3 nohumanwrites.py check <path> --badge   one-line badge for a README
  python3 nohumanwrites.py check <path> --transcripts   score against Claude Code logs even if a ledger exists
  python3 nohumanwrites.py setup                  create the signing key + install the Claude Code hook

Evidence is used in this order, and the report says which one it found:
  1. a signed ledger in the repository (.nhw/attest.jsonl)   — exact, verifiable
  2. Claude Code transcripts on this machine (~/.claude/projects) — exact for logged writes, no signatures
  3. nothing                                                    — then the honest answer is "no provenance",
                                                                  never a guess from writing style.
Standard library + OpenSSH. Nothing leaves the machine.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from nhw import attest, verify  # noqa: E402

MIN_LEN = 12

def repo_root(path):
    d = os.path.abspath(path if os.path.isdir(path) else os.path.dirname(path))
    while d and d != "/":
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None

def list_files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "dist", "build")]
                out += [os.path.join(root, f) for f in files if not f.startswith(".") and os.path.getsize(os.path.join(root, f)) < 2_000_000]
        elif os.path.isfile(p):
            out.append(p)
    return out

def is_text(path):
    try:
        with open(path, "rb") as fh:
            return b"\x00" not in fh.read(4096)
    except OSError:
        return False

def check_ledger(repo, files):
    records = verify.load_ledger(repo); signers = verify.allowed_signers(repo)
    if not records:
        return None
    tot = un = 0; per = []
    for f in files:
        rel = os.path.relpath(os.path.abspath(f), repo)
        covered, nrec, stale = verify.attested_lines(repo, rel, records, signers)
        lines = open(f, errors="replace").read().split("\n")
        consider = [i for i in range(1, len(lines) + 1) if len(lines[i - 1].strip()) >= MIN_LEN]
        u = [i for i in consider if i not in covered]
        tot += len(consider); un += len(u)
        per.append({"file": rel, "lines": len(consider), "unattested": u})
    return {"evidence": "signed ledger (.nhw/attest.jsonl)", "verified_signatures": bool(signers),
            "lines": tot, "unattested": un, "files": per}

def check_transcripts(files):
    if not os.path.isdir(attest.LOGDIR):
        return None
    pf, stats = attest.load_index()
    if not stats.get("records"):
        return None
    tot = un = 0; per = []
    for f in files:
        r = attest.attribute(f, pf, MIN_LEN)
        if "error" in r: continue
        tot += r["considered"]; un += len(r["unattested"])
        per.append({"file": f, "lines": r["considered"], "unattested": [i for i, _ in r["unattested"]]})
    return {"evidence": f"Claude Code transcripts on this machine ({stats['records']} logged writes, unsigned)",
            "verified_signatures": False, "lines": tot, "unattested": un, "files": per}

def render(res, badge=False, as_json=False):
    if as_json:
        print(json.dumps(res, indent=1)); return
    if res is None:
        print("NoHumanWrites: no provenance available here.")
        print("  No signed ledger in this repository and no agent transcripts on this machine.")
        print("  Writing style is not evidence (see the paper, §6), so no score is given.")
        print("  To get one: python3 nohumanwrites.py setup   (signs every future agent edit)")
        return
    pct = 100 * (res["lines"] - res["unattested"]) / (res["lines"] or 1)
    if badge:
        print(f"![NoHumanWrites](https://img.shields.io/badge/NoHumanWrites-{pct:.0f}%25_attested-{'2ea44f' if pct >= 90 else 'e0b23a' if pct >= 50 else 'd23a2e'})"); return
    print(f"NoHumanWrites: {pct:.0f}% attested — {res['lines'] - res['unattested']} of {res['lines']} lines")
    print(f"  evidence: {res['evidence']}" + ("" if res["verified_signatures"] else "  (no signature check)"))
    worst = sorted((f for f in res["files"] if f["lines"]), key=lambda f: -len(f["unattested"]) / f["lines"])[:8]
    for f in worst:
        if f["unattested"]:
            u = f["unattested"]
            print(f"  {f['file']}: {len(u)} unattested line(s) " + (f"→ {u[:12]}{'…' if len(u) > 12 else ''}"))
    if res["unattested"] == 0:
        print("  every considered line carries machine provenance.")
    else:
        print("  unattested = typed by hand, or written through a channel with no hook. Review those first.")

def cmd_check(args):
    flags = {a for a in args if a.startswith("--")}; paths = [a for a in args if not a.startswith("--")] or ["."]
    files = [f for f in list_files(paths) if is_text(f)]
    if not files:
        print("nothing to check"); return 2
    repo = repo_root(paths[0])
    res = None if "--transcripts" in flags else (check_ledger(repo, files) if repo else None)
    if res is None:
        res = check_transcripts(files)
    elif os.path.isdir(attest.LOGDIR) and "--json" not in flags and "--badge" not in flags:
        print("  (a signed ledger was found and used; add --transcripts to score against unsigned agent logs instead)")
    render(res, badge="--badge" in flags, as_json="--json" in flags)
    return 0

def cmd_setup():
    r = subprocess.run(["bash", os.path.join(HERE, "setup-key.sh")])
    if r.returncode: return r.returncode
    settings = os.path.expanduser("~/.claude/settings.json")
    cmd = f"python3 \"{os.path.join(HERE, 'nhw', 'hook.py')}\""
    try:
        s = json.load(open(settings)) if os.path.exists(settings) else {}
    except json.JSONDecodeError:
        print(f"{settings} is not valid JSON; add the hook by hand (see nhw/hook.py docstring)"); return 1
    pt = s.setdefault("hooks", {}).setdefault("PostToolUse", [])
    if any(h.get("command", "").endswith("nhw/hook.py\"") or "nhw/hook.py" in h.get("command", "") for m in pt for h in m.get("hooks", [])):
        print("hook already installed"); return 0
    pt.append({"matcher": "Write|Edit", "hooks": [{"type": "command", "command": cmd, "timeout": 10}]})
    json.dump(s, open(settings, "w"), indent=2); print(f"hook installed in {settings}")
    return 0

def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    if argv[0] == "check": return cmd_check(argv[1:])
    if argv[0] == "setup": return cmd_setup()
    print(__doc__); return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
