# reports.py
# Downloadable reports: plain text, CSV and a styled HTML page with charts.

import html
from datetime import datetime

import pandas as pd

from scanner import ALL_PATTERNS, CATEGORIES, CATEGORY_BY_KEY, GENE_CATEGORY, GENE_INFO
import visuals as vz


def gene_table(scan, threshold):
    rows = []
    for gene in ALL_PATTERNS:
        s = scan["results"].get(gene, 0.0)
        hit = scan["best_hits"].get(gene, {})
        rows.append({
            "Category": CATEGORY_BY_KEY[GENE_CATEGORY[gene]]["name"],
            "Gene": gene,
            "Similarity %": round(s, 1),
            "Found": "Yes" if s >= threshold else "No",
            "Best protein": hit.get("protein", ""),
            "Position": hit.get("position", ""),
            "Pattern": hit.get("motif", ""),
            "Coral sequence": hit.get("window", ""),
        })
    return pd.DataFrame(rows)


def text_report(name, scan, summary, threshold):
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    lines = [
        "Coral Resilience Report",
        "=======================",
        f"Coral file:        {name}",
        f"Date:              {now}",
        f"Proteins scanned:  {scan['total_proteins']:,}",
        f"Found threshold:   {threshold:.0f}% similarity",
        f"Overall score:     {summary['overall']:.1f}%  ({len(summary['found'])} of {len(ALL_PATTERNS)} genes)",
        "",
    ]
    for cat in CATEGORIES:
        c = summary["per_category"][cat["key"]]
        lines.append(f"{cat['name']}: {c['found']}/{c['total']} found ({c['pct']:.0f}%)")
        for gene in cat["patterns"]:
            s = scan["results"].get(gene, 0.0)
            mark = "+" if s >= threshold else "-"
            lines.append(f"   {mark} {gene:<14} {s:5.1f}%")
        lines.append("")
    lines.append("Made with the Coral Resilience Multi-Scanner - github.com/srikeerthi-2006/coral")
    return "\n".join(lines)


def csv_report(scan, threshold):
    return gene_table(scan, threshold).to_csv(index=False)


def html_report(name, scan, summary, threshold):
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    gauge = vz.gauge(summary["overall"]).to_html(full_html=False, include_plotlyjs="cdn", config=vz.PLOT_CONFIG)
    radar = vz.radar([(name, summary["per_category"], vz.CORAL)]).to_html(full_html=False, include_plotlyjs=False, config=vz.PLOT_CONFIG)
    rows = []
    for _, r in gene_table(scan, threshold).iterrows():
        col = vz.level_color(r["Similarity %"], threshold)
        rows.append(
            f"<tr><td>{html.escape(r['Category'])}</td><td><b>{html.escape(r['Gene'])}</b><br>"
            f"<small>{html.escape(GENE_INFO.get(r['Gene'], ''))}</small></td>"
            f"<td style='color:{col};font-weight:600'>{r['Similarity %']:.1f}%</td><td>{r['Found']}</td>"
            f"<td><code>{html.escape(str(r['Pattern']))}</code><br><code>{html.escape(str(r['Coral sequence']))}</code></td>"
            f"<td><small>{html.escape(str(r['Best protein']))}</small></td></tr>"
        )
    cats = "".join(
        f"<div class='cat' style='background:{c['light']}'><span style='color:{c['color']}'>{c['icon']} {c['name']}</span>"
        f"<b>{summary['per_category'][c['key']]['found']}/{summary['per_category'][c['key']]['total']}</b></div>"
        for c in CATEGORIES
    )
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Coral report - {html.escape(name)}</title>
<style>
body{{font-family:system-ui,sans-serif;color:#0B3C5D;max-width:960px;margin:0 auto;padding:24px;background:#F7FBFD}}
header{{background:#0B3C5D;color:#fff;border-radius:16px;padding:22px 26px}}
header h1{{margin:0;font-size:26px}} header p{{margin:6px 0 0;color:#BFE3F5}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin:16px 0}}
.card{{background:#fff;border:1px solid #DCE8F0;border-radius:14px;padding:10px}}
.cats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}}
.cat{{border-radius:12px;padding:12px 14px;display:flex;justify-content:space-between}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden;margin-top:16px;font-size:14px}}
th,td{{padding:9px 10px;border-bottom:1px solid #EEF3F7;text-align:left;vertical-align:top}}
th{{background:#EAF4FA}} code{{letter-spacing:2px}} small{{color:#6B7C8F}}
footer{{text-align:center;color:#6B7C8F;font-size:13px;margin-top:24px}}
</style></head><body>
<header><h1>🪸 Coral Resilience Report</h1>
<p>{html.escape(name)} · {scan['total_proteins']:,} proteins scanned · threshold {threshold:.0f}% · {now}</p></header>
<div class="grid"><div class="card">{gauge}</div><div class="card">{radar}</div></div>
<div class="cats">{cats}</div>
<table><tr><th>Category</th><th>Gene</th><th>Similarity</th><th>Found</th><th>Pattern / coral match</th><th>Best protein</th></tr>
{''.join(rows)}</table>
<footer>Made with the Coral Resilience Multi-Scanner by Srikeerthi · github.com/srikeerthi-2006/coral</footer>
</body></html>"""
