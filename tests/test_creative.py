#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Beyond code: books, lyrics, poetry, sheet music, exported documents, media.

Run:  python3 tests/test_creative.py     (exit 0 = pass)
"""
import json, os, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "nohumanwrites.py")
sys.path.insert(0, ROOT)
from nhw.common import profile_for, units  # noqa: E402

CHAPTER = """The harbour at dawn was quieter than the town ever admitted to being. Boats knocked against the quay in a rhythm nobody kept and everybody heard. Marta counted the gulls because counting was easier than deciding.

By the time the bakery opened she had decided anyway. She would take the early train, and she would not telephone first, and she would let the door do the explaining when she stood in it.

The train was late, which she took as agreement.
"""

LYRICS = """Woke up with the road in my chest
Sand in the tank, no time to rest

Love over fear, that's the deal
Twist it open, let it feel

Chorus comes round like the sun
Never stopped and never done
"""

ABC = """X:1
T:Ubaye Morning
M:6/8
L:1/8
K:D
D2 F A2 d | f2 e d2 B | A2 F D2 F | E3 E3 |
D2 F A2 d | f2 e d2 B | A2 F E2 D | D3 D3 |
"""

MUSICXML = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0"><part-list><score-part id="P1"><part-name>Music</part-name></score-part></part-list>
<part id="P1">
<measure number="1"><note><pitch><step>D</step><octave>4</octave></pitch><duration>2</duration></note></measure>
<measure number="2"><note><pitch><step>F</step><alter>1</alter><octave>4</octave></pitch><duration>2</duration></note></measure>
<measure number="3"><note><pitch><step>A</step><octave>4</octave></pitch><duration>4</duration></note></measure>
</part></score-partwise>
"""


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def main():
    work = tempfile.mkdtemp(prefix="nhw-creative-"); checks = 0
    try:
        home = os.path.join(work, "home"); repo = os.path.join(work, "book")
        os.makedirs(os.path.join(home, ".nhw")); os.makedirs(repo); run(["git", "init", "-q", repo])
        key = os.path.join(home, ".nhw", "id_nhw")
        assert run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", key]).returncode == 0
        pub = open(key + ".pub").read().split()[:2]
        open(os.path.join(home, ".nhw", "allowed_signers"), "w").write(f'nhw namespaces="nhw" {pub[0]} {pub[1]}\n')
        env = dict(os.environ, HOME=home, NHW_KEY=key)

        # 0. profiles are detected from content, not just extension
        assert profile_for("x.md", CHAPTER) == "prose" and profile_for("x.txt", LYRICS) == "verse"; checks += 1
        assert profile_for("tune.abc", ABC) == "abc" and profile_for("score.musicxml", MUSICXML) == "musicxml"; checks += 1
        assert len(units(ABC, "abc")) == 8 and len(units(MUSICXML, "musicxml")) == 3 and len(units(CHAPTER, "prose")) == 3; checks += 1

        # 1. a book chapter received from an AI is imported as received → 3 paragraphs attested
        ch = os.path.join(repo, "chapter1.md"); open(ch, "w").write(CHAPTER)
        r = run([sys.executable, CLI, "import", ch, "--from", "claude.ai"], env=env)
        assert "1 signed record" in r.stdout and "prose" in r.stdout, r.stdout + r.stderr; checks += 1
        r = run([sys.executable, CLI, "check", ch, "--json"], env=env); d = json.loads(r.stdout)
        assert d["state"] == "scored" and d["unattested"] == 0 and d["files"][0]["unit"] == "paragraph", r.stdout; checks += 1

        # 2. the author rewrites one sentence of paragraph 2 → "edited"; adds a new paragraph → "unattested"
        edited = CHAPTER.replace("She would take the early train,", "She would take the night ferry,") + "\nShe had never once been late for anything that mattered.\n"
        open(ch, "w").write(edited)
        r = run([sys.executable, CLI, "check", ch, "--json"], env=env); d = json.loads(r.stdout); f = d["files"][0]
        assert f["edited"] == ["paragraph 2"] and f["unattested"] == ["paragraph 4"], r.stdout; checks += 1

        # 3. lyrics: imported, then one line changed by the songwriter → that verse line is unattested
        ly = os.path.join(repo, "song.txt"); open(ly, "w").write(LYRICS)
        run([sys.executable, CLI, "import", ly, "--from", "chatgpt"], env=env)
        open(ly, "w").write(LYRICS.replace("Twist it open, let it feel", "Twist it open, let it heal"))
        r = run([sys.executable, CLI, "check", ly, "--json"], env=env); d = json.loads(r.stdout); f = d["files"][0]
        assert f["profile"] == "verse" and f["unattested"] == ["stanza 2 line 2"], r.stdout; checks += 1

        # 4. sheet music in ABC: a bar changed by hand → that bar is unattested
        ab = os.path.join(repo, "tune.abc"); open(ab, "w").write(ABC)
        run([sys.executable, CLI, "import", ab, "--from", "suno"], env=env)
        open(ab, "w").write(ABC.replace("A2 F E2 D | D3 D3 |", "A2 F E2 D | D6 |"))
        r = run([sys.executable, CLI, "check", ab, "--json"], env=env); d = json.loads(r.stdout); f = d["files"][0]
        assert f["profile"] == "abc" and f["unattested"] == ["bar 8"], r.stdout; checks += 1

        # 5. MusicXML: a measure changed → that measure is unattested
        mx = os.path.join(repo, "score.musicxml"); open(mx, "w").write(MUSICXML)
        run([sys.executable, CLI, "import", mx, "--from", "claude.ai"], env=env)
        open(mx, "w").write(MUSICXML.replace("<duration>4</duration>", "<duration>3</duration>"))
        r = run([sys.executable, CLI, "check", mx, "--json"], env=env); d = json.loads(r.stdout); f = d["files"][0]
        assert f["profile"] == "musicxml" and f["unattested"] == ["measure 3"], r.stdout; checks += 1

        # 6. exported .docx of the (edited) chapter: paragraphs matched against the whole ledger
        docx = os.path.join(repo, "chapter1.docx")
        paras = [p for p in edited.split("\n\n") if p.strip()]
        xml = '<?xml version="1.0"?><w:document xmlns:w="w"><w:body>' + "".join(f"<w:p><w:r><w:t>{p.strip()}</w:t></w:r></w:p>" for p in paras) + "</w:body></w:document>"
        with zipfile.ZipFile(docx, "w") as z:
            z.writestr("word/document.xml", xml)
        r = run([sys.executable, CLI, "check", docx, "--json"], env=env); d = json.loads(r.stdout); f = d["files"][0]
        assert f["unit"] == "paragraph" and f["edited"] == ["paragraph 2"] and f["unattested"] == ["paragraph 4"], r.stdout; checks += 1

        # 7. media: a file with a C2PA marker is reported as carrying credentials, one without as no provenance
        os.makedirs(os.path.join(repo, "art"))
        with open(os.path.join(repo, "art", "cover.jpg"), "wb") as fh: fh.write(b"\xff\xd8\xff\xe0" + b"\x00" * 64 + b"jumb\x00\x00\x00c2pa" + b"\x00" * 64)
        with open(os.path.join(repo, "art", "plain.png"), "wb") as fh: fh.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
        r = run([sys.executable, CLI, "check", os.path.join(repo, "art")], env=env)
        assert "cover.jpg: carries a C2PA" in r.stdout and "plain.png: no Content Credentials" in r.stdout, r.stdout; checks += 1

        # 8. a poem nobody imported: no provenance, and the word "human" never appears in the verdict
        po = os.path.join(work, "loose.txt"); open(po, "w").write("Roses in the rain\n\nNobody logged this\n\nAnd nobody should guess\n")
        r = run([sys.executable, CLI, "check", po], env=dict(env, HOME=os.path.join(work, "nohome")))
        assert "no provenance" in r.stdout and "human" not in r.stdout.lower().replace("nohumanwrites", ""), r.stdout; checks += 1

        print(f"ok: {checks} checks passed"); return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
