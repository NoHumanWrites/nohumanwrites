# Guaranteed AI — the label

Spec v0.1 · 6 September 2026 · Plus de Fun Agency, Geneva · part of [NoHumanWrites](https://github.com/NoHumanWrites/nohumanwrites)

A mark for work that came through a signed machine channel. It is backed by a ledger anyone can re-check, and every unit that did not come through the channel is listed next to the number. Where the human-made labels say "a human made this, trust us", this one says "a machine channel produced this, verify it".

One sentence governs the whole spec: **the key proves the channel, not the author.** A person who dictates every line in a prompt, or has an agent copy a hand-written file back into place, earns an attested hunk. The label reports that the bytes came through the channel; who decided them sits upstream of the record. The names *Pure AI* and *Guaranteed AI* are the maintainer's choice and carry this caveat wherever they appear.

## The two grades

| Grade | Threshold | Meaning |
|---|---|---|
| **Pure AI** | 100 % of scored units attested | Every line, paragraph, verse or bar sits inside a signed machine hunk that still matches. Nothing was typed by hand after the machine finished, and nothing arrived through an unlogged channel. |
| **Guaranteed AI** | at least 90 % attested | The machine wrote the work. The remainder, at most one unit in ten, is listed by location in the report the label links to. |

Below 90 % there is no label. The check still prints its report, and the report is the useful part.

The 90 % figure mirrors the Not By AI "90 % rule", which asks a creator to *estimate* that at least 90 % of their content was made by humans. Ours is the same number pointing the other way, and it is measured, not estimated.

## Two verification levels

The grade says how much of the work is attested. The level says how hard the attestation is to fake.

| Level | Who signs | Shipped |
|---|---|---|
| **Level 1 · self-signed** | The author's machine key, through the harness hook, at the moment each hunk is written. The verifier uses its own trust root (`~/.nhw/allowed_signers`), never the repository's. | Yes, v0.1 |
| **Level 2 · anchored** | The ledger head is anchored in a transparency log (Sigstore Rekor), or the hunks are signed by a trusted executor that the writing model cannot reach. This is the design the paper's §10.3 calls for once the writer itself may be an adversary. | No. The record format allows it; nothing produces it yet. |

A Level 1 label says "the key-holder's tools recorded this". A Level 2 label will say "this ledger's history cannot have been rewritten without leaving a gap"; it does not make a false record true, and a key-holder can still sign anything. Taking the key-holder out of the loop needs a trusted executor that produces or countersigns the hunks, which is a third design and not yet built. The badge names its level so a reader knows which of the three they are looking at.

## Units, denominator, scope

- **Unit:** a line for code, a paragraph for prose, a line and stanza for verse, a bar or measure for sheet music. Detected from the file, or forced with `--profile`.
- **Denominator:** every scored unit under the path named on the badge. Generated and vendored files are not excluded; if you want them out, name a narrower path and say so.
- **Attested:** the unit sits in a signed hunk whose hash still matches, or, when the hunk as a whole no longer matches, the unit's own signed per-line hash matches, each hash usable at most as many times as it was signed. A pasted copy of a signed line is attested; a formatter's reflow is edited or unattested depending on how much survives. A signed one-line edit inside a table block currently reads as unattested (known limit).
- **Scope:** a badge covers the path it names and nothing else. A badge without a path is invalid.

## Keys

The trust root is the verifier's own `allowed_signers` file. A stolen key signs as its owner until the owner's line in that file is replaced; revocation is that edit, and the spec defines no PKI. Records name their key by fingerprint. On a small team a fingerprint identifies a person by elimination, which is why reports aggregate per repository and never print names.

## The three guarantees

Each one is a sentence a verifier can check by running the tool, not a promise to take on faith.

1. **Every attested unit passed through a named machine channel and was signed when it was written.** The record carries the harness, the model and the session in its `producer` field, and a signature from a key the verifier chose to trust.
2. **Every unit that did not is listed.** The label links to a report that names each unattested and each edited unit by file and position. Nothing hides behind the percentage.
3. **Anyone with the public key gets the same number.** The check is deterministic on the ledger and the file bytes. The label is a claim you can re-derive, not one you must believe.

## What the label does not guarantee

- **Not quality, correctness or safety.** A machine-written bug is an attested bug. The label counts provenance, nothing else.
- **Not that no human decided the content.** A prompt of "write exactly these lines" produces an attested hunk that is human-authored in every useful sense. The key proves the channel, not the author (see `SECURITY.md`).
- **Not the absence of human judgement.** The prompt, the constraints and the review are human, by design. The label counts bytes; the decisions sit upstream of it, and that is where they belong.
- **Not a statement about any person.** The ledger records a machine key, never a name. The report says "unattested", never "written by X".

## How it differs from the marks that already exist

| Mark | Direction | How it is earned | Verifiable by a third party |
|---|---|---|---|
| Not By AI (2023–) | human-made | self-estimate, at least 90 % human | no; "not an AI detection tool", the creator is accountable |
| Authors Guild "Human Authored" (2025) | human-made | the author certifies the book was not made with AI | no; declaration |
| iHeartMedia "Guaranteed Human" (2025) | human-made | announced on air | no; announcement |
| Spotify "Verified" (2026) | human-made | the platform decides what it deems AI-generated | no; the platform's judgement, method not public |
| EU AI Office icons (10 June 2026) | AI-made | voluntary icons for the Article 50 marking duty; signed metadata for media, in practice C2PA | for media with a manifest, yes; text has no manifest profile |
| **Guaranteed AI** (this spec) | AI-made | a signed ledger, checked at label time, threshold 90 % or 100 % | yes; anyone with the public key reruns the check |

The EU icons and this label are complementary. The icons tell the public that a machine was involved. This label tells a reviewer, an auditor or a reader exactly which parts, with a signature, for the reader's own benefit rather than as a warning.

## How to earn it

```bash
python3 nohumanwrites.py setup                 # once: hook + dedicated key
# ... work with the agent inside the repository ...
python3 nohumanwrites.py check <path> --label  # grade, badge and the wording to paste
```

`--label` is refused when there is no signed ledger, when the evidence is unsigned transcripts, when the trust root is the repository's own keys, and below 90 %. In each case the tool says why. A label with no ledger behind it is exactly the kind of mark this spec exists to replace.

## How to display it

- The badge, from the tool, carries the grade, the percentage and the check date. A badge without a date is stale by definition.
- The seal (`label/guaranteed-ai.svg`, `label/pure-ai.svg`) may sit on a README, a paper, a book page or a site, next to a link to the report (`--json` output, or a published provenance card).
- Wording: "Guaranteed AI · 97 % attested · `src/` · checked 2026-09-06 · Level 1". Never "human-free", never "no human involved", never "written by AI" as a claim about a person's authorship, never a claim about a named person.

## Terms of use

The mark is free to display on any repository, document or page that passed the check at the time the badge was generated. It may not be displayed on work with no ledger, on work below the threshold, or with a number older than the last change to the work. The spec, the thresholds and the seal files are maintained by Plus de Fun Agency and change only with a version bump to this file. Names of people never appear in a label, a report or a registry entry.

## On the name

"Guaranteed AI" is the deliberate inverse of "Guaranteed Human", the mark iHeartMedia put on its radio hosts in 2025. "Pure AI" names the 100 % grade. All `pureai.*` and `guaranteedai.*` domains were registered by others before this spec was written (checked 6 September 2026); the label lives at nohumanwrites.org/label.

## Why this is worth a label

The full argument, with sources, is in `label/whitepaper.md`. In one paragraph: writing that comes through a logged machine channel arrives with a prompt, a diff, a log, a test run and a signature; writing through any other channel arrives with none of those. The largest software organisations report that the machine now produces most of their new code, with engineers reviewing and accepting it. The attested share is the one per-unit record of that division that a third party can check. It is a coverage statistic of logged channels, not a measure of autonomy or capability, and the white paper says so. A label makes the number public, scoped and, above all, checkable.
