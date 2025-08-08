#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Hit:
    """Data class representing a single hit information"""
    asterisk: bool
    original_columns: List[str]
    ko: str
    gene_name: str


def parse_tsv_content(content: str) -> Tuple[Optional[str], Dict[str, List[Hit]]]:
    """Parse TSV file content and convert to data structure."""
    gene_data: Dict[str, List[Hit]] = {}
    header_line = None

    for line in content.splitlines():
        line = line.rstrip()

        # Save the first comment line as header if it exists
        if line.startswith('#'):
            if header_line is None:
                header_line = line
            continue

        # Skip empty lines
        if not line:
            continue

        columns = line.split('\t')
        if len(columns) < 7:
            continue

        # Parse columns
        asterisk_mark = columns[0] == '*'
        gene_name = columns[1]
        ko = columns[2]

        # Save hits by gene_name
        if gene_name not in gene_data:
            gene_data[gene_name] = []

        hit = Hit(
            asterisk=asterisk_mark,
            original_columns=columns,
            ko=ko,
            gene_name=gene_name
        )
        gene_data[gene_name].append(hit)
    
    return header_line, gene_data


def determine_selected_indices(hits: List[Hit], top_n: int) -> Set[int]:
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


def format_detail_output(
    gene_data: Dict[str, List[Hit]],
    header_line: Optional[str],
    top_n: int,
    detail_top: int
) -> List[str]:
    """Generate output lines for detail mode."""
    output_lines = []
    
    # Write header
    if header_line:
        # Remove the leading # and split
        header_cols = header_line.lstrip('#').split('\t')
        header_str = '\t'.join(header_cols[1:])
        output_lines.append(f"rank\thit\tasterisk_mark\t{header_str}")
    else:
        # Default header if no header in input file
        output_lines.append("rank\thit\tasterisk_mark\tgene_name\tKO\tthreshold\tscore\te_value\tKO_definition")
    
    # Process each gene_name
    for i, (gene_name, hits) in enumerate(gene_data.items()):
        print(f"Gene {gene_name}: {len(hits)} hits")
        
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
                output_lines.append(f"{original_rank}\t{hit_mark}\t{asterisk_mark}\t{cols_str}")

    return output_lines


def format_ko_output(gene_data: Dict[str, List[Hit]], top_n: int) -> List[str]:
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


def read_tsv_file(file_path: str) -> str:
    """Read file and return its content as string."""
    with open(file_path, 'r') as file:
        return file.read()


def write_output_file(file_path: str, lines: List[str]) -> None:
    """Write list of lines to file."""
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(line + '\n')


def process_tsv_file(
    input_file: str, 
    output_file: str, 
    top_n: int = 10,
    detail_mode: bool = False, 
    detail_top: int = 10
) -> None:
    """Process a single TSV file and extract top N hits per gene."""
    # Read file
    content = read_tsv_file(input_file)
    
    # Parse content
    header_line, gene_data = parse_tsv_content(content)
    
    # Format output
    if detail_mode:
        output_lines = format_detail_output(gene_data, header_line, top_n, detail_top)
    else:
        output_lines = format_ko_output(gene_data, top_n)
    
    # Write output
    write_output_file(output_file, output_lines)
    
    print(f"Output written to: {output_file}")


def main():
    """Main function to process a single TSV file."""
    parser = argparse.ArgumentParser(
        description='Process KOfam TSV files and extract top hits per gene.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_file', 
                        help='Path to the input TSV file')
    parser.add_argument('output_file', 
                        help='Path to the output TSV file')
    parser.add_argument('--top', 
                        type=int, 
                        default=1,
                        help='Number of top hits to select for KO extraction (default: 1)')
    parser.add_argument('--detail', 
                        action='store_true',
                        help='Output detailed information with headers (default: output unique KO values only)')
    parser.add_argument('--detail-top', 
                        type=int, 
                        default=10,
                        help='Number of top hits to display in detail mode (default: 10)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Process the TSV file
    process_tsv_file(args.input_file, args.output_file, args.top, args.detail, args.detail_top)
    
    print("Processing completed!")
    print(f"Output file: {args.output_file}")


if __name__ == "__main__":
    main()