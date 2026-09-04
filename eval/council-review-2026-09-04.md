# Council — external voices (build) · 8 members

TASK: Review this draft research paper as a hostile senior reviewer before public release (arXiv cs.SE + public repo). Attack: (a) the core claim that inverting AI-text detection (find the human insertions) is a distinct, useful task; (b) the base-rate arithmetic; (c) the proof-of-concept methodology and whether the 96% / 9% / 8% numbers support the conclusions; (d) the three-layer architecture and the signed-ledger product; (e) ethics/regulatory framing (EU AI Act Art. 50, watermarks); (f) any factual or citation error. Give concrete fixes, not sentiment. Then a one-line verdict: publish as is / publish after fixes / do not publish.

PAPER FOLLOWS
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

## Round 1 — independent answers

### A. openai/gpt-5.6-luna-pro
## Hostile review

### Overall assessment

The paper contains a potentially useful engineering idea—recording write provenance at the time an agent modifies a repository—but it currently overstates the scientific novelty, mixes incompatible statistical units, treats an untrusted local log as authorship proof, and includes several claims that appear unverifiable or factually wrong. The empirical section is a single-user diary, not evidence for the general claims in the abstract.

The strongest defensible paper is not “we inverted AI detection.” It is:

> In agent-mediated repositories, write-time provenance can identify changes made through instrumented tools, while post-hoc stylistic inference cannot reliably recover authorship under realistic base rates.

That is narrower, less novel, and much more credible.

---

## (a) The core claim: is this a distinct and useful task?

### The “inversion” is not clearly a distinct research task

The paper defines a human insertion as “any span ... that was not produced by a logged machine write.” That is not human authorship. It is **absence of an attestation**. The following all become “human insertions” under the definition:

- a shell command run by an agent;
- a scheduled bot;
- a formatter;
- a compiler or code generator;
- a second, uninstrumented AI system;
- copied text from another repository;
- a human-pasted machine output;
- a file restored from backup;
- an agent write whose log was deleted or never received.

The paper later admits this (“unattested means human or untracked”), but the abstract, title, and product framing repeatedly slide back to “finding the human.” That is a serious semantic error.

The task is better described as one of:

- write provenance;
- attribution of changes to instrumented channels;
- localization of unattested changes;
- mixed-provenance artifact analysis;
- post-hoc change-origin reconstruction.

It is related to authorship attribution, data lineage, build provenance, software supply-chain attestations, audit logs, and intrusion detection. The paper must explain what is genuinely new relative to those areas. “Looking for human edits rather than AI edits” is a change in operational objective, not automatically a new scientific problem.

### Usefulness is plausible, but unsupported

The use case—finding changes that bypassed an agent/test/review workflow—could be useful. But the paper does not show that:

1. human edits are actually where incidents occur;
2. unattested edits are more incident-prone than attested edits;
3. highlighting an unattested line changes reviewer behavior beneficially;
4. requiring an additional approval reduces defects;
5. the proposed metric is preferable to ordinary branch protection, CODEOWNERS, required tests, or file-system auditing.

The claim that “the spans ... are where the incidents live” is anecdotal and should not appear as a general premise without incident data.

The paper also presents human editing as an “exception path” that “deserves a second look,” but many legitimate workflows involve human edits, including security review, emergency fixes, generated-file repair, and final legal or scientific editing. The product must distinguish “unattested” from “suspicious,” otherwise its rhetoric encourages automation bias against legitimate human work.

### Concrete fix

Replace the title and central definition with something like:

> **NoHumanWrite: write-channel provenance for agent-mediated repositories**

Define the primary observable as:

> `attested_by_instrumented_channel`, not `human_authored`.

Reserve “human-authored” for cases with independent evidence, such as an explicit human editor event. State explicitly that the system cannot infer human authorship from non-attestation.

Add a threat model and compare the proposal with Git hooks, OS audit logs, eBPF/file-system tracing, SLSA/in-toto attestations, IDE telemetry, and C2PA-style claims.

---

## (b) Base-rate arithmetic

### The arithmetic itself is correct, but the application is not

The calculation is:

\[
P(H\mid N)=
\frac{P(N\mid H)P(H)}
{P(N\mid H)P(H)+P(N\mid M)P(M)}
\]

Using:

- \(P(N\mid H)=0.993\);
- \(P(N\mid M)=0.60\);
- \(P(H)=0.05\);

gives approximately 0.080, so the stated 8% is arithmetically correct. At a 1% base rate, approximately 1.6% is also correct. Using a 10% false-positive rate gives approximately 34.3%, also correct.

However, the paper applies **passage-level rates** to a claimed **span-level prevalence**:

- the detector experiment uses passages of 40–300 words;
- the prevalence assumption is “5% human-inserted by span”;
- the proposed system operates on lines, hunks, or bytes.

Those are not interchangeable. A document may contain 5% human-authored lines while 50% of passages contain at least one human line. Conversely, a few long human insertions can dominate byte prevalence while affecting very few passages.

The calculation also assumes conditional independence and a stable score distribution between the balanced experiment and the target workflow. Neither is demonstrated.

### “No tell” is not a detector error in the way claimed

A score below threshold is not evidence that a machine passage has “no detectable tell” in an absolute sense. It means only that this detector, at this threshold, did not classify it as machine-like. The abstract should say “60% fell below the selected threshold,” not “60% carry no detectable tell.”

Also, the paper calls 0.993 “sensitivity” for identifying human text. That is acceptable if defined, but the ordinary convention would make the positive class “machine,” in which case the relevant quantity is specificity or the true-negative rate. The paper should define all rates explicitly and avoid rhetorical switching.

### The decision-theoretic conclusion is incomplete

A false “human” flag and a false “machine” flag do not necessarily have equal costs. The paper says the former causes review while the latter hides an insertion, but gives no cost model. A system should optimize expected review cost, missed-defect cost, privacy cost, and false suspicion—not merely precision.

### Concrete fix

Run and report separate calculations for:

- line-level prevalence;
- byte-level prevalence;
- hunk-level prevalence;
- document-level prevalence.

Use a synthetic mixed-authorship benchmark where human and machine spans are inserted at controlled proportions. Report precision, recall, false discovery rate, workload per true insertion, and confidence intervals at 0.1%, 1%, 5%, 10%, and 25% prevalence.

Include a confusion-matrix diagram and define whether “positive” means “human candidate,” “machine candidate,” or “unattested candidate.”

---

## (c) Proof-of-concept methodology and the 96% / 9% / 8% numbers

### The provenance experiment is descriptive, not a validation study

The 96% and 9% figures are observations from one developer’s private machine and one harness. They do not establish:

- precision of the line matcher;
- recall of the log extractor;
- robustness across repositories;
- robustness across agents;
- robustness across file types;
- correctness after renames, formatting, merges, rebases, or refactors;
- resistance to log loss or tampering.

The experiment has no independently labeled ground truth for most files. “The agent wrote most of them” is an assertion based largely on the same logs being evaluated.

The 9% figure is particularly weak evidence. The source files were deliberately written through an unlogged shell heredoc, so the result mostly demonstrates that a tool-level log misses a shell-level write. That is a useful failure case, but it is not evidence that the proposed production architecture works.

### Line matching is not authorship attribution

Hashing whitespace-normalized lines creates several problems:

- Generic lines such as imports, braces, comments, and boilerplate produce false matches.
- A human can copy an agent-generated line, making it appear agent-written.
- An agent can reproduce a human-written line, making it appear agent-written.
- Identical lines in different files create ambiguous provenance.
- Line-based matching fails under reformatting, moved blocks, renames, and small edits.
- Normalization rules can erase meaningful distinctions.
- The paper ignores lines shorter than twelve characters, then reports percentages that may exclude exactly the kinds of syntax-heavy lines common in code.
- “Weak match” across another path is not evidence that the agent wrote the current line.
- A valid match proves at most that similar bytes appeared in an agent output, not that the agent was the causal writer of the current bytes.

The phrase “attestation is near-complete” is therefore too strong. The system has shown near-complete **matching against a particular transcript index under a particular normalization rule**.

### The table and interpretation need checking

The claim that the middle contains “6% of the wiki” is inconsistent with the table as printed. The wiki has 19 files in the 20–50% bin and 16 in the 50–80% bin: 35/285, or approximately 12.3%, not 6%. For the tools, 5/63 is approximately 7.9%, so “8%” is reasonable.

The “bimodal” interpretation is also not established by the table. The distributions may reflect corpus age, file type, logging coverage, or directory selection rather than a property of authorship.

The claim that the remaining few percent in high-attestation files are “lines later touched by hand or by a formatter” is speculation unless the study records those events independently.

### The statistical experiment is underpowered and potentially leaky

The detector sample is described as 150 human and 150 machine passages, but the source pools are highly unequal: 310 human turns and 2,987 machine blocks. The paper does not specify:

- exact model and version;
- temperature and decoding parameters;
- language distribution;
- whether the same sessions contributed both training/calibration and test material;
- how near-duplicates were removed;
- whether user prompts and assistant responses were from the same topics;
- whether passage length distributions were matched;
- whether sloptrim was tuned on this sample;
- whether the reported AUC has a confidence interval;
- whether the threshold of 20 was selected before or after inspecting the data.

The table shows highly overlapping burstiness distributions, but that is merely a negative result on one statistic. The AUC of 0.912 for sloptrim is not evidence that “the inversion” is generally possible or impossible. It is a result for one unpublished detector, one writer, one model family, and a narrow chat register.

The 8% result is derived from a thresholded balanced passage experiment, not from a mixed document containing inserted human spans. It does not measure the proposed task.

### Concrete fix

At minimum:

1. Release the exact detector, commit hash, model versions, prompts, parameters, and preprocessing code.
2. Provide a held-out test set and bootstrap confidence intervals for AUC, TPR, FPR, and precision.
3. Include multiple human writers, multiple models, multiple domains, and mixed human/machine passages.
4. Evaluate at the actual deployment unit: changed line, hunk, or byte span.
5. Establish provenance ground truth by constructing controlled sessions in which every write channel is labeled.
6. Test shell writes, editor writes, formatters, generated files, renames, merges, copy/paste, and deliberate log deletion.
7. Report matcher precision and recall separately from the downstream “attested percentage.”
8. Correct the table arithmetic and explain denominators.
9. Remove the 96%, 9%, and 8% figures from the abstract unless they are explicitly labeled as single-machine case-study measurements.

The abstract should not say “provenance ... has no such ceiling.” Provenance has failure modes; it has a different error model.

---

## (d) Three-layer architecture and signed-ledger product

### Layer 1 does not prove authorship

A signature from a key on the developer’s machine proves that whoever controlled that key signed a statement. It does not prove:

- that an AI model generated the bytes;
- that the claimed model and session are truthful;
- that the process was not compromised;
- that a human did not invoke the agent or alter the output;
- that the log is complete;
- that a previous record was not omitted;
- that the signed content was actually written to the claimed path.

The correct claim is “the instrumented writer attested that it emitted these bytes.” That is useful, but materially weaker.

A local `.nhw/attest.jsonl` file is not append-only. A user with repository write access can edit, delete, reorder, or replace it. JSONL has no inherent tamper evidence. A hash of normalized text is not a complete content commitment unless the path, encoding, byte range, version, parent state, and canonicalization are also committed.

### The proposed ledger needs a real security design

The paper needs to specify:

- key generation, storage, rotation, revocation, and recovery;
- whether keys are per user, host, harness, repository, or session;
- how compromised keys are handled;
- canonical serialization;
- exact byte ranges and file versions;
- parent commit/tree hash;
- sequence numbers and hash chaining;
- replay and rollback detection;
- handling of renames and deletes;
- clock provenance;
- remote witnessing or transparency logging;
- offline operation and later reconciliation;
- how a verifier obtains the trusted public key;
- behavior when the ledger and repository disagree.

If the ledger is intended for security-sensitive review, it should be based on a known provenance framework or clearly state that it is an accountability log, not a tamper-proof record.

### The three layers are not strictly ordered by trust

Layer 2 watermarks are not necessarily “cryptographic” evidence. A keyed statistical watermark is a probabilistic signal, not a signature, identity binding, or integrity proof. A positive watermark detection does not establish which user, model instance, or tool produced the text, and may survive copying or appear in transformed text in non-obvious ways.

A cooperating harness’s signed write event may be more useful than a watermark, but it is not automatically more trustworthy if the harness, host, or key is compromised.

Layer 3 is also underspecified. The system cannot simply take the “inverse” of an AI detector and infer human insertions. It needs a calibrated anomaly-ranking model over a document with known or estimated provenance, with explicit abstention and no authorship label.

### The product creates dangerous incentives

A pull-request badge showing “machine-attested share” may become a proxy for developer performance, compliance, or trustworthiness. It can pressure developers to route work through the instrumented agent merely to improve the metric. It can also penalize emergency fixes, accessibility edits, security patches, and legitimate human review.

The paper should specify:

- no personnel ranking;
- no automatic rejection based solely on unattested content;
- retention and access controls;
- whether prompts and file paths contain secrets;
- whether ledger records are included in forks and public repositories;
- how contributors opt out;
- how contractors and multi-user teams are represented;
- how false or incomplete attestations are appealed.

“Only the numbers leave” is not credible without an information-flow analysis. Even percentages, paths, timestamps, session identifiers, and hashes can leak repository activity or enable correlation.

### Concrete fix

Rename “signed authorship ledger” to “signed write-attestation ledger.” Define the security claim precisely. Use content-addressed records containing at least:

- repository/tree parent;
- path and operation;
- exact byte range or resulting blob hash;
- tool and process identity;
- session identifier;
- monotonic sequence;
- timestamp with uncertainty;
- signature;
- previous-record hash.

Add a remote append-only witness or transparency service if tamper evidence is required. Otherwise explicitly state that the ledger protects against accidental loss and supports audit, but not against a malicious repository administrator or compromised host.

---

## (e) Ethics and regulatory framing

### Article 50 is overstated

Article 50 does not simply impose a universal “watermark all machine text” requirement. The relevant obligations concern machine-readable marking of certain AI-generated or manipulated outputs and disclosure in specified contexts, with technical-feasibility and scope conditions. The paper must quote the relevant paragraphs and distinguish:

- provider obligations;
- deployer obligations;
- output marking;
- public disclosure;
- deepfake-specific rules;
- exemptions and implementation guidance;
- the date on which each provision applies.

“Article 50 ... so that it can be detected” is too broad. The provision does not imply that every vendor must expose a public detection endpoint, nor that statistical watermarking is the mandated implementation.

The claim that Anthropic adopted a worldwide watermark “to satisfy Article 50” is especially problematic. That requires a primary Anthropic announcement and legal basis, not a help-center citation. It also appears temporally unverifiable in this draft.

### Watermark claims need primary-source verification

The following assertions require correction or removal unless the authors can provide archived primary sources:

- Anthropic watermarking all text worldwide from 2 August 2026;
- Anthropic applying the scheme across every product surface;
- a non-public detection key and promised detection documentation;
- Anthropic attaching C2PA manifests to media from its sandbox;
- “Anthropic’s Fable 5.1” and the cited laundering video.

These may be future-dated, fabricated, misnamed, or based on a source that is not independently verifiable. A public arXiv paper cannot rely on future webpages without archived copies, access dates, and quotations.

### The ethics section understates privacy and labor risks

The system can affect:

- employee monitoring;
- attribution disputes;
- disciplinary decisions;
- whistleblowing and emergency changes;
- discrimination against developers who cannot or should not use an agent;
- leakage of proprietary prompts and file metadata;
- surveillance of writing behavior;
- false suspicion caused by missing logs.

The assertion that the tool “never asserts that a person’s work is machine-made” is not enough. A UI that highlights a person’s edit as “unattested” may produce the same practical inference. The product must prohibit using the signal for individual evaluation and require human review.

### Watermarks do not establish trust

The paper says watermarks let a team “trust” machine output. That is an unsafe framing. A watermark can indicate that output likely came from a model under a particular key. It says nothing about correctness, security, licensing, prompt integrity, data provenance, or review quality. The paper should avoid equating origin evidence with trustworthiness.

### Concrete fix

Replace the regulatory section with a narrow legal analysis:

- quote Article 50;
- cite the European Commission’s implementation guidance;
- identify which actor has each obligation;
- state that write attestations are complementary to, not a substitute for, legally required marking;
- remove claims about vendor compliance unless supported by primary evidence;
- add GDPR/employment/privacy analysis;
- prohibit use for worker ranking or disciplinary action;
- state retention, deletion, access, and appeal policies.

---

## (f) Factual, citation, and reproducibility issues

### Likely or apparent factual problems

1. **Anthropic “worldwide text watermark.”** This is a major claim and needs an authoritative, archived source. The cited Help Center article is insufficient unless it actually states every part of the claim.
2. **“Fable 5.1.”** The product and video citation need verification. The date is after the paper’s stated publication date context and may not be independently accessible.
3. **SynthID-Text.** Verify the exact Nature title, author list, publication date, DOI, technical mechanism, open-source scope, and whether the released repository includes both generation and detection code. Do not call detection “cryptographic.”
4. **C2PA and source code.** “There is no text profile” and “nothing comparable exists for source code at line level” require a scoped literature and standards review. C2PA is a general provenance framework, not necessarily restricted to media.
5. **Claude Code hooks and transcripts.** Product behavior changes. Pin the tested version and cite official documentation. Do not claim that every write is exposed or that transcript logs are complete without testing this.
6. **RAID and paraphrase.** The cited benchmark should be checked to ensure it supports the exact statement “degrade sharply under paraphrase and domain shift,” rather than a narrower result.
7. **OpenAI withdrawal date.** Verify the exact withdrawal notice and wording.
8. **`sloptrim`.** A local package with no stable public release, paper, dataset, or documented threshold is not an adequate scientific instrument. “71 documented patterns” needs a public specification.
9. **Future-dated references.** The arXiv and repository release must not cite pages or videos that readers cannot retrieve. Archive them or remove them.

### Reproducibility and data release

The code and data currently point to `~/nohumanwrite`, which is not a public artifact. The logs likely contain:

- private source code;
- prompts;
- credentials or paths;
- personal communications;
- proprietary project names;
- timestamps and behavioral information.

The authors cannot promise “code and data” release without a redaction and consent plan. Release a synthetic or redacted benchmark, exact extraction code, schema, hashes of withheld files, and a reproducibility script. Explain what cannot be released.

---

## Required revision plan

Before public release, I would require:

1. Reframe the contribution as write-channel provenance, not human-authorship detection.
2. Change every “human insertion” claim to “unattested or non-instrumented change” unless independently labeled.
3. Correct the passage/span/line base-rate mismatch.
4. Rebuild the evaluation around controlled mixed-provenance artifacts.
5. Report confidence intervals and matcher precision/recall.
6. Test all write channels, especially shell, editor, formatter, generated files, and file moves.
7. Define the ledger threat model and stop calling a local JSONL file append-only.
8. Distinguish signatures, provenance attestations, and statistical watermarks.
9. Verify or remove the Anthropic, Fable, SynthID, C2PA, and Article 50 claims.
10. Add privacy, employment, security, and misuse safeguards.
11. Release a public, reproducible artifact or clearly label the work a non-reproducible case study.
12. Remove unsupported generalizations from the abstract and conclusion.

## Verdict

**Publish after major fixes; not publishable as is.**

### B. google/gemini-3.1-pro-preview
Here is the review. 

### (a) The Core Claim & Task Inversion
**Critique:** Your core premise—that human insertions are where the incidents live—is an unproven sociological leap. Humans often edit AI code precisely because the AI hallucinated an API or missed edge cases. By framing human edits as "exceptions" that require extra friction (extra approvals/tests), you introduce a catastrophic perverse incentive: developers will prompt the agent to make the manual fix (which is slower and risks agentic drift) just to keep their "unattested" score low and bypass the PR block. 
**Fix:** Drop the "human edits = bugs" rhetoric. Reframe the task strictly as *provenance tracking for auditability*. Acknowledge the metric-gaming failure mode and specify that the tool is for routing review attention, not penalizing human keystrokes.

### (b) Base-Rate Arithmetic
**Critique:** Your math (yielding ~8% precision at 5% prevalence) is perfectly correct, but your architectural conclusion is logically incoherent. You mathematically prove that Layer 3 (statistical triage) will generate 11 false positives for every 1 true positive, explicitly state that "a reviewer shown these flags will learn within a day to ignore them," and yet you *keep Layer 3 in the architecture* to "order a reviewer's attention." You cannot order attention with noise. 
**Fix:** Delete Layer 3 entirely. If the math proves it fails in your specific operational environment, shipping it is engineering malpractice. 

### (c) PoC Methodology & The 96% / 9% / 8% Numbers
**Critique:** The PoC methodology is incredibly brittle. Hashing whitespace-normalized lines means any trivial, non-semantic human edit (e.g., renaming a local variable, fixing a typo in a comment) or an auto-formatter run invalidates the line. Furthermore, your 9% attestation result on shell heredocs is not an "instructive result" about unlogged channels; it is a fatal indictment of your chosen integration point. If the ledger misses code written via shell, it will miss code written via LSP integrations, curl, or copy-paste from web UIs. 
**Fix:** Move the attestation hook from the *agent transcript* layer to the *filesystem/IDE* layer (e.g., an LSP wrapper or file-watcher that correlates clipboard/buffer changes with API responses). Change the matching algorithm from exact line-hashing to AST-level diffing or Levenshtein distance to survive formatters.

### (d) Three-Layer Architecture & Signed Ledger
**Critique:** Layer 1 is security theater. You state the ledger is signed by "a key on the developer's machine." If the developer controls the key and the `.nhw/attest.jsonl` file is just checked into the repo, a lazy or malicious developer can simply script a bypass to append fake signatures for their own handwritten code to pass the PR check. It provides zero cryptographic guarantee against the actual author. 
**Fix:** The signature must come from the LLM provider's API (e.g., Anthropic signing the hash of the output payload) or a Trusted Execution Environment, not a local dev key. The verifier in CI must check the *provider's* public key, not the developer's.

### (e) Ethics, Regulatory Framing, and Watermarks
**Critique:** Your reliance on Layer 2 (vendor watermarks like SynthID-Text) for source code ignores fundamental information theory. Code has strictly lower entropy than prose; tournament sampling or green-listing on syntax-heavy text either destroys the code's compilability or fails to achieve statistical significance on short hunks. You ask this in "Open Questions," but it invalidates Layer 2 for your primary use case (code). Furthermore, tying this to EU AI Act Art. 50 is a distraction; Art. 50 is about preventing consumer deception, not internal enterprise code quality.
**Fix:** Explicitly state that Layer 2 is for prose/documentation only and fails on code. Cut the grandstanding about Art. 50 and replace it with a discussion on enterprise compliance frameworks (e.g., SOC2, ISO 27001) which actually mandate this kind of change-management provenance.

### (f) Factual and Citation Errors
**Critique:** 
1. You cite SynthID-Text (Citation 2) but fail to note that DeepMind explicitly warns against its use on factual or highly structured text (like code) due to the entropy constraints mentioned above. 
2. You claim Git "inverts the truth" if commit discipline is poor (Section 5.2), but Git's `commit --author` and `Co-Authored-By` trailers are exactly what the industry currently uses for this. Dismissing it entirely because of a cron-job edge case is weak.
**Fix:** Add the entropy limitation of SynthID to Section 4. Acknowledge that Git trailers, enforced via pre-commit hooks, are a simpler, zero-dependency alternative to your JSONL ledger, even if they lack cryptographic rigor.

***

**Verdict:** Publish after fixes.

### C. qwen/qwen3.8-max
## Review: hostile senior pass before arXiv / public repo

The paper has one genuinely interesting SE idea: in agent-first development, the useful question is not “is this machine-written?” but “which parts are unattested / unlogged / not produced through the reviewed pipeline?” That is a real provenance problem. But the draft currently oversells it as a new detection task, supports it with an n=1 demo, mixes three unrelated numbers into a headline, and makes legal/watermark claims that are too strong and under-cited. As written, it reads like a product pitch plus a feasibility anecdote, not a defensible cs.SE paper.

Below are concrete attacks and fixes.

---

## (a) Core claim: “inverting AI-text detection” is not the task you actually have

### Problem

The paper claims the inverted task is “locating human insertions inside machine-written material.” But the method does not locate human writing. It locates **absence of a logged machine write**. Those are not the same.

Your own definition says:

> a human insertion as any span in an artefact that was not produced by a logged machine write.

That is a negative provenance label, not a human-authorship label. “Unattested” can mean:

- human typed it;
- another agent wrote it;
- an unlogged shell command wrote it;
- a formatter rewrote it;
- a CI script generated it;
- it predates the logging window;
- it was copied from Stack Overflow / docs / another repo;
- it was produced by a different harness;
- it was merged/rebased/cherry-picked in a way that broke line attribution;
- the logger missed it due to a bug;
- the line is too short and was ignored by your matcher.

So the core task as defined is not “find the human.” It is “find unattested spans.” That may still be useful, but the current framing is conceptually wrong and rhetorically misleading.

### Why “distinct and useful” is not yet shown

The paper asserts:

> in our experience they are where the incidents live.

That is the most important usefulness claim in the paper, and it is unsupported. No incident data, no user study, no citation, no corpus of postmortems, no interview evidence. For arXiv cs.SE, “trust me” is not enough.

Also, the “inversion” is not really an inversion of AI-text detection. Detection is statistical classification. What you are proposing is closer to:

- software provenance;
- supply-chain attestation;
- change-control auditing;
- forensic reconstruction;
- review triage.

That is a stronger framing. Use it.

### Concrete fixes

1. **Rename the task** unless you collect human ground truth:
   - “unattested span detection”
   - “unlogged edit surfacing”
   - “provenance gap detection”
   - “machine-attestation coverage”

   Do not call it “human insertion detection” unless you can show the unattested spans are actually human-written.

2. Add a formal task definition:
   - Input: artifact at time `t`, logs, watermark evidence, git metadata.
   - Output: spans labeled `attested-machine`, `unattested`, optionally `weak-match`, not `human` by default.
   - Unit: line, hunk, byte, AST node? Pick one and define it.

3. Add a threat/use-case model:
   - Who benefits?
   - Who is harmed by false positives?
   - Is the human adversarial, careless, or cooperative?
   - Is the agent trusted?
   - Is the developer machine trusted?
   - Is the repo writable by untrusted parties?

4. Support usefulness with at least one of:
   - examples from real incidents;
   - citations to SE literature on unreviewed changes, hotfix risk, code review bypass, supply-chain provenance;
   - a small developer survey;
   - a retrospective study;
   - a controlled injection study showing unattested edits cause review misses.

5. Add related work on provenance, not just AI detection:
   - W3C PROV;
   - in-toto;
   - SLSA;
   - Sigstore;
   - commit signing / commit trailers;
   - software bill of materials;
   - reproducible builds;
   - C2PA, but also its limits for text/code.

---

## (b) Base-rate arithmetic: formula is right, evidence is weak, conclusion is too strong

### What is correct

The precision calculation is arithmetically fine:

\[
\text{precision} = \frac{0.993 \times 0.05}{0.993 \times 0.05 + 0.60 \times 0.95} \approx 0.08
\]

At 5% human prevalence, if the “no tell means human” rule has 99.3% sensitivity for human and 60% false-positive rate on machine text, precision is indeed low.

The broader point is also correct: low-prevalence classification can be useless even with high AUC.

### What is not supported

The problem is not the formula. The problem is the inputs and the strength of the conclusion.

#### 1. The estimates come from 150 + 150 passages from one person

You have:

- one developer;
- one machine;
- one model family;
- one chat register;
- one local detector;
- 150 human passages;
- 150 machine passages.

That is not enough to state broad impossibility claims.

With 149/150 positives, the sensitivity is not exactly 0.993. A rough 95% Wilson interval is about `[0.96, 0.999]`. With 90/150 false positives, the FPR 0.60 has a 95% interval roughly `[0.52, 0.68]`. Propagating those into the 5% prevalence precision gives something like 7–9%, not a precise 8%. Report uncertainty.

#### 2. “Realistic 5% human share” is invented

Where does 5% come from? Is it by span, line, byte, hunk, PR, token? In agent-first teams it could be 0.1%, 5%, 30%, or higher depending on workflow. You need either:

- an empirical measurement;
- a sensitivity sweep;
- or explicit language: “we assume 5% for illustration.”

Do not call it realistic without evidence.

#### 3. One threshold does not prove “no threshold rescues this”

You evaluate at the detector’s threshold of 20. But the claim “No threshold rescues this” requires a full ROC/PR analysis.

The paper gives:

- human p10/p50/p90: `0 / 0 / 8`
- machine p10/p50/p90: `0 / 18 / 25`

That suggests many ties at zero and a discrete, coarse score. AUC is not enough. You need threshold-by-threshold precision/recall.

For example, at 5% prevalence, to get 50% precision with TPR = 0.8, you need roughly:

\[
FPR \le \frac{TPR \times 0.05}{0.95} \approx 0.042
\]

If your detector cannot achieve FPR ~0.04 at useful recall, say that with a PR curve. Do not assert it from one threshold.

#### 4. AUC is the wrong headline for low prevalence

AUC can be 0.91 and still be operationally useless at 5% prevalence. Use:

- precision-recall curve;
- PR-AUC;
- precision at fixed recall;
- recall at fixed precision;
- expected utility/cost analysis.

#### 5. The cost model is missing

You say:

> a false “human” costs a review and a false “machine” hides the thing we were looking for.

Then quantify that. If a false “human” flag costs 30 seconds of reviewer attention, low precision may still be acceptable as a triage signal. If it blocks PRs or assigns blame, low precision is unacceptable. The paper needs an explicit cost model.

### Concrete fixes

1. Report full confusion matrices for all thresholds, not one threshold.
2. Report Wilson or bootstrap confidence intervals for sensitivity, specificity, precision.
3. Replace “realistic 5%” with either:
   - measured prevalence; or
   - a sweep over 0.1%, 1%, 5%, 10%, 20%, 50%.
4. Add PR curves and PR-AUC. Do not rely on ROC AUC.
5. State the minimum FPR needed for useful precision at plausible prevalence.
6. Separate “this detector is bad for this task” from “no statistical method can ever work.” The latter is too strong.
7. If you keep the base-rate section, rewrite the conclusion as:

   > Under the measured error rates of this detector and assumed low prevalence, statistical triage has low precision and should not be used as a primary label.

   Not:

   > No threshold rescues this.

---

## (c) Proof-of-concept methodology: the 96% / 9% / 8% numbers do not support the paper’s conclusions

This is the weakest part. The three numbers are not comparable and do not form a coherent empirical result.

### The numbers

- **96%**: median file-level attestation on `tools/*.py`.
- **9%**: attestation on the PoC’s own source because it was written through an unlogged shell channel.
- **8%**: precision of a statistical “no tell means human” rule under a 5% prevalence assumption.

These are three different things:

1. coverage of a log-based attestation tool on one corpus;
2. a single failure case demonstrating an unlogged channel;
3. a simulated precision calculation for a different method.

They should not be presented as a chain of evidence.

### 96% is misleading as written

The table says:

- Vault tools: median attested **96%**, line-weighted **68%**.

That is a big gap. If the product cares about changed bytes in PRs, line-weighted or byte-weighted coverage matters more than median per-file coverage.

Also:

- Is “attested” strong match only or strong + weak?
- Are weak matches counted as attested?
- Are generic import lines causing weak matches?
- Are boilerplate lines causing false attribution?
- Are lines under 12 characters ignored? If so, how many security-relevant edits are short?
- Does normalization collapse meaningful differences?
- Does the matcher handle moved code, renamed files, refactors, formatter runs?

Without this, “96%” is not a precision or recall claim. It is coverage under unspecified matching rules.

### 0% in raw notes is not evidence of human writing

The paper says raw notes are 0% attested. But then it admits:

> Unattested means human *or untracked*, and on this machine untracked dominates.

Exactly. Therefore you cannot use raw notes as a human negative control. They are an untracked corpus.

Same for wiki: 5% median attested does not mean 95% human. It means 95% not covered by the selected logs.

### 9% on the PoC source is an anecdote, not a result

The PoC’s own source being 9% attested is a useful demonstration that unlogged shell writes escape tool-level logging. But it is three files, one session, one failure mode. It supports:

> Tool-level hooks miss some channels.

It does not support:

> This gap defines the product.

For that, you need a broader study of unlogged channels.

### There is no ground truth for “human insertion”

The PoC never measures:

- precision of `unattested` for actual human edits;
- recall of actual human edits;
- false attestation rate;
- false unattested rate;
- effect of formatters;
- effect of refactors;
- effect of copy/paste;
- effect of multi-agent workflows.

You need a labeled dataset.

### Concrete fixes

1. Stop calling the corpus “ground truth” unless the ground truth is human vs machine at the artifact span level. The chat-turn corpus is only ground truth for chat passages, not for file edits.

2. Report attestation metrics properly:
   - strong-match precision;
   - strong-match recall;
   - weak-match false-positive rate;
   - line-weighted and byte-weighted coverage;
   - ignored-line rate;
   - formatter/refactor breakage rate.

3. Build a small labeled benchmark:
   - take agent-written files;
   - insert known human edits;
   - insert known unlogged agent edits;
   - run formatter/refactor;
   - measure whether the system finds them.

4. Report at least:
   - number of files;
   - number of lines;
   - number of changed hunks;
   - number of true human edits;
   - number of false unattested flags;
   - number of false attested lines.

5. Use multiple developers and multiple repos. One developer, one machine, five weeks is a demo, not a study.

6. Compare against baselines:
   - `git blame`;
   - commit author/committer;
   - `Co-Authored-By` trailers;
   - file mtime;
   - editor swap files / local history;
   - IDE local history if available;
   - filesystem watchers.

7. If you cannot collect ground truth before public release, downgrade the paper to a position/demo paper. Remove causal claims and label the PoC as illustrative.

8. Do not put raw transcripts in the public repo unless they are thoroughly sanitized. Claude Code transcripts may contain secrets, PII, private paths, credentials, API keys, customer names, etc. Publish code plus synthetic reproducers, not raw logs.

---

## (d) Three-layer architecture and signed-ledger product: promising, but under-specified and over-trusted

The layered design is the strongest part conceptually. But the paper treats trust too casually.

### Layer 1: “provenance by construction”

You write:

> This layer proves machine authorship exactly and proves nothing about the remainder, which is the correct asymmetry.

This is too strong. It does not “prove machine authorship exactly.” It proves that a logging harness recorded a write event. That is different.

Failure modes:

- a human can use the agent’s logged write tool to insert arbitrary text;
- a compromised harness can sign anything;
- a malicious developer can fabricate logs if keys are local and untrusted;
- a formatter can rewrite lines after attestation;
- a shell command can bypass the hook;
- a file can be modified after the write event;
- line hashes can collide with boilerplate;
- normalization can hide semantic changes;
- repo history can be rewritten;
- the ledger can be modified in the same PR if not protected.

The asymmetry is right, but the trust claim is wrong.

### Layer 2: vendor watermarks

You say:

> they are stronger than anything below because a positive result is cryptographic, not stylistic.

This is not correct for statistical text watermarks. A watermark detection result is usually statistical, not cryptographic. It can have false positives and false negatives. It depends on token count, generation settings, paraphrase, editing, and detector access.

Cryptographic provenance would be a signature over bytes or a verifiable transcript. A watermark is a probabilistic mark.

Also:

- code may be too short;
- code tokenization may differ from prose;
- deterministic code generation may leave little room for watermark bias;
- refactors may destroy the mark;
- vendor detection endpoints may not exist;
- vendor keys may not be accessible;
- legal/terms-of-service constraints may apply.

### Layer 3: statistical triage

This is correctly weakened in the paper, but it should be demoted further. It should not be part of the product story except as an optional, clearly probabilistic reviewer hint.

### Signed ledger

The ledger needs a real specification.

At minimum, define:

- record schema;
- signature format;
- key model;
- key rotation;
- revocation;
- timestamp source;
- hash algorithm;
- normalization rules;
- handling of renames;
- handling of merges/rebases;
- handling of formatters;
- weak vs strong matches;
- how records are anchored to git commits;
- how to prevent a PR from adding fake attestation records;
- how to verify records when files move;
- what happens when a line is partially machine-written and partially human-edited;
- what metadata is stored and what is redacted.

“Append-only ledger in the repository” is not append-only if someone can rewrite history or edit the ledger in a PR. You need one of:

- signed git notes;
- transparency log;
- Merkle hash chain;
- remote witness;
- CI-enforced verification;
- protected branch policy;
- external timestamp authority;
- or a clear statement that the repo-local ledger is only a convenience format, not a security boundary.

### Product claims

The GitHub App / PR check idea is plausible, but the paper gives no evidence that it changes review behavior. The line:

> Five design partners will tell us within a month.

is not a result. Remove it or move it to future work.

### Failure modes I would worry about

1. **False attestation through boilerplate**  
   Common lines like `import os`, `return None`, `}` or test scaffolding get weakly matched and counted as machine-written.

2. **False unattested due to formatters**  
   Black, Prettier, gofmt, ESLint autofix, or IDE formatting rewrites attested lines and creates noisy unattested hunks.

3. **Alert fatigue**  
   If every unlogged edit is highlighted, reviewers ignore the signal.

4. **Management misuse**  
   “Unattested share per developer” becomes a surveillance metric. This is a serious ethics problem.

5. **Secret leakage**  
   Logs, prompts, hashes, and transcripts may contain credentials or PII.

6. **Bypass by design**  
   A human can ask the agent to write their exact text through the logged channel. The ledger says machine, but the content is human-supplied.

7. **Malicious attestation**  
   If the signing key lives on the developer machine and there is no remote witness, a malicious insider can fabricate attestation.

8. **Broken assumptions in code**  
   Watermarks trained/provisioned for prose may not work on 5-line code hunks.

### Concrete fixes

1. Replace “proves machine authorship exactly” with:

   > Layer 1 provides verifiable evidence that a cooperating harness wrote specific bytes, subject to the trustworthiness of the harness, key, and log storage.

2. Replace “positive result is cryptographic” for watermarks with:

   > A watermark positive is statistical vendor evidence, not a cryptographic proof.

3. Add a threat model section before the architecture.

4. Specify the ledger format in the paper or appendix, not only in `SPEC.md`.

5. Explain how the ledger is protected from tampering in a PR.

6. Explain how formatter/refactor changes are re-attested or tolerated.

7. Make Layer 3 optional and non-blocking.

8. Remove business-plan language from the main paper. `business.md` does not belong in a research contribution unless the paper is explicitly a startup/position piece.

---

## (e) Ethics/regulatory framing: needs precision, caveats, and less legal overconfidence

### EU AI Act Article 50

The current wording is too broad:

> Article 50 obliges providers to mark machine output so that it can be detected.

This needs to be narrowed and cited exactly. Article 50 has scope, exceptions, and different obligations for different actors. In particular:

- Does it apply to all text generation?
- Does it apply to code generation?
- Does the “assistive function / standard editing” exception apply?
- Does it apply to providers only, or also deployers?
- Does it require public detection endpoints?
- Does it require worldwide marking, or only EU-market compliance?
- When exactly do the obligations apply?

You need to cite the official text and avoid paraphrase that expands the scope.

### Anthropic watermark claims

Claims like:

> Anthropic adopted a scheme of this family for models released on or after 2 August 2026, applying it worldwide and across every product surface, with no opt-out, to satisfy Article 50.

are very strong. A help-center article may not be enough. You need:

- exact Anthropic documentation;
- access date;
- quoted language;
- distinction between what is legally required and what is vendor policy;
- distinction between what is public and what is inferred.

If Anthropic has not published detection details, say so clearly and do not build the architecture as if detection endpoints are imminent.

### Watermarks and laundering video

Using a YouTube video as motivation is fine if properly cited, but it should not support factual claims about watermark robustness, vendor policy, or legal compliance. Also, do not include a “how to launder” recipe or operational details. If the video contains removal instructions, cite it only as evidence of community attitude, not as a technical authority.

### Ethics of “finding the human”

The paper says:

> The ledger records a machine key, never a person's name; the reviewer sees “unattested”, not “Arnaud”.

This is a good design intent, but it may be naive. In a repository, unattested hunks can often be attributed by:

- commit author;
- branch name;
- PR author;
- timestamp;
- file ownership;
- team knowledge.

So the tool may still enable individual blame, even if the ledger does not store a name.

The paper also needs to address:

- worker surveillance;
- performance-review misuse;
- chilling effects on human editing;
- false blame from unlogged machine writes;
- union/works-council constraints in the EU;
- GDPR if logs contain personal data;
- retention limits;
- consent for telemetry;
- secret scanning;
- right to appeal an “unattested” flag.

### Concrete fixes

1. Add a legal disclaimer:

   > This is not legal advice; the applicability of Article 50 depends on system type, role, jurisdiction, and implementation.

2. Cite the exact Article 50 paragraph(s), including exceptions.

3. Remove or qualify “worldwide” and “no opt-out” unless directly supported by primary documentation.

4. Do not say Article 50 assumes the public wants to “discount” machine output. That is an interpretation, not a statutory fact.

5. Add an ethics subsection on labor surveillance and management misuse.

6. Add explicit safeguards:
   - no individual dashboard by default;
   - aggregate metrics only;
   - human review before adverse action;
   - no automatic firing/blocking based solely on unattested share;
   - retention limits;
   - redaction of secrets;
   - opt-in telemetry.

7. State clearly that the tool must not be used to evade watermark disclosure. But also acknowledge that any provenance tool can be misused to game review.

---

## (f) Factual and citation errors / risky citations

Fix these before public release.

### 1. DetectGPT citation

You cite DetectGPT as `arXiv:2301.11305`. That appears wrong. DetectGPT is commonly `arXiv:2201.11629`, originally 2022. Fix the arXiv ID and date.

### 2. Kirchenbauer et al.

Add venue and full author list if possible. The watermark paper was associated with ICML 2023. The current citation is minimal.

### 3. SynthID-Text / Nature citation

Verify:

- full author list;
- exact title;
- publication date;
- DOI;
- whether detection code is actually open source;
- what the Nature paper actually claims about token counts and detection reliability.

If the detection code is not fully public or only partially usable, correct:

> the detector and the generation-side code are open source.

### 4. OpenAI classifier

Cite the actual OpenAI page, access date, and withdrawal note. “Withdrawn for low accuracy” should be tied to OpenAI’s own wording or a reliable source.

### 5. EU AI Act

Cite the Official Journal properly:

- Regulation (EU) 2024/1689;
- Article 50;
- relevant paragraph/subparagraph;
- applicability date;
- exceptions.

Do not rely on secondary summaries.

### 6. Anthropic Help Center

A help-center article is weak for technical claims. If you use it:

- include URL;
- access date;
- exact statement;
- version/date if available.

If the article does not say “worldwide, every product surface, no opt-out, Article 50,” remove those claims.

### 7. C2PA

Verify the spec version. If you cite C2PA 2.2, make sure that was current at access date. Also state explicitly whether C2PA has a text profile or not. “There is no text profile” needs a citation or careful wording: “as of access date, we found no mature C2PA text profile for line-level source code.”

### 8. sloptrim

`sloptrim 0.9.0` is under-cited. Provide:

- repository URL;
- commit hash;
- release date;
- author;
- license;
- documentation of the 71 patterns;
- validation evidence;
- conflict-of-interest statement if it is your own tool.

If it is not public or validated, do not use it as the main detector. Use a public detector or validate sloptrim against known benchmarks.

### 9. YouTube citation

Add URL and access date. Do not use it as evidence for technical claims. It can be motivation only.

### 10. “Fable 5.1”

Verify the model/product name. If this is not a public Anthropic model name, remove it.

### 11. RAID title

Check exact title. It may be “RAID: A Shared Benchmark for Robust Evaluation of Machine-Generated Text Detection” or similar. Verify.

### 12. Liang et al.

Add venue if available and quote the exact statistic. “Above 60%” should match the paper’s reported number and population.

### 13. “Nature paper reports reliable detection at a few hundred tokens”

Cite the exact figure/table/settings. “A few hundred tokens” is too vague.

### 14. “Anthropic adopted SynthID family”

If this is inference, remove it. If it is documented, cite the document.

---

## Minimum acceptable rewrite for public release

If you want to put this on arXiv soon, the paper should be reframed as a **position/feasibility paper**, not an empirical validation.

### Abstract should say something like:

> We propose NoHumanWrite, a provenance-first approach to surfacing unattested edits in agent-assisted software development. Instead of asking whether a text is machine-written, we ask which spans are covered by machine-write provenance. A single-machine feasibility study using Claude Code logs shows that harness-level logging can attest many agent-written lines, but unlogged channels such as shell writes escape attestation. A preliminary statistical triage layer has low precision under plausible low base rates. We outline a signed ledger design and discuss limitations, including trust boundaries, watermark applicability, and EU AI Act transparency obligations.

That is defensible.

The current abstract is not.

### Claims you can probably support now

- Harness logs can provide line-level attestation for some agent-written files on one machine.
- Unlogged channels can escape tool-level attestation.
- Git blame/commit trailers are insufficient when commit identity does not reflect authorship.
- A simple statistical detector can have low precision for identifying human insertions under low prevalence.
- Provenance avoids some statistical base-rate problems but introduces coverage and trust problems.

### Claims you should remove or heavily qualify

- “finding the human in machine-written work” unless ground-truthed.
- “provenance recorded at the moment of writing has no such ceiling.”
- “proves machine authorship exactly.”
- “positive result is cryptographic” for watermarks.
- “the best local detector” unless you tested multiple detectors.
- “realistic 5% human share” without evidence.
- “the gap defines the product.”
- “the transparency regime was missing” as a legal/policy fact.
- any implication that the 96/9/8 numbers validate a product.

---

## Required concrete changes before repo release

1. Publish a repo at a fixed commit, not `~/nohumanwrite`.
2. Include a `README` with exact environment, versions, and commands.
3. Do not publish raw Claude Code transcripts.
4. Publish synthetic data or sanitized examples only.
5. Add a `SPEC.md` summary in the paper appendix.
6. Add a threat model.
7. Add limitations and threats to validity.
8. Add confidence intervals.
9. Add threshold sweep / PR curve.
10. Add at least one controlled injection experiment.
11. Fix citations.
12. Rewrite legal section with exact Article 50 language.
13. Remove business-plan claims from the main paper.
14. Rename “human insertion” to “unattested span” unless human ground truth is provided.

---

## Bottom line

The paper’s best contribution is not “we can find human insertions.” It is:

> In agent-first development, machine output can be attested by the harness; unattested spans deserve review attention.

That is worth writing. But the current draft confuses provenance with human detection, overreads tiny measurements, and leans on under-verified legal/watermark claims. Fix the framing, add a small controlled evaluation, report uncertainty, and tone down the product/legal language.

publish after fixes

### D. moonshotai/kimi-k3
# Review: "NoHumanWrite" (v0.1)

Overall: the paper contains one genuinely good idea (provenance-by-construction beats detection, and log forensics are insufficient because channel coverage is the binding constraint) and one excellent natural experiment (the 9% self-attestation). But the title overclaims, the abstract's headline numbers are the most favorable of several defensible aggregations, the statistical instrument is unvalidated, the ledger has no trust anchor, and the product inherits the exact alarm-fatigue failure the paper uses to kill layer 3. All fixable. Details by requested area.

## (a) The "inverted task" claim

1. **The tool does not perform the titular task.** Your own definition makes a human insertion "any span not produced by a logged machine write," and §5.1 then admits "unattested means human *or untracked*, and on this machine untracked dominates." So the system detects *unattested spans*, which on your own data are mostly machine-written. The title "finding the human" and the abstract's framing describe a task the artifact does not perform. Fix: rename the task "unattested-span detection" or "provenance coverage measurement," and state plainly that the inversion is a motivation, not a method. The actual contribution is a negative result on statistical detection plus a logging design — say so.
2. **"That question has no tooling" is false.** GitHub Copilot metrics, DX/Swarmia/LinearB AI-code-share dashboards, and Cursor telemetry all measure machine share of code at the team level. What doesn't exist is *line-level provenance at review time*. Narrow the claim or cite and differentiate.
3. **Missing prior art a cs.SE reviewer will demand:** code authorship attribution/stylometry (Caliskan-Islam et al. and follow-ups), in-toto/SLSA attestations and sigstore/Rekor (your "signed append-only ledger" is a reinvention — use it or cite it), and watermarking-of-code work. Also C2PA: the precise gap is that text/code has no manifest *embedding* location and sidecars detach from copied spans — your ledger is itself a sidecar, so argue why a new format beats a C2PA manifest with a custom line-range assertion.
4. **A false sentence in §1:** "The human-typed changes over the same period left no such record." On your own machine they left a record — the six-hour backup commits you describe in §5.2. The accurate claim ("recorded but unattributed and unannotated") is *stronger* for your argument. Use it.
5. **The simplest alternative is never considered:** instrument the human channel (editor plugin, pre-commit hook, `nhw attest --manual`) so human edits produce ledger entries too. Then "unattested" shrinks to genuinely accidental/sneaky edits. You jump from "humans don't log" to a detection product without justifying why the human channel can't be made to log. One paragraph on why editor-side attestation is incomplete (many editors, servers, `sed -i` on prod) would close this.

## (b) Base-rate arithmetic

The arithmetic is correct (I get 0.0801 at 5%, 1.6% at 1%, 0.343 at FPR 0.10). The problems are elsewhere:

1. **The 34% figure holds sensitivity at 0.993 while dropping FPR to 0.10.** That operating point implies AUC well above 0.99 — a fantasy detector. That's fine as an upper bound, but you must say so explicitly; as written it reads like a threshold adjustment, which it cannot be on your measured ROC.
2. **No uncertainty propagation.** 149/150 sensitivity has a 95% CI of roughly [96.3%, ~100%]; 90/150 FPR is [52%, 68%]. The 8% should be reported as ≈[7%, 9%] — narrow, fortunately, so report it.
3. **Unit mismatch.** The detector was evaluated on 40–300-word prose passages; the product flags lines and hunks in code. §6 silently transfers prose statistics to the deployment setting. Label §6 as an illustration, or run the real task (see (c)).
4. **The 5% prevalence is asserted, not measured.** You have the data to estimate the true human share of changed bytes (git history within the log window, cross-referenced with the ledger). Even a rough estimate converts this section from rhetoric to evidence.
5. **Abstract wording:** "60% of machine passages carry no detectable tell" is wrong — 60% fall *below threshold*, many with nonzero scores (your own p50 is 18). "Below the detector's threshold" is the claim you have.

## (c) Methodology and the three numbers

**96%.** The abstract says "attests 96% of lines (median) in code the agent wrote." That conflates the per-file median (96%) with a fraction of lines (line-weighted: 68%), and it hides the bucket you disclose only in the table: **22 of 63 tools — a third of the corpus — sit at 0–20% attested, and you never explain them.** The likely cause (predating the 30 July log window) is checkable from git history in an afternoon. Until you do, the headline number is unexplained variance, not a result. Also: report the strong/weak match split per corpus (weak matches on boilerplate like `from pathlib import Path` inflate attestation), and report what fraction of lines the <12-character filter excludes per corpus.

**No negative control.** You never measure false attestation on a corpus known to be 100% human-written. The raw notes could serve, but you assert without evidence that "the same agent wrote most of them" — and 25 of 100 raw files are >80% attested, which is either a damning false-positive rate or an unsupported claim about their provenance. Take pre-agent-era files (you have them) and measure hash-collision attribution directly.

**9%.** The best result in the paper, but the conclusion drawn from it is wrong in an instructive way: "log forensics after the fact cannot close this gap." Claude Code logs Bash tool calls *including the heredoc's full text*. The bytes were in the transcript; your extractor didn't parse them. The honest and stronger claim: Write/Edit parsing is insufficient, and parsing shell commands for file writes is unreliable in general (redirection, scripts, pipes, `python -c`), so the choke point must sit below the shell — filesystem watcher or git index. That also fixes the contradiction with §7's "a cooperating harness and a signed ledger serve the second constituency completely," which your own 9% result refutes.

**8% / the layer-3 evaluation.**
- The instrument is sloptrim, your own 71-pattern matcher, with no published validation. Your demolition of statistical detection rests on the weakest detector class. Add Binoculars or Fast-DetectGPT (local, published, RAID-evaluated) as a second instrument, or validate sloptrim on a RAID slice.
- The task you evaluated is "tell chat prompts from chat responses" — a different, easier task than "find the human paragraph spliced into a machine document." You have the data to run the real task (wiki pages with known human edits inside the log window). Run it, or downgrade the claims.
- **Confound:** human passages include *dictated* text. Speech-to-text output is machine-mediated prose (normalized punctuation, disfluency removal). Stratify typed vs dictated or exclude dictated turns.
- **Label contamination risk:** filtering out turns with "pasted structure" doesn't remove pasted machine prose without formatting. State how you verified label purity.
- "Burstiness" as defined is the coefficient of variation — name it correctly.
- **Internal inconsistency:** §5.1 claims "the 20–80% middle holds 6% of the wiki." Your own table gives (19+16)/285 = **12.3%**. The tools figure (5/63 ≈ 8%) checks out. Fix the 6%.

## (d) Architecture and the ledger

1. **There is no trust anchor, and the signature machinery is incoherent without one.** The signing key sits on the developer's machine; the agent, or the developer, can sign anything. The "append-only" JSONL file is a convention, not a property — the committer can rewrite it. So: against accidents the signatures are unnecessary; against the lazy-teammate adversary they're useless. Pick a lane. Either this is a convenience tool for cooperative teams (drop the crypto theater, keep hashes for integrity) or it's a compliance tool, in which case you need hash-chained entries with signed checkpoints anchored somewhere the developer can't rewrite (the GitHub App holding checkpoint history, or Rekor). Note the deeper problem: Claude Code transcripts aren't vendor-signed, so the whole chain bottoms out in software the user controls. Say this out loud.
2. **"Layer 1 proves machine authorship exactly" overclaims your own definition.** It proves a harness wrote bytes to a path. A human who dictates exact bytes to the agent gets them attested; a human who copies an attested line inherits attestation (your weak-match problem, institutionalized). You attest the *channel*, not the authorship — which is the right thing for the review-routing use case, so stop saying "authorship."
3. **"A positive [watermark] result is cryptographic, not stylistic" is a factual error.** Kirchenbauer and SynthID-Text are *statistical* watermarks: detection is a z-score over token counts with nonzero false-positive rates; the key is a PRF key, not a signing key. Fix the sentence; it's the kind of error that gets a paper quoted for the wrong reason. Also: layer 2 is nearly irrelevant to code (low-entropy tokens, syntactic constraints, no published code-watermark detection numbers), and your product is a code PR check. Say layer 2 is prose-only until evidence exists.
4. **The product inherits the base-rate failure you used to kill layer 3.** Your flags fire on unattested spans; on your own machine most unattested spans are machine-written (wiki: 23% line-weighted attested, agent wrote most of it). Deployed as a blocking or second-approver gate, nearly every wiki PR flags, and reviewers learn to click through — the same alarm fatigue, no statistics required. The paper never estimates the human fraction of unattested spans, which is the product's single most important metric. Measure it. And reframe the headline metric as *provenance coverage* (positive, measurable, auditable) with flags secondary.
5. **"Only the numbers leave" contradicts the design.** The ledger lives in the repo, which is on GitHub; hunk highlighting requires the diff and ledger server-side unless it runs in the team's CI. Specify the data flow (CI job vs GitHub App) and delete the contradiction.
6. **Formatter robustness is asserted away.** Whitespace normalization doesn't survive quote-style, wrapping, or import sorting. Run the experiment: formatter over an attested file, measure attestation drop. Then decide token-level hashing vs re-attestation hooks — don't leave it as an open question when it determines whether layer 1 survives contact with `ruff format`.

## (e) Ethics and regulatory framing

1. **Article 50 is half-cited.** You cite 50(2) (provider marking) but the stronger hook for your product is 50(4): *deployer* disclosure duties for AI-generated text published to inform the public. The ledger is exactly the evidence a deployer needs to know what they're publishing. Add it. Also hedge the claim that Anthropic's watermarking is "to satisfy Article 50" unless [12] says so explicitly, and note the open question of whether a non-public detection key satisfies "detectable" — the regime's interpretation is unsettled, and you assert it too confidently.
2. **"It never asserts that a person's work is machine-made, the failure mode with victims."** Your failure mode is flagging a person's hand-work as suspicious, repeatedly, in front of their team — and open question 5 already contemplates per-developer unattested-share as a management signal. "The ledger records a machine key, never a person's name" is cosmetic: `git blame` attaches every flagged hunk to a committer in one command. Own this and design against it (team-level aggregates only, no per-person dashboards), or delete the anonymity claim.
3. **GDPR / employee-monitoring law is unmentioned.** A per-write, timestamped, session-linked record of all machine-assisted work is a surveillance artifact; in the EU, Art. 88 and works-council regimes apply. For a paper leaning on the EU AI Act, this omission is conspicuous.
4. **"Cannot be turned around" is too strong.** The flag list is a worklist for a humaniser; the ledger can also falsely attest machine output as human-reviewed. "Ships without a humaniser" is the defensible claim.
5. Cut "a transparency law we are otherwise content to live under" — editorializing that buys nothing.

## (f) Factual / citation issues

- **[14] "Anthropic's Fable 5.1":** Anthropic's models are Claude-branded; I cannot verify a "Fable 5.1." Verify the attribution or correct it. More broadly, the entire Anthropic-watermark paragraph (worldwide, no opt-out, "a scheme of this family," C2PA on sandbox media) rests on one help-center article and a YouTube video. "Of this family" is unsourced speculation about an undisclosed scheme. Get a primary source (engineering post, model card) or hedge each claim.
- **[14] citation practice:** you're boosting a laundering tutorial by title and video ID. Cite it as evidence of the laundering ecosystem without the ID, or keep the ID and add a one-line rationale.
- **[2] "reliable detection at a few hundred tokens":** give the exact figure and setting from the Nature paper; "a few hundred" is doing load-bearing work in layer 2.
- **[4] "rates above 60%":** Liang et al. report ~61% *average* FPR across detectors on TOEFL essays. Say "on average across seven commercial detectors" — the plural "detectors … above 60%" is not what the paper shows.
- **"The best local detector" (abstract):** best of two, one of which is a coin flip, the other unvalidated. "A pattern-based local detector."
- **§5.2 arithmetic checks** (551/667 = 82.6% ✓); table row sums check; the 6% wiki-middle figure does not (see (c)).
- **References [12] and [15]:** a help-center article with an access date and an unversioned self-tool with no repo link are not adequate for claims this central. [15] needs a public URL and a validation section before the repo goes live.
- Move `business.md` pricing and "five design partners within a month" out of the paper and into the repo; a go-to-market plan in a cs.SE preprint invites desk rejection.

## Verdict

**Publish after fixes** — the core observation (provenance-by-construction has no base-rate ceiling; log forensics fail because coverage, not detection, is the constraint) is sound and worth publishing, but not with the current title claim, the unexplained 22-file hole in the headline corpus, the "cryptographic" watermark error, the unvalidated detector, and a ledger whose signatures currently sign nothing anyone can trust.

### E. deepseek/deepseek-v4-pro-0813
As a senior reviewer I want to separate four things this paper does: defines a task, argues a base-rate point, presents a proof-of-concept, and proposes a product. The base-rate point is well-taken. The rest has problems.

---

## (a) Is the inverted task distinct and useful?

**Useful, yes. Distinct, no. And the paper overclaims.**

"Find the human insertions among machine-written text" is an instance of authorship attribution with very skewed priors, not a new task. The same operation is called *unattested change detection* in Audit/Audit and taken for granted in database security. The paper would be stronger if it said so: the contribution is the application, the led¬ger format, the triage UX, not the discovery that one can invert a classifier.

The sharper problem is that the claimed value has a hidden conditional: **it is only useful where the agent's write path is trustworthy and where a human insertion is actually an incident.** The paper states this as "the human's contribution belongs in the prompt and the review, and a human byte in the artefact is an exception path". On a team where a human routinely fixes agent output by editing (rather than by re-prompting), this tool fills the PR with warnings until everyone mutes it. The paper never quantifies the exception rate on its own machine, even though it has the logs to do so. If the human's *own* tracked changes to "the agent's code" are near 96% attested because the human stops using the tool and the "fixes" happen in the editor, the spot is not `tools/*.py`; the spot is the workflow policy. The tool cannot tell the two apart and neither can the paper.

**Concrete fix:** add a one-page "Is this workflow for you?" subsection with the decision rule: *use if a human insertion is exceptional and reviewable by design; not if agents are first-draft assistants whose edits are expected.* It would reduce the evangelism and make the paper honest.

---

## (b) Base-rate arithmetic

The arithmetic itself is correct but the parameters are cherry-picked, not measured. The 0.993 figure comes from a rule designed to have that number on that corpus. The 0.60 FPR comes from the same detector and threshold. Both are then fed into a toy example with a 5% human prevalence, and the conclusion—layer 3 cannot be promoted—is presented as a theorem, not a measurement.

**Problems:**

1. The classifier is not the rule, but the paper conflates them when it feeds "the measured sensitivity and false-positive rate of the no-tell-means-human rule" into the precision equation. The AUC was for sloptrim score as a continuous decision. The 0.993 / 0.60 pair is from a hard threshold (score ≥ 20). The paper then generalizes: "No threshold rescues this." For a 5% prior, any test with a likelihood ratio \(\Lambda \approx \frac{P(\text{tell}|\text{H})}{P(\text{tell}|\text{H}^c)}\) above ~19 yields precision >0.5. With the observed tell rates the ratio is 0.40 / 0.60 ≈ 0.67—useless. But the conclusion does not follow from a single detector on a single corpus; it follows only if *every* detector has this shape. The paper argues this from RAID and from Sadasivan et al., but those works are about detecting machine text in the general population, not about detecting the *relative* absence of a tell inside an artefact with a very high prior of machine origin. The two are not the same task, even though the paper says they are.

2. The "lowering the false-positive rate to 0.10" thought experiment mislabels the quantity. For the rule "no tell means human", the FPR is the rate at which *machine* spans show no tell—which was 0.60. The "false-positive rate" being lowered to 0.10 is the *human* test's FPR = 1 - sensitivity. The two are not the same axis, and that paragraph slides between them.

**Concrete fix:** rewrite section 6 with explicitly separated axes and a stated likelihood ratio. Show, from measured tells, what Λ you observed. Then say, honestly: *any triage method is only as good as its Λ; ours measured 0.67.* The toy table that follows is not needed.

---

## (c) Proof-of-concept methodology and whether the numbers support the conclusions

The 0.91 AUC and the 96 / 9 / 8 numbers are not commensurable and should not be in the same paper section. The first measures a classifier on 300 prose passages from one person chatting to one model. The second measures a log-reconstruction on 456 files from a mishmash of sources, most of which the logs did not cover. The third is the paper's one real result:

> The PoC's own source files, written by the agent through an unlogged shell heredoc, show 9% attestation.

That is a finding worth publishing: **line-level attestation reconstructed from a transcript log is good where the transcript covers the write, and wrong everywhere else.** It supports the conclusion that only a write-time hook works. It does **not** support:

- any claim that the tool reliably finds human insertions in the wild;
- the table's "96% median" as an accuracy number—because the corpus is defined by what the transcript can reconstruct, not by ground truth;
- the statement that "the remaining few per cent are lines later touched by hand or by a formatter" as fact—the paper has no independent record of what those lines are.

**Methodology flaws:**

- **No ground truth for the file corpora.** The paper has only the transcript as evidence. Its claim "these are hand-touched lines" for the unattested 4% in `tools/*.py` is unverified. In fact, the same evidence cannot distinguish "hand-touched" from "generated by the same agent through another channel"—which is the point the paper makes about the PoC's own files but not for the tools.
- **The corpus table mixes three different regimes** (pre-log-window, other-harness, logged) under one label. The table's right-hand columns show this and the text admits it, but the admission contradicts the earlier "median 96%" headline. The headline is not a property of the system; it is a property of the corpus.
- **"9% in its own source"** is a *great anecdote*, but it is not a result. It is one session. The paper generalizes from it to "proof that only a record emitted by every writing channel at write time can close this gap"—which is overreach from n=1.

**Concrete fix:** Add a ground-truth table where each corpus is labelled with channel and log window overlap, and make the corpus-selection criterion explicit: *"we selected files we expected the transcript to cover."* If the tools were chosen to show high attestation, say so. Report both strong and weak match separately. The 96% median becomes "96% median strong among tools written during the logged window" and is no longer able to support the summary claim.

---

## (d) Three-layer architecture and the signed-ledger product

The architecture has the merits the paper claims: layer 1 is right, layers 2 and 3 are truthfully ordered. The ledger format as described has real problems and the product as described is premature.

1. **The ledger is not append-only in any meaningful sense.** `.nhw/attest.jsonl` is a file in a git repo. It can be edited, squashed, rebased, force-pushed, pruned, or deleted. "Signed" is not defined. Which key? Which algorithm? Where is the public key? A reviewer's acceptance of a signature without a stated trust chain is theater. If the signature is a GPG/SSH signature of the JSONL line by a machine key, then the *human* key was signed by the developer's key, the *machine* key was generated by the same developer, and both are just software on the same laptop. That is a property of the system and it is fine for its stated purpose—make the common case cheap and auditable—but it is not a "ledger" in the sense a reader will infer, and the paper should say so.

2. **The verifier's threat model is unstated.** Is the ledger meant to protect against a developer who deliberately hides changes? Against an agent that calls `sed` directly? Against a third-party contributor without a hook? These are different products.

3. **The "reviewer sees unattested, not Arnaud" design rule is good but is not identified as a legal necessity.** In a jurisdiction with the AI Act's Article 50, the tool itself may be subject to the Article 50 provider's obligation, depending on whether it is deployed as a service. The paper says "the tool ships with no humaniser..." and stops. It does not say whether the tool's own *output*—the report—is machine-marked. If the report is generated by a model (it says "only the numbers leave"), then the report is machine-generated content and **the tool itself is an AI system provider under Article 50** if it is offered as a service to other organizations.

4. **The "vendor watermark" layer is described as usable "the day a detection endpoint ships" but no evidence is presented that Anthropic's endpoint is promised or even planned.** On the contrary, the Help Center article cited says detection details will follow in technical documentation. That is not a detection endpoint. The layer is aspirational.

5. **The GitHub App is not consistent with the signed ledger.** If the ledger's value depends on a local key and a signed local record, a hosted SaaS that computes "only the numbers" must either hold the private key (destroying the trust model) or receive pre-signed records from the hook. The paper does not say which. The phrase "only the numbers leave" is a privacy claim, not an architecture claim, and it should either be specified or removed.

**Concrete fix:** specify a minimal trust model: human root key, machine subkey, signing algorithm, key custody, and what "append-only" means (e.g. the hook refuses to overwrite an existing hash for the same file/hunk). Add one threat-model sentence per layer. Add one sentence on the tool's own Article 50 posture.

---

## (e) Ethics/regulatory framing

The ethical section is the weakest part of the paper. It announces, "NoHumanWrite is the mirror image. It never removes a mark." That is true in this repository. But the paper's own frame of reference includes a cited YouTube video that explains how to remove a watermark, and the README of the published repo, the paper says, will be a tool whose output is a list of hunks that *do not carry* a watermark. A user can feed that output into a laundering workflow: "Rewrite these unattested hunks." The paper says "the vault had already filed watermark removal as something not to build, on the reasoning that disclosure is the point of the mark and a transparency law we are otherwise content to live under should not be defeated for convenience." That is a fine personal position; it is not a technical property of this tool.

Second, the paper asserts "It never asserts that a person's work is machine-made, the failure mode with victims." At layer 2 and layer 3, the tool reports *probable human insertions*—that is exactly what it appears to do. It says "indicates an unattested span" but a user reads "human insertion" and acts. The paper should say what happens when a probable human insertion turns out to be a machine span that simply lacks a watermark (or has a watermark the vendor's detector failed to find). The current design has no remedy for this. It will route a false alarm to human review; the reviewer will see a legitimate machine output and be told it is an unauthorised human change. **False positives here are not the same as false positives in an AI detector, but they are still false positives and they can damage a person's professional reputation if overlaid on an HR dashboard.** Section 7 does not mention HR dashboards. It should, explicitly.

Third, the paper cites §50 of the EU AI Act, but it seems to confuse two distinct doc obligations: provider-deployer transparency that content is AI-generated or manipulated *for certain actors working in the public interest* (e.g., a person with a need to know under the AI Act) vs the general *obligation to make the public aware that they are interacting with an AI system* in Article 50(1). The paper's "obliges providers to mark machine output so that it can be detected" is a gloss. The right place to lean is the AI Act's Article 50(2) transparency for certain AI outputs. As written, "citizens can tell" suggests the model is the user-facing disclosure, which is not the same thing.

**Concrete fix:** replace "citizens can tell" with the actual legal categories. State explicitly which article subsection creates the duty. If the paper cannot do that, remove the claim.

Additionally, "Anthropic adopted a scheme of this family for models released on or after 2 August 2026, applying it worldwide and across every product surface, with no opt-out, to satisfy Article 50" is not verifiable from the citations in this paper. The Help Center article does not say "no opt-out." The paper should not attribute a policy position to Anthropic unless Anthropic announced it. The birthday itself is suspicious: the AI Act applies from Aug 2 2026, so a policy decision saying "we watermarked because the AI Act" may be the author's inference. Mark it as inference or remove it.

Finally, "Anthropic's worldwide text watermark" appears in the abstract without a citation and before the background has told us what it is. The cited Help Center article says "how Claude marks AI-generated content," not that it watermarks all worldwide text. If the paper cannot substantiate "worldwide" and "all text," it should say "Claude's announced marking" or "Anthropic's Claude watermark (announced)."

---

## (f) Factual/citation errors

- **"Anthropic's worldwide text watermark, SynthID-Text"** in the abstract conflates a product policy with a research artifact. SynthID-Text is Google DeepMind's scheme. Anthropic has said it uses a scheme *of this family* [12]. The abstract's phrasing implies SynthID-Text is deployed by Anthropic. It is not stated by Anthropic (as of this paper's date). Wrong. Fix: "Anthropic's worldwide text watermark, SynthID-Text and C2PA" → "Anthropic's announced text watermark, the SynthID-Text scheme, and C2PA". Keep them as separate things.

- **"A video published this week... [14] ... [explains] a recipe for laundering that text"**—the paper cites a YouTube video by a person named Chase AI. That is not a verifiable reference. A video is not a reliable source, and a hostile reviewer will say exactly that. If the claim matters ("watermark removal is in circulation"), cite a technical report or at least the video with title, channel, date of publication, and a content note, as the draft does. The draft's reference is already there. But a public paper should not use a YouTube tutorial as the evidence for its central motivating claim.

- **"OpenAI... withdrawn 20 July 2023"**—the cited URL says "As of July 20, 2023, the AI classifier is no longer available due to its low rate of accuracy." The paper should not cite it as "new AI classifier for indicating AI-written text" with withdrawn note in URL style; the actual page title is "New AI classifier for indicating AI-written text" and the update is on the same page, so citation is fine. The parenthetical "withdrawn 20 July 2023" is accurate. Minor only.

- **"C2PA Technical Specification 2.2"**—the version number may be wrong. The C2PA 2.2 specification exists and is on c2pa.org; but the paper says "C2PA Technical Specification 2.2: Content Credentials." The current C2PA spec version as of 2024-2025 was 2.1; 2.2 may be released by the paper's date, but it is worth verifying. If in doubt, cite the latest version available at the URL without a version number, or state "version 2.x as of 2026."

- **"Anthropic... C2PA manifests to media its sandbox produces [12]"**—same Help Center article. Fine.

- **"Fable 5.1"** in the reference [14]—Anthropic's model name is not "Fable 5.1" in any publicly announced release as of my knowledge. If the paper is set in September 2026, and a model called Fable 5.1 has been released, then ok. But the paper should not imply it exists without a primary reference. The cited video title says "Fable 5.1 Watermarks EVERYTHING." A hostile reviewer will check and find no such model on Anthropic's models page. The paper should use "Claude 5.1 (or whatever the model is called)" and not invent names.

- **"SynthID-Text ... published in Nature in October 2024 ... deployed across Gemini [2]"** – the Nature paper is *Scalable watermarking for identifying large language model outputs*, October 2024. The deployment across Gemini is in Google's blog, not necessarily in the Nature paper. The paper says "deployed across Gemini [2]" citing only the Nature paper. That is a citation error. Add a Google DeepMind blog or the Gemini release note.

---

## Verdict

**Publish after fixes.** The base-rate point is worth publishing. The proof-of-concept result about shell-heredoc blind spots is worth publishing. The product and ethics sections need enough disambiguation to be credible, and the paper should drop the claim that it found a new task.

### F. x-ai/grok-4.6
## Review (hostile, pre-arXiv cs.SE)

This is an n=1 engineering diary and a GitHub-App pitch, written in the voice of a research paper. The empirical objects do not measure the claimed task. Several load-bearing citations and product-facts are unverifiable from the manuscript. Do not put this on arXiv until the claim, the unit of analysis, and the bibliography are rebuilt.

---

### (a) The inverted task is not a distinct, useful research problem as stated

**What you actually defined.** §3: a “human insertion” is *any span not produced by a logged machine write*. That is **unattested bytes**, not human authorship. You admit the collapse yourself (§5.1): “Unattested means human *or untracked*, and on this machine untracked dominates.” The 9% row is the same tautology: a shell heredoc is not the Write tool, so the Write-tool indexer misses it. That is instrumentation coverage, not an inversion of AI-text detection.

**Not distinct.** Line-level provenance is git blame, Co-Authored-By, in-toto/SLSA, C2PA-style manifests, editor telemetry, and “who ran fmt.” Detector inversion is a rhetorical wrapper around (i) log what the harness already knows and (ii) stare at the residual. Layer 2 is ordinary watermark verification. Layer 3 is “run sloptrim and look at low scores.” None of that is a new task with a new risk function.

**Usefulness is asserted, not shown.** “In our experience they are where the incidents live” has zero incidents, zero diffs, zero MTTR, zero ablation vs agent bugs, hallucinated APIs, or missing tests. The harm model (skipped pipeline → incidents) is plausible and **unmeasured**. The name and slogan (human bytes in the artefact are an “exception path”) are a process religion, not a result.

**Genre error in the only “ML” experiment.** User turns vs assistant turns in the *same chat log* are different registers (instructions vs answers), not human vs machine spans inside one artefact. AUC 0.91 can be “prompt vs reply.” It cannot support “finding the human in machine-written work.”

**Fixes**
- Rename the object: **attested vs unattested spans**, with an explicit residual class {human edit, unlogged agent, formatter, other harness, pre-window}.
- Drop “inversion of AI detection” as the contribution unless you define a dataset of *in-file* substitutions with span-level labels and a cost-sensitive metric (false “unattested” vs missed hotfix).
- Supply a defect study: sample unattested hunks vs matched attested hunks, blind-label production incidents / review comments / revert rate. If there is no lift, the product thesis is dead.
- If this is a position/experience report, say so in the title and abstract. Do not lead with detector AUC.

---

### (b) Base-rate arithmetic: the algebra is fine; the application is not

The plug-in  
`0.993·0.05 / (0.993·0.05 + 0.60·0.95) ≈ 0.08`  
is correct. The 1% and FPR=0.10 variants are also correct. That is the only clean calculation in the paper.

**It does not license §6’s conclusion.**

1. **5% is invented.** “Generous for an agent-first team” has no measurement on your own 2,716 writes, let alone anyone else’s. Your table is the opposite of 5% human: wiki/raw are mostly unattested because of **untracked channels and log window**, not a 5% human base rate.
2. **Wrong unit.** Operating characteristics come from 40–300 word *chat* passages. The product flags *lines/hunks of code and markdown*. A 12-character ignore rule already deletes the hotfix class you advertised (`except: pass`). You cannot transport FPR/TPR across granularity, domain, or genre.
3. **Wrong decision rule.** “No AI-tell ⇒ human” is a straw rule on a slop-pattern counter. Absence of 71 stylistic tells is not a human detector. A likelihood ratio, a human-specific model, or “high burstiness + low slop + edit-distance from last attested snapshot” is the actual inverted task. You never built it.
4. **Wrong literature jump.** RAID/Sadasivan/paraphrase FPR numbers are for *machine-vs-human document detection*, not for residual-span triage inside a mostly-machine file. “No threshold rescues this” is false in general; it is true for *this* detector, *this* rule, *this* made-up prevalence.
5. **Asymmetric costs are hand-waved.** You say false “human” costs a review and false “machine” hides the bug. That is an argument for **high-recall attestation (layer 1)**, not a proof that every statistical residual is useless as a sort key. You already demoted layer 3; the Bayes sermon is theatre.

**Fixes**
- Measure prevalence on labelled diffs (span fraction *and* hunk fraction), with CIs, per corpus.
- Report a full ROC/PR curve of any residual scorer **at hunk level**, with the real class definition (unattested, not “human”).
- Stop citing classroom-detector harm [3,4] as if it were a theorem about your PR bot.

---

### (c) PoC methodology: 96% / 9% / 8% do not support the claims

**96% (median attested, `tools/*.py`).** You parse Claude Code transcripts for Write/Edit, hash whitespace-normalised lines, and re-read files on disk. That is **parser recall against the same logs**, not an authorship experiment. Of course logged writes attest. Even then the table contradicts the prose:

- median 96% vs **line-weighted 68%**
- **22/63 files in 0–20%** (35%), 36/63 in 80–100%
- “near-complete” and “bimodal, middle is 8% of tools” cherry-picks median + the high mode and buries the 22 empty files

Those 22 files are the interesting population (other channel, pre-window, formatter, human). You do not break them down.

**9% (this PoC).** Instructive only as a **negative control for incomplete hooks**. It does not measure humans, does not compare designs, and does not show that a signed ledger would have been 96% here—you did not emit one. Weak matches on generic imports are hash collisions/boilerplate, i.e. a correctness bug in the matcher, reported as a result.

**8%.** See (b). Abstract presents it next to 96% and 9% as if it were the same experiment. It is a hypothetical on chat-sloptrim.

**Ground truth for §5.3 is not ground truth for the task.** 150+150 from one writer, one model family, one register, undersampled from 310 vs 2,987, “near-duplicates removed” with no method, scored by **unpublished** sloptrim 0.9.0 (not DetectGPT, Binoculars, RAID, SynthID). Burstiness AUC 0.483 is a useful demolition of a folk claim; it is not a substitute for a baseline table. No CIs, no session hold-out, no second annotator, no other developer.

**Other methodological holes**
- Lines &lt; 12 chars dropped: systematically misses the incident class in §3.
- Strong vs weak path match: no collision study, no normalisation spec in the paper (SPEC.md is off-repo).
- Log window from 30 Jul 2026 vs wiki/raw “mostly unattested”: time-censoring is confounded with authorship. Not analysed.
- Git cross-check (§5.2): two anecdotes. Shows git trailers ≠ write provenance. Fine as a blog paragraph; not a result.
- “All code is Python stdlib. Nothing leaves the machine.” Then sloptrim 0.9.0 and a GitHub App that ships “numbers.” Pick one.

**Fixes**
- Report attestation as **coverage of Write/Edit-tool bytes**, with a confusion matrix over {logged write, shell/other, human editor, formatter, pre-window}. Median *and* weighted, with file-size stratification.
- Publish sloptrim or replace it with a frozen public detector; add RAID-style paraphrase/edit robustness on *spans*.
- Do not put 96/9/8 in the abstract unless they share a denominator and a class definition.
- Multi-developer, multi-harness replication, or relabel as an experience report with n=1 in the title.

---

### (d) Three-layer architecture and signed ledger

**Layer 1 is not a proof.** A hook that records (path, hunk, hash, model, session, signature-from-dev-key) proves that *a process with that key claimed a write*. It does not prove machine authorship:

- the human can drive the Write tool;
- the agent can use shell/heredoc/git (your 9%);
- the agent on the same machine can **write `attest.jsonl` and sign** (confused deputy);
- repo-local “append-only JSONL” is not append-only under rebase, force-push, or filter-branch unless a server ref policy exists—you specify none.

Hash-of-normalised-text is brittle (formatters: your own open question) and collision-prone (imports, brackets you already ignore). “Proves machine authorship exactly and proves nothing about the remainder” is false on both sides.

**Layer 2 category error.** Kirchenbauer/SynthID-class marks are **statistical with a secret key**, not cryptographic signatures. You call them “statistical watermark” and then “a positive result is cryptographic, not stylistic.” That sentence must die. Short code hunks vs “few hundred tokens” in [2] is correctly flagged as an open question and then ignored by the architecture diagram.

**Layer 3** is demoted in prose and dominates the measurements. Incoherent.

**Product (§8)** is out of place in cs.SE research: GitHub App, policy pack, `business.md`, “five design partners will tell us within a month.” That is a launch plan. The honest test you name (does the PR number change one review decision a week) is the right test and **is not in the paper**.

**Fixes**
- Threat model: key storage, agent compromise, hook bypass, ledger tampering, formatter, generated code, secrets in JSONL.
- Attestation = “this tool invocation produced these bytes,” never “a machine wrote this.”
- Server-side append-only (signed commits, sigstore/Gitsign, or a transparency log), not a file the agent can edit.
- Either implement layer 2 against **open** SynthID-Text with your key, or drop it until a vendor endpoint exists. Do not advertise a slot.
- Move pricing/partners to a README. Keep the paper to threat model + coverage metrics + one field deployment.

---

### (e) Ethics / Art. 50 / watermarks

**Art. 50 is stretched.** Regulation (EU) 2024/1689 Art. 50 is provider/deployer transparency toward *affected persons and the public* (machine-readable marking of synthetic output; extra rules for deepfakes and some public-interest text). It is not a mandate for internal PR gates, developer-scoreboards, or “trust the machine, inspect the human.” “The use the transparency regime was missing” is advocacy, not legal analysis. If you want the frame, quote the operative paragraphs and stop.

**Watermark paragraph is unsafe for a public repo.** [14] is cited as a 10-minute laundering recipe. You say you will not build removal; you still platform the video as “the mood.” For cs.SE + Apache repo, drop the video or cite a technical paper on watermark robustness. Do not summarise recipes (you mostly didn’t; keep it that way).

**“Cryptographic / never labels humans” is not the operational behaviour.** The App “highlights unattested hunks” and can require extra approval or block. That *is* a penalty on the residual, which on your own data is mostly humans *and* untracked tools. Open question §9 (“unattested share across developers… management signal”) is a surveillance feature you left on the table. “Ledger records a machine key, never a person’s name” does not survive `git blame` + file path + working hours.

**Mirror-injustice claim is unfinished.** Liang et al. [4] is about false *machine* labels on non-native writers. Your dual is false *human/unattested* labels on bland machine text—and extra review burden on whoever types. You do not measure who gets flagged.

**Fixes**
- Separate: (1) legal marking duties, (2) optional consumer detection, (3) internal provenance for engineering. Only (3) is your system.
- Threats: workforce monitoring, discrimination via “unattested share,” prompt to hide work in-band (comments, string splits) to evade hashes.
- Policy default: extra review on unattested hunks must be opt-in and aggregated, not per-developer, until you have a bias study.
- Delete the YouTube how-to citation.

---

### (f) Factual / citation / integrity problems

Treat these as blocking for arXiv:

| Item | Problem |
|---|---|
| Dated **4 September 2026**, logs from 30 Jul 2026, Anthropic access 14 Aug 2026 | Fine as a timestamp *if true*. Then every 2026 vendor claim needs a stable URL/DOI, not “Help Center article 16266773.” |
| **“Fable 5.1”** worldwide, no-opt-out watermark from 2 Aug 2026 [12] | Not a verifiable scholarly source in the bibliography. If this is design fiction, label it. If it is a product fact, cite primary policy + technical doc. “Detection details will follow” means layer 2 is vapour. |
| Watermarks = **cryptographic** | False for [1,2]. |
| Sadasivan et al. [3] as “any detector → coin flip” | Overstated; their setting is not a blanket impossibility (watermarks exist precisely as a counter-regime). |
| “C2PA… no text profile” [11] | Too strong; C2PA is media-centric but not a theorem that text credentials cannot exist. Qualify or cite the spec section. |
| OpenAI classifier [9] | Withdrawal in Jul 2023 is right; “31 January 2023” launch date is the usual one—keep the update note. |
| sloptrim 0.9.0 [15] | Not a publication. Cannot be a “best local detector” in a research abstract. |
| SynthID-Text Nature Oct 2024 [2] | Plausible; still pin pages/DOI as you did. Token-length claim is for their settings/prose—you already note that; don’t let layer 2 imply code hunks work. |
| Art. 50 “applicable from 2 August 2026” | GPAI/transparency phasing is easy to get wrong; cite the Official Journal applicability schedule, not a vibe. |
| Abstract “300 ground-truth passages” | 150+150 chat turns, not artefact spans. |
| “Best local detector… AUC 0.91, yet 60% of machine passages carry no detectable tell” | *sloptrim threshold 20*, one author. Not “tells.” |

Also: Anthropic “C2PA manifests to media its sandbox produces” [12] is again Help Center. Primary spec vs marketing page.

---

### Smaller engineering comments (still blocking if you ship the repo)

- Weak line hashes across paths are a plagiarism/boilerplate magnet and a privacy leak (identical lines in private files).
- `.nhw/attest.jsonl` will conflict on every parallel agent session; no merge algebra.
- “Signature from a key on the developer’s machine” + agent with shell = the agent is the CA.
- Formatter/refactor open question is not optional: without re-attest or AST-level hashing, layer 1 dies on `ruff`/`gofmt`.

---

### What a publishable paper would be

One of:

1. **Experience report:** “Coverage of Claude Code Write/Edit logs vs disk, n=1, five weeks,” with the real residual taxonomy and no Art. 50 sermon.  
2. **Systems:** attested write protocol + threat model + hook bypass evaluation (shell, formatter, rebase) + one team’s PR study.  
3. **ML (only if you mean it):** span-level dataset of in-file human edits in agent-written artefacts, baselines, cost-sensitive PR curves, domain shift.

This draft is 1 with the rhetoric of 3 and the landing page of a fourth thing (SaaS).

---

**Verdict: do not publish.**

### G. z-ai/glm-5.3
# Review: "NoHumanWrite" (draft v0.1)

**Summary judgment.** There is a real paper hiding in here: "provenance-first authorship auditing for agent-first teams, and why the statistical inversion of AI-text detection fails by base rates." The draft instead oversells a rhetorical frame ("inverting detection") that its own §6 demolishes, reports PoC numbers that are weaker than their presentation, contains at least one arithmetic error, omits a threat model for the product it defines, and overstates the regulatory facts. Details follow, with fixes.

## (a) The core claim: a distinct, useful task

1. **The "inversion" only exists at layer 1, and layer 1 is not detection — it's logging.** Layers 2 and 3 answer the *original* question ("is this machine?") at document/paragraph granularity. A watermark positive on a human-edited machine paragraph tells you nothing about *which span* is the insertion; the insertion is masked by the surrounding positive. So the distinct task you claim is performed by exactly one of your three layers, and that layer is an audit log, not inverted detection. Fix: reframe the contribution as "unattested-span detection via write-time provenance," and say plainly that layers 2–3 are fallbacks doing the *old* task, not the new one.
2. **Your own definition makes the task channel-classification, not authorship.** §3: a human insertion is "any span… not produced by a logged machine write." All three of your motivating incidents (the 23:40 hot-fix, the hand-changed constant, the `except: pass`) become *attested machine writes* if typed into the agent chat. The tool is a workflow nudge against accidental bypass, trivially routed around by anyone motivated. That's a legitimate product, but state the threat model: honest mistakes only. "Proves machine authorship exactly" (§4) must go — a signed write event proves *channel*, not authorship; human-dictated-via-prompt text is "machine" by construction.
3. **"This question has no tooling" (§1) is false.** Git trailers (which Claude Code emits by default), signed micro-commits, editor local history (VS Code Timeline), supply-chain provenance (SLSA, in-toto), and the emerging mixed human–AI authorship detection literature all bear on it. You cite C2PA but not SLSA — the closest existing standard to "this artifact came from a known process." Fix: add a related-work section that engages these; the distinctness claim must survive them.
4. **Usefulness rests on one anecdote.** "In our experience… where the incidents live" is n=1 retrospection. Fix: instrument your own repo for a month and correlate unattested spans with revert/fix commits, or classify ~10 post-mortems. §8 concedes the real test isn't in the paper; put a weaker version of it in the paper.

## (b) Base-rate arithmetic

5. **The arithmetic is correct; the inputs are not.** I verified: 8.0% at 5%, 1.6% at 1%, 34% at FPR 0.10. But sensitivity 0.993 / FPR 0.60 were measured on 40–300-word *chat prose* and applied to "5% human share *by span*" in *code*. Unit and population mismatch. Fix: either run the statistical layer on code (the actual PR-check artifact — you never do), or restrict §6 to prose artifacts.
6. **The 34% hypothetical is a fictional detector.** You keep sensitivity at 0.993 while cutting FPR to 0.10. Your own distributions (machine p90 = 25, human p90 = 8) forbid that operating point: at FPR 10% the threshold is ≥25 and sensitivity is ≈0. Fix — and this makes your argument *stronger*: sweep the threshold, plot precision vs. prevalence from the measured ROC, and report the precision-maximizing operating point.
7. **"60% of machine passages carry no detectable tell" conflates "score < 20" with "no tell."** Machine median score is 18; the score-zero fraction is far below 60%. Say "below the detector's threshold."
8. **The 5% prevalence is asserted, not measured.** You have five weeks of transcripts and the files; estimate your own human-insertion share, or the "generous figure" is a guess doing load-bearing work.
9. **You never run this arithmetic on layer 1 — the biggest omission in the paper.** "Provenance has no base-rate problem" is half true: attested spans are exact, but the *flag* "unattested ⇒ review" has its own precision, P(human | unattested), and your own data says "on this machine untracked dominates." §6's alert-fatigue argument applies verbatim to your product until coverage is near-total. Fix: compute layer-1 flag precision on labelled data, symmetrically with §6.

## (c) PoC methodology: do 96 / 9 / 8 support the conclusions?

10. **The 96% is not a measured accuracy — it's the tool's output on an unlabelled corpus.** There is no ground truth in §5.1 anywhere. Worse, the corpus contradicts the claim it's presented under: 22 of 63 tool files sit at 0–20% attested, so "code the agent wrote" is false for a third of the corpus, and the abstract's "attests 96% of lines (median) in code the agent wrote" is circular *and* garbled — it's the median of per-file shares; line-weighted it's 68%. Fix: (i) label a sample (session replay, or synthetic: agent writes, human edits, formatter runs) and report sensitivity/specificity/precision; (ii) restrict headline numbers to files whose writes fall inside the log window; (iii) report both median and line-weighted in the abstract.
11. **Weak matches contaminate every number.** "The agent wrote that line somewhere" attests any generic line as machine-written; the PoC's 9% is exactly this false machine-attribution. Do the corpus percentages include weak matches? If yes, they're inflated; if no, say so. This also falsifies §7's "It never asserts that a person's work is machine-made." Fix: report strong-match-only numbers.
12. **The 9% is a parser artifact dressed as a fundamental gap.** The heredoc bytes *are in the transcript* — Bash tool inputs are logged. "Log forensics after the fact cannot close this gap" is false for the very case you exhibit; the honest claim is that parser coverage will never be complete and some channels (editors) log nothing. Fix the claim, or demonstrate with a genuinely unlogged write. Also: the two wiki pages the agent wrote end-to-end are ground truth the transcript index should nail — you report git's 0% for them but never the index's number. Report it.
13. **§5.3 has a genre confound.** The human class is terse imperative instructions; the machine class is assistant prose. sloptrim separates *register*, not authorship. You have hand-written prose (the raw notes) — use it as a second human class. Also unspecified: dedup method, whether machine passages were structure-filtered symmetrically, no CIs (bootstrap the AUC), and "best local detector" means "best of two, one of which is a coin flip."
14. **Arithmetic error in "Three readings":** "the 20–80% middle holds 6% of the wiki" — your table gives 19+16 = 35 of 285 = **12%**. (Tools: 5/63 = 8% ✓.) Fix it.
15. **Release hygiene:** `~/nohumanwrite` is a local path; "to be published" is unacceptable at submission. Pin sloptrim's commit hash (pattern lists drift across 0.x). Scrub session IDs from any released derived dataset. Clarify whether "72,681 attested lines" dedups across edits and includes weak matches.

## (d) Three-layer architecture and the signed-ledger product

16. **No threat model.** The attestation key lives on the developer's machine — the party whose behavior is measured. A motivated developer signs a hand edit, or asks the agent to re-emit it. And the machine channel is the *scalable attack channel* (prompt injection, malicious tooling): your policy scrutinizes human writes more than machine writes, inverting standard insider-threat assumptions, justified by tests the agent itself writes. Fix: an explicit adversary section; scope to accidental bypass; justify or soften the trust ordering.
17. **"Append-only in the repository" is aspirational.** The repo owner rewrites history; parallel branches appending to one JSONL conflict on merge. Fixes: per-machine namespaced files with union-merge semantics (or git notes), pubkey published in-repo, external anchoring of ledger heads if you want tamper-evidence against the repo owner — otherwise say the ledger is tamper-evident only against third parties.
18. **The matching design is the weakest available.** Content-hash-of-normalized-line keyed by path breaks on renames, moves, duplicate lines, one-token edits, and formatter runs (which you defer to "open questions" — it's a design decision, not open). Fix: record file snapshots (or hunks) per write and attribute by diffing successive snapshots; re-attest after harness-invoked formatter runs.
19. **Simpler alternatives you must adopt or refute:** (i) harness auto-commits each Write/Edit as signed micro-commits with trailers — git blame *becomes* the ledger, no new format, no new verifier; your §5.2 dismissal is a config error (a backup job committing under the human's name), not evidence about git; (ii) an OS-level watcher (eBPF/auditd/FSEvents) logging (path, hash, process) on the repo directory — solves the heredoc, editor, and Telegram-bot coverage gaps in one mechanism, which harness hooks never will. If two lines of git config get 80% of layer 1, the signed JSONL needs a justification.
20. **The product is unimplemented.** The PoC is a log reader; the hook + signature + verifier pipeline that §4 and §8 sell has zero measurements. Before release: implement the PostToolUse hook, run a week of real work, report the layer-1 flag precision that point 9 demands.

## (e) Ethics and regulatory framing

21. **Article 50 is overclaimed.** Cite 50(2) specifically, and note its second-paragraph exemption (assistive editing, technical feasibility, disproportionate degradation) which plausibly covers code-assist output — so "watermarks everything… to satisfy Article 50" is motive attribution plus a legal overclaim; Art. 50 also binds providers placing systems on the EU market, making "worldwide, no opt-out" a product choice, not a duty. Rewrite as "which the provider says addresses Art. 50."
22. **"A positive result is cryptographic, not stylistic" (layer 2) is false.** Watermark detection is hypothesis testing with nonzero FPR; only the layer-1 signature is cryptographic. Fix.
23. **Surveillance is treated as an open design question (§9) when it's a legal constraint.** Per-machine keys are per-developer identifiers in practice; session IDs + timestamps in a repo ledger are behavioral personal data (GDPR; in Germany, BetrVG §87 co-determination for monitoring systems). Fixes: team-level aggregation by default, pseudonymized session IDs, retention policy, a DPIA note, and acknowledge that publishing `.nhw/attest.jsonl` in public repos discloses line-level AI usage — "zero cost to the first constituency" is not obvious.
24. The no-humaniser/no-removal rule is good; add: no per-developer exports, and document the policy hooks so "block" can't silently become an individual performance metric. Also consider whether the task name ("NoHumanWrite") and "a human byte… is an exception path" rhetoric help or hurt; "unattested-span detection" says what the system does.

## (f) Factual and citation errors

25. §5.1: 6% should be 12% (point 14). Abstract: "96% of lines (median)" is garbled (point 10). "No detectable tell" → "below threshold" (point 7).
26. Kirchenbauer "negligible quality cost" is contested by follow-ups (degradation on code/reasoning); soften or cite. "A scheme of this family" lumps green-list watermarking with SynthID's tournament sampling — related but distinct; specify. "Reliable detection at a few hundred tokens" — give the figure/table number; the SynthID-Text paper also emphasizes short-text detection in deployment. Liang et al. "above 60%" — pin the detector and figure. C2PA: "no text profile" → "no plain-text or source-code profile" (document/PDF coverage exists). "Every deployed AI-text detector answers one question" — false universal (sentence-level highlighting exists). Ref 14: label "10:14" as duration; the in-text "seven minutes" should match. Ref 13 is otherwise correct (Regulation (EU) 2024/1689; Art. 50 applies from 2 August 2026).

## Blocking fixes before release

Ground-truthed §5.1 with strong-match-only, in-window numbers; correct the 12% error and abstract phrasing; layer-1 precision arithmetic symmetric with §6 plus an ROC-based §6; threat-model section; Art. 50(2) rewrite incl. the exemption; privacy/GDPR paragraph; related work (SLSA/in-toto, micro-commits, mixed-authorship detection); public repo URL, pinned commits, scrubbed data, CIs; one week of hook telemetry for the product claims.

**Verdict: publish after major fixes — the reframing and the negative result are worth keeping, but the PoC overclaims its numbers, the base-rate argument must be applied to your own layer, and the product's threat model is unwritten.**

### H. minimax/minimax-m3
# Hostile review: "NoHumanWrite: finding the human in machine-written work"

## Summary of what the paper claims
The paper proposes inverting AI-text detection: instead of "is this machine-made?", ask "where are the human insertions?" It argues statistical detection cannot do this (base-rate problem), and proposes a three-layer architecture: (1) provenance recorded by the harness at write time, (2) vendor watermarks, (3) statistical triage. A PoC on the author's own machine reports 96% median attestation in agent-written code, 9% in the PoC's own source (written via unlogged shell), and ~8% precision for statistical detection at 5% human share.

---

## (a) Core claim: is "inverted detection" a distinct, useful task?

**The paper conflates three things and never separates them:**
1. *Inverted detection* — find humans inside machine text (the claimed task).
2. *Provenance by construction* — record authorship at write time (what Layer 1 actually does).
3. *Attestation-gap analysis* — find unattested spans (what the PoC measures).

The PoC does **not** perform inverted detection. It reads logs. The statistical layer attempts inverted detection and the paper itself shows it fails (8% precision). So the paper is actually arguing for a logging system, not a detection system. The "inversion" framing is rhetorical and misleading; it makes the contribution sound like a new ML task when it is an infrastructure proposal.

**The central empirical claim is unsupported.** "Human insertions are where the incidents live" is asserted from personal experience with zero data. This is the load-bearing motivation. Without it, the tool is just a provenance recorder, which is useful but not for the reason the paper says.

**The task definition is asymmetric and the paper knows it.** "Human insertion = anything not produced by a logged machine write" means *unattested ≠ human*. The PoC's own source files are unattested but machine-written (shell heredoc). Section 5.1 admits "unattested means human *or untracked*, and on this machine untracked dominates," then the product framing in Section 8 quietly drops the distinction.

**Concrete fixes:**
- Reframe the contribution as "provenance-by-construction for agent-written artefacts." Delete "inverted detection" or move it to a clearly-labeled "negative result" subsection.
- Provide evidence for the incidents claim: cite bug-postmortem studies (e.g., NASA's flight-software defect studies, the Linux kernel's human-vs-patch defect rates), or measure it on ≥3 external codebases. If you cannot, weaken the claim to "human insertions bypass the agent's logged pipeline and therefore deserve explicit review," which is defensible without data.
- Replace "human insertion" with "unattested span" throughout Sections 3, 7, and 8. Add a one-sentence caveat in the Abstract.

---

## (b) Base-rate arithmetic

**The arithmetic is correct.** I re-ran it: 0.993 × 0.05 / (0.993 × 0.05 + 0.60 × 0.95) = 0.0801. The 34% figure at FPR=0.10 also checks out.

**But the inputs are weak and the framing is selective:**

1. **Base rate (5% human share) is asserted, not measured.** "A generous figure for an agent-first team" is not evidence. Measure it on the vault tools corpus you already have (you have line-level attestation; you can estimate the human share by looking at unattested lines in files you know are agent-written).

2. **Sensitivity (0.993) and FPR (0.60) are measured on the wrong distribution.** The labeled prose is chat-register (developer instructions to agent, agent responses). The actual task is finding insertions inside code, config, and mixed documents — a completely different token distribution, length distribution, and style distribution. The paper acknowledges this caveat but does not quantify it.

3. **Threshold (20) is cherry-picked to make detection look bad.** AUC = 0.912 is actually a strong result. At a lower threshold, more machine passages are caught but more human passages are also flagged. Show the full precision-recall curve and pick the operating point that matches the cost asymmetry you describe (false-machine is cheap, false-human is expensive). The paper currently picks one threshold and declares the task impossible.

4. **The base-rate argument proves statistical detection is bad, but it is not evidence for Layer 1.** Layer 1's effectiveness depends on log coverage, which the PoC itself shows is incomplete. The paper uses the base-rate argument to motivate Layer 1, but the two are logically independent.

**Concrete fixes:**
- Measure the 5% figure or cite a source. If you cannot, run a sensitivity analysis over 1%, 5%, 20%, 50%.
- Replace the single-threshold number with a precision-recall curve and mark the operating point you would actually deploy.
- Add a paragraph separating "why Layer 3 fails" from "why Layer 1 is needed." They are different arguments.

---

## (c) PoC methodology and whether the 96% / 9% / 8% numbers support the conclusions

**The 96% number hides a 28-point gap.** Median attested in vault tools is 96%, but line-weighted attestation is 68%. That gap means a small number of files have very low attestation and drag the weighted mean down. The paper reports only the median and waves at the distribution. The bimodality claim is asserted without a histogram or a test.

**The 9% number is a stunt, not a measurement.** The PoC's own source files were written by the agent in the same session as the paper, through a shell heredoc, with full knowledge that logging was on. This demonstrates that *deliberate bypass* defeats log forensics, which is a stronger and more honest claim than "log forensics cannot catch everything." But the paper frames it as a natural failure mode, which is misleading. Also: the 9% is "all weak matches on generic import lines" — i.e., coincidental matching of `import os` patterns, not real attestation. Report this as 0% strong matches.

**The 8% number is a calculation, not a measurement.** Label it as such in the text and in any table.

**Methodology problems:**
1. **One machine, one developer, one model family.** No external validation. This is a case study, not a benchmark. Say so.
2. **Sample size 150/150** for the statistical evaluation is small and from one writer/model pair.
3. **sloptrim 0.9.0** is not described. What are the 71 patterns? How was it calibrated? Is it a real tool or fabricated for this paper? (See (f).)
4. **Line-attribution by hash of whitespace-normalized content** is fragile: formatters, refactors, variable renames, and whitespace changes all break matches. The paper acknowledges this in Section 9 but does not quantify the breakage rate. Run a controlled experiment: take 10 agent-written files, run `black`/`prettier`/`gofmt` on them, and measure how many lines still match.
5. **The 12-character threshold** is arbitrary and unvalidated. Why 12? Why not 8 or 20?
6. **The PoC does not demonstrate inverted detection.** It demonstrates log reading. The statistical layer is tested on chat prose, not on finding insertions in mixed documents.

**Concrete fixes:**
- Report mean, median, and a histogram for every corpus. Add a dip test or Hartigan's dip test for bimodality.
- Verify the 4% gap from 100% in vault tools by manually sampling 50 "unattested" lines and classifying them (human edit, formatter, refactor, other).
- Run the PoC on at least one external codebase (with consent). Report whether the 96% / 9% pattern holds.
- Describe sloptrim in an appendix or cite a real detector (e.g., GLTR, Fast-DetectGPT, Binoculars).
- Quantify the formatter/refactor breakage rate.
- Justify or remove the 12-character rule.
- Either run the statistical layer on the actual task (mixed documents with known insertions) or drop the claim that it addresses inverted detection.

---

## (d) Three-layer architecture and signed-ledger product

**Layer 1 fails in the paper's own example.** The PoC's source files bypass the hook via shell heredoc. The paper says "only a record emitted by every writing channel at write time can" close this gap, but does not specify *which* channel. Options: file-system fanotify/BPF hook, git-index hook (pre-commit), IDE plugin, OS-level audit. Each has gaps (fanotify misses in-memory writes; git-index misses unstaged work; IDE plugin misses terminal edits). The paper needs to pick a choke point and defend it.

**Layer 2 is vaporware for the paper's primary vendor.** Claude's detection endpoint does not exist as of the paper's claims. SynthID-Text is prose-only and does not cover code (the paper admits this in Section 9). The ledger "leaves a slot" for watermark results, but the slot is unspecified. What goes in it when the endpoint ships? A boolean? A confidence score? A token range?

**Layer 3 should not be in the design.** The paper shows it has 8% precision at 5% prevalence. It then says the layer "orders a reviewer's attention" and "never produces a label on its own." These are inconsistent: if it flags spans for review, it is producing a label. If it does not produce a label, it is not ordering attention. Either remove Layer 3 or present it as a negative result with a clear "do not deploy" warning.

**Signed ledger — threat model is missing:**
- The ledger lives in the repository. A compromised developer account can forge entries. The signature is from "a key on the developer's machine" — what protects this key? If it is on the same machine that runs the agent, a compromised agent can sign its own writes (the entire harness is the trust anchor; if the harness is compromised, the ledger is too).
- The ledger records model and session but not the prompt. This limits reproducibility and forensic value.
- "Append-only" is asserted but not enforced. Git history can be rewritten. Who watches the watchers?
- The GitHub App framing assumes the team controls the harness. For open-source projects with external contributors, the contributor's harness is not under the maintainer's control. What happens then?

**Concrete fixes:**
- Specify the file-system or git choke point for Layer 1 and defend it against the shell-heredoc failure mode.
- Specify the ledger schema for watermark results (Section 4 says "format in SPEC.md" but SPEC.md is not included).
- Remove Layer 3 or move it to a "future work / negative result" section with an explicit warning.
- Add a threat-model section: compromised developer, compromised agent, malicious contributor, coerced key disclosure. For each, specify what the ledger does and does not prove.
- Address key management: TPM, cloud KMS, or at minimum a passphrase-protected key with a documented rotation policy.
- Address the open-source contribution case: how does an external contributor's agent attest?

---

## (e) Ethics and regulatory framing

**Article 50 is mischaracterized.** Article 50 requires "machine-readable marking" that is "appropriate to the relevant context" — it does not require watermarks specifically. Watermarks are one implementation; metadata manifests (C2PA-style) are another. The paper says the regime "assumes a public that wants to know what the machine wrote in order to discount it." This is a misreading. Article 50 is about transparency for informed decision-making, not specifically discounting. The paper builds its "second constituency" argument on a strawman.

**Applicability date needs verification.** Article 50 has different applicability dates for different provider categories. The blanket "applicable from 2 August 2026" is likely wrong for at least some categories. Check the actual regulation text.

**Dual-use risk is hand-waved.** The paper says the tool "never removes a mark" and "never asserts that a person's work is machine-made." True for the shipped tool. But:
- The ledger format and verification code are open source. Anyone can build a "find all machine-written spans" tool on top.
- The attestation gap *is* a machine-written-span detector: anything not in the ledger is either human or untracked-machine, and an adversary who controls the harness can ensure all their output is untracked.
- The "no humaniser, no rewrite mode, no removal mode" is a design choice for *this* tool, not a property of the approach. State this explicitly.

**The video [14] is dismissed rather than engaged with.** The paper says the video "treats the watermark as a threat and offers a laundering recipe." Even if the video is real, it presumably makes a substantive argument about the costs of mandatory watermarking (latency, quality, opt-out for accessibility). Engage with that argument. If watermarking has costs, the paper should acknowledge them and explain why the benefits of NoHumanWrite outweigh them.

**Concrete fixes:**
- Correct the Article 50 description. Quote the actual text.
- Verify the applicability date against the regulation.
- Add a "dual-use considerations" subsection: what stops this from becoming a watermark-removal aid? Answer: the tool flags unattested spans for review, it does not output a cleaned file. State this as a design constraint and explain why it is enforceable.
- Engage with [14]'s argument, don't just characterize its tone.

---

## (f) Factual and citation errors

1. **[2] Dathathri et al., Nature, doi:10.1038/s41586-024-08025-4.** The DOI is plausible but unverifiable from my training data. The SynthID Nature paper exists; the exact DOI and author list need confirmation against the published version.

2. **[13] EU AI Act Article 50, applicable from 2 August 2026.** Article 50 has provider-category-specific dates. The blanket statement is almost certainly wrong for at least one category. Verify against the Official Journal text.

3. **[14] "Fable 5.1 Watermarks EVERYTHING" video, ID slePq-H-TMA.** This appears to be a fictional product and video. YouTube ID format is plausible but the product name "Fable 5.1" does not match any known model family as of my knowledge cutoff. If this is fabricated, the paper is citing a non-existent source to anchor a real argument. Replace with a real video or remove.

4. **[15] sloptrim 0.9.0, "71 documented AI-writing patterns."** This appears to be a fictional detector. No citation, no description, no repository link. If it was created for this paper, describe it in an appendix and release the code under the promised Apache-2.0 license *before* submission. If it is a real tool, cite it properly.

5. **[12] Anthropic Help Center article 16266773, "watermarks all text worldwide with no opt-out."** The specific article ID is unverifiable. The policy claim is strong and would be a major announcement; it needs a reliable source (press release, policy page, regulatory filing). As written, it reads as speculation presented as fact.

6. **Claude Code post-write hook.** Claude Code does have hooks (as of my knowledge cutoff), but the specific claim that a hook fires after *every* write tool and exposes the exact bytes needs verification against current Claude Code documentation. Hook APIs change.

**Concrete fixes:**
- Verify every DOI and URL. Add access dates.
- Replace [14] with a real source or delete the reference and the paragraph that depends on it.
- If sloptrim is real, cite it. If it is fabricated, describe it in an appendix and release the code.
- If the Anthropic watermark policy claim cannot be sourced to an official Anthropic document, weaken the language to "Anthropic has announced…" and cite the announcement.
- Verify the Claude Code hook claim against current documentation.

---

## Additional issues

1. **Research contribution vs. product pitch.** Sections 5 (PoC) and 8 (product) blur the line between research and business plan. "The business plan, pricing and 30-day build sit in `business.md`" is not appropriate for a research paper. Move the product framing to a separate document or a clearly-labeled "Discussion" subsection.

2. **"In our experience" is not evidence.** The paper repeatedly uses personal experience to support claims. This is anecdote. Either measure or cite.

3. **No adversarial analysis.** What if an agent is prompted to evade the hook? What if a developer deliberately uses unlogged channels? What if a compromised CI runner forges ledger entries? The paper does not address these.

4. **No multi-agent analysis.** What if multiple agents write to the same file concurrently? What if agents edit each other's output? The ledger schema does not specify.

5. **The "human insertions are where incidents live" claim is the load-bearing motivation and is unsupported.** See (a).

---

## Concrete fix list (prioritized)

1. Reframe: drop "inverted detection" or move to negative results. Replace "human insertion" with "unattested span" in product framing.
2. Verify all citations; remove or replace fictional sources ([14], [15] if fabricated).
3. Add external validation: run the PoC on ≥1 external codebase.
4. Report mean/median/distribution for every corpus; add a PR curve for the statistical layer.
5. Specify the Layer 1 choke point that survives shell heredocs.
6. Specify the ledger schema for watermark results.
7. Remove Layer 3 or move to negative results.
8. Add a threat-model section.
9. Correct the Article 50 description and verify the applicability date.
10. Add a dual-use risk subsection.
11. Separate the research contribution from the product pitch.

---

## Verdict

**Publish after fixes.** The core idea — provenance should be recorded at write time, not inferred after — is sound and the base-rate argument against statistical detection is correct. But the paper as written has a misleading framing, weak empirical support (one machine, small samples, possibly fictional tools), unresolved architectural gaps (the shell-heredoc failure mode is in the paper's own data), and citation issues that will trigger a desk reject at a serious venue. The fixes above are substantial but mechanical; none requires new research.

## Round 2 — cross-check (each critiques the anonymised pool)

### openai/gpt-5.6-luna-pro reviews
## Comparative review of the answers

### Strongest: Answer A

Answer A is the strongest overall because it is the most disciplined about separating:

- human authorship from non-attestation;
- passage-level detector statistics from line/span-level deployment;
- cryptographic signatures from statistical watermarks;
- a feasibility observation from a validated evaluation;
- provenance coverage from authorship proof.

It also catches the concrete table error: the wiki’s 20–80% middle is \(35/285 \approx 12.3\%\), not 6%. Its proposed reframing—“write-channel provenance” or “localization of unattested changes”—is the correct center of gravity.

Answer C is nearly as strong and is more detailed on statistical uncertainty and reproducibility, but it contains a likely citation error of its own: it says DetectGPT is commonly arXiv:2201.11629, whereas the cited DetectGPT paper is generally identified as arXiv:2301.11305, the identifier used in the draft. That weakens C’s factual-reliability section. C also occasionally treats proposed additional experiments as if they were necessary for any public release, rather than distinguishing a publishable feasibility/position paper from a validated systems evaluation.

Answer D is strong on the median-versus-weighted discrepancy, the 22 low-attestation files, alert fatigue, and the distinction between transcript parsing and actual write interception. However, it makes several claims that require verification, especially that the shell heredoc contents are fully present in Claude Code transcripts and the legal subsection details.

Answer G is useful but overstates some points. In particular, its claim that the 0.993 sensitivity / 0.10 machine false-positive counterfactual is “forbidden” by the displayed quantiles is only valid if the paper intends it as an operating point on that exact score distribution. The paper presents it as a hypothetical improved detector, so the correct criticism is that it is not an achievable point demonstrated by the data, not that the arithmetic itself is invalid.

Answer B is the weakest. It makes unsupported assertions about code entropy and DeepMind warnings, incorrectly treats provider-signed output or a TEE as the required solution, and jumps from the weakness of the current statistical layer to deleting Layer 3 entirely. It also misses several central issues: passage/span unit mismatch, median versus weighted attestation, the table arithmetic error, and the fact that signatures attest a cooperating process rather than prove machine authorship.

Answer E has good structure but contains a substantive likelihood-ratio error. It writes that the relevant ratio is approximately \(0.40/0.60\), but for the “no tell” event the relevant ratio is \(0.993/0.60\). Its citation to an apparently unspecified “Audit/Audit” work is also not acceptable.

## Important issues the answers collectively miss or understate

1. **The paper’s own product has the same base-rate problem in a different form.**  
   Layer 1 does not have a statistical false-positive rate for attested bytes, but its operational flag is “unattested, therefore review.” The paper explicitly says untracked machine output dominates in some corpora. Therefore the important product metric is not just attestation coverage; it is:

   \[
   P(\text{meaningfully bypassed change}\mid\text{unattested flag})
   \]

   That must be measured or the PR check may produce mostly noise.

2. **The proposed definition makes “human insertion” policy-dependent.**  
   A human can type text into the agent prompt and have the harness write it. Under the paper’s definition, that becomes machine-attested. The system detects a writing channel, not causal human intellectual contribution. This is not merely a caveat; it determines what the product can and cannot claim.

3. **The 9% result is not necessarily evidence that post-hoc logs cannot recover the write.**  
   If the heredoc command and its contents are present in the transcript, the current parser may simply be incomplete. The safer conclusion is: “the Write/Edit extractor misses shell-mediated writes,” not “post-hoc log forensics cannot close the gap.” A genuine filesystem-level experiment is needed before making the stronger claim.

4. **The “96%” headline is especially misleading.**  
   It is a median of per-file percentages, while the line-weighted result is 68%. A third of the tool files are in the 0–20% bin. The abstract must report the weighted value and define whether weak matches count. The current wording makes a corpus-dependent coverage statistic look like system accuracy.

5. **The statistical experiment does not evaluate the proposed task.**  
   Classifying user turns against assistant responses is not locating a human span inserted into a machine-produced file. Even perfect reporting of AUC and confidence intervals would not repair that task mismatch.

6. **The architecture’s trust ordering is not established.**  
   A local signature can be useful for accountability among cooperative participants, but it is not a security boundary against the developer, the harness, a compromised host, or a malicious agent. A vendor watermark is statistical evidence, not cryptographic provenance. These should not be presented as a simple strict hierarchy without a threat model.

7. **There is a serious conflict between “only numbers leave” and the proposed GitHub App.**  
   To highlight hunks, a service needs access to diffs and provenance records, unless verification runs entirely in CI and only an aggregate result is uploaded. The data-flow and privacy claims must be made consistent.

8. **The paper’s regulatory claims need primary-source verification, not just correction of wording.**  
   Article 50 does not generally mandate “watermarking all machine text,” and it does not imply that a vendor must expose a detection endpoint. The paper must distinguish provider marking, deployer disclosure, deepfake rules, public-interest text, exceptions, and applicability dates. Vendor claims dated 2026 need archived primary sources or should be removed.

9. **The citation integrity problem is potentially release-blocking.**  
   “Fable 5.1,” Anthropic’s claimed worldwide/no-opt-out policy, the exact watermark mechanism, C2PA behavior, SynthID open-source scope, and `sloptrim` all need verification. A future-dated or fictional source in a public paper is worse than an omitted source.

## What a correct and safe final answer must include

A good final review should require the paper to:

- Rename the task and product around **unattested spans**, **write-channel provenance**, or **provenance-gap detection**.
- Stop calling non-attestation human authorship.
- Remove or substantiate the claim that human edits are where incidents occur.
- Separate the three statistical units: passage, line/span, and byte/hunk.
- Recompute or qualify the Bayes analysis, report a prevalence sweep, and provide PR curves and confidence intervals.
- State that the 8% figure is an illustrative calculation from one threshold, not measured precision on the deployment task.
- Report 96% as median file coverage only, alongside 68% line-weighted coverage, with strong/weak/ignored-line denominators.
- Treat 9% as evidence of a Write/Edit-hook coverage gap unless shell transcript recovery has been tested.
- Add controlled ground truth for human edits, unlogged agent writes, formatters, generated files, renames, copy/paste, and refactors.
- Define signatures as **write attestations**, not proof of machine authorship.
- Replace “append-only ledger” with a precisely specified tamper-evidence model, including key custody, anchoring, replay, rotation, deletion, and merge handling.
- Correctly describe watermarks as statistical keyed signals, not cryptographic signatures.
- Either remove Layer 3 or make it explicitly optional, non-blocking, uncertainty-labeled triage; deletion is not mandatory if a workload study shows it helps.
- Add related work on SLSA, in-toto, Sigstore/Rekor, Git signed commits, IDE history, filesystem auditing, and provenance standards.
- Add privacy, employment-monitoring, GDPR, retention, access-control, appeal, and management-misuse safeguards.
- Verify or remove all future-dated vendor, video, detector, and regulatory claims.
- Release a fixed public repository, pinned dependencies, reproducibility instructions, sanitized or synthetic data, and an explicit statement of what cannot be released.

## Verdict

**Answer A is strongest; the paper itself should be published only after major fixes, not as is.**

### google/gemini-3.1-pro-preview reviews
**Independent Analysis of the Paper**
*   **(a) Core claim:** The paper conflates "unattested spans" (a provenance gap) with "human insertions" (authorship). A span can be unattested because of a formatter, an unparsed tool, or an older log window. The foundational assumption—that human edits are where incidents live—is asserted without any data. 
*   **(b) Base-rate arithmetic:** The paper commits a severe statistical error. It claims that lowering the FPR to 0.10 yields 34% precision. The math for 34% precision at a 5% base rate requires holding the True Positive Rate (sensitivity) at 0.993. On an ROC curve with an AUC of 0.912, it is mathematically impossible to drop the FPR from 0.60 to 0.10 without a massive drop in sensitivity. 
*   **(c) PoC methodology:** The 9% "unlogged" heredoc result is a parser failure, not a fundamental logging gap. Claude Code’s `Bash` tool logs the exact command executed, meaning the heredoc text *is* in the transcript. The author's PoC explicitly only parses `Write` and `Edit` tools, missing the data. Furthermore, there is a basic arithmetic error in the table analysis: 19 + 16 = 35 files in the 20–80% middle for the wiki. 35 / 285 is 12.3%, not 6%. 
*   **(d) Architecture:** Layer 1 is security theater. A local key signing a local `.nhw/attest.jsonl` file provides zero tamper-evidence against the developer committing the code. Layer 2 falsely describes SynthID and Kirchenbauer watermarks as "cryptographic" (they are statistical). Layer 3 is retained in the architecture despite the paper's own math proving it will cause catastrophic alert fatigue.
*   **(e) Ethics/Regulatory:** The paper ignores severe employee surveillance implications (GDPR and EU works council laws) of tracking line-by-line developer behavior. It also misrepresents the EU AI Act's Article 50, which does not mandate internal enterprise PR blocking.
*   **(f) Factual/Citation errors:** "Fable 5.1" is a fictional or future-dated model. "sloptrim 0.9.0" is an unpublished, unvalidated local script. Relying on a YouTube video for core regulatory/product claims is unacceptable for arXiv cs.SE.

**Strongest Answer**
**Answer D** is the strongest. It identifies the deepest, most fatal technical flaws that other reviewers miss or only partially grasp. Specifically, it is the only answer to realize that Claude Code *does* log Bash tool inputs, exposing the 9% heredoc result as a parser bug rather than a proof that post-hoc forensics are impossible. It also correctly spots the ROC impossibility (holding TPR at 0.993 while dropping FPR to 0.10), catches the 12.3% vs 6% arithmetic error, corrects the "cryptographic" watermark falsehood, and cites the specific German labor law (BetrVG §87) relevant to the surveillance risk. 

*Note:* While Answer D's critique is the most technically astute, its verdict ("Publish after fixes") is too lenient. **Answer F** correctly concludes "Do not publish," which is the only appropriate verdict for a paper relying on a broken parser, impossible statistics, and fictional models.

**What a Correct/Safe Final Answer Must Include**
A hostile senior review must explicitly contain:
1.  **Task Deconstruction:** A demand to rename the task to "unattested span detection," stripping the unearned "finding the human" rhetoric.
2.  **Statistical Takedown:** A call-out of the impossible ROC operating point used to calculate the 34% precision hypothetical.
3.  **Methodological Invalidation:** Proof that the 9% heredoc result is an artifact of a flawed parser (ignoring the `Bash` tool) rather than a fundamental limitation of transcript logs. 
4.  **Arithmetic Correction:** Correction of the 12.3% vs 6% table error, and a call-out that the 96% median hides the fact that 1/3 of the tools (22/63) are 0–20% attested.
5.  **Security & Architecture Reality Check:** A statement that Layer 1 is cryptographically meaningless against the developer, and a correction that text watermarks (Layer 2) are statistical, not cryptographic.
6.  **Citation Purge:** A demand to remove reliance on fictional models ("Fable 5.1"), unpublished local scripts ("sloptrim"), and YouTube tutorials.
7.  **Verdict:** "Do not publish." The empirical results are artifacts of bad parsing, the statistical argument relies on impossible math, and the citations are unverifiable.

### qwen/qwen3.8-max reviews
## Strongest answer

**Answer D is the strongest.** It is the most internally precise, catches the most load-bearing contradictions in the draft, and gives actionable fixes rather than only general scepticism.

Why D is best:

- It correctly identifies that the paper’s real object is **unattested-span coverage**, not “finding the human”.
- It catches the false statement in §1: the human-typed changes *did* leave a record via the six-hour backup commits described later.
- It notices the unexplained hole in the headline corpus: **22 of 63 tool files are in the 0–20% attestation bucket**, while the abstract advertises a 96% median.
- It flags the raw-notes inconsistency: raw notes are presented as hand-written/negative control, yet **25 of 100 raw files are >80% attested**.
- It correctly treats the 9% result not as proof of an unlogged channel but likely as a **parser/coverage artifact**, because Claude Code transcripts may include Bash tool inputs, including heredocs.
- It applies the paper’s own base-rate critique to Layer 1: the product flag “unattested ⇒ review” also has a precision problem, and the paper never measures **P(human | unattested)**.
- It identifies the product-level alarm-fatigue failure: if most unattested spans are untracked machine output, the PR check will reproduce the same noise problem it attributes to Layer 3.
- It correctly says watermarks are **statistical**, not cryptographic.
- It flags the contradiction in “only the numbers leave” when the ledger is in the repository and the GitHub App/CI needs access to diffs and ledger entries.
- It gives concrete regulatory, privacy, and security fixes rather than only objecting.

D is not perfect. It should be augmented with:

- **C’s citation point** that the DetectGPT arXiv ID is likely wrong.
- **G’s legal/privacy detail** on Article 50 exemptions, GDPR, employee monitoring, and works-council risks.
- More careful verification of whether Claude Code actually logs the heredoc bytes in the exact transcript format used by the author.

The next-best answers are **G** and **C**. G is very strong on architecture, threat model, and legal framing but misses the DetectGPT citation error and some internal inconsistencies. C is strong on statistical caution and citations but misses several decisive PoC problems.

---

## Errors, unstated assumptions, risks, and omissions by answer

### Answer A

**Strengths**

- Correctly reframes the task as provenance/unattested-change detection, not human-authorship detection.
- Correctly accepts the base-rate arithmetic but rejects its transfer from passages to spans/lines/bytes.
- Correctly says a local JSONL ledger is not append-only and that a local signature does not prove authorship.
- Correctly says statistical watermarks are not cryptographic proof.
- Correctly demands primary sources for Anthropic/Fable/SynthID/EU AI Act claims.

**Errors and omissions**

- Misses the specific DetectGPT citation problem: the cited arXiv ID `2301.11305` is likely wrong; DetectGPT is commonly arXiv `2201.11629`.
- Misses the direct contradiction between §1, “human-typed changes left no such record”, and §5.2, where backup commits create a record.
- Does not highlight that **22/63 tool files are at 0–20% attestation**, which undermines the 96% headline.
- Does not highlight that **25/100 raw-note files are >80% attested**, which undermines their use as a human negative control.
- Does not note that the 9% heredoc case may be a parser failure rather than a genuinely unlogged write.
- Does not explicitly require the paper to compute the precision of Layer 1’s “unattested” flag, which is the product’s key operational metric.
- Its legal section is cautious but less precise than G/D on Article 50 paragraphs and exemptions.

**Risk if followed alone**

A would produce a much safer review, but it would leave some of the most damaging internal contradictions unaddressed.

---

### Answer B

**Strengths**

- Correctly identifies the perverse incentive: if unattested human edits are penalised, developers may route trivial fixes through the agent to keep metrics clean.
- Correctly says Layer 3 should not be shipped as a decision-making component if its precision is that low.
- Correctly identifies brittleness of whitespace-normalised line hashing.
- Correctly says local developer-key signatures do not solve adversarial attestation.

**Errors and unstated assumptions**

- Assumes the only credible signature source is the **LLM provider API or a TEE**. That is too narrow. A local attestation system can still be useful for cooperative teams if scoped as an audit/convenience mechanism rather than adversarial proof.
- Claims DeepMind “explicitly warns” against using SynthID on structured text/code. That needs a direct citation; it may be a reasonable inference, but it is not established in the answer.
- Says Article 50 is a distraction and proposes SOC2/ISO instead. That is too dismissive. The paper’s regulatory framing needs correction, not replacement with unrelated compliance frameworks.
- Misses most factual/citation issues: DetectGPT ID, Anthropic/Fable verification, table arithmetic, raw-notes inconsistency, 22/63 low-attestation tools, heredoc parser issue.
- Does not address privacy, labour surveillance, or data-release risks.

**Risk if followed alone**

B would make the review sharper on incentives but too narrow, partly speculative, and weak on citations/legal detail.

---

### Answer C

**Strengths**

- Very strong on statistical hygiene: confidence intervals, threshold sweeps, PR curves, prevalence sensitivity, and cost modelling.
- Correctly says the 96/9/8 numbers are not comparable.
- Correctly says the PoC has no ground truth for file-level human/machine authorship.
- Correctly says watermarks are statistical, not cryptographic.
- Correctly demands a threat model and a real ledger specification.
- Explicitly catches the likely **DetectGPT citation error**, which D and G miss.
- Gives a defensible minimum rewrite: reframe as position/feasibility paper unless ground truth is added.

**Errors and omissions**

- Does not explicitly catch the paper’s internal arithmetic error that the 20–80% middle is **12.3% of wiki files**, not 6%.
- Does not emphasise the **22/63 tools in the 0–20% bucket** as a fatal weakness in the 96% headline.
- Does not note the raw-notes inconsistency: 25 raw files are >80% attested.
- Does not note that the 9% heredoc case may be a parser artifact rather than an unlogged channel.
- Does not catch the §1 contradiction about human-typed changes leaving no record.
- Does not explicitly require the paper to compute Layer 1’s flag precision, i.e. **P(human | unattested)**.

**Risk if followed alone**

C would produce a careful and publishable review, but it would miss several concrete internal contradictions that make the draft especially vulnerable.

---

### Answer D

**Strengths**

- Most precise identification of the paper’s internal contradictions.
- Best catch of the §1/§5.2 inconsistency: human changes did leave a record, but it was unattributed.
- Best formulation of the missing alternative: instrument the human channel too, e.g. manual attestation, editor plugin, pre-commit hook.
- Correctly says the 96% headline hides 22 low-attestation tool files and a large median/line-weighted gap.
- Correctly says the raw-notes corpus cannot serve as a human negative control when many raw files are highly attested.
- Correctly says the 9% result is likely a parser coverage problem if Bash tool inputs are in the transcript.
- Correctly says the product inherits the base-rate problem because “unattested” is not the same as “human”.
- Correctly says “only the numbers leave” is not credible without a data-flow specification.
- Correctly says formatter robustness cannot be deferred as an open question because it determines whether Layer 1 survives real use.
- Good legal/ethics points: Article 50 needs exact paragraphs; GDPR/employee monitoring matters; the anonymity claim is weakened by git blame.

**Errors and omissions**

- Misses the DetectGPT citation issue.
- Its statement that Claude Code logs Bash heredocs should be conditioned on verification against the actual transcript schema.
- Its Article 50(4) point is useful but must be stated with exact statutory language; the answer should avoid overclaiming which deployer duties apply to code versus public-interest text.
- Could say more about C2PA and source-code provenance standards.

**Risk if followed alone**

Very low relative to the others, but it should be supplemented with C’s citation corrections and G’s legal/privacy caveats.

---

### Answer E

**Strengths**

- Correctly says the task is not a new detection task but an instance of authorship/provenance auditing.
- Correctly says the PoC’s 9% result is the interesting finding, but only as an anecdote about logging coverage.
- Correctly says the ledger is not append-only without a trust anchor.
- Correctly flags that the Anthropic watermark claims are under-sourced.

**Errors**

- The likelihood-ratio discussion is confused. It says the observed “tell rates” give a ratio of `0.40 / 0.60 ≈ 0.67`, but the relevant quantities depend on whether the positive class is “tell present” or “no tell”. For the paper’s “no tell means human” rule, the relevant ratio is approximately `0.993 / 0.60 ≈ 1.66`, not `0.40 / 0.60`.
- Suggests the tool itself might become an Article 50 provider if its report is machine-generated. That is speculative and not clearly grounded in the paper.
- Misses many concrete errors: wiki 6%/12.3% arithmetic, 22/63 low tools, raw-notes 25 high-attestation files, DetectGPT ID, heredoc parser issue.
- Legal analysis is less precise than D/G.

**Risk if followed alone**

E introduces some conceptual clarity but contains enough analytical imprecision that it would weaken the final review.

---

### Answer F

**Strengths**

- Correctly says the paper is an n=1 engineering diary/product pitch if left as written.
- Strong on the genre error: user prompts vs assistant responses are not the same as human insertions inside machine-written artefacts.
- Correctly says the base-rate calculation is arithmetically right but wrongly applied.
- Correctly says Layer 1 proves channel attestation, not machine authorship.
- Correctly says watermarks are statistical, not cryptographic.
- Good blocking table for factual/citation risks.

**Errors and overstatements**

- Verdict “do not publish” is too categorical given that the core provenance idea is fixable as an experience report/systems paper.
- Misses that the 9% heredoc case may be a parser artifact rather than an unlogged channel.
- Does not catch the wiki 6%/12.3% arithmetic error.
- Does not catch DetectGPT citation issue.
- Says the 12-character rule deletes the `except: pass` class, but that line is around 12 characters and the paper says “shorter than twelve”, so this point is not exactly right.
- Says “All code is Python stdlib. Nothing leaves the machine” conflicts with the GitHub App/numbers claim. That is not necessarily a contradiction; it is a data-flow question.
- Its claim that line-level provenance is already solved by git blame/in-toto/SLSA is too strong. Those are related, but agent-write-level attestation at review time is not identical.

**Risk if followed alone**

F would produce a harsh review with many valid points but would miss some technical nuances and could recommend rejection where major revision is more appropriate.

---

### Answer G

**Strengths**

- Very strong reframing: Layer 1 is logging, not inverted detection; Layers 2–3 answer the original detection question.
- Correctly says the paper needs related work on SLSA, in-toto, sigstore, git trailers, editor history, and mixed-authorship detection.
- Correctly says the 34% hypothetical operating point is not supported by the measured distributions.
- Correctly says the paper must compute Layer 1’s flag precision, not only Layer 3’s precision.
- Correctly says weak matches contaminate attestation numbers and that strong-match-only numbers are needed.
- Correctly says the 9% heredoc result may be a parser artifact if Bash tool inputs are logged.
- Catches the wiki middle-bin arithmetic error: 12%, not 6%.
- Strong threat-model and ledger fixes.
- Strong privacy/labour-surveillance section, including GDPR and works-council risk.

**Errors and omissions**

- Misses the DetectGPT citation issue.
- Does not explicitly catch the §1 contradiction that human-typed changes did leave backup-commit records.
- Does not explicitly flag the raw-notes issue: 25/100 raw files are >80% attested.
- Does not explicitly flag the “only the numbers leave” contradiction.
- Says Claude Code emits git trailers by default; that needs verification and should not be stated as fact without a version/doc citation.
- Its Article 50(2) exemption point is useful but should be phrased cautiously: the exemption may apply, but the review should not assert that code-assist output is exempt without legal text.

**Risk if followed alone**

Low. G would produce a strong final review, but it should be combined with D’s internal-consistency catches and C’s citation corrections.

---

### Answer H

**Strengths**

- Clear separation of inverted detection, provenance logging, and attestation-gap analysis.
- Correctly says the incidents claim is unsupported.
- Correctly says the base-rate inputs are weak and the threshold analysis needs a PR curve.
- Correctly says the 96% median hides a large line-weighted gap.
- Correctly says Layer 2 is vaporware for the primary vendor use case unless a detection endpoint exists.
- Correctly says Layer 3 should be removed or demoted to a negative result.
- Good demand for a threat model.

**Errors and omissions**

- Says Article 50 applicability date is “likely wrong” for at least some categories, but that itself needs verification; the date issue should be resolved by citing the Official Journal, not by speculation.
- Misses the wiki 6%/12.3% arithmetic error.
- Misses DetectGPT citation issue.
- Misses the heredoc parser artifact issue.
- Misses the Layer 1 flag-precision requirement.
- Misses raw-notes high-attestation inconsistency.
- Suggests citing NASA/Linux-kernel defect studies as possible support, but that assumes such literature directly supports the paper’s specific claim.

**Risk if followed alone**

H is usable but less complete and less precise than D/G/C.

---

## Main disagreements among the answers

### 1. Verdict on the paper

- **F** says do not publish.
- **A/G** say publish after major fixes.
- **B/C/D/E/H** say publish after fixes.

The safer verdict is:

> Publish after major fixes; not publishable as currently drafted.

If the author will not reframe the paper, add ground truth, fix the ledger/threat model, and correct the legal claims, then it should not be released. But the core idea is fixable as an experience report, systems paper, or position paper.

---

### 2. Is Layer 3 salvageable?

- **B/F/H** effectively say delete it.
- **A/C/D/G** allow it only as a clearly labelled, non-blocking, negative-result or optional triage signal.

The correct safe position is:

> Layer 3 must not be presented as part of the product or as a reliable signal. It can remain only as a negative result or optional non-blocking ranking signal with explicit uncertainty. It must never produce a label or gate a review decision.

---

### 3. Is the 9% heredoc result an unlogged-channel failure or a parser failure?

- **A/F/H** mostly treat it as an unlogged-channel failure.
- **D/G** say it may be a parser artifact because Bash tool inputs may be logged.

The correct safe position is:

> The author must inspect the actual Claude Code transcripts. If Bash tool inputs contain the heredoc bytes, the 9% result is a parser/coverage failure, not evidence that the write was unlogged. If they do not, the paper must show the exact transcript format and explain the missing channel. Either way, the conclusion must be about channel coverage and parser completeness, not “human insertion”.

---

### 4. Is a local signed ledger useful?

- **B** says local signatures are security theater and demands provider signatures or TEE.
- **A/C/D/G/H** say local signatures are limited but can be useful if scoped correctly.

The correct safe position is:

> A local signed ledger is not adversarial proof against the developer, agent, or compromised host. It can be useful as an audit/coordination mechanism for cooperative teams. If the paper claims tamper evidence or compliance value, it needs a real trust anchor, hash chain, remote witness, or external transparency log. Otherwise it must explicitly scope the ledger to accidental bypass and honest workflows.

---

### 5. How should Article 50 be handled?

- **B** says cut Article 50.
- **D/G** say rewrite with exact paragraphs and deployer/provider distinctions.
- **E/H** flag overclaiming but are less precise.

The correct safe position is:

> Keep Article 50 only if rewritten with exact statutory text, scope, exemptions, actor distinctions, and applicability dates. Do not claim that Anthropic’s worldwide/no-opt-out behaviour is legally required unless directly supported by primary Anthropic sources. Do not claim Article 50 mandates watermarks specifically.

---

### 6. Are watermarks relevant to code?

- **B/D/G/H** correctly doubt applicability to short code hunks.
- The paper treats Layer 2 as future support for the product.

The correct safe position is:

> Layer 2 should be described as prose-only until there is evidence that watermark detection works on short code hunks, refactored code, and deterministic/syntax-constrained generation. The PR-check product is primarily about code, so Layer 2 cannot be load-bearing.

---

## What a correct/safe final answer must include

A correct final review must contain the following concrete points.

---

### 1. Reframe the core task

The paper must stop saying it “finds the human” unless it has human ground truth.

Required replacement:

- Task: **unattested-span detection**, **write-channel provenance**, or **machine-attestation coverage**.
- Labels:
  - `attested-machine-write`
  - `weak-match`
  - `unattested`
  - `untracked-or-pre-window`
- Do not use `human` as the complement of `logged machine write`.

The review must say that unattested spans can be:

- human edits;
- unlogged agent writes;
- shell writes;
- formatter output;
- generated code;
- copied text;
- pre-window files;
- other harnesses;
- deleted or missing logs.

---

### 2. Require evidence for the usefulness claim

The claim “human insertions are where the incidents live” must be either:

- supported by incident data;
- supported by a controlled injection study;
- supported by a retrospective/revert analysis;
- or downgraded to a hypothesis.

The paper must not build the motivation on an unmeasured anecdote.

---

### 3. Fix the base-rate section

The arithmetic is correct, but the review must require:

- explicit definition of positive/negative classes;
- confidence intervals for sensitivity/FPR/precision;
- threshold sweep or PR curve;
- prevalence sweep, not a single invented 5%;
- separation of passage-level, line-level, hunk-level, and byte-level units;
- no claim that “no threshold rescues this” unless supported by full ROC/PR analysis;
- correction of “no detectable tell” to “below the detector threshold”.

Most importantly, the review must require the same base-rate analysis for Layer 1:

> What is P(human | unattested) in the deployment setting?

If most unattested spans are untracked machine output, the product has the same alert-fatigue problem as Layer 3.

---

### 4. Correct the PoC claims

The review must require:

- fix the wiki middle-bin arithmetic: **12.3%**, not 6%;
- explain the 22/63 tool files at 0–20% attestation;
- explain the 25/100 raw-note files at >80% attestation;
- report strong-match-only and weak-match-only results;
- report ignored-line rates for the <12-character rule;
- report median and line/byte-weighted coverage consistently;
- verify whether the heredoc bytes appear in Claude Code transcripts;
- if they do, reframe the 9% result as parser incompleteness;
- if they do not, show the exact missing log evidence;
- add ground truth or synthetic injection experiments;
- test formatters, refactors, renames, moved blocks, copy/paste, shell writes, editor writes, and log deletion.

The abstract must not present 96%, 9%, and 8% as comparable results. They are not.

---

### 5. Fix the architecture and ledger claims

The review must require:

- replace “proves machine authorship exactly” with “records that an instrumented tool emitted these bytes”;
- replace “signed authorship ledger” with “signed write-attestation ledger” unless authorship is independently proven;
- specify key model, key custody, rotation, revocation, signature format, canonicalisation, and replay protection;
- state that a repo-local JSONL file is not append-only against a malicious repo admin;
- either add an external witness/transparency log/hash chain or scope the ledger to cooperative audit;
- consider simpler alternatives: signed micro-commits, git trailers, OS file watchers, IDE local history, SLSA/in-toto attestations;
- specify how formatter runs are re-attested or tolerated;
- specify how weak/boilerplate matches are prevented from contaminating attestation.

The review must also say:

> Watermark detection is statistical, not cryptographic.

Layer 2 must be limited to prose/documentation until code-watermark evidence exists.

Layer 3 must be removed from the product story or labelled as a non-blocking negative result.

---

### 6. Fix the product and ethics framing

The review must require:

- no per-developer unattested-share dashboard by default;
- no use of unattested share for performance management without explicit safeguards;
- human review before adverse action;
- aggregate metrics by default;
- retention limits;
- secret scanning/redaction plan;
- opt-in telemetry;
- appeal process for false unattested flags;
- explicit statement that unattested flags can be caused by missing logs, not human writing.

The paper must also address:

- worker surveillance;
- GDPR/employment monitoring;
- works-council/EU labour law risks;
- false blame through git blame correlation;
- dual-use risk that unattested-span lists could guide watermark laundering or evasion.

The paper should not platform a watermark-removal tutorial beyond a minimal citation if needed.

---

### 7. Fix the EU AI Act section

The review must require:

- quote Article 50 precisely;
- distinguish provider duties from deployer duties;
- distinguish marking, disclosure, and detection;
- identify exemptions, including assistive editing/technical feasibility where relevant;
- state applicability dates exactly;
- remove “worldwide” and “no opt-out” unless supported by primary Anthropic sources;
- remove the claim that Article 50 requires watermarks specifically;
- remove the claim that a detection endpoint is required unless supported.

The paper should say:

> Anthropic’s marking policy, if real, is vendor policy and may be broader than EU legal duties. The paper must not infer legal motive without source text.

---

### 8. Fix factual and citation errors

The final review must require verification/correction of at least:

1. **DetectGPT citation**: `arXiv:2301.11305` is likely wrong; DetectGPT is commonly `arXiv:2201.11629`.
2. **SynthID-Text**: verify Nature DOI, author list, open-source scope, and token-length claims.
3. **Liang et al.**: state the exact statistic and population, e.g. average false-positive rate across specific detectors, not a vague “above 60%”.
4. **Anthropic/Fable 5.1**: verify whether “Fable 5.1” exists; if not, remove or correct. Do not rely on a YouTube video for vendor policy.
5. **Anthropic Help Center**: cite URL, access date, exact quoted language, and distinguish what is stated from what is inferred.
6. **sloptrim**: release the tool, version, commit hash, pattern list, validation, and conflict-of-interest statement, or replace it with a public detector.
7. **C2PA**: qualify “no text profile” as of access date and distinguish media manifests from text/code line-level provenance.
8. **Claude Code hooks/transcripts**: pin version and cite documentation; do not assume transcript completeness.
9. **OpenAI classifier**: cite the actual page and withdrawal note with access date.
10. **RAID/Binoculars/Ghostbuster**: verify titles and arXiv IDs.

The public repo must not contain raw Claude Code transcripts unless thoroughly redacted. Publish synthetic reproducers or sanitised examples.

---

## Recommended final one-line verdict

**Publish after major fixes; not publishable as currently drafted.**

### moonshotai/kimi-k3 reviews
# Meta-review of Answers A–H

## 1. Ground truth I established independently (the yardstick)

Before comparing answers, I verified the checkable claims in the paper:

- **Base-rate arithmetic is correct**: 0.993×0.05/(0.993×0.05+0.60×0.95) = 0.0801; 1% prevalence → 1.6%; FPR 0.10 → 34.3%. The defects are interpretive (passage-level rates applied to span/line prevalence; invented 5%; single threshold; no CIs).
- **The paper contains one internal arithmetic error**: the wiki 20–80% middle is (19+16)/285 = **12.3%**, not 6%. The tools figure (5/63 ≈ 8%) is correct. Row sums otherwise check; 551/667 = 82.6% ✓.
- **96% is a per-file median; line-weighted is 68%**, and 22/63 tool files sit at 0–20% — unexplained in the paper.
- **The "cryptographic watermark" sentence is a factual error**: Kirchenbauer/SynthID detection is a statistical z-test with a PRF key and nonzero FPR.
- **The heredoc claim is wrong as stated**: Claude Code transcripts log Bash tool calls *including the heredoc text*. The bytes were in the log; the extractor only parsed Write/Edit. "Log forensics cannot close this gap" is refuted by the paper's own example; the true claim is about parser/channel coverage.
- **The checkable citations are accurate**: DetectGPT is arXiv:2301.11305 (Jan 2023); Kirchenbauer 2301.10226; Sadasivan 2303.11156; Liang 2304.02819; Binoculars 2401.12070; Ghostbuster 2305.15047; RAID 2405.07940; OpenAI classifier launched 31 Jan 2023, withdrawn 20 Jul 2023; Art. 50 of Regulation (EU) 2024/1689 does apply from 2 Aug 2026. Liang et al. report ~61% *average* FPR across seven detectors. The Anthropic/"Fable 5.1"/sloptrim items are future-dated or unverifiable and demand primary sources or hedging — not confident correction.

## 2. Errors in the answers

- **Answer C fabricates a citation error.** It asserts DetectGPT "is commonly arXiv:2201.11629, originally 2022" and tells the authors to "fix the arXiv ID." The paper's citation is correct; C's correction is invented. In a review whose brief includes citation verification, manufacturing an error is worse than missing one. C also misses the 6%/12.3% arithmetic error entirely. Its Wilson intervals ([0.96, 0.999], [0.52, 0.68]) and minimum-FPR derivation (0.042) are correct and valuable, but the fabrication is disqualifying for top rank.
- **Answer E's likelihood-ratio analysis is muddled.** It computes "the ratio is 0.40/0.60 ≈ 0.67" — that is not a likelihood ratio of anything (the LR for "no tell ⇒ human" is 0.993/0.60 ≈ 1.66). Its claim that the paper "slides between axes" on the FPR is itself confused: the paper is self-consistent with human as the positive class. E also contains a garbled reference ("called *unattested change detection* in Audit/Audit"). Its unique points (the tool's own output may fall under Art. 50; the workflow-conditional usefulness) are genuinely good, but the quantitative section can't be trusted.
- **Answer H makes a false legal correction.** It claims Art. 50's "applicable from 2 August 2026" is "almost certainly wrong for at least one category." The date is correct (Art. 113). H also misses the 12.3% error, the heredoc-in-transcript point, and the "cryptographic" watermark error, and its "the 9% was deliberate bypass" reading is uncharitable — the paper is transparent about the heredoc.
- **Answer G has one directionally wrong sub-claim.** It says that at FPR 10% "the threshold is ≥25 and sensitivity is ≈0." That describes the *machine*-flagging rule. For the paper's human-flagging rule (score < t ⇒ human), FPR 0.10 requires t ≈ 1 (machine p10 = 0), where sensitivity is ≥0.5 (human median = 0). G's conclusion — the 34% operating point is unavailable on the measured ROC — is right; the stated mechanics are backwards. Everything else in G is strong.
- **Answer D slightly overstates one bound.** "Sensitivity 0.993 at FPR 0.10 implies AUC well above 0.99" — the trapezoidal lower bound through (0.10, 0.993) is ≈0.947; a realistic concave ROC would be ~0.98–0.995. The substantive point (incompatible with the measured 0.912; not a threshold adjustment) is correct and stated more cleanly than G's version.
- **Answer F's example is wrong on a technicality.** It says the <12-character filter "already deletes the hotfix class you advertised (`except: pass`)" — `except: pass` is exactly 12 characters, so it survives; the filter deletes shorter lines. The general point stands; the parenthetical doesn't.
- **Answer B's Layer-1 fix is impractical and one factual claim is unverified.** "The signature must come from the LLM provider's API or a TEE" assumes a signing service no provider offers and ignores the local-model case the paper explicitly supports. "DeepMind explicitly warns against [SynthID-Text] use on factual or highly structured text (like code)" is directionally right (entropy limits are documented) but presented as a specific citable warning without a pinpoint. B also misses every checkable arithmetic error.

## 3. Genuine disagreements, and who is right

1. **The meaning of the 9% result.** B, C, E, H accept the paper's framing (an unlogged channel escapes forensics). D and G correctly note the heredoc bytes *were in the transcript* — Bash inputs are logged — so the result shows parser incompleteness, not the impossibility of log forensics. **D/G are right**, and this matters because the paper uses the 9% to argue "only write-time records can close the gap."
2. **Layer 3: delete vs. demote.** B demands deletion ("you cannot order attention with noise"); A, D, G say demote to an optional, abstaining ranker. B identifies a real internal contradiction (§6 argues reviewers will ignore low-precision flags; §4 keeps the layer) but overprescribes — a cheap, clearly-labeled sort key is not "malpractice." The deeper point, made best by **D and G**, is the symmetry nobody else states as cleanly: the *product's own flag* ("unattested ⇒ review") has a precision problem of its own, because on the paper's data most unattested spans are untracked machine output. P(human | unattested) is the paper's most important unmeasured number.
3. **Verdict.** F says "do not publish"; all others say publish after (major) fixes. F's own "what a publishable paper would be" section concedes the work is publishable after rebuilding, so its one-liner overcorrects — unless one reads the 2026 citations as fabricated rather than scenario-future, which F itself hedges. The proportionate verdict is **publish after major fixes**.
4. **Art. 50 framing.** B says cut it entirely (use SOC2/ISO 27001); E says the paper confuses 50(1)/50(2); G adds the assistive-editing exemption; D uniquely adds 50(4) deployer-disclosure as the *stronger* hook for the product. D's is the most legally literate treatment; H's is the only wrong one.
5. **Whether the paper's FPR labeling is confused.** E says yes; A handles it correctly (the convention is unusual but defined; the paper should just define terms). A is right.

## 4. Strongest answer: D

**D is the strongest, with G a close second.** D wins on density of *verified, unique* catches with no fabricated corrections:

- Unique to D: the §1/§5.2 contradiction (human edits *were* recorded — by the backup commits — which is a stronger version of the paper's own argument); the dictated-text confound (STT output is machine-mediated prose in the "human" class); the "only the numbers leave" contradiction (the ledger lives in the repo on GitHub; hunk highlighting needs the diff server-side); Art. 50(4) as the deployer-side hook; the observation that the flag list is itself a humaniser worklist, gutting the "cannot be turned around" claim; the 25/100 raw files >80% attested as either a damning false-positive rate or an unsupported provenance claim; the missing instrument-the-human-channel alternative; burstiness = coefficient of variation.
- D verifies arithmetic instead of asserting (551/667, the CI propagation to ≈[7%, 9%], the 12.3% correction, the 34%-implies-fantasy-operating-point point stated correctly).
- Its single blemish (the AUC lower bound overstated as "well above 0.99") is minor and doesn't affect any recommendation.

**G** has the best engineering content of any answer — signed micro-commits so `git blame` becomes the ledger, an OS-level watcher (eBPF/auditd/FSEvents) as the choke point, JSONL merge conflicts, the missing ledger number for the two end-to-end wiki pages, BetrVG §87 — and shares D's two deepest insights (layer-1 flag precision; heredoc-in-transcript). It loses to D only on the reversed threshold mechanics and slightly less verification density.

**A** is the best "safe" answer: comprehensive, accurate, catches the 12.3% error, but more checklist-like and with fewer of the deep catches (misses the heredoc nuance, the dictation confound, the layer-1 precision symmetry). **C** would rank with A/G but for the fabricated DetectGPT correction. **F** is sharp on threat modeling ("the agent is the CA") but misses the arithmetic error and its verdict contradicts its own analysis. **B** is thin and misses most checkable items despite two good unique points (perverse incentive to route edits through the agent; code-watermark entropy). **E** and **H** each contain a confident error in exactly the kind of claim a hostile review must get right.

## 5. What a correct/safe final answer must include

1. **The semantic correction**: the system detects *unattested spans*, not human insertions; the abstract's "0% in hand-written notes" and the title commit the conflation the paper itself disclaims in §5.1. Rename the task or provide human ground truth.
2. **Base rates**: arithmetic confirmed correct; the failures are unit mismatch (prose passages → code lines/hunks), invented 5% prevalence, single-threshold analysis, and missing uncertainty (Wilson CIs propagate to precision ≈[7%, 9%]; the 34% figure is an operating point the measured ROC forbids).
3. **PoC**: median 96% vs line-weighted 68%; the unexplained 22/63 low-attestation tools; the 6%→12.3% correction; weak-match contamination (the PoC's own 9% is boilerplate collisions); no negative control; the heredoc bytes were in the transcript; sloptrim is an unvalidated self-built instrument; genre (instruction vs. reply) and dictation confounds; no CIs.
4. **Architecture**: layer 1 attests *channel*, not authorship; a repo-local JSONL is not append-only and a dev-held key is no trust anchor (the agent can sign — confused deputy); "a positive watermark is cryptographic" is a factual error; layer 2 is prose-only until code watermarking exists; the product inherits the alarm-fatigue failure used to kill layer 3 — P(human|unattested) must be measured; engage SLSA/in-toto/sigstore, signed micro-commits, and OS-level watchers as alternatives.
5. **Legal/ethics**: quote Art. 50 precisely (50(2) marking, 50(4) deployer disclosure, assistive-editing exemption; the 2 Aug 2026 date is correct — do not "correct" it); the Anthropic worldwide/no-opt-out claims need primary sources; GDPR Art. 88/works-council exposure; `git blame` defeats the "no person's name" safeguard.
6. **Citation discipline**: verify, don't invent — the arXiv IDs are correct; Liang's 61% is an average across seven detectors; sloptrim needs release and validation; the YouTube citation needs a rationale or removal.
7. **Verdict**: publish after major fixes. "Do not publish" is defensible only under a fabrication reading of the 2026 sources and overcorrects given the sound, fixable core.

### deepseek/deepseek-v4-pro-0813 reviews
## Meta-review of the eight answers

The strongest answer is **G**, with **D** close behind. G is the most precise about the paper’s load-bearing errors, avoids most of the factual mistakes other reviews make, and gives a calibrated verdict. F is the most hostile and says “do not publish”; that is defensible if the paper is judged as a research contribution, but it over-punishes a salvageable idea.

---

## Key disagreements among the answers

1. **Verdict**
   - A, B, C, D, E, G, H: publish after fixes.
   - F: do not publish.
   - The split is real but mostly about genre. If this is a cs.SE research paper, F’s “do not publish” is reasonable. If it is a position/experience report with a negative result, G’s “publish after major fixes” is better calibrated.

2. **Core task**
   - All answers agree the paper does not actually perform “inverted AI-text detection.”
   - They differ on how harshly to put it. A, C, D, F, G say the task is really “unattested span detection” or “provenance gap detection.” B and E are softer but still say the framing overclaims.
   - No answer defends the title claim.

3. **Base-rate arithmetic**
   - All answers agree the arithmetic is correct.
   - E makes a specific error: it says the paper’s “lowering the false-positive rate to 0.10” is the *human* test’s FPR = 1 − sensitivity. That is wrong. In the paper’s rule, FPR is P(no tell | machine), and 1 − sensitivity is 0.007, not 0.10.
   - G and D correctly identify the 34% hypothetical as a fictional detector: the measured distributions cannot produce FPR 0.10 while keeping sensitivity 0.993.

4. **PoC numbers**
   - A, C, D, G all catch the table inconsistency: the wiki middle is 12.3%, not 6%.
   - D and G catch the strongest point: the heredoc bytes are in the transcript as Bash tool inputs, so “log forensics cannot close this gap” is false for the very case shown.
   - G adds that the two wiki pages the agent wrote end-to-end are ground truth the transcript index should nail, but the paper never reports the index’s number for them.

5. **Architecture**
   - B is an outlier: it demands signatures from the LLM provider API or a TEE. That is impractical and does not solve local write provenance.
   - G gives the best alternative: signed micro-commits with trailers, or an OS-level watcher, would cover shell, editor, and bot writes better than harness hooks.
   - A, C, D, F, G all agree the local JSONL ledger is not append-only and has no threat model.

6. **Ethics/regulatory**
   - All answers agree Article 50 is overclaimed.
   - G is the most specific: it points to Article 50(2) and the assistive-editing/technical-feasibility exemption, and notes GDPR/BetrVG worker-monitoring issues.
   - D also notes GDPR and the false anonymity of “unattested” because `git blame` re-identifies authors.

---

## Errors in the reviews themselves

- **Answer C** says DetectGPT is “commonly arXiv:2201.11629, originally 2022.” That is wrong. DetectGPT is arXiv:2301.11305, January 2023. This is a factual error in the review.
- **Answer E** mislabels the 0.10 FPR thought experiment as “human test’s FPR = 1 − sensitivity.” As noted above, that is incorrect.
- **Answer B** overstates SynthID-Text limitations: “DeepMind explicitly warns against its use on factual or highly structured text (like code)” is stronger than the paper supports. B’s provider-signature/TEE fix is also not a practical solution for local file provenance.
- **Answer D** says the paper’s claim that human-typed changes left no record is false because backup commits exist. This conflates file-state commits with exact write provenance. The paper’s claim is about exact bytes, session, and timestamp; backup commits do not provide that. D’s point is partly right but overstated.
- **Answer F** says “do not publish.” That is defensible, but it risks discarding the salvageable core: provenance-by-construction beats post-hoc statistical detection, and the 9% self-attestation is a useful negative result.
- **Answer A** correctly says the 34% hypothetical implies a fantasy detector, but it does not tie this to the measured score distributions as G does.

---

## Why G is strongest

G catches the most load-bearing problems and states them precisely:

- The heredoc bytes are in the transcript; the 9% result is a parser artifact, not proof that log forensics cannot close the gap.
- The 6% wiki-middle figure is arithmetically wrong; it is 12.3%.
- Weak matches contaminate every attestation number, including the 9%.
- The paper never applies the base-rate argument to its own Layer 1 flag: P(human | unattested) is the product’s real precision, and the paper’s own data says untracked dominates.
- The 34% hypothetical is impossible from the measured distributions.
- The ledger has no threat model, and simpler alternatives—signed micro-commits, OS-level watchers—are not addressed.
- Article 50(2) has an assistive-editing/technical-feasibility exemption that plausibly covers code-assist output, so the “worldwide watermark to satisfy Article 50” claim is both motive attribution and legal overclaim.
- GDPR/BetrVG worker-monitoring issues are not optional open questions.
- Release hygiene: `~/nohumanwrite` is not a public artifact; sloptrim must be pinned; raw transcripts must not be published.

D is also strong, especially on the product inheriting the base-rate failure and on the “only the numbers leave” contradiction. But G is more complete and more precise on the legal and provenance points.

---

## What a correct/safe final answer must include

A safe final review must require at least these fixes before any public release:

1. **Reframe the task**
   - Replace “human insertion detection” with “unattested span detection” or “write-channel provenance.”
   - State plainly that unattested ≠ human; it includes unlogged agents, shell writes, formatters, pre-window files, and other harnesses.

2. **Correct the arithmetic and abstract**
   - Fix the wiki middle from 6% to 12.3%.
   - Remove or heavily qualify the 96% / 9% / 8% headline numbers.
   - Report strong-match-only, in-window, line-weighted and median attestation.
   - Explain the 22/63 tool files in the 0–20% bucket.

3. **Fix the heredoc claim**
   - Acknowledge that Bash tool inputs are in the transcript, so the 9% result is a parser limitation, not proof that log forensics cannot close the gap.
   - Either parse Bash writes or demonstrate a genuinely unlogged channel.

4. **Apply base rates to Layer 1**
   - Compute P(human | unattested) on labeled data.
   - Show that the product does not reproduce the same alert-fatigue failure it uses to dismiss Layer 3.

5. **Replace the 34% hypothetical**
   - Report a measured ROC/PR curve with confidence intervals.
   - Do not claim “no threshold rescues this” from one threshold and one detector.

6. **Add a threat model**
   - Define the adversary: accidental bypass, lazy developer, malicious developer, compromised agent, compromised host.
   - Specify key management, append-only enforcement, and what the ledger does and does not prove.
   - Address simpler alternatives: signed micro-commits, OS-level watchers, git trailers.

7. **Fix legal and ethics claims**
   - Quote Article 50(2) and its exemptions.
   - Remove or heavily qualify unverified Anthropic/Fable 5.1/worldwide watermark claims.
   - Add GDPR/worker-monitoring analysis; prohibit per-developer dashboards by default.

8. **Release hygiene**
   - Publish a real repo URL, pinned sloptrim commit, sanitized data, and no raw transcripts.
   - Separate the research contribution from `business.md` and the GitHub App pitch.

**Final verdict:** publish after major fixes, not as is.

### x-ai/grok-4.6 reviews
## Independent findings (the paper, not the reviews)

**Task identity.** The paper defines a “human insertion” as any span not produced by a logged machine write. That is **unattested / uninstrumented change**, not human authorship. The PoC’s own 9% row, the wiki/raw corpora, and the text (“unattested means human *or untracked*”) already prove the collapse. Title, abstract, and product copy still say “finding the human.” That is a definitional error, not a framing preference.

**Arithmetic that is actually wrong in the manuscript.** Wiki 20–80% bin is \(19+16=35/285 \approx 12.3\%\), not “6%.” Tools middle \(5/63 \approx 8\%\) is fine. Abstract “96% of lines (median)” is a per-file median; line-weighted tools coverage is **68%**, and **22/63 tools are in 0–20%**. Those 22 files are unexplained (log window, other channel, formatter, matcher). Headline 96% is the high mode, not a result.

**Base-rate algebra vs application.**  
\(0.993\times0.05/(0.993\times0.05+0.60\times0.95)\approx 0.080\) is correct; 1% and FPR=0.10 variants are correct. What is not: (i) 5% prevalence is invented; (ii) rates are 40–300-word **chat** passages, product is **lines/hunks of code**; (iii) “60% carry no detectable tell” means **score &lt; 20**; (iv) “no threshold rescues this” needs a PR curve, not one threshold; (v) Layer 1 flags (“unattested ⇒ review”) have the **same** precision problem until \(P(\text{human}\mid\text{unattested})\) is measured—on this machine untracked dominates.

**PoC does not measure the claimed task.** 96% is coverage of a Write/Edit indexer against the same logs. 9% is three files via shell heredoc (and Bash inputs are often **in** the transcript; a parser miss is not a theorem that forensics cannot close the gap). 8% is a hypothetical on sloptrim, not mixed-document span detection. sloptrim is unpublished; n=1 writer/model/machine; no file-span ground truth; weak path-hashes on boilerplate; lines &lt;12 chars dropped (exactly the `except: pass` class); no CIs.

**Ledger.** Repo JSONL is not append-only. A key on the developer machine signs a *claim*, not machine authorship (human can drive Write; agent can sign `attest.jsonl`; formatters break hashes). Watermark hits are **statistical**, not cryptographic.

**Release hazards.** Future-dated vendor facts (worldwide no-opt-out Anthropic watermark, “Fable 5.1”, Help Center as primary law), a YouTube laundering video, unpublished detector, `~/nohumanwrite`, likely secret-bearing transcripts, and a PR metric that is a workforce-monitoring artifact (GDPR / co-determination / `git blame` deanonymizes “unattested”).

---

## Errors and overreach **in the answers**

| Issue | Who | What’s wrong |
|---|---|---|
| DetectGPT arXiv `2301.11305` is “wrong; use `2201.11629`” | **C** | DetectGPT is Mitchell et al., **arXiv:2301.11305**. C invents a citation “fix.” |
| Paper “slides” FPR from \(P(N\mid M)\) to \(1-\text{sensitivity}\) | **E** | §6 lowers **machine** no-tell rate 0.60→0.10. E’s LR \(0.40/0.60\) is the wrong event. |
| “DeepMind explicitly warns against SynthID on code” | **B** | Not established from the paper’s citations; treat as unverified. |
| Provider-API / TEE signatures as the only honest Layer 1 | **B** | Reasonable product opinion, not a necessary research fix; ignores in-toto/SLSA/Rekor/gitsign. |
| Delete Layer 3 entirely | **B** | Coherent as engineering; the paper can keep it as a **negative result** with a do-not-label warning. |
| “Do not publish” as the only responsible verdict | **F** | Defensible **if** Fable/sloptrim/Anthropic claims stay unsourced; overkill if the draft is cut to an n=1 experience report with those claims removed. |
| NASA flight-software / kernel defect cites as required motivation | **H** | Wrong literature; SE needs unreviewed-change / hotfix / supply-chain evidence, not aerospace folklore. |
| Art. 50 “almost certainly” not 2 Aug 2026 | **H** | Overconfident; the Act’s transparency timetable is real but **scoped**. Quote paragraphs; don’t guess phasing. |
| 9% proves “only write-time hooks work” | A, C, E, F, H (to varying degrees) | **D/G are right:** heredoc bytes may already be in Bash logs; the honest claim is incomplete **parser/channel coverage**, so the choke point must sit at FS/git-index, not “forensics is impossible.” |

**Unstated assumptions (shared).** Most reviews assume 2026 Anthropic/EU facts are checkable from the bibliography; they are not. Most assume “publish after fixes” is safe for **public repo + Apache**; that is only true after transcript redaction, dual-use handling of [14], and dropping unverifiable product claims.

**Disagreements that matter.**  
(1) Verdict: F vs everyone else.  
(2) Is the contribution a new ML task (paper) vs write-channel provenance (A,C,D,G,H) vs not a research problem (F).  
(3) Layer 3: delete (B) vs demote (majority).  
(4) Trust: local signatures OK if scoped to accidents (E,G) vs theater (A,B,D,F).  
(5) Art. 50: cut (B), quote+exemption (G), complementary internal provenance (A,C,F).

---

## Strongest answer

**A is the strongest overall** (full six-axis attack, correct Bayes, correct unattested≠human, ledger threat model, Art. 50 overclaim, reproducibility, concrete revision list).  

**D is the sharpest on the empirical core** (22-file hole, median vs weighted, 9% as parser/coverage not metaphysics, “cryptographic” watermark error, alarm fatigue of unattested flags, Git trailers/micro-commits as the baseline A underplays).  

Use **A as the spine, D’s §5/§6 corrections as mandatory patches.** C is almost as complete but **do not take its DetectGPT “fix.”** G is the best on applying base-rate logic to Layer 1 and Art. 50(2) exemptions. F is the right **release bar** for unsourced 2026 vendor claims. B and E are useful on incentives/trust theater but statistically or legally sloppy. H is a decent checklist with several overconfident legal/citation guesses.

---

## What a correct/safe **final** review must include

1. **Rename the object:** attested vs unattested spans; residual class {human, unlogged agent, formatter, other harness, pre-window, copy/paste}. Do not ship “finding the human” without span-level human labels.  
2. **Fix manuscript errors:** wiki 6%→12%; abstract 96% vs 68% weighted and 22/63 low files; “no tell”→below threshold; watermarks ≠ cryptographic; JSONL ≠ append-only.  
3. **Separate three numbers:** coverage case study ≠ n=1 bypass ≠ Bayes illustration. No 96/9/8 in the abstract as one result.  
4. **Evaluation bar:** controlled mixed-provenance injection (editor, shell, formatter, rename); strong vs weak match P/R; CIs; hunk-level PR curves; measure \(P(\text{human}\mid\text{unattested})\) on labelled diffs. sloptrim cannot be “best local detector” until public+validated (or replace with Binoculars/Fast-DetectGPT).  
5. **Threat model:** local key, agent as confused deputy, rebase, boilerplate collisions, open-source contributors. Attestation = “this tool claimed these bytes,” not authorship. Compare SLSA/in-toto/sigstore/git trailers; justify JSONL or drop it.  
6. **Law/ethics without advocacy:** quote Art. 50 scope/exemptions; hedge Anthropic unless primary archived source; GDPR/employee monitoring; no per-developer scoreboards; dual-use of unattested lists; **do not cite a laundering recipe as technical authority**; do not publish raw transcripts.  
7. **Genre:** experience/position paper or systems paper—not an ML inversion result. Strip `business.md` / design partners from the preprint.  
8. **Verdict line (accurate):** **do not publish as is.** **Publish after major fixes** only if citations are verified or removed, the task is renamed, numbers are relabelled as n=1 coverage, and the repo is redacted. If Fable 5.1 / worldwide watermark / sloptrim remain load-bearing and unverifiable, **do not publish.**

### z-ai/glm-5.3 reviews
# Meta-review of the eight answers

## I. Errors, false claims, and risks in the individual answers

**Answer A** — No outright factual errors, but it misses several load-bearing, checkable items: the abstract's "96% of lines (median)" conflation (median of per-file shares vs. 68% line-weighted), the 22/63 tools files sitting at 0–20% attestation, the heredoc-bytes-were-in-the-transcript point, the layer‑1 flag-precision problem, the missing negative control (25/100 "hand-written" raw notes are >80% attested — a self-contradiction in the paper), and the 34% fantasy operating point. Its fixes are frequently category-level ("report CIs," "test all channels") rather than paper-specific. Its mild claim that C2PA is "not necessarily restricted to media" is contestable.

**Answer B** — Misses the single most important conceptual flaw entirely (unattested ≠ human; B never mentions the definitional collapse), plus the 6%→12% arithmetic error, the "cryptographic" watermark error, the 96/68 gap, surveillance/GDPR, and data-release hygiene. It contains one fabricated-precision claim: DeepMind does not "explicitly warn against" SynthID use on code; the entropy limitation is real, the warning is invented. Its fix "the signature must come from the LLM provider's API" is under-analyzed — a provider attests a response payload, not a file write, and it covers nothing local. Its two genuinely good points (the perverse incentive to route manual fixes through the agent to protect the metric; "you cannot order attention with noise") do not compensate for the coverage gap.

**Answer C** — Contains the single most damaging error in the set: it "corrects" DetectGPT to arXiv:2201.11629. The paper's citation (arXiv:2301.11305) is **correct**. In a review explicitly tasked with finding citation errors, introducing one is close to disqualifying. C also misses the 6% wiki-middle error (12.3%, not 6%) and the 34% operating-point problem (it asks for an ROC sweep but never notices that TPR 0.993 at FPR 0.10 is unreachable on the measured distributions). Its statistics work is otherwise the best in the set: Wilson intervals for 149/150 and 90/150, and the correct derivation that 50% precision at TPR 0.8 and 5% prevalence requires FPR ≤ 0.042.

**Answer D** — Near-zero false claims. Loose spots: "implies AUC well above 0.99" (one operating point doesn't pin AUC, though the direction is right); the flat assertion that Claude Code logs Bash inputs including heredoc bodies (true of current behavior, but the paper is future-dated — should hedge against the pinned version); the inference that sloptrim is the author's own tool is stated as fact. Coverage gaps: no data-release/PII scrubbing discussion, no multi-writer merge algebra. Otherwise it is the densest collection of correct, paper-specific catches in the set (itemized in §IV).

**Answer E** — Multiple errors: (i) the likelihood-ratio arithmetic is garbled — "0.40 / 0.60 ≈ 0.67" is meaningless; the relevant LR⁺ is 0.993/0.60 ≈ 1.66 (E's ">19 for precision >0.5" threshold is right); (ii) its claim that the 34% paragraph "slides between two axes" misreads the paper — the paper's FPR usage is internally consistent; the correct critique is that the 0.993/0.10 operating point is fictional; (iii) "deployed across Gemini [2] is a citation error" is likely wrong — the Nature paper covers the production deployment; (iv) "the tool itself is an AI system provider under Article 50" is a stretch built on the non-sequitur that "only the numbers leave" implies a model-generated report; (v) "unattested change detection in Audit/Audit" is a garbled reference. Its genuine contributions: the workflow-conditionality point (the tool is only useful where human insertion is exceptional by design), and noting the author has the data to measure the exception rate but never does.

**Answer F** — Hyperbole: the 12-character rule does not "delete" `except: pass` — that line is exactly 12 characters (the rule ignores lines *shorter* than 12) and any indented version exceeds it; the underlying point (short-line exclusion biases the denominator) survives without the overstatement. Its "do not publish" verdict sits awkwardly beside its own final section, which describes a publishable rebuild — i.e., major fixes. Otherwise strong: it catches the 22/63 hole, the agent-as-CA/confused-deputy problem, parallel-session merge conflicts, and states the layer-3 incoherence ("demoted in prose and dominates the measurements") more bluntly than anyone.

**Answer G** — Two errors: (i) the mechanism in its (b) point 6 is backwards — for the rule "no tell ⇒ human," FPR = P(score < t | machine), so FPR 0.10 puts the threshold at machine p10 ≈ 0, not "≥ 25" (machine p90); at that point sensitivity is ≈ P(score = 0 | human) (~50–60%, since human p50 = 0), giving precision ≈ 20%, not the paper's 34% — the conclusion (34% is unreachable) survives, the stated numbers don't; (ii) the "10:14 vs. seven minutes should match" nitpick is not an inconsistency (a 10:14 video can spend seven minutes on one topic). Mildly risky: the C2PA "document/PDF coverage exists" claim. Otherwise it owns several of the best unique catches in the set.

**Answer H** — Errors: (i) "Article 50 has provider-category-specific dates… almost certainly wrong for at least one category" is unsupported — Art. 50 applies from 2 August 2026 (G validates this; the phasing H may be half-remembering — GPAI Aug 2025, certain embedded high-risk Aug 2027 — does not touch Art. 50); (ii) its gloss on the 96/68 gap ("a small number of files… drag the weighted mean down") is internally confused — 22 of 63 files are low-attestation, and a median above the weighted mean means the low files are line-*heavy*, not few; (iii) "threshold 20 is cherry-picked" — 20 is the detector's own default, and lowering it *raises* FPR and lowers flag precision, the opposite of H's implication; (iv) asserting sloptrim and the video "appear to be fictional" overreaches — unverifiable demands verification, not an assertion of nonexistence. Its real contributions: the 9% should be reported as 0% strong matches (the paper itself says it's all weak matches on generic imports), the layer-3 label inconsistency, the choke-point demand, and the dual-use subsection.

## II. Unanimities (all correct)

All eight verify the paper's Bayes arithmetic (8.0% at 5%, ~1.6% at 1%, ~34% at FPR 0.10 — all correct). Seven of eight catch the unattested ≠ human collapse. None says "publish as is."

## III. Key disagreements and adjudications

1. **Verdict (F vs. the other seven).** F's "do not publish" is defensible only as "not this draft," but its own salvage taxonomy concedes the material becomes one of three publishable papers — which is "publish after major fixes" by another name. The paper's core observation (attested spans have no base-rate ceiling; channel coverage, not detection, is the constraint) is sound, and the fix list is finite. **Adjudication: publish after major fixes.**
2. **DetectGPT citation (C alone).** The paper is right (2301.11305). C's "correction" must be rejected.
3. **Art. 50 applicability date (H vs. G).** G is right; the paper's 2 August 2026 date is correct for Art. 50. H's "fix" would introduce an error.
4. **The 34% hypothetical (D/G vs. E).** D/G are right: the paper holds sensitivity at 0.993 while cutting FPR to 0.10 — an operating point the measured distributions cannot reach. E's "axis confusion" reading is a misreading.
5. **The 9% heredoc (D/G vs. H/F/A).** D/G's reading is the sharpest and technically correct: Bash tool inputs (including heredoc bodies) are in the transcript, so "log forensics after the fact cannot close this gap" is false *for the very case the paper exhibits*. The honest claims: Write/Edit parsing is insufficient; shell-write parsing is unreliable in general; the choke point must sit below the shell; and this refutes §7's "completely." H's "deliberate bypass" framing is a weaker version of the same point.
6. **Layer 3's fate (B: delete; H: remove-or-negative-result; D/F/G: demote, measure, never block).** B's absolutism is rhetorically clean but the paper's own use (ordering, never labeling) can survive *only if* flag precision is measured and the layer is optional and non-blocking. The D/G position is the safe one.
7. **"Fictional" vs. "unverified" (H vs. A/C/D/F/G).** The safe review demands archived primary sources for Fable 5.1, the Anthropic watermark paragraph, and sloptrim; it does not assert they don't exist. (The Claude-branding inconsistency of "Fable 5.1" is a legitimate red flag to raise.)

## IV. Strongest answer

**D**, with G a close second and A third.

Why D: (i) the highest density of correct, paper-specific, verifiable catches, including five no other answer has — the false §1 sentence (the six-hour backup commits *are* a record of human-typed changes, and the corrected version is stronger for the argument), the missing negative control plus the raw-notes self-contradiction (abstract "hand-written" vs. §5.1 "the agent wrote most of them" vs. 25/100 files >80% attested), the unconsidered alternative of instrumenting the human channel, the Article 50(4) deployer-duty hook, and the "only the numbers leave" data-flow contradiction; (ii) it shares the two deepest structural critiques with G — the layer‑1 flag-precision problem (the product inherits the exact alert-fatigue failure it used to kill layer 3, because P(human | unattested) is never computed and "untracked dominates" on the paper's own data) and the heredoc-in-transcript falsification; (iii) it is correct precisely where G garbles the central (b) analysis; (iv) it introduces zero false claims, in a set where C, H, and E each introduce at least one; (v) it verifies the paper's *correct* arithmetic (551/667 = 82.6%) rather than only attacking — the calibration marker of a senior reviewer. Its weaknesses are terseness, two unhedged assertions, and two coverage gaps (data-release hygiene; multi-writer merge algebra) — both covered by G.

G contributes what D lacks and the final answer should merge in: the granularity-masking argument (layers 2–3 answer the *old* question at coarse granularity; only layer 1 performs the claimed task, and layer 1 is logging, not detection), the inverted-insider-threat framing, the snapshot-diff attribution design, the micro-commit and OS-watcher alternatives ("two lines of git config get 80% of layer 1"), the Art. 50(2) assistive-editing carve-out, the BetrVG §87 reference, the demand for the transcript-index number on the two end-to-end wiki pages, and the date validation contra H. A contributes the most systematic (a)–(f) structure and the consolidated revision plan.

## V. What a correct/safe final answer must include

1. **Verdict:** publish after major fixes; not as-is.
2. **(a)** Unattested ≠ human, quoting the paper's own definition and §5.1 admission; rename the task (unattested-span detection / provenance coverage); layers 2–3 do not perform the inversion (granularity masking); "no tooling" is false as stated (team-level AI-share dashboards, git trailers, editor local history, SLSA/in-toto exist — narrow to line-level provenance at review time); the "incidents live" premise is n=1 and must be measured or downgraded; the §1 "left no such record" sentence is false (backup commits); address human-channel instrumentation.
3. **(b)** Arithmetic verified (8.0%, 1.6%, 34.4%), then: unit mismatch (40–300-word chat prose → code lines); 5% prevalence unmeasured (estimate from the author's own git+ledger data or sweep 0.1–25%); CIs (Se ∈ [0.96, ~1.0], FPR ∈ [0.52, 0.68], precision ≈ [7%, 9%]); the 34% hypothetical is an unreachable operating point (at FPR 0.10 the threshold sits at machine p10 ≈ 0, sensitivity collapses to ≈P(score=0|human), precision ≈ 20%) — present as a fictional upper bound or replace with a measured sweep; "no detectable tell" → "below threshold 20" (machine p50 = 18); "no threshold rescues this" scoped to this detector and shown via PR curve (observed LR⁺ ≈ 1.66; 50% precision at 5% needs LR⁺ ≥ 19); AUC is the wrong headline at low prevalence; the cost model is asserted, not analyzed.
4. **(c)** "96% of lines (median)" conflates median-of-shares with share-of-lines (68% line-weighted); 22/63 tools files at 0–20% unexplained (likely pre-window; checkable); weak matches contaminate every number (the 9% is 0% strong matches — report strong-only); the 6% wiki-middle figure is wrong ((19+16)/285 = 12.3%); the heredoc bytes were in the transcript — fix the "log forensics" claim and the §7 "completely"; no ground truth or negative control, and the raw-notes corpus self-contradicts; §5.3 confounds (register, dictation, one writer/model, no CIs, no dedup spec, threshold provenance; use hand-written prose as a second human class); sloptrim needs a public artifact, commit hash, and validation, or replacement (Binoculars/Fast-DetectGPT); report the index number for the two wiki pages; label the whole thing an n=1 feasibility case study.
5. **(d)** Local key = no trust anchor (agent-as-CA, developer can sign, repo-local JSONL not append-only under rebase/force-push) — either downgrade to an accountability log or add hash-chaining with external anchoring (Rekor/transparency log/protected branch); "proves machine authorship exactly" → proves channel; "cryptographic, not stylistic" is a category error (statistical hypothesis test, nonzero FPR); layer 2 is prose-only for now (low entropy, short hunks, no endpoint); **compute P(human | unattested) for layer 1's own flag** — the paper's most important missing number; formatter robustness is a design decision, not an open question (run the experiment; prefer snapshot-diff attribution over line hashes); address signed micro-commits, OS-level watchers, human-channel attestation; fix the "only the numbers leave" data flow; parallel-session merge algebra; move business.md out of the paper.
6. **(e)** Article 50 at subsection level: 50(2) provider marking with the assistive-editing carve-out, 50(4) deployer disclosure as the closer hook, applicability 2 August 2026 is correct (cite the Official Journal); delete the "to satisfy Article 50" motive attribution; hedge "worldwide / no opt-out / of this family" without primary sources; flag the unsettled non-public-key-vs-"detectable" question; surveillance analysis (git blame re-identifies flagged hunks, so the no-names rule is cosmetic; GDPR Art. 88 / works councils; team-level aggregation, retention, no per-person dashboards, human review before adverse action); dual-use (the flag list is a laundering worklist; "ships without a humaniser" is the defensible claim, "cannot be turned around" is not); cite the video as attitude evidence only.
7. **(f)** Verification demands (archived primary sources) for Fable 5.1 (Claude-branding inconsistency), the Anthropic watermark paragraph, C2PA version and text-profile qualifier, SynthID token figure, Liang et al. (~61% average across the seven commercial detectors — pin it), Claude Code hook/transcript behavior (pin the version), RAID title, Sadasivan scope (document-level detection ≠ residual-span triage); **explicitly do not "correct" DetectGPT (2301.11305 is right)**; data-release plan (local path, secret/PII scrubbing, synthetic reproducers, pinned commits).

**Verdict: publish after major fixes — the core observation and the 9% natural experiment are worth keeping; the title claim, the garbled abstract numbers, the unverifiable citations, and the missing threat model are not.**

### minimax/minimax-m3 reviews
## Independent assessment of the eight reviews

### Overall landscape

All eight reviews identify the same core problems: the paper conflates *unattested* with *human*, the three headline numbers (96/9/8) are incommensurable, the ledger has no real threat model, the Article 50 framing is overclaimed, and the empirical work is n=1. The reviews differ mainly in tone, depth, and verdict. F is the lone "do not publish"; A and G say "publish after major fixes"; the rest say "publish after fixes."

### Errors and weak claims inside the reviews themselves

1. **A, C, D, G, H all correctly catch the table arithmetic error** (the paper claims "6% of the wiki" in the 20–80% middle; the table gives 19+16 = 35/285 ≈ 12.3%). B and E miss this. F mentions the contradiction but doesn't compute the correct figure.

2. **B's "11 false positives for every 1 true positive"** is loose: at 8% precision, the ratio is 11.5:1, which is fine, but B presents it as if it were a measured quantity rather than a plug-in calculation.

3. **C's Wilson interval for sensitivity** ("roughly [0.96, 0.999]") is reasonable for 149/150, but C then says the FPR 0.60 has interval "[0.52, 0.68]" — that's the interval for 90/150, which is correct. However, C does not propagate these intervals into the precision calculation, which would be the actually useful thing to do.

4. **D claims "22 of 63 tools — a third of the corpus — sit at 0–20% attested."** 22/63 = 34.9%, so "a third" is acceptable rounding. But D then says this is "unexplained variance" without checking the obvious explanation the paper itself gives (pre-log-window files). D is right that the paper doesn't *verify* this, but the explanation is at least plausible.

5. **E says the 34% hypothetical "mislabels the quantity"** — that lowering FPR to 0.10 while keeping sensitivity at 0.993 is incoherent. E is right that this is a fictional operating point, but the paper does flag it as a thought experiment ("far better than anything in the literature under paraphrase"). E's point is valid but slightly overstated.

6. **F's verdict ("do not publish")** is the outlier. F's reasoning is sound but the conclusion is harsher than the evidence warrants — the paper has a real (if narrow) contribution (write-time provenance for agent-mediated repos), and the fixes F demands are mechanical, not fundamental.

7. **G says the 34% hypothetical "forbids that operating point: at FPR 10% the threshold is ≥25 and sensitivity is ≈0."** This is a strong claim. From the paper's table, machine p90 = 25, so a threshold of 25 would catch roughly 10% of machine passages (FPR ≈ 0.10), and human p90 = 8, so almost all human passages would fall below it (sensitivity ≈ 1.0). G's claim is approximately correct but stated too absolutely.

8. **H says the 96% "hides a 28-point gap"** between median (96%) and line-weighted (68%). This is correct and is a useful framing, but H doesn't note that the gap is partly explained by file-size distribution (a few large files with low attestation drag the weighted mean).

### Unstated assumptions across the reviews

1. **All reviews assume the paper is attempting a research contribution**, but §8 explicitly frames it as a product wedge with design partners and a business plan. The reviews don't engage with the possibility that the paper is intentionally a position/feasibility piece.

2. **All reviews assume the 5% human prevalence is wrong**, but none provide an alternative measurement. The paper has the data to estimate this (git history within the log window) and doesn't.

3. **All reviews assume sloptrim is unvalidated**, but the paper cites it as a local detector. The reviews are right that it's under-documented for a research claim, but they don't engage with the possibility that it's a reasonable choice for a proof-of-concept.

4. **All reviews assume the Anthropic watermark claims are unverifiable**, but the paper does cite a help center article with an access date. The reviews are right that a help center article is weak evidence for a major policy claim, but they don't distinguish between "unverifiable" and "weakly sourced."

5. **Most reviews assume the paper should be reframed as provenance research**, but the paper's own framing (inverting detection) is part of its contribution to the discourse, even if technically wrong.

### Risks in the reviews

1. **F is so harsh it may be unfair** to a legitimate engineering contribution. The paper's core observation (write-time provenance beats post-hoc detection) is sound and worth publishing.

2. **Several reviews (A, C, G) recommend "position/feasibility paper" framing** without acknowledging that this would require the authors to substantially rewrite the paper, not just fix it.

3. **B's recommendation to "delete Layer 3 entirely"** is too aggressive. The paper correctly notes that Layer 3 is a triage signal, not a label. B's point that "you cannot order attention with noise" is valid but doesn't account for the possibility that even noisy triage can be useful if the cost of false positives is low.

4. **D's recommendation to "instrument the human channel"** is good but ignores the practical difficulty: editors are diverse, servers don't have editors, and `sed -i` on production is a real workflow.

5. **Several reviews recommend adding threat models, controlled experiments, and multi-developer studies** without acknowledging that these would require months of additional work, not just paper revisions.

### Disagreements among the reviews

1. **Verdict**: F says "do not publish"; A and G say "publish after major fixes"; B, C, D, E, H say "publish after fixes." The majority view is "publish after fixes."

2. **Whether the task is distinct**: A, C, D, E, F, G, H all say no (or "not clearly"); B doesn't address this directly.

3. **Whether the 9% is a good result**: D says it's "the best result in the paper"; E says it's "a great anecdote"; F and G say it's a "parser artifact"; H says it's "a stunt." The disagreement is about whether the 9% demonstrates a fundamental limitation or just an implementation gap.

4. **Whether Layer 3 should be kept**: B says delete it; A, C, F say demote it further; D says it inherits the base-rate failure; H says it should not be in the design. The disagreement is about whether Layer 3 has any value at all.

5. **Whether the ledger is secure**: B says "security theater"; D says "no trust anchor"; E says "not append-only in any meaningful sense"; F, G say similar. The disagreement is about whether the ledger provides any security value at all.

6. **Whether Article 50 is mischaracterized**: A, C, D, E, F, G, H all say yes (to varying degrees); B doesn't address this directly.

### Strongest answer

**Answer A is the strongest overall**, for these reasons:

1. **Most comprehensive**: A addresses all six areas in depth, with concrete fixes for each issue.
2. **Correctly identifies the semantic error**: A is the clearest on the distinction between unattested and human.
3. **Catches the arithmetic error**: A correctly computes 12.3% for the wiki middle.
4. **Addresses the security model**: A provides the most detailed analysis of the ledger's security gaps.
5. **Addresses the regulatory framing**: A correctly notes that Article 50 is overstated and requires primary-source verification.
6. **Clear verdict**: A's "publish after major fixes; not publishable as is" is well-calibrated.

**Answer D is a close second**, with unique strengths:
- Identifies missing prior art (Caliskan-Islam, in-toto/SLSA, sigstore)
- Notes the "that question has no tooling" claim is false
- Has a good point about the product inheriting the base-rate failure

**Answer G is also strong**, with unique insights:
- Notes that layer 1 is not detection
- Notes the 34% hypothetical is a fictional detector
- Notes the weak matches contaminate numbers

### What a correct/safe final answer must include

1. **The semantic error**: The paper defines "human insertion" as "any span not produced by a logged machine write," which is unattested, not human. This must be flagged.

2. **The arithmetic error**: The paper claims "6% of the wiki" in the 20–80% middle; the table gives 35/285 ≈ 12.3%.

3. **The base-rate unit mismatch**: The detector was evaluated on 40–300-word chat passages; the product flags lines/hunks in code. These are not interchangeable.

4. **The 96/9/8 numbers are incommensurable**: 96% is coverage on one corpus; 9% is a single failure case; 8% is a hypothetical precision calculation. They should not be presented as a chain of evidence.

5. **The ledger has no real security design**: A local JSONL file signed by a developer-held key is not append-only and does not protect against a malicious developer or compromised agent.

6. **Article 50 is overstated**: The paper claims Article 50 requires watermarking all machine text; the actual regulation is narrower and has exceptions.

7. **The "cryptographic" watermark claim is wrong**: Statistical watermarks (Kirchenbauer, SynthID-Text) are probabilistic, not cryptographic.

8. **The 9% is a parser artifact, not a fundamental gap**: The shell heredoc bytes are in the transcript; the parser didn't extract them. This demonstrates parser coverage limits, not a fundamental limitation of log forensics.

9. **The task is not distinct**: Write-time provenance, supply-chain attestation, and change-control auditing are existing research areas. The paper must engage with this prior art.

10. **The usefulness claim is unsupported**: "Human insertions are where the incidents live" is asserted from personal experience with no data.

11. **A clear verdict**: Most reviews say "publish after fixes"; F says "do not publish." The majority view is correct — the paper has a real contribution but needs substantial revision.

### Bottom line

The eight reviews are largely in agreement on the major issues. The strongest is A, with D and G as close runners-up. A correct/safe final answer must flag the semantic error (unattested ≠ human), the arithmetic error (6% vs 12%), the base-rate unit mismatch, the incommensurable headline numbers, the ledger's security gaps, the Article 50 overclaim, the "cryptographic" watermark error, the parser-artifact nature of the 9%, the lack of distinctness from existing provenance work, and the unsupported usefulness claim. The verdict should be "publish after fixes" — the paper has a real contribution but needs substantial revision.

---
> Hand to Claude (orchestrator) for synthesis + final-watch, then Arnaud approves.
