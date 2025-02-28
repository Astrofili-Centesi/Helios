#!/usr/bin/env python3
import csv
import json
import argparse
from datetime import datetime, timedelta

TIMESTAMP_KEY = 'timestamp'

def parse_timestamp(ts_str):
    # Assumes ISO format; adjust if necessary.
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        raise ValueError(f"Unable to parse timestamp: {ts_str}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert fft.csv to a JSON file containing only the last 24 hours of data.")
    parser.add_argument("-i", "--input", default="fft.csv",
                        help="Input CSV file (default: fft.csv)")
    parser.add_argument("-o", "--output", default="fft.json",
                        help="Output JSON file (default: fft.json)")
    args = parser.parse_args()

    rows = []
    with open(args.input, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert the timestamp and all FFT values.
            try:
                ts = parse_timestamp(row[TIMESTAMP_KEY])
            except Exception as e:
                print(e)
                continue
            # Convert all keys (except timestamp) to float.
            for key in row:
                if key != TIMESTAMP_KEY:
                    try:
                        row[key] = float(row[key])
                    except ValueError:
                        row[key] = None
            # Add parsed datetime for sorting (will not be saved).
            row['_dt'] = ts
            rows.append(row)

    if not rows:
        print("No data loaded.")
        return

    # Sort rows by timestamp.
    rows.sort(key=lambda r: r['_dt'])
    max_time = rows[-1]['_dt']
    one_day_ago = max_time - timedelta(hours=24)

    # Filter rows to only those within the last 24 hours.
    filtered_rows = [{k: v for k, v in row.items() if k != '_dt'}
                     for row in rows if row['_dt'] >= one_day_ago]

    # Write the filtered data to a JSON file.
    with open(args.output, 'w') as jsonfile:
        json.dump(filtered_rows, jsonfile, indent=2)
    print(f"Output written to {args.output} ({len(filtered_rows)} rows)")

if __name__ == '__main__':
    main()
