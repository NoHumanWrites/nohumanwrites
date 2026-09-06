# Level 3 — taking the key out of the writer's reach

Design note v0.1 · 6 September 2026 · Plus de Fun Agency, Geneva · part of the AI Grade label (`label/README.md`)

## The problem Level 3 exists for

Level 1 says "the key-holder's tools recorded this". Level 2 says "and the record has not been rewritten since". Neither says anything about a writer that holds the key. On a developer's machine today the writing model and the signing hook run as the same user. Whatever the hook can sign, the model's shell can sign too: it can read the private key, forge a record for text it never wrote through the hooked tool, and append it under a lock the hook itself would respect. The parent paper's §10.3 names the fix: the hunk must be produced or countersigned by a component outside the model's reach, a trusted executor in the sense of the AI-control literature. This note turns that sentence into three designs, says which one ships now, and is exact about what it does and does not prove.

Two adversaries stack here. The developer who wants a high number, and the model that wants one, or that is following an instruction hidden in something it read. Level 3 is about the second. Nothing in it stops the first, who can always type the bytes and route them through the hook.

## Three designs

**A. Local isolation through the harness sandbox.** The harness already runs the model's shell commands in an operating-system sandbox when told to: on macOS through Seatbelt, on Linux through bubblewrap. The sandbox applies to Bash commands and their child processes, and to nothing else; the hook is spawned by the harness on a tool event, not through the Bash tool, so it runs outside the sandbox. If the sandbox denies the model's shell any read of the signing key, then only the hook can sign, and the hook signs only what the harness reports it wrote. The hook can observe the settings that make this true and write that observation into each record. Cost: a settings block in the repository. Proof strength: self-reported by the hook, on the same machine, from configuration the model cannot edit through its shell but the human can edit at any time.

**B. Remote countersigning.** The hook forwards each record to a signer on another host, which checks the record against an independent copy of the harness's event stream and countersigns. The model's shell can reach the network but not the remote key. Proof strength: a third party can verify the countersignature. Weakness: the remote signer has to know that a record really came from a harness event and not from a shell command that imitates one, and today the harness gives it no way to know. Without an authenticated event stream the remote signer countersigns whatever it is sent, which is Level 1 with a longer cable. Not built.

**C. Trusted executor.** The untrusted model proposes; a trusted, weaker component executes every write and signs it; the model never holds a shell in the environment where the ledger lives. This is the protocol the control literature describes and the parent paper's §10.3 asks for. It is a change to the harness, not to this tool, and it is the only design under which a verifier learns something about the writer rather than about the key. Not built, and not buildable from outside the harness.

## What ships now: A, named honestly

`nohumanwrites.py setup --level3` writes a sandbox block into the repository's `.claude/settings.json`: the sandbox on, reads of `~/.nhw` denied to sandboxed commands, the escape hatch that retries a failed command outside the sandbox turned off, and the Rekor host allowed through the network proxy so anchoring keeps working. The harness protects that file from edits by sandboxed commands, so the model's shell cannot switch the block off.

The hook then checks, on every write, that the effective settings still say so. When they do, the record's `producer` gains an `executor` field:

```json
"executor": {"kind": "harness-hook", "isolation": "sandbox-denies-key", "self_reported": true}
```

When they do not, the field is absent, and the check reports how many records carry it. The label line stays at Level 2; a separate line says "executor: N of M records signed under sandbox isolation (self-reported)". The badge does not change. A number that a verifier cannot recompute does not belong on the badge.

## What A proves, and what it does not

It proves, to the person running the check on the same machine, that at the moment of each write the configuration denied the model's shell the key. That is worth having: it closes the one attack a Level 2 ledger cannot see, a forged record signed with the real key by the model's own shell.

It does not prove anything to a third party. The `executor` field is a claim written by the hook, and a hook that has been replaced writes whatever its replacement says. The holes, in order of size:

- **The human.** Anything typed at the harness's own shell prompt runs outside the sandbox. The developer adversary is untouched, by design.
- **The file-editing tools.** The sandbox governs shell commands. The harness's own write and edit tools are governed by permissions instead, and a permission mode that lets the model edit any file lets it edit the settings that define the sandbox. The harness refuses some of those edits on its own; this note does not rely on that.
- **The unsandboxed retry.** With the escape hatch on, a command that fails inside the sandbox may be retried outside it, where the key is readable. `setup --level3` turns the hatch off. A human can turn it back on.
- **Replacement of the hook.** The hook file lives in the tool's checkout, which the model can edit through the file tools. A replaced hook can write any `executor` field it likes.

Each hole is a place where the claim is only as good as the environment, which is the definition of self-reported. The field is named `self_reported` so that no reader mistakes it for more.

## The path to a verifiable Level 3

Design B becomes real the day the harness signs its own tool events, or exposes them through a channel the model's shell cannot write to. Then a remote signer can check that a record matches a genuine event before countersigning, and the countersignature is something a verifier can recompute from the remote public key. The ledger format already has room for it: a second signature on the record, a second signer field, and a Level 3 line on the badge. This tool will add the fields when there is something to put in them.

Design C is a harness architecture, and the parent paper's §10.3 lays out what its records must carry: which model, in which trust tier, under which monitor, on whose authority. When such a harness exists, this ledger is the audit-trail leg of it and nothing more.

## Terms of use for Level 3 claims

The words "Level 3" appear on a badge only when a third party can recompute the claim. Until then, the check prints the executor line with the word self-reported, and the spec, the site and the paper describe Level 3 as partly shipped: the local isolation of design A, and nothing else.
