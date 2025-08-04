#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from typing import Dict, List, Any, Set, Tuple


def determine_selected_indices(hits: List[Dict[str, Any]], top_n: int) -> Set[int]:
    """
    Determine which hit indices should be selected for KO output.
    Returns set of indices that should be selected.
    """
    selected_indices = set()
    has_asterisk = any(hit['asterisk'] for hit in hits)
    
    for index, hit in enumerate(hits):
        # Mark as selected if: has asterisk OR (no asterisk in gene and within top_n)
        if hit['asterisk'] or (not has_asterisk and index < top_n):
            selected_indices.add(index)
    
    return selected_indices


def process_tsv_file(input_file: str, output_file: str, top_n: int = 10, detail_mode: bool = False, detail_top: int = 10) -> None:
    """
    Process a single TSV file and extract top N hits per gene.
    """
    
    # Group hits by gene_name
    gene_data: Dict[str, List[Dict[str, Any]]] = {}
    header_line = None
    
    with open(input_file, 'r') as file:
        for line_num, line in enumerate(file):
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
            
            gene_data[gene_name].append({
                'asterisk': asterisk_mark,
                'original_columns': columns,
                'ko': ko
            })
    
    # Write output based on mode
    with open(output_file, 'w') as output:
        if detail_mode:
            # Detail mode: output with full information
            
            # Write header
            if header_line:
                # Remove the leading # and split
                header_cols = header_line.lstrip('#').split('\t')
                header_str = '\t'.join(header_cols[1:])
                output.write(f"rank\tselected\tasterisk_mark\t{header_str}\n")
            else:
                # Default header if no header in input file
                output.write("rank\tselected\tasterisk_mark\tgene_name\tKO\tthreshold\tscore\te_value\tKO_definition\n")
            
            # Process each gene_name
            for i, (gene_name, hits) in enumerate(gene_data.items()):

                # Add separator line between genes (except before the first gene)
                if i > 0:
                    output.write('-' * 100 + '\n')
                
                # Use common function to determine which rows would be selected
                selected_indices = determine_selected_indices(hits, top_n)
                
                # Output hits up to detail_top
                for index, hit in enumerate(hits):
                    if index < detail_top or hit['asterisk']:
                        original_rank = index + 1
                        # Mark with 'Y' if this row would be selected for KO output
                        hit_mark = 'Y' if index in selected_indices else ''
                        asterisk_mark = '*' if hit['asterisk'] else ''
                        original_cols = hit['original_columns']
                        
                        # Output: rank, hit mark, asterisk_mark, then all original columns except the first one
                        cols_str = '\t'.join(original_cols[1:])
                        output.write(f"{original_rank}\t{hit_mark}\t{asterisk_mark}\t{cols_str}\n")
        
        else:
            # Non-detail mode: output unique KO values
            unique_kos: Set[str] = set()
            
            # Process each gene
            for gene_name, hits in gene_data.items():
                # Use common function to determine which rows to select
                selected_indices = determine_selected_indices(hits, top_n)
                
                # Add KOs from selected indices
                for index in selected_indices:
                    if index < len(hits):
                        unique_kos.add(hits[index]['ko'])
            
            # Output unique KOs
            for ko in sorted(unique_kos):
                output.write(f"{ko}\n")
    
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