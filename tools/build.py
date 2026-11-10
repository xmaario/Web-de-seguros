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
    ("tools.html", "Tools"),
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

CAT_CLASS = {"Car insurance": "cat-car", "Home insurance": "cat-home"}

CUR = ' aria-current="page"'

# Official and authoritative sources listed at the end of guides ("sources:" header, comma-separated ids).
# Only stable pages of government agencies, state regulators' association and nonprofit institutes.
SOURCES = {
    "naic-doi": ("Find your state insurance department",
                 "National Association of Insurance Commissioners (NAIC)",
                 "https://content.naic.org/state-insurance-departments"),
    "naic": ("Consumer insurance information and complaint tools",
             "National Association of Insurance Commissioners (NAIC)",
             "https://content.naic.org/"),
    "iii-auto": ("Auto insurance basics",
                 "Insurance Information Institute (Triple-I)",
                 "https://www.iii.org/publication/insurance-handbook/insurance-basics/auto-insurance-basics"),
    "cfpb-auto": ("Auto loans: tools and guides",
                  "Consumer Financial Protection Bureau (CFPB)",
                  "https://www.consumerfinance.gov/consumer-tools/auto-loans/"),
    "cfpb-crc": ("List of consumer reporting companies, including insurance claims history reports",
                 "Consumer Financial Protection Bureau (CFPB)",
                 "https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/consumer-reporting-companies/companies-list/"),
    "nhtsa-recalls": ("Check your vehicle for safety recalls",
                      "National Highway Traffic Safety Administration (NHTSA)",
                      "https://www.nhtsa.gov/recalls"),
    "floodsmart": ("National Flood Insurance Program (NFIP)",
                   "FEMA, FloodSmart.gov",
                   "https://www.floodsmart.gov/"),
    "fema-msc": ("Flood Map Service Center",
                 "Federal Emergency Management Agency (FEMA)",
                 "https://msc.fema.gov/portal/home"),
}
# Topic clusters inside each category ("topic:" header in every guide).
TOPICS = {
    "Car insurance": ["Coverage basics", "Costs and savings", "Claims and accidents",
                      "Car loans and leases", "Drivers and special situations"],
    "Home insurance": ["What homeowners insurance covers", "Costs and deductibles",
                       "Renters and condo owners", "Extra protection"],
}

# Glossary terms linked to the guide that explains them (only where the definition has no link yet).
GLOSSARY_LINKS = {
    "accident-forgiveness": "guides/how-long-does-an-accident-stay-on-your-insurance.html",
    "actual-cash-value": "guides/replacement-cost-vs-actual-cash-value.html",
    "adjuster": "guides/how-to-file-a-car-insurance-claim.html",
    "claim": "guides/how-to-file-a-car-insurance-claim.html",
    "clue-report": "guides/how-long-does-an-accident-stay-on-your-insurance.html",
    "collision": "guides/comprehensive-vs-collision-coverage.html",
    "comprehensive": "guides/comprehensive-vs-collision-coverage.html",
    "condo-insurance": "guides/condo-insurance-ho6-explained.html",
    "deductible": "guides/car-insurance-deductibles-explained.html",
    "depreciation": "guides/upside-down-car-loan.html",
    "dwelling-coverage": "guides/what-does-homeowners-insurance-cover.html",
    "fr-44": "guides/what-is-an-sr-22.html",
    "gap-coverage": "guides/what-is-gap-insurance.html",
    "ho-3": "guides/what-does-homeowners-insurance-cover.html",
    "ho-4": "guides/renters-insurance-basics.html",
    "liability-coverage": "guides/how-much-car-insurance-do-you-need.html",
    "limit": "liability-coverage-calculator.html",
    "loss-assessment": "guides/condo-insurance-ho6-explained.html",
    "master-policy": "guides/condo-insurance-ho6-explained.html",
    "nfip": "guides/do-you-need-flood-insurance.html",
    "premium": "guides/why-did-my-car-insurance-go-up.html",
    "replacement-cost": "guides/replacement-cost-vs-actual-cash-value.html",
    "sr-22": "guides/what-is-an-sr-22.html",
    "total-loss": "guides/what-is-gap-insurance.html",
    "umbrella": "guides/what-is-umbrella-insurance.html",
    "water-backup": "guides/does-homeowners-insurance-cover-water-damage.html",
    "wind-hail-deductible": "guides/home-insurance-deductibles-explained.html",
}


def link_glossary(body, prefix):
    def fix(m):
        tid, dt, dd = m.group(1), m.group(2), m.group(3)
        target = GLOSSARY_LINKS.get(tid)
        if target and "<a " not in dd:
            name = by_path[target]["h1"] if target in by_path else "Liability limits calculator"
            dd = dd.rstrip() + f' See <a href="{rel(prefix, target)}">{name}</a>.'
        return f'<dt id="{tid}">{dt}</dt>\n        <dd>{dd}</dd>'
    return re.sub(r'<dt id="([^"]+)">(.*?)</dt>\s*<dd>(.*?)</dd>', fix, body, flags=re.S)


DEFAULT_SOURCES = {
    "Car insurance": ["naic-doi", "iii-auto"],
    "Home insurance": ["naic-doi", "naic"],
}


def guide_sources(meta):
    ids = [x.strip() for x in meta.get("sources", "").split(",") if x.strip()]
    for d in DEFAULT_SOURCES.get(meta.get("category"), []):
        if d not in ids:
            ids.append(d)
    return [SOURCES[i] for i in ids]

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
    "guides/what-is-gap-insurance.html",
    "guides/how-to-file-a-car-insurance-claim.html",
    "guides/how-much-car-insurance-do-you-need.html",
    "guides/what-is-full-coverage-car-insurance.html",
    "guides/what-does-homeowners-insurance-cover.html",
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
            <p class="card-eyebrow {CAT_CLASS.get(a["category"], "")}">{a["category"]}</p>
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
        elif cat == "latest":
            items = sorted(articles, key=lambda a: a["date"], reverse=True)
        else:
            items = [a for a in articles if a["category"] == cat]
        items = [a for a in items if a["path"] != current][:n]
        return guide_cards(prefix, items)
    body = re.sub(r"<!--GUIDES:([^:]+):(\d+)-->", repl, body)

    def topics(m):
        cat, level = m.group(1), int(m.group(2))
        out = []
        for topic in TOPICS[cat]:
            items = [a for a in articles if a["category"] == cat and a.get("topic") == topic and a["path"] != current]
            if items:
                slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
                out.append(f'        <h{level} class="topic-title" id="topic-{slug}">{topic}</h{level}>\n'
                           + guide_cards(prefix, items, heading_level=level + 1))
        missing = [a["path"] for a in articles if a["category"] == cat and a.get("topic") not in TOPICS[cat]]
        if missing:
            sys.exit(f"ERROR: missing or unknown 'topic:' in {missing}. Use one of {TOPICS[cat]}")
        return "\n".join(out)
    return re.sub(r"<!--TOPICS:([^:]+):(\d)-->", topics, body)


def breadcrumbs(meta):
    path = meta["path"]
    crumbs = [("Home", "index.html")]
    if path.startswith("guides/") and path != "guides/index.html":
        crumbs.append(("Guides", "guides/index.html"))
    elif meta.get("section") == "tools.html" and path != "tools.html":
        crumbs.append(("Tools", "tools.html"))
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
            "author": {"@type": "Person", "name": AUTHOR, "url": canonical("author.html"), "image": SITE + "/images/author-mario.jpg", "jobTitle": "Founder and editor", "worksFor": {"@id": SITE + "/#organization"}},
            "publisher": org,
            "mainEntityOfPage": canonical(meta["path"]),
            "articleSection": meta["category"],
            "wordCount": meta["words"],
            "citation": [{"@type": "CreativeWork", "name": t_, "publisher": {"@type": "Organization", "name": o_}, "url": u_}
                         for t_, o_, u_ in guide_sources(meta)],
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
    if meta["path"] == "author.html":
        graph[-1]["@type"] = "ProfilePage"
        graph[-1]["mainEntity"] = {
            "@type": "Person",
            "@id": SITE + "/author#person",
            "name": AUTHOR,
            "jobTitle": "Founder and editor",
            "image": SITE + "/images/author-mario.jpg",
            "url": canonical("author.html"),
            "worksFor": {"@id": SITE + "/#organization"},
        }
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
    chip = f'      <p class="category-chip {CAT_CLASS.get(meta.get("category"), "")}">{meta.get("category", "")}</p>\n'
    body = body.replace("      <h1>", "\n".join(bc) + "\n" + chip + "      <h1>", 1)
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

    src = guide_sources(meta)
    if src:
        items = "\n".join(f'          <li><a href="{u}" rel="noopener">{t_}</a> <span class="source-org">{o_}</span></li>'
                          for t_, o_, u in src)
        block = ('      <section class="sources" aria-labelledby="sources-h">\n'
                 '        <h2 id="sources-h">Sources and official resources</h2>\n'
                 '        <p>Rules and requirements vary by state. These official and nonprofit resources can help you check details for your situation.</p>\n'
                 f'        <ul>\n{items}\n        </ul>\n      </section>\n\n')
        body = body.replace('      <p class="note">', block + '      <p class="note">', 1)

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
        col("Tools", [("calculator.html", "Car insurance calculator"),
                      ("gap-insurance-quiz.html", "Gap insurance quiz"),
                      ("liability-coverage-calculator.html", "Liability limits calculator"),
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
    if t == "glossary":
        body = link_glossary(body, prefix)
    if "<!--GLOSSARY-JSON-->" in body:
        gl = by_path["glossary.html"]["body"]
        terms = [{"id": i, "name": html.unescape(re.sub("<[^>]+>", "", n)).strip(),
                  "text": html.unescape(re.sub(r"\s+", " ", re.sub("<[^>]+>", "", d))).strip()}
                 for i, n, d in re.findall(r'<dt id="([^"]+)">(.*?)</dt>\s*<dd>(.*?)</dd>', gl, re.S)]
        body = body.replace("<!--GLOSSARY-JSON-->",
                            '<script type="application/json" id="glossary-data">'
                            + json.dumps(terms, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    body = body.replace("<!--COUNT:guides-->", str(len(articles)))
    if "<!--COUNT:terms-->" in body:
        gl = by_path.get("glossary.html")
        body = body.replace("<!--COUNT:terms-->", str(len(re.findall(r"<dt id=", gl["body"])) if gl else 0))
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
  <link rel="alternate" type="application/rss+xml" title="{BRAND} guides" href="{SITE}/feed.xml">
  <link rel="stylesheet" href="{prefix}css/styles.css">
{scripts}{jsonld(meta)}</head>
<body class="page-{t or 'page'}">
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{prefix}index.html">{LOGO_SVG}<span>{BRAND}</span></a>
      <div class="header-actions">
        <a class="header-search" href="{prefix}guides/index.html#search" aria-label="Search guides and glossary">
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.5 15.5L21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </a>
        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
          <span class="nav-toggle-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Menu</span>
        </button>
      </div>
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

# feed.xml (RSS 2.0): the 20 newest guides. Search engines and readers use it to find new pages fast.
from email.utils import format_datetime
def rfc822(d):
    return format_datetime(datetime.datetime.fromisoformat(d + "T09:00:00+00:00"))
items = []
for a in sorted(articles, key=lambda a: (a.get("updated", a["date"]), a["date"]), reverse=True)[:20]:
    items.append(f"""    <item>
      <title>{html.escape(a["h1"])}</title>
      <link>{canonical(a["path"])}</link>
      <guid isPermaLink="true">{canonical(a["path"])}</guid>
      <pubDate>{rfc822(a["date"])}</pubDate>
      <category>{a["category"]}</category>
      <description>{html.escape(a["description"])}</description>
    </item>""")
newest = max(a.get("updated", a["date"]) for a in articles)
with open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8") as fh:
    fh.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{BRAND} guides</title>
    <link>{SITE}/</link>
    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Plain-English guides to US car and home insurance.</description>
    <language>en-us</language>
    <lastBuildDate>{rfc822(newest)}</lastBuildDate>
""" + "\n".join(items) + """
  </channel>
</rss>
""")
print("wrote feed.xml", len(items), "items")
