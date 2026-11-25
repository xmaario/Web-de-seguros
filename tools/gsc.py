#!/usr/bin/env python3
"""Read Search Console data through the site's private /api/gsc endpoint.

The X-Stats-Token header is added by the session's network proxy (saved credential),
so this script sends no secret itself.

Usage: python3 tools/gsc.py [days=7] [dimension ...]
  python3 tools/gsc.py 7 date
  python3 tools/gsc.py 28 page
  python3 tools/gsc.py 28 query page
"""
import datetime, json, sys, urllib.request

days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
dims = sys.argv[2:] or ["date"]
end = datetime.date.today()
body = {"startDate": str(end - datetime.timedelta(days=days)), "endDate": str(end),
        "dimensions": dims, "dataState": "all", "rowLimit": 1000}
req = urllib.request.Request("https://unpackinsurance.com/api/gsc", data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json", "User-Agent": "unpack-gsc-report/1.0"}, method="POST")
rows = json.load(urllib.request.urlopen(req, timeout=60)).get("rows", [])
rows.sort(key=lambda r: r["keys"] if dims == ["date"] else [-r["impressions"]])
for r in rows:
    print(f'{r["impressions"]:6} {r["clicks"]:3} {r["position"]:6.1f}  ' + " | ".join(r["keys"]))
