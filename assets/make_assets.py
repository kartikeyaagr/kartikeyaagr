"""Generate the profile README's dot-matrix SVGs. Usage: python3 assets/make_assets.py assets

Everything is drawn on dot grids: an LED-board header, 12x12 project icons,
link chips and a scrolling dot wave for the footer. Graphite palette.
"""
import math
import random
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

CARD, BORDER, OFF = "#111317", "#22262e", "#22262e"          # tile, outline, unlit dot
TEXT, MID, ACCENT = "#e6e8ec", "#5d6470", "#5b8cff"           # lit dot colours
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# 5x7 dot font, only the letters the name needs
FONT = {
    "K": "10001 10010 10100 11000 10100 10010 10001", "A": "01110 10001 10001 11111 10001 10001 10001",
    "R": "11110 10001 10001 11110 10100 10010 10001", "T": "11111 00100 00100 00100 00100 00100 00100",
    "I": "01110 00100 00100 00100 00100 00100 01110", "E": "11111 10000 10000 11110 10000 10000 11111",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "G": "01110 10001 10000 10111 10001 10001 01111",
    "W": "10001 10001 10001 10101 10101 10101 01010", "L": "10000 10000 10000 10000 10000 10000 11111",
}


def svg(name, w, h, body, label, defs=""):
    (OUT / f"{name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(label)}">\n<defs>{defs}</defs>\n{body}\n</svg>\n')


def card(w, h, rx):
    return (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="{CARD}" stroke="{BORDER}"/>')


def word(text, col, row):
    """Lit cells for a word in the dot font, keyed by column so the header can sweep."""
    cells, c = [], col
    for ch in text:
        for r, bits in enumerate(FONT[ch].split()):
            cells += [(c + i, row + r) for i, b in enumerate(bits) if b == "1"]
        c += 6
    return cells


# ── Header: an LED board spelling the name, swept on column by column ─────────
def header():
    P, cols, rows = 20, 61, 22
    w, h = cols * P, rows * P
    lit = set(word("KARTIKEYA", 4, 3) + word("AGRAWAL", 4, 12))
    cursor = {(c, r) for c in range(47, 52) for r in range(12, 19)}
    rnd = random.Random(11)
    twinkle = rnd.sample([(c, r) for c in range(1, cols - 1) for r in range(1, rows - 1)
                          if (c, r) not in lit | cursor], 14)
    out = [card(w, h, 28)]
    out += [f'<circle cx="{c * P + P / 2}" cy="{r * P + P / 2}" r="2.6" fill="{OFF}"/>'
            for c in range(1, cols - 1) for r in range(1, rows - 1) if (c, r) not in lit | cursor]
    by_col = {}
    for c, r in lit:
        by_col.setdefault(c, []).append(r)
    for c in sorted(by_col):          # one group per column: lights up in a left-to-right sweep
        dots = "".join(f'<circle cx="{c * P + P / 2}" cy="{r * P + P / 2}" r="7"/>' for r in by_col[c])
        out.append(f'<g fill="{TEXT}" opacity="0"><set attributeName="opacity" to="1" '
                   f'begin="{0.2 + (c - 4) * 0.03:.2f}s" fill="freeze"/>{dots}</g>')
    dots = "".join(f'<circle cx="{c * P + P / 2}" cy="{r * P + P / 2}" r="7"/>' for c, r in cursor)
    out.append(f'<g fill="{ACCENT}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
               f'dur="1.1s" repeatCount="indefinite"/>{dots}</g>')
    for c, r in twinkle:
        out.append(f'<circle cx="{c * P + P / 2}" cy="{r * P + P / 2}" r="3.4" fill="{ACCENT}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0.9;0" dur="{rnd.uniform(2.5, 4.5):.1f}s" '
                   f'begin="{rnd.uniform(1.5, 6):.1f}s" repeatCount="indefinite"/></circle>')
    svg("header", w, h, "\n".join(out), "Kartikeya Agrawal")


# ── Project icons: 12x12 dot art on a dark tile ───────────────────────────────
def icon(name, grid, label, alpha=None):
    P, pad = 8, 8
    n = len(grid)
    size = n * P + 2 * pad
    colour = {"t": TEXT, "a": ACCENT, "m": MID}
    out = [card(size, size, 18)]
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            x, y = pad + c * P + P / 2, pad + r * P + P / 2
            if ch == ".":
                out.append(f'<circle cx="{x}" cy="{y}" r="1.3" fill="{OFF}"/>')
            else:
                op = f' opacity="{alpha[r][c]:.2f}"' if alpha else ""
                out.append(f'<circle cx="{x}" cy="{y}" r="3.1" fill="{colour[ch]}"{op}/>')
    svg(f"icon-{name}", size, size, "\n".join(out), label)


def line(grid, a, b, ch):
    """Bresenham line of `ch` cells on a mutable grid, from cell a to cell b."""
    (c0, r0), (c1, r1) = a, b
    dc, dr = abs(c1 - c0), -abs(r1 - r0)
    sc, sr, err = (1 if c0 < c1 else -1), (1 if r0 < r1 else -1), abs(c1 - c0) - abs(r1 - r0)
    while True:
        grid[r0][c0] = ch
        if (c0, r0) == (c1, r1):
            return
        e2 = 2 * err
        if e2 >= dr:
            err += dr; c0 += sc
        if e2 <= dc:
            err += dc; r0 += sr


def icons():
    icon("khana", [
        "....tttt....",
        "..tt....tt..",
        ".t.aa..mm.t.",
        ".t.aa..mm.t.",
        "t..........t",
        "t...tttt...t",
        "t...tttt...t",
        "t..........t",
        ".t.mm..aa.t.",
        ".t.mm..aa.t.",
        "..tt....tt..",
        "....tttt....",
    ], "A thali in dots")
    icon("fineprint", [
        ".ttttttt....",
        ".t.....tt...",
        ".t.mmm..tt..",
        ".t.......t..",
        ".t.aaaaa.t.a",
        ".t.......t..",
        ".t.mmmmm.t..",
        ".t.......t..",
        ".t.aaaa..t.a",
        ".t.......t..",
        ".t.mmm...t..",
        ".ttttttttt..",
    ], "A terms page with two clauses flagged")
    g = [["."] * 12 for _ in range(12)]
    for tr, ch in ((5, "m"), (9, "m"), (1, "a")):   # accent path last so it isn't overdrawn
        line(g, (2, 5), (9, tr + 1 if tr < 5 else tr), ch)
        for r in (tr, tr + 1):
            g[r][10] = g[r][11] = ch
    for r in (5, 6):
        g[r][0] = g[r][1] = "t"
    icon("smartroute", ["".join(row) for row in g], "A request fanning out to three model tiers")
    rnd = random.Random(3)
    alpha = [[min(1, 0.25 + 0.75 * math.exp(-(r - c) / 2.5) * rnd.uniform(0.7, 1)) for c in range(12)] for r in range(12)]
    icon("quark", ["".join("a" if c <= r else "." for c in range(12)) for r in range(12)],
         "A causal attention map", alpha)
    rows = ["tttttttt....", "............", "mmmmmmmmmm..", "............", "mmmmmm......", "............",
            "aaaaaaaa....", "............", "mmmmmmmmm...", "............", "tttttt......", "............"]
    alpha = [[0.3 if row.startswith("m") else 1 for _ in range(12)] for row in rows]
    icon("laya", rows, "A chat log with stale tool output faded out", alpha)


# ── Link chips ────────────────────────────────────────────────────────────────
def chip(name, text):
    cw, h = 9.6, 40                    # mono advance at 16 units; textLength pins it in every font
    w = round(52 + len(text) * cw + 18)
    glyph = "".join(f'<circle cx="{18 + c * 6}" cy="{14 + r * 6}" r="2" fill="{ACCENT}"/>'
                    for c in range(3) for r in range(3) if (c + r) % 2 == 0)
    body = (f'{card(w, h, 20)}{glyph}<text x="52" y="26" font-family="{MONO}" font-size="16" fill="{TEXT}" '
            f'textLength="{len(text) * cw:.0f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
    svg(name, w, h, body, text)


# ── Footer: an equaliser of dots, scrolling one wavelength per loop ───────────
def footer():
    P, cols, rows, L = 20, 61, 6, 20
    w, h = cols * P, rows * P
    dots = []
    for c in range(cols + L):
        height = 1 + round(2.5 + 2.5 * math.sin(2 * math.pi * c / L))
        for r in range(rows):
            lit = r >= rows - height
            fill, rad = (ACCENT, 4.2) if lit else (OFF, 2.4)
            op = f' opacity="{0.35 + 0.65 * (r + 1) / rows:.2f}"' if lit else ""
            dots.append(f'<circle cx="{c * P + P / 2}" cy="{r * P + P / 2}" r="{rad}" fill="{fill}"{op}/>')
    body = (f'<g clip-path="url(#clip)"><g>{"".join(dots)}'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{-L * P} 0" '
            f'dur="6s" repeatCount="indefinite"/></g></g>')
    svg("footer", w, h, body, "", f'<clipPath id="clip"><rect width="{w}" height="{h}"/></clipPath>')


header()
icons()
chip("link-site", "kartikeyaagr.com")
chip("link-email", "kartikay3@outlook.com")
footer()
print("wrote", *sorted(p.name for p in OUT.glob("*.svg")))
