import pandas as pd
import sys

src=sys.argv[1]
dst=sys.argv[2]
dst2=sys.argv[3]

d = pd.read_csv(src)

d['data'] = pd.to_datetime(d.data)
d.index=d['data']
d.drop(columns=['data'],inplace=True)

d24=d.last('24h')

d24.to_json(dst)


# Salva un file con l'ultimo giorno intero
lastTime=d.index[-1]
yesterdayFrom=lastTime.floor('1D')-pd.Timedelta('1D')
yesterdayTo=lastTime.ceil('1D')-pd.Timedelta('1D')

dYesterday=d[(d.index>yesterdayFrom) & (d.index < yesterdayTo)]

dYesterday.to_json(dst2)

