# CSV Benchmark Input for query_protvar.py Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `query_protvar.py` run against the `ProtVar/subset_input_benchmark.csv` benchmark dataset instead of its hardcoded two-variant example list, and trace each result row back to its source CSV row via `seqNum`.

**Architecture:** Add a small CSV-to-VCF-string loader function that produces the same input shape `query_protvar()` already consumes, so `query_protvar()` itself is untouched. Recover `seqNum` from the echoed VCF string inside `filter_result()` rather than threading extra state through the async pipeline. Point `main()` at the new loader and a new output file.

**Tech Stack:** Python 3.10, pandas 2.3.3, uv (run via `uv run python3 ...`). No test framework (pytest) is installed in this project — tests are plain scripts using `assert`, run directly with `uv run python3 <path>`.

## Global Constraints

- Project root: `/Users/avitalsteinberg/my-project2/my-research-project2`
- Run all commands via `uv run python3 ...` from the project root (uses the project's `.venv`, pandas 2.3.3).
- Do not add pytest or any new dependency — this project currently has none beyond `mcp`, `numpy`, `pandas`, `requests` (see `pyproject.toml`).
- `query_protvar()` (the async MCP-calling function) must not change signature or behavior — it must keep accepting a plain list of `"chr pos id ref alt"` strings.
- `ProtVar/protvar_results.csv` (existing hardcoded-example output) must not be touched or overwritten.

---

### Task 1: CSV loader — `load_variants_from_csv`

**Files:**
- Modify: `ProtVar/query_protvar.py` (insert new function after line 14, i.e. right after `_call_tool` and before `async def query_protvar`)
- Create: `ProtVar/test_query_protvar.py`

**Interfaces:**
- Produces: `load_variants_from_csv(csv_path: str) -> list[str]` — reads a CSV with columns `chr,pos,ref,alt,seqNum`, returns a list of `"{chr} {pos} {seqNum} {ref} {alt}"` strings, one per row, in file order. This is the exact list shape `query_protvar(variant_list)` already expects.

- [ ] **Step 1: Write the failing tests**

Create `ProtVar/test_query_protvar.py`:

```python
import csv
import os
import tempfile

from query_protvar import load_variants_from_csv


def test_load_variants_from_csv_builds_vcf_strings():
    rows = [
        {"chr": "1", "pos": "935779", "ref": "G", "alt": "A", "seqNum": "1"},
        {"chr": "1", "pos": "1341803", "ref": "C", "alt": "T", "seqNum": "3"},
    ]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=["chr", "pos", "ref", "alt", "seqNum"])
        writer.writeheader()
        writer.writerows(rows)
        tmp_path = f.name

    try:
        result = load_variants_from_csv(tmp_path)
    finally:
        os.remove(tmp_path)

    assert result == ["1 935779 1 G A", "1 1341803 3 C T"]


def test_load_variants_from_csv_matches_real_benchmark_file():
    result = load_variants_from_csv("ProtVar/subset_input_benchmark.csv")

    assert len(result) == 189
    assert result[0] == "1 935779 1 G A"
    assert result[1] == "1 1336473 2 G C"
    assert result[-1] == "1 27547624 189 C T"


if __name__ == "__main__":
    test_load_variants_from_csv_builds_vcf_strings()
    test_load_variants_from_csv_matches_real_benchmark_file()
    print("All tests passed.")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ProtVar && uv run python3 test_query_protvar.py`
Expected: `ImportError: cannot import name 'load_variants_from_csv' from 'query_protvar'`

- [ ] **Step 3: Implement `load_variants_from_csv`**

In `ProtVar/query_protvar.py`, insert this function after `_call_tool` (after line 14) and before `async def query_protvar(variant_list):`:

```python
def load_variants_from_csv(csv_path):
    """Load a benchmark CSV (columns: chr,pos,ref,alt,seqNum) and return it
    as VCF-style strings in the format query_protvar() expects."""
    df = pd.read_csv(csv_path)
    return [
        f"{row.chr} {row.pos} {row.seqNum} {row.ref} {row.alt}"
        for row in df.itertuples()
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ProtVar && uv run python3 test_query_protvar.py`
Expected: `All tests passed.`

- [ ] **Step 5: Commit**

```bash
git add ProtVar/query_protvar.py ProtVar/test_query_protvar.py
git commit -m "Add CSV loader for benchmark variant input"
```

---

### Task 2: Carry `seqNum` into `filter_result()` output

**Files:**
- Modify: `ProtVar/query_protvar.py:57-73` (the `rows.append({...})` block inside `filter_result`)
- Modify: `ProtVar/test_query_protvar.py` (append new test)

**Interfaces:**
- Consumes: nothing new — operates on `entry["vcf"]`, which is already the string produced by `load_variants_from_csv` (Task 1) and echoed back by the ProtVar MCP API as `inputStr`.
- Produces: `filter_result(annotated)` output DataFrame gains a `"seqNum"` column (the 3rd whitespace-separated field of `entry["vcf"]`).

- [ ] **Step 1: Write the failing test**

Append to `ProtVar/test_query_protvar.py` (add this function, and add its call to the `if __name__ == "__main__":` block):

```python
from query_protvar import filter_result


def test_filter_result_includes_seqnum():
    annotated = [
        {
            "vcf": "1 1341803 3 C T",
            "isoform": {"accession": "P12345", "isoformPosition": 10},
            "function": {},
        }
    ]

    df = filter_result(annotated)

    assert df.loc[0, "seqNum"] == "3"
    assert df.loc[0, "accession"] == "P12345"
```

Update the `if __name__ == "__main__":` block at the bottom of the file to:

```python
if __name__ == "__main__":
    test_load_variants_from_csv_builds_vcf_strings()
    test_load_variants_from_csv_matches_real_benchmark_file()
    test_filter_result_includes_seqnum()
    print("All tests passed.")
```

- [ ] **Step 2: Run tests to verify the new test fails**

Run: `cd ProtVar && uv run python3 test_query_protvar.py`
Expected: `KeyError: 'seqNum'`

- [ ] **Step 3: Implement the `seqNum` extraction**

In `ProtVar/query_protvar.py`, in `filter_result`, change:

```python
        rows.append({
            "vcf": entry["vcf"],
            "accession": isoform["accession"],
```

to:

```python
        rows.append({
            "vcf": entry["vcf"],
            "seqNum": entry["vcf"].split()[2],
            "accession": isoform["accession"],
```

(Leave every other key in that dict literal exactly as-is.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ProtVar && uv run python3 test_query_protvar.py`
Expected: `All tests passed.`

- [ ] **Step 5: Commit**

```bash
git add ProtVar/query_protvar.py ProtVar/test_query_protvar.py
git commit -m "Carry seqNum through to filter_result output"
```

---

### Task 3: Wire `main()` to the benchmark CSV

**Files:**
- Modify: `ProtVar/query_protvar.py:77-82` (the `main()` function)

**Interfaces:**
- Consumes: `load_variants_from_csv` (Task 1), `query_protvar` (unchanged), `filter_result` (Task 2).
- Produces: running `ProtVar/query_protvar.py` now writes `ProtVar/subset_benchmark_results.csv` instead of `ProtVar/protvar_results.csv`.

This task wires together two already-tested pure functions with the pre-existing (unchanged) network-calling `query_protvar()`. Because a full run makes ~189+ live calls to the public ProtVar MCP server, it is not exercised by the automated test script — verify the wiring by inspection plus a manual run.

- [ ] **Step 1: Update `main()`**

In `ProtVar/query_protvar.py`, replace:

```python
def main():
    variant_list = ["1 1341803 . C T", "1 6130220 . G A"]
    annotated = asyncio.run(query_protvar(variant_list))
    df = filter_result(annotated)
    print(df)
    df.to_csv("ProtVar/protvar_results.csv", index=False)
```

with:

```python
def main():
    variant_list = load_variants_from_csv("ProtVar/subset_input_benchmark.csv")
    annotated = asyncio.run(query_protvar(variant_list))
    df = filter_result(annotated)
    print(df)
    df.to_csv("ProtVar/subset_benchmark_results.csv", index=False)
```

- [ ] **Step 2: Verify the change by inspection**

Run: `grep -n "load_variants_from_csv\|subset_benchmark_results\|protvar_results" ProtVar/query_protvar.py`
Expected output shows `main()` calling `load_variants_from_csv("ProtVar/subset_input_benchmark.csv")` and writing to `"ProtVar/subset_benchmark_results.csv"`, and no remaining reference to `ProtVar/protvar_results.csv`.

- [ ] **Step 3: Re-run the full test script**

Run: `cd ProtVar && uv run python3 test_query_protvar.py`
Expected: `All tests passed.` (confirms Task 1/2 changes still hold after this edit)

- [ ] **Step 4: Commit**

```bash
git add ProtVar/query_protvar.py
git commit -m "Point main() at the benchmark CSV and its own output file"
```

- [ ] **Step 5 (manual, not automated — hits a live external service): run the full pipeline**

Run: `cd ProtVar && uv run python3 query_protvar.py`
Expected: prints a DataFrame with up to 189 rows (fewer if some variants don't map to a canonical isoform) including a `seqNum` column, and writes `ProtVar/subset_benchmark_results.csv`. This step is manual because it makes live calls to `https://www.ebi.ac.uk/ProtVar/mcp` for every benchmark variant — run it yourself when ready rather than as part of automated verification.
