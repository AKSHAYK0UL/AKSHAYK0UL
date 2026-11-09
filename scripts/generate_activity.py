#!/usr/bin/env python3
"""Generate a contribution heatmap SVG from your public GitHub profile.
Standard library only.
Usage: python scripts/generate_activity.py [username] [output] [year]
  no year  -> rolling last 12 months
  year     -> that calendar year (e.g. 2025)"""
import re, sys, urllib.request
from datetime import date, timedelta
from html import unescape

USER = sys.argv[1] if len(sys.argv) > 1 else "AKSHAYK0UL"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/activity.svg"
YEAR = int(sys.argv[3]) if len(sys.argv) > 3 else None
FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', 'Segoe UI', Arial, sans-serif"
CARD, STROKE, P, S = "#161618", "#2c2c2e", "#f5f5f7", "#8e8e93"
LEVELS = ["#262629", "#123a66", "#1664b8", "#0a84ff", "#6fbfff"]

url = f"https://github.com/users/{USER}/contributions"
if YEAR:
    url += f"?from={YEAR}-01-01&to={YEAR}-12-31"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
tds = re.findall(r"<td[^>]*data-date=\"[^\"]+\"[^>]*>", html)
tips = [unescape(t) for t in re.findall(r"<tool-tip[^>]*>([^<]*)</tool-tip>", html)]
if not tds:
    sys.exit("No contribution data found; leaving existing file untouched.")

days = {}
for i, td in enumerate(tds):
    d = date.fromisoformat(re.search(r'data-date="([^"]+)"', td).group(1))
    lvl = int(re.search(r'data-level="(\d)"', td).group(1))
    m = re.match(r"(\d+) contribution", tips[i]) if i < len(tips) else None
    days[d] = (lvl, int(m.group(1)) if m else 0)

first = min(days)
start = first - timedelta(days=(first.weekday() + 1) % 7)   # Sunday
last = max(days)
weeks = (last - start).days // 7 + 1
total = sum(c for _, c in days.values())

W, PAD = 690, 26
pitch = (W - 2 * PAD) / weeks
cell = pitch - 3
gx, gy = PAD, 84
vp = 12                      # fixed row height so every card is exactly the same height
ch = vp - 3
H = gy + 7 * vp + 46         # = 214

def t(x, y, s, size, fill, weight=400, anchor="start", ls=0):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}">{s}</text>'

body = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1:.0f}" rx="18" fill="{CARD}" stroke="{STROKE}"/>'
title = f"Commit history · {YEAR}" if YEAR else "Commit history"
sub = f"{total:,} contributions in {YEAR}" if YEAR else f"{total:,} contributions in the last year"
body += t(PAD, 40, title, 16, P, 600)
body += t(W - PAD, 40, sub, 12.5, S, 400, "end")

for d in sorted(days):
    wk, dow = (d - start).days // 7, (d.weekday() + 1) % 7
    body += f'<rect x="{gx + wk*pitch:.2f}" y="{gy + dow*vp:.2f}" width="{cell:.2f}" height="{ch:.2f}" rx="3" fill="{LEVELS[days[d][0]]}"/>'

# month labels at the first week that contains the 1st-7th of a month
done = set()
for wk in range(weeks):
    d0 = start + timedelta(days=wk * 7)
    key = (d0 + timedelta(days=6)).month
    first_of_month_in_week = any((d0 + timedelta(days=k)).day == 1 for k in range(7))
    if (first_of_month_in_week or wk == 0) and key not in done and wk < weeks - 2:
        label = (d0 + timedelta(days=6)).strftime("%b")
        body += t(gx + wk * pitch, gy - 10, label, 11, S, 500)
        done.add(key)

ly = gy + 7 * vp + 24
lx = W - PAD - 5 * (cell + 3) - 30
body += t(lx - 8, ly + ch - 2, "Less", 11, S, 400, "end")
for i, c in enumerate(LEVELS):
    body += f'<rect x="{lx + i*(cell+3):.1f}" y="{ly:.1f}" width="{ch:.1f}" height="{ch:.1f}" rx="3" fill="{c}"/>'
body += t(lx + 5 * (cell + 3) + 4, ly + ch - 2, "More", 11, S)

svg = f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{title}: {total} contributions">\n{body}\n</svg>\n'
open(OUT, "w", encoding="utf-8").write(svg)
print(f"wrote {OUT}: {total} contributions, {weeks} weeks")
