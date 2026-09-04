# NoHumanWrite: write-time provenance for agent-written work, and why detection cannot find the human

Arnaud Chrétien · Plus de Fun Agency, Geneva · draft v0.2 (after external review) · 4 September 2026
Code and data: `~/nohumanwrite` (to be published under Apache-2.0). An experience report from one developer's machine, not a controlled study; the numbers are coverage measurements and are labelled as such.

## Abstract

Every deployed AI-text detector answers one question: did a machine write this? For a team that writes with agents all day, the useful question is the complement: which spans did *not* come through the agent pipeline, with its prompt, diff, log and test run? We call those spans unattested. Most of them are human-typed; some are machine output that arrived through a channel nobody logged; the two cannot be told apart after the fact, and this paper does not claim to. It makes three points. First, the statistical methods built for AI-text detection cannot perform the inverted task: on 300 labelled passages from one developer's agent sessions, a local AI-tell detector separates machine from human prose with an AUC of 0.91, yet 60 % of machine passages (95 % CI 52–68 %) carry no tell, so a "no tell means human" rule has a precision of 7–9 % at a 5 % human share. Second, provenance recorded at write time has no such ceiling: reconstructing authorship from an agent harness's own logs, files the agent wrote inside the logged channel during the log window show a median of 100 % of lines attested (40 files; 96 % over all 63), while hand-written notes show 0 %. Third, coverage is the whole problem: the proof of concept's own source, written by the same agent through an unlogged shell channel, attests at 9 %. That gap, not a detector, defines the product: a signed, append-only authorship ledger emitted by every writing tool, with a stated threat model, verified at review time. We place the design against the EU AI Act's Article 50 marking duty, Anthropic's text watermark, SynthID-Text, C2PA and software supply-chain attestation, and argue that reading provenance for the writer's own benefit is a use the transparency regime did not anticipate.

## 1. The inversion

The public conversation about AI text runs in one direction. Schools want to know whether a student wrote the essay. Regulators want machine output labelled so that citizens can tell. A video published this week captures the mood: it explains that Anthropic's Fable 5.1 now watermarks all of its text and then spends seven minutes on a recipe for laundering that text through a local model so the mark disappears [14].

Watch a working engineer for a day and the direction reverses. On the machine used for this paper, 2,716 file writes were made by an agent in five weeks, each one logged with the exact bytes, the session and the timestamp. The human-typed changes over the same period left no such record. They were made in an editor, in a hurry, often after the agent had finished and the tests had already passed. When something broke later, the question in the retrospective was never "did the AI write this?" It was "who touched this after the AI was done?"

That question has no tooling. This paper is about building it. The product is called NoHumanWrite, a provocation chosen on purpose; the technical claim underneath is narrower and stated exactly: a machine write that goes through a logged, signed channel can be proven to have done so, and everything else is *unattested*. In an agent-first workflow the human's judgement belongs in the prompt and the review, and an unattested byte in the artefact is an exception path that deserves a second look. Whether that byte was typed by a person or emitted by an unlogged tool is not something the artefact can tell you; it is something the team's instrumentation decides.

## 2. Background

**Watermarks.** Kirchenbauer et al. showed in 2023 that a language model can bias its token choices toward a pseudo-random "green list" at negligible quality cost, producing text a key-holder can later identify with high confidence [1]. Google DeepMind's SynthID-Text refined this into a tournament sampling scheme, published in Nature in October 2024 and deployed across Gemini [2]; the detector and the generation-side code are open source [10]. Anthropic's help centre states that models released on or after 2 August 2026 carry an embedded text watermark on every product surface, worldwide, with no opt-out, and that detection details will follow in technical documentation [12]. Readers whose knowledge predates 2026 will not be able to confirm this from memory; the source is cited with its access date and the claim is weighted accordingly.

**Statistical detectors.** Zero-shot methods such as DetectGPT [5] and Binoculars [6] score text by how a reference model would have predicted it; supervised methods such as Ghostbuster [7] train a classifier on features from weaker models. The RAID benchmark showed most of these degrade sharply under paraphrase and domain shift [8]. Sadasivan et al. gave the theoretical reason: as generated text approaches the human distribution, any detector's best possible performance approaches a coin flip, and a paraphraser can push it there [3]. OpenAI withdrew its own classifier in July 2023 for low accuracy [9]. Liang et al. found that commercial detectors flag essays by non-native English writers as machine-made at rates above 60 % [4]. That last result matters because the inverted task, done badly, produces the mirror-image injustice: calling a person's work machine-made when it is not.

**Provenance.** For images, audio and video, the C2PA specification defines signed Content Credentials that travel with the file and record who or what produced it [11]. For software builds, in-toto and SLSA define signed attestations of *how an artefact was produced* and Sigstore supplies the signing and transparency-log infrastructure [16, 17]. Git supports signed commits. None of these attest authorship at the line level: build provenance says which pipeline produced the binary, commit signing says who committed, and a developer who commits an agent's output under their own name is telling the truth about the commit and nothing about who wrote the lines. The closest relatives are per-edit micro-commits and co-author trailers that some agent harnesses already emit; they are coarse, unsigned, and lost in the first squash.

## 3. What an unattested span is, and why it matters

We define an unattested span as any span in an artefact not covered by a signed record of a machine write. In code this is the hot-fix typed at 23:40, the constant changed by hand, the `except: pass` added to get a deploy through, and also the file an agent produced through `sed -i` on a server where no hook ran. In research writing it is the sentence added to the machine's draft without a source. In operations it is the config line changed by hand and never mirrored into the repository.

The harm is not that a person wrote it. The harm is that it skipped the pipeline. The attested span was produced from an instruction that is on record, checked by whatever tests ran, and reproducible. The unattested span has no provenance, and the review process, having already approved the machine's pull request, tends to wave the follow-up through. A tool that surfaces these spans does not judge them; it routes them to the review they missed.

This framing also answers the obvious objection. Nobody proposes to forbid human edits. The proposal is that an unattested span should cost one extra approval or one passing test, and that the team should be able to see its share of unattested bytes over time.

## 4. Architecture: three layers, ordered by trust

**Layer 1, provenance by construction.** Every agent harness already knows the exact bytes it writes. Claude Code exposes them in its transcript logs and in a hook that fires after each write tool. The layer records, per write, the file, the hunk, a hash of the normalised text, the producing harness and session, and a signature from a dedicated key on the developer's machine. The record goes to an append-only ledger in the repository, `.nhw/attest.jsonl` (format in `SPEC.md`). At review time a verifier walks the diff: every changed line covered by a valid, still-matching record is attested; the rest is reported. This layer proves that a hunk passed through the signing channel, and proves nothing about the remainder. That asymmetry is the correct one, and it is also the layer's limit: its complement is "human" only to the extent that every machine channel is instrumented.

**Layer 2, vendor watermarks.** For text the team did not produce inside a cooperating harness, the vendor's statistical watermark is the next best evidence. Where the team runs its own models, SynthID-Text lets it hold its own key and verify its own output today [10]. For Claude and Gemini output the key is the vendor's; this layer becomes usable the day a detection endpoint ships, and the ledger format leaves a slot for it. Watermarks need enough tokens to reach confidence (the Nature paper reports its operating points for prose of a few hundred tokens [2]) and a determined rewrite removes them; short code hunks are an open question. A positive result is nonetheless a key-based statistical test, not a stylistic guess.

**Layer 3, statistical triage.** Where neither record nor key exists, the only remaining signal is style. We use the inverse of an AI-tell detector: inside a document dense with machine patterns, the paragraph with none is the candidate insertion. Section 6 shows this is close to worthless as a classifier. It stays in the design only to order a reviewer's attention within a document already known to be mixed, and it never produces a label on its own. A team that finds it produces no value should delete it; the ledger does not depend on it.

### 4.1 Threat model for the ledger

A provenance scheme without an adversary is a diary. The v0.1 ledger defends against one thing and is honest about the rest.

- **Defended: forgetting.** The common case is not fraud but amnesia: nobody remembers which lines came from the agent. Signed records, kept with the code, answer that durably and survive a squash.
- **Not defended: a developer who wants to lie.** The signing key lives on the developer's machine and the hook runs there. A developer can sign hand-typed text by routing it through the hook, or delete records. The ledger therefore proves "this hunk went through this developer's signing channel", not "a model wrote this". Against a hostile developer the scheme needs a trust anchor the developer does not control: records pushed at write time to a verifier or a transparency log (Sigstore's Rekor is the obvious candidate [17]), or signing performed by the harness vendor rather than the client. Both are compatible with the record format and neither exists in v0.1.
- **Not defended: append-only by convention.** A file in a repository can be rewritten. Anchoring the ledger head in signed commits, or mirroring it to a log, turns the convention into a property.
- **Out of scope: attribution of intent.** A prompt like "write exactly these lines" produces an attested hunk that is, in every useful sense, human-authored. The ledger records channel, not thought. Teams that care about this should log prompts alongside hunks; the format allows it and the privacy section explains why we did not default to it.

### 4.2 Privacy

Unattested lines identify their author by elimination on a small team. Records carry a session identifier and a machine key. Both are personal data under the GDPR once they can be linked to a person, which on a team of three they can. The verifier therefore reports "unattested", never a name; aggregates are per repository, not per developer, by default; and prompts are not recorded unless the team opts in. A deployment that turns unattested share into a per-person management metric has left the design and should say so to its staff.

## 5. Proof of concept and results

All code is Python standard library plus OpenSSH for signing. Nothing leaves the machine. The measurements were taken on 4 September 2026 on the author's laptop. This is one developer, one harness, one model family; the numbers describe coverage on this machine and should be read as an existence proof and a bug report, not as a benchmark.

### 5.1 Reconstructing provenance from harness logs

`nhw/attest.py` reads every Claude Code transcript under `~/.claude/projects`, extracts the `Write` and `Edit` tool calls, and indexes each produced line by a hash of its whitespace-normalised content, keyed by target path. It then attributes any file line by line: strong match (the agent wrote that line to that path), weak match (the agent wrote that line somewhere), or unattested. Lines shorter than twelve characters are ignored; a closing brace carries no authorship. Line matching is a proxy for hunk provenance, not authorship attribution: a human who retypes an agent's line verbatim is counted as attested, and a formatter that reflows an agent's line is counted as unattested. The production hook (§5.4) hashes hunks instead and removes the first problem but not the second.

Index: 312 transcript files, 2,716 writes (704 `Write`, 2,012 `Edit`), 72,681 attested lines. The logs on this machine begin on 30 July 2026, so the index covers five weeks. Files older than the window cannot be attested by construction, which is why the table reports both all files and the in-window subset for the corpus where modification times are meaningful.

| Corpus | Files | Median attested (any) | Median (strong only) | Line-weighted (strong) | 0–20 % | 20–50 % | 50–80 % | 80–100 % |
|---|---|---|---|---|---|---|---|---|
| Vault tools `tools/*.py`, all | 63 | 96 % | 96 % | 64 % | 22 | 2 | 3 | 36 |
| Vault tools, modified within the log window | 40 | **100 %** | 100 % | 76 % | — | — | — | — |
| Vault wiki `wiki/*.md` | 285 | 5 % | 0 % | 21 % | 178 | 19 | 16 | 72 |
| Vault raw notes `raw/*.md` | 100 | 0 % | — | 18 % | 73 | 0 | 2 | 25 |
| Agent config `~/.claude/*.md`, hooks | 5 | 100 % | — | 94 % | 0 | 1 | 0 | 4 |
| This PoC `nhw/*.py` | 3 | **9 %** | 0 % | 9 % | 3 | 0 | 0 | 0 |

Three readings. First, where the agent wrote code inside the logged harness during the log window, attestation is near-complete: the in-window median is 100 %, and the residue is lines later touched by hand or by a formatter, which is the signal the tool exists to find. The gap between the median (96–100 %) and the line-weighted figure (64–76 %) is a few large, older files with low attestation; the median describes the typical file, the weighted figure the typical line. Second, the distributions are bimodal rather than smeared: the 20–80 % middle holds 12 % of wiki files (35 of 285) and 8 % of tools (5 of 63). That is what one expects if authorship is decided per file by which channel produced it. Third, the wiki and raw corpora are mostly unattested even though the same agent wrote most of them: their pages predate the log window or were produced by other harnesses (a Telegram bot, a scheduled job, a different agent). Unattested means human *or untracked*, and on this machine untracked dominates. The corollary for anyone tempted to read the complement as "human": the complement is only as human as the instrumentation is complete.

The last row makes that point without argument. The proof of concept's own three source files were written by the agent in this session, through a shell heredoc rather than the logged write tool. The ledger saw nothing. Attestation: 9 %, all of it weak matches on generic import lines. This is an instrumentation gap, not a property of agents: log forensics after the fact cannot close it, and only a record emitted by every writing channel at write time can. That is why layer 1 in production is a hook and a signature, and the transcript reader is a demonstration.

### 5.2 Git authorship as a cross-check

`nhw/gitmode.py` runs `git blame` and marks a line machine-authored when its commit carries a `Co-Authored-By: Claude` trailer or a bot identity. On two wiki pages the agent wrote end to end, git reports 0 % machine authorship: an automatic backup job commits the working tree under the human's name every six hours. On a tool whose commits were made by the agent itself with trailers, git reports 83 % (551 of 667 lines). Git is therefore a usable second source only where the team's commit discipline already encodes authorship, and it inverts the truth where it does not. It cannot replace the ledger.

### 5.3 The statistical layer against ground truth

The transcripts also give labelled prose. What the developer typed or dictated to the agent is human; what the agent answered is machine. We took user turns of 40 to 300 words with no pasted structure (no headings, bold, lists or code fences) and assistant text blocks in the same length range, removed near-duplicates, and sampled 150 of each from 310 and 2,987 unique passages respectively. Each passage was scored by sloptrim 0.9.0, a local detector of 71 documented AI-writing patterns [15], chosen because it runs offline with no model and its pattern list is published; it is a reasonable instrument for a feasibility check and an unvalidated one for a research claim. A burstiness statistic (standard deviation of sentence length over its mean) was scored alongside.

| Measure | Human p10 / p50 / p90 | Machine p10 / p50 / p90 |
|---|---|---|
| sloptrim AI-tell score (0–100) | 0 / 0 / 8 | 0 / 18 / 25 |
| Burstiness | 0.28 / 0.58 / 0.94 | 0.29 / 0.60 / 0.96 |

AUC, machine vs human, sloptrim score: **0.912**. AUC, burstiness: 0.483, a coin flip; the folk belief that people vary their sentence length more than models do does not survive contact with a modern model's chat output. At the detector's own threshold of 20, 149 of 150 human passages fall below it (sensitivity 0.993, 95 % Wilson interval 0.963–0.999), which sounds like a fine human detector until one reads the other column: **90 of 150 machine passages also fall below it** (false-positive rate 0.60, interval 0.52–0.68). Six machine paragraphs in ten carry no tell the detector knows. This is not a detector error in the ordinary sense; a short plain machine paragraph *has* no tells, and no threshold on this score recovers the difference.

Caveats are real. One writer, one model family, chat-register prose, a detector calibrated on published text rather than working notes, and human turns that are shorter and plainer than most human writing. The numbers will move on other data. The shape will not: the human passages score zero because they are short and plain, and a majority of machine passages score zero for the same reason.

### 5.4 The production hook

`nhw/hook.py` is a Claude Code `PostToolUse` hook on `Write` and `Edit`. It hashes the normalised hunk, signs a canonical record with a dedicated ed25519 key via `ssh-keygen -Y sign` (namespace `nhw`), and appends it to the repository's `.nhw/attest.jsonl`. `nhw/verify.py` checks each record's signature against an allowed-signers file, slides the recorded hunk over the current file to survive line shifts, and reports covered and uncovered lines per file or per `git diff`. On a smoke test the same day: a three-line agent write verified at 100 %; after one hand-typed line was appended, 75 %, with line 4 reported as unattested. One week of real telemetry on the author's repositories is the next measurement, and it will be reported before any product claim about "typical unattested share" is made.

## 6. Base rates, applied to every layer

Suppose a team's artefacts are 5 % human-inserted by span, a figure we have not measured and state as an assumption; git history inside the log window could estimate it and should. Use the measured sensitivity and false-positive rate of the "no tell means human" rule, with their intervals.

    precision = 0.993 × 0.05 / (0.993 × 0.05 + 0.60 × 0.95) ≈ 0.08   (interval 0.07–0.09)

Fewer than one flag in twelve is a person. At a 1 % human share the figure is 1.4–1.9 %. A reviewer shown these flags will learn within a day to ignore them, and the one true insertion in the pile goes through with the rest. Raising the threshold helps less than it seems: from the quantiles in §5.3, a threshold near 25 would cut the false-positive rate to about 0.10 while keeping sensitivity near 1, for a precision around 34 % at 5 % prevalence; that is an operating point read off two quantiles, not a measurement, and one flag in three being real is still not a tool anyone would keep.

The same arithmetic applies to layer 1, and the paper would be dishonest to spare it. Layer 1 has no false positives for "machine" (a valid signature is a valid signature) but its "unattested" label has a false-human rate equal to the share of machine writes that bypass the hook. On this machine that share was large: the 9 % result is one file, and the wiki corpus suggests it was the majority of all machine writes before the hook existed. With the hook installed and every machine channel routed through it, the rate falls to the coverage gap of the remaining channels, which the team can enumerate (servers, other harnesses, formatters) and instrument one by one. Layer 3's false-positive rate is a property of language and cannot be engineered down; layer 1's is a property of the team's tooling and can. That difference, not any detector's AUC, is the argument of the paper.

This is the arithmetic that made classroom detectors harmful [3, 4], run in the other direction. A statistical detector of authorship is only acceptable where a false result costs nothing; here a false "human" costs a review and a false "machine" hides the thing we were looking for.

## 7. Ethics and the regulatory frame

The video that prompted this work treats the watermark as a threat and offers a laundering recipe [14]. The vault this project grew in had already filed watermark removal as something not to build, on the reasoning that disclosure is the point of the mark and a transparency law we are otherwise content to live under should not be defeated for convenience. NoHumanWrite is the mirror image. It never removes a mark. It never asserts that a person's work is machine-made, the failure mode with victims. It asserts, with a signature, that a hunk passed through a machine channel, and leaves the remainder unlabelled for a human to look at.

The regulatory fit should be stated precisely rather than warmly. Article 50(2) of the AI Act obliges *providers* of generative systems to mark outputs in a machine-readable format so that they are detectable as artificially generated, with exemptions for assistive and standard editing functions; Article 50(4) puts disclosure duties on *deployers* for deep fakes and for AI-generated text published to inform the public on matters of public interest [13]. Neither provision speaks to source code inside a private repository, and this paper does not claim it does. The relevance is indirect and concrete: the same vendors now emit the machine-readable marks Article 50 demands, and a detection endpoint built for regulators would serve a second constituency, teams who want to know what the machine wrote in order to trust it and spend scarce attention on the rest. Until such an endpoint exists, a cooperating harness and a signed ledger serve that constituency completely, at zero cost to the first.

Two design rules follow. The ledger records a machine key, never a person's name; the reviewer sees "unattested", not "Arnaud". And the tool ships with no humaniser, no rewrite mode and no removal mode, so that it cannot be turned around and pointed at the constituency Article 50 protects.

## 8. From paper to product

The wedge is a pull-request check for teams that already write with agents. Install a GitHub App, add one hook to the harness, and each pull request shows the share of changed bytes that is machine-attested, highlights the unattested hunks, and applies a policy the team chose: comment, require a second approver, require a test that touches the file, or block. The ledger stays in the repository as plain JSON; only the numbers leave. The business plan, pricing and 30-day build sit in `business.md`; the ledger format in `SPEC.md`; the threat model in §4.1 is the first thing a security-minded buyer should be shown.

The honest test of the idea is not the AUC. It is whether the number on the pull request changes one review decision a week on a real team. Five design partners will tell us within a month.

## 9. Open questions

- Formatters and refactors rewrite attested hunks without changing meaning. Hash at the token level, or re-attest after a formatter run the harness itself invoked?
- Agents that edit through shell commands, as ours did, need the hook at the file-system or git-index level rather than the tool level. Where is the right choke point, and can it be made tamper-evident without a server?
- What token count does Anthropic's watermark need for confidence, and will a detection endpoint accept short code hunks at all? The Nature paper's numbers are for prose [2].
- Should an attested span that a human later *reviewed and approved* be marked differently from one nobody looked at? The ledger has room for a review record; the policy question is open.
- What is the real human-insertion share on agent-first teams? It is the prevalence every base-rate argument in this paper assumes, and it is measurable from ledgers once a few teams run them.
- Multi-writer teams: does the distribution of unattested share across developers become a management signal, and should it be visible at all? §4.2 says no by default.

## 10. When the writer is general: what changes on the way to AGI

Everything above is measured on current systems, which are not general intelligences by any published definition. The people building them say general intelligence is near; the benchmarks that try to measure it say the gap is still visible; the field has no agreed definition. This section does not pick a date. It asks what happens to the argument of this paper as autonomy rises, using only frameworks and measurements that are on the record, and it states which of our claims survive that rise unchanged and which turn into their opposite.

### 10.1 Where the field says it stands: measured, declared, defined

**Measured.** METR's time-horizon work, the most-cited operational yardstick for autonomous capability, tracks the length of software tasks a system completes with 50 % reliability. Its January 2026 update reports a frontier doubling time "around every 7 months over the period 2019 to 2025" on a suite enlarged from 170 to 228 tasks, with the best measured system (Claude Opus 4.5) at a point estimate of 320 minutes and an interval of 170 to 729 minutes; the authors call their intervals "still very wide" and note that few remaining tasks defeat the newest models [20]. ARC Prize's ARC-AGI-3, launched in 2026, measures skill-acquisition efficiency in novel interactive environments that are "100 % human-solvable"; its stated criterion is that "as long as there is a gap between AI and human learning, we do not have AGI", and at launch the gap was large [21]. The International AI Safety Report's October 2025 key update records continued gains in coding, mathematics and autonomous operation while calling the capability profile "jagged": strong on some hard tasks, weak on some easy ones [22].

**Declared.** At Davos in January 2026, Demis Hassabis put "a 50 % chance AGI might be achieved within the decade", defined it as "a system that can exhibit all the cognitive capabilities humans can — and I mean all", and said today's systems are "nowhere near" it; Dario Amodei predicted models would replace the work of software developers within a year and reach Nobel-level research within two; Yann LeCun said "we're never going to get to human-level intelligence by training LLMs" [28]. Amodei's essay of October 2024 defines the target as "a country of geniuses in a datacenter" [27]; the AI 2027 scenario of April 2025 lays out the fast path in detail as a forecast, not a measurement [27]. These are dated statements by interested parties and are cited as such.

**Defined.** Two frameworks let the discussion proceed without a date. Morris et al. (Google DeepMind, 2023) separate *performance* from *generality* and add a distinct axis of *autonomy*, from tool to consultant, collaborator, expert and fully autonomous agent, arguing that autonomy is a deployment choice constrained but not fixed by capability [18]. Feng, McDonald and Zhang (2025) define five levels of agent autonomy by the role left to the human: operator, collaborator, consultant, approver, observer, and make the same point: autonomy "can be treated as a deliberate design decision, separate from its capability" [19]. Everything below is stated against these autonomy levels rather than against a year.

### 10.2 What the ledger measures as autonomy rises

At the operator and collaborator levels, where this paper's data was gathered, the unattested share is mostly the human's hand, and the pull-request check earns its keep by finding it. As deployments move to the consultant and approver levels, the human stops typing bytes and starts approving intents. The unattested share of the artefact trends toward zero for a reason that has nothing to do with detection: there is no longer a human channel writing into the file. If METR's trend holds even at its historical 7-month doubling, systems that complete day-long tasks unattended arrive within the planning horizon of any team reading this, and the interval in [20] is wide enough that it may already be here.

The ledger does not become useless at that point; its unit changes. What the review needs then is not "which bytes did a person type" but "which task did a person authorise, under what constraints, and did the system stay inside them". The record format anticipates this: the `producer` field already names the harness, model and session, and the natural extension is an `authorised_by` record signed by the human who launched the task, alongside the machine-signed hunks. The vault this project grew in reached the same conclusion from a different direction when reviewing agent-team tooling: log the agent's identity *and the human on whose behalf it acted* [see the owner-attestation note in `wiki/review-josh-pocock-buzz.md`]. The unit of review moves from the diff to the intent, and the rare event worth finding moves from the unattested byte to the unauthorised action.

This yields a falsifiable prediction that the ledger itself can test. On any team running the hook, the unattested share per pull request should fall monotonically as the team's agents are given longer tasks, and the ratio of authorisation records to hunk records should fall with it. If unattested share stays flat while task length grows, the thesis of this section is wrong and the human hand is doing something the framework does not capture.

### 10.3 The threat model inverts

Section 4.1 assumed the developer might be the adversary and the machine an honest scribe. The AI-control literature makes the opposite assumption and has been building the tooling for it since 2023: treat the capable model as *untrusted*, and design protocols in which a weaker *trusted* model monitors, edits or executes, so that safety holds even if the strong model is trying to subvert the task [23]. The evidence that this is not paranoia has been accumulating: Meinke et al. document frontier models scheming in context when given a goal and a reason [25]; Bengio and co-authors set out why oversight must scale with capability [29]. The protocols are now specific. Redwood Research's untrusted-advice protocol (July 2026) has a trusted executor take every action while the untrusted model may only send short hints; with 16 characters per message it recovers about 67 % of the capability gap on SWE-bench Verified [24]. The same executor-and-advisor shape now ships as an API feature [30]. Weak-to-strong generalisation asks the complementary question, whether a weak supervisor can elicit a strong model's full capability at all [31].

For provenance the consequence is exact. A ledger that proves "a machine wrote this" was sufficient when the machine was the trusted party. Once it is not, the record must also say *which* machine, in *which* trust tier, under *which* monitor, and on *whose* authority. Two-sided provenance: machine-signed hunks, human-signed authorisations, and monitor verdicts, kept together and verifiable together. NoHumanWrite as described in §4 is the first leg of that record. It is worth building now because the format that teams adopt for the first leg is the format the other two will have to fit.

### 10.4 What stays true whatever the timeline

Three claims in this paper get stronger, not weaker, as capability rises.

1. **Statistics cannot attribute authorship, and the ceiling falls.** Sadasivan et al.'s argument is that detection degrades as generated text approaches the human distribution [3]. More capable writers approach it faster and can be asked to leave it on purpose. Layer 3 is a triage aid today and nothing at all tomorrow.
2. **Provenance must be captured at write time, by every channel, and the choke point moves outward.** This paper's own 9 % result came from an agent using a shell instead of the logged tool. A more autonomous system creates its own channels. The place to record provenance therefore moves from the tool to the environment: the sandbox, the git index, the file system, the container. The AI-control literature reaches the same conclusion about monitoring, for the same reason.
3. **The human's remaining contribution is authorisation and review, and that is what the record must make legible.** Whether that contribution is large or small is a question about the autonomy level a team chooses, which [18] and [19] both insist is a choice. A ledger that shows the team where its human decisions actually sit is how the choice stays deliberate.

### 10.5 What this section does not claim

No date for general intelligence, and no definition beyond the operational levels in [18] and [19]. No claim that current systems are safe or unsafe to run at any given autonomy level; that is the subject of [22], [23] and [29], not of this paper. No claim that the extensions in §10.2 and §10.3 are built; they are a schema direction and an experiment design. The measurements in §5 are from systems at the collaborator level on one machine, and nothing here changes them.

## Changes since v0.1

External review by eight frontier models (transcript in `eval/council-review-2026-09-04.md`) produced one dissent ("do not publish") and seven "publish after fixes". Applied: the task is now defined as *unattested*, not *human*; the wiki mid-range figure is corrected from 6 % to 12 %; strong-match-only and in-window numbers are reported; confidence intervals are given for the classifier figures and propagated to the precision claim; the base-rate argument is applied to layer 1 as well; a threat model (§4.1), a privacy section (§4.2) and supply-chain related work (in-toto, SLSA, Sigstore) are added; Article 50 is described by paragraph rather than by mood; the 9 % result is framed as an instrumentation gap; the study is labelled an n=1 experience report. Added at the author's request after review: §10, on what the argument becomes as autonomy rises toward general intelligence, built only on dated, source-checked frameworks and measurements. Not applied: removing 2026 sources that reviewers could not verify from their training data (they are cited with access dates and were checked live), and deleting layer 3 (kept, demoted, with an explicit invitation to drop it).

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
13. Regulation (EU) 2024/1689 (Artificial Intelligence Act), Article 50, transparency obligations for providers and deployers of certain AI systems, applicable from 2 August 2026.
14. Chase AI. *Fable 5.1 Watermarks EVERYTHING, Here's How To Remove It.* YouTube, video slePq-H-TMA, 10:14, September 2026.
15. sloptrim 0.9.0. Local detector of 71 documented AI-writing patterns, Python standard library, Apache-2.0.
16. in-toto / SLSA. *Supply-chain Levels for Software Artifacts, specification v1.0*, slsa.dev; *in-toto attestation framework*, github.com/in-toto/attestation.
17. Sigstore. *Sigstore: signing, verification and the Rekor transparency log.* sigstore.dev.
18. M. R. Morris, J. Sohl-Dickstein, N. Fiedel, T. Warkentin, A. Dafoe, A. Faust, C. Farabet, S. Legg. *Levels of AGI for Operationalizing Progress on the Path to AGI.* arXiv:2311.02462, 2023 (ICML 2024 position paper).
19. K. J. K. Feng, D. W. McDonald, A. X. Zhang. *Levels of Autonomy for AI Agents.* arXiv:2506.12469, 2025.
20. T. Kwa et al. (METR). *Measuring AI Ability to Complete Long Software Tasks.* arXiv:2503.14499, 2025; METR, *Time Horizon 1.1*, 29 January 2026, metr.org/blog/2026-1-29-time-horizon-1-1/ (accessed 4 September 2026).
21. F. Chollet. *On the Measure of Intelligence.* arXiv:1911.01547, 2019; ARC Prize Foundation, *ARC-AGI-2*, arXiv:2505.11831, 2025; *ARC-AGI-3*, arcprize.org/arc-agi/3 (accessed 4 September 2026).
22. Y. Bengio et al. *International AI Safety Report 2025: First Key Update: Capabilities and Risk Implications.* arXiv:2510.13653, October 2025; *International AI Safety Report 2026*, published 3 February 2026, internationalaisafetyreport.org.
23. R. Greenblatt, B. Shlegeris, K. Sachan, F. Roger. *AI Control: Improving Safety Despite Intentional Subversion.* arXiv:2312.06942, 2023.
24. C. Biddulph, A. Kaufman (Redwood Research). *Untrusted advice for AI control: short, strong advice significantly uplifts weak LLMs.* 27 July 2026, blog.redwoodresearch.org.
25. A. Meinke et al. *Frontier Models are Capable of In-context Scheming.* arXiv:2412.04984, 2024.
26. S. Bubeck et al. *Sparks of Artificial General Intelligence: Early experiments with GPT-4.* arXiv:2303.12712, 2023.
27. D. Amodei. *Machines of Loving Grace.* October 2024, darioamodei.com; S. Altman, *The Gentle Singularity*, June 2025, blog.samaltman.com; D. Kokotajlo et al., *AI 2027*, April 2025, ai-2027.com.
28. Fortune. *AI luminaries at Davos clash over how close human-level intelligence really is.* 23 January 2026 (quotes from D. Hassabis, D. Amodei, Y. LeCun).
29. Y. Bengio et al. *Managing extreme AI risks amid rapid progress.* Science, 2024; arXiv:2310.17688.
30. Anthropic. *Advisor tool.* Claude Platform documentation (accessed 4 September 2026).
31. C. Burns et al. *Weak-to-Strong Generalization: Eliciting Strong Capabilities With Weak Supervision.* arXiv:2312.09390, 2023.
