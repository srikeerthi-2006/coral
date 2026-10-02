# 🪸 Coral Light & Heat Resilience Scanner

A tool that scans coral genomes for heat tolerance genes.

## What It Does

Upload a coral protein file (.fasta.gz) and get a **Heat Resilience Score** based on the presence of known heat-protection genes.

## Why This Matters

Coral reefs are dying from rising ocean temperatures. Scientists need to know which corals have the genetic tools to survive heat stress. This tool provides a fast, free way to check.

## Genes Detected

| Gene | Function |
|------|----------|
| HSP70 | Protects proteins from heat damage |
| HSP90 | Protein folding under stress |
| HSP20 | Small heat shock protein |
| SOD | Fights oxidative stress |
| Catalase | Breaks down harmful peroxides |
| Bcl-2 | Prevents cell self-destruction |

## Try It Live

👉 👉 [coral-heat-scanner.streamlit.app](https://coral-heat-scanner.streamlit.app/)

## How It Works

1. Reads protein sequences from a coral genome file
2. Searches for conserved amino acid patterns unique to heat tolerance genes
3. Calculates a resilience score (genes found / genes searched × 100)

## Test Result

*Astrangia poculata* (northern star coral):
- **Score: 100%**
- Found: HSP70, HSP20, SOD, Catalase, Bcl-2
- Missing: none

## Run Locally

```bash
pip install -r requirements.txt
python coral_heat_score.py


