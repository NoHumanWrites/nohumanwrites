#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""nohumanwrites — check how much of what you use was written through an attested machine channel.

  python3 nohumanwrites.py check <path>...              score files or a directory
  python3 nohumanwrites.py check <path> --json          machine-readable
  python3 nohumanwrites.py check <path> --badge         one-line badge for a README (refused when there is no score)
  python3 nohumanwrites.py check <path> --transcripts   score against Claude Code logs even if a ledger exists
  python3 nohumanwrites.py check <path> --signers FILE  use this allowed-signers file
  python3 nohumanwrites.py check <path> --trust-repo-signers   accept the repository's own keys (prints a warning)
  python3 nohumanwrites.py setup                        create the signing key + install the Claude Code hook

Evidence is used in this order, and the report says which one it found:
  1. a signed ledger in the repository (.nhw/attest.jsonl)   — exact, verifiable with YOUR keys
  2. Claude Code transcripts on this machine (~/.claude/projects) — exact for logged writes, unsigned, strong
     matches only (the line was written to that path)
  3. nothing                                                    — then the honest answer is "no provenance",
                                                                  never a guess from writing style.
Three states: attested / unattested / unverifiable.  "Unattested" means typed by hand OR written through a
channel with no hook; this tool never says "human".  Standard library + OpenSSH.  Nothing leaves the machine.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile

__version__ = "0.1.0-rc1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from nhw import attest, verify  # noqa: E402
from nhw.common import MIN_LEN, norm_text, read_text, repo_root  # noqa: E402

SKIP_DIRS = {"node_modules", "__pycache__", "dist", "build", ".git", ".nhw"}


def list_files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS]
                for f in files:
                    fp = os.path.join(root, f)
                    if not f.startswith(".") and os.path.isfile(fp) and os.path.getsize(fp) < 2_000_000:
                        out.append(fp)
        elif os.path.isfile(p):
            out.append(p)
    return [f for f in out if read_text(f) is not None]


def considered(body):
    lines = norm_text(body).split("\n")
    return [i for i in range(1, len(lines) + 1) if len(lines[i - 1].strip()) >= MIN_LEN]


def check_ledger(repo, files, explicit=None, trust_repo=False):
    records, malformed = verify.load_ledger(repo)
    if not records and not malformed:
        return None
    signers, src = verify.allowed_signers(repo, explicit, trust_repo)
    fps = verify.fingerprints(signers) if signers else {}
    tot = un = 0; per = []; verified_total = unverified_total = 0; unverifiable_files = 0
    for f in files:
        rel = os.path.relpath(os.path.realpath(f), repo)
        covered, verified, stale, unverified = verify.attested_lines(repo, rel, records, signers, fps)
        verified_total += verified; unverified_total += unverified
        cons = considered(read_text(f) or "")
        if not cons:
            continue
        if verified == 0 and unverified > 0:
            unverifiable_files += 1; per.append({"file": rel, "lines": len(cons), "state": "unverifiable"}); continue
        u = [i for i in cons if i not in covered]
        tot += len(cons); un += len(u)
        per.append({"file": rel, "lines": len(cons), "unattested": u, "state": "scored"})
    state = "scored" if tot else ("unverifiable" if unverifiable_files else "no-evidence")
    return {"state": state, "evidence": "signed ledger (.nhw/attest.jsonl)", "trust_root": src, "keys": len(fps),
            "records_valid": len(records), "records_malformed": malformed,
            "records_verified": verified_total, "records_unverified": unverified_total,
            "files_unverifiable": unverifiable_files, "lines": tot, "unattested": un, "files": per}


def check_transcripts(files):
    if not os.path.isdir(attest.LOGDIR):
        return None
    pf, stats = attest.load_index()
    if not stats.get("records"):
        return None
    tot = un = 0; per = []
    for f in files:
        r = attest.attribute(f, pf, MIN_LEN)
        if "error" in r or not r["considered"]:
            continue
        # strong matches only: the agent wrote that line to THAT path; "weak" (same line elsewhere) is not evidence
        strong_un = r["considered"] - r["strong"]
        tot += r["considered"]; un += strong_un
        per.append({"file": f, "lines": r["considered"], "unattested_count": strong_un, "unattested": [i for i, _ in r["unattested"]]})
    return {"state": "scored" if tot else "no-evidence",
            "evidence": f"Claude Code transcripts on this machine ({stats['records']} logged writes; unsigned; strong matches only)",
            "trust_root": "none (unsigned logs)", "lines": tot, "unattested": un, "files": per}


def render(res, badge=False, as_json=False):
    if as_json:
        print(json.dumps(res, indent=1)); return 0
    if res is None or res["state"] == "no-evidence":
        print("NoHumanWrites: no provenance available here.")
        print("  No signed ledger for these files and no agent transcripts on this machine.")
        print("  Writing style is not evidence (paper §6), so no score is given.")
        print("  To get one: python3 nohumanwrites.py setup   (signs every future agent edit)")
        return 3
    if res["state"] == "unverifiable":
        print(f"NoHumanWrites: UNVERIFIABLE — ledger present ({res['records_valid']} record(s)) but none verify with your keys "
              f"(trust root: {res['trust_root']}). No score. Use --signers FILE, or --trust-repo-signers if you accept the repo's own keys.")
        return 4
    pct = 100 * (res["lines"] - res["unattested"]) / res["lines"]
    if badge:
        colour = "2ea44f" if pct >= 90 else "e0b23a" if pct >= 50 else "d23a2e"
        print(f"![NoHumanWrites](https://img.shields.io/badge/NoHumanWrites-{pct:.0f}%25_attested-{colour})"); return 0
    print(f"NoHumanWrites: {pct:.0f}% attested — {res['lines'] - res['unattested']} of {res['lines']} lines")
    print(f"  evidence: {res['evidence']}; trust root: {res['trust_root']}")
    if res.get("records_malformed"):
        print(f"  {res['records_malformed']} malformed ledger record(s) ignored")
    if res.get("files_unverifiable"):
        print(f"  {res['files_unverifiable']} file(s) unverifiable (records present, none verify with your keys) — not scored")
    scored = [f for f in res["files"] if f.get("state", "scored") == "scored" and f["lines"]]
    worst = sorted(scored, key=lambda f: -(len(f.get("unattested", [])) or f.get("unattested_count", 0)) / f["lines"])[:8]
    for f in worst:
        u = f.get("unattested", [])
        n = len(u) if u else f.get("unattested_count", 0)
        if n:
            print(f"  {f['file']}: {n} unattested line(s)" + (f" → {u[:12]}{'…' if len(u) > 12 else ''}" if u else ""))
    if res["unattested"] == 0:
        print("  every considered line carries machine provenance.")
    else:
        print("  unattested = typed by hand, or written through a channel with no hook. Review those first.")
    return 0


def cmd_check(args):
    flags = {a for a in args if a.startswith("--")}
    explicit = args[args.index("--signers") + 1] if "--signers" in args else None
    paths = [a for i, a in enumerate(args) if not a.startswith("--") and not (i > 0 and args[i - 1] == "--signers")] or ["."]
    files = list_files(paths)
    if not files:
        print("nothing to check (no UTF-8 text files)"); return 2
    repo = repo_root(paths[0])
    res = None if "--transcripts" in flags else (check_ledger(repo, files, explicit, "--trust-repo-signers" in flags) if repo else None)
    if res is None:
        res = check_transcripts(files)
    return render(res, badge="--badge" in flags, as_json="--json" in flags)


def cmd_setup():
    r = subprocess.run(["bash", os.path.join(HERE, "setup-key.sh")])
    if r.returncode:
        return r.returncode
    settings = os.path.expanduser("~/.claude/settings.json")
    if os.path.islink(settings):
        print(f"{settings} is a symlink; add the hook by hand (see nhw/hook.py docstring)"); return 1
    cmd = f"python3 \"{os.path.join(HERE, 'nhw', 'hook.py')}\""
    try:
        s = json.load(open(settings, encoding="utf-8")) if os.path.exists(settings) else {}
    except json.JSONDecodeError:
        print(f"{settings} is not valid JSON; add the hook by hand (see nhw/hook.py docstring)"); return 1
    pt = s.setdefault("hooks", {}).setdefault("PostToolUse", [])
    if any("nhw/hook.py" in h.get("command", "") for m in pt for h in m.get("hooks", [])):
        print("hook already installed"); return 0
    pt.append({"matcher": "Write|Edit|MultiEdit", "hooks": [{"type": "command", "command": cmd, "timeout": 10}]})
    if os.path.exists(settings):
        with open(settings + ".bak", "w", encoding="utf-8") as b, open(settings, encoding="utf-8") as o:
            b.write(o.read())
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(settings) or ".", prefix=".settings.", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)
    os.replace(tmp, settings)
    print(f"hook installed in {settings} (backup: {settings}.bak)")
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    if argv[0] in ("-V", "--version"):
        print(__version__); return 0
    if argv[0] == "check":
        return cmd_check(argv[1:])
    if argv[0] == "setup":
        return cmd_setup()
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
