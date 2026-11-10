# scanner.py
# Coral Resilience Multi-Scanner - gene patterns and scanning logic.
#
# The patterns and the scoring rule are Srikeerthi's originals:
# a gene's score is the best % of letters that line up exactly between
# one of its patterns and any same-length window of any coral protein.
# This file only makes that same calculation run much faster (NumPy)
# and remembers WHERE the best match was, for the match viewer.

import gzip
import io
from collections import Counter

import numpy as np
from Bio import SeqIO


# ============================================================
# GENE PATTERNS  (unchanged)
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


# ============================================================
# CATEGORIES
# To add a new group (e.g. calcification), add a dict of patterns
# above and one entry here - every chart picks it up automatically.
# ============================================================

CATEGORIES = [
    {"key": "heat",   "name": "Heat tolerance",   "short": "Heat",   "icon": "🔥",
     "color": "#E4572E", "light": "#FCE3D9", "patterns": HEAT_PATTERNS,
     "stressor": "Rising sea temperature"},
    {"key": "light",  "name": "Light adaptation", "short": "Light",  "icon": "☀️",
     "color": "#E8A317", "light": "#FCF0D4", "patterns": LIGHT_PATTERNS,
     "stressor": "Too much sunlight"},
    {"key": "uv",     "name": "UV protection",    "short": "UV",     "icon": "🛡️",
     "color": "#6C5CE7", "light": "#ECE9FD", "patterns": UV_PATTERNS,
     "stressor": "Ultraviolet radiation"},
    {"key": "immune", "name": "Immune defence",   "short": "Immune", "icon": "🦠",
     "color": "#119C7B", "light": "#DDF4EC", "patterns": IMMUNE_PATTERNS,
     "stressor": "Disease-causing bacteria"},
]

ALL_PATTERNS = {}
GENE_CATEGORY = {}
for _cat in CATEGORIES:
    ALL_PATTERNS.update(_cat["patterns"])
    for _gene in _cat["patterns"]:
        GENE_CATEGORY[_gene] = _cat["key"]

CATEGORY_BY_KEY = {c["key"]: c for c in CATEGORIES}

GENE_INFO = {
    "HSP70":        "Heat shock protein 70 - a 'chaperone' that refolds proteins damaged by heat.",
    "HSP90":        "Heat shock protein 90 - helps other proteins fold correctly under stress.",
    "HSP20":        "Small heat shock protein - stops damaged proteins clumping together.",
    "SOD":          "Superoxide dismutase - neutralises toxic oxygen molecules (ROS) made during heat stress.",
    "Catalase":     "Breaks down hydrogen peroxide, another harmful oxygen by-product of stress.",
    "Bcl-2":        "Blocks programmed cell death, helping cells survive stress instead of self-destructing.",
    "GFP-like":     "Fluorescent proteins - linked to managing strong light and protecting the algae inside.",
    "CP-like":      "Chromoproteins - coloured pigments that can absorb excess light.",
    "MAA":          "Patterns linked to mycosporine-like amino acids - natural sunscreen compounds.",
    "DHQ-synthase": "Enzyme in the pathway corals use to make their own UV sunscreens.",
    "Galectin":     "Sugar-binding protein that recognises microbes - part of coral immunity and symbiosis.",
}


# ============================================================
# ORIGINAL SIMILARITY FUNCTION (kept as the reference definition)
# ============================================================

def get_similarity(seq, pattern):
    """Finds the highest similarity percentage of a pattern within a sequence."""
    best_score = 0
    p_len = len(pattern)
    for i in range(len(seq) - p_len + 1):
        window = seq[i:i + p_len]
        matches = sum(1 for a, b in zip(window, pattern) if a == b)
        score = (matches / p_len) * 100
        if score > best_score:
            best_score = score
    return best_score


# ============================================================
# READING THE FILE
# ============================================================

class ScanError(Exception):
    """Raised when the uploaded file can't be read as protein FASTA."""


def read_proteins(data: bytes):
    """Return a list of (protein_id, sequence) from FASTA bytes (gzipped or not)."""
    if not data:
        raise ScanError("The file is empty.")
    try:
        if data[:2] == b"\x1f\x8b":
            text = gzip.decompress(data).decode("utf-8", errors="replace")
        else:
            text = data.decode("utf-8", errors="replace")
    except (OSError, EOFError) as exc:
        raise ScanError("This .gz file looks damaged or incomplete.") from exc

    try:
        proteins = [(rec.id, str(rec.seq)) for rec in SeqIO.parse(io.StringIO(text), "fasta")]
    except ValueError as exc:
        raise ScanError("It doesn't look like a FASTA file (each protein should start with a '>' line).") from exc
    if not proteins:
        raise ScanError("No protein sequences were found. Is this a FASTA file?")
    return proteins


# ============================================================
# FAST SCAN  (same answer as get_similarity, much faster)
# ============================================================

def scan_proteins(proteins, patterns=ALL_PATTERNS, on_gene_done=None):
    """
    Scan proteins for every gene pattern.

    Returns a dict with:
      results    {gene: best similarity %}
      best_hits  {gene: {protein, motif, window, position, score}}
      total_proteins, lengths, composition

    on_gene_done(gene, score, index, total) is called after each gene,
    so the app can animate progress.
    """
    max_len = max(len(m) for motifs in patterns.values() for m in motifs)
    sep = b"\x00" * max_len  # gap between proteins so no window spans two of them

    pieces, starts, pos = [], [], 0
    for _, seq in proteins:
        starts.append(pos)
        b = seq.encode("latin-1", errors="replace")
        pieces.append(b)
        pieces.append(sep)
        pos += len(b) + max_len
    genome = np.frombuffer(b"".join(pieces), dtype=np.uint8)
    starts = np.array(starts)
    is_sep = (genome == 0).astype(np.int32)
    sep_cum = np.concatenate(([0], np.cumsum(is_sep)))

    results, best_hits = {}, {}
    genes = list(patterns.keys())
    for gi, gene in enumerate(genes):
        best = 0.0
        hit = None
        for motif in patterns[gene]:
            L = len(motif)
            n_win = len(genome) - L + 1
            if n_win <= 0:
                continue
            counts = np.zeros(n_win, dtype=np.uint16)
            for j, ch in enumerate(motif.encode("latin-1")):
                counts += genome[j:j + n_win] == ch
            # only windows that sit fully inside one protein (like the original loop)
            valid = (sep_cum[L:L + n_win] - sep_cum[:n_win]) == 0
            counts[~valid] = 0
            if not valid.any():
                continue
            idx = int(np.argmax(counts))
            score = (int(counts[idx]) / L) * 100
            if score > best:
                best = score
                p = int(np.searchsorted(starts, idx, side="right") - 1)
                pid, seq = proteins[p]
                offset = idx - int(starts[p])
                hit = {
                    "protein": pid,
                    "motif": motif,
                    "window": seq[offset:offset + L],
                    "position": offset + 1,
                    "score": score,
                }
        results[gene] = best
        if hit:
            best_hits[gene] = hit
        if on_gene_done:
            on_gene_done(gene, best, gi + 1, len(genes))

    lengths = [len(s) for _, s in proteins]
    composition = Counter()
    for _, s in proteins:
        composition.update(s)

    return {
        "results": results,
        "best_hits": best_hits,
        "total_proteins": len(proteins),
        "lengths": lengths,
        "composition": dict(composition),
    }


# ============================================================
# SCORING
# ============================================================

def summarise(results, threshold=80.0):
    """Overall and per-category scores at a given 'found' threshold."""
    found = [g for g, s in results.items() if s >= threshold]
    overall = len(found) / len(ALL_PATTERNS) * 100
    per_cat = {}
    for cat in CATEGORIES:
        genes = list(cat["patterns"])
        n_found = sum(1 for g in genes if g in found)
        per_cat[cat["key"]] = {
            "found": n_found,
            "total": len(genes),
            "pct": n_found / len(genes) * 100,
        }
    return {"found": found, "overall": overall, "per_category": per_cat}
