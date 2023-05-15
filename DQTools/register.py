import yaml
import logging
import datetime
import os.path as op
from .connect.connect import Connect
from .connect.log.setup_logger import SetUpLogger


class Register:
    """
    Class for registering data with the DataCube
    """

    def __init__(self, identfile=None):
        """
        Initialise the Register class
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

    def register_from_yaml(self, config_file_path):
        """
        Register a new product/sub-product or tile from a config.yaml file
        file.

        :param config_file_path: The full path to the config file
        :return:
        """

        try:
            # Extract the config information from the yaml file
            with open(config_file_path, 'r') as file:
                config_dict = yaml.load(file)

            # Connect to DQ
            conn = Connect(self.identfile)

            # Send to the connector
            conn.register(config_dict)

            #self.logger.info(f"Contents of {config_file_path} registered.")
            self.logger.info("Contents of %s registered." % config_file_path)

        except (FileNotFoundError, OSError) as e:
            self.logger.error("Unable to load configuration for registration.\n"
                              "%s" % e)
            print("Unable to load configuration for registration, "
                  "please see logfile for details.")
        except Exception as e:
            self.logger.error("Unable to create Registration object.\n%s" % e)
            print("Unable to create Registration object, "
                  "please see logfile for details.")

    def register_tiles_from_local_file(self, filepath):
        """
        Transfer the contents of a local tile definition file to the server and
        use it to register its contents.
        The user must have permission to REGISTER, and the file
        *MUST* be in the right format with all necessary metadata.
        The name of the file will be used but held in temporary storage.
        :param path: fully qualified location of file on the client. The file's name
                     MUST be in the standard format for the Assimila DataCube.
        :return:
        """
        try:
            # Instantiate the datacube connector
            conn = Connect(identfile=self.identfile)

            conn.register_tiles_from_file(filepath)

        except Exception as e:
            self.logger.error("Failed to register tile(s) with the datacube.\n"
                              "%s" % e)
            print("Failed to register tile(s) with the datacube.")
