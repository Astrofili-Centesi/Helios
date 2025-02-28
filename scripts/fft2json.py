#!/usr/bin/env python3
import csv
import cbor2
import argparse
from datetime import datetime, timedelta

TIMESTAMP_KEY = 'timestamp'

def parse_timestamp(ts_str):
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        raise ValueError(f"Unable to parse timestamp: {ts_str}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert fft.csv to a compact CBOR file for the last 24 hours using header separation."
    )
    parser.add_argument("-i", "--input", default="fft.csv",
                        help="Input CSV file (default: fft.csv)")
    parser.add_argument("-o", "--output", default="fft.cbor",
                        help="Output CBOR file (default: fft.cbor)")
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
                print(e)
                continue
            for key in row:
                if key != TIMESTAMP_KEY:
                    try:
                        row[key] = float(row[key])
                    except ValueError:
                        row[key] = None
            row['_dt'] = ts
            rows.append(row)

    if not rows:
        print("No data loaded.")
        return

    # Sort rows by timestamp.
    rows.sort(key=lambda r: r['_dt'])
    max_time = rows[-1]['_dt']
    one_day_ago = max_time - timedelta(hours=24)
    filtered = [row for row in rows if row['_dt'] >= one_day_ago]
    for row in filtered:
        del row['_dt']
    if args.step > 1:
        filtered = filtered[::args.step]

    # Build a compact structure that separates header from row data.
    header = [key for key in filtered[0] if key != TIMESTAMP_KEY]
    compact_rows = []
    for row in filtered:
        compact_rows.append({
            "timestamp": row[TIMESTAMP_KEY],
            "levels": [row[f] for f in header]
        })

    output_data = {
        "header": header,
        "rows": compact_rows
    }

    with open(args.output, 'wb') as outfile:
        cbor2.dump(output_data, outfile)
    print(f"Output written to {args.output} ({len(compact_rows)} rows)")

if __name__ == '__main__':
    main()
