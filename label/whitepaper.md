# AI Grade: a number for how much of a work came through a signed machine channel

White paper v0.3.2 · 6 September 2026 · Plus de Fun Agency, Geneva
Companion to *NoHumanWrites* (doi:10.5281/zenodo.22362427) and to the label spec in `label/README.md`.
Author's interest: the author wrote NoHumanWrites and maintains the label; the label exists to sell the ledger.
v0.2 followed an eight-model hostile review (`eval/council-review-label-2026-09-06.md`). v0.3 renames the mark, defines the scale, and is written to be read by anyone, not only engineers. Changes are listed at the end.

## Summary

Every mark on the market for AI-era content says the same thing: a human made this, take our word for it. None of them can be checked by an outsider. This paper proposes the opposite kind of mark, and a checkable one. AI Grade is a number from 0 to 100. It is the share of a piece of work, a source tree, a book, a song, that came through a machine channel whose every write was signed at the moment it happened. Anyone holding the public key can recompute the number from the files and the ledger, and every part that did not come through the channel is listed beside it.

The number is deliberately modest. It says which bytes came through a logged, signed channel. It does not say who decided them, whether they are any good, or how autonomous the machine was. The case for publishing such a number rests on two facts. Work that comes through a logged channel arrives with a prompt, a diff, a log, a test run and a signature; work through any other channel arrives with none of those. And the largest software companies now say, in their own words, that machines write most of their new code with engineers approving it. If that is true, there are bytes to count, and nothing else counts them per unit in a way a third party can verify.

## 1. The marks that exist, and the gap

Since 2023 a family of marks has appeared to certify human production. Not By AI gives its badge to anyone who estimates "that at least 90 % of your content is created by humans" and says of itself that it "is not an AI detection tool" [1]. The Authors Guild opened its "Human Authored" certification to members in January 2025 and to all authors published in the United States in March 2026; it rests on the author's declaration [2]. iHeartMedia made "Guaranteed Human" part of its on-air identity in November 2025 [3]. Spotify's "Verified by Spotify" badge follows the platform's own review [4]. Each is a declaration, an estimate or a private judgement. A reader cannot re-derive any of them.

Marks that point toward machine production exist too, and they cover media rather than text. C2PA Content Credentials record, in signed metadata, that an image, audio or video file was generated or edited by an AI tool [5]. Vendor watermarks such as SynthID-Text and Anthropic's text marking make machine output detectable by whoever holds the key [6]. Spotify announced an "AI Persona" badge on 11 August 2026 for artist profiles whose identity is AI-generated [4]. The European AI Office's Code of Practice of 10 June 2026 provides icons and requires provenance to be "digitally signed and time-stamped (on systems where time information is available) in a secure and tamper-evident manner"; IPTC's reading is that "while it is not named specifically, the only technology that meets these criteria is C2PA" [7]. These marks warn the public that a machine was involved. None gives a per-unit account of a text file or a source repository that a reviewer can verify with a public key, and none lists the parts the machine did *not* produce. That is the gap.

## 2. What a signed channel records

Some vocabulary, once. A *channel* is a way bytes reach a file: an agent's write tool, a text editor, a shell command, a formatter. A *hunk* is one contiguous block of text written in one go. A *ledger* is an append-only file of records, one per hunk, each carrying a hash of the bytes, the harness, the model, the session, the time, and a signature from a key. A *trust root* is the list of public keys the person doing the checking has decided to believe. NoHumanWrites installs a hook that signs every hunk an agent writes and appends the record to the ledger [8].

When an agent writes through the hooked tool, the hunk gets a record. When the same file is changed in an editor at 23:40, or by a formatter, or by the same agent through a shell command that bypasses the hook, nothing is recorded. This paper calls such a unit *unattested*, and the word means exactly that: no signed record covers it. It does not mean a human wrote it. The project's own measurement makes the point [8]: on one developer's machine over five weeks the agent made 2,716 logged writes covering 72,681 lines; tools the agent wrote through the hooked channel attested at a median of 96 % of lines; hand-written notes attested at 0 %; and the project's own source, which the same agent had written through a shell heredoc, attested at 9 %. The 9 % is the method reporting an unlogged channel. Coverage is the whole problem, which is why a grade must be read next to a list of the channels a team uses (§7).

The same study shows why the grade cannot rest on writing style. A local detector separated machine from human prose with an AUC of 0.91, yet 60 % of machine passages carried no tell at all, so under one rule, "no tell means human", at a 5 % human share, precision was near 8 % [8]. Sadasivan et al. give the theoretical reason: detection degrades as generated text approaches the human distribution [9]. AI Grade never guesses from style. It reads a signature or it says nothing.

## 3. The grade

### The number

For a named path, at a named commit, on a named date, the grade is the share of scored units covered by a signed record from a key the verifier trusts, rounded down to a whole number. 99.6 % is grade 99. The units are a line of code, a paragraph of prose, a line and stanza of verse, a bar of sheet music; the denominator is every scored unit under the named path, with nothing excluded. A hunk counts as attested when its signed hash still matches, or, when the hunk as a whole no longer matches, unit by unit against the signed per-unit hashes, each hash usable at most as many times as it was signed [8]. A pasted copy of a signed line is attested; a formatter's reflow of a signed paragraph is edited or unattested depending on how much survives.

### The scale

Two everyday scales work the same way. A petrol pump shows an octane number, 95 or 98, and the number is the grade. Gold is stamped with its purity: 24 carat is pure, 18 carat is three quarters gold, and the hallmark says which. The number carries the meaning; the band names tell you what it is good for.

| Grade | Band | Meaning |
|---|---|---|
| 100 | Pure | Every unit sits in a signed hunk that still matches. Nothing typed by hand after the machine finished, nothing through an unlogged channel. |
| 90–99 | High | The channel produced the work. The rest, at most one unit in ten, is listed by location. |
| 50–89 | Mixed | Most of the work came through the channel and a large minority did not. The seal says "Mixed" on its face. |
| 0–49 | no label | Most of the work did not come through a signed channel. The report is still printed; the seal is refused. |

The lines are chosen for reasons a reader can check. 100 is exact. 90 is Not By AI's threshold pointed the other way: they ask a creator to *estimate* at least 90 % human, we *count* at least 90 % through the channel [1]. 50 is where the sentence "a machine channel produced this work" stops being true, and below it there is nothing to certify.

### Two levels

Level 1, self-signed: the author's machine key signs each hunk through the hook, and the verifier uses their own trust root, never the repository's. Level 2, anchored: the head of the ledger, its hash, length, record count and commit, is signed and recorded in Sigstore's public Rekor log, by hand or from a git post-commit hook, and the receipt is committed beside the ledger. A verifier checks that the anchored prefix of today's ledger still hashes to the anchored value, that the anchor carries a signature from a trusted key, and that Rekor still serves the same entry, so a deleted or rewritten record leaves a visible gap. Anchoring makes the history tamper-evident; it does not make a false record true, and a key-holder can still sign anything. Taking the key-holder out of the loop is Level 3, a trusted executor outside the writer's reach that produces or countersigns the hunks; the parent paper's §10.3 describes it [8]. What ships of it today is the local half: the harness's sandbox can deny the model's shell any read of the signing key, so only the hook spawned by the harness can sign, and the hook records that it observed this. The claim is self-reported and stays off the badge; the design note `label/level3.md` gives the three designs, the holes, and what a verifiable Level 3 would need from the harness. The seal names its level so a reader knows which assurance they are looking at.

### What it guarantees, and what it does not

Three sentences a verifier can check by running the tool. Every attested unit is covered by a record naming harness, model and session, signed by a key the verifier chose to trust. Every unit not so covered is listed by file and position. Anyone with the public key, the ledger and the files gets the same number.

Four things it does not guarantee. Not quality, correctness or safety: a machine-written bug is an attested bug. Not authorship: a prompt of "write exactly these lines", or an agent copying a hand-written file back into place, yields an attested hunk, so the key proves the channel, not the author. Not the absence of human judgement, which sits in the prompt and the review and is not made of bytes. Not anonymity: the ledger records a key fingerprint, never a name, but on a small team a key identifies a person by elimination, and reports aggregate per repository for that reason.

## 4. Is there work to grade?

The figures below are claims by interested parties about their own organisations. Each uses its own undisclosed definition of "code" and "written by AI", and they are not comparable with each other. They are cited for what they are: the largest software organisations describing their own practice.

| Date | Who | Statement | Source |
|---|---|---|---|
| 29 Oct 2024 | Sundar Pichai, Alphabet Q3 2024 earnings call | "more than a quarter of all new code at Google is generated by AI, then reviewed and accepted by engineers" | primary, blog.google [10] |
| 29 Apr 2025 | Satya Nadella, at Meta's LlamaCon | "20 % to 30 % of code inside the company's repositories was 'written by software'" | as reported by TechCrunch [11] |
| 24 Apr 2026 | Sundar Pichai | 75 % of new code at Google AI-generated, up from 50 % the previous autumn | as reported by Semafor; primary transcript not located; not independently verified [12] |
| 14 May 2026 | Krishna Rao, Anthropic CFO, on the *Invest Like the Best* podcast | "90 %-plus" of Anthropic's code written by Claude | as reported by TechSpot; not independently verified [13] |

The one primary quotation describes the human's role as review and acceptance. That is the division a signed ledger is built to make visible: which units the machine channel produced, and which a person changed afterwards.

Two other measurements are relevant and measure different things. METR reports the length of software task a frontier system completes at 50 % reliability "doubling around every 7 months over the period 2019 to 2025", with the best system in its January 2026 update at a point estimate of 320 minutes on an interval of 170 to 729 minutes [14]. A 50 % horizon means the system fails half the tasks of that length. Anthropic's Economic Index of 26 June 2026 reports that agentic coding sessions run with more autonomy, on the report's own index, than chat sessions on the same model [15]. Neither measures the share of code a machine writes, and this paper does not chain them to the table.

The counter-evidence belongs in the same section. METR's randomised trial of July 2025 found that sixteen experienced open-source developers, using Cursor Pro with Claude 3.5 and 3.7 Sonnet on 246 real tasks, took 19 % longer with AI tools than without; they had forecast a 24 % speed-up and afterwards believed they had got 20 % [16]. The authors call it "a snapshot of early-2025 AI capabilities in one relevant setting". The perception gap is the part that matters for a label: the developers could not tell, from the inside, what the machine had done for them. A team that cannot tell from the inside needs a record, and the record has to count bytes rather than ask people.

## 5. What the number is not

The grade is a coverage statistic: the fraction of a work's units that passed through logged, signed machine channels. Three things move it. Delegation moves it, when a team hands its agents more of the work. Instrumentation moves it, when a channel that used to be unlogged gets a hook. Gaming moves it, when work is routed through the hook to raise the number. From the number alone the three cannot be told apart. A public registry of grades would therefore be a self-selected adoption index of logged channels, and once published it would be a leaderboard with all the distortions that implies. An earlier draft of this paper called such a registry a thermometer of rising machine autonomy. It is not, and the claim is withdrawn.

The published frameworks for grading progress toward general intelligence make the point from the other side. Morris et al. (Google DeepMind, 2023) place today's frontier chatbots at the lowest rung of general capability, "Emerging", and describe a separate autonomy axis of six levels, 0 to 5, from no AI to AI as agent; autonomy, they argue, is a deployment choice constrained but not fixed by capability [17]. Feng, McDonald and Zhang (2025) define five levels by the role left to the human, operator, collaborator, consultant, approver, observer, and state that autonomy "can be treated as a deliberate design decision, separate from its capability" [18]. On both ladders the human who approves each change sits in the middle. A team whose engineers "review and accept" every machine hunk is at the approver level, and a ledger records precisely that: machine-produced units, human decisions upstream and downstream of them. Nothing in the ledger says which rung a team is on, because the rung is defined by what the human does, and the human's decisions are not bytes.

A ledger could feed a real study of delegation, but only under a protocol fixed in advance: an inventory of every channel a team uses and which are hooked, the unit rules of §3, a coverage audit at each measurement (write through every channel and see what the ledger catches), an independent record of task length and of the human's role per task, and a list, written beforehand, of which rises in grade would *not* count as delegation: a new hook, a formatter routed through the agent, a rewrite of an existing file. None of this exists yet.

## 6. Why fix the record now

The people who study how to deploy a capable model safely treat it as untrusted. Greenblatt et al. design protocols in which a weaker, trusted model monitors or executes what the capable model proposes [19]; Meinke et al. document frontier models scheming in context when given a goal and a reason [20]; Redwood Research's July 2026 protocol has a trusted executor take every action while the untrusted model sends short hints, recovering about 67 % of the capability gap at 16 characters per message [21]. If the writer can be an adversary, a recorder that runs inside the writer's environment can be tampered with, and a Level 1 grade is exactly as good as the honesty of the machine and the key-holder. That is why the spec defines the anchored level and names the trusted-executor design before anyone needs them. The failure the ledger shows *today*, the heredoc that bypassed the hook, is a coverage loss that neither anchoring nor a transparency log addresses. Only hooking the channel does.

What the grade contributes to the larger question of machine autonomy is small and specific. If the delegation the labs describe is real, it leaves bytes, and a ledger is the only record of those bytes that survives the end of the session. It does not measure the delegation; it makes one component of it auditable, per unit, by a third party. Anyone looking for a date for general intelligence will not find one here.

## 7. How the grade can be gamed

- Prompt-supplied content. "Write exactly these lines" yields an attested hunk. Not defended; disclosed on the seal and in §3.
- Rewrite laundering. An agent reads a hand-written file and writes it back, grade 100. Same as above; the ledger's `producer` field and the prompt log, where a team keeps one, are the only trace.
- Non-AI automation through the hook. A formatter or a `sed` run routed through the agent's write tool is attested, because it is a machine channel. The grade says "machine channel", not "model output".
- Scope cherry-picking. A seal on the one clean subdirectory. Every seal names its path; one that does not is invalid.
- Threshold gaming. Re-emitting a grade-89 file through the agent to reach 91. Rewrite laundering with a target; same trace, same disclosure.
- Repository splitting. Hand work in one repository, agent work in another, seal on the second. The seal covers what it names and nothing else.
- The key-holder lying. Signing anything, deleting records. Level 1 does not defend; Level 2 makes deletion visible; only a trusted executor removes the key-holder.
- Key theft. A stolen key signs as its owner until the owner's entry in the trust root is replaced. Revocation is that edit; the spec defines no PKI and does not pretend to.
- A stale number. The seal carries path and date, and once anchored, commit. The terms forbid a number older than the last change to the named path.
- Identification by elimination. Reports give lines and files, never names, and aggregate per repository.
- Goodhart. A published grade becomes a target. The paper attaches no claim about autonomy to the number, so raising it buys nothing but the number.

## 8. The grade applied to itself

Checked on 6 September 2026 against the repository's own signed ledger, verified with the maintainer's trust root:

```
$ python3 nohumanwrites.py check . --label
NoHumanWrites: no label — AI Grade 13 is below 50: most of this work did not come through a signed machine channel.

$ python3 nohumanwrites.py anchor
anchored: 103 records, ledger sha256 40da063ca400024f…, commit 75e07ddf2d19 → Rekor index 2742870568 (https://rekor.sigstore.dev)

$ python3 nohumanwrites.py check label/ --label --seal label/ai-grade.svg
AI Grade 100 · Pure · 98 of 98 units attested · checked 2026-09-06 · Level 2 (anchored · Rekor #2742870568 · commit 75e07ddf · inclusion verified, 1 record(s) since, not yet anchored)
seal written: label/ai-grade.svg (signed into the ledger)
```

Signing key fingerprint: `SHA256:6t3ttnXr9M4hfcT7NHQvAqzemNizJnzU/1z/e6TzsYg` (ed25519, `nhw-Arnauds-MacBook-Pro`); the public key is in `.nhw/allowed_signers`, and a verifier must place it in their own trust root to reproduce the number. The commit that contains this text is tagged `label-v0.3`. The repository as a whole does not earn a label: most of its prose reached the disk through shell heredocs, which the hook does not see. The `label/` directory earns grade 100 at the moment of writing, and the number should be read with §7 in mind. Writing this version taught two lessons the tool now embodies. The seal the tool generated was itself an unsigned machine write and dragged the directory to grade 86 until the tool learned to record its own output in the ledger. And a search-and-replace edit across a bullet list left four paragraphs reading as "edited", so the final text was written again in full through the signed channel, which is rewrite laundering by the paper's own definition, done here in the open. A label that had to exempt its own authors would be a declaration, which is the thing it replaces.

## 9. What comes next

- Now. `--label` and `--seal` in the CLI, the scale of §3, Level 1 and Level 2 (`anchor`, with the Rekor index and commit on the badge line). Free to display on anything that passes, with path and date on the face.
- Next. Level 3, the verifiable half: remote countersigning once the harness signs its own tool events, then the trusted executor itself (`label/level3.md`).
- The protocol of §5, written up as a pre-registered study design before any registry publishes a number.
- A registry, if the protocol exists: opt-in, delayed by a quarter, per-channel aggregates only, no per-team figures, no content.
- Text provenance beyond code. The ledger already scores paragraphs, verse lines and bars of music [8]; the format is offered to the C2PA working group as one answer to the text gap in §1.

## Changes

v0.3.2 (6 September 2026, night). Level 3 started: design note `label/level3.md` with three designs (local isolation through the harness sandbox, remote countersigning, trusted executor) and the holes in each. The local design ships as `setup --level3` plus an `executor` claim the hook writes into each record when the sandbox denies it the key; the check prints it as a separate self-reported line and the badge is unchanged. §3 and §9 updated.

v0.3.1 (6 September 2026, evening). Level 2 shipped: `anchor` signs the ledger head and records it in Sigstore's public Rekor log; the check verifies continuity, signature and inclusion and prints the Rekor index and commit on the badge line, or says why it fell back to Level 1. The trusted-executor design is now called Level 3. §3, §8 and §9 updated; the anchor record format is in the repository's SPEC.md. First anchor: Rekor index 2742870568, commit 75e07ddf.

v0.3 (6 September 2026). The mark is renamed from Guaranteed AI to AI Grade, on the maintainer's decision after one reviewer's objection that the old name promised authorship the ledger cannot prove. The number is now the label, with a defined scale (Pure 100, High 90–99, Mixed 50–89, no label below 50) and stated reasons for each line; the seal is generated with the number on its face and signed into the ledger. The paper is shortened by about a third and rewritten for readers who are not engineers, with the vocabulary defined once in §2 and the gaming list cut to a line each. Sources re-checked on the day at the live URLs: Not By AI's 90 % rule and "not an AI detection tool" [1], Pichai's Q3 2024 sentence [10], Semafor's 75 % report [12], METR's doubling and 320-minute figures [14], Morris et al. [17] and Feng et al. [18].

v0.2 (6 September 2026). After the eight-model review: the label certifies a channel, not authorship; the "thermometer of autonomy" claim and its one-line falsifier are withdrawn; the autonomy ladders are corrected (approver mid-ladder; Morris et al. have six levels, 0 to 5); the doubling-cadence comparison and several superlatives are removed; §4 marks primary versus reported rows; existing AI-origin marks are acknowledged; Level 2 is stated exactly; units, denominator and counting rules are defined; the attack list grew from two to eleven; §8 became reproducible; the author's interest is disclosed. Two reviewer claims were wrong and are recorded as such: the METR paper's title is "Long Software Tasks", not "Long Tasks" (arXiv:2503.14499); iHeartMedia's mark dates from November 2025, not 2024.

## References

1. Not By AI. *Add the Badge to Your Human-Created Content.* notbyai.fyi, accessed 6 September 2026 (archived). Both quotations verbatim.
2. The Authors Guild. *Authors Guild Launches "Human Authored" Certification to Preserve Authenticity in Literature*, January 2025; *Authors Guild Launches Expanded "Human Authored" Certification Program*, March 2026. authorsguild.org/news, accessed 6 September 2026.
3. Inside Radio. *iHeartMedia Makes "Guaranteed Human" a Core Branding Message Across All Stations.* November 2025; iHeartMedia, *Guaranteed Human at CES 2026*, iheartmedia.com/advertise/insights. Accessed 6 September 2026.
4. Spotify Newsroom. *Introducing a New Label for AI-Generated Artist Identities on Spotify.* 11 August 2026, newsroom.spotify.com; the same page describes "Verified by Spotify". Accessed 6 September 2026.
5. Coalition for Content Provenance and Authenticity. *C2PA Technical Specification 2.2.* c2pa.org. The absence of a text or source-file profile is the author's reading of the specification.
6. S. Dathathri et al. *Scalable watermarking for identifying large language model outputs.* Nature, October 2024, doi:10.1038/s41586-024-08025-4; Anthropic Help Center, *How Claude marks AI-generated content*, article 16266773, accessed 14 August 2026.
7. IPTC. *European AI Office releases Code of Practice on Transparency of AI-Generated Content.* iptc.org/news, 10 June 2026, accessed 6 September 2026. Both quotations verbatim.
8. A. Chrétien (Plus de Fun Agency). *NoHumanWrites: find the human in machine-written work.* v0.2.2, September 2026, doi:10.5281/zenodo.22362427, sections 5, 6, 10.2, 10.3, and the repository's `SECURITY.md`.
9. V. S. Sadasivan, A. Kumar, S. Balasubramanian, W. Wang, S. Feizi. *Can AI-Generated Text be Reliably Detected?* arXiv:2303.11156, 2023.
10. S. Pichai. *Alphabet Q3 2024 earnings call, CEO remarks.* 29 October 2024, blog.google/inside-google/message-ceo/alphabet-earnings-q3-2024/, accessed 6 September 2026. Primary; quoted verbatim.
11. M. Zeff. *Microsoft CEO says up to 30 % of the company's code was written by AI.* TechCrunch, 29 April 2025, accessed 6 September 2026.
12. Semafor. *Google CEO says 75 % of company's new code is AI-generated.* 24 April 2026 (archived 6 September 2026). Reports 25 % in 2024 and 50 % in autumn 2025 as the earlier figures. Primary transcript not located.
13. TechSpot. *Anthropic says more than 90 % of its code is now written by AI.* 14 May 2026, reporting K. Rao on *Invest Like the Best*. Not independently verified.
14. T. Kwa et al. (METR). *Measuring AI Ability to Complete Long Software Tasks.* arXiv:2503.14499, 2025; METR, *Time Horizon 1.1*, 29 January 2026 (archived 4 September 2026). The 320-minute point estimate is Claude Opus 4.5 under TH1.1.
15. Anthropic. *Economic Index report: Cadences.* 26 June 2026 (archived 6 September 2026).
16. J. Becker, N. Rush, B. Barnes, D. Rein (METR). *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity.* 10 July 2025 (archived 6 September 2026).
17. M. R. Morris et al. *Levels of AGI for Operationalizing Progress on the Path to AGI.* arXiv:2311.02462, 2023, v5 September 2025; autonomy levels in Table 2.
18. K. J. K. Feng, D. W. McDonald, A. X. Zhang. *Levels of Autonomy for AI Agents.* arXiv:2506.12469, 2025. Quotation verbatim from the abstract.
19. R. Greenblatt, B. Shlegeris, K. Sachan, F. Roger. *AI Control: Improving Safety Despite Intentional Subversion.* arXiv:2312.06942, 2023.
20. A. Meinke et al. *Frontier Models are Capable of In-context Scheming.* arXiv:2412.04984, 2024.
21. C. Biddulph, A. Kaufman (Redwood Research). *Untrusted advice for AI control.* 27 July 2026 (archived 4 September 2026).
