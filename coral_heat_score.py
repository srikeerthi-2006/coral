# coral_heat_score.py
# Coral Heat Resilience Scanner

import gzip
import sys
from Bio import SeqIO

# Get filename from command line, or use default
if len(sys.argv) > 1:
    protein_file = sys.argv[1]
else:
    protein_file = "apoculata_proteins.fasta.gz"

heat_patterns = {
    "HSP70":   ["IDLGTTYS", "DLGTTYS"],
    "HSP90":   ["NKEIFLRE"],
    "HSP20":   ["LFDPFSL", "DPFSLD"],
    "SOD":     ["DVWEHAYY", "WEHAYY"],
    "Catalase":["FDRERIPERVVHAK", "RERIPERVVHAK"],
    "Bcl-2":   ["NWGRIVA", "GRIVAF"],
}

found_genes = set()
total_proteins = 0

print(f"Scanning: {protein_file}")
print("-" * 40)

with gzip.open(protein_file, "rt") as handle:
    for protein in SeqIO.parse(handle, "fasta"):
        total_proteins += 1
        seq = str(protein.seq)
        for gene, patterns in heat_patterns.items():
            if gene in found_genes:
                continue
            for pattern in patterns:
                if pattern in seq:
                    found_genes.add(gene)
                    print(f"  Found {gene} -> {protein.id}")
                    break

print("-" * 40)
print(f"Coral: {protein_file}")
print(f"Total proteins scanned: {total_proteins}")
print(f"Heat genes found: {len(found_genes)} out of {len(heat_patterns)}")
print(f"Heat Resilience Score: {len(found_genes) / len(heat_patterns) * 100:.1f}%")
print(f"Genes: {sorted(found_genes)}")