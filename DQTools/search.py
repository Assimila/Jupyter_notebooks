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
        Return all the subproducts available.
        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # extract a dataframe of the subproduct table
        df = conn.get_all_table_data("subproduct")

        return df
