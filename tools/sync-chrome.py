#!/usr/bin/env python3
"""
sync-chrome.py — push a change to the shared header/footer out to every page.

WHY THIS EXISTS
Each page in this site is a complete, standalone HTML file, which is what makes
them easy to read and edit. The cost of that choice is that the navigation and
the footer are repeated in all of them. This script is the fix: edit the
templates once, run it, and every page is updated.

HOW TO USE
    1. Edit  tools/_chrome/header.html  and/or  tools/_chrome/footer.html
       (use {{PREFIX}} wherever a link needs "../" on sub-pages and "" on the
       home page — the script fills it in).
    2. Run:   python3 tools/sync-chrome.py
       Add --check to report what would change without writing anything.

WHAT IT TOUCHES
Only the regions between these markers, which are already in every page:
    <!-- BEGIN SHARED HEADER -->   ...   <!-- END SHARED HEADER -->
    <!-- BEGIN SHARED FOOTER -->   ...   <!-- END SHARED FOOTER -->
Everything outside those markers — all of your actual page content — is left
exactly as it is. The script also sets aria-current="page" on the nav link for
whichever page it is writing, so the current page stays highlighted.
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.path.join(REPO, "tools", "_chrome")

BLOCKS = [
    ("header", "<!-- BEGIN SHARED HEADER -->", "<!-- END SHARED HEADER -->"),
    ("footer", "<!-- BEGIN SHARED FOOTER -->", "<!-- END SHARED FOOTER -->"),
]


def pages():
    """Every index.html in the site, ignoring tooling and version control."""
    found = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", ".github", "tools", "assets", "files")]
        if "index.html" in filenames:
            found.append(os.path.join(dirpath, "index.html"))
    return sorted(found)


def slug_and_prefix(path):
    """'research/index.html' -> ('research', '../');  'index.html' -> ('home', '')."""
    rel = os.path.relpath(path, REPO)
    parts = rel.split(os.sep)[:-1]
    if not parts:
        return "home", ""
    return parts[-1], "../" * len(parts)


def render(template, prefix, slug):
    out = template.replace("{{PREFIX}}", prefix)
    # Highlight the current page in the navigation.
    out = re.sub(r'\s+aria-current="page"', "", out)
    if slug == "home":
        target = 'data-nav="home"'
    else:
        target = 'data-nav="%s"' % slug
    if target in out:
        out = out.replace(target, target + ' aria-current="page"', 1)
    else:
        # Sub-pages of Research are not themselves nav items; mark Research.
        out = out.replace('data-nav="research"', 'data-nav="research" aria-current="page"', 1)
    return out


def main():
    check = "--check" in sys.argv
    templates = {}
    for name, _, _ in BLOCKS:
        p = os.path.join(CHROME, name + ".html")
        if not os.path.exists(p):
            sys.exit("missing template: %s" % p)
        templates[name] = open(p, encoding="utf-8").read()

    changed = 0
    for path in pages():
        slug, prefix = slug_and_prefix(path)
        html = open(path, encoding="utf-8").read()
        original = html

        for name, begin, end in BLOCKS:
            body = render(templates[name], prefix, slug)
            # Keep only what is between the markers in the template itself.
            bi, bj = body.find(begin), body.find(end)
            inner = body[bi + len(begin): bj] if bi != -1 and bj != -1 else "\n" + body + "\n"

            i, j = html.find(begin), html.find(end)
            if i == -1 or j == -1:
                print("  ! %s: %s markers not found — skipped" % (os.path.relpath(path, REPO), name))
                continue
            html = html[:i + len(begin)] + inner + html[j:]

        if html != original:
            changed += 1
            print("  %s %s" % ("would update" if check else "updated", os.path.relpath(path, REPO)))
            if not check:
                open(path, "w", encoding="utf-8").write(html)

    if changed == 0:
        print("  all pages already in sync")
    print("\n%d of %d page(s) %s" % (changed, len(pages()), "would change" if check else "changed"))


if __name__ == "__main__":
    main()
