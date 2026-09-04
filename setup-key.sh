#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# NoHumanWrites — one-time setup on a developer machine.
# Makes a DEDICATED ed25519 signing key (never your SSH login key), registers it in
# YOUR allowed-signers file (merging, not clobbering), and runs a smoke test in a
# throwaway git repository.  Re-runnable.  Needs OpenSSH 8.0+ (ssh-keygen -Y).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
NHW_DIR="$HOME/.nhw"; KEY="$NHW_DIR/id_nhw"; SIGNERS="$NHW_DIR/allowed_signers"

# OpenSSH 8.0+ knows `-Y sign`; older builds answer "unknown option -- Y"
if ssh-keygen -Y sign 2>&1 | grep -qi "unknown option\|illegal option"; then
  echo "ssh-keygen -Y is not available (OpenSSH 8.0+ required): $(ssh -V 2>&1)"; exit 1
fi
mkdir -p "$NHW_DIR"; chmod 700 "$NHW_DIR"
if [ ! -f "$KEY" ]; then
  ssh-keygen -q -t ed25519 -N "" -C "nhw-$(hostname 2>/dev/null | cut -d. -f1)" -f "$KEY"
  echo "signing key created: $KEY"
else
  echo "signing key present: $KEY"
fi
PUB="$(cut -d' ' -f1-2 "$KEY.pub")"
touch "$SIGNERS"; chmod 600 "$SIGNERS"
grep -qF "$PUB" "$SIGNERS" || printf 'nhw namespaces="nhw" %s\n' "$PUB" >> "$SIGNERS"
echo "allowed signers (yours, user-owned): $SIGNERS"

# smoke test in a throwaway repository, never in this project
T="$(mktemp -d 2>/dev/null || mktemp -d -t nhw)"; trap 'rm -rf "$T"' EXIT
git init -q "$T/repo"; F="$T/repo/hooktest.txt"
printf '# hook smoke test\nline one of the attested block\nline two of the attested block\n' > "$F"
python3 - "$F" <<'EOF' | python3 "$HERE/nhw/hook.py"
import json, sys
p = sys.argv[1]
print(json.dumps({"session_id": "smoke", "tool_name": "Write",
                  "tool_input": {"file_path": p, "content": open(p, encoding="utf-8").read()}}))
EOF
echo "--- agent-written file:"; python3 "$HERE/nhw/verify.py" "$T/repo" "$F" | tail -2
printf 'a line a human typed after the agent finished\n' >> "$F"
echo "--- after a human appends one line:"; python3 "$HERE/nhw/verify.py" "$T/repo" "$F" | tail -2
echo "done — the hook signs every Write/Edit Claude Code makes inside a git repository (install: python3 $HERE/nohumanwrites.py setup)."
echo "The key proves the CHANNEL, not the author; keep ~/.nhw backed up; see SECURITY.md."
