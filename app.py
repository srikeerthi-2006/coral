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

DISEASE_PATTERNS = {
    "Galectin": ["HFNPRF"],
}

ALL_PATTERNS = {**HEAT_PATTERNS, **LIGHT_PATTERNS, **DISEASE_PATTERNS}


# ============================================================
# CORE LOGIC
# ============================================================

def get_similarity(seq, pattern):
    """Finds the highest similarity percentage of a pattern within a sequence."""
    best_score = 0
    p_len = len(pattern)
    
    for i in range(len(seq) - p_len + 1):
        window = seq[i:i+p_len]
        matches = sum(1 for a, b in zip(window, pattern) if a == b)
        score = (matches / p_len) * 100
        
        if score > best_score:
            best_score = score
            
    return best_score


def scan_genome(file_path, patterns):
    """Scan a coral genome and return similarity percentages."""
    results = {}
    total_proteins = 0

    with gzip.open(file_path, "rt") as handle:
        for protein in SeqIO.parse(handle, "fasta"):
            total_proteins += 1
            seq = str(protein.seq)

            for gene, motifs in patterns.items():
                if gene not in results:
                    results[gene] = 0.0
                
                for motif in motifs:
                    score = get_similarity(seq, motif)
                    if score > results[gene]:
                        results[gene] = score

    return results, total_proteins


# ============================================================
# DISPLAY
# ============================================================

def display_results(results, total_proteins, all_patterns):
    """Show scan results with similarity percentages."""
    
    found_genes = [g for g, score in results.items() if score >= 80.0]
    score = len(found_genes) / len(all_patterns) * 100

    st.success(f"Scan complete! Scanned {total_proteins:,} proteins.")
    st.metric("Combined Resilience Score", f"{score:.1f}%")

    # Visual chart
    heat_found = sum(1 for g in HEAT_PATTERNS if g in found_genes)
    light_found = sum(1 for g in LIGHT_PATTERNS if g in found_genes)
    disease_found = sum(1 for g in DISEASE_PATTERNS if g in found_genes)
    
    chart_data = {
        "Category": ["Heat Tolerance", "Light Adaptation", "Disease Resistance"],
        "Genes Found": [heat_found, light_found, disease_found],
    }
    st.bar_chart(chart_data, x="Category", y="Genes Found")

    st.subheader("Similarity Analysis")
    st.write("Percentage indicates how closely the coral's proteins match known survival genes.")
    
    for gene in sorted(all_patterns.keys()):
        sim = results.get(gene, 0.0)
        
        if sim >= 80.0:
            st.write(f"✅ **{gene}**: {sim:.1f}% similarity")
        elif sim >= 50.0:
            st.write(f"⚠️ **{gene}**: {sim:.1f}% similarity")
        else:
            st.write(f"❌ **{gene}**: {sim:.1f}% similarity")


# ============================================================
# MAIN APP
# ============================================================

st.set_page_config(page_title="Coral Light & Heat Scanner", page_icon="🪸")

st.title("🪸 Coral Resilience Multi-Scanner")
st.write("Upload a coral protein file (.fasta.gz) to scan for heat, light, and disease resistance genes.")

uploaded_file = st.file_uploader("Choose a .fasta.gz file", type=["gz"])

if uploaded_file is not None:
    with st.spinner("Scanning genome... this may take 30 seconds"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gz") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        results, total_proteins = scan_genome(tmp_path, ALL_PATTERNS)
        os.unlink(tmp_path)

    display_results(results, total_proteins, ALL_PATTERNS)
