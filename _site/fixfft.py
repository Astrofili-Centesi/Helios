#!/usr/bin/env python3
import os
import glob
import argparse
import pandas as pd
import numpy as np

def process_file(infile, outfile, normalization=32768.0):
    # Compute the full-scale offset
    offset = 20 * np.log10(normalization)
    
    # Read the CSV with xz compression; treat all columns as strings to preserve data.
    df = pd.read_csv(infile, compression='xz', dtype=str, header=0)
    
    # Process only the middle columns (skip first and last)
    for col in df.columns[1:-1]:
        # Convert to numeric; non-numeric cells become NaN
        numeric = pd.to_numeric(df[col], errors='coerce')
        # For cells that successfully convert, subtract the offset and format to two decimals
        mask = numeric.notna()
        df.loc[mask, col] = numeric[mask].apply(lambda x: f"{(x - offset):.2f}")
        # Cells that fail conversion remain unchanged.
    
    # Write the DataFrame back to CSV with xz compression, preserving header and structure.
    df.to_csv(outfile, index=False, compression="xz")

def main():
    parser = argparse.ArgumentParser(
        description="Recursively convert FFT CSV data to proper dBFS (16-bit normalization) using vectorized pandas operations."
    )
    parser.add_argument("input_folder", help="Path to folder containing .csv.xz files")
    parser.add_argument("output_folder", help="Path to folder for saving converted files")
    args = parser.parse_args()
    
    # Recursively find all .csv.xz files in the input folder.
    files = glob.glob(os.path.join(args.input_folder, '**', '*.csv.xz'), recursive=True)
    if not files:
        print("No .csv.xz files found in", args.input_folder)
        return

    for infile in files:
        # Compute relative path to preserve folder structure in output
        rel_path = os.path.relpath(infile, args.input_folder)
        outfile = os.path.join(args.output_folder, rel_path)
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        print(f"Processing {infile} -> {outfile}")
        process_file(infile, outfile)
    
    print("Conversion complete.")

if __name__ == "__main__":
    main()
