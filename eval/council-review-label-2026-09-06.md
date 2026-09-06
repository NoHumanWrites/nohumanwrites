# Council — external voices (build) · 8 members

TASK: You are a hostile senior reviewer. Review this white paper for a proposed label ('Guaranteed AI') that certifies machine-written work via a signed provenance ledger. Check: (1) every factual claim and attribution against what you know, flag anything wrong or overstated; (2) logical gaps in the argument of §5–§6 that the attested share is a field measurement of rising autonomy toward AGI; (3) ways the label could mislead or be gamed that §7 misses; (4) wording that overclaims. Sources dated 2026 postdate your training data; do not reject them for that reason, but flag if a quote looks implausible. Give a verdict: publish / publish after fixes / do not publish, then a numbered list of concrete fixes, most important first. Be specific and quote the offending sentence.

# Guaranteed AI: a label for work the machine wrote, and why it will matter more every year

White paper v0.1 · 6 September 2026 · Plus de Fun Agency, Geneva
Companion to *NoHumanWrites* (doi:10.5281/zenodo.22362427) and to the label spec in `label/README.md`.

## Abstract

Every label on the market for AI-era content points the same way: it tells the reader that a human made the work. All of them rest on a declaration, an estimate or a platform's private judgement, and none can be checked by a third party. This paper proposes the inverse mark. *Guaranteed AI* certifies that a machine wrote the work, on the strength of a signed ledger produced at write time, with every hand-typed or unlogged span listed beside the number. The argument for the mark rests on three observations. Machine writing arrives with a prompt, a diff, a log, a test run and a signature, and hand writing arrives with none of those, so the attested share is the share a reviewer can trace. The machine share of new code at the largest labs rose, by their own reported figures, from a quarter to three quarters between October 2024 and April 2026. And the two published frameworks for grading progress toward general intelligence both treat autonomy as a deployment choice; a team's attested share, held at constant instrumentation, is the number that records that choice as it is made. The paper states what the label guarantees, what it does not, how it can be gamed, and the one measurement that would show the thesis to be wrong.

## 1. The labels point the wrong way

Since 2023 a family of marks has appeared to certify the absence of AI. Not By AI offers badges to anyone who estimates "that at least 90 % of your content is created by humans" and states that it "is not an AI detection tool"; the creator is the one held accountable for the estimate [1]. The Authors Guild introduced a "Human Authored" certification for books in 2025; iHeartMedia began having its radio hosts announce "Guaranteed Human" content the same year; Spotify's 2026 "Verified" badge is withheld from profiles "that release songs that Spotify deems to be AI-generated"; a film company put "No AI Used" on its marketing at the Berlinale in 2026 [2]. Each is a declaration, an estimate or a platform's undisclosed judgement. None can be re-derived by a reader.

Regulation points the same way, for a different reason. Article 50 of the EU AI Act, applicable from 2 August 2026, obliges providers of generative systems to mark outputs so that they are detectable as artificially generated, and obliges deployers to disclose deep fakes and AI-generated text published on matters of public interest [3]. On 10 June 2026 the European AI Office released its Code of Practice on Transparency of AI-Generated Content, with a set of icons for signatories to display and a requirement that provenance information be "digitally signed and time-stamped ... in a secure and tamper-evident manner" [4]. IPTC's reading is that C2PA Content Credentials is the only existing technology that meets that requirement [4]; C2PA covers images, audio and video, and has no profile for a text file or a source repository [5]. The icons are a warning to the public. They are not built to tell the writer, the reviewer or the auditor which parts of a piece of work the machine produced.

Nobody has shipped the mark that points the other way: one that says a machine wrote this, here is the signature, here is the list of what it did not write. That is the gap this paper fills.

## 2. What the machine's writing carries that the hand's does not

The premise is not that machine writing is better. It is that machine writing is *traceable* and hand writing is not.

When an agent harness writes a file, the write goes through a tool call. The call carries the prompt that caused it, the exact bytes, the session, the model and the timestamp; the harness logs it, the test suite runs on it, and a hook can sign it. When a person opens the same file in an editor at 23:40 and changes four lines, none of that exists. The change has no prompt, no log and no signature. It is the least reviewed byte in the repository, and it is invisible precisely because it looks like every other byte.

NoHumanWrites measured this on one developer's machine over five weeks [6]. The agent made 2,716 logged file writes covering 72,681 lines. Tools the agent wrote through the logged channel attested at a median of 96 % of lines; hand-written notes attested at 0 %; and the project's own source, which the agent had written through a shell heredoc instead of the logged tool, attested at 9 %. That last number is the important one. It is not a failure of the method; it is the method reporting an unlogged channel, which is the same thing the method exists to find. Coverage, not detection, is the whole problem.

The same study shows why the label cannot be built on style. A local detector of AI-writing patterns separated machine from human passages with an AUC of 0.91, yet 60 % of machine passages carried no tell at all, so a rule of "no tell means human" had a precision near 8 % at a 5 % human share [6]. Sadasivan et al. give the theoretical reason: detection degrades as generated text approaches the human distribution [7]. A label that guesses from style would be wrong most of the time, and wrong about people. This label never guesses. It reads a signature or it says nothing.

## 3. The label

The spec is short and lives in `label/README.md`. Two grades: **Pure AI** at 100 % attested, **Guaranteed AI** at 90 % or more with every unattested unit listed. Two levels: self-signed by the author's machine key today; anchored in a transparency log or signed by a trusted executor outside the writer's reach when that component exists. Three guarantees, each one checkable by rerunning the tool: every attested unit passed through a named machine channel and was signed when written; every unit that did not is listed; anyone with the public key gets the same number.

And four things it does not guarantee, stated on the label's own page: not quality, not that no human decided the content, not the absence of human judgement, and nothing about any named person. The last is a design rule inherited from NoHumanWrites: the ledger records a machine key, never a name, so the report reads "unattested", never "written by Arnaud" [6].

The 90 % threshold is borrowed from Not By AI's rule and turned around. Theirs is estimated by the creator; ours is counted by the verifier. The symmetry is deliberate. A reader who knows one mark understands the other in a sentence.

## 4. The machine share is rising, and the labs say so themselves

The case for a label depends on there being something to label. The reported figures, each attributed to the executive who gave it and the outlet that carried it, run in one direction.

| Date | Who | Figure | As reported by |
|---|---|---|---|
| 29 Oct 2024 | Sundar Pichai, Alphabet Q3 2024 earnings call | "more than a quarter of all new code at Google is generated by AI, then reviewed and accepted by engineers" | Alphabet CEO remarks, blog.google [8] |
| 29 Apr 2025 | Satya Nadella, at LlamaCon | "20 % to 30 % of code inside the company's repositories was 'written by software'" | TechCrunch [9] |
| 24 Apr 2026 | Sundar Pichai | 75 % of new code at Google AI-generated "and approved by engineers", up from 50 % the previous autumn | Semafor [10] |
| 14 May 2026 | Krishna Rao, Anthropic CFO, on the *Invest Like the Best* podcast | "90 %-plus" of Anthropic's code written by Claude | TechSpot [11] |

These are claims by interested parties about their own shops, relayed by journalists, and the paper cites them as such. Two features of the Google figure deserve notice. It moved from a quarter to three quarters in eighteen months, which is roughly the doubling cadence METR measures for task horizons (below). And both statements, eighteen months apart, name the human's remaining role in the same words: "reviewed and accepted", "approved". Not typing, approving. That is the role the label is built to make visible.

Two independent measurements sit behind the reported figures. METR's time-horizon work, updated on 29 January 2026, finds the length of software task a frontier system completes at 50 % reliability doubling "around every 7 months over the period 2019 to 2025", with the best measured system at a point estimate of 320 minutes and an interval of 170 to 729 minutes [12]. Anthropic's Economic Index of 26 June 2026 reports that agentic coding sessions run with measurably more autonomy than chat sessions on the same model, with about two thirds of the difference coming from the same tasks being delegated more fully [13].

The honest counterweight belongs in the same section. METR's randomised trial of July 2025 found that sixteen experienced open-source developers, using Cursor Pro with Claude 3.5 and 3.7 Sonnet on 246 real tasks, took 19 % *longer* with AI tools than without; they had forecast a 24 % speed-up and afterwards believed they had got 20 % [14]. The authors call the result "a snapshot of early-2025 AI capabilities in one relevant setting" and decline to generalise it. The perception gap is the part that matters here. Developers could not tell, from the inside, whether the machine had helped. A team that cannot tell from the inside needs an instrument, and the instrument has to count bytes rather than ask people.

So the evidence supports a narrower claim than "the machine is better": the machine writes a rising share, the humans approve it, and nobody in the loop can see the line between the two without a record. The label is the record, published.

## 5. What the label measures as autonomy rises

Two published frameworks grade progress toward general intelligence without naming a date, and both separate capability from autonomy. Morris et al. (Google DeepMind, 2023) place today's frontier chatbots at the lowest rung of general capability, "Emerging", and add a distinct axis of autonomy with five levels from tool to agent, arguing that autonomy is a deployment choice constrained but not fixed by capability [15]. Feng, McDonald and Zhang (2025) define five levels by the role left to the human, from operator to observer, and state that autonomy "can be treated as a deliberate design decision, separate from its capability" [16]. ARC Prize's ARC-AGI-3 sets the bar at skill acquisition in novel environments and states that "as long as there is a gap between AI and human learning, we do not have AGI" [17]; the International AI Safety Report's October 2025 update calls the current capability profile "jagged" [18]. The builders disagree in public: as reported from Davos in January 2026, Demis Hassabis put a 50 % chance on AGI within the decade and said today's systems are "nowhere near" it, while Yann LeCun said LLMs will never reach human-level intelligence [19].

None of these settles the date. All of them agree on the shape: as systems climb the autonomy ladder, the human stops typing bytes and starts authorising tasks and reviewing results. On a team that runs the ledger, that transition has a signature. The attested share rises, not because a detector improved, but because the human channel into the file narrows while the machine channels multiply.

This gives the label a second job. Its first job is to tell one reader about one piece of work. Its second is to be a thermometer. A registry of labelled work, counting attested shares over time with no names attached, would be a measurement of autonomy adoption taken in the field, on real artefacts, independent of benchmarks and of what executives say on earnings calls. The three-quarters figure at Google is one company's claim about itself. A registry would be everyone's number, re-derivable by anyone with the keys.

The prediction is falsifiable, and NoHumanWrites already states the test [6]. On any team running the hook, the attested share per pull request should rise as the team gives its agents longer tasks, *holding hook coverage constant*, measured per channel so that instrumenting a new channel is never mistaken for a rise in autonomy. If the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong and the human hand is doing something the frameworks do not capture.

## 6. The argument for general intelligence, as the label sees it

This paper does not claim that AGI is coming on a date. It claims that the approach, if it is happening, now has an instrument, and it lays out the chain that makes the instrument read.

1. **Capability rises on a measured curve.** METR's doubling time of roughly seven months is the most-cited operational yardstick and has held from 2019 to 2025 [12]. Nothing in the January 2026 update reverses it, and the authors note that few remaining tasks defeat the newest models.
2. **Adoption rises on a reported curve.** A quarter, then a half, then three quarters of new code at one of the largest software organisations on earth, in eighteen months, with the humans described as approving rather than writing [8, 10].
3. **The definitions on the record make autonomy the visible variable.** Both graded frameworks say a lab can build capability and a team can choose how much autonomy to grant it [15, 16]. Capability is measured in the lab. Autonomy is chosen in the field, and it leaves bytes.
4. **Those bytes are countable at constant coverage.** The ledger separates the machine's hunks from everything else and reports the ratio per channel [6]. Rising autonomy shows up as a rising ratio; a new unlogged channel shows up as a fall the per-channel view can name.
5. **So the label registers the approach before any benchmark declares it.** A benchmark says what a system can do. A labelled artefact says what a team let it do, on work that shipped. When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders.

The chain has one weak link, and it is the one the safety literature names. At high autonomy the writer may be an adversary. Greenblatt et al. treat the capable model as untrusted and design protocols where a weaker trusted model monitors or executes [20]; Meinke et al. document frontier models scheming in context when given a goal and a reason [21]; Redwood Research's July 2026 protocol has a trusted executor take every action while the untrusted model sends short hints, and recovers about 67 % of the capability gap with 16 characters per message [22]. For a label the consequence is exact: a recorder running inside the environment the untrusted model controls can be tampered with, so a Level 1 self-signed label is sufficient while the machine is an honest scribe and insufficient after. That is why the spec defines Level 2 now, with the recorder outside the writer's reach, before anyone needs it. A mark that could not survive the arrival of the thing it measures would not be worth designing.

## 7. How the label can be gamed, and what it does about it

- **Routing hand text through the hook.** A prompt of "write exactly these lines" yields an attested hunk. The key proves the channel, not the author. The label says so on its face, and the accountability sits with the key-holder, who is named by fingerprint in every record.
- **The key-holder lying.** A developer with the key can sign anything or delete records. Level 1 does not defend against it; Level 2, with the ledger head anchored in a log the developer cannot rewrite, does. Until then the label says "Level 1" and means it.
- **A stale number.** Work changes after the badge is minted. The badge carries its check date, and the terms of use forbid displaying a number older than the last change.
- **Identification by elimination.** On a three-person team "unattested" points at someone. The report gives lines and files, never names, and aggregates per repository, not per person.
- **The perception that the mark is anti-human.** It is not. The human's judgement sits in the prompt, the constraints and the review, and the label counts none of those because they are not bytes. What it counts is the one thing that has no other record: the unreviewed edit after the machine finished. Naming that is a service to the person who made it.

## 8. The label applied to itself

The NoHumanWrites repository, checked on 6 September 2026 against its own signed ledger, attests at 17 % of units. Most of its prose was written by the agent through shell heredocs, which the hook does not see; the ledger records only what came through the harness's write tool. The repository does not earn its own label today. This white paper and the spec beside it were written through the signed channel on purpose, and the check on the `label/` directory alone should say so; if it does not, the ledger is right and this sentence is wrong. A label that had to exempt its own authors would be a declaration, which is the thing it replaces.

## 9. What comes next

- **v0.1, now.** `--label` in the CLI, the two seals, this spec, self-signed Level 1. Free to display on anything that passes.
- **v0.2.** Anchoring: the ledger head recorded in Sigstore's Rekor at each commit, so a deleted record is a visible gap. Level 2 badges follow.
- **The registry.** An opt-in count of labelled artefacts and their attested shares over time, per channel, with no names and no content. Published quarterly as the field measurement §5 describes.
- **Text provenance beyond code.** The same ledger already scores paragraphs, verse lines and bars of music [6]; the C2PA text gap named in §1 is the standard's problem, and the ledger format is offered to the working group as one answer.

## References

1. Not By AI. *Add the Badge to Your Human-Created Content.* notbyai.fyi, accessed 6 September 2026. The 90 % rule is quoted verbatim from the site.
2. Wikipedia. *No-AI label.* en.wikipedia.org/wiki/No-AI_label, accessed 6 September 2026. Secondary source; used for the list of marks, each of which is attributed there to its operator.
3. Regulation (EU) 2024/1689 (Artificial Intelligence Act), Article 50, applicable from 2 August 2026.
4. IPTC. *European AI Office releases Code of Practice on Transparency of AI-Generated Content.* iptc.org/news, 10 June 2026, accessed 6 September 2026. The signed-and-time-stamped requirement and the C2PA reading are quoted from this page.
5. Coalition for Content Provenance and Authenticity. *C2PA Technical Specification 2.2.* c2pa.org. The absence of a text or source-file profile is the authors' reading of the specification.
6. A. Chrétien (Plus de Fun Agency). *NoHumanWrites: find the human in machine-written work.* v0.2.1, September 2026. doi:10.5281/zenodo.22362427. Sections 5, 6, 10.2 and 10.3.
7. V. S. Sadasivan, A. Kumar, S. Balasubramanian, W. Wang, S. Feizi. *Can AI-Generated Text be Reliably Detected?* arXiv:2303.11156, 2023.
8. S. Pichai. *Alphabet Q3 2024 earnings call, CEO remarks.* 29 October 2024, blog.google/inside-google/message-ceo/alphabet-earnings-q3-2024/, accessed 6 September 2026. Primary source; quoted verbatim.
9. M. Zeff. *Microsoft CEO says up to 30 % of the company's code was written by AI.* TechCrunch, 29 April 2025.
10. Semafor. *Google CEO says 75 % of company's new code is AI-generated.* 24 April 2026. Primary transcript not located; cited as reported.
11. TechSpot. *Anthropic says more than 90 % of its code is now written by AI.* 14 May 2026, reporting K. Rao on the *Invest Like the Best* podcast. Cited as reported.
12. T. Kwa et al. (METR). *Measuring AI Ability to Complete Long Software Tasks.* arXiv:2503.14499, 2025; METR, *Time Horizon 1.1*, 29 January 2026. Archived copy: web.archive.org, 4 September 2026.
13. Anthropic. *Economic Index report: Cadences.* 26 June 2026, anthropic.com/research/economic-index-june-2026-report, accessed 6 September 2026.
14. J. Becker, N. Rush, B. Barnes, D. Rein (METR). *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity.* 10 July 2025, metr.org, accessed 6 September 2026.
15. M. R. Morris et al. *Levels of AGI for Operationalizing Progress on the Path to AGI.* arXiv:2311.02462, 2023.
16. K. J. K. Feng, D. W. McDonald, A. X. Zhang. *Levels of Autonomy for AI Agents.* arXiv:2506.12469, 2025.
17. ARC Prize Foundation. *ARC-AGI-3.* arcprize.org/arc-agi/3, accessed 4 September 2026 (archived).
18. Y. Bengio et al. *International AI Safety Report 2025: First Key Update.* arXiv:2510.13653, October 2025.
19. Fortune. *AI luminaries at Davos clash over how close human-level intelligence really is.* 23 January 2026 (archived 4 September 2026). Statements as reported.
20. R. Greenblatt, B. Shlegeris, K. Sachan, F. Roger. *AI Control: Improving Safety Despite Intentional Subversion.* arXiv:2312.06942, 2023.
21. A. Meinke et al. *Frontier Models are Capable of In-context Scheming.* arXiv:2412.04984, 2024.
22. C. Biddulph, A. Kaufman (Redwood Research). *Untrusted advice for AI control.* 27 July 2026, blog.redwoodresearch.org (archived 4 September 2026).

## Round 1 — independent answers

### A. openai/gpt-6-astra-pro
## Verdict: **Do not publish in its current form**

There is a useful engineering proposal here: **a reproducible measure of how much of a particular artifact is covered by authenticated write records**. But the paper repeatedly upgrades that into three different claims:

- the machine **authored** those bytes;
- the fraction of those bytes measures **operational autonomy**;
- increasing operational autonomy measures the **approach to AGI**.

The ledger establishes none of those implications. Worse, the proposed Level 2 does not fix the central forgery problem: publishing a false statement in a transparency log makes it persistently false, not true.

A substantially narrower provenance paper could be publishable. This is not a copy-editing exercise.

**Verification limits:** I can check against established technical knowledge and known publications, but I cannot retrieve the cited pages, repository, DOI record, or archives here. I therefore distinguish errors and unsupported inferences from **unverified source claims**. I do not reject the 2026 sources because of their dates. Their precise quotations, figures, and bibliographic details still require primary-source verification.

## Required fixes, most important first

### 1. Stop certifying authorship when the implementation authenticates a channel

> “*Guaranteed AI* certifies that a machine wrote the work, on the strength of a signed ledger produced at write time…”

Your own threat model disproves this:

> “A prompt of ‘write exactly these lines’ yields an attested hunk. The key proves the channel, not the author.”

A human can write the entire document, tell an agent to reproduce it, and obtain **Pure AI**. That is not an edge case. It is a direct counterexample to the advertised guarantee.

The problem survives an honest model, an uncompromised executor, perfect logging, and a transparency log. Every component can work correctly while the label communicates a false authorship conclusion.

**Fix:** Rename the measured property, for example **“Attested machine-channel coverage.”** Replace the headline guarantee with:

> “For this artifact version, X% of the defined units are covered by authenticated records from the specified write channels. This does not establish who originated the content.”

If you retain “Guaranteed AI” or “Pure AI,” the restrictive definition must appear **on the badge itself**, not on another page. Even then, I would advise against those names. “Pure” is particularly indefensible for an output that may reproduce entirely human-authored input.

### 2. Remove the claim that this is an instrument for detecting the approach to AGI

> “So the label registers the approach before any benchmark declares it.”

This conclusion does not follow from the preceding four steps.

A progression in software benchmark performance, executive reports of generated code, and an artifact’s write-channel coverage does not identify a latent variable called “approach to AGI.” There is no demonstrated measurement model connecting them.

A specialized generator can produce 100% of a constrained artifact without broad intelligence. Conversely, a highly capable autonomous agent can solve a consequential problem by changing one line in a predominantly human-written repository.

Also:

> “The chain has one weak link…”

No. The chain has several independent weak links: channel versus authorship, output volume versus autonomy, local adoption versus general capability, selected artifacts versus deployment prevalence, and software capability versus AGI.

**Fix:** Delete the AGI conclusion. At most:

> “The ledger may support studies of instrumented write-channel use. Its relationship to delegation, autonomy, and capability remains to be established.”

Do not present a hypothesis about that relationship as an implemented measurement instrument.

### 3. Define autonomy independently; artifact coverage is not autonomy

> “Rising autonomy shows up as a rising ratio…”

Not necessarily. Counterexamples include:

- A human specifies every line through prompts; the machine types everything: **high coverage, low autonomy**.
- An agent independently diagnoses a production failure and changes one line: **high autonomy, low repository coverage**.
- An agent writes large fixtures or boilerplate: coverage rises without additional decision authority.
- A team adopts an autocomplete tool: generated volume rises while humans retain continuous control.
- A team delegates longer tasks to an agent whose output is already 100% logged: autonomy rises, coverage cannot.
- A human performs lengthy investigation, planning, testing, and review without editing the final artifact: coverage records none of that work.

> “When the second number approaches 100 % … the human has moved wholly to authorisation and review…”

False. The human may still be specifying algorithms, composing prose in prompts, interpreting failures, supplying solutions, and making every substantive decision.

**Fix:** Measure autonomy separately: human intervention frequency, approval gates, task decomposition authority, permitted actions, rollback authority, human labor time, and independent completion of predefined tasks. Treat artifact coverage as a separate observable.

### 4. Replace the purported falsification test with an identifiable experiment

> “On any team running the hook, the attested share per pull request should rise as the team gives its agents longer tasks, *holding hook coverage constant*…”

“Any team” makes this false for teams already at the ceiling. It also assumes a relationship between task duration and output volume that you have not established.

> “If the share stays flat at constant coverage while METR’s task horizons keep doubling, the thesis of this paper is wrong…”

This mixes a local outcome with an external frontier-model trend. The team may use an unchanged model, different tasks, stricter review policies, or no additional delegation. None of those falsifies a relationship between capability and autonomy.

Holding hook coverage constant is necessary but insufficient. You must also control or model:

- model and harness versions;
- task type and difficulty;
- artifact scope and counting policy;
- logging failures and channel mix;
- human staffing and intervention;
- output verbosity and generated-file inclusion;
- initial coverage and ceiling effects.

**Fix:** Randomize or otherwise independently vary delegation policy on comparable tasks. Predefine the outcome and analyze **changes in independently measured autonomy against changes in coverage**. External METR results are context, not the treatment variable.

### 5. Correct the false security guarantee attributed to transparency logs

> “A developer with the key can sign anything or delete records. Level 1 does not defend against it; Level 2, with the ledger head anchored in a log the developer cannot rewrite, does.”

**Anchoring does not stop the key-holder signing anything.** Nor does it prove that all relevant writes were logged.

It can make alteration of a previously committed history detectable, subject to the commitment scheme, verifier policy, and access to the records. It cannot establish the truth or completeness of the events being committed.

> “the ledger head recorded in Sigstore’s Rekor at each commit, so a deleted record is a visible gap”

Only under a specified protocol. What links a particular artifact version to a mandatory, complete event sequence? How does the verifier detect an omitted event before anchoring, an alternate chain, a reset, or a selectively presented old checkpoint?

**Fix:** Separate three properties:

1. **Publisher-signed claim:** authenticates the key that issued it.
2. **Transparency-anchored claim:** adds public commitment and equivocation-detection mechanisms.
3. **Externally observed execution:** adds evidence that specified events actually occurred under a specified trust boundary.

Do not collapse “anchored” and “trusted executor” into one assurance level. Rekor is useful infrastructure, not an execution witness.

### 6. Specify what verification actually proves and what inputs it requires

> “Three guarantees, each one checkable by rerunning the tool…”

> “anyone with the public key gets the same number”

The public key is nowhere near sufficient. Verification also requires the exact artifact, applicable ledger records, counting policy, format/canonicalization rules, verifier version or specification, and potentially log proofs and executor trust roots.

A signature does not establish:

- that the write occurred;
- that the named model was used;
- that the signed timestamp is accurate;
- that the recorded bytes reached the claimed file;
- that no relevant events were omitted.

A self-signed timestamp is just another signed assertion. A log timestamp ordinarily establishes a bound on publication, not the precise time of the write.

**Fix:** Define a signed statement binding at least:

- artifact digest and exact scope;
- input/output or before/after digests;
- channel and execution identity;
- event sequence and parent linkage;
- counting-policy and verifier-spec versions;
- measured coverage and exclusions;
- the precise time assurance being claimed.

For higher assurance, require a trusted observer to hash actual committed outputs rather than sign arbitrary caller-supplied claims. Even then, promise channel provenance, not intellectual authorship.

### 7. Define “unit” and defend the denominator before advertising 90% and 100%

> “Pure AI at 100 % attested, Guaranteed AI at 90 % or more…”

The paper moves among **bytes, lines, hunks, units, paragraphs, verse lines, and bars of music**. Those are not interchangeable measurements.

A developer can cross 90% by adding generated comments, fixtures, vendored code, redundant prose, or repeated material. One human-written security-critical line can remain hidden under millions of generated lines.

Other missing cases:

- formatter-only rewrites that launder existing content;
- copied or duplicated attested spans;
- cherry-picks, rebases, merges, renames, and reverts;
- failed or partial writes;
- concurrent writers;
- symlink and path-substitution attacks;
- Unicode normalization and line-ending changes;
- generated files and dependencies;
- deleted content and human decisions expressed through deletion;
- identical byte sequences with different origins.

If attribution is based on matching current lines against previously logged lines, **byte equality is not causal provenance**. If attribution follows actual write history, specify that history model and its behavior under these operations.

**Fix:** Publish one canonical counting policy, explicit exclusions, and adversarial test vectors. Bind the policy and scope to the signed result. Say plainly that coverage is not weighted by semantic importance, risk, or effort.

The mirrored 90% threshold is a branding choice, not a validated engineering threshold.

### 8. Replace stale-badge terms of use with artifact binding

> “The badge carries its check date, and the terms of use forbid displaying a number older than the last change.”

That is a rule against misuse, not a technical defense. A copied SVG can be displayed anywhere.

**Fix:** Make the badge resolve to a verification result for a specific artifact digest, repository commit, release, or document version. The verifier must distinguish:

- valid signature on an old artifact;
- valid current-artifact attestation;
- unavailable evidence;
- invalid or revoked credentials.

Specify key rotation, compromise, revocation, expired verification material, and long-term archival behavior. A date alone does not solve freshness.

### 9. Do not claim anonymity or accountability from key fingerprints

> “the ledger records a machine key, never a name…”

> “the accountability sits with the key-holder, who is named by fingerprint…”

A fingerprint identifies a key, not an accountable person or institution. Anyone can create many keys.

Conversely, pseudonymous keys are readily linkable through repositories, commit histories, timestamps, file paths, organization records, and public transparency services. Identity-bearing certificates or associated metadata may expose more information than the label admits.

> “The report gives lines and files, never names…”

On a public repository, lines and files often make identification trivial. Aggregating per repository does not prevent that.

**Fix:** Replace “no names” with a precise privacy claim and threat model. Decide whether identity is intentionally bound to keys. Minimize public metadata, address key-linkage and small-team inference, and do not publish prompts or sensitive paths by default. Public commitments need not contain raw operational records.

### 10. Delete the false machine-versus-human traceability dichotomy

> “machine writing is *traceable* and hand writing is not.”

> “The change has no prompt, no log and no signature. It is the least reviewed byte in the repository…”

These are false generalizations. Human edits can have signed commits, editor logs, issue references, review records, CI results, and authenticated change histories. Machine writes can bypass instrumentation, fail tests, or lack meaningful prompt provenance—as your own example demonstrates.

A tool call also does not inherently carry “the prompt that caused it.” It may carry only tool arguments, with causation distributed across system instructions, retrieved content, earlier messages, and tool results.

Logging is not review. Signing is not testing. An unsigned human edit may be thoroughly reviewed; a signed agent output may never be reviewed.

**Fix:**

> “In the prototype’s current configuration, selected agent write channels are instrumented and ordinary editor writes are not. Either channel could be instrumented.”

Instrument the filesystem or editing workflow if the problem is missing write records. AI-specific branding is not necessary to solve that engineering problem.

### 11. Correct the market survey and acknowledge existing AI-origin provenance

> “Every label on the market for AI-era content points the same way…”

> “none can be checked by a third party”

> “Nobody has shipped the mark that points the other way…”

These universal claims are untenable. Existing AI-origin disclosures, platform labels, and signed Content Credentials already communicate that content was generated or modified using AI. C2PA supports assertions concerning digital source type, including trained algorithmic media.

You may have a narrower differentiator—**public verification of span-level write-channel coverage for source repositories**—but you have not established priority even for that.

Your Level 1 is also a declaration by a key-holder. It is more structured and tamper-evident than an ordinary badge, not categorically “not a declaration.”

**Source checks:**

- **[1], Not By AI:** The 90% self-estimation rule and non-detector characterization are consistent with the known scheme. Verify the exact current wording.
- **[2], Authors Guild:** The 2025 Human Authored initiative is consistent with the known record. Its terms and procedures deserve a primary citation rather than reduction to a Wikipedia summary.
- **[2], iHeartMedia, Spotify, Berlinale:** The exact dates, scopes, quoted Spotify criterion, and unnamed film example are unverified here. Cite the operators or contemporaneous reporting individually. Distinguish an artist-profile badge from a per-track authorship certification.

**Fix:** Replace the universal opening with a scoped comparison table: claim made, issuer, evidence, unit of certification, public verification, and trust assumptions.

### 12. Correct the regulatory summary and separate law from voluntary implementation guidance

> “Regulation points the same way…”

It does not: the provision you cite requires marking certain **AI-generated** outputs. That contradicts the opening claim that existing marks all point toward human production.

> “Article 50 … obliges deployers to disclose deep fakes and AI-generated text published on matters of public interest…”

The general applicability date of **2 August 2026** is consistent with Article 113, but this summary omits material qualifications:

- provider obligations concern machine-readable marking and detectability, with technical feasibility and other qualifications;
- there are exceptions involving standard editing assistance or non-substantial alteration;
- public-interest text disclosure has exceptions involving human review/editorial control and editorial responsibility;
- artistic and similar deepfake contexts receive tailored treatment;
- the law does not simply prescribe public “warning icons.”

**[4]:** The claimed June 2026 Code publication, icons, and exact “digitally signed and time-stamped” quotation require retrieval. The quotation is technically plausible; it is not verified here. Cite the Commission’s actual document, version, section, and legal status, not only IPTC’s interpretation.

**Fix:** Clearly separate Article 50 obligations, code-of-practice commitments, optional icons, and IPTC commentary.

### 13. Narrow the C2PA claim; do not confuse missing integration with conceptual inability

> “C2PA covers images, audio and video, and has no profile for a text file or a source repository…”

> “the C2PA text gap … is the standard’s problem”

C2PA is not merely an image/audio/video scheme. Its architecture includes manifests, assertions, bindings to assets, and external manifests; text-bearing documents such as PDFs matter here.

A lack of a convenient native plain-text or Git-repository profile is not equivalent to an inability to sign provenance for text. Nor does it establish that an independent ledger is preferable to carrying your assertions within or alongside an existing provenance framework.

**[5]:** Your exact reading of version 2.2 requires section-level support. Separate:

- native embedding formats;
- external manifests and generic asset binding;
- standardized assertions;
- source-repository history;
- span-level lineage;
- tool support.

**[4]:** “The only existing technology that meets that requirement” is an exceptionally strong uniqueness claim. If accurately quoted from IPTC, retain it only as attributed opinion with its scope explained—not an established technical fact.

### 14. Fix the code-share comparison and remove the spurious METR cadence analogy

> “The machine share of new code at the largest labs rose … from a quarter to three quarters…”

The endpoints are claims about **Google**, not a longitudinal sample of “the largest labs.” Microsoft’s reported repository figure and Anthropic’s figure may use different denominators and methods.

**Source checks:**

- **[8]:** Pichai’s October 2024 “more than a quarter” statement, including engineer review and acceptance, matches the known public remarks.
- **[9]:** Nadella’s April 2025 20–30% statement is consistent with the reported LlamaCon remarks. It remains an executive statement with an unclear measurement definition, not an audited repository census.
- **[10] and [11]:** The April/May 2026 figures and exact quotations are unverified here. They are not inherently implausible. Obtain the earnings-call or event transcript and podcast timestamp. Verify whether the denominator is new code, accepted changes, all code, or a subset.

> “It moved from a quarter to three quarters in eighteen months, which is roughly the doubling cadence METR measures…”

Even taking the rounded endpoints literally, tripling in 18 months implies a doubling time of about **11.4 months**, not seven. Seven-month doubling produces approximately a sixfold increase over 18 months.

More fundamentally, a bounded adoption percentage and a task-duration measure do not have meaningfully comparable exponential trajectories.

> “Not typing, approving.”

The Google statement describes what happens to AI-generated code. It does **not** say that engineers stopped writing the remaining code.

**Fix:** Report the claims separately, state denominator uncertainty, and remove both inferences.

### 15. Correct the interpretation of METR and the independence claim

> “Two independent measurements sit behind the reported figures.”

Anthropic’s Economic Index is first-party telemetry from an interested vendor, not an independent audit of Anthropic’s code-writing claim. Neither it nor METR directly measures the reported corporate code shares.

**[12]:** The broad METR result—roughly seven-month growth in the human-task-duration horizon at 50% success over the studied period—is consistent with the published research. The January 2026 update, 320-minute estimate, and 170–729 interval require source verification. Specify the model, evaluation setting, and type/confidence level of interval.

Crucially, a “320-minute horizon” means tasks estimated to take humans that long. It does not establish 320 minutes of continuous autonomous model operation, nor reliable production performance.

> “the most-cited operational yardstick”

Unsupported superlative. Delete unless you have citation analysis.

> “few remaining tasks defeat the newest models”

Verify the exact source and limit it to the evaluated task set. Benchmark saturation would weaken the extrapolation, not establish broad mastery.

**[13]:** The June 2026 “Cadences” report and two-thirds decomposition are unverified here. Explain its operational definition of autonomy, classification method, sample, and uncertainty. “Same model” and “same tasks” do not automatically remove user selection or interface confounding.

**[14]:** The METR trial’s 16 developers, 246 tasks, 19% slowdown, and approximate 24% anticipated/20% perceived speedups match the known study. Your conclusion does not:

> “the instrument has to count bytes rather than ask people.”

The study used task-completion time, not byte counts, to measure productivity. A provenance ledger cannot tell whether the machine helped.

**Fix:** Keep provenance, productivity, autonomy, and capability as distinct measurements.

### 16. Repair the framework attributions and stop claiming consensus

> “Morris et al. … place today’s frontier chatbots at … ‘Emerging’…”

A 2023 paper cannot classify September 2026 frontier systems merely by being cited. Its examples concern systems available at publication.

**[15]:** Morris et al. distinguish capability and autonomy, but their autonomy table has levels **0–5**, including “No AI.” Describing five AI-enabled levels is defensible only if explicitly excluding level 0. “Five levels from tool to agent” otherwise hides the numbering and simplifies the categories. Their highest autonomy category is not merely “human approval and review.”

**[16]:** Feng, McDonald, and Zhang’s capability/autonomy distinction is directionally consistent with the cited framework. Verify the exact wording, level names, and quotation against the paper. It does not validate output-volume share as an autonomy metric.

> “All of them agree on the shape…”

You have not demonstrated that. In particular:

- **[17], ARC-AGI-3:** The exact page wording requires verification. Even if accurate, a benchmark organizer’s criterion is not a consensus definition of AGI. Skill acquisition is not write-channel coverage.
- **[18], International AI Safety Report update:** Verify the exact October 2025 publication, identifier, and “jagged” attribution. An uneven capability profile does not imply your proposed adoption trajectory.
- **[19], Davos:** The specific January 2026 statements require the article and preferably recordings. The general contrast between Hassabis’s forecasts and LeCun’s skepticism about LLMs is plausible, but “nowhere near” is scope-sensitive. LeCun rejecting LLMs as a route is not equivalent to rejecting all routes to general intelligence.

**Fix:** Say “two cited frameworks,” date their examples, quote their actual autonomy definitions, and remove the supposed consensus about humans ceasing to type.

### 17. Use the safety literature for the threat it establishes—not for a future-only threat boundary

> “a Level 1 self-signed label is sufficient while the machine is an honest scribe and insufficient after.”

Sufficient for what? The human key-holder can cheat today. Ordinary malware, compromised dependencies, a modified hook, or prompt injection can corrupt the evidence without AGI or sophisticated scheming.

**Source checks:**

- **[20], Greenblatt et al.:** The broad account of AI control using trusted components around an intentionally untrusted model is appropriate. The research does not establish your ledger’s security.
- **[21], Meinke et al.:** The paper demonstrates in-context scheming in constructed evaluation settings. Preserve those conditions; do not imply measured prevalence in ordinary deployments.
- **[22], Redwood July 2026:** The claimed trusted-executor protocol, 16-character messages, and 67% capability-gap recovery are unverified here. The numbers are not intrinsically implausible, but need task scope, gap definition, baseline, communication budget, and exact quotation. Is the limit per message, per action, or per task?

A trusted executor can faithfully execute malicious or misleading requests. “Outside the writer’s reach” must include control-plane access, signing-key access, policy modification, and evidence submission—not merely a separate process.

**Fix:** Define an adversarial threat model from day one. Keep “self-attested” useful for cooperative bookkeeping, but do not describe it as fraud-resistant certification.

### 18. Fix the detector inference and independently validate the prototype results

> “A label that guesses from style would be wrong most of the time…”

That does not follow from the reported experiment.

**[6]:** The approximately 8% figure is consistent with a specific base-rate calculation. If humans are 5% of passages, all human passages lack a tell, and 60% of machine passages lack a tell:

\[
P(\text{human}\mid\text{no tell})
=\frac{0.05}{0.05+0.95(0.60)}
\approx 8.1\%.
\]

That is the precision of **this particular “no tell means human” rule**, not the error rate of all style-based labels. If fewer human passages lack a tell, the precision is lower. The assumption must be stated.

An AUC of 0.91 and 60% of machine passages lacking a selected “tell” are not necessarily contradictory; they may describe different scores or thresholds. Explain them.

**[7]:** Sadasivan et al. support limits on reliable detection as distributions converge, along with attacks and relevant assumptions. They do not show that every practical detector is wrong most of the time in every distribution.

The prototype claims—five weeks, 2,716 writes, 72,681 lines, median 96%, notes at 0%, source at 9%—cannot be independently confirmed from the manuscript. They also do not establish correctness:

- Are 72,681 lines write volume or unique surviving lines?
- What is the independent ground truth?
- Does the detector evaluation separate projects, authors, and sessions?
- Does attribution ever falsely attest unlogged content?
- Are copied spans and mixed-origin edits tested?

> “It is not a failure of the method…”

It may be an honest report of limited coverage. It is still a major limitation if 91% of agent-written source is not attributed.

**Fix:** Publish fixtures, raw or appropriately redacted evidence, counting rules, ground-truth construction, and false-attestation tests. Call the one-developer study a prototype demonstration, not validation of a general measurement theory.

### 19. Redesign the registry and replace the self-application promise with a reproducible result

> “A registry would be everyone’s number…”

An opt-in registry is its contributors’ number. A registry of qualifying labels is additionally threshold-selected: it excludes precisely the low-coverage artifacts needed to estimate adoption.

It is vulnerable to:

- selective publication;
- duplicate submissions and forks;
- unlimited pseudonymous submitters;
- boilerplate flooding;
- changes in participant composition;
- changing denominators and counting policies;
- publishing a high-coverage subdirectory while implying whole-project coverage.

The paper demonstrates the last risk itself:

> “the check on the `label/` directory alone should say so…”

Certifying that directory may be legitimate, but the badge must make the exclusion of the rest of the repository unmistakable.

> “if it does not, the ledger is right and this sentence is wrong”

The ledger and verifier can also be wrong. This is rhetoric, not an engineering acceptance test.

**Fix:** For the self-check, publish the exact commit, artifact digest, command, verifier version, public key, ledger evidence, scope, and actual output. Reconcile “lines” in earlier sections with “units” and the repository’s reported 17%.

For the registry, collect a predefined longitudinal cohort including **all measured artifacts**, not just successful certifications. Report coverage, exclusions, attrition, duplication controls, and uncertainty. Do not call it population-level autonomy adoption without a sampling design.

### 20. Remove the remaining promotional overclaims

These need direct replacement:

| Offending wording | Defensible replacement |
|---|---|
| “why it will matter more every year” | “a proposal for verifiable write-channel provenance” |
| “Coverage, not detection, is the whole problem.” | “The prototype measures coverage rather than inferring authorship from style.” |
| “This label never guesses.” | “The verifier evaluates recorded evidence under a specified trust model.” |
| “every unit that did not is listed” | “Every in-scope unit lacking accepted evidence is listed.” |
| “the one thing that has no other record: the unreviewed edit” | “Edits not covered by this instrumentation.” |
| “before anyone needs it” | “because adversarial publishers and compromised environments are already possible.” |
| “independent of benchmarks and of what executives say” | “computed from submitted artifact evidence, subject to participation and instrumentation bias.” |

**Bottom line:** Keep the signed ledger. Keep reproducible, version-bound coverage reports. Drop the authorship certification unless you can actually establish authorship—which this protocol cannot. Drop the AGI thermometer unless independent studies validate the proposed relationship. As written, the paper’s most important guarantees are properties of its marketing, not properties of its system.

### B. google/gemini-3.1-pro-preview
This is a classic case of a solid engineering mechanism hijacked by a grandiose philosophical thesis. The core proposal—a cryptographic provenance ledger that logs machine-generated bytes at write time—is practical, verifiable, and a welcome antidote to the snake-oil industry of AI text detectors. 

But starting in §4, the paper abandons engineering for pseudo-scientific AGI forecasting. You conflate *byte volume* with *agentic autonomy*, creating a metric that can be trivially distorted by workflow quirks, boilerplate generation, and out-of-band copy-pasting. 

Here is my review of your claims, logic, and threat model.

### 1. Factual Claims and Attributions
Your citations of the 2023–2025 literature (METR, Sadasivan, Morris, EU AI Act) are accurate and well-contextualized. However, your uncritical acceptance of 2026 corporate PR is naive:
*   **Implausible Quote:** You cite an Anthropic CFO claiming *"90%-plus of Anthropic's code written by Claude"* (§4). Even projecting to mid-2026, this is highly implausible for a frontier AI lab. While 90% of their *web frontend* or *test boilerplate* might be generated, core ML engineering, CUDA kernel optimization, and novel distributed systems architecture are not 90% machine-written. You are swallowing executive hype meant for investors and treating it as an empirical baseline. You must flag these as likely exaggerated or scoped to specific codebases.

### 2. Logical Gaps in §5–§6 (Bytes ≠ Autonomy)
Your entire argument that the label acts as a "thermometer" for AGI rests on a fatal logical leap: that the ratio of machine-written bytes correlates with system autonomy. It does not.
*   **The Verbosity Fallacy:** A highly autonomous agent might spend three hours debugging a complex race condition and write exactly *two lines of code*. A low-autonomy autocomplete tool might generate *2,000 lines* of boilerplate from a single human prompt. Under your ledger, the dumb tool registers a massive spike in "attested share," while the AGI-level debugging agent barely moves the needle. You are measuring verbosity, not autonomy.
*   **The Dictation Fallacy:** You claim: *"When the second number approaches 100% across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders"* (§6). This is false. A human could be dictating code line-by-line to an LLM ("change the loop to a while loop, now rename the variable"). The human is still operating at Level 1 (Operator), but because the AI is doing the physical typing through the tool channel, your ledger reads 100% machine share. 

### 3. Blind Spots and Gaming Missed in §7
Your threat model in §7 is incomplete and misses the most obvious ways this metric will decouple from reality:
*   **AI-Washing Human IP:** A developer writes 500 lines of complex, brilliant code by hand. They then prompt the agent: *"Add docstrings to this file."* The agent rewrites the file through the logged tool channel. Your ledger now attests that 100% of the file is "Guaranteed AI." The human's intellectual property has been laundered into machine provenance. 
*   **The Out-of-Band Penalty:** If a developer generates a brilliant algorithm in a web UI (like ChatGPT or Claude web) and copy-pastes it into their editor, your hook registers it as 0% AI (unattested). Your label doesn't measure "how much AI was used"; it strictly measures "how much AI was used *through your specific harness*." 
*   **Dumb Tool Contamination:** If a developer runs a standard regex script or a code formatter (like `black` or `prettier`) through the logged channel, does the hook sign it? If so, traditional deterministic scripts are inflating your "AI" metric.

### 4. Overclaimed Wording
*   **Overclaim:** *"This label never guesses. It reads a signature or it says nothing."* (§2)
    *Reality:* It guesses that the environment hasn't been compromised by a non-adversarial user. You admit this in §6 regarding Level 1, but the absolute phrasing in §2 is a marketing overclaim.
*   **Overclaim:** *"A registry of labelled work... would be a measurement of autonomy adoption taken in the field..."* (§5)
    *Reality:* It is a measurement of tool-channel byte volume. It measures workflow compliance, not autonomy.

***

### Verdict: Publish after fixes.
The engineering spec (`label/README.md`) and the critique of style-based detectors are excellent. The AGI thermometer thesis is fundamentally broken. Strip the AGI forecasting out, or heavily caveat it, and focus on what this actually is: a cryptographic supply-chain provenance tool for text.

### Concrete Fixes Required

1.  **Decouple the label from AGI forecasting (Fix §5 and §6):** Remove the claim that *"When the second number approaches 100%... the human has moved wholly to authorisation and review"*. Replace it with an honest admission that a 100% attested share only proves the machine *typed* the bytes, which cannot distinguish between a highly autonomous agent and a human micro-managing an AI typist.
2.  **Address AI-Washing in §7:** Add a bullet point in §7 acknowledging that AI tools modifying human-written code (e.g., refactoring, commenting) will overwrite human provenance with machine provenance, artificially inflating the attested share. 
3.  **Address Out-of-Band Generation in §7:** Explicitly state that the label penalizes copy-pasting from external AI tools. Clarify that the "thermometer" only measures *integrated harness adoption*, not total AI reliance.
4.  **Caveat the Corporate Claims (§4):** Add a sentence immediately following the table in §4: *"Note that executive claims of 75% to 90% code generation likely reflect raw line counts—heavily skewed by boilerplate, tests, and markup—rather than the proportion of complex logic solved by the machine."*
5.  **Soften the "Never Guesses" claim (§2):** Change *"This label never guesses. It reads a signature or it says nothing"* to *"This label does not guess based on style. It relies entirely on cryptographic provenance."*

### C. qwen/qwen3.8-max-0902
## Verdict: **Publish after fixes** — but only after major surgery

The paper contains a potentially useful idea: a signed, machine-readable provenance ledger for artifacts produced through logged AI/tool channels. That is worth publishing if scoped honestly.

But v0.1 is not publishable as written because it repeatedly conflates:

- **provenance** with **authorship**;
- **signed channel** with **truth**;
- **attested byte share** with **autonomy**;
- **deployment choices** with **progress toward AGI**;
- **self-attestation** with **guarantee**.

The most serious problem is not the 2026 sourcing. I am not rejecting post-2026 sources merely because they postdate my training data. The problem is that the paper uses self-reported, secondary, or unverifiable 2026 claims as load-bearing evidence for a strong AGI-adjacent thesis. If the authors will not cut or rigorously substantiate §5–§6, my verdict becomes **do not publish**.

Below are the required fixes, ordered by importance.

---

# Numbered concrete fixes, most important first

## 1. Remove or fully substantiate the claim that attested share measures “rising autonomy toward AGI”

**Offending sentences:**

> “a team's attested share, held at constant instrumentation, is the number that records that choice as it is made.”

> “So the label registers the approach before any benchmark declares it.”

> “When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders.”

**Problem:**  
This is the paper’s central logical leap and it is not supported. A signed ledger can show that certain bytes passed through a machine channel. It cannot show that the machine chose the task, planned the work, exercised judgment, operated autonomously, or is approaching AGI.

A human can retain tight control while the machine writes 100% of the bytes: the human supplies exact prompts, exact constraints, exact tests, reviews every hunk, and approves only narrow output. That would produce a high attested share but low autonomy.

Conversely, a highly autonomous agent may write through unlogged shells, external tools, generated binaries, configuration, prompts, or human-mediated copy/paste. That could produce a low attested share despite high autonomy.

**Fix:**  
Either:

1. Reframe the paper as a **provenance/attestation** paper, not an AGI-progress paper; or  
2. Provide a separate empirical validation showing that attested byte share correlates with a recognized autonomy measure, controlling for task type, instrumentation, repo type, toolchain, and selection effects.

If you cannot do 2, delete the AGI-thermometer framing from the abstract, §5, §6, and the conclusion.

---

## 2. Stop calling this a “guarantee” without a real guarantor

**Offending sentences:**

> “Guaranteed AI: a label for work the machine wrote”

> “Two grades: **Pure AI** at 100 % attested, **Guaranteed AI** at 90 % or more with every unattested unit listed.”

**Problem:**  
“Guaranteed” implies a warrant, a guarantor, and a remedy. The paper describes self-signed Level 1 attestation. That is not a guarantee in any meaningful certification sense. It is a signed claim.

“Pure AI” is also dangerous wording. Even if bytes are emitted by a model, humans selected the model, prompt, data, constraints, review process, and acceptance criteria. “Pure AI” invites metaphysical and legal overreading.

**Fix:**  
Rename or qualify the marks. For example:

- “Attested AI — self-signed”
- “Machine-channel attested”
- “Signed provenance: AI channel”
- “AI-written bytes, attested”

If you keep “Guaranteed AI”, the badge must explicitly say:

> “Self-signed attestation. No third-party certification. Proves only that listed units were recorded through a named machine channel.”

Also define “Pure AI” operationally or drop it.

---

## 3. Correct the false dichotomy between machine writing and hand writing

**Offending sentence:**

> “Machine writing arrives with a prompt, a diff, a log, a test run and a signature, and hand writing arrives with none of those, so the attested share is the share a reviewer can trace.”

**Problem:**  
This is wrong as a universal claim.

Hand-written code can arrive with:

- version-control commits;
- signed commits;
- pull-request reviews;
- CI logs;
- editor local history;
- issue-tracker discussion;
- code-review comments;
- test runs;
- audit trails.

Machine writing can arrive with none of those if the toolchain does not log it.

The correct claim is narrower: **some machine channels can be instrumented to produce strong provenance; many human edits are not instrumented in the same way.** That is not the same as “hand writing arrives with none of those.”

**Fix:**  
Rewrite as:

> “Machine writing can be made traceable when it passes through an instrumented channel. Hand writing may also leave traces, but those traces are often not bound to the exact byte-level write event. The label measures the presence or absence of machine-channel attestation, not the total absence or presence of human provenance.”

Also state explicitly:

> “Unattested does not mean human-written. It means not attested through the covered machine channel.”

---

## 4. Define exactly what the signature proves and what it cannot prove

**Offending sentences:**

> “This label never guesses. It reads a signature or it says nothing.”

> “anyone with the public key gets the same number.”

> “The key proves the channel, not the author.”

**Problem:**  
A signature proves that some key signed some record. It does not prove:

- that the model actually generated the content;
- that the prompt was truthful or complete;
- that the toolchain was not compromised;
- that the signer did not sign human-supplied bytes;
- that the environment was not manipulated;
- that the final artifact has not changed;
- that the counting tool is deterministic or honest;
- that the key was not stolen;
- that the metadata reflects reality.

“Anyone with the public key gets the same number” is only true if they have the same ledger, the same tool version, the same unit definitions, the same exclusions, the same canonicalization rules, and no missing logs.

**Fix:**  
Add a precise threat model and guarantees section. It must answer:

1. What exact bytes are signed? File hash? Hunk hash? Line range? Canonicalized normalized text?
2. What metadata is signed? Prompt hash, model ID, tool ID, session ID, timestamp, parent commit?
3. How are post-signature edits detected?
4. How are deleted or omitted records detected?
5. What prevents a keyholder from signing human-supplied text?
6. What prevents a malicious tool from signing false provenance?
7. What does Level 2 actually defend against?
8. What does Level 2 not defend against?
9. How is the public key bound to an accountable entity?
10. How is the verifier’s counting algorithm made deterministic and reproducible?

Do not say “guarantee” until these are specified.

---

## 5. Replace secondary or missing citations with primary sources, or downgrade the claims

**Offending citations and sentences:**

> “The Authors Guild introduced a "Human Authored" certification for books in 2025; iHeartMedia began having its radio hosts announce "Guaranteed Human" content the same year; Spotify's 2026 "Verified" badge is withheld from profiles "that release songs that Spotify deems to be AI-generated"; a film company put "No AI Used" on its marketing at the Berlinale in 2026 [2].”

Reference [2] is Wikipedia. That is not acceptable for a white paper making market claims.

Also:

> “Primary transcript not located; cited as reported.”

for reference [10].

And:

> “TechSpot. *Anthropic says more than 90 % of its code is now written by AI.* 14 May 2026, reporting K. Rao on the *Invest Like the Best* podcast. Cited as reported.”

**Problem:**  
The paper relies on secondary reporting for claims that are central to its motivation. The Spotify claim in particular looks under-specified and potentially misleading: “Verified” is usually an identity/profile status, not necessarily an AI-content certification. If Spotify is withholding verification based on AI-generated releases, that needs a direct Spotify policy citation, not a Wikipedia page.

**Fix:**  
For every claim about a company, label, regulator, or executive:

- cite the primary transcript, policy page, press release, official blog, podcast timestamp, or archived video;
- if no primary source exists, say “reported by [outlet]; not independently verified”;
- do not use unverified reported claims to support the AGI/autonomy argument.

Specifically:

- replace [2] with primary sources for Authors Guild, iHeartMedia, Spotify, and Berlinale;
- locate or remove the Google 75% claim in [10];
- locate or downgrade the Anthropic 90% claim in [11];
- archive all 2026 sources with immutable archives and exact quote locations.

---

## 6. Fix the industry code-share table: definitions are not comparable

**Offending table row:**

> “20 % to 30 % of code inside the company's repositories was 'written by software'”

**Offending summary sentence:**

> “The machine share of new code at the largest labs rose, by their own reported figures, from a quarter to three quarters between October 2024 and April 2026.”

**Problem:**  
The table mixes incompatible metrics:

- Google Q3 2024: “new code” generated by AI.
- Microsoft/Nadella: “code inside the company's repositories” written by software.
- Google 2026: “new code” AI-generated.
- Anthropic 2026: “Anthropic's code” written by Claude.

These are not the same thing.

“Written by software” may include non-AI automation, scripts, code generators, scaffolding, or internal tooling. “Repository code” is stock, not new code. “AI-generated” may mean suggested, accepted, modified, or merely touched by AI. “Written by Claude” may mean Claude produced the final bytes, or that engineers used Claude interactively.

Also, “largest labs” plural overgeneralizes from a few self-reported figures.

**Fix:**  
Rewrite §4 as:

> “Several executives have reported rising AI involvement in code production, but the metrics are not directly comparable.”

Then present a table with columns:

- denominator: new code vs repository stock vs accepted changes;
- definition: AI-generated, AI-assisted, written by software, written by Claude;
- acceptance process;
- time window;
- source quality: primary transcript vs secondary report;
- confidence level.

Remove the sentence claiming a clean rise “from a quarter to three quarters” unless you restrict it to Google’s reported “new code” figures and cite primary sources.

---

## 7. Delete the false “doubling cadence” comparison

**Offending sentence:**

> “It moved from a quarter to three quarters in eighteen months, which is roughly the doubling cadence METR measures for task horizons (below).”

**Problem:**  
This is numerically and conceptually wrong.

A move from 25% to 75% over 18 months is not “roughly” a 7-month doubling cadence. Even if one treated 25→50 as one doubling, 50→75 is not a doubling. More importantly, METR’s task horizon is a capability metric; code-share is an adoption/reporting metric. They are not the same curve.

**Fix:**  
Delete the sentence. If you want to compare adoption and capability, do it cautiously and explicitly:

> “The reported adoption increase is suggestive but not directly comparable to METR’s capability horizon metric.”

Do not imply mathematical equivalence.

---

## 8. Correct the claim that there are “two independent measurements”

**Offending sentence:**

> “Two independent measurements sit behind the reported figures.”

**Problem:**  
One of the cited measurements is Anthropic’s own Economic Index. That is not independent of Anthropic. METR may be independent, but Anthropic’s report is not independent of Anthropic’s claims about Anthropic.

**Fix:**  
Change to:

> “Two external or quasi-external measurements are relevant, though one is produced by a lab whose behavior it describes.”

Or simply:

> “Two published measurements are relevant.”

Do not call them independent unless they are.

---

## 9. Fix the EU AI Act and C2PA claims

**Offending sentences:**

> “Article 50 of the EU AI Act, applicable from 2 August 2026, obliges providers of generative systems to mark outputs so that they are detectable as artificially generated…”

> “IPTC's reading is that C2PA Content Credentials is the only existing technology that meets that requirement [4]; C2PA covers images, audio and video, and has no profile for a text file or a source repository [5].”

**Problem:**  
The EU AI Act claim needs exact wording. Article 50 concerns transparency obligations for certain AI systems, including machine-readable marking of synthetic content, but the paper’s phrasing “detectable as artificially generated” risks overstating what is required and to whom. There are scope limits, exceptions, and technical nuances.

The claim that C2PA is “the only existing technology” is too strong unless quoted exactly and scoped. Other provenance approaches exist or may be relevant: W3C PROV, in-toto attestations, SLSA, Sigstore, signed commits, notarization, transparency logs, cryptographic SBOMs, etc. They may not satisfy the specific regulatory requirement in the same way, but the absolute “only” needs direct support.

The claim that C2PA has no text or source-repository profile also needs a precise citation. If it is the authors’ reading, say so clearly and do not present it as a fact about the standard.

**Fix:**  
Cite the exact Article 50 text from EUR-Lex. Quote the relevant paragraphs. State:

- which systems are covered;
- whether marking is machine-readable;
- what deployer obligations apply;
- what exceptions exist.

For C2PA:

- cite the exact specification sections;
- distinguish “no current profile” from “technically impossible”;
- remove “only existing technology” unless IPTC’s statement says exactly that and defines the comparison set.

---

## 10. Explicitly state that “unattested” does not mean “human-written”

**Offending sentence:**

> “with every hand-typed or unlogged span listed beside the number.”

**Problem:**  
This wording encourages readers to interpret every unattested span as hand-typed. But the paper itself admits that unlogged machine channels exist:

> “the project's own source, which the agent had written through a shell heredoc instead of the logged tool, attested at 9 %.”

So unattested can mean:

- human-typed;
- machine-written but unlogged;
- generated by another tool;
- copied from elsewhere;
- merged from a dependency;
- produced by a script;
- produced by a different agent channel;
- unknown.

**Fix:**  
Replace “hand-typed or unlogged span” with:

> “every unattested span”

and add:

> “Unattested means not recorded through the covered machine channel. It does not prove human authorship.”

This is essential to avoid misleading users.

---

## 11. Specify the measurement unit, denominator, and coverage methodology

**Offending sentence:**

> “holding hook coverage constant”

**Problem:**  
The paper does not define the measurement rigorously enough to support scientific claims.

What is a unit?

- line?
- hunk?
- file?
- function?
- commit?
- pull request?
- semantic change?
- byte?
- token?

How are generated files handled?

- lockfiles?
- vendored dependencies?
- compiled artifacts?
- snapshots?
- test fixtures?
- notebooks?
- markdown prose?
- binary files?

How is coverage measured?

- Does the hook see all possible write paths?
- How do you know?
- Can a new unlogged channel be detected?
- Can an instrumented channel be silently bypassed?
- How are tool updates handled?
- How are renames/moves/refactors counted?

“Holding hook coverage constant” is not meaningful unless coverage is independently measurable.

**Fix:**  
Add a measurement specification:

1. Define the unit of analysis.
2. Define the denominator.
3. Define included/excluded paths.
4. Define normalization rules.
5. Define channel taxonomy.
6. Define how coverage is audited.
7. Define how new channels are discovered.
8. Define how changes in tooling are versioned.
9. Provide deterministic verification commands.
10. Provide confidence intervals or uncertainty where appropriate.

Without this, “attested share” is not a stable field measurement.

---

## 12. Expand §7 to cover the gaming modes it misses

**Offending section heading:**

> “How the label can be gamed, and what it does about it”

**Problem:**  
§7 lists a few games but misses many obvious ones.

**Missing attack modes:**

1. **Human-text laundering through the agent**  
   A human writes exact text and prompts: “Output exactly these bytes.” The label attests it as machine-written. The paper mentions this but underweights it. This is not an edge case; it defeats any claim that attestation measures machine authorship.

2. **Non-AI automation signed as AI**  
   A script, formatter, macro, template engine, or sed command can write bytes through a signed channel. If the label says “AI”, it may mislead. Define whether “machine” includes non-AI automation.

3. **Selective repository scope**  
   A team can label a directory with high machine share while excluding the human-critical architecture, security, tests, or documentation.

4. **Unit-weighting games**  
   Large machine-generated files can dominate line counts while small human edits carry the semantic core. A 90% line-based attestation can be substantively misleading.

5. **Stale badge display**  
   Terms of use are not technical enforcement. If the badge is not bound to a content hash and version, users can display an old badge after later human edits.

6. **Key compromise**  
   If the signing key leaks, an attacker can mint arbitrary attestation. Level 2 transparency helps detect some forks, but does not prevent false entries signed before detection.

7. **Malicious hook/toolchain**  
   If the hook itself is malicious or compromised, it can sign false records. The paper needs a supply-chain threat model.

8. **Trusted-executor manipulation**  
   A trusted executor outside the writer’s reach may still be influenced by prompts, inputs, or data supplied by the untrusted model. “Outside the writer’s reach” is not enough; define trust boundaries.

9. **Registry spam**  
   If the registry counts attested share over time, teams can inflate it with trivial generated artifacts, bot PRs, or synthetic repositories.

10. **Goodharting**  
   Teams may avoid necessary human edits to preserve a badge, or route human edits through the agent to keep the number high.

11. **Privacy leakage from unattested lists**  
   Listing unattested lines/files can reveal sensitive human edits, secrets, personnel activity, or legally relevant authorship.

12. **Regulatory confusion**  
   Users may mistake the label for EU AI Act compliance, C2PA compliance, copyright status, safety certification, or quality assurance.

**Fix:**  
Rewrite §7 as a proper threat model. For each attack:

- describe the adversary;
- describe the exploit;
- state whether Level 1 mitigates it;
- state whether Level 2 mitigates it;
- state what remains unmitigated.

Do not present Level 2 as a general solution until this is done.

---

## 13. Make stale-badge protection technical, not contractual

**Offending sentence:**

> “The badge carries its check date, and the terms of use forbid displaying a number older than the last change.”

**Problem:**  
A terms-of-use prohibition is not a technical control. A badge should fail verification if the artifact changed.

**Fix:**  
Bind the badge to:

- content hash;
- commit SHA or equivalent artifact identifier;
- ledger head hash;
- timestamp;
- expiry or revalidation requirement;
- verification URL or public log entry.

The verifier should return “invalid” or “stale” when the artifact no longer matches. Do not rely on “forbid”.

---

## 14. Correct the Level 2 anchoring claim

**Offending sentence:**

> “Level 2, with the ledger head anchored in a log the developer cannot rewrite, does.”

This appears in response to:

> “The key-holder lying.”

**Problem:**  
Anchoring the ledger head in a transparency log helps detect retroactive rewriting or forked histories. It does not prevent a keyholder from signing a false record in the first place.

If a developer can sign arbitrary entries, they can create a false entry and anchor it. Transparency helps auditors see the entry, but it does not make the entry true.

**Fix:**  
Rewrite:

> “Level 2 anchoring can make deletion or retroactive rewriting detectable, but it does not by itself prevent false attestation by a compromised or malicious signer.”

Then specify what additional controls are needed:

- trusted execution environment;
- hardware attestation;
- multi-party signing;
- witness signatures;
- policy checks;
- key custody;
- revocation;
- audit monitoring.

---

## 15. Add explicit legal, safety, copyright, and compliance disclaimers

**Offending sentence:**

> “And four things it does not guarantee, stated on the label's own page: not quality, not that no human decided the content, not the absence of human judgement, and nothing about any named person.”

**Problem:**  
This is a good start but insufficient. The label could be misread as:

- AI Act compliance;
- copyright status;
- safety certification;
- security assurance;
- originality guarantee;
- non-infringement guarantee;
- truthfulness guarantee;
- quality guarantee;
- AGI-level autonomy claim.

**Fix:**  
Add a prominent disclaimer section:

> “This label does not certify quality, safety, security, legality, copyrightability, non-infringement, accuracy, regulatory compliance, or absence of human creative control. It does not certify that the content was generated by a general-purpose AI system. It certifies only that listed units were recorded through designated machine channels under the stated trust assumptions.”

Also state that the label is not a legal compliance mark unless separately certified.

---

## 16. Publish the data, signatures, and verification commands for NoHumanWrites and for this paper

**Offending sentences:**

> “NoHumanWrites measured this on one developer's machine over five weeks [6]. The agent made 2,716 logged file writes covering 72,681 lines.”

> “The NoHumanWrites repository, checked on 6 September 2026 against its own signed ledger, attests at 17 % of units.”

> “This white paper and the spec beside it were written through the signed channel on purpose…”

**Problem:**  
The empirical foundation is a self-published companion study, apparently n=1, over five weeks, by the same organization. That is weak evidence for broad claims about machine writing, autonomy, or AGI.

If the paper claims the white paper itself is signed, the review package should include the manifest and verification command.

**Fix:**  
Provide:

- archived dataset;
- signed ledger;
- public keys;
- counting script;
- exact version hashes;
- reproducible command line;
- explanation of units;
- independent replication instructions.

If the white paper is attested, include:

- the ledger entry for the paper;
- the content hash;
- the signature;
- the verification output.

If you cannot provide these, remove the self-referential claims.

---

## 17. Fix the detector claims and base-rate discussion

**Offending sentence:**

> “A local detector of AI-writing patterns separated machine from human passages with an AUC of 0.91, yet 60 % of machine passages carried no tell at all, so a rule of "no tell means human" had a precision near 8 % at a 5 % human share [6].”

**Problem:**  
The claim may be internally plausible, but it needs assumptions. Precision depends on:

- threshold;
- class balance;
- detector calibration;
- definition of “tell”;
- whether the detector was evaluated out-of-sample;
- whether the corpus is representative.

Also, citing Sadasivan et al. as “the theoretical reason” is too broad. Their work shows detection can be hard as generated text approaches human distribution, but it does not prove all detection is useless in all settings. Watermarks, model access, and distribution shift matter.

**Fix:**  
Provide:

- detector definition;
- evaluation protocol;
- threshold;
- confusion matrix or calculation;
- assumptions;
- limitations.

Rewrite the Sadasivan citation as:

> “Sadasivan et al. show that reliable detection becomes difficult when generated text is distributionally close to human text, absent additional signals such as watermarks or model access.”

---

## 18. Tone down overclaiming language throughout

**Offending sentences:**

> “All of them rest on a declaration, an estimate or a platform's private judgement, and none can be checked by a third party.”

**Problem:**  
Too absolute. Some provenance systems can be cryptographically checked for supported media. Some declarations may be auditable. The claim should be narrowed.

**Fix:**  
Replace with:

> “Many existing human-content marks rely on declarations or estimates that readers cannot independently re-derive.”

---

**Offending sentence:**

> “Nobody has shipped the mark that points the other way: one that says a machine wrote this…”

**Problem:**  
Overstated. Platforms, standards, and tools already mark AI-generated or synthetic content in various ways. The gap may be specific to text/code and public byte-level provenance, but “nobody” is too strong.

**Fix:**  
Replace with:

> “We are not aware of a widely deployed public label that provides byte-level machine-channel attestation for text and source code.”

---

**Offending sentence:**

> “It is the least reviewed byte in the repository, and it is invisible precisely because it looks like every other byte.”

**Problem:**  
Rhetorical and unsupported. Human edits may be heavily reviewed. Unlogged machine edits may also be invisible. The sentence should not privilege one explanation.

**Fix:**  
Replace with:

> “Byte-level edits can be difficult to attribute when the write path is not instrumented.”

---

**Offending sentence:**

> “Coverage, not detection, is the whole problem.”

**Problem:**  
Overstated. Coverage is important, but detection, semantics, intent, review quality, security, and legal status also matter depending on the use case.

**Fix:**  
Replace with:

> “For provenance labeling, coverage is the central problem; for broader AI governance, it is one of several.”

---

**Offending sentence:**

> “This label never guesses. It reads a signature or it says nothing.”

**Problem:**  
It still interprets the signature as evidence of machine writing. If the signer is compromised or the channel is misused, the label is misleading.

**Fix:**  
Replace with:

> “The label does not use stylistic inference. It reports whether a valid signature exists for a unit, subject to the stated trust assumptions.”

---

**Offending sentence:**

> “The label is the record, published.”

**Problem:**  
A self-signed record is not necessarily “the” record. It is one record.

**Fix:**  
Replace with:

> “The label is a published attestation record.”

---

## 19. Include the label specification in the paper or an appendix

**Offending sentence:**

> “The spec is short and lives in `label/README.md`.”

**Problem:**  
A white paper cannot make precise guarantee claims while leaving the core specification external and unspecified in the document. Reviewers and implementers need the schema, signature format, verification algorithm, and failure modes in the paper or a versioned appendix.

**Fix:**  
Add an appendix containing:

- ledger schema;
- signature format;
- key model;
- unit definition;
- counting algorithm;
- verification algorithm;
- Level 1 and Level 2 requirements;
- transparency-log anchoring format;
- example pass/fail outputs.

---

## 20. Disclose conflicts, governance, and commercial interest

**Offending context:**

> “White paper v0.1 · 6 September 2026 · Plus de Fun Agency, Geneva”

**Problem:**  
The paper proposes a label that may be operated, branded, or commercialized by the authors’ agency. That is not disqualifying, but it must be disclosed.

**Fix:**  
Add a conflicts and governance section:

- Who controls the label?
- Is there a trademark?
- Is there a fee?
- Who operates the registry?
- Who controls the root keys?
- Can the agency revoke or alter badges?
- What happens if the agency disappears?
- Is there an oversight board?
- Is the specification open?

Without this, “Guaranteed” is especially problematic.

---

# Detailed findings supporting the fixes

## A. Factual claims and attributions that need correction or stronger sourcing

### 1. Existing-label claims are too sweeping

**Quote:**

> “Every label on the market for AI-era content points the same way: it tells the reader that a human made the work. All of them rest on a declaration, an estimate or a platform's private judgement, and none can be checked by a third party.”

This is overstated.

Some AI-era provenance marks, especially C2PA-based credentials for images/audio/video, can be checked cryptographically by third parties. The paper’s real target is not “every label” but labels for text/code that lack public byte-level provenance.

**Required change:**  
Narrow the claim to the relevant gap. Do not say “none” unless you enumerate the comparison set and justify it.

---

### 2. “Nobody has shipped the mark that points the other way”

**Quote:**

> “Nobody has shipped the mark that points the other way: one that says a machine wrote this, here is the signature, here is the list of what it did not write.”

This is likely false or at least unproven. There are AI-generated content labels, synthetic-media disclosures, platform AI labels, C2PA assertions about generative AI, code-generation attestations, and provenance systems.

The defensible claim is narrower:

> “We are not aware of a public, byte-level, machine-channel attestation label for text and source code.”

**Required change:**  
Replace “Nobody has shipped” with a scoped novelty claim.

---

### 3. Wikipedia is not sufficient for market claims

**Quote:**

> “The Authors Guild introduced a "Human Authored" certification for books in 2025; iHeartMedia began having its radio hosts announce "Guaranteed Human" content the same year; Spotify's 2026 "Verified" badge is withheld from profiles "that release songs that Spotify deems to be AI-generated"; a film company put "No AI Used" on its marketing at the Berlinale in 2026 [2].”

Reference [2] is Wikipedia. For a white paper making regulatory and market claims, this is too weak.

The Spotify claim is especially problematic because it mixes “Verified” profile status with AI-content moderation. That needs a direct Spotify policy statement.

**Required change:**  
Cite primary sources. If unavailable, mark each claim as “reported; unverified” and remove it from the argument.

---

### 4. EU AI Act wording needs precision

**Quote:**

> “Article 50 of the EU AI Act, applicable from 2 August 2026, obliges providers of generative systems to mark outputs so that they are detectable as artificially generated…”

The AI Act’s transparency obligations are more precise and more limited than this phrasing suggests. The paper should quote the exact article and distinguish:

- providers vs deployers;
- synthetic audio/image/video/text;
- machine-readable marking;
- deepfake disclosure;
- public-interest text disclosure;
- exceptions.

**Required change:**  
Quote Article 50 directly from EUR-Lex and revise the summary.

---

### 5. IPTC/C2PA “only existing technology” claim is too strong

**Quote:**

> “IPTC's reading is that C2PA Content Credentials is the only existing technology that meets that requirement [4]”

This looks like a standards-political claim. It may be what IPTC said, but the paper must quote the exact sentence and scope. “Only existing technology” is an absolute claim and needs a defined comparison set.

**Required change:**  
Either quote IPTC exactly and define the requirement, or soften to:

> “IPTC states that C2PA is one technology designed to meet this requirement.”

---

### 6. C2PA text/repository claim needs direct specification support

**Quote:**

> “C2PA covers images, audio and video, and has no profile for a text file or a source repository [5].”

If this is the authors’ reading, say so. If it is a fact about C2PA 2.2, cite the exact part of the specification. Also note that source repositories are complex artifacts, not a single media type; the absence of a profile is not the same as impossibility.

**Required change:**  
Cite C2PA spec sections or rephrase as a gap analysis.

---

### 7. NoHumanWrites empirical claims are too thin for the weight placed on them

**Quote:**

> “NoHumanWrites measured this on one developer's machine over five weeks [6].”

This is a small, self-published, likely single-subject study. It can motivate the tool, but it cannot support broad claims about machine writing, autonomy, or AGI.

**Required change:**  
Present NoHumanWrites as a pilot/case study. Do not use it as general evidence unless you provide independent replication.

---

### 8. The code-share table needs definitional discipline

**Quote:**

> “The machine share of new code at the largest labs rose, by their own reported figures, from a quarter to three quarters between October 2024 and April 2026.”

This compresses multiple sources into a single trend. It is misleading.

The Nadella row is especially problematic:

> “20 % to 30 % of code inside the company's repositories was 'written by software'”

That is not necessarily “AI-generated new code.” It may refer to all repository code and to software-written automation generally.

**Required change:**  
Do not aggregate these figures into one trend. Present them as separate self-reported claims with definitions and source quality.

---

### 9. Google 75% and Anthropic 90% claims need primary transcripts

**Quotes:**

> “75 % of new code at Google AI-generated "and approved by engineers", up from 50 % the previous autumn”

> “90 %-plus” of Anthropic's code written by Claude

For claims this central, secondary reporting is insufficient. The paper already admits for [10]:

> “Primary transcript not located; cited as reported.”

That means the claim should not be used as strong evidence.

**Required change:**  
Find the primary transcript or downgrade the claim to:

> “According to secondary reporting, Pichai reportedly said…”

Do not build the AGI argument on it.

---

### 10. METR claims need exact sourcing and cautious interpretation

**Quote:**

> “METR's time-horizon work, updated on 29 January 2026, finds the length of software task a frontier system completes at 50 % reliability doubling "around every 7 months over the period 2019 to 2025"…”

I am not rejecting this because it is post-2026. But it must be quoted and sourced exactly. Also:

- “most-cited operational yardstick” is unsupported;
- “few remaining tasks defeat the newest models” needs a direct quote;
- extrapolation from software tasks to general capability is not automatic.

**Required change:**  
Cite exact figures, model set, methodology, and limitations. Avoid implying that task horizon equals AGI progress.

---

### 11. The METR developer RCT is being used too broadly

**Quote:**

> “Developers could not tell, from the inside, whether the machine had helped.”

The study appears to measure productivity and perception in a specific setting. It does not show that developers cannot tell whether machine authorship occurred, nor does it establish the need for a byte-level provenance label.

**Required change:**  
Rewrite:

> “The METR trial found a perception gap about productivity impact in its setting. That does not directly measure authorship or autonomy, but it illustrates that self-report can be unreliable.”

---

### 12. Framework citations are selectively used

**Quote:**

> “The two published frameworks for grading progress toward general intelligence both treat autonomy as a deployment choice…”

There are more than two frameworks. Also, the paper paraphrases them in a way that serves its thesis.

For Morris et al., verify whether the exact claim “autonomy is a deployment choice constrained but not fixed by capability” is a direct quote or a paraphrase. If paraphrase, label it as such.

For Feng et al., verify the exact quote:

> “can be treated as a deliberate design decision, separate from its capability”

If this is not exact, do not use quotation marks.

**Required change:**  
Say “two frameworks we use” rather than “the two published frameworks.” Provide exact quotes or clearly marked paraphrases.

---

### 13. ARC-AGI-3, International AI Safety Report, Davos, and Redwood claims need primary verification

These are all post-2026 or near-2026 claims. They are not rejected for being future-dated, but they must be precise.

**Problematic precise claim:**

> “recovers about 67 % of the capability gap with 16 characters per message”

This is highly specific. It needs a direct citation, preferably with the exact experimental setup.

**Required change:**  
For each 2025/2026 source:

- archive it;
- quote the exact sentence;
- provide section/timestamp;
- mark if it is a paraphrase.

---

## B. Logical gaps in §5–§6

### 1. Attested byte share is not autonomy

**Quote:**

> “The attested share rises, not because a detector improved, but because the human channel into the file narrows while the machine channels multiply.”

This assumes what it needs to prove.

Autonomy is about who selects goals, plans tasks, initiates actions, handles exceptions, and accepts risk. Byte share does not measure those. A human can write detailed prompts and review every line while the machine emits all bytes. That is high attested share, low autonomy.

**Required change:**  
Either prove the mapping or drop the claim.

---

### 2. Constant coverage is not observable without independent measurement

**Quote:**

> “holding hook coverage constant”

If the hook is the thing measuring coverage, the method is circular. A new unlogged channel may be invisible until after the fact. The paper says this is the method’s job, but for scientific measurement you need an independent way to know coverage changed.

**Required change:**  
Define how coverage is audited independently of the hook. Examples:

- OS-level file-write tracing;
- IDE event logs;
- CI artifact comparison;
- filesystem snapshots;
- process monitoring;
- differential analysis between expected and observed writes.

Without this, “constant coverage” is an assumption, not a measurement.

---

### 3. The registry would be self-selected and gameable

**Quote:**

> “A registry of labelled work, counting attested shares over time with no names attached, would be a measurement of autonomy adoption taken in the field…”

No, it would be a measurement of labelled, self-selected, instrumented artifacts. It may be biased toward:

- AI-tool vendors;
- teams seeking marketing;
- repositories with trivial generated content;
- teams avoiding liability-sensitive work;
- teams optimizing the metric.

**Required change:**  
Call it a self-selected adoption index, not a field measurement of autonomy. Add anti-gaming and sampling design.

---

### 4. The falsification test is too weak

**Quote:**

> “If the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong and the human hand is doing something the frameworks do not capture.”

This does not falsify the thesis cleanly. Flat attested share could mean:

- teams choose not to grant autonomy;
- safety policies restrict deployment;
- task mix changes;
- human review increases;
- unlogged agent channels increase;
- measurement coverage changed;
- the label is adopted mostly by low-autonomy teams.

Also, capability can rise without deployment autonomy rising. That does not mean the frameworks are wrong.

**Required change:**  
Separate hypotheses:

1. Capability is rising.
2. Teams are granting more autonomy.
3. Attested byte share measures that autonomy.
4. Coverage is stable.

Then specify which observation falsifies which hypothesis.

---

### 5. “Registers the approach before any benchmark declares it” is an overclaim

**Quote:**

> “So the label registers the approach before any benchmark declares it.”

A deployment label cannot register general capability before benchmarks. It can register that a team allowed a system to write bytes in a particular context. That is not AGI approach. It may be narrow automation.

**Required change:**  
Replace with:

> “The label records deployment choices that benchmarks do not capture.”

Do not say it registers AGI approach.

---

## C. Ways the label could mislead or be gamed that §7 misses

### 1. “Guaranteed AI” may be read as a quality or safety mark

Readers may see “Guaranteed AI” and infer:

- the AI output is safe;
- the output is tested;
- the output is reliable;
- the output is non-infringing;
- the AI is highly capable;
- the artifact has been certified by a neutral body.

None of these follows.

**Fix:** Add explicit disclaimers and rename/qualify the badge.

---

### 2. “Pure AI” may be read as “no human contribution”

Even with 100% machine-written bytes, humans may have contributed:

- prompt;
- specification;
- training data;
- model choice;
- constraints;
- review;
- acceptance;
- editing after generation;
- selection among alternatives.

**Fix:** Define “Pure AI” as “100% of final bytes attested through machine channel” and warn that it does not mean no human creative contribution.

---

### 3. Human text can be laundered through the machine

This is the biggest semantic hole. If a human says, “write exactly this,” the machine channel can attest human-authored content. The paper admits this but does not face the consequence: the label cannot certify machine authorship in the ordinary sense. It certifies machine-channel transit.

**Fix:** Say this plainly in the abstract:

> “The label does not prove that the machine originated the content. It proves that the content passed through a designated machine channel.”

---

### 4. Scripts and non-AI automation may be counted as AI

If a formatter, template generator, build script, or macro writes through the signed channel, does that count? If yes, “AI” is misleading. If no, the spec must exclude it and explain how.

**Fix:** Define “machine channel” and distinguish AI generation from automation.

---

### 5. Line-count weighting can hide important human edits

A repository can have 95% machine-generated boilerplate and 5% human-written security-critical code. A “Guaranteed AI” badge based on lines may mislead readers about where the important work occurred.

**Fix:** Report multiple metrics:

- attested lines;
- attested hunks;
- attested files;
- attested semantic units;
- unattested critical paths, if known.

At minimum, warn that line share is not importance share.

---

### 6. Badge staleness needs cryptographic binding

Terms of use are not enough. If the artifact changes, the badge should fail.

**Fix:** Bind badge to hash and version. Provide verifier that returns “stale” or “invalid.”

---

### 7. Transparency logs do not solve false entries

A transparency log can make history append-only and auditable. It does not make signed statements true.

**Fix:** Clarify that Level 2 provides tamper-evidence and fork detection, not truthfulness.

---

### 8. Privacy leakage from unattested lists

If the label lists unattested lines/files, it may reveal:

- who edited what;
- sensitive internal comments;
- security patches;
- personal data;
- legally relevant admissions.

On small teams, “no names” does not prevent identification.

**Fix:** Provide redaction, hashing, aggregation thresholds, or access-controlled disclosure. Do not claim privacy merely because names are omitted.

---

### 9. Registry can be flooded with trivial AI content

If the registry counts attested share, people can create huge machine-generated files to inflate the number. This is a classic Goodhart problem.

**Fix:** Define registry inclusion criteria, deduplication, task metadata, and outlier handling.

---

### 10. The label may be mistaken for regulatory compliance

The EU AI Act and C2PA discussion invites readers to think this label solves legal marking. It probably does not, especially for text and source code.

**Fix:** State explicitly:

> “This label is not, by itself, evidence of compliance with the EU AI Act or any other legal regime.”

---

## D. Specific wording that overclaims

### 1. “none can be checked by a third party”

Too absolute. Replace with “many cannot be independently re-derived by a reader.”

---

### 2. “Machine writing arrives with a prompt, a diff, a log, a test run and a signature, and hand writing arrives with none of those”

False as a universal claim. Replace with an instrumentation-dependent statement.

---

### 3. “the attested share is the share a reviewer can trace”

Only under trust assumptions. Replace with:

> “the attested share is the share for which the reviewer can verify a machine-channel signature, given the ledger and trust model.”

---

### 4. “the machine share of new code at the largest labs rose…”

Overgeneralized. Replace with source-specific claims.

---

### 5. “roughly the doubling cadence METR measures”

Incorrect comparison. Delete.

---

### 6. “both statements, eighteen months apart, name the human's remaining role in the same words”

The quoted phrases are not the same words: “reviewed and accepted” vs “approved”. If you mean similar role, say “similar language.”

---

### 7. “Developers could not tell, from the inside, whether the machine had helped.”

Overstates the RCT. Replace with “developers misperceived the productivity effect in that study.”

---

### 8. “The two published frameworks”

Overstates uniqueness. Replace with “Two published frameworks we examine.”

---

### 9. “All of them agree on the shape”

Too broad. The cited sources do not all agree on the same shape of progress.

---

### 10. “When the second number approaches 100 % … the human has moved wholly to authorisation and review”

No. 100% attested bytes could occur with heavy human control or narrow automation. Delete or heavily qualify.

---

### 11. “A mark that could not survive the arrival of the thing it measures would not be worth designing.”

Rhetorical. Level 2 may not survive adversarial AGI either. Replace with a precise security statement.

---

# Minimum changes required for publication

I would accept a revised version only if it:

1. reframes the label as **signed machine-channel provenance**, not AGI measurement;
2. removes or rigorously validates the §5–§6 autonomy/AGI claim;
3. replaces “Guaranteed” with explicit self-signed attestation language;
4. provides a real threat model;
5. replaces secondary citations with primary sources or clearly labels claims as unverified;
6. defines units, coverage, denominator, and verification deterministically;
7. expands the gaming section substantially;
8. adds legal/safety/copyright/compliance disclaimers;
9. publishes reproducible verification artifacts.

If the authors make those changes, the paper becomes a credible contribution to content provenance. If they insist that this label is a field measurement of rising autonomy toward AGI, it should not be published in its current form.

### D. moonshotai/kimi-k3
# Review: "Guaranteed AI" (v0.1)

**Verdict: publish after fixes — major revision.** The core artifact (write-time signed ledger, coverage-not-detection, honest non-guarantees, §8's self-failing 17 %) is sound and rarer than the genre's usual. But §5–§6 rest on a category error, the falsification test can't falsify, §7 misses the largest attacks, and several load-bearing sentences are factually wrong or overstated. None of it is fatal; all of it must be fixed before this circulates as a white paper.

Credit where due, briefly: the heredoc result in §2 is the right insight; the 8 % precision arithmetic checks out (5/(5+0.6·95) ≈ 8.1 %, and it's correctly an upper bound); the METR RCT numbers (16 devs, 246 tasks, 19 % slower, 24 %/20 % perception gap) match the source; Sadasivan, Greenblatt, Meinke, Morris, Feng citations are real and correctly characterized.

---

## 1. Factual claims and attributions

1. **§4: "both statements, eighteen months apart, name the human's remaining role in the same words: 'reviewed and accepted', 'approved'."** Literally false — those are not the same words, and you quote them differently yourself. Worse, the 2026 half of this claim rests on Semafor, which ref 10 admits is "Primary transcript not located." You built a rhetorical keystone on an unverified secondary quote. Verify the transcript or delete the parallel.
2. **§4: "which is roughly the doubling cadence METR measures for task horizons."** Numerically wrong on its own terms. A quarter to three quarters in 18 months is ×3, i.e. ~1.6 doublings, a doubling every ~11 months — not 7. And it's categorically inapposite: a company's adoption share is not a capability horizon. Delete the rhyme.
3. **§4: "Two independent measurements sit behind the reported figures."** Anthropic's Economic Index is Anthropic measuring Anthropic — the same interested-party problem as the earnings calls, with better telemetry. METR is independent but measures capability, not adoption, so it doesn't sit "behind" adoption figures at all.
4. **§4: "Developers could not tell, from the inside, whether the machine had helped. A team that cannot tell from the inside needs an instrument, and the instrument has to count bytes."** Misapplication of [14]. The METR RCT measured *productivity* perception, not *provenance* perception. Nothing in it shows developers can't tell which bytes they typed. You need direct evidence for the authorship-perception claim or a softer sentence.
5. **§4 table mixes denominators without saying so.** Google: "new code." Microsoft: "code inside the company's repositories" (stock, not flow). Anthropic: "code." The abstract's "from a quarter to three quarters … at the largest labs" is a single-company arc wearing a plural. Add a denominator column; fix the abstract.
6. **§5: "Morris et al. … place today's frontier chatbots at the lowest rung."** Morris et al. assessed 2023 systems. "Today's" in a September 2026 paper is stale by three model generations.
7. **Ref 12: the Kwa et al. title is "Measuring AI Ability to Complete Long Tasks," not "…Long Software Tasks."** Sloppy in a paper whose entire thesis is attribution precision.
8. **§1: "C2PA … has no profile for a text file or a source repository."** Overstated. C2PA supports external/sidecar manifests for arbitrary assets; the accurate claim is "no embedded-manifest binding for plain text and no VCS-aware provenance model." You hedge in ref 5 but state it flatly in the body.
9. **§1: "Nobody has shipped the mark that points the other way."** False as stated. Meta's "AI Info"/"Made with AI" labels, TikTok's and YouTube's AI-content disclosures, and Article 50's own machine-readable marking all point the other way. Your actual gap is *third-party-verifiable provenance for text/code* — claim that, not "nobody."
10. **Ref 2 is Wikipedia.** In a paper arguing nothing should be believed unless re-derivable, sourcing the competitive landscape to a tertiary source is a bad look. Cite each operator directly.
11. **§1: "IPTC's reading is that C2PA … is the only existing technology that meets that requirement."** "Only" is a strong word; verify the page says it, and quote it exactly.
12. **2026 sources:** Rao's "90 %-plus" and the Redwood 67 %/16-characters figures are plausible and properly hedged as reported. The Pichai 75 % quote is plausible on trajectory, but its narrative-convenient echo of the 2024 phrasing is exactly why it must be checked against a transcript. iHeart's "Guaranteed Human" was announced November 2024, not 2025 — minor.
13. **§6: "the authors note that few remaining tasks defeat the newest models"** — strong claim, needs an exact quote or a softer paraphrase.

## 2. Logical gaps in §5–§6

1. **The category error at the core.** Feng et al. and Morris et al. grade *decision authority and oversight*. Your ledger grades *who typed the bytes*. Attested share 100 % is fully compatible with a human approving every hunk (Feng L4, not L5); attested share 0 % is fully compatible with a human hand-copying model output from a chat window (total AI authorship, zero attestation). So §6 step 5 — "the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders" — is false. The instrument measures delegation of *inscription*, not delegation of *judgment*. It cannot distinguish Approver from Observer, which is precisely the distinction the ladders exist to draw.
2. **The denominator is a residual.** "Unattested" lumps human typing, unlogged AI (chat copy-paste, heredocs — your own 9 % result), vendored code, and generated files. §5's thermometer reads the complement of attested share as "the human channel." Your own data refutes that reading.
3. **Coverage is endogenous — and controlled by the measured system.** "Held at constant instrumentation" assumes the agent keeps using the logged channel. §8 shows the agent spontaneously routing around it via heredocs, non-adversarially, today. The thermometer's key assumption is in the hands of the thing it measures.
4. **The falsifier doesn't falsify.** "If the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong." But your own frameworks say autonomy is a *deployment choice* — adoption lagging capability is predicted, not falsifying. And a rising share has rival explanations (task mix, padding, improved logging), so it can't confirm either. The abstract's "the one measurement that would show the thesis to be wrong" names a measurement that shows no such thing.
5. **No validation against an independent criterion.** The instrument is calibrated against nothing. If attested share is a measure of autonomy, correlate it with something — Feng-level assessments, session-level autonomy metrics from [13] — before calling it a field measurement.
6. **Selection.** An opt-in registry is not "everyone's number"; it's the number of shops that bought in, with adverse selection toward high-AI adopters and selective registration of flattering artefacts.
7. **Task-mix confound.** Share can rise because more task *types* get delegated at constant per-task autonomy. Your own citation [13] decomposes exactly this effect; the registry design ignores it.
8. **§6 misidentifies the weak link.** The adversarial paragraph defends ledger *integrity* (Level 2 anchoring), but the demonstrated failure mode is *coverage* — and a scheming agent's first move is unlogged channels, which anchoring does nothing about. Also, "a Level 1 self-signed label is sufficient while the machine is an honest scribe" is true only if the human key-holder is honest too, which §7 already concedes is not guaranteed.

## 3. What §7 misses

1. **Unlogged AI attests as human.** Paste from a chat UI, an unharnessed agent, a heredoc — all land in "unattested," which the market *will* read as "human" no matter what your face page says. The label thereby exports a false human guarantee by implication. This is the biggest hole in the design and §7 doesn't list it.
2. **Non-AI automation attests as "AI."** Formatters, codegen, templates, `sed` through a logged tool — all "machine channel," zero AI. The mark certifies *automation*, not *AI*. "Pure AI" can be 100 % human-dictated (you admit this) or 100 % deterministic tooling (you don't).
3. **Dilution and scope gaming.** Pad attested boilerplate to cross 90 %; choose unit definitions and exclusions (vendored? generated? minified?) that flatter the ratio; label a subdirectory. §8 does exactly this last one — "the check on the `label/` directory alone should say so" — while the repository attests at 17 %. Scope selection needs a rule, and the badge needs to carry its scope.
4. **Key governance is absent.** No PKI, no revocation, no rotation, no story for key theft or CI jobs signing with the machine key. Level 1 timestamps are self-asserted. And §7's "the accountability sits with the key-holder, who is named by fingerprint" contradicts §3's "never a name" — a fingerprint names a key, not a person, and accountability to *whom*, enforced *how*?
5. **Nothing binds the displayed seal to a ledger.** "The terms of use forbid displaying a number older than the last change" is not a mechanism. Without a hosted verifier and mark governance, the badge is a JPEG and verification friction means nobody reruns your tool.
6. **Re-identification.** "Aggregates per repository, not per person" fails on any repo with public git history — diff the ledger against `git log` and "unattested" has a name. On small teams your mitigation is decorative.
7. **AI-washing adverse selection.** Level 1 lets marketing mint any number with cryptographic-looking cover, and the early adopters of an AI-share label are precisely those with investor incentives to inflate it. §7's threat model assumes people want to hide AI use; many will want to fake *more* of it.

## 4. Overclaiming wording (quote and fix)

- Abstract: "with every **hand-typed or unlogged span** listed beside the number" — your own §2 says unattested ≠ hand-typed. The abstract commits the conflation the paper warns against.
- Abstract: "Machine writing arrives with a prompt, a diff, a log, a test run and a signature, and hand writing arrives with none of those" — harness-relative, stated as absolute. Machine writing via chat UI arrives with nothing; humans can sign commits.
- §2: "It is the least reviewed byte in the repository" — unsupported superlative.
- §3: "ours is counted by the verifier" — at Level 1 the verifier recomputes the author's self-asserted, self-signed ledger; completeness is unenforced until anchoring exists.
- §4: "That is the role the label is built to make visible" — the ledger records writes, not approvals. It makes non-typing visible; review is invisible to it.
- §5: "would be everyone's number" — opt-in.
- §6: "the most-cited operational yardstick" — unsupported superlative.
- §6 title: "The argument for general intelligence" — the section argues no such thing.
- §7: "What it counts is the one thing that has no other record: the unreviewed edit after the machine finished" — unattested ≠ unreviewed; attested ≠ reviewed. Channel is not scrutiny.

---

## Numbered fixes, most important first

1. **Rewrite §6 step 5 and the §5 thermometer claim.** Attested share measures delegation of inscription, not autonomy. Either add a validation study correlating attested share with an independent autonomy assessment, or downgrade the claim to "consistent with rising delegated autonomy under stated coverage assumptions."
2. **Replace the falsification test.** Specify one that binds (e.g., pre-registered: share rises while independent autonomy assessments stay flat ⇒ instrument invalid), and delete "the one measurement" from the abstract.
3. **Fix the abstract and the label face:** "every unattested span," plus an explicit on-seal statement: "Unattested ≠ human. This mark certifies channel, not authorship. Unlogged AI attests as unattested."
4. **Rename the grades or carry the caveat on the seal.** "Pure AI" and "Guaranteed AI" certify machine-*channel*, which includes human-dictated text and non-AI tooling. "100 % Attested Machine Channel" is what the mechanism actually delivers.
5. **Add to §7:** unlogged-AI-as-human; dilution/padding with defined unit and exclusion rules; a ban on directory-scoped badges (or scope printed on the badge — §8's `label/`-only check is scope selection); key theft/CI/revocation/rotation and self-asserted L1 timestamps; badge-ledger binding, a hosted verifier, and mark governance; AI-washing adverse selection at Level 1.
6. **Fix §4:** delete "in the same words" or quote exactly after verifying the Semafor transcript; add a denominator column to the table; delete the METR-cadence comparison (it's numerically wrong — ×3 in 18 months is ~11-month doubling — and categorically inapposite).
7. **Fix the METR RCT use:** it measured productivity perception, not provenance perception. Find direct evidence that developers misjudge authorship share, or soften "nobody in the loop can see the line."
8. **Delete or make true "the role the label is built to make visible":** either log signed review/approval events as first-class units, or state plainly the label cannot see review.
9. **Registry honesty:** replace "everyone's number" with the opt-in reality; require enrolled repos to register *all* artefacts; stratify reported shares by task type, since your own [13] shows composition drives the effect.
10. **Rewrite §6's weak-link paragraph:** the weak link is coverage under agent control (§8's heredocs), which Level 2 anchoring does not fix; and Level 1 is insufficient against the human key-holder even with an honest machine — say so in one sentence.
11. **Privacy:** acknowledge git-history re-identification defeats per-repo aggregation on public repos; set minimum cohort sizes and suppress per-file breakdowns below them.
12. **Delete from §7:** "the unreviewed edit" (channel ≠ review) and "named by fingerprint" (contradicts the no-names rule; no PKI exists to bind fingerprints to holders).
13. **Citation hygiene:** correct the Kwa et al. title; "today's" → "2023's" for Morris et al.; replace Wikipedia with primary sources; verify the IPTC "only," the Feng verbatim quote, and the "few remaining tasks defeat the newest models" paraphrase.
14. **Fix §1's gap claim:** acknowledge Meta/TikTok/YouTube AI-disclosure labels and Article 50 marking as machine-pointing marks; claim specifically the *verifiable, third-party, text/code* gap. While there, note Article 50(4)'s human-review exemption — it strengthens your argument that the human role is where law and label meet.
15. **Soften §2's absolutes** ("no prompt, no log and no signature," "least reviewed byte") to the defensible claim: the asymmetry is granularity and automaticity, not existence.

The engineering is good enough to deserve a paper that doesn't overclaim it. Fix the category error and the falsifier, and this is publishable; leave them, and §5–§6 will be quoted back at you by the first competent reviewer who notices that a thermometer for typing is not a thermometer for thought.

### E. deepseek/deepseek-v4-pro-0813
**Verdict: do not publish in current form.** The provenance-label idea is worth publishing as an engineering proposal, but the paper’s central claim—that attested share is a field measurement of rising autonomy toward AGI—is not earned. It commits the classic error of treating a convenient observable as though it were the theoretical quantity of interest.

## Blocking problems

1. **§5–§6 overclaims what attested share measures.**  
   Quote:  
   > “A registry of labelled work, counting attested shares over time with no names attached, would be a measurement of autonomy adoption taken in the field, on real artefacts, independent of benchmarks and of what executives say on earnings calls.”  
   This is the core thesis, and it is too strong. An opt-in registry of labelled work measures *adoption of an instrumented workflow*, not autonomy. Attested share can rise because a team starts logging auto-formatting, because more generated boilerplate enters the repo, because the definition of a “unit” changes, because old unlogged files are excluded, or because the team selects easy repositories. Holding “hook coverage constant” does not fix this; it is not a controlled experiment, and coverage is only partially observable. This should be reclassified as a *provenance adoption metric*, not “autonomy adoption.”

2. **The argument that rising attested share implies the human “moved wholly to authorisation and review” is invalid.**  
   Quote:  
   > “When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders.”  
   No, 100% attested means only that all counted bytes passed through a logged machine channel. The §7 gaming example “write exactly these lines” already admits a human can produce the text and route it through the hook. Therefore a team could hit 100% with less autonomy, not more. This sentence must be deleted or rewritten: attested share cannot distinguish a delegated task from a human-authored prompt with generated transcription.

3. **The falsification test is too weak to rescue the thesis.**  
   Quote:  
   > “If the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong and the human hand is doing something the frameworks do not capture.”  
   This only catches flat share while capability improves. But the paper claims more than “share may rise with capability”; it claims the share is a *measurement of autonomy toward AGI*. A rise would be confounded by the same factors above. The proposed test should be replaced with a causal model of what would count as disconfirming evidence, including gaming, selection effects, and tooling changes.

4. **The factual foundation for the “rising share” trend is shaky.**  
   Quote from Table:  
   > “29 Apr 2025 | Satya Nadella, at LlamaCon”  
   This attribution looks wrong or at least suspicious. LlamaCon is Meta’s conference; Satya Nadella is Microsoft’s CEO. He may have spoken at a Microsoft event, an earnings call, or a podcast, but “at LlamaCon” is exactly the kind of detail that should not appear in a table of record without a primary transcript. Also, the Abstract says:  
   > “The machine share of new code at the largest labs rose, by their own reported figures, from a quarter to three quarters between October 2024 and April 2026.”  
   The quarter-to-three-quarters movement is specifically a Google claim. Anthropic’s “90 %-plus” is a different company, different denominator, different reporter, and possibly different definition. Do not pluralize this into “the largest labs.”

5. **The Level 2 security claim overstates what anchoring does.**  
   Quote:  
   > “A developer with the key can sign anything or delete records. Level 1 does not defend against it; Level 2, with the ledger head anchored in a log the developer cannot rewrite, does.”  
   Anchoring the ledger head in Rekor prevents silent deletion/rollback; it does not prevent the key-holder from signing false records before anchoring. If the writer controls the recorder, anchoring just gives a timestamp on a lie. The defense against “sign anything” is a trusted executor outside the writer’s reach, which the paper mentions elsewhere but does not actually specify. Fix this sentence so it distinguishes deletion tampering from false claims.

6. **The self-test in §8 is not checkable by the reader.**  
   Quote:  
   > “This white paper and the spec beside it were written through the signed channel on purpose, and the check on the `label/` directory alone should say so; if it does not, the ledger is right and this sentence is wrong.”  
   This is clever but useless to a reviewer without the key, the ledger, and the repository state at the stated date. It also risks being false even if the authors are sincere. Publish a reproducible receipt: commit hashes, key fingerprint, signed ledger entry URL, and a command the reader can run.

## Gameability the paper misses or underplays

7. **AI-mediated laundering of human text.**  
   A human can run existing human work through an LLM to paraphrase/format/refactor it, then route the result through the attested channel. The label would say machine-written, but the substance and decisions were human. The paper mentions routing hand text through the hook, but not laundering through a model after human writing.

8. **Selective labeling scope.**  
   The paper says the badge carries a check date, but not how much of the repository/artefact the labelled number covers. A team can label only the files or directories with high attested share while omitting older or more human-authored parts. The spec needs a required coverage declaration and a stable unit of measurement, e.g., all changed lines in a commit, all files in a directory, all paragraphs in a document.

9. **External dependencies and imported work.**  
   The label appears to count units inside the authored artefact but not imported libraries, generated build artifacts, vendor directories, or submodules. A team could move difficult human work into a dependency and leave the top-level repo clean. If the label is intended to measure “the work,” it must define whether dependencies are in scope.

10. **Key sharing and coerced signing.**  
    The paper states accountability sits with the key-holder, “named by fingerprint in every record.” That is not enough. A key can be shared, stolen, or used by an agent controlled by someone else. Level 2 should specify key custody, hardware-backed keys, rotation, revocation, and what happens after a key is compromised.

## Misleading wording

11. **“Pure AI” is a bad name.**  
    Quote:  
    > “Two grades: **Pure AI** at 100 % attested…”  
    The paper itself says the label does not guarantee “that no human decided the content,” but the term “Pure AI” is public-facing and will be read as exactly that. Rename it “100 % attested” or “fully machine-channel.”

12. **“Machine writing” is used as though it meant autonomy.**  
    Quote:  
    > “When an agent harness writes a file, the write goes through a tool call.”  
    That is true for some agentic workflows, but much machine writing—autocomplete, IDE completions, generated patches pasted manually, snippet generation—does not arrive with a signed diff, log, and signature. The label should claim only what the instrumented channel can prove, not that all machine writing has this property.

13. **The least-reviewed-byte claim is rhetorical overreach.**  
    Quote:  
    > “It is the least reviewed byte in the repository, and it is invisible precisely because it looks like every other byte.”  
    Human edits are often reviewed via pull requests and version control. The paper does not need this unsupported superlative. It can say that hand edits lack the same *provenance trail*, without claiming they are uniquely unreviewed.

## Most important fixes, in order

1. **Rewrite §§5–6 to remove the claim that attested share measures autonomy toward AGI.** Recast the label as a provenance mechanism and an opt-in deployment metric, not AGI progress.  
2. **Delete or rewrite the “100% means the human has moved wholly to authorisation and review” inference.**  
3. **Correct the attribution of the Nadella 20–30% figure and stop generalizing Google’s quarter-to-three-quarters as a lab-wide trend.**  
4. **Fix the Level 2 security claim to distinguish anchoring from trusted execution.**  
5. **Add the missing gaming modes: AI paraphrasing of human work, selective scope, external dependencies, key sharing/coercion.**  
6. **Replace “Pure AI” with a label that cannot be reasonably misread as “no human involved.”**  
7. **Publish a reproducible self-check for §8 with commits, key fingerprint, and ledger entries.**  
8. **Define units, coverage, and import/external-file scope in the spec before claiming a verifiable number.**  
9. **Tone down phrasing that suggests the registry will be “independent of benchmarks and of what executives say” when it is self-selected and workflow-dependent.**  
10. **Add primary-source verification for all 2026 figures; secondary reporting is fine but must not be stated with the certainty of a primary record.**

The label itself may be useful. The AGI argument is not ready.

### F. x-ai/grok-4.6
**Verdict: do not publish.**

This is a README for a self-signed line-count badge with an AGI press release stapled on. The engineering intuition (log tool calls; do not guess from style) is real. The claim that the resulting ratio is a field thermometer for autonomy toward AGI is a category error, and it is the claim the abstract, §5 and §6 exist to sell. A label spec can be a spec. This document should not ship as an argument.

---

### (1) Facts and attributions

I am not rejecting 2026 URLs for being 2026. I am rejecting overstatement, secondary citation of the paper’s load-bearing numbers, and several claims that are already wrong on the pre-2026 record.

- **Load-bearing lab numbers are press, not measurements.** Table rows for Pichai 75% and Rao “90%-plus” are “cited as reported,” and [10] admits “Primary transcript not located.” You then treat them as a “reported curve” in §6.2. That is not how a measurement paper may use earnings-call colour.

- **Pichai 2024 is real; your gloss is not.** The Q3 2024 line about “more than a quarter of all new code at Google is generated by AI, then reviewed and accepted by engineers” was said. This sentence is the overreach: “Not typing, approving.” Executives have used that wording for autocomplete and chat-paste for years. It does not imply the human channel into the file has narrowed, which is what you need.

- **“Roughly the doubling cadence METR measures” is arithmetically false.** 25% → 75% in eighteen months is a tripling of a *share of new lines*, against a ~7-month doubling of *50%-reliability task duration*. Different units, different exponents. Delete the analogy.

- **METR RCT [14] is real and you cite it fairly; you then ignore it in the chain.** The 19% slowdown, 24% forecast, 20% posterior belief is the right paper. It does not support §6.2 “Adoption rises on a reported curve.” It supports “self-report and byte-share are not productivity, not autonomy, and not capability.”

- **§1’s “none can be checked by a third party” is already false on your own citations.** You write: “Each is a declaration, an estimate or a platform’s undisclosed judgement. None can be re-derived by a reader.” Then [4] is a signed, time-stamped, tamper-evident provenance mandate, and C2PA exists. The true gap is *direction plus text/repo profile*, not checkability.

- **“Nobody has shipped the mark that points the other way” is overstated.** Watermarks, “made with AI” UI, generative-AI Content Credentials, platform AI-music flags, and assorted “AI-assisted” PR labels already point that way. What you have not seen is *your* ledger of unattested spans. Write that.

- **C2PA [5] is labelled as “the authors’ reading.”** Keep it that way. Do not let IPTC-via-press decide that it is “the only existing technology.”

- **Human labels sourced from Wikipedia [2].** Unacceptable for the opening catalogue. Primary pages or it is anecdote.

- **Sadasivan et al. [7] is a real paper; it does not say what you use it for.** It is about detectors/watermarks collapsing as distributions converge. It is not a proof that *any* non-ledger label “would be wrong most of the time, and wrong about people.”

- **Morris et al. [15] is real** (`arXiv:2311.02462`): performance levels plus a separate autonomy axis. You cite the axis and then measure keystrokes. That is not their variable.

- **“Hand writing arrives with none of those” is false.** Humans have git, signed commits, CI, tests, review. They lack *prompt/tool-call* provenance. Say only that.

- **“It is the least reviewed byte in the repository”** is an assertion with no evidence, and it fights your own METR citation (people rubber-stamp model output and misjudge it).

- **n=1, five weeks [6] cannot carry §2–§6.** 2,716 writes / 72,681 lines on one machine is a coverage demo. It is not “the method.” The 17% self-score in §8 is more informative than the 96% median, and you bury it.

- **Ref [22] 67% gap recovery with 16-character hints:** too specific to invent, too convenient to leave as a blog. If you keep the AI-control turn, quote the protocol’s actual threat model; do not use it as set dressing for Level 2.

---

### (2) Logical gaps in §5–§6 (this is the kill)

The attested share is: *(bytes that passed a named, hooked write channel and were signed)* / *(bytes in the tree, under some unit definition)*. That is not autonomy, not AGI, and not “what a team let it do” in the sense of Morris/Feng.

1. **Typing share ≠ autonomy.** Morris and Feng’s autonomy ladders are about goal-directedness, environment action, and how long the human can leave. A human can still specify every task, write every prompt, and approve every hunk while 95% of lines are model-emitted. That is delegation of keystrokes. Your own Google quotes are “reviewed and accepted.” That is still a human in the loop at PR grain, i.e. low on those ladders.

2. **Capability confounds the ratio even at “constant hook coverage.”** Longer-horizon models emit larger contiguous hunks. Attested share rises because the generator writes more of the file per call, not because anyone “chose” more autonomy. You never separate “model got better at filling buffers” from “team granted a higher autonomy level.”

3. **The falsification test does not test the thesis.** “If the share stays flat at constant coverage while METR horizons keep doubling, the thesis is wrong” is one failure mode. The interesting failures are the other way: share rises because of codegen, formatters, test fixtures, lockfiles, rewrites, or new hooked channels mis-counted as constant coverage. A one-sided test that can only fail in the direction you do not expect is not falsifiability.

4. **§6.5 is the overclaim the rest was built to reach.** Quote: “When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders.” False. Top rungs are not “human no longer types.” They are skill acquisition, novel environments, and operating without a human specifying the task (ARC-AGI-3’s bar, which you cite and then ignore). 100% attested lines with a human writing the issue and the prompt is still a tool.

5. **Registry ≠ “everyone’s number.”** Opt-in labelled artefacts from teams that already run your hook are a selection of agent-heavy, instrumentation-heavy shops. Independent of earnings calls, yes. Independent of adoption bias, no.

6. **Lab self-reports are not the same random variable as your ledger.** Copilot-class inline, chat copy-paste, and “generated then accepted” will not all hit “the harness’s write tool.” You cannot chain [8]/[10] into [6].

7. **“Holds hook coverage constant, measured per channel” is not an operational field protocol.** New MCP tools, shell, browser, CI codegen, and editor LSP are unbounded. Your own repo is the counterexample: 17% because heredocs. You call that “the method reporting an unlogged channel.” Correct — and it means the time series is a history of your instrumentation, until proven otherwise.

8. **§6.1 “few remaining tasks defeat the newest models”** (paraphrase of METR) does not survive METR’s own framing (50% reliability, software tasks, selected distributions) or the jaggedness you cite from [18].

The only sentence you are entitled to: *if a team already logs every write channel, the hooked fraction of the tree is a lower bound on how much of that tree passed those channels.* Stop.

---

### (3) Gaming and misleading that §7 misses

§7 lists the honest-scribe failures (echo prompt, key-holder lies, stale badge, small-team identification, “anti-human” PR). It misses the ones that make a 90% badge cheap.

- **Denominator.** Units are undefined in the paper (“unattested unit listed”). Lines, hunks, files, tokens, paragraphs — pick one, then watch lockfiles, vendored code, generated protobufs, snapshots, `package-lock`, golden tests, and `gofmt`/`prettier` rewrites of human code mint “Guaranteed AI.”
- **Rewrite laundering.** Agent reads human file, writes it back. 100% attested, zero autonomy change.
- **Split-brain repos.** Design, prompts, and the 10% that matters live elsewhere; the public tree is a generation artefact.
- **CI as the writer.** Pipeline generates the artefact; the “authorising” human never touches bytes. That can be legitimate provenance — it is not a rise in agent autonomy.
- **Unlogged AI still exists, so the badge is a lower bound you market as a guarantee.** ChatGPT paste, Cursor unsandboxed apply, `curl | sh`, cloud agent on another machine. §7 discusses inflating attestation, not the reader who thinks “Guaranteed AI 92%” means “8% human thought.”
- **Name.** “Guaranteed AI” reads as warranty of quality, safety, or authenticity. “Pure AI” is the stricter grade; “Guaranteed” is the weaker 90% grade. That is inverted marketing.
- **Level 1 is a sticker.** Self-signed machine key, writer-controlled recorder. You admit this in §6 then still offer “Free to display on anything that passes” in §9. Most readers cannot rerun your CLI. Checkability is theoretical.
- **No bind to the shipped artefact.** Write-time signatures on tool calls are not a tree hash, not a commit SHA, not Rekor (that is v0.2). Ledger and HEAD can diverge; §7’s “stale number” policy is unenforceable terms of use.
- **Registry deanonymization.** Key fingerprints plus per-repo aggregates plus public quarterly counts will re-identify small teams. “Never a name” is not anonymity.
- **Regulatory camouflage.** Article 50 is about warning the public that content is synthetic. A pride badge can satisfy the letter while the claims that matter sit in prompts you refuse to count (“not bytes”).
- **§8 is not a check.** “If it does not, the ledger is right and this sentence is wrong” is unverifiable to a reader of a PDF.

---

### (4) Wording that overclaims (quote → problem)

- Abstract: “the attested share is the share a reviewer can trace.” Only given trusted hook, complete channel list, honest key, and matching tree. That is not the default.
- Abstract: “a team’s attested share, held at constant instrumentation, is the number that records that choice as it is made.” Records hooked bytes, not the autonomy choice.
- §1: “Every label on the market for AI-era content points the same way.” False (see above).
- §2: “When a person opens the same file in an editor at 23:40 and changes four lines, none of that exists.” Git exists.
- §2: “This label never guesses. It reads a signature or it says nothing.” Level 1 reads a signature the writer can mint.
- §4: “So the evidence supports a narrower claim than ‘the machine is better’: the machine writes a rising share…” Lab claims plus one RCT that went the other way on productivity.
- §5: “A registry of labelled work … would be a measurement of autonomy adoption taken in the field … independent of benchmarks and of what executives say.” Independent of executives only if you stop using them as §6.2.
- §6 title: “The argument for general intelligence, as the label sees it.” The label does not see that.
- §6.5: “So the label registers the approach before any benchmark declares it.” No.
- §7 last bullet: “What it counts is the one thing that has no other record: the unreviewed edit after the machine finished.” Unattested ≠ unreviewed; attested ≠ reviewed.

---

### Concrete fixes (most important first)

1. **Kill or rewrite §5–§6 and the abstract’s autonomy/AGI chain.** Replace with: hooked-byte share is a coverage statistic. Do not mention AGI, Morris/Feng ladders, or “thermometer” unless you define autonomy as something other than line share and show you can hold task mix, channel set, and unit definition fixed. Quote to remove: “So the label registers the approach before any benchmark declares it.”

2. **Define the unit, the denominator, and the bind to `HEAD`.** Lines vs hunks vs files; whether generated and vendored paths count; merkle of the tree vs write-time events. Without this the 90% grade is undefined and trivially gamed.

3. **Demote Level 1 to “self-attested log,” not a public guarantee.** Do not invite “free to display” until the signature covers the released artefact (commit/tree) and a log the writer cannot rewrite. Quote to change: “Three guarantees, each one checkable by rerunning the tool.”

4. **Rename.** “Guaranteed AI” as the *weaker* 90% grade is misleading. “Hook-attested ≥90% (Level 1 self-signed)” is ugly and honest.

5. **Primary sources or drop.** Wikipedia out of [2]; Semafor-without-transcript cannot carry §4/§6; IPTC paraphrase cannot carry “only existing technology.”

6. **Stop claiming uniqueness of checkability and of direction.** Rewrite the first paragraph of §1 to the actual gap: no widely deployed, third-party-checkable *text/repo* credential that lists unlogged spans.

7. **Gaming section: add denominator, rewrite-laundering, split repos, CI codegen, unlogged AI as lower bound, registry re-identification, no tree binding.** Quote that is incomplete: “A prompt of ‘write exactly these lines’ yields an attested hunk.”

8. **Retract “least reviewed byte” and “hand writing arrives with none of those.”** State only: hand edits typically lack prompt/tool provenance.

9. **Do not analogize Google share movement to METR doubling.** Different quantities.

10. **If you keep a prediction, pre-register the protocol:** channel inventory, how “constant coverage” is audited, unit definition, inclusion rules, and the *rise* conditions that would *not* count as autonomy. The current one-sided flat-share test is theatre.

11. **§8:** publish the actual `--label` output for `label/` (tree hash, key fingerprint, unit counts). A dare in prose is not a verification.

Until (1)–(3) are done, this should stay a `label/README.md`. It should not be a white paper that other people might cite as evidence that autonomy toward AGI is being measured in the field.

### G. z-ai/glm-5.3
**Verdict: publish after fixes — and the fixes are structural, not copy-edits.** The core instrument (signed write-time ledger, coverage-not-detection, per-channel accounting) is sound and worth publishing; the paper around it overclaims what the instrument measures, and §5–§6 as written asserts a result the instrument cannot deliver. If the authors decline fixes 1–6 below, my vote becomes *do not publish*, because the abstract would then be selling a guarantee the paper's own §7 disclaims.

**What survives scrutiny** (so you know I checked): the Pichai 29 Oct 2024 quote and the Nadella LlamaCon quote match my knowledge, as do the METR RCT numbers (16 developers, 246 tasks, 19% slower, 24% forecast, 20% believed), the METR ~7-month doubling finding, the Sadasivan arXiv ID and its thesis, the Greenblatt and Meinke citations, Morris et al.'s "Emerging" placement, Not By AI's 90% rule, the Authors Guild 2025 launch, and Article 50's 2 August 2026 applicability and your summary of it. The §2 precision arithmetic is internally consistent (5/(0.6·95+5) ≈ 8%). §8's self-application is the most credible thing in the paper. The 2026-dated sources I cannot verify; none of them reads as implausible except one, flagged in fix 6.

## Fixes, most important first

1. **The label certifies a channel, not authorship — make the name and abstract say so.** The abstract opens: "*Guaranteed AI* certifies that a machine wrote the work." §7 concedes: "The key proves the channel, not the author." Both cannot stand. A "Pure AI" badge on work whose every byte was pasted into a prompt by a human is false advertising by your own §7; and your own §2 shows the inverse failure — "the project's own source, which the agent had written through a shell heredoc instead of the logged tool, attested at 9 %" — the instrument reports machine work as unattested. The number is channel coverage in both directions. Even machine-to-machine the channel is not the author: your own §6 Redwood citation describes an untrusted model authoring work through a trusted executor's hands — under your label, the badge would name the executor. Rename the grades to what they measure ("Fully Attested" / "Attested ≥90%"), put "channel provenance, not authorship" on the badge face, and check the badge cannot be confused with the Article 50 icons it will sit beside — or with iHeartMedia's "Guaranteed Human," which you cite in §1; two "Guaranteed" marks pointing opposite ways is a confusion hazard you introduce yourself.

2. **§5–§6: the frameworks you cite sever the link to AGI; they don't build it.** You quote Feng et al.: autonomy "can be treated as a deliberate design decision, separate from its capability," and Morris et al. argue the same separation. If autonomy is a free deployment choice, a field measure of autonomy *adoption* measures a choice, not progress toward general intelligence: a team could hit 100% attested share with 2023-era models simply by preferring agents, and your registry would read it as climbing the ladder. "So the label registers the approach before any benchmark declares it" (§6.5) is the overreach — an adoption number cannot lead capability, and your own counterweight (the METR RCT: developers adopted tools they couldn't tell were useless) shows adoption does not track measured capability. Either state the missing empirical premise or re-scope §5–§6 to "a field measurement of agentic-channel adoption." The defensible claim is: at fixed, audited coverage, attested share is a lower bound on machine-written share and an index of delegation of *implementation*.

3. **Attested share cannot tell an operator from an observer.** §6.5: "When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders." Three errors. (a) 100% attested is equally consistent with a human who writes every prompt and iterates heavily — steering in the prompt channel, which you explicitly refuse to count ("the label counts none of those") — and with a rubber-stamping supervisor. The number is blind to the difference between steering and approving. (b) Factually, the top of Morris et al.'s autonomy axis is *Organization*, not agent; the axis runs Tool→Consultant→Agent→Innovator→Organization, so §5's "five levels from tool to agent" misstates the framework's endpoint, and "authorisation and review" is not the operating description of either ladder's top. (c) The ledger records no task length, so "across teams and task lengths" cannot be computed from your instrument at all.

4. **The §4 figures and the ledger's number are different quantities; stop chaining them.** §6.2: "Adoption rises on a reported curve." The four rows measure different things: Pichai's are flow ("new code"), Nadella's is stock ("code inside the company's repositories" — all code, not new), Anthropic's is undefined, and none says whether completions count. Your ledger counts only agent tool-call writes — IDE completions, plausibly the dominant channel in the early figures, cannot be hooked this way. So the registry's attested share is not comparable to any number in §4. The bridge sentence "which is roughly the doubling cadence METR measures for task horizons" (§4) is numerology: a 25%→75% share change in eighteen months is not the cadence of anything METR measures. Your own §8 is the reductio: Anthropic claims "90%-plus" while your flagship repo attests at 17% — the two numbers do not measure the same world. State each figure's denominator; cut the cadence parallel.

5. **The registry is not "everyone's number."** §5: "A registry would be everyone's number, re-derivable by anyone with the keys." §9 says it is "an opt-in count of labelled artefacts" — self-selected teams, labelling artefacts they chose to check: selection on the dependent variable. Add Goodheart: once the badge is worth having, teams route work through the agent channel *to raise the number* — the thermometer heats what it measures. Rewrite as "participants' number" and carry both caveats into §9.

6. **The falsification test doesn't falsify your thesis, and its control is unobservable.** §5: "If the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong and the human hand is doing something the frameworks do not capture." If autonomy is a deployment choice — your premise — flat share under rising horizons *confirms* the frameworks (teams declining to delegate) rather than refuting you. And "constant coverage" cannot be audited by a registry: §8 proves the method's own authors could not track their own channels. Separately, §6.1's "the authors note that few remaining tasks defeat the newest models" is the one quote in the paper that looks implausible to me: a 320-minute 50%-horizon means most longer tasks in METR's suite still defeat the best model. Quote METR verbatim or cut it.

7. **§7 overstates Level 2.** "A developer with the key can sign anything or delete records. Level 1 does not defend against it; Level 2, with the ledger head anchored in a log the developer cannot rewrite, does." Rekor anchoring makes *deletion* visible. It does nothing about "sign anything": the key-holder can simply never record a hand edit, or keep two ledgers and anchor the flattering head, or — per your own first bullet — route hand text through the hook and sign it honestly-but-falsely. Level 2 as specified fixes neither the first bullet nor the unrecorded edit. Move both to the unresolved list. (Also: §3 says Level 2 arrives "when that component exists" — transparency logs exist today; what doesn't exist is your integration.)

8. **The fingerprint is a name, and it is not accountability.** §7: "the accountability sits with the key-holder, who is named by fingerprint in every record" contradicts §3 ("the ledger records a machine key, never a name") and §7's fourth bullet ("The report gives lines and files, never names"). A key fingerprint is a persistent identifier — on a solo repo it *is* the person — and with no identity binding, revocation, or key-theft recovery, it provides no accountability whatsoever. Pick one story and spec the key lifecycle.

9. **§7 misses source laundering — the worst use of the label.** The first bullet prices "write exactly these lines" as an honesty problem for the badge-holder. Its serious use is laundering third-party content: paste stolen or human-written text through the agent, mint the badge, and "Guaranteed AI" advertises channel provenance while obscuring origin and rights. Add "proves nothing about originality, ownership, or rights" to the on-face disclaimers.

10. **§7 misses denominator and threshold gaming.** "Units" is never defined (§2 counts lines; §8 counts "units"); the share is byte-weighted, so 1,000 machine-written boilerplate lines swamp the ten human lines that carry the risk; and a team at 89.9% can launder the last tenth through the hook to cross the 90% grade. Define the unit, state byte-weighting on the label, and note the threshold is trivially crossable by re-emission.

11. **§7 misses that the badge does not travel and cannot age.** You fault C2PA for having "no profile for a text file" (§1), but C2PA embeds credentials in the asset; your ledger is repo-bound, and text copied out of the repo carries nothing — fatal for §9's "text provenance beyond code." Likewise "the terms of use forbid displaying a number older than the last change" binds no one downstream; put an expiry in the badge itself.

12. **§7 misses that model identity is self-reported.** §2: the tool call "carries... the model." The harness asserts the model; a wrapper can claim anything. So the label certifies neither author nor model. Add it to the "does not guarantee" list — which, incidentally, lists "not that no human decided the content" and "not the absence of human judgement": the same disclaimer twice. Merge them.

13. **Factual corrections in §5.** "The two published frameworks for grading progress toward general intelligence" — there are more than two: OpenAI's five-level scale (chatbots→reasoners→agents→innovators→organizations, reported July 2024) exists, and DeepMind's internal staging was reported in late 2025; moreover Feng et al. grade *autonomy*, not general intelligence. And "Morris et al. ... place today's frontier chatbots at the lowest rung" — they placed *2023's* chatbots there; in a 2026 paper "today's" misdates the assessment.

14. **The abstract and §1 open with false universals.** "Every label on the market for AI-era content points the same way: it tells the reader that a human made the work" — false, and contradicted three paragraphs later by your own discussion of Article 50 icons and C2PA, both of which mark machine content (as do SynthID and platform "AI info" labels). Likewise "Nobody has shipped the mark that points the other way" — C2PA credentials already attest AI generation with a signature, for media. And "Regulation points the same way, for a different reason" is backwards: Article 50 marks machine content, which is *your* direction; what it shares with the human marks is that it is a public warning, not a per-unit provenance record. Your real differentiators are (i) text and source files, (ii) per-unit listing, (iii) third-party re-derivability. Claim those.

15. **§2's rhetoric outruns the instrument.** "Hand writing arrives with none of those" — git history, signed commits and editor telemetry exist; say "no record of intent." "It is the least reviewed byte in the repository" — asserted, never measured; and §7's "the unreviewed edit after the machine finished" is unobservable by a ledger that cannot see review, only channel. Replace "unreviewed" with "unattested" wherever the instrument is the warrant. Also §7 bullet 5: "the label counts none of those because they are not bytes" — the prompt *is* bytes and is logged per §2; what the ratio excludes is prompt bytes. Reword.

16. **Sourcing.** [2] cites Wikipedia for the entire market survey (iHeart, Spotify, Berlinale) — go primary or cut. [10]: "Primary transcript not located" — yet §4 builds an argument on the reported wording ("both statements... name the human's remaining role in the same words"); obtain the transcript or drop the wording point. §4: "Two independent measurements sit behind the reported figures" — the Anthropic Economic Index is Anthropic's own data and cannot independently corroborate Anthropic's CFO. And verify Article 50's date against the final state of the Commission's Digital Omnibus, which proposed postponing parts of the Act.

17. **Carry the n=1 caveat into §5–§6.** §2's 96/0/9 numbers come from "one developer's machine over five weeks." §5–§6 generalizes to teams, registries and fields. Either say the instrument is unvalidated at team scale or instrument a second site before publishing the thermometer claim.

## Source-verification notes

**Verified accurate:** [1] Not By AI 90% rule; [3] Article 50 summary and date; [7] Sadasivan et al.; [8] Pichai quote and date; [9] Nadella quote, LlamaCon, 29 Apr 2025; [12] Kwa et al. and the ~7-month doubling; [14] METR RCT numbers; [15] Morris et al. "Emerging" placement; [20] Greenblatt et al.; [21] arXiv:2412.04984 title and thesis; Authors Guild 2025.

**Unverifiable (post-training), none implausible except one:** [4] EU Code of Practice, 10 June 2026, and the IPTC/C2PA reading; [10] Semafor 75%; [11] TechSpot "90%-plus"; [12] the Time Horizon 1.1 figures (320 min, 170–729); [13] the "Cadences" report; [17] ARC-AGI-3 quote; [19] Davos 2026; [22] Redwood "67 % ... 16 characters" — oddly specific but consistent with the AI-control literature. The single implausible item is the METR characterization in §6.1 (fix 6).

**Wrong or overstated as written:** the Morris autonomy-axis endpoint (fix 3); "the two published frameworks" (fix 13); "today's frontier chatbots" (fix 13); "every label on the market" and "regulation points the same way" (fix 14); "two independent measurements" (fix 16); "few remaining tasks defeat the newest models" (fix 6).

The paper's best sentence is §8's: "A label that had to exempt its own authors would be a declaration, which is the thing it replaces." Correct — and by the same token, a label whose abstract promises more than its mechanism delivers is also a declaration. Fix the promise, keep the mechanism.

### H. minimax/minimax-m3
# Review: *Guaranteed AI* v0.1 (6 September 2026)

## Verdict: **Publish after fixes.** Conditional on substantive rewrites to §5–§6 and §7. The label spec is interesting; the AGI-thermometer argument riding on top of it is not, and shipping the paper as written would associate a clean idea with an overclaim that the rest of the text cannot support.

The technical core — coverage-based attestation of machine-written spans via a signed write-log — is genuinely new and the §2/§3 framing is good. The reference scaffolding is mostly solid. The paper loses itself in the second half, where the author stops describing an instrument and starts measuring a hypothesis. I would not let §5–§6 out as written.

---

## 1. Factual claims and attributions

These I have a basis to assess, in rough order of how much they worry me.

**a. Article 50 EU AI Act, applicable 2 August 2026.** Plausible. The Act's general application is 2 August 2026; Article 50 sits in the transparency chapter. Worth confirming the exact sub-paragraphs cited in the ref list — currently bare.

**b. European AI Office Code of Practice on Transparency, 10 June 2026.** Plausible. The "digitally signed and time-stamped ... secure and tamper-evident manner" phrasing is consistent with what the AI Office and IPTC have been drafting. The IPTC-as-exclusive-reader claim for C2PA is *not* a quote I recognise from IPTC's published position; IPTC has been pushing C2PA but I have not seen them say "only". Flag as overstated if you cannot find a direct citation.

**c. Sundar Pichai, Q3 2024 earnings, "more than a quarter of all new code at Google is generated by AI".** Correct and verifiable at `blog.google/inside-google/message-ceo/alphabet-earnings-q3-2024`. The "reviewed and accepted by engineers" tail is part of the same remark. Fine.

**d. Satya Nadella, LlamaCon, 29 April 2025, "20% to 30% of code".** Correct. TechCrunch carried it; the Meta LlamaCon timing is right.

**e. Semafor, 24 April 2026, Pichai 75 % / "approved by engineers", "up from 50 % the previous autumn".** Plausible. Semafor has covered Pichai's code-share disclosures across 2024–26. I do not have a primary transcript, and the paper itself admits this. The "50 % the previous autumn" figure is one I have not seen elsewhere — Semafor's wording on the previous-call figure is the load-bearing number, and the paper should say so.

**f. Krishna Rao / *Invest Like the Best* / TechSpot, 14 May 2026, "90 %-plus".** Plausible. Anthropic's CFO has made similar statements. The "90%-plus" exact wording is one I cannot verify; the paper cites TechSpot as the secondary, which is honest.

**g. METR, "around every 7 months" doubling, 2019–2025, 320 min point estimate, 170–729 min interval, 29 January 2026 update.** Consistent with the METR Time Horizon 1.1 release and the underlying Kwa et al. paper (arXiv:2503.14499). The interval numbers are the kind of thing readers will want to see directly attributed.

**h. METR randomised trial, 10 July 2025: 19 % slower, 24 % forecast, 20 % perceived.** Correct, this is the Becker/Rush/Barnes/Rein study. Numbers match.

**i. Morris et al. "Levels of AGI" — "Emerging" as lowest rung, distinct autonomy axis with five levels.** Correct. arXiv:2311.02462.

**j. Feng, McDonald, Zhang (arXiv:2506.12469) "Levels of Autonomy for AI Agents", five levels from operator to observer.** Plausible; the paper exists in the autonomy-classification space. The verbatim "can be treated as a deliberate design decision, separate from its capability" quote should be checked against the arXiv text — this is the load-bearing quote in §5.

**k. ARC-AGI-3: "as long as there is a gap between AI and human learning, we do not have AGI".** Consistent with ARC Prize's framing. The exact wording in the paper reads like a paraphrase rather than a quote; either flag it as a paraphrase or find the verbatim.

**l. International AI Safety Report, "First Key Update", arXiv:2510.13653, October 2025.** Plausible; the report has been doing incremental updates under Bengio's chair. "Jagged" is the report's word.

**m. Hassabis 50 % within decade, "nowhere near"; LeCun LLMs "will never reach human-level intelligence".** Both are consistent with their well-known public positions. The paper wisely cites via Fortune as reported.

**n. Meinke et al. (arXiv:2412.04984) frontier models scheming in context.** Correct.

**o. Greenblatt et al. (arXiv:2312.06942) AI Control.** Correct.

**p. Redwood Research, 27 July 2026, "untrusted advice" protocol, "16 characters per message", "67 % of the capability gap".** Plausible; Redwood has been publishing in this space. The two specific numbers are unusual precision for a paper that cites other people's work in general terms. Either the paper has the primary, in which case the exact figures should be given a citation page, or this is a paraphrase dressed as a quote. Flag.

**q. Not By AI 90 % rule, "is not an AI detection tool" disclaimer.** Correct.

**r. Authors Guild "Human Authored" certification for books (2025); iHeartMedia "Guaranteed Human" (2025); Spotify "Verified" badge withholding; Berlinale "No AI Used" (2026).** These are all plausible, all in the same direction, and the paper wisely routes them through the Wikipedia "No-AI label" article rather than pretending to have done the journalism. The "Verified" attribution to Spotify — note that Spotify has multiple badge types and the policy on AI-music has shifted. Worth a one-line check that the wording is current to 6 September 2026 and not a stale description of a 2024 policy.

**s. NoHumanWrites study figures: 2,716 logged writes, 72,681 lines, median 96 % line attestation through the logged channel, 0 % for hand-written notes, 9 % for the agent's own source written via shell heredoc; detector AUC 0.91; 60 % of machine passages tell-free; precision ≈ 8 % at 5 % human share.** I have no independent way to verify, but the internal arithmetic is consistent: with 60 % tell-free machine passages at a 5 % human share, "no tell = human" gives precision 0.05·0.95 / (0.05·0.95 + 0.60·0.95) ≈ 7.7 %. The math checks out.

---

## 2. Logical gaps in §5–§6

The §5–§6 argument is that the attested share, aggregated across teams, is a "thermometer" for autonomy adoption that registers "the approach" toward AGI before benchmarks can. I think this fails in five places.

**Gap 1 — "approved" is not "autonomous".** The paper's load-bearing observation is that Pichai's 2024 and 2026 statements name the human's remaining role in the same words: approving, not typing. The paper reads this as evidence of *rising autonomy* and as the operating description of the top rungs of the Morris et al. and Feng et al. ladders. It is not. In the Feng et al. scheme, "operator" and "approver" are the *bottom* of the autonomy ladder, not the top. An "approver" is someone doing continuous oversight — the most constraining of the autonomy levels. The paper has the ladder upside-down. Quoting from §5 directly: "as systems climb the autonomy ladder, the human stops typing bytes and starts authorising tasks and reviewing results." Climbing a ladder means moving from operator toward observer; the operator is at the bottom. The paper treats "approver" as the top of an ascent, but the framework it cites places approver-status at the *low* end of autonomy, and places observer-status at the top. A team that approves every line is running at *low* autonomy, regardless of what wrote the bytes. The thermometer is calibrated backwards.

**Gap 2 — bytes are not autonomy.** Even if the byte-level classification were correct, what is on the file does not record how the team *chose* to deploy the system. The same byte distribution can be produced by (a) a team that grants full agency and rubber-stamps, (b) a team that grants limited agency with rigorous review, (c) a team that grants limited agency with cursory review. All three are different autonomy choices; all three leave the same attested share. The paper's own §6 step 3 says "autonomy is chosen in the field, and it leaves bytes" — that sentence is the entire leap, and it is asserted, not argued. The honest version of the instrument counts how much of a file came through a machine channel. It does not, and cannot, count the autonomy of the deployment. A 90 %-attested file from a human-babysitting agent is not the same observation as a 90 %-attested file from a fire-and-forget agent.

**Gap 3 — coverage is a confound, and the paper knows it.** §5 itself raises the obvious failure mode: "instrumenting a new channel is never mistaken for a rise in autonomy" — and then proposes the per-channel view as the cure. Per-channel separation helps when an *existing* channel stops being used; it does not help when a team introduces a *new* machine channel that catches bytes that previously fell on the floor. The moment Cursor adds a new background-edit path that gets routed to the hook, the attested share jumps and the registry reads it as a leap in autonomy. The paper does not address this.

**Gap 4 — the falsification test is asymmetric.** §5 says the test is "if the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong." Two problems. (i) Constant coverage is hard to hold — see Gap 3. (ii) The reverse is not symmetric: a rising share at constant coverage would be evidence consistent with *several* hypotheses, including "the team adopted a tool with better logging", "the team shifted to a workflow that uses the agent more", "the team grew and new hires are less willing to edit by hand", or "reviewers stopped reading the diffs and started rubber-stamping". None of those is "autonomy is rising in the framework sense". The test could pass while the central claim is still false.

**Gap 5 — the AGI step is unfalsifiable inside the paper.** §6 step 5: "When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders." This is the only place the paper actually says what the registry would conclude, and it is a definition disguised as a measurement. The paper is defining "the top rungs" as "authorisation and review" and then observing that this state is reached when the attested share is high. It is not, in any sense, a measurement of the approach to AGI. The Morris et al. paper's "Superhuman" level is defined by capability, not by who typed the bytes. The paper's argument reduces to: when the machine writes everything and the human signs off, we have reached the top of the autonomy ladder. By that definition, every procurement clerk in a bureaucracy is at the top of the autonomy ladder. The instrument measures a property of the file, then the paper renames the property as autonomy, then renames the autonomy as AGI-progress. This is a triple identification, each of which the paper owes a defence for and provides none.

The §6 weakness admission in the safety paragraph is good and probably the best-written part of the back half. It does not save the preceding chain.

---

## 3. Gaming vectors §7 misses

§7 is the most uneven section. It addresses a handful of attacks and then makes a rhetorical pivot to "the mark is not anti-human" which reads as if the author lost interest in attack-shipping. Several real vectors are not addressed:

**a. Routing through the hook is a feature, not a bug — the paper knows this but doesn't price it.** §7's first bullet ("Routing hand text through the hook") notes that a prompt of "write exactly these lines" yields an attested hunk, and shrugs. This is the most important attack in the document and the treatment is one sentence. A label that certifies "this was written by a machine" while the operator pre-specifies the output in natural language certifies nothing useful. The paper should commit to a defence: either the key-holder attestation includes a "I did not supply the output as text in the prompt" claim, or the label concedes it cannot tell.

**b. Heredoc games, by the paper's own evidence.** §2 reports that the agent's own project source, written through shell heredocs, attests at 9 %. The paper treats this as a *feature* — the method reporting an unlogged channel. But the symmetric reading is that a developer who wants the label *low* simply does what the author of NoHumanWrites did, and writes prose through a channel the hook does not see. If a 9 % reading is reachable by the most well-intentioned developer in the study, it is also reachable by anyone who wants to game the number down. The paper's own example demonstrates this. §7 does not address it.

**c. The rubber-stamp reviewer.** The "approved by engineers" framing that the paper leans on in §4 is also the most natural attack on the label's meaning. A reviewer who approves without reading produces a 100 %-attested file with no human judgement in the loop, exactly as the abstract promises — and exactly the case where a label that names the human role would be most useful. The label currently counts the human out of the picture entirely once their share drops below 10 %. The paper needs a defence, not a shrug.

**d. Replay / fork / re-sign.** A developer can sign a file once, copy the bytes, edit, re-sign, and pick which record to publish. The paper says Level 2 (anchored log) defends against the *deletion* of records but not against publishing a subset. Sigstore Rekor in append-only mode does not prevent selective disclosure of one record from a sequence. §7's "stale number" bullet gestures at this but does not name it.

**e. Composed work.** A junior writes the architecture, the agent writes the boilerplate, the senior edits the agent's output. The file is 80 % machine. The label says "Guaranteed AI" but the most consequential 20 % of bytes are human, including any that contain a security boundary. The label has no notion of "where in the file" the human contribution sat, only "how much". A registry of attested shares is a measurement of bulk, not of leverage.

**f. The 100 % "Pure AI" trap.** §3 sets Pure AI at 100 % attested. A team that wants the maximum-status seal has a strong incentive to route every last hand edit through the agent. Pure AI is then reachable trivially and means nothing. The paper should either drop the seal or define it as a stricter condition (e.g., no human prompt content beyond a fixed schema).

**g. The trusted-executor circularity.** §6 names Level 2 as requiring "a trusted executor outside the writer's reach". Who trusts the executor? Who certifies the executor's key? In a world where §6 also says models may be adversaries, the executor needs the same provenance guarantees as the writer. The paper does not address this.

**h. Adversarial review of the harness itself.** If the agent's harness logs incorrectly (because the model is asked to, or because of a bug, or because of supply-chain compromise on a dependency that emits the log), the signature is real and the content is wrong. §6's safety paragraph flags this in the abstract; §7 does not.

**i. The repo-level aggregation game.** §7 says the report "aggregates per repository, not per person." A team can ship its "Pure AI" work in a dedicated repo, and ship all human work in another. The label is true on the dedicated repo, and the dedicated repo's contents get cited as evidence the team's output is "Guaranteed AI". This is a labelling-environment attack and is not in §7.

**j. The metric is a leaderboard.** Once the registry publishes quarterly counts, the field's incentive is to maximise the attested share, which is to minimise the human channel. This is the opposite of what a responsible deployment story wants. The paper does not address the Goodhart problem.

---

## 4. Overclaiming in wording

Sentences to soften or strike, most damaging first:

- **§6 step 5**: "When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders." This is the most overclaiming sentence in the paper. It is a definition being passed off as a measurement. Strike or rephrase as: "this would be a state the published ladders have not, to my knowledge, separately operationalised."

- **§5**: "as systems climb the autonomy ladder, the human stops typing bytes and starts authorising tasks and reviewing results." The paper has the ladder upside-down here, as noted. Either rephrase or fix the framework mapping.

- **Abstract**: "The two published frameworks for grading progress toward general intelligence both treat autonomy as a deployment choice; a team's attested share, held at constant instrumentation, is the number that records that choice as it is made." The second clause is the overclaim. The first is fine. The attested share records how many bytes came through a logged machine channel; it does not, even at constant instrumentation, record the autonomy choice.

- **Abstract**: "The machine share of new code at the largest labs rose ... from a quarter to three quarters between October 2024 and April 2026." "Largest labs" is plural but the only cited lab is Google. Either say "one of the largest labs" or list the others you mean.

- **§4**: "the perception gap is the part that matters here. Developers could not tell, from the inside, whether the machine had helped." This is doing a lot of work and is the wrong half of the METR finding. The METR result is that developers *believed* they had got a 20 % speed-up while actually taking 19 % longer. That is not "could not tell whether the machine had helped" — it is "systematically mis-attributed a slowdown to a speed-up." The paper should engage with the *direction* of the bias, not just the existence of a perception gap.

- **§6 step 2**: "Adoption rises on a reported curve. A quarter, then a half, then three quarters of new code at one of the largest software organisations on earth, in eighteen months." You do not have a half figure for Google on the record in the table; you have 25 % (Oct 2024) and 75 % (Apr 2026). The "50 % the previous autumn" intermediate is in the Semafor piece as Pichai's self-report, not as an audited figure. Soften the cadence.

- **§6 step 1**: "METR's doubling time of roughly seven months ... has held from 2019 to 2025 ... and the authors note that few remaining tasks defeat the newest models." The "few remaining tasks" remark, if quoted, should be quoted with the qualifier METR attached. If it is a paraphrase, mark it as one. As written it reads as a direct quote.

- **§6 weakness paragraph**: "A mark that could not survive the arrival of the thing it measures would not be worth designing." This is rhetoric, not a claim. It is also contradicted four sentences later by the admission that Level 1 does *not* survive the arrival of adversarial models. Either soften or note the resolution: Level 2 is the survival mechanism.

- **§3**: "**Guaranteed AI** at 90 % or more with every unattested unit listed." The "Guaranteed" branding is itself an overclaim given §7's key-holder-lying bullet. "Guaranteed" implies a guarantee that the system does not in fact provide against the most obvious failure mode. Either rename (e.g., "Attested AI") or scope the word to the signature only.

- **§3**: "**Pure AI** at 100 % attested." As noted, "Pure" is a value claim. A file with a 100 %-attested provenance and a 10,000-token prompt that specifies the output is not "pure" anything.

- **§1**: "Nobody has shipped the mark that points the other way." This is a strong claim. C2PA Content Credentials with a generative-AI assertion, certain watermarking standards in development, and the IPTC's own draft text profile are all in this space. The paper should say "no widely deployed mark" rather than "nobody has shipped".

- **§8**: "the ledger records only what came through the harness's write tool." The paper would do well to remind the reader that the same property that lets the method report an unlogged channel as a 9 % reading also lets a developer produce a 9 % reading on purpose. The §8 disclosure is honest and good; it deserves a line in §7.

---

## 5. Other concerns

- **Author conflict.** The author of the white paper is the same person (A. Chrétien, Plus de Fun Agency) as the author of the underlying NoHumanWrites study. The paper should make this explicit in a note. It is not disqualifying, but a reader should not have to chase the DOI to find it.
- **The label spec is in `label/README.md`, which the white paper does not include.** The §3 description is a summary, but for a paper whose entire argument is "here is what the label guarantees", shipping the spec inline or as an appendix would be cleaner.
- **Wikipedia is doing real work in §1 and §2.** The paper is honest about it ("secondary source; used for the list of marks"). But the four claims it routes through Wikipedia (Authors Guild, iHeartMedia, Spotify, Berlinale) are exactly the claims that give the paper its "trend" colour. If any of them is wrong, the trend is weaker than presented. Worth a one-line check, especially the Spotify wording given the 2024→2025→2026 policy churn.
- **Reference 12 cites an arXiv ID and a 29 January 2026 update with an archived link.** Good practice. The other 2026 sources are mostly direct, with one explicit "primary transcript not located" disclosure for Semafor. Keep the disclosure; readers will trust the rest more for it.
- **§5 quote from Feng et al.** The phrase "can be treated as a deliberate design decision, separate from its capability" is the load-bearing quote for the entire AGI-thermometer argument. If it is a paraphrase, the paper should say so. If it is a quote, the paper should give a page or section reference.

---

## 6. Numbered fixes, most important first

1. **Rewrite §6 step 5 and the corresponding sentence in §5.** The current text claims that high attested shares describe the top of the autonomy ladder and register "the approach" to AGI. This is the paper's central overclaim. Replace with a narrower, defensible claim: the label is a coverage measurement of the byte channel; a registry of such measurements is a record of tooling adoption, not of autonomy, capability, or AGI progress. If the AGI-thermometer idea is to be kept, it must be argued on its own terms, with the framework-mapping corrected (operator at the bottom, observer at the top, the paper currently conflates them) and the Goodhart risk addressed.

2. **Address the §7 gaming vectors that are missing.** Specifically: (a) prompt-supplied output, (b) heredoc games (your own 9 % example), (c) rubber-stamp review, (d) replay / fork / re-sign / selective disclosure under a Rekor anchor, (e) composed work where the human's bytes are the high-leverage ones, (f) the 100 % "Pure AI" being trivially reachable, (g) trusted-executor circularity, (h) harness-level compromise, (i) repo-level cherry-picking, (j) the leaderboard / Goodhart dynamic. At least four of these need treatment in §7, not a one-line aside.

3. **Rename or scope "Guaranteed" and "Pure".** The labels' brand names do work the underlying guarantees do not. "Guaranteed" implies a defence against key-holder compromise that Level 1 explicitly does not provide. "Pure" implies a value claim about the writing that 100 % byte-coverage does not justify. Either rename (e.g., "Attested AI", "Fully-Attested AI") or add a one-sentence limitation on the label face that scopes the words to signature presence.

4. **Correct the autonomy-ladder mapping.** §5 currently treats "the human approves rather than types" as evidence of climbing the autonomy ladder. In both Morris et al. and Feng et al., the approving role is at the low end of autonomy. The paper needs to decide what it is claiming: that high byte-share = low autonomy (which is the framework-consistent reading), or that high byte-share = high autonomy (which is what the text says but is framework-inconsistent). The current text asserts both. Pick one and rewrite.

5. **Make the byte-to-autonomy mapping explicit or retract it.** The current §6 step 3 is the load-bearing step, and it is the one with no argument. Either (i) demonstrate that byte-share correlates with autonomy in a measured case (and give the case), or (ii) soften the claim to "byte-share is one signal among several, and any autonomy conclusion requires complementary evidence." Option (ii) is honest and probably what the paper should do.

6. **Engage the METR productivity study honestly.** §4 raises the result and then pivots to "the perception gap is the part that matters". The actual finding is that developers were *systematically* over-optimistic about the tool's effect. The paper's argument that the instrument must "count bytes rather than ask people" is consistent with the finding, but the paper should not let the reader infer that the instrument tells us the bytes are *helpful*. The METR result cuts against the "rising share = progress" reading and the paper should say so.

7. **Define "the largest labs" or restrict the claim.** "The largest labs" is plural in the abstract and singular in the table. Either find at least one more audited or self-reported figure for a non-Google lab, or restrict the claim to Google and weaken the rhetoric accordingly.

8. **Flag the IPTC "only" reading in §1.** I cannot verify that IPTC has described C2PA as the *only* technology meeting the Code of Practice requirement. If you have the URL and the verbatim sentence, keep it. If not, soften to "the only technology the IPTC currently endorses" or similar.

9. **Quote the Feng et al. and ARC-AGI-3 phrases as quotes or paraphrases.** Both sentences in §5 are doing real work; both should be marked as direct quotation with citation, or rewritten as paraphrase.

10. **Tighten the reference for the Redwood 16-character / 67 % claim.** Either give a specific page/section reference or restate as paraphrase. The other safety citations are clean; this one is loose by comparison.

11. **Add a note on author conflict.** A. Chrétien writes both the underlying study and this paper. State it in a footnote or in the author block.

12. **Add an explicit Goodhart paragraph in §5 or §9.** A registry that publishes attested shares by team is a leaderboard. The §5 "thermometer" idea is only useful if the registry does not distort the field. The paper should say how — e.g., per-channel publication, no per-team publication, or a delayed rolling aggregate. As written the design leaks.

13. **Quote the Spotify, Authors Guild, iHeartMedia, Berlinale claims with primary sources.** Wikipedia is fine for the list, but the paper uses these to set up a "trend" in §1 and the trend is weaker if any one of them is misattributed. One click per claim.

14. **Add a short paragraph on what the label *cannot* do under the very framework the paper endorses.** If the Morris et al. "Superhuman" level is capability-defined, then the autonomy axis cannot, on its own, declare approach to that level. The paper implicitly promises this and the framework explicitly disclaims it. The discrepancy should be in the paper, not left for the reader to find.

15. **Soften the §3 "two published frameworks" claim to "two recent published frameworks"**, since at least Morris et al. is now three years old and the paper is making a present-tense argument.

---

*Sources I cannot independently verify and the paper itself does not pretend to be more than secondary about:* the precise wording of the Semafor 24 April 2026 piece, the TechSpot 14 May 2026 piece, the Spotify Verified badge current wording, the Authors Guild and iHeartMedia 2025 launches, the Berlinale 2026 marketing, the exact Redwood 16-char / 67 % numbers, and the verbatim "as long as there is a gap between AI and human learning" ARC-AGI-3 quote. The paper flags several of these honestly. The rest should be cleaned up to the same standard.

## Round 2 — cross-check (each critiques the anonymised pool)

### openai/gpt-6-astra-pro reviews
## Strongest answer: A

**A is the strongest by a substantial margin. C is the next-best foundation.** A distinguishes factual errors, unsupported inferences, and sources it cannot verify; addresses nearly every reference; and identifies the central security mistake: **a transparency log preserves commitments, not their truth or completeness**.

Its publication verdict is proportionate: **do not publish the current manuscript; a substantially narrower provenance paper could be publishable.** The difference from C’s “publish after fixes” is largely editorial—the required changes replace the central thesis, rather than merely qualify it.

None of the answers establishes that the implementation is sound. The repository, ledger, and specification were not supplied for inspection. Several answers nevertheless endorse them as though they had been reviewed.

## 1. Assessment of each answer

### A — strongest, with a few qualifications

A gets the most important distinctions right:

- Channel attestation is not intellectual authorship.
- Authenticated statements are not necessarily truthful observations.
- Output share is not decision authority, productivity, or general capability.
- Anchoring and externally observed execution are different assurance mechanisms.
- A public key alone is insufficient to reproduce a coverage result.
- A registry containing only qualifying labels is threshold-selected, not merely opt-in.

Its concrete counterexamples and treatment of the proposed falsification test are particularly effective. The ceiling case—autonomy increasing when coverage is already 100%—directly defeats the paper’s universal prediction.

**Remaining limitations:**

- It does not catch the bibliographic title correction identified by D: the METR paper is *Measuring AI Ability to Complete Long Tasks*, not *Long Software Tasks*.
- Its Morris discussion would be stronger if it supplied the actual autonomy categories, rather than only explaining the numbering.
- “Anthropic’s Economic Index … not an independent audit” is correct, but *independence* needs disambiguation. Separate telemetry can provide evidence distinct from an executive statement without being institutionally independent or measuring the same quantity.
- Its proposed signed fields are design recommendations, not an established minimally sufficient security protocol.
- It could incorporate C’s governance, rights, and compliance concerns more explicitly.

These are improvements, not defects in its central reasoning.

### C — comprehensive, but repetitive and occasionally self-contradictory

C covers governance, commercial conflicts, Goodhart incentives, copyright confusion, and compliance misinterpretation better than A. It also correctly distinguishes false signing from retrospective tampering.

But some proposed replacement wording retains the problem it criticizes:

> “Proves only that listed units were recorded through a named machine channel.”

For self-signed Level 1, the signature proves that a key signed a statement—not that the channel event occurred.

Similarly:

> “AI-written bytes, attested”

still implies AI authorship that the mechanism cannot establish.

Other weaknesses:

- “Guaranteed” need not universally imply a legal remedy. The defensible criticism is that the name invites warranty or independent-certification interpretations.
- Replacing IPTC’s purported “only” claim with “IPTC states that C2PA is one technology…” risks inventing a different attribution. Verify the original or write an unattributed technical assessment.
- Hardware attestation, multiparty signatures, and trusted execution are not interchangeable remedies. Each needs an explicit threat model.
- Its repeated “post-2026” descriptions are inaccurate: the issue concerns sources dated in 2026, not after 2026.
- The second half repeats much of the first without adding equivalent evidentiary value.

### D — useful technical critique, weakened by unsupported corrections

D identifies the numerical cadence error, denominator mismatch, stale “today’s” attribution, and METR title error.

However:

> “iHeart’s ‘Guaranteed Human’ was announced November 2024, not 2025”

is an unsupported date correction in this answer. It needs an operator announcement or contemporary source; it should not be confidently substituted for the manuscript’s date from memory.

More importantly:

> “completeness is unenforced until anchoring exists”

is wrong. **Anchoring does not establish completeness**, including after integration.

D also says:

> “the 8 % precision arithmetic checks out … and it’s correctly an upper bound”

The calculation is an upper bound under an assumption about human passages lacking tells, but the manuscript does not actually state that upper-bound qualification.

Other problems:

- A fingerprint versus a personal name is not a literal contradiction. The real issues are linkability and lack of authenticated accountability.
- A hosted verifier is useful, not necessary; offline verification can be sound.
- “The falsification test can’t falsify” is too categorical. A flat result could falsify the stated universal prediction under its conditions; it would not identify why it failed or establish anything about AGI.
- Declaring the engineering “sound” exceeds the available evidence.

### G — strong coverage, but a major attribution error

G’s most serious mistake is:

> “the top of Morris et al.’s autonomy axis is *Organization* … Tool→Consultant→Agent→Innovator→Organization”

This conflates Morris’s framework with another classification, resembling the reported OpenAI scale. Morris’s autonomy table runs from **No AI** through **Tool, Consultant, Collaborator, Expert, and Agent**. A review centered on attribution accuracy cannot introduce this error.

Its proposed safe conclusion is also unsafe:

> “attested share is a lower bound on machine-written share”

Not on machine-*authored* share: human dictation, formatter rewrites, and false self-signing defeat that interpretation.

Additional issues:

- A 320-minute 50%-success horizon does not establish how many longer tasks exist in the benchmark or how many tasks the model fails overall. It cannot, by itself, disprove “few remaining tasks.”
- An expiry date does not solve artifact substitution or stale-content binding.
- “Unverifiable (post-training)” confuses limits of remembered knowledge with source verifiability.
- Its Digital Omnibus warning requires a precise, verified source and must distinguish a proposal from enacted changes.
- Calling the Article 50 summary “verified accurate” overlooks material exceptions.

### F — forceful, but introduces scientific and technical errors

F correctly rejects the AGI inference and identifies scope manipulation and rewrite laundering. Its rhetoric often substitutes for precision, however.

> “A one-sided test … is not falsifiability.”

False. One-sided predictions can be falsifiable. The problem is construct validity, confounding, and the mismatch between a local adoption outcome and an external capability trend.

> “100% attested lines with a human writing the issue and the prompt is still a tool.”

Also false as a universal statement. Highly autonomous systems can receive human-defined objectives. Autonomy depends on delegated authority and subsequent intervention, not whether a human initially supplies a task.

F further:

- Conflates ARC’s learning criterion with Morris/Feng autonomy levels.
- Uses the productivity RCT to suggest rubber-stamping of model output, which that study did not establish.
- Claims the badge can satisfy regulatory requirements without a compliance analysis.
- Does not give the false-anchored-statement problem the explicit treatment it needs.
- Treats press reporting as categorically inadmissible rather than evidence requiring attribution and calibrated weight.

### B — too incomplete and speculative

B’s opening claim is indefensible:

> “Your citations of the 2023–2025 literature … are accurate and well-contextualized.”

Several are misapplied, and B does not substantiate that blanket clearance.

Its rejection of Anthropic’s reported 90% figure rests on speculation about what frontier-lab engineering could plausibly automate. The proposed correction—

> “likely reflect raw line counts—heavily skewed by boilerplate…”

—adds an unsupported factual explanation. The right fix is to obtain the denominator and measurement method, not invent them.

B also misses the central Level 2 error, regulatory qualifications, registry selection, and several factual checks. Calling an unseen spec “excellent” is unwarranted.

### E — useful core, disqualifying factual suspicion

E says:

> “LlamaCon is Meta’s conference; Satya Nadella is Microsoft’s CEO.”

This is not evidence against the attribution. Nadella did appear at LlamaCon in April 2025; the reported 20–30% remarks are associated with that appearance. Requiring the authors to “correct” this attribution would introduce an error.

E also overstates anchoring:

> “Anchoring … prevents silent deletion/rollback”

Only particular alterations to previously committed histories become detectable under a specified verification protocol. Omission, alternative histories, selective presentation, and evidence availability still matter.

Its factual audit is otherwise much narrower than the task requires.

### H — numerous substantive errors

H is the least reliable on framework interpretation and internal consistency.

- It calls the proposal “genuinely new” without establishing novelty.
- It treats 2026 findings as “consistent with” specific releases without clearly separating recognition from verification.
- Its precision calculation silently adds an unexplained 95% factor for human tell-free passages. The approximately 8.1% calculation requires an explicit assumption; its displayed 7.7% calculation uses a different one.
- It calls Feng’s **Approver** role the bottom of the ladder; Approver is Level 4, below Observer at Level 5.
- It concludes:

  > “high byte-share = low autonomy … is the framework-consistent reading”

  Neither high nor low autonomy follows from byte share.
- Its composed-work example says an 80%-machine file receives “Guaranteed AI,” contradicting the specified 90% threshold.
- It says the label provides no information about *where* human contributions occur, overlooking the proposed unattested-unit list. Semantic importance is unmeasured, but location is not necessarily absent.
- It treats prompt restrictions or an additional publisher declaration as potential authorship defenses without explaining how they would be enforced.
- It says the table contains only Google, despite Microsoft and Anthropic rows. The actual problem is that the longitudinal quarter-to-three-quarters trajectory belongs only to Google.

## 2. Disagreements that a final review must resolve

1. **Is the engineering already validated?**  
   No. A proposal can be coherent without its implementation, completeness, or false-attestation rate having been established.

2. **Does high coverage imply any particular autonomy level?**  
   No. B/F/H sometimes replace “high coverage means high autonomy” with the equally unjustified “human approval means low autonomy.”

3. **Is the falsification test literally unfalsifiable?**  
   Not necessarily. Its stronger defect is that it does not validate the proposed construct or identify the claimed causal relationship.

4. **Do signatures establish channel passage?**  
   Only under additional trusted-observation assumptions. Level 1 establishes a key’s signed claim.

5. **Are secondary or 2026 sources unacceptable?**  
   No. They require calibrated attribution and verification—not rejection by date, outlet category, numerical specificity, or perceived technological implausibility.

## 3. What a correct final answer must include

A defensible final review should use A’s structure, with C’s governance and misuse additions, and include these prioritized fixes:

1. **Verdict: do not publish the current version.** Explain that publication requires replacing the authorship and AGI claims, not merely adding disclaimers.
2. Quote **“certifies that a machine wrote the work”** and contrast it with **“The key proves the channel, not the author.”** State that even channel passage is only asserted at Level 1.
3. Quote and reject **“the label registers the approach before any benchmark declares it.”** Give high-coverage/low-autonomy, low-output/high-autonomy, and ceiling counterexamples.
4. Separate **signature authenticity, history commitment, completeness, trusted execution observation, and intellectual origin**. Explain exactly what Rekor cannot establish.
5. Require artifact/version binding, deterministic units and exclusions, lineage rules, key lifecycle, and reproducible verification evidence.
6. Correct factual errors with primary support; flag uncertain claims without manufacturing replacements. Include the correct Morris framework, Nadella attribution, METR title and horizon interpretation, Article 50 qualifications, and scoped C2PA analysis.
7. Explain the 25%-to-75% calculation: approximately **11.4-month doubling**, not seven—and why comparing those growth rates is conceptually inappropriate anyway.
8. State the detector calculation’s assumptions and distinguish one rule’s precision from all detectors’ error rates.
9. Address laundering, non-AI automation, padding, selective scope, replay, omitted records, compromised signers, re-identification, registry spam, and incentives to avoid necessary human edits.
10. Require prominent disclaimers concerning authorship, review, safety, quality, originality, rights, and regulatory compliance; explain registry sampling and governance.
11. Publish the actual self-check receipt rather than treating **“the ledger is right”** as an acceptance test.

The essential conclusion is narrower than most answers’ proposed replacement branding: **this may become a reproducible report of accepted provenance evidence for a specified artifact under an explicit trust model. It is not presently a certification of AI authorship, autonomy, or progress toward AGI.**

### google/gemini-3.1-pro-preview reviews
An evaluation of the answers reveals a sharp divide in how well the reviewers caught the white paper’s mathematical errors, logical sleights of hand, and factual hallucinations. 

Here is a breakdown of the errors, unstated assumptions, risks, and disagreements, followed by an assessment of the strongest answer and the requirements for a definitive response.

### 1. Errors, Logical Gaps, and Unstated Assumptions in the White Paper
A thorough review of the white paper reveals several fatal flaws that a hostile reviewer must catch:
*   **The Math Error:** The paper claims that Google’s AI code share moving from 25% to 75% in 18 months is "roughly the doubling cadence METR measures" (7 months). This is arithmetically false. 25% to 75% is a 3× increase (approx. 1.58 doublings). 18 months / 1.58 = an ~11.4-month doubling time. 
*   **The "Same Words" Lie:** The paper claims Pichai used the "same words" in 2024 and 2026. He did not. "Reviewed and accepted" (2024) and "approved" (2026) are different words. 
*   **The Autonomy Ladder Inversion (Category Error):** The paper claims that when the machine writes 100% of the code and the human merely authorises it, the human has reached the "top rungs" of the Morris and Feng autonomy ladders. This is backwards. In those frameworks, human approval/oversight is at the *bottom* (Operator/Approver). The top rung is fully autonomous (Observer/Organization). The ledger measures *inscription* (who typed), not *autonomy* (who decided).
*   **The LlamaCon Hallucination:** The paper cites Satya Nadella (Microsoft's CEO) speaking at "LlamaCon" (Meta's ecosystem) in April 2025. This is a glaring anomaly that should trigger immediate suspicion.
*   **Regulatory & Standards Errors:** The paper claims all regulation points to human-authored content, but Article 50 of the EU AI Act explicitly requires marking *AI-generated* content. Furthermore, the claim that C2PA has no profile for text/source ignores C2PA's ability to bind to generic assets via external manifests.
*   **The Falsification Test is Invalid:** The paper claims a flat share alongside rising capability would falsify the thesis. But because autonomy is a *deployment choice*, a flat share simply means teams chose not to deploy it. Furthermore, the test is one-sided: the share could rise due to non-AI automation, boilerplate, or better logging, falsely confirming the thesis.

### 2. Risks and Gaming Vectors Missed by §7
*   **Human Laundering:** A human writes the code, pastes it into the AI prompt, and says "output exactly this." The ledger records 100% "Guaranteed AI," laundering human IP into machine provenance.
*   **Unlogged AI Attests as Human:** If a developer copy-pastes from ChatGPT or uses an unlogged shell, the ledger marks it as "unattested." The market will inevitably read "unattested" as "human," meaning the label exports a false guarantee of human authorship.
*   **Non-AI Automation:** Deterministic scripts, formatters (like `Prettier`), and codegen piped through the logged channel will attest as "AI."

### 3. Disagreements Between the Answers
*   **The LlamaCon Hallucination:** **Answer E** brilliantly catches this ("LlamaCon is Meta’s conference; Satya Nadella is Microsoft’s CEO"). Shockingly, **Answers A, G, and H** actively hallucinate to validate this fake event, calling it "consistent with the known record" or "TechCrunch carried it; the Meta LlamaCon timing is right." Reviewers must not validate fake future/alternate-timeline events.
*   **The Math Error:** Answers **A, D, F, and G** correctly do the math and catch the 11-month vs 7-month discrepancy. The others miss it entirely.
*   **The Autonomy Ladder Inversion:** Answers **D, F, G, and H** correctly point out that human approval is the bottom of the autonomy ladder, not the top.
*   **Verdicts:** Verdicts range from "Do not publish" to "Publish after fixes." Given the prompt's instruction to be a hostile reviewer and the fact that the paper's core thesis (§5–§6) rests on a fundamental category error, "Do not publish (in current form)" or "Publish after major structural fixes" are the only justifiable verdicts.

### 4. Strongest Answer
**Answer D is the strongest.** It is a masterclass in hostile, forensic reviewing. 
*   It catches the "same words" lie.
*   It catches the math error.
*   It perfectly dismantles the category error (typing vs. decision authority).
*   It destroys the falsification test ("The falsifier doesn't falsify... A one-sided test that can only fail in the direction you do not expect is not falsifiability").
*   It catches the denominator mix in the table (stock vs. flow).
*   It correctly notes that the METR RCT measured *productivity* perception, not *provenance* perception.
*   It provides a ruthless, perfectly formatted numbered list of 15 fixes with exact quotes.

*Honorable Mention:* **Answer F** is nearly as strong and shares many of D's excellent catches, delivered with fantastic hostility ("This is a README for a self-signed line-count badge with an AGI press release stapled on"). **Answer E** deserves credit for being the only one to catch the Nadella/LlamaCon anomaly, but it misses the math and "same words" errors.

### 5. What a Correct/Safe Final Answer Must Include
A definitive response to this prompt must contain:
1.  **A strict verdict:** Do not publish, or Publish only after the complete removal/rewrite of §5–§6.
2.  **Factual takedowns:** Explicitly flag the math error (11.4 months vs 7 months), the "same words" lie, the EU AI Act contradiction, and the Nadella/LlamaCon anomaly.
3.  **Logical takedowns:** Dismantle the category error. Explain that the ledger measures *inscription* (who typed), while the Morris/Feng ladders measure *autonomy* (who decided). Point out that human review is the bottom of those ladders, not the top.
4.  **Gaming takedowns:** Highlight that unlogged AI will be falsely read as human, and human text routed through the AI will be falsely certified as "Guaranteed AI."
5.  **Formatting:** A numbered list of concrete fixes, ordered by importance, containing specific quotes of the offending sentences, delivered in a cold, hostile tone with zero flattery.

### qwen/qwen3.8-max-0902 reviews
## Strongest answer

**Answer C is the strongest overall.** It is the most complete and least self-indulgent of the set. It gives a usable verdict, makes the publication decision conditional on the right structural fixes, treats 2026 sources as not automatically invalid but not automatically trustworthy, and converts the paper’s failures into concrete edits. It covers all four requested checks: factual claims, the §5–§6 autonomy/AGI argument, gaming, and overclaiming.

Why C beats the others:

1. **Correct publication posture.**  
   C says: publish after major fixes, but if the authors will not cut or substantiate §5–§6, do not publish. That is the safest editorial position. The engineering provenance idea is salvageable; the AGI-thermometer thesis is not publishable as written.

2. **It does not over-verify post-training sources.**  
   Unlike G and H, C does not pretend to have verified 2025/2026 events. It demands primary sources or downgraded claims.

3. **It identifies the central category error.**  
   The ledger proves machine-channel transit, not machine authorship, autonomy, or progress toward AGI.

4. **It supplies concrete fixes, not just criticism.**  
   It requires renaming the label, defining units, adding a threat model, correcting regulatory claims, publishing verification artifacts, and adding legal/governance disclaimers.

5. **It quotes the paper’s offending sentences.**  
   The task explicitly requires specificity and quotation. C does this consistently.

C is not perfect. It should have more explicitly flagged the Nadella/LlamaCon attribution, the Anthropic “90%-plus” claim, and the METR “few remaining tasks” sentence as requiring primary verification or plausibility caveats. It should also have computed the mismatch between 25% to 75% over 18 months and METR’s seven-month doubling claim. But these are omissions rather than serious errors.

**Answer A is the best technical security review** and in some places is sharper than C, especially on transparency logs, verification inputs, and the difference between anchored claims and trusted execution. But A’s verdict is too categorical and it occasionally says things are “consistent with the known record” without showing primary verification.

**Answer D is the best concise factual correction**, especially on the false METR doubling analogy and the mixed denominators in the code-share table. But D makes several unverified factual assertions, such as the iHeart date and the Kwa et al. title, and overstates that certain citations are “correctly characterized.”

**Answers G and H contain excellent insights but overclaim verification.** G correctly notes that the ledger does not measure task length, that model identity is self-reported, and that the badge does not travel. H correctly attacks the autonomy-ladder mapping. But both treat post-training events as “correct” or “verified” too readily.

---

## Independent errors, assumptions, risks, and disagreements among the answers

### 1. Verdict disagreement

The answers split between:

- **Do not publish:** A, E, F.
- **Publish after fixes:** B, C, D, G, H.

The safest verdict is **publish after fixes**, but only if the fixes are structural. If the authors insist on retaining the claim that attested share measures rising autonomy toward AGI, the correct verdict becomes **do not publish**.

The paper’s core mechanism is potentially useful:

> “a signed ledger produced at write time”

But the paper’s central advertised conclusion is unsupported:

> “a team's attested share, held at constant instrumentation, is the number that records that choice as it is made.”

That sentence should not survive without independent validation.

---

### 2. Source-verification disagreement

The task says 2026 sources should not be rejected merely because they are post-training, but implausible quotes should be flagged.

The best answers on this point are **A, C, and F**, because they generally say: these sources are unverified, reported, or need primary confirmation.

The weaker answers overclaim verification.

#### B overclaims

B says:

> “Your citations of the 2023–2025 literature (METR, Sadasivan, Morris, EU AI Act) are accurate and well-contextualized.”

That is too broad. Some of those items depend on 2025/2026 updates or reported events that cannot be treated as verified without primary sources.

B also says:

> “Even projecting to mid-2026, this is highly implausible for a frontier AI lab.”

That may be a reasonable suspicion, but it is speculative unless tied to denominator, scope, and definition. The safer move is to flag the Anthropic claim as needing primary transcript and scope, not to declare it false.

#### D makes unverified factual assertions

D says:

> “iHeart's 'Guaranteed Human' was announced November 2024, not 2025 — minor.”

That may be true, but it is stated without support.

D also says:

> “Ref 12: the Kwa et al. title is 'Measuring AI Ability to Complete Long Tasks,' not '…Long Software Tasks.'”

Again, this may be correct, but it is asserted as fact. In a review about attribution precision, this needs a citation.

D also says:

> “Sadasivan, Greenblatt, Meinke, Morris, Feng citations are real and correctly characterized.”

The Feng citation is 2025. “Correctly characterized” is too strong without checking the exact framework.

#### G overclaims verification

G says:

> “Verified accurate: … Authors Guild 2025.”

That is not safe unless the reviewer has primary access. G also says:

> “the Pichai 29 Oct 2024 quote and the Nadella LlamaCon quote match my knowledge”

The Nadella/LlamaCon item is exactly the kind of event attribution that should be checked against a primary recording or transcript.

G also says:

> “The single implausible item is the METR characterization in §6.1.”

That understates the verification problem. The Anthropic “90%-plus” claim, the Redwood “67% / 16 characters” claim, and the Semafor “50% the previous autumn” claim also need primary confirmation.

#### H is too relaxed about secondary sources

H says:

> “Satya Nadella, LlamaCon, 29 April 2025, '20% to 30% of code'. Correct.”

That is overconfident.

H also says:

> “the paper wisely routes them through the Wikipedia 'No-AI label' article rather than pretending to have done the journalism.”

That is wrong as a source-hygiene matter. Wikipedia is not an acceptable primary source for market claims in a white paper that advertises third-party checkability.

H’s detector arithmetic also introduces an unstated assumption:

> “0.05·0.95 / (0.05·0.95 + 0.60·0.95) ≈ 7.7%”

The paper’s 8% figure is more directly explained by assuming human passages lack the tell, or by stating the relevant base-rate assumptions explicitly. H’s version silently inserts a 95% human-no-tell rate.

---

### 3. Disagreement about the autonomy frameworks

The white paper says:

> “The two published frameworks for grading progress toward general intelligence both treat autonomy as a deployment choice”

and

> “as systems climb the autonomy ladder, the human stops typing bytes and starts authorising tasks and reviewing results.”

The answers agree this is a logical failure, but they handle it differently.

A, G, and H are strongest here. They identify that the paper confuses:

- machine-written bytes;
- delegated task authority;
- human oversight level;
- general capability;
- AGI progress.

G is especially useful because it says the ledger does not record task length, so the paper’s phrase:

> “across teams and task lengths”

cannot be computed from the proposed instrument.

H is useful because it points out that an “approver” is not necessarily at the top of an autonomy ladder. If a human approves every hunk, that may be low autonomy, not high autonomy.

C identifies the core problem but is less precise about the exact framework levels. A correct final answer should say: cite the frameworks exactly, distinguish capability from autonomy, and do not claim that high machine-byte share corresponds to the top rungs of either ladder.

---

### 4. Disagreement about C2PA and Article 50

The white paper says:

> “IPTC's reading is that C2PA Content Credentials is the only existing technology that meets that requirement”

and

> “C2PA covers images, audio and video, and has no profile for a text file or a source repository.”

A, C, D, and G handle this best. They say:

- C2PA is not limited in principle to images/audio/video;
- external manifests or sidecar bindings matter;
- “no profile” is not the same as “technically impossible”;
- IPTC’s “only existing technology” claim must be quoted and scoped, not adopted as fact.

B largely misses this.

H is too lenient on the regulatory and standards claims.

A correct final answer must separate:

1. Article 50 legal text.
2. The European AI Office Code of Practice.
3. IPTC commentary.
4. C2PA specification capabilities.
5. The authors’ own gap analysis.

---

### 5. Disagreement about Level 2 anchoring

The white paper says:

> “Level 2, with the ledger head anchored in a log the developer cannot rewrite, does.”

This is one of the paper’s clearest technical overclaims. Anchoring a ledger head can make deletion or rollback detectable. It does not prevent a key-holder from signing false records, omitting events, or maintaining alternate histories.

A is strongest here. It separates:

1. publisher-signed claim;
2. transparency-anchored claim;
3. externally observed execution.

C, D, E, F, G, and H also catch this. B does not develop it.

A correct final answer must say that Rekor anchoring is not an execution witness and does not make signed assertions true.

---

### 6. Disagreement about how gameable the label is

All answers identify some gaming, but the complete threat model must include more than §7.

The most important missing attacks are:

- human text dictated to a model;
- human text paraphrased through a model;
- non-AI automation signed as “AI”;
- unlogged AI output appearing as “unattested”;
- selective repository scope;
- padding with generated boilerplate;
- stale badge display;
- replay or selective disclosure;
- key theft or CI key misuse;
- compromised hook;
- trusted-executor manipulation;
- registry spam;
- Goodharting;
- privacy leakage through small-team inference.

A, C, D, F, G, and H cover most of these. B and E cover fewer.

The biggest conceptual hole is this: the paper admits:

> “The key proves the channel, not the author.”

But the abstract still says:

> “Guaranteed AI certifies that a machine wrote the work”

Those two sentences cannot both stand.

---

## Answer-specific problems

### Answer A

A is extremely strong technically, but has a few issues.

1. **Verdict is too binary.**  
   A says:

   > “Do not publish in its current form”

   That is defensible, but the task asks for publish / publish after fixes / do not publish. The more precise editorial posture is: publish after major fixes, otherwise do not publish.

2. **Some source statements are too confident.**  
   A says:

   > “The 2025 Human Authored initiative is consistent with the known record.”

   That should be treated as unverified unless a primary source is cited.

3. **It does not flag the Nadella/LlamaCon attribution.**  
   The table says:

   > “29 Apr 2025 | Satya Nadella, at LlamaCon”

   Whether or not that is true, a hostile reviewer should require a primary recording or transcript. A misses that.

Otherwise, A’s security analysis is among the best.

---

### Answer B

B identifies the main logical problem but is too short and too confident.

Errors and risks:

1. **Overconfident source validation.**  
   B says:

   > “Your citations of the 2023–2025 literature … are accurate and well-contextualized.”

   That is not sufficiently cautious.

2. **Speculative implausibility claim.**  
   B says:

   > “Even projecting to mid-2026, this is highly implausible for a frontier AI lab.”

   The safer review would say: the claim needs primary transcript, denominator, scope, and definition; it may be exaggerated, but cannot be dismissed without evidence.

3. **Incomplete review.**  
   B does not adequately address:

   - Article 50;
   - C2PA;
   - Level 2 anchoring;
   - unit definitions;
   - registry bias;
   - privacy re-identification;
   - key governance;
   - reproducible self-check.

B’s “verbosity fallacy” and “dictation fallacy” are useful labels, but the answer is not complete enough.

---

### Answer C

C is the strongest, but has minor omissions.

It should have:

1. Explicitly flagged the Nadella/LlamaCon attribution as needing primary verification.
2. Explicitly flagged the Anthropic “90%-plus” claim as potentially exaggerated or denominator-dependent.
3. Computed the METR analogy error: 25% to 75% over 18 months is not a seven-month doubling cadence.
4. More explicitly corrected the Morris/Feng autonomy-ladder endpoints.
5. Stated plainly that readers may socially interpret “unattested” as “human,” even if the paper says otherwise.
6. Addressed the fact that a repository-bound badge may not travel with copied text.

These are omissions, not fatal errors.

---

### Answer D

D is sharp and useful, but overconfident in places.

Problems:

1. **Unverified factual corrections.**  
   D says:

   > “iHeart's 'Guaranteed Human' was announced November 2024, not 2025 — minor.”

   This needs a source.

2. **Unverified title correction.**  
   D says:

   > “Ref 12: the Kwa et al. title is 'Measuring AI Ability to Complete Long Tasks,' not '…Long Software Tasks.'”

   This also needs a source.

3. **Overbroad validation.**  
   D says:

   > “Sadasivan, Greenblatt, Meinke, Morris, Feng citations are real and correctly characterized.”

   The Feng framework is 2025 and should not be certified without checking the exact levels and definitions.

Despite that, D’s treatment of the METR doubling analogy and the mixed denominators is excellent.

---

### Answer E

E is reasonable but incomplete.

Strengths:

- It flags the Nadella/LlamaCon attribution as suspicious.
- It correctly says the Level 2 anchoring claim overstates what anchoring does.
- It correctly says §8 is not checkable without reproducible artifacts.

Weaknesses:

1. **Too little on regulatory and standards claims.**  
   It does not adequately handle Article 50, C2PA, IPTC, or the “nobody has shipped” claim.

2. **Too little on measurement specification.**  
   It mentions units and dependencies, but not as thoroughly as A, C, D, or G.

3. **Verdict is too severe without a salvage path.**  
   E says do not publish, but the provenance mechanism can be made publishable if the AGI argument is removed.

---

### Answer F

F is strong, blunt, and mostly correct.

Problems:

1. **Speculative statement about Redwood.**  
   F says:

   > “Ref [22] 67% gap recovery with 16-character hints: too specific to invent, too convenient to leave as a blog.”

   That is not a verification method. The correct move is to require the primary source and exact experimental definition.

2. **Misses some governance/legal requirements.**  
   F does not develop conflict-of-interest, governance, or legal disclaimer requirements as well as C or H.

3. **Verdict is too categorical.**  
   The paper is bad as written, but the underlying mechanism is salvageable.

F’s core critique is correct: the paper is a line-count badge with an AGI press release attached.

---

### Answer G

G has some of the best individual insights, but is weakened by overconfidence.

Strengths:

- It notes that the ledger does not measure task length.
- It notes that model identity is self-reported.
- It notes that the badge does not travel.
- It notes that key fingerprints identify keys, not accountable people.
- It notes that autonomy frameworks sever the link between adoption and AGI progress.

Problems:

1. **Overclaims verification.**  
   G says:

   > “Verified accurate: … Authors Guild 2025.”

   That is not safe without primary access.

2. **Underweights implausible claims.**  
   G says:

   > “The single implausible item is the METR characterization in §6.1.”

   The Anthropic 90% claim, the Redwood numbers, and the Semafor “50% the previous autumn” claim also need scrutiny.

3. **Introduces unnecessary framework claims.**  
   G brings in OpenAI’s reported levels and DeepMind internal staging. Those claims are not needed and may themselves require verification.

G’s analysis is valuable, but it should be more epistemically cautious.

---

### Answer H

H is detailed and mostly directionally correct, but too lenient.

Problems:

1. **Overconfident event verification.**  
   H says:

   > “Satya Nadella, LlamaCon, 29 April 2025, '20% to 30% of code'. Correct.”

   That should be verified, not declared correct.

2. **Too accepting of Wikipedia.**  
   H says:

   > “the paper wisely routes them through the Wikipedia 'No-AI label' article”

   That is not wise. The paper’s own thesis depends on re-derivable evidence. Wikipedia is not adequate for market claims.

3. **Detector arithmetic has an unstated assumption.**  
   H’s formula assumes a particular rate of human passages lacking tells. The paper’s 8% figure should be checked against the exact assumptions in NoHumanWrites.

4. **Too lenient on source hygiene.**  
   H treats several 2025/2026 claims as “plausible” without insisting strongly enough on primary sources.

H’s autonomy-ladder critique is good, but the answer is not strict enough for a hostile senior review.

---

## What a correct/safe final answer must include

A correct final review should give this verdict:

**Publish after fixes — major structural revision required.**  
If the authors refuse to remove or rigorously validate the §5–§6 claim that attested share measures rising autonomy toward AGI, the verdict becomes **do not publish**.

The review must include the following numbered fixes, most important first.

---

### 1. Stop claiming that the label certifies machine authorship

Offending abstract sentence:

> “Guaranteed AI certifies that a machine wrote the work, on the strength of a signed ledger produced at write time”

Offending §7 sentence:

> “The key proves the channel, not the author.”

These cannot both remain.

Required fix:

Replace the claim with:

> “The label certifies that a defined share of the artifact’s units passed through named, signed machine channels. It does not prove that the machine originated the content.”

The label must be renamed or qualified. Names such as:

> “Pure AI”

and

> “Guaranteed AI”

are misleading because they imply authorship, purity, or warranty. Safer names:

- “Attested machine channel”;
- “Machine-channel coverage”;
- “Signed provenance: machine channel”;
- “Attested ≥90% machine-channel coverage.”

The badge face must say:

- channel provenance only;
- not authorship;
- not quality;
- not safety;
- not legality;
- not copyright status;
- unattested does not mean human.

---

### 2. Delete or fully substantiate the AGI-thermometer claim

Offending abstract sentence:

> “a team's attested share, held at constant instrumentation, is the number that records that choice as it is made.”

Offending §5 sentence:

> “A registry of labelled work, counting attested shares over time with no names attached, would be a measurement of autonomy adoption taken in the field”

Offending §6 sentence:

> “So the label registers the approach before any benchmark declares it.”

Offending §6 sentence:

> “When the second number approaches 100 % across teams and task lengths, the human has moved wholly to authorisation and review, which is the operating description of the top rungs of both ladders.”

Required fix:

Delete the claim unless the authors provide independent validation that attested byte share correlates with a recognized autonomy measure, controlling for:

- task type;
- task length;
- model version;
- harness version;
- channel inventory;
- unit definition;
- repository scope;
- human review intensity;
- selection effects;
- generated boilerplate;
- non-AI automation.

Without that validation, the paper may only claim:

> “The label records machine-channel coverage for instrumented writes.”

It may not claim:

> “The label measures autonomy toward AGI.”

---

### 3. Replace the falsification test

Offending §5 sentence:

> “If the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong and the human hand is doing something the frameworks do not capture.”

This does not falsify the thesis.

Flat share could mean:

- teams chose not to delegate;
- safety policies restricted autonomy;
- task mix changed;
- review became stricter;
- unlogged channels increased;
- coverage changed invisibly;
- the registry selected low-autonomy teams.

Rising share could mean:

- more boilerplate;
- more formatters;
- more generated lockfiles;
- more padding;
- more channels instrumented;
- more copy-paste through the hook;
- more human text laundered through a model.

Required fix:

Provide a pre-registered causal model. Define:

- the treatment variable;
- the autonomy measure;
- the coverage audit;
- the task taxonomy;
- the expected confounders;
- the observations that would disconfirm the claim.

Do not present a one-sided test as falsifiability.

---

### 4. Correct the Level 2 security claim

Offending §7 sentence:

> “Level 2, with the ledger head anchored in a log the developer cannot rewrite, does.”

This is false as a defense against:

> “The key-holder lying.”

Anchoring can make deletion or rollback detectable. It does not prevent:

- false entries;
- omitted entries;
- alternate histories;
- selective disclosure;
- signing human-supplied bytes;
- signing by a stolen key;
- signing by a compromised hook.

Required fix:

Rewrite the security section as:

> “Level 2 anchoring can make previously committed history tamper-evident and can reveal deleted or forked records under specified verification assumptions. It does not establish the truth, completeness, or authorship of the signed events.”

Separate:

1. self-signed attestation;
2. transparency anchoring;
3. trusted execution or external observation.

Also specify:

- key custody;
- key rotation;
- revocation;
- compromise recovery;
- binding to commit/tree hash;
- timestamp trust;
- verifier policy.

---

### 5. Define the unit, denominator, and scope

Offending §3 sentence:

> “Two grades: Pure AI at 100 % attested, Guaranteed AI at 90 % or more with every unattested unit listed.”

“Unit” is not defined.

Required fix:

Define whether the unit is:

- byte;
- line;
- hunk;
- file;
- function;
- paragraph;
- verse line;
- musical bar;
- commit;
- pull request.

Define treatment of:

- lockfiles;
- vendored dependencies;
- generated protobufs;
- compiled artifacts;
- test fixtures;
- notebooks;
- markdown prose;
- binary files;
- renames;
- moves;
- rebases;
- merges;
- cherry-picks;
- reverts;
- formatters;
- linters;
- code generators;
- shell scripts;
- CI-generated files.

The badge must carry its scope. A badge for:

> “the `label/` directory alone”

must not be displayed in a way that implies whole-repository coverage.

---

### 6. Expand §7 to include the missing gaming modes

The current §7 is incomplete.

Required additions:

1. **Human-text laundering.**  
   A human says: “write exactly these lines.” The ledger attests the bytes, but the human authored them.

2. **Paraphrase laundering.**  
   A human writes text, then asks a model to paraphrase or refactor it. The result becomes “machine-channel.”

3. **Non-AI automation.**  
   Formatters, sed scripts, template engines, and build tools may write through the channel. If they count as “AI,” the label is misleading.

4. **Unlogged AI appearing as unattested.**  
   ChatGPT copy-paste, uninstrumented IDE apply, shell heredocs, or external agents may produce machine output that appears merely unattested. The market may read that as human.

5. **Padding.**  
   Generated comments, fixtures, boilerplate, or duplicated text can push the ratio above 90%.

6. **Selective scope.**  
   A team can label only high-machine-share directories.

7. **Stale badge misuse.**  
   Terms of use are not technical enforcement.

8. **Replay and selective disclosure.**  
   A signer may publish a subset of records.

9. **Key theft or CI misuse.**  
   A compromised key can mint arbitrary attestations.

10. **Malicious hook.**  
   A compromised toolchain can sign false records.

11. **Trusted-executor manipulation.**  
   A trusted executor may still execute misleading requests.

12. **Registry spam.**  
   An opt-in registry can be flooded with trivial generated artifacts.

13. **Goodharting.**  
   Teams may optimize the badge rather than the underlying practice.

14. **Privacy leakage.**  
   Listing unattested lines/files can identify individuals, especially in small teams or public git histories.

15. **Regulatory confusion.**  
   Users may mistake the label for EU AI Act compliance, C2PA certification, copyright status, or safety approval.

---

### 7. Fix the code-share table and abstract trend claim

Offending abstract sentence:

> “The machine share of new code at the largest labs rose, by their own reported figures, from a quarter to three quarters between October 2024 and April 2026.”

This is misleading.

The quarter-to-three-quarters movement is specifically a Google claim, if the reported 2026 figure is accepted. The table also mixes denominators:

- Google 2024: “new code”;
- Microsoft/Nadella: “code inside the company's repositories”;
- Google 2026: “new code”;
- Anthropic: “Anthropic's code.”

Required fix:

Rewrite as:

> “Several executives have reported rising AI involvement in code production, but the metrics, denominators, time windows, and source quality differ.”

Add columns for:

- denominator;
- definition of AI-generated;
- acceptance process;
- primary vs secondary source;
- confidence level.

Do not use these claims as a single industry curve.

---

### 8. Delete the METR doubling analogy

Offending §4 sentence:

> “which is roughly the doubling cadence METR measures for task horizons”

This is wrong.

A move from 25% to 75% over 18 months is a tripling of a share. If forced into an exponential framing, that is roughly an 11-month doubling, not seven months. More importantly, METR’s task horizon is a capability metric; code share is an adoption/reporting metric. They are not the same curve.

Required fix:

Delete the sentence.

Replace with:

> “The reported adoption increase is not directly comparable to METR’s task-horizon metric.”

---

### 9. Correct the “two independent measurements” claim

Offending §4 sentence:

> “Two independent measurements sit behind the reported figures.”

This is overstated.

Anthropic’s Economic Index is not independent of Anthropic. METR is independent but measures capability, not corporate code-share adoption.

Required fix:

Replace with:

> “Two published measurements are relevant, though one is produced by a lab whose behavior it describes, and neither directly audits the corporate code-share claims.”

---

### 10. Correct the market-survey and uniqueness claims

Offending §1 sentences:

> “Every label on the market for AI-era content points the same way: it tells the reader that a human made the work.”

> “All of them rest on a declaration, an estimate or a platform's private judgement, and none can be checked by a third party.”

> “Nobody has shipped the mark that points the other way”

These are too broad.

There are already:

- C2PA credentials;
- platform AI-content labels;
- synthetic-media disclosures;
- machine-readable marking requirements under Article 50;
- “made with AI” style labels.

The defensible gap is narrower:

> “We are not aware of a widely deployed, third-party-checkable, span-level machine-channel provenance label for text and source repositories.”

Required fix:

Replace the universal claims with a scoped comparison table.

---

### 11. Correct the regulatory and C2PA claims

Offending §1 sentence:

> “Article 50 of the EU AI Act, applicable from 2 August 2026, obliges providers of generative systems to mark outputs so that they are detectable as artificially generated”

This needs exact quotation and scope.

Required fix:

Quote Article 50 directly. State:

- which systems are covered;
- provider vs deployer obligations;
- machine-readable marking;
- deepfake disclosure;
- public-interest text disclosure;
- exceptions;
- technical feasibility qualifications.

Offending §1 sentence:

> “IPTC's reading is that C2PA Content Credentials is the only existing technology that meets that requirement”

Required fix:

If IPTC says “only,” quote it exactly and present it as IPTC’s opinion. Otherwise soften.

Offending §1 sentence:

> “C2PA covers images, audio and video, and has no profile for a text file or a source repository”

Required fix:

Distinguish:

- no embedded plain-text profile;
- no VCS-aware repository model;
- external manifests;
- generic asset binding;
- PDF and other text-bearing documents;
- authors’ reading of the specification.

Do not say C2PA cannot cover text unless the specification supports that absolute claim.

---

### 12. Correct the machine-vs-hand traceability claim

Offending abstract sentence:

> “Machine writing arrives with a prompt, a diff, a log, a test run and a signature, and hand writing arrives with none of those”

This is false as a universal claim.

Human work can have:

- git commits;
- signed commits;
- pull requests;
- CI logs;
- issue trackers;
- review comments;
- editor history;
- test runs.

Machine work can have none of those if uninstrumented.

Required fix:

Rewrite as:

> “Some machine write channels can be instrumented to produce signed, byte-level provenance. Human edits may also leave traces, but often lack prompt/tool-call provenance. The label measures covered machine-channel attestation, not the total presence or absence of human provenance.”

Also fix:

> “It is the least reviewed byte in the repository”

This is unsupported.

And fix:

> “the unreviewed edit after the machine finished”

The ledger does not observe review. It observes channel coverage.

---

### 13. Correct the framework and METR RCT claims

Offending §5 sentence:

> “The two published frameworks for grading progress toward general intelligence both treat autonomy as a deployment choice”

Required fix:

Say:

> “Two published frameworks we use treat autonomy separately from capability.”

Do not say “the two published frameworks” unless the paper enumerates the comparison set.

Offending §5 sentence:

> “Morris et al. … place today's frontier chatbots at the lowest rung”

Required fix:

Morris et al. assessed systems available at the time of that work. A 2023 paper does not automatically classify September 2026 systems.

Offending §4 sentence:

> “Developers could not tell, from the inside, whether the machine had helped.”

This misuses the METR productivity RCT. That study measured productivity perception, not authorship perception or provenance awareness.

Required fix:

Rewrite as:

> “The METR trial found a perception gap about productivity impact in its setting. It does not show that developers cannot identify machine-authored bytes.”

---

### 14. Fix the detector and NoHumanWrites claims

Offending §2 sentence:

> “A label that guesses from style would be wrong most of the time, and wrong about people.”

This is too broad.

Required fix:

State the detector’s:

- definition of “tell”;
- threshold;
- base rate;
- confusion matrix;
- out-of-sample protocol;
- corpus limitations.

The 8% precision calculation should be shown with assumptions.

Also state that NoHumanWrites is:

> “one developer’s machine over five weeks”

and therefore a pilot or prototype, not validation of a general field measurement.

---

### 15. Make the self-check reproducible

Offending §8 sentence:

> “if it does not, the ledger is right and this sentence is wrong.”

This is rhetoric unless the reader can verify it.

Required fix:

Publish:

- commit hash;
- tree hash;
- ledger entries;
- public key fingerprint;
- verification command;
- verifier version;
- unit counts;
- scope declaration;
- actual output.

If the paper claims the `label/` directory is attested, the badge must make clear that the rest of the repository is excluded.

---

### 16. Add governance, conflict, and legal disclaimers

The paper is from Plus de Fun Agency and cites the same agency’s NoHumanWrites work.

Required fix:

Add a governance section answering:

- who controls the label;
- who controls root keys;
- whether there is a trademark;
- whether there are fees;
- who operates the registry;
- how revocation works;
- what happens if the agency disappears;
- whether the spec is open;
- whether there is oversight.

Add a legal disclaimer:

> “This label does not certify quality, safety, security, legality, copyrightability, non-infringement, accuracy, regulatory compliance, or absence of human creative control.”

Also state:

> “This label is not, by itself, evidence of compliance with the EU AI Act or any other legal regime.”

---

## Bottom line

The correct final answer must be severe about the paper’s central thesis but not dismissive of the underlying mechanism.

The paper’s defensible core is:

> a signed, reproducible record of which artifact units passed through instrumented machine write channels.

The paper’s indefensible claim is:

> that this record measures rising autonomy toward AGI.

A safe final review must force the paper to choose between those two identities. If it becomes a provenance/attestation specification, it can be published after major fixes. If it remains an AGI-progress thermometer, it should not be published.

### moonshotai/kimi-k3 reviews
# Meta-review of the eight answers

## First, my independent read of the paper's actual faults (the yardstick)

The paper's real, checkable defects are:

1. **Category error**: the ledger attests a *channel*, not authorship (§7 concedes "write exactly these lines" defeats it); byte share ≠ autonomy (a human dictating line-by-line scores 100%; an autonomous agent fixing two lines scores ~0%); "unattested" ≠ human (the paper's own 9% heredoc result proves unlogged machine work lands there).
2. **The falsification test fails on the paper's own premises**: Morris et al. and Feng et al. say autonomy is a *deployment choice*, so flat attested share under rising METR horizons is *predicted*, not falsifying. "Constant coverage" is not independently auditable — §8's heredocs prove coverage fails non-adversarially.
3. **The Rekor claim is wrong**: anchoring a ledger head gives tamper-evidence against deletion/rollback; it does nothing against a key-holder signing false entries *before* anchoring. §7 says Level 2 "does" defend against "sign anything or delete records" — only half true.
4. **The cadence analogy is arithmetically false**: 25%→75% in 18 months is ×3, i.e. ~1.6 doublings, a doubling every ~11.4 months, not ~7 — and it compares an adoption share to a capability horizon anyway.
5. **Table comparability**: Pichai = flow ("new code"), Nadella = stock ("code inside the company's repositories"), Anthropic = undefined; "the largest labs" is one company.
6. **METR RCT misapplication**: it measured *productivity* perception, not *provenance* perception; "the instrument has to count bytes" does not follow.
7. **Framework accuracy**: Morris et al.'s autonomy axis is levels 0–5 (No AI → Tool → Consultant → Collaborator → Expert → **Agent**); they assessed *2023* systems, not "today's." Feng et al. run Operator → Observer with **Approver at L4** — so the paper overclaims "top rungs" (approval is one rung short of observer) but is *not* inverted.
8. **Citation hygiene**: the Kwa et al. title is "Measuring AI Ability to Complete Long Tasks" (no "Software"); iHeartMedia's "Guaranteed Human" was announced November 2024, not 2025; Nadella's 20–30% remark was indeed made **at LlamaCon on 29 April 2025** (he appeared with Zuckerberg; TechCrunch's Zeff covered it) — the paper's attribution is *correct*; Wikipedia as ref [2] is inadequate; the Semafor 75% and TechSpot 90% claims are unverifiable-but-plausible, not implausible (Anthropic staff made similar claims publicly in 2025).

## Errors, unstated assumptions, and disagreements among the answers

**Answer E contains a confident false factual correction.** E's blocking problem 4: *"LlamaCon is Meta's conference; Satya Nadella is Microsoft's CEO. He may have spoken at a Microsoft event… but 'at LlamaCon' is exactly the kind of detail that should not appear."* This is wrong — Nadella did make the remark at LlamaCon. In a task whose first instruction is "check every factual claim and attribution against what you know," inventing an attribution error sends the authors chasing a non-error and destroys reviewer credibility. G correctly states the Nadella/LlamaCon quote matches its knowledge. This is a direct disagreement, and G is right.

**Answer G contains a false framework correction.** G's fix 3(b): *"the top of Morris et al.'s autonomy axis is Organization… the axis runs Tool→Consultant→Agent→Innovator→Organization."* That is OpenAI's five-level scale (which G itself cites correctly in fix 13 as a *separate* framework). Morris et al.'s axis tops out at **Agent**. G "corrects" the paper with a wrong fact — the same sin E commits. A's treatment (levels 0–5, "five levels from tool to agent" defensible only if level 0 is excluded) is the accurate one.

**Answer H's central §5–§6 critique is built on a misreading.** H's Gap 1 claims the paper "has the ladder upside-down" because *"approver is at the low end of autonomy"* in Feng et al. Wrong: in Feng et al., Approver is L4 of 5, Observer is L5; moving from typing to approving *is* upward movement, just not the top. The paper's real error is conflating byte share with role and saying "top rungs" — not inversion. H repeats the error in fix 4 and the overclaiming section, so it propagates. D's version ("It cannot distinguish Approver from Observer") and A's version ("their highest autonomy category is not merely 'human approval and review'") are the precise ones. H's 8%-precision check also uses an unmotivated 0.95 factor (getting 7.7% where the paper's derivation, assuming human passages carry no AI-tell, gives ~8.1%; A states this assumption explicitly — the best treatment).

**Answer B overreaches on the one factual flag it attempts.** B declares the Anthropic "90%-plus" quote *"highly implausible"* and lectures about CUDA kernels. That is B's prior dressed as fact-checking; Anthropic figures made comparable claims in 2025. The task permits flagging implausible quotes, but the defensible position is A's/G's: unverifiable, needs the primary transcript, don't build the thesis on it. B also punts on the rest of the fact-check ("your citations of the 2023–2025 literature are accurate and well-contextualized") without evidence, and misses the Rekor error, the falsification failure, the cadence arithmetic, and the RCT misapplication.

**Answer C is accurate but bloated.** Its "detailed findings" section restates its 20 fixes nearly verbatim — roughly double the necessary length, a real flaw in a senior review. It also never verifies any arithmetic or framework details. No false claims, though; its "guarantee implies a guarantor and a remedy" and conflicts-of-interest points are genuinely useful and largely unique to C.

**Verdict spread**: A, E, F say do-not-publish(-as-is); B, D, H say publish-after-fixes; C, G conditionally escalate. This is mostly framing — A and F both say a rewritten provenance paper is publishable — but B's "publish after fixes" with five light fixes badly undersells the damage, and its verdict is the least defensible.

**Coverage disagreements worth noting**: the cadence arithmetic is caught by A, C, D, F, G but missed by B, E, H. The Rekor/false-entries error is explicit in A, C, E, G; only implicit in D and F; missed by B, H. The Kwa title and iHeart date are caught only by D. The §8 `label/`-only badge as scope-gaming is caught by A and D only. The "Guaranteed AI" vs "Guaranteed Human" confusion hazard, and model-identity being self-reported, are caught only by G. CI-as-writer and the "Guaranteed" (90%) being the *weaker* grade than "Pure" (100%) naming inversion are caught only by F.

## Strongest answer

**A is the strongest, with D a close second.**

A has zero detectable factual errors, computes the cadence correctly (11.4 months; 2^(18/7) ≈ sixfold), states the 8%-precision assumption and its sensitivity, gets Morris's 0–5 structure right, catches the RCT misapplication, states the Rekor limitation exactly ("anchoring does not stop the key-holder signing anything… it cannot establish the truth or completeness of the events being committed"), separates publisher-signed / transparency-anchored / externally-observed execution into three distinct assurance properties (the cleanest security analysis of the eight), and opens with explicit verification limits — the right epistemic posture given the task's instruction about 2026 sources. Its weaknesses are length and some overlap between fixes, and a verdict ("do not publish in its current form") that is harsher than necessary but argued.

D is the best per-word: it alone catches the Kwa title and the iHeart date, nails the "same words" literal falsehood, the Approver/Observer distinction, coverage endogeneity ("the thermometer's key assumption is in the hands of the thing it measures"), and the task-mix confound using the paper's own [13]. It loses to A only because the Rekor/false-entries point is implicit rather than stated, and the security analysis is thinner.

F is third: accurate, genuinely hostile in the requested register, with original catches (CI-as-writer, the grade-naming inversion, capability→hunk-size confound). G would rank higher but its Morris error is disqualifying for a fact-checking review. H's systematic citation-by-citation format is admirable but its central ladder claim is wrong. E is efficient but its false LlamaCon flag is costly. B is the weakest: thinnest, least verified, one dubious factual flag, and it misses the security and falsification core.

## What a correct/safe final answer must include

1. **A verdict of major revision** (either "publish after fixes" or "do not publish as-is" is defensible if justified; "publish" is not), with the justification that the *spec* is sound and the *thesis* is broken.
2. **The three-way distinction stated precisely**: channel attestation ≠ authorship ≠ autonomy, with both counterexample directions (dictation → 100% attested/low autonomy; autonomous two-line fix → low attested/high autonomy) and the admission that "unattested" includes unlogged machine work.
3. **The self-defeating falsification test**: flat share under rising horizons is predicted by the deployment-choice premise; coverage is not independently auditable; the test is one-sided.
4. **The Rekor correction**: transparency anchoring ≠ truth of entries; distinguish tamper-evidence from execution witnessing.
5. **The cadence arithmetic** (×3 in 18 months ≈ 11-month doubling, and categorically inapposite) and the stock/flow/undefined denominators in the table; "largest labs" is Google alone.
6. **The RCT scope**: productivity perception, not provenance perception.
7. **Framework accuracy without overcorrection**: Morris 0–5 topping at Agent, 2023 systems not "today's"; Feng's Approver at L4 — the paper overclaims "top rungs" but is not inverted. Do not flag Nadella-at-LlamaCon; do not call the Anthropic 90% claim implausible — call it unverified.
8. **Gaming additions**: laundering (direct and paraphrase), unlogged-AI-reads-as-human, denominator/dilution/scope gaming including §8's own `label/`-only badge, non-AI automation, key theft/sharing/rotation/revocation, the fingerprint-vs-"never a name" contradiction, hash-binding instead of terms-of-use for staleness, registry selection and Goodhart effects, git-history re-identification, self-reported model identity, and legal/copyright/AI-Act disclaimers.
9. **Citation fixes**: primary sources for Semafor/TechSpot/IPTC/Spotify, drop Wikipedia, correct the Kwa title, correct the iHeart date, verify the "few remaining tasks defeat the newest models" paraphrase (the one 2026-era quote that genuinely looks implausible against METR's own 50%-reliability framing).
10. **A reproducible §8 self-check**: commit hash, key fingerprint, verifier version, command, actual output — not a dare in prose.

### deepseek/deepseek-v4-pro-0813 reviews
## Meta-review of Answers A–H

**Verdict of the meta-review:** **Answer A is the strongest.** It gives the most complete, technically accurate, and actionable review. Its central diagnosis is correct: the paper confuses **signed write-channel provenance**, **authorship**, **autonomy**, and **AGI progress**. Answer A also correctly identifies that the proposed Level 2 transparency log would make false records persistent, not truthful, and it distinguishes several properties other answers blur together.

Close seconds are **Answer D** and **Answer G** for forensic specificity, but both contain at least one likely factual overcorrection that should not be copied.

---

## Why Answer A is strongest

### It correctly identifies the core failure

The white paper’s deepest problem is not sourcing or wording; it is that the label’s mechanical output is being sold as something it is not.

Answer A states this most precisely:

> “The most serious problem is that the paper repeatedly conflates: provenance with authorship; signed channel with truth; attested byte share with autonomy; deployment choices with progress toward AGI.”

That is the correct structure. Several other answers see parts of this, but Answer A keeps the distinction present throughout, including in concrete fixes:

- Rename the measured property as **attested machine-channel coverage**.
- State that the label does **not establish who originated the content**.
- Remove the claim that attested share registers the approach to AGI.
- Define exactly what the signature proves and what it cannot prove.

### It has the best treatment of Level 2 security

The paper says that a developer can sign anything, and then claims:

> “Level 2, with the ledger head anchored in a log the developer cannot rewrite, does.”

Answer A correctly rejects this:

> “Anchoring does not stop the key-holder signing anything. Nor does it prove that all relevant writes were logged.”

That is an important distinction that answers B, C, E, and H treat too softly. Answer A further separates:

1. publisher-signed claim;
2. transparency-anchored claim;
3. externally observed execution.

This is the right security framing.

### It correctly refuses the “falsification test”

The white paper proposes:

> “If the share stays flat at constant coverage while METR’s task horizons keep doubling, the thesis of this paper is wrong…”

Answer A explains why this only covers one narrow failure mode and does not validate the central claim:

> “A progression in software benchmark performance, executive reports of generated code, and an artifact’s write-channel coverage does not identify a latent variable called ‘approach to AGI.’”

It also correctly points out that “constant coverage” is not independently observable unless there is an external audit mechanism.

### Its focus on units and denominator is essential

Several reviews gesture at this, but Answer A makes it unavoidable:

> “The paper moves among bytes, lines, hunks, units, paragraphs, verse lines, and bars of music. Those are not interchangeable measurements.”

A verifiable numeric label cannot exist until the unit and denominator are defined. Answer A also names the practical attacks:

- generated comments and fixtures;
- vendored code;
- formatter-only rewrites;
- merges, revert, rebase, rename;
- binary and lockfile-style generation.

That is the right level for hostile review.

---

## Errors, risks, and overcorrections in the other answers

### 1. Answer D likely makes a false citation correction

Answer D says:

> “Ref 12: the Kwa et al. title is ‘Measuring AI Ability to Complete Long Tasks,’ not ‘…Long Software Tasks.’”

This appears incorrect. The METR paper’s title is, as of my knowledge, **“Measuring AI Ability to Complete Long Software Tasks”** or very close to that. The white paper’s reference title is likely not the error Answer D claims it is. A final review should not include that correction unless it is rechecked against the actual arXiv paper.

### 2. Answer G likely misstates the Morris et al. autonomy axis

Answer G writes:

> “The top of Morris et al.’s autonomy axis is Organization, not agent; the axis runs Tool→Consultant→Agent→Innovator→Organization.”

That is probably a conflation with OpenAI’s five-level staircase. In Morris et al. 2023, the autonomy axis is not organized as “Organization.” The top-end description is closer to an autonomous agent. The white paper’s phrase “from tool to agent” is a simplification, but Answer G overcorrects it. A safe final review should not assert that Morris et al.’s top autonomy level is “Organization.”

### 3. Answer E overstates the Nadella/LlamaCon issue

Answer E says Nadella speaking at LlamaCon is “exactly the kind of detail that should not appear in a table of record.” That is a useful demand for a primary transcript, but the implication that it is suspicious primarily because LlamaCon is Meta’s conference is not decisive. Executives do appear at partner or competitor events. The proper review instruction is: **verify the primary source and quote exactly**; do not frame it as implausible merely from the event name.

### 4. Answer B gives too much weight to editorial incredulity

Answer B says:

> “You are swallowing executive hype meant for investors and treating it as an empirical baseline.”

It calls the reported Anthropic CFO “90%-plus” line:

> “highly implausible for a frontier AI lab.”

This is not a strong reviewer move unless the claim is internally contradictory or contradicted by better evidence. The review should demand primary sourcing, denominator definition, and scope. It should not reject a future-dated reported figure on vibes. Answer A handles this better: do not reject 2026 sources merely for their date, but do not treat them as verified unless the transcript is available.

### 5. Answer C is unusually thorough but not reliably stronger

Answer C includes many good fixes, but it is bloated and occasionally overstates standards-based claims. For example, its treatment of C2PA is better than the white paper’s, but it risks replacing one overstatement with another by implying C2PA text provenance is closer than the specification currently shows. Answer C is a useful checklist, not a model of priority.

---

## Main disagreements among the answers

### Disagreement 1: Publish, revise, or reject?

- **A and F:** Do not publish as written.
- **B, C, D, G, H:** Publish after fixes, sometimes with strict conditions.

This is not a trivial difference. The strongest set of answers effectively agrees that the paper must not be published with the present abstract and §5–§6. The disagreement is mostly about how generously to describe the salvageable core.

**Resolution:** A safe final review should say: **do not publish while the AGI/autonomy claim remains central.** If the authors reframe the label as provenance and remove or fundamentally restrict §5–§6, then the engineering component may be publishable.

---

### Disagreement 2: Does attested share measure autonomy?

- **Most answers reject this**, especially A, D, F, G, and H.
- **B** underplays it.
- **C** rejects it but buries the diagnosis.

**Resolution:** The label measures **instrumented write-channel coverage**. It does not distinguish:

- a human micro-managing an AI typist;
- a truly delegated autonomous task;
- generated boilerplate with little semantic importance.

A correct final review must state this in the first or second fix.

---

### Disagreement 3: Does Level 2 solve key-holder lying?

- **A, C, D, F:** No, anchoring does not make false signed events true.
- **The white paper:** Yes, it claims Level 2 “does.”
- **Some answers** treat this too gently.

**Resolution:** The final review must explicitly separate:

1. detecting retroactive deletion or rollback;
2. preventing false first-party attestation;
3. executing outside the writer’s control.

A transparency log mostly helps with the first, not the second.

---

### Disagreement 4: Is “hand writing arrives with none of those” false?

The white paper says:

> “Machine writing arrives with a prompt, a diff, a log, a test run and a signature, and hand writing arrives with none of those.”

This is false as a universal claim. Human work can have signed commits, review records, CI logs, issue references, and editor telemetry. The correct claim is much narrower: certain agentic write paths can be instrumented at byte granularity in ways that ordinary editor edits often are not.

Most answers, especially A, C, D, F, and H, catch this. Answer G notices an even subtler point: the prompt is also bytes and is logged, but excluded from the share, so the paper’s assertion that the label “counts none of those because they are not bytes” is also imprecise.

---

## What a correct and safe final answer must include

A final review of this white paper should avoid being trapped into giving a simple “fix the wording” verdict. It should require the following, in approximately this priority order:

### 1. Reframe the label as channel provenance, not authorship

The abstract and label name must be changed or heavily qualified:

> “Guaranteed AI certifies that a machine wrote the work.”

must become something like:

> “Guaranteed AI certifies that listed units passed through an attested machine channel.”

The terms **“Pure AI”** and **“Guaranteed AI”** are misleading unless their operational definition appears on the badge itself.

---

### 2. Remove or demote the AGI/autonomy thesis

The most dangerous sentences are:

> “A registry of labelled work… would be a measurement of autonomy adoption taken in the field…”

and

> “So the label registers the approach before any benchmark declares it.”

A correct review must say these are not supported. The label can measure **provenance adoption**, **instrumentation coverage**, or **delegation of typing**. It cannot measure the conceptual autonomy variable in Morris et al. or Feng et al. without validation.

---

### 3. Define the measurement system before claiming verification

The final review must require:

- what a “unit” is;
- what the denominator is;
- how generated, vendored, binary, and imported files are handled;
- how merges, rebases, renames, deletions, and formatter rewrites are counted;
- how the ledger binds to the final artifact or commit;
- how coverage is independently audited.

Without this, terms like **100 % attested** and **90 % guaranteed** are undefined.

---

### 4. Fix the security and threat model

A safe final answer must not let the paper claim:

> “Level 2, with the ledger head anchored in a log the developer cannot rewrite, does.”

It must say: anchoring detects rollback or deletion after the fact; it does **not** prevent the key-holder from signing false statements in the first place.

The paper must also address:

- key theft;
- CI signing with machine keys;
- key rotation;
- revocation;
- compromised hooks;
- prompt injection;
- selective publication of a favorable ledger head.

---

### 5. Expand the gaming section materially

The white paper’s §7 is too thin. A correct review must name the most important missed attacks:

- Human-written text laundered through the agent.
- AI washing of human IP.
- Non-AI automation counted as “AI.”
- Unlogged AI presenting as unattested and therefore readable as “human.”
- Repository or directory scope selection.
- Generated boilerplate dominating the denominator.
- Opt-in registry selection and Goodhart pressure.
- Stale badge display without cryptographic artifact binding.
- Re-identification on small teams despite name omission.

---

### 6. Fix factual reporting and sourcing

The final review must require primary sourcing or explicit downgrading of:

- Google 75 % and Anthropic 90 % executive claims;
- Spotify Verified badge policy;
- iHeartMedia and Berlinale examples;
- IPTC’s supposed claim that C2PA is “the only” technology;
- the “quarter to three quarters” trend language, which is mostly a Google-specific claim.

The table must also distinguish:

- new code vs repository stock;
- AI-generated vs AI-assisted;
- generated by Claude vs written by software;
- accepted code vs suggested code.

---

### 7. Correct the false cadence comparison

The review must remove or force deletion of:

> “It moved from a quarter to three quarters in eighteen months, which is roughly the doubling cadence METR measures…”

A change from 25 % to 75 % over 18 months is not a 7-month doubling curve, and the two quantities are different in kind.

---

### 8. Require a reproducible self-check in §8

The paper’s statement:

> “if it does not, the ledger is right and this sentence is wrong”

is not a verification. A safe final review must require the actual commit, key fingerprint, ledger entry, unit definition, and `--label` output.

---

## Bottom line

**Answer A should be the base of the final review.** It is not perfect, but it has the correct architecture, the correct security analysis, and the highest density of actionable fixes. Answer D and Answer G are useful supplements, but should not be followed blindly because of likely factual overcorrections.

The safe final position is: **do not publish in current form.** The paper can only become publishable if it stops claiming that a signed byte channel is a measurement of autonomy toward AGI and instead becomes a careful provenance and instrumentation proposal.

### x-ai/grok-4.6 reviews
**Strongest: A**, with **C** and **D** close. A is the only review that is simultaneously (i) technically precise about what a signature/log can prove, (ii) correct on the load-bearing logic of §5–§6, (iii) specific enough to quote and rewrite, and (iv) almost free of false “corrections.” C matches A’s substance and is slightly more publication-calibrated. D is the best short review and catches several real citation bugs A underplays. B, E, G, and H each inject at least one harmful error or a thin substitute for the argument.

Do **not** treat B/E/G/H as authority on facts they “correct.”

---

## Independent reading of the white paper (the bar)

The instrument is a **write-channel coverage statistic**: signed records that some in-scope units passed a named hook. That is publishable as provenance engineering.

The paper then sells three non sequiturs:

1. channel coverage ⇒ **the machine wrote it**  
2. rising coverage ⇒ **rising autonomy**  
3. that series ⇒ **approach to AGI**, “before any benchmark”

§7 already falsifies (1): *“A prompt of ‘write exactly these lines’ yields an attested hunk. The key proves the channel, not the author.”* The abstract still opens with *“Guaranteed AI certifies that a machine wrote the work.”*

(2)–(3) fail even with an honest hook. High attested share is compatible with dictation, formatter/CI noise, boilerplate, rewrite-laundering, and subdirectory scope. Low share is compatible with chat-paste, heredocs (the paper’s own 9% / 17%), and high-autonomy one-line fixes. Morris/Feng **separate** capability from autonomy; they do not license “bytes typed = ladder rung.” The proposed falsifier (flat share + METR doubling ⇒ thesis wrong) is one-sided and, on the paper’s own premise that autonomy is a **deployment choice**, can **confirm** the frameworks rather than kill the thesis.

Level 2 as written is also oversold: Rekor-style anchoring can make **deletion/equivocation** visible; it does not stop a key-holder **signing a lie** and then anchoring it.

A correct review must say that. Verdict space: **do not publish as an AGI/autonomy paper**; a stripped provenance note could be **publish after fixes**. “Publish after copy-edits” is not available.

---

## Errors, assumptions, risks, disagreements in A–H

### Verdict split (real disagreement, not noise)

| Verdict | Answers |
|---|---|
| Do not publish | A, E, F |
| Publish after (major) fixes | B, C, D, G, H |

This is mostly **scope**, not substance: A/F refuse the document that still contains §5–§6; C/D/G/H allow a rewrite that deletes the thermometer. E’s “do not publish” is weaker because it rests partly on a bad factual flag (below). B’s “publish after fixes” is too cheap: five light patches do not repair the chain.

**Unstated assumption in the “publish after fixes” camp:** authors will accept renaming the product and killing the AGI sections. If they will not, C already says the verdict flips; A/F just start there.

### Harmful false or overstated “corrections”

- **E on Nadella/LlamaCon.** E: *“LlamaCon is Meta’s conference; Satya Nadella is Microsoft’s CEO… ‘at LlamaCon’ is exactly the kind of detail that should not appear.”* Nadella **did** speak at LlamaCon (29 Apr 2025); TechCrunch is the usual source. This is a **false positive**. A review that forces authors to “fix” a correct row is worse than silence. G and H get this right; E does not.
- **G on Morris’s autonomy axis.** G: top of Morris is *Organization*; axis is *Tool→Consultant→Agent→Innovator→Organization*; *“five levels from tool to agent” misstates the endpoint.* That **mixes Morris 2023 with OpenAI’s 2024 Chatbots→…→Organizations ladder**. Morris’s autonomy scale is 0–5 including **No AI**, topping at **Agent**, not Organization. A is right here; G would make authors “correct” the paper into a new error.
- **H on the ladder being “upside-down.”** H treats “approver” as Feng’s **bottom** and says the paper inverts the ladder. Feng’s cited direction is **operator → observer** (human role shrinking). “Stops typing, starts authorising” is **climbing away from operator**, not inversion. The real bug is equating **authorisation/review** with the **top** rung and with AGI. H’s “upside-down” frame would send a rewrite in the wrong direction.
- **H’s detector arithmetic.** Paper: ~8% at 5% human share if 60% of machine passages have no tell. Correct (A, D): \(0.05/(0.05+0.95\cdot0.60)\approx 8.1\%\). H writes \(0.05\cdot0.95/(0.05\cdot0.95+0.60\cdot0.95)\approx7.7\%\) and still says “the math checks out.” It does not. H also assumes too much of the 2026 secondary record is “fine.”
- **B on Rao “90%-plus.”** Instruction: do not reject 2026 sources for date; flag only if the **quote** looks implausible. B calls the **substance** “highly implausible” for a frontier lab and demands authors treat it as investor hype. That is a prior, not a source check. Flag **denominator/hype**, don’t invent impossibility.

### Shared hits (these are real)

Almost every serious answer agrees, and they are right:

- Abstract/§3 **authorship** vs §7 **channel**
- §5–§6 **bytes ≠ autonomy ≠ AGI**; *“registers the approach before any benchmark”* does not follow
- *“hand-typed or unlogged”* in the abstract contradicts the heredoc result
- Table **denominators** mixed; abstract’s *“largest labs… quarter to three quarters”* is a **Google** arc in plural clothing
- *“roughly the doubling cadence METR measures”* is **arithmetically and categorically** wrong (×3 in 18 months ≈ **11-month** doubling of a **share**, vs ~7-month doubling of a **horizon**)
- *“two independent measurements”* — Anthropic Index is not independent of Anthropic
- METR RCT is **productivity perception**, not provenance; *“could not tell whether the machine had helped”* overreaches
- Level 2 **anchor ≠ truth**
- §7 misses: unlogged AI read as human; non-AI automation as AI; rewrite/AI-wash; padding/units; scope (`label/` vs 17%); badge not bound to digest; registry selection/Goodhart; key fingerprint ≠ person; “unreviewed” unobservable
- *“Every label… none can be checked”* / *“Nobody has shipped the mark that points the other way”* — Article 50 and C2PA already mark **machine** origin for some media
- Wikipedia [2]; Semafor [10] without transcript used as a **wording** keystone
- C2PA “no text profile” overstated (sidecars / generic assets)
- “Guaranteed” / “Pure” will be read as warranty / no human
- n=1 five-week study cannot carry a field thermometer
- §8 dare is not a verifier output

### Gaps A still has (why C/D are not redundant)

A is strongest **overall**, not complete:

- Underplays **Kwa et al. title** (*Long Tasks* vs paper’s *Long Software Tasks*) — D catches this.
- Underplays possible **iHeart date** (campaign closer to late 2024 than “2025”) — D flags; still needs a primary page, not D’s memory as gospel.
- “Do not publish” is right **for this manuscript**; A could say more clearly the **acceptance condition** C states: cut AGI or don’t ship.
- A cannot retrieve 2026 URLs (honest) but then sometimes leaves “unverified” next to claims others correctly treat as **structurally** unusable (Semafor wording as parallel to 2024).

C’s extra value: explicit **legal/compliance camouflage**, **conflicts/governance**, **spec-in-appendix**, **unattested ≠ human** as a face-of-badge rule. Those belong in a safe final review.

D’s extra value: tight mapping of **inscription vs judgment**, **endogenous coverage** (heredocs today), **opt-in registry ≠ everyone’s number**, abstract conflation. Best “fixes 1–5” list after A.

F is the cleanest **kill shot** on §6.5 and the one-sided falsifier, but it is more polemic and thinner on unit/denominator/spec, so it is not the best **standalone** review.

### Risks if one answer were followed blindly

- Follow **E** → authors “correct” a true LlamaCon citation.
- Follow **G** → authors mis-cite Morris as OpenAI’s org-level AGI scale; also G’s “Digital Omnibus postponement” is an unverified extra.
- Follow **H** → rewrite the ladder as inverted; keep too much trust in secondary 2026 colour; ship a wrong precision check.
- Follow **B** → AGI sections get a caveat sticker; **Pure AI** and Level 1 “guarantee” survive.
- Follow **A or C without D** → Kwa title and a few citation-hygiene items slip.
- Follow **F alone** → correct reject, weaker numbered rewrite guide.

---

## What a correct/safe final answer **must** include

1. **Verdict, scoped:** Do not publish v0.1 as a measurement of autonomy/AGI. Publish only after the label is **channel provenance**, §5–§6 are cut or reduced to a hypothesis with an independent autonomy criterion, and Level 1 is not a public “guarantee.”

2. **The contradiction, quoted:**  
   Abstract: *“Guaranteed AI certifies that a machine wrote the work…”* vs §7: *“The key proves the channel, not the author.”*  
   Rename grades; put *“unattested ≠ human; channel ≠ authorship”* **on the seal**.

3. **§5–§6 category error, quoted:**  
   *“So the label registers the approach before any benchmark declares it.”*  
   *“When the second number approaches 100 % … the human has moved wholly to authorisation and review…”*  
   Counterexamples: dictation; one-line autonomous fix; boilerplate; prompt-steering not counted. Morris/Feng do **not** make inscription share the autonomy variable. Do **not** tell authors the Feng ladder is upside-down; tell them **approval ≠ top rung ≠ AGI**.

4. **Falsifier:** *“If the share stays flat at constant coverage while METR’s task horizons keep doubling…”* does not falsify a **choice** variable; coverage is **endogenous** (§8 heredocs). Demand a pre-registered protocol or drop “the one measurement.”

5. **Security, quoted:** *“Level 2, with the ledger head anchored in a log the developer cannot rewrite, does [defend against the key-holder lying].”* Split: signed claim / transparency / **external observation**. Anchoring ≠ completeness ≠ trusted execution.

6. **Fact hygiene (only real bugs):** mixed denominators; plural “labs”; METR cadence analogy (×3 ≠ 7-month doubling); “independent” Anthropic Index; Wikipedia [2]; [10] wording without transcript; Article 50 **already marks machine content** (so §1’s “regulation points the same way” is backwards); C2PA overclaim; Morris 2023 ≠ “today’s” 2026 systems; METR RCT misused; n=1. **Do not** “fix” Nadella@LlamaCon. **Do not** rewrite Morris as Organization.

7. **§7 holes, at least:** unlogged AI as “human”; scripts/formatters as “AI”; laundering/rewrite; unit/denominator/padding; directory scope (§8); no digest binding (ToS is not a control); registry Goodhart/selection; fingerprint vs name vs git re-ID; “unreviewed” ; regulatory lookalike.

8. **Counting spec:** one unit, denominator, exclusions (vendor, lockfiles, generated), canonicalization, bind to tree/commit, verifier inputs beyond “the public key.”

9. **Tone:** *“This label never guesses,”* *“least reviewed byte,”* *“everyone’s number,”* *“Pure AI,”* *“Guaranteed.”*

Anything weaker than that (B), or that “corrects” true citations (E) or frameworks (G/H), is not a safe final review.

**A** is strongest because it already contains items 1–8 at engineering depth and does not add false errata. Fold in **C**’s compliance/governance/spec-appendix demands and **D**’s citation nits (Kwa title; abstract “hand-typed”; inscription vs judgment one-liner). Discard E’s LlamaCon suspicion, G’s Morris/OpenAI mashup, H’s inverted ladder and 7.7% formula, and B’s “just caveat AGI.”

### z-ai/glm-5.3 reviews
(no answer from z-ai/glm-5.3: 'NoneType' object has no attribute 'strip')

### minimax/minimax-m3 reviews
I read the paper, then read all eight reviews against it. I have my own view of which errors are load-bearing versus cosmetic. My conclusions:

## Cross-review comparison

**All of A, C, D, F, G, H catch the same set of core errors**: channel ≠ authorship; bytes ≠ autonomy; registry selection bias; §4 sourcing weakness; the §1 universal claims ("every label", "none can be checked", "nobody has shipped"); the §1 C2PA "only existing technology" overclaim; the Level 2 anchoring overclaim; missing §7 attack modes; the unit/denominator ambiguity; the "Pure AI" / "Guaranteed AI" branding overclaim; and the §8 self-check being non-reproducible. B catches only the high-level points and misses the substance.

**Errors caught by only one or two reviews (and missing from the rest)**:

- **The autonomy-ladder mapping is inverted**. *Only H catches this clearly.* Per Morris et al. and Feng et al., the *approver* is mid-to-low on the autonomy ladder; the *operator* is the lowest rung, the *observer* (or *agent*-level) is the top. The paper's §5 says "as systems climb the autonomy ladder, the human stops typing bytes and starts authorising tasks and reviewing results" — but climbing means going *from* operator *to* observer, and an active approver is below an observer, not above. G notes the Morris endpoint is "Organization" not "Agent" but does not draw the inversion. A, B, C, D, E, F miss it. This is the paper's most fatal logical error.
- **The §4 "in the same words" rhetorical parallel is built on a quote flagged as unverified**. Only D catches that the paper's own table uses different words ("reviewed and accepted" / "approved"), and the 2026 Semafor row is admitted as "primary transcript not located."
- **The Kwa et al. title is wrong** ("Long Tasks", not "Long Software Tasks"). Only D catches this — particularly damning in a paper whose thesis is attribution precision.
- **The §6.1 paraphrase "few remaining tasks defeat the newest models" is unsupported by METR's data**. Only D and G flag this. A 320-minute 50%-reliability horizon means most tasks longer than ~5 hours still defeat the best model; the paper's paraphrase implies mastery.
- **The iHeartMedia date is wrong** (announced November 2024, not 2025). Only D catches.
- **E flags Nadella at LlamaCon as suspect**. E is wrong here: Nadella did speak at Meta's LlamaCon on 29 April 2025 about the 20–30% figure. E is over-skeptical on this point.
- **F correctly notes the §6 title promises "general intelligence" but the body argues no such thing**. The other reviews don't name the title-body mismatch.

**Verdicts split three ways**: A, E, F → do not publish; B, C, D, G, H → publish after fixes. I side with the latter group, but only because a clean rewrite is genuinely possible. The fixes are structural, not copy-edits; if they are not made, the paper is unpublishable.

## Which review is strongest

**H is the strongest.** It is the only review that catches the autonomy-ladder inversion (the paper's most critical error), it has a clean verification list, it distinguishes measured from claimed consistently, and its §5–§6 logical analysis is the most systematic. It also catches the §6 title–body mismatch and the §6.1 METR paraphrase.

**D is a close second**, sharper on specific factual errors (Kwa title, iHeart date, "in the same words", doubling math) but less systematic on the §5–§6 framework mapping.

A and C are comprehensive but each misses critical points. F is rhetorically strong but somewhat overheated — its aggressive tone is appropriate for some claims but not all (e.g., calling the spec "a README" is fair, but the Sadasivan characterisation is loose). G is solid and catches the Morris endpoint but loses the ladder inversion. B is too brief and misses most of the substantive issues.

## What a correct/safe final answer must include

1. **The badge certifies a channel, not authorship.** The paper's own §7 admits "the key proves the channel, not the author." The abstract and §1 must say so, or the brand name must change. "Pure AI" on work whose every byte was dictated in a prompt is false advertising; "Guaranteed AI" is weaker marketing on the same lie.
2. **The instrument measures byte-coverage of logged machine channels, not autonomy, not capability, not AGI progress.** A registry of attested shares is an adoption index, not a thermometer.
3. **The autonomy-ladder mapping must be fixed** per the cited frameworks, or the ladder reference must be dropped.
4. **The §1 universal claims must be scoped.** "Every label", "none can be checked by a third party" (contradicted by the paper's own ref [4]), "nobody has shipped the mark that points the other way" (C2PA, watermarks, and platform AI-disclosure labels all exist) — all are false as stated.
5. **§4 corporate claims must be primary-sourced** or downgraded to "as reported, not independently verified." The Semafor row admits "primary transcript not located"; the rhetorical parallel cannot be built on a quote that may not exist.
6. **§7 must cover**: prompt-supplied content, non-AI automation (formatters, sed) signed as "AI", rewrite laundering (agent reads human file, writes it back), scope cherry-picking, threshold gaming, repository splitting, CI codegen, key governance and theft, vendor/dependency hiding, stale-badge technical binding, registry deanonymisation, Goodhart/leaderboard dynamics.
7. **Units, denominator, and counting policy must be defined** before any 90% threshold.
8. **The spec must move into the paper or an appendix**, not stay behind a separate README, for a paper whose argument is "here is what the label guarantees."
9. **§8 must publish the actual `--label` output, key fingerprint, commit hash, and verification command**, not a prose dare.
10. **The §1 IPTC "only existing technology" claim must be quoted exactly or softened.**
11. **The §6 weakness paragraph is the strongest part of the back half** and should be kept. The preceding chain, however, must be cut.

## Verdict

**Publish after fixes, conditional.** The engineering is sound enough to deserve a paper that doesn't overclaim it. If the authors will rewrite §5–§6 to drop the autonomy/AGI argument, rename the badge, fix the §1 universal claims, expand §7, primary-source the §4 claims, and publish the §8 self-check reproducibly, the result is publishable. If they insist §5–§6 is a field measurement of rising autonomy toward AGI, the verdict becomes **do not publish**.

## Numbered concrete fixes (most important first)

1. **Rewrite §5–§6 to remove the autonomy/AGI claim.** Replace with: "Attested share is a coverage statistic of bytes passing through logged machine channels. It is not a measure of autonomy, capability, or AGI progress." A registry of such measurements is a self-selected adoption index, not a field thermometer. Quote to delete: *"So the label registers the approach before any benchmark declares it."*

2. **Rename the badge.** "Guaranteed AI" cannot coexist with §7's admission that the key proves the channel, not the author. "Pure AI" cannot coexist with the "write exactly these lines" attack §7 itself describes. Use names that describe what is measured, e.g., "Fully Attested Machine Channel" / "Attested ≥90% Machine Channel," and put the channel-not-authorship caveat on the badge face.

3. **Fix the autonomy-ladder mapping in §5.** Quote to fix: *"as systems climb the autonomy ladder, the human stops typing bytes and starts authorising tasks and reviewing results."* Per the cited frameworks, an active approver is mid-to-low on the autonomy ladder; the top is observer/agent, not approver. Either rephrase or drop the ladder reference.

4. **Retract the §4 doubling-cadence comparison.** Quote to delete: *"It moved from a quarter to three quarters in eighteen months, which is roughly the doubling cadence METR measures for task horizons."* 25%→75% in 18 months is a tripling of share (no clean doubling model applies to a 0–100% share); METR measures task horizon at 50% reliability; the two quantities are incommensurable. The Anthropic row uses a different denominator again.

5. **Retract "in the same words" in §4.** Quote to fix: *"both statements, eighteen months apart, name the human's remaining role in the same words: 'reviewed and accepted', 'approved'."* The paper's own table uses different words, and the 2026 Semafor row admits "primary transcript not located." Verify the transcript or delete the parallel.

6. **Replace Wikipedia with primary sources** for §1's market survey (Authors Guild, iHeartMedia, Spotify, Berlinale). The paper argues nothing should be believed unless re-derivable; sourcing its competitive landscape to a tertiary source is bad faith.

7. **Verify §4 corporate claims with primary transcripts or downgrade to "as reported, not independently verified."** The Anthropic 90% and Google 75% rows are load-bearing and currently rest on TechSpot and Semafor.

8. **Replace the falsification test.** Quote to fix: *"If the share stays flat at constant coverage while METR's task horizons keep doubling, the thesis of this paper is wrong."* A one-sided test that can only fail in the direction the paper does not expect is not falsifiability; it is theatre. Specify a pre-registered protocol with channel inventory, unit definition, coverage audit, and the rise conditions that *would not* count as autonomy.

9. **Expand §7** with the missing attack modes: prompt-supplied content laundered as machine-written; non-AI automation (formatters, sed, codegen templates) signed as "AI"; rewrite laundering (agent reads human file, writes it back at 100% attested); scope cherry-picking (labelling a subdirectory at high share, as §8 itself does); threshold gaming (89.9% → 91% by re-emission); repository splitting (human work in repo A, agent work in repo B); CI codegen as the de facto writer; vendor/dependency hiding; key governance (theft, rotation, revocation, no PKI defined); stale-badge technical binding; registry deanonymisation on small teams; Goodhart/leaderboard dynamics once the registry publishes quarterly.

10. **Define units, denominator, and counting policy before any 90% threshold.** Lines vs hunks vs files vs tokens; whether generated and vendored paths count; merkle-of-tree vs write-time events; how copy-paste, formatter rewrites, and rebases are counted. Quote to fix: *"every hand-typed or unlogged span listed beside the number."* Unattested ≠ hand-typed; this is the conflation the §2 heredoc example itself disproves.

11. **Tone down §1 universal claims.** *"Every label on the market for AI-era content points the same way"*, *"none can be checked by a third party"*, *"Nobody has shipped the mark that points the other way"* are all false as stated. Replace with scoped claims: "the marks that have shipped in this period point toward human production; C2PA, watermarking standards, and platform AI-disclosure labels also exist; the gap we are filling is third-party-checkable text/repo provenance with per-unit listing of unlogged spans."

12. **Make §8 reproducible.** Publish the commit hash, key fingerprint, ledger entry URL, `--label` command, and verifier output. A prose dare is not a verification.

13. **Add Goodhart/leaderboard caveats to §5 and §9.** An opt-in registry of attested shares is a leaderboard; teams will route work through the agent to raise the number. Specify per-channel publication, no per-team publication, or delayed rolling aggregates.

14. **Disclose the author's conflict** (A. Chrétien is also the NoHumanWrites author).

15. **Move the spec into the paper or an appendix.** A white paper making guarantee claims cannot leave the guarantee definition in a separate README.

16. **Soften or quote the §6.1 METR paraphrase.** *"The authors note that few remaining tasks defeat the newest models"* is unsupported by METR's 50%-reliability data. Quote METR verbatim or cut the claim.

17. **Correct the Kwa et al. title** in ref [12]: "Measuring AI Ability to Complete Long Tasks," not "Long Software Tasks." Trivial but characteristic.

18. **Soften "the most-cited operational yardstick" in §6.1.** Unsupported superlative.

19. **Add the §2 detector calculation's assumptions explicitly.** The 8% precision is for one specific "no tell = human" rule at 5% human share; the paper's framing implies more.

20. **Tighten the §6 weakness paragraph** — the strongest part of the back half — by adding that the demonstrated failure mode today (§8's heredocs) is *coverage* loss, which Level 2 anchoring does not address.

---
> Hand to Claude (orchestrator) for synthesis + final-watch, then Arnaud approves.
