import os.path as op
import yaml
from collections import namedtuple


def get_country_names():
    """
    Parse the regions.yaml file and extract the 
    country names as list.
    """
    # Define the directory that this file is sitting in
    path = op.abspath(op.dirname(__file__))

    # Open the config file in the same directory and extract all
    # the bounds data
    with open(op.join(path, "regions.yaml")) as f:
        data = yaml.load(f)
    
    # Converts the dictionary to list of country names
    country_names = list(data)
    
    return country_names


def get_bounds(region):
    """
    Parse the regions.yaml config file and extract bounds information
    for reading data.

    NOTE: It is not advised to try and write data for a region, unless
    they are an exact match to a tile. If the data extents don't match a
    tile in the DataCube they will be kicked out with an error. Use
    tiles for data that needs to be written.

    :param region: String name of a region defined in the bounds config
                   file or a list containing coordinates for the
                   bounding box in order [NESW].

    :return: Named tuple of bounding box to be extracted.
    """

    if isinstance(region, str):

        # Define the directory that this file is sitting in
        path = op.abspath(op.dirname(__file__))

        # Open the config file in the same directory and extract all
        # the bounds data
        with open(op.join(path, "regions.yaml")) as f:
            bounds_data = yaml.load(f)

        # Extract the bounds for this region
        try:
            bounds_dict = bounds_data[region]
        except KeyError:
            raise KeyError("Region %s does not exist in regions.yaml" % region)

    elif isinstance(region, list):

        bounds_dict = {'north': region[0],
                       'east': region[1],
                       'south': region[2],
                       'west': region[3]}

    else:
        raise ValueError("Regions kwarg must be list of [NESW] or string of a "
                         "valid region in regions.yaml")

    # Set up structure of named tuple to hold the information
    Bounds = namedtuple('Bounds', 'north south east west')

    # Add bounds to named tuple instance
    region_bounds = Bounds(**bounds_dict)

    return region_bounds

# Todo: This part of the DQTools codebase could be extended to do some or
#       all of the following:
#
#       1. Allow a user to pass a latitude/longitude point
#       2. Allow an interface to graphical area-select tools
#       3. Integrate with geo-locations library to allow a user to enter a city
#           or country name instead of lat/lon information
#
