# Batch mapVariants Calls to Cover the Full Benchmark

## Problem

Running `ProtVar/query_protvar.py` against the 189-row `subset_input_benchmark.csv`
produced only 25 result rows in `ProtVar/subset_benchmark_results.csv`, with
no error. Direct probing of the ProtVar MCP server's `mapVariants` tool
confirmed the cause: it silently truncates its response to the first 25
input variants, no matter how many are sent in one call.

```
sent 10, got back 10
sent 25, got back 25
sent 26, got back 25
sent 30, got back 25
sent 50, got back 25
```

`query_protvar()` currently sends the entire `variant_list` in one
`mapVariants` call (`ProtVar/query_protvar.py:21`), so any list longer than
25 silently loses data — the 164 variants past index 25 are never even
sent to `getFunction`.

## Design

### 1. Batch size constant

Add to `ProtVar/query_protvar.py`, near the top-level constants:

```python
# ProtVar's mapVariants MCP tool silently truncates its response to the
# first 25 input variants per call, regardless of how many are sent —
# confirmed empirically (10/25/26/30/50-variant probes all returned <=25).
MAPVARIANTS_BATCH_SIZE = 25
```

### 2. Pure chunking helper

```python
def _chunk_list(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]
```

No network, no async — trivially unit-testable in isolation.

### 3. `query_protvar()` batches internally

Replace the single `mapVariants` call with a sequential loop over chunks,
merging each chunk's `inputs` list before continuing to the existing
per-isoform `getFunction` loop:

```python
async def query_protvar(variant_list):
    async with Client(PROTVAR_MCP_URL) as client:
        inputs = []
        for chunk in _chunk_list(variant_list, MAPVARIANTS_BATCH_SIZE):
            mapping = await _call_tool(client, "mapVariants", {"variants": "\n".join(chunk)})
            inputs.extend(mapping["content"]["inputs"])

        annotated = []
        for variant_input in inputs:
            ...  # unchanged from here down
```

`query_protvar()`'s signature and return shape are unchanged — this is
purely an internal implementation change. Chunks are processed one at a
time (sequential, not concurrent), matching the existing pattern of
sequential `getFunction` calls and avoiding concurrent load on the public
ProtVar server.

## Testing

Add a unit test for `_chunk_list` to `ProtVar/test_query_protvar.py` (plain
`assert`, no network):

```python
def test_chunk_list_splits_into_groups():
    result = list(_chunk_list([1, 2, 3, 4, 5, 6, 7], 3))
    assert result == [[1, 2, 3], [4, 5, 6], [7]]
```

No test is added for the batched loop inside `query_protvar()` itself —
this project has no mocking infrastructure for the MCP client, and the
live run against the real server is the integration check for this change.

## Out of scope

- Retry logic or backoff for failed `mapVariants` calls.
- Rate-limit handling.
- Concurrent/parallel batch execution (sequential chosen to avoid
  hammering the public ProtVar server with simultaneous requests).

## Verification

After implementation, re-run `uv run python3 ProtVar/query_protvar.py`
from the project root once, manually, against the live ProtVar MCP server.
Expect `ProtVar/subset_benchmark_results.csv` to now reflect results for
(up to) all 189 benchmark variants instead of just the first 25.
