# 🪸 Coral Resilience Multi-Scanner

Scan a coral genome for the genes that help it survive a warming ocean.

## Try It Live

👉 [coral-heat-scanner.streamlit.app](https://coral-heat-scanner.streamlit.app/)

## Why This Matters

Coral reefs are dying from rising ocean temperatures. During the 2023–2025 global bleaching event,
84% of the world's coral reef area faced bleaching-level heat stress (NOAA, 2025). Scientists need
to know which corals have the genetic tools to survive. This tool gives a fast, free way to check.

## What It Does

Upload a coral protein file (`.fasta` or `.fasta.gz`), or try the built-in sample, and get:

- **Resilience score**: a gauge, a reef illustration that bleaches as the score drops, and a radar
  chart across four gene groups
- **Gene similarity bars** and an interactive **gene bubble map**
- **Gene explorer**: shows which coral protein matched each gene, letter by letter
- **Genome overview**: protein lengths and amino-acid makeup
- **Compare mode**: two corals side by side (overlaid radar, head-to-head chart, gene table)
- **Why corals bleach**: an illustrated explainer linking each stress to the genes that defend against it
- **Downloads**: an HTML report with charts, a CSV data table and a text summary

## Genes Detected

| Group | Gene | Function |
|-------|------|----------|
| 🔥 Heat tolerance | HSP70 | Refolds proteins damaged by heat |
| | HSP90 | Protein folding under stress |
| | HSP20 | Small heat shock protein; stops damaged proteins clumping |
| | SOD | Neutralises toxic oxygen molecules (oxidative stress) |
| | Catalase | Breaks down harmful peroxides |
| | Bcl-2 | Prevents cell self-destruction |
| ☀️ Light adaptation | GFP-like | Fluorescent proteins linked to managing strong light |
| | CP-like | Chromoproteins that absorb excess light |
| | MAA | Linked to natural sunscreen compounds |
| 🛡️ UV protection | DHQ-synthase | Enzyme used to make UV sunscreens |
| 🦠 Immune defence | Galectin | Recognises microbes; immunity and symbiosis |

## How It Works

1. Reads every protein sequence in the coral's genome file
2. Slides each known gene pattern along every protein and counts how many letters line up
3. Keeps each gene's best similarity score; a gene counts as **found** at ≥ 80% (adjustable)
4. Resilience score = genes found / genes searched × 100

## Test Result

*Astrangia poculata* (northern star coral), 45,867 proteins:
- **Score: 90.9%** (10 of 11 genes found at ≥ 80%)
- Missing: DHQ-synthase (42.9% best similarity)

## Project Files

| File | What it is |
|------|------------|
| `app.py` | The Streamlit web app (layout, tabs, sidebar) |
| `scanner.py` | Gene patterns, categories and the scanning logic |
| `visuals.py` | Charts, illustrations and page styling |
| `reports.py` | Downloadable reports |
| `coral_heat_score.py` | Original command-line heat scanner |
| `.streamlit/config.toml` | Ocean colour theme |

To add a new gene group (for example calcification genes), add a pattern dictionary and one
entry to `CATEGORIES` in `scanner.py`. Every chart picks it up automatically.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Command-line heat scan:

```bash
python coral_heat_score.py apoculata_proteins.fasta.gz
```

## License

MIT, © 2026 Srikeerthi Kotamaraju
