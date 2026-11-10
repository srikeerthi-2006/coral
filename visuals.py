# visuals.py
# All the graphics for the Coral Resilience Multi-Scanner:
# page styling, the animated reef banner, SVG illustrations and Plotly charts.

import html

import plotly.graph_objects as go

from scanner import CATEGORIES, CATEGORY_BY_KEY, GENE_CATEGORY, GENE_INFO, ALL_PATTERNS

OCEAN = "#0B3C5D"
DEEP = "#062A43"
SEA = "#1F7A9E"
CORAL = "#E4572E"
SAND = "#F6EAD3"
GOOD = "#119C7B"
MID = "#E8A317"
BAD = "#D64545"
MUTED = "#6B7C8F"

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


def clean(s: str) -> str:
    """Strip indentation and blank lines so Streamlit's markdown keeps the HTML intact."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def level_color(score, threshold):
    if score >= threshold:
        return GOOD
    if score >= 50:
        return MID
    return BAD


# ============================================================
# PAGE STYLE
# ============================================================

GLOBAL_CSS = """
<style>
.cs-hero{position:relative;border-radius:20px;overflow:hidden;margin-bottom:18px;height:240px}
.cs-hero svg{position:absolute;inset:0;width:100%;height:100%}
.cs-hero-text{position:absolute;left:44px;top:50%;transform:translateY(-58%);max-width:62%}
.cs-hero-text h1{color:#FFFFFF !important;font-size:38px;font-weight:700;margin:0;padding:0;line-height:1.15}
.cs-hero-text .a{color:#BFE3F5;font-size:19px;margin:10px 0 0}
.cs-hero-text .b{color:#8FC3DE;font-size:14px;margin:6px 0 0}
@media (max-width:640px){.block-container{padding-top:4.2rem !important}.cs-hero{height:200px}.cs-hero-text{left:20px;right:20px;max-width:none;top:16px;transform:none}
.cs-hero-text h1{font-size:25px}.cs-hero-text .a{font-size:15px}.cs-hero-text .b{display:none}}
.block-container{padding-top:3.2rem !important;padding-bottom:2rem;max-width:1200px}
h1,h2,h3{color:#0B3C5D}
.cs-card{background:#FFFFFF;border:1px solid #DCE8F0;border-radius:16px;padding:16px 18px;margin-bottom:12px}
.cs-label{font-size:13px;color:#6B7C8F;margin:0 0 8px}
.cs-cat{border-radius:14px;padding:12px 14px;border:1px solid transparent}
.cs-cat .t{font-size:13px;margin:0}
.cs-cat .n{font-size:26px;font-weight:600;margin:2px 0 0;color:#0B3C5D}
.cs-cat .s{font-size:12px;color:#6B7C8F;margin:0}
.cs-row{display:grid;grid-template-columns:110px minmax(0,1fr) 58px;gap:10px;align-items:center;font-size:14px;margin:7px 0}
.cs-track{height:10px;background:#EEF3F7;border-radius:6px;overflow:hidden}
.cs-track i{display:block;height:100%;border-radius:6px;transition:width .8s ease}
.cs-mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:16px;letter-spacing:3px;overflow-x:auto;white-space:nowrap}
.cs-chip{display:inline-block;font-size:13px;padding:5px 12px;border-radius:20px;margin:3px;background:#EEF3F7;color:#8496A9;transition:all .4s}
.cs-chip.on{background:#DDF4EC;color:#0B6B53;font-weight:600}
.cs-chip.miss{background:#FBE3E3;color:#9B2C2C}
.cs-grid{display:grid;gap:12px}
.cs-footer{text-align:center;color:#6B7C8F;font-size:13px;margin-top:2.5rem;padding-top:1rem;border-top:1px solid #DCE8F0}
.cs-footer a{color:#1F7A9E;text-decoration:none}
div[data-testid="stTabs"] button p{font-size:16px}
section[data-testid="stSidebar"]{background:#EAF4FA}
@keyframes cs-sway{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}
@keyframes cs-rise{0%{transform:translateY(0);opacity:.9}100%{transform:translateY(-120px);opacity:0}}
@keyframes cs-scan{0%{left:0}100%{left:calc(100% - 4px)}}
@keyframes cs-wave{0%{transform:translateX(0)}100%{transform:translateX(-340px)}}
@keyframes cs-swim{0%{transform:translateX(-60px)}100%{transform:translateX(760px)}}
@keyframes cs-burst{0%{transform:translateY(0) scale(.6);opacity:0}10%{opacity:.85}100%{transform:translateY(-90vh) scale(1.2);opacity:0}}
@keyframes cs-slide{0%,8%{transform:translateX(0)}92%,100%{transform:translateX(var(--d))}}
@keyframes cs-fade{0%,20%{fill:#E4572E}55%,100%{fill:#F4F1EA}}
.cs-sway{transform-origin:50% 100%;transform-box:fill-box;animation:cs-sway 4.5s ease-in-out infinite}
.cs-bub{animation:cs-rise 5s linear infinite}
.cs-wave{animation:cs-wave 9s linear infinite}
.cs-fish{animation:cs-swim 18s linear infinite}
@media (max-width:640px){.cs-row{grid-template-columns:84px minmax(0,1fr) 50px;font-size:13px}}
</style>
"""


# ============================================================
# HERO BANNER
# ============================================================

def hero_banner():
    corals = """
    <g class="cs-sway"><path d="M930 232 L930 150 M930 182 L898 140 M930 168 L966 124 M898 140 L886 108 M898 140 L914 112 M966 124 L960 92 M966 124 L986 100" stroke="#E4572E" stroke-width="13" stroke-linecap="round" fill="none"/></g>
    <g class="cs-sway" style="animation-delay:-1.6s"><path d="M1020 232 L1020 172 M1020 194 L1000 164 M1020 184 L1044 154" stroke="#F28C6B" stroke-width="10" stroke-linecap="round" fill="none"/></g>
    <g class="cs-sway" style="animation-delay:-2.8s"><path d="M850 232 L850 186 M850 204 L834 178 M850 196 L868 172" stroke="#EC8FB0" stroke-width="9" stroke-linecap="round" fill="none"/></g>
    <g class="cs-sway" style="animation-delay:-.8s"><path d="M1090 232 L1090 196 M1090 210 L1076 190 M1090 204 L1104 186" stroke="#F6B26B" stroke-width="8" stroke-linecap="round" fill="none"/></g>
    """
    bubbles = "".join(
        f'<circle class="cs-bub" cx="{x}" cy="220" r="{r}" fill="none" stroke="#BFE3F5" stroke-width="2" style="animation-delay:{d}s"/>'
        for x, r, d in [(880, 5, 0), (950, 4, -1.2), (1000, 6, -2.4), (1060, 3, -3.4), (910, 3, -4.2), (820, 4, -1.8)]
    )
    svg = f"""
    <div class="cs-hero">
    <svg viewBox="0 0 1200 240" preserveAspectRatio="xMaxYMid slice" role="img" aria-label="Animated coral reef">
    <rect width="1200" height="240" fill="{OCEAN}"/>
    <rect y="120" width="1200" height="120" fill="{DEEP}" opacity=".55"/>
    <g class="cs-wave"><path d="M0 24 Q85 6 170 24 T340 24 T510 24 T680 24 T850 24 T1020 24 T1190 24 T1360 24 T1530 24 V0 H0Z" fill="#1F7A9E" opacity=".6"/></g>
    <g fill="#FFFFFF" opacity=".07"><path d="M600 0 L540 240 L620 240Z"/><path d="M760 0 L720 240 L790 240Z"/></g>
    <g class="cs-fish"><path d="M0 0 q14 -9 28 0 q-14 9 -28 0z M28 0 l9 -6 v12z" transform="translate(0 204)" fill="#F6EAD3" opacity=".7"/></g>
    <rect y="226" width="1200" height="14" fill="{SAND}"/>
    {corals}{bubbles}
    </svg>
    <div class="cs-hero-text">
    <h1>🪸 Coral Resilience Multi-Scanner</h1>
    <p class="a">Which corals have the genes to survive a warming ocean?</p>
    <p class="b">Scans a coral genome for heat, light, UV and immune survival genes</p>
    </div></div>
    """
    return clean(svg)


# ============================================================
# LANDING
# ============================================================

def landing_steps():
    steps = [
        ("📤", "1 · Upload", "A coral protein file (.fasta or .fasta.gz) - or press <b>Try sample coral</b> in the sidebar."),
        ("🔬", "2 · Scan", f"{len(ALL_PATTERNS)} survival genes in {len(CATEGORIES)} groups are searched across every protein."),
        ("📊", "3 · Explore", "See the resilience score, charts, the coral's best matches - and compare two corals."),
    ]
    cards = "".join(
        f"""<div class="cs-card" style="margin:0">
        <div style="font-size:30px">{icon}</div>
        <p style="font-size:18px;font-weight:600;margin:6px 0 4px;color:#0B3C5D">{title}</p>
        <p style="font-size:14px;color:#4A5C6E;margin:0">{body}</p></div>"""
        for icon, title, body in steps
    )
    return clean(f'<div class="cs-grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">{cards}</div>')


# ============================================================
# SCANNING ANIMATION
# ============================================================

STRIP = "MKTLIDLGTTYSCVGVFQHGKVEIIANDQGNRTTPSYVAFTDTERLIGDAAKNQVAMNPTNTVFDAKRLIGRRFDDAVVQSDMKHWPFMVVNDAGRPKVQVEYKGETKSFYPEEVSSMVLTKMKEIAEAYLGK"


def scan_progress(stage, total_proteins, done, results, threshold, current=None):
    pct = int(len(done) / len(ALL_PATTERNS) * 100) if stage == "genes" else 3
    chips = []
    for gene in ALL_PATTERNS:
        cls = "cs-chip"
        if gene in done:
            cls += " on" if results[gene] >= threshold else " miss"
        chips.append(f'<span class="{cls}">{html.escape(gene)}</span>')
    if stage == "read":
        status = "Reading the coral's proteins…"
    else:
        status = (f"{total_proteins:,} proteins loaded · checking "
                  f"<b>{html.escape(current or '')}</b> ({len(done)} of {len(ALL_PATTERNS)})")
    block = f"""
    <div class="cs-card">
    <p class="cs-label">🔬 Scanning genome</p>
    <div style="position:relative;height:34px;border-radius:10px;background:#EEF3F7;overflow:hidden;
    font-family:ui-monospace,Menlo,monospace;font-size:13px;line-height:34px;color:#9AAABB;padding-left:10px;white-space:nowrap">{STRIP}
    <span style="position:absolute;top:0;width:4px;height:100%;background:{GOOD};box-shadow:0 0 12px {GOOD};
    animation:cs-scan 1.6s linear infinite alternate"></span></div>
    <div style="display:flex;justify-content:space-between;font-size:14px;color:#4A5C6E;margin:10px 0 6px">
    <span>{status}</span><span>{pct}%</span></div>
    <div class="cs-track" style="margin-bottom:10px"><i style="width:{pct}%;background:{SEA}"></i></div>
    <div>{''.join(chips)}</div></div>
    """
    return clean(block)


def bubble_burst():
    bubbles = "".join(
        f'<span style="position:fixed;bottom:-40px;left:{x}%;width:{s}px;height:{s}px;border-radius:50%;'
        f'border:2px solid #7CC6E8;background:rgba(191,227,245,.35);pointer-events:none;z-index:9999;'
        f'opacity:0;animation:cs-burst {dur}s ease-out {d}s 1 forwards"></span>'
        for x, s, dur, d in [
            (8, 22, 3.2, 0), (15, 14, 2.8, .3), (24, 30, 3.6, .1), (33, 18, 3, .5), (41, 26, 3.4, .2),
            (50, 16, 2.9, .6), (58, 34, 3.8, .1), (66, 20, 3.1, .4), (74, 28, 3.5, .25), (82, 15, 2.7, .55),
            (90, 24, 3.3, .15), (96, 18, 3, .45), (20, 12, 2.6, .8), (46, 12, 2.6, .9), (70, 12, 2.6, .7),
        ]
    )
    return clean(f"<div>{bubbles}</div>")


# ============================================================
# REEF HEALTH ILLUSTRATION (colour fades as the score drops)
# ============================================================

def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def reef_health(score):
    t = max(0.0, min(1.0, score / 100))
    bleached = "#F2EFE8"
    main = _mix(bleached, "#E4572E", t)
    side = _mix(bleached, "#F28C6B", t)
    pink = _mix(bleached, "#EC8FB0", t)
    water = _mix("#DCE6EC", "#CDEAF7", t)
    if score >= 75:
        label, sub = "Healthy reef", "Strong genetic toolkit"
    elif score >= 50:
        label, sub = "Stressed reef", "Some defences missing"
    else:
        label, sub = "Bleaching risk", "Few survival genes found"
    fish = '<path d="M0 0 q10 -7 20 0 q-10 7 -20 0z M20 0 l7 -5 v10z" transform="translate(30 50)" fill="#F6B26B"/>' if score >= 75 else ""
    svg = f"""
    <div class="cs-card" style="text-align:center;height:100%">
    <p class="cs-label">Reef health view</p>
    <svg viewBox="0 0 240 160" width="100%" style="max-width:280px" role="img" aria-label="{label}">
    <rect width="240" height="160" rx="12" fill="{water}"/>
    <rect y="140" width="240" height="20" fill="{SAND}"/>
    <g class="cs-sway"><path d="M120 144 L120 82 M120 106 L94 70 M120 96 L150 60 M94 70 L84 42 M94 70 L108 46 M150 60 L144 30 M150 60 L170 38" stroke="{main}" stroke-width="12" stroke-linecap="round" fill="none"/></g>
    <g class="cs-sway" style="animation-delay:-1.5s"><path d="M54 144 L54 102 M54 118 L38 92 M54 110 L72 88" stroke="{side}" stroke-width="9" stroke-linecap="round" fill="none"/></g>
    <g class="cs-sway" style="animation-delay:-2.6s"><path d="M192 144 L192 108 M192 122 L178 98 M192 116 L208 94" stroke="{pink}" stroke-width="9" stroke-linecap="round" fill="none"/></g>
    {fish}
    <circle class="cs-bub" cx="80" cy="130" r="3" fill="none" stroke="#7CC6E8"/>
    <circle class="cs-bub" cx="168" cy="130" r="2.5" fill="none" stroke="#7CC6E8" style="animation-delay:-2s"/>
    </svg>
    <p style="margin:6px 0 0;font-size:16px;font-weight:600;color:#0B3C5D">{label}</p>
    <p style="margin:0;font-size:13px;color:{MUTED}">{sub}</p></div>
    """
    return clean(svg)


# ============================================================
# CARDS AND BARS
# ============================================================

def category_cards(per_cat):
    cards = []
    for cat in CATEGORIES:
        c = per_cat[cat["key"]]
        cards.append(f"""<div class="cs-cat" style="background:{cat['light']};border-color:{cat['color']}33">
        <p class="t" style="color:{cat['color']}">{cat['icon']} {cat['name']}</p>
        <p class="n">{c['found']}/{c['total']}</p>
        <p class="s">{c['pct']:.0f}% of genes found</p></div>""")
    return clean(f'<div class="cs-grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:6px 0 14px">{"".join(cards)}</div>')


def gene_bars(cat, results, threshold):
    rows = []
    for gene in cat["patterns"]:
        s = results.get(gene, 0.0)
        col = level_color(s, threshold)
        mark = "✅" if s >= threshold else ("⚠️" if s >= 50 else "❌")
        rows.append(f"""<div class="cs-row"><span>{mark} {html.escape(gene)}</span>
        <div class="cs-track"><i style="width:{s:.1f}%;background:{col}"></i></div>
        <span style="text-align:right;font-weight:600;color:{col}">{s:.1f}%</span></div>""")
    return clean(f"""<div class="cs-card"><p class="cs-label" style="color:{cat['color']};font-weight:600">
    {cat['icon']} {cat['name']}</p>{''.join(rows)}</div>""")


def match_viewer(gene, hit, score, threshold):
    cat = CATEGORY_BY_KEY[GENE_CATEGORY[gene]]
    info = html.escape(GENE_INFO.get(gene, ""))
    if not hit:
        body = '<p style="color:#6B7C8F">No protein was long enough to compare with this pattern.</p>'
    else:
        letters = []
        for a, b in zip(hit["window"], hit["motif"]):
            ok = a == b
            letters.append(
                f'<span style="color:{GOOD if ok else BAD};{"" if ok else "text-decoration:underline;"}">{html.escape(a)}</span>'
            )
        marks = "".join("|" if a == b else "&nbsp;" for a, b in zip(hit["window"], hit["motif"]))
        n_ok = sum(1 for a, b in zip(hit["window"], hit["motif"]) if a == b)
        body = f"""
        <p class="cs-label">Best match in protein <b>{html.escape(hit['protein'])}</b> at position {hit['position']:,}</p>
        <div class="cs-mono" style="background:#F5F9FC;border-radius:10px;padding:12px 14px;line-height:1.6">
        <div><span style="color:#8496A9;display:inline-block;width:92px;letter-spacing:0">pattern</span>{html.escape(hit['motif'])}</div>
        <div><span style="display:inline-block;width:92px"></span><span style="color:#B8C6D3">{marks}</span></div>
        <div><span style="color:#8496A9;display:inline-block;width:92px;letter-spacing:0">coral</span>{''.join(letters)}</div></div>
        <p style="font-size:14px;color:#4A5C6E;margin:10px 0 0">{n_ok} of {len(hit['motif'])} letters match
        → <b style="color:{level_color(score, threshold)}">{score:.1f}% similarity</b>. Green letters match the known gene; red ones differ.</p>
        """
    return clean(f"""<div class="cs-card" style="border-left:5px solid {cat['color']}">
    <p style="font-size:20px;font-weight:600;margin:0;color:#0B3C5D">{cat['icon']} {html.escape(gene)}</p>
    <p style="font-size:15px;color:#4A5C6E;margin:4px 0 12px">{info}</p>{body}</div>""")


# ============================================================
# "WHY CORALS BLEACH" GRAPHICS
# ============================================================

def bleaching_story():
    stages = [
        ("Healthy", "#E4572E", "Algae living inside the coral give it colour and food.", True),
        ("Heat stress", "#F28C6B", "Hot water makes the algae produce toxic oxygen molecules.", True),
        ("Algae expelled", "#F7C6B3", "To protect itself, the coral pushes the algae out.", False),
        ("Bleached", "#F2EFE8", "Without algae the white skeleton shows. Long heat can kill it.", False),
    ]
    panels = []
    for i, (title, col, text, algae) in enumerate(stages):
        dots = ""
        if algae:
            dots = "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#6E8B3D"/>' for x, y in [(52, 60), (66, 48), (58, 76), (74, 66), (46, 84)])
        elif i == 2:
            dots = "".join(f'<circle class="cs-bub" cx="{x}" cy="{y}" r="3" fill="#6E8B3D" style="animation-delay:{d}s"/>' for x, y, d in [(40, 40, 0), (88, 50, -1.5), (60, 30, -3)])
        therm = ""
        if i >= 1:
            therm = f'<rect x="104" y="20" width="8" height="60" rx="4" fill="#FFFFFF" stroke="#D64545"/><rect x="106" y="{40 - i * 6}" width="4" height="{40 + i * 6}" rx="2" fill="#D64545"/>'
        panels.append(f"""<div class="cs-card" style="margin:0;text-align:center">
        <svg viewBox="0 0 120 120" width="100%" style="max-width:150px" role="img" aria-label="{title}">
        <rect width="120" height="120" rx="12" fill="#E6F3FA"/><rect y="104" width="120" height="16" fill="{SAND}"/>
        <path d="M60 106 L60 58 M60 76 L42 50 M60 68 L80 42 M42 50 L36 30 M80 42 L86 24" stroke="{col}" stroke-width="10" stroke-linecap="round" fill="none"/>
        {dots}{therm}</svg>
        <p style="font-weight:600;margin:6px 0 2px;color:#0B3C5D">{i + 1}. {title}</p>
        <p style="font-size:13px;color:#4A5C6E;margin:0">{text}</p></div>""")
    return clean(f'<div class="cs-grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">{"".join(panels)}</div>')


def stressor_map():
    cards = []
    for cat in CATEGORIES:
        genes = ", ".join(cat["patterns"])
        cards.append(f"""<div class="cs-cat" style="background:{cat['light']};text-align:center">
        <div style="font-size:30px">{cat['icon']}</div>
        <p style="font-weight:600;margin:4px 0;color:#0B3C5D">{cat['stressor']}</p>
        <p style="font-size:13px;margin:0;color:{cat['color']}">↓ defended by ↓</p>
        <p style="font-size:14px;margin:4px 0 0;color:#0B3C5D"><b>{cat['name']}</b></p>
        <p style="font-size:12px;margin:2px 0 0;color:#4A5C6E">{genes}</p></div>""")
    cards.append("""<div class="cs-cat" style="background:#F6F8FA;border:2px dashed #C5D2DD;text-align:center">
    <div style="font-size:30px;opacity:.6">🫧</div>
    <p style="font-weight:600;margin:4px 0;color:#6B7C8F">Ocean acidification</p>
    <p style="font-size:13px;margin:0;color:#8496A9">↓ defended by ↓</p>
    <p style="font-size:14px;margin:4px 0 0;color:#6B7C8F"><b>Calcification genes</b></p>
    <p style="font-size:12px;margin:2px 0 0;color:#8496A9">Future work</p></div>""")
    return clean(f'<div class="cs-grid" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr))">{"".join(cards)}</div>')


def how_it_works():
    pattern = "NKEIFLRE"
    protein = "MSTNKDIFLRAQGE"
    step = 23
    prot = "".join(f'<text x="{20 + i * step}" y="96" style="font:600 18px monospace;fill:#0B3C5D" text-anchor="middle">{c}</text>' for i, c in enumerate(protein))
    pat = "".join(f'<text x="{20 + i * step}" y="40" style="font:600 18px monospace;fill:#E4572E" text-anchor="middle">{c}</text>' for i, c in enumerate(pattern))
    dist = 3 * step
    svg = f"""
    <div class="cs-card">
    <svg viewBox="0 0 360 120" width="100%" style="max-width:480px;display:block;margin:auto" role="img" aria-label="Sliding window comparison">
    <text x="0" y="14" style="font:12px sans-serif;fill:#6B7C8F">known gene pattern slides along…</text>
    <g style="--d:{dist}px;animation:cs-slide 5s ease-in-out infinite alternate">
    <rect x="8" y="20" width="{len(pattern) * step}" height="28" rx="6" fill="#FCE3D9"/>{pat}
    <rect x="8" y="76" width="{len(pattern) * step}" height="28" rx="6" fill="none" stroke="#1F7A9E" stroke-width="2" stroke-dasharray="4 3"/></g>
    {prot}
    <text x="0" y="118" style="font:12px sans-serif;fill:#6B7C8F">…the coral protein. Each position: count the letters that line up.</text>
    </svg>
    <p style="font-size:14px;color:#4A5C6E;margin:10px 0 0">At the best position here, <b>6 of 8</b> letters line up
    (N K _ I F L R _) → <b>75% similarity</b>. The scanner does this for every pattern, at every position, in every protein,
    and keeps the best score for each gene. A gene counts as <b>found</b> when its best score reaches the threshold (80% by default).</p></div>
    """
    return clean(svg)


def compare_cards(a, b, diff, verdict, n_genes):
    def card(name, score, found, color):
        return f"""<div class="cs-card" style="margin:0;border-top:5px solid {color};border-radius:0 0 14px 14px">
        <p class="cs-label">{html.escape(name)}</p>
        <p style="font-size:34px;font-weight:600;margin:0;color:{color}">{score:.1f}%</p>
        <p style="font-size:13px;color:#6B7C8F;margin:0">{found} of {n_genes} genes found</p></div>"""
    mid = f"""<div class="cs-card" style="margin:0;text-align:center;background:#EAF4FA">
    <p class="cs-label">Difference</p>
    <p style="font-size:34px;font-weight:600;margin:0;color:#0B3C5D">{diff:.1f} pts</p>
    <p style="font-size:13px;color:#6B7C8F;margin:0">{html.escape(verdict)}</p></div>"""
    return clean(f"""<div class="cs-grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr));margin:8px 0 14px">
    {card(*a)}{mid}{card(*b)}</div>""")


def footer():
    return clean("""<div class="cs-footer">
    🪸 Built by <b>Srikeerthi</b> ·
    <a href="https://github.com/srikeerthi-2006/coral" target="_blank">GitHub</a> · MIT license
    </div>""")


# ============================================================
# PLOTLY CHARTS
# ============================================================

def _layout(fig, height=260, **kw):
    kw.setdefault("margin", dict(l=20, r=20, t=30, b=20))
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=OCEAN, size=13),
        **kw,
    )
    return fig


def gauge(score):
    col = GOOD if score >= 75 else (MID if score >= 50 else BAD)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "valueformat": ".1f", "font": {"size": 44, "color": OCEAN}},
        title={"text": "Overall resilience", "font": {"size": 14, "color": MUTED}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)", "tickfont": {"size": 10, "color": MUTED}},
            "bar": {"color": col, "thickness": 0.32},
            "bgcolor": "#EEF3F7",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "#FBE9E9"},
                {"range": [50, 75], "color": "#FCF3DE"},
                {"range": [75, 100], "color": "#E2F4EE"},
            ],
        },
    ))
    return _layout(fig, 250, margin=dict(l=25, r=25, t=50, b=10))


def radar(series):
    """series: list of (name, per_category_dict, color)."""
    labels = [f"{c['icon']} {c['short']}" for c in CATEGORIES]
    fig = go.Figure()
    for name, per_cat, color in series:
        vals = [per_cat[c["key"]]["pct"] for c in CATEGORIES]
        fig.add_trace(go.Scatterpolar(
            r=vals + vals[:1], theta=labels + labels[:1], name=name, fill="toself",
            line=dict(color=color, width=3), fillcolor=color, opacity=0.55,
            hovertemplate="%{theta}: %{r:.0f}%<extra>" + name + "</extra>",
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], ticksuffix="%", tickvals=[25, 50, 75, 100], showticklabels=False, gridcolor="#DCE8F0"),
            angularaxis=dict(gridcolor="#DCE8F0", tickfont=dict(size=13), rotation=90, direction="clockwise"),
        ),
        showlegend=len(series) > 1,
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )
    return _layout(fig, 250 if len(series) == 1 else 360, margin=dict(l=72, r=72, t=25, b=25 if len(series) == 1 else 60))


def bubble_map(results, threshold):
    """Genes in a zig-zag line, grouped by category; bubble area = similarity."""
    fig = go.Figure()
    x, n = 0.0, 0
    for cat in CATEGORIES:
        xs, ys, sizes, text, pos, hover = [], [], [], [], [], []
        for g in cat["patterns"]:
            s = results.get(g, 0.0)
            up = n % 2 == 0
            xs.append(x)
            ys.append(1 if up else 0)
            sizes.append(max(s, 6))
            mark = "✓" if s >= threshold else "✗"
            text.append(f"{g} {mark}")
            pos.append("top center" if up else "bottom center")
            status = "found" if s >= threshold else "not found"
            hover.append(f"<b>{g}</b> - {s:.1f}% similarity ({status})<br>{GENE_INFO.get(g, '')}")
            x += 1
            n += 1
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers+text", text=text, textposition=pos,
            textfont=dict(size=11, color=OCEAN), name=f"{cat['icon']} {cat['short']}",
            marker=dict(size=sizes, sizemode="area", sizeref=2 * 100 / 46 ** 2, color=cat["light"],
                        line=dict(color=cat["color"], width=3)),
            hovertext=hover, hoverinfo="text",
        ))
        x += 0.6
    fig.update_xaxes(visible=False, range=[-1.0, x - 0.4])
    fig.update_yaxes(visible=False, range=[-1.1, 2.1])
    fig.update_layout(legend=dict(orientation="h", y=-0.02, x=0.5, xanchor="center"),
                      hoverlabel=dict(bgcolor="white"))
    return _layout(fig, 300, margin=dict(l=10, r=10, t=10, b=30))


def length_histogram(lengths):
    cap = 3000
    clipped = [min(x, cap) for x in lengths]
    fig = go.Figure(go.Histogram(x=clipped, xbins=dict(start=0, end=cap + 100, size=100),
                                 marker=dict(color="#7CC6E8", line=dict(color="#FFFFFF", width=1)),
                                 hovertemplate="%{x} letters: %{y:,} proteins<extra></extra>"))
    fig.update_xaxes(title="Protein length (amino acids, 3000+ grouped)", gridcolor="#EEF3F7")
    fig.update_yaxes(title="Proteins", gridcolor="#EEF3F7")
    return _layout(fig, 280, bargap=0.05)


AA_GROUPS = [
    ("Water-avoiding", "AVILMFW", "#1F7A9E"),
    ("Water-loving", "STNQYC", "#7CC6E8"),
    ("Positive charge", "KRH", "#E4572E"),
    ("Negative charge", "DE", "#F28C6B"),
    ("Special (G, P)", "GP", "#E8A317"),
]


def aa_donut(composition):
    labels, values, colors = [], [], []
    used = set()
    for name, letters, col in AA_GROUPS:
        labels.append(name)
        values.append(sum(composition.get(a, 0) for a in letters))
        colors.append(col)
        used |= set(letters)
    other = sum(v for k, v in composition.items() if k not in used)
    if other:
        labels.append("Other / stop")
        values.append(other)
        colors.append("#C5D2DD")
    total = sum(values) or 1
    labels_txt = [f"{v / total * 100:.0f}%" if v / total >= 0.03 else "" for v in values]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.58, marker=dict(colors=colors),
                           text=labels_txt, textinfo="text", sort=False,
                           hovertemplate="%{label}: %{percent}<extra></extra>"))
    fig.update_layout(legend=dict(font=dict(size=12)))
    return _layout(fig, 280)


def butterfly(name_a, per_a, name_b, per_b):
    labels = [f"{c['icon']} {c['short']}" for c in CATEGORIES]
    a = [per_a[c["key"]]["pct"] for c in CATEGORIES]
    b = [per_b[c["key"]]["pct"] for c in CATEGORIES]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=labels, x=[-v for v in a], orientation="h", name=name_a, marker_color=SEA,
                         customdata=a, hovertemplate="%{y}: %{customdata:.0f}%<extra>" + name_a + "</extra>",
                         text=[f"{v:.0f}%" for v in a], textposition="inside"))
    fig.add_trace(go.Bar(y=labels, x=b, orientation="h", name=name_b, marker_color=CORAL,
                         hovertemplate="%{y}: %{x:.0f}%<extra>" + name_b + "</extra>",
                         text=[f"{v:.0f}%" for v in b], textposition="inside"))
    fig.update_xaxes(range=[-105, 105], tickvals=[-100, -50, 0, 50, 100], ticktext=["100%", "50%", "0", "50%", "100%"], gridcolor="#EEF3F7")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(barmode="relative", bargap=0.35, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
    return _layout(fig, 320, margin=dict(l=20, r=20, t=20, b=50))
