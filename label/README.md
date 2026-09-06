# AI Grade — the label

Spec v0.2 · 6 September 2026 · Plus de Fun Agency, Geneva · part of [NoHumanWrites](https://github.com/NoHumanWrites/nohumanwrites)

A number on a piece of work that says how much of it came through a signed machine channel. Petrol pumps show an octane number; gold is stamped with its purity. AI Grade works the same way: the number is the label, and anyone with the public key can recompute it.

One sentence governs the whole spec: **the key proves the channel, not the author.** If a person dictates every line in a prompt, or has an agent copy a hand-written file back into place, those lines still count as attested. The grade says the bytes came through the channel. Who decided them sits upstream of the record, and the label makes no claim about it.

## The scale

The grade is the share of scored units that a signed record still covers, as a whole number, rounded down. 99.6 % is grade 99, never 100. The bands give the number a name, the way "18 carat" and "24 carat" name bands of gold purity.

| Grade | Band | What it means |
|---|---|---|
| **100** | Pure | Every line, paragraph, verse or bar sits in a signed machine hunk that still matches. Nothing typed by hand after the machine finished, nothing through an unlogged channel. |
| **90–99** | High | The machine channel produced the work. The rest, at most one unit in ten, is listed by location in the report the label links to. |
| **50–89** | Mixed | Most of the work came through the channel, and a large minority did not. The seal carries the word "Mixed" so nobody mistakes it for a High grade. |
| **0–49** | no label | Most of the work did not come through a signed channel. The check still prints its report, and the report is the useful part. |

Why these lines. 100 is exact. 90 is Not By AI's "90 % rule" pointed the other way: they ask a creator to *estimate* that at least 90 % of the content is human, we *count* that at least 90 % came through the channel. 50 is where the claim "a machine channel produced this work" stops being true. Below it there is nothing to certify.

## Two verification levels

The grade says how much of the work is attested. The level says how hard the attestation is to fake.

| Level | Who signs | Shipped |
|---|---|---|
| **Level 1 · self-signed** | The author's machine key, through the harness hook, at the moment each hunk is written. The verifier uses its own trust root (`~/.nhw/allowed_signers`), never the repository's. | Yes, v0.1 |
| **Level 2 · anchored** | The ledger head (its hash, byte length, record count and the git commit) is signed with the same key and recorded in Sigstore's public Rekor log by `nohumanwrites.py anchor`, by hand or from a git post-commit hook (`setup --anchor`). The receipt lives in `.nhw/anchors.jsonl` and is committed. At check time the tool verifies continuity (the anchored prefix of the ledger still hashes to the anchored value), the signature against your own trust root, and, online, that Rekor still serves the same hash and signature at the recorded index. | Yes, v0.2 (2026-09-06). |
| **Level 3 · trusted executor** | The hunks are produced or countersigned by a component outside the writing model's reach, the design the paper's §10.3 calls for once the writer itself may be an adversary. Three designs in `label/level3.md`. | Partly. **Local isolation** ships (`setup --level3`): the harness sandbox denies the model's shell the signing key, and the hook records an `executor` claim per write. It is self-reported, so it never appears on the badge; the check prints it as a separate line. Remote countersigning and the full trusted executor are not built. |

A Level 1 grade says "the key-holder's tools recorded this". A Level 2 grade says "this ledger's history cannot have been rewritten without leaving a gap": anything changed or deleted before the anchor breaks the prefix hash, and the anchor itself sits in a public log the key-holder cannot edit. Neither level makes a false record true, and a key-holder can still sign anything. Taking the key-holder out of the loop is Level 3, not yet built. The seal names its level so a reader knows which of the three they are looking at, and the check prints how many records were appended since the last anchor, since those are not yet covered.

## Units, denominator, scope

- **Unit:** a line for code, a paragraph for prose, a line and stanza for verse, a bar or measure for sheet music. Detected from the file, or forced with `--profile`.
- **Denominator:** every scored unit under the path named on the seal. Generated and vendored files are not excluded; if you want them out, name a narrower path and say so.
- **Attested:** the unit sits in a signed hunk whose hash still matches, or, when the hunk as a whole no longer matches, the unit's own signed per-line hash matches, each hash usable at most as many times as it was signed. A pasted copy of a signed line is attested; a formatter's reflow is edited or unattested depending on how much survives. A signed one-line edit inside a table block currently reads as unattested (known limit).
- **Scope:** a seal covers the path it names and nothing else. A seal without a path is invalid.

## Keys

The trust root is the verifier's own `allowed_signers` file. A stolen key signs as its owner until the owner's line in that file is replaced; revocation is that edit, and the spec defines no PKI. Records name their key by fingerprint. On a small team a fingerprint identifies a person by elimination, which is why reports aggregate per repository and never print names.

## The three guarantees

Each one is a sentence a verifier can check by running the tool, not a promise to take on faith.

1. **Every attested unit passed through a named machine channel and was signed when it was written.** The record carries the harness, the model and the session in its `producer` field, and a signature from a key the verifier chose to trust.
2. **Every unit that did not is listed.** The label links to a report that names each unattested and each edited unit by file and position. Nothing hides behind the number.
3. **Anyone with the public key gets the same number.** The check is deterministic on the ledger and the file bytes. The grade is a claim you can re-derive, not one you must believe.

## What the grade does not guarantee

- **Not quality, correctness or safety.** A machine-written bug is an attested bug. The grade counts provenance, nothing else.
- **Not that no human decided the content.** A prompt of "write exactly these lines" produces an attested hunk that is human-authored in every useful sense. The key proves the channel, not the author (see `SECURITY.md`).
- **Not the absence of human judgement.** The prompt, the constraints and the review are human, by design. The grade counts bytes; the decisions sit upstream of it, and that is where they belong.
- **Not a statement about any person.** The ledger records a machine key, never a name. The report says "unattested", never "written by X".

## How it differs from the marks that already exist

| Mark | Direction | How it is earned | Verifiable by a third party |
|---|---|---|---|
| Not By AI (2023–) | human-made | self-estimate, at least 90 % human | no; "not an AI detection tool", the creator is accountable |
| Authors Guild "Human Authored" (2025) | human-made | the author certifies the book was not made with AI | no; declaration |
| iHeartMedia "Guaranteed Human" (2025) | human-made | announced on air | no; announcement |
| Spotify "Verified" (2026) | human-made | the platform decides what it deems AI-generated | no; the platform's judgement, method not public |
| EU AI Office icons (10 June 2026) | AI-made | voluntary icons for the Article 50 marking duty; signed metadata for media, in practice C2PA | for media with a manifest, yes; text has no manifest profile |
| **AI Grade** (this spec) | AI-made, by share | a signed ledger, counted at check time, one number from 0 to 100 | yes; anyone with the public key reruns the check |

The EU icons and this label are complementary. The icons tell the public that a machine was involved. The grade tells a reviewer, an auditor or a reader how much, and exactly which parts, with a signature.

## How to earn it

```bash
python3 nohumanwrites.py setup                              # once: hook + dedicated key
# ... work with the agent inside the repository ...
python3 nohumanwrites.py check <path> --label               # grade, band, dated badge, wording
python3 nohumanwrites.py check <path> --label --seal g.svg  # the same, plus the numbered seal
```

`--label` is refused when there is no signed ledger, when the evidence is unsigned transcripts, when the trust root is the repository's own keys, and below grade 50. In each case the tool says why. A label with no ledger behind it is exactly the kind of mark this spec exists to replace.

## How to display it

- The badge, from the tool, carries the grade, the band and the check date. A badge without a date is stale by definition.
- The seal (`--seal`) is generated with the number on its face and may sit on a README, a paper, a book page or a site, next to a link to the report (`--json` output, or a published provenance card). `label/ai-grade.svg` is the seal this directory earned.
- Wording: "AI Grade 97 · High · `src/` · checked 2026-09-06 · Level 1". Never "human-free", never "no human involved", never "written by AI" as a claim about a person's authorship, never a claim about a named person.

## Terms of use

The mark is free to display on any repository, document or page that passed the check at the time the grade was generated. It may not be displayed on work with no ledger, on work below grade 50, or with a number older than the last change to the work. The spec, the bands and the seal design are maintained by Plus de Fun Agency and change only with a version bump to this file. Names of people never appear in a label, a report or a registry entry.

## On the name

v0.1 of this spec (earlier on 6 September 2026) called the mark "Guaranteed AI", with "Pure AI" for the 100 % grade, as the inverse of iHeartMedia's "Guaranteed Human". The eight-model review objected that the name promised authorship the ledger cannot prove. v0.2 renames it AI Grade: the label is the number, and a number promises only what it measures. The label lives at nohumanwrites.org/label.

## Why this is worth a label

The full argument, with sources, is in `label/whitepaper.md`. In one paragraph: writing that comes through a logged machine channel arrives with a prompt, a diff, a log, a test run and a signature; writing through any other channel arrives with none of those. The largest software organisations report that the machine now produces most of their new code, with engineers reviewing and accepting it. The attested share is the one per-unit record of that division a third party can check. It is a coverage statistic of logged channels, not a measure of autonomy or capability, and the white paper says so. A grade makes the number public, scoped and, above all, checkable.
