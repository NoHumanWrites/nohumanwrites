#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""NoHumanWrites — the signing hook (layer 1 in production).

Claude Code PostToolUse hook for Write / Edit / MultiEdit.  Reads the hook event
on stdin, finds the text the agent just wrote *as it now sits in the file*
(whole lines, so a partial-line Edit still hashes to what the verifier will
see), signs a canonical record with a DEDICATED ed25519 key via
`ssh-keygen -Y sign` (namespace "nhw"), and appends it under a file lock to
<repo>/.nhw/attest.jsonl — the ledger described in SPEC.md.

What a record proves: this hunk passed through this machine's signing channel.
What it does not prove: who decided its content.  See SECURITY.md.

Never blocks the agent: any failure is logged to ~/.nhw/hook.log and exits 0.
Silent until setup-key.sh has created the key.
"""
from __future__ import annotations
import base64, datetime, fcntl, json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nhw.common import (NAMESPACE, hunk_sha, line_key, norm_text, read_text, repo_root, inside,  # noqa: E402
                        profile_for, unit_keys, sentence_keys)

KEY = os.path.expanduser(os.environ.get("NHW_KEY", "~/.nhw/id_nhw"))
LOG = os.path.expanduser("~/.nhw/hook.log")
MAX_HUNK_LINES = 100_000


def sign(payload: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, dir=os.path.dirname(KEY)) as f:
        f.write(payload); p = f.name
    try:
        subprocess.run(["ssh-keygen", "-Y", "sign", "-f", KEY, "-n", NAMESPACE, "-q", p],
                       check=True, capture_output=True, timeout=20)
        with open(p + ".sig", "rb") as fh:
            armored = fh.read()                      # ssh-keygen writes an ASCII-armoured signature
        return base64.b64encode(armored).decode("ascii")
    finally:
        for x in (p, p + ".sig"):
            try: os.unlink(x)
            except OSError: pass


def fingerprint() -> str:
    out = subprocess.run(["ssh-keygen", "-lf", KEY + ".pub"], capture_output=True, text=True, timeout=10).stdout
    m = re.search(r"(SHA256:\S+)", out)
    return m.group(1) if m else "unknown"


def whole_line_span(body: str, text: str):
    """Locate `text` in the file body and widen to whole lines.  Returns (start, end, hunk_text) 1-based, or None."""
    t = text.strip("\n")
    if not t:
        return None
    i = body.find(t)
    if i < 0:
        return None
    ls = body.rfind("\n", 0, i) + 1
    le = body.find("\n", i + len(t))
    le = len(body) if le < 0 else le
    start = body.count("\n", 0, ls) + 1
    hunk = body[ls:le]
    return start, start + hunk.count("\n"), hunk


def texts_from_event(ev: dict) -> list[str]:
    name, inp = ev.get("tool_name"), ev.get("tool_input", {}) or {}
    if name == "Write":
        return [inp.get("content") or ""]
    if name == "Edit":
        return [inp.get("new_string") or ""]
    if name == "MultiEdit":
        return [e.get("new_string") or "" for e in inp.get("edits", []) or []]
    return []


def append_locked(path: str, line: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)


def record_file(path: str, text: str, producer: dict, root: str | None = None) -> int:
    """Sign every unit of `text` as it sits in `path` (used by `nohumanwrites.py import` for text a
    person received from an AI elsewhere and saved).  Returns records written."""
    root = root or repo_root(path)
    if not root or not inside(root, path):
        return 0
    body = read_text(path)
    if body is None:
        return 0
    return _attest(path, root, body, [text], producer, "import")


def _attest(path, root, body, texts, producer, tool) -> int:
    fp = fingerprint()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    written = 0
    for text in texts:
        span = whole_line_span(body, text)
        if span is None:
            continue                                  # text no longer in the file (overwritten since): nothing to attest
        start, end, hunk = span
        hunk_n = norm_text(hunk)
        if not hunk_n or hunk_n.count("\n") + 1 > MAX_HUNK_LINES:
            continue
        profile = profile_for(path, body)
        rec = {
            "v": 1, "ts": ts,
            "path": os.path.relpath(os.path.realpath(path), root),
            "hunk": {"start": start, "end": end, "lines": hunk_n.count("\n") + 1,
                     "sha256": hunk_sha(hunk), "line_sha": [k for k in (line_key(l) for l in hunk_n.split("\n")) if k]},
            "units": {"profile": profile, "sha": unit_keys(hunk_n, profile),
                      "sentence_sha": sentence_keys(hunk_n) if profile == "prose" else []},
            "producer": dict(producer, tool=tool),
            "signer": "ssh-ed25519:" + fp,
        }
        canonical = json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                               allow_nan=False).encode("utf-8")
        rec["sig"] = sign(canonical)
        os.makedirs(os.path.join(root, ".nhw"), exist_ok=True)
        append_locked(os.path.join(root, ".nhw", "attest.jsonl"),
                      json.dumps(rec, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")
        written += 1
    return written


def main() -> None:
    if not os.path.exists(KEY):                       # not set up on this machine: stay silent
        return
    ev = json.load(sys.stdin)
    if ev.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return
    resp = ev.get("tool_response")
    if isinstance(resp, dict) and resp.get("is_error"):  # the write failed: nothing to attest
        return
    path = (ev.get("tool_input") or {}).get("file_path")
    if not path:
        return
    root = repo_root(path)
    if not root or not inside(root, path):            # only repositories carry a ledger; no escapes
        return
    body = read_text(path)
    if body is None:
        return
    _attest(path, root, body, texts_from_event(ev),
            {"kind": "agent", "harness": "claude-code", "session": ev.get("session_id")}, ev["tool_name"])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never block the agent
        try:
            os.makedirs(os.path.dirname(LOG), exist_ok=True)
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now().isoformat()} {type(e).__name__}: {e}\n")
        except Exception:
            pass
    sys.exit(0)
