import os
import pandas as pd
from datetime import datetime, timedelta
import shutil
import logging

# Configuration
NEW_CSV_PATH = "../fftnew.csv"       # Path to the new FFT data
MAIN_CSV_PATH = "fft.csv"            # Path to the main FFT data
ARCHIVE_DIR = "fft"                  # Base directory for archives
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"    # Adjust based on your timestamp format

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ensure archive directory exists
def ensure_archive_dir(date):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    path = os.path.join(ARCHIVE_DIR, year, month)
    os.makedirs(path, exist_ok=True)
    return path

# Compress and move a dataframe to archive
def archive_day(df, date):
    archive_path = ensure_archive_dir(date)
    filename = date.strftime("%Y-%m-%d.csv.xz")
    file_path = os.path.join(archive_path, filename)
    try:
        # Save to compressed xz format
        df.to_csv(file_path, index=False, compression='xz')
        logging.info(f"Archived data for {date.strftime('%Y-%m-%d')} to {file_path}")
    except Exception as e:
        logging.error(f"Failed to archive data for {date.strftime('%Y-%m-%d')}: {e}")

# Main processing function
def process_fft():
    try:
        # Check if MAIN_CSV_PATH exists; if not, create it with header and initial data
        if not os.path.exists(MAIN_CSV_PATH):
            logging.info(f"{MAIN_CSV_PATH} does not exist. Creating a new file with header and initial data.")
            shutil.copyfile(NEW_CSV_PATH, MAIN_CSV_PATH)
            return

        # Read new data from NEW_CSV_PATH
        new_df = pd.read_csv(NEW_CSV_PATH)

        # Check if there is at least one data row (excluding header)
        if len(new_df) < 2:
            logging.info("No new data to append.")
        else:
            # Extract the new data row(s) (excluding header)
            new_data = new_df.iloc[1:]  # Assuming first row is header
            # Append new data to main CSV
            new_data.to_csv(MAIN_CSV_PATH, mode='a', header=False, index=False)
            logging.info("Appended new data to fft.csv")

        # Read the main CSV with parsed timestamps
        try:
            df = pd.read_csv(MAIN_CSV_PATH, parse_dates=[0])
        except Exception as e:
            logging.error(f"Error reading {MAIN_CSV_PATH}: {e}")
            return

        # Rename the first column to 'timestamp' if not already named
        if df.columns[0].lower() != 'timestamp':
            df.rename(columns={df.columns[0]: 'timestamp'}, inplace=True)

        # Ensure all timestamps are properly parsed and timezone-aware
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'], format=TIME_FORMAT, utc=True)
            except Exception as e:
                logging.error(f"Error parsing timestamps: {e}")
                return
        else:
            # If already datetime64[ns, UTC], ensure they are in UTC
            if df['timestamp'].dt.tz is None:
                # If timestamps are naive, localize to UTC
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
                logging.info("Localized naive timestamps to UTC.")
            else:
                # Convert to UTC if they are timezone-aware but not in UTC
                df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')

        # Sort the dataframe by timestamp to ensure correct ordering
        df = df.sort_values(by='timestamp').reset_index(drop=True)

        # Extract date from timestamp
        df['date'] = df['timestamp'].dt.date

        # Determine the latest date in the file as the "current date"
        latest_timestamp = df['timestamp'].max()
        if pd.isna(latest_timestamp):
            logging.error("No valid timestamps found in the data.")
            return

        current_date = latest_timestamp.date()
        archive_before = current_date - timedelta(days=2)  # Dates <= archive_before will be archived

        logging.info(f"Latest timestamp in data: {latest_timestamp}")
        logging.info(f"Current date based on data: {current_date}")
        logging.info(f"Archiving dates on or before: {archive_before}")

        # Identify unique dates to potentially archive
        unique_dates = df['date'].unique()
        dates_to_archive = [d for d in unique_dates if d <= archive_before]

        # Archive each eligible date
        for date in dates_to_archive:
            # Create timezone-aware day_start and day_end in UTC
            day_start = pd.Timestamp(datetime.combine(date, datetime.min.time()), tz='UTC')
            day_end = day_start + pd.Timedelta(days=1)
            day_data = df[(df['timestamp'] >= day_start) & (df['timestamp'] < day_end)]

            if not day_data.empty:
                # Archive the day's data
                archive_day(day_data, day_start)
                # Remove archived data from the dataframe
                df = df[df['timestamp'] >= day_end]
                logging.info(f"Archived and removed data for {date}")
            else:
                logging.warning(f"No data found for {date} to archive.")

        # Sort the remaining data by timestamp
        df_sorted = df.sort_values(by='timestamp').reset_index(drop=True)

        # Drop the auxiliary 'date' column
        df_sorted.drop(columns=['date'], inplace=True)

        # Save the updated data back to MAIN_CSV_PATH
        try:
            df_sorted.to_csv(MAIN_CSV_PATH, index=False)
            logging.info("Updated fft.csv by removing archived data and sorting by timestamp.")
        except Exception as e:
            logging.error(f"Error writing to {MAIN_CSV_PATH}: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    process_fft()
