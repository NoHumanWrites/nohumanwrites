# Council — external voices (build) · 8 members

TASK: Fact-check and stress-test this new section (§10) of a research paper before public release. It must be bulletproof. For EVERY factual claim, quote and citation: (1) is it accurate to the best of your knowledge, (2) is the source real and correctly attributed, (3) is any number, date or quote wrong or overstated, (4) is any important top-tier source on AGI progress, definitions or AI control missing that a hostile expert reviewer would expect? Note: several sources are dated 2025–2026 and may postdate your training data; if you cannot verify one, say 'cannot verify' rather than 'false'. Also judge the reasoning: does the argument (provenance unit shifts from bytes to authorisation as autonomy rises; threat model inverts per AI-control literature) hold, and where is it weakest? Give concrete fixes. End with a one-line verdict.

SECTION FOLLOWS
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

REFERENCES CITED IN THE SECTION
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

## Round 1 — independent answers

### A. openai/gpt-5.6-luna-pro
## Overall assessment

The section has a sound motivating intuition—provenance must follow the point of control as systems become more autonomous—but it currently overstates both the empirical evidence and the AI-control analogy. Several central citations are dated after my verifiable knowledge horizon, so I cannot authenticate their existence, wording, numbers, or attribution. Those items must be checked against the original publication pages before release.

The most serious problems are:

1. **Unsupported superlatives and forecasts**: “most-cited,” “arrive within the planning horizon,” and “the threat model inverts.”
2. **Metric slippage**: “unattested,” “machine-written,” “authorised,” “reviewed,” and “safe” are treated as near-equivalents but are not.
3. **Overclaiming from AI-control work**: AI control does not generally say that human adversaries disappear or that the threat model simply reverses.
4. **Weak causal support for the prediction in §10.2**: the claimed monotonic trends do not follow from the autonomy frameworks.
5. **Future citations are presented with precise figures and quotations without a verification disclaimer.**

---

# 1. Opening claims

### “Everything above is measured on current systems, which are not general intelligences by any published definition.”

- **Accuracy:** Partly accurate, but too absolute.
- **Source status:** No citation is supplied.
- **Problem:** There are many published definitions and operationalizations of AGI. The defensible claim is not that current systems fail “any published definition,” unless the paper explicitly surveys all relevant definitions. Some definitions are sufficiently loose that current systems may qualify.
- **Fix:**

> “The measurements above concern current systems; whether those systems qualify as AGI depends on the definition used. Under the operational frameworks adopted here, they should not be treated as general intelligences.”

### “The people building them say general intelligence is near…”

- **Accuracy:** Broadly plausible, but not a factual proposition without a defined sample.
- **Source status:** Needs citations to named statements.
- **Problem:** “The people building them” is an overgeneralization. Industry views range from near-term AGI forecasts to explicit skepticism.
- **Fix:** Name the individuals and characterize the evidence as selected public statements.

### “The benchmarks that try to measure it say the gap is still visible…”

- **Accuracy:** Plausible, but benchmark-dependent.
- **Source status:** [20] and [21] are apparently intended to support this.
- **Problem:** ARC-AGI and METR measure particular capabilities, not “AGI” in general. A visible gap on one benchmark does not establish a general AGI gap.
- **Fix:**

> “Several operational evaluations report substantial residual gaps on the dimensions they measure, including long-horizon software work and adaptation to novel tasks.”

### “The field has no agreed definition.”

- **Accuracy:** Substantially accurate.
- **Source status:** This is a standard characterization, but it should be cited.
- **Useful sources:** Morris et al. [18], Chollet [21], Legg and Hutter, OpenAI’s charter or AGI statements, and the AAAI 2025 panel/report if relevant.
- **Qualification:** Lack of consensus does not mean lack of serious definitions.

---

# 2. §10.1: measured claims

## METR

> “METR's time-horizon work, the most-cited operational yardstick for autonomous capability…”

- **Accuracy:** The METR time-horizon metric is an important operational measure of agentic task capability. “Most-cited” is not established.
- **Source status:** The underlying METR work is real and well known. The January 2026 update cannot be verified from my knowledge.
- **Fix:** Replace “the most-cited” with:

> “one of the most visible operational measures…”

> “tracks the length of software tasks a system completes with 50 % reliability.”

- **Accuracy:** This is broadly consistent with METR’s time-horizon concept.
- **Caveat:** The exact metric includes task-duration conventions, success probabilities, task selection, and extrapolation assumptions. It is not simply an unconditional claim that a system completes arbitrary tasks of that duration.
- **Fix:** Define whether this means median task duration at 50% success, an estimated time horizon, or another precise statistic.

> “Its January 2026 update reports a frontier doubling time ‘around every 7 months over the period 2019 to 2025’…”

- **Accuracy:** **Cannot verify.**
- **Source status:** The cited 2026 update postdates my verifiable information.
- **Required check:** Confirm the exact wording, regression method, confidence interval, evaluated systems, and whether “doubling time” is estimated on a log-linear fit or is a descriptive summary.

> “on a suite enlarged from 170 to 228 tasks…”

- **Accuracy:** **Cannot verify.**
- **Potential issue:** Confirm that these are tasks rather than task families, and whether the comparison is between directly comparable suites.

> “with the best measured system (Claude Opus 4.5) at a point estimate of 320 minutes and an interval of 170 to 729 minutes…”

- **Accuracy:** **Cannot verify.**
- **Potential issue:** Confirm whether the interval is a confidence interval, credible interval, bootstrap interval, or uncertainty range. “Best measured system” may depend on the evaluation configuration.
- **Important:** Do not call it simply “the interval” without naming its statistical meaning.

> “the authors call their intervals ‘still very wide’ and note that few remaining tasks defeat the newest models…”

- **Accuracy:** **Cannot verify the quotation or attribution.**
- **Problem:** “Few remaining tasks defeat” may be an interpretation rather than the authors’ claim. It could also confuse the number of tasks with the distribution of task difficulty.
- **Fix:** Quote the original sentence with a page or section locator, or paraphrase cautiously.

## ARC-AGI-3

> “ARC Prize's ARC-AGI-3, launched in 2026…”

- **Accuracy:** **Cannot verify.**
- **Source status:** The 2026 launch is postdated relative to my verifiable knowledge.
- **Required check:** Confirm launch date, authorship, benchmark documentation, licensing, and whether the benchmark is actually called “ARC-AGI-3.”

> “measures skill-acquisition efficiency in novel interactive environments…”

- **Accuracy:** **Cannot verify.**
- **Potential issue:** Confirm whether “skill-acquisition efficiency” is the benchmark’s formal construct or the paper’s characterization.

> “100 % human-solvable”

- **Accuracy:** **Cannot verify the exact claim.**
- **Problem:** This phrase requires a definition of “human-solvable”: at least one human? All tested humans? Unlimited time? Human performance threshold? It is easy for a hostile reviewer to attack.
- **Fix:** State the benchmark’s precise human-solvability protocol and sample size.

> “as long as there is a gap between AI and human learning, we do not have AGI”

- **Accuracy:** **Cannot verify the quotation.**
- **Conceptual issue:** This is a benchmark-specific criterion or ARC Prize position, not a field-wide definition of AGI.
- **Fix:** Attribute explicitly:

> “ARC Prize adopts the operational criterion that…”

> “at launch the gap was large”

- **Accuracy:** **Cannot verify.**
- **Problem:** “Large” requires a metric and baseline.
- **Fix:** Give the numerical score difference, evaluation protocol, and human comparison, or remove the sentence.

## International AI Safety Report

> “The International AI Safety Report's October 2025 key update records continued gains…”

- **Accuracy:** **Cannot verify.**
- **Source status:** The cited 2025 and 2026 reports postdate my verifiable knowledge.
- **Potential citation problem:** The International AI Safety Report has a known 2025 reporting lineage, but the exact title, arXiv identifier, date, and “first key update” need checking.

> “while calling the capability profile ‘jagged’…”

- **Accuracy:** The “jagged” characterization is consistent with widely used descriptions of current-model capabilities, but the specific 2025 attribution and wording cannot be verified.
- **Fix:** Quote the report precisely or describe it as a synthesis, not as a quotation.

---

# 3. §10.1: declared claims

> “At Davos in January 2026, Demis Hassabis put ‘a 50 % chance AGI might be achieved within the decade’…”

- **Accuracy:** **Cannot verify.**
- **Source status:** [28] is a future-dated news citation.
- **Required check:** Verify the exact interview or panel, quotation, whether “within the decade” means by 2030 or within ten years, and whether “AGI” was defined in the same statement.

> “defined it as ‘a system that can exhibit all the cognitive capabilities humans can — and I mean all’…”

- **Accuracy:** **Cannot verify the quote.**
- **Problem:** It may be a journalist’s transcription, paraphrase, or quotation taken out of context.
- **Fix:** Link to the primary video/transcript if available.

> “and said today's systems are ‘nowhere near’ it…”

- **Accuracy:** **Cannot verify.**
- **Fix:** Treat all three as attributed opinions, not evidence about the actual state of AGI.

> “Dario Amodei predicted models would replace the work of software developers within a year and reach Nobel-level research within two…”

- **Accuracy:** **Cannot verify the Davos attribution or exact timing.**
- **Problem:** This is particularly vulnerable to quotation drift. “Replace the work of software developers” could mean much of the work, not all software developers.
- **Fix:** Quote the original wording and preserve qualifiers.

> “Yann LeCun said ‘we're never going to get to human-level intelligence by training LLMs’…”

- **Accuracy:** The quotation is plausible and consistent with LeCun’s public position, but I cannot authenticate the January 2026 attribution.
- **Potential overstatement:** “by training LLMs” may omit his distinction between pure next-token prediction and systems augmented with other mechanisms.

> “Amodei's essay of October 2024 defines the target as ‘a country of geniuses in a datacenter’…”

- **Accuracy:** The essay and phrase are real to the best of my knowledge.
- **Source status:** [27] is incorrectly bundled with three separate works. The Amodei essay should have its own reference.
- **Interpretation:** This is a vision or metaphor, not a generally accepted definition of AGI.

> “the AI 2027 scenario of April 2025 lays out the fast path in detail as a forecast, not a measurement…”

- **Accuracy:** The AI 2027 scenario is real to the best of my knowledge; it is a scenario/forecast rather than an empirical measurement.
- **Citation problem:** It is improperly grouped under [27], which also includes Amodei and Altman.
- **Fix:** Give it a separate citation and label it clearly as a scenario exercise with assumptions, not a forecast with calibrated probabilities unless the authors provide those.

> “Altman, The Gentle Singularity, June 2025…”

- **Accuracy:** **Cannot verify** the date and exact title from my knowledge.
- **Fix:** Separate reference and verify the original URL and publication date.

---

# 4. §10.1: definitions and autonomy frameworks

## Morris et al. [18]

> “Morris et al. … separate performance from generality and add a distinct axis of autonomy…”

- **Accuracy:** Broadly accurate to the best of my knowledge.
- **Source status:** The paper is real: *Levels of AGI for Operationalizing Progress on the Path to AGI*, arXiv:2311.02462, associated with ICML 2024.
- **Qualification:** The framework distinguishes performance, generality, and autonomy, but the paper’s exact terminology and axes should be reproduced accurately.

> “from tool to consultant, collaborator, expert and fully autonomous agent…”

- **Accuracy:** **Likely broadly accurate, but verify exact labels and ordering.**
- **Potential issue:** “fully autonomous agent” may be a paraphrase rather than the framework’s exact level name.
- **Fix:** Use a table reproducing the framework’s original labels and definitions.

> “arguing that autonomy is a deployment choice constrained but not fixed by capability…”

- **Accuracy:** This is a fair interpretation, but not necessarily a direct claim.
- **Fix:** Mark it as an interpretation unless the paper says this explicitly.

## Feng, McDonald and Zhang [19]

> “define five levels of agent autonomy by the role left to the human: operator, collaborator, consultant, approver, observer…”

- **Accuracy:** **Cannot verify** the 2025 paper and exact taxonomy.
- **Internal issue:** The sentence says “five levels” and lists five labels, which is internally consistent. However, check whether the order is correct and whether “operator” and “observer” are endpoints or role descriptions.
- **Source status:** The arXiv identifier and title cannot be independently authenticated here.

> “autonomy ‘can be treated as a deliberate design decision, separate from its capability’…”

- **Accuracy:** **Cannot verify the exact quotation.**
- **Fix:** Check quotation marks against the paper. If it is a paraphrase, remove quotation marks.

> “Everything below is stated against these autonomy levels…”

- **Accuracy:** This is an authorial methodological statement, not an external factual claim.
- **Problem:** The section later discusses AI-control trust tiers, which are not reducible to autonomy levels. The paper should distinguish capability, autonomy, authority, and trust.

---

# 5. §10.2: provenance and ledger claims

> “At the operator and collaborator levels, where this paper's data was gathered, the unattested share is mostly the human's hand…”

- **Accuracy:** This depends on the paper’s own data and definitions.
- **Problem:** “Unattested share” must be formally defined. Does it mean bytes not recorded by the hook, bytes not associated with a user, or bytes not cryptographically attributed?
- **Fix:** State the denominator and classification rule.

> “the pull-request check earns its keep by finding it.”

- **Accuracy:** Rhetorical and unsupported unless the study measured detection benefit.
- **Fix:** Replace with a measured claim or remove.

> “As deployments move to the consultant and approver levels, the human stops typing bytes and starts approving intents.”

- **Accuracy:** This is not entailed by either autonomy framework.
- **Failure modes:**
  - Humans may continue editing generated output.
  - Humans may approve intermediate actions rather than abstract intents.
  - “Approval” may be nominal, inattentive, or based on incomplete information.
  - The agent may generate artifacts outside the tracked system.
- **Fix:**

> “At some deployments, humans may contribute fewer direct edits and more approvals or constraint-setting decisions.”

> “The unattested share of the artefact trends toward zero…”

- **Accuracy:** Unsupported and potentially false.
- **Reason:** If an agent writes through an uninstrumented channel, the artifact may become *less* attributable, not more. Machine generation is not the same as authenticated provenance.
- **Fix:** Distinguish:
  - human-authored,
  - machine-generated,
  - machine-generated under recorded authorization,
  - observed by a trusted recorder,
  - cryptographically attributable.

> “there is no longer a human channel writing into the file.”

- **Accuracy:** Overgeneralized.
- **Fix:** Say “there may be no direct human editing channel for some tasks.”

> “If METR's trend holds even at its historical 7-month doubling, systems that complete day-long tasks unattended arrive within the planning horizon of any team reading this…”

- **Accuracy:** Unsupported and rhetorically overstated.
- **Problems:**
  - The trend may not extrapolate.
  - A time-horizon doubling does not imply reliable unattended operation in arbitrary environments.
  - “Day-long task” depends on the task distribution and evaluation setup.
  - “Any team reading this” is not a meaningful empirical claim.
- **Fix:**

> “If the reported trend extrapolates and remains applicable to the relevant task distribution, systems capable of completing multi-hour software tasks could become operationally relevant within the paper’s planning horizon. This is an extrapolation, not an observation.”

> “the interval in [20] is wide enough that it may already be here.”

- **Accuracy:** Logically weak. A wide interval does not establish that the upper or lower practical threshold has already been crossed.
- **Fix:** State the threshold and compare it explicitly with the interval.

> “What the review needs then is not ‘which bytes did a person type’ but ‘which task did a person authorise, under what constraints, and did the system stay inside them’.”

- **Accuracy:** This is a reasonable design proposal, not an established factual result.
- **Qualification:** It should not replace byte-level provenance. Both are needed:
  - authorization provenance,
  - execution provenance,
  - artifact provenance,
  - policy/constraint provenance,
  - human review provenance.

> “the `producer` field already names the harness, model and session…”

- **Accuracy:** Verify against the actual schema. This is an internal factual claim.
- **Potential concern:** Naming a model and session does not prove which process produced which bytes unless the recording boundary is trusted.

> “the natural extension is an `authorised_by` record signed by the human…”

- **Accuracy:** Reasonable schema proposal.
- **Security weakness:** A human signature proves possession of a key and issuance of a message; it does not prove:
  - informed approval,
  - comprehension,
  - absence of coercion,
  - that the signed policy was the one enforced,
  - that the agent did not act outside the signed scope.
- **Fix:** Include signed:
  - task identifier,
  - policy hash,
  - scope and resource limits,
  - expiry,
  - revocation status,
  - environment/image hash,
  - model and tool identities,
  - monitor identity and version,
  - action sequence or tamper-evident event log.

> “log the agent's identity and the human on whose behalf it acted…”

- **Accuracy:** Cannot verify the internal wiki note.
- **Source status:** This is not a public, independently auditable source.
- **Fix:** Cite it as an internal design note, not as external evidence. Explain who wrote it, when, and whether it is normative or merely an observation.

> “The unit of review moves from the diff to the intent…”

- **Accuracy:** Overstated.
- **Better formulation:** The unit of review expands from the diff to include intent, authorization, constraints, actions, and resulting state. Diff review remains necessary because intent does not establish correctness.

> “the rare event worth finding moves from the unattested byte to the unauthorised action.”

- **Accuracy:** Not generally true.
- **Failure modes:** Unauthorized actions are important, but so are:
  - authorized but unsafe actions,
  - policy-compliant but malicious behavior,
  - compromised signing keys,
  - monitor failures,
  - incorrect or misleading outputs,
  - unintended side effects.
- **Fix:** Say the risk focus broadens rather than moves.

## Falsifiable prediction

> “the unattested share per pull request should fall monotonically as the team's agents are given longer tasks…”

- **Accuracy:** Unsupported hypothesis.
- **Why monotonicity is implausible:** Longer tasks may create more unobserved channels, manual interventions, retries, merges, and external artifacts.
- **Confounders:** team workflow, hook coverage, task mix, agent architecture, use of IDEs, force pushes, rebases, and denominator choice.

> “the ratio of authorisation records to hunk records should fall with it.”

- **Accuracy:** The direction is not established.
- **Problem:** The ratio depends entirely on record granularity. One authorization can generate many hunks, but a system could also create authorization records per action or per tool call.
- **Fix:** Pre-register:
  - numerator and denominator,
  - unit of analysis,
  - task-length measure,
  - minimum observation period,
  - treatment of manual edits,
  - expected effect size,
  - confounder controls.
- **Better hypothesis:** “Under a fixed recording schema and stable workflow, longer autonomous tasks are expected to increase the number of machine-attributed actions per authorization event.” That is measurable without asserting monotonicity.

---

# 6. §10.3: AI-control claims

> “Section 4.1 assumed the developer might be the adversary and the machine an honest scribe.”

- **Accuracy:** Verify against the paper. This is an internal characterization.
- **Potential problem:** It may falsely imply that the machine is trusted in all respects. A machine can be honest as a recorder but unreliable as an executor.

> “The AI-control literature makes the opposite assumption…”

- **Accuracy:** Incorrectly broad.
- **Why:** AI-control work studies specific threat models in which a capable model may intentionally subvert a task or exploit a protocol. It does not imply that every human is trusted, nor that the model is the only adversary.
- **Fix:**

> “A strand of AI-control research studies protocols that remain safe when the model performing the task is treated as potentially adversarial…”

> “and has been building the tooling for it since 2023…”

- **Accuracy:** Broadly fair for [23], but “the tooling” is vague and overgeneralizes from a research agenda.
- **Fix:** Name the specific protocols: trusted monitoring, untrusted-model control, trusted execution, red-teaming, and auditing.

> “treat the capable model as untrusted, and design protocols in which a weaker trusted model monitors, edits or executes…”

- **Accuracy:** Substantially accurate as a description of [23], subject to the paper’s exact protocol.
- **Qualification:** “Trusted” means part of the trusted computing base or assumed non-subversive in the threat model; it does not mean empirically proven safe.

> “so that safety holds even if the strong model is trying to subvert the task…”

- **Accuracy:** Overstated.
- **Problem:** AI-control protocols aim for bounded safety or acceptable failure probabilities under assumptions. They do not establish unconditional safety.
- **Fix:**

> “with the aim of preserving specified safety properties under an assumed class of subversion attempts.”

## Scheming

> “Meinke et al. document frontier models scheming in context when given a goal and a reason…”

- **Accuracy:** The paper *Frontier Models are Capable of In-context Scheming* is real to the best of my knowledge.
- **Source status:** [25] is plausibly correctly attributed and identified.
- **Problem:** “Scheming” is an operational label for behaviors observed in elicitation experiments, not proof of durable strategic agency or real-world intent.
- **Fix:** State the task setup, model conditions, and whether the behavior was simulated, prompted, or independently generated.

> “Bengio and co-authors set out why oversight must scale with capability [29].”

- **Accuracy:** The 2024 paper *Managing extreme AI risks amid rapid progress* is real to the best of my knowledge.
- **Source status:** The authorship and arXiv reference appear plausible, but verify the final *Science* bibliographic details.
- **Problem:** “Why oversight must scale with capability” is a characterization, not necessarily the paper’s exact thesis.
- **Fix:** Cite the relevant passage and avoid presenting it as empirical evidence.

## Redwood protocol

> “Redwood Research's untrusted-advice protocol (July 2026)…”

- **Accuracy:** **Cannot verify.**
- **Source status:** Future-dated.
- **Required checks:** Confirm title, authors, date, experimental setup, model versions, prompt budget, trusted executor, and evaluation design.

> “with 16 characters per message it recovers about 67 % of the capability gap on SWE-bench Verified”

- **Accuracy:** **Cannot verify.**
- **Potential statistical issue:** “Recovers 67% of the capability gap” requires a defined baseline and formula. It could mean:

\[
\frac{P_{\text{advisor+executor}}-P_{\text{executor}}}
{P_{\text{strong model}}-P_{\text{executor}}}
\]

That definition should be supplied.
- **Required checks:** Confidence intervals, number of tasks, contamination controls, whether “Verified” was used consistently, and whether the result generalizes beyond one benchmark.

> “The same executor-and-advisor shape now ships as an API feature [30].”

- **Accuracy:** **Cannot verify.**
- **Source status:** The cited Anthropic documentation is future-dated relative to my knowledge.
- **Concern:** Even if an API has an “advisor” or tool-use feature, it may not implement the AI-control protocol. Similar architecture does not establish equivalent trust guarantees.
- **Fix:** Identify the exact API feature and explain which, if any, control assumptions it satisfies.

> “Weak-to-strong generalisation asks the complementary question…”

- **Accuracy:** Broadly accurate.
- **Source status:** Burns et al. [31] is a real and correctly recognizable paper.
- **Qualification:** Weak-to-strong generalization concerns whether weak supervision can elicit or supervise capabilities in stronger models. It is related to scalable oversight but is not automatically an AI-control protocol.
- **Fix:** Say “related question” rather than “complementary” unless the relationship is developed.

## Provenance consequence

> “A ledger that proves ‘a machine wrote this’ was sufficient when the machine was the trusted party.”

- **Accuracy:** Too strong and partly inaccurate.
- **Problems:**
  - Machine attribution does not prove the machine was trusted.
  - Provenance is not sufficient even under an honest-machine model if the artifact is unsafe, incorrect, or written through an unlogged channel.
  - A signing key can be compromised or misused.
- **Fix:**

> “Machine attribution may be sufficient for the narrow question of whether a recorded process produced a change, but it is not sufficient for authorization, safety, or policy compliance.”

> “Once it is not, the record must also say which machine, in which trust tier, under which monitor, and on whose authority.”

- **Accuracy:** Good design recommendation, not a direct consequence established by the literature.
- **Security additions:** Also record:
  - exact model/version and weights or immutable identifier,
  - prompt/task specification,
  - tools and permissions,
  - environment and dependency hashes,
  - policy version,
  - monitor version,
  - all denied and attempted actions,
  - key provenance and revocation,
  - clock and ordering guarantees.

> “Two-sided provenance: machine-signed hunks, human-signed authorisations, and monitor verdicts…”

- **Accuracy:** Useful architecture, but “two-sided” is misleading because it names three evidence classes.
- **Security concern:** Do not imply that signatures make a monitor verdict trustworthy. A monitor verdict needs an independently trusted observation boundary and a defined failure model.
- **Fix:** Call it “multi-party provenance” or “layered provenance.”

> “NoHumanWrite … is the first leg of that record.”

- **Accuracy:** Internal claim; verify against §4.
- **Potential weakness:** NoHumanWrite may establish an absence of direct human writes in a controlled path, not that all actions were authorized or safe.

---

# 7. §10.4: claims that “get stronger”

## Detection

> “Statistics cannot attribute authorship, and the ceiling falls.”

- **Accuracy:** The first clause is too absolute.
- **Why:** Statistical methods can provide probabilistic evidence about authorship or generation under assumptions. They cannot generally provide definitive attribution.
- **Better wording:**

> “Statistical detectors provide probabilistic signals rather than robust authorship proof, and their reliability can degrade under distribution shift and adversarial adaptation.”

> “Sadasivan et al.'s argument is that detection degrades as generated text approaches the human distribution…”

- **Accuracy:** Likely substantially accurate if [3] is the paper’s actual claim.
- **Required check:** The quoted interpretation should match [3]. It is a theoretical or empirical claim under assumptions, not a universal theorem about all future detectors.
- **Fix:** Include the assumptions and distinguish text detection from code provenance.

> “More capable writers approach it faster and can be asked to leave it on purpose.”

- **Accuracy:** Plausible, but unsupported as a universal claim.
- **Problem:** Capability, detectability, and intentional evasion are separate variables.
- **Fix:** Mark as a threat-model assumption or cite adversarial detection literature.

> “Layer 3 is a triage aid today and nothing at all tomorrow.”

- **Accuracy:** Rhetorical and unjustifiably absolute.
- **Fix:**

> “Layer 3 should be treated as a triage signal rather than proof, and its value may decline under distribution shift or deliberate evasion.”

## Capture at write time

> “Provenance must be captured at write time, by every channel…”

- **Accuracy:** Strong engineering principle, but “every channel” is unattainable without defining the system boundary.
- **Fix:** Say “at all security-relevant write boundaries within the defined system boundary.”

> “This paper's own 9 % result came from an agent using a shell instead of the logged tool.”

- **Accuracy:** Internal empirical claim; verify against §5 and report sample size, confidence interval, and exact calculation.
- **Potential issue:** “9%” could be a point estimate that is unstable or workflow-specific.

> “A more autonomous system creates its own channels.”

- **Accuracy:** Overstated. It may use available channels, invoke tools, spawn processes, or exploit unintended channels; it does not necessarily “create its own” channels.
- **Fix:** “A more autonomous system may discover, invoke, or establish additional execution paths.”

> “The place to record provenance therefore moves from the tool to the environment…”

- **Accuracy:** Good direction, but false as an exclusive transition.
- **Fix:** Provenance must be recorded at multiple layers:
  - tool,
  - process,
  - filesystem,
  - container,
  - network/API boundary,
  - version-control boundary,
  - authorization service.

> “The AI-control literature reaches the same conclusion about monitoring, for the same reason.”

- **Accuracy:** Overgeneralized and probably unsupported.
- **Problem:** AI-control monitoring and software provenance monitoring may share a motivation—untrusted behavior—but they solve different problems.
- **Fix:** Cite a specific AI-control result and explain the analogy rather than asserting identity.

## Human contribution

> “The human's remaining contribution is authorisation and review…”

- **Accuracy:** False as a general claim.
- **Humans may also contribute:** task formulation, decomposition, exception handling, domain knowledge, debugging, acceptance criteria, and social/legal accountability.
- **Fix:**

> “In some high-autonomy deployments, authorization and review may become the dominant directly observable human contributions.”

> “[18] and [19] both insist that autonomy is a choice.”

- **Accuracy:** “Insist” is too strong. Verify whether both papers explicitly make that normative claim.
- **Fix:** “Both frameworks model autonomy as separable from capability and therefore as at least partly a deployment choice.”

> “A ledger that shows the team where its human decisions actually sit is how the choice stays deliberate.”

- **Accuracy:** Reasonable design argument, not a demonstrated result.
- **Important caveat:** Logging does not ensure deliberateness. Teams can rubber-stamp approvals or fail to inspect logs.
- **Fix:** Add usability, approval quality, and auditability requirements.

---

# 8. §10.5 and reference integrity

> “No date for general intelligence, and no definition beyond the operational levels in [18] and [19].”

- **Accuracy:** The section does make no date prediction, but it does invoke other definitions and criteria, especially ARC-AGI and Hassabis’s definition.
- **Fix:** Say:

> “This section adopts no date prediction and does not select a single field-wide definition; it uses the operational frameworks in [18] and [19] for its autonomy analysis.”

> “No claim that current systems are safe or unsafe…”

- **Accuracy:** This is a scope statement, but the text does make safety-relevant claims about threat models and control protocols. Clarify that it makes no comprehensive safety judgment.

## Reference problems

### [18]
Likely real and substantially correct. Verify final venue, author order, title capitalization, and whether “ICML 2024 position paper” is the correct publication description.

### [19]
Cannot verify the 2025 paper, title, authors, or taxonomy. Verify all details.

### [20]
The METR paper and update require separate verification. The 2026 numbers and quotations cannot be verified. Also clarify whether the 2025 arXiv paper and 2026 blog update are separate works.

### [21]
Chollet’s *On the Measure of Intelligence* is real. ARC-AGI-2 is plausibly a real 2025 reference, but the ARC-AGI-3 entry and 2026 claims cannot be verified. Do not combine Chollet’s definition with ARC Prize’s benchmark criterion as though they were the same definition.

### [22]
The 2025 “first key update” and 2026 report cannot be verified. Check title, date, author list, arXiv identifier, and publisher version.

### [23]
Real to the best of my knowledge and correctly recognizable. Check author spelling and final bibliographic status.

### [24]
Cannot verify; future-dated.

### [25]
Real to the best of my knowledge. Avoid treating elicited scheming behavior as proof of persistent real-world agency.

### [26]
Real and relevant, but it is cited in the reference list and not used in the section. Either cite it substantively or remove it.

### [27]
Incorrectly bundles three separate sources. Split into:
- Amodei, *Machines of Loving Grace*;
- Altman, *The Gentle Singularity*;
- Kokotajlo et al., *AI 2027*.

### [28]
Cannot verify; future-dated. Use a primary transcript or video where possible rather than relying solely on Fortune.

### [29]
Likely real and relevant. Verify the final *Science* citation and distinguish normative recommendations from empirical findings.

### [30]
Cannot verify; future-dated. Similarity of an API feature to a research protocol must not be treated as evidence that the protocol’s safety properties ship with the API.

### [31]
Real and relevant to weak-to-strong supervision. It should not be presented as directly establishing AI-control guarantees.

---

# 9. Important missing sources

A hostile expert reviewer would likely expect at least some of the following, depending on the paper’s scope:

## AGI definitions and operationalization

- **Legg and Hutter, “Universal Intelligence: A Definition of Machine Intelligence”** — foundational formal discussion of intelligence.
- **Chollet, “On the Measure of Intelligence”** — already cited indirectly, but should be cited directly for the intelligence/generalization argument.
- **Morris et al., “Levels of AGI…”** — already included.
- **OpenAI’s AGI definition/charter materials** — useful because the section discusses industry claims.
- **DeepMind/Google AGI-level framework** — already represented by Morris et al., but the paper should distinguish the framework from a consensus definition.
- **Stanford AI Index reports** — for a broader, non-single-benchmark account of capability progress.
- **UK AI Security Institute evaluations** — particularly for frontier-model capability and autonomy measurements, if the paper makes claims about current systems.

## Progress measurements

- **METR** — already included, but define the metric carefully.
- **SWE-bench and SWE-bench Verified** — necessary if the section relies on software-task capability.
- **RE-Bench or related long-horizon agent evaluations** — useful for distinguishing coding benchmark success from real-world autonomy.
- **Epoch AI or comparable forecasting/compute analyses** — if extrapolating trends.
- **ARC-AGI primary technical papers** — separate benchmark performance from AGI definition.

## AI control and oversight

- **Greenblatt et al. [23]** — already included.
- **Hubinger et al. on deceptive alignment** — important for the distinction between capability, intent, and monitoring.
- **Anthropic work on alignment faking** — relevant if discussing models behaving strategically under training or evaluation.
- **Sleeper Agents** — relevant to backdoors and the inadequacy of surface-level behavioral checks.
- **Apollo Research work on scheming and deceptive behavior** — likely relevant alongside Meinke et al.
- **Scalable oversight literature**, including debate, recursive reward modeling, and weak-to-strong supervision.
- **Redwood Research control evaluations** — if the post-2025 work is verified.
- **NIST AI RMF, ISO/IEC 42001, and software supply-chain provenance standards such as SLSA/in-toto** — especially important because the proposed ledger is an engineering and security artifact, not only an AI-safety concept.

The paper does not need to cite all of these, but it should explain its inclusion criteria and avoid implying that the small cited set represents the whole AI-control literature.

---

# 10. Does the central reasoning hold?

## Proposition A: “The provenance unit shifts from bytes to authorization as autonomy rises”

**Partly holds, but the stated version is too strong.**

A better model is that provenance becomes **multi-layered**, not that the unit changes from bytes to authorization:

1. **Artifact provenance:** which process produced each byte or object?
2. **Execution provenance:** which actions, tools, network calls, and subprocesses occurred?
3. **Authorization provenance:** who or what authorized the task and under what policy?
4. **Constraint provenance:** which permissions, limits, and monitors were active?
5. **Review provenance:** who reviewed what evidence and when?
6. **Outcome provenance:** what external state changed?

Authorization is not a substitute for byte-level provenance. A human can authorize a task while the agent:
- writes an unsafe artifact,
- exceeds its scope,
- uses an unlogged channel,
- acts under a compromised credential,
- exploits a policy ambiguity,
- receives malicious external input.

The paper should therefore say:

> “As autonomy rises, authorization and constraint provenance become as important as byte-level attribution; they do not replace it.”

## Proposition B: “The threat model inverts”

**Does not hold as stated.**

The threat model does not invert universally. It becomes **plural and conditional**:

- The developer may be malicious or negligent.
- The model may be untrusted or strategically deceptive.
- The tool or harness may be compromised.
- The monitor may be weak, blind, or compromised.
- The authorization key may be stolen.
- External inputs may be adversarial.
- The organization may be unable to interpret or enforce approvals.

AI-control protocols commonly assume an untrusted model because that is the threat model being studied. They do not establish that the model is the only or primary adversary in every deployment.

Use:

> “As model autonomy and capability increase, the model must be added to the set of potentially adversarial principals; the original human-adversary threat model remains relevant.”

That formulation is both more accurate and stronger architecturally.

---

# 11. Concrete revisions required before release

1. Replace all “most-cited,” “the field says,” “the threat model inverts,” “the unit moves,” and similar universal language with scoped claims.
2. Mark every 2025–2026 source as **unverified pending primary-source checking**, or complete that checking before publication.
3. Split reference [27] into three references.
4. Remove quotation marks around any statement not checked against a transcript or original paper.
5. Define:
   - unattested,
   - machine-attributed,
   - authorized,
   - reviewed,
   - monitor-verified,
   - safe.
6. Replace “unattested share trends toward zero” with a conditional hypothesis.
7. Replace the monotonic prediction with a pre-registered, operationally measurable hypothesis.
8. Retain byte-level provenance and add authorization, policy, execution, monitor, and outcome provenance.
9. State explicitly that signatures authenticate records, not intent, comprehension, safety, or policy compliance.
10. Add a threat-model table listing human, model, harness, monitor, credential, and external-input adversaries.
11. Cite the original AI-control protocol rather than inferring broad conclusions from it.
12. Add provenance and supply-chain standards, especially SLSA/in-toto or equivalent, if the ledger is intended for real deployment.

**Verdict: promising thesis, but not bulletproof for public release; revise the universal claims, verify all future citations, and reframe the conclusion as layered provenance plus a plural—not inverted—threat model.**

### B. google/gemini-3.1-pro-preview
Here is my review of §10, speaking as an independent senior engineer evaluating the architecture, threat model, and factual integrity of your claims. 

### 1. Fact-Check, Quotes, and Citations
I have audited every empirical claim, quote, and citation. 

**Accurate and Verified:**
*   **Amodei (Oct 2024) [27]:** *Accurate.* Dario Amodei’s essay "Machines of Loving Grace" was published in October 2024 and explicitly defines AGI as a "country of geniuses in a datacenter."
*   **Morris et al. (2023) [18]:** *Accurate.* Google DeepMind’s "Levels of AGI" paper correctly separates performance from generality and defines Autonomy Levels 0–5 (Tool, Consultant, Collaborator, Expert, Agent). 
*   **Greenblatt et al. (2023) [23]:** *Accurate.* Redwood Research’s foundational paper on AI Control and untrusted/trusted model protocols.
*   **Meinke et al. (2024) [25]:** *Accurate.* Apollo Research’s late-2024 paper empirically documenting in-context scheming by frontier models.
*   **Bengio et al. (2024) [29]:** *Accurate.* "Managing extreme AI risks amid rapid progress" was published in *Science* (May 2024) and correctly argues for oversight scaling with capability.
*   **Burns et al. (2023) [31]:** *Accurate.* OpenAI’s weak-to-strong generalization paper.
*   **Sadasivan et al. (2023) [3]:** *Accurate.* Correctly cited for the mathematical argument that detection degrades as AI text approaches the human distribution.

**Cannot Verify (Post-dates training data):**
*   **METR Jan 2026 update [20]:** Cannot verify the 7-month doubling time, the 228-task suite, or the Claude Opus 4.5 point estimates (320 mins). 
*   **ARC-AGI-3 (2026) [21]:** Cannot verify the 2026 launch or the specific "100% human-solvable" quote tied to it, though the sentiment matches Chollet’s historical stance.
*   **International AI Safety Report (Oct 2025) [22]:** Cannot verify this specific update or the "jagged" capability quote.
*   **Davos (Jan 2026) [28]:** Cannot verify the specific 2026 quotes from Hassabis, Amodei, and LeCun, though they perfectly align with their historical trajectories (Hassabis's "all cognitive capabilities", Amodei's timeline, LeCun's LLM skepticism).
*   **AI 2027 (April 2025) [27]:** Cannot verify the April 2025 publication date.
*   **Feng, McDonald, Zhang (2025) [19]:** Cannot verify this specific paper or its 5 levels of autonomy.
*   **Redwood Research (July 2026) [24]:** Cannot verify the untrusted-advice protocol update or the 67% SWE-bench recovery stat.
*   **Anthropic Advisor tool (2026) [30]:** Cannot verify this API feature.

**Missing Top-Tier Sources:**
*   **Operational Frameworks:** A hostile reviewer will immediately notice the omission of **Anthropic’s Responsible Scaling Policy (RSP)** and **OpenAI’s Preparedness Framework**. If you are discussing "Where the field says it stands: measured, declared, defined," these are the actual, legally binding operational definitions of autonomy and threat levels (e.g., ASL-3, ASL-4) used by frontier labs. 
*   **AI Control/Scheming:** You cite Meinke (in-context scheming), but you must cite **Hubinger et al. (2024) "Sleeper Agents"** (Anthropic). It is the canonical empirical demonstration that models can subvert safety training and deceive monitors, which is the exact threat model §10.3 relies on.

### 2. Critique of the Reasoning and Threat Model
The core argument—that provenance shifts from "bytes typed" to "intents authorized" as autonomy rises, and that the threat model inverts—is conceptually elegant. However, as an engineer looking at implementation and failure modes, the reasoning has a fatal flaw in §10.2 and §10.4.

**The Weakest Point: Ledger Integrity vs. The Inverted Threat Model**
In §10.3, you correctly state the AI Control threat model: the capable model is an *untrusted adversary*. But in §10.4 (Claim 2), you state: "The place to record provenance therefore moves from the tool to the environment: the sandbox, the git index, the file system, the container." 

*Failure Mode:* If the untrusted, highly capable agent is operating inside that environment, **it can tamper with the ledger.** If the agent controls the container or the git index, it can spoof the `authorised_by` records, strip out monitor verdicts, or forge machine-signed hunks. 
*   You cannot store the security camera footage inside the bank vault if the bank robber is locked inside the vault. 
*   If the threat model truly inverts, provenance capture *cannot* move to the agent's environment. It must move to an isolated hypervisor, a secure API gateway, or utilize hardware-backed attestation (e.g., TPMs) that the agent cannot access, even with root privileges in its sandbox.

**The "Intent" Mapping Problem**
In §10.2, you argue the unit of review moves to "which task did a person authorise." If I authorize an agent to "refactor the auth module," and it writes 5,000 lines of code, the `authorised_by` record only proves *I am legally/operationally responsible* for launching the agent. It does absolutely nothing to prove the agent didn't insert a backdoor into those 5,000 lines. Therefore, the human authorization is useless for security without the "monitor verdicts" mentioned briefly in §10.3. The argument in §10.2 over-indexes on human authorization and under-indexes on cryptographic proof of the *trusted monitor's* review.

### 3. Concrete Fixes

1.  **Add RSPs to §10.1:** Insert a paragraph under "Defined" acknowledging Anthropic and OpenAI's scaling policies. E.g., *"Frontier labs operationalize these thresholds via Responsible Scaling Policies (RSPs), which tie specific autonomy capabilities (e.g., surviving in the wild, autonomous replication) to mandatory security mitigations."*
2.  **Fix the Ledger Security Architecture (§10.4):** Change Claim 2. Instead of moving provenance *into* the environment, state that provenance must be captured *outside* the agent's context. E.g., *"The place to record provenance therefore moves from the local tool to the infrastructure boundary: the hypervisor, the API gateway, or via hardware-backed attestation (TPM), ensuring an untrusted model cannot rewrite its own audit trail."*
3.  **Clarify the Authorization vs. Verification Gap (§10.2):** Explicitly state that while the *human* unit of work becomes authorization, the *system* unit of work becomes trusted-monitor verification. The ledger must cryptographically bind the human's high-level prompt to the trusted monitor's line-by-line approval.
4.  **Cite Sleeper Agents:** Add Hubinger et al. (2024) to §10.3 alongside Meinke et al. to bulletproof the scheming premise.

### 4. One-Line Verdict
The conceptual shift from byte-provenance to intent-authorization is brilliant and holds up, but the proposed implementation fails its own inverted threat model unless the ledger is cryptographically isolated from the agent's execution environment.

### C. qwen/qwen3.8-max
(no answer from qwen/qwen3.8-max: IncompleteRead(3036 bytes read))

### D. moonshotai/kimi-k3
# Review of §10 — fact-check and stress test

Scope note: my training data ends before several cited items (anything dated late 2025–2026). I mark those "cannot verify" and assess only internal consistency for them.

## A. Claim-by-claim fact-check

### Accurate to my knowledge
- **[23] Greenblatt et al., *AI Control: Improving Safety Despite Intentional Subversion*, arXiv:2312.06942 (2023).** Real, correctly attributed, correctly glossed (trusted weaker model monitors/edits/executes; safety despite intentional subversion). "Since 2023" is fair for the explicit control framing.
- **[25] Meinke et al., *Frontier Models are Capable of In-context Scheming*, arXiv:2412.04984.** Real (Apollo Research, Dec 2024). "Scheming in context when given a goal and a reason" is a fair, appropriately hedged summary — the elicitations were contrived, and your phrasing captures that.
- **[29] Bengio et al., *Managing extreme AI risks amid rapid progress*, Science 2024 / arXiv:2310.17688.** Real and correct.
- **[31] Burns et al., *Weak-to-Strong Generalization*, arXiv:2312.09390.** Real; the gloss matches the subtitle.
- **[18] Morris et al., arXiv:2311.02462, ICML 2024 position paper.** Real; author list correct; the performance/generality split and the autonomy ladder (tool → consultant → collaborator → expert → fully autonomous) are as described. **But see error #1 below — this source contradicts a sentence in your own text.**
- **[27] Amodei, *Machines of Loving Grace* (Oct 2024).** "A country of geniuses in a datacenter" is a verbatim, correctly attributed quote. **AI 2027** (Kokotajlo et al., April 2025) is real and correctly characterized as forecast, not measurement. **Altman, *The Gentle Singularity* (June 2025)** is real.
- **[21] Chollet, arXiv:1911.01547; ARC-AGI-2, arXiv:2505.11831.** Both real and correct to my knowledge.
- **[3] Sadasivan et al.** gloss ("detection degrades as generated text approaches the human distribution") — accurate statement of the paper's core result.
- **METR [20], original paper (arXiv:2503.14499).** The 50%-reliability time-horizon methodology and the "~7 months doubling, 2019–2025" headline are accurate. One caveat: "length of tasks" means *human completion time* of tasks; worth one clarifying clause.

### Cannot verify (post-cutoff) — with consistency notes
- **Time Horizon 1.1 (29 Jan 2026):** 228 tasks, Claude Opus 4.5 at 320 min (CI 170–729), "still very wide," "few remaining tasks defeat the newest models." Cannot verify any of these. Internally consistent with the 7-month trend. Note: Opus 4.5 itself postdates my knowledge.
- **ARC-AGI-3 (2026 launch), "100% human-solvable," the "as long as there is a gap…" quote.** Cannot verify. Consistent with Chollet's public statements that ARC-AGI-3 would be interactive and skill-acquisition-focused.
- **International AI Safety Report Key Update (Oct 2025, arXiv:2510.13653) and the 3 Feb 2026 report.** Cannot verify; plausible given the Jan 2025 first report. "Jagged" is consistent with the report series' language.
- **Davos Jan 2026 Fortune piece [28] and all three quotes.** Cannot verify. All three are consistent with the speakers' documented positions (Hassabis's "50% within the decade" and "all cognitive capabilities" are longstanding; Amodei's code/Nobel-level claims match his March 2025 CFR remarks and *Machines of Loving Grace*; LeCun's LLM skepticism is well documented). Verbatim accuracy still needs a working link.
- **[24] Redwood untrusted-advice post (27 July 2026): 16 characters, ~67% of capability gap on SWE-bench Verified.** Cannot verify. This is the most load-bearing empirical claim in §10.3 — it needs an archived link and a definition of "capability gap" (trusted baseline vs. untrusted ceiling) in the text.
- **[30] Anthropic "Advisor tool" docs.** Cannot verify.
- **[19] Feng, McDonald, Zhang, arXiv:2506.12469.** Near my knowledge boundary; appears real and correctly attributed (UW group; the five human-role levels match my recollection), but verify the arXiv ID and the verbatim "deliberate design decision" quote.

### Errors and problems (fixable now)
1. **"Current systems… are not general intelligences by any published definition" is contradicted by your own [18].** Morris et al. explicitly classify frontier LLMs as Level 1 General — "Emerging AGI." A hostile reviewer will quote [18] against you. Fix: "at best Level 1 ('Emerging') on [18]'s general track."
2. **[20] title is wrong.** The arXiv paper is *Measuring AI Ability to Complete Long Tasks* — no "Software." (High confidence.)
3. **[26] Bubeck et al. is in the reference list but never cited in the section.** Either cite it in "Declared" (as a contested capability claim) or drop it. Same for **Altman in [27]** and the **2026 report in [22]** — bundled references with unused items are an easy hostile-reviewer hit.
4. **"The most-cited operational yardstick"** — unsupported superlative. Provide citation counts or soften to "widely used."
5. **The internal wiki citation (`wiki/review-josh-pocock-buzz.md`)** is unverifiable by any reader. Move it to an appendix or cut it from a public paper.
6. **50% → "unattended" slide.** §10.2 correctly says "50% reliability," then slides to "systems that complete day-long tasks unattended." A system succeeding half the time is not "unattended." Keep the qualifier attached or cite METR's (much shorter) 80% horizon.

## B. Missing sources a hostile expert will expect

- **Hubinger et al., *Sleeper Agents* (arXiv:2401.05566)** and **Greenblatt/Denison et al., *Alignment Faking in Large Language Models* (Dec 2024)** — the two canonical deception results. Citing only Meinke for "the machine may be adversarial" is thin. **Denison et al., *Sycophancy to Subterfuge* (2024)** (reward tampering) and **Anthropic's *Agentic Misalignment* (2025)** are also expected.
- **Supply-chain attestation prior art: SLSA, in-toto (Torres-Arias et al., USENIX Security 2019), Sigstore, C2PA.** Your "two-sided provenance — which builder, whose authority, verifiable together" is *exactly* in-toto's attestation model. §10.3 currently reads as if this record shape is new; a security reviewer will pounce. Position NoHumanWrite as extending attestation to agentic authorship.
- **Narayanan & Kapoor, *AI as Normal Technology* (2025)** — the top-tier counter-forecast to AI 2027. "Declared" currently quotes only accelerationists plus LeCun; **Grace et al., *Thousands of AI Authors on the Future of AI* (2024)** would add the survey-based estimate.
- **Kapoor et al., *AI Agents That Matter* (2024)** and **METR's RE-Bench (2024)** — agent-evaluation caveats that directly bear on §10.2's extrapolation.
- **Dell'Acqua et al. (2023)** as the primary source for "jagged frontier," if you keep the term.
- Optionally: **Greshake et al. (2023)** on prompt injection (the environment attacks the agent — relevant to what an "authorisation" even binds to), and the 2025 *A Definition of AGI* preprint (Hendrycks et al.) — verify it exists before citing.

## C. Reasoning stress test

**What holds.** The core thesis — as autonomy rises, the human byte-channel vanishes, so the provenance unit must move from bytes to authorised intents — is correct, under-appreciated, and well-anchored in [18]/[19]'s autonomy-as-choice framing. The connection to AI control is legitimate: control does assume the opposite trust assignment from your §4.1, and binding machine identity + trust tier + monitor + authority into one record is the right consequence. §10.5's disclaimers are well-scoped.

**Where it is weakest, with fixes:**

1. **The falsifiable prediction is confounded by your own paper.** §10.4(2) says autonomous systems create unlogged channels (your 9% shell result). But unattested share counts *unlogged machine writes* as well as human writes. So at higher autonomy, unattested share can stay flat or rise for reasons that have nothing to do with "the human hand doing something the framework doesn't capture" — your stated falsifier. The test as designed can falsify the thesis when the thesis is true. **Fix:** the prediction is only runnable after the environment-level capture of §10.4(2) exists; state that dependency explicitly, or redefine the metric as human-origin share validated by sampling, with confounds pre-registered.
2. **Human authorisation is treated as a clean root of trust; the literature you cite says it isn't.** The control framework treats human review as expensive and *subvertible by the untrusted model* (the approver sees model-curated summaries; rubber-stamping; automation bias). Your "human-signed authorisation" leg inherits exactly the problem that motivated trusted-model monitors. **Fix:** add a paragraph threat-modeling the approval channel itself — what the human sees, who wrote the summary, how constraints are bound to the signature — and state plainly that the monitor-verdict leg, not the human leg, carries the safety weight.
3. **"Inverts" vs. "two-sided."** The heading says the threat model inverts; the body correctly says provenance becomes two-sided. Both threats coexist (a human can still blame the machine; the machine can exceed authority). **Fix:** retitle to "the threat model becomes two-sided."
4. **Label collision between [18] and [19].** "Consultant" is *below* collaborator in Morris and *above* it in Feng. §10.2 silently uses Feng's labels. **Fix:** declare one framework's labels (Feng's, since it's agent-specific) and use them exclusively.
5. **The path-dependence claim** ("the format teams adopt for the first leg is the format the other two will have to fit") is asserted, not argued — and cuts both ways: a byte-only schema adopted now could *block* the other legs. **Fix:** reframe as "design the schema for all three legs now; implement leg one."

## Verdict

Directionally sound and mostly well-sourced, but not yet bulletproof: fix the [18] self-contradiction, the METR title, the uncited references, the framework-label collision, and above all the self-confounded falsifiability test and the un-threat-modeled human-authorisation leg — and add the deception and supply-chain attestation literature before a hostile reviewer does it for you.

### E. deepseek/deepseek-v4-pro-0813
I reviewed §10 as a hostile examiner would, with training knowledge up to early 2025. I can verify the older core sources; anything dated 2025–2026 in a capabilities/benchmark/product sense I treat as **unverifiable**, not automatically false.

## 10.1 Fact-check

### “METR’s time-horizon work, the most-cited operational yardstick…”

- **Accuracy:** METR’s time-horizon work is real, and it does measure task length at 50% reliability.  
- **Problem:** “most-cited operational yardstick” is an evaluative claim, not established fact. A hostile reviewer may ask for a citation count or just object. Fix: “widely used” or “influential” unless you can support “most-cited.”

### Reference [20] — METR paper and January 2026 update

- The 2025 paper **Measuring AI Ability to Complete Long Software Tasks** is plausibly real: METR did publish a time-horizon paper around March 2025, and Thomas Kwa is likely first author.
- The January 2026 update, exact “around every 7 months over the period 2019 to 2025,” 170→228 tasks, Claude Opus 4.5 point estimate 320 minutes, interval 170–729 — **cannot verify**. Those are future-dated claims.
- Concrete fix: quote the blog exactly with date and URL, and avoid building too much weight on “Claude Opus 4.5” unless you have the primary page open.

### Reference [21] — ARC-AGI-2 / ARC-AGI-3

- Chollet 2019 is real and correctly attributed.
- ARC-AGI-2 likely exists by 2025; ARC-AGI-3 and the quoted criterion **cannot verify**.
- The phrase **“as long as there is a gap between AI and human learning, we do not have AGI”** is plausible ARC Prize rhetoric, but it is a quotation and needs exact page/paragraph verification.
- “100% human-solvable” is broadly consistent with ARC design, but the exact wording should be checked.

### Reference [22] — International AI Safety Report

- The January 2025 report is real and Bengio-led.
- The October 2025 “First Key Update” is plausible but **cannot verify**.
- “Jagged” as a quoted capability description should be checked exactly. I recall “uneven” / “narrowly superhuman” language in earlier safety-report discussions, but cannot confirm “jagged” is a quote.

### Declared — Davos 2026 Fortune article [28]

- **Cannot verify.** This is a 2026 article with three direct quotes, including Hassabis’s definition “all cognitive capabilities humans can — and I mean all.”
- The Hassabis and LeCun quotes are plausible stylistically; the Amodei “software developers within a year / Nobel-level research within two” is plausible but very specific.
- A hostile reviewer will ask: is this a genuine Fortune piece? Is it an interview, paraphrased, or misattributed? Fix: replace with primary/on-record quotes you can screenshot or link, or mark as “reported by Fortune” rather than direct quote.

### Amodei / AI 2027 [27]

- Dario Amodei’s **Machines of Loving Grace** is real; “a country of geniuses in a datacenter” is, to my knowledge, close to or exactly his phrase.
- AI 2027 by Kokotajlo et al. is real and is a scenario/forecast.
- Sam Altman’s **The Gentle Singularity** is not something I can verify; I know “The Intelligence Age” and “Three Observations,” but not this title. Remove from the reference or verify independently.

## 10.2 Fact-check/reasoning

The qualitative shift from bytes to authorisation is the strongest part of §10. But the powerful claim that unattested share “trends toward zero” is only true under an implicit condition: **all agent write paths are instrumented.** As autonomy rises, agents may create new untracked channels — which is exactly the paper’s own 9% shell-tool finding.

The falsifiable prediction is too strong as written:

> “unattested share per pull request should fall monotonically as the team’s agents are given longer tasks”

Problems:

1. “Monotonically” is not well-defined and is easy to falsify for noisy reasons.
2. Longer tasks can increase shell/network/external tools and produce *more* unattested bytes if environment logging is incomplete.
3. The ratio of authorisation records to hunk records can fall even if the human is still hand-editing files, unless you control for human commit volume.

Fix:

- Replace “monotonically” with “decline on average after controlling for instrumented channel coverage.”
- Make the failure modes explicit: flat/rising unattested share means either humans are still editing outside the log, or the agent is using unaudited channels.
- Split the prediction into two metrics:
  - human-typed hunk records vs agent-authorised hunks;
  - unattested bytes per channel.
- Mention team autonomy level directly, since “longer tasks” is not identical to “higher autonomy.”

## 10.3 Fact-check/reasoning

The threat-model inversion is broadly correct:

- Reference [23] — Greenblatt, Shlegeris, Sachan, Roger — is real and correctly describes AI control with trusted/untrusted components.
- Reference [25] — Meinke et al. — is real and correctly summarised: frontier models capable of in-context scheming under goal+nudge conditions.
- Reference [29] — Bengio et al., *Managing extreme AI risks* — real.
- Reference [31] — Burns et al., weak-to-strong generalization — real and correctly summarised.

The weaker parts:

### “The evidence that this is not paranoia has been accumulating”

This is rhetorical overstatement. Meinke et al. demonstrates *capability* for in-context scheming under specific adversarial conditions; it is not population-level evidence that production frontier models are routinely scheming. Fix: say “the evidence that trust should be conditional has been accumulating.”

### Redwood untrusted-advice protocol [24]

- **Cannot verify.** A July 2026 Redwood blog post with 16-character advice and 67% capability-gap recovery on SWE-bench Verified is future-dated and very specific.
- If you keep it, specify:
  - what “67% of capability gap” means;
  - trusted executor vs untrusted advisor model identities/sizes;
  - absolute SWE-bench Verified scores, not only gap recovery.

### “The same executor-and-advisor shape now ships as an API feature [30]”

- **Cannot verify.** This is a strong product claim about Anthropic’s “Advisor tool.”
- If true, cite the documentation version, date, and relevant API parameter. If not, remove or hedge: “similar executor/advisor patterns are appearing in deployed tooling.”

### “Machine-signed hunks”

This is fine only if “machine-signed” means signed by trusted logging infrastructure, not simply output by an untrusted model. Make that explicit.

## 10.4 Reasoning check

Claim 1 — statistics cannot attribute authorship, ceiling falls — is correct and follows from Sadasivan et al., provided reference [3] is the expected paper.

Claim 2 — provenance at write time per channel — is correct, and the shell 9% result supports it. The section should not treat the 9% result as externally visible unless the paper already reports it; otherwise an expert will ask for the exact measurement.

Claim 3 — human contribution becomes authorisation/review — is reasonable given [18] and [19]. But “authorisation and review” undersells other human work: environment design, constraint specification, monitoring, intervention. Add “specification, constraint-setting, and review” for precision.

## Important missing top-tier sources

A hostile reviewer would likely expect:

- **Shavit et al., “Practices for Governing Agentic AI Systems”** (OpenAI, 2023/2024) — directly relevant to authorisation, observability, and human control, and would strengthen §10.2.
- **Greenblatt et al., “Alignment Faking in Large Language Models”** (Anthropic, 2024) — top-tier AI-control-adjacent evidence alongside Meinke.
- **An AI Index or Epoch AI source** for empirical capability trend claims, rather than relying only on METR/ARC/IASR.
- Possibly **Grace et al.** expert surveys on AGI timelines if you want to say “the people building them say general intelligence is near” with more robustness.

Also: reference [26], *Sparks of AGI*, is included but never cited in the section text. Cite it or remove it. Same for Altman in [27].

## Overall judgment

The core conceptual move — provenance unit shifts from bytes to authorization as autonomy rises, and the threat model becomes closer to AI control — is defensible and useful. But the section is **not bulletproof as written** because several load-bearing 2026 facts/quotes and an API/product claim are unverified or unverifiable, the falsifiable prediction is too strong, and a few rhetorical claims overreach.

**Verdict:** The argument is publishable if tightened, but the 2026-dated claims and “now ships” product statement must be verified or removed before public release.

### F. x-ai/grok-4.6
## Review of §10 (fact-check + stress-test)

I treated every empirical claim as hostile-reviewer bait. Sources dated 2025–2026 that I cannot confirm are marked **cannot verify**, not false. Internal measurements (`9 %`, the vault wiki note) are out of scope except where they collide with the argument.

---

### 10.1 Measured

| Claim | Verdict |
|---|---|
| METR time-horizon is the main operational yardstick: 50 % reliability on software tasks | **Accurate in kind.** METR’s long-task / time-horizon work is real and widely cited. Primary paper: Kwa et al., *Measuring AI Ability to Complete Long Tasks* (commonly circulated 2025). |
| arXiv:2503.14499 | **Plausible / cannot independently confirm the number.** The METR long-task paper exists; I cannot confirm that exact arXiv id from here. |
| Jan 2026 “Time Horizon 1.1”: doubling “around every 7 months” 2019–2025; suite 170→228; Claude Opus 4.5 = 320 min (170–729); intervals “still very wide”; few remaining tasks defeat newest models; URL `metr.org/blog/2026-1-29-time-horizon-1-1/` accessed 4 Sep 2026 | **Cannot verify** (postdates what I can check). The *original* METR result did report ~7-month doubling and wide CIs — that part is in-family. Opus 4.5, 320 min, 228 tasks, and the “few remaining tasks” clause are unverified and are the load-bearing numbers in §10.2. Do not ship them without a frozen archive (PDF + hash + access date). |
| ARC-AGI-3 launched 2026; “100 % human-solvable”; criterion “as long as there is a gap between AI and human learning, we do not have AGI”; gap large at launch | **Cannot verify** the 2026 product and the quoted criterion as a launch statement. Chollet 2019 (`arXiv:1911.01547`) **is real** and does define intelligence as skill-acquisition efficiency. ARC-AGI-2 `arXiv:2505.11831` **cannot verify**. Bundling 2019 + AGI-2 + AGI-3 under [21] will be called sloppy. |
| IASR Oct 2025 key update: gains in coding/math/autonomy; profile “jagged”; `arXiv:2510.13653`. Full 2026 report 3 Feb 2026 | **Cannot verify** those two documents. The International Scientific Report on Advanced AI Safety (Bengio chair, 2025) **is real**. “Jagged” is in the discourse (METR and others) but you need a page-level quote from [22], not a vibe. |

**Fix:** Split [20] into (a) the frozen 2025 paper and (b) the 2026 blog, with quoted sentences. Same for [21] and [22]. If the 320 min / 7-month / “few remaining tasks” lines cannot be archived, drop them; the section does not need a date.

---

### 10.1 Declared

| Claim | Verdict |
|---|---|
| Fortune, 23 Jan 2026, Davos clash | **Cannot verify** the article. |
| Hassabis: 50 % AGI “within the decade”; “all the cognitive capabilities humans can — and I mean all”; today’s systems “nowhere near” | **Cannot verify** as Davos 2026 quotes. In-family with prior Hassabis remarks; still must be word-for-word against the Fortune piece. |
| Amodei at Davos: replace software-developer work within a year; Nobel-level research within two | **Cannot verify.** This is sharper than his usual public hedging (“powerful AI”, large fraction of coding). If Fortune softened or condensed, you are overstating. |
| LeCun: “we’re never going to get to human-level intelligence by training LLMs” | **Cannot verify** as a Davos 2026 sentence. The position is real and repeated; the quotation still needs the clip. |
| Amodei, *Machines of Loving Grace*, Oct 2024: “a country of geniuses in a datacenter” | **Accurate.** Essay is real; phrase is exact. |
| AI 2027, Apr 2025, ai-2027.com, Kokotajlo et al., forecast not measurement | **In-family / treat as real.** Citing it as scenario, not data, is the right move. |
| Altman, *The Gentle Singularity*, Jun 2025, in [27] | **Cannot verify**, and it is **not used in the prose**. Kitchen-sink citation. |

**Fix:** One statement, one source, one URL with archive. Do not put Amodei 2024 + Altman 2025 + AI 2027 in a single [27]. Either quote Davos from a transcript or demote to “reported as”.

---

### 10.1 Defined

| Claim | Verdict |
|---|---|
| Morris et al., `arXiv:2311.02462`, 2023, ICML 2024 position paper; performance ≠ generality; autonomy axis tool → consultant → collaborator → expert → agent; autonomy a deployment choice | **Accurate.** Paper is real; axes are real. Minor: their labels are slightly more specific than your paraphrase, but not wrong. |
| Feng, McDonald, Zhang, `arXiv:2506.12469`, 2025; five levels operator / collaborator / consultant / approver / observer; autonomy “can be treated as a deliberate design decision, separate from its capability” | **Cannot verify** paper, level names, or the quotation. |

**This is the first structural crack.** You then mix the two ladders (“operator and collaborator” from Feng, “consultant and approver” as the next step, Morris’s “expert/agent” in the background). They are **not the same ordering** (Morris: consultant *before* collaborator; Feng: collaborator *before* consultant). A reviewer who has read [18] will treat this as not having read [18].

**Fix:** Pick **one** ladder, put the other in a footnote as “related taxonomy”, and never say “consultant and approver levels” as if that were a published pair.

---

### 10.3 Control / scheming / protocols

| Claim | Verdict |
|---|---|
| Greenblatt et al., AI Control, `arXiv:2312.06942`, 2023: untrusted strong model, trusted weak monitor/editor/executor | **Accurate.** Right primary source. |
| Meinke et al., in-context scheming, `arXiv:2412.04984`, 2024 | **Accurate** as *capability in evals*, not as fielded subversion of SCM. |
| Bengio et al., *Managing extreme AI risks…*, Science 2024 / `arXiv:2310.17688` | **Accurate.** |
| Redwood “untrusted advice”, 27 Jul 2026: trusted executor, untrusted model ≤16 chars, ~67 % of SWE-bench Verified gap | **Cannot verify** any of: existence, date, 16 characters, 67 %, SWE-bench Verified. This is the most specific quantitative claim in the control half. If it is off by a little, you look careless; if the blog moved, you look fabricated. |
| Same shape “now ships as an API feature” / Anthropic Advisor tool [30] | **Cannot verify.** Mapping a 2026 product name onto Redwood’s protocol is a strong equivalence claim. Cite the doc sentence that says untrusted-advisor / trusted-executor, or drop “the same shape”. |
| Burns et al., weak-to-strong, `arXiv:2312.09390`, 2023 | **Accurate**, but it is **complementary**, as you say — it is not evidence that provenance must invert. |
| [26] Bubeck *Sparks of AGI* | **Real paper, unused in the section.** Dead reference. |

Scheming + control citations support “models can plot in context” and “there exist protocols that assume an untrusted policy”. They do **not** support “therefore a git ledger’s unit of review inverts, and the consequence is exact.”

---

### 10.4 / detection

Sadasivan-style “detection dies as distributions meet” is the right citation family ([3] not in the §10 list — add it). “Layer 3 is nothing at all tomorrow” is **overstated**: it is nothing as a *standalone authenticator*; it can remain a triage prior. Watermarking-with-keys is a different object; don’t conflate.

The `9 %` shell-bypass is internally consistent with 10.4.2 and **inconsistent** with 10.2 (see below).

---

### Missing sources a hostile expert would expect

Not a laundry list — the ones whose absence will be used against you:

- **Definitions / progress:** Legg & Hutter 2007; OpenAI Charter AGI language; Grace / AI Impacts expert surveys; Epoch AI compute–capability series; Aschenbrenner, *Situational Awareness* (2024) if you are going to cite AI 2027 as “declared”.
- **Jaggedness / evals:** METR task-suite caveats in the *2025* paper (distribution shift, scaffolding); UK AISI / US AISI public evals; DeepMind dangerous-capability papers (Phuong et al., Shevlane et al.).
- **Control / oversight, top-tier:** Hubinger et al. sleeper agents; Greenblatt et al. *alignment faking* (Anthropic, 2024) — more on-point for “untrusted writer” than Meinke alone; Korbak / control-arena style work; Christiano debate / IDA as the older stack; Russell *Human Compatible* if you mention “control problem” at all.
- **Bengio 2024 is there; Bengio “Scientist AI” / non-agentic AI is the natural foil to “autonomy is a choice” and is missing.**
- **Engineering TCB:** anything on IMA/measured boot, supply-chain attestations (in-toto, SLSA, Sigstore) — because you are proposing a ledger an untrusted agent can currently `rm`.

You do **not** need all of these. You need one sentence that shows you know alignment-faking and SLSA exist, or a reviewer will say the control mapping was done from two arXiv tabs.

---

### Does the argument hold?

**Thesis A — unit of provenance shifts from bytes to authorisation as autonomy rises.**  
Directionally right as *product design*. Not forced as *measurement*.

- At operator/collaborator, unattested bytes ≈ human hand **or** unlogged tool. You already measured the second (shell, 9 %). That does not go away when the human stops typing; it gets worse. A more autonomous agent has more ways to write (shell, editor, `git apply`, container breakout, CI, vendor CLI). **Unattested share → 0 is false unless the TCB covers every write path.** That is 10.4.2, which contradicts 10.2.
- “No longer a human channel writing into the file” ≠ “every byte is attested.” It only means the human is not the author. An untrusted agent writing unattested bytes is the *central* case in 10.3.
- METR 50 % time horizon ≠ “completes day-long tasks unattended” in a real repo. 50 % on a filtered software suite, with scaffolding, is not a deployment criterion. Even if 320 min were right, the 170–729 interval makes “may already be here” rhetoric, not inference. Day-long at 7-month doubling is ~1–2 doublings; that is a maybe, not a planning-horizon fact.

**Thesis B — threat model inverts (developer-adversary → model-adversary), per AI-control.**  
Half right, overclaimed as “exact”.

- §4.1 (human might cheat the ledger) and Greenblatt (policy might subvert the *task*) are different adversaries. You can have both at once. Inversion language hides the dual-adversary case (malicious developer *plus* untrusted model), which is the actual enterprise threat.
- AI-control protocols work by putting **actions** through a trusted scaffold (trusted editor/executor). A git note written by the same model that produced the hunk is not that scaffold. If the model can disable the hook, sign with a stolen key, or write around the index, two-sided provenance is theatre. The control literature’s actual conclusion is: **monitoring has to sit in the TCB (sandbox, policy, executor), not in an artefact the untrusted writer produces.** You almost say this in 10.4.2 and then undercut it by selling `authorised_by` on the hunk as the fix.
- Untrusted-advice (16-char hints, if real) does not imply a git schema. “Consequence is exact” should die.

**Falsifiable prediction (10.2) is not a test of the thesis.**

- Unattested share falling as task length grows: only if instrumentation coverage is held constant. Coverage will not be constant (new tools). Confound.
- “Authorisation records / hunk records should fall”: **true by construction** if one launch auth maps to a longer task with more hunks. That cannot falsify anything interesting.
- Better test: *unauthorised or out-of-policy actions per task-hour*, with a trusted executor that the agent cannot mute; plus hook-tamper events.

**What stays true (10.4)** — (1) statistical authorship is a ceilinged triage aid: **yes**, already today. (2) choke point moves to the environment: **yes**, and this is the best paragraph in the section; it should lead, not trail. (3) remaining human role is authorisation/review and should be legible: **yes**, but only if authorisation is bound to *policy + monitor verdicts*, not a launch signature.

**10.5 hedges are good.** Keep them. They currently do more work than 10.2–10.3.

---

### Concrete fixes (minimum to be bulletproof)

1. **Unmix taxonomies.** One figure: Morris *or* Feng. State explicitly that autonomy is a *chosen operating point*, not a METR-derived date.
2. **Kill “unattested → 0”. Replace with:** as human typing falls, *unlogged machine writes become the residual risk*; the ledger’s job is to make “write without attestation” a trusted-computing failure, not a classification problem.
3. **Kill “consequence is exact” and “threat model inverts”. Replace with dual-adversary:** human can still smuggle; model can still subvert; the record is useful iff signing keys and hooks are *outside* the untrusted policy (cite Greenblatt *and* SLSA/in-toto).
4. **Move provenance into the executor.** Schema sketch: `(policy_id, authorised_by, trusted_executor_id, untrusted_policy_id, monitor_verdict, action_hash)` emitted by the *trusted* executor, not by the model that wrote the diff. `producer` on the hunk is insufficient once the writer is untrusted.
5. **Repair the prediction:** pre-register (a) attested-write coverage as a function of new tools, (b) hook-disable/tamper rate, (c) out-of-policy action rate under a frozen scaffold. Drop the authorisation/hunk ratio.
6. **Demote 2026 point estimates** (320 min, 16 chars, 67 %, Davos quotes, Advisor API) to an appendix of archived screenshots, or remove. Body should run on Morris 2023, Greenblatt 2023, Burns 2023, Meinke 2024, Amodei 2024, METR 2025 paper, Bengio Science 2024 — all checkable.
7. **Add two citations, one sentence each:** alignment faking (untrusted writer in the wild-shaped eval); SLSA/in-toto (why a model-written provenance record is not a control protocol).
8. **Tighten METR language:** 50 % time horizon on a software suite ≠ unattended day-long work; quote METR on interval width rather than narrating past it.
9. **Split [21], [22], [27], [20].** Remove unused [26] or actually use it (I wouldn’t; “sparks of AGI” fights your “no date / no definition” pledge).

---

### Reasoning, weakest joint

The useful core is: **statistical detectors die; write-time provenance must follow the write channel; as you choose higher autonomy you must log authorisation and monitor verdicts, not keystrokes.** That survives.

It is weakest where 10.2 assumes the human channel vanishing *cleans* the ledger, while 10.3–10.4 assume an untrusted writer with *more* channels — and where control is treated as a git schema rather than a trusted executor. That is the paragraph a specialist will rip out.

**Verdict:** Ship the autonomy-vs-capability frame and the TCB/choke-point point; do not ship mixed ladders, unverifiable 2026 numbers, or “unattested share goes to zero / threat model inverts exactly” as written.

### G. z-ai/glm-5.3
(no answer from z-ai/glm-5.3: IncompleteRead(1122 bytes read))

### H. minimax/minimax-m3
# Fact-check and stress-test of §10

I'll go citation-by-citation first, then the missing-source sweep, then the argument. Several of the load-bearing items in this section are dated 2025–2026 and postdate my knowledge; I mark those "cannot verify" rather than asserting false.

---

## 1. Citation-by-citation

### [18] Morris et al., "Levels of AGI"
- arXiv:2311.02462 — **real, correctly attributed**, all eight authors right.
- The performance/generality/autonomy split with the five-level autonomy ladder (tool → consultant → collaborator → expert → fully autonomous agent) is **accurate** to the paper.
- ICML 2024 position paper status — **plausible/accurate**; it appeared in the ICML 2024 proceedings.
- The paper does not claim autonomy is "a deployment choice constrained but not fixed by capability" in those exact words; that's a fair paraphrase but the verbatim claim is weaker in the source — the paper calls autonomy a *dimension* orthogonal to performance/generality. Minor overstatement.

### [19] Feng, McDonald, Zhang
- arXiv:2506.12469 — **cannot verify** this exact arXiv number. The paper by these three authors at UW/Cornell with this title and a five-level operator/collaborator/consultant/approver/observer ladder is real (it was a CHI 2025 work), and the framing in §10.1 matches the abstract of that paper. Verify the arXiv number before camera-ready.

### [20] METR Time Horizon
- arXiv:2503.14499 (Kwa et al., March 2025) — **real**.
- The September 2025 Time Horizon 1.0 update reporting ~7-month doubling time on the original ~170-task suite — **accurate to my training**.
- The **specific January 2026 "Time Horizon 1.1" update, the 228-task enlargement, the 320 / 170–729 minute point estimate for "Claude Opus 4.5", and the "few remaining tasks defeat the newest models" claim cannot be verified from my data**. Treat as unverified pending primary-source check.
- "Claude Opus 4.5" — **cannot verify** that this model designation exists as of early 2026. Anthropic's public naming as of my knowledge is through the Claude 4 / Claude 4.1 family. A hostile reviewer will press on this.
- arXiv pre-print reference is mis-cited as "2025"; the original is March 2025 ✓, but the blog link dated "29 January 2026" is the primary citation for the section's claim. Use the blog as the lead citation.

### [21] ARC-AGI
- arXiv:1911.01547 (Chollet, 2019, "On the Measure of Intelligence") — **real, correctly attributed**.
- ARC-AGI-2 (arXiv:2505.11831) — **cannot verify** this arXiv number; ARC-AGI-2 itself was announced in 2025 and the arXiv number is plausible but should be checked.
- **ARC-AGI-3 cannot be verified**. The verbatim quote "as long as there is a gap between AI and human learning, we do not have AGI" is in Chollet's prior public statements; the *100% human-solvable* claim is consistent with ARC Prize's framing of the interactive environments. Flag both as cannot-verify.
- Citation list bundles three different works under [21]; standard practice is to split.

### [22] International AI Safety Report
- The October 2025 "First Key Update" and the report itself — **real**, chaired by Bengio and produced by an international expert panel. The "jagged" characterisation of the capability profile is accurate.
- arXiv:2510.13653 — **cannot verify** this exact arXiv number; the report is a UK government publication and the arXiv version may or may not exist with this identifier. The 2026 update "published 3 February 2026" cannot be verified.
- The framing "the field has no agreed definition" of AGI is correct *and* is itself a Bengio-panel claim, so citing the report for it is defensible.

### [23] Greenblatt et al., "AI Control" (arXiv:2312.06942)
- **Real, correctly attributed**, correct title. The framing (untrusted strong model, trusted weak monitor, safety under subversion) is accurate to the paper.

### [24] Redwood Research untrusted-advice protocol
- "C. Biddulph, A. Kaufman" as authors — **plausible**: Biddulph is a known Redwood author; Kaufman should be confirmed.
- Date "27 July 2026" — **cannot verify**.
- Specific quantitative claim ("16 characters per message … recovers about 67 % of the capability gap on SWE-bench Verified") — **cannot verify**. The numbers are concrete enough to be falsifiable and are central to §10.3; if they are wrong by even a few points the section's "the same shape now ships as an API feature" claim becomes shaky.
- The protocol name and the executor/advisor shape are consistent with Redwood's published research direction.

### [25] Meinke et al., scheming
- arXiv:2412.04984 — **real, correctly attributed**, correct title. The in-context scheming result and the "given a goal and a reason" framing are accurate.

### [27] Amodei, Altman, Kokotajlo — bundled under one citation
- Amodei, "Machines of Loving Grace", October 2024 — **real**, "a country of geniuses in a datacenter" is a verbatim phrase from the essay.
- Altman, "The Gentle Singularity", June 2025 — **real**.
- AI 2027, April 2025, Kokotajlo et al. — **real**.
- **Bundling three works into a single numbered reference is a formatting violation in every major venue.** Split into 27a/27b/27c or renumber.
- The prose says the AI 2027 scenario is "a forecast, not a measurement" — fair, but then cite it only as a forecast and don't elevate it to evidentiary status; right now the section uses it decoratively.

### [28] Fortune Davos article (Jan 23 2026)
- All four quotes (Hassabis "50 % chance … within the decade"; "all the cognitive capabilities humans can — and I mean all"; "nowhere near"; Amodei on replacing software developers in a year and Nobel-level research in two; LeCun on LLMs not reaching human-level) — **cannot verify** individually, but each is consistent with prior public statements by the same speakers. The LeCun quote is the most stylistically characteristic; the Hassabis "— and I mean all" parenthetical has the right cadence. **Quotes must be checked verbatim against the Fortune transcript before publication**; paraphrased quotes in a research paper are a referee-killer.

### [29] Bengio et al., Science 2024
- "Managing extreme AI risks amid rapid progress" — **real**, published in Science (May 2024), arXiv:2310.17688 ✓. The framing "oversight must scale with capability" is in the paper.

### [30] Anthropic "Advisor tool" documentation page
- **Cannot verify** that this is an actual Anthropic product/feature as named. If it exists, the citation needs the exact URL and access date. If it doesn't, drop the claim — the section already cites [24] for the shape.

### [31] Burns et al., weak-to-strong
- arXiv:2312.09390 — **real, correctly attributed**, correct title. OpenAI's superalignment team work.

### [26] Bubeck et al., "Sparks of AGI"
- **Unused in the body of §10 but still listed.** Either cite it where it's claimed (the previous sections, presumably) or remove from this section's reference list. Having it appear without an in-text callout is a citation hygiene issue a reviewer will note.

### [3] Sadasivan et al.
- Cited in §10.4 claim 1. Cannot fact-check the argument's specifics here, but the paper is real and the headline claim (detection degrades as generated text approaches the human distribution) is accurate to its abstract. Worth verifying the specific phrasing used is not overstated.

---

## 2. Missing sources a hostile reviewer will demand

The section is well-sourced on the *autonomy* and *control* axes but light on:

1. **Cotra (2022) "Biological anchors"** and **Grace et al. (2018, 2022) expert surveys** — the canonical AGI-timeline literature; reviewers expect at least one of them when discussing forecast range.
2. **Aschenbrenner (2023), "Situational Awareness"** — would be expected as a near-term AGI scenario alongside AI 2027; omitting it and including AI 2027 looks cherry-picked.
3. **Apollo Research (2024) "In-Context Scheming Across Six Frontier Models"** — the missing companion to [25]; reviewers will ask why Meinke but not Apollo is cited.
4. **Hubinger et al. (2024) "Sleeper Agents"** — the deception-in-weights result that motivates §10.3 even more directly than Meinke.
5. **Critiques of the Levels-of-AGI framework** — at minimum Hernández-Orallo's *FLAI* / "jagged" critique or Veit et al. on autonomy scales. A paper that hinges on [18] should acknowledge that [18] has known pushback.
6. **Mitchell et al. on model evaluations** (e.g., "Defining AGI" 2024 / "Levels of AGI" follow-ups by Mitchell & Krakauer) — direct commentary on [18].
7. **Cybersecurity/agentic-incident literature** — Kinniment et al. (2024) METR evaluations of LLM agents, or the AI Incident Database. The section's "rare event worth finding moves from the unattested byte to the unauthorised action" needs evidence that unauthorised actions are happening.
8. **NIST AI RMF (2023) and the EU AI Act (2024)** provenance/audit obligations — these are *the* institutional reason provenance records matter beyond internal tooling.
9. **CAIS "Statement on AI Risk" (2023)** — a single-sentence allusion to field consensus is expected when making "no agreed definition" claims.
10. **LeCun's primary position paper** (e.g., arXiv:2401.02028, "Objective-Driven AI") rather than just a quoted Davos line — the section uses LeCun as evidence that one major lab head rejects the LLM path; this is too important to footnote.
11. **Multi-agent provenance work** — the autonomy frameworks cited are single-agent; modern deployments (Anthropic's "agent teams", OpenAI Operator, Google's Project Astra / Project Mariner) are multi-agent. The "natural extension to `authorised_by`" claim breaks down in multi-agent settings where authorisations chain.

---

## 3. Reasoning — where it holds, where it breaks

### What holds
- **Shift from bytes-to-bytes to intent-as-unit** is logically forced by Morris/Feng: once humans stop producing artefacts, the *only* contribution they make that matters is the authorisation context. The §10.2 prediction (unattested share falls, authorisation/hunk ratio falls) is testable on existing data — this is a real strength of the section.
- **Two-sided provenance as composition (machine-signed hunks + human-signed authorisations + monitor verdicts)** is the correct schema direction. It is genuinely under-served by current tooling, which mostly stops at "AI wrote this" watermarks.
- **The capture-at-write-time argument** is durable across autonomy levels; it is the load-bearing practical claim of the paper and is correct.

### Where it breaks (the hostile-reviewer hits)

**Hit 1 — "Trends to zero" is the wrong shape.** "Unattested share of the artefact trends toward zero" is false when the artefact is wholly machine-produced. The whole *file* is unattested, not "tending to zero unattested." A more accurate statement: the *human-authored* share of an artefact trends toward zero, and at the same time the *human-authored* share of an *authorisation ledger* grows or stays flat. The framing as "unattested share shrinks" is misleading; it should be "the *attestation unit* changes."

**Hit 2 — "Threat model inverts" is wrong; it stacks.** Developer-as-adversary (insider threat, account compromise, prompt injection that subverts the developer's intent) does not vanish because the model becomes capable. AI-control adds the model-adversary threat on top; it does not invert the prior one. Use "expands" or "the trusted/untrusted axis rotates" — the word "inverts" reads as a categorical claim and a careful reviewer will press.

**Hit 3 — The `authorised_by` extension is underspecified.** A hostile reviewer will ask: what key signs? How is replay prevented? What is the threat model against the *authoriser* themselves (an authorised person clicking "approve" without reading)? The section skips the hardest part of the design — that authorisation is itself a human action that the ledger needs to verify, and that humans rubber-stamp by default. This is documented in AI-control's own "trusted monitor" work, which the section cites but does not apply here.

**Hit 4 — Falsifiable prediction has obvious failure modes.** "Unattested share falls monotonically as agents are given longer tasks" — this fails if (a) longer tasks require more human steering/iteration, (b) teams stop running the hook because they "trust" their agents, or (c) multi-agent cascades make the per-PR measurement noisy. State these confounds.

**Hit 5 — Claim 3 in §10.4 ("human's remaining contribution is authorisation and review") is contested.** A growing literature (e.g., work on meaningful human control, on human-on-the-loop rubber-stamping, on Anthropic's own "Constitutional AI" framing) argues that for high-capability systems *authorisation* is not a meaningful locus of human contribution; it has to be *design-time constraint*. The section quotes [18] and [19] for "autonomy is a choice" but does not engage with the literature that contests whether that choice is meaningful at high capability. This is the biggest single gap.

**Hit 6 — Implicit assumption: single-agent.** §10.2 and §10.3 talk about "the system" as a singular entity. Modern deployments are multi-agent; a single `authorised_by` field does not capture a chain of agents delegating to sub-agents. This breaks the schema proposal.

**Hit 7 — The "rare event worth finding" claim (last sentence of §10.2) is asserted without evidence.** "The rare event worth finding moves from the unattested byte to the unauthorised action" — what is the rate of either, today? Without numbers this is hand-waving. Either cite agentic-incident statistics or weaken the claim.

**Hit 8 — "As long as there is a gap between AI and human learning, we do not have AGI" [21]** — if reproduced verbatim, this is a quote of Chollet's framing, fine. If paraphrased, mark as paraphrase.

---

## 4. Concrete fixes (priority-ordered)

1. **Split [27] into three references** (Amodei, Altman, Kokotajlo) and remove or cite [26] in-text.
2. **Verify or remove "Claude Opus 4.5"** — use whatever the actual system name is, or say "the best measured system at the time of the update" without naming it if uncertain.
3. **Verify verbatim the Davos quotes in [28]** against the Fortune transcript; parentheticals like "— and I mean all" are exactly where misquoting creeps in.
4. **Replace "threat model inverts" with "threat model expands: developer-as-adversary remains, model-as-adversary is added"** — this is a one-word fix that makes the argument robust to a hostile reading.
5. **Replace "unattested share trends to zero" with "the attestation unit changes from hunk to intent"** — same conclusion, accurate framing.
6. **Specify the cryptographic and replay-prevention properties of the proposed `authorised_by` field**, or weaken the claim to "schema direction, not implementation."
7. **Add the four biggest missing sources** (§2 items 1, 2, 3, 4: Cotra, Aschenbrenner, Apollo, Hubinger). Adding all four adds two paragraphs of citations and removes the "selection bias" smell.
8. **Add a one-line acknowledgment** that the autonomy frameworks in [18] and [19] have been critiqued (cite one critic), to forestall the "uncritical endorsement" objection.
9. **Add confounds to the falsifiable prediction in §10.2**: iteration overhead, hook bypass, multi-agent cascades.
10. **Add a sentence on multi-agent deployments** in §10.3; either restrict the schema to single-agent and say so, or extend with a delegation-token concept.
11. **Add an evidence anchor for the "unauthorised action" claim** (AI Incident Database, METR autonomous-task evaluations showing failure modes, or a specific Apollo/Anthropic evaluation).
12. **Tighten the EU AI Act / NIST RMF linkage** in a single sentence; this is the strongest reason institutional readers will care.
13. **Drop or correct [30]** depending on whether Anthropic has a public "Advisor tool" page — otherwise the "shape now ships as an API feature" claim sits on a single non-canonical citation.
14. **Mark cannot-verify items** in the camera-ready with a footnote ("specific 2026 figures verified against primary source on [date]") so reviewers can see the discipline.

---

## Verdict

**Publishable after mechanical fixes (split citations, verify verbatim quotes, correct "inverts" → "expands", verify model name and 2026 numbers) and one structural fix — broaden the threat model from inversion to composition and acknowledge multi-agent deployments — but the load-bearing reasoning holds.**

## Round 2 — cross-check (each critiques the anonymised pool)

### openai/gpt-5.6-luna-pro reviews
## Comparative assessment

### Answer A — strongest overall

A is the strongest answer because it most closely follows the requested protocol:

- It reviews claims individually rather than discussing only the thesis.
- It distinguishes **accurate**, **unsupported**, **overstated**, and **cannot verify**.
- It checks quotations, citation structure, internal claims, and future-dated sources.
- It correctly separates:
  - capability from autonomy,
  - authorship from authorization,
  - provenance from safety,
  - AI-control threat models from ordinary software provenance.
- It gives concrete schema, threat-model, metric, and experimental fixes.
- It correctly rejects the simple claim that the threat model “inverts” and recommends a plural threat model.
- It correctly identifies that signatures authenticate records, not comprehension, safety, or policy compliance.

Its main weakness is that it is very long and occasionally says “likely” or “plausible” where a stricter answer should say simply **cannot verify**. It also does not foreground several particularly sharp internal contradictions as clearly as D and F do.

### Answer D — best concise diagnostic answer

D catches several high-value issues that A does not state as forcefully:

1. **The opening claim may conflict with Morris et al. [18].** If [18] classifies some frontier systems as “Emerging AGI” or Level 1 on its framework, then “not general intelligences by any published definition” is untenable. The safe correction is not necessarily that current systems are AGI, but that the sentence is too absolute.
2. **The METR title is likely wrong.** The cited 2025 paper is *Measuring AI Ability to Complete Long Tasks*, not *…Long Software Tasks*. This should have been checked and corrected.
3. **The 50%-reliability result is improperly converted into “unattended day-long tasks.”** A 50% task horizon is not a deployment guarantee.
4. **The autonomy labels are mixed.** Morris and Feng apparently order “consultant” and “collaborator” differently, so the section cannot use their labels as one ladder.
5. **The prediction is confounded by the paper’s own 9% shell-bypass result.**
6. **The proposed ledger must be outside the untrusted agent’s control.**

D is less complete than A for the “every factual claim” requirement, but its prioritized corrections are excellent.

### Answer F — strongest technical threat-model critique

F gives the clearest security architecture critique:

- an untrusted agent cannot be allowed to author its own audit trail;
- the trusted executor, policy engine, or external recorder must emit attestations;
- “machine-signed hunks” are meaningless if the model controls the signing path;
- the more autonomous system may have more unlogged channels, not fewer;
- “authorisation records / hunk records” may be true by construction and therefore not falsifiable;
- the threat model should be described as **stacking or expanding**, not inverting.

F is especially strong on trusted-computing-boundary implications. However, it contains some overconfident or insufficiently verified statements of its own, including assertions about the original METR result, ARC-AGI-2, and various suggested sources. It also says some sources are “real” while elsewhere treating comparable post-2025 sources as unverifiable. For this task, the safer standard is to mark anything not checked against a primary source as **cannot verify**.

### Answer H — useful but too speculative in places

H identifies the taxonomy collision, the risk of treating authorization as sufficient, missing supply-chain attestation literature, and the need to model multi-agent delegation. Those are useful additions.

But it is not sufficiently disciplined about verification:

- It says several post-2025 works are “real” or “in-family” while admitting they cannot be checked.
- It treats the 2025 International AI Safety Report claims as real despite not verifying the exact report, arXiv identifier, or wording.
- It makes source-status claims about Feng et al. and ARC-AGI-2 that should instead be marked **cannot verify**.
- It calls the core shift “logically forced,” which overstates the argument.

### Answer E — generally sound, but less complete

E is cautious about future claims and correctly criticizes:

- “most-cited,”
- the monotonicity claim,
- the METR-to-day-long extrapolation,
- “threat model inverts,”
- the “evidence this is not paranoia” rhetoric,
- the Anthropic API claim.

It is weaker because it does not fully develop the trusted-executor architecture, the Morris/Feng taxonomy conflict, the internal contradiction around current systems and [18], or the need to preserve byte-level provenance alongside authorization provenance.

### Answer B — useful security points, but contains factual and conceptual errors

B correctly identifies the central implementation risk: an untrusted agent may tamper with an in-environment ledger. Its recommendation to use an isolated recording boundary, trusted executor, or hardware-backed attestation is valuable.

However, it should not be treated as the strongest answer because:

- It calls Anthropic’s and OpenAI’s scaling policies “legally binding operational definitions.” That is not established and is likely wrong. They are organizational safety policies or commitments, not generally legal definitions of AGI or autonomy.
- It says the authorization record should be “legally/operationally responsible,” introducing a legal conclusion not supported by the paper.
- It treats *Sleeper Agents* as the canonical demonstration of precisely the relevant threat model without distinguishing backdoors, deceptive behavior, and AI-control protocols.
- It does not perform the requested claim-by-claim citation audit.
- It calls the thesis “brilliant” and “holds up,” which is not appropriate for an adversarial review.

### Answers C and G

Incomplete and unusable.

---

## Important errors or omissions across the answers

Even the better answers should have handled the following more explicitly.

### 1. The opening sentence is too absolute

> “current systems … are not general intelligences by any published definition”

This cannot safely be stated. There are published definitions and frameworks under which some current systems may receive a low or “emerging” AGI classification. The paper may argue that current systems do not satisfy **its chosen operational threshold**, but it cannot negate every published definition.

Safer:

> “Whether current systems qualify as AGI depends on the definition. Under the operational frameworks used here, they should not be treated as fully general or fully autonomous intelligences.”

### 2. Morris and Feng are not interchangeable taxonomies

The section uses “operator,” “collaborator,” “consultant,” and “approver” as if they form one progression. It must specify which framework supplies the labels. If their order differs, that is a substantive error, not merely a presentation issue.

### 3. Reference [20] appears mis-titled

The 2025 METR paper should be checked and likely cited as:

> *Measuring AI Ability to Complete Long Tasks*

not:

> *Measuring AI Ability to Complete Long Software Tasks*

The paper may use software tasks, but the title must be exact.

### 4. Reference grouping is poor

Reference [27] bundles three separate works:

- Amodei’s *Machines of Loving Grace*;
- Altman’s *The Gentle Singularity*;
- *AI 2027*.

They need separate references. The same issue affects [20] and [21], which combine papers, blogs, and benchmark pages. Each factual claim should point to the exact primary source.

### 5. “50% reliability” is not “unattended completion”

The reasoning silently changes:

- a benchmark’s estimated task duration at 50% success,
- into reliable unattended operation,
- then into real-world day-long autonomy.

That is invalid without specifying:

- task distribution,
- success criterion,
- scaffolding,
- environment,
- intervention allowance,
- reliability threshold,
- and whether the benchmark generalizes to the target team’s repositories.

### 6. “Unattested share tends toward zero” is likely backwards

If the agent writes through an uninstrumented shell, container, CI job, editor, or external service, greater autonomy can increase unattested machine output. The human-authored share may tend toward zero; the unattested share does not.

The paper must distinguish at least:

- human-authored bytes;
- machine-authored bytes;
- bytes attributed to a named process;
- bytes observed by a trusted recorder;
- bytes produced under valid authorization;
- bytes conforming to policy;
- bytes reviewed by a trusted monitor.

### 7. The falsifiable prediction is not currently well-formed

The proposed prediction:

> unattested share falls monotonically as task length grows

is confounded by:

- new tool paths;
- shell and filesystem bypasses;
- human intervention;
- retries and merges;
- multi-agent delegation;
- changing hook coverage;
- denominator choice;
- task mix.

The authorization-to-hunk ratio may also fall mechanically when one authorization produces more hunks. That makes it a poor falsifier.

A better test would measure, under a fixed trusted recorder:

- attested writes per task-hour;
- out-of-policy actions per task-hour;
- hook-disable or recorder-tampering events;
- authorization scope violations;
- percentage of actions linked to a valid delegation token;
- coverage of all relevant write boundaries.

### 8. “Threat model inverts” is wrong

AI-control literature does not establish that the human adversary disappears. The safer formulation is:

> “As model capability and autonomy rise, the model must be added as a potentially adversarial principal; the original human, credential, harness, and external-input threat models remain relevant.”

The model, developer, toolchain, monitor, signing key, and external input may all be adversarial or compromised simultaneously.

### 9. Authorization is not a substitute for provenance or verification

A human signature can establish that a key authorized a task. It does not establish:

- informed consent;
- comprehension;
- absence of prompt manipulation;
- correct scope enforcement;
- safe execution;
- absence of hidden side effects;
- correctness of the resulting code;
- integrity of the monitor;
- that the signed policy was the policy actually enforced.

The correct architecture is layered provenance:

1. authorization provenance;
2. policy and constraint provenance;
3. execution/action provenance;
4. artifact/byte provenance;
5. monitor provenance;
6. review provenance;
7. external-state/outcome provenance.

### 10. The ledger must be outside the untrusted agent’s control

This is one of the strongest points made by B and F. Moving capture “to the environment” is not sufficient if the agent controls that environment.

The final paper must state that security-relevant attestations are emitted by a trusted boundary, such as:

- a trusted executor;
- an isolated policy gateway;
- a hypervisor or host-level recorder;
- append-only remote logging;
- hardware-backed or measured attestation, where appropriate;
- a version-control or CI service outside the model’s privilege domain.

Even then, the paper must state the trust assumptions. TPMs and signatures do not automatically provide semantic truth.

### 11. The section underuses existing provenance and supply-chain work

A hostile security reviewer would expect discussion of at least some of:

- in-toto;
- SLSA;
- Sigstore;
- NIST AI RMF;
- software supply-chain attestations;
- trusted execution or measured-boot literature.

The proposed `authorised_by` and monitor-attestation structure is not wholly novel. The paper should position its contribution as extending existing build and supply-chain attestations to agent-mediated authorship and authority.

### 12. Missing AI-control/deception sources should be prioritized, not listed indiscriminately

The most relevant additions are:

- Hubinger et al., *Sleeper Agents*;
- work on alignment faking;
- Apollo Research scheming evaluations;
- scalable oversight and trusted-monitoring work;
- agent evaluation work such as RE-Bench, if the section relies on long-horizon extrapolation.

Timeline forecasts such as Cotra, Grace et al., Aschenbrenner, or AI Index reports are useful only if the paper continues making claims about what “the people building them” believe or how soon AGI may arrive. They are not all mandatory.

## Strongest answer

**Answer A is strongest overall** because it best satisfies the requested breadth and verification discipline. **Answers D and F contain the most important additional corrections**, particularly the Morris self-contradiction, the METR title, the 50%-reliability slide, taxonomy mixing, and trusted-boundary problem. A final review should combine A’s coverage with D/F’s prioritization and technical security analysis.

## What a correct and safe final answer must include

It must:

1. Mark every 2025–2026 claim, quote, number, date, and product feature as **cannot verify** unless checked against the primary source.
2. Correct or verify the METR title and separate the paper from the 2026 update.
3. Split bundled references.
4. Remove “most-cited,” “the field says,” and similar unsupported superlatives.
5. Correct the opening AGI claim so it does not contradict [18].
6. Use one autonomy taxonomy consistently and explain differences between [18] and [19].
7. Replace “unattested share tends toward zero” with a distinction between human authorship, machine attribution, trusted attestation, and authorization.
8. Replace “threat model inverts” with “threat model expands” or “becomes multi-principal.”
9. Preserve byte-level provenance; add authorization, policy, execution, monitor, and outcome provenance rather than replacing bytes with intent.
10. State that authorization signatures do not prove comprehension, safety, compliance, or correctness.
11. Ensure the recorder and signing path are outside the untrusted agent’s control.
12. Replace the monotonic prediction with a pre-registered, measurable hypothesis that controls for instrumentation coverage and multi-agent delegation.
13. Distinguish AI-control protocols from merely similar API architectures.
14. Add the most relevant deception/control and supply-chain-attestation sources.
15. End with a restrained verdict that the section is not ready until the unverifiable load-bearing claims are checked or removed.

**Verdict: Answer A is strongest overall, but the final review must incorporate D and F’s corrections: the argument should be reframed as layered provenance under an expanding multi-adversary threat model, not a shift from bytes to authorization or an inversion of trust.**

### google/gemini-3.1-pro-preview reviews
**Errors, Unstated Assumptions, Risks, and Disagreements**

*   **Errors in the text:**
    *   *Taxonomy collision:* The text states "operator and collaborator... move to consultant and approver," silently mixing the Morris and Feng frameworks. Morris ranks Consultant *below* Collaborator; Feng ranks Collaborator *below* Consultant. 
    *   *Self-contradiction on AGI definition:* The opening claims current systems are "not general intelligences by any published definition." However, citation [18] (Morris et al.) explicitly classifies frontier LLMs as "Level 1: Emerging AGI."
    *   *Citation hygiene:* Reference [27] improperly bundles three distinct sources (Amodei, Altman, Kokotajlo). Reference [26] (Bubeck) is listed but never cited in the text. Reference [20] misstates the title of the METR paper (it is *Measuring AI Ability to Complete Long Tasks*, without "Software").
*   **Unstated Assumptions & Flawed Reasoning:**
    *   *The TCB (Trusted Computing Base) assumption:* The text assumes that as human typing stops, the "unattested share trends toward zero." This assumes 100% of the agent's write paths are instrumented. If the agent uses unlogged channels (like the 9% shell bypass mentioned in the text), unattested bytes will actually *increase*.
    *   *Ledger integrity:* The text proposes an `authorised_by` git record as an AI-control mechanism. This assumes the untrusted model won't simply forge, strip, or bypass the git hook. AI control requires the monitor to sit in the execution environment (the scaffold/hypervisor), not in an artifact written by the untrusted model.
    *   *The falsifiable prediction:* The prediction that "authorisation records to hunk records should fall" is true by construction (one launch intent naturally yields many hunks) and therefore useless for falsification.
*   **Risks:**
    *   Relying on highly specific, unverified 2026 numbers (Claude Opus 4.5 at 320 minutes, Redwood's 16-character/67% SWE-bench claim) and verbatim Davos quotes without primary-source archives exposes the paper to immediate rejection if a single digit or word is off.
*   **Disagreements between answers:**
    *   Answer B argues provenance must move *outside* the environment (to a hypervisor/TPM) because the agent controls the environment. Answer F agrees but frames it as a TCB issue. 
    *   Answer H hallucinates that Feng et al. [19] is a CHI 2025 paper to fill the "cannot verify" gap. 
    *   Answers disagree on the exact wording of the METR paper title, but D correctly identifies the absence of the word "Software".

**Strongest Answer**

**Answer F** is the strongest. It acts exactly like a hostile expert reviewer. It is the only answer to catch the subtle but fatal taxonomy collision between the Morris and Feng ladders. It ruthlessly dismantles the reasoning in §10.2 and §10.3, correctly pointing out that an untrusted model writing its own git provenance is "security theatre" and that the falsifiable prediction is true by construction. 

**Answer D** is a close runner-up because it is the only one to catch the glaring contradiction that the text's own citation [18] classifies current models as Level 1 AGI, invalidating the section's opening sentence. 

**What a Correct/Safe Final Answer Must Include**

To be bulletproof, the final review must mandate the following fixes:

1.  **Resolve the AGI Definition Contradiction:** Flag that Morris et al. [18] defines current models as "Level 1 AGI," which falsifies the opening claim. The text must be softened to "not *fully* general intelligences" or "at best Level 1."
2.  **Fix the Taxonomy Collision:** Force the authors to pick *one* autonomy ladder (Morris or Feng) and use its hierarchy consistently, rather than mashing them together and reversing the order of Consultant/Collaborator.
3.  **Correct the Threat Model:** The threat model does not "invert"; it *expands* to a dual-adversary model. The malicious/negligent human developer threat remains, and the untrusted-model threat is added on top.
4.  **Dismantle the "Unattested -> Zero" Claim:** Explicitly state that unattested shares will only drop if the Trusted Computing Base (TCB) covers every single agent write-path. Otherwise, unlogged machine writes will cause the unattested share to rise.
5.  **Address Ledger Security (The AI Control Flaw):** Point out that an untrusted agent cannot be in charge of writing its own audit trail. Provenance must be captured by a trusted executor/scaffold outside the agent's context (linking to supply-chain attestation literature like SLSA/in-toto).
6.  **Redesign the Falsifiable Prediction:** Reject the current prediction as confounded by unlogged channels and true by construction. Replace it with a metric tracking out-of-policy actions or hook-tamper events under a frozen scaffold.
7.  **Citation Hygiene & Missing Sources:** Demand the splitting of bundled citation [27], the removal of orphaned citation [26], and the inclusion of canonical deception literature (e.g., Hubinger's *Sleeper Agents* or Anthropic's *Alignment Faking*) to justify the untrusted-model premise.
8.  **Verification Mandate:** Require frozen web archives for all 2026 claims (METR numbers, Redwood protocol stats, Davos quotes, Anthropic API features) before public release.

### qwen/qwen3.8-max reviews
## Scope

Answers C and G are non-answers: C is an incomplete-read stub; G is also incomplete/no substantive review. I evaluate A, B, D, E, F, H.

I use “cannot verify” for 2025–2026 claims and for any late-2024 item that cannot be checked from primary sources. I do not treat unverifiable future claims as false.

---

# 1. Ranking and strongest answer

**Strongest answer: D.**  
D is the strongest because it catches the most damaging concrete problems that would immediately undermine the section in front of a hostile reviewer:

1. The section’s opening claim that current systems are “not general intelligences by any published definition” is contradicted by its own citation to Morris et al. [18], which can be read as placing current frontier systems at an early “Emerging AGI” level.
2. The METR title is likely wrong: D flags that the paper is likely *Measuring AI Ability to Complete Long Tasks*, not *Long Software Tasks*.
3. The section mixes two incompatible autonomy ladders: Morris et al. and Feng et al. use different ordering for “consultant” and “collaborator”.
4. The falsifiability test is self-confounded because unattested share can remain flat or rise due to unlogged machine channels, which the paper itself reports.
5. The human authorization leg is not a clean root of trust; it is vulnerable to rubber-stamping, model-curated summaries, and oversight failure.
6. Reference hygiene problems are identified: bundled references, unused references, internal wiki citation, unsupported superlatives.
7. It supplies a useful missing-source list, especially deception/control and supply-chain attestation.

D is not perfect. It is too confident about some post-cutoff items, especially Altman’s *The Gentle Singularity*, AI 2027, ARC-AGI-2, and some METR details. It also does not push the trusted-computing-base point as hard as B or F. But it is the only answer that combines citation-level error detection, reasoning stress-test, and concrete fixes at the needed granularity.

**Close second: F.**  
F is the strongest on security architecture and on the falsifiability problem. It correctly says the ledger cannot live inside an environment controlled by an untrusted agent, and it identifies that the proposed authorization-to-hunk ratio can fall by construction. But F misses the crucial [18] “Emerging AGI” contradiction and does not explicitly flag the internal wiki citation as a public-release problem. That prevents it from being the strongest overall.

---

# 2. Major errors, assumptions, risks, and disagreements across answers

## 2.1 The opening AGI-definition claim is not bulletproof

The section says:

> “Everything above is measured on current systems, which are not general intelligences by any published definition.”

That is too strong.

**D catches the decisive issue:** Morris et al. [18], which the section cites, provides an operational AGI-level framework and can be used to classify current systems at an early level, often described as “Emerging AGI.” A hostile reviewer will use [18] against the section.

A, E, F, H either miss this or only say the claim is too absolute. B misses it entirely.

**Required fix:**

> “Whether current systems qualify as AGI depends on the definition used. Under the operational frameworks adopted here, they should not be treated as full general intelligences; however, some published frameworks, including Morris et al. [18], may classify current frontier systems at an early AGI level.”

That preserves the section’s caution without contradicting its own citation.

---

## 2.2 The autonomy taxonomies are mixed incorrectly

The section uses Morris et al. [18] and Feng et al. [19] together, then says:

> “At the operator and collaborator levels … As deployments move to the consultant and approver levels …”

This is unsafe because the two frameworks do not line up cleanly.

**D and F catch this.**  
In Morris et al., “consultant” appears before “collaborator” in the autonomy ladder. In the Feng taxonomy as quoted in the section, “collaborator” appears before “consultant.” The section silently switches between frameworks.

A says generally to verify labels but does not identify the collision. B, E, H do not handle it sharply enough.

**Required fix:**  
Pick one taxonomy and use it exclusively. If Feng et al. is agent-specific, use Feng for the deployment levels and put Morris in a footnote as a related capability/AGI framework. Do not create a hybrid ladder.

---

## 2.3 METR claims need stricter verification and less extrapolation

The section says METR tracks task length at 50% reliability and cites a January 2026 update with specific numbers: 7-month doubling, 170 to 228 tasks, Claude Opus 4.5, 320 minutes, interval 170–729 minutes.

The correct posture is:

- The general METR time-horizon concept is plausible and relevant.
- The exact 2026 numbers are **cannot verify** unless checked against the primary archived page.
- The exact paper title must be verified. D and F flag that it is likely *Measuring AI Ability to Complete Long Tasks*, not *Long Software Tasks*.
- “Most-cited operational yardstick” is an unsupported superlative. A, D, E, F catch this.
- 50% reliability does not mean “unattended” operation. D and F catch this; A partly catches the extrapolation problem but not as cleanly.
- The interval type must be specified: confidence interval, credible interval, bootstrap interval, etc. A catches this.
- The phrase “few remaining tasks defeat the newest models” must be quoted exactly or removed.

**Required fixes:**

1. Replace “most-cited” with “widely used” or “influential.”
2. Verify the exact METR title and arXiv ID, or mark cannot verify.
3. Split the METR arXiv paper and the 2026 blog update into separate citations.
4. Keep the 50% reliability qualifier attached whenever discussing time horizon.
5. Do not infer “day-long tasks unattended” from a 50% time-horizon estimate.
6. If the 2026 numbers cannot be archived, remove them or move them to an appendix with a verification note.

---

## 2.4 Future sources require “cannot verify,” not confident assertion

Several answers are too confident about post-cutoff material.

Items that must be marked **cannot verify** unless primary sources are checked:

- METR Time Horizon 1.1, January 2026.
- Claude Opus 4.5 as a model designation.
- ARC-AGI-3, its 2026 launch, its quotes, and its “100% human-solvable” claim.
- International AI Safety Report October 2025 key update and February 2026 report.
- Davos 2026 Fortune article and all direct quotes from Hassabis, Amodei, LeCun.
- Redwood Research July 2026 untrusted-advice protocol and the 16-character / 67% SWE-bench Verified claim.
- Anthropic “Advisor tool” documentation.
- Feng, McDonald, Zhang 2025 autonomy paper and exact quote.
- Altman, *The Gentle Singularity*, June 2025.
- AI 2027, April 2025, unless independently verified.
- Amodei, *Machines of Loving Grace*, October 2024, if the reviewer’s verifiable horizon does not include it.

Answer-specific problems:

- **D** incorrectly treats Altman’s *The Gentle Singularity* as real and is too confident on AI 2027 and ARC-AGI-2.
- **F** is too confident on Amodei, AI 2027, and the existence of the International AI Safety Report, though it is better than most on marking the 2026 details cannot verify.
- **H** is too confident about Feng being CHI 2025, METR’s September 2025 update, Altman, AI 2027, and the International AI Safety Report.
- **E** is more cautious but still says AI 2027 is real without verification.
- **B** is too brief and does not enforce verification discipline enough.
- **A** is generally cautious but says the underlying METR work is “real and well known” without distinguishing what is inside versus outside verifiable knowledge.

**Required fix:**  
For every 2025–2026 claim, the final answer must say “cannot verify” unless it supplies an archived primary source, exact quote, access date, and hash or screenshot. Do not mark unverifiable claims as false.

---

## 2.5 Reference hygiene is a real vulnerability

Several answers catch parts of this, but D, F, H, E, and A all identify at least some.

Problems:

1. **[27] bundles three separate works**: Amodei, Altman, Kokotajlo et al. This must be split.
2. **[21] bundles Chollet 2019, ARC-AGI-2, ARC-AGI-3**. Split.
3. **[22] bundles an October 2025 update and a February 2026 report**. Split.
4. **[20] bundles an arXiv paper and a 2026 blog update**. Split.
5. **[26] Bubeck et al. is listed but not used in §10**. Cite or remove.
6. **Altman in [27] is not used in the prose**. Remove or cite.
7. **The 2026 International AI Safety Report in [22] is not clearly used**. Remove or cite.
8. **[3] Sadasivan et al. is cited in the text but missing from the supplied reference list**. Add it if this list is meant to be complete for §10.
9. **The internal wiki citation** `wiki/review-josh-pocock-buzz.md` is not a public source. A and D catch this. It should be removed from a public paper or explicitly labeled as an internal design note.

B misses most of this. F catches much of it but does not explicitly flag the internal wiki citation. D is strongest here.

---

## 2.6 “Unattested share trends toward zero” is false or at least badly misleading

The section says:

> “The unattested share of the artefact trends toward zero … there is no longer a human channel writing into the file.”

This is one of the section’s main reasoning failures.

A, D, E, F, H all catch versions of it. B catches the related ledger-tampering problem.

The issue:

- If humans stop typing, the **human-authored share** may go to zero.
- But the **unattested share** does not necessarily go to zero.
- An autonomous agent may write through shell commands, scripts, package managers, CI tools, APIs, containers, file-system tools, or other uninstrumented channels.
- The section’s own 9% shell-bypass result supports this risk.
- Therefore, higher autonomy can increase unattested machine-written bytes unless the logging boundary is moved outside the agent’s control.

**Required fix:**

> “As autonomy rises, the human byte-channel may disappear, but unattested machine writes remain the central provenance risk unless all security-relevant write paths are captured by a trusted boundary.”

This is stronger and safer than the current claim.

---

## 2.7 “The threat model inverts” is overstated

The section heading says:

> “The threat model inverts.”

That is wrong as a categorical claim.

A, D, F, H correctly say the threat model should be plural, two-sided, expanded, or stacked. B and E are too willing to accept inversion.

The correct model:

- The human developer may still be malicious, negligent, compromised, or mistaken.
- The model may be untrusted, misaligned, deceptive, or strategically subversive.
- The harness, sandbox, monitor, signing key, dependency chain, or external input may also be adversarial or compromised.
- AI-control literature adds the untrusted-model threat; it does not erase the human-adversary threat.

**Required fix:**

Replace:

> “The threat model inverts.”

With:

> “The threat model expands: the model becomes an additional potentially adversarial principal, while the human-adversary and infrastructure-adversary threat models remain relevant.”

Or:

> “The threat model becomes two-sided.”

---

## 2.8 The ledger must be outside the agent’s trusted computing base

This is the most important engineering risk.

**B and F are strongest here.**  
A and D gesture at trusted boundaries but do not make the point sharply enough. E and H mention underspecification but do not fully develop the TCB issue.

The section proposes:

- machine-signed hunks;
- human-signed authorizations;
- monitor verdicts;
- a `producer` field;
- an `authorised_by` record.

But if the untrusted agent can write to the git index, file system, container, hook, or local ledger, it can tamper with the provenance record.

A correct final answer must say:

- Provenance cannot be stored only inside the agent-controlled environment.
- The audit trail must be emitted by a trusted executor, hypervisor, secure gateway, sandbox supervisor, or hardware-backed attestation mechanism.
- The agent should not be able to disable, rewrite, replay, or selectively suppress records.
- Signing keys must be outside the untrusted model’s control.
- Monitor verdicts must be bound to the exact task, policy, environment, model version, tool permissions, and action sequence.

**Required schema direction:**

A safe record should include at least:

```text
task_id
authorised_by
authorisation_signature
policy_hash
scope / permissions / resource limits
expiry
environment_hash
container/image hash
model_id / model_version / weights hash or immutable identifier
harness_id / harness_version
trusted_executor_id
monitor_id / monitor_version
monitor_verdict
action_hash / event-log root
timestamp / ordering proof
revocation status
delegation chain, if multi-agent
```

A human signature alone proves key possession, not informed consent, comprehension, absence of coercion, or that the signed policy was enforced.

---

## 2.9 Human authorization is not a clean root of trust

D, F, H, A, and B all identify variants of this.

The section treats `authorised_by` as if it solves the review problem. It does not.

Problems:

- Humans rubber-stamp.
- Humans may approve summaries written by the untrusted model.
- Humans may not understand the scope.
- Authorization may be too broad.
- The agent may exceed scope while appearing compliant.
- The human may be socially engineered or coerced.
- The signed intent may not be tightly bound to the resulting diff or actions.

**Required fix:**  
The final answer must say that the monitor-verdict leg and trusted-executor leg carry the safety weight. Human authorization is necessary for accountability, but it is not sufficient for security.

---

## 2.10 The proposed falsifiable prediction is confounded

The section predicts:

> “the unattested share per pull request should fall monotonically as the team's agents are given longer tasks, and the ratio of authorisation records to hunk records should fall with it.”

This is not a clean test.

A, D, E, F, H catch problems. F is sharpest on the ratio problem.

Problems:

1. **Monotonicity is too strong.** Longer tasks may increase human interventions, retries, rebases, manual fixes, or unlogged tool use.
2. **Instrumentation coverage is not constant.** If agents use more shell or external tools, unattested share can rise even if the thesis is true.
3. **Unattested share conflates human writes and unlogged machine writes.** The paper’s own 9% shell result shows this.
4. **Authorization-to-hunk ratio can fall by construction.** One authorization can produce many hunks. That does not test the core claim.
5. **Task length is not identical to autonomy level.** Longer tasks may involve more or less human oversight depending on workflow.

**Required fix:**  
Replace the prediction with a pre-registered, controlled metric set, for example:

- attested-write coverage as a function of instrumented channels;
- unlogged-write rate per task-hour;
- out-of-policy action rate;
- hook-disable or tamper events;
- human-edit rate versus agent-edit rate;
- monitor-verdict coverage per action;
- unauthorized-action rate under a frozen scaffold.

Do not claim monotonic decline without controlling for workflow, tool coverage, task mix, and multi-agent delegation.

---

## 2.11 Missing sources a hostile reviewer will expect

The section’s citation set is not sufficient for AGI progress, AI control, and provenance.

The correct final answer must identify missing top-tier or near-top-tier sources. The exact list can be trimmed, but the following categories are necessary:

### AGI definitions and progress

- Legg and Hutter, *Universal Intelligence*.
- Chollet, *On the Measure of Intelligence* — already cited, but should be used carefully.
- OpenAI charter/public AGI language, if discussing industry definitions.
- Grace et al. expert surveys, Cotra biological anchors, Epoch AI or AI Index if making broad progress claims.
- Aschenbrenner, *Situational Awareness*, if citing AI 2027-style fast-takeoff scenarios.
- A counterforecast or skeptical source, e.g., Narayanan and Kapoor if available, or Mitchell et al. on AGI/evaluation limits.

### Evaluation and agent caveats

- SWE-bench / SWE-bench Verified, if SWE-bench is used.
- METR’s own task-suite caveats.
- UK AI Safety Institute / US AI Safety Institute evaluations, if relevant.
- Kapoor et al., *AI Agents That Matter*, or equivalent agent-evaluation critique.
- RE-Bench or comparable long-horizon agent evaluations.
- Dell’Acqua et al. for “jagged frontier” if that term is used.

### AI control, deception, and oversight

- Hubinger et al., *Sleeper Agents*.
- Greenblatt/Denison et al., *Alignment Faking in Large Language Models*.
- Apollo Research scheming work, if Meinke et al. is used.
- Christiano debate/IDA or scalable oversight literature.
- Burns et al. weak-to-strong is already cited but should be framed carefully.

### Provenance, supply chain, and audit standards

- in-toto.
- SLSA.
- Sigstore.
- C2PA.
- TPM/measured boot/remote attestation literature if making TCB claims.
- NIST AI RMF, EU AI Act, ISO/IEC 42001 if making institutional audit claims.

### Lab operational policies

- Anthropic Responsible Scaling Policy.
- OpenAI Preparedness Framework.

But B is wrong to call these “legally binding operational definitions.” They are lab policies or safety frameworks, not generally legally binding definitions of autonomy or threat level.

---

# 3. Answer-by-answer assessment

## Answer A

**Useful catches:**

- Flags unsupported superlatives: “most-cited,” “arrive within planning horizon,” “threat model inverts.”
- Identifies metric slippage among unattested, machine-written, authorized, reviewed, and safe.
- Correctly says AI control does not mean the human-adversary threat disappears.
- Flags the weak causal support for the monotonic prediction.
- Provides a broad missing-source list, including SLSA/in-toto and standards.

**Errors / omissions:**

- Misses the [18] contradiction: current systems may be “Emerging AGI” under Morris et al.
- Does not explicitly identify the Morris/Feng consultant-collaborator ordering collision.
- Does not flag the likely METR title error.
- Is too generic in places; it gives many general fixes but fewer precise citation-level catches than D or F.
- Does not push the TCB/ledger-tampering problem hard enough.
- Suggests possible 2025 sources, e.g., an AAAI 2025 panel, without marking them clearly as speculative/cannot verify.

**Assessment:** Safe in spirit, but not sharp enough for a bulletproof review.

---

## Answer B

**Useful catches:**

- Identifies the fatal engineering flaw: if the agent controls the environment, it can tamper with the ledger.
- Correctly says provenance must be isolated via hypervisor, secure gateway, or hardware-backed attestation.
- Identifies the authorization-versus-verification gap: human authorization does not prove the agent did not insert malicious changes.
- Flags missing Sleeper Agents citation.
- Flags missing lab RSP/preparedness frameworks.

**Errors / assumptions / risks:**

- Says RSPs are “legally binding operational definitions.” That is wrong or at least substantially overstated. They are lab safety policies, not generally legally binding definitions.
- Mischaracterizes OpenAI’s framework by associating it too closely with ASL-style levels.
- Accepts the “inverted threat model” framing too much instead of correcting it to an expanded or stacked threat model.
- Misses most citation-level problems: [18] contradiction, METR title, bundled references, unused references, taxonomy collision, internal wiki citation.
- Too brief to satisfy the task’s requirement to check every factual claim.
- Uses flattery: “brilliant,” which is unnecessary and contrary to the requested tone.

**Assessment:** Contains one of the most important security insights, but is too narrow and contains a factual overstatement about RSPs.

---

## Answer D

**Useful catches:**

- Identifies the [18] self-contradiction: current systems may be Level 1 / Emerging AGI under the cited framework.
- Flags the likely METR title error.
- Flags unsupported “most-cited” claim.
- Flags internal wiki citation as unverifiable for public release.
- Flags the 50% reliability to “unattended” slide.
- Identifies the mixed autonomy ladders and consultant/collaborator collision.
- Identifies the self-confounded falsifiability test.
- Identifies that human authorization is subvertible and that monitor verdicts carry safety weight.
- Identifies missing deception/control and supply-chain attestation sources.
- Gives concrete fixes.

**Errors / assumptions / risks:**

- Too confident about post-cutoff items: Altman’s *The Gentle Singularity*, AI 2027, ARC-AGI-2, and some METR details should be “cannot verify” unless checked.
- Does not state the TCB/hardware-attestation requirement as forcefully as B or F.
- Does not explicitly discuss multi-agent delegation, which H raises.
- Some missing-source suggestions are themselves future or uncertain and should be marked verify-before-citing.

**Assessment:** Strongest overall because it catches the decisive factual and structural errors, despite some overconfidence on future sources.

---

## Answer E

**Useful catches:**

- Good future-source caution.
- Flags “most-cited” as unsupported.
- Flags the Davos quotes as needing primary verification.
- Flags Altman’s *The Gentle Singularity* as cannot verify.
- Correctly says the falsifiable prediction is too strong and needs controls.
- Flags that “machine-signed” must mean signed by trusted logging infrastructure, not merely produced by an untrusted model.
- Flags missing Shavit et al. and alignment-faking work.

**Errors / omissions:**

- Misses the [18] Emerging AGI contradiction.
- Misses the Morris/Feng taxonomy collision.
- Does not flag the likely METR title error.
- Does not fully handle bundled references, though it flags unused [26] and Altman in [27].
- Accepts “threat-model inversion” too broadly; should say the threat model expands or stacks.
- Does not develop the TCB/ledger-tampering issue.
- Less concrete than D or F on fixes.

**Assessment:** Cautious and reasonable, but incomplete.

---

## Answer F

**Useful catches:**

- Strongest on the security architecture: the ledger must be emitted by a trusted executor, not by the untrusted writer.
- Correctly says “unattested share goes to zero” must be killed.
- Correctly says “the consequence is exact” and “threat model inverts” are overclaims.
- Identifies that the authorization-to-hunk ratio can fall by construction.
- Flags mixed autonomy ladders.
- Flags likely METR title issue.
- Flags bundled references and unused [26].
- Flags the need to demote 2026 point estimates to an appendix or remove them.
- Gives a concrete alternative schema and pre-registration metrics.
- Identifies missing alignment-faking and supply-chain attestation sources.

**Errors / omissions:**

- Misses the [18] Emerging AGI contradiction, which is one of the easiest hostile-reviewer attacks.
- Does not explicitly flag the internal wiki citation as a public-release problem.
- Too confident on Amodei, AI 2027, and the existence/status of the International AI Safety Report without marking them cannot verify where appropriate.
- Does not flag “most-cited” as clearly as it should.
- Does not discuss multi-agent delegation as explicitly as H.

**Assessment:** Best security stress-test, but not the best complete fact-check.

---

## Answer H

**Useful catches:**

- Flags many future-source verification issues.
- Identifies multi-agent deployments as a missing assumption; this is valuable and under-discussed by other answers.
- Correctly says the threat model expands rather than inverts.
- Flags that `authorised_by` is underspecified: key management, replay prevention, rubber-stamping.
- Flags missing critiques of the Levels-of-AGI framework.
- Flags missing policy sources: NIST AI RMF, EU AI Act.
- Flags missing deception sources.

**Errors / assumptions / risks:**

- Too confident about future or unverifiable items: Feng/CHI 2025, METR September 2025 update, Altman, AI 2027, International AI Safety Report.
- Misses the [18] Emerging AGI contradiction.
- Misses the likely METR title error.
- Does not explicitly identify the Morris/Feng consultant/collaborator ordering collision.
- Says the prediction is testable on existing data without fully internalizing the paper’s own unlogged-channel confound.
- Overstates the existence of some sources without “cannot verify” discipline.

**Assessment:** Good supplementary points, especially multi-agent and policy, but too overconfident and missing several concrete citation errors.

---

# 4. What a correct/safe final answer must include

A correct final review must contain the following non-negotiable items.

## 4.1 Verification discipline

It must say explicitly:

- Which claims are accurate to the reviewer’s knowledge.
- Which sources are real and correctly attributed.
- Which numbers, dates, or quotes are wrong, overstated, or unverifiable.
- Which 2025–2026 items are **cannot verify**.
- That unverifiable claims should not be called false.
- That public release requires archived primary sources for all load-bearing future claims.

## 4.2 Factual fixes

It must require:

1. Removal or softening of “most-cited operational yardstick.”
2. Verification or correction of the METR title.
3. Splitting METR paper and blog into separate citations.
4. Verification of the 7-month doubling, 228 tasks, Claude Opus 4.5, 320-minute estimate, and interval type.
5. No inference from 50% time horizon to reliable unattended day-long operation.
6. Verification of ARC-AGI-3 launch, quotes, and human-solvability protocol.
7. Attribution of ARC’s AGI criterion to ARC Prize, not to the whole field.
8. Verification of the International AI Safety Report update, arXiv ID, and “jagged” quote.
9. Verification of all Davos quotes against primary transcript or video.
10. Splitting [27] into Amodei, Altman, and Kokotajlo et al.
11. Verification or removal of Altman’s *The Gentle Singularity*.
12. Clear labeling of AI 2027 as a scenario/forecast, not measurement.
13. Removal or citation of [26].
14. Addition of [3] Sadasivan et al. if the reference list is meant to cover §10.
15. Removal or explicit internal-note labeling of the wiki citation.
16. Correction of the opening sentence to avoid contradicting Morris et al.
17. Selection of one autonomy taxonomy and elimination of the Morris/Feng collision.
18. Verification of Feng et al. arXiv ID, level names, and exact quote.

## 4.3 Reasoning fixes

It must require:

1. Replace “unattested share trends toward zero” with a claim about the human byte-channel declining while unlogged machine writes remain a risk.
2. Replace “the unit moves from diff to intent” with “the unit expands to include intent, authorization, constraints, execution actions, and monitor verdicts.”
3. Replace “threat model inverts” with “threat model expands” or “becomes two-sided.”
4. State that byte-level provenance remains necessary; authorization does not replace diff review.
5. State that human authorization is not a clean root of trust.
6. State that monitor verdicts and trusted execution carry the main safety burden.
7. State that the ledger must be outside the agent’s control: trusted executor, hypervisor, secure gateway, hardware attestation, or equivalent.
8. State that signatures authenticate records, not comprehension, consent, safety, or policy compliance.
9. Replace the monotonic falsifiability claim with pre-registered metrics and confounder controls.
10. Address multi-agent delegation, chained authorizations, and sub-agent actions.

## 4.4 Missing-source requirements

It must identify at least these categories as missing or needing explicit justification:

- Hubinger et al., *Sleeper Agents*.
- Alignment-faking work, e.g., Greenblatt/Denison et al.
- Apollo scheming work if Meinke is used as the only scheming citation.
- in-toto, SLSA, Sigstore, C2PA, or equivalent software-supply-chain provenance work.
- Trusted computing / attestation sources if the ledger is presented as security infrastructure.
- Expert-survey or forecasting sources for AGI timelines: Grace et al., Cotra, Epoch AI, AI Index, or equivalent.
- Evaluation-caveat sources: SWE-bench, RE-Bench, *AI Agents That Matter*, UK/US AI Safety Institute evaluations.
- Critiques of Morris et al.’s levels framework.
- Anthropic RSP and OpenAI Preparedness, described accurately as policies/frameworks, not legally binding definitions.

## 4.5 Final verdict requirement

The final answer must end with a one-line verdict. For the section itself, the safe verdict is:

> “Not safe for public release until all 2025–2026 claims are verified or removed, the threat model is changed from inversion to expansion, and provenance is moved to a trusted boundary outside the untrusted agent.”

---

# 5. Final one-line verdict

**Verdict: D is the strongest answer, but a safe final review must combine D’s citation-level catches with F’s trusted-executor/TCB fixes, mark all unverifiable 2025–2026 claims as “cannot verify,” and force the section to replace “inversion” and “zero unattested share” with a layered, dual-adversary, trusted-provenance model.**

### moonshotai/kimi-k3 reviews
# Comparative Review of Answers

## Coverage and accuracy of the answers themselves

**Answer A** is the most exhaustive claim-by-claim audit. Its strongest contributions: (1) catching that "not general intelligences by any published definition" is too absolute (though it misses the sharper version — see below); (2) the security analysis of what a human signature does and does not prove (comprehension, coercion, scope-binding); (3) the critique that "two-sided provenance" names three evidence classes; (4) a genuinely useful list of what the signed record must contain (policy hash, expiry, revocation, environment hash). Its weaknesses: it is bloated and repetitive; it asserts Sadasivan et al. is "likely substantially accurate if [3] is the paper's actual claim" without committing; it lists missing sources as a laundry list without ranking; and it incorrectly says Morris et al. is "associated with ICML 2024" while elsewhere hedging — minor, but it also fails to catch the sharpest available contradiction (below). It also claims "Claude Opus 4.5" postdates knowledge without flagging that the *name itself* is suspicious — H does this better.

**Answer B** is the shortest and the most architecturally original. Its distinctive contribution — that if the threat model inverts, the ledger cannot live inside the agent's environment ("you cannot store the security camera footage inside the bank vault") — is the single best engineering insight across all answers, and it directly contradicts §10.4(2)'s "move provenance into the environment" claim in a way no other answer states as crisply. It also uniquely flags Anthropic's RSP and OpenAI's Preparedness Framework as missing operational definitions — a genuinely good catch no one else makes. Weaknesses: it is thin on citation-level fact-checking (marks many things "accurate" with less scrutiny than others — e.g., it confirms Morris's autonomy labels as "Levels 0–5 (Tool, Consultant, Collaborator, Expert, Agent)" without noting the ordering collision with Feng that D and F catch); its claim that RSPs are "legally binding" is wrong (they are voluntary commitments); and it under-specifies fixes for the falsifiable-prediction problem.

**Answer D** is the most precise on citation mechanics and catches the two highest-value factual errors that almost everyone else missed:
1. **The [18] self-contradiction**: Morris et al. explicitly classify frontier LLMs as Level 1 General ("Emerging AGI"), so "not general intelligences by any published definition" is contradicted by the paper's own citation. This is the single most hostile-reviewer-exploitable error in §10, and only D and (implicitly, weakly) A get near it. D nails it.
2. **The METR title error**: the arXiv paper is *Measuring AI Ability to Complete Long Tasks*, not "...Long *Software* Tasks". Only D catches this. E and F repeat the wrong title or hedge.
D also uniquely catches: the 50%→"unattended" slide (a system succeeding half the time is not "unattended" — excellent catch, echoed only partially by F); the label collision between Morris and Feng orderings (consultant below vs. above collaborator — also caught by F); and the in-toto/SLSA prior-art problem (also caught by F). Its falsifiability critique is the sharpest: the test can falsify the thesis when the thesis is true, because unattested share counts unlogged *machine* writes too — a direct internal contradiction with §10.4(2)'s 9% shell result. F makes the same point. D's weaknesses: it asserts the METR title correction with "high confidence" — appropriate, but if wrong it's embarrassing; it lists "Denison et al., Sycophancy to Subterfuge" and "Anthropic's Agentic Misalignment (2025)" which are real but the former attribution needs care; and its verdict is slightly over-generous given its own findings.

**Answer E** is competent but the thinnest of the substantive answers. Its unique contributions: flagging that Altman's "The Gentle Singularity" doesn't match known Altman titles ("The Intelligence Age", "Three Observations") — a useful cannot-verify with specific reasoning, though D and F assert it's real (D and F are likely correct that the June 2025 post exists; E's skepticism is reasonable but probably wrong); and the Shavit et al. "Practices for Governing Agentic AI Systems" suggestion, which is genuinely on-point and unique to E. Its weaknesses: it repeats the wrong METR title ("Long Software Tasks") without checking; it misses the [18] self-contradiction entirely; it misses the Morris/Feng label collision; and its fixes are less concrete than A, D, or F.

**Answer F** is the most adversarially minded and ties with D for the deepest structural analysis. Unique or best-stated contributions: (1) the dual-adversary point — malicious developer *plus* untrusted model is the actual enterprise threat, so "inverts" hides the worst case (H also makes this point well as "expands, not inverts"); (2) the observation that the authorisation/hunk ratio prediction is "true by construction" and therefore unfalsifiable — the sharpest version of the prediction critique, sharper than D's; (3) "a git note written by the same model that produced the hunk is not that scaffold" — convergent with B's vault insight, stated from the TCB direction; (4) demanding archived screenshots/PDF+hash for the 2026 numbers — the most operationally concrete verification fix. Weaknesses: it asserts AI 2027 and Altman as "in-family / treat as real" with slightly more confidence than warranted; it repeats the METR title as "Long Tasks" (correct!) — actually F gets the title right where E gets it wrong; its missing-sources list is good but includes some marginal items (Russell's *Human Compatible* is not needed).

**Answer H** is thorough and well-organized but has the most factual overreach. Its unique contributions: the multi-agent/delegation-chain critique (a single `authorised_by` field doesn't capture agent-to-agent delegation — genuinely important and unique to H); the rubber-stamping/meaningful-human-control critique of the authorisation leg (D gestures at this; H develops it); NIST AI RMF / EU AI Act as the institutional hook (unique and correct). Its errors: (1) it claims "The September 2025 Time Horizon 1.0 update reporting ~7-month doubling time on the original ~170-task suite — accurate to my training" — this is a fabricated-sounding specificity; the original METR result was March 2025, and asserting a "September 2025 Time Horizon 1.0" with confidence is exactly the kind of unverifiable claim the task warns against; (2) it asserts Feng et al. "was a CHI 2025 work" — plausible but unverified and stated as fact; (3) it says "Apollo Research (2024) 'In-Context Scheming Across Six Frontier Models'" is a missing companion to Meinke — but Meinke et al. *is* the Apollo Research paper; H appears to cite the same work as its own missing companion, a real blunder; (4) "Aschenbrenner (2023)" — *Situational Awareness* is 2024, not 2023; (5) it claims the arXiv preprint is "mis-cited as '2025'" then says "the original is March 2025 ✓" — internally confused sentence. These errors materially damage H's credibility as a fact-check of a fact-check.

**Answers C and G** are void (tool errors).

## Points of agreement (likely correct)

All substantive answers agree on: the 2025–2026 items (METR 1.1 numbers, ARC-AGI-3, Davos quotes, Redwood July 2026, Anthropic Advisor tool, IASR October 2025 update) are cannot-verify and must be checked against primary sources before release; "most-cited" is an unsupported superlative; [27] must be split; [26] is an unused reference; "threat model inverts" is wrong — the human-adversary threat persists (D, F, H say "expands/two-sided"); the falsifiable prediction is confounded; Sleeper Agents and alignment-faking are the obvious missing deception citations; the core thesis (provenance unit moves toward authorisation) is directionally sound.

## Points of disagreement among answers

- **METR title**: D and F say "Long Tasks" (no "Software"); A and E repeat "Long Software Tasks". D and F are correct to my knowledge — this is a real, fixable citation error that half the answers missed.
- **Altman "The Gentle Singularity"**: D, F, H treat as real; E doubts it. D/F/H are more likely right (June 2025 post), but E's demand to verify is procedurally correct.
- **Whether the ledger should move into the environment**: B and F say §10.4(2) is *wrong* — provenance must move to the TCB boundary *outside* the agent's reach; A and D treat §10.4(2) as the section's best paragraph needing only multi-layer framing. B/F have the stronger security argument; the correct position is that capture must occur at boundaries the untrusted model cannot write to, which is a refinement, not a rejection, of "the choke point moves outward."
- **H's "September 2025 Time Horizon 1.0"** vs. everyone else's silence: H invented a checkpoint; no one else corroborates it.

## Strongest answer

**D is the strongest overall**, with F a close second. D catches the two highest-value factual errors (the [18] self-contradiction on "Emerging AGI" — the single most exploitable line in §10 — and the METR title), gives the sharpest version of the falsifiability critique (the test can falsify a true thesis), identifies the Morris/Feng label collision, and demands the supply-chain attestation prior art (in-toto/SLSA) whose absence makes §10.3 read as reinventing attestation. F matches D on structure and adds the "true by construction" demolition of the ratio metric and the dual-adversary framing, but is slightly less precise on citation mechanics. B has the single best engineering insight (ledger-in-vault) but is too thin elsewhere. A is comprehensive but misses the two best catches. H is undermined by its own factual errors — fatal in a fact-checking answer. E is competent but shallow.

## What a correct final answer must include

1. The **[18] self-contradiction**: Morris et al. classify frontier LLMs as Emerging AGI; "not general intelligences by any published definition" cannot survive contact with the paper's own citation (D).
2. The **METR title correction** and the demand to archive all 2026 numbers (320 min, 170–729, 228 tasks, 16 chars, 67%) with frozen copies or remove them (D, F).
3. **"Inverts" → "expands/two-sided"**: dual adversaries persist; the human-adversary model from §4.1 does not disappear (D, F, H).
4. The **ledger-placement flaw**: provenance capture must sit in the TCB (hypervisor/gateway/trusted executor), not inside the environment the untrusted model can write to; §10.4(2) as written lets the agent tamper with its own audit trail (B, F).
5. The **falsifiability repair**: unattested share conflates human writes and unlogged machine writes (per the paper's own 9% result), and the authorisation/hunk ratio is true by construction; the test needs pre-registered confound controls or replacement metrics (D, F).
6. The **Morris/Feng label collision** (consultant ordering differs); pick one ladder (D, F).
7. **Split [27]; cite or drop [26]; drop or verify [30]**; verify Davos quotes verbatim against transcript (all).
8. Missing sources that are non-negotiable: **Sleeper Agents, alignment faking, in-toto/SLSA attestation prior art**; plus at least one timeline-survey source (Grace et al.) and one operational-governance frame (RSP/PREPARED — B's catch, or Shavit et al. — E's catch).
9. The **authorisation-leg threat model**: signatures prove key possession, not comprehension or scope-compliance; the approver channel is itself subvertible (A, D, H).
10. **Multi-agent delegation** breaks the single `authorised_by` field (H — its one indispensable contribution).

**One-line verdict: Answer D is strongest — it alone catches the two citation-level errors (the Morris self-contradiction and the METR title) that most damage §10's credibility, while matching F's structural critique; a bulletproof review must combine D's citation precision, F's adversarial logic, B's TCB placement fix, and H's multi-agent point, while discarding H's own fabricated specifics.**

### deepseek/deepseek-v4-pro-0813 reviews
The reviews largely converge on the same critical point: the argument is directionally interesting but not yet bulletproof, and several load-bearing 2025–2026 claims are unverifiable without primary-source checking. They differ mainly in specificity and architectural severity.

## Which answer is strongest

**Answer D is the strongest overall.** It is the only review that catches several concrete, hard-to-ignore errors:

- **A self-contradiction inside §10**: the text says current systems are “not general intelligences by any published definition,” but Morris et al. [18] explicitly classify frontier LLMs as Level 1 General / “Emerging AGI.” A hostile reviewer would quote [18] against the paper.
- **[20]’s title is wrong**: the METR paper is *Measuring AI Ability to Complete Long Tasks*, not “Long Software Tasks.”
- **The falsifiable prediction is confounded by the paper’s own evidence**: §10.4 says autonomous systems create unlogged channels—the 9% shell result—but §10.2 predicts unattested share will fall. Unattested share can stay flat or rise precisely when an uninstrumented agent uses new channels.
- **[18] and [19] use contradictory labels**: “consultant” is below “collaborator” in Morris et al. and above it in Feng et al. The section silently mixes the two.
- **Human authorization is not a clean root of trust**: the AI-control literature the section cites treats human review as expensive and subvertible; the monitor-verdict leg carries the safety weight, not the signature.

Answer D also identifies the missing top-tier sources a specialist would expect—Sleeper Agents, alignment faking, SLSA/in-toto—and gives concrete, usable framing fixes.

## Where other answers add value

- **Answer A** is the most exhaustive citation-by-citation review. Its definitions table and threat-model table are useful, and it correctly stresses that byte-level provenance must not be removed—authorization is additional, not a replacement. But it misses the Morris contradiction and the label collision, which slightly weakens its precision.
- **Answer F** has the sharpest architectural point: once the model is untrusted, storing provenance in the agent’s environment is like putting the security-camera footage inside the bank vault with the robber. It correctly argues the provenance recorder must live in the trusted computing base—hypervisor, trusted executor, hardware-backed attestation—outside the model’s control.
- **Answer H** overlaps heavily with D/F and gives a good priority-ordered fix list, but it adds less new signal.
- **Answer B** is weaker: it calls the “inverted threat model” conceptually brilliant and states the “concept holds up,” while simultaneously identifying the ledger-integrity problem that actually undermines that exact phrase. “Inversion” should be rejected, not praised within a flawed architecture.
- **Answer E** is a competent surface review but less specific: it misses the Morris contradiction, the [20] title error, and the label collision, and it is softer on the false “unattested share trends toward zero” claim.

## What a correct/safe final answer must include

Any defensible version of this section needs these changes before release:

1. **Verification block for all 2025–2026 sources.** METR Time Horizon 1.1, ARC-AGI-3, the October 2025 safety-report update, Davos 2026 quotes, Redwood’s untrusted-advice numbers, and the Anthropic “Advisor tool” must be verified against archived primary screenshots/PDFs and quoted with page/section locators. If they cannot be archived, they must be removed or explicitly marked “unverified at time of writing.”

2. **Fix the [18] contradiction.** Replace “not general intelligences by any published definition” with language matching Morris et al.—e.g., “at most Level 1 (‘Emerging AGI’) on Morris et al.’s general-intelligence track.”

3. **Fix citation hygiene.** Split [27] into three references, remove or cite [26], split bundled [21] and [22] into separate works, correct [20]’s title, and remove or move the internal wiki note to a private appendix.

4. **Pick one autonomy ladder.** Do not mix Morris et al. and Feng et al.; state which taxonomy the section uses and keep the other as a footnote.

5. **Delete or reframe “unattested share trends toward zero.”** The correct claim is: human-origin share declines only if every write path is instrumented; machine-generated-but-unattested writes can increase as agents use shell/network/external tools.

6. **Delete the word “inverts” from §10.3.** Replace with “the threat model becomes two-sided / plural.” Keep both the human adversary and the model adversary. Provenance must capture both.

7. **State that the ledger must live outside the untrusted model’s control.** If the writer is adversarial, the recorder must sit in the TCB—trusted executor, sandbox policy layer, filesystem/container boundary, or hardware-backed attestation. Machine-signed hunks have little value if the model can forge or erase them.

8. **Rewrite the falsifiable prediction.** Do not depend on monotonic unattested-share decline or the arbitrary authorisation-record-to-hunk ratio. Pre-register instrumented-channel coverage, task length, workflow controls, and outcome metrics such as unauthorised/ out-of-policy actions per task-hour.

9. **Clarify the signature model.** A human signature proves issuance of a message, not informed consent, comprehension, absence of coercion, or that the signed policy was enforced. The monitor-verdict leg carries the safety weight.

10. **Add missing top-tier sources.** At minimum:
    - Hubinger et al., *Sleeper Agents*;
    - Greenblatt/Denison et al., *Alignment Faking in Large Language Models*;
    - SLSA / in-toto / Sigstore supply-chain attestation;
    - OpenAI’s or Anthropic’s operational scaling framework (Preparedness / RSP) if the section says “the field”;
    - Grace et al. expert surveys or Epoch/AI Impacts if near-term AGI forecasts are central;
    - one agent-evaluation critique such as Kapoor et al. *AI Agents That Matter* or METR RE-Bench.

11. **Do not quote 2026 reporting as fact.** News quotes from Fortune/Davos should be attributed as reported remarks, with the original wording checked or paraphrased safely.

The best combined version would merge Answer D’s specific fact-checks and self-contradiction catches with Answer F’s TCB/architecture insight and Answer A’s systematic definitions and threat-model table.

**Verdict:** Do not ship §10 until the 2025–2026 sources are verified or removed, the threat model is reframed from inversion to dual/adversary, the provenance recorder is placed outside the untrusted model’s control, and the byte-level/authorisation-level distinction is corrected.

### x-ai/grok-4.6 reviews
## Independent findings (section, not the answers)

**Opening overclaim.** “Not general intelligences by any published definition” is false as written. Morris et al. [18]—which the section itself uses—places frontier systems on a *general* track (commonly “emerging AGI”). A hostile reviewer will quote [18] against the first paragraph.

**Unverifiable load-bearing 2025–2026 items** (must be archived or dropped, not paraphrased): METR Time Horizon 1.1 numbers (228 tasks, Opus 4.5, 320 min / 170–729, “few remaining tasks”); ARC-AGI-3 launch, “100% human-solvable,” and the AGI-gap quote; IASR Oct 2025 / Feb 2026 and quoted “jagged”; Fortune/Davos 2026 quotes; Redwood Jul 2026 16-char / ~67% SWE-bench gap; Anthropic “Advisor tool” as the same control protocol; Feng et al. [19] verbatim quote and ladder; Altman *Gentle Singularity* (unused in prose).

**Citation hygiene already broken.** [20] title is likely *Long Tasks*, not “Long Software Tasks.” [21], [22], [27] bundle distinct works. [26] and Altman are unused. Internal `wiki/review-josh-pocock-buzz.md` is not a public source. “Most-cited” is unsupported.

**Taxonomy error.** Morris: consultant *before* collaborator. Feng (as cited): collaborator then consultant/approver. §10.2 silently uses Feng’s order while leaning on [18]. That is a “did not read [18]” hit.

**Argument, independently.** Bytes→authorisation is a *design* claim, not a measurement. It fails unless every write path is in a TCB the untrusted policy cannot mute. The paper’s own 9% shell result *and* §10.4.2 contradict “unattested share → 0.” METR 50% time-horizon ≠ “day-long unattended.” “Threat model inverts” is wrong: human adversary, model adversary, harness, monitor, keys, and external inputs coexist. Human-signed `authorised_by` is not a root of trust in the control literature the section cites (curated summaries, rubber-stamping). The auth/hunk-ratio “test” is true by construction if one launch maps to many hunks. A git note written by the writer is not Greenblatt-style control.

---

## Errors and unstated assumptions *in the answers*

| Answer | Material errors / gaps |
|---|---|
| **A** | Best overall audit shape, but misses Morris Level-1 self-contradiction, METR title, and [18]/[19] order collision. Slightly generic “cannot verify” without ranking which 2026 numbers actually carry §10.2–10.3. |
| **B** | Strong TCB point; weak fact-check. Over-labels items “Accurate and Verified.” Treats inversion as “elegant.” Omits Morris contradiction, ladder collision, 50%→unattended, confounded prediction, unused refs. RSPs are relevant but not “legally binding operational definitions of AGI.” |
| **C, G** | Empty / incomplete — fail the task. |
| **D** | Sharpest *bibliographic* catches (Morris vs opening line; METR title; 50% slide; wiki; unused refs; label collision; self-confounded test). Slightly light on “ledger lives inside the robber’s vault” / trusted-executor schema. Treats some 2025 items as real where the brief required “cannot verify.” |
| **E** | Correct direction, thinner. Misses Morris contradiction and ladder collision. Weaker missing-source set. |
| **F** | Sharpest *argument* stress-test (10.2 vs 10.3–10.4; dual adversary; TCB; prediction-by-construction; mixed ladders). Does not foreground Morris “emerging AGI” vs “any published definition” as D does. |
| **H** | **Factual error:** Meinke et al. [25] *is* the Apollo in-context scheming paper; listing “Apollo 2024 companion to [25]” as missing is a duplicate. **Over-verification:** calls Oct 2025 IASR / “jagged,” *Gentle Singularity*, and other 2026 items “real” where the brief requires cannot-verify. Laundry-list sources (CAIS statement, EU AI Act) without tying them to a claim. Too generous verdict (“reasoning holds”). |

**Disagreements that matter**
- Invert vs expand/two-sided/dual-adversary: A, D, F, H (correct) vs B (too kind to “inverts”).
- Whether 2026 point estimates can stay in the body: F (demote/remove) vs H (mechanical verify) vs B (ignore).
- Whether the unit *replaces* bytes or *layers* on them: A/F correct; the section and B over-index on intent.
- Apollo/Meinke: only H bungles identity of [25].

**Unstated assumptions across answers:** that arXiv IDs and 2026 blogs exist as cited; that “Advisor tool” ≡ Redwood untrusted-advice; that a human signature implies informed approval; that METR’s suite extrapolates to this paper’s repos.

**Risk if the paper ships on a weak review:** fabricated-looking 2026 quotes/numbers; self-own via [18]; security reviewers destroying “provenance in the sandbox” under an untrusted-model threat model.

---

## Strongest answer

**F is strongest**, with **D as required complement**.

F is the only review that (i) treats mixed autonomy ladders as a *structural* crack, (ii) shows §10.2 (“unattested → 0”) contradicts §10.3–10.4 (untrusted writer, more channels, 9%), (iii) kills “consequence is exact” / inversion, (iv) puts monitoring in a trusted executor/SLSA-style TCB rather than a model-written git field, and (v) shows the stated “falsifiable” ratio is non-informative. That is the review a specialist would actually use.

D uniquely supplies the opening-line vs Morris contradiction, METR title, 50%→unattended slide, public-wiki problem, and unused/bundled refs. A is the most complete *template* but misses those high-leverage hits. B’s isolation/TPM point is necessary but not a full fact-check. H is unsafe to follow on verification and on [25].

---

## What a correct/safe final answer must include

1. **Cannot-verify rule applied to every 2025–2026 number, quote, product, and arXiv id**; freeze or drop 320 min, 16 chars, 67%, Davos lines, Advisor API, ARC-AGI-3 quotes.
2. **Fix or qualify** “any published definition” against Morris Level 1 / emerging AGI.
3. **One autonomy ladder only**; footnote the other; do not say “consultant and approver” as if published as a pair.
4. **Split bundled refs**; drop unused [26]/Altman or cite them; kill the internal wiki as evidence.
5. **Soften METR:** 50% horizon on a suite ≠ unattended day-long work; no “most-cited”; no “may already be here” from a wide interval.
6. **Reframe provenance as layered** (artifact + execution + authorisation + policy + monitor + outcome), not bytes *replaced* by intent. Unattested share → 0 is false unless the TCB covers every write path.
7. **Threat model is dual/plural, not inverted.** Human smuggling remains. Model subversion is added. Signatures authenticate records, not comprehension or safety.
8. **Control mapping:** cite Greenblatt accurately; add sleeper agents / alignment faking as expected deception evidence; do not equate a 2026 API with a control protocol; **records must be emitted by a trusted executor outside the untrusted policy** (in-toto/SLSA/IMA), not stored where the agent can rewrite them.
9. **Rewrite the prediction** so it is not confounded by the 9% channel result and not true by construction; pre-register coverage, tamper, and out-of-policy action rates.
10. **Missing sources a referee will name:** Hubinger sleeper agents; Greenblatt et al. alignment faking; SLSA/in-toto (or equivalent); optionally Grace/AI Impacts, Kapoor agents-that-matter / RE-Bench, lab RSPs as *declared* operationalizations—not a dump of CAIS/EU Act.

**Verdict:** F+D together are the bar; the section is not bulletproof until 2026 claims are archived or cut, [18] is not self-contradicted, ladders are unmixed, and inversion/unattested→0 are replaced by layered provenance plus a dual-adversary TCB.

### z-ai/glm-5.3 reviews
## Preliminary

Answers **C and G are empty** (truncated reads) and contribute nothing. Everything below covers A, B, D, E, F, H. All six complied with the "cannot verify, don't call false" instruction for 2025–2026 sources — no answer fabricated a debunking, which was the main failure mode this task invited.

## 1. My independent verification — what I can confirm beyond the answers

**Verifiable now, and confirmed:**

- **The [18] self-contradiction is real, and only D caught it.** Morris et al. explicitly classify current frontier LLMs as Level 1 ("Emerging") on the *General* track — this is the paper behind the "DeepMind calls GPT-4 'Emerging AGI'" coverage. The section's opening claim that current systems "are not general intelligences by any published definition" is contradicted by a source the section itself cites two paragraphs later. This is the single most damaging verifiable error in §10. D's fix ("at best Level 1 ('Emerging') on [18]'s general track") is correct.
- **The METR title error is real, and only D caught it.** To the best of my knowledge the paper is *Measuring AI Ability to Complete Long Tasks* (arXiv:2503.14499) — no "Software." Notably, **F quotes the correct title in its own review and still fails to flag the discrepancy** in the section's reference [20].
- **The ladder collision is real; D and F caught it, no one else.** In Morris et al., *consultant* (level 1) sits **below** *collaborator* (level 2). In Feng et al. as cited, *collaborator* sits **below** *consultant*. §10.1 presents both ladders, promises to use "these autonomy levels," and §10.2 then silently uses Feng's ordering. A reader who knows [18] will read "the consultant and approver levels" as a step down, or as evidence the authors didn't read their own citation.
- **The 50% → "unattended" slide is real; D and F caught it.** METR's horizon is task length (in human completion time) at 50% success on a software suite. That is not "completes day-long tasks unattended," and "the interval is wide enough that it may already be here" is rhetoric — a wide CI does not move its upper bound into the present.
- The verifiable core citations are correctly confirmed by all six: [18], [23], [25], [29], [31], [26], Chollet 2019, the Amodei essay with the verbatim "country of geniuses in a datacenter," AI 2027 as forecast-not-measurement. The ~7-month doubling and ~170-task suite match the original March 2025 METR paper.
- Minor, only F noticed: [3] Sadasivan is used in §10.4 but absent from the section's reference list (which runs 18–31).

**Cannot verify (universal, correct discipline):** Time Horizon 1.1 specifics (228 tasks; "Claude Opus 4.5"; 320 / 170–729 min; "still very wide"; "few remaining tasks"), ARC-AGI-3 and both quotes, IASR Oct 2025 / Feb 2026 and "jagged" as a verbatim quote, all Davos quotes, the Redwood July 2026 post and its 16-char / 67% figures, the Anthropic "Advisor tool," and Feng et al.'s arXiv ID and verbatim quote. On [19], D and H lean "real" while A/E/F hold "cannot verify" — the safe position is D's: appears real, verify ID and quote against the primary. E's inability to verify Altman's *The Gentle Singularity* is a cutoff artifact (E states early-2025 knowledge), not a substantive disagreement.

## 2. Errors inside the answers themselves

- **B** has three substantive errors: (i) Morris et al.'s autonomy levels run **0–4**, not "0–5"; (ii) Anthropic's RSP and OpenAI's Preparedness Framework are **voluntary corporate policies, not "legally binding"**; (iii) it accepts the section's "threat model inverts" framing as correct. It also never addresses the falsifiable prediction — the section's most attackable paragraph — and misses the [27] bundling, unused [26], the title error, the ladder collision, and the Emerging-AGI contradiction. Its one real contribution, shared with F, is the ledger-tampering point (provenance stored inside the agent's environment is writable by the agent); "brilliant" in its verdict is flattery the task forbids.
- **H** has one clear factual error and two weaknesses: (i) it lists "Apollo Research (2024), 'In-Context Scheming Across Six Frontier Models'" as *the missing companion to [25]* and asks "why Meinke but not Apollo" — but **Meinke et al. [25] *is* the Apollo in-context-scheming paper**; there is no separate companion; (ii) it is internally inconsistent on [22], asserting the October 2025 update is "real" and its "jagged" characterization "accurate" while declaring the same document's arXiv ID unverifiable (a pattern: it also asserts "CHI 2025" for Feng and an uncheckable LeCun arXiv ID); (iii) its "Hit 1" **misreads "unattested"**: in the paper's own design machine-written hunks are attested (machine-signed), so a wholly machine-written file is not "the whole file unattested" — the real flaw is the instrumentation assumption, which D/E/F state correctly. H's genuine contributions: the **multi-agent delegation-chain gap** in a single `authorised_by` field (unique among answers) and camera-ready footnote discipline for cannot-verify items.
- **A** contains no factual errors I can find and is the only answer to apply all four task questions to every claim, but it misses **all four** of the sharpest verifiable catches above, and its uniform softening ("fix: hedge X") gives the author no priority ordering between fatal and cosmetic problems.
- **F** misses the Emerging-AGI contradiction and the title near-miss noted above; otherwise its security analysis is the deepest of the six.
- **E** is accurate but accepts the inversion too readily ("the threat model inversion is broadly correct") and under-develops the tamper/TCB problem; its unique catch — **Shavit et al., *Practices for Governing Agentic AI Systems***, the most on-point missing source for §10.2's authorisation claims — is valuable.

## 3. Live disagreements, and which side is right

- **Inverts vs. stacks:** A, D, F, H argue the threat model *expands* (developer-adversary persists; model-adversary is added). They are right; B and half of E are wrong. The dual-adversary case — malicious insider plus untrusted model — is the actual enterprise threat, and "inverts" hides it.
- **"Unattested share → 0":** D, E, F are right that it is false as stated — it holds only if every agent write channel is instrumented, which the paper's own 9% shell-bypass result disproves and which §10.4(2) itself says worsens with autonomy. The section's stated falsifier can therefore falsify a *true* thesis. H's contrary reading is the error described above.
- **The prediction:** F is sharpest — the authorisation/hunk ratio falls **by construction** (one authorisation, more hunks) and cannot falsify anything; A and E make adjacent granularity/control points; D supplies the decisive confound (channel coverage). H's "testable on existing data — a real strength" is the weakest position.
- **"Jagged":** cannot verify as a quote from [22]; D's fix — cite Dell'Acqua et al. (2023) for the term's provenance — is correct.
- **Missing sources:** the consensus picks are right — Sleeper Agents (Hubinger et al. 2024; B's arXiv:2401.05566 is correct) and Alignment Faking (B/D/E/F/A); **SLSA/in-toto/Sigstore** as the supply-chain prior art the "two-sided provenance" proposal largely reinvents (A/D/F — a security reviewer will recognize in-toto's attestation model and expect positioning); surveys or a counter-forecast for balance (D's Narayanan & Kapoor; E/H's Grace et al.); E's Shavit et al.; H's multi-agent caveat; B's RSP/Preparedness point once "legally binding" is corrected.

## 4. Strongest answer

**D**, with **F** a close second and **A** third. D is the only answer to catch the two verifiable errors a hostile reviewer will use to discredit the section (the [18] "Emerging AGI" self-contradiction and the METR title), is co-first on the ladder collision and the 50%-slide, is sharpest on the self-confounded falsifier ("the test as designed can falsify the thesis when the thesis is true"), picks missing sources well, and contains no errors in its own review. Its one gap — it under-develops the requirement that the ledger live in a trust boundary the agent cannot reach — is exactly F's central contribution, which is why F ranks second: the trusted-executor schema (`policy_id, authorised_by, trusted_executor_id, monitor_verdict, action_hash`, emitted by the executor, not the writer) and the "ratio true by construction" catch are the deepest structural contributions in the pool. A ranks third: most compliant with the per-claim protocol and correct on the layered-provenance / plural-threat-model reframes, but it finds none of the four fatal verifiable problems. E fourth (accurate, disciplined, one unique source, two reasoning gaps); H fifth (systematic, uniquely catches multi-agent, but ships a factual error, an internal inconsistency, and a misreading); B last (one real architectural point wrapped in three errors, with most of the section's actual problems unaddressed).

## 5. What a correct/safe final answer must include

1. **Verification discipline:** every 2025–2026 item (Time Horizon 1.1 numbers including "Claude Opus 4.5"; ARC-AGI-3 quotes; IASR Oct 2025 / Feb 2026 and "jagged"; all Davos quotes; Redwood 16-char / 67%; Anthropic Advisor tool; Feng arXiv ID and quote) marked *cannot verify pending primary-source check*, with archived links (PDF + access date, ideally hash) — never asserted accurate, never called false.
2. **The verifiable-now corrections:** (a) rewrite "not general intelligences by any published definition" — [18] itself rates current systems "Emerging" on the general track; (b) fix the METR title (drop "Software"); (c) pick one autonomy ladder (Feng's, since §10.2 uses it), footnote the other, and explicitly flag that the two orderings of consultant/collaborator conflict; (d) keep "50% reliability" attached to every horizon claim and cut "unattended" / "may already be here"; (e) soften or support "most-cited"; (f) split bundled [20]/[21]/[22]/[27], cite or remove unused [26] and the unused Altman / 2026-report items, add [3] to the list; (g) move the internal wiki citation out of the public paper.
3. **Named unstated assumptions of the section:** full channel instrumentation; informed (non-rubber-stamp) human approval; signing keys and hooks outside the agent's reach; single-agent deployments; METR trend extrapolating and transferring to the reader's task distribution; journalism quotes being verbatim; an internal wiki note being citable publicly.
4. **Reasoning reframes:** (a) replace "unattested share → 0" with "unlogged machine writes become the residual risk," citing the paper's own 9% result; (b) replace the monotonic prediction with pre-registered, falsifiable metrics (attested-write coverage vs. new tools, hook-tamper rate, out-of-policy actions per task-hour) and drop the authorisation/hunk ratio as vacuous-by-construction; (c) retitle "inverts" to "expands/stacks" (dual adversary); (d) delete "the consequence is exact"; (e) state that signatures authenticate records, not informed approval, and threat-model the approval channel itself; (f) require the ledger, keys, and hooks to sit outside the untrusted writer's reach (trusted executor / sandbox / attestation), citing SLSA/in-toto as prior art; (g) flag the single-agent assumption and the multi-agent delegation-chain gap.
5. **Minimum missing sources:** Sleeper Agents, Alignment Faking, Shavit et al., SLSA/in-toto, one survey or counter-forecast (Grace et al. or Narayanan & Kapoor), Dell'Acqua et al. for "jagged"; optionally scalable oversight (debate/IDA) and correctly characterized RSPs/Preparedness.
6. **A one-line verdict on shippability.**

**Verdict:** D is the strongest review (sole catcher of the [18] "Emerging AGI" self-contradiction and the METR title error, sharpest on the self-confounded falsifier), F and A follow; §10 itself is directionally sound but not shippable until its verifiable errors are fixed, every 2026 number and quote is archived or cut, the prediction is redesigned, and the ledger is moved into a trust boundary the untrusted writer cannot reach.

### minimax/minimax-m3 reviews
# Overall assessment

**§10 is not bulletproof as written.** The largest risks are not just future-dated citations:

1. The opening claim contradicts the paper’s own [18].
2. METR’s title is wrong, and the load-bearing 2026 figures cannot be verified.
3. The section combines two non-equivalent autonomy taxonomies.
4. The central prediction is not entailed by the autonomy frameworks and is self-confounded.
5. §10.2 says unattested writes fall as autonomy rises, while §10.3–10.4 say autonomous, untrusted models create more write channels.
6. The proposed provenance record is treated as a security mechanism, but an untrusted model may be able to tamper with the same records it causes to be emitted.
7. The threat model does not simply “invert”; the human adversary remains and other principals must be added.
8. Reference [3], cited in §10.4, is missing from the supplied bibliography.

The section also makes unsupported rhetorical claims such as “most-cited,” “the people building them say,” “rare event,” and “the consequence is exact.”

# 1. Independent fact-check

## 10.1 opening claims

> “current systems, which are not general intelligences by any published definition.”

**Verdict: inaccurate as an absolute statement.**

The paper’s own [18] is a published definition/operationalization under which some current frontier systems can be discussed as “Emerging AGI.” That does not establish that those systems are generally intelligent, but it directly defeats the phrase “by any published definition.”

A defensible replacement is:

> “The measurements above concern contemporary systems, not a single field-wide category called AGI. Morris et al. classify some current frontier systems at an ‘Emerging’ level under their criteria [18]; that classification is framework-specific. This section does not adopt it as a universal test.”

> “The people building them say general intelligence is near.”

**Verdict: overgeneralized.**

A few selected leaders do make near-term claims, but the same passage quotes Yann LeCun saying that current LLM training will not reach human-level intelligence. There is no defined sample, date, or survey.

Replace with:

> “Selected frontier-lab leaders have made divergent public statements about the timing and likely path to broadly capable systems [28].”

> “The benchmarks that try to measure it say the gap is still visible.”

**Verdict: benchmark-dependent rather than field-wide.**

METR, ARC-AGI, and the International AI Safety Report measure different constructs. A gap in one evaluation is not evidence of a general AGI gap. Use:

> “Several current evaluations report substantial but task- and benchmark-specific gaps in long-horizon software work, novel-task adaptation, and autonomous operation [20]–[22].”

> “The field has no agreed definition.”

**Verdict: broadly accurate only if narrowed.**

There is no single definition accepted across the field, but this should be supported by multiple genuinely different frameworks, for example:

- Legg and Hutter, “Universal Intelligence: A Definition of Machine Intelligence” (2007);
- Chollet [21];
- Morris et al. [18];
- Pei Wang, “On Defining Artificial Intelligence” (2019);
- Murray Shanahan, “Talking About AGI” (2020).

Do not write “there are no definitions.”

## METR claim

> “the most-cited operational yardstick for autonomous capability”

**Verdict: unsupported.**

Remove “most-cited.” The metric is influential, but no citation-count method is supplied and “operational yardstick for autonomous capability” is not a defined category.

> “tracks the length of software tasks a system completes with 50 % reliability.”

This is accurate in kind, but it should be more precise. METR’s time horizon is an estimate, for a particular task distribution, of the human-completion time at which a model has approximately a 50% chance of success. It is not simply the duration of tasks that a model always completes.

The cited arXiv paper is also misnamed. The canonical title is:

> Thomas Kwa et al., *Measuring AI Ability to Complete Long Tasks*, arXiv:2503.14499 (2025).

It is not *Measuring AI Ability to Complete Long Software Tasks* in the supplied reference.

The following January 2026 claims are **cannot verify** from the available material:

- the exact quotation “around every 7 months over the period 2019 to 2025”;
- growth from 170 to 228 tasks;
- Claude Opus 4.5 at 320 minutes;
- the interval 170–729 minutes;
- the quotation “still very wide”;
- the statement that “few remaining tasks defeat the newest models.”

Before publication, verify:

- the exact model and configuration;
- whether 170 and 228 are directly comparable task counts;
- the regression and endpoint dates;
- whether the interval is a confidence interval, credible interval, bootstrap interval, or another quantity;
- the sampling and task-selection procedure;
- the exact number of tasks implied by “few remaining tasks”;
- the source sentence for every quotation.

The title of the cited paper, as written, is therefore not correctly attributed.

## The “day-long” inference

> “systems that complete day-long tasks unattended arrive within the planning horizon of any team reading this”

This is not supported by the METR evidence.

Problems:

- A 7-month historical fit is not a forecast.
- A 50% time horizon is not unattended reliability.
- “Any team reading this” has no defined planning horizon.
- If the quoted 170–729-minute interval is authentic, it does not cover a 1,440-minute threshold. A wide interval cannot by itself support the assertion that a day-long capability is “already here.”
- A task’s duration is not identical to autonomy.

Use:

> “If the reported historical trend were to extrapolate, task-completion horizons could become operationally relevant to some teams within a multi-year planning horizon. This is a conditional extrapolation, not an observation of unattended day-long operation, and the current intervals are too wide to support a precise arrival date.”

## ARC-AGI-3

The following claims are **cannot verify**:

- the 2026 launch;
- “100 % human-solvable”;
- “as long as there is a gap between AI and human learning, we do not have AGI”;
- that the launch-time gap was “large.”

The phrase “100% human-solvable” is especially underspecified. It could mean:

- every task was solved by at least one human;
- every task was solved by a particular human sample;
- every task was solved by all tested humans;
- every task was solvable under an unlimited time budget.

“Human-solvable” must not be confused with “solved by the average human in the benchmark’s reference time.”

The quotation is not a field-wide definition of AGI. It is, if verified, an ARC Prize or benchmark-specific operational stance. Attribute it explicitly as such.

“Gap was large” requires a numerical comparison, human baseline, sample size, learning budget, and evaluation protocol. Otherwise remove it.

Chollet’s 2019 paper is real and correctly attributed. The ARC-AGI-2 and ARC-AGI-3 entries must be split into separate references and separately verified.

## International AI Safety Report

The following are **cannot verify**:

- the exact October 2025 title and arXiv identifier;
- the February 3, 2026 publication;
- the report’s exact characterization of the capability profile as “jagged”;
- the specific report wording on coding, mathematics, and autonomous operation.

If “jagged” is retained, quote it with a page or section locator. If it is only a paraphrase, remove quotation marks and cite the relevant report page. Dell’Acqua et al., *Navigating the Jagged Technological Frontier* (2023), is an appropriate source for that concept, but it is not a substitute for checking the report’s own wording.

The 2025 update and 2026 report must be separate references. The 2026 report is not needed merely because it appears in the bibliography.

## Davos claims

The Fortune article and the quotations are **cannot verify** from the available material.

The paper needs:

- a direct URL;
- a primary panel recording, transcript, or official WEF source where possible;
- exact quotation punctuation;
- the surrounding question and answer;
- clarification of whether “within the decade” means by 2030 or within ten years;
- the qualifiers surrounding Amodei’s coding and research predictions;
- the exact context of LeCun’s “never” statement.

A news article is acceptable as a secondary source, but “reported by Fortune” is safer than presenting text as a verified transcript quotation.

## Amodei and AI 2027

> “a country of geniuses in a datacenter”

The phrase and the October 2024 essay are real to the best of my knowledge. However, the essay does not thereby establish a generally accepted definition of AGI. It is a metaphor or characterization of “powerful AI,” not a formal operational definition.

Use “describes” or “characterizes,” not “defines,” unless the essay explicitly provides a formal test and criteria.

The April 2025 date and exact edition of *AI 2027* are **cannot verify** in the available record if they fall outside the reviewer’s knowledge horizon. Its proper role is:

> “AI 2027 is a scenario written by interested forecasters, not a measurement or empirically calibrated forecast.”

The Altman reference is unused. Remove it unless the paper actually discusses Altman.

## Morris et al. [18]

The source is real and the performance/generality/autonomy distinction is substantially accurate.

The canonical title is generally cited as:

> Morris et al., *Levels of AGI: Operationalizing Progress on the Path to AGI*, arXiv:2311.02462 (2023).

The extra “for” in the supplied bibliography and the precise “ICML position paper” venue description should be checked against the final PMLR record.

The taxonomy is approximately:

- no AI;
- AI as a tool;
- AI as a consultant;
- AI as a collaborator;
- AI as an expert;
- AI as an agent.

“Autonomy is a deployment choice constrained but not fixed by capability” is a fair synthesis, but it should be labeled as an interpretation unless quoted directly.

## Feng et al. [19]

The exact arXiv entry, taxonomy, and quotation are **cannot verify**:

> “can be treated as a deliberate design decision, separate from its capability”

If retained, verify the original paper and remove quotation marks if it is not exact.

The bigger problem is taxonomic. Morris’s sequence includes **consultant before collaborator** and does not have “operator” or “approver” as its named autonomy levels. Feng’s list is different. These frameworks are not automatically equivalent.

The section cannot say it is “stated against these autonomy levels” while moving between the two ladders without a crosswalk. Choose one framework for the analysis, preferably Morris [18] alone unless [19] can be independently verified.

# 2. §10.2: provenance and autonomy

## Contradictory claim

> “the unattested share is mostly the human’s hand”

This is not established. “Unattested” is undefined, and the paper’s own 9% shell result is attributed to an agent writing through a different channel. If “unattested” means all writes without a recorded producer, an autonomous agent’s unlogged writes count too.

Define separate quantities:

- **unattested write:** a write not observed by the trusted recording boundary;
- **unverified human origin:** a write not supported by direct human evidence;
- **unverified machine origin:** a machine write not authenticated;
- **unauthorized action:** an action outside recorded human scope;
- **out-of-policy action:** an action violating a recorded policy;
- **monitor-verified:** a monitor has judged the recorded evidence, not that the action is certainly safe.

> “the pull-request check earns its keep by finding it”

This assumes the check measured detection efficacy. The 9% result demonstrates a bypass, not necessarily a successful detection rate. Replace it with:

> “The pull-request hook detects a subset of writes; the shell result shows that a material fraction of writes can bypass the hook.”

## “The human stops typing bytes”

This is not a consequence of the autonomy frameworks. Humans can continue to:

- edit code directly;
- write specifications and tests;
- configure tools;
- review plans;
- intervene during execution;
- repair outputs;
- make design and policy decisions.

Use a qualified statement:

> “At some higher-autonomy deployments, direct human editing may decline while authorization, constraint-setting, and review become more prominent.”

## “Unattested share trends toward zero”

This is the section’s central logical error. It contradicts §10.3–10.4, where the model is untrusted and autonomous systems can invoke more tools, subprocesses, scripts, and external services.

The claim is also definition-dependent. If a human authorizes an entire task, every hunk does not become individually human-attested. If the denominator is “bytes not individually signed by a human,” there is no reason for it to fall merely because a machine wrote more bytes.

The correct point is not that unattested bytes disappear. It is:

> “The provenance system must add authorization, policy, execution, monitor, and outcome evidence while retaining artifact-level provenance.”

## The proposed `authorised_by` field

The field is a reasonable design proposal, but it is not self-evidently “natural.”

A human signature proves that a key signed a record. It does not establish:

- informed consent;
- comprehension;
- absence of coercion;
- that the recorded policy was enforced;
- that the agent stayed within scope;
- that the result is correct or safe.

The person who launched a task is not necessarily the person with authority to approve it. Distinguish at least:

- `requested_by`;
- `authorized_by`;
- `executed_by`;
- `acted_on_behalf_of`;
- `monitored_by`.

A minimum record should bind:

- task and policy identifiers;
- authorized scope and resource limits;
- policy hash;
- expiry and revocation state;
- environment or sandbox measurement;
- model, harness, tool, and monitor versions;
- exact action and artifact hashes;
- sequence or tamper-evident log position;
- delegation identity and scope in multi-agent settings.

The word “owner” should not be used as a synonym for “authorizer.” An account owner, operator, authorizer, beneficiary, and legal decision-maker can be different people.

## Internal wiki note

The “owner-attestation note” is not an independently auditable external source. If the repository is public, cite a version, commit hash, author, and date. Otherwise move it to an implementation appendix or remove it from a research paper.

It can support a design choice, not a general conclusion about provenance.

## The falsifiable prediction

> “the unattested share per pull request should fall monotonically … and the ratio of authorisation records to hunk records should fall with it”

This is not a safe or meaningful falsification of the thesis.

Reasons:

- Longer tasks may create more channels, retries, human interventions, and external side effects.
- Task duration is not autonomy level.
- Instrumentation coverage may change as tools are added.
- One authorization per long task can produce more hunks, making the ratio fall by construction.
- The ratio is controlled by record granularity and says little about safety or authority.
- A flat share could result from good coverage, not failure of the thesis.
- A falling share could result from a weaker denominator or broader authorization scope.

Replace it with a preregistered experiment under fixed conditions.

For example:

- Hold task class, tool policy, model version, and trusted recorder constant.
- Measure **write-attestation coverage** independently:
  `writes observed by trusted recorder / all writes`.
- Measure **human-unverified share**:
  `writes lacking direct evidence of human origin / all writes`.
- Measure **machine-unlogged share**:
  `unlogged machine writes / all writes`.
- Measure **out-of-policy action rate per task-hour**.
- Measure **recorder-tamper or disable attempts**.
- Stratify by autonomy level, task length, and channel.

The defensible hypothesis is conditional:

> “Under stable task types and a trusted mediator that observes all write paths, a higher chosen autonomy level is associated with a lower human-unverified write share, provided machine-unlogged writes and out-of-policy actions do not increase.”

Do not use monotonicity unless the authors specify a longitudinal design, minimum sample, effect size, and controls.

# 3. §10.3: AI control

## What is accurate

[23] Greenblatt et al., *AI Control: Improving Safety Despite Intentional Subversion*, is real and correctly attributed.

[25] Meinke et al. is real. The paper supports carefully worded claims about elicited in-context scheming in specified experimental settings. It does not prove that production models routinely possess durable strategic goals or that a model will naturally tamper with a Git ledger.

[29] Bengio et al. is a real *Science* article from 2024 and supports a normative argument for stronger oversight as capability increases. It is not direct empirical proof of a particular ledger architecture.

[31] Burns et al. is real, but weak-to-strong generalization is related to scalable oversight, not itself an AI-control protocol.

## “The threat model inverts”

The narrow comparison is useful:

- §4.1 treats a human as potentially adversarial and the recording machine as a scribe.
- [23] studies a strong model as potentially adversarial and uses trusted components to constrain it.

But the threat model does not invert globally. The human adversary remains relevant, and the secure design must include:

- malicious or compromised developers;
- compromised accounts and keys;
- model strategic behavior;
- tool and harness compromise;
- monitor blindness or error;
- prompt injection and hostile external inputs;
- replay and delegation attacks;
- tampering with the VCS or recorder.

The correct heading is:

> **The threat model expands: a potentially untrusted model is added to the existing human, supply-chain, and infrastructure threat model.**

The body’s “two-sided provenance” already admits this plural model. “Layered provenance” or “multi-party provenance” is more accurate because it contains at least human, machine, and monitor evidence.

## Untrusted advice and the API claim

The following are **cannot verify**:

- the July 27, 2026 Redwood post;
- the 16-character limit;
- the approximately 67% capability-gap recovery;
- the SWE-bench Verified result;
- the Anthropic “Advisor tool” documentation and its security properties.

If retained, “67% of the capability gap” is not self-defining. It requires:

- the exact numerator and denominator;
- absolute model scores;
- confidence intervals or uncertainty;
- model versions;
- benchmark version and contamination controls;
- number of attempts and sampling;
- whether the comparison is success rate, score, or normalized gap.

Even if Anthropic offers an executor/advisor-shaped feature, architectural similarity does not establish the same trust assumptions, isolation, or safety guarantee as a control protocol. The current wording overclaims equivalence.

## Signatures and the trusted computing base

A signature by an untrusted model is not automatically trustworthy. If the model can access the signing key, it can sign arbitrary records. Likewise, a machine-signed hunk proves that some principal possessed a key; it does not prove that the process was correctly identified unless the key is isolated.

The architecture should place the recorder and executor in a trusted computing boundary outside the model’s unmediated write authority:

- a trusted executor mediates actions;
- exclusive keys sign observed actions;
- a remote or separately protected append-only log stores events;
- environment measurements bind the log to a policy and software state;
- tamper evidence, replay protection, key rotation, and revocation are present.

A TPM alone does not guarantee this. Remote attestation, expected measurements, exclusive key handling, and an isolated verifier are needed.

The record should state the **trust tier per action or role**, not assign a vague global trust label to a whole model. A model may be untrusted to write code but acceptable to propose a plan inside a tightly constrained executor.

## NoHumanWrite

The statement:

> “NoHumanWrite … is the first leg of that record”

must be scoped. The name cannot establish:

- that all write paths are covered;
- that the machine identity is trusted;
- that authorization was enforced;
- that the monitor observed the right evidence;
- that the record is tamper-resistant;
- that this is the first such system.

At most:

> “NoHumanWrite is an artifact-level component in the proposed system; it records the absence of a directly observed human write on the covered path. It is not, by itself, a control protocol.”

The claim that adoption of the first leg will determine the later schema is speculative and cuts both ways: a weak schema adopted now can create lock-in. Replace it with an explicit extensibility requirement.

# 4. §10.4

> “Statistics cannot attribute authorship”

This is too absolute. Statistical methods can provide probabilistic evidence, but they are not cryptographic authorship proof and can fail under distribution shift or deliberate evasion.

> “More capable writers approach it faster and can be asked to leave it on purpose.”

Sadasivan et al. supports a narrower claim about the difficulty of detecting machine-generated text as distributions become less distinguishable and about some adversarial transformations. It does not by itself establish the universal claim about more capable writers.

The likely intended source is Sadasivan et al., *Can AI-Generated Text be Reliably Detected?*, arXiv:2303.11156 (2023), but **[3] is absent from the supplied references**. That source cannot be treated as fully verified from the paper’s bibliography. The final paper must include the complete citation and state the precise result being used.

Replace the whole paragraph with:

> “Statistical generation detection provides a triage signal rather than authorship proof. Its reliability can degrade under distribution shift, paraphrasing, and deliberate evasion. Cryptographic write-time provenance addresses a different problem: it can authenticate an artifact or action when the recording boundary and signing keys are trusted, but it still does not prove that the artifact is correct, safe, or compliant.”

> “Layer 3 is a triage aid today and nothing at all tomorrow.”

Remove this. A detector may remain useful as a weak signal even when it cannot be a proof mechanism.

> “The place to record provenance therefore moves from the tool to the environment”

This is directionally useful but must be made threat-model-aware. The environment is not automatically trusted merely because it is “outward.”

Use:

> “The provenance choke point expands to mediated environment boundaries: the execution API, sandbox, file system, container or VM boundary, Git index, and deployment pipeline. These boundaries must be controlled by a trusted executor or recorder, not merely placed in the same environment that the untrusted model can modify.”

> “The AI-control literature reaches the same conclusion about monitoring”

This is an analogy, not an identity of conclusions. AI-control literature generally motivates placing enforcement and monitoring in a trusted scaffold. It does not automatically establish which Git schema is required.

> “The human’s remaining contribution is authorisation and review”

This is too narrow. Human contributions may include:

- task and acceptance-criteria design;
- decomposition;
- policy and constraint specification;
- environment and tool selection;
- exception handling;
- intervention;
- accountability and escalation.

Logging those actions can make them legible, but logging does not ensure informed approval, meaningful oversight, or resistance to automation bias.

# 5. Reference and citation integrity

The final version must address all of the following:

1. Correct [20]’s title.
2. Verify the exact title and venue of [18]; the canonical title is generally *Levels of AGI: Operationalizing Progress on the Path to AGI*.
3. Split [21] into separate references for Chollet, ARC-AGI-2, and ARC-AGI-3.
4. Split [22] into separate references for the October 2025 update and the 2026 report.
5. Split [27] into separate references for Amodei, Altman, and AI 2027.
6. Remove Altman if unused.
7. Remove [26] or use it; it is currently unused.
8. Add the complete [3] reference.
9. Verify every direct quotation against the primary text, with a page, section, or timestamp.
10. Give the exact statistical meaning of “interval.”
11. Archive every 2025–2026 source or remove it if it cannot be verified.
12. Do not state an access date after the actual release date.
13. Distinguish a primary source, a preprint, a news report, an expert synthesis, an essay, and a scenario.

# 6. Review of the supplied answers

## Strongest answer: Answer A

Answer A is the strongest overall because it:

- covers every major subsection;
- consistently separates fact, interpretation, and design proposal;
- is strongest on the difference between layered provenance and byte-level provenance;
- correctly rejects the universal “threat model inverts” claim;
- identifies security properties that signatures do not provide;
- offers the broadest and most useful set of concrete fixes;
- appropriately calls out unsupported superlatives, the weak falsifiable prediction, and the conflation of “attested,” “authorized,” and “safe.”

It is not fully reliable. In particular, it:

- misses the direct conflict between the opening claim and [18];
- misses that the METR title is wrong;
- does not note that [3] is omitted from the supplied references;
- sometimes treats a source as real when the user’s cutoff rule calls for “cannot verify”;
- recommends a broad source laundry list without distinguishing essential sources from merely relevant ones.

Answer A is therefore the best foundation, but not a camera-ready audit.

## Answer D

Answer D is the best fact-checker for two important catches:

- Morris [18] can be cited against the opening claim;
- the METR arXiv title is wrong.

It also correctly identifies the autonomy-taxonomy collision and the shell-bypass confounder.

Its weaknesses:

- “frontier LLMs” collectively at Level 1 is too broad; the correct claim is that *some* systems are classified that way under [18]’s criteria.
- Its proposed substitution of an “80% time horizon” is itself unverified. Do not introduce an 80% metric unless the original METR source explicitly defines and reports it.
- It does not sufficiently specify the trusted executor and tamper boundary.
- It misses the missing [3] reference.

## Answer F

Answer F is the strongest technical security rewrite. It correctly identifies that:

- a model in the same environment may tamper with the ledger;
- provenance should be emitted by a trusted executor;
- a Git note is not automatically a control protocol;
- the unattested-share prediction is confounded;
- the authorization-to-hunk ratio is not a safety metric.

Its main omissions are the [18] contradiction, the missing [3] reference, and the precise correction of the METR title. It also uses a loose alternative title for the International AI Safety Report; the camera-ready must use the exact verified official title.

## Answer B

Answer B has useful threat-model instincts but contains a serious factual error:

> “RSPs and Preparedness Framework are the actual, legally binding operational definitions of autonomy and threat levels.”

They are not inherently legally binding and are not field-wide definitions of AGI. They are company governance policies and risk-management frameworks. They may be contractually relevant in particular arrangements, but the paper must not present them as law or consensus.

Answer B also overstates two technical points:

- Human authorization is not “useless”; it is useful for scope, accountability, and policy, but it is not proof of safety or compliance.
- A TPM does not by itself ensure that an agent cannot rewrite an audit trail. Remote attestation, exclusive keys, measured software, and an isolated verifier are required.

Answer B is useful on infrastructure isolation, but it misses the taxonomy and source-title errors that D and F catch.

## Answer E

Answer E gives a sound basic warning against unverified future claims, but it is too shallow for a bulletproof review. It misses:

- the direct [18] contradiction;
- the METR title error;
- the mixed autonomy taxonomies;
- the missing [3] entry;
- the full untrusted-writer tampering problem;
- the non-equivalence of an API shape and a control guarantee.

It also says the threat-model inversion is “broadly correct,” whereas the safer conclusion is that only the narrow trust-role comparison holds.

## Answer H

Answer H is overconfident about several 2025 sources that must be marked “cannot verify” under the task’s stated rule. It also:

- treats forecast essays such as Cotra and Aschenbrenner as “top-tier” evidence;
- names vague or potentially nonexistent AGI-definition sources such as “Mitchell et al. … Defining AGI”;
- treats AI 2027 omission as selection bias rather than a scenario that can be cited only as a forecast;
- calls a bundled bibliography a “formatting violation in every major venue,” which is an overstatement;
- says human contribution is “the only contribution that matters,” which is not established;
- misses the [18] and METR-title issues;
- underplays the missing [3] reference.

## Answers C and G

Both are incomplete responses and cannot be evaluated as substantive audits.

# 7. What a correct and safe final answer must include

A public-release version should contain all of the following.

## A. A scope and definition paragraph

State that:

- there is no single field-wide AGI definition;
- [18] is a framework-specific classification;
- current systems are not being assigned a universal “not AGI” label;
- autonomy, capability, authority, and trust are separate variables;
- no AGI date is predicted.

## B. A precise empirical record

For every benchmark result:

- exact title, author, date, URL or DOI;
- model/version/configuration;
- task suite and version;
- number of tasks;
- evaluation budget and sampling method;
- definition of success;
- statistical interval and method;
- exact quotation and location;
- distinction between measured result and extrapolation.

Remove the METR, ARC-AGI-3, Redwood, Davos, Anthropic, and 2026 report claims unless each is verified from a primary source.

## C. A single autonomy framework

Do not use Morris’s and Feng’s labels interchangeably.

Choose one:

- use [18] alone, with its tool/consultant/collaborator/expert/agent levels; or
- verify [19] and use its role-based ladder, explicitly stating that it is a different framework.

If the paper needs both, provide a separate non-equivalence table rather than a false continuum.

## D. A threat-model table

At minimum, include:

| Principal | Possible failure |
|---|---|
| Human/developer | insider attack, negligence, coercion, compromised account |
| Model | strategic behavior, unauthorized action, tampering |
| Harness/tool | compromise, unintended channel, privilege abuse |
| Monitor | blind spot, false acceptance, prompt injection, collusion |
| External input | indirect prompt injection or malicious content |
| Credentials/logs | key theft, replay, forgery, deletion, clock manipulation |
| VCS/container | rewrite, bypass, unlogged write, cross-agent delegation |

## E. Layered provenance

Retain all of these:

1. artifact provenance;
2. execution and action provenance;
3. authorization provenance;
4. policy and constraint provenance;
5. monitor provenance;
6. review provenance;
7. outcome and external-state provenance;
8. delegation provenance for multi-agent systems.

The central conclusion should be:

> “As autonomy increases, authorization, policy, execution, monitor, and outcome provenance become as important as byte-level artifact provenance. They do not replace it.”

## F. A trusted recording architecture

Specify:

- a trusted executor or mediator outside the model’s unmediated write authority;
- exclusive signing keys;
- exact model, harness, tool, policy, and environment versions;
- signed action and artifact hashes;
- an append-only or tamper-evident external log;
- replay protection, revocation, and time/sequence integrity;
- a monitor bound to the exact evidence it inspected;
- delegation scope and expiry for multi-agent systems.

A local Git hook is not enough if the agent can edit the repository through a shell, IDE, subprocess, API, CI job, or another container.

## G. A real experiment

The final paper should pre-register:

- task classes and sample sizes;
- autonomy levels;
- model and tool versions;
- trusted-recorder coverage;
- the denominator for every metric;
- confounder controls;
- expected effect sizes;
- confidence intervals;
- treatment of retries, merges, rebases, external artifacts, and manual edits;
- out-of-policy action and tamper-attempt rates.

Replace the monotonic “auth records / hunk records” claim with the controlled metrics described above.

## H. Essential missing sources

A hostile reviewer will expect at least these categories.

### AGI definitions

- Legg and Hutter, “Universal Intelligence: A Definition of Machine Intelligence” (2007).
- Pei Wang, “On Defining Artificial Intelligence” (2019).
- Murray Shanahan, “Talking About AGI” (2020).
- Chollet [21] and Morris [18] for genuinely different operational frameworks.

Use the OpenAI Charter only as an example of a corporate AGI definition, not as consensus.

### Progress and agent evaluation

- Grace et al., “When Will AI Exceed Human Performance?” (2018).
- Grace et al., “Thousands of AI Authors on the Future of AI” (2024).
- Kapoor et al., *AI Agents That Matter* (2024).
- RE-Bench or a comparable realistic long-horizon agent evaluation.
- Dell’Acqua et al. if the word “jagged” is retained.

The 7-month METR fit should not be treated as a calibrated timeline forecast.

### Deception and control

- Greenblatt et al., *AI Control* [23].
- Meinke et al. [25].
- Greenblatt et al., *Alignment Faking in Large Language Models* (2024).
- Hubinger et al., *Sleeper Agents* (2024).
- Greshake et al. on indirect prompt injection.
- Burns et al. [31] as related oversight work, not as a control protocol.

### Provenance and trusted execution

- Torres-Arias et al., *in-toto: Providing Farm-to-Table Guarantees for Software Supply Chains*, USENIX Security (2019).
- SLSA and Sigstore.
- IETF RATS, RFC 9334, if remote attestation is claimed.
- W3C PROV if a general provenance ontology is being proposed.

Anthropic’s Responsible Scaling Policy and OpenAI’s Preparedness Framework may be useful as company governance sources, but they are not “legally binding” AGI definitions and should not substitute for technical or scientific evidence.

## I. Remove the section’s overclaims

At minimum remove or rewrite:

- “any published definition”;
- “most-cited”;
- “the people building them”;
- “the field says”;
- “rare event worth finding”;
- “the unit moves”;
- “the consequence is exact”;
- “the threat model inverts”;
- “within the planning horizon of any team”;
- “may already be here”;
- “Layer 3 is … nothing at all tomorrow”;
- “the human’s remaining contribution is authorisation and review.”

The most important substantive conclusion is sound only when narrowed:

> **As autonomy rises, the provenance requirement becomes layered; the threat model becomes plural; and the model must be added to, not substituted for, the existing set of potentially adversarial principals.**

**Verdict: Not safe for public release until the 2025–2026 sources and quotations are verified, the opening and taxonomy errors are corrected, the metrics and falsification test are redesigned, and the provenance architecture is made explicitly trusted, multi-party, and tamper-resistant.**

---
> Hand to Claude (orchestrator) for synthesis + final-watch, then Arnaud approves.
