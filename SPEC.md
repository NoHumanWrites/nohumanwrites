# NoHumanWrites ledger — proposed format v0.1

File: `.nhw/attest.jsonl` at the repository root. One JSON object per line, append-only. Committed with the code, or pushed to the verifier; either works.

```json
{"v":1,
 "ts":"2026-09-04T14:02:11Z",
 "path":"src/router.py",
 "hunk":{"start":120,"end":148,"lines":29,"sha256":"<sha256 of the normalised hunk text>",
         "line_sha":["<first 16 hex of sha256 of each stripped line ≥ 12 chars>", "..."]},
 "producer":{"kind":"agent","harness":"claude-code","model":"claude-fable-5-1","session":"c76f7980-…"},
 "signer":"ssh-ed25519:SHA256:<public key fingerprint>",
 "sig":"<base64 of the ASCII-armoured `ssh-keygen -Y sign -n nhw` signature over the canonical JSON (sorted keys, no spaces, UTF-8) of every field above>"}
```

Rules.

1. A record asserts only that a machine produced the hunk. Absence of a record asserts nothing about who did.
2. The signing key belongs to the developer's machine, one per harness install. The verifier holds the public keys, as with SSH.
3. Hunk text is normalised before hashing, identically in the hook and the verifier (`nhw/common.py`): bytes decoded as UTF-8 (non-UTF-8 files are not scored), CRLF and CR folded to LF, trailing whitespace stripped per line, indentation preserved. `line_sha` entries are over the *stripped* line (indentation removed), first 16 hex of SHA-256, only for lines of 12+ characters. Formatters that change more than whitespace produce a new hunk and a new record; that is intended.
4. The verifier, for a pull request: for each added or modified line, take the union of all records for that path whose signature verifies against a trusted key *and* whose hunk still matches the file (the hunk may have moved); report covered lines over changed lines and list the uncovered ranges. When a whole hunk no longer matches (a later edit, a formatter), the signed `line_sha` list covers surviving lines, newest record first, each hash at most as many times as it was signed; lines that were reflowed are reported uncovered, which is intended.
4b. Trust root: the verifier reads an allowed-signers file owned by the verifier (`~/.nhw/allowed_signers` or `--signers`), never the repository's own, unless explicitly told to; it verifies each record only against the key named in `signer`, so that field is bound to the verifying key. Malformed records (schema, size caps) are counted and ignored. Three output states: attested / unattested / unverifiable.
4c. The hook widens a partial-line edit to whole lines before hashing, records only text still present in the file, appends under a file lock, and does nothing outside a git repository or for paths that resolve outside it.
5. Beyond code, every record also carries `units`: `{"profile": "prose|verse|abc|musicxml|code", "sha": [...], "sentence_sha": [...]}`. The profile is chosen from the file (extension, then content: an `X:`/`K:` header means ABC notation, `<score-partwise>` means MusicXML, short blank-line-separated lines mean verse). Units are what a reader edits: paragraphs for prose (whitespace-collapsed), lines within stanzas for verse, bars for ABC (header fields and chord symbols excluded), `<measure>` elements for MusicXML. `sha` is the 16-hex prefix of SHA-256 of each unit; `sentence_sha` (prose only) covers sentences of 25+ characters so a paragraph with one changed sentence is reported as *edited* rather than lost. The verifier scores non-code files by unit, budgets each signed hash by how many times it was signed, and for exported documents (.docx/.epub/.odt, unpacked to paragraphs) matches against the whole ledger rather than one path.
5b. Records made by `nohumanwrites.py import` carry `producer.kind = "pasted-ai"` and `producer.harness` = the label the person gave (claude.ai, chatgpt, suno…): they attest what the person *received*, signed at receipt, so later human changes surface. The signature still proves the channel, not the origin; the label is the person's statement.
6. A record never carries a human identity beyond the machine key. Reviewers see "unattested", not a name.

Harness adapters emit one record per write. For Claude Code that is a `PostToolUse` hook matching `Write|Edit`; the tool input already contains the exact text.

## Anchors (Level 2) — `.nhw/anchors.jsonl`, format v0.1

One JSON object per anchor, append-only, committed with the code. Written by `nohumanwrites.py anchor` (by hand, or from the git post-commit hook that `setup --anchor` installs).

```json
{"head":{"v":1,"kind":"nhw-anchor","ts":"2026-09-06T19:55:17Z",
         "ledger_sha256":"<sha256 of .nhw/attest.jsonl as it stood>","ledger_bytes":179973,"records":103,
         "commit":"<git HEAD at anchor time, or null>","signer":"ssh-ed25519:SHA256:<fingerprint>"},
 "sig":"<base64 of the ASCII-armoured `ssh-keygen -Y sign -n file` signature over the canonical JSON of head>",
 "rekor":{"server":"https://rekor.sigstore.dev","uuid":"<entry uuid>","logIndex":2742870568,
          "integratedTime":1788724517,"logID":"<log id>"}}
```

Rules. (a) The head is uploaded to Rekor as a `rekord` entry with an `ssh`-format signature; Rekor stores the sha256 of the head and the signature, not the head bytes, so verifiers recompute the hash from the recorded head. (b) The namespace is `file` because Rekor's ssh verifier hardcodes it; per-hunk records keep `nhw`. (c) A verifier checks continuity (the first `ledger_bytes` bytes of today's ledger still hash to `ledger_sha256`), the signature against its OWN trust root, and, online, that Rekor serves the same hash, signature and index. Any failure drops the label to Level 1 and says why; records appended after the last anchor are reported as "not yet anchored". (d) Anchoring makes history tamper-evident. It does not make a false record true; the key-holder can still sign anything (paper §3, Levels).

## Executor claim (Level 3, local) — `producer.executor`, format v0.1

When the harness's sandbox denies the model's shell any read of the signing key (`setup --level3` writes the block into `<repo>/.claude/settings.json`: `sandbox.enabled`, `allowUnsandboxedCommands: false`, the key directory under `credentials.files` with `mode: deny`), the hook adds to each record's `producer`:

```json
"executor": {"kind": "harness-hook", "isolation": "sandbox-denies-key", "self_reported": true}
```

Rules. (a) The hook reads the repository's and the user's settings at write time, project keys winning, and writes the field only when all three conditions hold. (b) The field is a claim by the hook about its environment, not a signature by a second party; it is never used for the grade or the badge. `check` reports the count of records carrying it on a separate line marked self-reported. (c) A verifiable Level 3 (remote countersignature, trusted executor) will add a second `signer` and `sig` pair; see `label/level3.md`.
