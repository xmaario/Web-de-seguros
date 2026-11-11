# Site tools (not published)

The website is plain static HTML in the repo root. These tools regenerate it from source fragments.
This folder is excluded from the live site by `.assetsignore`.

- `content/*.html` — one source fragment per page: a small header (`title`, `description`, `path`,
  `type`, and for guides `category`, `date`, `related`), a `---` line, then the page body.
- `build.py` — run `python3 tools/build.py` from the repo root. Writes every page, the shared header
  and footer, SEO tags, structured data and `sitemap.xml`. Never edit the generated root HTML by hand.
- `check.py` — run `python3 tools/check.py` after building. Must print "All checks passed."
- `guide-topics.md` — backlog of future guides.

## Adding a guide
1. Copy an existing guide fragment (for example `content/guide-20.html`) to `content/guide-<next number>.html`.
2. Update the header: `title` (ends with `| UnpackInsurance`, about 60 characters), `description`
   (under 160 characters), `path: guides/<slug>.html`, `section: guides/index.html`, `type: article`,
   `category: Car insurance` or `Home insurance`, `date: YYYY-MM-DD`, and `related:` with three existing guide paths.
   Also `takeaways:` with 3 or 4 short key points separated by ` | ` (shown in a "Key takeaways" box).
   Required `topic:` with one topic cluster from `TOPICS` in `build.py`. Car insurance: Coverage basics, Costs and savings, Claims and accidents, Car loans and leases, Drivers and special situations. Home insurance: What homeowners insurance covers, Costs and deductibles, Renters and condo owners, Extra protection. The build stops if it is missing.
   Add at least 2 in-text links TO the new guide from older related guides (not only the "related:" cards), so it is never an orphan page.
   Optional `sources:` with extra source ids from `SOURCES` in `build.py`, comma-separated (for example `sources: cfpb-auto` for loan topics, `cfpb-crc` for claims history, `floodsmart, fema-msc` for flood). Default sources for the category are always added, and a "Sources and official resources" box is generated. Add new ids to `SOURCES` only for stable pages of government agencies, the NAIC, or nonprofit institutes.
   Start the body with an h2 "The short answer": a direct 40-60 word answer to the title question (Google uses this format for featured snippets and AI answers). Add a simple comparison table (`<div class="table-wrap"><table>` with `<th scope="col">` headings) when the topic compares options; the build makes it readable on phones.
   Link a free tool where it fits: `gap-insurance-quiz.html` (loans, leases, gap, new cars), `liability-coverage-calculator.html` (limits, umbrella, how much coverage), `calculator.html` (prices).
   Optional `updated: YYYY-MM-DD` when an existing guide is revised (shown as "Updated" next to the publication date).
   The build adds the category illustration, the "On this page" table of contents and section ids automatically.
3. Write the body inside `<article class="container prose">`: one `<h1>`, a `lead` paragraph, `<h2>` sections,
   a "The bottom line" section, and a closing `<p class="note">` disclaimer.
4. Run `python3 tools/build.py` then `python3 tools/check.py`.

## Content rules
- US English, original text, 800 to 1,000 words per new guide (check.py allows up to 1,300 for guides expanded later). Title at most about 60 characters, description at most 160.
- No real insurance company names, logos or implied partnerships.
- No invented reviews, testimonials, ratings, statistics or savings claims. No promised prices.
- Use "may", "often", "varies by state and provider". General information, not advice.
- Only state facts you are confident are accurate and current; otherwise keep the wording general.
- `indexnow.py` — after a change is live, run `python3 tools/indexnow.py <url>` (or no arguments for the
  whole sitemap) to notify Bing and other IndexNow search engines. The public key file is `<key>.txt` at the root.
- Callout boxes: guides may include 1-2 callouts where they genuinely help, e.g.
  `<aside class="callout tip"><span class="callout-title">Tip</span><p>…</p></aside>`
  (classes: `tip`, `warn` with title "Watch out", `example` with title "Example"). Examples must be clearly illustrative.
