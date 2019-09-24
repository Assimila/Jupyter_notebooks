from .connect.connect import Connect


class Search:
    """
    Tools to allow a user to check the contents of the datacube from the
    commandline.

    New search requests can be serviced by adding to the BespokeSearch
    class in the DataCube at: src/datacube/dq_database/db_view.py
    """

    @staticmethod
    def tiles():
        """
        Return all the tiles available.
        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # extract a dataframe of the tile table
        df = conn.get_all_table_data("tile")

        return df

    @staticmethod
    def products():
        """
        Return all the products available.
        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # extract a dataframe of the product table
        df = conn.get_all_table_data("product")

        return df

    @staticmethod
    def subproducts():
        """
        Return all the sub-products available.
        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # extract a dataframe of the sub-product table
        df = conn.get_all_table_data("subproduct")

        return df

    def get_subproduct_list_of_product(self, product):
        """
        Return a list of sub-products based on product selected
        :param product: The name of the product
        :return:
        """
        # Instantiate the datacube connector
        conn = Connect()

        return conn.get_product_subproducts(product)

        # # Get product's dataframe
        # result = conn.get_product_meta(product)
        #
        # # Initialise list
        # list = []
        #
        # # Gets sub-product of the product
        # # result[index][1].name -- gets indexth sub-product
        # for r in result:
        #     # Identifies unique sub-product names
        #     sub = (r[1].name.unique().tolist())
        #     # Adds to list
        #     list.append(sub)
        #
        # # Use monoids to extract the list
        # subproduct_list = sum(list, [])
        #
        # return subproduct_list

