#!/usr/bin/env python3
import csv
import json
import argparse
from datetime import datetime, timedelta

TIMESTAMP_KEY = 'timestamp'

def parse_timestamp(ts_str):
    """
    Parse a timestamp in the format "2025-02-27 00:00:01+00:00".
    First try using datetime.fromisoformat (Python 3.7+). If that fails,
    remove the colon in the timezone and use strptime.
    """
    try:
        return datetime.fromisoformat(ts_str)
    except (AttributeError, ValueError):
        if ts_str[-3] == ':':
            ts_str = ts_str[:-3] + ts_str[-2:]
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S%z")

def get_peak(row):
    """
    Return the maximum FFT value in the row, ignoring the timestamp.
    Only consider numeric values that are not None.
    """
    values = [v for k, v in row.items() if k != TIMESTAMP_KEY and v is not None]
    return max(values) if values else -float('inf')

def downsample_preserving_peaks(rows, block_size):
    """
    For each block of 'block_size' consecutive rows,
    select the row that contains the highest peak (based on get_peak).
    """
    downsampled = []
    for i in range(0, len(rows), block_size):
        block = rows[i:i+block_size]
        if block:
            best_row = max(block, key=get_peak)
            downsampled.append(best_row)
    return downsampled

def main():
    parser = argparse.ArgumentParser(
        description="Convert fft.csv to a compact JSON file for the last 24 hours with peak-preserving downsampling."
    )
    parser.add_argument("-i", "--input", default="fft.csv",
                        help="Input CSV file (default: fft.csv)")
    parser.add_argument("-o", "--output", default="fft.json",
                        help="Output JSON file (default: fft.json)")
    parser.add_argument("--step", type=int, default=4,
                        help=("Downsampling factor: group rows in blocks of this size and select the row with the highest peak "
                              "(default: 4)"))
    args = parser.parse_args()

    rows = []
    with open(args.input, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                ts = parse_timestamp(row[TIMESTAMP_KEY])
            except Exception as e:
                print(f"Error parsing timestamp: {e}")
                continue
            # Convert FFT bin values to float.
            for key in row:
                if key != TIMESTAMP_KEY:
                    try:
                        row[key] = float(row[key])
                    except ValueError:
                        row[key] = None
            row['_dt'] = ts  # temporary field for sorting and filtering
            rows.append(row)

    if not rows:
        print("No data loaded.")
        return

    # Sort rows by timestamp.
    rows.sort(key=lambda r: r['_dt'])
    max_time = rows[-1]['_dt']
    one_day_ago = max_time - timedelta(hours=24)

    # Filter rows for the last 24 hours.
    filtered = [row for row in rows if row['_dt'] >= one_day_ago]
    for row in filtered:
        del row['_dt']

    # Downsample using peak-preserving method if requested.
    if args.step > 1:
        filtered = downsample_preserving_peaks(filtered, args.step)

    # Create a compact JSON structure with a one-time header and rows.
    header = [key for key in filtered[0] if key != TIMESTAMP_KEY]
    compact_rows = []
    for row in filtered:
        compact_rows.append({
            "timestamp": row[TIMESTAMP_KEY],
            "levels": [row[f] for f in header]
        })

    output = {
        "header": header,
        "rows": compact_rows
    }

    with open(args.output, 'w') as jsonfile:
        json.dump(output, jsonfile, indent=2)
    print(f"Output written to {args.output} ({len(compact_rows)} rows)")

if __name__ == '__main__':
    main()
