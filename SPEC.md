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
5. Prose profile: same schema, `hunk` becomes `{"paragraph": n, "sha256": …}` over the normalised paragraph.
6. A record never carries a human identity beyond the machine key. Reviewers see "unattested", not a name.

Harness adapters emit one record per write. For Claude Code that is a `PostToolUse` hook matching `Write|Edit`; the tool input already contains the exact text.
