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

def pill(label, active):
    if active:
        rect, fill = '<rect x="0.5" y="0.5" width="119" height="37" rx="11" fill="#0a84ff"/>', "#ffffff"
    else:
        rect, fill = '<rect x="0.5" y="0.5" width="119" height="37" rx="11" fill="#161618" stroke="#2c2c2e"/>', "#8e8e93"
    w = 600 if active else 500
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="120" height="52" viewBox="0 0 120 52" role="img" aria-label="{label}">\n'
            f'{rect}\n<text x="60" y="24.5" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="{w}" fill="{fill}">{label}</text>\n</svg>\n')

def block(active, heat, assets, pages):
    """HTML for heatmap (left) + year list (right)."""
    rows = []
    for y in range(NOW, FIRST - 1, -1):
        img = f'{assets}pill-{y}{"-active" if y == active else ""}.svg'
        href = PROFILE if y == NOW else f"{pages}{y}.md"
        rows.append(f'  <a href="{href}"><img alt="{y}" src="{img}" width="14%"></a>')
    return (f'<p align="right">\n  <img align="left" alt="Commit history" src="{heat}" width="83%">\n'
            + "<br>\n".join(rows) + '\n</p>\n<br clear="all">\n')

os.makedirs("assets", exist_ok=True); os.makedirs("years", exist_ok=True)
for y in range(FIRST, NOW + 1):
    open(f"assets/pill-{y}.svg", "w", encoding="utf-8").write(pill(str(y), False))
    open(f"assets/pill-{y}-active.svg", "w", encoding="utf-8").write(pill(str(y), True))

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
