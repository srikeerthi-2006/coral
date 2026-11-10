# app.py
# Coral Resilience Multi-Scanner - Streamlit web app.
# Gene patterns and scoring live in scanner.py; graphics in visuals.py.

import hashlib
from pathlib import Path

import streamlit as st

import reports
import visuals as vz
from scanner import (
    ALL_PATTERNS, CATEGORIES, GENE_CATEGORY, CATEGORY_BY_KEY,
    ScanError, read_proteins, scan_proteins, summarise,
)

SAMPLE_FILE = Path(__file__).parent / "apoculata_proteins.fasta.gz"
SAMPLE_NAME = "Astrangia poculata (northern star coral)"
FILE_TYPES = ["gz", "fasta", "fa", "faa", "fas", "txt"]

st.set_page_config(page_title="Coral Resilience Multi-Scanner", page_icon="🪸", layout="wide")
st.markdown(vz.GLOBAL_CSS, unsafe_allow_html=True)


def html_block(markup):
    st.markdown(markup, unsafe_allow_html=True)


def plot(fig):
    st.plotly_chart(fig, width="stretch", config=vz.PLOT_CONFIG)


# ============================================================
# SCANNING (results remembered per file, so moving the slider
# or switching tabs never re-scans)
# ============================================================

def get_scan(data, threshold, animate=True):
    """Return (scan, fresh) for these file bytes, scanning only the first time."""
    key = hashlib.sha256(data).hexdigest()
    cache = st.session_state.setdefault("scans", {})
    if key in cache:
        return cache[key], False

    box = st.empty() if animate else None
    if box:
        box.markdown(vz.scan_progress("read", 0, [], {}, threshold), unsafe_allow_html=True)
    proteins = read_proteins(data)
    genes = list(ALL_PATTERNS)
    done, scores = [], {}

    def tick(gene, score, i, n):
        done.append(gene)
        scores[gene] = score
        if box:
            nxt = genes[i] if i < n else gene
            box.markdown(vz.scan_progress("genes", len(proteins), done, scores, threshold, nxt),
                         unsafe_allow_html=True)

    if box:
        box.markdown(vz.scan_progress("genes", len(proteins), [], {}, threshold, genes[0]), unsafe_allow_html=True)
    scan = scan_proteins(proteins, on_gene_done=tick)
    if box:
        box.empty()
    cache[key] = scan
    return scan, True


def safe_scan(data, threshold, animate=True):
    try:
        return get_scan(data, threshold, animate)
    except ScanError as exc:
        st.error(f"Couldn't read that file. {exc} Try a protein FASTA file (.fasta or .fasta.gz).")
    except Exception:
        st.error("Something went wrong while reading that file. Make sure it's a protein FASTA file (.fasta or .fasta.gz).")
    return None, False


@st.cache_data(show_spinner=False)
def sample_bytes():
    return SAMPLE_FILE.read_bytes() if SAMPLE_FILE.exists() else b""


# ============================================================
# SIDEBAR
# ============================================================

def use_upload():
    st.session_state["source"] = "upload"


def use_sample():
    st.session_state["source"] = "sample"


def clear_all():
    st.session_state["source"] = None
    st.session_state["uploader_gen"] = st.session_state.get("uploader_gen", 0) + 1


with st.sidebar:
    st.markdown("## 🪸 Your coral")
    uploaded = st.file_uploader("Coral protein file", type=FILE_TYPES,
                                key=f"uploader_{st.session_state.get('uploader_gen', 0)}",
                                on_change=use_upload,
                                help="A protein FASTA file, plain or gzipped (.fasta.gz).")
    if sample_bytes():
        st.button("🐚 Try sample coral", on_click=use_sample, width="stretch", help=SAMPLE_NAME)
    threshold = st.slider("'Found' threshold (% similarity)", 50, 100, 80, 1,
                          help="A gene counts as found when its best match is at least this similar.")
    download_area = st.container()
    if st.session_state.get("source") or uploaded is not None:
        st.button("Start over", on_click=clear_all, width="stretch")

source = st.session_state.get("source")
if source == "sample":
    data, name = sample_bytes(), SAMPLE_NAME
elif uploaded is not None:
    data, name = uploaded.getvalue(), uploaded.name
else:
    data, name = None, None


# ============================================================
# HEADER + TABS
# ============================================================

html_block(vz.hero_banner())
tab_scan, tab_compare, tab_why = st.tabs(["🔬 Scan", "⚖️ Compare", "🌊 Why corals bleach"])


# ------------------------------------------------------------
# SCAN TAB
# ------------------------------------------------------------
with tab_scan:
    if not data:
        st.markdown("### Start here")
        html_block(vz.landing_steps())
        st.info("👈 Upload a coral protein file in the sidebar, or press **Try sample coral** to see it in action.")
    else:
        scan, fresh = safe_scan(data, threshold)
        if scan:
            summary = summarise(scan["results"], threshold)
            results = scan["results"]
            if fresh and summary["overall"] >= 75:
                html_block(vz.bubble_burst())

            st.markdown(f"#### {name}")
            st.caption(f"{scan['total_proteins']:,} proteins scanned · {len(summary['found'])} of "
                       f"{len(ALL_PATTERNS)} survival genes found at ≥{threshold}% similarity")

            c1, c2, c3 = st.columns(3)
            with c1:
                with st.container(border=True):
                    plot(vz.gauge(summary["overall"]))
            with c2:
                html_block(vz.reef_health(summary["overall"]))
            with c3:
                with st.container(border=True):
                    st.markdown('<p class="cs-label" style="text-align:center">Category balance</p>',
                                unsafe_allow_html=True)
                    plot(vz.radar([(name, summary["per_category"], vz.CORAL)]))

            html_block(vz.category_cards(summary["per_category"]))

            left, right = st.columns([1.1, 1])
            with left:
                st.markdown("##### Gene similarity")
                for cat in CATEGORIES:
                    html_block(vz.gene_bars(cat, results, threshold))
            with right:
                st.markdown("##### Gene bubble map")
                with st.container(border=True):
                    st.caption("Bubble size = similarity. Hover a bubble to learn what the gene does.")
                    plot(vz.bubble_map(results, threshold))

                st.markdown("##### 🔍 Gene explorer")
                options = list(ALL_PATTERNS)
                labels = {g: f"{CATEGORY_BY_KEY[GENE_CATEGORY[g]]['icon']} {g} — {results.get(g, 0):.1f}%"
                          for g in options}
                gene = st.selectbox("Pick a gene to see where it matched", options, format_func=labels.get)
                html_block(vz.match_viewer(gene, scan["best_hits"].get(gene), results.get(gene, 0.0), threshold))

            st.markdown("##### 🧬 Genome overview")
            g1, g2 = st.columns(2)
            with g1:
                with st.container(border=True):
                    st.caption("How long are this coral's proteins?")
                    plot(vz.length_histogram(scan["lengths"]))
            with g2:
                with st.container(border=True):
                    st.caption("What kinds of amino acids are they built from?")
                    plot(vz.aa_donut(scan["composition"]))

            with download_area:
                st.markdown("**📥 Download report**")
                base = "astrangia_poculata" if source == "sample" else Path(name).name.split(".")[0].replace(" ", "_")
                st.download_button("Report (HTML, with charts)",
                                   reports.html_report(name, scan, summary, threshold),
                                   f"{base}_coral_report.html", "text/html", width="stretch")
                st.download_button("Data table (CSV)", reports.csv_report(scan, threshold),
                                   f"{base}_coral_genes.csv", "text/csv", width="stretch")
                st.download_button("Summary (text)", reports.text_report(name, scan, summary, threshold),
                                   f"{base}_coral_report.txt", "text/plain", width="stretch")


# ------------------------------------------------------------
# COMPARE TAB
# ------------------------------------------------------------
with tab_compare:
    st.markdown("### Compare two corals")
    st.caption("Which coral is better equipped for a warming ocean? Pick two and see them side by side.")

    sides = {}
    ca, cb = st.columns(2)
    for col, label in [(ca, "A"), (cb, "B")]:
        with col:
            with st.container(border=True):
                st.markdown(f"**Coral {label}**")
                choices = ["Upload a file", "Sample coral"] if sample_bytes() else ["Upload a file"]
                mode = st.radio("Source", choices, key=f"cmp_mode_{label}", horizontal=True,
                                label_visibility="collapsed",
                                index=1 if (label == "A" and len(choices) > 1) else 0)
                if mode == "Sample coral":
                    sides[label] = (sample_bytes(), "Sample: A. poculata")
                else:
                    f = st.file_uploader(f"Coral {label} file", type=FILE_TYPES, key=f"cmp_file_{label}",
                                         label_visibility="collapsed")
                    sides[label] = (f.getvalue(), f.name) if f else (None, None)

    (data_a, name_a), (data_b, name_b) = sides["A"], sides["B"]
    if not (data_a and data_b):
        st.info("Choose both corals above to compare them. Tip: use the sample on one side and your own file on the other.")
    else:
        if name_a == name_b:
            name_b = name_b + " (B)"
        scan_a, _ = safe_scan(data_a, threshold)
        scan_b, _ = safe_scan(data_b, threshold)
        if scan_a and scan_b:
            sum_a = summarise(scan_a["results"], threshold)
            sum_b = summarise(scan_b["results"], threshold)

            diff = sum_b["overall"] - sum_a["overall"]
            verdict = "Evenly matched" if abs(diff) < 0.05 else f"{name_b if diff > 0 else name_a} ahead"
            html_block(vz.compare_cards(
                (name_a, sum_a["overall"], len(sum_a["found"]), vz.SEA),
                (name_b, sum_b["overall"], len(sum_b["found"]), vz.CORAL),
                abs(diff), verdict, len(ALL_PATTERNS)))

            r1, r2 = st.columns(2)
            with r1:
                with st.container(border=True):
                    st.caption("Category balance - both corals overlaid")
                    plot(vz.radar([(name_a, sum_a["per_category"], vz.SEA),
                                   (name_b, sum_b["per_category"], vz.CORAL)]))
            with r2:
                with st.container(border=True):
                    st.caption("Head to head - % of genes found per category")
                    plot(vz.butterfly(name_a, sum_a["per_category"], name_b, sum_b["per_category"]))

            st.markdown("##### Gene by gene")
            rows = []
            for g in ALL_PATTERNS:
                a, b = scan_a["results"].get(g, 0.0), scan_b["results"].get(g, 0.0)
                cat = CATEGORY_BY_KEY[GENE_CATEGORY[g]]
                rows.append({"Group": f"{cat['icon']} {cat['short']}", "Gene": g,
                             name_a: a, name_b: b, "Difference": b - a})
            st.dataframe(
                rows, hide_index=True, width="stretch",
                column_config={
                    name_a: st.column_config.ProgressColumn(name_a, format="%.1f%%", min_value=0, max_value=100),
                    name_b: st.column_config.ProgressColumn(name_b, format="%.1f%%", min_value=0, max_value=100),
                    "Difference": st.column_config.NumberColumn("B − A", format="%+.1f"),
                },
            )


# ------------------------------------------------------------
# WHY CORALS BLEACH TAB
# ------------------------------------------------------------
with tab_why:
    st.markdown("### Why do corals bleach?")
    st.markdown(
        "Corals get their colour - and most of their food - from tiny algae living inside them. "
        "When the ocean gets too hot for too long, this partnership breaks down: the algae start "
        "producing toxic oxygen molecules, the coral expels them, and its white skeleton shows through. "
        "A bleached coral isn't dead yet, but if the heat lasts it can starve."
    )
    html_block(vz.bleaching_story())

    html_block(
        '<div class="cs-card" style="background:#0B3C5D;color:#fff;border:none;margin-top:14px">'
        '<span style="font-size:34px;font-weight:700;color:#F28C6B">84%</span>'
        '<span style="font-size:16px;margin-left:10px">of the world\'s coral reef area faced bleaching-level heat stress '
        'during the 2023-2025 global bleaching event - the largest on record (NOAA, 2025).</span>'
        '<p style="font-size:12px;color:#BFE3F5;margin:6px 0 0">Heat stress doesn\'t always mean a reef bleached or died - '
        'it means conditions were hot enough to cause bleaching.</p></div>'
    )

    st.markdown("### Many stresses, many defences")
    st.markdown(
        "Heat is the main cause, but bright light, UV and disease-causing bacteria make things worse - "
        "especially together. Each gene group this scanner looks for is a defence against one of them. "
        "**SOD** and **Catalase** neutralise the toxic oxygen molecules made during heat stress, and **Bcl-2** "
        "stops stressed cells from self-destructing."
    )
    html_block(vz.stressor_map())

    st.markdown("### How the scanner works")
    html_block(vz.how_it_works())
    st.markdown(
        "Each gene has one or more short **patterns** - stretches of amino acids (protein letters) that stay "
        "almost the same in that gene across many animals. The overall resilience score is the share of all "
        f"{len(ALL_PATTERNS)} genes that are found."
    )
    st.caption("Sources: NOAA Coral Reef Watch (April 2025); Science Feedback review of the 84% figure. "
               "Gene roles are simplified for a general audience.")

html_block(vz.footer())
