# archive_old.py

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

        # Read db.csv
        logger.info('Reading db.csv')
        df = pd.read_csv('db.csv', parse_dates=['data'])
        logger.debug(f'Read {len(df)} rows from db.csv')

        if df.empty:
            logger.warning('db.csv is empty. Exiting the script.')
            return

        # Get latest date
        latest_date = df['data'].max()
        logger.info(f'Latest date in db.csv: {latest_date}')

        # Calculate cutoff date
        cutoff_date = latest_date - max_time_delta
        logger.info(f'Cutoff date calculated: {cutoff_date}')

        # Separate data before cutoff_date
        old_data = df[df['data'] < cutoff_date]
        new_data = df[df['data'] >= cutoff_date]
        logger.debug(f'Found {len(old_data)} old records to archive')
        logger.debug(f'{len(new_data)} records will remain in db.csv')

        # Group old_data by date
        if not old_data.empty:
            old_data['date_only'] = old_data['data'].dt.date
            for date, group in old_data.groupby('date_only'):
                year = date.year
                month = '{:02d}'.format(date.month)
                dir_path = os.path.join('archive', str(year), month)
                os.makedirs(dir_path, exist_ok=True)
                file_path = os.path.join(dir_path, f'{date}.csv')
                if os.path.exists(file_path):
                    # Append to existing file
                    group.drop(columns=['date_only']).to_csv(file_path, mode='a', index=False, header=False)
                    logger.info(f'Appended data to {file_path}')
                else:
                    # Write new file
                    group.drop(columns=['date_only']).to_csv(file_path, index=False)
                    logger.info(f'Created new archive file {file_path}')
        else:
            logger.info('No old data to archive')

        # Write new_data back to db.csv
        new_data.to_csv('db.csv', index=False)
        logger.info('Updated db.csv with recent data')

    except Exception as e:
        logger.exception('An error occurred during processing')
        sys.exit(1)

    logger.info('Processing completed successfully')

if __name__ == '__main__':
    main()
