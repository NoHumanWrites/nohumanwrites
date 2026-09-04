# NoHumanWrite — from idea to business

Draft v0.1 · 4 September 2026 · companion to `paper/nohumanwrite.md`

## One line

A pull-request check that tells an AI-first engineering team which bytes a human typed by hand, so those bytes get the review the agent's work already had.

## Why now

Three things landed in the same month. Agents write most new code on serious teams. The EU began requiring machine-generated text to be marked (Article 50, 2 August 2026) and Anthropic complied worldwide. And nobody shipped the tool that reads those facts back to the team. Every existing detector points the wrong way: at students and job applicants, asking whether a machine helped. Our customer has the opposite worry and no vendor.

## The wedge (first product)

**NoHumanWrite for GitHub.** Install the app, add one hook to the agent harness, and every pull request gets:

1. One number in the status check: *94 % of changed bytes machine-attested*.
2. The unattested hunks highlighted inline, with the reason (no signature / signature mismatch / unlogged channel).
3. A policy the team picks: comment only, require a second approver on unattested hunks, require a passing test touching the file, or block.

Under the hood: a signed ledger, `.nhw/attest.jsonl`, appended by a PostToolUse hook on each agent write (Claude Code first; Codex and Cursor adapters next). The app verifies signatures and does the diff arithmetic. Nothing leaves the repo except the numbers; the ledger is plain JSON any auditor can read.

What it is not: a detector of AI text, a "humaniser", or a watermark remover. Those are the competitor's category and the video's recipe, and we stay out of both on principle.

## Who pays

- **Teams already agent-first** (10–200 engineers, Claude Code / Codex / Cursor in daily use). Pain: they trust the agent more than their own 23:40 hot-fixes and cannot see where the hot-fixes are. Buyer: engineering lead. Price: **$12 per seat per month**, free for public repositories.
- **Regulated engineering** (fintech, medtech, anyone with a change-management audit). Pain: auditors now ask "which parts did the AI write?" and the answer today is a shrug. Buyer: compliance plus engineering. Price: custom, starting around $1,500 per month per organisation, sold on the ledger as audit evidence.
- **Later, documents.** The same ledger at paragraph level for research notes and reports, sold to labs and consultancies. This waits on vendor watermark detectors (paper §4, layer 2); when Anthropic or Google expose one, the document product needs no harness cooperation at all.

No market-size figure is invented here. The addressable base is the population of teams paying for agent coding tools, which the vendors publish quarterly; take the current number from their reports rather than from this page.

## Competition and moat

| Who | What they do | Why they do not cover this |
|---|---|---|
| GPTZero, Originality, Turnitin | Statistical AI detection for education and publishing | Opposite direction; the paper shows statistics fail at ours (PPV under 10 %) |
| C2PA / Content Credentials | Signed provenance for images, audio, video | No text profile; no repository integration |
| Sigstore, SLSA, GitHub artifact attestations | Signed build provenance | Attest who built the binary, not who wrote the source lines |
| Vendor watermarks (Anthropic, Google) | Prove a machine produced text, key held by issuer | No public detector yet; we are the reader when one ships, not a rival |
| GitHub / Anthropic themselves | Could add a native "written by agent" badge | Real risk. Moat is being cross-vendor and policy-driven: a team with Claude and Codex needs one ledger, not two badges |

## What makes it defensible

- The ledger format, published as an open spec and adopted before vendors ship their own.
- The policy engine and the audit story, which vendors have no incentive to build across each other's tools.
- The data: months of per-team ratios become the benchmark nobody else has ("your unattested share is 6 %; median for teams your size is 11 %").

## 30-day build

| Week | Deliverable | Done when |
|---|---|---|
| 1 | Claude Code hook → signed `.nhw/attest.jsonl` (ed25519, key per developer) | Every `Write`/`Edit` in a test repo produces a verifiable record |
| 2 | GitHub App: status check + inline annotations + three policies | Runs on our own repos; blocks an unattested hunk on purpose |
| 3 | Codex and Cursor adapters; `nhw` CLI for local runs | Same ledger from three harnesses |
| 4 | Publish: paper v1 on arXiv (cs.SE), repo public under Apache-2.0, 8-minute video, five design partners from the Claude Code community | Five installs on real repositories, ratios reported back |

Cost to reach week 4: developer time plus under $100 in hosting. The proof of concept already exists (`nhw/`), measured on real data.

## Risks, stated

- **Vendor ships native.** Mitigation: be the cross-vendor standard first; make the ledger format boring and open.
- **Teams do not care which hunks are human.** Test in week 4 with the five partners: if the number does not change one review decision per week, stop.
- **Coverage gap.** Any unlogged channel looks human (paper §5, the 9 % result). Mitigation: the hook is the product; log forensics is only the demo.
- **Perception.** "No human write" reads as anti-human. The framing that lands is "no unreviewed bytes"; the human's judgement stays in the prompt and the review, where it belongs.

## Publishing plan

1. **arXiv preprint** (cs.SE, cross-list cs.CL), the paper as is, with the repository link. Establishes the inversion and the base-rate argument in public.
2. **Repository** public under Apache-2.0 with the ledger spec, the PoC and the evaluation scripts, reproducible on any Claude Code user's own transcripts in under a minute.
3. **Video** (see `video-outline.md`): the Chase AI video as foil, the inversion as the turn, the 9 % result as the honest punchline, a live install as the close.
4. **Discussion venues:** the Claude Code community, r/ExperiencedDevs, Hacker News with the title "Detecting the human in AI-written code", and a short note to the C2PA text working group.

## Decision points for Arnaud

- Name: keep **NoHumanWrite** (memorable, provocative) or ship the product as the softer **Attest** with NoHumanWrite as the paper's title. Recommendation: keep the name for the paper and the launch, rename only if partners object.
- Entity: this is a parallel project, separate from Plus de Fun and LOVE&RIDE. It needs its own repository and, if it earns revenue, its own invoicing line.
- Go on the arXiv submission: needs an endorsement for cs.SE if the account has none; a first-time submitter typically waits one to two days for moderation.
