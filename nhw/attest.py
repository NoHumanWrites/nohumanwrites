#!/usr/bin/env python3
"""NoHumanWrite — layer 1: provenance by construction.

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
CACHE = os.path.expanduser("~/nohumanwrite/eval/attested-index.json")

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
