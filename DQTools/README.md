# DQTools
Tools for working with the DataCube. Includes reading metadata, registering new products and writing new data to the Datacube.

If using DQTools on the same VM as a running datacube, it's possible to use DASK for more efficient data retrieval. In this case, you must also give your DQTools Dataset class a suitable configuration file as found in the datacube repository at datacube/src/datacube/system_*_vm.yaml
