# NoHumanWrites: pointers for agents

- The checks are the ones in `.github/workflows/test.yml`; run the same steps before pushing.
- Provenance: the Claude Code hook signs Claude Code writes only. Text written through any other harness (Codex, Pi, a shell heredoc) is signed before commit with `python3 nohumanwrites.py import <file> --from <harness>`. CI holds `docs/` at 95% attested or above (`check --fail-under`), verified against `.nhw/allowed_signers`.
- Sandboxed runs: `NHW_TEST_NO_NET=1` skips the loopback Rekor fixture in `tests/test_ledger.py`; `NHW_DOCS_OFFLINE=1` skips the external requests in `tests/check_docs.py`.
- A PR body carries before/after evidence and a merge-danger line (one-way or two-way door); captures and receipts stay in the assigned evidence directory and are referenced from the body, as in PR #1.
- Once per clone: `python3 nohumanwrites.py setup --guard` installs the pre-commit guard (`nhw/precommit.py`); it refuses a commit that would drop `docs/` below the CI floor or leaves the ledger unstaged, and prints the `import` line to run. Worktrees share it.
