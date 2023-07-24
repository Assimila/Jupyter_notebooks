import os.path as op
import sys
import datetime as dt
import xarray as xr
import numpy as np

from DQTools import Dataset

product = 'mlstas'
subproduct = 'q_flag'
year = 2021
month = 8
day = 13

# using the file directly
filename = f"/datacube/{product}/{subproduct}/era5_africa" \
           f"/{product}_{subproduct}_era5_africa_{year}-{month:02}-" \
           f"{day:02}.tif"
file_data = xr.open_rasterio(filename)

# using dqtools to get the data
ds = Dataset(product=product, subproduct=subproduct,
        identfile='/workspace/DQTools/DQTools/connect/.assimila_dq')
ds.get_data(start=dt.datetime(year, month, day, 5, 0),
            stop=dt.datetime(year, month, day, 6, 0),
            tile='era5_africa')

# print(ds.data)

# comparing the data
adjusted_file = file_data[:, 300:310, 400]
adjusted_ds = (ds.data[subproduct][:, 300:310, 400])
#
# printing the xarrays
print('***************FILE DATA****************')
print(adjusted_file)
print('***************DQTOOLS DATA****************')
print(adjusted_ds)

# comparing them
print('***********Equal?***************')
print(np.array_equal(adjusted_ds.values, adjusted_file.values))


# tamsat = Dataset(product='tamsat', subproduct='rfe')
#
# tamsat.get_data(start=dt.datetime(1999, 1, 1),
#                 stop=dt.datetime(1999, 1, 2))
#
# print(tamsat.data)
