#!/usr/bin/env python3
"""End-to-end test of the ledger: temp repo, temp key, hook event, verifier.

Run:  python3 tests/test_ledger.py          (exit 0 = pass)
Needs OpenSSH 8.0+ (ssh-keygen -Y). No network.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "nhw", "hook.py")
VERIFY = os.path.join(ROOT, "nhw", "verify.py")

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def main():
    work = tempfile.mkdtemp(prefix="nhw-test-")
    try:
        home = os.path.join(work, "home"); repo = os.path.join(work, "repo")
        os.makedirs(os.path.join(home, ".nhw")); os.makedirs(repo)
        run(["git", "init", "-q", repo])
        key = os.path.join(home, ".nhw", "id_nhw")
        assert run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", key]).returncode == 0, "ssh-keygen failed"
        pub = open(key + ".pub").read().split()[:2]
        open(os.path.join(home, ".nhw", "allowed_signers"), "w").write(f'nhw namespaces="nhw" {pub[0]} {pub[1]}\n')
        env = dict(os.environ, HOME=home, NHW_KEY=key)

        # 1. agent writes a file through the hook
        target = os.path.join(repo, "app.py")
        body = "import os\n\ndef main():\n    print('hello from the agent')\n    return os.getcwd()\n"
        open(target, "w").write(body)
        ev = {"session_id": "t1", "tool_name": "Write", "tool_input": {"file_path": target, "content": body}}
        r = run([sys.executable, HOOK], input=json.dumps(ev), env=env)
        assert r.returncode == 0, r.stderr
        ledger = os.path.join(repo, ".nhw", "attest.jsonl")
        assert os.path.exists(ledger), "no ledger written"
        rec = json.loads(open(ledger).read().splitlines()[-1])
        assert rec["path"] == "app.py" and rec["sig"].startswith("-----BEGIN SSH SIGNATURE-----")
        assert rec["hunk"]["line_sha"], "per-line hashes missing"

        # 2. clean file verifies at 100 %
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "100% attested" in r.stdout, r.stdout + r.stderr

        # 3. a human appends a line → exactly that line is unattested
        with open(target, "a") as fh: fh.write("    # hotfix typed by hand at 23:40, nobody reviewed it\n")
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "unattested: [6]" in r.stdout, r.stdout

        # 4. an edit in the middle breaks the whole-hunk match; per-line hashes still cover the rest
        lines = open(target).read().split("\n"); lines.insert(2, "import sys  # added by hand")
        open(target, "w").write("\n".join(lines))
        r = run([sys.executable, VERIFY, repo, target], env=env)
        assert "1 stale" in r.stdout and "unattested: [3, 7]" in r.stdout, r.stdout

        # 5. tampered record fails signature and covers nothing
        bad = dict(rec); bad["path"] = "other.py"
        open(ledger, "a").write(json.dumps(bad, sort_keys=True) + "\n")
        other = os.path.join(repo, "other.py"); open(other, "w").write(body)
        r = run([sys.executable, VERIFY, repo, other], env=env)
        assert "0% attested" in r.stdout, r.stdout

        # 6. a Write outside any git repo produces no record and no error
        loose = os.path.join(work, "loose.txt"); open(loose, "w").write("not in a repo\n" * 3)
        ev2 = {"session_id": "t2", "tool_name": "Write", "tool_input": {"file_path": loose, "content": open(loose).read()}}
        r = run([sys.executable, HOOK], input=json.dumps(ev2), env=env)
        assert r.returncode == 0 and not os.path.exists(os.path.join(work, ".nhw"))

        print("ok: 6 checks passed")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
