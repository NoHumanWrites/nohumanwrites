# Council — external voices (build) · 8 members

TASK: Hostile senior code review before public release (Apache-2.0, GitHub) of NoHumanWrites: a provenance ledger for agent-written code. Context: a Claude Code PostToolUse hook (nhw/hook.py) signs each agent Write/Edit into <repo>/.nhw/attest.jsonl with a dedicated ssh-ed25519 key via 'ssh-keygen -Y sign'; nhw/verify.py verifies signatures against allowed_signers and matches hunks (and per-line hashes) to the current file; nohumanwrites.py is the public single-file CLI (check/setup/badge); nhw/attest.py reconstructs provenance from Claude Code transcripts; setup-key.sh creates the key. Review for: (1) correctness bugs and edge cases (paths, encodings, CRLF, empty files, huge files, concurrent hook runs, JSON canonicalisation and signature stability, the sliding-window hunk match, the per-line fallback, git-diff parsing); (2) security: signature model, canonical JSON, key handling, temp files, allowed_signers trust, tampering, injection via file paths or hook stdin, what a malicious repo could do to a verifier; (3) false attestation: ways a line could be counted attested that a human actually typed, and vice versa; (4) portability: macOS/Linux, Python 3.9+, OpenSSH versions (ssh-keygen -Y needs 8.0+), missing tools; (5) UX honesty: does the output ever imply 'human' when it only knows 'unattested'; (6) what a maintainer would want before v0.1 tag (tests, CI, licence header, packaging). Give concrete patches or exact line-level fixes, ranked by severity. End with a one-line verdict: tag v0.1 as is / after fixes / not yet.

===== FILE: SPEC.md =====
# NoHumanWrites ledger — proposed format v0.1

File: `.nhw/attest.jsonl` at the repository root. One JSON object per line, append-only. Committed with the code, or pushed to the verifier; either works.

```json
{"v":1,
 "ts":"2026-09-04T14:02:11Z",
 "path":"src/router.py",
 "hunk":{"start":120,"end":148,"lines":29,"sha256":"<sha256 of the normalised hunk text>",
         "line_sha":["<first 16 hex of sha256 of each stripped line ≥ 12 chars>", "..."]},
 "producer":{"kind":"agent","harness":"claude-code","model":"claude-fable-5-1","session":"c76f7980-…"},
 "signer":"ed25519:<public key fingerprint>",
 "sig":"<base64 signature over the canonical JSON of every field above>"}
```

Rules.

1. A record asserts only that a machine produced the hunk. Absence of a record asserts nothing about who did.
2. The signing key belongs to the developer's machine, one per harness install. The verifier holds the public keys, as with SSH.
3. Hunk text is normalised before hashing: trailing whitespace stripped, line endings unified, tabs preserved. Formatters that change more than whitespace produce a new hunk and a new record; that is intended.
4. The verifier, for a pull request: for each added or modified line, find the most recent record whose hunk covers it and whose signature verifies; report covered bytes over changed bytes and list the uncovered ranges. When a whole hunk no longer matches (a later edit, a formatter), the signed `line_sha` list still covers the individual lines that survived unchanged; lines that were reflowed are reported uncovered, which is intended.
5. Prose profile: same schema, `hunk` becomes `{"paragraph": n, "sha256": …}` over the normalised paragraph.
6. A record never carries a human identity beyond the machine key. Reviewers see "unattested", not a name.

Harness adapters emit one record per write. For Claude Code that is a `PostToolUse` hook matching `Write|Edit`; the tool input already contains the exact text.

===== FILE: nohumanwrites.py =====
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

===== FILE: nhw/hook.py =====
#!/usr/bin/env python3
"""NoHumanWrites — layer 1 in production: the signing hook.

Claude Code PostToolUse hook for Write / Edit.  Reads the hook event on stdin,
hashes the text the agent just wrote, signs a canonical record with the
developer's SSH ed25519 key (ssh-keygen -Y sign, namespace "nhw"), and appends
it to <repo>/.nhw/attest.jsonl — the ledger described in SPEC.md.

Standard library + OpenSSH only.  Never blocks the agent: any failure is logged
to ~/.nhw/hook.log and exits 0.

Install (settings.json → hooks.PostToolUse):
  {"matcher": "Write|Edit",
   "hooks": [{"type": "command", "command": "python3 ~/nohumanwrites/nhw/hook.py"}]}
"""
import hashlib, json, os, re, subprocess, sys, tempfile, datetime

# A dedicated signing key, never the developer's SSH login key: `setup-key.sh` makes it.
KEY = os.path.expanduser(os.environ.get("NHW_KEY", "~/.nhw/id_nhw"))
NAMESPACE = "nhw"
LOG = os.path.expanduser("~/.nhw/hook.log")

def norm(text: str) -> str:
    return "\n".join(l.rstrip() for l in text.replace("\r\n", "\n").split("\n")).strip("\n")

def repo_root(path: str) -> str | None:
    d = os.path.dirname(os.path.abspath(path))
    while d and d != "/":
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None

def line_span(path: str, text: str):
    """Find where the written text now sits in the file (1-based, inclusive)."""
    try:
        body = open(path, errors="replace").read()
    except Exception:
        return None
    i = body.find(text.strip("\n"))
    if i < 0:
        return None
    start = body.count("\n", 0, i) + 1
    return start, start + text.strip("\n").count("\n")

def sign(payload: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(payload); p = f.name
    try:
        subprocess.run(["ssh-keygen", "-Y", "sign", "-f", KEY, "-n", NAMESPACE, "-q", p],
                       check=True, capture_output=True)
        return open(p + ".sig").read()
    finally:
        for x in (p, p + ".sig"):
            try: os.unlink(x)
            except OSError: pass

def fingerprint() -> str:
    out = subprocess.run(["ssh-keygen", "-lf", KEY + ".pub"], capture_output=True, text=True).stdout
    m = re.search(r"(SHA256:\S+)", out)
    return m.group(1) if m else "unknown"

def main():
    if not os.path.exists(KEY):          # not set up on this machine: stay silent
        return
    ev = json.load(sys.stdin)
    if ev.get("tool_name") not in ("Write", "Edit"):
        return
    inp = ev.get("tool_input", {})
    path = inp.get("file_path")
    text = inp.get("content") if ev["tool_name"] == "Write" else inp.get("new_string")
    if not path or not text:
        return
    root = repo_root(path)
    if not root:                       # only repositories carry a ledger
        return
    hunk_text = norm(text)
    span = line_span(path, text)
    rec = {
        "v": 1,
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "path": os.path.relpath(path, root),
        "hunk": {"start": span[0] if span else None, "end": span[1] if span else None,
                 "lines": hunk_text.count("\n") + 1,
                 "sha256": hashlib.sha256(hunk_text.encode()).hexdigest(),
                 # per-line hashes let the verifier keep covering lines after a later edit
                 # or formatter breaks the whole-hunk match (short lines carry no authorship)
                 "line_sha": [hashlib.sha256(l.strip().encode()).hexdigest()[:16]
                              for l in hunk_text.split("\n") if len(l.strip()) >= 12]},
        "producer": {"kind": "agent", "harness": "claude-code", "tool": ev["tool_name"],
                     "session": ev.get("session_id")},
        "signer": "ssh-ed25519:" + fingerprint(),
    }
    canonical = json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()
    rec["sig"] = sign(canonical)
    os.makedirs(os.path.join(root, ".nhw"), exist_ok=True)
    with open(os.path.join(root, ".nhw", "attest.jsonl"), "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never block the agent
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} {type(e).__name__}: {e}\n")
    sys.exit(0)

===== FILE: nhw/verify.py =====
#!/usr/bin/env python3
"""NoHumanWrites — the verifier for the signed ledger.

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
            # whole hunk moved or was edited: fall back to the signed per-line hashes
            want_lines = set(r["hunk"].get("line_sha") or [])
            if want_lines:
                for i, l in enumerate(lines, 1):
                    if len(l.strip()) >= 12 and hashlib.sha256(l.strip().encode()).hexdigest()[:16] in want_lines:
                        covered.add(i)
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

===== FILE: nhw/attest.py =====
#!/usr/bin/env python3
"""NoHumanWrites — layer 1: provenance by construction.

Every byte an agent writes through Claude Code passes through a logged tool
call (Write / Edit).  Those logs live in ~/.claude/projects/**/*.jsonl.  This
module indexes them into an "attested line set" and then attributes any file on
disk line by line: a line is AI-attested if an agent produced it, otherwise it
is unattested (human-typed, or produced outside the logged harness).

No statistics, no model, no key.  Exact match on normalised line content.
"""
import hashlib, json, os, sys, glob, re
from collections import defaultdict

LOGDIR = os.path.expanduser("~/.claude/projects")
CACHE = os.path.expanduser("~/nohumanwrites/eval/attested-index.json")

def norm(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())

def h(line: str) -> str:
    return hashlib.sha1(norm(line).encode()).hexdigest()[:16]

def index_transcripts(logdir=LOGDIR):
    """Return {file_path: set(line_hash)}, plus a global set and stats."""
    per_file = defaultdict(set)
    stats = {"files": 0, "records": 0, "write": 0, "edit": 0, "lines": 0}
    for path in glob.glob(os.path.join(logdir, "*", "*.jsonl")):
        stats["files"] += 1
        with open(path, errors="replace") as fh:
            for raw in fh:
                try:
                    d = json.loads(raw)
                except Exception:
                    continue
                if d.get("type") != "assistant":
                    continue
                content = d.get("message", {}).get("content")
                if not isinstance(content, list):
                    continue
                for b in content:
                    if b.get("type") != "tool_use":
                        continue
                    name, inp = b.get("name"), b.get("input", {})
                    if name == "Write":
                        text = inp.get("content", "")
                        stats["write"] += 1
                    elif name == "Edit":
                        text = inp.get("new_string", "")
                        stats["edit"] += 1
                    else:
                        continue
                    stats["records"] += 1
                    fp = inp.get("file_path", "")
                    for ln in text.splitlines():
                        if norm(ln):
                            per_file[fp].add(h(ln)); stats["lines"] += 1
    return per_file, stats

def load_index(rebuild=False):
    if not rebuild and os.path.exists(CACHE):
        d = json.load(open(CACHE))
        return {k: set(v) for k, v in d["per_file"].items()}, d["stats"]
    per_file, stats = index_transcripts()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump({"per_file": {k: sorted(v) for k, v in per_file.items()},
               "stats": stats}, open(CACHE, "w"))
    return per_file, stats

def attribute(path, per_file, min_len=12):
    """Line-level attribution of one file.

    A line counts as attested if its hash appears among lines the agent wrote
    to THAT path (strong) or to any path (weak — copied/moved content).  Very
    short lines (braces, blanks, 'fi') are ignored: they carry no authorship.
    """
    path = os.path.abspath(path)
    strong = per_file.get(path, set())
    weak = set().union(*per_file.values()) if per_file else set()
    out = {"path": path, "considered": 0, "strong": 0, "weak": 0,
           "unattested": [], "lines": 0}
    try:
        lines = open(path, errors="replace").read().splitlines()
    except Exception as e:
        out["error"] = str(e); return out
    out["lines"] = len(lines)
    for i, ln in enumerate(lines, 1):
        n = norm(ln)
        if len(n) < min_len:
            continue
        out["considered"] += 1
        k = h(ln)
        if k in strong:
            out["strong"] += 1
        elif k in weak:
            out["weak"] += 1
        else:
            out["unattested"].append((i, ln[:120]))
    c = out["considered"] or 1
    out["attested_ratio"] = round((out["strong"] + out["weak"]) / c, 4)
    out["human_or_untracked_ratio"] = round(len(out["unattested"]) / c, 4)
    return out

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rebuild = "--rebuild" in sys.argv
    per_file, stats = load_index(rebuild)
    if "--stats" in sys.argv or not args:
        print(json.dumps(stats, indent=1)); sys.exit(0)
    for a in args:
        r = attribute(a, per_file)
        print(f"{r['path']}\n  lines={r['lines']} considered={r['considered']} "
              f"attested={r['strong']+r['weak']} ({r['attested_ratio']:.0%}) "
              f"unattested={len(r['unattested'])} ({r['human_or_untracked_ratio']:.0%})")
        if "--show" in sys.argv:
            for i, ln in r["unattested"][:40]:
                print(f"    {i:>5}: {ln}")

===== FILE: setup-key.sh =====
#!/usr/bin/env bash
# NoHumanWrites — one-time setup on a developer machine.
# Makes a DEDICATED ed25519 signing key (not your SSH login key), registers it as an
# allowed signer, and runs a smoke test of the hook + verifier.  Re-runnable.
set -euo pipefail
NHW_DIR="$HOME/.nhw"; KEY="$NHW_DIR/id_nhw"; HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$NHW_DIR"
if [ ! -f "$KEY" ]; then
  ssh-keygen -q -t ed25519 -N "" -C "nhw-$(hostname -s)" -f "$KEY"
  echo "signing key created: $KEY"
else
  echo "signing key present: $KEY"
fi
printf 'nhw namespaces="nhw" %s\n' "$(cut -d' ' -f1-2 "$KEY.pub")" > "$NHW_DIR/allowed_signers"
echo "allowed signers: $NHW_DIR/allowed_signers"
# smoke test inside this repository
T="$HERE/eval/hooktest.txt"
printf '# hook smoke test\nline one of the attested block\nline two of the attested block\n' > "$T"
python3 - "$T" <<'EOF' | python3 "$HERE/nhw/hook.py"
import json, sys
p = sys.argv[1]
print(json.dumps({"session_id": "smoke", "tool_name": "Write",
                  "tool_input": {"file_path": p, "content": open(p).read()}}))
EOF
echo "--- agent-written file:"; python3 "$HERE/nhw/verify.py" "$HERE" "$T"
printf 'a line a human typed after the agent finished\n' >> "$T"
echo "--- after a human appends one line:"; python3 "$HERE/nhw/verify.py" "$HERE" "$T"
echo "done — the hook will now sign every Write/Edit Claude Code makes inside a git repository."

## Round 1 — independent answers

### A. openai/gpt-5.6-luna-pro
# Hostile release review

## Verdict summary

The core idea is useful as a **positive evidence ledger**, but the current implementation overstates what it can prove and has several correctness and trust-boundary failures. In particular:

1. A repository can currently supply its own `allowed_signers`, making signatures self-authorizing.
2. Verification does not bind the declared `signer` fingerprint to the key that actually verified the signature.
3. The verifier does not implement “most recent matching record”.
4. The line-hash fallback can attribute human-written duplicate/copy-pasted lines as agent-written.
5. The code does not support Python 3.9 despite claiming to.
6. Malformed or hostile repository data can crash or DoS the verifier.
7. Hook failures are silently converted into an apparently valid “unattested” result.
8. Transcript attribution is not provenance: it can count copied or human-written lines as agent-written.

---

# P0 — Must fix before release

## 1. Repository-controlled `allowed_signers` defeats the signature trust model

### Current code

```python
def allowed_signers(repo: str) -> str | None:
    for p in (os.path.join(repo, ".nhw", "allowed_signers"),
              os.path.expanduser("~/.nhw/allowed_signers")):
```

This makes `.nhw/allowed_signers` repository-controlled. A malicious repository can contain:

```text
nhw namespaces="nhw" ssh-ed25519 AAAA...attacker-key
```

It can then include attacker-signed records and have the verifier report them as verified.

This is not merely “the repository can tamper with its ledger”; it is the repository choosing the trust root.

### Fix

Do not trust a signer file from the repository by default.

Use one of these models:

- Explicit external trust configuration:
  ```text
  ~/.config/nohumanwrites/allowed_signers
  ```
- A command-line option:
  ```text
  nhw verify --allowed-signers /path/to/pinned-signers repo
  ```
- A repository file only when explicitly pinned by a user-owned configuration:
  ```text
  ~/.config/nohumanwrites/trusted-repos/<repo-id>
  ```

At minimum:

```python
def allowed_signers(repo: str, explicit: str | None = None) -> str | None:
    candidates = []
    if explicit:
        candidates.append(os.path.abspath(os.path.expanduser(explicit)))
    candidates.append(os.path.expanduser("~/.nhw/allowed_signers"))
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None
```

The output should clearly say:

```text
trust source: user-owned ~/.nhw/allowed_signers
```

Never call a repository-controlled key file “trusted” without a warning.

---

## 2. The `signer` field is not authenticated or checked

The record contains:

```python
"signer": "ssh-ed25519:" + fingerprint(),
```

But `sig_ok()` ignores it:

```python
body = {k: v for k, v in rec.items() if k != "sig"}
...
ssh-keygen -Y verify ...
```

The actual key that verified the signature is not compared with `rec["signer"]`. A record can claim any signer string and still verify using another allowed key.

This breaks the stated schema and makes audit output misleading.

### Fix

Do not treat a self-declared fingerprint as authoritative. Extract the signer identity from the verification operation or verify against each configured key individually.

A practical format is to make the allowed-signers file one key per identity and verify each candidate, then compare its calculated fingerprint:

```python
def public_key_fingerprint(pub_line: str) -> str:
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(pub_line + "\n")
        name = f.name
    try:
        p = subprocess.run(
            ["ssh-keygen", "-lf", name],
            check=True, capture_output=True, text=True
        )
        return parse_fingerprint(p.stdout)
    finally:
        os.unlink(name)
```

Better: make `signer` a stable configured key ID and bind that ID to a specific public key in external configuration. Do not accept arbitrary fingerprint text from the signed payload as an identity assertion.

Also fix the prefix inconsistency:

- SPEC says `ed25519:<fingerprint>`
- hook emits `ssh-ed25519:<fingerprint>`

Pick one format and validate it.

---

## 3. Verification does not implement “most recent record”

The specification says:

> find the most recent record whose hunk covers it

The implementation loops through all records and unions their coverage:

```python
for r in records:
    ...
    covered.update(...)
```

Consequences:

- An old agent record can continue to attest a line after a later human edit.
- An earlier record can cover a line that a later record replaced.
- An old matching hunk elsewhere can be used even when the latest record is stale.
- The result depends on all historical records, not the latest applicable record.

### Fix

Add a monotonically increasing ledger sequence number:

```json
{"seq": 42, ...}
```

Do not use timestamps for ordering. Timestamps can be equal, malformed, or moved across machines.

Then:

```python
records = sorted(records, key=lambda r: r["seq"], reverse=True)

for r in records:
    if not valid_record(r):
        continue
    if r["path"] != rel:
        continue
    if hunk_matches(...):
        return coverage_for(r)
```

If the intended semantics are union-of-surviving-lines, change the specification instead. Do not claim “most recent” while implementing union semantics.

---

## 4. The per-line fallback creates false attestation

Current fallback:

```python
want_lines = set(r["hunk"].get("line_sha") or [])
for i, l in enumerate(lines, 1):
    if len(l.strip()) >= 12 and hashlib.sha256(l.strip().encode()).hexdigest()[:16] in want_lines:
        covered.add(i)
```

This can attest a human-written line if it is identical to a line previously produced by an agent. Examples:

- A human types the same common declaration.
- A human copies a line from documentation.
- A duplicated line appears twice, but only one occurrence was agent-written.
- A human retypes a line after deleting the agent’s version.

Truncated 64-bit hashes also introduce avoidable collision risk.

The transcript implementation is even weaker: it uses SHA-1 truncated to 64 bits and explicitly searches all files:

```python
weak = set().union(*per_file.values())
```

That means a line written by an agent in one file can attest a human-written identical line in another file.

### Fix

For signed verification:

- Use full SHA-256.
- Include file identity, line ordinal, and preferably a surrounding context hash.
- Do not use a global “same content anywhere” fallback.
- If content moves, report it as “content match” rather than “attested current line”.
- Treat ambiguous duplicate matches as uncovered.

For example:

```json
"line_sha256": [
  {
    "ordinal": 3,
    "sha256": "...",
    "context_before": "...",
    "context_after": "..."
  }
]
```

Or simpler: remove the fallback for v0.1. A conservative false-negative is preferable to a false-positive provenance claim.

For transcripts, remove weak attribution entirely:

```python
if k in strong:
    ...
else:
    out["unattested"].append(...)
```

If weak matches remain, label them explicitly:

```text
content seen in an agent transcript; not proven to have been written here
```

Never include them in the main attested percentage.

---

## 5. The signing key is not a secure provenance boundary

The private key is:

```text
~/.nhw/id_nhw
```

Any process able to run as the user can use it. Claude Code tools may include shell execution, so an agent or malicious project can potentially read or invoke the key unless the operational environment prevents it.

Also, the hook itself is a user-controlled Python process. A malicious repository cannot directly change the installed hook unless the user runs repository-local code, but a malicious agent can invoke arbitrary commands if its harness permits that.

The system proves:

> this key signed this payload

It does not prove:

> the intended Claude Code process generated this payload

### Required documentation and UX fix

The README and output must explicitly state:

```text
The key authenticates this machine/user installation, not a hardware-backed
agent identity. Any process able to use ~/.nhw/id_nhw can create attestations.
```

For stronger deployments:

- Use a passphrase-protected key plus an agent or signing broker.
- Restrict signing to a small local daemon.
- Use hardware-backed keys where available.
- Record a hook installation ID and version.
- Consider a separate signing helper with a narrow API rather than exposing the private key to arbitrary subprocesses.

Do not market this as tamper-proof or complete provenance.

---

## 6. Hook failures are silently converted into an apparently valid result

The hook catches everything:

```python
except Exception as e:
    ...
sys.exit(0)
```

This means all of these silently pass:

- malformed stdin
- missing `ssh-keygen`
- unsupported OpenSSH
- failed signature
- permission denied
- ledger write failure
- encoding errors
- path resolution failure
- concurrent corruption

The user then receives a lower attestation score without knowing that the hook is broken.

The docstring says “never blocks the agent”, which is reasonable, but silent failure is not acceptable for provenance tooling.

### Fix

Keep exit code zero if Claude Code requires it, but make failure observable:

- Log structured failure records.
- Add a health command:
  ```text
  nohumanwrites doctor
  ```
- Have setup install a periodic or startup check.
- Emit a clear warning when the verifier sees hook failures.
- Record a local failure counter.

For example:

```text
NoHumanWrites: hook health unknown
  7 hook failures recorded since 2026-09-04
  run: nohumanwrites doctor
```

Do not say “every considered line carries machine provenance” if the hook has known signing failures.

---

# P1 — Serious correctness bugs

## 7. Python 3.9 support is false

The code uses:

```python
def repo_root(path: str) -> str | None:
```

The `X | Y` union syntax requires Python 3.10. Python 3.9 will fail at import time unless postponed annotations are enabled, which they are not.

### Fix

Either require Python 3.10+, or replace all such annotations:

```python
from typing import Optional

def repo_root(path: str) -> Optional[str]:
```

Given the stated requirement, use `Optional[...]` throughout and test under 3.9.

---

## 8. Path traversal and path identity are unsafe

The hook writes:

```python
"path": os.path.relpath(path, root)
```

The verifier later does:

```python
path = os.path.join(repo, rel)
```

There is no validation that `rel` remains inside `repo`. A malicious ledger can use:

```text
"path": "../../some/other/file"
```

The verifier can read and score files outside the repository.

Symlinks create a similar problem. A path inside the repo can resolve to an external file.

### Fix

Canonicalize and validate all paths:

```python
def repo_relative(root: str, path: str) -> str:
    root_real = os.path.realpath(root)
    path_real = os.path.realpath(path)
    try:
        rel = os.path.relpath(path_real, root_real)
    except ValueError:
        raise ValueError("path is on a different filesystem")
    if rel == os.pardir or rel.startswith(os.pardir + os.sep):
        raise ValueError("path escapes repository")
    return rel.replace(os.sep, "/")
```

At verification time, reject:

- absolute paths
- paths containing `..`
- paths that resolve outside the repository
- symlinked files unless explicitly supported

Use POSIX-style relative paths in the ledger regardless of host OS.

---

## 9. Encoding and CRLF handling are inconsistent

The code repeatedly uses locale-default text decoding with replacement:

```python
open(path, errors="replace").read()
```

This is not a stable hashing or provenance format.

Problems:

- UTF-8 files can be decoded differently under different locales.
- Invalid bytes become `�`, changing content.
- CRLF is normalized in some places by Python universal-newline mode and in other places manually.
- `line_span()` searches raw `text` in a text-decoded file. A CRLF input can fail to locate the hunk.
- `norm()` strips leading/trailing blank lines from the entire hunk, changing line counts and boundaries.

### Fix

Specify UTF-8 explicitly for JSON and source text, and decide how arbitrary bytes are handled.

For text files:

```python
open(path, "r", encoding="utf-8", newline="")
```

Normalize explicitly:

```python
def norm(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    return "\n".join(line.rstrip(" \t") for line in lines)
```

Do not call `.strip("\n")` on the entire hunk if line positions matter. Preserve the exact number of lines. Hash a clearly specified normalized representation, including whether the final newline exists.

For non-UTF-8 text, either:

- mark the file unsupported, or
- hash bytes and define byte-based line handling.

Do not silently use replacement characters.

---

## 10. `line_span()` is ambiguous and can attach an edit to the wrong occurrence

```python
i = body.find(text.strip("\n"))
```

If identical text occurs multiple times, the first occurrence is selected, regardless of where the `Edit` actually applied.

For Edit operations, the hook input includes `old_string`; use it to locate the exact replacement context. For Write, verify that the file content after the tool call matches the requested content or record the write as an unlocated event.

### Fix

For Edit:

1. Read `old_string`.
2. Locate exactly one occurrence before/after the operation if possible.
3. Use the tool result or current file to determine the replacement range.
4. Reject ambiguous matches.

If there are multiple matches:

```text
cannot determine edit location; record emitted without line span
```

Do not guess.

---

## 11. Hook signs text that may not have been written

The hook uses tool input:

```python
text = inp.get("content") if ev["tool_name"] == "Write" else inp.get("new_string")
```

It does not inspect whether:

- the tool succeeded,
- the file was actually written,
- a formatter or permission error changed the result,
- another process overwrote it before the hook ran.

The specification says the hook signs “what the agent wrote”, but implementation signs “what the tool input requested”.

### Fix

Consume the PostToolUse result and require a successful tool status. Then read the resulting file and record:

- requested content hash
- resulting content hash
- whether the exact requested hunk was found

If the result is unavailable, label the event:

```text
requested_by_agent
```

not:

```text
agent_wrote
```

---

## 12. Empty writes and deletions are silently ignored

```python
if not path or not text:
    return
```

This skips:

- an empty file write
- replacing content with an empty string
- deletion edits
- edits where `new_string == ""`

That may be acceptable for line coverage, but it is not documented and makes the ledger incomplete.

### Fix

Record zero-line operations with an explicit event type:

```json
"operation": "delete",
"hunk": {"start": 10, "lines": 0, "sha256": "..."}
```

Or explicitly state that v0.1 does not attest deletions and ensure the UI does not imply complete write provenance.

---

## 13. Ledger append is not safe under concurrent hook execution

Current code:

```python
with open(os.path.join(root, ".nhw", "attest.jsonl"), "a") as f:
    f.write(json.dumps(rec, sort_keys=True) + "\n")
```

Concurrent hooks can race. Depending on platform and write behavior, records can be interleaved or reordered. There is no sequence number, lock, fsync, or recovery strategy.

### Fix

Use:

- a per-ledger lock (`fcntl.flock` on Unix),
- a single encoded write,
- `flush()` and optionally `os.fsync()`,
- sequence allocation while holding the lock.

Example:

```python
line = (json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
with open(ledger, "ab", buffering=0) as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    f.write(line)
    os.fsync(f.fileno())
    fcntl.flock(f, fcntl.LOCK_UN)
```

If Windows support is intended, provide a platform abstraction. Otherwise document Unix-only behavior.

---

## 14. Ledger parsing silently ignores corruption

```python
for ln in open(p):
    try: out.append(json.loads(ln))
    except Exception: pass
```

A truncated or tampered ledger is treated as if the records never existed. This produces false “unattested” results with no warning.

### Fix

Track malformed lines:

```python
return records, {"malformed_lines": malformed, "truncated": ...}
```

Report:

```text
ledger warning: 3 malformed records ignored
```

For a signed append-only ledger, malformed records should generally make verification fail or at least produce a non-zero warning status.

---

## 15. Malformed records can crash verification

Examples:

```python
n = r["hunk"]["lines"]
want = r["hunk"]["sha256"]
```

```python
s.write(rec["sig"].encode())
```

A repository can commit arbitrary JSON. Missing fields, wrong types, huge integers, or huge strings can raise exceptions or consume excessive resources.

### Fix

Validate every record against a strict schema before verification:

- exact allowed keys
- integer bounds
- string length limits
- path constraints
- hash format
- signature size
- producer field types
- `hunk.lines` bounded, e.g. `0 <= lines <= 1_000_000`

Invalid records should be reported and skipped safely.

---

# P1 — Security and denial-of-service concerns

## 16. Verification has an avoidable O(records × files × lines) cost

For every record, the verifier:

1. launches `ssh-keygen`
2. scans the whole file with sliding windows
3. may scan the whole file again for line fallback

A hostile ledger can contain millions of records or gigantic hunks. A repository can cause the verifier to launch an enormous number of subprocesses.

### Fix

Before verification:

- impose ledger size and record count limits,
- index records by normalized path,
- verify signatures once and cache results,
- reject hunks above a configured size,
- hash candidate windows more efficiently,
- cap total verification work.

At minimum:

```text
maximum ledger size: 50 MiB
maximum records: 100,000
maximum hunk lines: 100,000
maximum file size: configured, not hard-coded silently
```

If limits are exceeded, fail closed with a clear warning.

---

## 17. Temporary-file handling needs stronger guarantees

`sign()` uses `NamedTemporaryFile(delete=False)` and then invokes `ssh-keygen` by path. The file is mode 0600 on normal Unix systems, which is good, but:

- the `.sig` file is created by `ssh-keygen`; permissions should be checked,
- temp files are not explicitly created in a private directory,
- verifier cleanup can fail,
- signature content is trusted without size limits.

Use a private temporary directory with mode 0700 and validate file size before reading.

Also handle `FileNotFoundError` for missing `ssh-keygen` and report it distinctly.

---

## 18. `allowed_signers` file handling is weak

`setup-key.sh` overwrites:

```bash
> "$NHW_DIR/allowed_signers"
```

Problems:

- no atomic replacement,
- no permissions check,
- follows symlinks,
- destroys manually added keys,
- no backup,
- `cut` assumes a normal public-key line,
- a compromised `$HOME` or symlink can redirect writes.

### Fix

In shell:

```bash
umask 077
mkdir -p -- "$NHW_DIR"
chmod 700 "$NHW_DIR"

tmp="$(mktemp "$NHW_DIR/allowed_signers.XXXXXX")"
chmod 600 "$tmp"
printf '%s\n' ... > "$tmp"
mv -f -- "$tmp" "$NHW_DIR/allowed_signers"
```

Refuse to operate if the target is a symlink.

Do not overwrite an existing trust file without confirmation or merging.

---

## 19. JSON canonicalization is underspecified

The implementation uses:

```python
json.dumps(..., sort_keys=True, separators=(",", ":")).encode()
```

This is deterministic for these Python objects, but the format does not define:

- UTF-8 explicitly
- escaping behavior
- numeric constraints
- duplicate-key handling
- Unicode normalization
- whether `ensure_ascii` is required
- whether `-0`, exponents, or non-finite numbers are permitted

Python accepts `NaN` and `Infinity` by default, which are not standard JSON.

### Fix

Define a canonical serialization profile:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")
```

Validate input with duplicate-key rejection and strict types. Better still, sign a canonical byte payload with an explicit envelope:

```text
nhw-v1\0<canonical-json>
```

This prevents cross-format ambiguity.

Add golden test vectors containing:

- Unicode
- escaped characters
- empty strings
- CRLF-normalized text
- nested objects
- missing optional fields

---

# P1 — Git and diff correctness

## 20. `git diff` parsing is not safe for arbitrary filenames

Current parser:

```python
if ln.startswith("+++ b/"):
    cur = ln[6:]
```

It does not correctly handle:

- tabs in filenames
- quotes
- escaped paths
- newlines in filenames
- renames
- `/dev/null`
- binary files
- filenames beginning with unusual characters

Also:

```python
subprocess.run(..., capture_output=True, text=True).stdout
```

ignores non-zero return codes and stderr. A failed `git diff` can result in an empty report.

### Fix

Use Git’s machine-readable format:

```bash
git diff --unified=0 --no-ext-diff --no-renames -z ...
```

Or use `--raw -z` plus a proper parser. At minimum:

```python
p = subprocess.run(..., check=False, ...)
if p.returncode not in (0, 1):
    raise RuntimeError(p.stderr)
```

Handle rename and deletion statuses explicitly.

Do not interpret `--diff` output as proof that a file is text. Git already has binary markers that should be honored.

---

## 21. `repo_root()` is Unix-specific

```python
while d and d != "/":
```

On Windows this is incorrect. It also does not recognize worktrees or some Git layouts robustly.

### Fix

Use:

```python
parent = os.path.dirname(d)
if parent == d:
    break
d = parent
```

Or invoke:

```bash
git -C path rev-parse --show-toplevel
```

and validate the command result.

---

## 22. Directory scanning has races and policy surprises

```python
os.path.getsize(...)
```

can fail after `os.walk()` returns the file. Symlinks can change between enumeration and open. Hidden files are excluded, including potentially relevant source files. The 2 MB limit is undocumented in output.

### Fix

Catch `OSError`, use `os.stat` carefully, and report skipped files. Make file selection explicit:

```text
skipped: 4 files over 2 MiB, 2 symlinks, 1 unreadable
```

Do not silently omit files from a percentage.

---

# P1 — False attestation and false negatives

## 23. Human content pasted into an agent tool call is counted as agent-written

This is inherent in the model. If a human pastes a block into a prompt and the agent sends it through `Write`, the ledger counts it as agent-produced.

That may be acceptable if the claim is exactly:

> the machine harness wrote this content

It is not acceptable if users interpret it as:

> the model authored this content

The output and specification should use “machine-channel attested”, not “agent-written”, unless the distinction is intentional and clearly documented.

---

## 24. Human edits that reproduce an old agent line are counted as agent-attested

This follows from both the hunk sliding window and per-line fallback. It is especially likely for boilerplate and repeated code.

The tool cannot distinguish:

```text
agent wrote line A
human deleted line A
human retyped identical line A
```

The implementation currently implies that it can.

### Fix

Document this as an explicit limitation and either remove line fallback or downgrade matches to:

```text
historical content match; authorship of this current occurrence is ambiguous
```

Do not count ambiguous matches in the headline percentage.

---

## 25. A formatter can cause large false negatives

The implementation hashes trailing-whitespace-normalized text, but:

- indentation changes are not normalized,
- line wrapping changes invalidate the hunk,
- line ending and encoding differences can invalidate it,
- leading/trailing blank line behavior changes line counts,
- an Edit may be recorded with the new string but the actual file may be reformatted.

This is conservative, but the output should explain why coverage disappeared:

```text
stale hunk: content changed after attestation
```

not simply “unattested”.

---

## 26. Transcript indexing does not verify successful writes

`attest.py` indexes assistant `tool_use` messages only. It does not check the corresponding tool result. It also caches the index indefinitely:

```python
if not rebuild and os.path.exists(CACHE):
```

A cached result can be stale after new writes, and a cache can be manually modified.

### Fix

- Parse tool results and require success.
- Store source file mtimes and sizes in the cache.
- Rebuild automatically when logs change.
- Label transcript data as local, unsigned, and unverified.
- Never use cached transcript data for a “signed” result.

---

# P2 — UX and semantic honesty

## 27. “Attested” still risks being read as “human vs AI”

The final line is:

```python
unattested = typed by hand, or written through a channel with no hook.
```

That is honest, but the headline:

```text
NoHumanWrites: 93% attested
```

can easily be interpreted as “93% AI-written” or “7% human-written”.

The badge is worse:

```text
NoHumanWrites-93%_attested
```

Badges are commonly consumed without the explanatory text.

### Fix

Use wording such as:

```text
93% machine-channel coverage
7% provenance unknown
```

Avoid “NoHumanWrites” as a positive score unless the project is intentionally making a provocative claim. The badge should say:

```text
provenance-93%-machine-channel
```

or include a tooltip/link explaining that unknown does not mean human.

Never say:

```text
every considered line carries machine provenance
```

unless signatures were actually verified and the trust root was external and valid.

---

## 28. `verified_signatures` is too coarse

```python
"verified_signatures": bool(signers)
```

This is true merely because a signer file exists, even if:

- all signatures fail,
- the signer file is repository-controlled,
- `ssh-keygen` is missing,
- records are malformed.

### Fix

Return counts:

```json
{
  "signatures": {
    "verified": 17,
    "invalid": 2,
    "unknown_signer": 3,
    "malformed": 1
  }
}
```

The headline must distinguish:

- no trust configuration
- trust configured but no valid records
- valid signed records
- unsigned transcript evidence

---

## 29. Evidence fallback behavior is surprising

If a ledger exists but has no valid signatures, `check_ledger()` still returns a ledger result, preventing fallback to transcripts:

```python
if not records:
    return None
```

A ledger with records but zero verifiable signatures is treated as selected evidence.

### Fix

Select evidence based on validity, not mere file presence:

```python
if not valid_signed_records:
    if transcripts_available:
        use transcripts
    else:
        report "ledger present but no valid signed records"
```

Do not silently substitute one provenance source for another.

---

# P2 — Portability

## 30. OpenSSH version handling is missing

The project depends on:

```text
ssh-keygen -Y sign
ssh-keygen -Y verify
```

These require sufficiently recent OpenSSH. Missing or old versions currently produce:

- hook failure silently logged
- verifier exception or crash

### Fix

Add a preflight:

```bash
ssh-keygen -Y sign -f /nonexistent -n nhw </dev/null
```

or parse `ssh -V`, and report:

```text
OpenSSH 8.0+ is required for signing; found ...
```

Do not claim “standard library + OpenSSH only” without checking the exact feature availability.

Test at least:

- macOS system OpenSSH
- Ubuntu/Debian OpenSSH
- Fedora/RHEL OpenSSH
- missing `ssh-keygen`
- old OpenSSH
- non-English locale
- Python 3.9 and current Python

The current shell scripts are Unix-oriented and should not imply Windows support.

---

# P2 — Setup and packaging

## 31. `cmd_setup()` rewrites settings non-atomically and can destroy data

```python
json.dump(s, open(settings, "w"), indent=2)
```

A crash can leave an empty or truncated settings file. File descriptors are not explicitly closed. Permissions and symlinks are not checked.

The hook command is constructed as:

```python
cmd = f"python3 \"{os.path.join(HERE, 'nhw', 'hook.py')}\""
```

A path containing a double quote breaks the generated shell command. The command also assumes `python3` is available in Claude Code’s execution environment.

### Fix

- Refuse symlinked settings files unless explicitly allowed.
- Write a temporary file in the same directory and `os.replace`.
- Preserve mode.
- Back up the original.
- Use `sys.executable` where appropriate.
- Properly shell-quote, or avoid shell interpretation if Claude Code supports argv-style hooks.

Also make the setup operation idempotent with respect to existing hook entries and preserve unrelated hook configuration.

---

## 32. The single-file CLI is not actually self-contained

`nohumanwrites.py` imports:

```python
from nhw import attest, verify
```

It therefore requires the adjacent package directory. That is fine for a repository checkout, but it is not a single-file CLI in the practical distribution sense.

The import also places `HERE` at the front of `sys.path`, which can cause surprising module shadowing.

### Fix

Either:

- package it properly and expose a console script, or
- genuinely vendor the implementation into the single file.

For public GitHub release, prefer a package:

```toml
[project.scripts]
nohumanwrites = "nohumanwrites.cli:main"
```

Support `python -m nohumanwrites`.

---

## 33. Missing license headers

The repository claims Apache-2.0, but the displayed source files have no Apache license header. A `LICENSE` file alone can be sufficient legally, but maintainers and downstream users will expect:

```text
Copyright ...
SPDX-License-Identifier: Apache-2.0
```

Add headers consistently, plus:

- `LICENSE`
- `NOTICE` if applicable
- contribution guidance
- dependency/license inventory
- release metadata

---

# Required tests before tagging

At minimum, add automated tests covering:

## Canonicalization

- Unicode
- UTF-8
- invalid UTF-8
- CRLF, LF, lone CR
- trailing spaces and tabs
- empty files
- final newline present/absent
- blank first/last lines
- duplicate JSON keys
- non-finite numbers
- signature golden vectors

## Paths

- spaces
- Unicode filenames
- symlinks
- `..`
- absolute paths
- repository root
- nested Git worktrees
- filenames containing tabs/newlines if supported
- files outside the repository

## Edits

- Write
- replacement with empty string
- insertion/deletion
- repeated `old_string`
- repeated new hunk
- edit after formatter
- edit with CRLF
- tool failure
- file changed between tool completion and hook execution

## Ledger

- concurrent append
- truncated final line
- malformed JSON
- invalid schema
- duplicate sequence number
- invalid signature
- wrong signer field
- unknown signer
- repository-controlled `allowed_signers`
- omitted historical records
- huge records and huge hunk counts

## Git

- added lines
- modified lines
- deleted files
- renames
- binary files
- quoted paths
- spaces/tabs
- failed Git command
- unusual refs

## Portability

- Python 3.9
- Python 3.10+
- macOS
- Linux
- missing `ssh-keygen`
- OpenSSH without `-Y`
- non-English locale

## Security

- malicious ledger
- malicious signer file
- path traversal
- symlink escape
- signature substitution
- copied line fallback
- stale transcript cache
- shell metacharacters in setup paths

---

# Recommended v0.1 scope reduction

For a safer first release, I would deliberately reduce the feature set:

1. External, user-owned allowed-signers only.
2. Full SHA-256 only.
3. No per-line fallback, or label it ambiguous and exclude it from the score.
4. Exact current-hunk matching only.
5. Strict UTF-8 and explicit newline rules.
6. Validated repository-relative POSIX paths.
7. Sequence numbers and locked append.
8. Strict record schema.
9. No transcript percentage in the headline; expose transcripts as unsigned experimental evidence.
10. Headline wording: “machine-channel coverage” and “provenance unknown”.
11. Python 3.9-compatible syntax or update the supported-version claim.
12. A `doctor` command and non-silent health reporting.

**Verdict: not yet.**

### B. google/gemini-3.1-pro-preview
This is a clever, lightweight approach to provenance. Relying on the agent’s tool-use stream rather than trying to reverse-engineer authorship from git history is the right architectural choice. 

However, there are two critical security flaws, a Python 3.9 parsing crash, and a major false-attestation bug in the fallback logic. 

Here is the review, ranked by severity.

### 1. Security: Repo-local Trust Root (Critical)
In `nhw/verify.py`, the verifier looks for `allowed_signers` inside the repository being checked:
```python
for p in (os.path.join(repo, ".nhw", "allowed_signers"), os.path.expanduser("~/.nhw/allowed_signers")):
```
**The flaw:** A malicious repository can simply commit its own `.nhw/allowed_signers` containing the attacker's public key, alongside a forged `.nhw/attest.jsonl`. Your verifier will silently trust it and report "100% verified AI-written code." This defeats the entire threat model. 
**The fix:** The verifier must *only* trust the user's global `~/.nhw/allowed_signers` (just like SSH relies on `~/.ssh/known_hosts`).

### 2. Portability: Python 3.9 SyntaxError (Critical)
In `nhw/hook.py` and `nhw/verify.py`, you use the union type operator:
```python
def repo_root(path: str) -> str | None:
```
**The flaw:** `str | None` was introduced in Python 3.10. On Python 3.9, this raises a `TypeError` at import time, completely breaking the tool.
**The fix:** Remove the `| None` return type hints, or use `typing.Optional`.

### 3. False Attestation: The Global Fallback Bug (High)
In `nhw/verify.py`, if a hunk match fails, you fall back to per-line hashes:
```python
for i, l in enumerate(lines, 1):
    if len(l.strip()) >= 12 and hashlib.sha256(l.strip().encode()).hexdigest()[:16] in want_lines:
        covered.add(i)
```
**The flaw:** `want_lines` is a `set`. If the agent writes a common line (e.g., `self.assertEqual(a, b)`), and the hunk match breaks, this loop will scan the *entire file* and falsely attest *every single instance* of that line, including ones written by humans years ago.
**The fix:** Use a `Counter` to ensure a hash can only attest as many lines as actually appeared in the agent's hunk.

### 4. Security: Temp File Symlink Race (High)
In `nhw/hook.py` and `nhw/verify.py`, you write payloads to a `NamedTemporaryFile`, but then rely on `ssh-keygen` to write to `p + ".sig"`:
```python
subprocess.run(["ssh-keygen", "-Y", "sign", "-f", KEY, "-n", NAMESPACE, "-q", p]...)
return open(p + ".sig").read()
```
**The flaw:** Because `p` is in `/tmp`, an attacker watching the filesystem can race to create `p + ".sig"` as a symlink to another file (e.g., `/etc/passwd`), potentially causing `ssh-keygen` to overwrite it or leak data.
**The fix:** Use `tempfile.TemporaryDirectory()` so both the payload and the signature are written inside a secure, `0700` directory.

### 5. Correctness: Missing Tool Crashes (Medium)
If `ssh-keygen` is not installed, `hook.py` safely catches the `FileNotFoundError` and doesn't block the agent. But `verify.py` will throw a traceback and crash.
**The fix:** Catch `FileNotFoundError` in `verify.py`'s `sig_ok` and return `False`, or exit gracefully.

### 6. Edge Cases & UX (Minor)
* **Git diff quoted paths:** If a file has spaces, `git diff` outputs `+++ "b/my file.py"`. Your parser `ln.startswith("+++ b/")` will miss it.
* **Empty files:** Handled correctly (division by zero is avoided via `res["lines"] or 1`).
* **CRLF:** Handled correctly (your `norm` and `.strip()` logic safely consumes `\r`).
* **UX Honesty:** Excellent. The tool clearly distinguishes between "unattested" and "human", and refuses to guess.

---

### Concrete Patches

Apply these fixes before tagging.

**Patch 1: Fix Trust Root & Python 3.9 (nhw/verify.py)**
```python
# Replace allowed_signers function:
def allowed_signers(repo: str):
    p = os.path.expanduser("~/.nhw/allowed_signers")
    return p if os.path.exists(p) else None

# Remove | None from sig_ok:
def sig_ok(rec: dict, signers: str) -> bool:
```

**Patch 2: Secure Temp Files & Missing Tools (nhw/hook.py & nhw/verify.py)**
```python
# In nhw/hook.py:
def sign(payload: bytes) -> str:
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "payload")
        with open(p, "wb") as f: f.write(payload)
        subprocess.run(["ssh-keygen", "-Y", "sign", "-f", KEY, "-n", NAMESPACE, "-q", p],
                       check=True, capture_output=True)
        with open(p + ".sig") as f: return f.read()

# In nhw/verify.py (sig_ok function):
    with tempfile.TemporaryDirectory() as d:
        sp = os.path.join(d, "sig")
        with open(sp, "w") as f: f.write(rec["sig"])
        try:
            r = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", signers, "-I", "nhw", "-n", NAMESPACE, "-s", sp],
                               input=payload, capture_output=True)
            return r.returncode == 0
        except FileNotFoundError:
            return False
```

**Patch 3: Fix Over-Attestation Fallback (nhw/verify.py)**
```python
            # Replace the want_lines block in attested_lines:
            want_lines = r["hunk"].get("line_sha") or []
            if want_lines:
                from collections import Counter
                avail = Counter(want_lines)
                for i, l in enumerate(lines, 1):
                    if i in covered or len(l.strip()) < 12: continue
                    h = hashlib.sha256(l.strip().encode()).hexdigest()[:16]
                    if avail[h] > 0:
                        covered.add(i)
                        avail[h] -= 1
```

**Patch 4: Fix Git Diff Quoted Paths (nhw/verify.py)**
```python
        # Replace the startswith("+++ b/") block in diff_added:
        if ln.startswith("+++ "):
            cur = ln[6:] if ln.startswith("+++ b/") else (ln[7:-1] if ln.startswith('+++ "b/') else ln[4:])
            files.setdefault(cur, set())
```

### Maintainer Checklist before v0.1
1. **Licensing:** Add `# SPDX-License-Identifier: Apache-2.0` to the top of all `.py` and `.sh` files.
2. **Testing:** You need at least one `pytest` file that mocks `ssh-keygen` and verifies the JSON canonicalisation and sliding-window logic.
3. **CI:** Add a basic `.github/workflows/test.yml` running on `ubuntu-latest` and `macos-latest`.

**Verdict:** Tag v0.1 after fixes.

### C. qwen/qwen3.8-max
(no answer from qwen/qwen3.8-max: 'NoneType' object has no attribute 'strip')

### D. moonshotai/kimi-k3
# Review: NoHumanWrites pre-v0.1

I went through all five files adversarially, as both a malicious repo author and a hostile CI environment. Ranked by severity. The short version: the crypto plumbing is fine; everything *around* it — the trust root, the honesty of the output, and the failure modes — is not ready.

---

## P0 — release-blocking

### 1. The trust root is circular, and the UI then lies about it

`verify.py`:

```python
def allowed_signers(repo: str) -> str | None:
    for p in (os.path.join(repo, ".nhw", "allowed_signers"), os.path.expanduser("~/.nhw/allowed_signers")):
```

The **repo's own** `allowed_signers` is preferred. A malicious repo ships `.nhw/allowed_signers` (attacker key) + `.nhw/attest.jsonl` (signed by it, backdated timestamps — `ts` is self-asserted). Verifier says: verified, 100% attested, green badge. The party being attested supplies the key that attests them. SPEC rule 2 says "the verifier holds the public keys" — the implementation does the opposite by default.

Compounding it, `nohumanwrites.py`:

```python
"verified_signatures": bool(signers),
```

That's "a keyring file *exists*", not "any signature verified". And the mirror-image failure: a reviewer clones a repo, has no keyring (or only their own key from `setup`), every signature fails, every line is "unattested", and the tool prints *"unattested = typed by hand… Review those first."* — asserting human authorship when it actually means "I could not check anything."

For a tool whose entire value is the meaning of its output, these two bugs are the product. Fix:

```python
def allowed_signers(repo):
    user = os.path.expanduser("~/.nhw/allowed_signers")
    if os.path.exists(user):
        return user, "user keyring"
    repo_file = os.path.join(repo, ".nhw", "allowed_signers")
    if os.path.exists(repo_file):
        return repo_file, "SELF-ASSERTED repo keyring (circular trust)"
    return None, None
```

- Plumb `verified/stale` counts (already computed, currently discarded in `check_ledger`) into the report. `verified_signatures` must be `verified_records > 0`, plus `"keyring": <source>`.
- Three-state output: **attested / unattested / unverifiable**. If records exist but none verified, print "ledger present, 0/N records verified against trusted keys — no verdict" and *do not* print a percentage or the "typed by hand" line.
- When the repo keyring was used, print the circular-trust warning on every human-readable report and include it in `--json`.

### 2. `str | None` crashes on Python 3.9, which you claim to support

`hook.py` (`def repo_root(path: str) -> str | None:`) and `verify.py` (twice). PEP 604 unions evaluate at def time; on 3.9 both files die at import. The hook then *silently never attests* (exit 0 by design). Fix in both files, first line after the docstring:

```python
from __future__ import annotations
```

And add 3.9 to CI so this class of bug is caught (see checklist).

### 3. Worktrees/submodules get no ledger, silently

Both `repo_root()` implementations test `os.path.isdir(os.path.join(d, ".git"))`. In git worktrees and submodules `.git` is a **file** (`gitdir: …`). The hook hits `if not root: return` — no record, no log, no sign. A whole class of repos silently produces zero attestation while everything looks installed.

```python
def repo_root(path):
    d = os.path.abspath(path if os.path.isdir(path) else os.path.dirname(path))
    while True:
        if os.path.exists(os.path.join(d, ".git")):  # dir or gitfile
            return d
        nd = os.path.dirname(d)
        if nd == d:
            return None
        d = nd
```

(This also fixes the repo-at-`/` edge the current loop misses.) Or call `git rev-parse --show-toplevel` — git is already a hard dependency for `--diff`.

### 4. Concurrent hook runs corrupt the ledger

Two Claude Code sessions (or parallel subagents) on the same repo → two hook processes appending. Whole-file `Write` records are large (see P1.8: a 5k-line file → ~100KB of `line_sha`), and Python's buffered writer flushes in chunks — multiple `write()` syscalls → **interleaved lines** → `load_ledger` silently `except: pass`es the mangled records. Permanent, silent attestation loss. Fix in `hook.py`:

```python
import fcntl
line = json.dumps(rec, sort_keys=True) + "\n"
with open(os.path.join(root, ".nhw", "attest.jsonl"), "a", encoding="utf-8") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    f.write(line)
    f.flush()
```

POSIX-only, which matches your stated platform support.

### 5. The verifier crashes on adversarial ledgers

`load_ledger` accepts any parseable JSON — including `42` or `"hello"` — then `attested_lines` does `r.get("path")`, `r["hunk"]["lines"]`, `rec["sig"]` with no guards. A PR from a fork containing a one-line `attest.jsonl` of `{}` crashes the reviewer's `verify.py` with a traceback. A verifier whose input is attacker-controlled must be the most paranoid code in the repo. Also: one `ssh-keygen` subprocess **per record** — 50k junk records for one path is a fork-bomb DoS.

```python
for r in records:
    if not isinstance(r, dict) or r.get("v") != 1 or r.get("path") != rel:
        continue
    try:
        h = r["hunk"]; n = int(h["lines"]); want = str(h["sha256"])
        line_sha = [str(x) for x in (h.get("line_sha") or [])]
        sig = r["sig"]
    except (KeyError, TypeError, ValueError):
        malformed += 1; continue
    ...
```

Plus a hard cap (`MAX_RECORDS_PER_FILE = 10_000`) with a printed warning, and report `malformed` in the output — silent skipping hides attacks.

### 6. Hashes are locale-dependent → verdicts aren't reproducible across machines

Every file read is `open(path, errors="replace")` — **no encoding**, so it's locale-dependent. On a C-locale CI container (Python ≤3.14 without `PYTHONUTF8`), non-ASCII source decodes to U+FFFD mojibake; the hook hashed the true UTF-8 text from tool input; every hunk hash mismatches; every record goes stale. Same repo, same ledger, different verdict depending on `LC_ALL`. This kills the "verify in CI" story.

Fix: hash bytes, not str, in **one shared function** used by hook and verifier:

```python
def norm_bytes(b: bytes) -> bytes:
    b = b.replace(b"\r\n", b"\n")
    return b"\n".join(l.rstrip() for l in b.split(b"\n")).strip(b"\n")
```

Hook: `hunk = norm_bytes(text.encode("utf-8"))`. Verifier: `body = open(path, "rb").read()`. Keep both sides on bytes (note `str.rstrip()` is Unicode-aware and `bytes.rstrip()` isn't — mixing them reintroduces mismatch on lines ending in U+00A0 etc.). This also subsumes the CRLF handling and makes hook/verifier normalization identical *by construction* instead of by parallel maintenance of two `norm()`s.

---

## P1 — must fix before tag

### 7. `--diff` scores the whole file when a diff entry has no added lines

`verify.py` `report_file`:

```python
consider = [i for i in (added or range(1, len(lines) + 1)) ...]
```

`added == set()` is falsy → falls back to the entire file. Pure-deletion or mode-change entries in a PR get whole-file attribution. `main()` passes `sorted(added)` (empty list, still falsy). Fix: `pool = range(1, len(lines)+1) if added is None else added`.

### 8. Transcript layer: weak matches counted as attested, stale cache, hardcoded path

- `attribute()` counts `strong + weak` as attested; `weak` = "the agent once wrote this line in **any project on this machine**", with whitespace-collapsed normalization, including lines from tool calls that **failed or were rejected** (you never check the tool result). `if __name__ == "__main__":` is 26 chars — it will be weak-matched everywhere, forever. `check_transcripts` then drops the strong/weak distinction entirely. Report strong matches as attested, weak as a separate informational count, and say so in the evidence string.
- `CACHE = ~/nohumanwrites/eval/attested-index.json` — hardcodes the dev's own checkout path; on any other install it silently creates `~/nohumanwrites/eval/`. Move to `~/.nhw/transcript-index.json`.
- The cache has **no invalidation** — new transcripts never appear until someone discovers `--rebuild`, which `nohumanwrites.py` can't even pass. Rebuild when the newest transcript mtime > cache mtime, and wrap `json.load(open(CACHE))` so a corrupt cache triggers rebuild instead of a traceback.

### 9. Coverage gaps vs. your own claims

- The matcher is `Write|Edit`; the hook then rejects anything but exactly those two. **MultiEdit** (regex-matched by the harness, rejected by the hook) and **NotebookEdit** are never attested. Handle `MultiEdit` (`inp["edits"]`, one record per edit) and widen the matcher.
- The hook never inspects `tool_response`: failed Edits (old_string not found) still get signed. Check the response and skip on error.
- `attest.py`'s docstring — "Every byte an agent writes through Claude Code passes through a logged tool call (Write / Edit)" — is false: **`Bash` writes bypass everything** (`cat >`, `sed -i`, codegen scripts). Under-claiming is the honest direction, but the docstring overclaims exactness. Rewrite it.

### 10. Edit context lines are attested as machine-written

`Edit.new_string` routinely contains unchanged anchor lines around the actual change — frequently human-written pre-existing code. The hook signs the whole `new_string`. Combined with SPEC's careful rule 1 ("asserts only that a machine produced the hunk"), this is *technically* in-spec but will be read as authorship. Options for v0.1: document it loudly in SPEC/README as channel-level provenance; for v0.2, diff `old_string`/`new_string` and attest only changed lines. Also note the inherent hole: a human can dictate code into the prompt and the agent re-emits it. Your project *name* claims authorship; your evidence claims channel. The README needs a threat-model section that says this before a security researcher says it for you.

### 11. Position-independent matching inflates attestation; spans recorded but unused

The verifier ignores `start`/`end` entirely (SPEC rule 4 says to use them): the sliding window matches a recorded hunk **anywhere** in the file, and the per-line fallback (on any whole-hunk miss) matches **any line anywhere** in the file. One stale record containing a common idiom (`logger = logging.getLogger(__name__)`) covers every identical human-typed line in that file forever. Minimum for v0.1:

- Report `covered-by-hunk` and `covered-by-line-fallback` as separate counts — the fallback is much weaker evidence and the output should say so.
- Use `start`/`end` when present to search near the recorded span first (also fixes the O(records × lines) full-file scan per record).
- SPEC: document duplicate-line inflation as a known limitation.

Also: `if not text: return` in the hook doesn't reject `text == "\n"`, which produces junk records with `sha256("")` and `lines: 1`. Skip on `not text.strip()`.

### 12. `diff_added` drops non-ASCII paths and ignores untracked files

Git C-quotes non-ASCII paths in `+++ "b/\303\251.py"` headers → `os.path.exists` fails → file silently excluded from PR scoring. Also brand-new *untracked* files never appear in `git diff` at all. Fixes: run `git -c core.quotePath=false diff -U0 --no-prefix …` (and handle the quoted remnant), handle `+++ /dev/null` explicitly, and union in `git status --porcelain` untracked files as fully-added. Docs should show the actual PR invocation (`git diff main...HEAD`), since `HEAD` includes unstaged noise.

### 13. `setup-key.sh` is not re-runnable and doesn't verify its own smoke test

- `printf … > "$NHW_DIR/allowed_signers"` **clobbers** any signers the user added on a previous run. Merge instead: `grep -qF "$(cut -d' ' -f2 "$KEY.pub")" file || printf … >> file`.
- `T="$HERE/eval/hooktest.txt"` — `eval/` may not exist → `set -e` kills the script. `mkdir -p "$HERE/eval"`.
- No OpenSSH ≥ 8.0 check (`ssh-keygen -Y` is 8.0+; Ubuntu 18.04 ships 7.6). Fail loudly up front.
- The smoke test pipes into the hook, which *by design* exits 0 on failure — so the smoke test asserts nothing. After running it, `grep` the ledger for a `hooktest` record and `exit 1` if absent; then test `ssh-keygen -Y verify` round-trip.
- `chmod 700 "$NHW_DIR"`; the key has no passphrase (necessary for the hook, but say in output what that means: any process as this user — including the agent itself and anything it runs — can sign).
- Bonus gap: setup never writes the repo-side story — no `.gitattributes` with `.nhw/attest.jsonl merge=union`. An append-only JSONL committed from branches **will** conflict on every merge. Ship the gitattributes line and document committing the ledger.

### 14. Canonical JSON is not specified — only Python can verify

Verification re-serializes with `json.dumps(sort_keys=True, separators=(",",":"))` — which in CPython means `ensure_ascii=True` (`\uXXXX` escaping). A Go/Rust/JS verifier implementing the SPEC as written will produce different bytes for any non-ASCII path or content and reject valid records. For a public spec, pin it byte-for-byte: either "exactly CPython `json.dumps(…, sort_keys=True, separators=(',',':'))`, ensure_ascii on" or JCS (RFC 8785) — and ship test vectors with non-ASCII content. Related spec gaps: `start`/`end` are nullable in the implementation but not in the schema; the `signer` field is unauthenticated metadata (verification uses hardcoded `-I nhw` against the keyring, never checks the fingerprint — either bind it or document it as cosmetic); records aren't bound to a repo, so a ledger can be **replayed** into another repo containing identical lines; `ts` is self-asserted. All four belong in a SPEC "known limitations" section.

### 15. `cmd_setup` rewrites `~/.claude/settings.json` with no backup

`json.dump(s, open(settings, "w"))` on the user's live config. One line before: `shutil.copy2(settings, settings + ".bak")`. Also wrap the idempotence scan in `try/except AttributeError` for hand-edited hook structures.

---

## P2 — fix soon, not blocking

- **"Single-file CLI" is false**: `nohumanwrites.py` imports `nhw/` and shells out to `setup-key.sh`. Vendor or package (`pyproject.toml`, `pipx install`, console entry point), and drop the claim.
- **The docstring advertises "git diff aware"** but `check` has no `--diff`; the PR workflow (SPEC's own rule 4) is only in the dev tool. Expose it.
- **Badge honesty**: badges render from unsigned transcript evidence with no tier marking. Include the evidence tier in the badge text or only badge on verified ledgers. Also: "Nothing leaves the machine" vs. a shields.io URL — trivially fine, but the badge implies otherwise to a pedant.
- **Perf**: `attest.attribute` rebuilds `weak = set().union(*per_file.values())` per file (precompute once); `sig_ok` spawns per record (cache verified `sha256(canonical)` per keyring); window search is O(lines × hunk) per record — fine until a monorepo.
- **UX**: no non-zero exit / `--fail-under` for CI gating; `--json` with no evidence prints bare `null`; `-I nhw` failures are swallowed (`capture_output=True`) — add `--verbose` surfacing ssh-keygen stderr; add a `doctor` subcommand (key exists, sign/verify round-trip, hook installed, ledger writable) since the hook's failures are silent by design.
- **Robustness nits**: `list_files` `os.path.getsize` races (file vanishes → crash) and silently skips >2MB files; `check` takes `repo_root(paths[0])` only — multi-repo invocations misattribute; `sig_ok`'s `os.unlink(sp)` unguarded in `finally`; `fingerprint()` spawned per record (cache it); hook log grows forever; `MIN_LEN`/`12` hardcoded in three files; case-insensitive filesystems (macOS) can mismatch record path case vs. disk.
- **`fingerprint()` regex** on `ssh-keygen -lf` output is fine, but if it fails you write `"signer": "ssh-ed25519:unknown"` records — log that.

---

## False-attestation ledger (as requested, explicit)

**Counted attested though human-typed:** (a) Edit context lines in `new_string`; (b) duplicate lines — any line matching any stale record's `line_sha`, anywhere in the file; (c) whole-hunk hash match at a *different* location than recorded; (d) transcript weak matches (cross-project, whitespace-collapsed, includes failed/rejected tool calls); (e) human dictates code → agent emits it → signed; (f) anyone pipes a forged event into `hook.py` on a machine with the key, or the agent itself signs via `Bash` — the signature proves key access, never harness provenance; (g) repo ships its own `allowed_signers` and self-signs (P0.1).

**Counted unattested though agent-written:** MultiEdit/NotebookEdit/Bash writes; worktrees/submodules (P0.3); C-locale hash mismatch (P0.6); interleaved ledger corruption (P0.4); reviewer lacking the keyring; formatter reflow beyond per-line granularity (intended per SPEC); short agent lines <12 chars (intended); stale transcript cache.

The honest-direction asymmetry you aimed for mostly holds — except (b), (c), (d) and (g), which all inflate.

---

## v0.1 maintainer checklist

- **License**: `LICENSE` (full Apache-2.0 text), `NOTICE`, `SPDX-License-Identifier: Apache-2.0` + copyright header in each of the 5 files.
- **Tests** (pytest, `tmp_path` + `NHW_KEY` override + fixture key — the env override is already there, use it): hook→verify round-trip; CRLF file; Latin-1 file under `LC_ALL=C`; Unicode paths; empty file / `"\n"`-only write; MultiEdit event; failed-Edit event; tampered record (bit-flip must fail); malformed ledger lines (`{}`, `42`, missing `hunk`, string `lines`); 50k-record DoS cap; 8 parallel hook appends → all records parse; worktree `.git` file; diff with quoted path; `added=set()` regression; canonical-JSON vectors incl. non-ASCII.
- **CI**: GitHub Actions, {ubuntu, macos} × {3.9–3.13}, plus one container pinned to OpenSSH 8.0; shellcheck on `setup-key.sh`; an e2e job that runs `setup` + a simulated hook event + `verify`.
- **Packaging**: `pyproject.toml`, `__version__`, console script; `SECURITY.md` with the threat model above; SPEC: canonicalization section, nullable spans, known limitations (replay, self-asserted `ts`, channel-vs-authorship, duplicate lines); docs for `merge=union` and key rotation/revocation (`ssh-keygen -Y verify -V` exists for validity windows — plan for it).

---

**Verdict: not yet — the code is a good prototype, but P0.1 and P0.6 mean the tool's headline output is currently forgeable by the attested party and non-reproducible across machines; fix the six P0s (≈2 days) before tagging v0.1.**

### E. deepseek/deepseek-v4-pro-0813
I reviewed the implementation against the spec and the threat model. Overall this is a useful idea and the `ssh-keygen -Y` signing core is sound, but the current code is not ready for a public v0.1. The biggest problem is a trust-root bug that lets any repo self-attest 100% by committing its own `allowed_signers`.

Ranked issues with concrete fixes:

## 1. CRITICAL — a malicious repo can forge 100% attestation by controlling `.nhw/allowed_signers`

`verify.allowed_signers()` currently checks the repo’s own `.nhw/allowed_signers` before the real `~/.nhw/allowed_signers`:

```python
for p in (os.path.join(repo, ".nhw", "allowed_signers"),
          os.path.expanduser("~/.nhw/allowed_signers")):
```

A malicious repo can commit:

- `.nhw/allowed_signers` containing the attacker’s public key
- `.nhw/attest.jsonl` containing any `path`/`hunk` payloads signed by that key

`verify.sig_ok()` will then verify those signatures and `check` will print a high attested percentage. This destroys the provenance model: the repo itself becomes the trust anchor.

Patch:

```python
# verify.py
import sys
from typing import Optional

def allowed_signers(repo: str) -> Optional[str]:
    p = os.environ.get("NHW_ALLOWED_SIGNERS",
                       os.path.expanduser("~/.nhw/allowed_signers"))
    if p and os.path.exists(p):
        return p

    # Never trust a repo-controlled .nhw/allowed_signers for verification.
    # It can contain the fork's own public key and make forged records verify.
    return None
```

If you want repo-bundled signer files later, they must be pinned out-of-band or treated only as advisory. For v0.1, the trust root must live in `~/.nhw` or an explicit env var.

## 2. HIGH — untrusted ledger records can crash the verifier

`load_ledger()` only catches `json.loads()` errors. A malformed but valid JSON record like:

```json
{"v":1, "path":"x", "hunk":{"lines":"not-an-int", "sha256":"x"}, "sig":"..."}
```

will cause a `TypeError` in `verify.attested_lines()`:

```python
n = r["hunk"]["lines"]
for i in range(0, len(lines) - n + 1):
```

Other records with missing `sha256`, missing `hunk`, or a string `line_sha` will cause `KeyError`/`TypeError`. A malicious repo can DoS any verifier.

Add schema validation and per-record exception handling:

```python
# verify.py
def _valid_record(r):
    try:
        if not isinstance(r, dict) or r.get("v") != 1:
            return False
        if not isinstance(r.get("path"), str) or not r["path"]:
            return False
        h = r.get("hunk")
        if not isinstance(h, dict):
            return False
        if not isinstance(h.get("lines"), int) or h["lines"] < 0:
            return False
        sha = h.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            return False
        ls = h.get("line_sha", [])
        if not isinstance(ls, list) or not all(isinstance(x, str) for x in ls):
            return False
        if not isinstance(r.get("sig"), str) or not r["sig"]:
            return False
        return True
    except Exception:
        return False
```

In `load_ledger()`:

```python
for raw in open(p, encoding="utf-8"):
    try:
        r = json.loads(raw)
        if _valid_record(r):
            out.append(r)
    except Exception:
        pass
```

And wrap each record’s processing in `attested_lines()` with `try: ... except Exception: continue`.

Also add a ledger size / record count cap. A repo can still put thousands of plausible records for one file and cause the verifier to spawn `ssh-keygen` repeatedly.

## 3. HIGH — `check` silently assumes all paths are in one repository

`nohumanwrites.py:cmd_check()` does:

```python
repo = repo_root(paths[0])
res = check_ledger(repo, files) if repo else None
```

If the user runs:

```bash
python3 nohumanwrites.py check /repo-a /repo-b
```

all files are scored against `/repo-a`’s ledger. A file in `/repo-b` gets:

```python
rel = os.path.relpath(os.path.abspath(f), repo)
```

which produces `../../repo-b/...`. That can read outside the repo and attribute lines against the wrong ledger.

Minimal fix: reject mixed roots in ledger mode.

```python
# nohumanwrites.py, inside cmd_check()
if "--transcripts" in flags:
    repo = None
else:
    roots = {repo_root(f) for f in files}
    if len(roots) != 1 or None in roots:
        print("check can only score one git repo at a time in ledger mode; "
              "run per repo or use --transcripts")
        return 2
    repo = roots.pop()
```

Also guard `verify.attested_lines()` against `../` paths:

```python
repo = os.path.abspath(repo)
p = os.path.abspath(os.path.join(repo, rel))
if os.path.commonpath([repo, p]) != repo:
    return set(), 0, 0
```

## 4. HIGH — transcript mode counts cross-file weak matches as “attested”

`attest.attribute()` currently does:

```python
strong = per_file.get(path, set())
weak = set().union(*per_file.values()) if per_file else set()
...
if k in strong:
    out["strong"] += 1
elif k in weak:
    out["weak"] += 1
else:
    out["unattested"].append((i, ln[:120]))
```

`nohumanwrites.check_transcripts()` then treats both strong and weak as attested because it only reads `r["unattested"]`.

This means a human who writes a line an agent happened to write anywhere else on the machine — including a different repo — is counted as attested. That is exactly the false-attestation failure mode the UI claims not to do.

Patch:

```python
# attest.py
def attribute(path, per_file, min_len=12, include_weak=False):
    strong = per_file.get(path, set())
    weak = set().union(*per_file.values()) if include_weak and per_file else set()
    ...
        if k in strong:
            out["strong"] += 1
        elif include_weak and k in weak:
            out["weak"] += 1
        else:
            out["unattested"].append((i, ln[:120]))
```

And in public CLI transcript scoring:

```python
r = attest.attribute(f, pf, MIN_LEN, include_weak=False)
```

Also rename `human_or_untracked_ratio` to `unattested_ratio`. It is not evidence of human input.

## 5. MEDIUM-HIGH — append to `attest.jsonl` is not concurrency-safe

`hook.py` does:

```python
with open(os.path.join(root, ".nhw", "attest.jsonl"), "a") as f:
    f.write(json.dumps(rec, sort_keys=True) + "\n")
```

Concurrent hook runs can interleave writes. Even if Claude Code is usually serial, the design should not lose or corrupt the ledger when concurrent.

Patch using `fcntl.flock` and a single `os.write`:

```python
# hook.py
import fcntl

def append_record(rec, root):
    ledger = os.path.join(root, ".nhw", "attest.jsonl")
    os.makedirs(os.path.dirname(ledger), exist_ok=True)
    fd = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
    finally:
        os.close(fd)
```

This works on both macOS and Linux.

## 6. MEDIUM — Python 3.9 claim is false

`hook.py` and `verify.py` use:

```python
def repo_root(path: str) -> str | None:
def allowed_signers(repo: str) -> str | None:
```

`str | None` in runtime annotations is Python 3.10+ syntax. The project claims Python 3.9+, but importing these modules on Python 3.9 raises:

```text
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

Patch:

```python
from typing import Optional

def repo_root(path: str) -> Optional[str]:
def allowed_signers(repo: str) -> Optional[str]:
```

Or add `from __future__ import annotations` and be aware that `typing.get_type_hints()` may still fail on 3.9.

## 7. MEDIUM — `setup-key.sh` uses Linux-only `hostname -s` and assumes `eval/` exists

Current:

```bash
ssh-keygen -q -t ed25519 -N "" -C "nhw-$(hostname -s)" -f "$KEY"
```

macOS `hostname` may not support `-s`, and with `set -e` the setup script will abort.

Also:

```bash
T="$HERE/eval/hooktest.txt"
```

is written without creating `$HERE/eval`.

Patch:

```bash
mkdir -p "$NHW_DIR" "$HERE/eval"
HNAME="$(hostname 2>/dev/null || echo nhw)"
ssh-keygen -q -t ed25519 -N "" -C "nhw-$HNAME" -f "$KEY"
```

Also add an explicit OpenSSH `-Y` support check before relying on it; otherwise smoke testing gives a confusing failure on OpenSSH < 8.0.

## 8. MEDIUM — transcript cache is stale forever

`attest.load_index()` caches `~/nohumanwrites/eval/attested-index.json` and only rebuilds with `--rebuild`, which the public `check --transcripts` path never exposes.

A user can run `check --transcripts`, then Claude Code writes more files, then run it again and still get the old cached index.

Patch with mtime-based invalidation:

```python
# attest.py
def _cache_valid(cache, logdir=LOGDIR):
    try:
        files = glob.glob(os.path.join(logdir, "*", "*.jsonl"))
        if not files:
            return False
        cache_mtime = os.path.getmtime(cache)
        return all(os.path.getmtime(p) <= cache_mtime for p in files)
    except OSError:
        return False

def load_index(rebuild=False):
    if not rebuild and os.path.exists(CACHE) and _cache_valid(CACHE):
        ...
```

## 9. MEDIUM — UX wording wrongly implies “human”

The spec explicitly says:

> Absence of a record asserts nothing about who did.

But `nohumanwrites.render()` prints:

```text
unattested = typed by hand, or written through a channel with no hook.
```

And `attest.attribute()` exposes `human_or_untracked_ratio`.

This is not honest and will cause false blame in review. Patch the output:

```python
print("  unattested = no verifiable machine provenance; this does not identify the author.")
```

Rename `human_or_untracked_ratio` to `unattested_ratio`.

Also, the line:

```python
if res["unattested"] == 0:
    print("  every considered line carries machine provenance.")
```

is misleading if `res["lines"] == 0`. Guard it.

## 10. LOW-MEDIUM — setup can fail because `~/.claude` may not exist

`cmd_setup()` does:

```python
json.dump(s, open(settings, "w"), indent=2)
```

If `~/.claude` does not exist, this fails. Also the write is non-atomic, so interrupted setup can corrupt `settings.json`.

Patch:

```python
os.makedirs(os.path.dirname(settings), exist_ok=True)
tmp = settings + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(s, fh, indent=2)
os.replace(tmp, settings)
```

## 11. LOW-MEDIUM — `git diff` parsing and missing `git` are not handled

`verify.diff_added()` runs:

```python
subprocess.run(["git", "diff", "-U0", ref, "--", "."], ...)
```

If `git` is missing or the directory is not a git worktree, this raises `FileNotFoundError`.

Patch:

```python
try:
    proc = subprocess.run(["git", "diff", "-U0", ref, "--", "."],
                          cwd=repo, capture_output=True, text=True)
except FileNotFoundError:
    print("git not found", file=sys.stderr)
    return {}
if proc.returncode != 0:
    print(proc.stderr, file=sys.stderr)
    return {}
out = proc.stdout
```

Also note that `repo_root()` checks `os.path.isdir(os.path.join(d, ".git"))`. In a linked git worktree, `.git` is a file, not a directory. Use `os.path.exists(os.path.join(d, ".git"))`.

## 12. LOW — data/spec mismatches and hardening

- `hook.py`’s `producer` block omits `model`, despite the spec example including it.
- Several file reads/writes use the locale default encoding. Use `encoding="utf-8"` for `attest.jsonl`, `load_ledger()`, and cache files.
- `line_sha` uses only the first 16 hex chars of SHA-256. That is a 64-bit content fingerprint per line. Given the parallel weak-match false-attestation risk, use full SHA-256 or at least 128 bits.
- The ledger can grow without bound. A malicious or runaway agent can create enormous records. Add a maximum record size or log a warning when oversized.
- `noHumanWrites.list_files()` silently ignores files > 2 MB. Surface skipped files, especially in `--json` output.

## Portability and tooling needs

Concrete test matrix before v0.1:

- Python: 3.9, 3.10, 3.11, 3.12
- OS: macOS, Linux
- OpenSSH: 8.0 baseline, plus current
- Git: normal clone and linked worktree
- Shell: `/bin/sh` and `bash` for setup
- Scenarios:
  - empty file, CRLF file, binary file, file > 2 MB
  - concurrent hook invocations
  - malformed ledger records
  - repo with malicious `.nhw/allowed_signers`
  - path with spaces, Unicode, quotes, `../`
  - symlinked repo root and linked worktree

Also add SPDX/Apache-2.0 headers to every source file and a `pyproject.toml` if this is intended as an installable CLI.

## False-attestation summary

A line should not be counted attested unless the verifier can honestly tie it to a specific signed write. As written, these paths can over-claim:

- Repo-controlled `.nhw/allowed_signers` — forged repo can claim anything.
- Transcript `weak` set — same content anywhere on the machine counts.
- Per-line `line_sha` fallback — same stripped line anywhere in the file counts.
- Sliding-window hunk match — human-pasted identical hunk counts.
- Stale transcript cache — old agent lines count against new human edits.

And false negatives happen because:

- Short lines are ignored entirely.
- Hook failures are logged to `~/.nhw/hook.log` and exit 0, so agent code silently becomes unattested.
- `repo_root()` misses linked worktrees.
- `check` silently skips files > 2 MB.
- Output labels unattested as “typed by hand” when it should only say “no verifiable provenance.”

---

**Verdict:** after fixes — the repo-controlled signer trust, ledger validation, cross-repo path handling, and transcript weak-match false attestation must be fixed before v0.1.

### F. x-ai/grok-4.6
## Review: NoHumanWrites v0.1 (hostile, pre-tag)

This is a coherent idea (machine-key signatures over hunk hashes, absence ≠ human) implemented in a way that will **over-claim provenance** in the exact situations a public badge/PR check will be used. I would not ship this as evidence. Ranked issues below; line numbers refer to the files you pasted.

---

### S0 — Trust model inverted (security)

`verify.allowed_signers` prefers **the repo under test**:

```python
for p in (os.path.join(repo, ".nhw", "allowed_signers"), os.path.expanduser("~/.nhw/allowed_signers")):
```

SPEC §2 says the verifier holds keys, “as with SSH.” This is the opposite: a PR/repo can add `.nhw/allowed_signers` + a matching `attest.jsonl` and verify at 100%. That is the whole product, gamed.

`sig_ok` also never binds `rec["signer"]` to the key that verified; `-I nhw` is a constant principal, so any key in that file is equivalent.

**Patch (minimum):**

- Default signers path: **only** `~/.nhw/allowed_signers` (or `--signers`).
- Repo copy: require `--trust-repo-signers` (and print that scores are then self-attested).
- For PR mode: load signers from a trusted ref (`git show main:.nhw/allowed_signers`), never from the working tree being scored.
- Fail closed if no signers (`check_ledger` should not report “signed ledger” with `verified_signatures: bool(signers)` — that flag is “file existed,” not “sigs checked”).

Until that changes, a public `% attested` badge is an honor system with extra steps.

---

### S1 — False attestation: `line_sha` fallback (correctness + honesty)

`verify.attested_lines` (stale path):

```python
if len(l.strip()) >= 12 and hashlib.sha256(l.strip().encode()).hexdigest()[:16] in want_lines:
    covered.add(i)
```

This marks **any** line in the file whose stripped text matches a 64-bit prefix of a signed line. Combined with hook `line_sha` using `l.strip()` (indent discarded):

- Common lines (`from typing import Any`, `return None`, license lines, `self.assertEqual(...)`) stamp the rest of the file.
- A human typing the same statement later is “attested.”
- Duplicate copies: the sliding window only credits the **first** match then `break`s; the fallback then paints every equal line. Asymmetry is nonsense.

SPEC §4 says “most recent record whose hunk covers it.” The code **unions every record**, ignores `ts`, ignores `start`/`end`.

**Patch:**

- Drop truncated hashes; store full sha256 of **exact** normalised line (same `norm` as hunk, **do not** `strip()` indent).
- Fallback match: greedy, **each signed hash used at most once**, scan in record order newest-first.
- Require a second factor for fallback (same line ± N of recorded `start`, or neighbour-hash). Otherwise only whole-hunk match counts for v0.1.
- Sort records by `ts` descending; do not let a 2024 hunk attest a 2026 retype.

---

### S1b — Transcripts: global “weak” match counted as attested

`attest.attribute` unions **every line the agent ever wrote on this machine**, then `check_transcripts` treats `strong+weak` as attested.

A human `import os` in repo B is attested because Claude wrote `import os` in repo A. Auto-fallback in `cmd_check` (ledger missing → transcripts) plus `--badge` will publish that number.

`load_index()` never rebuilds unless `--rebuild`; cache is hardcoded `~/nohumanwrites/eval/attested-index.json`. First run freezes provenance forever.

**Patch:**

- Weak matches: never increment attested (debug-only).
- No transcript fallback for `--badge` / `--json`.
- Cache keyed by log mtimes; default rebuild if stale.
- Do not emit a shields badge from unsigned logs.

---

### S2 — 0 considered lines → 100% attested (UX lie)

```python
pct = 100 * (res["lines"] - res["unattested"]) / (res["lines"] or 1)
```

Empty file, or only lines `< 12` chars → **100% attested**. Same in `verify.report_file`.

**Patch:** if `tot == 0`, print `n/a (no lines ≥ 12 chars)` and refuse `--badge`.

---

### S2b — Copy claims “human” (SPEC violation)

SPEC §1/§6: absence asserts nothing; reviewers see “unattested.”

`render()`:

```
unattested = typed by hand, or written through a channel with no hook.
```

`verify.py` module docstring: “human-typed, or written through a channel with no hook.”

**Patch:** wording everywhere: **“unattested” only**. Never “human,” never “typed by hand.” Badge: `unattested`, not a green “attested” that implies the complement is human.

Also: `check` docstring says “git diff aware”; `cmd_check` never calls `diff_added`. Either wire `--diff` or delete the claim.

`verified_signatures: bool(signers)` must be “N signatures verified,” not “signers file present.”

---

### S3 — Concurrent hooks tear `attest.jsonl`

`open(..., "a"); f.write(...)` with records that easily exceed POSIX `PIPE_BUF` (line_sha arrays). Two PostToolUse hooks → interleaved JSON → `load_ledger` drops the line → silent loss of provenance.

**Patch:**

```python
import fcntl
path = os.path.join(root, ".nhw", "attest.jsonl")
os.makedirs(os.path.dirname(path), exist_ok=True)
fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
with os.fdopen(fd, "a") as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
    f.flush(); os.fsync(f.fileno())
```

Document POSIX-only locking for v0.1. `cmd_setup` writing `~/.claude/settings.json` in-place can truncate the file on crash — write temp + `os.replace`.

---

### S4 — Canonical JSON / signature (correctness)

Sign:

```python
canonical = json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()
```

Store: `json.dumps(rec, sort_keys=True)` (different separators — OK because verify re-dumps parsed object).

Still fragile:

- Default `ensure_ascii` / `allow_nan` not pinned.
- `sig` is the **full SSH armor** including newlines; OK if round-tripped, but one `json.loads` that doesn’t preserve the string exactly + a later re-sign path would break. Store `sig` as a single-line base64 of the `.sig` file, or sign a detached hash and keep armor out of JSON.
- `fingerprint()` can be `"unknown"` and is **inside** the signed body; cosmetic, but then you cannot map signer → key.
- `ssh-keygen -Y verify` input is the payload bytes; good. Missing `sig` / `hunk` → **uncaught** in `attested_lines` (one bad line crashes the CLI). Wrap per-record.

**Patch:** `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)`; schema-check `v,ts,path,hunk,producer,signer,sig`; skip + count invalid.

---

### S5 — Paths, encodings, CRLF, empties, huge files

| Case | What happens |
|---|---|
| Locale `open()` vs UTF-8 hash | Hook/verify/CLI all `open(path, errors="replace")` with **no encoding**. Hash is `.encode()` UTF-8 of maybe-wrong decode. **Always `encoding="utf-8", errors="surrogateescape"`.** |
| CRLF | `norm` unifies; `line_span` searches raw `text.strip("\n")` in raw body → often `None`. Verifier ignores span (good) but recorded start/end are lies. |
| Empty / whitespace `text` | Hook `if not path or not text: return` — no record. |
| Duplicate substring | `body.find` first hit; span wrong (unused for match). |
| `rel` from ledger `../.ssh/id_rsa` | `os.path.join(repo, rel)` then `open` — **path traversal** if you ever iterate records as files. Reject `rel` with `..` or abs paths; `os.path.normpath` + must stay under root. |
| Huge files | Hook reads whole file; verify is **O(records × lines × hunk_len)** hash. CLI skips >2MB; hook/verify do not → 10s timeout, hook “never blocks” except when it does. Cap hunk size; if `start`/`end` present try that window first. |
| Git worktree | `isdir(.git)` misses `.git` **file**. `repo_root` returns None → no ledger. Use `exists(.git)`. Loop `d != "/"` also skips Windows `C:\`. |
| Files >2MB / binaries | `is_text` only checks NUL in first 4k. |

`line_span` can be deleted for v0.1 if you don’t use it to accelerate verify.

---

### S6 — Sliding window bugs

```python
n = r["hunk"]["lines"]
for i in range(0, len(lines) - n + 1):
    seg = norm("\n".join(lines[i:i + n]))
```

- `norm` **strips leading/trailing newlines of the whole window**, so a window of n lines can hash-equal a shorter hunk.
- Duplicate blocks: only first window covered.
- `n` from attacker-controlled JSON: `n=1` scans every line; missing `hunk` throws.
- Hunk hash is over `norm(text)` of the **tool payload**, not necessarily the n file lines (leading blank lines stripped). Off-by-one vs `lines` count.

**Patch:** define hunk bytes as `norm` **without** outer `strip("\n")`, or hash `join(rstrip(line) for line in lines)` with explicit length; compare `n == want_text.count("\n")+1` after the same function. Try recorded `[start,end]` first; only then slide; allow multiple hits.

---

### S7 — `git diff -U0` parser

```python
if ln.startswith("+++ b/"):
    cur = ln[6:]
```

Breaks on: quoted/C-escaped names, `diff.noprefix`, tabs, renames, binary, `/dev/null`. `int(m.group(2) or 1)` is OK for omitted count, but `m` can be `None` → crash.

`ref` from argv without `--` → `git diff -U0 -cpack.foo=...`. Use `git diff -U0 -- <ref> -- .` still treats `-foo` as rev; validate rev with `git rev-parse --verify`.

Untracked files never appear — `--diff` under-reports new agent files.

---

### S8 — Key handling / temp files / hook stdin

- `setup-key.sh`: **empty passphrase** key in `~/.nhw/id_nhw`. Anyone with that file forges agent provenance. Document; `chmod 700 ~/.nhw`.
- Re-run **overwrites** `allowed_signers` (one key only).
- Smoke test writes `eval/hooktest.txt` and **appends to the tool repo’s `.nhw/attest.jsonl`**. That must not ship. Use `mktemp -d` + `git init`.
- `NamedTemporaryFile` payload in `/tmp` (hunk contents); `p+".sig"` mode depends on umask. `ssh-keygen` supports signing stdin on recent versions; if not, `tempfile.mkstemp` in `~/.nhw` with 0600.
- Hook `json.load(sys.stdin)` — unbounded; a huge Write can OOM. Cap size.
- `NHW_KEY` is used as `-f` **without** checking it isn’t the user’s login key. Refuse if it matches `~/.ssh/id_ed25519`.
- Failures swallowed (`exit 0`) — correct for the agent, but `~/.nhw/hook.log` should be mentioned in `check` when coverage is 0.

Malicious **repo** vs verifier: besides fake signers, a huge/cyclic `attest.jsonl` is a DoS (quadratic window). Cap records per path; ignore records with `lines > 10000`.

Malicious **path** in hook event: not shell-interpolated (good). Still writes `relpath` into the ledger; keep it relative and reject `..`.

---

### S9 — Portability

Claim: Python 3.9+. Code: `str | None` in `hook.py` / `verify.py` → **SyntaxError on 3.9**. Use `Optional[str]`.

`ssh-keygen -Y` needs OpenSSH ≥ 8.0. `setup-key.sh` should `ssh -V` and fail with a message. macOS/Linux OK if not ancient; **no Windows** (`fcntl`, `bash`, `python3`, `hostname -s`).

`python3` hardcoded in hook install; `cmd_setup` can embed `sys.executable`.

`nohumanwrites.py` is **not** a single-file CLI (`from nhw import attest, verify`). Either vendor or package.

---

### S10 — Maintainer bar before v0.1

Missing: tests, CI, `LICENSE`, SPDX headers, `pyproject.toml`, version pin of the jsonl schema.

Minimum tests (no network):

1. Sign/verify round-trip, including unicode path + CRLF file.
2. Concurrent 20 appends → 20 valid jsonl lines.
3. Repo `allowed_signers` **ignored** by default; forged ledger → 0 verified.
4. Duplicate 20-line block: both attested or documented not.
5. Human inserts a 12+ char line the agent once wrote → **unattested**.
6. `tot==0` → no 100% badge.
7. `git diff` parser: new file, delete-only, `+12` vs `+12,0`.
8. Worktree `.git` file finds root.
9. Transcript weak match does not count.

CI: 3.9, 3.12, ubuntu + macos; OpenSSH present; `python -m compileall`.

---

### Concrete patch list (severity order)

1. **Signers not from the tree being scored**; fail closed; don’t set `verified_signatures` from file existence.
2. **Disable line_sha fallback** (or make it injective + newest-only). Disable transcript **weak** and badge fallback.
3. **Never say “human” / “typed by hand.”** Zero-line → `n/a`.
4. **`fcntl` + `fsync` append**; atomic settings write; smoke test in a temp git repo.
5. **`encoding="utf-8"`** everywhere; reject `..` in `path`; `exists(.git)`; `Optional[str]`.
6. Pin canonical `json.dumps`; per-record try/except; cap window work; try recorded span first.
7. `setup-key.sh`: don’t clobber signers; don’t pollute this repo; check `ssh -V`.
8. Tests/CI/LICENSE as above.
9. Wire or drop “git diff aware”; store armor-free `sig`.

I would not bikeshed namespace/`producer.model` vs `tool` until the above is fixed — schema drift is real (`SPEC` has `model`, hook has `tool`) but it is not what will embarrass you on day one.

---

**Verdict: not yet.**

### G. z-ai/glm-5.3
# Hostile review: NoHumanWrites v0.1

The architecture is sound — sign at the write boundary, verify content-hashes later, fall back to per-line hashes, and *never* guess from style. The spec's rule 1 is exactly the right honesty posture. The problem is that the implementation violates the spec's two headline guarantees: the signature model is forgeable by any repo it's pointed at, and the CLI *does* produce a score when it has verified nothing. Both are small patches. Ranked:

---

## P0 — fix before tag

### P0-1: The trust anchor lives inside the attacker-controlled repo

`verify.allowed_signers()` prefers `<repo>/.nhw/allowed_signers` over `~/.nhw/allowed_signers`. SPEC rule 2 says "the verifier holds the public keys, as with SSH" — the code does the opposite. A malicious repo ships a forged `attest.jsonl` **plus its own `allowed_signers`** containing its own key. Every record "verifies." `check_ledger` prints `verified_signatures: True` and 100% attested. This is circular trust: the signature proves "a key the repo nominated signed the repo's claims."

```python
def allowed_signers(repo, trust_repo_keys=False):
    local = os.path.expanduser("~/.nhw/allowed_signers")
    if os.path.exists(local):
        return local
    in_repo = os.path.join(repo, ".nhw", "allowed_signers")
    if trust_repo_keys and os.path.exists(in_repo):
        print("WARNING: using repo-supplied keys; signatures prove nothing about origin")
        return in_repo
    return None
```
Add `--trust-repo-keys` (and print which key verified what). Document the out-of-band key distribution story, because right now there isn't one: `setup-key.sh` never puts a signers file *in* the repo, so the only way a second machine ever verifies anything is via the repo file — i.e., the attack path is also the only feature path. Pick one: TOFU-with-prompt, a committed keys file pinned by fingerprint at clone-review time, or CI-held keys.

### P0-2: An unverifiable ledger is reported as "0% attested", not "unknown"

If no `allowed_signers` exists anywhere, `sig_ok` returns False for everything, `check_ledger` still returns a result, and the user sees **"0% attested"** — which reads as "100% human." That directly violates SPEC rule 1 ("absence of a record asserts nothing") and is the exact dishonesty the project exists to prevent. Compounding it:

- `"verified_signatures": bool(signers)` means "a signers file existed," not "signatures verified." A forged ledger with a repo key reports True.
- `check_ledger` discards the counts `attested_lines` already computes (`nrec`, `stale` are bound and dropped), so the user can't distinguish "0/12 signatures verified" from "12 verified, 0 matched."

Fix: `attested_lines` must also return a `failed` count; `check_ledger` returns `None` (falls through to transcripts / "no provenance") when `signers is None or verified == 0`, printing e.g. `ledger present, 0/12 signatures verifiable — not scored`.

### P0-3: Python 3.9 breaks the hook *silently*

`hook.py` and `verify.py` use `str | None` annotations with no `from __future__ import annotations`. PEP 604 unions are 3.10+. On 3.9 the module raises `TypeError` at import — and hook.py's blanket `except Exception → log → exit 0` swallows it. So on any 3.9 box the hook **never records anything, forever, with no visible failure** — the worst possible failure mode for a provenance tool (users believe they have coverage). One line at the top of both files:

```python
from __future__ import annotations
```

The `setup-key.sh` smoke test would catch this — only if run on 3.9. CI must (see checklist).

### P0-4: `git diff` in an untrusted repo executes repo-controlled config

`diff_added()` runs plain `git diff` with `cwd=repo`. A hostile repo distributed with its `.git/config` (`diff.external=`, `diff.<driver>.textconv=`, `core.fsmonitor=`) or attributes referencing a driver gets command execution in the verifier's context. Cheap fix:

```python
subprocess.run(["git", "-c", "diff.external=", "-c", "core.fsmonitor=false",
                "diff", "--no-ext-diff", "--no-textconv", "-U0", ref, "--", "."],
               cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")
```
While there: guard `m is None` in the `@@` regex (malformed diff → `AttributeError` today), skip `.nhw/attest.jsonl` itself (otherwise every ledger append shows up as unattested added lines and drags the score), and skip git-quoted paths (`+++ b/"a\tb"` currently mis-slices).

---

## P1 — fix for v0.1 or immediately after

**P1-1: Partial-line `Edit` is never attested (false "human").** `new_string` frequently starts/ends mid-line. The hook hashes `norm(new_string)` — the fragment — while the verifier's sliding window hashes *whole file lines*. Hash of `"foobar"` never equals hash of `"x = foobar()"` → record is stale, and `line_sha` was computed over the fragment (`"foobar"` < 12 chars → no fallback). The most common agent operation produces phantom-unattested lines. Fix in `line_span`: locate the edit, then expand to line boundaries and hash **the full containing lines**:

```python
i = body.find(t)
ls = body.rfind("\n", 0, i) + 1
le = body.find("\n", i + len(t));  le = len(body) if le < 0 else le
whole = body[ls:le]                 # hash norm(whole), build line_sha from its lines
```

**P1-2: Window scan `break`s after first hit.** `attested_lines` covers only the first duplicate copy of a hunk. `Edit` with `replace_all: true`, or copy-pasted identical blocks, leave the second occurrence unattested (false "human"). Remove the `break`; keep scanning. Also: the scan is O(records × file_lines × hunk_lines) with a fresh SHA-256 per window — precompute a rolling hash or at least cap `n` (reject non-int / negative / > 10_000 / > len(lines)).

**P1-3: Worktrees are silently unhooked.** `repo_root` (both hook.py and nohumanwrites.py) tests `os.path.isdir(.git)`. Git worktrees and submodules have `.git` as a *file*. Every write in a worktree produces no record, silently. Use `os.path.exists`.

**P1-4: Concurrent hook runs interleave; corruption is swallowed.** `open(..., "a")` + buffered write from two sessions can tear lines; `load_ledger` silently skips unparseable lines, so the ledger quietly under-reports attestation. Fix both directions: single `os.write` on an `O_APPEND` fd (one syscall, atomic in practice), and `load_ledger` returns a bad-line count that `verify` prints ("3 unparseable ledger lines — corruption or concurrent write").

**P1-5: Transcript layer over-claims.** `attest.attribute` counts a line attested if the agent wrote it to **any path, ever** (`weak = set().union(*per_file.values())` — also recomputed per file, quadratic). Cross-project boilerplate becomes "attested." There's no time ordering, so a line a human typed *before* an agent later wrote an identical one flips to attested. Make weak matching opt-in (`--weak`), report strong/weak separately (the signed layer needs the same two-tier reporting for its line-hash fallback), and `os.path.realpath` both sides (macOS `/tmp` symlink breaks the absolute-path match today).

**P1-6: Transcript cache is wrong by construction.** `CACHE = ~/nohumanwrites/eval/attested-index.json` — hardcoded to one checkout location; on any other machine it silently creates `~/nohumanwrites/eval/`. No staleness check, so new sessions never appear until a manual `--rebuild` (false "unattested"). Move to `~/.cache/nhw/`, invalidate on transcript mtime.

**P1-7: `setup` clobbers `~/.claude/settings.json` non-atomically and pollutes the repo.** `json.dump(..., open(settings, "w"))` truncates first — a crash mid-write destroys the user's Claude config. Write temp + `os.replace`, keep a `.bak`. The smoke test appends a real record for `eval/hooktest.txt` to the *project's* real `.nhw/attest.jsonl` and leaves an untracked file — run it in `mktemp -d` + `git init`. Also: matcher `Write|Edit` misses `MultiEdit` (and `NotebookEdit`); handle the `edits` array or you'll have a whole class of silent false-unattesteds.

**P1-8: Record schema is unvalidated.** Once past `sig_ok`, `r["hunk"]["lines"]` as a string/float → `TypeError` crashes the verifier; a 100 MB `sig` field → 100 MB temp write per record. With P0-1 unfixed this is a trivial DoS. Validate types, cap `len(sig) < 4096`, check `r.get("v") == 1` (the version field is currently decorative), and reject records whose `path` escapes the repo (`os.path.normpath(join(repo, rel))` containment check — otherwise a record path of `../../etc/...` makes the verifier read outside the repo).

---

## P2 — real but tolerable for v0.1

- **`line_sha` contradicts SPEC rule 3.** Spec says "tabs preserved"; code hashes `l.strip()`, so leading whitespace/indentation is ignored and a human re-indent keeps the line attested. Either use `l.rstrip()` (stricter, spec-conformant) or amend the spec — currently they disagree.
- **Canonical JSON is "whatever CPython's json.dumps does."** Stable in practice for str/int/None across 3.9–3.13, but the spec must pin it exactly (sorted keys, `(",", ":")` separators, `ensure_ascii`, decimal ints), and a golden test vector must be committed so non-Python verifiers have a reference. Also: the *stored* line uses spaced separators while the *signed* payload is compact — fine, but document that the signature is over the reconstructed compact form.
- **0-line contradiction in `render`:** `lines == 0` gives "0% attested — 0 of 0 lines" followed by "every considered line carries machine provenance." Add `if res["lines"] == 0: print("  no lines long enough to score")`.
- **`--json` with no evidence prints prose**, not JSON. Print `{"evidence": null}`.
- **Badge honesty:** the badge encodes only a percentage — an unsigned-transcript score renders identically to a cryptographically verified one. Include the evidence tier in the label (`...-87%25_signed` vs `_unsigned`) and refuse `--badge` when unverified. Also the docstring's "nothing leaves the machine" coexists with a shields.io URL that publishes the percentage to a third party whenever anyone views the README — caveat it.
- **`render`'s explanation omits formatter reflow** ("unattested = typed by hand, or written through a channel with no hook" — or *reflowed by a formatter*, per SPEC rule 4; reviewers will misread that as human).
- **`check` flags** are hand-rolled (`a.startswith("--")`); paths starting with `--` are unusable, unknown flags vanish silently, and `repo_root(paths[0])` assumes one repo for all args (files from a second repo get garbage relpaths). Use `argparse`, dedupe `list_files` output, compute repo per file. Add `--min-attested N` exit code for CI gating — currently `check` exits 0 even at 0%.
- **MIN_LEN=12 is duplicated as a magic literal in three files**, with *different* length semantics (strip vs whitespace-collapse) so the two layers score the same file differently. One constant, one definition.
- **Path portability:** records store `os.path.relpath` separators; verify on Windows joins with `\` and never matches. Write `path.replace(os.sep, "/")` and normalize on read.
- **Non-UTF-8 files:** hook hashes the true UTF-8 tool input; verifier hashes `errors="replace"` output → permanent stale/false-unattested. Document; or hash bytes with a declared encoding.
- **Temp files:** fine (mkstemp, 0600), but `sign()` reads `p + ".sig"` in text/locale mode — read bytes. And the hook will happily append through a symlinked (or FIFO) `.nhw/attest.jsonl` — a repo-side symlink redirects appends into an arbitrary user file, and a FIFO hangs the hook for its 10 s timeout per write. Check `os.path.islink` / `stat.S_ISFIFO` before opening.
- `verify.py` re-opens every file (once in `attested_lines`, once in `report_file`); `check_transcripts` silently `continue`s on file errors; dangling "(see the paper, §6)" reference with no paper in the repo.

---

## False-attestation taxonomy (question 3)

Counted attested though a human typed it:

1. **Forged ledger + repo-supplied `allowed_signers`** (P0-1) — total forgery.
2. **Content-hash reuse:** human types a line identical to any line the agent previously wrote to that path (ledger fallback) or *any* path (transcript weak tier). `import argparse` is 15 chars — the MIN_LEN bar does not stop common-line collisions.
3. **Order blindness:** agent writes an identical line *later*; the human's earlier line flips to attested. Neither layer records or checks ordering.
4. **The model-level one, which the spec papers over:** the key signs *the channel*, not *the author*. An agent told (including via prompt injection) to "rewrite this file unchanged" attests human-authored text; a human dictating to the agent gets machine provenance. SPEC rule 1 should say "passed through the attested agent channel," not "a machine produced the hunk." The name *NoHumanWrites* invites the stronger reading — say this explicitly in `--help` and the README, in one sentence, before someone quotes the badge in a hiring decision.

Counted unattested though the agent wrote it: partial-line edits (P1-1), duplicate/`replace_all` occurrences (P1-2), worktrees (P1-3), MultiEdit (P1-7), formatter reflow (spec-intended, but say so in output), stale transcript cache (P1-6), non-UTF-8 files, other harnesses with no hook.

---

## Portability (question 4)

3.9 breaks silently (P0-3) — the one portability claim that's currently false. OpenSSH ≥ 8.0 needed for `-Y` and `namespaces=`; macOS 13+/Ubuntu 20.04+/RHEL 8 all fine, but `setup-key.sh` should explicitly probe `ssh-keygen -Y sign -h` and fail loudly instead of relying on the smoke test. Windows: unsupported and the relpath separator bug guarantees it stays that way — say so in the docstring. `bash` dependency is fine; `hostname -s` is fine.

## Pre-v0.1 checklist (question 6)

1. **LICENSE (Apache-2.0) + NOTICE + license headers** — claimed in the brief, absent in the files.
2. **Tests, at minimum:** golden vector (committed test key + ledger + expected verify output — this pins canonicalization and sshsig compatibility); tamper tests (mutate each field, assert fail); the P0-1 forgery attack as a regression test; partial-line Edit; `replace_all` duplicates; CRLF/BOM/empty/huge; malformed-record fuzz of `load_ledger`; concurrent-append; `diff_added` fixture parsing; a 3.9 import smoke test.
3. **CI matrix:** Python 3.9–3.13 × Ubuntu/macOS, plus one old-OpenSSH leg.
4. **`pyproject.toml`** with entry point, `nhw/__init__.py` + `__version__`, `--version` flag; currently `from nhw import ...` only works from a checkout.
5. **Threat-model doc** (what the signature proves, key distribution, the channel-not-authorship caveat) and spec/code reconciliation — "most recent record whose hunk covers it" is not implemented (any matching record wins), `start`/`end` are recorded and never used, `signer` prefix is `ssh-ed25519:` not the spec's `ed25519:`, the recorded fingerprint isn't checked against the verifying key.

---

**Verdict: after fixes — the four P0s are each under ~20 lines, but as-is the tool's two headline guarantees (unforgeable provenance, never guesses) are both false, and the 3.9 hook silently no-ops.**

### H. minimax/minimax-m3
# Hostile Review: NoHumanWrites v0.1

I'll work through this as if I were the maintainer who has to ship this on Monday. I've ordered by severity. The short version: the signature pipeline is broken end-to-end, the `allowed_signers` trust model is a footgun, and the per-line fallback is going to attest lines that humans actually typed. None of these are subtle.

---

## CRITICAL — showstoppers, do not tag v0.1

### C1. Signature is read as text; the whole ledger pipeline is dead
**File:** `nhw/hook.py`, `sign()` (lines ~37–45), and the symmetric read in `nhw/verify.py`, `sig_ok()` (lines ~24–37).

`ssh-keygen -Y sign` writes `payload.sig` as the **OpenSSH binary signature blob** (`"SSHsig" || uint32 ver || string pubkey_alg || string hash_alg || string namespace || string reserved || string msg_hash || string sig`). Everything after the first ~40 bytes is arbitrary (the 64-byte Ed25519 signature is essentially random). You are doing:

```python
return open(p + ".sig").read()   # hook.py
...
s.write(rec["sig"].encode())     # verify.py
```

On Python 3, `open(...).read()` decodes UTF-8. The probability that 64 random bytes form valid UTF-8 is ≈ 2⁻²⁵⁶, so `read()` raises `UnicodeDecodeError`. The hook's outer `except Exception` swallows it, writes to `~/.nhw/hook.log`, and **no record is ever appended**. The smoke test in `setup-key.sh` doesn't check the verifier's percentage, so it never noticed.

If you somehow forced ASCII and got a string into the ledger, `json.loads` would then reject the line because JSON requires valid Unicode in strings, so the verifier would `try/except` past it in `load_ledger` and you'd still see zero coverage.

**Patch — hook.py:**
```python
import base64
def sign(payload: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(payload); p = f.name
    try:
        r = subprocess.run(["ssh-keygen","-Y","sign","-f",KEY,"-n",NAMESPACE,"-q",p],
                           check=True, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode("utf-8","replace"))
        return base64.b64encode(open(p + ".sig","rb").read()).decode("ascii")
    finally:
        for x in (p, p + ".sig"):
            try: os.unlink(x)
            except OSError: pass
```

**Patch — verify.py:**
```python
import base64
def sig_ok(rec, signers):
    if not signers: return False
    body = {k: v for k, v in rec.items() if k != "sig"}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    sig_bytes = base64.b64decode(rec["sig"])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sig") as s:
        s.write(sig_bytes); sp = s.name
    try:
        r = subprocess.run(["ssh-keygen","-Y","verify","-f",signers,"-I","nhw",
                            "-n",NAMESPACE,"-s",sp],
                           input=payload, capture_output=True)
        return r.returncode == 0
    finally:
        try: os.unlink(sp)
        except OSError: pass
```

Add a test in the smoke script that **fails** if the verifier reports 0% for a freshly-attested file.

---

### C2. `allowed_signers` trust model is upside-down
**File:** `nhw/verify.py`, `allowed_signers()` (lines ~19–23).

```python
for p in (os.path.join(repo, ".nhw", "allowed_signers"),
          os.path.expanduser("~/.nhw/allowed_signers")):
    if os.path.exists(p): return p
```

A malicious repository can drop `.nhw/allowed_signers` containing the attacker's public key, and the verifier will use it. Now the attacker (who has the corresponding private key) can sign any `attest.jsonl` they like, and `nohumanwrites.py check` will report a perfect score on a PR full of human-written malware. The whole point of a provenance ledger is to prevent exactly this.

The repository should never be the trust root for the repository's own attestations.

**Patch:**
```python
def allowed_signers(repo, allow_local=False):
    # Local file is opt-in and always warned about.
    if allow_local:
        local = os.path.join(repo, ".nhw", "allowed_signers")
        if os.path.exists(local):
            print(f"warning: trusting repo-local {local}", file=sys.stderr)
            return local
    p = os.path.expanduser("~/.nhw/allowed_signers")
    return p if os.path.exists(p) else None
```

Wire `allow_local` to a `--trust-repo-keys` flag (default off). For `check_ledger` in the CLI, do **not** pass it. Document that a repo can ship a suggested signers list but the verifier will only honour `~/.nhw/allowed_signers`.

---

### C3. Path injection: the hook will sign records for arbitrary filesystem paths
**File:** `nhw/hook.py`, `main()`.

`path` comes straight from `inp.get("file_path")` — controlled by the model. A misbehaving or compromised harness can call `Write` with `file_path: "/etc/passwd"`. The hook then:

1. Walks parents to find a repo root (it will find one at `/` only if you walk that far, but most setups have one at `/`, and even if not, `repo_root` returns `None` and the hook bails — so the write itself isn't a write. **But** if `/` happens to be a git worktree, or the agent's working directory is a repo, the record *is* appended).
2. The record's `path` field is `os.path.relpath(path, root)`. With `path=/etc/passwd` and `root=/home/user/proj`, that's `../../etc/passwd`.
3. The verifier, on `check src/`, ignores it (path filter). But `verify.py <repo>` with no file argument currently **doesn't exist**, and if you add `--all`, you walk those arbitrary paths. More importantly, the sliding window in `attested_lines` does `os.path.join(repo, rel)` with `rel="../../etc/passwd"` and `open()`s it — that's an arbitrary file read by a tool the user runs.

**Patches:**

a. Refuse paths that escape the repo after `relpath`:
```python
rel = os.path.relpath(path, root)
if rel.startswith("..") or os.path.isabs(rel):
    return
```

b. In the verifier, when given an explicit file list, validate the same way before opening.

---

### C4. Python 3.9 compatibility is broken on import
**File:** `nhw/hook.py` and `nhw/verify.py`.

```python
def repo_root(path: str) -> str | None:        # hook.py
def allowed_signers(repo: str) -> str | None:  # verify.py
```

PEP 604 `X | Y` syntax is **3.10+**. Without `from __future__ import annotations`, the annotations are evaluated at function-definition time and `str | None` raises `TypeError` on 3.9. The SPEC says "Python 3.9+". Either drop the runtime annotation (use `Optional[str]` from `typing`) or add the future import at the top of both files.

```python
from __future__ import annotations
```

---

### C5. `setup-key.sh` uses `hostname -s` which is not portable
**File:** `setup-key.sh`.

`hostname -s` is a GNU coreutils / util-linux thing. macOS `/bin/hostname` (BSD) does **not** support `-s` and exits non-zero under `set -e`. The script aborts before creating the key on macOS.

**Patch:**
```bash
NHW_HOST="$(hostname -s 2>/dev/null || hostname)"
ssh-keygen -q -t ed25519 -N "" -C "nhw-${NHW_HOST}" -f "$KEY"
```

While here: the `eval/hooktest.txt` artefact is left behind. Trap and `rm` it, and `gitignore` the `eval/` dir.

---

## HIGH — false attestations and correctness

### H1. `line_span` is wrong, and worse, the stored line numbers are unused
**File:** `nhw/hook.py`, `line_span()`.

```python
i = body.find(text.strip("\n"))
```

This is a substring search. It returns the **first** occurrence. If the agent writes a snippet that already exists elsewhere in the file (a common function, a comment block, an import), the line numbers are wrong. And the line numbers are *never used by the verifier anyway* — `attested_lines` only uses `hunk.lines` and `hunk.sha256`. The `start`/`end` fields in the record are decorative and the `line_span` work is dead.

Two fixes — pick one:

a. **Remove it.** Delete `line_span`, delete the call, drop `start`/`end` from the record, and update SPEC.md so verifiers don't come to depend on them.

b. **Use it.** In `attested_lines`, *seed* the sliding window at `start - 1` (with bounds checks) and only fall back to a full slide if the seed misses. This makes the line numbers meaningful and speeds up verification for large files.

Either way, the current code is misleading.

### H2. CRLF mismatch makes `line_span` return `None` silently
**File:** `nhw/hook.py`.

`text` from the tool input is LF-normalised by Claude Code, but `body` on disk is read raw. `body.find(text)` fails on CRLF files, so every Windows-checkout record carries `start: null, end: null`. Combined with H1, this means the spec is lying about what's stored. If you keep line numbers, normalise the file body too:

```python
body = open(path, errors="replace").read().replace("\r\n","\n")
```

### H3. The sliding-window hunk match produces false positives
**File:** `nhw/verify.py`, `attested_lines()`.

You slide a window of `n` lines over the whole file and accept the first match. If the agent wrote a function, a human later copies that function (or another copy of it) elsewhere in the file, or a formatter re-emits a similar block, the verifier attributes those lines to the agent. The "first match wins" behaviour means a single human paste at the top of a file can claim the rest of the file as attested.

For v0.1, at minimum:

- Use the line number hint (H1.b) and require the match to start within ±1 line of the recorded `start` (when available), falling back to a full slide only when `start` is null.
- When multiple windows match, prefer the one whose start is closest to the recorded `start`.

### H4. The per-line fallback certifies lines a human restored
**File:** `nhw/verify.py`, `attested_lines()`, the `stale` branch.

```python
if want_lines:
    for i, l in enumerate(lines, 1):
        if len(l.strip()) >= 12 and hashlib.sha256(l.strip().encode()).hexdigest()[:16] in want_lines:
            covered.add(i)
```

Scenario: agent writes `foo(); bar(); baz();` → all three lines get into `line_sha`. A human later deletes `bar();` then retypes it. The retyped `bar();` matches the recorded hash byte-for-byte and is reported as **attested**. The human typing that line is the exact case the ledger is supposed to detect, and you just blessed it.

The per-line fallback is a footgun. Either:

- Remove it and report those lines as uncovered (matching the spec's "formatters change more than whitespace → new hunk" rule), or
- Mark them as `attested:weak` in the report so a reviewer can tell, and don't count them in the badge numerator.

The current spec text says "lines that were reflowed are reported uncovered, which is intended" — your code contradicts the spec on this point. Pick one and be consistent.

### H5. Transcript weak-match creates cross-file false positives
**File:** `nhw/attest.py`, `attribute()`.

```python
weak = set().union(*per_file.values()) if per_file else set()
...
elif k in weak: out["weak"] += 1
```

`check_transcripts` in the CLI then counts `weak` as attested:
```python
tot += r["considered"]; un += len(r["unattested"])
```
because `unattested` is only the truly unmatched list.

If the agent ever wrote `print("usage: see README")` to `/tmp/scratch.py`, every human who later types that string in any file is reported as machine-attested. For boilerplate-heavy code (imports, headers, common error messages), this is going to be a *lot* of false positives.

**Patch:** either don't union across files (drop `weak`), or compute it but don't include it in the headline percentage. The CLI should default to `strong`-only and offer `--include-weak` for the curious.

### H6. Transcript cache has no invalidation and lives at a hardcoded absolute path
**File:** `nhw/attest.py`, `CACHE`.

`CACHE = "~/nohumanwrites/eval/attested-index.json"`. Two problems:

1. **Hardcoded absolute path under the user's `$HOME`.** Breaks any user whose checkout isn't at `~/nohumanwrites`. Move to `XDG_CACHE_HOME` / `~/.cache/nohumanwrites/` and respect env override.
2. **No invalidation.** The cache is built once and reused forever. If the user adds new transcripts (which happens on every Claude Code session), the cache is stale and attribution silently misses everything new. Add an mtime check: if any file under `LOGDIR` is newer than `CACHE`, rebuild.

```python
def load_index(rebuild=False):
    if not rebuild and os.path.exists(CACHE):
        newest = max((os.path.getmtime(p) for p in glob.glob(...)), default=0)
        if newest <= os.path.getmtime(CACHE):
            d = json.load(open(CACHE))
            return {k: set(v) for k, v in d["per_file"].items()}, d["stats"]
    ...
```

Also, the cache write isn't atomic — two concurrent `check --transcripts` runs can corrupt the JSON. Write to a temp file in the same dir, then `os.replace`.

### H7. Concurrent hook runs are not safe
**File:** `nhw/hook.py`.

`open(..., "a").write(json.dumps(rec) + "\n")` is atomic only for writes < `PIPE_BUF` (4096 on Linux). A record with a long hunk or many `line_sha` entries can exceed that and interleave with another concurrent hook invocation. Take an exclusive `flock` on a sentinel file in `.nhw/`:

```python
import fcntl
lock_path = os.path.join(root, ".nhw", ".lock")
with open(lock_path, "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    with open(os.path.join(root, ".nhw", "attest.jsonl"), "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
```

`fcntl` is POSIX; on Windows you'd need `msvcrt`, but Claude Code's hook runtime is Unix-y.

### H8. `verify.py` allows repo-local `allowed_signers` via the path-walk too
Same as C2 from the entry point. Additionally, the public CLI `nohumanwrites.py` calls `check_ledger(repo, files)` which calls `verify.allowed_signers(repo)` — so the unfixed behaviour leaks into the user-facing command.

---

## MEDIUM — portability, UX, hardening

### M1. `is_text` rejects UTF-16 / UTF-8-BOM files with non-ASCII first char
**File:** `nohumanwrites.py`. Reading 4096 bytes and checking for `b"\x00"` flags UTF-16 (BOM: `FF FE` or `FE FF`) as binary. Fine for v0.1; add a BOM sniff (`b"\xef\xbb\xbf"`, `b"\xff\xfe"`, `b"\xfe\xff"`) before the null-byte test.

### M2. `is_text` allows huge binary files
The `list_files` size cap is 2 MB but `is_text` doesn't enforce it — and binary files under 2 MB pass the null-byte sniff (e.g. a PNG header is non-null, but a 1 MB PNG will still be scanned as if it were text and the verifier will then read it with `errors="replace"` and split on `\n`). Add an extension denylist or a stricter heuristic (e.g., `chardet` is forbidden by "standard library only"; use a 0-byte-ratio check after reading).

### M3. `settings.json` is not written atomically
**File:** `nohumanwrites.py`, `cmd_setup()`.

```python
json.dump(s, open(settings, "w"), indent=2)
```

A SIGKILL between `open` (truncate) and `dump` leaves the user with a zero-byte `settings.json` and a broken Claude Code install. Write to `settings + ".tmp"` and `os.replace`.

### M4. `ssh-keygen` is not on `$PATH` for some hooks
The hook assumes `ssh-keygen` resolves. On some minimal containers or hardened macOS, the binary is at `/usr/bin/ssh-keygen` or `/opt/homebrew/bin/ssh-keygen`. Use `shutil.which` and bail with a clear message instead of a stack trace in `~/.nhw/hook.log`.

### M5. OpenSSH < 8.0 fails silently
`ssh-keygen -Y sign` is OpenSSH 8.0 (2019). RHEL 7, CentOS 7, some older Ubuntu LTS AMIs, and every macOS before Big Sur are < 8.0. The hook will raise `ssh-keygen: illegal option -- Y`, the exception is swallowed, and the user gets no ledger. Add a one-time version check in `setup-key.sh` and refuse to install.

### M6. The "evidence" string is shown without an `unverified` warning when the ledger is used
**File:** `nohumanwrites.py`, `render()`. If `check_ledger` returns a result but `verified_signatures` is `False` (no `~/.nhw/allowed_signers`), the output is:

```
NoHumanWrites: 80% attested — 80 of 100 lines
  evidence: signed ledger (.nhw/attest.jsonl)
```

That's a lie — it's a ledger, but the signatures weren't checked, so it's the same evidence class as the transcript path. Show "(no signature check)" in this case (you already build that string but never use it in `check_ledger`'s return — `verified_signatures: bool(signers)` is just `True/False`, the annotation is dropped).

### M7. The hook doesn't know the model
SPEC.md says `producer.model: "claude-fable-5-1"`. The hook event doesn't carry the model in PostToolUse. Either drop the field from the spec, or grab it from a `~/.claude/session-env` file or a separate `producer` extension populated by a sibling `SessionStart` hook. As-is, every record omits the field silently.

### M8. `git diff -U0` parsing is fragile
**File:** `nhw/verify.py`, `diff_added()`. The regex `r"\+(\d+)(?:,(\d+))?"` will match `+1,2` inside a hunk header comment if anyone has one. More importantly, `git diff` can produce a `diff --git a/x b/x` line and a `rename from` / `rename to` block where the new path is in a `+++ b/` line but the line numbers belong to a different file. You're fine for plain `+ b/path` lines but not for the `rename to` case. Use `--diff-filter=AM` and pass `--find-renames` explicitly, or just use `git diff --name-only -z` to enumerate files and `git log -p` to enumerate hunks per file. For v0.1, at least gate on `diff --cc` / combined diff being absent.

---

## LOW

- `verify.py` accepts no `--help` other than the docstring print. Add proper argparse.
- `eval/attested-index.json` is committed by accident risk — the path suggests it should be gitignored. Add `.gitignore` for `eval/`.
- The `v` field is set but never validated. A future v2 record would be parsed and likely mis-verified. Add `if rec.get("v") != 1: continue` in `load_ledger`.
- `fingerprint()` returns `"unknown"` silently. If `ssh-keygen -lf` fails, the record gets signed with signer `"ssh-ed25519:unknown"`. Bail instead.
- `os.path.dirname(LOG)` is created on every error; the `makedirs(..., exist_ok=True)` is fine but could move outside the except.
- The `MIN_LEN = 12` magic number is duplicated in `attest.py`'s default, the CLI's check, and the hook's filter. Put it in one place.
- `attest.attribute` returns `weak` count but the CLI never uses it; dead field.
- `badge` URL has no `?` cache-buster; if a user re-runs after a change, the shields.io cache hides the new value for minutes. Add `&cacheSeconds=30` or just don't bother — it's a badge, not a build artifact.

---

## Maintainer checklist before v0.1

| Item | Status |
|---|---|
| License header in every `.py` (SPDX: Apache-2.0) | Missing |
| `pyproject.toml` so it's `pip install`-able | Missing |
| `__version__ = "0.1.0"` exposed via `nohumanwrites --version` | Missing |
| Test suite (`pytest`) with golden ledger + tamper tests | Missing — the smoke test in `setup-key.sh` is not a test |
| CI matrix: Linux + macOS, Python 3.9/3.10/3.12 | Missing |
| `CHANGELOG.md` | Missing |
| README that says **what this is not** (not a content classifier, not a human-vs-AI detector) | Missing |
| `gitignore` for `eval/`, `__pycache__/`, `*.pyc` | Missing |
| Atomic writes for `settings.json` and the cache | Missing |
| Atomic / locked writes for the ledger | Missing (H7) |
| `v` field validated, model field added or removed from spec | Open (M7) |
| `allowed_signers` trust model documented and enforced | Open (C2) |
| `line_sha` semantics documented in spec (or removed) | Open (H4) |
| Per-line fallback behaviour reconciled with SPEC.md rule 4 | Open (H4) |
| `hostname -s` portability (C5), `from __future__ import annotations` (C4) | Open |
| OpenSSH 8.0+ preflight in `setup-key.sh` (M5) | Open |
| Decide on transcript cache location + invalidation (H6) | Open |
| False-positive rate statement in README (what `attested` does and does not mean) | Open |

---

## Concrete fix priority (the order I'd merge)

1. C1 — signature base64. The whole pipeline is dead without it.
2. C2 — `allowed_signers` trust model. Security footgun.
3. C3 — path containment. Arbitrary file read on `check`.
4. C4 + C5 — `from __future__ import annotations`, `hostname` portability. 5 minutes.
5. H4 — decide and implement per-line fallback. Spec contradiction.
6. H1 + H2 — kill or use `line_span`, fix CRLF.
7. H5 — drop or demote transcript `weak` match.
8. H6 — transcript cache: location + mtime invalidation + atomic write.
9. H7 — `flock` on the ledger.
10. M3 — atomic `settings.json` write.
11. M5 — OpenSSH version check in `setup-key.sh`.
12. Everything else.

---

## Verdict

**Not yet.** Tag v0.1 after at minimum C1, C2, C3, C4, C5, H4, H5 are fixed and a pytest suite covering round-trip sign/verify, signature tampering, repo-local-signer rejection, and CRLF/empty-file paths is in CI.

## Round 2 — cross-check (each critiques the anonymised pool)

### openai/gpt-5.6-luna-pro reviews
## Overall assessment

The answers converge on the main release blockers:

- repository-controlled `allowed_signers` makes the trust root circular;
- Python 3.9 support is broken;
- current output conflates “unverified/untracked” with “human”;
- the per-line fallback and transcript weak matching produce false attestations;
- malformed or hostile ledgers can crash or exhaust the verifier;
- append-only JSONL writes are not concurrency-safe;
- path, encoding, CRLF, edit-location, and Git-diff handling are incomplete.

The implementation is not ready for a public provenance badge.

## Strongest answer

**Answer D is strongest overall.** It is broad, prioritised, and catches several issues the others miss:

- the `allowed_signers` circular trust root;
- the distinction between “no trusted signatures” and “0% attested”;
- linked worktrees where `.git` is a file;
- locale-dependent decoding and reproducibility;
- the `added or range(...)` bug that scores the entire file when a diff has no added lines;
- stale and cross-project transcript attribution;
- Edit context lines being signed as if newly authored;
- canonicalisation/spec drift;
- malicious Git configuration during diff execution;
- the lack of sequence/order semantics and the ignored `start`/`end` fields;
- setup smoke tests polluting the real repository.

It also gives a useful false-attestation/false-negative taxonomy and a reasonable pre-release test matrix.

That said, D is not completely correct. Its proposed default behavior still permits repository signers as a warned fallback:

```python
if repo_file exists:
    return repo_file, "SELF-ASSERTED repo keyring"
```

That is acceptable only if the result is explicitly **untrusted/advisory** and excluded from a cryptographic coverage score. It should not be treated as equivalent to a user-pinned signer file.

## Significant errors in the answers

### Answer H has a major false finding

H claims that `ssh-keygen -Y sign` produces a binary signature that cannot be read as text, and therefore that the entire signing pipeline is dead.

That is not generally correct. OpenSSH SSHSIG files produced by `ssh-keygen -Y sign` are normally ASCII armored:

```text
-----BEGIN SSH SIGNATURE-----
...
-----END SSH SIGNATURE-----
```

The existing `open(...).read()` / JSON string approach is therefore not inherently broken. It is still worth reading and writing the signature with explicit UTF-8, bounding its size, and perhaps storing a defined representation, but **Answer H’s C1 is not a valid release blocker**. Its priority list is consequently distorted.

H also overstates the path traversal issue. A malicious ledger record containing `../../etc/passwd` is dangerous only when the verifier uses that record’s path as a path to open. In the current code, `attested_lines()` is called for a caller-supplied `rel`; a malformed record alone does not make the verifier walk every arbitrary path. Nevertheless, repository-relative path validation is still required, especially for multi-path CLI use and future “verify all” behavior.

### Answer B’s `Counter` fix is insufficient

Using a `Counter` limits how many duplicate lines can be credited, but it does not establish which current occurrence corresponds to the signed occurrence. A human can delete an agent line and retype the same line; the Counter still credits it. It also does not solve copies at different locations.

For v0.1, the safe fix is to **remove the fallback from the headline score**, or report it separately as an ambiguous historical content match. A full hash and a Counter do not turn content equality into provenance.

B also incorrectly says CRLF is “handled correctly”; `line_span()` searches for the unnormalised tool text in a text-decoded file and can fail on CRLF. It misses the ignored `start`/`end` semantics, incomplete edit handling, signing of failed tool requests, and the “most recent record” disagreement.

### Several answers understate the trust-model problem

Some answers suggest allowing a repository signer file with a warning. That is only safe if the result is not presented as verified provenance. A repository can legitimately publish a signer list for a project, but that list requires an **out-of-band trust decision**:

- user-pinned fingerprint;
- trusted main branch/ref;
- organization configuration;
- CI-injected signer file;
- explicit TOFU with a warning.

The current default—repository file first—is unsafe.

### “Most recent” is not implemented

The specification says:

> find the most recent record whose hunk covers it

The verifier unions coverage from every valid record and ignores `ts`, `start`, and `end`. This is not a cosmetic mismatch. It permits old records to continue covering lines after deletion, movement, or human retyping.

A timestamp alone is inadequate because it is self-asserted and can collide or be backdated. Add a ledger sequence number allocated under the append lock, or explicitly change the specification to say “union of surviving matching content” and accept the weaker semantics.

### The Python 3.9 issue is a runtime `TypeError`, not necessarily a syntax error

`str | None` is parsed as an expression on Python 3.9 but evaluates `type.__or__` at function definition time. The practical result is an import-time `TypeError`, not normally a syntax error. The impact identified by the answers is correct: the hook catches it, exits 0, and silently stops recording.

Use `typing.Optional` if 3.9 support is real. A future-annotations import is also viable, but test it explicitly under 3.9.

## Ranked release blockers

### P0 — Fix before any tag

#### 1. Establish a non-circular trust model

Do not prefer:

```python
<repo>/.nhw/allowed_signers
```

Use an explicit user-owned or CI-provided trust configuration:

```python
~/.config/nohumanwrites/allowed_signers
```

or:

```bash
nohumanwrites check --allowed-signers /trusted/path repo
```

Repository-provided keys may be displayed as **advisory/self-asserted**, but must not produce a “verified” score by default.

The report must include:

```json
{
  "trust_source": "user-configured",
  "verified_records": 17,
  "invalid_records": 2,
  "unknown_signers": 1
}
```

Do not use:

```python
"verified_signatures": bool(signers)
```

That only says a file exists.

#### 2. Make output three-state

These states must be distinct:

1. **Verified machine-channel coverage**
2. **Unattested / no matching provenance**
3. **Unverifiable** — no trusted key, invalid signatures, malformed ledger, or unsupported verifier

Never report 0% when signatures could not be checked. Never say “typed by hand.” Use:

```text
no verifiable machine provenance
```

not:

```text
typed by hand
```

A badge must be refused or explicitly tiered when the evidence is unsigned, transcript-only, self-asserted, or unverifiable.

#### 3. Remove or demote ambiguous matching

The current fallback:

```python
hash(line.strip()) in want_lines
```

can credit any identical line anywhere in the file. The transcript layer is weaker still because it matches lines from any path on the machine.

For v0.1:

- remove `line_sha` fallback from the headline score, or;
- report it as `ambiguous_content_match`, never as verified coverage;
- remove transcript `weak` matches from the attested numerator;
- do not use truncated 64-bit hashes for a provenance claim;
- do not strip indentation if indentation is part of the declared normalization.

Content equality is not occurrence identity.

#### 4. Validate all untrusted ledger input

A repository’s `.nhw/attest.jsonl` is attacker-controlled input. Validate before signature verification:

- record must be an object;
- `v == 1`;
- bounded string lengths;
- valid repository-relative path;
- integer `hunk.lines` within limits;
- 64-character lowercase SHA-256;
- bounded signature size;
- `line_sha` is a list of valid hashes;
- required producer and signer fields have correct types.

Malformed records must be counted and reported, not silently discarded or allowed to crash the process.

Also cap:

- total ledger size;
- record count;
- records per path;
- hunk line count;
- total verification work.

#### 5. Make append safe

Use a per-ledger lock and one encoded write while holding it. Allocate a monotonically increasing `seq` under the same lock.

On POSIX:

```python
with open(lock_path, "w") as lock:
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
    with open(ledger, "ab", buffering=0) as out:
        out.write(line_bytes)
        os.fsync(out.fileno())
```

Report malformed/truncated ledger lines. Do not silently turn concurrency corruption into missing provenance.

#### 6. Define bytes, encoding, and newline normalization

The hook, verifier, and transcript code currently use different and locale-dependent text paths.

Choose one explicit policy:

- UTF-8 only, rejecting invalid UTF-8; or
- byte-based hashing with a documented newline transformation.

Define precisely:

- LF, CRLF, and lone CR behavior;
- trailing whitespace behavior;
- preservation of tabs and indentation;
- final newline behavior;
- empty text and blank lines;
- BOM handling;
- whether outer blank lines are retained.

The current `.strip("\n")` changes the representation and can make line counts inconsistent with the stored `lines` field.

Use shared normalization code and golden test vectors.

## P1 — Required correctness fixes

### Hook must verify the actual operation

The hook signs `content` or `new_string` without checking:

- whether the tool succeeded;
- whether the file exists afterward;
- whether a formatter changed the result;
- whether another process overwrote it;
- whether an Edit matched exactly one `old_string`.

At minimum, inspect the PostToolUse result and label records as “requested” if actual success cannot be established.

For Edit:

- use `old_string` and replacement context;
- reject ambiguous matches;
- handle partial-line replacements by expanding to containing lines or record them separately;
- do not sign unchanged context lines as newly authored unless the product explicitly claims channel provenance rather than changed-line authorship.

Record empty writes and deletions explicitly, or state that v0.1 does not cover them.

### Fix path containment and symlink behavior

Canonicalize paths with `realpath`, reject:

- absolute ledger paths;
- `..` escapes;
- files resolving outside the repository;
- unexpected symlink/FIFO ledger targets.

Use POSIX `/` separators in records. Handle multi-repository CLI arguments explicitly rather than scoring all files against the first repository’s ledger.

### Fix repository discovery

Use `os.path.exists(".git")`, not `isdir`, so linked worktrees and submodules are not silently skipped. Better, use:

```bash
git -C path rev-parse --show-toplevel
```

and handle failures clearly.

### Fix Git diff processing

The current parser is not safe for quoted, escaped, Unicode, newline-containing, renamed, deleted, or binary paths. It also ignores subprocess failure.

Use a machine-readable Git format or a robust parser, disable external diff/text conversion:

```bash
git -c diff.external= -c core.fsmonitor=false \
    diff --no-ext-diff --no-textconv -U0 ...
```

Fix this bug:

```python
added or range(...)
```

An empty added set means “no added lines,” not “score the entire file.” Use:

```python
pool = range(1, len(lines) + 1) if added is None else added
```

Exclude `.nhw` metadata from the code coverage score. Decide explicitly how untracked files, renames, deletions, and binary files are handled.

### Fix matching semantics

The verifier currently:

- scans every record;
- scans every window;
- uses the first matching window only;
- ignores recorded `start`/`end`;
- unions old and new records;
- falls back to all matching lines globally.

At minimum:

- validate `n`;
- try the recorded span first;
- use a defined fallback policy;
- report duplicate/ambiguous matches;
- implement sequence ordering or change the spec;
- separate exact-hunk coverage from weaker content matches.

### Fix transcript evidence

Transcript records are unsigned and do not prove successful writes. The index must:

- check corresponding tool results;
- invalidate or rebuild when logs change;
- use atomic cache writes;
- handle corrupt cache files;
- use realpath consistently;
- keep strong same-path matches separate from weak cross-path content matches;
- never present weak matches as verified provenance.

The public CLI currently cannot expose the rebuild option even though the underlying module supports it.

## P2 — Portability and release hygiene

Before release:

- Python 3.9–current CI;
- macOS and Linux CI;
- explicit OpenSSH `-Y` preflight and missing-tool handling;
- document Unix-only behavior if using `fcntl`;
- avoid `hostname -s` portability assumptions;
- use `sys.executable` or a validated interpreter in installed hooks;
- atomic `settings.json` replacement with backup and mode preservation;
- atomic transcript cache writes;
- do not clobber existing `allowed_signers`;
- setup smoke test in a temporary Git repository, not the project checkout;
- make the smoke test assert a successful signature verification;
- fix the “single-file CLI” claim or package properly with `pyproject.toml`;
- add `LICENSE`, Apache-2.0 SPDX headers, version metadata, README threat model, and security policy.

## Required tests

At minimum:

- signed hook-to-verifier round trip;
- tampering with every signed field;
- trusted versus repository-supplied signer file;
- wrong/unbound `signer` fingerprint;
- malformed JSON and valid-but-malformed objects;
- oversized records and hunks;
- concurrent append;
- CRLF/LF/lone CR and final-newline cases;
- Unicode and invalid-UTF-8 policy;
- empty writes, deletion edits, partial-line edits, repeated edit matches;
- duplicate hunks and duplicate lines;
- human retyping of an old agent line;
- worktrees with `.git` files;
- symlink/path traversal cases;
- quoted and Unicode Git paths;
- delete-only diff and empty added set;
- failed Git command;
- missing/old `ssh-keygen`;
- stale/corrupt transcript cache;
- Python 3.9 import and end-to-end execution;
- zero considered lines must produce `n/a`, not 100%.

## Final judgement

The answers correctly identify the principal risks, but H should not be selected because its claimed binary-signature failure is wrong, and B is too narrow and proposes an inadequate Counter-based fix. D provides the best overall review, with F close behind in breadth but containing the same false signature diagnosis.

**Verdict: tag v0.1 not yet; tag only after the trust model, evidence-state UX, false-attestation matching, input validation, path/encoding semantics, and concurrency fixes are implemented and tested.**

### google/gemini-3.1-pro-preview reviews
An analysis of the reviews reveals a mix of excellent catches and one major hallucination. Here is the breakdown of errors, disagreements, and the strongest answer.

### Errors and Disagreements

1. **Answer H's Hallucinated "Binary Signature" (Critical Error):** Answer H claims as its top issue that `ssh-keygen -Y sign` outputs a binary blob, which will cause `open().read()` to crash with a `UnicodeDecodeError`. This is factually incorrect. OpenSSH signatures created with `-Y sign` are ASCII-armored (they begin with `-----BEGIN SSH SIGNATURE-----` and contain base64). `open().read()` works perfectly fine. Answer H's C1 is entirely fabricated.
2. **Answer B's Symlink Race:** Answer B claims `p + ".sig"` is vulnerable to a symlink race because it is in `/tmp`. Because `NamedTemporaryFile` generates a cryptographically random filename, an attacker would have to guess the filename in the millisecond before `ssh-keygen` runs to pre-create a symlink. While using `TemporaryDirectory` is cleaner, Answer B overstates this as a "High" severity flaw.
3. **Locale-Dependent Hashing:** Answers D and F correctly identify a subtle but fatal flaw: `open(path, errors="replace")` without an explicit encoding uses the system's default locale. On a CI server with `LC_ALL=C`, non-ASCII characters decode differently than on a developer's macOS machine, causing all hashes to mismatch and destroying reproducibility. Most other answers miss this.
4. **Git Worktrees:** Answers D and G correctly point out that `os.path.isdir(".git")` fails for git worktrees and submodules, where `.git` is a text file, not a directory. This silently disables the hook for those users.
5. **Git Diff Code Execution:** Answer G brilliantly points out that running `git diff` in an untrusted repository can lead to arbitrary code execution if the repository includes a malicious `.git/config` defining `diff.external` or `textconv` drivers. 
6. **Empty Diff Fallback:** Answer D catches a nasty logic bug in `verify.py`: if `added` is an empty set (e.g., a PR with only deletions or mode changes), `consider` falls back to `range(1, len(lines) + 1)`, falsely scoring the entire file instead of skipping it.

### Strongest Answer

**Answer D is the strongest.** It provides an incredibly thorough, accurate, and adversarial analysis. It catches the glaring architectural flaws (the circular trust root, the Python 3.9 `str | None` crash, the concurrent write interleaving) while also finding the deepest edge cases: the locale-dependent hashing, the `.git` file vs. directory bug, the empty `added` set bug, and Git's C-quoting of non-ASCII paths (`+++ "b/\303\251.py"`). Its breakdown of exactly how the tool falsely attests human code is spot on. 

*(Answer G is a close runner-up due to its catch of the `git diff` RCE vector, but Answer D is more comprehensive overall).*

### What a Correct/Safe Final Answer Must Include

To safely tag v0.1, the implementation must address the following:

**1. Security & Trust Boundaries**
*   **Fix Circular Trust:** The verifier must *never* trust `<repo>/.nhw/allowed_signers` by default. The trust root must be passed explicitly or loaded from the user's `~/.nhw/` directory.
*   **Prevent Git Diff RCE:** `subprocess.run(["git", "diff", ...])` must be invoked with config overrides (e.g., `-c diff.external= -c core.fsmonitor=false`) to prevent the execution of repo-supplied scripts.
*   **Path Traversal:** The verifier must reject `path` or `rel` values in the JSONL that contain `../` or absolute paths to prevent arbitrary file reads.

**2. Correctness & Portability**
*   **Python 3.9 Compatibility:** The `str | None` type hints must be replaced with `typing.Optional` or preceded by `from __future__ import annotations`.
*   **Deterministic Hashing:** File reading and JSON serialization must explicitly specify `encoding="utf-8"` (and `ensure_ascii=True` for JSON) to ensure hashes match across different operating systems and CI locales.
*   **Concurrency:** Appending to `.nhw/attest.jsonl` must use file locking (e.g., `fcntl.flock`) and atomic writes to prevent interleaved JSON lines when multiple agents/hooks run simultaneously.
*   **Worktree Support:** `repo_root` must use `os.path.exists(".git")` or `git rev-parse --show-toplevel` to support git worktrees and submodules.

**3. Provenance Logic & False Attestations**
*   **Restrict Line Fallback:** The per-line hash fallback and the transcript "weak" match allow a human to type a common line (e.g., `import os`) and have it falsely flagged as AI-attested because the AI wrote it elsewhere. These must be removed, strictly bounded by proximity, or separated out of the headline percentage.
*   **Robust Parsing:** The verifier must validate the JSON schema of ledger records (types, bounds) to prevent malformed data from crashing the tool. `git diff` parsing must handle quoted paths and empty added-line sets correctly.

### qwen/qwen3.8-max reviews
## Strongest answer

**Answer D is the strongest overall**, but it is not complete.

It is the best because it correctly treats the following as release-blocking, with concrete fixes:

- Repo-supplied `.nhw/allowed_signers` creates circular trust.
- `verified_signatures: bool(signers)` is dishonest: it means “a key file exists”, not “signatures verified”.
- Python 3.9 support is broken by `str | None` annotations.
- Git worktrees/submodules are missed because `.git` may be a file.
- Concurrent hook appends can corrupt the JSONL ledger.
- The verifier is fragile against malformed attacker-controlled ledger records.
- Locale-dependent text decoding makes verification non-reproducible.
- `--diff` has a real bug where an empty added-line set causes whole-file scoring.
- Transcript mode over-claims via weak cross-file matches and has a stale hardcoded cache.
- `MultiEdit`, failed tool writes, and `Bash` writes break the “every agent write” claim.
- Canonical JSON is underspecified for non-Python verifiers.
- Setup writes and smoke tests are unsafe/non-assertive.
- The output needs an explicit trust source, verified counts, and honest “unattested / unknown” language.

However, **Answer D misses at least two important issues that Answer G catches**:

1. Running `git diff` inside an untrusted repository should disable repo-config-driven execution paths such as external diff/textconv/fsmonitor where applicable.
2. Partial-line `Edit` payloads can be signed as fragments that never match whole-file lines, causing false-unattested lines.

Answer A is also strong and broader than D in a few areas, especially signer-field binding, “most recent record” spec mismatch, canonicalisation, and test requirements. A correct final review should combine D’s prioritisation with G’s missing correctness/security items and A’s spec/signature-model rigor.

---

# Independent review: what must be fixed before v0.1

Ranked by severity.

---

## P0-1: The trust root is inside the repository being attested

`nhw/verify.py`:

```python
def allowed_signers(repo: str) -> str | None:
    for p in (os.path.join(repo, ".nhw", "allowed_signers"),
              os.path.expanduser("~/.nhw/allowed_signers")):
        if os.path.exists(p):
            return p
    return None
```

This prefers the repo’s own key file. A malicious repository can commit:

```text
.nhw/allowed_signers
.nhw/attest.jsonl
```

where the ledger is signed by the attacker’s key and the repo supplies that attacker key as trusted. The verifier will then report a high or perfect attestation score.

This defeats the entire provenance model.

### Required fix

For v0.1, do not trust a repo-local `allowed_signers` file by default.

```python
def allowed_signers(repo: str, explicit: str | None = None) -> str | None:
    if explicit:
        p = os.path.abspath(os.path.expanduser(explicit))
        return p if os.path.isfile(p) else None

    p = os.path.expanduser("~/.nhw/allowed_signers")
    return p if os.path.isfile(p) else None
```

If repo-local keys are ever allowed, require an explicit flag such as:

```text
--trust-repo-signers
```

and print a loud warning that the score is self-attested.

For PR review, the safer model is to load signers from a trusted ref, not the working tree being scored:

```bash
git show origin/main:.nhw/allowed_signers
```

or use an out-of-band pinned keyring.

The output must also state which trust source was used:

```text
trust source: ~/.nhw/allowed_signers
```

or:

```text
trust source: repo-local allowed_signers — self-asserted, circular trust
```

---

## P0-2: `verified_signatures` is false/misleading

`nohumanwrites.py`:

```python
return {"evidence": "signed ledger (.nhw/attest.jsonl)",
        "verified_signatures": bool(signers),
        ...}
```

This is true if a signers file exists, even if:

- no record verifies;
- `ssh-keygen` is missing;
- the ledger is malformed;
- the repo supplied its own attacker key;
- all signatures are invalid.

Also, `check_ledger()` discards the `verified` and `stale` counts returned by `verify.attested_lines()`.

### Required fix

`check_ledger()` must aggregate and return real counts:

```json
{
  "records": 17,
  "verified_records": 12,
  "invalid_records": 3,
  "malformed_records": 1,
  "stale_records": 2,
  "trust_source": "~/.nhw/allowed_signers"
}
```

`verified_signatures` must mean:

```python
verified_records > 0
```

If a ledger exists but zero records verify, the tool should not print a normal attestation percentage. It should print something like:

```text
Ledger present, but 0/17 records verified against trusted keys.
No provenance score is given.
```

Do not silently fall back to transcripts unless the user explicitly asked for transcript mode.

---

## P0-3: Python 3.9 support is broken, and the hook fails silently

`nhw/hook.py` and `nhw/verify.py` use:

```python
def repo_root(path: str) -> str | None:
```

and:

```python
def allowed_signers(repo: str) -> str | None:
```

PEP 604 union syntax is Python 3.10+. On Python 3.9 this raises `TypeError` at import/definition time. It is not a `SyntaxError`, but it still breaks the tool.

This is especially bad in `hook.py` because the outer exception handler turns import/runtime failure into:

```python
sys.exit(0)
```

So on Python 3.9 the hook can silently never attest anything.

### Required fix

Add this near the top of `nhw/hook.py` and `nhw/verify.py`:

```python
from __future__ import annotations
```

or replace annotations with:

```python
from typing import Optional

def repo_root(path: str) -> Optional[str]:
```

CI must test Python 3.9 explicitly.

---

## P0-4: The verifier can crash or be DoSed by attacker-controlled ledger records

`verify.load_ledger()` accepts any parseable JSON:

```python
for ln in open(p):
    try: out.append(json.loads(ln))
    except Exception: pass
```

Then `attested_lines()` does:

```python
n = r["hunk"]["lines"]
want = r["hunk"]["sha256"]
```

and:

```python
s.write(rec["sig"].encode())
```

A malicious ledger can contain:

```json
{}
```

or:

```json
{"path":"x","hunk":{"lines":"not-an-int"}}
```

or huge strings/arrays. This can crash the verifier or cause excessive CPU/subprocess load.

Also, `sig_ok()` launches one `ssh-keygen` process per record. A hostile ledger with thousands of records is a fork-bomb-like DoS.

### Required fix

Add strict schema validation before signature verification.

Minimum validator:

```python
def _valid_record(r):
    if not isinstance(r, dict):
        return False
    if r.get("v") != 1:
        return False
    if not isinstance(r.get("path"), str) or not r["path"]:
        return False
    if ".." in r["path"].split("/") or r["path"].startswith("/"):
        return False

    h = r.get("hunk")
    if not isinstance(h, dict):
        return False

    lines = h.get("lines")
    if not isinstance(lines, int) or lines < 0 or lines > 100_000:
        return False

    sha = h.get("sha256")
    if not isinstance(sha, str) or len(sha) != 64:
        return False

    line_sha = h.get("line_sha", [])
    if not isinstance(line_sha, list):
        return False
    if len(line_sha) > lines:
        return False
    if not all(isinstance(x, str) and len(x) <= 128 for x in line_sha):
        return False

    sig = r.get("sig")
    if not isinstance(sig, str) or len(sig) > 20_000:
        return False

    return True
```

`load_ledger()` should return:

```python
records, malformed_count
```

and the CLI should report malformed records instead of silently dropping them.

Also impose caps:

```python
MAX_LEDGER_BYTES = 50 * 1024 * 1024
MAX_RECORDS = 100_000
MAX_RECORDS_PER_PATH = 10_000
MAX_HUNK_LINES = 10_000
```

Fail closed or warn loudly when caps are exceeded.

---

## P0-5: Encoding and normalisation are not stable across machines

Multiple places read files as:

```python
open(path, errors="replace").read()
```

No encoding is specified. The decoded text therefore depends on locale/environment. The hook hashes Python strings from tool input; the verifier hashes locale-decoded file text. This can produce different hashes on different machines.

This is fatal for CI verification.

Additional issues:

- CRLF handling is inconsistent.
- Lone `\r` is not normalised.
- `norm()` strips leading/trailing blank lines from the whole hunk, while `hunk.lines` may still count them.
- `line_span()` searches raw tool text in a decoded file and can fail on CRLF.
- Non-UTF-8 files are silently mangled via `errors="replace"`.

### Required fix

Pick one canonical byte-level normalisation and use it in both hook and verifier.

For example:

```python
def norm_bytes(b: bytes) -> bytes:
    b = b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lines = b.split(b"\n")
    return b"\n".join(line.rstrip(b" \t") for line in lines)
```

Then:

- hook hashes `norm_bytes(text.encode("utf-8"))`;
- verifier reads files with `open(path, "rb")`;
- line hashes are computed from the same byte normalisation;
- non-UTF-8 files are either explicitly unsupported or handled as bytes.

If you keep string-based normalisation, use explicit UTF-8 everywhere:

```python
open(path, "r", encoding="utf-8", newline="")
```

and define exactly how invalid UTF-8, BOMs, CRLF, CR, trailing newlines, and blank edge lines are handled.

---

## P0-6: Worktrees and submodules are silently ignored

Both `repo_root()` implementations test:

```python
os.path.isdir(os.path.join(d, ".git"))
```

In git worktrees and submodules, `.git` is often a file, not a directory. The hook then finds no repo root and silently writes no ledger record.

### Required fix

Use:

```python
os.path.exists(os.path.join(d, ".git"))
```

or better:

```python
subprocess.run(["git", "-C", dirname, "rev-parse", "--show-toplevel"], ...)
```

Also fix the root-loop termination so it works on Windows and at filesystem root:

```python
while True:
    parent = os.path.dirname(d)
    if parent == d:
        return None
    d = parent
```

---

## P0-7: Concurrent hook runs can corrupt the ledger

`hook.py` appends with:

```python
with open(os.path.join(root, ".nhw", "attest.jsonl"), "a") as f:
    f.write(json.dumps(rec, sort_keys=True) + "\n")
```

Large records can exceed atomic-write comfort zones, and multiple concurrent hook processes can interleave writes. `load_ledger()` then silently discards corrupted lines.

### Required fix

Use POSIX locking and a single write:

```python
import fcntl

def append_record(root, rec):
    ledger = os.path.join(root, ".nhw", "attest.jsonl")
    os.makedirs(os.path.dirname(ledger), exist_ok=True)

    line = (json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    fd = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, line)
        os.fsync(fd)
    finally:
        os.close(fd)
```

Document that v0.1 locking is POSIX-only.

If sequence numbers are added, allocate them under this lock.

---

## P0-8: `git diff` handling is unsafe and incomplete

`verify.diff_added()` runs:

```python
subprocess.run(["git", "diff", "-U0", ref, "--", "."], ...)
```

Problems:

- `git` missing or failing is not handled.
- `ref` is not validated and may begin with `-`.
- Quoted/C-escaped paths are not parsed correctly.
- Non-ASCII paths may be dropped.
- `/dev/null` is not handled.
- Renames/binary files are not handled robustly.
- Untracked files are not included.
- `report_file()` treats an empty added-line set as “score the whole file”.

The last bug is here:

```python
consider = [i for i in (added or range(1, len(lines) + 1)) ...]
```

If `added == set()` or `added == []`, Python treats it as false and scores the whole file.

### Required fix

Fix the empty-set bug:

```python
pool = range(1, len(lines) + 1) if added is None else added
```

Harden git invocation:

```python
subprocess.run(
    [
        "git",
        "-c", "diff.external=",
        "-c", "core.fsmonitor=false",
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        "--no-renames",
        "-U0",
        "-z",
        ref,
        "--",
        ".",
    ],
    cwd=repo,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
```

Validate `ref` before use, for example:

```python
if ref.startswith("-"):
    raise ValueError("invalid ref")
```

and optionally:

```bash
git rev-parse --verify --quiet <ref>
```

Handle:

- quoted paths;
- `/dev/null`;
- binary files;
- renames;
- deletion-only diffs;
- untracked files if the UX claims to score new files.

---

# P1 issues that must be addressed for a safe v0.1

## P1-1: The per-line fallback creates false attestation

`verify.py`:

```python
want_lines = set(r["hunk"].get("line_sha") or [])
if want_lines:
    for i, l in enumerate(lines, 1):
        if len(l.strip()) >= 12 and hashlib.sha256(l.strip().encode()).hexdigest()[:16] in want_lines:
            covered.add(i)
```

This can mark human-written lines as attested if they match any previously agent-written line.

Examples:

```python
return None
```

```python
self.assertEqual(expected, actual)
```

```python
logger = logging.getLogger(__name__)
```

Also:

- hashes are truncated to 64 bits;
- indentation is stripped;
- duplicate lines are all covered;
- there is no positional/contextual check;
- the fallback applies to the entire file.

### Required fix

For v0.1, the safest fix is:

```text
Disable the per-line fallback for headline scoring.
```

If retained, it must be:

- reported separately as weak/content match;
- excluded from the badge/percentage;
- full SHA-256, not 16 hex chars;
- limited to at most the number of signed occurrences;
- constrained by recorded line span/context;
- evaluated newest-record-first;
- ambiguous matches should be reported as unknown, not attested.

Better schema:

```json
"line_sha256": [
  {
    "ordinal": 3,
    "sha256": "...",
    "context_before": "...",
    "context_after": "..."
  }
]
```

---

## P1-2: Transcript mode over-claims via weak global matching

`nhw/attest.py`:

```python
weak = set().union(*per_file.values()) if per_file else set()
```

Then:

```python
elif k in weak:
    out["weak"] += 1
```

`nohumanwrites.check_transcripts()` counts both strong and weak as attested because it only subtracts `unattested`.

This means a line written by an agent in one project can attest an identical human-written line in another project.

### Required fix

Weak matches must not count as attested by default.

```python
def attribute(path, per_file, min_len=12, include_weak=False):
    ...
```

CLI:

```python
r = attest.attribute(f, pf, MIN_LEN, include_weak=False)
```

If weak matches are shown, label them:

```text
content seen elsewhere in agent transcripts; not provenance for this file
```

Also:

- move the transcript cache out of `~/nohumanwrites/eval/`;
- invalidate cache by transcript mtimes;
- handle corrupt cache;
- use `os.path.realpath()` for path matching;
- check tool results/success before indexing writes;
- never render an unsigned transcript score as a verified badge.

---

## P1-3: The hook signs tool input, not confirmed writes

`hook.py` signs:

```python
inp.get("content")
```

or:

```python
inp.get("new_string")
```

It does not check:

- whether the tool succeeded;
- whether the file actually changed;
- whether the exact text is present;
- whether a formatter/linter modified the result;
- whether another process raced the write.

So the ledger says “agent requested this text”, not “this text was actually written”.

### Required fix

Inspect the PostToolUse result if available. If the tool failed, do not emit an attestation.

Record at least:

```json
"result": "success"
```

or:

```json
"result": "unknown"
```

and make the semantics explicit:

```text
This record attests that the harness passed this content through the write channel.
```

Not:

```text
This proves the model authored this content.
```

---

## P1-4: Partial-line edits can become permanently unattested

`Edit.new_string` may be a fragment inside a line. The hook hashes the fragment. The verifier hashes whole file lines. A fragment like:

```python
foobar
```

will not match:

```python
x = foobar()
```

So many legitimate edits become stale/unattested.

### Required fix

For line-based attestation, expand the edited region to containing line boundaries before hashing.

Conceptually:

```python
start = body.rfind("\n", 0, match_index) + 1
end = body.find("\n", match_index + len(fragment))
if end == -1:
    end = len(body)
whole_lines = body[start:end]
```

Then hash the normalised whole lines.

Alternatively, change the schema to support fragment-level hashes, but v0.1 line scoring should use whole lines.

---

## P1-5: `MultiEdit`, empty edits, deletions, and Bash writes are not covered

The matcher/hook only handles:

```python
("Write", "Edit")
```

But Claude Code may have other write paths:

- `MultiEdit`;
- `NotebookEdit`;
- `Bash` commands such as `sed -i`, `cat > file`, codegen scripts;
- empty-string replacements;
- deletions.

The docstring claim that every byte an agent writes passes through `Write`/`Edit` is too strong.

### Required fix

For v0.1:

- handle `MultiEdit` by emitting one record per edit;
- explicitly document that `Bash` writes are not attested;
- either record zero-line/deletion events or state that deletions are not attested;
- do not silently ignore empty writes.

---

## P1-6: The spec says “most recent record”, but the verifier unions all records

SPEC rule 4 says:

> find the most recent record whose hunk covers it

The implementation loops over all records and unions coverage.

Consequences:

- old records can continue covering lines after later edits;
- timestamp ordering is not implemented;
- `ts` is self-asserted anyway;
- there is no sequence number.

### Required fix

Either:

1. implement monotonic sequence numbers:

```json
"seq": 123
```

and verify newest-first; or

2. change the spec to say “any verified matching record covers the line”.

For a provenance ledger, sequence numbers are better. Timestamps are not reliable.

---

## P1-7: The `signer` field is decorative and unbound

Hook:

```python
"signer": "ssh-ed25519:" + fingerprint(),
```

Verifier:

```python
subprocess.run(["ssh-keygen", "-Y", "verify", "-f", signers, "-I", "nhw", ...])
```

The verifier never checks that the key that verified the signature matches the claimed `signer` fingerprint.

Also, SPEC says:

```json
"signer":"ed25519:<public key fingerprint>"
```

but hook emits:

```json
"signer":"ssh-ed25519:..."
```

### Required fix

Either:

- remove `signer` from the signed payload and treat it as optional metadata; or
- bind it cryptographically by verifying against individual allowed keys and checking the fingerprint.

Also pick one prefix format and validate it.

---

## P1-8: Canonical JSON is not specified precisely

Current signing uses:

```python
json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()
```

This is stable enough inside this Python code, but not specified for other verifiers.

Unspecified:

- UTF-8 vs other encodings;
- `ensure_ascii` behaviour;
- duplicate keys;
- NaN/Infinity;
- numeric representation;
- Unicode normalisation;
- signature envelope/domain separation.

### Required fix

Define canonicalisation explicitly:

```python
def canonical_json(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
```

Reject duplicate keys during parsing.

Add golden test vectors including:

- Unicode paths;
- Unicode content;
- empty strings;
- CRLF normalisation;
- nested objects;
- tampered fields.

Optionally sign with domain separation:

```python
payload = b"nhw-v1\0" + canonical_json(rec)
```

---

## P1-9: Signature storage should be byte-safe

Current code reads the signature as text:

```python
return open(p + ".sig").read()
```

and writes:

```python
s.write(rec["sig"].encode())
```

OpenSSH `ssh-keygen -Y sign` normally produces an ASCII-armoured signature, so this is not necessarily dead on arrival. Answer H’s claim that the signature file is always raw binary and therefore guaranteed to raise `UnicodeDecodeError` is not correct for standard OpenSSH behaviour.

However, storing exact signature bytes as base64 is still more robust.

### Required fix

In `sign()`:

```python
with open(p + ".sig", "rb") as fh:
    return base64.b64encode(fh.read()).decode("ascii")
```

In `sig_ok()`:

```python
sig_bytes = base64.b64decode(rec["sig"])
with tempfile.NamedTemporaryFile(delete=False, suffix=".sig") as s:
    s.write(sig_bytes)
```

This avoids newline, encoding, and armour ambiguity.

---

## P1-10: Path handling is unsafe and under-specified

Issues:

- `os.path.relpath()` can produce `../` paths.
- The verifier joins repo and rel without containment checks.
- Symlinks inside the repo can point outside.
- `nohumanwrites.py check /repo-a /repo-b` scores everything against the first repo.
- Hook events can contain arbitrary `file_path` values.
- Windows path separators are not normalised.

### Required fix

In the hook, reject records whose relative path escapes the repo:

```python
rel = os.path.relpath(path, root)
if rel == ".." or rel.startswith(".." + os.sep) or os.path.isabs(rel):
    return
```

In the verifier:

```python
repo_real = os.path.realpath(repo)
full_real = os.path.realpath(os.path.join(repo, rel))
if os.path.commonpath([repo_real, full_real]) != repo_real:
    return set(), 0, 0
```

In `nohumanwrites.py check`, either:

- group files by repo; or
- reject mixed-repo invocations in ledger mode.

Store paths in the ledger as POSIX-style relative paths:

```python
rel.replace(os.sep, "/")
```

---

## P1-11: Sliding-window matching has correctness and DoS issues

`attested_lines()` slides a window over the whole file:

```python
for i in range(0, len(lines) - n + 1):
```

Problems:

- first match wins, so duplicate blocks elsewhere are not covered;
- if fallback is used, all duplicate lines may be covered;
- `norm()` strips outer blank lines, so line-count semantics can drift;
- attacker-controlled `n` can cause wasted work or weird edge cases;
- recorded `start`/`end` are ignored.

### Required fix

For v0.1:

- validate `n`;
- use recorded `start`/`end` as a search hint first;
- define duplicate-block policy explicitly;
- do not silently choose first occurrence if provenance is positional;
- cap scan work.

If the simplest safe behaviour is desired:

```text
Only whole-hunk matches at or near the recorded span count as attested.
```

---

## P1-12: UX violates the spec’s honesty rule

SPEC says absence of a record asserts nothing. But output says:

```text
unattested = typed by hand, or written through a channel with no hook.
```

That implies human authorship.

Also:

- zero considered lines can print “every considered line carries machine provenance”;
- badges show a percentage without evidence tier;
- transcript-derived unsigned scores look the same as signed scores.

### Required fix

Replace wording with:

```text
unattested = no verifiable machine provenance.
```

Never say:

```text
typed by hand
```

or:

```text
human
```

For zero considered lines:

```text
No lines met the minimum-length threshold; no score is given.
```

For badges:

- include evidence tier: `signed`, `unsigned-transcript`, or `unknown`;
- refuse to emit a badge when signatures were not verified;
- do not badge transcript-only evidence as if it were cryptographic provenance.

Rename:

```python
human_or_untracked_ratio
```

to:

```python
unattested_ratio
```

---

## P1-13: Setup is fragile and unsafe

`cmd_setup()`:

```python
json.dump(s, open(settings, "w"), indent=2)
```

Problems:

- non-atomic write;
- no backup;
- `~/.claude` may not exist;
- paths with quotes can produce broken hook commands;
- uses `python3` instead of `sys.executable`;
- hook detection is brittle.

`setup-key.sh`:

- overwrites `~/.nhw/allowed_signers`;
- assumes `eval/` exists;
- smoke test does not assert success;
- smoke test can pollute the real repo ledger;
- no OpenSSH version check;
- no atomic allowed_signers write.

### Required fix

For `cmd_setup()`:

```python
os.makedirs(os.path.dirname(settings), exist_ok=True)
tmp = settings + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(s, fh, indent=2)
os.replace(tmp, settings)
```

Use:

```python
sys.executable
```

and proper quoting or argv-style hook configuration if supported.

For `setup-key.sh`:

```bash
umask 077
mkdir -p "$NHW_DIR"
chmod 700 "$NHW_DIR"
```

Do not clobber `allowed_signers`; merge or back up.

Run smoke tests in a temporary git repository:

```bash
tmpdir="$(mktemp -d)"
git init "$tmpdir"
```

Then assert that a record was written and verifies.

Check OpenSSH support:

```bash
ssh-keygen -Y sign ... 
```

or parse `ssh -V`, and fail with:

```text
OpenSSH 8.0+ is required.
```

---

## P1-14: Packaging, licence, and maintainer requirements

Before a public Apache-2.0 v0.1 tag, the repo needs:

### Licensing

- `LICENSE` containing Apache-2.0 text.
- `NOTICE` if applicable.
- SPDX header in source files:

```python
# SPDX-License-Identifier: Apache-2.0
```

### Packaging

The “single-file CLI” claim is false because `nohumanwrites.py` imports:

```python
from nhw import attest, verify
```

Either vendor everything into one file or package properly:

```toml
[project.scripts]
nohumanwrites = "nohumanwrites.cli:main"
```

Support:

```bash
python -m nohumanwrites
```

### Tests

Minimum required tests:

1. Sign/verify round-trip.
2. Tampered record fails verification.
3. Repo-local `allowed_signers` is ignored by default.
4. Forged repo ledger scores zero/unverified.
5. Malformed ledger records are skipped and counted.
6. Concurrent appends produce valid JSONL.
7. CRLF, LF, lone CR, empty file, whitespace-only file.
8. Unicode filenames and paths.
9. Path traversal attempts are rejected.
10. Worktree `.git` file is detected.
11. `--diff` with empty added set does not score whole file.
12. Transcript weak matches are not counted as attested.
13. Python 3.9 import smoke test.
14. Canonical JSON golden vectors.
15. OpenSSH missing/too-old handling.

### CI

Matrix:

- Ubuntu latest.
- macOS latest.
- Python 3.9 through current.
- OpenSSH 8.0 baseline if possible.

### Git ledger ergonomics

Ship:

```gitattributes
.nhw/attest.jsonl merge=union
```

Append-only JSONL will otherwise create painful merge conflicts.

---

# Specific errors and unstated assumptions in the answers

## Answer A

Mostly strong.

Correctly identifies:

- repo-local trust failure;
- signer field not bound;
- “most recent record” spec mismatch;
- per-line fallback false positives;
- Python 3.9 breakage;
- encoding/CRLF instability;
- concurrency;
- schema/DoS issues;
- canonicalisation gaps;
- setup/packaging gaps.

Weaknesses:

- Overstates direct path traversal from ledger `path` fields. In the current code, the verifier generally opens paths supplied by the user/diff, not paths taken from ledger records. Still, path sanitisation is needed.
- Misses the `added=set()` whole-file `--diff` bug.
- Misses `MultiEdit` and `Bash` write bypass.
- Misses git-config/external-diff hardening.
- Does not emphasise partial-line `Edit` mismatch strongly enough.

## Answer B

Too shallow.

Good catches:

- repo-local trust;
- Python 3.9;
- temp-file hygiene;
- fallback over-attestation.

Problems:

- The proposed `Counter` fix for line fallback is insufficient. It still arbitrarily attests duplicate lines and does not solve human-retyped common lines.
- Says CRLF is handled correctly, but `line_span()` and file normalisation have CRLF problems.
- Misses schema validation, concurrency, worktrees, transcript weak matching, canonicalisation, UX honesty, and setup issues.
- “Tag after fixes” is too lenient given the omitted issues.

## Answer C

No answer provided.

## Answer D

Strongest answer.

Major strengths:

- Correctly prioritises the inverted trust model and dishonest `verified_signatures`.
- Catches Python 3.9 silent failure.
- Catches worktree/submodule `.git` file issue.
- Catches concurrent ledger corruption.
- Catches malformed ledger crash/DoS.
- Catches locale-dependent hashing as a reproducibility blocker.
- Catches `--diff` empty-added whole-file bug.
- Catches transcript weak-match overclaiming and stale cache.
- Catches `MultiEdit`, failed tool writes, and `Bash` bypass.
- Catches canonical JSON ambiguity.
- Provides a useful false-attestation taxonomy.

Weaknesses:

- Misses git-config/external-diff/textconv/fsmonitor hardening in untrusted repos.
- Misses partial-line `Edit` false-unattested bug.
- Its byte-normalisation patch needs care: `bytes.rstrip()` only strips ASCII whitespace, while Python `str.rstrip()` strips Unicode whitespace. The final spec must define this explicitly.
- Suggests `--no-prefix` without fully accounting for parser changes.

## Answer E

Solid but incomplete.

Good catches:

- repo-local trust;
- schema validation;
- mixed-repo path handling;
- transcript weak-match overclaiming;
- concurrency;
- Python 3.9;
- stale transcript cache;
- UX wording.

Misses:

- locale-dependent hashing as a P0 reproducibility bug;
- `--diff` empty-added bug;
- git-config execution hardening;
- partial-line `Edit`;
- canonical JSON cross-language specifics;
- `MultiEdit`/`Bash` implications.

## Answer F

Broad and useful, but contains factual errors.

Good catches:

- trust model;
- line fallback;
- transcript weak matching;
- concurrency;
- canonical JSON;
- path/encoding issues;
- sliding-window problems;
- git diff parsing;
- setup pollution.

Errors:

- Claims zero considered lines gives 100% attested. In the code, `pct = 100 * (0 - 0) / 1`, so it gives 0%, not 100%. The real bug is still misleading output plus “every considered line carries machine provenance”.
- Says Python 3.9 causes `SyntaxError`; it is a `TypeError` from evaluating `str | None` annotations.
- Some path traversal implications are overstated for the current call paths, though sanitisation is still required.

## Answer G

Contains several important unique catches.

Good catches:

- unverifiable ledger should be “unknown”, not “0% attested”;
- Python 3.9 silent hook failure;
- git-config/external-diff hardening;
- partial-line `Edit` mismatch;
- duplicate hunk first-match issue;
- worktrees;
- transcript weak matching;
- hardcoded transcript cache;
- setup smoke test pollution.

Weaknesses:

- Misses locale-dependent decoding as a top-level reproducibility blocker.
- Misses the `added=set()` whole-file `--diff` bug.
- Suggests removing the sliding-window `break`; that fixes duplicate false negatives but can increase false positives unless combined with span/context constraints.
- The git-config execution risk is real as defence-in-depth, but its severity depends on whether the verifier runs inside arbitrary `.git` directories rather than ordinary clones.

## Answer H

Has several valid points but one major false critical claim.

Incorrect:

- Claims `ssh-keygen -Y sign` output is raw binary and `open(...).read()` will almost certainly raise `UnicodeDecodeError`. Standard OpenSSH signature output is ASCII-armoured, so this “pipeline is dead” claim is not correct.
- The proposed base64 fix is still reasonable as robustness, but not for the reason given.
- `hostname -s` portability is overstated as a critical macOS failure.
- Path injection is overstated as an immediate arbitrary-file-read via ledger records in the current verifier call paths, though sanitisation is still needed.

Valid:

- trust model;
- Python 3.9;
- schema validation;
- fallback false positives;
- transcript weak matching;
- concurrency;
- setup issues.

---

# Disagreements and correct positions

## 1. Is the signature file binary?

Answer H says yes and calls it fatal. The other answers mostly assume it works.

Correct position: standard OpenSSH `ssh-keygen -Y sign` usually emits an ASCII-armoured signature. The current text read is not necessarily fatal. Still, storing the exact signature bytes as base64 is safer.

## 2. Is the verdict “after fixes” or “not yet”?

Answers B/E/G say after fixes. Answers A/D/F/H say not yet.

Correct safe position: **not yet as-is**. The trust model, verification honesty, Python 3.9 support, schema validation, encoding stability, and false-attestation behaviour are too broken for a public provenance tool. After the P0/P1 fixes and tests, a v0.1 could be reasonable.

## 3. Does zero considered lines produce 100%?

Answer F says yes. That is wrong.

Correct position: it produces 0% but then misleadingly prints:

```text
every considered line carries machine provenance.
```

The correct UX is:

```text
No lines met the minimum-length threshold; no score is given.
```

## 4. Is Python 3.9 failure a SyntaxError?

Some answers say SyntaxError.

Correct position: it is a `TypeError` from evaluating `str | None` annotations at function-definition time. The practical effect is still import failure.

## 5. Is repo-controlled `path` in the ledger directly exploitable for file reads?

Answers A/H imply stronger direct exploitability than the current code always provides.

Correct position: the verifier mostly opens paths supplied by the user or git diff, not arbitrary ledger paths. But path sanitisation is still required because:

- the hook can record bad paths;
- the CLI can be invoked across repos;
- symlinks can escape;
- future `--all` or record-driven modes would be dangerous.

---

# Minimum safe v0.1 scope

A safe v0.1 should reduce claims and disable ambiguous features:

1. Trust only user-owned or explicitly supplied `allowed_signers`.
2. Report three states: attested / unattested / unverifiable.
3. Do not call unverified ledger evidence “signed”.
4. Do not count transcript weak matches as attested.
5. Disable or separately report the per-line fallback.
6. Use explicit UTF-8 or byte-level normalisation.
7. Validate ledger schema and cap work.
8. Lock ledger appends.
9. Fix Python 3.9 annotations.
10. Handle worktrees.
11. Replace “human” language with “no provenance”.
12. Add tests, CI, licence headers, and packaging.
13. Document that the signature proves access to the local signing key, not model authorship.
14. Document that `Bash` writes and other non-hooked channels are not covered.

---

# What the final answer must include

A correct/safe final answer must include, at minimum:

1. The repo-local `allowed_signers` trust bug as P0, with a patch that defaults to `~/.nhw/allowed_signers` or an explicit flag.
2. The `verified_signatures` honesty bug, with real verified/invalid/malformed counts.
3. The Python 3.9 annotation failure and silent hook failure.
4. Strict ledger schema validation and DoS caps.
5. Explicit encoding/normalisation rules, preferably byte-based and shared by hook/verifier.
6. Worktree/submodule `.git` file handling.
7. Locked, atomic-ish JSONL appends.
8. Removal or demotion of the per-line fallback and transcript weak matching.
9. The partial-line `Edit` mismatch and tool-success requirement.
10. `MultiEdit`/`Bash` coverage gaps and honest documentation.
11. Path containment and symlink policy.
12. Canonical JSON specification and golden vectors.
13. Binding or removal of the decorative `signer` field.
14. Git diff hardening, including empty-added-set bug and untrusted-repo options.
15. UX changes: never say “human”, never badge unverified evidence, handle zero-line case.
16. Setup fixes: atomic settings write, safe smoke test, OpenSSH version check, no clobbering.
17. Tests/CI/licence/packaging requirements.
18. A clear threat-model statement: the key authenticates a local signing installation, not the model or the agent harness.

Verdict: not yet.

### moonshotai/kimi-k3 reviews
# Review of reviews

## First, establish ground truth on the contested technical facts

Before ranking, I checked the load-bearing claims against the actual code and OpenSSH behavior:

1. **`ssh-keygen -Y sign` output is binary, not armored.** The `.sig` file is the raw SSHSIG blob: 6-byte `SSHSIG` magic, then uint32 version, then length-prefixed strings containing the raw 32-byte ed25519 public key and raw 64-byte signature — arbitrary bytes. (The `-----BEGIN SSH SIGNATURE-----` armor you see in git commits is applied by *git*, not by `ssh-keygen`.) Consequence: `hook.py`'s `open(p + ".sig").read()` decodes as UTF-8/locale text and raises `UnicodeDecodeError` with probability ≈ 1. The outer `except Exception` swallows it, logs to `~/.nhw/hook.log`, exits 0. **No record is ever appended. The product as shipped cannot produce a single attestation.** Even under a Latin-1 locale (where the read succeeds), `json.dumps`→`json.loads`→`.encode()` in the verifier is UTF-8 by default, corrupting the blob, so `-Y verify` fails on every record. The smoke test in `setup-key.sh` cannot catch this: the hook exits 0 by design, the script asserts nothing, `set -e` never trips.

2. **`str | None` in annotations** evaluates at def time and raises `TypeError` on Python 3.9 — an import-time failure, silent in the hook due to the same blanket `except`. True (A, B, D, E, F, G, H all correct).

3. **Repo-local `allowed_signers` is checked first** (`verify.py`) — circular trust, repo self-attests. True (all non-empty answers).

4. **Empty-file math:** `100 * (0 - 0) / (0 or 1)` = **0%**, printed as "0% attested — 0 of 0 lines" followed by the vacuous "every considered line carries machine provenance." F's claim of "100% attested" is **wrong**; G described the actual behavior exactly; B's "division by zero avoided" is true but missed the vacuous-message bug.

5. **`hostname -s` on macOS:** macOS/BSD `hostname` supports `-s` ("Trim off any domain information"). H's C5 ("script aborts before creating the key on macOS") is **false**; E's #7 is the same error, hedged. G explicitly and correctly said it's fine. (`hostname` isn't POSIX at all, so a portability note is defensible; a critical ranked bug is not.)

6. **CRLF and `line_span`:** `open(path, errors="replace")` uses universal-newline mode, so the on-disk body is already LF-normalized on read. H's H2 mechanism ("body is read raw") is **backwards**. The real failure runs the other way: if the *tool input* contains `\r\n` (agent writing a CRLF file), the raw `text` is searched in the translated body and `find()` fails — A's phrasing ("searches raw text in a text-decoded file") is the accurate one.

7. **`git diff` path quoting:** git C-quotes paths with non-ASCII bytes (default `core.quotePath`), tabs, newlines — not mere spaces. D's version is correct; B's premise ("a file has spaces → quoted header") is **wrong**, though B's patch happens to handle the quoted form anyway.

8. **`--json` with no evidence:** `render()` prints `json.dumps(None)` → `null` — valid JSON. G's claim that it "prints prose" is **wrong**; D's "prints bare `null`" is right.

9. **C-locale mojibake (D's P0.6):** overstated. Since Python 3.7, PEP 538/540 coerce C/POSIX locales to UTF-8 mode by default, so `open()` is UTF-8 in the common CI case. The risk survives only with explicit `PYTHONUTF8=0`/exotic locales. Direction and byte-level fix are correct; the stated trigger scenario is mostly wrong.

10. **Record-path traversal (A #8, H C3):** as shipped, record `path` values are only *compared* for equality (`r.get("path") != rel`), never joined and opened. The live traversal is `os.path.relpath(abspath(f), repo)` on user-supplied files outside the repo (multi-repo `check`) — E's framing. A and H describe an attack path the current code doesn't have (H concedes "if you add --all"). The hygiene fix (reject `..`, containment check) is still correct.

11. **B's temp-file symlink race:** real class, but `mkstemp` names are unpredictable and modern Linux `fs.protected_symlinks=1` blunts the clobber vector; "High" is generous. Critically, **B's own Patch 2 rewrites `sign()` and still reads `p + ".sig"` in text mode** — it reintroduces the fatal bug.

12. **D's pure-deletion diff bug** (`added == set()` is falsy → `added or range(...)` scores the whole file): verified real — `@@ -5,3 +4,0 @@` yields `range(4,4)` = empty set. A subtle, correct, unique catch.

13. **G's partial-line Edit finding:** verified real and major — an in-line rename (`foo(` → `bar(`) yields a fragment whose `norm()` hash can never match any whole-line window, and the fragment is <12 chars so `line_sha` is empty. The most common agent edit attests nothing. Unique to G.

14. **G's git-config RCE:** real but conditional — `.git/config` does not propagate via clone; the vector is tarball-with-`.git` distribution or fsmonitor/textconv in pre-existing config. Correctly hedged by G, worth the one-line mitigation.

15. **F's "sig is the full SSH armor including newlines":** false premise (it's binary, see #1). Ironically, F's prescribed fix — base64 the `.sig` file — is the correct cure for the disease F misdiagnosed.

16. **H's M6** misreads `render()`: the "(no signature check)" suffix *is* rendered when `verified_signatures` is False, and the scenario H constructs (80% attested with unverified ledger) is unreachable — with no keyring all records fail `sig_ok` and the score is 0%, which is the *different* bug G correctly identified as P0-2 (0% presented instead of "unverifiable"). H error.

## Per-answer assessment

**A** — Broad, well-organized, almost everything verifiable. Best on scope-reduction advice and the signer-field/schema mismatches. Slips: the traversal attack path (#10 above); missed the fatal sig bug. Its severity ranking is sensible throughout. Safe but adds nothing the top tier lacks.

**B** — Thinnest substantive answer. Wrong premise on git quoting, "CRLF handled correctly" hand-wave (right conclusion, no mechanism), missed the fatal bug, and **its own patch preserves the fatal bug** — so its verdict "tag after fixes" is unsafe on its own terms. Its prescribed test *mocks* ssh-keygen, which would entrench the blind spot (the mock hides the binary format). The `Counter` duplicate-line fix is its one solid contribution. Weakest non-empty answer.

**C** — Empty (API error). Disqualified.

**D** — The most precise answer line-by-line. Unique real catches: pure-deletion whole-file bug, MultiEdit (regex-matched by the harness, then rejected by the hook — stated more precisely than G), `.nhw/attest.jsonl merge=union`, ledger replayability across repos, junk `"\n"`-only records, untracked files missing from `--diff`, smoke test asserting nothing. The false-attestation taxonomy is the best of the set. Only real blemish: the C-locale scenario is overstated (PEP 538/540). Missed the fatal sig bug — though its demanded pytest round-trip would have surfaced it in CI immediately.

**E** — Competent mid-tier. Correct on multi-repo `check` (the accurate version of the traversal bug), `~/.claude` mkdir, cache invalidation. Repeats the false `hostname -s`/macOS claim, misses the deep items (no most-recent semantics, no MultiEdit, no partial-line Edit), and "after fixes" is unsupported by its own list.

**F** — Sharp, concrete, good unique catches (git option-injection via unvalidated `ref`, smoke test polluting the real repo ledger, `NHW_KEY` login-key footgun, window/`norm()` outer-strip mismatch). Two factual errors: the "0 lines → 100% attested" claim (it's 0% plus a vacuous line) and the "SSH armor" claim; plus the "SyntaxError on 3.9" misnomer (it's a `TypeError`). Never realized the pipeline is dead, though its base64 suggestion would accidentally fix it.

**G** — Best attacker mindset. Unique major finds: partial-line Edit false negatives, git-config/textconv RCE (correctly scoped), FIFO/symlinked ledger (append redirect + 10 s hook hang), attestation order-blindness, and the structural insight that *the attack path is also the only key-distribution path* — `setup-key.sh` never installs a repo-side signers file, so cross-machine verification only works via the untrusted file. Errors: the `--json` claim is wrong; MultiEdit phrasing slightly off; and it noticed the text-mode sig read but filed it as a P2 nit ("read bytes"), which both misranks it and wouldn't fix it (bytes aren't JSON-serializable; base64 is required). So close to the kill, didn't take it.

**H** — The only answer that found the decisive bug: **the signature file is binary, the hook's text-mode read raises `UnicodeDecodeError`, the blanket `except` swallows it, and no record is ever written — the entire product is a no-op as shipped, and the smoke test is incapable of noticing.** Correct fix on both sides (base64 at write, `b64decode` at verify), correct severity, and the right test demand (smoke must fail if a freshly attested file verifies at 0%). Also good: the spec-vs-code contradiction on reflowed lines, transcript cache invalidation, `flock`. But H has three clear errors a maintainer must disregard: C5 (`hostname -s` works fine on macOS — fabricated critical), H2 (CRLF mechanism backwards), M6 (misread of `render()`), plus the 2⁻²⁵⁶ hyperbole (the true probability is merely ≈ 1, not that) and a C3 attack path that doesn't exist in the current code.

## Strongest answer: **H** — with explicit reservations

The criterion that matters for a hostile pre-release review is decision-relevance: which answer changes the ship decision regardless of what else is fixed. Every other answer's fix list, applied in full, still ships a ledger that never records a single byte. B's patch even preserves the bug. H alone identified that the tool cannot function, with the correct patch and the correct test. That outweighs its noise.

That said: if graded on accuracy-per-claim rather than decisive findings, **D is the winner** — nearly error-free, deepest on spec semantics, and its mandated round-trip test is the process control that catches what the review missed. G is third, and would be second if it had followed its own P2 observation one step further.

One useful meta-observation: every answer that prescribed a real sign/verify round-trip or golden-vector test (A, D, F, G, H) would have surfaced the fatal bug in CI despite missing it in review. B alone prescribed a mock, which would not. That is the difference between a test plan and a test plan that tests something.

## What a correct/safe final answer must include, ranked

**P0 — the tool is non-functional or forgeable without these:**

1. **Binary signature handling (from H, the find of the review):** base64 the SSHSIG blob in `hook.py:sign()`; `base64.b64decode` before writing the temp `.sig` in `verify.py:sig_ok()`. Add an end-to-end assertion: smoke test must fail unless a freshly written file verifies ≥ expected.
2. **Trust root (all answers):** never default to repo-local `allowed_signers`; user keyring or explicit flag only; print the trust source; bind `rec["signer"]` to the actually-verifying key or document it as cosmetic; `verified_signatures` must mean *N records verified*, not *file exists*; three-state output (attested / unattested / **unverifiable**) with no percentage when zero records verify (G's P0-2).
3. **Python 3.9:** `from __future__ import annotations` or `Optional[...]`; CI on 3.9 — currently the hook silently no-ops forever on a claimed-supported version.
4. **Concurrent append:** `flock` + single `os.write` on an `O_APPEND` fd + fsync; surface malformed-ledger counts instead of silent `except: pass`.
5. **Input validation / DoS:** strict per-record schema, caps on records/hunk size/sig size, per-record try/except, path containment (`..` rejection), no per-record unbounded `ssh-keygen` storms.

**P1 — correctness of the score:**

6. Partial-line Edits attest nothing — expand to containing line boundaries before hashing (G). Remove the `break` on first window hit; `added or range(...)` empty-set bug (D); MultiEdit handling (D); tool-response success check (A/D).
7. False attestation: remove or demote the per-line fallback (global set, 64-bit truncation, indent-stripped, order-blind — A/D/F/G) and transcript weak matches (all); never badge from unsigned transcripts (F/D).
8. Encoding discipline: one shared byte-level `norm` (D), explicit UTF-8, defined final-newline rule; canonical-JSON pinned with golden vectors including non-ASCII (A/D/G).
9. Worktree `.git`-file detection (D/F/G/E); git hardening: `--no-ext-diff --no-textconv`, quoted-path handling, `rev-parse --verify` the ref (F), skip `.nhw/` itself (G).
10. UX honesty: "unattested / provenance unknown" only, never "typed by hand"; fix the 0-line vacuous message (G); evidence tier on the badge; non-zero exit / `--fail-under` for CI.

**P2 — release mechanics:** atomic `settings.json` write with backup and `~/.claude` mkdir; OpenSSH ≥ 8.0 probe; merge (don't clobber) `allowed_signers`; smoke test in a temp git repo; LICENSE + SPDX headers; `pyproject.toml`; tests including a *real* (not mocked) ssh-keygen round-trip, the forgery attack as a regression test, and the tamper matrix; SECURITY.md stating the channel-not-authorship caveat and that the key proves key access, not harness provenance.

## Verdict

**Not yet — as shipped the hook can never write a record (binary sig read as text), the trust root is repo-controlled, and the hook silently no-ops on the advertised Python 3.9; only H saw the first of these, which is why every "after fixes" verdict in the set is premature.**

### deepseek/deepseek-v4-pro-0813 reviews
The central disagreement across these reviews is whether the signature path works at all. **Answer H is the strongest**, because it is the only one that catches a fatal bug in the current implementation: `ssh-keygen -Y sign` emits a binary `SSHSIG` blob, not armored text, but `hook.py` does:

```python
return open(p + ".sig").read()
```

This attempts to decode arbitrary binary bytes as locale text. A valid Ed25519 signature contains roughly random bytes, so this will almost always raise `UnicodeDecodeError`. That exception is swallowed by the hook’s blanket `except Exception: ... exit 0`, so no record is appended. The `setup-key.sh` smoke test runs the verifier but never asserts that coverage was actually produced, so the whole pipeline can be dead while setup reports success.

Several other reviews miss this entirely. Answer D explicitly says “the crypto plumbing is fine,” and Answer E says the signing core is sound. Answer F incorrectly calls the signature “full SSH armor,” and Answer A/B/G do not identify the binary encoding problem. This alone disqualifies most of the others from being strongest.

That said, **H is not perfect**. It overstates the UTF-8 probability, and its path-injection example is more conditional than it presents: `repo_root()` derives the root from ancestors of the inbound path, so a literal `../../` record path is less likely directly from the hook than via symlinks or a hostile `attest.jsonl`. But the underlying path-containment requirement is correct.

---

## Strongest answer

**Answer H** provides the highest-value review because it identifies the dead signature pipeline and combines that with the most important trust, path, Python-version, false-attestation, and setup issues.

Second tier: **D** and **G** are broad and substantially correct, but they both miss the binary-signature failure. **A** is also detailed but misses it. **B** is too narrow and has at least one false claim: CRLF is not “handled correctly,” because `line_span()` compares raw tool text against a raw file body, so CRLF files can produce `span: null`. **F** repeats plausible issues but gets the signature format wrong.

---

## Key disagreements and known errors in the reviews

| Issue | Reviews that address it | Reviews that get it wrong or miss it |
|---|---|---|
| `ssh-keygen -Y sign` writes binary `SSHSIG`; current `open(...).read()` is fatal | H only | D says “crypto plumbing fine”; E says signing core sound; F calls it “SSH armor”; A/B/G miss it |
| Repo-controlled `.nhw/allowed_signers` is circular trust | A/B/D/E/F/G/H | Some propose opt-in repo keys, but the correct default is user/CI trust only |
| `verified_signatures` should mean signatures verified, not “a signers file exists” | A/D/G/H | B misses the semantic lie |
| Python 3.9 `str \| None` breaks import | A/B/E/H | G correctly notes hook swallows this; some others understate it |
| Transcript `weak` global matching over-claims | A/D/F/G/H | B mostly misses; E makes it opt-in but does not fully address stale cache |
| Per-line fallback over-claims duplicate/human-restored lines | A/B/D/F/G/H | Counter alone, as B suggests, is insufficient because it still ignores position, history, and duplication |
| Concurrent `attest.jsonl` append can interleave | A/D/E/F/G/H | B misses |
| Worktrees/submodules have `.git` as a file, not directory | D/G/H | A/B/E/F mostly omit |
| `line_span()` raw CRLF and first-match ambiguity | D/F/G/H | B says CRLF handled correctly |
| Git diff parsing/path quoting/untrusted config | D/F/G/H | B gives a partial parser; A misses repo-controlled git config |
| Setup script clobbers `allowed_signers`, pollutes repo, non-atomic settings | A/D/F/G/H | B misses |

---

## What a correct/safe final answer must include

A correct pre-v0.1 review must make these points, roughly in this order:

### 0. Fatal: binary SSH signature encoding

Fix `hook.sign()` to read bytes and base64-encode them:

```python
import base64

def sign(payload: bytes) -> str:
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "payload")
        with open(p, "wb") as f:
            f.write(payload)
        subprocess.run(
            ["ssh-keygen", "-Y", "sign", "-f", KEY, "-n", NAMESPACE, "-q", p],
            check=True,
            capture_output=True,
        )
        with open(p + ".sig", "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
```

In `verify.sig_ok()`, base64-decode `rec["sig"]` into a real `.sig` file and size-limit it. Add a real round-trip test in setup/CI; this bug is fatal because the hook silently exits 0.

### 1. Trust model and output honesty

Fix `allowed_signers()` so the default trust root is not inside the repo being verified. For v0.1, use only `~/.nhw/allowed_signers` or an explicit external signers path. If repo-local keys are ever permitted, require an explicit `--trust-repo-keys` flag and print a warning in every report.

`verified_signatures` must be true only when at least one relevant signature actually verified. The UI must distinguish:

- attested
- unattested
- unverifiable

The current output says “unattested = typed by hand …” and can show `0% attested` when no signers file exists. That is false and violates SPEC rule 1. “Unattested” must never imply “human.” A zero-length scoring set must not produce 100% or 0% misleading badges.

### 2. Record and path validation

Untrusted `attest.jsonl` is attacker-controlled input. A verifier must:

- validate record shape and types
- reject `v != 1`
- cap record size, `sig` size, `hunk.lines`, and number of records per file
- reject paths that contain `..` or are absolute
- use `realpath()` and containment checks against the repo root
- count and report malformed records instead of silently `except: pass`
- not launch one `ssh-keygen` per untrusted record without strict caps

### 3. Python 3.9 compatibility

Remove `str | None` runtime unions or add:

```python
from __future__ import annotations
```

And include Python 3.9 in CI. The hook’s blanket exception handling makes this especially dangerous: on Python 3.9 the hook can silently stop producing provenance without any user-visible error.

### 4. Concurrency and append integrity

Use a POSIX lock around ledger appends, a single `os.write()` on an `O_APPEND` fd, and ideally an explicit sequence number. `json.dumps` records can exceed atomic pipe-buffer size, especially with large `line_sha` arrays.

### 5. False-attestation fixes

The final answer must be explicit that the current code counts these as attested when they may be human-written:

- any identical stripped line in the file via `line_sha`
- duplicate hunks because the sliding window breaks after first match
- human-restored lines identical to previously signed lines
- transcript weak cross-file matches
- human-dictated code emitted through an agent channel

The verifier must either remove/demote `line_sha` fallback or consume each signed line hash at most once, match newest-first, and report fallback coverage separately from whole-hunk coverage. It must not present weak transcript matches as the headline provenance number.

Also, the review must say that the signature proves **channel provenance**, not model authorship. Human-pasted or human-dictated content sent through `Write` will be signed.

### 6. Encoding and CRLF normalization

Use a single byte-level normalization function shared by hook and verifier, or explicitly `encoding="utf-8", newline=""`. Do not hash locale-dependent decoded text. The current two separate `norm()` functions will diverge.

### 7. Pragmatics before public tag

- OpenSSH 8.0+ preflight
- worktree `.git` file support
- atomic `~/.claude/settings.json` writes with backup
- setup smoke test in a temporary repo, not the current repository
- do not clobber `~/.nhw/allowed_signers`
- SPDX/Apache-2.0 headers
- `pyproject.toml`, `__version__`
- CI: Python 3.9–3.13, macOS/Linux, OpenSSH versions
- tests for the round-trip signature, tamper rejection, malformed ledger, concurrent appends, CRLF, empty files, quoted git paths, path traversal, and repo-local signer rejection

---

**Verdict:** H is the strongest review, but no answer is complete. The final public answer must lead with the binary signature encoding bug, then the trust-root/output-honesty issue, then path/resource validation, Python 3.9, concurrency, and false-attestation semantics.

### x-ai/grok-4.6 reviews
## Independent findings (from the code, not the reviews)

**Trust is inverted.** `verify.allowed_signers` prefers `<repo>/.nhw/allowed_signers` over `~/.nhw/allowed_signers`. A repo can ship its own key + ledger and verify at 100%. `check_ledger` then sets `"verified_signatures": bool(signers)` (file exists, not “any sig verified”). That is the product bug.

**UX violates SPEC §1/§6.** `render()` says `unattested = typed by hand…`. Absence is treated as human. Zero considered lines (`lines or 1`) can print 100% and “every considered line carries machine provenance.”

**False positives (attested though a human typed it):** per-line `line_sha` is a 64-bit prefix of `l.strip()` matched *anywhere* in the file; sliding window matches a hunk *anywhere*; transcript `weak` unions every agent line on the machine and the CLI counts it as attested; Edit `new_string` includes unchanged context; channel ≠ authorship (prompt-paste / “rewrite unchanged”).

**False negatives:** worktrees/submodules (`.git` *file* → hook never records); `str | None` on 3.9 → hook import fails, `except` + `exit 0` → silent no-op; MultiEdit/NotebookEdit/Bash; partial-line Edit hashed as a fragment vs whole file lines; locale `open()` vs UTF-8 hashes; concurrent append + `load_ledger` swallowing torn JSON; hook never checks tool success.

**Other real bugs:** path `join(repo, rel)` with `..`; unvalidated ledger (`hunk.lines` as str → crash / DoS via `ssh-keygen` per record); `git diff` in repo cwd (config/attributes can run code); quoted/C-escaped paths; `added == set()` is falsy → whole-file scoring; no flock; `setup` truncates `settings.json`; cache path `~/nohumanwrites/eval/…` with no invalidation; SPEC “most recent record” vs union of all records; `signer` never bound to the key (`-I nhw` is constant).

**Not a bug:** `ssh-keygen -Y sign` writes **ASCII-armored** SSHSIG (`-----BEGIN SSH SIGNATURE-----`). Text `open().read()` / JSON / `.encode()` is the intended round-trip. The pipeline is not “dead.”

---

## Errors in the answers

| Answer | Concrete errors |
|---|---|
| **H** | **C1 is false.** Signatures are armored, not a binary blob; UTF-8 `read()` does not kill the ledger. Ranking this as the #1 showstopper invalidates the review. **C5 is false:** macOS `hostname` supports `-s`. Path injection via `/etc/passwd` is overstated (hook bails without a `.git`); the real issue is ledger `..` at verify time. |
| **B** | “UX Honesty: Excellent” is wrong. CRLF is not “handled correctly” (`line_span` searches raw body; locale decode). `Counter` on `line_sha` still attests a human retype of the same line. Git-quoted-path patch is a brittle string hack. Verdict “after fixes” with four patches is under-scoped. |
| **F** | Calls 3.9 `str \| None` a **SyntaxError**; it is a **TypeError** at def time (`\|` parses; types don’t support it). |
| **A** | Treats “most recent record” as P0 while SPEC §4 also *intends* surviving `line_sha` after hunk mismatch — spec is internally tense, not a clear impl bug. Hardware-backed keys as P0 overreaches the stated model. |
| **E** | `hostname -s` as “Linux-only” is wrong. Verdict “after fixes” undersells remaining honesty/false-attestation work. |
| **G** | “Four P0s ≈ 20 lines then tag” is optimistic; P1s (Edit fragments, weak transcripts, schema, worktrees) still make a public badge unsafe. |
| **C** | Empty. |

## Unstated assumptions / risks if you follow the wrong review

- **H’s C1 patch** (base64 of raw `.sig`) would fork the on-disk format for no reason; both sides must change together. Do not treat “pipeline is dead” as fact.
- **B’s Counter** can be merged and still ship false attestation.
- **Repo keys:** G is right that *some* out-of-band story is required (CI, second machine). “Never read repo signers” without `--signers` / pin / TOFU leaves verification impossible except on the signing laptop — that is a product hole, not just a security win.
- Unix-only `fcntl`, no Windows, OpenSSH ≥ 8.0: implied, rarely stated as a support matrix.

## Disagreements that matter

1. **Verdict:** B/E/G “after fixes” vs A/D/F/H “not yet.” For a *public provenance badge*, “not yet” is the only honest bar: trust root + “typed by hand” + line/transcript over-claim must change first.
2. **What is P0:** All serious reviews agree on repo `allowed_signers`. D/G correctly add *output lies* (0% = human; unverified ledger still scored). A inflates spec-union and key-hardware. H inflates a non-bug.
3. **line_sha:** disable / demote vs Counter vs context hashes. Safe v0.1 = **do not count fallback in the headline %**.
4. **Transcripts:** several would keep them in the badge. They must not drive `--badge` / headline %.

## Strongest answer: **D**

It ranks by *what the headline number means*: circular trust + UI that calls unverifiable “human,” locale-dependent hashes (CI ≠ laptop), worktrees silently unhooked, concurrent tear + silent skip, adversarial JSON crash/DoS, `--diff` empty-set bug, MultiEdit/tool-result holes, Edit context as “machine,” `quotePath`, setup clobber/smoke-test that cannot fail, canonical JSON for non-Python verifiers, `merge=union`. Severity matches a public Apache-2.0 release.

**A** is the best *checklist* (packaging, tests, doctor, path canonicalization) but slightly mis-ranks. **F** is the best *short* ranking (never say human; 0-line ≠ 100%; fail closed on signers) but misses worktrees/git-config/MultiEdit. **G** has the best unique security catch (`git diff` + repo `diff.external` / textconv). **H** and **B** should not be followed as primary.

## A correct/safe final answer must include

1. **Trust:** default **only** user/env/`--allowed-signers`; repo file opt-in + loud “self-attested”; never `verified_signatures: bool(file)`. Fail closed / three-state: attested / unattested / **unverifiable** (no % , no “typed by hand”).
2. **Honesty:** wording = “no machine-channel provenance,” never human; no 100% on 0 lines; no badge from unsigned transcripts; evidence tier in output.
3. **False attestation:** drop or demote `line_sha` and transcript `weak` from the score; don’t union all historical records as if they were “most recent”; document channel ≠ author.
4. **Correctness:** `Optional` or `from __future__ import annotations` + **3.9 CI** (silent hook death); `exists(.git)`; UTF-8/bytes `norm` shared by hook and verify; path containment; schema + caps; flock+fsync append; don’t swallow malformed ledger lines; hook: tool success, MultiEdit, refuse `..`.
5. **Security:** `git -c diff.external= --no-ext-diff --no-textconv`; temp dir 0700; don’t clobber `allowed_signers` / `settings.json`.
6. **Maintainer bar:** Apache headers + LICENSE, pytest (forgery, 3.9 import, concurrent jsonl, CRLF, `LC_ALL=C`, path `..`, empty/`\n`, tamper), CI ubuntu/macos × 3.9+, OpenSSH `-Y` preflight, `pyproject.toml`. Do **not** require H’s binary-sig rewrite.

**Verdict the release review should end with: not yet** (tag only after trust-root, scoring honesty, and over-attestation paths are fixed — not after B’s four patches).

### z-ai/glm-5.3 reviews
# Meta-review: adjudicating eight hostile reviews of NoHumanWrites

## 0. Ground truth I established first (needed to adjudicate)

I re-derived the behaviour independently; these facts settle most disagreements below.

**The crypto core works.** `ssh-keygen -Y sign` writes an **ASCII-armored** `file.sig` (`-----BEGIN SSH SIGNATURE-----` + base64 of the SSHSIG blob). `open(p + ".sig").read()` is therefore correct; the armor survives `json.dumps` (newlines escaped) and round-trips into `ssh-keygen -Y verify`. Additionally, `json.dumps(..., ensure_ascii=True)` (the default) makes both the stored ledger line and the reconstructed signed payload pure ASCII, so **signature verification is locale-independent**. The encoding bug is confined to *hunk matching* (below). This matters: it scopes the encoding fix correctly and it falsifies Answer H's #1 "critical".

**Real P0-class bugs (all confirmed against the source):**

1. **Trust root inverted.** `verify.allowed_signers()` prefers `<repo>/.nhw/allowed_signers`. A repo ships its own key + self-signed ledger → "verified, 100%". Worse (G's point, missed by others): `setup-key.sh` never writes a repo-side signers file, so for a second machine the attack path is *also the only feature path* — the key-distribution design must be decided, not just the lookup order flipped.
2. **Honesty fails in both directions.** `verified_signatures: bool(signers)` means "a file existed". A reviewer with no keyring gets `0% attested` plus *"unattested = typed by hand… Review those first"* — asserting human authorship when nothing was checkable (violates SPEC rule 1). And a 0-considered-line file prints **"0% attested — 0 of 0 lines"** followed by **"every considered line carries machine provenance"** (the formula gives 0%, not 100%).
3. **Python 3.9.** `str | None` raises **`TypeError` at import** (annotations evaluate at `def` time; it is *not* a `SyntaxError`, and it is *not* swallowed — the module-level `def` fails before the `try/except` around `main()` ever runs, so the hook exits 1 with a traceback, not 0).
4. **Partial-line Edits never match** (found only by G). `Edit.new_string` is frequently a mid-line fragment; the hook hashes the fragment, the verifier hashes whole file lines → record permanently stale, and fragment lines <12 chars get no `line_sha` fallback. The dominant agent operation produces phantom-unattested lines.
5. **Concurrency.** Buffered multi-syscall appends can tear lines; `load_ledger`'s `except: pass` silently eats them → permanent silent attestation loss. Need `flock` + single write (+ fsync) and a malformed-line count in output.
6. **Malicious-ledger robustness.** `r["hunk"]["lines"]` as string/float → `TypeError`; missing `hunk`/`sig` → `KeyError`; `m = re.search(...)` on a malformed `@@` → `AttributeError`. One `ssh-keygen` spawn per record per file = fork-bomb DoS. No caps anywhere.
7. **Encoding.** Hook hashes UTF-8 of tool input; verifier hashes locale-decoded file text (`open(path, errors="replace")`, no `encoding=`). Under `LC_ALL=C` (pre-3.15, no `PYTHONUTF8`) every non-ASCII hunk goes stale → verdicts differ by locale; the verify-in-CI story dies. Fix: hash bytes on both sides (note `str.rstrip()` strips U+00A0, `bytes.rstrip()` doesn't — keep both sides on bytes).

**Confirmed P1s:** `line_sha` fallback attests any identical stripped line anywhere in the file (human retypes an agent line → attested); `l.strip()` discards indent, contradicting SPEC rule 3 "tabs preserved"; 64-bit truncated hashes; SPEC rule 4 says "most recent record" but code unions all records with no ordering (`ts` self-asserted); sliding window `break`s after first match (duplicates/`replace_all` under-covered) and matches anywhere (human paste over-covered); `start`/`end` recorded, never used; worktrees/submodules have `.git` as a *file* → `isdir` misses → silent zero attestation; `MultiEdit`/`NotebookEdit`/`Bash` writes never attested; hook ignores `tool_response` (failed Edits signed) and signs anchor context lines in `new_string`; transcripts: cross-file `weak` union counted as attested, SHA-1@64-bit, failed tool calls indexed, cache hardcoded at `~/nohumanwrites/eval/…` with no invalidation and a corrupt-cache crash, `--rebuild` unreachable from the CLI; `diff_added`: C-quoted paths (`core.quotePath`), `m is None`, untracked files missing, non-zero git exit ignored, ref picked from any non-`--` argv (so `verify.py repo file --diff` silently scores nothing and exits 0), repo config execution (`diff.external`/textconv via a tarball-distributed `.git` or attributes) → need `--no-ext-diff --no-textconv -c diff.external=`; `.nhw/attest.jsonl` itself shows up as unattested added lines in `--diff`; `added or range(...)` — an empty set is falsy → pure-deletion entries score the whole file (D's find); `setup-key.sh` clobbers `allowed_signers`, aborts if `eval/` is missing, pollutes the real repo ledger with smoke records and asserts nothing, no OpenSSH ≥8.0 preflight; `cmd_setup` truncates `settings.json` non-atomically with no backup and no `makedirs(~/.claude)`; canonical JSON unpinned for other implementations; `signer` field never bound to the verifying key; records replayable across repos; SPEC/code drift (`signer` prefix, `producer.model` vs `tool`).

**Points none of the answers made (or made completely):**
- `+++ /dev/null` leaves `cur` stale, and a `@@ -1 +0,0 @@` deletion yields line number **0**, which `report_file`'s `i <= len(lines)` maps to `lines[-1]` — the *previous* diff file's last line gets scored from an unrelated deletion.
- The `ensure_ascii` observation above: it rescues the signature layer from locale issues, so the encoding fix is about hunk matching only — this changes the severity argument D makes (right conclusion, slightly overbroad mechanism).
- `hostname -s` **works on macOS** (BSD `hostname(1)` supports `-s`) — G says this explicitly and is the only one who does.

---

## 1. Per-answer audit

**Answer A** — Broadest coverage (33 items) and a serious test matrix; mostly accurate. Errors: **#8's traversal attack is wrong as stated** — the verifier never opens a record's `path`; it opens user-supplied files and only *compares* record paths, so "a malicious ledger can make the verifier read outside the repository" is false for this code (the real vectors are multi-repo invocations and symlinks). The defensive `repo_relative` validation is still worth taking. #30's version probe (`ssh-keygen -Y sign -f /nonexistent`) always fails and is a sloppy suggestion. Misses: partial-line Edits, the empty-set diff bug, git-config execution, smoke-test ledger pollution, cache path, `merge=union`. Verdict "not yet" — consistent with its findings.

**Answer B** — Weakest substantive review. Real top-3 (trust root, 3.9 TypeError, fallback over-attestation) but: the quoted-path example is **fabricated** (git does not C-quote paths containing spaces; `+++ b/my file.py` parses fine — quoting triggers on tabs/quotes/control chars/non-ASCII), and its patch is wrong anyway (`ln[7:-1]` drops the `b/` prefix and no C-escape decoding); "empty files handled correctly" misses the 0-of-0 contradiction; **"UX honesty: Excellent"** is flatly wrong given the `typed by hand` line, the score-when-unverifiable behaviour, and the untiered badge; the /tmp symlink race is overweighted at "High" (local attacker racing a random mkstemp name); it entirely misses concurrency, malformed-record crashes, encoding, transcripts, cache, MultiEdit, canonical JSON, DoS. "After fixes" is lenient on an incomplete reading.

**Answer C** — Non-answer (model failure). Nothing to evaluate.

**Answer D** — Excellent. Sharpest statement of the two-sided honesty failure (forgeable highs *and* false "human" lows); best encoding treatment (P0.6, bytes-based, with the correct NBSP/`rstrip` subtlety); unique correct finds: the **empty-set `added` bug** (`added is None` fix), `merge=union` gitattributes for the committed ledger, cross-repo **replay**, Edit anchor lines, the `if __name__ == "__main__":` weak-match example, case-insensitive-FS path mismatch, MultiEdit/NotebookEdit/Bash/`tool_response` cluster. Errors: **P0.2 claims the 3.9 failure is "exit 0 by design"** — wrong mechanism (module-level TypeError, exit 1, traceback); misses partial-line Edits, git-config execution, the 0-of-0 render contradiction, symlink/FIFO ledger. Verdict "not yet" with a scoped fix estimate. 

**Answer E** — Solid mid-tier. Correct on trust root, malformed records (good `_valid_record`), multi-repo misattribution (correctly framed as user-input-driven, not ledger-driven), transcript `include_weak=False`, `os.write` O_APPEND, 3.9 (right mechanism, plus the `get_type_hints` caveat), cache mtime invalidation, `~/.claude` makedirs, git-missing handling, worktrees. Errors: **#7's macOS `hostname -s` claim is false**; misses partial-line Edits, window `break`, canonical-JSON pinning, empty-set bug, smoke-test pollution, git-config execution. "After fixes" with a credible blocking list.

**Answer F** — Densest technical audit; uniquely confirms the sig **armor** (implicitly refuting H's C1) and catches the window-`break` asymmetry, FIFO/symlink ledger redirect, `NHW_KEY` login-key hygiene, hook-timeout loss on huge files, ref validation. Errors: **S2 is factually backwards** — a 0-considered-line file reports **0%**, not "100% attested" (the real bug is the 0-of-0 + "every considered line" contradiction, which G states correctly); "SyntaxError on 3.9" is wrong (TypeError); `errors="surrogateescape"` is incomplete (hashing then needs `encode(..., "surrogateescape")` or you trade a decode error for an encode error); S6's "window of n lines can hash-equal a shorter hunk" is mostly theoretical since `lines` is computed from the same stripped text; misses partial-line Edits, the empty-set bug, git-config execution, Edit anchors. Verdict "not yet".

**Answer G** — Strongest single collection of unique, verifiable, high-severity finds: **partial-line Edit hash mismatch** (the bug that breaks the tool's primary workflow — every other reviewer missed it), **git-config execution** in `diff_added` (with the right `-c diff.external= --no-ext-diff --no-textconv` patch), the **trust-distribution design point** ("the attack path is also the only feature path"), `.nhw/attest.jsonl` appearing as unattested added lines in `--diff`, the exact 0-of-0 behaviour, the `line_sha`-strips-indent vs SPEC rule 3 "tabs preserved" contradiction, `--min-attested` CI gating, and the **correct hostname debunk**. Cleanest false-attestation taxonomy (including order-blindness and channel-vs-authorship). Errors: P0-3's claim that the blanket `except` swallows the 3.9 error is wrong (same mechanism error D makes); P1-8's "record path of `../../etc/...` makes the verifier read outside the repo" is overstated for current code (paths are compared, not opened); the P2 claim that `--json` with no evidence "prints prose" is wrong (it prints JSON `null` — D gets this right); the macOS `/tmp` realpath point is marginal. Under-weights encoding (one P2 line vs D's P0) and misses the empty-set diff bug and `merge=union`.

**Answer H** — Right shape, unreliable content. **C1 is fabricated**: `ssh-keygen -Y sign` output is ASCII armor, the pipeline is not dead, and the "≈2⁻²⁵⁶" probability math is nonsense on a false premise (H quotes the *inner* binary SSHSIG blob and mistakes it for the file format). **C5 is fabricated**: macOS `hostname` supports `-s`. C3's "arbitrary file read" is overstated (H itself concedes the path filter blocks it, then hypothesises an `--all` that doesn't exist). M6 is false — the `(no signature check)` string *is* used in `render`. H3's "a single human paste… can claim the rest of the file" overstates (only the pasted lines). H4's spec-contradiction claim is muddled (the code's fallback matches the spec's rule 4; the real contradictions are "most recent" vs union and tabs vs strip). Correct finds do exist (trust root, 3.9, fallback, transcript weak/cache, concurrency, line_span dead weight, settings atomicity), but a maintainer following H's priority list would "fix" a non-existent showstopper first. "Not yet" verdict is right despite the fabrications.

---

## 2. Disagreements, adjudicated

| Contested point | Positions | Correct |
|---|---|---|
| Signature file format | H: binary, pipeline dead; F: armor, OK | **F** (armor; H's C1 is a fabrication) |
| 0-considered-line result | F: 100%; G: 0% + contradiction line | **G** |
| `hostname -s` on macOS | E, H: breaks; G: fine | **G** |
| 3.9 failure mode | A/B/E/H: TypeError at import; F: SyntaxError; D: exit 0; G: swallowed | **A/B/E/H** |
| Ledger-path traversal | A/G/H: verifier opens record paths; E: multi-repo user input; F: hedged | **E/F** (record paths are compared, not opened) |
| Git quoting trigger | B: spaces; D/F/G: non-ASCII/tabs/quotePath | **D/F/G** |
| Fallback vs SPEC | H: code contradicts spec; A/F/G: spec *endorses* the fallback, real contradictions are elsewhere | **A/F/G** |
| UX honesty | B: "Excellent"; everyone else: dishonest in places | **Everyone else** |
| Verdict | B/E/G: after fixes; A/D/F/H: not yet | Operationally identical; "as is" is indefensible |

---

## 3. Strongest answer

**G**, with **D a very close second** (and F third, A fourth, E fifth, H sixth, B last among substantive answers; C is absent).

Why G: it contains the highest density of unique, verifiable, high-severity findings — the partial-line Edit mismatch (which no other reviewer found and which silently breaks the product's core loop), the git-config execution vector in `diff_added`, the trust-distribution design insight that reframes the trust-root fix as a decision rather than a lookup-order patch, the ledger-pollutes-its-own-diff-score interaction, the exact 0-of-0 behaviour, and the `line_sha`/SPEC-tabs contradiction — and it is the only answer that is right on both points where other strong answers fabricated or flipped facts (hostname, 0-of-0). Its taxonomy of false attestation/false negatives is the cleanest and includes the two philosophical points any final answer must carry (order-blindness; key-proves-channel-not-authorship). Its own errors (3.9 swallow mechanism, `--json` null, the traversal aside) are correction-level, not fabrication-level.

D beats G on encoding depth (P0.6 should be a P0 and G under-weights it), the empty-set diff bug, `merge=union`, replay, and the sharpest honesty framing; take D's P0.6/P1.7/P1.13/P1.14 wholesale. F's armor confirmation, FIFO/symlink catch, and window-`break` analysis should also be merged.

---

## 4. What a correct/safe final answer must include

**Blocking (P0):**
1. Trust root: user-held `~/.nhw/allowed_signers` (or explicit flag/env) only; repo file opt-in with a loud self-attestation warning; for PR mode load signers from a trusted ref; fail closed; **decide and document the key-distribution model** (TOFU/pinned/CI-held).
2. Three-state output: attested / unattested / **unverifiable**. `verified_signatures` must be a verified-record count, not file existence; when `signers is None or verified == 0`, print "ledger present, 0/N verified — not scored" and emit no percentage, no badge, no "typed by hand" line. 0-considered-line files → `n/a`. Badge must carry the evidence tier and refuse unsigned evidence. Reword "unattested = typed by hand…" and drop the unwired "git diff aware" claim.
3. `from __future__ import annotations` (or `Optional`) in hook.py and verify.py; state the true 3.9 failure mode; add a 3.9 CI leg.
4. Fix partial-line Edits: locate the fragment, expand to line boundaries, hash whole lines (G's patch), or record both fragment and whole-line hashes.
5. Ledger append: `flock` + single encoded write + fsync; `load_ledger` returns and reports a malformed-line count instead of silent `except: pass`.
6. Record schema validation (types, `v==1`, `sig` size cap, `hunk.lines` bounds, path containment) with per-record `try/except`; caps on records/hunk size; cache signature verification per payload hash to kill the per-record `ssh-keygen` DoS.
7. Byte-consistent hashing: one shared `norm_bytes` used by hook and verifier; `open(path, "rb")` on the verify side; explicit UTF-8 for JSON/ledger I/O; note that `ensure_ascii` already makes the *signature* layer locale-safe, so this is about hunk matching.

**P1:** `line_sha` full SHA-256, `rstrip` not `strip` (or amend SPEC rule 3), count-limited and newest-first matching, reported as a separate weak tier excluded from the headline (or dropped for v0.1) — and amend SPEC rule 4, which currently *endorses* the false-attestation vector; remove the window `break`; use `start`/`end` to seed the search; `os.path.exists(.git)` for worktrees; handle `MultiEdit`/`NotebookEdit`, check `tool_response`, document `Bash` bypass and anchor-line attestation; transcripts: no `weak` in the score, mtime-invalidated cache at `~/.cache`/`~/.nhw`, corrupt-cache rebuild; `diff_added`: `core.quotePath=false`/`-z`, `--no-ext-diff --no-textconv -c diff.external=`, `m` guard, `/dev/null` handling (including the line-0→`lines[-1]` path), untracked files, ref validation, honour git's exit code, exclude `.nhw/` from scoring; `added is None` fix; `setup-key.sh`: merge-not-clobber signers, `mkdir -p eval`, smoke test in `mktemp -d` + `git init` that *asserts* a record landed, OpenSSH ≥8.0 preflight, `chmod 700 ~/.nhw`, document the empty-passphrase key threat (any process as the user — including the agent via `Bash` — can sign: the signature proves key access, not harness provenance); `cmd_setup`: temp + `os.replace` + backup + `makedirs`; pin canonical JSON in SPEC (sorted keys, `(",",":")`, `ensure_ascii`, `allow_nan=False`) with committed golden vectors; document replay/self-asserted `ts`/unbound `signer`/prefix and `model`-vs-`tool` drift; defensive path containment and symlink/FIFO checks on the ledger.

**Maintainer bar:** Apache-2.0 `LICENSE` + SPDX headers, `pyproject.toml` + console script (drop the "single-file CLI" claim), pytest suite (sign/verify round-trip incl. non-ASCII + CRLF, tamper-each-field, the repo-signers forgery as a regression test, partial-line Edit, duplicate/`replace_all`, empty/0-of-0, malformed-ledger fuzz, concurrent appends, worktree, diff fixtures incl. `/dev/null` and quoted paths, 3.9 import), CI matrix (3.9–3.13 × ubuntu/macos + one pre-8.0 OpenSSH leg), `SECURITY.md`/threat model, `.gitattributes` `merge=union` for the ledger, `doctor` subcommand, `--fail-under` exit code.

---

**Verdict: not yet — tag v0.1 only after the P0 set (trust root + key-distribution decision, three-state honesty output, 3.9 annotations, partial-line-Edit hashing, locked appends, ledger schema validation, byte-consistent hashing) and a minimal tests/CI/licence pass land.**

### minimax/minimax-m3 reviews
## Independent findings

Reading the five source files myself before triangulating the answers, here is what I see, then how the answers compare.

### Bugs the answers cluster on (high confidence)

1. **Repo-controlled `allowed_signers` defeats the signature model.** Every competent answer flags this. `verify.allowed_signers()` prefers `<repo>/.nhw/allowed_signers`, so any repo can ship its own key and verify itself. This is the headline product failure. **A, B, D, E, F, G, H** all call it P0/S0/C2. **C** has no answer.

2. **`sig` field is binary SSHsig, not a text-safe string.** The hook does `open(p+".sig").read()` (locale/UTF-8 text mode) and the verifier writes it with `.encode()`. UTF-8-decoding 64 random bytes almost always raises `UnicodeDecodeError`; if it doesn't, JSON will reject control bytes. **H (C1)** is the only answer that actually proves this — **F** gestures at "store `sig` as single-line base64" but treats it as a hardening nit, and **D** says `verify` does `s.write(rec["sig"].encode())` is "fine." It isn't. This is a release blocker **H** got right that nobody else did.

3. **Python 3.9 `str | None` imports crash.** Real. Caught by **A, B, D, E, F, G, H**. **C** again absent.

4. **`repo_root` checks `.git` as a directory only.** Misses git worktrees and submodules where `.git` is a file. Silently zero-attests those repos. Caught by **D, F, G, H**.

5. **Concurrent hook appends can interleave** when a record exceeds `PIPE_BUF` (4096 B); a record with many `line_sha` entries does. Caught by **A, D, E, F, G, H**.

6. **`line_sha` fallback attests any identical line anywhere in the file** (truncated 64-bit hash, indent stripped via `.l.strip()` which **also contradicts SPEC.md rule 3** "tabs preserved" — no answer except **G** notices that exact contradiction). Caught by **A, B, D, E, F, G, H**. **B** and **H** independently propose `Counter` consumption so a hash can attest at most as many lines as the agent actually wrote — that's the correct fix and only they propose it.

7. **Transcript weak-match attributes cross-file identical lines** (and includes failed/rejected tool calls; the `if __name__ == "__main__":` string from `attest.py` will weak-match itself, an attractive nuisance). Caught by **A, D, E, F, G, H**. **H** notes the failed-tool-result gap; **D** notes the self-match.

8. **No record schema validation in the verifier** → a one-line `{}` from a hostile PR crashes `verify.py` with a traceback; with the trust model broken, also a free DoS via millions of records. Caught by **A, D, E, F, G, H**. None of them separately call out that **Python's `json.loads` accepts `NaN`/`Infinity` by default** and those will happily round-trip through the canonicalizer — **A** does. That's the only complete answer on canonicalization.

9. **Path traversal via `rel = os.path.relpath(path, root)`** with no containment check; a record with `path: "../../etc/passwd"` is happily opened. Caught by **A, D, E, G, H**. **G** notes symlinks too.

10. **`line_span` finds the first occurrence of the substring, ignores ambiguity, ignores `start`/`end` in the verifier**, and is miscomputed on CRLF because `body.find(text)` mismatches a normalized-text input against a raw disk read. Caught by **A, D, F, H**.

11. **`cmd_setup` non-atomic `json.dump` over `~/.claude/settings.json`** can truncate the user's live Claude config. Caught by **D, G, H**.

12. **`setup-key.sh` portability: `hostname -s` is GNU-only** (BSD/macOS `hostname` rejects it under `set -e`); the smoke test writes `eval/hooktest.txt` and leaves it; the smoke test asserts nothing because the hook exits 0 by design; `> "$NHW_DIR/allowed_signers"` clobbers existing signers. Caught by **A, D, E, F, G, H**.

13. **0 considered lines → 100% attested.** Real UX lie. Caught by **A, F, G**.

14. **"Unattested" copy implies "human."** The CLI literally prints `"unattested = typed by hand, or written through a channel with no hook"` and `attest.py` exposes `human_or_untracked_ratio`. SPEC §1/§6 says the opposite. Caught by **A, D, E, F, G, H**.

15. **`verified_signatures: bool(signers)`** is "a signers file exists," not "any signature verified." Caught by **A, D, F, G**.

### Things only some answers catch

- **`B`** adds: temp-file symlink race on `p + ".sig"` in `/tmp`. Valid; minor relative to C1/C2 but real.
- **`D`** adds: `git -c core.quotePath=false` / `diff.external=` / non-ASCII path quoting; C-quoted paths break `+++ b/` matching. **G** independently makes the same `diff.external` point — this is a verifier-running-on-hostile-repo-class attack and only those two answers see it.
- **`D`** adds: ledger entries past signature verification count as added lines in `--diff`, dragging the score down. Real.
- **`F`** adds: tool calls that fail (Edit `old_string` not found, permission errors) are still signed because the hook never inspects `tool_response`. **G** independently notes this. Real.
- **`G`** adds: MultiEdit/NotebookEdit are silently unattested; `if not text: return` lets `text == "\n"` through (junk empty-hash records); `producer.model` is in SPEC but not produced. **D** independently notes MultiEdit.
- **`H`** adds: hook reads `~/.nhw/id_nhw` without checking it isn't the user's login key; symlinked/FIFO `.nhw/attest.jsonl` redirects appends into arbitrary files. Real, both.
- **`H`** is alone in being right about **C1** (UTF-8 decoding of binary signature bytes).
- **`B`** and **`H`** are alone in proposing `Counter`-bounded line-hash consumption (correct fix for H4); the others only say "remove or label weak."

### Things no answer gets fully right

- **None** of them audit the *secure* channel of `ssh-keygen -Y sign` itself: it requires the input file to be a regular file, the signature is written next to it, and on some OpenSSH builds `ssh-keygen -Y sign` rejects `-q` together with some other flags. The `verify` path also writes `payload` to a NamedTemporaryFile in the same dir as the signature, which on multi-user systems is information-disclosure (hunks may be confidential). Only **B** mentions the directory-permissions aspect, and only **F** mentions signing-from-stdin as an alternative on newer OpenSSH.
- **None** of them observe that `hook.py` uses `pathlib`-free `open(path, errors="replace")` *without specifying encoding*, so the **hook's** normalization happens on the UTF-8 of the tool-input text, while the **verifier's** normalization happens on the locale-decoded file body. On `LC_ALL=C` (the default in many CI containers) any non-ASCII source hashes to mojibake on the verifier side. **D** does catch this with a complete proposed fix (switch to a shared `norm_bytes` over `bytes`, not `str`). **A, F** mention it. **B** says CRLF is "handled correctly" — it isn't, see above.
- **None** fully reconcile SPEC.md with the implementation: SPEC says `signer: "ed25519:<fingerprint>"`, code writes `"ssh-ed25519:" + fingerprint()`. SPEC says "most recent record whose hunk covers it," code unions all records. SPEC says hunk text "tabs preserved," code `l.strip()` discards indent. **D** and **G** catch the last one specifically.
- **None** note that `verify.attested_lines` is called once per record in `report_file` even though `attested_lines` already returns `verified` and `stale` — those counts are computed and discarded (`nrec, stale` are returned but `report_file` recomputes). Wasted work, hidden stats.
- **None** note that **`open(p, encoding="utf-8")` is required for `attest.jsonl` itself** to be portable; the hook writes it in locale-default and the verifier reads it in locale-default. On a non-UTF-8 system the ledger file is unparseable.
- **None** audit `ssh-keygen`'s stderr on `-Y verify` failure; it is captured and discarded (`capture_output=True`) so the user has no idea *why* a signature failed (expired key? wrong namespace? wrong principal?).

### Specific patches I'd insist on before v0.1

1. **Signature round-trip.** `sign()` must `open(p+".sig", "rb").read()` and `base64.b64encode(...).decode("ascii")` (or write a single envelope format). `sig_ok` must `base64.b64decode(rec["sig"])` and write **bytes**. **H's** patch is correct; the others' are not.

2. **Trust root.** `allowed_signers()` must only return user-owned paths (`~/.nhw/allowed_signers` or explicit `--signers`). Repo-supplied signers must be opt-in via a flag that prints a loud warning. The verifier running on a PR must not see the PR's own keyring. **All seven useful answers agree.**

3. **Signer binding.** `rec["signer"]` must not be self-asserted inside the signed payload without verification. Either verify against each allowed key individually and compare its fingerprint to the claimed one, or treat `signer` as purely cosmetic and label it so in output. **A, F** are most explicit; **D** notes the `-I nhw` constant.

4. **Line-hash fallback.** Use a `Counter` so each signed hash attests at most as many lines as the agent actually wrote. Scan in newest-first order. Match against the normalized-but-*not-stripped* line. Either bind each hash to a recorded line ordinal, or accept the false-positive rate and document it loudly. **B, H** are correct on the fix; the rest hand-wave.

5. **Schema validation in the verifier.** Every record passes `isinstance` checks on `v, path, hunk.lines (int), hunk.sha256 (str, len 64), line_sha (list[str]), sig (str)`. Cap `len(sig) < 8192`, `hunk.lines <= 100_000`, total records per file `10000`. Report malformed counts. **A, D, E, F, G, H** all propose versions of this.

6. **Locked append** (`fcntl.flock` + single `os.write` + `os.fsync`). POSIX-only; document it.

7. **`from __future__ import annotations`** at the top of `hook.py` and `verify.py`; or replace with `Optional[...]`. **All seven agree.**

8. **`repo_root` accepts `.git` as either a directory or a file**; loop with `os.path.dirname(d) == d` sentinel instead of `d != "/"`. **D, G, H**.

9. **Path containment check** in hook and verifier: reject `rel` that escapes `repo` after `realpath`.

10. **Bytes-level normalization** in one shared helper, used by hook and verifier; explicit CRLF→LF; do not `.strip()` indent; do not use `errors="replace"` on text input — use `encoding="utf-8"` and treat decode failure as a non-text file.

11. **Spec/code reconciliation**: either implement "most recent record" (add a monotonic `seq` field, ignore `ts`) or rewrite SPEC §4 to say "union of all verified records whose hunk matches." Drop `start`/`end` from the schema or use them.

12. **0-line files** print `n/a (no lines ≥ 12 chars)` and refuse `--badge`. **A, F, G**.

13. **Drop `weak` transcript match from the headline percentage** entirely, or expose as a separate informational count. Drop `human_or_untracked_ratio` and reword CLI copy to "no provenance" not "human." **A, D, E, F, G, H**.

14. **`cmd_setup` writes `~/.claude/settings.json` atomically** (`tempfile` + `os.replace`, backup), refuses symlinks, refuses non-`json` files.

15. **`setup-key.sh`**: probe `ssh-keygen -Y sign -h` and refuse if missing; trap `EXIT` and clean the smoke-test dir; don't pollute the project repo's `eval/`; merge into `allowed_signers` rather than clobber; portable `hostname` invocation; `chmod 700` on `~/.nhw`; tell the user in the output that the key is unpassphrased.

16. **`git -c core.quotePath=false -c diff.external= -c core.fsmonitor=false diff --no-ext-diff -U0 ...`**; handle C-quoted paths; `--diff-filter=AM`; explicitly handle `/dev/null` and `rename from/to`; union in `git status --porcelain` for untracked files.

17. **Add license headers, `pyproject.toml`, `__version__`, `pytest`, GitHub Actions matrix (Ubuntu + macOS × 3.9–3.13), shellcheck.**

### Answer-by-answer ranking

- **Answer H** is the strongest. It is the only one that correctly diagnoses the UTF-8 decoding of binary signatures (C1), the only one with a fully formed fix for the per-line fallback (Counter-based consumption), and the only one that combines correctness + security + UX + maintainer-checklist in one place without padding. It also catches things the others miss (signer-is-login-key check, FIFO/symlink append redirection, `text == "\n"` empty-hash records). Its "concrete fix priority" list is the right merge order.

- **Answer D** is second. It is the most rigorous on canonicalization (bytes-level normalization across hook and verifier, the C-locale reproducibility argument), the most complete on the `--diff` parser, and its "False-attestation ledger" / "Counted attested though human-typed" enumeration is the clearest. It misses the binary-signature bug and over-states that the signature is "fine" — a meaningful miss — but it is otherwise close to H's quality.

- **Answer G** is third and overlaps significantly with D (likely the same reviewer voice). It catches the `.line.strip()` vs SPEC rule 3 contradiction, the `MultiEdit` gap, the failed-tool-result gap, and has the cleanest three-state output proposal. It also misses the binary-signature bug.

- **Answer A** is fourth: longest, most thorough, but its canonicalization section, while correct, is undercut by not noticing the actual signature round-trip is broken. Its "v0.1 scope reduction" list is genuinely useful. It catches `NaN`/`Infinity` in JSON that nobody else does.

- **Answer F** is fifth: catches most things, severity ordering is right, but its signature section is wrong (treats the broken base64 path as a hardening nit) and it misses several smaller items.

- **Answer E** is sixth: solid and well-organized but less complete than the top four; misses several portability items and the binary-signature bug.

- **Answer B** is seventh: short and useful but a fast first pass; gets the trust-root bug and Python 3.9 right, and has the right Counter fix for line hashes, but skips many items the others caught (MultiEdit, worktree, git config injection, schema validation, atomic writes, canonical JSON).

- **Answer C** is unusable (empty answer attributed to a model error). Treat as no input.

### What a correct, safe v0.1 answer must include

A trustworthy v0.1 ships only after at least these are fixed and tested:

- The binary-signature round-trip (`base64`, explicit `bytes`) — currently every record fails to load.
- User-owned-only `allowed_signers`; repo-bundled keys require an explicit opt-in flag that prints a warning.
- `signer` field bound to the verifying key (or removed from the spec).
- Bytes-level, CRLF-normalized, indent-preserving normalization in a single helper used by hook and verifier.
- Strict per-record schema validation with malformed-record counts.
- Locked (`fcntl.flock`) single-`write` ledger append + atomic `settings.json` write.
- `from __future__ import annotations` (or `Optional`) so the package actually imports on 3.9.
- `repo_root` accepts `.git` as a file (worktrees/submodules).
- Path containment in hook and verifier; no symlink/parent escape.
- Per-line fallback is either removed or Counter-bounded newest-first; SPEC and code reconciled.
- Drop or separate-count transcript `weak` matches; reword UI to say "unattested" not "human."
- `verified_signatures` returns verified counts, not file existence.
- `0` lines → no percentage, no badge.
- `git -c core.quotePath=false -c diff.external= -c core.fsmonitor=false --no-ext-diff`; handle quoted paths and renames.
- `setup-key.sh` OpenSSH ≥ 8.0 preflight, portable `hostname`, non-clobbering allowed-signers update, smoke test in a temp git repo, cleanup trap.
- Tool-result check in the hook; `MultiEdit` handling; drop or fix `text == "\n"` records.
- SPDX license headers, `pyproject.toml`, `__version__`, `pytest`, CI matrix (Ubuntu + macOS × 3.9–3.13), shellcheck on the shell script, golden signature vectors.
- `SECURITY.md` / threat-model doc stating explicitly: (a) the key authenticates the channel not the author; (b) absence of a record asserts nothing; (c) line-hash fallback is content-based not authorship-based.

### Verdict

**Not yet.** The signature pipeline does not actually round-trip today (`open(p+".sig").read()` will `UnicodeDecodeError` on essentially every Ed25519 signature), the trust root is inverted, and the per-line fallback will attest human-typed duplicates as agent-written. After the P0 fixes above — roughly the top half of H's "concrete fix priority" list, plus the binary-signature fix and the Counter-bounded line-hash fix — tag v0.1.

---
> Hand to Claude (orchestrator) for synthesis + final-watch, then Arnaud approves.
