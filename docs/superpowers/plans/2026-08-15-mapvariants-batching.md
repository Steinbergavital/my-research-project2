# Batch mapVariants Calls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop `query_protvar()` from silently losing variants past the 25th when given a longer list — chunk `mapVariants` calls to the API's undocumented 25-item cap and merge the results, so the full 189-row benchmark gets processed instead of just the first 25.

**Architecture:** Add a pure, network-free chunking helper (`_chunk_list`) and a batch-size constant, then change `query_protvar()`'s internals to loop `mapVariants` calls over chunks and concatenate their `inputs` before the existing per-isoform `getFunction` loop runs unchanged. No signature or return-shape change to `query_protvar()`.

**Tech Stack:** Python 3.10, pandas 2.3.3, uv (run via `uv run python3 ...`). No test framework (pytest) is installed — tests are plain scripts using `assert`, run with `uv run python3 ProtVar/test_query_protvar.py` from the project root.

## Global Constraints

- Project root: `/Users/avitalsteinberg/my-project2/my-research-project2`
- Run all commands via `uv run python3 ...` from the project root.
- Do not add pytest or any new dependency.
- `query_protvar(variant_list)`'s signature and return shape (a list of `{"vcf", "isoform", "function"}` dicts) must not change — only its internals.
- Batches are sequential (one `mapVariants` call at a time), not concurrent — do not use `asyncio.gather` or similar for the batch loop.
- `MAPVARIANTS_BATCH_SIZE` is `25` — this is the ProtVar MCP server's undocumented cap, confirmed empirically (see spec: `docs/superpowers/specs/2026-08-15-mapvariants-batching-design.md`).

---

### Task 1: Chunk mapVariants calls in query_protvar()

**Files:**
- Modify: `ProtVar/query_protvar.py` (add constant + helper near the top; modify `query_protvar()` body at lines 27-51)
- Modify: `ProtVar/test_query_protvar.py` (append new test + import)

**Interfaces:**
- Produces: `_chunk_list(items, size)` — a generator yielding successive `size`-length slices of `items` (the final slice may be shorter). Used only internally by `query_protvar()`; no other task or file depends on it.
- `query_protvar(variant_list)` keeps its existing signature and return shape — this task only changes what happens between receiving `variant_list` and building `annotated`.

- [ ] **Step 1: Write the failing test**

Add this import to the top of `ProtVar/test_query_protvar.py` (alongside the existing `from query_protvar import load_variants_from_csv, filter_result`):

```python
from query_protvar import load_variants_from_csv, filter_result, _chunk_list
```

Add this test function anywhere after the imports:

```python
def test_chunk_list_splits_into_groups():
    result = list(_chunk_list([1, 2, 3, 4, 5, 6, 7], 3))
    assert result == [[1, 2, 3], [4, 5, 6], [7]]
```

Update the `if __name__ == "__main__":` block at the bottom of the file to:

```python
if __name__ == "__main__":
    test_load_variants_from_csv_builds_vcf_strings()
    test_load_variants_from_csv_matches_real_benchmark_file()
    test_filter_result_includes_seqnum()
    test_chunk_list_splits_into_groups()
    print("All tests passed.")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run python3 ProtVar/test_query_protvar.py`
Expected: `ImportError: cannot import name '_chunk_list' from 'query_protvar'`

- [ ] **Step 3: Add the batch-size constant and chunking helper**

In `ProtVar/query_protvar.py`, add this after the `PROTVAR_MCP_URL = ...` line (line 7) and before `async def _call_tool(...)`:

```python
# ProtVar's mapVariants MCP tool silently truncates its response to the
# first 25 input variants per call, regardless of how many are sent —
# confirmed empirically (10/25/26/30/50-variant probes all returned <=25).
MAPVARIANTS_BATCH_SIZE = 25


def _chunk_list(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run python3 ProtVar/test_query_protvar.py`
Expected: `All tests passed.`

- [ ] **Step 5: Rewire query_protvar() to batch its mapVariants calls**

In `ProtVar/query_protvar.py`, replace:

```python
async def query_protvar(variant_list):
    """Map variants via ProtVar's mapVariants tool, then fetch M3DPred/Foldx
    predictions for each canonical isoform via getFunction."""
    async with Client(PROTVAR_MCP_URL) as client:
        mapping = await _call_tool(client, "mapVariants", {"variants": "\n".join(variant_list)})

        annotated = []
        for variant_input in mapping["content"]["inputs"]:
```

with:

```python
async def query_protvar(variant_list):
    """Map variants via ProtVar's mapVariants tool, then fetch M3DPred/Foldx
    predictions for each canonical isoform via getFunction."""
    async with Client(PROTVAR_MCP_URL) as client:
        inputs = []
        for chunk in _chunk_list(variant_list, MAPVARIANTS_BATCH_SIZE):
            mapping = await _call_tool(client, "mapVariants", {"variants": "\n".join(chunk)})
            inputs.extend(mapping["content"]["inputs"])

        annotated = []
        for variant_input in inputs:
```

Leave everything else in the function (from `vcf = variant_input["inputStr"]` at the original line 35 through the `return annotated` at the original line 51) exactly as-is — only the mapping/loop-source lines above change.

- [ ] **Step 6: Run the test suite to verify nothing broke**

Run: `uv run python3 ProtVar/test_query_protvar.py`
Expected: `All tests passed.` (all four tests, including the three from the prior plan)

- [ ] **Step 7: Commit**

```bash
git add ProtVar/query_protvar.py ProtVar/test_query_protvar.py
git commit -m "Batch mapVariants calls past the API's 25-item cap"
```

- [ ] **Step 8 (manual, not automated — hits a live external service): re-run the full benchmark pipeline**

Run: `uv run python3 ProtVar/query_protvar.py` from the project root.
Expected: the printed DataFrame and `ProtVar/subset_benchmark_results.csv` now reflect results for up to all 189 benchmark variants (up from the 25 the un-batched version produced), with `seqNum` values no longer capped at 25. This step is manual because it makes ~8 sequential `mapVariants` calls plus a `getFunction` call per canonical isoform against `https://www.ebi.ac.uk/ProtVar/mcp` — run it yourself when ready rather than as part of automated verification.
