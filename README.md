# NoHumanWrite

Find the bytes a human typed inside machine-written work.

Every AI-text detector asks "did a machine write this?". In an agent-first workflow the machine writes by default, and the interesting spans are the ones a person inserted by hand without the tests, sources and logs the agent's work carries. NoHumanWrite attributes files line by line against the agent harness's own logs, falls back to git authorship, and keeps a statistical layer only as triage.

## Layout

```
nhw/attest.py       layer 1: provenance from Claude Code transcripts (Write/Edit tool calls)
nhw/gitmode.py      layer 1b: git blame + Co-Authored-By trailers
nhw/stat.py         layer 3: inverted AI-tell scoring (sloptrim), labelled weak
nhw.py              CLI tying the layers together
eval/separability.py   human-vs-machine ground-truth test on your own transcripts
eval/*.json         results from the run reported in the paper
paper/nohumanwrite.md  the paper
business.md         the business plan
video-outline.md    the launch video
SPEC.md             proposed signed-ledger format (.nhw/attest.jsonl)
```

## Run

```bash
python3 nhw.py index            # build the attested-line index from ~/.claude/projects
python3 nhw.py file <path>...   # attribute files; add --show to list unattested lines
python3 nhw.py git <path>...    # git-based attribution
python3 nhw.py stat <path>...   # statistical triage (weak)
python3 eval/separability.py    # reproduce the AUC / base-rate numbers on your data
```

Standard library only. Nothing leaves the machine.

## Results on the author's machine (2026-09-04)

- 2,716 logged agent writes over 5 weeks → 72,681 attested lines.
- Code written inside the harness: 96 % median line attestation.
- The PoC's own source, written by the same agent through a shell heredoc: 9 %. Unlogged channels look human. That is why the product is a signed ledger, not log forensics.
- Statistical layer: AUC 0.91 for machine-vs-human, but 60 % of machine passages carry no tell, so as a human detector its precision at 5 % prevalence is about 8 %.

## What this is not

No AI-text detector for grading people. No humaniser. No watermark removal. See paper §7.

Licence: Apache-2.0 (proposed).
