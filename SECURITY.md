# Security model — read before trusting a number

NoHumanWrites is a positive-evidence ledger. Three sentences govern everything it prints.

1. **A record proves that a hunk passed through a signing channel on a machine holding the key. It does not prove who decided the hunk's content.** A developer can route hand-typed text through the hook; a prompt of "write exactly these lines" yields an attested hunk that is human-authored in every useful sense. The key authenticates the channel, not the author.
2. **The absence of a record asserts nothing.** An unattested line was typed by hand, or written through a channel with no hook, or written before the hook existed, or reflowed by a formatter. The tool never labels a line "human", and a build that does has left the design.
3. **The per-line fallback is content-based, not authorship-based.** When a whole signed hunk no longer matches, surviving lines are covered by their signed per-line hashes, each hash at most as many times as it was signed. A human who retypes an agent's line character for character is counted as attested; that is a known and accepted limit of hashing text.

## Trust root

The allowed-signers file is yours: `~/.nhw/allowed_signers` or `--signers FILE`. A repository's own `.nhw/allowed_signers` is ignored unless you pass `--trust-repo-signers`, and the verifier then prints where the trust came from. A repository that chooses its own trust root can attest anything; a pull-request check must never read the pull request's keyring.

Each record names its signer by fingerprint; the verifier checks the signature against that key only, so the field is bound to the key that actually verified. Records that fail schema validation, exceed size caps, or fail verification are counted and reported, never scored.

## What v0.1 defends against, and what it does not

- Defended: forgetting which lines came through the agent; casual after-the-fact editing of the ledger by someone without the key; a malicious repository trying to supply its own keys or crash the verifier with hostile records.
- Not defended: a developer who holds the key and wants to lie (they can sign anything, or delete records); an agent with control of the machine, which can do the same. Both need a trust anchor outside the writer's reach: records mirrored at write time to a verifier or a transparency log, or signing by a trusted executor rather than the client. The record format allows it; v0.1 does not ship it. See the paper, §4.1 and §10.3.
- Append-only is a convention until the ledger head is anchored in signed commits or a log.

## Privacy

Records carry a session id and a machine key fingerprint. On a small team, "unattested" identifies a person by elimination. The verifier reports lines and files, never names; aggregate per repository, not per developer; and do not record prompts unless the team opts in.

## Reporting

Security issues: open a private report to the maintainer (Plus de Fun Agency, Geneva) rather than a public issue.
