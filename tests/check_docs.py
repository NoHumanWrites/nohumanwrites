#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The published pages: every local link and anchor resolves, every external link answers.
Run:  python3 tests/check_docs.py     (exit 0 = pass; NHW_DOCS_OFFLINE=1 skips the external requests)
"""
import os, sys, glob, urllib.request, urllib.error
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = set(); self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        if tag == "link" and "stylesheet" not in (a.get("rel") or ""):
            return  # preconnect and icon hints are not destinations
        for key in ("href", "src"):
            if a.get(key):
                self.links.append((tag, a[key]))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 nohumanwrites-docs-check"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == 2:
                return None


def main():
    pages = {}
    for path in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
        p = Page(); p.feed(open(path, encoding="utf-8").read()); pages[os.path.basename(path)] = p
    errors, checked, unverified = [], 0, []
    external = set()
    for name, p in pages.items():
        for tag, link in p.links:
            if link.startswith(("mailto:", "data:", "javascript:")):
                continue
            if link.startswith(("http://", "https://")):
                external.add(link); continue
            target, _, frag = link.partition("#")
            target = target or name
            if target not in pages and not os.path.exists(os.path.join(DOCS, target)):
                errors.append(f"{name}: {link} -> {target} does not exist"); continue
            if frag and target in pages and frag not in pages[target].ids:
                errors.append(f"{name}: {link} -> no id '{frag}' in {target}")
            checked += 1
    if os.environ.get("NHW_DOCS_OFFLINE"):
        print(f"docs: {checked} local links ok, {len(external)} external links skipped (NHW_DOCS_OFFLINE)")
    else:
        for url in sorted(external):
            code = fetch(url)
            if code is None or code in (404, 410):
                errors.append(f"external {url}: {'no answer' if code is None else code}")
            elif code >= 400:
                unverified.append(f"{url}: {code}")  # bot walls (403/429) answer, so the destination exists
            checked += 1
        print(f"docs: {checked} links checked across {len(pages)} pages" + (f"; {len(unverified)} answered with a bot wall: " + ", ".join(unverified) if unverified else ""))
    for e in errors:
        print("FAIL " + e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
