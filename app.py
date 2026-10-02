import streamlit as st
import gzip
from Bio import SeqIO
import tempfile
import os

st.set_page_config(page_title="Coral Heat Scanner", page_icon="🪸")

st.title("🪸 Coral Light & Heat Resilience Scanner")
st.write("Upload a coral protein file (.fasta.gz) to scan for heat tolerance genes.")

heat_patterns = {
    "HSP70":   ["IDLGTTYS", "DLGTTYS"],
    "HSP90":   ["NKEIFLRE"],
    "HSP20":   ["LFDPFSL", "DPFSLD"],
    "SOD":     ["DVWEHAYY", "WEHAYY"],
    "Catalase":["FDRERIPERVVHAK", "RERIPERVVHAK"],
    "Bcl-2":   ["NWGRIVA", "GRIVAF"],
    "GFP-like":["TYG", "GYSST", "FSVSG"],
    "CP-like": ["NTFY", "SYG"],
    "MAA":     ["GAST", "GSST", "QGM"],
}

uploaded_file = st.file_uploader("Choose a .fasta.gz file", type=["gz"])

if uploaded_file is not None:
    with st.spinner("Scanning genome... this may take 30 seconds"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gz") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        found_genes = set()
        total_proteins = 0

        with gzip.open(tmp_path, "rt") as handle:
            for protein in SeqIO.parse(handle, "fasta"):
                total_proteins += 1
                seq = str(protein.seq)
                for gene, patterns in heat_patterns.items():
                    if gene in found_genes:
                        continue
                    for pattern in patterns:
                        if pattern in seq:
                            found_genes.add(gene)
                            break

        os.unlink(tmp_path)

    score = len(found_genes) / len(heat_patterns) * 100

    st.success(f"Scan complete! Scanned {total_proteins:,} proteins.")

    st.metric("Combined Resilience Score", f"{score:.1f}%")

    st.subheader("Genes Found")
    for gene in sorted(found_genes):
        st.write(f"✅ {gene}")

    st.subheader("Genes Not Found")
    for gene in sorted(heat_patterns.keys()):
        if gene not in found_genes:
            st.write(f"❌ {gene}")

    st.caption(f"Analyzed file: {uploaded_file.name}")
