"""Level 2 of the AI Grade label: anchor the ledger head in a public transparency log (Sigstore Rekor).

`nohumanwrites.py anchor` hashes `.nhw/attest.jsonl` as it stands, signs a small head record with the
ledger key, uploads it to Rekor as a `rekord` entry (ssh signature format) and appends the receipt to
`.nhw/anchors.jsonl`, which is committed with the code.  A later verifier checks three things:

  1. continuity  — the anchored byte-prefix of today's ledger still hashes to the anchored value
                   (append-only: nothing before the anchor was rewritten or deleted);
  2. signature   — the head was signed by a key in the verifier's OWN trust root (never the repo's);
  3. inclusion   — Rekor still serves the entry, with the same body, at the recorded index (online only).

What this does and does not give (paper §3, Levels): the ledger's history becomes tamper-evident.  It does
not make a false record true, and the key-holder can still sign anything; that needs a trusted executor.
Zero dependencies: urllib + ssh-keygen.  Rekor's ssh verifier expects namespace "file", so the anchor
signature uses that namespace (the per-hunk records keep "nhw")."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

REKOR = os.environ.get("NHW_REKOR", "https://rekor.sigstore.dev")
ANCHORS = os.path.join(".nhw", "anchors.jsonl")
LEDGER = os.path.join(".nhw", "attest.jsonl")
ANCHOR_NS = "file"          # what rekor's ssh verifier hardcodes
TIMEOUT = 15


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _git_head(repo: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None if r.returncode == 0 else None
    except Exception:
        return None


def ledger_head(repo: str) -> dict | None:
    p = os.path.join(repo, LEDGER)
    if not os.path.exists(p):
        return None
    data = open(p, "rb").read()
    return {"v": 1, "kind": "nhw-anchor", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ledger_sha256": hashlib.sha256(data).hexdigest(), "ledger_bytes": len(data),
            "records": sum(1 for ln in data.splitlines() if ln.strip()), "commit": _git_head(repo)}


def _sign_file(key: str, payload: bytes) -> bytes:
    with tempfile.NamedTemporaryFile(delete=False, dir=os.path.dirname(key)) as f:
        f.write(payload); p = f.name
    try:
        subprocess.run(["ssh-keygen", "-Y", "sign", "-f", key, "-n", ANCHOR_NS, "-q", p],
                       check=True, capture_output=True, timeout=20)
        return open(p + ".sig", "rb").read()
    finally:
        for x in (p, p + ".sig"):
            try: os.unlink(x)
            except OSError: pass


def _verify_sig(keyline: str, payload: bytes, armored: bytes) -> bool:
    with tempfile.NamedTemporaryFile("w", delete=False) as one:
        one.write(f"nhw {keyline.split()[-2]} {keyline.split()[-1]}\n"); onep = one.name
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".sig") as s:
        s.write(armored); sp = s.name
    try:
        r = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", onep, "-I", "nhw", "-n", ANCHOR_NS, "-s", sp],
                           input=payload, capture_output=True, timeout=20)
        return r.returncode == 0
    finally:
        os.unlink(sp); os.unlink(onep)


def _post(url: str, body: dict) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]


def _get(url: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]


def load_anchors(repo: str) -> list[dict]:
    p = os.path.join(repo, ANCHORS)
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            a = json.loads(ln)
            if isinstance(a, dict) and "head" in a and "rekor" in a:
                out.append(a)
        except ValueError:
            continue
    return out


def anchor(repo: str, key: str, fingerprint: str, quiet: bool = False) -> int:
    """Upload the current ledger head to Rekor and record the receipt.  Returns 0 ok, 2 nothing to do, 1 error."""
    head = ledger_head(repo)
    if head is None:
        if not quiet: print("no ledger to anchor (.nhw/attest.jsonl missing)")
        return 2
    prev = load_anchors(repo)
    if prev and prev[-1]["head"].get("ledger_sha256") == head["ledger_sha256"]:
        if not quiet: print(f"ledger unchanged since the last anchor (Rekor index {prev[-1]['rekor'].get('logIndex')}); nothing to do")
        return 2
    head["signer"] = f"ssh-ed25519:{fingerprint}"
    payload = canon(head)
    armored = _sign_file(key, payload)
    pub = open(key + ".pub", encoding="utf-8").read().strip()
    entry = {"apiVersion": "0.0.1", "kind": "rekord",
             "spec": {"data": {"content": base64.b64encode(payload).decode()},
                      "signature": {"format": "ssh", "content": base64.b64encode(armored).decode(),
                                    "publicKey": {"content": base64.b64encode(pub.encode()).decode()}}}}
    status, resp = _post(f"{REKOR}/api/v1/log/entries", entry)
    if status not in (200, 201) or not isinstance(resp, dict):
        print(f"Rekor refused the anchor (HTTP {status}): {resp}"); return 1
    uuid, meta = next(iter(resp.items()))
    rec = {"head": head, "sig": base64.b64encode(armored).decode(),
           "rekor": {"server": REKOR, "uuid": uuid, "logIndex": meta.get("logIndex"),
                     "integratedTime": meta.get("integratedTime"), "logID": meta.get("logID")}}
    with open(os.path.join(repo, ANCHORS), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    if not quiet:
        print(f"anchored: {head['records']} records, ledger sha256 {head['ledger_sha256'][:16]}…, commit "
              f"{(head['commit'] or 'none')[:12]} → Rekor index {meta.get('logIndex')} ({REKOR})")
        print(f"receipt appended to {ANCHORS}; commit it so verifiers can find the anchor.")
    return 0


def status(repo: str, fps: dict[str, str], online: bool = True) -> dict:
    """Level-2 verdict for the label.  Never raises; the dict says what was and was not checked."""
    anchors = load_anchors(repo)
    if not anchors:
        return {"level": 1, "why": "no anchor recorded (run `nohumanwrites.py anchor`)"}
    a = anchors[-1]; head = a["head"]; rk = a.get("rekor", {})
    out = {"level": 1, "logIndex": rk.get("logIndex"), "uuid": rk.get("uuid"), "server": rk.get("server", REKOR),
           "commit": head.get("commit"), "anchored_records": head.get("records"), "ts": head.get("ts")}
    p = os.path.join(repo, LEDGER)
    data = open(p, "rb").read() if os.path.exists(p) else b""
    n = head.get("ledger_bytes", 0)
    if len(data) < n or hashlib.sha256(data[:n]).hexdigest() != head.get("ledger_sha256"):
        out["why"] = "ledger prefix no longer matches the anchor: records before the anchor were changed or removed"
        out["continuity"] = False; return out
    out["continuity"] = True
    out["records_since"] = sum(1 for ln in data[n:].splitlines() if ln.strip())
    claimed = head.get("signer", "").split(":", 1)[-1]
    if claimed not in fps:
        out["why"] = f"anchor signed by a key not in your trust root ({claimed})"; return out
    try:
        armored = base64.b64decode(a["sig"], validate=True)
    except Exception:
        out["why"] = "anchor signature is not valid base64"; return out
    if not _verify_sig(fps[claimed], canon(head), armored):
        out["why"] = "anchor signature does not verify"; return out
    out["signature"] = True
    if not online:
        out["level"] = 2; out["inclusion"] = None; out["note"] = "Rekor entry not re-checked (offline)"; return out
    code, resp = _get(f"{out['server']}/api/v1/log/entries/{rk.get('uuid')}")
    if code != 200 or not isinstance(resp, dict) or not resp:
        out["level"] = 2; out["inclusion"] = None
        out["note"] = f"Rekor entry not re-checked (HTTP {code})"; return out
    _, meta = next(iter(resp.items()))
    try:   # rekor keeps the data's sha256 and the signature, not the data bytes themselves
        body = json.loads(base64.b64decode(meta["body"]))
        served_hash = body["spec"]["data"]["hash"]["value"].lower()
        served_sig = body["spec"]["signature"]["content"]
    except Exception:
        out["why"] = "Rekor served an entry this tool cannot parse"; return out
    strip = lambda b64: b"".join(base64.b64decode(b64).split())    # rekor re-wraps the armour; compare the bytes
    if (served_hash != hashlib.sha256(canon(head)).hexdigest() or strip(served_sig) != strip(a["sig"])
            or meta.get("logIndex") != rk.get("logIndex")):
        out["why"] = "Rekor's entry does not match the recorded anchor"; out["inclusion"] = False; return out
    out["level"] = 2; out["inclusion"] = True; out["integratedTime"] = meta.get("integratedTime")
    return out


def level_line(st: dict) -> str:
    """One phrase for the badge line."""
    if st.get("level") != 2:
        return "Level 1 (self-signed)"
    idx = st.get("logIndex"); c = (st.get("commit") or "")[:8]
    tail = "inclusion verified" if st.get("inclusion") else st.get("note", "recorded")
    since = st.get("records_since") or 0
    extra = f", {since} record(s) since, not yet anchored" if since else ""
    return f"Level 2 (anchored · Rekor #{idx}{' · commit ' + c if c else ''} · {tail}{extra})"
