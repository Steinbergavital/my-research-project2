import asyncio
import json

import pandas as pd
from mcp.client import Client

PROTVAR_MCP_URL = "https://www.ebi.ac.uk/ProtVar/mcp"


async def _call_tool(client, name, arguments):
    result = await client.call_tool(name, arguments)
    if result.is_error:
        raise RuntimeError(f"ProtVar MCP tool '{name}' failed: {result.content}")
    return json.loads(result.content[0].text)


async def query_protvar(variant_list):
    """Map variants via ProtVar's mapVariants tool, then fetch M3DPred/Foldx
    predictions for each canonical isoform via getFunction."""
    async with Client(PROTVAR_MCP_URL) as client:
        mapping = await _call_tool(client, "mapVariants", {"variants": "\n".join(variant_list)})

        annotated = []
        for variant_input in mapping["content"]["inputs"]:
            vcf = variant_input["inputStr"]
            for genomic_variant in variant_input.get("derivedGenomicVariants", []):
                for gene in genomic_variant.get("genes", []):
                    for isoform in gene.get("isoforms", []):
                        if not isoform.get("canonical"):
                            continue
                        function = await _call_tool(
                            client,
                            "getFunction",
                            {
                                "accession": isoform["accession"],
                                "position": isoform["isoformPosition"],
                                "variantAA": isoform["variantAA"],
                            },
                        )
                        annotated.append({"vcf": vcf, "isoform": isoform, "function": function})
        return annotated


def filter_result(annotated):
    rows = []
    for entry in annotated:
        isoform = entry["isoform"]
        function = entry["function"]
        m3d = function.get("m3dPred") or {}
        foldxs = function.get("foldxs") or []
        foldx = foldxs[0] if foldxs else {}
        am_score = isoform.get("amScore") or {}

        rows.append({
            "vcf": entry["vcf"],
            "accession": isoform["accession"],
            "position": isoform["isoformPosition"],
            "aminoAcidChange": isoform.get("aminoAcidChange"),
            "consequence": isoform.get("consequences"),
            "amPathogenicity": am_score.get("amPathogenicity"),
            "amClass": am_score.get("amClass"),
            "m3dPrediction": m3d.get("prediction"),
            "m3dDamagingFeature": m3d.get("damagingFeature"),
            "foldxDdg": foldx.get("foldxDdg"),
            "plddt": foldx.get("plddt"),
        })
    return pd.DataFrame.from_records(rows)


def main():
    variant_list = ["1 1341803 . C T", "1 6130220 . G A"]
    annotated = asyncio.run(query_protvar(variant_list))
    df = filter_result(annotated)
    print(df)


if __name__ == "__main__":
    main()
