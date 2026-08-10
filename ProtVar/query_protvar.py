from os import name
from socket import timeout
import sys
import csv
import pandas as pd
import requests
import json

def query_protvar(variant_list):
    # Query ProtVar using a variant list and get the response.
    result = mcp__protvar__mapVariants(variants=variant_list)
    #decoded = response.json()
    print(result)
    sys.exit()
    return result

def filter_result(decoded, variant_list):
    rows = []

    for variant_index, variant in enumerate(decoded):
        vcf = variant_list[variant_index]
        preds = variant.get("predictions", [])
        print(preds)
        sys.exit()
        

        row = {
            "vcf": vcf,
            "preds": variant.get("predictions", []),
        }

        rows.append(row)

    df = pd.DataFrame.from_records(rows)
    return df

def main():
    import json
    import requests

    url = "https://www.ebi.ac.uk/ProtVar/api/prediction/cadd"
    variant_list = ["1 1341803 C  T","1 6130220 G  A"]
    headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    decoded_res = query_protvar(variant_list, url, headers)
    filtered_res = filter_result(decoded_res, variant_list)
    print(filtered_res['most_severe_consequence'])

if __name__ == "__main__":
    main()
