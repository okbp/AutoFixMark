# AutoFixMark
AutoFixMark is a lightweight, cross-platform CLI tool that predicts the seven autotrophic natural CO₂ fixation pathways (CBB, rTCA, WL, 3HP, 3HP/4HB, DC/4HB, and rGly) from a list of KEGG Orthology (KO) IDs and outputs the results in TSV format.

## Overview

Given a JSON file of pathway‐definition rules and an input TSV of KO IDs, this tool outputs a TSV indicating **Y** (yes) or **N** (no) for each pathway.

- **Definitions**: JSON file defining key enzymes for each pathway  
- **Input**: TSV file, one KO ID per line  
- **Output**: TSV file, two columns (`pathway_name<TAB>Y/N`)

## Prerequisites

- **Python 3.6+**


## Installation

1. Clone this repository (or download the script):
```bash
git clone https://github.com/h-mori/AutoFixMark.git
cd AutoFixMark
```

## Usage
### macOS / Linux
```
python3 ./app/predict_pathways.py \
  ./definitions/kegg_key_enzymes.json \
  ./example/ko_list.tsv \
  ./example/result.tsv
```
It will run on Windows as long as Python is installed; please adapt the commands as needed.


### Arguments

| Argument                              | Description                                                                                                 |
|-----------------------------------|------------------------------------------------------------------------------------------------------|
| `definitions/kegg_key_enzymes.json`                | Path to the **JSON** file defining the reference pathway‐to‐enzyme rules. Specifies which KO IDs are required for each pathway. |
| `ko_list.tsv`                | Path to the **input TSV file**: one KO ID per line.      |
| `result.tsv`              | Path to the **output TSV file**. Each line will be formatted as `pathway_name<TAB>Y/N`.    |

## Example
### Input (`example/ko_list.tsv`):
```
K00855
K01601
```

### Run:
```
python3 ./app/predict_pathways.py \
  ./definitions/kegg_key_enzymes.json \
  ./example/ko_list.tsv \
  ./example/result.tsv
```
### Output (`example/result.tsv`):
```
CBB     Y
rTCA    N
WL      N
3HP     N
3HP/4HB N
DC/4HB  N
rGly    N
```

## Appendix: How to generate a list of KO IDs for a genome:
1. Perform gene prediction using tools such as DFAST, Prokka, or Prodigal to identify protein-coding genes.
2. Assign KO IDs to the predicted protein sequences using tools such as KofamScan, GhostKOALA, or KofamKOALA.
3. Format the KO ID list as a TSV file, with one KO ID per line.

### Extract KO ID list from KofamScan result file:
```
python3 ./app/kofamscan_parser.py \
  ./example/kofam_result.tsv \
  ./example/ko_list.tsv
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `input_file` | Path to the KofamScan result **TSV file** (required). |
| `output_file` | Path to the **output TSV file** (required). |
| `--top N` | Number of top hits to select for KO extraction when no asterisk is present (default: 1). |
| `--min-score-ratio R` | Minimum score/threshold ratio (0 < R < 1) for selecting hits without asterisk. If not specified, no ratio filtering is applied. |
| `--gene` | Output KO numbers with gene details including threshold, score, E-value, and asterisk. |
| `--detail` | Output detailed information with headers. Selected KO numbers are marked with "Y" in the hit column. |
| `--detail-top N` | Number of top hits to display in detail mode (default: 10). |

In the KofamScan results, an asterisk is assigned to KOs whose score exceeds the threshold (see: https://academic.oup.com/bioinformatics/article/36/7/2251/5631907). However, in some cases, better annotation results can be obtained by including hits without the asterisk.         
                                                                                                                                                                                                                                                                               
For genes without the asterisk, you can filter assignments based on the score/threshold ratio. In the example below, the top hit is selected for genes without an asterisk `--top 1`, but assignments with a ratio below 10% `--min-score-ratio 0.1` are excluded as low-quality. The `--detail` mode outputs selected KOs in a human-readable format for manual inspection. 

```
python3 ./app/kofamscan_parser.py \
  ./example/kofam_result_wo_asterisk.tsv \
  ./example/ko_list_qc_0.1.detail.tsv \
  --top 1 \
  --min-score-ratio 0.1 \
  --detail
```
## Paper
Will be soon.

## License
MIT License

## Contact
- Hiroshi Mori (National Institute of Genetics, Japan): hmori[@]nig.ac.jp   (please change [@] to @).
