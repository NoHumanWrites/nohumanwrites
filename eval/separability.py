#!/usr/bin/env python3
"""Ground-truth test of the statistical layer.

Human corpus  = what Arnaud typed/dictated to Claude Code (user turns, 40-300
words, no markdown structure, no pasted headers).
AI corpus     = what Claude answered (assistant text blocks, 40-300 words).
Both scored with the sloptrim AI-tell detector.  Reports distributions + AUC.
"""
import json, glob, os, sys, random, re, subprocess, statistics as st
sys.path.insert(0, os.path.expanduser("~/nohumanwrite"))
from nhw.stat import sloptrim_score, burstiness
random.seed(7)
human, ai = [], []
for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    for raw in open(path, errors="replace"):
        try: d = json.loads(raw)
        except: continue
        m = d.get("message", {}); c = m.get("content")
        if d.get("type") == "user" and isinstance(c, str):
            w = len(c.split())
            if 40 <= w <= 300 and not re.search(r"^#|\*\*|^- |```|<system|<command|<local-command", c, re.M):
                human.append(c)
        elif d.get("type") == "assistant" and isinstance(c, list):
            for b in c:
                if b.get("type") == "text":
                    w = len(b["text"].split())
                    if 40 <= w <= 300: ai.append(b["text"])
def dedupe(xs):
    seen=set(); out=[]
    for x in xs:
        k=re.sub(r'\W+',' ',x.lower())[:80]
        if k not in seen: seen.add(k); out.append(x)
    return out
human, ai = dedupe(human), dedupe(ai)
print('unique human', len(human), 'unique ai', len(ai))
random.shuffle(human); random.shuffle(ai)
human, ai = human[:150], ai[:150]
hs = [s for s in (sloptrim_score(t) for t in human) if s is not None]
as_ = [s for s in (sloptrim_score(t) for t in ai) if s is not None]
hb = [b for b in (burstiness(t) for t in human) if b]; ab = [b for b in (burstiness(t) for t in ai) if b]
def auc(pos, neg):  # P(score_ai > score_human)
    wins = sum((a > h) + 0.5*(a == h) for a in pos for h in neg); return round(wins/(len(pos)*len(neg)), 3)
def q(x): x=sorted(x); return [x[int(len(x)*p)] for p in (.1,.5,.9)]
res = {"n_human": len(hs), "n_ai": len(as_),
       "sloptrim_score_p10_p50_p90": {"human": q(hs), "ai": q(as_)},
       "burstiness_p10_p50_p90": {"human": q(hb), "ai": q(ab)},
       "auc_sloptrim_ai_vs_human": auc(as_, hs), "auc_burstiness_human_vs_ai": auc(hb, ab),
       "human_flagged_at_threshold_20": round(sum(h < 20 for h in hs)/len(hs), 3),
       "ai_flagged_as_human_at_threshold_20": round(sum(a < 20 for a in as_)/len(as_), 3)}
print(json.dumps(res, indent=1)); json.dump(res, open(os.path.expanduser("~/nohumanwrite/eval/separability.json"), "w"), indent=1)
