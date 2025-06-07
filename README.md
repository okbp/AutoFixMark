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
git clone https://github.com/h-mori/#TODO tool name.git
cd #TODO tool name#
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
| `definitions.json`                | Path to the **JSON** file defining pathway‐to‐enzyme rules. Specifies which KO IDs are required for each pathway. |
| `input_data.(tsv)`                | Path to the input file: either a TSV (one KO ID per line).      |
| `output_results.tsv`              | Path to the output TSV file. Each line will be formatted as `pathway_name<TAB>Y/N`.    |

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
## Paper
Will be soon..


## License
MIT License
