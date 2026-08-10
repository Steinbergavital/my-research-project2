from os import name
import sys
import csv
import pandas as pd
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
    return decoded

def filter_result(decoded, variant_list):
    rows = []

    for variant_index, variant in enumerate(decoded):
        vcf = variant_list[variant_index]
        transcript_cons_dict = variant.get("transcript_consequences", [{}])[0]
        alpha_dict = transcript_cons_dict.get("alphamissense", {})
        row = {
            "vcf": vcf,
            "most_severe_consequence": variant.get("most_severe_consequence"),
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
            "swissprot_list": transcript_cons_dict.get("swissprot"),
            "trembl": transcript_cons_dict.get("trembl"),
            "uniparc_list": transcript_cons_dict.get("uniparc"),
            "cadd_raw": transcript_cons_dict.get("cadd_raw"),
            "popeve_pop_adjusted_eve": transcript_cons_dict.get("popeve_pop_adjusted_eve"),
        }

        rows.append(row)

    df = pd.DataFrame.from_records(rows)
    return df

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

    decoded_res = query_Ensembl(variant_list, server, ext, headers)
    filtered_res = filter_result(decoded_res, variant_list)
    print(filtered_res['most_severe_consequence'])





if __name__ == "__main__":
    main()
