### Issue 2 - Querying ProtVar via its MCP server:
[ProtVar](https://www.ebi.ac.uk/ProtVar/) is EBI's tool for contextualising human missense variation.
The script `query_protvar.py`, inside this `ProtVar` directory, reads a benchmark CSV of variants,
queries the [ProtVar MCP server](https://www.ebi.ac.uk/ProtVar/mcp) for coordinate mapping and
pathogenicity predictions, and saves the results to a CSV.

## How to run the script:
From the repository root, run: `uv run python3 ProtVar/query_protvar.py`.

By default it reads `ProtVar/subset_input_benchmark.csv` and writes
`ProtVar/subset_benchmark_results.csv`.

## The input CSV:
`load_variants_from_csv()` expects columns `chr,pos,ref,alt,seqNum`:
- **chr**, **pos**, **ref**, **alt** - the variant's chromosome, position, reference and
  alternate allele (VCF-style).
- **seqNum** - a numeric ID for the row, used in place of the VCF `.` ID field. It is carried
  through to the output so each result row can be traced back to its source CSV row.

## How it works:
1. `mapVariants` maps each genomic variant to its canonical protein isoform (UniProt accession,
   amino acid position and variant amino acid), along with AlphaMissense (`amScore`) and
   consequence annotations. ProtVar's `mapVariants` tool silently truncates its response to the
   first 25 input variants per call, so `query_protvar()` splits the variant list into batches of
   `MAPVARIANTS_BATCH_SIZE` (25) and calls `mapVariants` once per batch, merging the results.
2. `getFunction` is then called per canonical isoform to retrieve Missense3D (`m3dPred`), FoldX
   (`foldxs`), conservation, EVE, and PopEVE predictions, where available. These are frequently
   `null`/empty for a given position, since ProtVar's coverage doesn't extend to every residue.

## The meaning of each output column:
- **vcf** - the original input variant line (chromosome, position, seqNum, ref, alt).
- **seqNum** - the source CSV row's numeric ID (see above).
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
- **conservScore** - sequence conservation score at this position.
- **eveScore** / **eveClass** - EVE (Evolutionary model of Variant Effect) pathogenicity score
  and classification (e.g. `BENIGN`, `PATHOGENIC`, `UNCERTAIN`).
- **popEve** - PopEVE score, combining EVE with population allele frequency.

Note that a variant can produce more than one output row (one per canonical isoform across genes
it overlaps), and some variants produce none (no canonical-isoform match at ProtVar) - `seqNum`
is not a one-to-one key back to the input CSV.