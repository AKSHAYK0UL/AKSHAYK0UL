#!/usr/bin/env python3
"""Builds the year selector: pill images, one page per past year, and the README activity block.
Standard library only. Usage: python scripts/build_years.py [first_year]
Run from the repo root. The README block lives between <!-- ACTIVITY:START --> and <!-- ACTIVITY:END -->."""
import os, re, sys
from datetime import date

USER = "AKSHAYK0UL"
FIRST = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
NOW = date.today().year
PROFILE = f"https://github.com/{USER}"
FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', 'Segoe UI', Arial, sans-serif"

# Sizing: the year list is exactly as tall as the heatmap card (214 units at 690 wide, shown at 83% width).
HEAT_W, HEAT_H, HEAT_PCT, PILL_W = 690, 214, 83, 120
PILL_PCT = round(HEAT_PCT * PILL_W / HEAT_W, 2)          # same scale as the heatmap, so heights line up
N = max(1, date.today().year - FIRST + 1)
GAP = 8 if N <= 5 else 6                                  # small gap between buttons
PILL_H = (HEAT_H - (N - 1) * GAP) / N                     # buttons grow/shrink to fill the card height

def pill(label, active, last):
    h = PILL_H
    canvas = h if last else h + GAP                        # no gap under the last button
    fs = min(14, round(h * 0.4, 1))
    ty = h / 2 + fs * 0.35
    if active:
        rect, fill, w = f'<rect x="0.5" y="0.5" width="{PILL_W-1}" height="{h-1:.2f}" rx="11" fill="#0a84ff"/>', "#ffffff", 600
    else:
        rect, fill, w = f'<rect x="0.5" y="0.5" width="{PILL_W-1}" height="{h-1:.2f}" rx="11" fill="#161618" stroke="#2c2c2e"/>', "#8e8e93", 500
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{PILL_W}" height="{canvas:.2f}" viewBox="0 0 {PILL_W} {canvas:.2f}" role="img" aria-label="{label}">\n'
            f'{rect}\n<text x="{PILL_W/2}" y="{ty:.2f}" text-anchor="middle" font-family="{FONT}" font-size="{fs}" font-weight="{w}" fill="{fill}">{label}</text>\n</svg>\n')

def block(active, heat, assets, pages):
    """HTML for heatmap (left) + year list (right)."""
    rows = []
    for y in range(NOW, FIRST - 1, -1):
        img = f'{assets}pill-{y}{"-active" if y == active else ""}.svg'
        href = PROFILE if y == NOW else f"{pages}{y}.md"
        rows.append(f'  <a href="{href}"><img align="top" alt="{y}" src="{img}" width="{PILL_PCT}%"></a>')
    return (f'<p align="right">\n  <img align="left" alt="Commit history" src="{heat}" width="{HEAT_PCT}%">\n'
            + "<br>\n".join(rows) + '\n</p>\n<br clear="all">\n')

os.makedirs("assets", exist_ok=True); os.makedirs("years", exist_ok=True)
for y in range(FIRST, NOW + 1):
    open(f"assets/pill-{y}.svg", "w", encoding="utf-8").write(pill(str(y), False, y == FIRST))
    open(f"assets/pill-{y}-active.svg", "w", encoding="utf-8").write(pill(str(y), True, y == FIRST))

for y in range(FIRST, NOW):
    page = (f'<h2 align="center">Activity · {y}</h2>\n\n'
            + block(y, f"../assets/activity-{y}.svg", "../assets/", "")
            + f'\n<br><br><br>\n\n<p align="center"><a href="{PROFILE}">← Back to profile</a></p>\n')
    open(f"years/{y}.md", "w", encoding="utf-8").write(page)

if os.path.exists("README.md"):
    s = open("README.md", encoding="utf-8").read()
    new = "<!-- ACTIVITY:START -->\n" + block(NOW, "assets/activity.svg", "assets/", "years/") + "<!-- ACTIVITY:END -->"
    s2, n = re.subn(r"<!-- ACTIVITY:START -->.*?<!-- ACTIVITY:END -->", lambda m: new, s, flags=re.S)
    if n: open("README.md", "w", encoding="utf-8").write(s2)
print(f"pills {FIRST}-{NOW}, pages {FIRST}-{NOW-1}")
