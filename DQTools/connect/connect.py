import os.path as op
import numpy as np

from .DQclient import AssimilaData


class Connect:
    """
    Establish a connection with the datacube
    """

    def __init__(self):
        """
        Make the connection when the engine libraries are imported.
        """
        self.http_client = AssimilaData(keyfile=op.join(op.dirname(__file__),
                                                        ".assimila_dq"))

    def get_subproduct_meta(self, product, subproduct, bounds=None, tile=None):
        """
        Extract all available metadata for this product+subproduct
        :param product:
        :param subproduct:
        :param bounds: dictionary of n-s-e-w bounds
        :return:
        """
        try:

            result = self.http_client.get({'command': 'GET_META',
                                           'product': product,
                                           'sub-product': subproduct,
                                           'bounds': bounds,
                                           'tile': tile})

            # Dereference to get 2nd (sub-prod) element of the first (and
            # only) sub-list
            return result[0][1]

        except Exception as e:
            # TODO add engine exceptions and logging
            raise e


    def get_subproduct_data(self, product, subproduct, start, stop, bounds,
                            res, tile):
        """
        Extract and return an xarray of data from the datacube

        :param product:
        :param subproduct:
        :param start:
        :param stop:
        :param bounds:
        :return:
        """

        # Prepare the product metadata
        get_request_metadata = {
            'product': product,
            'subproduct': [subproduct],
            'start_date': start,
            'end_date': stop,
            'gap_filled': True,
        }

        # if a resolution has been provided then we warp for this resolution
        if res:
            get_request_metadata['warp'] = {'xRes':res, 'yRes':res}
            get_request_metadata['warptobounds'] = True

        # Add in bounds information if required
        if tile:
            get_request_metadata['tile'] = tile
        elif bounds:
            get_request_metadata['north'] = bounds.north
            get_request_metadata['south'] = bounds.south
            get_request_metadata['east'] = bounds.east
            get_request_metadata['west'] = bounds.west
        else:
            get_request_metadata['north'] = 90
            get_request_metadata['south'] = -90
            get_request_metadata['east'] = 360
            get_request_metadata['west'] = 0

        # Request data
        data = self.http_client.get({
            'command': 'GET_DATA',
            'product_metadata': get_request_metadata})

        return data

    def put_subproduct_data(self, data):
        """
        Write data to the datacube

        :param product: name of product
        :param subproduct: name of sub-product
        :param data: an xarray DataSet object
        :return:
        """
        # 'name' is only an attribute of DataArray, not DataSet
        # # Add the subproduct as the xarray name
        # data.name = subproduct

        # Prepare put request
        put_request = {
            'command': 'PUT_DATA',
            'overwrite': 'True'}

        self.http_client.put(put_request, data)

    def get_all_table_data(self, tablename):
        """
        Method to return everything in a single table. Used for Search class
        methods.

        #Todo: make this work over HTTP. If not possible, then update this and
        # the Search class methods.

        :param table:
        :return:
        """

        request = {
            'command': 'GET_META',
            'bespoke_search': {'get_tables': tablename}
        }

        result = self.http_client.get(request)

        return result

    def register(self, config_dict):
        """
        Register tiles and/or products-subproduct groups intot he datacube.

        :param config_dict:
        :return:
        """
        # Prepare put request
        put_request = {
            'command': 'PUT_NEW',
            'reg_info': config_dict}

        self.http_client.put(put_request)
