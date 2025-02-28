#!/usr/bin/env python3
import csv
import json
import argparse
from datetime import datetime, timedelta

TIMESTAMP_KEY = 'timestamp'

def parse_timestamp(ts_str):
    # Try to use fromisoformat (available in Python 3.7+)
    try:
        return datetime.fromisoformat(ts_str)
    except AttributeError:
        # Fallback for older Python versions.
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1]  # remove 'Z' if present
        try:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")

def main():
    parser = argparse.ArgumentParser(
        description="Convert fft.csv to a compact JSON file for the last 24 hours."
    )
    parser.add_argument("-i", "--input", default="fft.csv",
                        help="Input CSV file (default: fft.csv)")
    parser.add_argument("-o", "--output", default="fft.json",
                        help="Output JSON file (default: fft.json)")
    parser.add_argument("--step", type=int, default=1,
                        help="Downsampling factor: output every nth row (default: 1)")
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
            for key in row:
                if key != TIMESTAMP_KEY:
                    try:
                        row[key] = float(row[key])
                    except ValueError:
                        row[key] = None
            row['_dt'] = ts  # temporary field for filtering and sorting
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

    # Downsample if requested.
    if args.step > 1:
        filtered = filtered[::args.step]

    # Create a compact JSON structure with a single header and rows.
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
