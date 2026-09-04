#!/usr/bin/env python3
"""NoHumanWrite — the verifier for the signed ledger.

  verify.py <repo> [<file>...]      attribute files against <repo>/.nhw/attest.jsonl
  verify.py <repo> --diff [<ref>]   attribute the lines a git diff adds (default: working tree vs HEAD)

For each record: check the signature (ssh-keygen -Y verify against
.nhw/allowed_signers, or ~/.nhw/allowed_signers), then check that the recorded
hunk hash still matches text present in the file.  A line is attested when it
sits inside a verified, still-matching hunk.  Everything else is reported as
unattested — human-typed, or written through a channel with no hook.
"""
import hashlib, json, os, subprocess, sys, tempfile, re

NAMESPACE = "nhw"

def norm(text: str) -> str:
    return "\n".join(l.rstrip() for l in text.replace("\r\n", "\n").split("\n")).strip("\n")

def allowed_signers(repo: str) -> str | None:
    for p in (os.path.join(repo, ".nhw", "allowed_signers"), os.path.expanduser("~/.nhw/allowed_signers")):
        if os.path.exists(p):
            return p
    return None

def sig_ok(rec: dict, signers: str | None) -> bool:
    if not signers:
        return False
    body = {k: v for k, v in rec.items() if k != "sig"}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sig") as s:
        s.write(rec["sig"].encode()); sp = s.name
    try:
        r = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", signers, "-I", "nhw", "-n", NAMESPACE, "-s", sp],
                           input=payload, capture_output=True)
        return r.returncode == 0
    finally:
        os.unlink(sp)

def load_ledger(repo: str):
    p = os.path.join(repo, ".nhw", "attest.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p):
        try: out.append(json.loads(ln))
        except Exception: pass
    return out

def attested_lines(repo: str, rel: str, records, signers):
    """Return the set of 1-based line numbers of <rel> covered by verified, matching hunks."""
    path = os.path.join(repo, rel)
    try:
        body = open(path, errors="replace").read()
    except Exception:
        return set(), 0, 0
    lines = body.split("\n")
    covered, verified, stale = set(), 0, 0
    for r in records:
        if r.get("path") != rel or not sig_ok(r, signers):
            continue
        verified += 1
        n = r["hunk"]["lines"]; want = r["hunk"]["sha256"]
        hit = False
        for i in range(0, len(lines) - n + 1):          # slide a window; formatters move hunks
            seg = norm("\n".join(lines[i:i + n]))
            if hashlib.sha256(seg.encode()).hexdigest() == want:
                covered.update(range(i + 1, i + n + 1)); hit = True; break
        if not hit:
            stale += 1
    return covered, verified, stale

def report_file(repo, rel, records, signers, added=None):
    covered, verified, stale = attested_lines(repo, rel, records, signers)
    lines = open(os.path.join(repo, rel), errors="replace").read().split("\n")
    consider = [i for i in (added or range(1, len(lines) + 1)) if i <= len(lines) and len(lines[i - 1].strip()) >= 12]
    un = [i for i in consider if i not in covered]
    pct = 100 * (len(consider) - len(un)) / (len(consider) or 1)
    print(f"{rel}: {pct:.0f}% attested ({len(consider) - len(un)}/{len(consider)} lines), "
          f"{verified} signed records, {stale} stale, unattested: {un[:20]}{'…' if len(un) > 20 else ''}")
    return len(consider), len(un)

def diff_added(repo, ref):
    out = subprocess.run(["git", "diff", "-U0", ref, "--", "."], cwd=repo, capture_output=True, text=True).stdout
    files, cur = {}, None
    for ln in out.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:]; files.setdefault(cur, set())
        elif ln.startswith("@@") and cur:
            m = re.search(r"\+(\d+)(?:,(\d+))?", ln)
            s, n = int(m.group(1)), int(m.group(2) or 1)
            files[cur].update(range(s, s + n))
    return files

def main(argv):
    if not argv: print(__doc__); return 2
    repo = os.path.abspath(argv[0]); records = load_ledger(repo); signers = allowed_signers(repo)
    if not signers:
        print("warning: no allowed_signers file — every record will count as unverified")
    tot = un = 0
    if "--diff" in argv:
        ref = next((a for a in argv[1:] if not a.startswith("--")), "HEAD")
        for rel, added in diff_added(repo, ref).items():
            if os.path.exists(os.path.join(repo, rel)):
                c, u = report_file(repo, rel, records, signers, sorted(added)); tot += c; un += u
    else:
        for f in argv[1:]:
            rel = os.path.relpath(os.path.abspath(f), repo)
            c, u = report_file(repo, rel, records, signers); tot += c; un += u
    if tot:
        print(f"TOTAL: {100 * (tot - un) / tot:.0f}% attested, {un} unattested line(s)")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
