#!/usr/bin/env python3
"""NoHumanWrite — layer 1b: git authorship.

Uses `git blame` + commit trailers.  A line is machine-attested when the commit
that introduced it carries a `Co-Authored-By: Claude …` trailer or comes from a
bot identity; otherwise it is human-attributed.  Coarser than transcript
attestation (a human can commit AI text and vice-versa) but works on any repo.
"""
import subprocess, sys, re, json, os
from collections import Counter

BOT = re.compile(r"bot|claude|codex|copilot|goldensis|\[bot\]", re.I)

def blame(path):
    out = subprocess.run(["git", "blame", "--line-porcelain", path],
                         capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(path)) or ".")
    if out.returncode: return None
    commits, order = {}, []
    cur = None
    for ln in out.stdout.splitlines():
        m = re.match(r"^([0-9a-f]{40}) \d+ \d+", ln)
        if m: cur = m.group(1); order.append(cur); commits.setdefault(cur, {})
        elif ln.startswith("author ") and cur: commits[cur]["author"] = ln[7:]
    return commits, order

def trailer_is_ai(sha, cwd):
    msg = subprocess.run(["git", "show", "-s", "--format=%B", sha], capture_output=True, text=True, cwd=cwd).stdout
    return bool(re.search(r"Co-Authored-By:.*(Claude|Codex|Copilot)", msg, re.I))

def attribute(path):
    r = blame(path)
    if not r: return {"path": path, "error": "not in git"}
    commits, order = r
    cwd = os.path.dirname(os.path.abspath(path))
    ai_sha = {s for s in commits if trailer_is_ai(s, cwd) or BOT.search(commits[s].get("author", ""))}
    c = Counter("ai" if s in ai_sha else "human" for s in order)
    n = sum(c.values()) or 1
    return {"path": path, "lines": n, "ai_lines": c["ai"], "human_lines": c["human"],
            "ai_ratio": round(c["ai"]/n, 3), "authors": Counter(commits[s].get("author") for s in order).most_common(3)}

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(attribute(p), default=str))
