import numpy as np
import re
import textwrap
import pandas as pd

from src.engine.connect.connect import Connect
from src.engine.regions import get_bounds

class Dataset:
    """
    The engine dataset class.
    """

    def __init__(self, product, subproduct, region=None, tile=None):
        """
        Connect to the datacube and extract metadata for this particular
        product/subproduct.

        Metadata attributes created:
        - last_gold
        - last_timestep

        :param product:
        :param subproduct:
        """

        # write product & subproduct as attributes
        self.product = product
        self.subproduct = subproduct

        # Write region as an attribute
        self.region = region

        # Extract the bounds for this region, if provided
        if self.region:
            bounds = get_bounds(self.region)._asdict()
        else:
            bounds = None

        # Write tile as an attribute
        self.tile = tile

        # Instatiate the datacube connector
        conn = Connect()

        # Download metadata for this product+subproduct+tile
        result = conn.get_subproduct_meta(product=self.product,
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
        The representation of the dataset object
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
        Extract the metadata specifically required by the engine from the
        bundle that's sent back from the datacube
        :param all_meta:
        :return:
        """

        # Extract the last timestep
        if 'datetime' in all_meta.columns:

            self.first_timestep = min(all_meta['datetime'])
            self.last_timestep = max(all_meta['datetime'])

            # Sort this dataframe by datetime
            all_meta.sort_values(['datetime'], inplace=True)

            # Extract last gold
            if (all_meta['gold'] == False).all():

                # Nothing is 'gold' so there is no concept of last gold here
                self.last_gold = None

            elif (all_meta['gold'] == True).all():

                # Last gold is the same as the last timestep
                self.last_gold = self.last_timestep

            elif (all_meta['gold'] == False).any():

                # Last gold is an update point. So if we have gappy gold date (
                # i.e. a fe gold, few not gold, few gold again, all not gold)
                # then the update point is the end of the batch of continuous gold.
                last_gold_idx = np.where(all_meta['gold'] == False)[0][0] - 1
                self.last_gold = all_meta['datetime'][last_gold_idx]


            else:
                raise Exception("Unable to ascertain last gold")

        else:
            self.last_timestep = None
            self.first_timestep = None
            self.last_gold = None

        # Check there is only one fill value:
        if len(all_meta['datafillvalue'].unique()) == 1:
            self.fill_value = all_meta['datafillvalue'][0]
        else:
            raise Exception("Multiple fill values for single datacube "
                            "subproduct. This shouldn't be possible.")

        # Available tiles
        self.all_subproduct_tiles = all_meta['tilename'].unique()

        # General Meta
        self.description = all_meta['description'].unique()[0]

        # Extract aquisition frequency / timestep from database. Store as an
        # np.timedelta64
        frequency_string = all_meta['frequency'].unique()[0]
        fs_split =  re.split('(\D+)', frequency_string)
        self.frequency = np.timedelta64(int(fs_split[0]), fs_split[1])

    def get_data(self, start, stop, region=None, tile=None, res=None):
        """
        Extract data from the datacube for the passed parameters

        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # Extract the bounds information
        if region:
            bounds = get_bounds(region)
        elif self.region:
            bounds = get_bounds(self.region)
        else:
            bounds = None

        if not tile and self.tile:
            tile = self.tile

        # Fetch the data from the datacube
        data = conn.get_subproduct_data(product=self.product,
                                        subproduct=self.subproduct,
                                        start=start,
                                        stop=stop,
                                        bounds=bounds,
                                        res=res,
                                        tile=tile)

        # Datacube returns a list of xarrays. We only have one subprduct by
        # definition
        self.data = data[0]

    def put(self):
        """
        Put this data and metadata into the datacube
        :return:
        """

        # Add product as an attribute to the data which will be written
        self.data.attrs['product'] = self.product

        # Process last gold. This value needs to go into the DataArray
        # attributes. The user could set them here, in the the DataSet
        # attributes or in self.data.attrs. Easiest if we just catch and
        # process all possibilities.
        if 'last_gold' not in self.data[self.subproduct].attrs:
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

        # Instatiate the datacube connector
        conn = Connect()

        # Put the data into the datacube
        conn.put_subproduct_data(data=self.data)

    def update(self, script, params=None):
        """
        Update this dataset by recalculating from script.
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
        Calculate the timesteps available, given the registered frequency of
        the data and the start and last timesteps
        :return:
        """

        # split the numpy timedelta into it's component parts (e.g. ['year', 1])
        bf_fq_vals = self.frequency.__str__().split(' ')

        # Create a pandas DataOffset object which represents this frequency
        frequency = pd.DateOffset(**{bf_fq_vals[1]:int(bf_fq_vals[0])})

        # Generate an array, using this as the step
        if self.first_timestep:
            timesteps = pd.date_range(self.first_timestep, self.last_timestep,
                                      freq=frequency)

            self.timesteps = timesteps.values

        else:
            self.timesteps = None




if __name__=='__main__':

    # For testing (only for now)
    tamsat = Dataset(product='tamsat', subproduct='rfe')
    tamsat.get_data(start='2019-06-01', stop='2019-06-30')
