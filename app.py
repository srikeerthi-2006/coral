import streamlit as st
import gzip
from Bio import SeqIO
import tempfile
import os


# ============================================================
# GENE PATTERNS
# ============================================================

HEAT_PATTERNS = {
    "HSP70":    ["IDLGTTYS", "DLGTTYS"],
    "HSP90":    ["NKEIFLRE"],
    "HSP20":    ["LFDPFSL", "DPFSLD"],
    "SOD":      ["DVWEHAYY", "WEHAYY"],
    "Catalase": ["FDRERIPERVVHAK", "RERIPERVVHAK"],
    "Bcl-2":    ["NWGRIVA", "GRIVAF"],
}

LIGHT_PATTERNS = {
    "GFP-like": ["TYG", "GYSST", "FSVSG"],
    "CP-like":  ["NTFY", "SYG"],
    "MAA":      ["GAST", "GSST", "QGM"],
}

ALL_PATTERNS = {**HEAT_PATTERNS, **LIGHT_PATTERNS}


# ============================================================
# CORE LOGIC
# ============================================================

def scan_genome(file_path, patterns):
    """
    Scan a coral genome file for gene patterns.
    Returns (found_genes, total_proteins).
    """
    found_genes = set()
    total_proteins = 0

    with gzip.open(file_path, "rt") as handle:
        for protein in SeqIO.parse(handle, "fasta"):
            total_proteins += 1
            seq = str(protein.seq)

            for gene, motifs in patterns.items():
                if gene in found_genes:
                    continue
                if any(motif in seq for motif in motifs):
                    found_genes.add(gene)

    return found_genes, total_proteins


# ============================================================
# DISPLAY
# ============================================================

def display_results(found_genes, total_proteins, all_patterns):
    """Show scan results on the page."""
    score = len(found_genes) / len(all_patterns) * 100

    st.success(f"Scan complete! Scanned {total_proteins:,} proteins.")
    st.metric("Combined Resilience Score", f"{score:.1f}%")
        # Visual chart
        # Visual chart - grouped by category
    heat_found = sum(1 for g in HEAT_PATTERNS if g in found_genes)
    light_found = sum(1 for g in LIGHT_PATTERNS if g in found_genes)

    chart_data = {
        "Category": ["Heat Tolerance", "Light Adaptation"],
        "Genes Found": [heat_found, light_found],
    }
    st.bar_chart(chart_data, x="Category", y="Genes Found")

    st.subheader("Genes Found")
    for gene in sorted(found_genes):
        st.write(f"✅ {gene}")

    st.subheader("Genes Not Found")
    for gene in sorted(all_patterns.keys()):
        if gene not in found_genes:
            st.write(f"❌ {gene}")
# ============================================================
# MAIN APP
# ============================================================

st.set_page_config(page_title="Coral Light & Heat Scanner", page_icon="🪸")

st.title("🪸 Coral Light & Heat Resilience Scanner")
st.write("Upload a coral protein file (.fasta.gz) to scan for heat and light adaptation genes.")


uploaded_file = st.file_uploader("Choose a .fasta.gz file", type=["gz"])

if uploaded_file is not None:
    with st.spinner("Scanning genome... this may take 30 seconds"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gz") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        found_genes, total_proteins = scan_genome(tmp_path, ALL_PATTERNS)
        os.unlink(tmp_path)

    display_results(found_genes, total_proteins, ALL_PATTERNS)


