import pandas as pd
import sys

src=sys.argv[1]
dst=sys.argv[2]

d = pd.read_csv(src)

d['data'] = pd.to_datetime(d.data)
d.index=d['data']
d.drop(columns=['data'],inplace=True)

d24=d.last('24h')

d24.to_json(dst)
