import pandas as pd

d = pd.read_csv('db.csv')

d['data'] = pd.to_datetime(d.data).dt.tz_localize('Europe/Rome')
d.index=d['data']
d.drop(columns=['data'],inplace=True)

d24=d.last('24h')

d24.to_json('db_latest.json')
