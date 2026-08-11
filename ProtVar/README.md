### Issue 2 - Querying ProtVar via its MCP server:
[ProtVar](https://www.ebi.ac.uk/ProtVar/) is EBI's tool for contextualising human missense variation.
The script `query_protvar.py`, inside this `ProtVar` directory, takes a list of VCF-style variant lines,
queries the [ProtVar MCP server](https://www.ebi.ac.uk/ProtVar/mcp) for coordinate mapping and
pathogenicity predictions, and saves the results in a Pandas dataframe.

## How to run the script:
From the repository root, run: `uv run python ProtVar/query_protvar.py`.

## How it works:
1. `mapVariants` maps each genomic variant to its canonical protein isoform (UniProt accession,
   amino acid position and variant amino acid), along with AlphaMissense (`amScore`) and
   consequence annotations.
2. `getFunction` is then called per canonical isoform to retrieve Missense3D (`m3dPred`) and
   FoldX (`foldxs`) structural predictions, where available. Both are frequently `null`/empty
   for a given position, since ProtVar's structural coverage doesn't extend to every residue.

## The meaning of each output column:
- **vcf** - the original input variant line (chromosome, position, ref, alt).
- **accession** - UniProt accession of the canonical protein isoform.
- **position** - amino acid position on that isoform.
- **aminoAcidChange** - reference/variant amino acid, e.g. `Ala/Thr`.
- **consequence** - predicted consequence of the variant, e.g. `missense`.
- **amPathogenicity** / **amClass** - AlphaMissense pathogenicity score and classification
  (`BENIGN`, `AMBIGUOUS`, `PATHOGENIC`).
- **m3dPrediction** - Missense3D's overall call for the variant, e.g. `Damaging` or `Neutral`.
- **m3dDamagingFeature** - free-text description of the specific structural issue Missense3D
  flagged, when the prediction is damaging (e.g. a disrupted salt bridge, an introduced buried
  charge, or an introduced clash). Empty when no specific feature was flagged or no prediction
  is available for this position.
- **foldxDdg** - FoldX-predicted change in folding free energy (ΔΔG, kcal/mol) from the
  substitution; higher values indicate a more destabilising effect.
- **plddt** - AlphaFold's per-residue confidence score (pLDDT) for the structure FoldX used.