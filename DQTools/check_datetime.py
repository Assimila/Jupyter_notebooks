import pandas as pd
import numpy as np
import datetime as dt


class Datetime_checker:

    def __init__(self, time):
        self.time = time
        self.formats = ['%Y-%m-%d', '%Y %m %d', '%Y/%m/%d', '%d-%m-%Y',
                        '%d %m %Y', '%d/%m/%Y', '%d-%m-%YT%H:%M']

    def c_and_c(self):
        """
        Runs checks on self.time
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
