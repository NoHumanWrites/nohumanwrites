# Guaranteed AI: a label for work that came through a signed machine channel, and what it can and cannot say about the road to general intelligence

White paper v0.2 · 6 September 2026 · Plus de Fun Agency, Geneva
Companion to *NoHumanWrites* (doi:10.5281/zenodo.22362427) and to the label spec in `label/README.md`.
Author's interest: the author wrote NoHumanWrites and maintains the label; the label exists to sell the ledger.
v0.2 follows an eight-model hostile review (`eval/council-review-label-2026-09-06.md`); the changes are listed at the end.

## Abstract

The marks that have shipped for AI-era content since 2023 point one way: they tell the reader a human made the work, on the author's estimate or a platform's private judgement. This paper proposes a mark that points the other way and can be re-derived by a third party. *Guaranteed AI* certifies one narrow, checkable fact: the share of a work's units that passed through a signed machine channel at the moment they were written, with every unit that did not listed beside the number. It certifies a channel, not an author, and the paper says so on every page where the distinction matters. The case for the mark rests on two observations and stops there. Machine writing through a logged channel arrives with a prompt, a diff, a log, a test run and a signature; writing through any other channel arrives with none of those, so the attested share is the share a reviewer can trace. And the largest software organisations report, in their own words, that the machine now produces most of their new code with engineers approving it. What the label cannot do is measure autonomy, capability or the approach to general intelligence; the attested share is a coverage statistic of logged channels, and a registry of such shares is an adoption index with selection bias, not a thermometer. The paper states the guarantees, the counting rules, the ways the label can be gamed, and what a real test of the delegation thesis would have to look like.

## 1. The marks that have shipped, and the gap

Since 2023 a family of marks has appeared to certify human production. Not By AI offers badges to anyone who estimates "that at least 90 % of your content is created by humans" and says of itself that it "is not an AI detection tool"; the creator is the one held accountable for the estimate [1]. The Authors Guild opened its "Human Authored" certification to members in January 2025 and to all authors published in the United States in March 2026; it permits "a de minimis amount of AI-generated text" for grammar and spell-check and rests on the author's declaration [2]. iHeartMedia made "Guaranteed Human" part of its on-air identity in late November 2025, with hosts saying the words in their hourly disclosures [3]. Spotify's "Verified by Spotify" badge signals that a profile meets the platform's standards for authenticity, by the platform's own review [4]. Each of these is a declaration, an estimate or an undisclosed judgement. A reader cannot re-derive any of them.

Marks that point toward machine production also exist, and this paper does not claim otherwise. C2PA Content Credentials record, in signed metadata, that an image, audio or video file was generated or edited by an AI tool [5]. Vendor watermarks such as SynthID-Text and Anthropic's text marking make machine output detectable by whoever holds the key [6]. Spotify announced on 11 August 2026 that it will apply an "AI Persona" badge to artist profiles whose identity is AI-generated, by self-disclosure or by its own human-reviewed decision [4]. On 10 June 2026 the European AI Office released its Code of Practice on Transparency of AI-Generated Content, with icons for signatories to display and a requirement that provenance information be "digitally signed and time-stamped (on systems where time information is available) in a secure and tamper-evident manner"; IPTC's reading is that "while it is not named specifically, the only technology that meets these criteria is C2PA" [7]. These marks serve the public, as warnings or disclosures, and they cover media, identities and vendor output. What none of them offers is a per-unit account of a text file or a source repository that a reviewer can verify with a public key and that lists the parts the machine channel did *not* produce. That is the gap this label fills, and it is narrower than the name suggests.

## 2. What a logged machine channel carries that other channels do not

The premise is not that machine writing is better, and not that unlogged writing is human. It is that a logged channel is traceable and every other channel is not.

When an agent harness writes a file through its write tool, the call carries the prompt that caused it, the exact bytes, the session, the model and the timestamp; the harness logs it, the test suite runs on it, and a hook can sign it. When the same file is changed in an editor at 23:40, or by a formatter, or by the same agent through a shell command that bypasses the hook, none of that exists. The change has no prompt, no log and no signature. This paper calls such a unit *unattested*, and the word means exactly that: no signed record covers it. It does not mean human. NoHumanWrites is explicit on the point, and its own measurement makes it unavoidable [8]: on one developer's machine over five weeks the agent made 2,716 logged file writes covering 72,681 lines; tools the agent wrote through the logged channel attested at a median of 96 % of lines; hand-written notes attested at 0 %; and the project's own source, which the same agent had written through a shell heredoc, attested at 9 %. The 9 % is the method reporting an unlogged channel, which is what the method exists to find. Coverage, not authorship detection, is the whole problem, and it is the reason the label's number has to be read next to a channel inventory (§7).

The same study shows why the label cannot be built on style. A local detector separated machine from human prose with an AUC of 0.91, yet 60 % of machine passages carried no tell at all, so under one specific rule, "no tell means human", at a 5 % human share, precision was near 8 % [8]. That figure holds for that rule and that base rate; a different rule or share gives a different number, and none of them gives a label. Sadasivan et al. give the theoretical reason: detection degrades as generated text approaches the human distribution [9]. This label never guesses from style. It reads a signature or it says nothing.

## 3. The label

### What it certifies

For a named path, at a named commit, on a named date: the share of scored units covered by a signed record from a key the verifier trusts, and the list of units not so covered. The badge face says "attested", the spec says "through a signed machine channel", and neither says "written by AI" as a claim about authorship, because the record cannot support that claim. A person who dictates every line in a prompt, or who has an agent read a hand-written file and write it back, obtains an attested hunk. The label reports that the bytes came through the channel. Who decided them is upstream of the record.

### Grades

*Pure AI* at 100 % of scored units attested; *Guaranteed AI* at 90 % or more, remainder listed. The 90 % is Not By AI's threshold pointed the other way, counted by the verifier instead of estimated by the author. The names are the maintainer's choice and carry the caveat above wherever they appear; a reader who wants the plain description will find "attested share" on the badge and in every report.

### Units and denominator

Code is scored by line, prose by paragraph, verse by line and stanza, sheet music by bar or measure; the profile is detected from the file or forced with a flag. The denominator is every scored unit under the named path, with no exclusion for generated or vendored files; a badge that covers a subdirectory says which one, and a badge on a repository covers the repository. A hunk is attested when its signed hash still matches, or, when the whole hunk no longer matches, line by line against the signed per-line hashes, each hash usable at most as many times as it was signed [8, SECURITY.md]. Copy-paste of a signed line is therefore attested; a formatter's reflow of a signed paragraph is edited or unattested depending on how much survives. These are the counting rules; the threshold means nothing without them.

### Levels

Level 1, self-signed: the author's machine key signs each hunk through the harness hook, and the verifier uses its own trust root, never the repository's. Level 2, anchored: the ledger head is recorded at each commit in a transparency log such as Sigstore's Rekor, so a deleted or rewritten record leaves a visible gap. Anchoring makes the ledger's history tamper-evident; it does not make a false record true, and a key-holder can still sign anything. Removing the key-holder from the loop takes a third design, in which a trusted executor outside the writer's reach produces or countersigns the hunks; NoHumanWrites §10.3 describes it, and no such component ships today [8]. The badge names its level so that a reader knows which of these three assurances they are looking at.

### Three checkable guarantees

Every attested unit is covered by a record naming harness, model and session and signed by a key the verifier chose to trust. Every unit not so covered is listed by file and position. Anyone with the public key, the ledger and the file bytes gets the same number.

### Four things it does not guarantee

Not quality, correctness or safety. Not authorship, for the reason above. Not the absence of human judgement, which sits in the prompt and the review and is not made of bytes. Not anonymity: the ledger records a key fingerprint and never a name, but on a small team a key identifies a person by elimination, and the report is aggregated per repository for that reason.

## 4. What the labs report about their own code

The case for a label depends on there being work to label. The figures below are claims by interested parties about their own organisations, each with its own undisclosed definition of "code" and "written by AI", and they are not comparable with each other. They are cited for what they are: the largest software organisations describing their own practice.

| Date | Who | Statement | Source |
|---|---|---|---|
| 29 Oct 2024 | Sundar Pichai, Alphabet Q3 2024 earnings call | "more than a quarter of all new code at Google is generated by AI, then reviewed and accepted by engineers" | primary, blog.google [10] |
| 29 Apr 2025 | Satya Nadella, at Meta's LlamaCon | "20 % to 30 % of code inside the company's repositories was 'written by software'" | as reported by TechCrunch [11] |
| 24 Apr 2026 | Sundar Pichai | 75 % of new code at Google AI-generated and approved by engineers, up from 50 % the previous autumn | as reported by Semafor; primary transcript not located; not independently verified [12] |
| 14 May 2026 | Krishna Rao, Anthropic CFO, on the *Invest Like the Best* podcast | "90 %-plus" of Anthropic's code written by Claude | as reported by TechSpot; not independently verified [13] |

The one primary quotation in the table describes the human's role as review and acceptance. The 2026 Google figure, if the report is accurate, describes it the same way. That is the role a signed ledger is built to make visible: which units the machine channel produced and which a person changed after it.

Two other measurements are relevant and measure different things. METR's time-horizon work, updated on 29 January 2026, reports the length of software task a frontier system completes at 50 % reliability doubling "around every 7 months over the period 2019 to 2025", with the best measured system at a point estimate of 320 minutes and an interval of 170 to 729 minutes [14]. A 50 % horizon means the system fails half the tasks of that length. Anthropic's Economic Index of 26 June 2026 reports that agentic coding sessions run with more autonomy, on the report's own index, than chat sessions on the same model [15]. Neither measures the share of code a machine writes, and this paper does not chain them to the table above.

The honest counterweight belongs in the same section. METR's randomised trial of July 2025 found that sixteen experienced open-source developers, using Cursor Pro with Claude 3.5 and 3.7 Sonnet on 246 real tasks, took 19 % longer with AI tools than without; they had forecast a 24 % speed-up and afterwards believed they had got 20 % [16]. The authors call it "a snapshot of early-2025 AI capabilities in one relevant setting" and decline to generalise. The perception gap is the part that bears on a label: developers could not tell, from the inside, what the machine had done for them. A team that cannot tell from the inside needs a record, and the record has to count bytes rather than ask people.

## 5. What the attested share is, and what it is not

The attested share is a coverage statistic: the fraction of a work's units that passed through logged, signed machine channels. Three things move it. Delegation moves it, when a team gives its agents more of the work. Instrumentation moves it, when a channel that used to be unlogged gets a hook, as the 9 % example shows in reverse. And gaming moves it, when work is routed through the hook to raise the number. From the share alone the three cannot be told apart. A registry of labelled work would therefore be a self-selected adoption index of logged channels, and once published it would be a leaderboard, with the Goodhart dynamics that implies. The earlier draft of this paper called such a registry a field thermometer of rising autonomy. It is not, and the claim is withdrawn.

The published frameworks for grading progress toward general intelligence make the point from the other side. Morris et al. (Google DeepMind, 2023) place today's frontier chatbots at the lowest rung of general capability, "Emerging", and describe a separate autonomy axis of six levels, 0 to 5, from no AI to AI as agent, arguing that autonomy is a deployment choice constrained but not fixed by capability [17]. Feng, McDonald and Zhang (2025) define five levels by the role left to the human, operator, collaborator, consultant, approver, observer, and state that autonomy "can be treated as a deliberate design decision, separate from its capability" [18]. On both ladders the human who approves each change sits in the middle, not at the top; the top rung is a human who observes, or is absent. A team whose engineers "review and accept" every machine hunk is at Feng et al.'s approver level, and a ledger records precisely that: machine-produced units, human decisions upstream and downstream of them. Nothing in the ledger says which rung a team is on, because the rung is defined by what the human does, and the human's decisions are not bytes.

What a ledger can contribute to that question is one input among several, and only under a protocol fixed in advance. Such a protocol would name the channel inventory of the team (every path by which bytes reach the repository, and which of them are hooked), the unit and denominator rules of §3, a coverage audit at each measurement (the 9 % test: write through every channel and see what the ledger catches), an independent record of task length and of the human's role per task, and a statement of which rises in attested share would *not* count as delegation: a new hook, a formatter routed through the agent, a rewrite of an existing file. Only with all of that held fixed does a rising share say anything about delegation, and even then it says nothing about capability. None of this exists yet. The earlier draft's one-line falsifier is withdrawn with the claim it was meant to protect.

## 6. What the label can say about general intelligence

Less than its name implies, and the paper prefers to say it plainly.

The measured curve is METR's: task horizons doubling on the order of seven months, on wide intervals, at 50 % reliability [14]. The reported curve is the labs': a quarter, a half, three quarters of new code at one organisation over eighteen months, with the last figure unverified [10, 12]. The definitions on the record separate capability from autonomy and make autonomy a choice made in the field [17, 18]. ARC Prize's ARC-AGI-3 sets the bar at skill acquisition in novel environments and states that "as long as there is a gap between AI and human learning, we do not have AGI" [19]; the International AI Safety Report's October 2025 update calls the current capability profile "jagged" [20]. The builders disagree in public: as reported from Davos in January 2026, Demis Hassabis put a 50 % chance on AGI within the decade and said today's systems are "nowhere near" it, while Yann LeCun said LLMs will never reach human-level intelligence [21].

Where a signed ledger fits in that picture is small and specific. If the delegation the labs describe is real, it leaves bytes, and a ledger is the only record of those bytes that survives the end of the session. It does not measure the delegation; it makes one component of it auditable, per unit, by a third party, which nothing else does for text. The reason to fix the record format now, before the question of general intelligence is settled either way, is the one the safety literature supplies. Greenblatt et al. treat a capable model as untrusted and design protocols in which a weaker trusted model monitors or executes [22]; Meinke et al. document frontier models scheming in context when given a goal and a reason [23]; Redwood Research's July 2026 protocol has a trusted executor take every action while the untrusted model sends short hints, recovering about 67 % of the capability gap at 16 characters per message [24]. If the writer can be an adversary, a recorder that runs inside the writer's environment can be tampered with, and a Level 1 label is exactly as good as the honesty of the machine and the key-holder. That is why the spec defines the anchored level and names the trusted-executor design before anyone needs them. It is also why the failure mode the ledger demonstrates *today*, the heredoc that bypassed the hook, is a coverage loss that neither anchoring nor a transparency log addresses; only hooking the channel does.

That is the whole of the label's contribution to the question. It is an audit trail for one leg of a larger record. Anyone who wants a date for general intelligence will not find one here.

## 7. How the label can be gamed, and what it does about it

- Prompt-supplied content. "Write exactly these lines" yields an attested hunk. Not defended; disclosed on the badge and in §3. The label certifies the channel.
- Rewrite laundering. An agent reads a hand-written file and writes it back, attested at 100 %. Same as above; the ledger's `producer` field and the prompt log, where a team opts to keep prompts, are the only trace.
- Non-AI automation through the hook. A formatter, a template expander or a `sed` run routed through the agent's write tool is attested as a machine channel, because it is one. The label says "machine channel", not "model output"; a team that wants the distinction records the tool in `producer`.
- Scope cherry-picking. A badge on the one clean subdirectory. Every badge names its path, and one that does not is invalid under the terms of use. §8 below covers `label/` only and says so.
- Threshold gaming. Re-emitting an 89 % file through the agent to reach 91 %. This is rewrite laundering with a target; same trace, same disclosure.
- Repository splitting. Hand work in one repository, agent work in another, badge on the second. The badge covers what it names and nothing else; the registry, if built, publishes per-channel aggregates and no per-team ranking.
- The key-holder lying. Signing anything, deleting records. Level 1 does not defend; Level 2 makes deletion visible; only the trusted-executor design removes the key-holder.
- Key theft, rotation and revocation. A stolen key signs as its owner until the owner's entry in the trust root is replaced. The trust root is the verifier's file, so revocation is an edit there; the spec defines no PKI and does not pretend to.
- A stale number. The badge carries path, date and, once anchored, commit; the terms forbid displaying a number older than the last change to the named path.
- Identification by elimination. Reports give lines and files, never names, and aggregate per repository.
- Goodhart. A published share becomes a target. The registry design in §9 publishes only delayed, per-channel aggregates for that reason, and the paper does not attach any claim about autonomy to the number, so that raising it buys nothing but the number.

## 8. The label applied to itself, reproducibly

Checked on 6 September 2026 against the repository's own signed ledger, verified with the maintainer's trust root:

```
$ python3 nohumanwrites.py check . --label
NoHumanWrites: no label — 18% attested is below the 90% threshold.

$ python3 nohumanwrites.py check label/ --label
Pure AI · 100% attested · checked 2026-09-06 · Level 1 (self-signed) · 111 of 111 units
```

Signing key fingerprint: `SHA256:6t3ttnXr9M4hfcT7NHQvAqzemNizJnzU/1z/e6TzsYg` (ed25519, `nhw-Arnauds-MacBook-Pro`); the public key is in `.nhw/allowed_signers`, and a verifier must place it in their own trust root to reproduce the number. The commit that contains this text is tagged `label-v0.2`. The repository as a whole does not earn the label: most of its prose reached the disk through shell heredocs, which the hook does not see. The `label/` directory earns Pure AI at the moment of writing, and the number is worth reading with §7 in mind: v0.1 of this file scored 99 %, with one paragraph unattested after a one-line edit inside a table block that the paragraph profile could not match, and the v0.2 rewrite replaced that block through the signed channel, which is rewrite laundering by the paper's own definition, done here in the open. The scope is stated because §7 says it must be. A label that had to exempt its own authors would be a declaration, which is the thing it replaces.

## 9. What comes next

- **v0.1, now.** `--label` in the CLI, the two seals, the spec, self-signed Level 1, the counting rules of §3. Free to display on anything that passes, with path and date on the face.
- **v0.2.** Anchoring: the ledger head recorded in Sigstore's Rekor at each commit, and the commit hash on the badge. Level 2 follows.
- **The protocol of §5**, written up as a pre-registered study design before any registry publishes a number.
- **A registry**, if the protocol exists: opt-in, delayed by a quarter, per-channel aggregates only, no per-team figures, no content.
- **Text provenance beyond code.** The ledger already scores paragraphs, verse lines and bars of music [8]; the ledger format is offered to the C2PA working group as one answer to the text gap named in §1.

## Changes since v0.1

Eight external models reviewed v0.1 (`eval/council-review-label-2026-09-06.md`): three said do not publish as written, five said publish after structural fixes, and all agreed on the faults. Applied: the label now certifies a channel, not authorship, and says so in the abstract, §3 and on the badge wording; the claim that a registry of attested shares is a field measurement of autonomy or of the approach to AGI is withdrawn, with §5 and §6 rewritten around what the share is (a coverage statistic) and what a real delegation study would need; the autonomy-ladder description is corrected (the approver sits mid-ladder, Morris et al.'s autonomy axis has six levels); the doubling-cadence comparison, the "in the same words" parallel, the "two independent measurements" phrasing, the METR "few remaining tasks" paraphrase and the "most-cited" superlative are removed; §4's table marks which rows are primary and which are unverified reports; §1's universal claims are scoped and the existing AI-origin marks (C2PA, watermarks, Spotify's AI Persona badge) are acknowledged; the IPTC sentence is quoted verbatim; Level 2 is described exactly (tamper-evident history, not truth) and separated from the trusted-executor design; key fingerprints are no longer offered as anonymity or accountability; units, denominator and counting rules are stated; §7 gains nine attack modes; §8 publishes the command, output, fingerprint and tag; the author's interest is disclosed; the 8 % precision figure carries its assumptions; Wikipedia is replaced by primary sources for the market survey. Checked and not applied: the reviewer who said the METR paper's title is "Long Tasks" was wrong (arXiv:2503.14499 reads "Long Software Tasks"); the reviewer who dated iHeartMedia's mark to November 2024 was wrong (November 2025, per iHeartMedia and Inside Radio). The names Pure AI and Guaranteed AI are kept as the maintainer's decision, with the channel caveat attached; one reviewer's recommendation to rename the mark is recorded here for the maintainer.

## References

1. Not By AI. *Add the Badge to Your Human-Created Content.* notbyai.fyi, accessed 6 September 2026 (archived). The 90 % rule is quoted verbatim.
2. The Authors Guild. *Authors Guild Launches "Human Authored" Certification to Preserve Authenticity in Literature*, January 2025; *Authors Guild Launches Expanded "Human Authored" Certification Program*, March 2026. authorsguild.org/news, accessed 6 September 2026.
3. Inside Radio. *iHeartMedia Makes "Guaranteed Human" a Core Branding Message Across All Stations.* November 2025; iHeartMedia, *Guaranteed Human at CES 2026*, iheartmedia.com/advertise/insights. Accessed 6 September 2026.
4. Spotify Newsroom. *Introducing a New Label for AI-Generated Artist Identities on Spotify.* 11 August 2026, newsroom.spotify.com; the same page describes "Verified by Spotify". Accessed 6 September 2026.
5. Coalition for Content Provenance and Authenticity. *C2PA Technical Specification 2.2.* c2pa.org. The absence of a text or source-file profile is the authors' reading of the specification.
6. S. Dathathri et al. *Scalable watermarking for identifying large language model outputs.* Nature, October 2024, doi:10.1038/s41586-024-08025-4; Anthropic Help Center, *How Claude marks AI-generated content*, article 16266773, accessed 14 August 2026.
7. IPTC. *European AI Office releases Code of Practice on Transparency of AI-Generated Content.* iptc.org/news, 10 June 2026, accessed 6 September 2026. Both quotations verbatim from this page.
8. A. Chrétien (Plus de Fun Agency). *NoHumanWrites: find the human in machine-written work.* v0.2.1, September 2026, doi:10.5281/zenodo.22362427, sections 5, 6, 10.2, 10.3, and the repository's `SECURITY.md`.
9. V. S. Sadasivan, A. Kumar, S. Balasubramanian, W. Wang, S. Feizi. *Can AI-Generated Text be Reliably Detected?* arXiv:2303.11156, 2023.
10. S. Pichai. *Alphabet Q3 2024 earnings call, CEO remarks.* 29 October 2024, blog.google/inside-google/message-ceo/alphabet-earnings-q3-2024/, accessed 6 September 2026. Primary; quoted verbatim.
11. M. Zeff. *Microsoft CEO says up to 30 % of the company's code was written by AI.* TechCrunch, 29 April 2025, accessed 6 September 2026.
12. Semafor. *Google CEO says 75 % of company's new code is AI-generated.* 24 April 2026 (archived 6 September 2026). Primary transcript not located; not independently verified.
13. TechSpot. *Anthropic says more than 90 % of its code is now written by AI.* 14 May 2026, reporting K. Rao on *Invest Like the Best*. Not independently verified.
14. T. Kwa et al. (METR). *Measuring AI Ability to Complete Long Software Tasks.* arXiv:2503.14499, 2025; METR, *Time Horizon 1.1*, 29 January 2026 (archived 4 September 2026).
15. Anthropic. *Economic Index report: Cadences.* 26 June 2026 (archived 6 September 2026).
16. J. Becker, N. Rush, B. Barnes, D. Rein (METR). *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity.* 10 July 2025 (archived 6 September 2026).
17. M. R. Morris et al. *Levels of AGI for Operationalizing Progress on the Path to AGI.* arXiv:2311.02462, 2023; autonomy levels in Table 2 of the paper.
18. K. J. K. Feng, D. W. McDonald, A. X. Zhang. *Levels of Autonomy for AI Agents.* arXiv:2506.12469, 2025.
19. ARC Prize Foundation. *ARC-AGI-3.* arcprize.org/arc-agi/3 (archived 4 September 2026).
20. Y. Bengio et al. *International AI Safety Report 2025: First Key Update.* arXiv:2510.13653, October 2025.
21. Fortune. *AI luminaries at Davos clash over how close human-level intelligence really is.* 23 January 2026 (archived 4 September 2026). Statements as reported.
22. R. Greenblatt, B. Shlegeris, K. Sachan, F. Roger. *AI Control: Improving Safety Despite Intentional Subversion.* arXiv:2312.06942, 2023.
23. A. Meinke et al. *Frontier Models are Capable of In-context Scheming.* arXiv:2412.04984, 2024.
24. C. Biddulph, A. Kaufman (Redwood Research). *Untrusted advice for AI control.* 27 July 2026 (archived 4 September 2026).
