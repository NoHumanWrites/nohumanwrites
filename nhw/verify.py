#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""NoHumanWrites — the verifier for the signed ledger.

  verify.py <repo> [<file>...] [--signers FILE] [--trust-repo-signers]
  verify.py <repo> --diff [<ref>] ...        attribute the lines a git diff adds (default: working tree vs HEAD)

Trust root: the allowed-signers file is YOURS — ~/.nhw/allowed_signers or
--signers FILE.  A repository's own .nhw/allowed_signers is ignored unless you
pass --trust-repo-signers, because a repository that chooses its own trust root
can attest anything it likes.

For each record: validate the schema, verify the signature (ssh-keygen -Y verify),
confirm the key that verified it is the key the record names, then check that the
signed hunk still matches text in the file.  A line is attested when it sits in a
verified, matching hunk; when a whole hunk no longer matches (a later edit, a
formatter) the signed per-line hashes cover surviving lines, each hash at most as
many times as it was signed.  Everything else is UNATTESTED: typed by hand, or
written through a channel with no hook.  Three states are reported: attested /
unattested / unverifiable (records present, none verifiable with your keys).
"""
from __future__ import annotations
import base64, collections, json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nhw.common import MIN_LEN, NAMESPACE, hunk_sha, line_key, norm_text, read_text, inside  # noqa: E402

MAX_SIG = 8192
MAX_RECORDS_PER_FILE = 10_000
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
LSHA_RE = re.compile(r"^[0-9a-f]{16}$")


def allowed_signers(repo: str, explicit: str | None = None, trust_repo: bool = False) -> tuple[str | None, str]:
    """→ (path, description).  User-owned first; repo-local only on explicit opt-in."""
    if explicit:
        return (explicit if os.path.exists(explicit) else None), f"--signers {explicit}"
    user = os.path.expanduser("~/.nhw/allowed_signers")
    if os.path.exists(user):
        return user, "~/.nhw/allowed_signers"
    if trust_repo:
        p = os.path.join(repo, ".nhw", "allowed_signers")
        if os.path.exists(p):
            return p, "REPOSITORY-SUPPLIED .nhw/allowed_signers (trusted because you asked; the repo picked this key)"
    return None, "none"


def valid_record(r) -> bool:
    try:
        h = r["hunk"]
        return (r.get("v") == 1 and isinstance(r.get("path"), str) and 0 < len(r["path"]) < 4096
                and isinstance(h.get("lines"), int) and 0 < h["lines"] <= 100_000
                and isinstance(h.get("sha256"), str) and SHA_RE.match(h["sha256"]) is not None
                and isinstance(h.get("line_sha", []), list) and all(isinstance(x, str) and LSHA_RE.match(x) for x in h.get("line_sha", []))
                and isinstance(r.get("sig"), str) and 0 < len(r["sig"]) <= MAX_SIG
                and isinstance(r.get("signer"), str))
    except (KeyError, TypeError, AttributeError):
        return False


def fingerprints(signers: str) -> dict[str, str]:
    """Map fingerprint → key line for every key in an allowed_signers file."""
    out = {}
    for ln in open(signers, encoding="utf-8", errors="replace"):
        parts = ln.split()
        if len(parts) < 3:
            continue
        keyline = " ".join(parts[-2:])
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pub") as f:
            f.write(keyline + "\n"); p = f.name
        try:
            fp = subprocess.run(["ssh-keygen", "-lf", p], capture_output=True, text=True, timeout=10).stdout
            m = re.search(r"(SHA256:\S+)", fp)
            if m:
                out[m.group(1)] = ln.strip()
        finally:
            os.unlink(p)
    return out


def sig_ok(rec: dict, signers: str | None, fps: dict[str, str]) -> bool:
    if not signers:
        return False
    claimed = rec["signer"].split(":", 1)[-1] if ":" in rec["signer"] else rec["signer"]
    if claimed not in fps:                              # the named key is not one you trust
        return False
    body = {k: v for k, v in rec.items() if k != "sig"}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    try:
        armored = base64.b64decode(rec["sig"], validate=True)
    except Exception:
        return False
    # verify against ONLY the claimed key, so the signer field is bound to the verifying key
    with tempfile.NamedTemporaryFile("w", delete=False) as one:
        one.write(fps[claimed] + "\n"); onep = one.name
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".sig") as s:
        s.write(armored); sp = s.name
    try:
        r = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", onep, "-I", "nhw", "-n", NAMESPACE, "-s", sp],
                           input=payload, capture_output=True, timeout=20)
        return r.returncode == 0
    finally:
        os.unlink(sp); os.unlink(onep)


def load_ledger(repo: str) -> tuple[list, int]:
    """→ (valid records, malformed count)."""
    p = os.path.join(repo, ".nhw", "attest.jsonl")
    if not os.path.exists(p):
        return [], 0
    out, bad = [], 0
    with open(p, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            try:
                r = json.loads(ln)
            except Exception:
                bad += 1; continue
            if valid_record(r):
                out.append(r)
            else:
                bad += 1
    return out, bad


def attested_lines(repo: str, rel: str, records, signers, fps):
    """→ (covered line numbers, verified count, stale count, unverified count) for <rel>."""
    path = os.path.join(repo, rel)
    body = read_text(path) if inside(repo, path) else None
    if body is None:
        return set(), 0, 0, 0
    lines = norm_text(body).split("\n")
    covered, verified, stale, unverified = set(), 0, 0, 0
    mine = [r for r in records if r["path"] == rel][-MAX_RECORDS_PER_FILE:]
    for r in reversed(mine):                            # newest first
        if not sig_ok(r, signers, fps):
            unverified += 1; continue
        verified += 1
        n, want = r["hunk"]["lines"], r["hunk"]["sha256"]
        hit = False
        if n <= len(lines):
            for i in range(0, len(lines) - n + 1):     # slide: hunks move when lines are inserted above
                if hunk_sha("\n".join(lines[i:i + n])) == want:
                    covered.update(range(i + 1, i + n + 1)); hit = True; break
        if hit:
            continue
        stale += 1
        budget = collections.Counter(r["hunk"].get("line_sha") or [])   # each signed hash covers at most as many lines as were signed
        for i, l in enumerate(lines, 1):
            k = line_key(l)
            if k and budget.get(k, 0) > 0 and i not in covered:
                covered.add(i); budget[k] -= 1
    return covered, verified, stale, unverified


def report_file(repo, rel, records, signers, fps, added=None):
    covered, verified, stale, unverified = attested_lines(repo, rel, records, signers, fps)
    body = read_text(os.path.join(repo, rel))
    if body is None:
        print(f"{rel}: not UTF-8 text, skipped"); return 0, 0, "skipped"
    lines = norm_text(body).split("\n")
    consider = [i for i in (added or range(1, len(lines) + 1)) if i <= len(lines) and len(lines[i - 1].strip()) >= MIN_LEN]
    if not consider:
        print(f"{rel}: n/a (no lines of {MIN_LEN}+ characters)"); return 0, 0, "n/a"
    if verified == 0 and unverified > 0:
        print(f"{rel}: UNVERIFIABLE — {unverified} record(s) present, none verifiable with your keys; no score")
        return len(consider), len(consider), "unverifiable"
    un = [i for i in consider if i not in covered]
    pct = 100 * (len(consider) - len(un)) / len(consider)
    print(f"{rel}: {pct:.0f}% attested ({len(consider) - len(un)}/{len(consider)} lines), "
          f"{verified} verified record(s), {stale} stale, {unverified} unverified, unattested: {un[:20]}{'…' if len(un) > 20 else ''}")
    return len(consider), len(un), "scored"


def diff_added(repo, ref):
    cmd = ["git", "-c", "core.quotePath=false", "-c", "diff.external=", "-c", "core.fsmonitor=false",
           "diff", "--no-ext-diff", "--no-color", "--diff-filter=AM", "-U0", ref, "--", "."]
    out = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    files, cur = {}, None
    for ln in out.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:]; files.setdefault(cur, set())
        elif ln.startswith("+++ /dev/null"):
            cur = None
        elif ln.startswith("@@") and cur:
            m = re.search(r"\+(\d+)(?:,(\d+))?", ln)
            s, n = int(m.group(1)), int(m.group(2) or 1)
            files[cur].update(range(s, s + n))
    return files


def main(argv):
    if not argv:
        print(__doc__); return 2
    flags = [a for a in argv if a.startswith("--")]
    explicit = argv[argv.index("--signers") + 1] if "--signers" in argv else None
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and not (i > 0 and argv[i - 1] == "--signers")]
    repo = os.path.realpath(pos[0])
    records, malformed = load_ledger(repo)
    signers, src = allowed_signers(repo, explicit, "--trust-repo-signers" in flags)
    fps = fingerprints(signers) if signers else {}
    print(f"trust root: {src} ({len(fps)} key(s)); ledger: {len(records)} valid record(s), {malformed} malformed")
    if not signers:
        print("warning: no allowed_signers — every record counts as unverified; run setup-key.sh or pass --signers")
    tot = un = 0; states = collections.Counter()
    if "--diff" in flags:
        ref = pos[1] if len(pos) > 1 else "HEAD"
        for rel, added in diff_added(repo, ref).items():
            if os.path.exists(os.path.join(repo, rel)):
                c, u, st = report_file(repo, rel, records, signers, fps, sorted(added)); tot += c; un += u; states[st] += 1
    else:
        for f in pos[1:]:
            rel = os.path.relpath(os.path.realpath(f), repo)
            c, u, st = report_file(repo, rel, records, signers, fps); tot += c; un += u; states[st] += 1
    if states["scored"] and tot:
        print(f"TOTAL: {100 * (tot - un) / tot:.0f}% attested, {un} unattested line(s)"
              + (f", {states['unverifiable']} file(s) unverifiable" if states["unverifiable"] else ""))
    elif states["unverifiable"]:
        print("TOTAL: unverifiable — records exist but none verify with your keys; no percentage is given")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
