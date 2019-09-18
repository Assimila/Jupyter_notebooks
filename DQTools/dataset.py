import numpy as np
import re
import textwrap
import pandas as pd

from .connect.connect import Connect
from .regions import get_bounds


class Dataset:
    """
<<<<<<< HEAD
    This is the representation of a DataCube Dataset in the DQTools library.
=======
    The class to interact with Assimila DataCube data.
>>>>>>> 44e427e99733328e8da9ca8378bcb2ef7a567b8e
    """

    def __init__(self, product, subproduct, region=None, tile=None, res=None,
                 key_file=None):
        """
        Connect to the datacube and extract metadata for this particular
        product/subproduct.

        Attributes passed from the caller are recorded in self:
        self.product: name of the product
        self.subproduct: name of subproduct
        self.region [optional]: name of region required
        self.tile [optional]: name of tile required


        NOTE: If a region/tile is defined, then metadata pertains only to
        that region or tile. If no region/tile is defined then metadata is
        returned for the entire subproduct extent.

        Empty attributes created for
        - self.data: The xarray DataSet
        - self.timesteps: The timesteps of data available

<<<<<<< HEAD
        :param product: product name (str)

        :param subproduct: sub product name (str)

        :param region [optional]: the name of a region for data/metadata,
                                  as defined in the regions directory
                                  (NOTE: writing data for regions
                                  is not possible, unless the bounds
                                  exactly match a tile... in which case
                                  just use tile to define our spatial
                                  extent!)

        :param tile [optional]: the tile to extract data/metadata for
                                (must match datacube record)

        :param res [optional]: the resolution of the output data
                               required. This will ultimately enact a
                               GDAL Warp inside the datacube to give
                               you the required resolution within the
                               bounds defined in either tile or region.

        :param key_file: Assimila DQ key file required to access the
                         HTTP server. Allows keyfile to be in a different
                         location as used by the QGIS Plugin.
=======
        :param product:     product name (str)

        :param subproduct:  sub product name (str)

        :param region:      optional - the name of a region for
                            data/metadata, as defined in the regions
                            directory (NOTE: writing data for regions is not
                            possible, unless the bounds exactly match a tile...
                            in which case just use tile to define our spatial
                            extent!)

        :param tile:        optional - the tile to extract data/metadata for
                            (must match datacube record)

        :param res:         optional - the resolution of the output data
                            required. This will ultimately execute a GDAL Warp
                            inside the datacube to give you the required
                            resolution within the bounds defined in either tile
                            or region.

        :param key_file:    optional - Assimila DQ key file required to access
                            theHTTP server. Allows keyfile to be in a different
                            location as used by the QGIS Plugin.
>>>>>>> 44e427e99733328e8da9ca8378bcb2ef7a567b8e

        """

        # write product & subproduct as attributes
        self.product = product
        self.subproduct = subproduct

        # Write region as an attribute
        self.region = region

        # Write resolution as an attribute
        self.res = res

        # Extract the bounds for this region, if provided
        if self.region:
            bounds = get_bounds(self.region)._asdict()
        else:
            bounds = None

        # Create empty attributes for later data
        self.last_timestep = None
        self.first_timestep = None
        self.last_gold = None
        self.fill_value = None
        self.all_subproduct_tiles = None
        self.description = None
        self.frequency = None

        # Write tile as an attribute
        self.tile = tile

        # Instatiate the datacube connector
        self.conn = Connect(key_file=key_file)

        # Download metadata for this product+subproduct+tile
        result = self.conn.get_subproduct_meta(product=self.product,
                                               subproduct=self.subproduct,
                                               bounds=bounds,
                                               tile=tile)

        # Extract relevant metadata as attributes.
        self.extract_metadata(result)

        # Create empty attributes
        self.data = None
        self.timesteps = None

    def __repr__(self):
        """
        User-friendly representation of the dataset object

        :return:
        """
        return f"""<DQ Dataset: {self.product}-{self.subproduct}>
================================================================================
Product:        {self.product}
Sub-product:    {self.subproduct}
================================================================================
{textwrap.fill(self.description, 79)}

Tiles:
    In datacube:    {self.all_subproduct_tiles}
    Selected tile:  {self.tile}

Timesteps available:
    First:          {self.first_timestep}
    Last:           {self.last_timestep}
    Frequency:      {str(self.frequency)}

Last Gold:          {self.last_gold}
================================================================================
Data:
{self.data}
================================================================================
        """

    def extract_metadata(self, all_meta):
        """
        Extract the metadata required to populate the attributes on
        initialisation. This parses the metadata sent from the data cube
        to extract and records key parameters:

        Metadata parameters created:
        - self.last_gold: The last 'good' time step of data. Defined by
        developer.
        - self.last_timestep: The last time step of data recorded in the
          DataCube
        - self.first_timestep: The first time step of data recorded in
          the DataCube
        - self.fill_value: The fill value for this data
        - self.all_subproduct_tiles: All tiles available for this
          subproduct in the data cube
        - self.tiles: The tile currently selected in this instance

        :param all_meta: metadata dump from the data cube 'get meta'
                         request

        :return:
        """

<<<<<<< HEAD
        # Silencing SettingWithCopyError caused by subset line below
        pd.options.mode.chained_assignment = None

        # Filter by selected tile so that mosaicking does not impact return
        # If >1 tilename specified
        if len(list(set(all_meta.tilename))) > 1:
            all_meta = all_meta.loc[all_meta['tilename'] == self.tile]

=======
>>>>>>> 44e427e99733328e8da9ca8378bcb2ef7a567b8e
        # Extract the last timestep
        if 'datetime' in all_meta.columns:

            self.first_timestep = min(all_meta['datetime'])
            self.last_timestep = max(all_meta['datetime'])

            # Sort this dataframe by datetime
<<<<<<< HEAD
            all_meta.sort_values(by=['datetime'], inplace=True)
=======
            all_meta.sort_values(['datetime'], inplace=True)
>>>>>>> 44e427e99733328e8da9ca8378bcb2ef7a567b8e

            # Extract last gold
            if (all_meta['gold'] == False).all():

                # Nothing is 'gold' so there is no concept of last gold
                self.last_gold = None

            elif (all_meta['gold'] == True).all():

                # Last gold is the same as the last timestep
                self.last_gold = self.last_timestep

            elif (all_meta['gold'] == False).any():

                # Last gold is an update point. So if we have gappy
                # gold date (i.e. a few gold, few not gold, few gold
                # again, all not gold) then the update point is the end
                # of the batch of continuous gold.
                last_gold_idx = np.where(all_meta['gold'] == False)[0][0] - 1
                self.last_gold = list(all_meta['datetime'])[last_gold_idx]

            else:
                raise Exception("Unable to ascertain last gold")

        else:
            self.last_timestep = None
            self.first_timestep = None
            self.last_gold = None

        # Check there is only one fill value:
        if len(all_meta['datafillvalue'].unique()) == 1:
<<<<<<< HEAD
            self.fill_value = all_meta['datafillvalue'].iloc[0]
=======
            self.fill_value = all_meta['datafillvalue'][0]
>>>>>>> 44e427e99733328e8da9ca8378bcb2ef7a567b8e
        else:
            raise Exception("Multiple fill values for single datacube "
                            "subproduct. This shouldn't be possible.")

        # Available tiles
        self.all_subproduct_tiles = all_meta['tilename'].unique()

        # General Meta
        self.description = all_meta['description'].unique()[0]

        # Extract acquisition frequency / time step from database. Store
        # as an np.timedelta64
        frequency_string = all_meta['frequency'].unique()[0]
        fs_split = re.split('(\D+)', frequency_string)
        self.frequency = np.timedelta64(int(fs_split[0]), fs_split[1])

<<<<<<< HEAD
    def get_data(self, start, stop, region=None, tile=None, res=None):
        """
        Extract data from the datacube for the passed parameters

        :return:
=======
    def get_data(self, start, stop,
                 region=None, tile=None, res=None,
                 country=None):
        """
        Extract data from the datacube to the specification supplied.

        :param start:   Start datetime for dataset

        :param stop:    Stop datetime for dataset

        :param region:  optional - geographic region, do not use tile too

        :param tile:    optional - specific tile, do not use region too
                        Tile or region are only needed here if not already
                        given when creating the Dataset object.

        :param res:     optional - resolution required
                        If providing a country and therefore expecting zonal
                        averaging, it is recommended to set this value to 0.01
                        to super-sample the data and ensure each county has
                        at least one pixel.

        :param country: optional - if country name is supplied, the returned
                        dataset will have been zonally averaged according to
                        county definitions within that country. The country
                        name is case insensitive but must be one for which
                        the system has a shapefile defining its counties.

        :return: xarray of data
>>>>>>> 44e427e99733328e8da9ca8378bcb2ef7a567b8e
        """

        # Extract the bounds information
        if region:
            bounds = get_bounds(region)
        elif self.region:
            bounds = get_bounds(self.region)
        else:
            bounds = None

        # Extract tile info
        if not tile and self.tile:
            tile = self.tile

        # Extract res info
        if not res and self.res:
            res = self.res

        # Fetch the data from the datacube
        data = self.conn.get_subproduct_data(product=self.product,
                                             subproduct=self.subproduct,
                                             start=start,
                                             stop=stop,
                                             bounds=bounds,
                                             res=res,
<<<<<<< HEAD
                                             tile=tile)

        # Datacube returns a list of xarrays. We only have one subprduct
        # by definition
        self.data = data[0]

    def put(self):
        """
        Prepare self.data and metadata for putting into the datacube.
=======
                                             tile=tile,
                                             country=country)

        # TODO Fix DQ to ALWAYS return list of xarrays
        if not country:
            # Datacube returns a list of xarrays. We only have one subproduct
            # by definition
            self.data = data[0]
        else:
            self.data = data

    def put(self):
        """
        Prepare self.data and metadata and send to the datacube.
>>>>>>> 44e427e99733328e8da9ca8378bcb2ef7a567b8e

        :return:
        """

        # Add product as an attribute to the data which will be written
        self.data.attrs['product'] = self.product

        # Process last gold. This value needs to go into the DataArray
        # attributes. The user could set them here, in the the DataSet
        # attributes or in self.data.attrs. Easiest if we just catch and
        # process all possibilities.
        if 'last_gold' not in self.data[self.subproduct].attrs or \
                self.data[self.subproduct].attrs['last_gold'] == None:

            if 'last_gold' not in self.data.attrs:
                self.data[self.subproduct].attrs['last_gold'] = self.last_gold
            else:
                self.data[self.subproduct].attrs['last_gold'] = \
                    self.data.attrs['last_gold']

        # Check that this has given us a last gold
        if not self.data[self.subproduct].attrs['last_gold']:
            raise Exception(f"Last gold not set for {self.subproduct}")

        if self.subproduct not in self.data.data_vars.keys():
            raise NameError("data.name must be equal to subproduct for "
                            "ingesting into the datacube")

        # Assign parent attributes to data variable
        for x in self.data.attrs:
            self.data[self.subproduct].attrs[x] = self.data.attrs[x]

        # Instatiate the datacube connector
        conn = Connect()

        # Put the data into the datacube
        conn.put_subproduct_data(data=self.data)

    def update(self, script, params=None):
        """
        Update this dataset using the update method in the script
        supplied. Following the calculation, re-initialise from the
        DataCube to update
        the metadata.

        :param script: The python script for updating this dataset
        :param params: A dictionary of keyword arguments to be passed
                       to the update method

        :return:
        """

        # Run the update script with the appropriate parameters
        if params:
            script.update(**params)
        else:
            script.update()

        # Re-initialise dataset information after update
        self.__init__(self.product, self.subproduct, region=self.region,
                      tile=self.tile)

    def calculate_timesteps(self):
        """
        Calculate the time steps available, given the frequency of the
        dataset (as recorded in the subproduct table) and the first and
        last time steps.

        NOTE: This method calculates ideal timesteps, rather than
        retrieving the actual timesteps of the data. This method cannot
        know about any data gaps.

        :return:
        """

        # split the numpy timedelta into it's component parts (e.g.
        # ['year', 1])
        bf_fq_vals = self.frequency.__str__().split(' ')

        # Create a pandas DataOffset object which represents this
        # frequency
        frequency = pd.DateOffset(**{bf_fq_vals[1]: int(bf_fq_vals[0])})

        # Generate an array, using this as the step
        if self.first_timestep:
            timesteps = pd.date_range(self.first_timestep,
                                      self.last_timestep,
                                      freq=frequency)

            self.timesteps = timesteps.values

        else:
            self.timesteps = None
