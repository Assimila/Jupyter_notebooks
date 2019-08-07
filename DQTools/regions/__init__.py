import os.path as op
import yaml
from collections import namedtuple


def get_bounds(region):
    """
    Parse the regions.yaml config file and extract bounds information for
    reading data.

    NOTE: It is not advised to try and write data for a region, unless they
    are an exact match to a tile. If the dataextents don't match a tile in
    the DataCube they will be kicked out with an error. Use tiles for data
    that needs to be written.

    :param region: name of a region defined in the bounds config file.
    :return:
    """

    # Define the directory that this file is sitting in
    path = op.abspath(op.dirname(__file__))

    # Open the config file in the same directory and extract all the bounds data
    with open(op.join(path, "regions.yaml")) as f:
        bounds_data = yaml.load(f)

    # Extract the bounds for this region
    try:
        bounds_dict = bounds_data[region]
    except KeyError:
        raise KeyError(f'Region {region} does not exist in regions.yaml')

    # Set up structure of named tuple to hold the information
    Bounds = namedtuple('Bounds', 'north south east west')

    # Add bounds to named tuple instance
    region_bounds = Bounds(**bounds_dict)

    return region_bounds


# Todo: This part of the code could be extended to do some or all of the
#       following:
#
#       1. Allow a user to pass a latitude/longitude point
#       2. Allow an interface to graphical area-select tools
#       3. Integrate with geo-locations library to allow a user to enter a city
#           or country name instead of lat/lon information
#
