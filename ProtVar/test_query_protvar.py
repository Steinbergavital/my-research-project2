import csv
import os
import tempfile

from query_protvar import load_variants_from_csv, filter_result, _chunk_list


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


def test_filter_result_includes_seqnum():
    rows = [
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
        vcf_strings = load_variants_from_csv(tmp_path)
    finally:
        os.remove(tmp_path)

    annotated = [
        {
            "vcf": vcf_strings[0],
            "isoform": {"accession": "P12345", "isoformPosition": 10},
            "function": {},
        }
    ]

    df = filter_result(annotated)

    assert df.loc[0, "seqNum"] == 3
    assert df.loc[0, "accession"] == "P12345"


def test_chunk_list_splits_into_groups():
    result = list(_chunk_list([1, 2, 3, 4, 5, 6, 7], 3))
    assert result == [[1, 2, 3], [4, 5, 6], [7]]


if __name__ == "__main__":
    test_load_variants_from_csv_builds_vcf_strings()
    test_load_variants_from_csv_matches_real_benchmark_file()
    test_filter_result_includes_seqnum()
    test_chunk_list_splits_into_groups()
    print("All tests passed.")
