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
