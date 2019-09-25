import yaml

from .connect.connect import Connect

class Register:

    """
    Class for registering data to the DataCube
    """

    def __init__(self, config_file_path):
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
            conn = Connect()

            # Send to the connector
            conn.register(config_dict)

        except (FileNotFoundError, OSError) as e:
            raise RuntimeError(f"Unable to load configuration for "
                               f"registration.\n{e}")
        except Exception as e:
            raise RuntimeError("Unable to create Registration object.") from e