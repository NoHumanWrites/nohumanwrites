# NoHumanWrite: finding the human in machine-written work

Arnaud Chrétien · draft v0.1 · 4 September 2026
Code and data: `~/nohumanwrite` (to be published under Apache-2.0)

## Abstract

Every deployed AI-text detector answers one question: did a machine write this? For a team that writes with agents all day, that question is backwards. The machine is the default author. Its output arrives with a prompt, a diff, a log and usually a test run. The spans a person inserts by hand arrive with none of that, and in our experience they are where the incidents live. This paper proposes the inverted task, locating human insertions inside machine-written material, and shows why the statistical methods built for the original task cannot perform it. On 300 ground-truth passages from one developer's own agent sessions, the best local detector separates machine from human prose with an AUC of 0.91, yet 60 % of machine passages carry no detectable tell, so a "no tell means human" rule has a precision near 8 % at a realistic 5 % human share. Provenance recorded at the moment of writing has no such ceiling. A proof of concept that reconstructs line-level authorship from an agent harness's own logs attests 96 % of lines (median) in code the agent wrote, 0 % in hand-written notes, and, in the most instructive result, 9 % in its own source, which the same agent produced through an unlogged shell channel. That gap defines the product: a signed, append-only authorship ledger emitted by every writing tool, verified at review time. We situate the design against the EU AI Act's Article 50 marking duty, Anthropic's worldwide text watermark, SynthID-Text and C2PA, and argue that reading these marks for the writer's own benefit is the use the transparency regime was missing.

## 1. The inversion

The public conversation about AI text runs in one direction. Schools want to know whether a student wrote the essay. Editors want to know whether a freelancer used a model. Regulators want machine output labelled so that citizens can tell. A video published this week captures the mood: it explains that Anthropic's Fable 5.1 now watermarks all of its text and then spends seven minutes on a recipe for laundering that text through a local model so the mark disappears [14].

Watch a working engineer for a day and the direction reverses. On the machine used for this paper, 2,716 file writes were made by an agent in five weeks, each one logged with the exact bytes, the session and the timestamp. The human-typed changes over the same period left no such record. They were made in an editor, in a hurry, often after the agent had finished and the tests had already passed. When something broke later, the question in the retrospective was never "did the AI write this?" It was "who touched this after the AI was done?"

That question has no tooling. This paper is about building it. We call the task NoHumanWrite, not because human writing is unwelcome but because in an agent-first workflow the human's contribution belongs in the prompt and the review, and a human byte in the artefact itself is an exception path that deserves a second look.

## 2. Background

**Watermarks.** Kirchenbauer et al. showed in 2023 that a language model can bias its token choices toward a pseudo-random "green list" at negligible quality cost, producing text a key-holder can later identify with high confidence [1]. Google DeepMind's SynthID-Text refined this into a tournament sampling scheme, published in Nature in October 2024 and deployed across Gemini [2]; the detector and the generation-side code are open source [10]. Anthropic adopted a scheme of this family for models released on or after 2 August 2026, applying it worldwide and across every product surface, with no opt-out, to satisfy Article 50 of the EU AI Act [12, 13]. The detection key is not public. As of this writing Anthropic has said only that detection details will follow in technical documentation [12].

**Statistical detectors.** Zero-shot methods such as DetectGPT [5] and Binoculars [6] score text by how a reference model would have predicted it; supervised methods such as Ghostbuster [7] train a classifier on features from weaker models. The RAID benchmark showed most of these degrade sharply under paraphrase and domain shift [8]. Sadasivan et al. gave the theoretical reason: as generated text approaches the human distribution, any detector's best possible performance approaches a coin flip, and a paraphraser can push it there [3]. OpenAI withdrew its own classifier in July 2023 for low accuracy [9]. Liang et al. found that commercial detectors flag essays by non-native English writers as machine-made at rates above 60 % [4]. The last result matters for us because our task, done badly, would produce the mirror-image injustice: calling a person's work machine-made when it is not.

**Provenance.** For images, audio and video, the C2PA specification defines signed Content Credentials that travel with the file and record who or what produced it [11]. Anthropic now attaches C2PA manifests to media its sandbox produces [12]. There is no text profile, and nothing comparable exists for source code at the line level. Git records who committed, not who wrote; a developer who commits an agent's output under their own name is telling the truth about the commit and nothing about the authorship.

## 3. What a human insertion is, and why it matters

We define a human insertion as any span in an artefact that was not produced by a logged machine write. In code this is the hot-fix typed at 23:40, the constant changed by hand, the `except: pass` added to get a deploy through. In research writing it is the sentence added to the machine's draft without a source. In operations it is the config line changed on the server and never mirrored into the repository.

The harm is not that a person wrote it. The harm is that it skipped the pipeline. The agent's span was produced from an instruction that is on record, checked by whatever tests ran, and reproducible. The human span has an author but no provenance, and the review process, having already approved the machine's pull request, tends to wave the follow-up through. A tool that surfaces these spans does not judge them; it routes them to the review they missed.

This framing also answers the obvious objection. Nobody proposes to forbid human edits. The proposal is that an unattested span should cost one extra approval or one passing test, and that the team should be able to see its share of unattested bytes over time.

## 4. Architecture: three layers, ordered by trust

**Layer 1, provenance by construction.** Every agent harness already knows the exact bytes it writes. Claude Code exposes them in its transcript logs and in a hook that fires after each write tool. The layer records, per write, the file, the hunk, a hash of the normalised text, the producing model and session, and a signature from a key on the developer's machine. The record goes to an append-only ledger in the repository, `.nhw/attest.jsonl` (format in `SPEC.md`). At review time a verifier walks the diff: every changed line covered by a valid record is attested; the rest is reported. This layer proves machine authorship exactly and proves nothing about the remainder, which is the correct asymmetry. It requires the harness to cooperate, which every harness a team controls can be made to do.

**Layer 2, vendor watermarks.** For text the team did not produce inside a cooperating harness, the vendor's statistical watermark is the next best evidence. Where the team runs its own models, SynthID-Text lets it hold its own key and verify its own output today [10]. For Claude and Gemini output the key is the vendor's; this layer becomes usable the day a detection endpoint ships, and the ledger format leaves a slot for it. Watermarks are weaker than layer 1 because they need enough tokens to reach confidence (the Nature paper reports reliable detection at a few hundred tokens for its settings [2]) and because a determined rewrite removes them. They are stronger than anything below because a positive result is cryptographic, not stylistic.

**Layer 3, statistical triage.** Where neither record nor key exists, the only remaining signal is style. We use the inverse of an AI-tell detector: inside a document that is dense with machine patterns, the paragraph with none is the candidate insertion. Section 6 shows how weak this is. It stays in the design only to order a reviewer's attention, and it never produces a label on its own.

The ordering is the design. Most systems in this space start at layer 3 and hope. We start at layer 1, where the answer is exact, and treat everything else as a fallback that must announce its own uncertainty.

## 5. Proof of concept and results

All code is Python standard library. Nothing leaves the machine. The measurements below were taken on 4 September 2026 on the author's laptop.

### 5.1 Reconstructing provenance from harness logs

`nhw/attest.py` reads every Claude Code transcript under `~/.claude/projects`, extracts the `Write` and `Edit` tool calls, and indexes each produced line by a hash of its whitespace-normalised content, keyed by target path. It then attributes any file line by line: strong match (the agent wrote that line to that path), weak match (the agent wrote that line somewhere), or unattested. Lines shorter than twelve characters are ignored; a closing brace carries no authorship.

Index: 312 transcript files, 2,716 writes (704 `Write`, 2,012 `Edit`), 72,681 attested lines. The logs on this machine begin on 30 July 2026, so the index covers five weeks.

| Corpus | Files | Median attested | Line-weighted | 0–20 % | 20–50 % | 50–80 % | 80–100 % |
|---|---|---|---|---|---|---|---|
| Vault tools (`tools/*.py`) | 63 | **96 %** | 68 % | 22 | 2 | 3 | 36 |
| Vault wiki (`wiki/*.md`) | 285 | 5 % | 23 % | 178 | 19 | 16 | 72 |
| Vault raw notes (`raw/*.md`) | 100 | 0 % | 18 % | 73 | 0 | 2 | 25 |
| Agent config (`~/.claude/*.md`, hooks) | 5 | 100 % | 94 % | 0 | 1 | 0 | 4 |
| This PoC (`nhw/*.py`) | 3 | **9 %** | 9 % | 3 | 0 | 0 | 0 |

Three readings. First, where the agent wrote code inside the logged harness during the log window, attestation is near-complete: 36 of 63 tools sit above 80 %, with a median of 96 %. The remaining few per cent are lines later touched by hand or by a formatter, which is the signal the tool exists to find. Second, the distributions are bimodal, not smeared. Files are either mostly attested or barely attested; the 20–80 % middle holds 6 % of the wiki and 8 % of the tools. That is what one expects if authorship is decided per file by which channel produced it, and it means a threshold is easy to set. Third, the wiki and raw corpora are mostly unattested even though the same agent wrote most of them. Their pages predate the log window or were produced by other harnesses (a Telegram bot, a scheduled job, a different agent). Unattested means human *or untracked*, and on this machine untracked dominates.

The last row makes that point without argument. The proof of concept's own three source files were written by the agent in this session, through a shell heredoc rather than the logged write tool. The ledger saw nothing. Attestation: 9 %, all of it weak matches on generic import lines. Log forensics after the fact cannot close this gap; only a record emitted by every writing channel at write time can. That is why layer 1 in production is a hook and a signature, and the transcript reader is a demonstration.

### 5.2 Git authorship as a cross-check

`nhw/gitmode.py` runs `git blame` and marks a line machine-authored when its commit carries a `Co-Authored-By: Claude` trailer or a bot identity. On two wiki pages the agent wrote end to end, git reports 0 % machine authorship: an automatic backup job commits the working tree under the human's name every six hours. On a tool whose commits were made by the agent itself with trailers, git reports 83 % (551 of 667 lines). Git is therefore a usable second source only where the team's commit discipline already encodes authorship, and it inverts the truth where it does not. It cannot replace the ledger.

### 5.3 The statistical layer against ground truth

The transcripts also give labelled prose. What the developer typed or dictated to the agent is human; what the agent answered is machine. We took user turns of 40 to 300 words with no pasted structure (no headings, bold, lists or code fences) and assistant text blocks in the same length range, removed near-duplicates, and sampled 150 of each from 310 and 2,987 unique passages respectively. Each passage was scored by sloptrim 0.9.0, a local detector of 71 documented AI-writing patterns [15], and by a burstiness statistic (standard deviation of sentence length over its mean).

| Measure | Human p10 / p50 / p90 | Machine p10 / p50 / p90 |
|---|---|---|
| sloptrim AI-tell score (0–100) | 0 / 0 / 8 | 0 / 18 / 25 |
| Burstiness | 0.28 / 0.58 / 0.94 | 0.29 / 0.60 / 0.96 |

AUC, machine vs human, sloptrim score: **0.912**. AUC, burstiness: 0.483, a coin flip; the folk belief that people vary their sentence length more than models do does not survive contact with a modern model's chat output. At the detector's own threshold of 20, 99.3 % of human passages fall below it, which sounds like a fine human detector until one reads the other column: **60 % of machine passages also fall below it**. Six machine paragraphs in ten carry no tell the detector knows.

Caveats are real. One writer, one model family, chat-register prose, and a detector calibrated on published text rather than working notes. The numbers will move on other data. The shape will not: the human passages score zero because they are short and plain, and a majority of machine passages score zero for the same reason.

## 6. Base rates, or why layer 3 cannot be promoted

Suppose a team's artefacts are 5 % human-inserted by span, a generous figure for an agent-first team. Use the measured sensitivity (0.993) and false-positive rate (0.60) of the "no tell means human" rule.

    precision = 0.993 × 0.05 / (0.993 × 0.05 + 0.60 × 0.95) ≈ 0.08

Fewer than one flag in twelve is a person. At a 1 % human share the figure is under 2 %. A reviewer shown these flags will learn within a day to ignore them, and the one true insertion in the pile goes through with the rest. No threshold rescues this; lowering the false-positive rate to 0.10, far better than anything in the literature under paraphrase [8], still yields a precision of about 34 % at 5 % prevalence.

This is the same arithmetic that made classroom detectors harmful [3, 4], run in the other direction. The lesson transfers intact: a statistical detector of authorship is only acceptable where a false result costs nothing, and in our setting a false "human" costs a review and a false "machine" hides the thing we were looking for. Provenance has no base-rate problem because it does not estimate; it reads a record that was written at the time.

## 7. Ethics and the regulatory frame

The video that prompted this work treats the watermark as a threat and offers a laundering recipe [14]. The vault this project grew in had already filed watermark removal as something not to build, on the reasoning that disclosure is the point of the mark and a transparency law we are otherwise content to live under should not be defeated for convenience. NoHumanWrite is the mirror image. It never removes a mark. It never asserts that a person's work is machine-made, the failure mode with victims. It asserts, with a signature, that a machine's work is machine-made, and leaves the remainder unlabelled for a human to look at.

Article 50 obliges providers to mark machine output so that it can be detected [13]. The regime assumes a public that wants to know what the machine wrote in order to discount it. We add a second constituency that wants to know what the machine wrote in order to trust it, and to spend its scarce attention on the rest. The same marks serve both. A vendor detection endpoint, when it ships, would serve both. Until then, a cooperating harness and a signed ledger serve the second constituency completely, at zero cost to the first.

Two design rules follow. The ledger records a machine key, never a person's name; the reviewer sees "unattested", not "Arnaud". And the tool ships with no humaniser, no rewrite mode and no removal mode, so that it cannot be turned around and pointed at the constituency Article 50 protects.

## 8. From paper to product

The wedge is a pull-request check for teams that already write with agents. Install a GitHub App, add one hook to the harness, and each pull request shows the share of changed bytes that is machine-attested, highlights the unattested hunks, and applies a policy the team chose: comment, require a second approver, require a test that touches the file, or block. The ledger stays in the repository as plain JSON; only the numbers leave. The business plan, pricing and 30-day build sit in `business.md`; the ledger format in `SPEC.md`.

The honest test of the idea is not the AUC. It is whether the number on the pull request changes one review decision a week on a real team. Five design partners will tell us within a month.

## 9. Open questions

- Formatters and refactors rewrite attested lines without changing meaning. Hash at the token level, or re-attest after a formatter run the harness itself invoked?
- Agents that edit through shell commands, as ours did, need the hook at the file-system or git-index level rather than the tool level. Where is the right choke point?
- What token count does Anthropic's watermark need for confidence, and will a detection endpoint accept short code hunks at all? The Nature paper's numbers are for prose [2].
- Should an attested span that a human later *reviewed and approved* be marked differently from one nobody looked at? The ledger has room for a review record; the policy question is open.
- Multi-writer teams: does the distribution of unattested share across developers become a management signal, and should it be visible at all?

## References

1. J. Kirchenbauer, J. Geiping, Y. Wen, J. Katz, I. Miers, T. Goldstein. *A Watermark for Large Language Models.* arXiv:2301.10226, 2023.
2. S. Dathathri et al. *Scalable watermarking for identifying large language model outputs.* Nature, October 2024. doi:10.1038/s41586-024-08025-4.
3. V. S. Sadasivan, A. Kumar, S. Balasubramanian, W. Wang, S. Feizi. *Can AI-Generated Text be Reliably Detected?* arXiv:2303.11156, 2023.
4. W. Liang, M. Yuksekgonul, Y. Mao, E. Wu, J. Zou. *GPT detectors are biased against non-native English writers.* arXiv:2304.02819, 2023.
5. E. Mitchell, Y. Lee, A. Khazatsky, C. D. Manning, C. Finn. *DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature.* arXiv:2301.11305, 2023.
6. A. Hans et al. *Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text.* arXiv:2401.12070, 2024.
7. V. Verma, E. Fleisig, N. Tomlin, D. Klein. *Ghostbuster: Detecting Text Ghostwritten by Large Language Models.* arXiv:2305.15047, 2023.
8. L. Dugan et al. *RAID: A Shared Benchmark for Robust Evaluation of Machine-Generated Text Detectors.* arXiv:2405.07940, 2024.
9. OpenAI. *New AI classifier for indicating AI-written text.* 31 January 2023; withdrawn 20 July 2023 (update note on the same page).
10. Google DeepMind. *synthid-text* (generation and detection code, Apache-2.0). github.com/google-deepmind/synthid-text.
11. Coalition for Content Provenance and Authenticity. *C2PA Technical Specification 2.2: Content Credentials.* c2pa.org.
12. Anthropic Help Center. *How Claude marks AI-generated content.* Article 16266773, accessed 14 August 2026.
13. Regulation (EU) 2024/1689 (Artificial Intelligence Act), Article 50, transparency obligations, applicable from 2 August 2026.
14. Chase AI. *Fable 5.1 Watermarks EVERYTHING, Here's How To Remove It.* YouTube, video slePq-H-TMA, 10:14, September 2026.
15. sloptrim 0.9.0. Local detector of 71 documented AI-writing patterns, Python standard library, Apache-2.0.
