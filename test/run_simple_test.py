import os.path as op
import sys
import datetime as dt

from DQTools import Dataset


tamsat = Dataset(product='tamsat', subproduct='rfe')

tamsat.get_data(start=dt.datetime(2000, 1, 1),
                stop=dt.datetime(2000, 1, 2),
                region=[100.0, 100.0, 110.0, 110.0])

print(tamsat.data)

start=dt.datetime(2018, 1, 1)
stop=dt.datetime(2018, 1, 31)
product, subproduct = 'MCD43A3', 'Albedo_WSA_vis'
north, east, south, west = 60.0, 3.2, 48.5, -11.0

ds = Dataset(product=product, subproduct=subproduct)
ds.get_data(start=start, stop=stop,
            region=[north, east, south, west])

print(ds.data)
