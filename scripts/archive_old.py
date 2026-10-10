# process_db.py

import pandas as pd
import os
from datetime import datetime, timedelta
import argparse
import logging
import sys

def setup_logging():
    """Set up logging configuration."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler('/tmp/process_db.log')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters
    c_format = logging.Formatter('%(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Add formatters to handlers
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

def main():
    logger = setup_logging()
    logger.info('Starting the processing of db.csv')

    try:
        parser = argparse.ArgumentParser(description='Process db.csv and archive old data.')
        parser.add_argument('--max_time', type=str, required=True, help='Max time delta, e.g., "7 days"')
        args = parser.parse_args()

        # Parse max_time
        max_time_parts = args.max_time.strip().split()
        if len(max_time_parts) != 2 or max_time_parts[1] != 'days':
            logger.error('Invalid format for max_time. It should be in the format "N days".')
            raise ValueError('max_time should be in the format "N days"')
        max_time_days = int(max_time_parts[0])
        max_time_delta = timedelta(days=max_time_days)
        logger.debug(f'Parsed max_time: {max_time_days} days')

        # Read freq.csv to create a mapping from channel names to frequencies
        logger.info('Reading freq.csv to get frequency mappings')
        freq_df = pd.read_csv('freq.csv')
        freq_mapping = dict(zip(freq_df['Canale'], freq_df['Freq'].astype(str)))
        logger.debug(f'Frequency mapping: {freq_mapping}')

        # Read db.csv without parsing dates to preserve date format
        logger.info('Reading db.csv')
        df = pd.read_csv('db.csv', dtype=str)
        logger.debug(f'Read {len(df)} rows from db.csv')

        if df.empty:
            logger.warning('db.csv is empty. Exiting the script.')
            return

        # Parse 'data' column into datetime for processing, but keep original strings
        df['data_parsed'] = pd.to_datetime(df['data'], utc=True)
        logger.info('Parsed dates for processing')

        # Remove duplicates based on 'data' column
        df = df.drop_duplicates(subset='data')
        logger.info(f'Dropped duplicates, {len(df)} unique records remain')

        # Get latest date
        latest_date = df['data_parsed'].max()
        logger.info(f'Latest date in db.csv: {latest_date}')

        # Calculate cutoff date
        date_minus_max_time = latest_date - max_time_delta
        cutoff_date = date_minus_max_time.replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info(f'Cutoff date calculated (midnight of the day): {cutoff_date}')

        # Separate data before cutoff_date
        old_data = df[df['data_parsed'] < cutoff_date]
        new_data = df[df['data_parsed'] >= cutoff_date]
        logger.debug(f'Found {len(old_data)} old records to archive')
        logger.debug(f'{len(new_data)} records will remain in db.csv')

        # Ensure new_data is sorted by 'data_parsed'
        new_data = new_data.sort_values(by='data_parsed')
        logger.info('Sorted new_data by date')

        # Drop 'data_parsed' before writing back to db.csv
        new_data = new_data.drop(columns=['data_parsed'])

        # Write new_data back to db.csv with original headers and date format
        new_data.to_csv('db.csv', index=False)
        logger.info('Updated db.csv with recent data')

        # Process old_data for archiving
        if not old_data.empty:
            # Rename columns in old_data using frequency mapping
            old_data.rename(columns=freq_mapping, inplace=True)
            logger.info('Renamed columns in old_data using frequency mappings')
            logger.debug(f'Columns after renaming: {old_data.columns.tolist()}')

            old_data['date_only'] = pd.to_datetime(old_data['data_parsed']).dt.date

            for date, group in old_data.groupby('date_only'):
                year = date.year
                month = '{:02d}'.format(date.month)
                dir_path = os.path.join('archive', str(year), month)
                os.makedirs(dir_path, exist_ok=True)
                file_path = os.path.join(dir_path, f'{date}.csv')

                # Sort the group by 'data_parsed' column
                group_sorted = group.sort_values(by='data_parsed').drop(columns=['date_only'])

                if os.path.exists(file_path):
                    # Read existing data
                    existing_data = pd.read_csv(file_path, dtype=str)

                    existing_data['data_parsed'] = pd.to_datetime(existing_data['data'], utc=True)

                    # Sort existing data by 'data_parsed' column

                    # Combine with current group
                    combined_data = pd.concat([existing_data, group_sorted])

                    # Remove duplicates based on 'data' column
                    combined_data = combined_data.drop_duplicates(subset='data_parsed')
                    logger.debug(f'After dropping duplicates, {len(combined_data)} records in {file_path}')

                    # Sort combined data by 'data' column (dates as strings)
                    combined_data = combined_data.sort_values(by='data_parsed')
                    combined_data['data']=combined_data['data_parsed']
                    combined_data = combined_data.drop(columns=['data_parsed'])

                    # Write back to archive file
                    combined_data.to_csv(file_path, index=False)
                    logger.info(f'Updated archive file {file_path}')
                else:
                    # Write new archive file
                    group_sorted.to_csv(file_path, index=False)
                    logger.info(f'Created new archive file {file_path}')
        else:
            logger.info('No old data to archive')

    except Exception as e:
        logger.exception('An error occurred during processing')
        sys.exit(1)

    logger.info('Processing completed successfully')

if __name__ == '__main__':
    main()
