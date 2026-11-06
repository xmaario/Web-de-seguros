"""Site generator: assembles the static HTML pages from tools/content/*.html.

Usage (from the repo root):  python3 tools/build.py
Output is plain static HTML written to the repo root; hosting needs no build step.
Add --html-links to keep .html links (for local static previews)."""
import os, sys, glob, re, json, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "content")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args else os.path.dirname(HERE)
# Clean URLs (no .html) for the live site; --html-links keeps .html for static previews.
CLEAN = "--html-links" not in sys.argv
SITE = "https://unpackinsurance.com"
BRAND = "UnpackInsurance"
AUTHOR = "Mario González Ordóñez"
ADSENSE = "ca-pub-XXXXXXXXXXXXXXXX"
OG_IMAGE = SITE + "/images/og-image.png"

NAV = [
    ("car-insurance.html", "Car Insurance"),
    ("home-insurance.html", "Home Insurance"),
    ("calculator.html", "Calculator"),
    ("guides/index.html", "Guides"),
    ("glossary.html", "Glossary"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

DISCLOSURE = (f"{BRAND} is not an insurance company or agency. We may receive compensation "
              "from partner providers, which can affect where and how products appear. "
              "Estimates are illustrative and not offers of coverage.")

LOGO_SVG = ('<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
            '<rect width="32" height="32" rx="8" fill="currentColor"/>'
            '<path d="M9 15.5h14V24H9z M9 15.5L6.5 11h7l2.5 4.5 2.5-4.5h7L23 15.5" fill="none" stroke="#fff" '
            'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>')

ART = {"Car insurance": "images/illustration-car.svg", "Home insurance": "images/illustration-home.svg"}

CUR = ' aria-current="page"'

AD_SLOT = ('<aside class="ad-slot" data-ad-key="{key}" aria-label="Advertisement" hidden>'
           '<p class="ad-label">Advertisement</p></aside>')


def parse(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    head, body = raw.split("\n---\n", 1)
    meta = {}
    for line in head.strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    meta["body"] = body.strip("\n")
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    meta["h1"] = re.sub("<[^>]+>", "", m.group(1)).strip()
    text = re.sub(r'<p class="note">.*?</p>', "", body, flags=re.S)
    text = re.sub("<[^>]+>", " ", text)
    meta["words"] = len(text.split())
    return meta


pages = [parse(f) for f in sorted(glob.glob(os.path.join(SRC, "*.html")))]
by_path = {p["path"]: p for p in pages}
articles = [p for p in pages if p.get("type") == "article"]
POPULAR = [
    "guides/how-much-car-insurance-do-you-need.html",
    "guides/what-is-full-coverage-car-insurance.html",
    "guides/what-does-homeowners-insurance-cover.html",
    "guides/home-insurance-deductibles-explained.html",
    "guides/why-did-my-car-insurance-go-up.html",
    "guides/do-you-need-flood-insurance.html",
]


def canonical(path):
    if path == "index.html":
        return SITE + "/"
    if path.endswith("index.html"):
        return SITE + "/" + path[: -len("index.html")]
    if CLEAN and path.endswith(".html"):
        path = path[:-5]
    return SITE + "/" + path


def version_assets(html_text):
    """Append ?v=<content hash> to illustration, CSS and JS URLs so browsers fetch new versions after changes."""
    import hashlib

    def fix(m):
        attr, url = m.group(1), m.group(2)
        local = os.path.normpath(os.path.join(OUT, url.lstrip("./").replace("../", "")))
        if not os.path.isfile(local):
            return m.group(0)
        h = hashlib.md5(open(local, "rb").read()).hexdigest()[:8]
        return f'{attr}="{url}?v={h}"'

    return re.sub(r'(src|href)="((?:\.\./|/)*(?:images/illustration-[a-z-]+\.svg|css/styles\.css|js/[a-z]+\.js))"', fix, html_text)


def clean_links(html_text):
    """Rewrite internal .html links to clean URLs (about.html -> about, guides/index.html -> guides/)."""
    if not CLEAN:
        return html_text

    def fix(m):
        attr, url, frag = m.group(1), m.group(2), m.group(3) or ""
        if url.startswith(("http:", "https:", "mailto:", "data:", "#")):
            return m.group(0)
        if url == "index.html":
            url = "./"
        elif url.endswith("/index.html"):
            url = url[: -len("index.html")]
        else:
            url = url[:-5]
        return f'{attr}="{url}{frag}"'

    return re.sub(r'(href)="([^"#]*?\.html)(#[^"]*)?"', fix, html_text)


def rel(prefix, target):
    return prefix + target


def read_time(meta):
    return max(1, round(meta["words"] / 230))


def nice_date(d):
    return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")


def guide_cards(prefix, items, heading_level=3):
    out = ['        <div class="card-grid">']
    for a in items:
        out.append(f'''          <article class="card card-link">
            <p class="card-eyebrow">{a["category"]}</p>
            <h{heading_level}><a href="{rel(prefix, a["path"])}">{a["h1"]}</a></h{heading_level}>
            <p>{html.escape(a["description"], quote=False)}</p>
            <p class="card-meta"><time datetime="{a["date"]}">{nice_date(a["date"])}</time> · {read_time(a)} min read</p>
          </article>''')
    out.append("        </div>")
    return "\n".join(out)


def expand_guides(body, prefix, current=None):
    def repl(m):
        cat, n = m.group(1), int(m.group(2))
        if cat == "all":
            items = [by_path[p] for p in POPULAR]
        else:
            items = [a for a in articles if a["category"] == cat]
        items = [a for a in items if a["path"] != current][:n]
        return guide_cards(prefix, items)
    return re.sub(r"<!--GUIDES:([^:]+):(\d+)-->", repl, body)


def breadcrumbs(meta):
    path = meta["path"]
    crumbs = [("Home", "index.html")]
    if path.startswith("guides/") and path != "guides/index.html":
        crumbs.append(("Guides", "guides/index.html"))
    crumbs.append((meta["h1"], path))
    return crumbs


def jsonld(meta):
    org = {
        "@type": "Organization",
        "@id": SITE + "/#organization",
        "name": BRAND,
        "url": SITE + "/",
        "logo": SITE + "/images/icon-512.png",
    }
    graph = []
    t = meta.get("type")
    if t == "home":
        graph += [org, {
            "@type": "WebSite",
            "@id": SITE + "/#website",
            "url": SITE + "/",
            "name": BRAND,
            "description": meta["description"],
            "publisher": {"@id": SITE + "/#organization"},
            "inLanguage": "en-US",
        }]
    elif t == "article":
        graph.append({
            "@type": "Article",
            "headline": meta["h1"],
            "description": meta["description"],
            "image": [OG_IMAGE],
            "datePublished": meta["date"],
            "dateModified": meta.get("updated", meta["date"]),
            "author": {"@type": "Person", "name": AUTHOR, "url": canonical("author.html"), "jobTitle": "Founder and editor", "worksFor": {"@id": SITE + "/#organization"}},
            "publisher": org,
            "mainEntityOfPage": canonical(meta["path"]),
            "articleSection": meta["category"],
            "wordCount": meta["words"],
            "inLanguage": "en-US",
        })
    else:
        graph.append({
            "@type": "CollectionPage" if t == "collection" else "WebPage",
            "name": meta["h1"],
            "description": meta["description"],
            "url": canonical(meta["path"]),
            "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE + "/"},
            "inLanguage": "en-US",
        })
    if t == "glossary":
        terms = re.findall(r'<dt id="([^"]+)">(.*?)</dt>\s*<dd>(.*?)</dd>', meta["body"], re.S)
        graph.append({
            "@type": "DefinedTermSet",
            "@id": canonical(meta["path"]) + "#terms",
            "name": meta["h1"],
            "url": canonical(meta["path"]),
            "hasDefinedTerm": [
                {
                    "@type": "DefinedTerm",
                    "name": html.unescape(re.sub("<[^>]+>", "", name)).strip(),
                    "description": html.unescape(re.sub(r"\s+", " ", re.sub("<[^>]+>", "", desc))).strip(),
                    "url": canonical(meta["path"]) + "#" + tid,
                    "inDefinedTermSet": canonical(meta["path"]) + "#terms",
                }
                for tid, name, desc in terms
            ],
        })
    if t != "home":
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": canonical(href)}
                for i, (name, href) in enumerate(breadcrumbs(meta))
            ],
        })
    data = {"@context": "https://schema.org", "@graph": graph}
    return ('  <script type="application/ld+json">\n'
            + json.dumps(data, indent=2, ensure_ascii=False).replace("</", "<\\/")
            + "\n  </script>\n")


def article_body(meta, body, prefix):
    crumbs = breadcrumbs(meta)
    bc = ['      <nav class="breadcrumb" aria-label="Breadcrumb"><ol>']
    for name, href in crumbs[:-1]:
        bc.append(f'        <li><a href="{rel(prefix, href)}">{name}</a></li>')
    bc.append(f'        <li aria-current="page">{crumbs[-1][0]}</li>')
    bc.append("      </ol></nav>")
    body = body.replace("      <h1>", "\n".join(bc) + "\n      <h1>", 1)
    published = meta["date"]
    updated = meta.get("updated")
    dates = (f'Published <time datetime="{published}">{nice_date(published)}</time>')
    if updated and updated != published:
        dates += (f' <span aria-hidden="true">·</span> '
                  f'Updated <time datetime="{updated}">{nice_date(updated)}</time>')
    byline = (f'\n      <p class="byline">{dates} '
              f'<span aria-hidden="true">·</span> {read_time(meta)} min read</p>')
    body = body.replace("</h1>", "</h1>" + byline, 1)

    # Section ids for the table of contents
    toc, used = [], set()

    def add_id(m):
        text = m.group(1)
        plain = re.sub("<[^>]+>", "", text)
        slug = re.sub(r"[^a-z0-9]+", "-", html.unescape(plain).lower()).strip("-") or "section"
        base, n = slug, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        toc.append((slug, plain))
        return f'<h2 id="{slug}">{text}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", add_id, body)

    # Illustration, key takeaways and table of contents after the lead paragraph
    art = ART.get(meta.get("category"))
    extras = ""
    takeaways = [x.strip() for x in meta.get("takeaways", "").split("|") if x.strip()]
    if takeaways:
        items = "\n".join(f"          <li>{x}</li>" for x in takeaways)
        extras += ('\n      <aside class="takeaways" aria-labelledby="takeaways-h">\n'
                   '        <h2 class="takeaways-title" id="takeaways-h">Key takeaways</h2>\n'
                   f'        <ul>\n{items}\n        </ul>\n      </aside>')
    if len(toc) >= 4:
        items = "\n".join(f'          <li><a href="#{i}">{txt}</a></li>' for i, txt in toc)
        extras += ('\n      <nav class="toc" aria-labelledby="toc-h">\n'
                   '        <h2 class="toc-title" id="toc-h">On this page</h2>\n'
                   f'        <ol>\n{items}\n        </ol>\n      </nav>')
    m = re.search(r'<p class="lead">.*?</p>', body, re.S)
    if m:
        figure = ""
        if art:
            figure = f'<img class="guide-art" src="{rel(prefix, art)}" alt="" width="1200" height="360">\n      '
        body = body[:m.start()] + figure + m.group(0) + extras + body[m.end():]

    # Ad slots: before the 3rd H2 and before "The bottom line".
    h2s = [m.start() for m in re.finditer(r"\n      <h2 id=", body)]
    if len(h2s) >= 3:
        i = h2s[2]
        body = body[:i] + "\n      " + AD_SLOT.format(key="inArticle") + body[i:]
    body = body.replace('\n      <h2 id="the-bottom-line">',
                        "\n      " + AD_SLOT.format(key="inArticle2") + '\n      <h2 id="the-bottom-line">', 1)

    related = [by_path[p.strip()] for p in meta.get("related", "").split(",") if p.strip()]
    if related:
        block = ('      <section class="related" aria-labelledby="related-h">\n'
                 '        <h2 id="related-h">Keep reading</h2>\n'
                 + guide_cards(prefix, related) + "\n      </section>\n\n")
        body = body.replace('      <p class="note">', block + '      <p class="note">', 1)
    return body


def footer(prefix):
    def col(title, links):
        items = "\n".join(f'              <li><a href="{rel(prefix, h)}">{l}</a></li>' for h, l in links)
        return f'''          <div class="footer-col">
            <h2 class="footer-heading">{title}</h2>
            <ul>
{items}
            </ul>
          </div>'''
    cols = "\n".join([
        col("Car insurance", [("car-insurance.html", "Car insurance basics"),
                              ("guides/how-much-car-insurance-do-you-need.html", "How much you need"),
                              ("guides/what-is-full-coverage-car-insurance.html", "Full coverage explained"),
                              ("guides/how-to-file-a-car-insurance-claim.html", "Filing a claim")]),
        col("Home insurance", [("home-insurance.html", "Home insurance basics"),
                               ("guides/what-does-homeowners-insurance-cover.html", "What it covers"),
                               ("guides/do-you-need-flood-insurance.html", "Flood insurance"),
                               ("guides/renters-insurance-basics.html", "Renters insurance")]),
        col("Tools", [("calculator.html", "Estimate calculator"),
                      ("guides/index.html", "All guides"),
                      ("glossary.html", "Glossary")]),
        col("Company", [("about.html", "About us"),
                        ("author.html", "Our editor"),
                        ("contact.html", "Contact"),
                        ("sitemap.xml", "Sitemap")]),
    ])
    return f'''  <footer class="site-footer">
    <div class="container">
      <p class="disclosure">{DISCLOSURE}</p>
      <nav class="footer-grid" aria-label="Footer">
{cols}
      </nav>
      <div class="footer-bottom">
        <p class="copyright">Copyright &copy; <span data-year>2026</span> {BRAND}. All rights reserved.</p>
        <ul class="footer-legal">
          <li><a href="{rel(prefix, "legal-notice.html")}">Legal Notice</a></li>
          <li><a href="{rel(prefix, "privacy-policy.html")}">Privacy Policy</a></li>
          <li><a href="{rel(prefix, "cookie-policy.html")}">Cookie Policy</a></li>
          <li><a href="{rel(prefix, "terms.html")}">Terms of Use</a></li>
          <li><a href="{rel(prefix, "do-not-sell.html")}">Do Not Sell or Share My Personal Information</a></li>
          <li><button type="button" class="link-button" data-privacy-settings>Privacy settings</button></li>
        </ul>
      </div>
    </div>
  </footer>'''


def render(meta):
    path = meta["path"]
    t = meta.get("type")
    prefix = "/" if t == "error" else "../" * path.count("/")
    section = meta.get("section", path)
    body = meta["body"]

    if t == "article":
        body = article_body(meta, body, prefix)
    body = expand_guides(body, prefix, current=path)
    body = body.replace("<!--AD-->", "      " + AD_SLOT.format(key="inContent"))

    nav_html = "\n".join(
        f'          <li><a href="{rel(prefix, h)}"{CUR if h == section else ""}>{l}</a></li>'
        for h, l in NAV)

    scripts = f'  <script src="{prefix}js/main.js" defer></script>\n'
    if meta.get("script"):
        scripts += f'  <script src="{prefix}{meta["script"]}" defer></script>\n'
    scripts += f'  <script src="{prefix}js/integrations.js" defer></script>\n'

    title = meta["title"]
    desc = meta["description"]
    url = canonical(path)
    robots = "noindex, follow" if t == "error" else "index, follow, max-image-preview:large"
    og_type = "article" if t == "article" else "website"
    canonical_tag = "" if t == "error" else f'  <link rel="canonical" href="{url}">\n'
    article_meta = ""
    if t == "article":
        article_meta = (f'  <meta property="article:published_time" content="{meta["date"]}">\n'
                        f'  <meta property="article:modified_time" content="{meta.get("updated", meta["date"])}">\n'
                        f'  <meta property="article:section" content="{meta["category"]}">\n')

    return f"""<!DOCTYPE html>
<html lang="en-US" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(title, quote=False)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="robots" content="{robots}">
{canonical_tag}  <meta name="theme-color" content="#f5f5f7" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
  <meta name="color-scheme" content="light dark">
  <meta name="google-adsense-account" content="{ADSENSE}">
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Car and home insurance, explained simply">
  <meta property="og:locale" content="en_US">
{article_meta}  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(desc)}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="icon" href="{prefix}favicon.ico" sizes="32x32">
  <link rel="icon" href="{prefix}images/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{prefix}images/apple-touch-icon.png">
  <link rel="manifest" href="{prefix}site.webmanifest">
  <link rel="stylesheet" href="{prefix}css/styles.css">
{scripts}{jsonld(meta)}</head>
<body class="page-{t or 'page'}">
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{prefix}index.html">{LOGO_SVG}<span>{BRAND}</span></a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
        <span class="nav-toggle-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Menu</span>
      </button>
      <nav id="site-nav" class="site-nav" aria-label="Main">
        <ul>
{nav_html}
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
{body}
  </main>

{footer(prefix)}
</body>
</html>
"""


for meta in pages:
    dest = os.path.join(OUT, meta["path"])
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(version_assets(clean_links(render(meta))))
    print("wrote", meta["path"], meta["words"], "words")

# sitemap.xml
urls = []
for meta in pages:
    if meta.get("type") == "error":
        continue
    lastmod = meta.get("updated", meta.get("date", "2026-11-03"))
    urls.append(f"  <url>\n    <loc>{canonical(meta['path'])}</loc>\n    <lastmod>{lastmod}</lastmod>\n  </url>")
with open(os.path.join(OUT, "sitemap.xml"), "w") as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
             + "\n".join(urls) + "\n</urlset>\n")
print("wrote sitemap.xml", len(urls), "urls")
