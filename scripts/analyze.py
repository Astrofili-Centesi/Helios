import pandas as pd
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

def safe_to_json(df, path_or_buf, **kwargs):
    """
    Write DataFrame to JSON after dropping duplicated index rows to ensure the index is unique.
    """
    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep='first')]
    df.to_json(path_or_buf, **kwargs)

def main():
    # Check command-line arguments
    if len(sys.argv) < 7:
        logging.error("Usage: script.py <src> <f_d24> <f_dday> <f_dmean5> <f_dlast5> <f_dlastmonth>")
        sys.exit(1)

    # File paths from command-line arguments
    src = sys.argv[1]
    f_d24 = sys.argv[2]
    f_dday = sys.argv[3]
    f_dmean5 = sys.argv[4]
    f_dlast5 = sys.argv[5]
    f_dlastmonth = sys.argv[6]

    # Read input data and frequency mapping
    df = pd.read_csv(src)
    freq = pd.read_csv('freq.csv')
    freq.index = freq['Canale']

    # Convert 'data' column to datetime and set it as the index, dropping the original column
    df['data'] = pd.to_datetime(df['data'])
    df.set_index('data', inplace=True)

    # Rename columns based on the mapping from freq.csv
    rename_mapping = dict(zip(freq['Canale'], freq['Sigla']))
    df.rename(columns=rename_mapping, inplace=True)

    # --- Save the last 24 hours of data ---
    last_time = df.index[-1]
    df_last24 = df.loc[df.index >= (last_time - pd.Timedelta(hours=24))]
    safe_to_json(df_last24, f_d24)

    # --- Process yesterday’s full day ---
    last_day = last_time - pd.Timedelta(days=1)
    logging.info(f"lastTime {last_time} lastDay {last_day}")

    yesterday_from = last_day.floor('D')
    yesterday_to = last_day.ceil('D')
    logging.info(f"yesterdayFrom {yesterday_from} yesterdayTo {yesterday_to}")

    df_yesterday = df[(df.index >= yesterday_from) & (df.index < yesterday_to)]
    df_yesterday = df_yesterday.resample('60s').mean().ffill()
    safe_to_json(df_yesterday, f_dday)

    # --- Save data for the last month ---
    last_month_from = last_time - pd.DateOffset(months=2)
    df_last_month = df[df.index >= last_month_from]
    logging.info(f"last month from {df_last_month.index[0]} to {df_last_month.index[-1]}")
    safe_to_json(df_last_month, f_dlastmonth)

    # --- Process the last 5 days for averaging ---
    df_resampled = df.resample('60s').mean()
    meanday_from = (last_day - pd.Timedelta(days=5)).floor('D')
    meanday_to = last_day.floor('D')
    logging.info(f"meandayFrom {meanday_from} meandayTo {meanday_to}")

    df_last5 = df_resampled[(df_resampled.index >= meanday_from) & (df_resampled.index < meanday_to)].ffill()

    # Compute the mean grouped by hour and minute
    df_mean = df_last5.groupby([df_last5.index.hour, df_last5.index.minute]).mean()
    df_mean.index.set_names(['hour', 'minute'], inplace=True)
    df_mean = df_mean.reset_index()

    # Create a new datetime index based on meanday_from plus the hour/minute offsets
    time_offsets = pd.to_timedelta(df_mean['hour'], unit='h') + pd.to_timedelta(df_mean['minute'], unit='m')
    df_mean.index = meanday_from + time_offsets
    df_mean.drop(columns=['hour', 'minute'], inplace=True)
    safe_to_json(df_mean, f_dmean5)

    # Save the last 5 days of data
    safe_to_json(df_last5, f_dlast5)

if __name__ == "__main__":
    main()
