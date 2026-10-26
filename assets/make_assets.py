"""Generate the bento profile tiles. Usage: python3 assets/make_assets.py assets

Every README row is 960 units wide (576 + 384, 2 x 480) and the README shows
it at 828 px, so all tiles share one scale on desktop. Tiles have fixed pixel
widths, so on a narrow screen they wrap onto their own lines and grow. The
binding case is a 576-unit tile on a ~311 px phone column (x0.54): text on wide
tiles is never under 22 units (~12 px there); on the narrower tiles 16 is enough.
PAD_X / PAD_Y are transparent gutters baked into each tile; PAD_Y is smaller
because inline images already leave a few px of line gap between rows.
"""
import math
import random
import sys
from pathlib import Path
from xml.sax.saxutils import escape

# Graphite palette. card: tile; raise: insets on a tile; line / line2: hairlines,
# faint and stronger; ink: text set on the accent colour
CARD, RAISE, LINE, LINE2, BORDER = "#111317", "#181b21", "#22262e", "#323844", "#22262e"
TEXT, DIM, MUTED, ACCENT, INK = "#e6e8ec", "#8b93a1", "#5d6470", "#5b8cff", "#0b0d11"

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
PAD_X, PAD_Y, H = 6, 3.5, 380   # H: height of the three big rows


def tile(name, w, h, body, label, defs=""):
    x, y, cw, ch = PAD_X, PAD_Y, w - 2 * PAD_X, h - 2 * PAD_Y
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(label)}">
  <defs><clipPath id="card"><rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="24"/></clipPath>{defs}</defs>
  <g clip-path="url(#card)">
    <rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{CARD}"/>
{body}
  </g>
  <rect x="{x + .5}" y="{y + .5}" width="{cw - 1}" height="{ch - 1}" rx="24" fill="none" stroke="{BORDER}"/>
</svg>
"""
    (OUT / f"{name}.svg").write_text(svg)


def t(x, y, s, size, fill=None, font=SANS, weight="normal", anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill or TEXT}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def title(name, sub, size=24, sub_size=16, x=30):
    return t(x, 62, name, size, weight="600") + t(x, 62 + sub_size + 14, sub, sub_size, DIM)


# ── Row 1: intro + orbit ──────────────────────────────────────────────────────
def intro():
    body = f"""
    {t(40, 116, "Kartikeya", 76, font=SERIF)}
    {t(40, 192, "Agrawal", 76, font=SERIF)}
    <rect x="42" y="214" width="56" height="3" fill="{ACCENT}"/>
    {t(40, 262, "AI engineer building tools", 26, DIM)}
    {t(40, 296, "for the common man", 26, DIM)}
    {t(40, 346, "Maths & CS · Ashoka '26 · Jaipur", 22, MUTED, MONO)}"""
    tile("intro", 576, H, body, "Kartikeya Agrawal. AI engineer building tools for the common man. "
         "Maths & CS, Ashoka University '26. Jaipur, India.")


def orbit():
    cx, cy = 192, 152
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}"/>' for r in (44, 78, 112))
    body = f"""
    <circle cx="{cx}" cy="{cy}" r="170" fill="url(#glow)">
      <animate attributeName="opacity" values="0.7;1;0.7" dur="6s" repeatCount="indefinite"/></circle>
    {rings}
    <circle cx="{cx}" cy="{cy}" r="11" fill="{ACCENT}"/>
    <g><circle cx="{cx + 78}" cy="{cy}" r="6" fill="{ACCENT}"/>
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="20s" repeatCount="indefinite"/></g>
    <g><circle cx="{cx}" cy="{cy - 112}" r="4" fill="{TEXT}" opacity="0.6"/>
      <animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="36s" repeatCount="indefinite"/></g>
    {t(cx, 318, "I benchmark it", 28, ACCENT, SERIF, anchor="middle", extra='font-style="italic"')}
    {t(cx, 352, "before I believe it.", 28, ACCENT, SERIF, anchor="middle", extra='font-style="italic"')}"""
    defs = f"""<radialGradient id="glow"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0.28"/>
      <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>"""
    tile("orbit", 384, H, body, "I benchmark it before I believe it.", defs)


# ── Khana: a thali whose compartments get detected and labelled ───────────────
def khana():
    cx, cy, k = 152, 238, 0.88
    food = [(-78, -54, 34, "#c8962f"), (82, -56, 34, "#76863b"), (86, 58, 32, "#e2dccd"), (-6, 98, 26, "#a8452f")]
    bowls = "".join(
        f'<circle cx="{cx + dx * k:.0f}" cy="{cy + dy * k:.0f}" r="{(r + 5) * k:.0f}" fill="{RAISE}" stroke="{LINE2}"/>'
        f'<circle cx="{cx + dx * k:.0f}" cy="{cy + dy * k:.0f}" r="{r * k:.0f}" fill="{c}" opacity="0.85"/>'
        for dx, dy, r, c in food)
    rice = f'<ellipse cx="{cx - 2}" cy="{cy + 5}" rx="39" ry="30" fill="#e9e3d3" opacity="0.9"/>'
    idli = "".join(f'<ellipse cx="{cx + x}" cy="{cy + y}" rx="19" ry="15" fill="#d9d1bf" stroke="#bdb4a0"/>'
                   for x, y in ((-81, 33), (-62, 58)))
    boxes = [  # x, y, w, h, label, begin, label below the box (the idli label would cover the dal box)
        (cx - 103, cy - 83, 70, 70, "dal", 0.6, False),
        (cx + 37, cy - 85, 70, 70, "sabzi", 1.2, False),
        (cx - 104, cy + 14, 66, 64, "idli", 1.8, True),
    ]
    det = ""
    for x, y, w, h, lab, b, below in boxes:
        per = 2 * (w + h)
        tw = round(len(lab) * 12.5 + 18)
        ly = y + h + 2 if below else y - 30
        det += f"""
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="none" stroke="{ACCENT}" stroke-width="2.5"
          stroke-dasharray="{per}" stroke-dashoffset="{per}">
      <animate attributeName="stroke-dashoffset" from="{per}" to="0" dur="0.6s" begin="{b}s" fill="freeze"/></rect>
    <g opacity="0"><set attributeName="opacity" to="1" begin="{b + 0.6}s" fill="freeze"/>
      <rect x="{x}" y="{ly}" width="{tw}" height="28" rx="5" fill="{ACCENT}"/>
      {t(x + 9, ly + 21, lab, 22, INK, weight="600")}</g>"""
    steps = "".join(t(300, 290 + 30 * i, s, 22, DIM if i else TEXT, MONO)
                    for i, s in enumerate(["classify", "→ detect", "→ top-down"]))
    body = f"""
    {title("Khana Thali Vision", "Indian food, dish to whole thali", 28, 22)}
    <circle cx="{cx}" cy="{cy}" r="118" fill="{RAISE}" stroke="{LINE2}" stroke-width="2"/>
    <circle cx="{cx}" cy="{cy}" r="107" fill="none" stroke="{LINE}"/>
    {bowls}{rice}{idli}{det}
    {t(300, 206, "95.78%", 62, ACCENT, SERIF)}
    {t(300, 242, "top-1 · 80 dishes", 22, DIM)}
    {steps}"""
    tile("khana", 576, H, body, "Khana Thali Vision: dish classifier with 95.78% top-1 accuracy on 80 Indian dishes, "
         "then thali compartment detection and top-down correction. Trained on the Khana dataset (arXiv:2509.06006) by Omkar Prabhu.")


# ── SmartRoute: a query fans out to three tiers; the cheap path wins ──────────
def smartroute():
    qx, qy, tx = 66, 186, 250
    tiers = [("cheap", 138, True), ("middle", 186, False), ("frontier", 234, False)]
    paths, nodes, cheap = "", "", ""
    for name, y, win in tiers:
        d = f"M{qx + 8},{qy} C{qx + 90},{qy} {tx - 90},{y} {tx - 8},{y}"
        dash = "" if win else ' stroke-dasharray="4 5"'
        cheap = d if win else cheap
        paths += (f'<path d="{d}" fill="none" stroke="{ACCENT if win else LINE2}" '
                  f'stroke-width="{2.5 if win else 1.5}"{dash}/>')
        nodes += (f'<circle cx="{tx}" cy="{y}" r="7" fill="{ACCENT if win else RAISE}" stroke="{ACCENT if win else LINE2}"/>'
                  + t(tx + 16, y + 6, name, 16, TEXT if win else DIM, MONO))
    body = f"""
    {title("SmartRoute", "LLM inference router + its own test")}
    {paths}{nodes}
    <circle cx="{qx}" cy="{qy}" r="8" fill="{TEXT}"/>
    {t(qx, qy + 32, "query", 16, DIM, MONO, anchor="middle")}
    <circle r="5" fill="{ACCENT}"><animateMotion path="{cheap}" dur="2.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="2.4s" repeatCount="indefinite"/></circle>
    {t(30, 290, "on 200 everyday queries,", 16, DIM)}
    {t(30, 328, "~¼ the cost", 34, ACCENT, SERIF)}
    {t(30, 354, "always-cheap matched routed accuracy", 16, DIM)}"""
    tile("smartroute", 384, H, body, "SmartRoute: an LLM inference router plus the harness that tests whether routing pays. "
         "On 200 everyday queries, always-cheap matched routed accuracy at about a quarter of the cost.")


# ── Quark: a causal attention map, a few cells breathing ──────────────────────
def quark():
    rnd, n, c, g, x0, y0 = random.Random(3), 8, 20, 4, 30, 118
    cells = ""
    for i in range(n):
        for j in range(n):
            x, y = x0 + j * (c + g), y0 + i * (c + g)
            if j > i:
                cells += f'<rect x="{x}" y="{y}" width="{c}" height="{c}" rx="3" fill="none" stroke="{LINE}"/>'
                continue
            o = min(1, 0.12 + 0.8 * math.exp(-(i - j) / 2.2) * rnd.uniform(0.55, 1))
            pulse = ""
            if rnd.random() < 0.3:
                pulse = (f'<animate attributeName="opacity" values="{o:.2f};{min(1, o + .4):.2f};{o:.2f}" dur="3.6s" '
                         f'begin="{rnd.uniform(0, 3.6):.2f}s" repeatCount="indefinite"/>')
            cells += f'<rect x="{x}" y="{y}" width="{c}" height="{c}" rx="3" fill="{ACCENT}" opacity="{o:.2f}">{pulse}</rect>'
    feats = "".join(t(240, 136 + 27 * i, s, 16, DIM, MONO) for i, s in enumerate(["GQA", "RoPE", "SwiGLU", "XSA", "TurboQuant", " KV cache"]))
    body = f"""
    {title("Quark", "a decoder-only LLM, from scratch")}
    {cells}{feats}
    <circle cx="36" cy="340" r="5" fill="{ACCENT}"/>
    {t(50, 346, "56 tests passing · PyTorch", 16, TEXT)}"""
    tile("quark", 384, H, body, "Quark: a decoder-only LLM built from scratch in PyTorch with grouped-query attention, "
         "RoPE, SwiGLU, Exclusive Self Attention and TurboQuant KV-cache compression. 56 tests passing.")


# ── fast-laya-compaction: stale tool output gets cut, messages stay ───────────
def laya():
    rows = [  # role, text, fate, begin
        ("user", "login test fails after refresh", None, 0),
        ("tool", "Read auth.ts", "dropped", 1.0),
        ("tool", "Grep token · 88 hits", "dropped", 1.6),
        ("claude", "expiry check in refresh()", None, 0),
        ("tool", "npm test · 2k lines", "truncated", 2.2),
    ]
    out = ""
    for k, (role, text, fate, b) in enumerate(rows):
        y = 136 + 39 * k
        out += f'<rect x="24" y="{y - 25}" width="528" height="34" rx="6" fill="{RAISE}"/>'
        out += t(36, y, role, 22, ACCENT if role == "claude" else DIM, MONO)
        if not fate:
            out += t(134, y, text, 22, TEXT, MONO)
            continue
        end = round(134 + len(text) * 13.2)
        out += f"""<g>{t(134, y, text, 22, DIM, MONO)}
      <animate attributeName="opacity" to="0.35" begin="{b + .5}s" dur="0.3s" fill="freeze"/></g>
    <line x1="132" y1="{y - 7}" x2="132" y2="{y - 7}" stroke="{ACCENT}" stroke-width="2">
      <animate attributeName="x2" from="132" to="{end}" begin="{b}s" dur="0.5s" fill="freeze"/></line>
    <g opacity="0"><set attributeName="opacity" to="1" begin="{b + .5}s" fill="freeze"/>{t(540, y, fate, 22, ACCENT, MONO, anchor="end")}</g>"""
    body = f"""
    {title("fast-laya-compaction", "keeps the conversation verbatim", 28, 22)}
    {out}
    {t(30, 340, "27–33% smaller", 38, ACCENT, SERIF)}
    {t(546, 340, "421M local model", 22, DIM, anchor="end")}"""
    tile("laya", 576, H, body, "fast-laya-compaction: Claude Code compaction that keeps every message verbatim and trims "
         "stale tool output instead, decided by a 421M-parameter classifier running locally. 27 to 33% smaller on real sessions.")


# ── FinePrint: a terms page whose risky clauses light up ──────────────────────
def fineprint():
    rnd, dx, dy, dw = random.Random(5), 34, 118, 214
    lines, flags = "", {2: 0.6, 5: 1.2, 8: 1.8}   # line index -> begin
    for i in range(10):
        y, w = dy + 26 + 16 * i, rnd.randint(128, 176)
        lines += f'<rect x="{dx + 18}" y="{y}" width="{w}" height="6" rx="3" fill="{LINE2}"/>'
        if i in flags:
            b = flags[i]
            lines += f"""<rect x="{dx + 14}" y="{y - 5}" width="0" height="16" rx="4" fill="{ACCENT}" opacity="0.35">
      <animate attributeName="width" from="0" to="{w + 8}" begin="{b}s" dur="0.4s" fill="freeze"/></rect>
    <circle cx="{dx + dw - 14}" cy="{y + 3}" r="5" fill="{ACCENT}" opacity="0">
      <set attributeName="opacity" to="1" begin="{b + 0.4}s" fill="freeze"/></circle>"""
    flagged = "".join(t(290, 238 + 30 * i, s, 22, TEXT if i == 0 else DIM, MONO)
                      for i, s in enumerate(["• arbitration", "• data sale", "• auto-renewal"]))
    body = f"""
    {title("FinePrint", "a nutrition label for Terms & Conditions", 28, 22)}
    {t(546, 62, "chrome extension", 22, MUTED, MONO, anchor="end")}
    <rect x="{dx}" y="{dy}" width="{dw}" height="190" rx="10" fill="{RAISE}" stroke="{LINE}"/>
    {lines}
    {t(290, 168, "10", 62, ACCENT, SERIF)}
    {t(360, 166, "red-flag", 22, DIM)}
    {t(360, 192, "patterns", 22, DIM)}
    {flagged}"""
    tile("fineprint", 576, 340, body, "FinePrint: a Chrome extension that finds a site's Terms & Conditions and Privacy Policy "
         "and gives a plain-English summary with a 1-10 security score, flagging 10 red-flag patterns such as forced "
         "arbitration, data sale and auto-renewal.")


# ── Status, then the two ways to reach me ─────────────────────────────────────
def status():
    body = f"""
    <circle cx="38" cy="48" r="6" fill="{ACCENT}"/>
    <circle cx="38" cy="48" r="6" fill="none" stroke="{ACCENT}">
      <animate attributeName="r" values="6;16" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.8;0" dur="2s" repeatCount="indefinite"/></circle>
    {t(56, 54, "status", 18, MUTED, MONO)}{t(354, 54, "Oct 2026", 18, MUTED, MONO, anchor="end")}
    {t(30, 164, "Open to", 36, TEXT, weight="600")}
    {t(30, 208, "AI/ML", 36, ACCENT, weight="600")}
    {t(30, 252, "engineering", 36, TEXT, weight="600")}
    {t(30, 296, "roles", 36, TEXT, weight="600")}"""
    tile("status", 384, 340, body, "Status, October 2026: open to AI/ML engineering roles.")


def contact():
    for name, label, value, size, font in [("site", "website", "kartikeyaagr.com", 32, SERIF),
                                           ("email", "email", "kartikay3@outlook.com", 26, SANS)]:
        body = f"""
    {t(30, 54, label, 18, MUTED, MONO)}{t(450, 58, "↗", 26, ACCENT, anchor="end")}
    {t(30, 116, value, size, TEXT, font)}"""
        tile(name, 480, 150, body, f"{label}: {value}")


for stale in ("hero.svg",):
    (OUT / stale).unlink(missing_ok=True)   # replaced by intro + orbit
for make in (intro, orbit, khana, smartroute, quark, laya, fineprint, status, contact):
    make()
print("wrote", *sorted(p.name for p in OUT.glob("*.svg")))
