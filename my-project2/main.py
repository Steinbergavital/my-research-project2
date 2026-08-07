from os import name
import sys
import csv
import requests
import json

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
    "dbNSFP": "ESM1b_score, GERP++, GERP_92_mammals, bStatistic in CADDv1.7"
}
    response = requests.post(server + ext, params=optional_params,headers=headers, json={"variants": variant_list})
    if not response.ok:
        response.raise_for_status()
        sys.exit("Err1")
    decoded = response.json()

    variant = decoded[0]
    transcript_cons_dict = variant.get("transcript_consequences", [{}])[0]
    alpha_dict = transcript_cons_dict.get("alphamissense", {})
    print("variant  keys:", variant.keys())
    print("transcript_cons_dict  keys:", transcript_cons_dict.keys())
    print("alpha_dict  keys:", alpha_dict.keys())
    print("%%%%%%%")
    print("most_severe_consequence:", variant["most_severe_consequence"])
    domains = transcript_cons_dict.get("domains")

    has_match = any(d.get('name') in ('transmembrane', 'TMHMM') for d in domains)
    bool_in_transmem = False
    if has_match:
        bool_in_transmem = True
    else:
        bool_in_transmem = False

    filtered_data = {
    "most_severe_consequence": variant["most_severe_consequence"],
    "AlphaMissense_patho": alpha_dict.get("am_pathogenicity"),
    "AlphaMissense_class": alpha_dict.get("am_class"),
    "gene_id": transcript_cons_dict.get("gene_id"),
    "popeve_pop_adjusted_esm1v": transcript_cons_dict.get("popeve_pop_adjusted_esm1v"),
    "sift_prediction": transcript_cons_dict.get("sift_prediction"),
    "gerp_92_mammals": transcript_cons_dict.get("GERP_92_mammals"),
    "bstatistic in caddv1.7": transcript_cons_dict.get("bStatistic in CADDv1.7"),
    "cadd_phred": transcript_cons_dict.get("cadd_phred"),
    "popeve_esm1v": transcript_cons_dict.get("popeve_esm1v"),
    "eve_score": transcript_cons_dict.get("eve_score"),
    "blosum62": transcript_cons_dict.get("blosum62"),
    "polyphen_prediction": transcript_cons_dict.get("polyphen_prediction"),
    "gerp++": transcript_cons_dict.get("GERP++"),
    "eve_class": transcript_cons_dict.get("eve_class"),
    "gene_symbol": transcript_cons_dict.get("gene_symbol"),
    "ESM1b_score": transcript_cons_dict.get("ESM1b_score"),
    "sift_score": transcript_cons_dict.get("sift_score"),
    "transcript_id": transcript_cons_dict.get("transcript_id"),
    "gene_symbol_source": transcript_cons_dict.get("gene_symbol_source"),
    "uniprot_isoform_list": transcript_cons_dict.get("uniprot_isoform"),
    "polyphen_score": transcript_cons_dict.get("polyphen_score"),
    "booldomains": bool_in_transmem ,
    "impact": transcript_cons_dict.get("impact"),
    "swissprot_list": transcript_cons_dict.get("swissprot"),
    "trembl": transcript_cons_dict.get("trembl"),
    "uniparc_list": transcript_cons_dict.get("uniparc"),
    "cadd_raw": transcript_cons_dict.get("cadd_raw"),
    "popeve_pop_adjusted_eve": transcript_cons_dict.get("popeve_pop_adjusted_eve"),
}

    print("&&&&&&&&")
    print("Filtered Data:", json.dumps(filtered_data, indent=4))
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
