#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""machinize: a human work in, a signed AI Made version out, derivation and verification on the record.

Run:  python3 tests/test_machinize.py     (exit 0 = pass).  Uses a command engine, so no model or network is needed.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "nohumanwrites.py")
KEY = os.path.expanduser(os.environ.get("NHW_KEY", "~/.nhw/id_nhw"))

DRAFT = """# A short note

The harbour at dawn was quieter than the town ever admitted to being. Boats knocked against the quay in a rhythm nobody kept and everybody heard. Marta counted the gulls because counting was easier than deciding.

By the time the bakery opened she had decided anyway. She would take the early train, and she would not telephone first, and she would let the door do the explaining when she stood in it.
"""
# a stand-in model: answers the CLAIMS and LOGIC prompts with fixed JSON, and rewrites a passage by
# reversing the words of every sentence, so nothing survives verbatim
STUB_SRC = r"""
import sys, re
t = sys.stdin.read()
if t.startswith("CLAIMS."):
    print('{"claims": ["The harbour is quiet at dawn", "Marta takes the early train"], "sources": ["Bradshaw railway guide"]}')
elif t.startswith("LOGIC."):
    print('[{"claim": "counting was easier than deciding", "problem": "unsupported step", "severity": "low", "fix": "counting felt easier than deciding"}, {"claim": "the train was late", "problem": "unsupported step", "severity": "low", "fix": null, "evidence": "a timetable"}]')
else:
    p = t.split("PASSAGE:\n", 1)[-1].split("VERSE:\n", 1)[-1]
    print("\n\n".join(" ".join(" ".join(reversed(s.split())) for s in re.split(r"(?<=[.!?])\s+", q)) for q in re.split(r"\n\s*\n", p)))
"""


def run(*args, cwd):
    return subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, cwd=cwd)


def main():
    if not os.path.exists(KEY):
        print("SKIP: no signing key (run setup)"); return 0
    d = tempfile.mkdtemp(prefix="nhw-mz-")
    try:
        subprocess.run(["git", "init", "-q", d], check=True)
        stub = os.path.join(d, "stub.py"); open(stub, "w").write(STUB_SRC)
        engine = f"command:{sys.executable} {stub}"
        src = os.path.join(d, "draft.md"); open(src, "w").write(DRAFT)
        # rewrite only
        p = run("machinize", "draft.md", "--engine", engine, "--no-verify", "--json", cwd=d)
        assert p.returncode == 0, p.stdout + p.stderr
        s = json.loads(p.stdout); co = s["derived_from"]["carry_over"]
        assert s["records"] == 2, s["records"]                       # the text and the report
        assert co["sentences"] >= 4 and co["sentences_verbatim"] == 0, co
        assert s["derived_from"]["declared"] == "human" and len(s["derived_from"]["sha256"]) == 64
        assert s["verification"] is None
        out = os.path.join(d, "draft-machinized.md")
        assert open(out).read().startswith("# A short note"), "heading should pass through unchanged"
        assert "skipped" in open(os.path.join(d, "draft-machinized-report.md")).read()
        # with verification (offline: sources stay unchecked, the logic issue is applied)
        p = run("machinize", "draft.md", "--out", "v.md", "--engine", engine, "--offline", "--json", cwd=d)
        assert p.returncode == 0, p.stdout + p.stderr
        s = json.loads(p.stdout); v = s["verification"]
        assert v == {"claims": 2, "sources_cited": 1, "sources_matched": 0, "sources_not_found": 0, "sources_unchecked": 1,
                     "sources_ambiguous": 0, "issues": 2, "issues_high": 0, "corrections_applied": 1, "needs_evidence": 1}, v
        rep = open(os.path.join(d, "v-report.md")).read()
        assert "Bradshaw" in rep and "unchecked" in rep and "applied in the text:" in rep and "needs evidence: a timetable" in rep, rep
        # a second run on the same output path leaves ONE derived line in the check, the live one
        p = run("machinize", "draft.md", "--out", "v.md", "--engine", engine, "--offline", "--json", cwd=d)
        assert p.returncode == 0, p.stdout + p.stderr
        # the source itself stays unattested: no record ever signs the human draft
        c = run("check", "draft.md", "--json", cwd=d); r = json.loads(c.stdout)
        assert r["unattested"] == r["lines"] > 0, r
        # the output is fully attested and reported as derived, with the verification summary
        c = run("check", "v.md", "--json", cwd=d); r = json.loads(c.stdout)
        assert r["unattested"] == 0 and r["lines"] > 0, r
        assert len(r["derived"]) == 1 and r["derived"][0]["declared"] == "human" and r["derived"][0]["verification"]["claims"] == 2, r["derived"]
        lab = run("check", "v.md", "--label", "--offline", cwd=d).stdout
        assert "AI Grade 100" in lab and "DERIVED" in lab and "_derived" in lab, lab
        # refuses to overwrite the source
        p = run("machinize", "draft.md", "--out", "draft.md", "--engine", engine, cwd=d)
        assert p.returncode == 2, p.stdout
        # verse: line by line, stanza by stanza
        open(os.path.join(d, "song.txt"), "w").write("Woke up with the road in my chest\nSand in the tank, no time to rest\n\nLove over fear, that is the deal\nTwist it open, let it feel\n")
        p = run("machinize", "song.txt", "--engine", engine, "--no-verify", "--profile", "verse", "--json", cwd=d)
        s = json.loads(p.stdout)
        assert s["profile"] == "verse" and s["derived_from"]["carry_over"]["unit"] == "line", s["profile"]
        print("machinize: 3 scenarios, 18 checks OK")
        return 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
