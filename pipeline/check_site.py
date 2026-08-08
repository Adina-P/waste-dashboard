"""Static integrity checks for the generated site: broken internal links,
missing assets, and authority-page/data consistency.

Run after pipeline/generate_site.py: python3 pipeline/check_site.py

This does NOT check visual/CSS correctness (contrast, layout, RTL rendering) —
those still need a look in the browser. It only catches broken references.
"""

import json
import os
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit

SITE_DIR = "site"
DATA_PATH = "site/data/waste.json"

LINK_ATTRS = {
    "a": "href",
    "img": "src",
    "script": "src",
    "link": "href",
}

EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "javascript:")


class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []  # (attr_value, line)

    def handle_starttag(self, tag, attrs):
        attr_name = LINK_ATTRS.get(tag)
        if not attr_name:
            return
        for name, value in attrs:
            if name == attr_name and value:
                self.links.append((value, self.getpos()[0]))


def find_html_files(root):
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".html"):
                yield os.path.join(dirpath, name)


def check_links():
    errors = []
    checked = 0
    pages = 0
    for html_path in find_html_files(SITE_DIR):
        pages += 1
        with open(html_path, encoding="utf-8") as f:
            content = f.read()
        parser = LinkExtractor()
        parser.feed(content)
        page_dir = os.path.dirname(html_path)
        for raw, line in parser.links:
            if raw.startswith(EXTERNAL_PREFIXES) or raw.startswith("#"):
                continue
            path_only = urlsplit(raw).path
            if not path_only:
                continue
            resolved = os.path.normpath(os.path.join(page_dir, path_only))
            checked += 1
            if not os.path.isfile(resolved):
                errors.append(f"{html_path}:{line}: broken link -> {raw} (resolved: {resolved})")
    return pages, checked, errors


def check_authority_pages():
    errors = []
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    slugs = {a["slug"] for a in data["authorities"]}
    existing = {
        name[:-5] for name in os.listdir(f"{SITE_DIR}/authority") if name.endswith(".html")
    }
    for slug in sorted(slugs - existing):
        errors.append(f"missing authority page for slug: {slug}")
    for slug in sorted(existing - slugs):
        errors.append(f"orphaned authority page with no data entry: {slug}")
    return len(slugs), errors


def main():
    pages, checked, link_errors = check_links()
    authority_count, authority_errors = check_authority_pages()

    errors = link_errors + authority_errors
    print(f"checked {checked} internal links across {pages} pages")
    print(f"checked {authority_count} authorities against site/authority/*.html")

    if errors:
        print(f"\n{len(errors)} problem(s) found:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("\nall checks passed")


if __name__ == "__main__":
    main()
