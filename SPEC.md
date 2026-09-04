# NoHumanWrites ledger — proposed format v0.1

File: `.nhw/attest.jsonl` at the repository root. One JSON object per line, append-only. Committed with the code, or pushed to the verifier; either works.

```json
{"v":1,
 "ts":"2026-09-04T14:02:11Z",
 "path":"src/router.py",
 "hunk":{"start":120,"end":148,"lines":29,"sha256":"<sha256 of the normalised hunk text>",
         "line_sha":["<first 16 hex of sha256 of each stripped line ≥ 12 chars>", "..."]},
 "producer":{"kind":"agent","harness":"claude-code","model":"claude-fable-5-1","session":"c76f7980-…"},
 "signer":"ed25519:<public key fingerprint>",
 "sig":"<base64 signature over the canonical JSON of every field above>"}
```

Rules.

1. A record asserts only that a machine produced the hunk. Absence of a record asserts nothing about who did.
2. The signing key belongs to the developer's machine, one per harness install. The verifier holds the public keys, as with SSH.
3. Hunk text is normalised before hashing: trailing whitespace stripped, line endings unified, tabs preserved. Formatters that change more than whitespace produce a new hunk and a new record; that is intended.
4. The verifier, for a pull request: for each added or modified line, find the most recent record whose hunk covers it and whose signature verifies; report covered bytes over changed bytes and list the uncovered ranges. When a whole hunk no longer matches (a later edit, a formatter), the signed `line_sha` list still covers the individual lines that survived unchanged; lines that were reflowed are reported uncovered, which is intended.
5. Prose profile: same schema, `hunk` becomes `{"paragraph": n, "sha256": …}` over the normalised paragraph.
6. A record never carries a human identity beyond the machine key. Reviewers see "unattested", not a name.

Harness adapters emit one record per write. For Claude Code that is a `PostToolUse` hook matching `Write|Edit`; the tool input already contains the exact text.
