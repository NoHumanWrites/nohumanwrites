#!/usr/bin/env bash
# NoHumanWrite — one-time setup on a developer machine.
# Makes a DEDICATED ed25519 signing key (not your SSH login key), registers it as an
# allowed signer, and runs a smoke test of the hook + verifier.  Re-runnable.
set -euo pipefail
NHW_DIR="$HOME/.nhw"; KEY="$NHW_DIR/id_nhw"; HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$NHW_DIR"
if [ ! -f "$KEY" ]; then
  ssh-keygen -q -t ed25519 -N "" -C "nhw-$(hostname -s)" -f "$KEY"
  echo "signing key created: $KEY"
else
  echo "signing key present: $KEY"
fi
printf 'nhw namespaces="nhw" %s\n' "$(cut -d' ' -f1-2 "$KEY.pub")" > "$NHW_DIR/allowed_signers"
echo "allowed signers: $NHW_DIR/allowed_signers"
# smoke test inside this repository
T="$HERE/eval/hooktest.txt"
printf '# hook smoke test\nline one of the attested block\nline two of the attested block\n' > "$T"
python3 - "$T" <<'EOF' | python3 "$HERE/nhw/hook.py"
import json, sys
p = sys.argv[1]
print(json.dumps({"session_id": "smoke", "tool_name": "Write",
                  "tool_input": {"file_path": p, "content": open(p).read()}}))
EOF
echo "--- agent-written file:"; python3 "$HERE/nhw/verify.py" "$HERE" "$T"
printf 'a line a human typed after the agent finished\n' >> "$T"
echo "--- after a human appends one line:"; python3 "$HERE/nhw/verify.py" "$HERE" "$T"
echo "done — the hook will now sign every Write/Edit Claude Code makes inside a git repository."
