#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass
class Row:
    """Data class representing a hit row information"""
    asterisk: bool
    original_columns: List[str]
    ko: str
    gene: str


def group_by_genes(result: str):
    """Parse TSV file content and convert to data structure."""
    gene_data: Dict[str, List[Row]] = {}

    for line in result.splitlines():
        line = line.rstrip()

        # Save the first comment line as header if it exists
        if line.startswith('#'):
            continue

        # Skip empty lines
        if not line:
            continue

        columns = line.split('\t')
        if len(columns) < 7:
            continue

        # Parse columns
        asterisk_mark = columns[0] == '*'
        gene = columns[1]
        ko = columns[2]

        # Save hits by gene
        if gene not in gene_data:
            gene_data[gene] = []

        hit = Row(
            asterisk=asterisk_mark,
            original_columns=columns,
            ko=ko,
            gene=gene
        )
        gene_data[gene].append(hit)
    
    return gene_data


def determine_selected_indices(hits: List[Row], top_n: int):
    """
    Determine which hit indices should be selected for KO output.
    Returns set of indices that should be selected.
    """
    selected_indices = set()
    has_asterisk = any(hit.asterisk for hit in hits)
    
    for index, hit in enumerate(hits):
        # Mark as selected if: has asterisk OR (no asterisk in gene and within top_n)
        if hit.asterisk or (not has_asterisk and index < top_n):
            selected_indices.add(index)
    
    return selected_indices


def format_detail_output(gene_data: Dict[str, List[Row]], top_n: int, detail_top: int):
    """
    Generate output lines for detail mode.
    Output the Top N results specified by the detail_top argument, and mark selected KO numbers with 'Y' in the hit column.
    """
    output_lines = []
    
    # Write header
    output_lines.append("hit\trank\tasterisk_mark\tgene\tKO\tthreshold\tscore\te_value\tKO_definition")
    
    # Process each gene
    for i, (gene, hits) in enumerate(gene_data.items()):

        # Add separator line between genes (except before the first gene)
        if i > 0:
            output_lines.append('-' * 100)

        # Use common function to determine which rows would be selected
        selected_indices = determine_selected_indices(hits, top_n)

        # Output hits up to detail_top
        for index, hit in enumerate(hits):
            if index < detail_top or hit.asterisk:
                original_rank = index + 1
                # Mark with 'Y' if this row would be selected for KO output
                hit_mark = 'Y' if index in selected_indices else ''
                asterisk_mark = '*' if hit.asterisk else ''
                
                # Output: rank, hit mark, asterisk_mark, then all original columns except the first one
                cols_str = '\t'.join(hit.original_columns[1:])
                output_lines.append(f"{hit_mark}\t{original_rank}\t{asterisk_mark}\t{cols_str}")

    return output_lines


def format_ko_output(gene_data: Dict[str, List[Row]], top_n: int):
    """Generate output lines for KO-only mode."""
    unique_kos: Set[str] = set()

    # Process each gene
    for gene_name, hits in gene_data.items():
        # Use common function to determine which rows to select
        selected_indices = determine_selected_indices(hits, top_n)

        # Add KOs from selected indices
        for index in selected_indices:
            if index < len(hits):
                unique_kos.add(hits[index].ko)

    # Return sorted unique KOs
    return sorted(unique_kos)


def load_tsv(file_path: str):
    """Read a TSV file and return its content as string."""
    with open(file_path, 'r') as file:
        return file.read()


def parse_kofamscan_result_file(input_file: str, output_file: str, top_n: int = 10, detail_mode: bool = False, detail_top: int = 10):
    """Parse the KofamScan result file and output a list of selected KO numbers"""
    # Load input KofamScan result file
    kofamscan_results = load_tsv(input_file)
    
    # Parse KofamScan results and group by genes
    gene_data = group_by_genes(kofamscan_results)

    if detail_mode: # Detail mode: To check the selected row
        output_lines = format_detail_output(gene_data, top_n, detail_top)
    else: # Nomal mode: output only KO numbers
        output_lines = format_ko_output(gene_data, top_n)
    
    # Write results to the output file in TSV format
    with open(output_file, 'w', encoding='utf-8') as out:
        if output_lines:
            out.write('\n'.join(output_lines))


def main():
    """Main function to process a Kofamscan result file."""
    parser = argparse.ArgumentParser(
        description='Process Kofamscan result TSV files and extract hits KO numbers.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_file', 
                        help='Path to the input TSV file')
    parser.add_argument('output_file', 
                        help='Path to the output TSV file')
    parser.add_argument('--top', 
                        type=int, 
                        default=1,
                        help='Number of top hits to select for KO extraction (default: 1, selected only if no line is marked with an asterisk)')
    parser.add_argument('--detail', 
                        action='store_true',
                        help='Output detailed information with headers, and mark selected KO numbers with "Y" in the hit column (default: output unique KO numbers only)')
    parser.add_argument('--detail-top', 
                        type=int, 
                        default=10,
                        help='Number of top hits to display in detail mode (default: 10)')
    
    args = parser.parse_args()
    
    # Check that input TSV exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist")
        sys.exit(1)
    
    # Check that output directory exists and is writable
    out_dir = os.path.dirname(args.output_file) or '.'
    if not os.path.isdir(out_dir):
        print(f"Error: Output directory '{out_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not os.access(out_dir, os.W_OK):
        print(f"Error: No write permission in output directory '{out_dir}'.", file=sys.stderr)
        sys.exit(1)
    
    # Parse the KofamScan result file and output a list of selected KO numbers
    parse_kofamscan_result_file(args.input_file, args.output_file, args.top, args.detail, args.detail_top)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ./kofamscan_parser.py ./example/kofamscan_result.tsv ./example/ko_list.tsv", file=sys.stderr)
        sys.exit(1)
    main()