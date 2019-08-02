from src.engine.connect.connect import Connect

class Search:
    """
    Tools to allow a user to check the contents of the datacube from the
    commandline
    """

    @staticmethod
    def tiles():
        """
        Return all the tiles available.
        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # extract a dataframe of the tiles table
        df = conn.get_all_table_data("tile")

        return df

    @staticmethod
    def products():
        """
        Return all the tiles available.
        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # extract a dataframe of the tiles table
        df = conn.get_all_table_data("product")

        return df

    @staticmethod
    def subproducts():
        """
        Return all the tiles available.
        :return:
        """
        # Instatiate the datacube connector
        conn = Connect()

        # extract a dataframe of the tiles table
        df = conn.get_all_table_data("subproduct")

        return df

