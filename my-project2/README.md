### Issue 1 - Querying the ENSEMBL REST API:
https://rest.ensembl.org/documentation/info/vep_region_post
The script main.py, which is inside the my-project2 directory and the tracked repository my-research-project directory takes 2 VCF variant lines, (based on the CSV file)
It downloads features and labels from ENSEMBL's REST API and saves them in a Pandas dataframe. 
## How to run the script:
Cd into the tracked directory. Then run: uv run my-project2/main.py.
## The meaning of each feature or label:
**VCF** - The input sequence.
**Most_severe_consequence** - All of the mutations in our database involved a change in a single amino acide. We are interested only in missense mutations. (not big changes like changes in stop codons, etc.)
**AlphaMissense_patho** - Annotates missense variants with the pre-computed AlphaMissense 0-1 pathogenicity scores. 0-0.34 likely benign, 0.34-0.66 uncertain, 0.66-1 likely pathogenic.
**AlphaMissense_class** - Annotates missense variants with the corresponding pre-computed AlphaMissense classifications: likely benign, uncertain, and likely pathogenic.
**gene_id** - The ENSEMBL gene ID. The ENS standas for ENSEMBL, G for gene, and 11 additional digits are in this gene identifier.
**popeve_pop_adjusted_esm1v** - From dbNSFP, originally from: https://github.com/debbiemarkslab/popEVE. These are the adjusted scores.
**sift_prediction** - From dbNSFP, it's either deleterious or tolerated. 
**gerp_92_mammals** - GERP conservation score calculated based on multiple sequence alignments of 92 mammals.
**bStatistic in CADDv1.7** - Background selection (B) value estimates from doi.org/10.1371/journal.pgen.1000471. Ranges from 0 to 1000. It estimates the expected fraction (*1000) of neutral diversity present at a site. Values close to 0 represent near complete removal of diversity as a result of background selection and values near 1000 indicating absent of background selection. Data from CADD v1.4.
**cadd_phred** - For improved interpretability, the scores are transformed into a PHRED-like (i.e. negative log10-derived) rank score based on the genome-wide distribution of scores for all ∼9 billion potential SNVs. The scale is 1-99. The higher - the more pathogenic. 
**popeve_esm1v** - Raw, non-adjusted scores. 
**eve_score** - 0-1 pathogenicity scores. 0 is benign, 1 is pathogenic.
**blosum62** - +11 to -4 conservation scores, positive is a conservative amino acide substitution, negative is non-conservative.
**polyphen_prediction** - 0.0-1.0 pathogenicity scores, 0 is benign and 1 is pathogenic.
**GERP++** - -12 to +6 conservation scores, negative positions are not conserved and positive positions are conserved. 
**eve_class** - Benign or pathogenic. 
**gene_symbol** - HGNC gene ID symbol. 
**ESM1b_score** - negative to close to zero. Near 0 is tolerated, negative is damaging. 
**sift_score** - SIFT score (SIFTori). Scores range from 0 to 1. The smaller the score the more likely the SNP has damaging effect. 
**transcript_id** - The ENSEMBL transcript ID. The ENS standas for ENSEMBL, T for gene, and 11 additional digits are in this gene identifier.
**gene_symbol_source** - Specifies which database the gene symbol came from.
**uniprot_isoform_list** - Include best match accessions for translated protein products from the UniProt-related database UniParc.
**polyphen_score**: 0.0-1.0 pathogenicity scores where 0 means benign and 1 means pathogenic.
**swissprot_list** - Include best match accessions for translated protein products from the UniProt-related database Swiss-Prot.
**trembl** - Include best match accessions for translated protein products from the UniProt-related database TrEMBL.
**cadd_raw**: The range is from negative to positive values, where negative values mean more benign values while positive values mean more deleterious.
**popeve_pop_adjusted_eve**: This is a log likelihood range in which < -5.056 is likely disease causing and near zero is likely benign.








