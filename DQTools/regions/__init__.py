import os.path as op
import yaml
from collections import namedtuple


def get_bounds(region):
    """
    Return the bounds for a region
    :param region:
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
    Bounds = namedtuple('Bounds','north south east west')

    # Add bounds to named tuple instance
    region_bounds = Bounds(**bounds_dict)

    return region_bounds

def add_region(region):
    #Todo: a method where a user can programatically add regions.
    pass

def show_regions():
    #Todo: a method where a user can programatically view all available regions.
    pass