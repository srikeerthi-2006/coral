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
UV_PATTERNS = {
    "DHQ-synthase": ["TIVIPDGEKSKTLETLERIYDALLEAGL"],
}

IMMUNE_PATTERNS = {
    "Galectin": ["HFNPRF"],
}
ALL_PATTERNS = {**HEAT_PATTERNS, **LIGHT_PATTERNS, **UV_PATTERNS, **IMMUNE_PATTERNS}


# ============================================================
# CORE LOGIC
# ============================================================

def get_similarity(seq, pattern):
    """Finds the highest similarity percentage of a pattern within a sequence."""
    best_score = 0
    p_len = len(pattern)
    
    # Slide a window the size of the pattern across the protein
    for i in range(len(seq) - p_len + 1):
        window = seq[i:i+p_len]
        
        # Count how many letters match exactly
        matches = sum(1 for a, b in zip(window, pattern) if a == b)
        score = (matches / p_len) * 100
        
        if score > best_score:
            best_score = score
            
    return best_score


def scan_genome(file_path, patterns):
    """
    Scan a coral genome and return similarities.
    """
    results = {}
    total_proteins = 0

    with gzip.open(file_path, "rt") as handle:
        for protein in SeqIO.parse(handle, "fasta"):
            total_proteins += 1
            seq = str(protein.seq)

            for gene, motifs in patterns.items():
                if gene not in results:
                    results[gene] = 0.0 # Start at 0% similarity
                
                # Check similarity for all motifs of this gene
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
    
    # A gene counts as "Found" if similarity is above 80%
    found_genes = [g for g, score in results.items() if score >= 80.0]
    score = len(found_genes) / len(all_patterns) * 100

    st.success(f"Scan complete! Scanned {total_proteins:,} proteins.")
    st.metric("Combined Resilience Score", f"{score:.1f}%")

    # Visual chart - grouped by category
    heat_found = sum(1 for g in HEAT_PATTERNS if g in found_genes)
    light_found = sum(1 for g in LIGHT_PATTERNS if g in found_genes)
    
    chart_data = {
        "Category": ["Heat Tolerance", "Light Adaptation"],
        "Genes Found": [heat_found, light_found],
    }
    st.bar_chart(chart_data, x="Category", y="Genes Found")

    st.subheader("Similarity Analysis")
    st.write("Percentage indicates how closely the coral's proteins match known survival genes.")
    
    # Show progress bars for every gene
    for gene in sorted(all_patterns.keys()):
        sim = results.get(gene, 0.0)
        
        # Color code: Green if >80%, Yellow if >50%, Red if low
        if sim >= 80.0:
            st.write(f"✅ **{gene}**: {sim:.1f}% similarity")
        elif sim >= 50.0:
            st.write(f"⚠️ **{gene}**: {sim:.1f}% similarity")
        else:
            st.write(f"❌ **{gene}**: {sim:.1f}% similarity")


    # Download button
    result_text = f"Coral Analysis Report\n"
    result_text += f"=====================\n"
    result_text += f"Proteins scanned: {total_proteins:,}\n"
    result_text += f"Score: {score:.1f}%\n\n"
    result_text += f"Genes Found:\n"
    for gene in sorted(found_genes):
        result_text += f"  + {gene}\n"
    result_text += f"\nGenes Not Found:\n"
    for gene in sorted(all_patterns.keys()):
        if gene not in found_genes:
            result_text += f"  - {gene}\n"

    st.download_button(
        label="📥 Download Report",
        data=result_text,
        file_name="coral_report.txt",
        mime="text/plain",
    )
# ============================================================
# MAIN APP
# ============================================================

st.set_page_config(page_title="Coral Light & Heat Scanner", page_icon="🪸")

st.title("🪸Coral Resilience Multi-Scanner")
st.write("Upload a coral protein file (.fasta.gz) to scan for heat and light adaptation genes.")


uploaded_file = st.file_uploader("Choose a .fasta.gz file", type=["gz"])

if uploaded_file is not None:
    with st.spinner("Scanning genome... this may take 30 seconds"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gz") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        results, total_proteins = scan_genome(tmp_path, ALL_PATTERNS)
        os.unlink(tmp_path)

    display_results(results, total_proteins, ALL_PATTERNS)

