import numpy as np
import re
import textwrap
import pandas as pd
import logging
import datetime
import os.path as op
import sys
from .check_datetime import Datetime_checker

from .connect.connect import Connect
from .regions import get_bounds
from .connect.log.setup_logger import SetUpLogger


class File:
    """
    Class to handle any file operations
    """
    def __init__(self, identfile=None):
        """
        Initialise the File class
        :param identfile: Assimila DQ credentials file required to access the
                         HTTP server. Allows the file to be in a different
                         location as used by the QGIS Plugin.
        """
        try:
            self.identfile = identfile

            # base, extension = op.splitext('./connect/log/dataset.log')
            # today = datetime.datetime.today()
            # log_filename = "{}{}{}".format(base,
            #                                today.strftime("_%Y_%m_%d"),
            #                                extension)
            #
            # SetUpLogger.setup_logger(
            #     log_filename=op.abspath(op.join(op.dirname(__file__),
            #                                     log_filename)),
            #     default_config=op.abspath(op.join(op.dirname(__file__),
            #                    "./connect/log/logging_config.yml")))
            self.logger = logging.getLogger("__main__")

        except Exception:
            raise

    def put_contents_of_local_file(self, product, subproduct, tile, path):
        """
        Transfer the contents of a local geotiff file to the server.
        The user must have permission to WRITE for this sub-product, and the file
        *MUST* be in the right format with all necessary metadata.
        The name of the file will be used; you are currently NOT allowed to over-write
        an existing file.
        :param product:
        :param subproduct:
        :param tile:
        :param path:
        :return:
        """
        try:
            # Instantiate the datacube connector
            conn = Connect(identfile=self.identfile)

            conn.put_file_contents(product, subproduct, tile, path)

        except Exception as e:
            self.logger.error("Failed to write file data to the datacube.\n"
                              "%s" % e)
            print("Failed to write file data to the datacube.")

    def put_native_files(self):
        pass

    def put_native_folder(self):
        pass