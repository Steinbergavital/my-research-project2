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
