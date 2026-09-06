#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""End-to-end tests of the ledger: temp repo, temp key, hook events, verifier.

Run:  python3 tests/test_ledger.py          (exit 0 = pass)
Needs OpenSSH 8.0+ (ssh-keygen -Y). No network.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "nhw", "hook.py")
VERIFY = os.path.join(ROOT, "nhw", "verify.py")
CLI = os.path.join(ROOT, "nohumanwrites.py")
BODY = "import os\n\ndef main():\n    print('hello from the agent')\n    return os.getcwd()\n"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def hook(env, path, tool="Write", **inp):
    ev = {"session_id": "t", "tool_name": tool, "tool_input": dict(file_path=path, **inp)}
    r = run([sys.executable, HOOK], input=json.dumps(ev), env=env)
    assert r.returncode == 0, r.stderr
    return r


def main():
    work = tempfile.mkdtemp(prefix="nhw-test-")
    checks = 0
    try:
        home = os.path.join(work, "home"); repo = os.path.join(work, "repo")
        os.makedirs(os.path.join(home, ".nhw")); os.makedirs(repo)
        run(["git", "init", "-q", repo])
        key = os.path.join(home, ".nhw", "id_nhw")
        assert run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", key]).returncode == 0, "ssh-keygen failed"
        pub = open(key + ".pub").read().split()[:2]
        open(os.path.join(home, ".nhw", "allowed_signers"), "w").write(f'nhw namespaces="nhw" {pub[0]} {pub[1]}\n')
        env = dict(os.environ, HOME=home, NHW_KEY=key)
        ledger = os.path.join(repo, ".nhw", "attest.jsonl")

        # 1. agent writes a file → one signed record with per-line hashes
        target = os.path.join(repo, "app.py"); open(target, "w").write(BODY)
        hook(env, target, content=BODY)
        rec = json.loads(open(ledger).read().splitlines()[-1])
        assert rec["path"] == "app.py" and rec["hunk"]["line_sha"], rec; checks += 1

        # 2. clean file verifies at 100 %
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "100% attested" in r.stdout and "1 verified" in r.stdout, r.stdout + r.stderr; checks += 1

        # 3. a human appends a line → exactly that line is unattested
        with open(target, "a") as fh: fh.write("    # hotfix typed by hand at 23:40, nobody reviewed it\n")
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "unattested: [6]" in r.stdout, r.stdout; checks += 1

        # 4. an insertion in the middle breaks the whole-hunk match; per-line hashes still cover the rest
        lines = open(target).read().split("\n"); lines.insert(2, "import sys  # added by hand")
        open(target, "w").write("\n".join(lines))
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "1 stale" in r.stdout and "unattested: [3, 7]" in r.stdout, r.stdout; checks += 1

        # 5. a PARTIAL-LINE Edit is widened to whole lines, so the verifier finds it
        body = open(target).read().replace("hello from the agent", "hello from the agent, v2"); open(target, "w").write(body)
        hook(env, target, tool="Edit", old_string="hello from the agent", new_string="hello from the agent, v2")
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "2 verified" in r.stdout and "unattested: [3, 7]" in r.stdout, r.stdout; checks += 1

        # 6. duplicate-line budget: a human pasting an attested line twice more gets only the signed count covered
        with open(target, "a") as fh: fh.write("    print('hello from the agent, v2')\n    print('hello from the agent, v2')\n")
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "unattested: [3, 7, 8, 9]" in r.stdout or "unattested: [3, 7, 9]" in r.stdout, r.stdout; checks += 1

        # 7. tampered record: signer field bound → fails; wrong path → no coverage
        bad = dict(rec); bad["path"] = "other.py"
        open(ledger, "a").write(json.dumps(bad, sort_keys=True) + "\n")
        other = os.path.join(repo, "other.py"); open(other, "w").write(BODY)
        r = run([sys.executable, VERIFY, repo, other], env=env)
        assert "UNVERIFIABLE" in r.stdout, r.stdout; checks += 1

        # 8. malformed and oversized records are counted, not crashed on
        open(ledger, "a").write('{"v":1,"path":"app.py","hunk":{"lines":"x"},"sig":"a","signer":"b"}\nnot json\n')
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert r.returncode == 0 and "malformed" in r.stdout, r.stdout + r.stderr; checks += 1

        # 9. repo-supplied allowed_signers is IGNORED by default (forgery attempt)
        atk = os.path.join(work, "atk"); os.makedirs(atk)
        run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", os.path.join(atk, "k")])
        apub = open(os.path.join(atk, "k.pub")).read().split()[:2]
        open(os.path.join(repo, ".nhw", "allowed_signers"), "w").write(f'nhw namespaces="nhw" {apub[0]} {apub[1]}\n')
        forged = os.path.join(repo, "forged.py"); open(forged, "w").write(BODY)
        hook(dict(env, NHW_KEY=os.path.join(atk, "k"), HOME=atk), forged, content=BODY)
        env_nokeys = dict(env, HOME=os.path.join(work, "nohome")); os.makedirs(os.path.join(work, "nohome"))
        r = run([sys.executable, VERIFY, repo, forged], env=env_nokeys)
        assert "UNVERIFIABLE" in r.stdout or "unverifiable" in r.stdout, r.stdout; checks += 1
        r = run([sys.executable, VERIFY, repo, forged, "--trust-repo-signers"], env=env_nokeys)
        assert "REPOSITORY-SUPPLIED" in r.stdout and "100% attested" in r.stdout, r.stdout; checks += 1

        # 10. a Write outside any git repo produces no record and no error
        loose = os.path.join(work, "loose.txt"); open(loose, "w").write("not in a repo\n" * 3)
        hook(env, loose, content=open(loose).read())
        assert not os.path.exists(os.path.join(work, ".nhw")); checks += 1

        # 11. the CLI refuses to score when it has no evidence, and never says "human"
        empty = os.path.join(work, "empty"); os.makedirs(empty); open(os.path.join(empty, "a.txt"), "w").write("typed by hand, nothing logged\n")
        r = run([sys.executable, CLI, "check", empty], env=dict(env, HOME=os.path.join(work, "nohome")))
        assert "no provenance" in r.stdout and "human" not in r.stdout.lower().replace("nohumanwrites", ""), r.stdout; checks += 1

        # 12. the label: earned only by a signed ledger under our own keys, refused on unsigned evidence
        clean = os.path.join(repo, "clean.py"); open(clean, "w").write(BODY); hook(env, clean, content=BODY)
        r = run([sys.executable, CLI, "check", clean, "--label"], env=env)
        assert r.returncode == 0 and "AI Grade 100" in r.stdout and "Pure" in r.stdout, r.stdout + r.stderr; checks += 1
        r = run([sys.executable, CLI, "check", forged, "--label", "--trust-repo-signers"], env=env_nokeys)
        assert r.returncode == 5 and "no label" in r.stdout and "not yours" in r.stdout, r.stdout + r.stderr; checks += 1

        # 13. Level 2: anchor against a fake Rekor (local HTTP server), verify inclusion, then break continuity
        import base64, hashlib, http.server, threading
        store = {}
        class FakeRekor(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def _send(self, code, obj):
                b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            def do_POST(self):
                e = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                data = base64.b64decode(e["spec"]["data"]["content"])
                body = {"apiVersion": "0.0.1", "kind": "rekord", "spec": {"data": {"hash": {"algorithm": "sha256", "value": hashlib.sha256(data).hexdigest()}},
                        "signature": e["spec"]["signature"]}}
                uuid = hashlib.sha256(data).hexdigest(); store[uuid] = {"logIndex": len(store) + 1, "integratedTime": 1, "logID": "fake",
                                                                        "body": base64.b64encode(json.dumps(body).encode()).decode()}
                self._send(201, {uuid: store[uuid]})
            def do_GET(self):
                uuid = self.path.rsplit("/", 1)[-1]
                self._send(200, {uuid: store[uuid]}) if uuid in store else self._send(404, {"message": "no such entry"})
        srv = http.server.HTTPServer(("127.0.0.1", 0), FakeRekor); threading.Thread(target=srv.serve_forever, daemon=True).start()
        env_rekor = dict(env, NHW_REKOR=f"http://127.0.0.1:{srv.server_port}")
        r = run([sys.executable, CLI, "anchor", "--repo", repo], env=env_rekor, cwd=repo)
        assert r.returncode == 0 and "Rekor index 1" in r.stdout and os.path.exists(os.path.join(repo, ".nhw", "anchors.jsonl")), r.stdout + r.stderr; checks += 1
        r = run([sys.executable, CLI, "check", clean, "--label"], env=env_rekor)
        assert "Level 2 (anchored" in r.stdout and "inclusion verified" in r.stdout, r.stdout + r.stderr; checks += 1
        b = bytearray(open(ledger, "rb").read()); i = b.find(b'"path"'); b[i + 1] = ord("P"); open(ledger, "wb").write(bytes(b))
        r = run([sys.executable, CLI, "check", clean, "--label"], env=env_rekor)
        assert "Level 1" in r.stdout and "prefix no longer matches" in r.stdout, r.stdout + r.stderr; checks += 1
        srv.shutdown()

        # 16. Level 3 (local): the hook records an executor claim only when the effective settings deny it the key
        iso = os.path.join(repo, "iso.py"); open(iso, "w").write(BODY); hook(env, iso, content=BODY)
        assert "executor" not in open(ledger).read().splitlines()[-1], "executor claimed without a sandbox"; checks += 1
        os.makedirs(os.path.join(repo, ".claude")); json.dump({"sandbox": {"enabled": True, "allowUnsandboxedCommands": False,
            "credentials": {"files": [{"path": os.path.dirname(key), "mode": "deny"}]}}}, open(os.path.join(repo, ".claude", "settings.json"), "w"))
        open(iso, "w").write(BODY + "x = 1\n"); hook(env, iso, content=BODY + "x = 1\n")
        last = json.loads(open(ledger).read().splitlines()[-1])
        assert last["producer"].get("executor", {}).get("self_reported") is True, last["producer"]; checks += 1

        print(f"ok: {checks} checks passed")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
