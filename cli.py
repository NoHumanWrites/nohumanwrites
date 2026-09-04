#!/usr/bin/env python3
"""nhw — NoHumanWrites command line.

  nhw.py index                 build/refresh the attested-line index
  nhw.py file <path>... [--show]  attribute files against the index
  nhw.py git <path>...         git blame + trailer attribution
  nhw.py stat <path>...        statistical triage (weak signal)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nhw import attest, gitmode, stat

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    cmd, rest = argv[0], [a for a in argv[1:] if not a.startswith("--")]
    if cmd == "index":
        _, s = attest.load_index(rebuild=True); print(json.dumps(s, indent=1)); return 0
    if cmd == "file":
        pf, _ = attest.load_index()
        for p in rest:
            r = attest.attribute(p, pf)
            print(f"{p}: attested {r.get('attested_ratio',0):.0%} of {r.get('considered',0)} lines, "
                  f"unattested {len(r.get('unattested',[]))}")
            if "--show" in argv:
                for i, ln in r.get("unattested", [])[:60]: print(f"  {i:>5}: {ln}")
        return 0
    if cmd == "git":
        for p in rest: print(json.dumps(gitmode.attribute(p), default=str)); return 0
    if cmd == "stat":
        for p in rest: print(json.dumps(stat.profile(p), indent=1)); return 0
    print(__doc__); return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
