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
