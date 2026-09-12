#!/usr/bin/env python3
import csv
import msgpack
import argparse
from datetime import datetime, timedelta

TIMESTAMP_KEY = 'timestamp'
LEVEL_SCALE = 100  # Multiply dB values by 100 (fixed-point conversion)

def parse_timestamp(ts_str):
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        if ts_str[-3] == ':':
            ts_str = ts_str[:-3] + ts_str[-2:]
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S%z")

def main():
    parser = argparse.ArgumentParser(
        description="Convert fft.csv to an optimized MessagePack file using a flat array structure (header + data)."
    )
    parser.add_argument("-i", "--input", default="fft.csv",
                        help="Input CSV file (default: fft.csv)")
    parser.add_argument("-o", "--output", default="fft.msgpack",
                        help="Output MessagePack file (default: fft.msgpack)")
    parser.add_argument("--step", type=int, default=1,
                        help="Downsampling factor: output every nth row (default: 1)")
    args = parser.parse_args()

    rows = []
    with open(args.input, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                ts = parse_timestamp(row[TIMESTAMP_KEY])
                row[TIMESTAMP_KEY] = ts  # overwrite with datetime object
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
            rows.append(row)

    if not rows:
        print("No data loaded.")
        return

    # Sort rows by timestamp.
    rows.sort(key=lambda r: r[TIMESTAMP_KEY])
    max_time = rows[-1][TIMESTAMP_KEY]
    one_day_ago = max_time - timedelta(hours=24)
    filtered = [row for row in rows if row[TIMESTAMP_KEY] >= one_day_ago]
    if args.step > 1:
        filtered = filtered[::args.step]

    # Build header from CSV column names (excluding the timestamp).
    raw_header = [key for key in filtered[0] if key != TIMESTAMP_KEY]
    # Convert header keys to integers (e.g. "4500.00" -> 4500)
    header = []
    for h in raw_header:
        try:
            header.append(int(round(float(h))))
        except ValueError:
            header.append(h)
    
    # Build data: each row is [timestamp, level0, level1, ...]
    data = []
    for row in filtered:
        ts_epoch = int(row[TIMESTAMP_KEY].timestamp())
        levels = []
        for key in raw_header:
            val = row.get(key)
            if val is None:
                levels.append(0)
            else:
                levels.append(int(round(val * LEVEL_SCALE)))
        data.append([ts_epoch] + levels)

    output_data = {"header": header, "data": data}
    with open(args.output, 'wb') as outfile:
        packed = msgpack.packb(output_data, use_bin_type=True)
        outfile.write(packed)

    print(f"Output written to {args.output} ({len(data)} rows)")

if __name__ == '__main__':
    main()
