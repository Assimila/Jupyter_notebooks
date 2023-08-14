from DQTools.search import Search
from DQTools.dataset import Dataset
import datetime as dt

s = Search()
print(s.tiles())
print(s.products())
print(s.subproducts())

# provide sysfile to use DASK, remove this arg to use http server
d = Dataset(product="era5", subproduct="skt", tile="era5_africa", res=0.25,
            sysfile="/workspace/datacube/src/datacube/system_staging_vm.yaml")

data = d.get_data(start=dt.datetime(2018, 8, 1),
                  stop=dt.datetime(2018, 8, 2),
                  tile='ken_prise')

print(data)