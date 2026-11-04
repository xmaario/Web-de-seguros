"""Quality checks for the generated site. Run from the repo root: python3 tools/check.py
Exits with code 1 if any check fails."""
import glob, json, os, re, sys

errors = []
pages = sorted(glob.glob("*.html") + glob.glob("guides/*.html"))
titles = {}
for f in pages:
    t = open(f, encoding="utf-8").read()
    if len(re.findall(r"<h1[ >]", t)) != 1:
        errors.append(f"{f}: must have exactly one <h1>")
    m = re.search(r"<title>(.*?)</title>", t)
    titles.setdefault(m.group(1) if m else "", []).append(f)
    d = re.search(r'name="description" content="([^"]*)"', t)
    if not d or not d.group(1).strip():
        errors.append(f"{f}: missing meta description")
    elif f != "404.html":
        import html as _h
        if len(_h.unescape(d.group(1))) > 160:
            errors.append(f"{f}: meta description longer than 160 characters")
        if m and len(_h.unescape(m.group(1))) > 65:
            errors.append(f"{f}: <title> longer than 65 characters")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(block.replace("<\\/", "</"))
        except Exception as e:
            errors.append(f"{f}: invalid JSON-LD ({e})")
    for href in re.findall(r'href="([^"#]+)', t):
        if href.startswith(("http", "mailto")):
            continue
        p = href.lstrip("/") if href.startswith("/") else os.path.normpath(os.path.join(os.path.dirname(f), href))
        if p in (".", ""):
            continue
        if not any(os.path.isfile(c) for c in (p, p + ".html", os.path.join(p, "index.html"))):
            errors.append(f"{f}: broken link {href}")
    if re.search(r"\[(CARRIER|PLACEHOLDER|DOMAIN|OWNER|NIF)", t):
        errors.append(f"{f}: visible placeholder text")
for title, files in titles.items():
    if len(files) > 1:
        errors.append(f"duplicate <title> in {files}")

# Word count for guides (800-1000 words, excluding the closing note)
for f in sorted(glob.glob("tools/content/guide-*.html")):
    body = open(f, encoding="utf-8").read().split("\n---\n", 1)[1]
    body = re.sub(r'<p class="note">.*?</p>', "", body, flags=re.S)
    words = len(re.sub("<[^>]+>", " ", body).split())
    if not 800 <= words <= 1000:
        errors.append(f"{f}: {words} words (must be 800-1000)")

print(f"Checked {len(pages)} pages.")
if errors:
    print("\n".join("ERROR " + e for e in errors))
    sys.exit(1)
print("All checks passed.")
