import pandas as pd
import numpy as np
import datetime as dt


class Datetime_checker:
    """
    Datetime_checker object contains a method to convert a given time
    variable to datetime
    :param time: The time to be converted to datetime.datetime can be in many
                 different datatypes such as string, np.datetime64 and
                 pd.Timestamp
    :attr formats: Variables where all acceptable formats of string are stored,
                  these are used to try convert string to datetime
    """

    def __init__(self, time):
        self.time = time
        self.formats = ['%Y-%m-%d', '%Y %m %d', '%Y/%m/%d', '%d-%m-%Y',
                        '%d %m %Y', '%d/%m/%Y', '%d-%m-%YT%H:%M',
                        '%Y-%m-%dT%H:%M:%S']

    def c_and_c(self):
        """
        Runs checks on self.time and if applicable converts it to
        datetime.datetime
        """
        try:
            if isinstance(self.time, dt.datetime):

                return self.time

            elif isinstance(self.time, dt.date) or isinstance(
                    self.time, dt.date):

                return dt.datetime.combine(self.time, dt.time(0))

            elif isinstance(self.time, pd.Timestamp):

                return self.time.to_pydatetime()

            elif isinstance(self.time, np.datetime64):

                self.time = (self.time - np.datetime64(
                    '1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

                return dt.datetime.utcfromtimestamp(self.time.astype(int))

            elif isinstance(self.time, str):

                for fmt in self.formats:
                    try:
                        new_time = dt.datetime.strptime(self.time, fmt)
                        return new_time
                    except ValueError as e:
                        pass

        except TypeError as e:
            raise e
