# CSV Benchmark Input for query_protvar.py

## Problem

`query_protvar.py` currently takes variants as a hardcoded Python list of
VCF-style strings (`"chr pos id ref alt"`), e.g.:

```python
variant_list = ["1 1341803 . C T", "1 6130220 . G A"]
```

A benchmark dataset now exists as `ProtVar/subset_input_benchmark.csv` with
columns `chr,pos,ref,alt,seqNum` (189 variant rows). `seqNum` plays the role
of the VCF ID field (`.` in the hand-written examples), giving each row a
stable numeric identifier. We want `query_protvar.py` to run against this
CSV instead of the hardcoded list, and to be able to trace each result row
back to its source CSV row via `seqNum`.

## Design

### 1. CSV loader

Add `load_variants_from_csv(csv_path)` to `query_protvar.py`:

- Reads the CSV with `pandas.read_csv`.
- For each row, builds a VCF string `f"{chr} {pos} {seqNum} {ref} {alt}"`.
- Returns the list of strings — the exact format `query_protvar()` already
  expects, so `query_protvar()` itself needs no changes.

### 2. Carry seqNum into results

`query_protvar()`'s MCP call echoes the original VCF string back as
`entry["vcf"]` (`variant_input["inputStr"]`). Since `seqNum` is embedded as
the ID field of that string, no extra state needs to be threaded through the
async pipeline. In `filter_result()`, split `entry["vcf"]` on whitespace and
take index 2 (the ID/seqNum field) into a new `"seqNum"` column on each
output row.

### 3. Wire up `main()`

Replace the hardcoded list and output path:

```python
def main():
    variant_list = load_variants_from_csv("ProtVar/subset_input_benchmark.csv")
    annotated = asyncio.run(query_protvar(variant_list))
    df = filter_result(annotated)
    print(df)
    df.to_csv("ProtVar/subset_benchmark_results.csv", index=False)
```

`ProtVar/protvar_results.csv` (output of the old hardcoded example) is left
untouched; benchmark runs write to their own file,
`ProtVar/subset_benchmark_results.csv`.

## Out of scope

- CLI argument for an arbitrary CSV path (not requested; `main()` points
  directly at the benchmark CSV).
- Batching/parallelizing the 189 MCP calls — synchronous sequential calls
  are acceptable at this volume.
