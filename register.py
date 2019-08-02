import yaml

from src.engine.connect.connect import Connect

class Register:

    def __init__(self, config_file_path):
        """
        Register a new tile. Pass in either a dictionary or a yaml file with
        the appropriate components.

        :param config_file_path:
        :return:
        """

        # Extract the config information from the yaml file
        with open(config_file_path, 'r') as file:
            config_dict = yaml.load(file)

        # Connect to DQ
        conn = Connect()

        # Send to the connector
        conn.register(config_dict)
