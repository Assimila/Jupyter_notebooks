import logging
from .connect.connect import Connect


class Authenticate:

    """
    Class for checking access to the DataCube
    """

    def __init__(self, identfile=None):
        """
        Class to check the identity of a user

        :param identfile: optionally provide specific identity file
        :return: none
        """
        try:

            self.logger = logging.getLogger("__main__")

        except Exception:
            raise

        try:
            # Connect to DQ Client objects
            self.conn = Connect(identfile)

        except Exception as e:
            self.logger.error("Unable to create Authentication object.\n%s" % e)
            print("Unable to create Authentication object, "
                  "please see logfile for details.")

    def check_ident(self):
        """
        Check the identity of a user

        :return: True if all OK, false otherwise
        """
        try:

            self.logger = logging.getLogger("__main__")

            # Send identity to the connector
            return self.conn.check_ident()

        except Exception:
            raise
