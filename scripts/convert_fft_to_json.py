import pandas as pd
import json
from datetime import datetime, timedelta, timezone
import argparse

def convert_fft_csv_to_json(csv_file, json_file, hours=12):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Parse the 'timestamp' column as datetime with timezone
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Get current UTC time
    current_time = datetime.now(timezone.utc)

    # Calculate the cutoff time
    cutoff_time = current_time - timedelta(hours=hours)

    # Filter rows within the last 'hours' hours
    filtered_df = df[df['timestamp'] >= cutoff_time]

    # If there are no rows after filtering, warn the user
    if filtered_df.empty:
        print(f"No data found in the last {hours} hours.")
        return

    # Extract frequency bins from the header (excluding 'timestamp')
    frequency_bins = [float(col) for col in filtered_df.columns if col != 'timestamp']

    # Prepare the JSON structure
    json_data = {
        "frequencies": frequency_bins,
        "data": []
    }

    for _, row in filtered_df.iterrows():
        entry = {
            "timestamp": row['timestamp'].isoformat(),
            "magnitudes": [row[f"{freq:.2f}"] for freq in frequency_bins]  # Updated line
        }
        json_data["data"].append(entry)

    # Write to JSON file
    with open(json_file, 'w') as f:
        json.dump(json_data, f)

    print(f"Successfully converted to {json_file} with {len(json_data['data'])} entries.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert FFT CSV to JSON (Latest 12 Hours)")
    parser.add_argument('--csv', type=str, default='fft.csv', help='Path to the input CSV file')
    parser.add_argument('--json', type=str, default='fft.json', help='Path to the output JSON file')
    parser.add_argument('--hours', type=int, default=12, help='Number of past hours to include')

    args = parser.parse_args()

    convert_fft_csv_to_json(args.csv, args.json, args.hours)
