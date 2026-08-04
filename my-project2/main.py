import sys
import csv
import requests

def query_Ensembl(variant_list, server, ext, headers):
    # Query Ensemble using a variant list and get the response.
    optional_params = {
    "AlphaMissense": 1,
    "Blosum62": 1,
    "CADD": 1,
    "EVE": 1,
    "uniprot": 1,
    "pick": 1,
    "domains": 1,
    "Transcript": 1,
    "dbNSFP": "ESM1b, GERP++, GERP_92_mammals, bStatistic in CADDv1.7"
}
    response = requests.post(server + ext, params=optional_params,headers=headers, json={"variants": variant_list})
    if not response.ok:
        response.raise_for_status()
        sys.exit("Err1")
    decoded = response.json()
    #print((decoded[0]['transcript_consequences'][0]['consequence_terms']))
    return decoded

def filter_result(results, target_consequences, output_csv):
    # Filter the requests result by missense_variant, etc.
    seen_rows = set()

    # Open the file for writing
    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write CSV Header
        writer.writerow(["Variant_ID", "Gene_ID", "Gene_Symbol", "Matched_Consequences"])

        # Process and write rows
        for variant in results:
            variant_id = variant.get("id")
            transcript_consequences = variant.get("transcript_consequences", [])

            for consequence in transcript_consequences:
                consequence_terms = consequence.get("consequence_terms", [])

                # Check for targeted impacts
                matching_terms = target_consequences.intersection(consequence_terms)

                if matching_terms:
                    row = (
                        variant_id,
                        consequence.get("gene_id"),
                        consequence.get("gene_symbol"),
                        ", ".join(matching_terms),
                    )

                    if row not in seen_rows:
                        seen_rows.add(row)
                        writer.writerow(row)

    print(f"Data successfully exported to {output_csv}")

def main():
    import json
    import requests
    print("Hello from my-project2!")

    server = "https://rest.ensembl.org"
    ext = "/vep/homo_sapiens/region"
    variant_list = ["1 1341803 1 C  T . . .","1 6130220 2 G  A . . ."]
    headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    result = query_Ensembl(variant_list, server, ext, headers)

    print((result[0]['transcript_consequences'][0]['consequence_terms']))


    target_consequences = {"missense_variant","start_lost","stop_gained","stop_lost"}
    filter_result(result, target_consequences, "/Users/avitalsteinberg/my-project2/my-research-project2/my-project2/ensembl_filtered_variants.csv")


if __name__ == "__main__":
    main()
