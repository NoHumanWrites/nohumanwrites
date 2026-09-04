#!/usr/bin/env python3
"""NoHumanWrites — layer 3: statistical fallback (weak, labelled as such).

Wraps the local sloptrim detector (71 documented AI-writing patterns, stdlib
only) and INVERTS it: a passage with almost no AI tells inside a document that
is otherwise dense with them is the candidate human insertion.  This layer is
evidence, never proof — see paper §6 on base rates.
"""
import subprocess, json, sys, os, re, statistics as st
DET = os.path.expanduser("~/.claude/plugins/cache/sloptrim/sloptrim/0.9.0/scripts/detect.py")

def sloptrim_score(text):
    p = subprocess.run([sys.executable, DET], input=text, capture_output=True, text=True)
    try: return json.loads(p.stdout)["_metrics"]["ai_tell_score"]
    except Exception: return None

def burstiness(text):
    s = [len(x.split()) for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
    return round(st.pstdev(s)/ (st.mean(s) or 1), 3) if len(s) > 1 else None

def profile(path):
    text = open(path, errors="replace").read()
    paras = [p for p in re.split(r"\n\s*\n", text) if len(p.split()) >= 40]
    scores = [(sloptrim_score(p), burstiness(p), p[:70].replace("\n"," ")) for p in paras]
    return {"path": path, "doc_score": sloptrim_score(text), "doc_burstiness": burstiness(text),
            "paragraphs": len(paras), "lowest_tell_paragraphs": sorted([s for s in scores if s[0] is not None], key=lambda t: t[0])[:3]}

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(profile(p), indent=1))
