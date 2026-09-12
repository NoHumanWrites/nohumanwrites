#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""NoHumanWrites — machinize: the mirror image of a humaniser.  The result is an "AI Made" version.

A humaniser takes machine-written text and rewrites it so that a style detector says "human".
It erases provenance.  `machinize` goes the other way and keeps the record.  It takes a work a
person wrote (a paper, a chapter, a song, a poem, a transcript) and produces a version made by
the machine end to end:

  1. claims    — the machine lists the work's claims and the sources it cites;
  2. sources   — each cited source is looked up (Crossref, Open Library, Wikipedia; stdlib only)
                 and recorded as matched / ambiguous (a bare name) / not found / unchecked, with the candidate
                 and the URL that answered (a match is a candidate for a person to confirm, not a confirmation);
  3. logic     — the machine reviews the claims for unsupported steps, contradictions and errors
                 it can identify, and proposes corrections;
  4. rewrite   — every passage is rewritten in the machine's own words with the corrections
                 applied; numbers, dates, names and terms are kept, nothing else is added;
  5. record    — the output is signed into the ledger with the derivation on the record (source
                 hash, declared origin, verbatim carry-over) and the verification summary; the
                 report file is signed too.

Nothing is asserted about the source.  "declared human" is the person's statement, exactly as
`import --from claude.ai` records the person's statement about where a text came from.  The
output earns the grade its channel earns and the report says "derived" next to it.

Engines: `ollama` (local, default; the text never leaves the machine — only the source look-ups do,
and `--offline` stops those), `claude` (the `claude` CLI, `-p`), or `command:<shell command>`
(reads the prompt on stdin, writes the answer on stdout).
"""
from __future__ import annotations
import json, os, re, shlex, subprocess, sys, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nhw.common import hunk_sha, norm_text, read_text, repo_root, sentence_keys, unit_keys, profile_for  # noqa: E402

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
PREFERRED = ("qwen2.5:14b", "qwen2.5:7b", "llama3.1:8b", "hermes3:8b")
CHUNK_WORDS = 320
UA = "NoHumanWrites/0.3 (+https://nohumanwrites.org)"

CLAIMS_PROMPT = (
    "CLAIMS. Read the work below and return ONLY a JSON object with two keys. "
    "\"claims\": a list of the work's factual or logical claims, each a short sentence, at most 25. "
    "\"sources\": a list of the works, authors or authorities the text cites or relies on, each as a short string "
    "(author and title or subject), at most 25. No prose before or after the JSON.\n\nWORK:\n"
)
LOGIC_PROMPT = (
    "LOGIC. You are reviewing a work for its logic and its facts, as a careful referee. Below are the work's claims, "
    "then what could be verified about its sources. Return ONLY a JSON list of issues, at most 15, each an object with "
    "\"claim\" (quote or paraphrase), \"problem\" (unsupported step, contradiction, factual error, outdated figure, or "
    "circular reasoning), \"severity\" (\"high\", \"medium\" or \"low\"), \"fix\" (the corrected statement, ONLY if you are "
    "confident the claim is wrong and know the right one; otherwise null) and \"evidence\" (what would settle it, when fix is null). "
    "Judge the work by the knowledge of its own time where it is a historical text, and say so in \"problem\". "
    "If the work holds up, return []. No prose before or after the JSON.\n\n"
)
REWRITE_PROMPT = (
    "REWRITE. Produce the machine-made version of the passage below. Rewrite every sentence in your own words. "
    "Keep the meaning, the order of the claims, and every number, date, proper name, citation and technical term "
    "exactly as given, except where the CORRECTIONS list says otherwise: apply those corrections in the text itself, "
    "plainly, without brackets or notes. Add no other fact. Drop no fact. Do not copy or quote any sentence verbatim. "
    "Output only the rewritten passage as plain paragraphs separated by blank lines, with no preamble and no notes.\n\n"
)
VERSE_PROMPT = (
    "REWRITE. Produce the machine-made version of the verse below: same number of lines and stanzas, same subject, "
    "same images in the same order, rewritten line by line in your own words so that no line survives verbatim. "
    "Keep names and numbers. Output only the verse, one line per line, stanzas separated by a blank line.\n\n"
)


# ---------------------------------------------------------------- engines

def ollama_models() -> list[str]:
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5) as r:
            return [m["name"] for m in json.load(r).get("models", [])]
    except Exception:
        return []


def pick_model(engine: str, model: str | None) -> str | None:
    if model or engine != "ollama":
        return model
    have = ollama_models()
    for p in PREFERRED:
        if p in have:
            return p
    return next((m for m in have if "embed" not in m and "llava" not in m), None)


def ask(prompt: str, engine: str, model: str | None) -> str:
    if engine == "ollama":
        body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                           "options": {"temperature": 0.5, "num_ctx": 8192}}).encode("utf-8")
        req = urllib.request.Request(OLLAMA + "/api/generate", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=1800) as r:
            return json.load(r)["response"].strip()
    if engine == "claude":
        cmd = ["claude", "-p"] + (["--model", model] if model else [])
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=1800)
        if p.returncode:
            raise RuntimeError(p.stderr.strip()[:300] or "claude -p failed")
        return p.stdout.strip()
    if engine.startswith("command:"):
        p = subprocess.run(shlex.split(engine[len("command:"):]), input=prompt, capture_output=True, text=True, timeout=1800)
        if p.returncode:
            raise RuntimeError(p.stderr.strip()[:300] or "command failed")
        return p.stdout.strip()
    raise ValueError(f"unknown engine {engine!r}: use ollama, claude, or command:<shell command>")


def parse_json(text: str, want=dict):
    """Small models wrap JSON in prose or fences; take the first object/list that parses."""
    text = re.sub(r"```(?:json)?", "", text)
    opener, closer = ("{", "}") if want is dict else ("[", "]")
    start = text.find(opener)
    while start != -1:
        end = text.rfind(closer)
        while end > start:
            try:
                v = json.loads(text[start:end + 1])
                if isinstance(v, want):
                    return v
            except ValueError:
                pass
            end = text.rfind(closer, 0, end)
        start = text.find(opener, start + 1)
    return want()


# ---------------------------------------------------------------- stages

def blocks(text: str, profile: str) -> list[tuple[str, str]]:
    """→ [(kind, text)]: headings pass through; prose paragraphs are grouped into passages; verse goes stanza by stanza."""
    out, chunk, n = [], [], 0
    for p in re.split(r"\n\s*\n", norm_text(text)):
        p = p.strip()
        if not p:
            continue
        if p.startswith("#") or (profile != "verse" and len(p.split()) < 8):
            if chunk:
                out.append(("prose", "\n\n".join(chunk))); chunk, n = [], 0
            out.append(("keep", p)); continue
        if profile == "verse":
            out.append(("verse", p)); continue
        chunk.append(p); n += len(p.split())
        if n >= CHUNK_WORDS:
            out.append(("prose", "\n\n".join(chunk))); chunk, n = [], 0
    if chunk:
        out.append(("prose", "\n\n".join(chunk)))
    return out


def _get_json(url: str):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=15) as r:
            return json.load(r)
    except Exception:
        return None


def _overlap(q: str, cand: str) -> bool:
    a = {w for w in re.findall(r"[a-z]{4,}", q.lower())}
    b = {w for w in re.findall(r"[a-z]{4,}", cand.lower())}
    return bool(a) and len(a & b) >= min(2, len(a)) and len(a & b) / len(a) >= 0.5


def lookup_source(q: str) -> dict:
    """Try Crossref (papers), Open Library (books), then Wikipedia (people, works, subjects).
    A query with a single significant word (a bare name) can only be ambiguous: it is reported as such, never matched."""
    qs = urllib.parse.quote(q)
    if len({w for w in re.findall(r"[a-z]{4,}", q.lower())}) < 2:
        d3 = _get_json(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={qs}&format=json&srlimit=1")
        hits = (d3 or {}).get("query", {}).get("search", []) if d3 else []
        return {"query": q, "status": "ambiguous", "where": "wikipedia" if hits else None, "match": hits[0]["title"] if hits else None,
                "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(hits[0]["title"].replace(" ", "_")) if hits else None}
    d = _get_json(f"https://api.crossref.org/works?query.bibliographic={qs}&rows=1")
    items = (d or {}).get("message", {}).get("items", []) if d else []
    if items:
        it = items[0]
        title = (it.get("title") or [""])[0]
        if _overlap(q, title + " " + " ".join(a.get("family", "") for a in it.get("author", []))):
            return {"query": q, "status": "matched", "where": "crossref", "match": title[:120], "url": it.get("URL")}
    d2 = _get_json(f"https://openlibrary.org/search.json?q={qs}&limit=1")
    docs = (d2 or {}).get("docs", []) if d2 else []
    if docs:
        t = docs[0].get("title", "") + " " + " ".join(docs[0].get("author_name", []))
        if _overlap(q, t):
            return {"query": q, "status": "matched", "where": "openlibrary", "match": docs[0].get("title", "")[:120],
                    "url": "https://openlibrary.org" + docs[0].get("key", "")}
    d3 = _get_json(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={qs}&format=json&srlimit=1")
    hits = (d3 or {}).get("query", {}).get("search", []) if d3 else []
    if hits and _overlap(q, hits[0].get("title", "")):
        return {"query": q, "status": "matched", "where": "wikipedia", "match": hits[0]["title"],
                "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(hits[0]["title"].replace(" ", "_"))}
    answered = any(x is not None for x in (d, d2, d3))
    return {"query": q, "status": "not found" if answered else "unchecked", "where": None, "match": None, "url": None}


def carry_over(src: str, out: str, profile: str) -> dict:
    """How much of the source survived verbatim, keyed like the ledger."""
    s_sent, o_sent = sentence_keys(src), set(sentence_keys(out))
    s_u, o_u = unit_keys(src, profile), set(unit_keys(out, profile))
    return {"sentences": len(s_sent), "sentences_verbatim": sum(k in o_sent for k in s_sent),
            "units": len(s_u), "units_verbatim": sum(k in o_u for k in s_u), "unit": "line" if profile == "verse" else "paragraph"}


def style_score(text: str):
    """The statistical layer, for the record only (weak; paper §6)."""
    try:
        from nhw.stat import sloptrim_score, DET
        return sloptrim_score(text) if os.path.exists(DET) else None
    except Exception:
        return None


# ---------------------------------------------------------------- the pipeline

def machinize(path: str, out: str, engine: str = "ollama", model: str | None = None, declared: str = "human",
              verify: bool = True, offline: bool = False, sign: bool = True, profile: str | None = None, log=print) -> dict:
    src = read_text(path)
    if src is None:
        raise ValueError(f"{path}: not UTF-8 text")
    model = pick_model(engine, model)
    if engine == "ollama" and not model:
        raise RuntimeError(f"no Ollama model found at {OLLAMA}; pull one (ollama pull qwen2.5:7b) or use --engine claude")
    profile = profile or profile_for(path, src)
    if profile not in ("prose", "verse"):
        profile = "prose"
    log(f"machinize: {os.path.basename(path)} → {os.path.basename(out)} via {engine}" + (f" ({model})" if model else "") + f", {profile}")

    # 1-3: claims, sources, logic
    claims, sources, checked, issues = [], [], [], []
    if verify:
        log("  1/4 claims and cited sources …")
        cj = parse_json(ask(CLAIMS_PROMPT + src, engine, model), dict)
        claims = [str(c)[:300] for c in cj.get("claims", []) if str(c).strip()][:25]
        sources = []
        for x in cj.get("sources", []):
            for part in re.split(r"\s+(?:and|&)\s+", str(x)) if re.search(r"^[A-Z][^,]*\s(?:and|&)\s[A-Z]", str(x)) else [str(x)]:
                if part.strip():
                    sources.append(part.strip()[:200])
        sources = sources[:25]
        log(f"  2/4 sources: {len(sources)} cited" + (", checking online …" if sources and not offline else ""))
        checked = [lookup_source(s) if not offline else {"query": s, "status": "unchecked", "where": None, "match": None, "url": None}
                   for s in sources]
        for c in checked:
            log(f"      {c['status']:9} {c['query'][:70]}" + (f"  → {c['url']}" if c.get("url") else ""))
        log("  3/4 logic review …")
        lj = ask(LOGIC_PROMPT + "CLAIMS:\n" + "\n".join(f"- {c}" for c in claims) + "\n\nSOURCES:\n"
                 + "\n".join(f"- {c['query']}: {c['status']}" + (f" ({c['match']})" if c.get("match") else "") for c in checked)
                 + "\n\nWORK:\n" + src, engine, model)
        issues = [i for i in parse_json(lj, list) if isinstance(i, dict) and i.get("problem")][:15]
        for i in issues:
            log(f"      [{str(i.get('severity', '?'))[:6]}] {str(i.get('problem', ''))[:60]}: {str(i.get('claim', ''))[:60]}")
    fixes = [i for i in issues if isinstance(i.get("fix"), str) and i["fix"].strip() and i["fix"].strip().lower() not in ("null", "none", "n/a")]
    corrections = "\n".join(f"- {i.get('claim', '')} → {i['fix']}" for i in fixes) or "- none"

    # 4: rewrite
    parts = blocks(src, profile)
    todo = sum(1 for k, _ in parts if k != "keep")
    log(f"  4/4 rewrite: {todo} passage(s) …")
    result, done = [], 0
    for kind, text in parts:
        if kind == "keep":
            result.append(text); continue
        done += 1
        log(f"      passage {done}/{todo}: {len(text.split())} words")
        if kind == "verse":
            result.append(ask(VERSE_PROMPT + "VERSE:\n" + text, engine, model))
        else:
            result.append(ask(REWRITE_PROMPT + "CORRECTIONS:\n" + corrections + "\n\nPASSAGE:\n" + text, engine, model))
    body = "\n\n".join(result).strip() + "\n"
    with open(out, "w", encoding="utf-8") as f:
        f.write(body)

    # 5: record
    co = carry_over(src, body, profile)
    root = repo_root(out)
    rel = (lambda p: os.path.relpath(os.path.realpath(p), root)) if root else os.path.basename
    derivation = {"path": rel(path), "sha256": hunk_sha(src), "declared": declared, "units": co["units"], "carry_over": co}
    verification = {"claims": len(claims), "sources_cited": len(sources),
                    "sources_matched": sum(c["status"] == "matched" for c in checked),
                    "sources_not_found": sum(c["status"] == "not found" for c in checked),
                    "sources_unchecked": sum(c["status"] == "unchecked" for c in checked),
                    "sources_ambiguous": sum(c["status"] == "ambiguous" for c in checked),
                    "issues": len(issues), "issues_high": sum(str(i.get("severity", "")).lower() == "high" for i in issues),
                    "corrections_applied": len(fixes), "needs_evidence": len(issues) - len(fixes)} if verify else None
    report_path = re.sub(r"(\.[^.]+)?$", "-report.md", out, count=1)
    report = render_report(out, engine, model, derivation, claims, checked, issues, verify)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    summary = {"source": path, "out": out, "report": report_path, "engine": engine, "model": model, "profile": profile,
               "derived_from": derivation, "verification": verification, "claims": claims, "sources": checked, "issues": issues,
               "words_in": len(src.split()), "words_out": len(body.split()),
               "style_score_weak": {"source": style_score(src), "out": style_score(body)}, "records": 0}
    if sign:
        from nhw import hook
        if not os.path.exists(hook.KEY):
            log("  not signed: no key (run: python3 nohumanwrites.py setup)")
        elif not root:
            log("  not signed: the output is not inside a git repository (the ledger lives in the repo)")
        else:
            producer = {"kind": "machinized", "harness": engine, "model": model, "session": None,
                        "derived_from": derivation, "verification": verification}
            summary["records"] = hook.record_file(out, body, producer)
            summary["records"] += hook.record_file(report_path, report, dict(producer, derived_from=dict(derivation, report_for=rel(out))))
    return summary


def render_report(out, engine, model, derivation, claims, checked, issues, verify) -> str:
    co = derivation["carry_over"]
    lines = [f"# AI Made · verification report for {os.path.basename(out)}", "",
             f"Source: `{derivation['path']}` (declared {derivation['declared']}; sha256 {derivation['sha256']}). "
             f"Engine: {engine}{' ' + model if model else ''}. Unit: {co['unit']}.", "",
             f"Verbatim carry-over: {co['sentences_verbatim']} of {co['sentences']} sentences, "
             f"{co['units_verbatim']} of {co['units']} {co['unit']}s.", ""]
    if not verify:
        lines += ["Verification was skipped (`--no-verify`): this is a rewrite only.", ""]
        return "\n".join(lines)
    lines += ["## Claims the machine read", ""] + [f"{i}. {c}" for i, c in enumerate(claims, 1)] + [""]
    lines += ["## Sources cited, and what answered", ""]
    lines += [f"- {c['query']} — **{c['status']}**" + (f" ({c['where']}: {c['match']}) {c['url']}" if c.get("url") else "") for c in checked] or ["- none cited"]
    lines += ["", "## Logic review", ""]
    def fix_of(i):
        f = i.get("fix")
        return f.strip() if isinstance(f, str) and f.strip() and f.strip().lower() not in ("null", "none", "n/a") else None
    lines += [f"- [{i.get('severity', '?')}] {i.get('claim', '')}: {i.get('problem', '')}"
              + (f" → applied in the text: {fix_of(i)}" if fix_of(i) else f" → needs evidence: {i.get('evidence') or 'not stated'}")
              for i in issues] or ["- no issue found"]
    lines += ["", "The review is the machine's. A matched source is a candidate record for a person to confirm, and a not-found one is a look-up miss as often as a bad citation. Both the text and this report are signed into the ledger with the derivation on the record.", ""]
    return "\n".join(lines)
