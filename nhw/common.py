# SPDX-License-Identifier: Apache-2.0
"""Shared normalisation, unit splitting and repository helpers for NoHumanWrites.

One definition, used by the hook, the verifier and the checker, so that a hash
computed at write time is the hash computed at verify time on any machine:
bytes decoded as UTF-8 (a file that is not UTF-8 is not scored), CRLF folded to
LF, trailing whitespace stripped per line, indentation kept.

A file is scored in UNITS chosen by its profile:
  code     — lines (the default)                              e.g. .py .js .go .sh .ly
  prose    — paragraphs (blank-line separated), then sentences e.g. .md .txt .tex .rst, books, articles
  verse    — lines, short ones allowed, grouped in stanzas      lyrics, poetry (auto-detected in .txt/.md)
  abc      — bars of an ABC-notation tune                       .abc (sheet music as text)
  musicxml — <measure> elements                                 .musicxml .mxl-extracted .xml scores
The same ledger record format carries a unit list for whichever profile applied.
"""
from __future__ import annotations
import hashlib, os, re

MIN_LEN = 12          # code lines shorter than this carry no authorship (braces, 'fi', blanks)
VERSE_MIN = 3         # verse lines: almost everything counts ("Oh!" does not)
NAMESPACE = "nhw"     # ssh-keygen -Y namespace

CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt", ".c", ".h", ".cpp", ".cs", ".rb",
            ".php", ".swift", ".sh", ".bash", ".zsh", ".sql", ".html", ".css", ".scss", ".json", ".yaml", ".yml",
            ".toml", ".ini", ".cfg", ".ly", ".m", ".r", ".jl", ".lua", ".pl", ".ex", ".exs", ".scala", ".dart"}
PROSE_EXT = {".md", ".markdown", ".txt", ".text", ".rst", ".tex", ".adoc", ".org", ".fountain", ".srt"}


def read_text(path: str) -> str | None:
    """UTF-8 text of a file, or None if it is not UTF-8 text."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    return decode_text(raw)


def decode_text(raw: bytes) -> str | None:
    if b"\x00" in raw[:4096]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def norm_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(l.rstrip() for l in text.split("\n")).strip("\n")


def hunk_sha(text: str) -> str:
    return hashlib.sha256(norm_text(text).encode("utf-8")).hexdigest()


def _key(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def line_key(line: str) -> str | None:
    """Per-line hash over the stripped line; None for lines too short to matter (code profile)."""
    s = line.strip()
    if len(s) < MIN_LEN:
        return None
    return _key(s)


# ---------------------------------------------------------------- profiles and units

def looks_like_verse(text: str) -> bool:
    lines = [l for l in norm_text(text).split("\n") if l.strip()]
    if len(lines) < 6 or "```" in text:
        return False
    short = sum(1 for l in lines if len(l.strip()) <= 50)
    stanza_breaks = norm_text(text).count("\n\n")
    return short / len(lines) >= 0.7 and stanza_breaks >= 1


def looks_like_abc(text: str) -> bool:
    head = norm_text(text)[:2000]
    return bool(re.search(r"^X:\s*\d+", head, re.M)) and bool(re.search(r"^K:", head, re.M))


def profile_for(path: str, text: str | None = None) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".abc":
        return "abc"
    if ext in (".musicxml", ".mxl") or (ext == ".xml" and text and "<score-partwise" in text[:5000]):
        return "musicxml"
    if ext in CODE_EXT:
        return "code"
    if ext in PROSE_EXT or ext == "":
        if text and looks_like_abc(text):
            return "abc"
        if text and looks_like_verse(text):
            return "verse"
        return "prose"
    if text and "<score-partwise" in text[:5000]:
        return "musicxml"
    return "code"


def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def units(text: str, profile: str) -> list[tuple[str, str]]:
    """→ [(label, normalised unit text)] for the profile.  Labels are human-readable positions."""
    t = norm_text(text)
    if profile == "code":
        return [(f"line {i}", l.strip()) for i, l in enumerate(t.split("\n"), 1) if len(l.strip()) >= MIN_LEN]
    if profile == "prose":
        out = []
        for i, p in enumerate([p for p in re.split(r"\n\s*\n", t) if _collapse(p)], 1):
            out.append((f"paragraph {i}", _collapse(p)))
        return out
    if profile == "verse":
        out, stanza, n = [], 1, 0
        for l in t.split("\n"):
            if not l.strip():
                if n:
                    stanza += 1; n = 0
                continue
            n += 1
            if len(l.strip()) >= VERSE_MIN:
                out.append((f"stanza {stanza} line {n}", _collapse(l)))
        return out
    if profile == "abc":
        out, bar = [], 0
        for l in t.split("\n"):
            if not l.strip() or re.match(r"^[A-Za-z]:", l) or l.lstrip().startswith("%"):
                continue                                   # header fields and comments carry no music
            for b in re.split(r"\|+[\]:0-9]*", l):
                b = _collapse(re.sub(r'"[^"]*"', "", b))    # chord symbols out, notes stay
                if len(b) >= 2:
                    bar += 1; out.append((f"bar {bar}", b))
        return out
    if profile == "musicxml":
        out = []
        for m in re.finditer(r"<measure\b([^>]*)>(.*?)</measure>", t, re.S):
            num = re.search(r'number="([^"]+)"', m.group(1))
            body = re.sub(r"<!--.*?-->", "", m.group(2), flags=re.S)
            body = _collapse(re.sub(r">\s+<", "><", body))
            if body:
                out.append((f"measure {num.group(1) if num else len(out) + 1}", body))
        return out
    return units(text, "code")


def unit_keys(text: str, profile: str) -> list[str]:
    return [_key(u) for _, u in units(text, profile)]


def sentence_keys(text: str) -> list[str]:
    """Finer fallback for prose: sentences of 25+ characters, so a lightly edited paragraph keeps its untouched sentences."""
    t = _collapse(norm_text(text))
    return [_key(s) for s in re.split(r"(?<=[.!?])\s+", t) if len(s) >= 25]


# ---------------------------------------------------------------- repositories

def repo_root(path: str) -> str | None:
    """Nearest ancestor holding .git (a directory, or the file a worktree/submodule uses)."""
    d = os.path.realpath(path if os.path.isdir(path) else os.path.dirname(path))
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def inside(repo: str, path: str) -> bool:
    """True if path resolves inside repo (no symlink or ../ escape)."""
    r = os.path.realpath(repo) + os.sep
    return os.path.realpath(path).startswith(r)
