# SPDX-License-Identifier: Apache-2.0
"""Shared normalisation and repository helpers for NoHumanWrites.

One definition, used by the hook, the verifier and the transcript reader, so
that a hash computed at write time is the hash computed at verify time on any
machine: bytes decoded as UTF-8 (a file that is not UTF-8 is not scored), CRLF
folded to LF, trailing whitespace stripped per line, indentation kept.
"""
from __future__ import annotations
import hashlib, os

MIN_LEN = 12          # lines shorter than this carry no authorship (braces, 'fi', blanks)
NAMESPACE = "nhw"     # ssh-keygen -Y namespace


def read_text(path: str) -> str | None:
    """UTF-8 text of a file, or None if it is not UTF-8 text."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
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


def line_key(line: str) -> str | None:
    """Per-line hash over the stripped line; None for lines too short to matter."""
    s = line.strip()
    if len(s) < MIN_LEN:
        return None
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


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
