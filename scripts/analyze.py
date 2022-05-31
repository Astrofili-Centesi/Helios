import pandas as pd
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

src=sys.argv[1]
f_d24=sys.argv[2]
f_dday=sys.argv[3]
f_dmean5=sys.argv[4]
f_dlast5=sys.argv[5]
f_dlastmonth=sys.argv[6]

d = pd.read_csv(src)

d['data'] = pd.to_datetime(d.data)
d.index=d['data']
d.drop(columns=['data'],inplace=True)

# Sync with 5 minutes interval

d=d.resample('300s').mean()

d24=d.last('24h')

d24.to_json(f_d24)


# Salva un file con l'ultimo giorno intero
lastTime=d.index[-1]
lastDay=lastTime-pd.Timedelta('1D')
logging.info("lastTime {} lastDay {}".format(lastTime,lastDay))
yesterdayFrom=lastDay.floor('1D')
yesterdayTo=lastDay.ceil('1D')
logging.info("yesterdayFrom {} yesterdayTo {}".format(yesterdayFrom,yesterdayTo))

dYesterday=d[(d.index>=yesterdayFrom) & (d.index < yesterdayTo)]

dYesterday.to_json(f_dday)

# Salva un file con la media degli ultimi 5 giorni
meandayFrom=(lastDay-pd.Timedelta('5D')).floor('1D')
meandayTo=(lastDay).floor('1D')
logging.info("meandayFrom {} meandayTo {}".format(meandayFrom,meandayTo))

dmeanday=d[(d.index>=meandayFrom) & (d.index < meandayTo)]

dmean=dmeanday.groupby([dmeanday.index.hour,dmeanday.index.minute]).mean()

dmean.index.set_names(['hour','minute'],inplace=True)
dmean.reset_index(inplace=True)
dmean.index=meandayFrom+pd.Series(map(lambda x:pd.Timedelta(hours=x),dmean['hour']))+pd.Series(map(lambda x:pd.Timedelta(minutes=x),dmean['minute']))
dmean.drop(columns=['hour','minute'],inplace=True)

dmean.to_json(f_dmean5)
dmeanday.to_json(f_dlast5)

# Salva un file con l'ultimo mese
dlastMonth=d.last('1m')

dlastMonth.to_json(f_dlastmonth)

