"""
Render a neofetch-style info card (role, stack, highlights) as a terminal-window
SVG that sits beside nurullah-ascii.svg. Same 840 x 880 canvas as the portrait,
so the two panels line up at equal widths in the README.

Lines fade + slide in one after another (CSS keyframes, plays once then holds),
then a cursor blinks on the last prompt. GitHub runs CSS/SMIL inside <img>
SVGs but never JS.

    python scripts/make_info_card.py            # animated
    STATIC=1 python scripts/make_info_card.py   # frozen frame for previews
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

USER = "nurullah@github"

# (key, value) rows; None = blank spacer, ("#", text) = section header
ROWS = [
    ("Name", "Nurullah Can"),
    ("Location", "Bursa, Türkiye"),
    ("Role", "Security Systems · Network · SysAdmin"),
    ("Now", "AI & image processing, security tech"),
    ("Prev", "5 yrs corporate system administrator"),
    ("Edu", "Bursa Uludağ Univ. · Computer Prog."),
    None,
    ("#", "highlights"),
    ("Award", "HikTech Star 2024 & 2025 TR Champion"),
    ("Certs", "HCSA ×6 · Ajax · Jablotron · Cisco"),
    ("Field", "7+ yrs · 100+ projects · 1000+ fixes"),
    None,
    ("#", "stack"),
    ("Code", "TypeScript · JavaScript · Node · C#"),
    ("", "Dart · Python · HTML/CSS"),
    ("Infra", "Hikvision · MikroTik · Proxmox · QNAP"),
    ("", "SonicWall · Ajax · Aruba · Ruijie"),
    None,
    ("Web", "nurullahcan.me"),
]

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
KEY = "#22d3ee"
HEAD = "#39d353"
GOLD = "#f2cc60"
ACCENT_USER = "#39d353"
ACCENT_HOST = "#22d3ee"

W, H = 840, 880
PAD = 32
TITLEBAR_H = 30
FONT = 24
LINE_H = 32
KEY_W = 128          # value column starts here (px from PAD)

STAGGER = 0.12
DUR = 0.45

css = (
    f".l{{opacity:0;animation:in {DUR}s ease-out both}}"
    "@keyframes in{0%{opacity:0;transform:translateX(-12px)}100%{opacity:1;transform:translateX(0)}}"
    "@media (prefers-reduced-motion: reduce){.l{opacity:1!important;transform:none!important;animation:none!important}}"
)
if STATIC:
    css = ".l{opacity:1}"

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    f"<style>{css}</style>",
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{20 + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{USER}: ~$ neofetch</text>')

step = 0


def line(y, inner):
    global step
    parts.append(f'<g class="l" style="animation-delay:{step * STAGGER:.2f}s">'
                 f'<text x="{PAD}" y="{y}" font-size="{FONT}" xml:space="preserve">{inner}</text></g>')
    step += 1


y = TITLEBAR_H + 52
u, h = USER.split("@")
line(y, f'<tspan fill="{ACCENT_USER}" font-weight="700">{u}</tspan>'
        f'<tspan fill="{INK}">@</tspan>'
        f'<tspan fill="{ACCENT_HOST}" font-weight="700">{h}</tspan>')
y += LINE_H
line(y, f'<tspan fill="{MUTED}">{"-" * len(USER)}</tspan>')
y += LINE_H

for row in ROWS:
    if row is None:
        y += LINE_H * 0.55
        continue
    k, v = row
    if k == "#":
        line(y, f'<tspan fill="{HEAD}" font-weight="700">## {html.escape(v)}</tspan>')
    else:
        vcol = GOLD if k == "Award" else INK
        key = f'<tspan fill="{KEY}" font-weight="700">{html.escape(k)}</tspan>' if k else ""
        line(y, f'{key}<tspan x="{PAD + KEY_W}" fill="{vcol}">{html.escape(v)}</tspan>')
    y += LINE_H

# neofetch colour blocks
y += 8
bx = PAD
for col in ["#30363d", "#ff5f56", "#27c93f", "#ffbd2e", "#1f6feb", "#bc8cff", "#22d3ee", "#e6edf3"]:
    parts.append(f'<rect class="l" style="animation-delay:{step * STAGGER:.2f}s" x="{bx}" y="{y}" '
                 f'width="40" height="22" fill="{col}"/>')
    bx += 40
step += 1

# final prompt with a blinking cursor
py = H - 30
parts.append(f'<line x1="0" y1="{py - 30}" x2="{W}" y2="{py - 30}" stroke="{FRAME}"/>')
prompt = f"{USER}:~$ "
cmd = 'echo "open to new projects"'
parts.append(f'<g class="l" style="animation-delay:{step * STAGGER:.2f}s">'
             f'<text x="20" y="{py}" fill="{MUTED}" font-size="18">{prompt}'
             f'<tspan fill="{INK}">{html.escape(cmd)}</tspan></text>'
             f'<rect x="{20 + (len(prompt) + len(cmd) + 1) * 18 * 0.6:.1f}" y="{py - 15}" width="10" height="18" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" '
             f'repeatCount="indefinite"/></rect></g>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}: {W} x {H}, last row y={y:.0f}")
