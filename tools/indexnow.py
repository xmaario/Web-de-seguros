"""Notify IndexNow search engines (Bing, Yandex, Seznam, Naver...) about new or changed pages.

Usage (from the repo root, after the change is live):
  python3 tools/indexnow.py                     # submit every URL in sitemap.xml
  python3 tools/indexnow.py <url> [<url> ...]   # submit specific URLs
The key file <key>.txt must be published at the site root (it already is).
"""
import json, re, sys, urllib.request, os

HOST = "unpackinsurance.com"
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(HERE, "indexnow-key.txt")).read().strip()

urls = sys.argv[1:]
if not urls:
    sitemap = open(os.path.join(os.path.dirname(HERE), "sitemap.xml"), encoding="utf-8").read()
    urls = re.findall(r"<loc>(.*?)</loc>", sitemap)

payload = {
    "host": HOST,
    "key": KEY,
    "keyLocation": f"https://{HOST}/{KEY}.txt",
    "urlList": urls,
}
req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow: submitted {len(urls)} URL(s), HTTP {r.status}")
except urllib.error.HTTPError as e:
    print(f"IndexNow: HTTP {e.code} {e.read().decode()[:300]}")
    sys.exit(1)
