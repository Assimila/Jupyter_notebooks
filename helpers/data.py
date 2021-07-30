from __future__ import print_function
import sys
sys.path.append("../")
from DQTools.DQTools.search import Search
from DQTools.DQTools.dataset import Dataset
from IPython.lib.display import FileLink
from IPython.display import display, clear_output
from ipyleaflet import (
    Map, Marker, basemaps, basemap_to_tiles,
    TileLayer, ImageOverlay, Polyline, Polygon, Rectangle,
    GeoJSON, WidgetControl, DrawControl, LayerGroup, FullScreenControl,
    interactive)
import ipywidgets as widgets
from pyproj import Proj, transform
from traitlets import traitlets
import pandas as pd
import datetime 
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import warnings
import subprocess
import json
import pickle
import xarray

import sys
sys.path.append("..")

warnings.filterwarnings("ignore", category=FutureWarning)


class Data:
    """
    Data reading, plotting and displaying methods.
    """

    def __init__(self, out, keyfile=None):

        self.out = out
        if keyfile is None:
            self.keyfile = os.path.join(os.path.expanduser("~"),
                                        '.assimila_dq.txt')
        else:
            self.keyfile = keyfile

    def get_data_from_datacube(self, product, subproduct, start, end,
                               latitude, longitude, projection=None):
        ds = Dataset(product=product,
                     subproduct=subproduct,
                     identfile=self.keyfile)

        first, last = self.get_dates(ds, start, end)
        ds.get_data(start=first, stop=last, projection=projection,
                    latlon=[latitude, longitude])

        return ds.data

#     def get_data_from_datacube(self, product, subproduct, start, end,
#                                latitude, longitude):
#         """
#         REMOVE
#         """

#         ds = Dataset(product=product,
#                      subproduct=subproduct,
#                      identfile=self.keyfile)

#         ds.get_data(start=start, stop=end,
#                     latlon=[latitude, longitude])

        return ds.data

    def get_data_from_datacube_nesw(self, product, subproduct, north, east,
                                    south, west, start, end):

        with self.out:
            clear_output()
            print("Getting data...")

            ds = Dataset(product=product,
                         subproduct=subproduct,
                         identfile=self.keyfile)

            ds.get_data(start=start, stop=end,
                        region=[north, east, south, west])

            return ds.data

    def check(self, north, east, south, west, start, end):

        if str(end) < str(start):
            raise ValueError('End date should not be before start date')

        if east and west and east < west:
            raise ValueError('East value should be greater than west')

        if north and south and north < south:
            raise ValueError('North value should be greater than south')

    def color_map_nesw(self, product, subproduct, north, east, south, west,
                       date, hour):

        with self.out:
            clear_output()
            print("Getting data...")

            start = Data.combine_date_hour(self, date, hour)
            end = Data.combine_date_hour(self, date, hour)

            Data.check(self, north, east, south, west, start, end)

            list_of_results = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east, south, west, start, end)

            y = list_of_results
            y.__getitem__(subproduct).plot()
            plt.show()

    @staticmethod
    def pickle_data(filename, your_content):
        # REMOVE AFTER TESTING
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump(your_content, f)

    @staticmethod
    def load_pickle(filename):
        import pickle
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data
  

    def color_map_subtraction(self, product, subproduct, north, east, south,
                                       west, date1, date2):
        
         with self.out:
            clear_output()
            print("Getting data...")

            # Close all existing figures
            try:
                plt.close('all')
            except ValueError:
                pass

            self.check_date(product, subproduct, date1)
            self.check_date(product, subproduct, date2)
            self.check(north, east, south, west, date1, date2)
                
            list_of_results1 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, date1, date1)

            y1 = list_of_results1
    
                
            list_of_results2 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, date2, date2)
            
            y2 = list_of_results2
            
            difference = y2[subproduct][0] - y1[subproduct][0]
    
            fig, axs = plt.subplots(figsize=(7, 4))
                
            difference.plot.imshow(ax=axs) 

            # Set aspect to equal to avoid any deformation
            axs.set_aspect('equal')

            plt.tight_layout()

            # plt.show()
            plt.show(block=False)


    
    def color_map_identifying_change(self, product, subproduct, north, east,
                                     south, west, dates):
        
        with self.out:
            clear_output()
            print("Getting data...")
            
            try:
                plt.close('all')
            except ValueError:
                pass
            
            results_arr = []

            for count, date in enumerate(dates):
                self.check_date(product, subproduct, date)
                
                results = Data.get_data_from_datacube_nesw(
                        self, product, subproduct, north, east,
                        south, west, dates[count], dates[count])

                results_arr.append(results)
                
            
            
            fig, axs = plt.subplots(1, len(dates), figsize=(9, 4),
                                    sharex=True, sharey=True)
                              
            for i in range(len(dates)):
                axs[i].set_aspect('equal')
                results_arr[i][subproduct][0].plot.imshow(ax=axs[i])
               
            plt.tight_layout()
            plt.show(block=True)
            
       
    def trend_analysis(self, product, subproduct, trend, north, east, 
                       south, west, date1, date2, date3, date4):
        
        with self.out:
            clear_output()
            print("Getting data...")
            
            try:
                plt.close('all')
            except ValueError:
                pass
            
            self.check_date(product, subproduct, date1)
            self.check_date(product, subproduct, date2)
            self.check_date(product, subproduct, date3)
            self.check_date(product, subproduct, date4)
            self.check(north, east, south, west, date1, date2)
            self.check(north, east, south, west, date3, date4 )
            
            list_of_results1 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, date1, date2)

            y1 = list_of_results1
    
                
            list_of_results2 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, date3, date4)
            
            y2 = list_of_results2
               
            if trend == 'timeseries':
                pass 

            else:

                # Share axis to allow zooming on both plots simultaneously
                fig, axs = plt.subplots(1, 2, figsize=(9, 4),
                                        sharex=True, sharey=True)

                y1[subproduct].mean('time').plot.imshow(ax=axs[0])
                y2[subproduct].mean('time').plot.imshow(ax=axs[1])

                # Set aspect to equal to avoid any deformation
                axs[0].set_aspect('equal')
                axs[1].set_aspect('equal')

                plt.tight_layout()
                plt.show(block=False)

    def average_subproduct(self, product, subproduct, frequency, north, 
                           east, south, west, date1, date2):
        
        pass
    
        
        

    def color_map_nesw_compare(self, product, subproduct, north, east, south,
                               west, date1, hour1, date2, hour2):

        with self.out:
            clear_output()
            print("Getting data...")

            start1 = Data.combine_date_hour(self, date1, hour1)
            end1 = Data.combine_date_hour(self, date1, hour1)
            start2 = Data.combine_date_hour(self, date2, hour2)
            end2 = Data.combine_date_hour(self, date2, hour2)

            Data.check(self, north, east, south, west, start1, end1)
            Data.check(self, north, east, south, west, start2, end2)

            list_of_results1 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, start1, end1)

            y1 = list_of_results1

            list_of_results2 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, start2, end2)

            y2 = list_of_results2

            fig, axs = plt.subplots(1, 2, figsize=(9, 4))
            y1.__getitem__(subproduct).plot(ax=axs[0])
            y2.__getitem__(subproduct).plot(ax=axs[1])
            plt.tight_layout()
            plt.show()
    

    def color_map_nesw_compare_reduced(self, product, subproduct, north, east, south,
                                       west, date1, date2):

        # TODO 3.9: option to display or save results for UI
        with self.out:
            clear_output()
            print("Getting data...")

            # Close all existing figures
            try:
                plt.close('all')
            except ValueError:
                pass

            Data.check(self, north, east, south, west, date1, date1)
            Data.check(self, north, east, south, west, date2, date2)
            self.check_date(product, subproduct, date1)
            self.check_date(product, subproduct, date2)

            list_of_results1 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, date1, date1)

            y1 = list_of_results1

            list_of_results2 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, date2, date2)

            y2 = list_of_results2

            # Share axis to allow zooming on both plots simultaneously
            fig, axs = plt.subplots(1, 2, figsize=(9, 4),
                                    sharex=True, sharey=True)

            y1[subproduct][0].plot.imshow(ax=axs[0])
            y2[subproduct][0].plot.imshow(ax=axs[1])

            # Set aspect to equal to avoid any deformation
            axs[0].set_aspect('equal')
            axs[1].set_aspect('equal')

            plt.tight_layout()

            # plt.show()
            plt.show(block=False)

            
    def compare_rfe_skt_time(self, longitude, latitude, start, end):

        Data.check(self, None, None, None, None, start, end)

        with self.out:
            clear_output()
            print("Getting data...")

            # temperature
            list_of_results = self.get_data_from_datacube('era5', 'skt',
                                                          start, end,
                                                          latitude, longitude)
            x = list_of_results.skt - 273.15

            # rainfall
            list_of_results = self.get_data_from_datacube('tamsat', 'rfe',
                                                          start, end,
                                                          latitude, longitude)
            y = list_of_results.rfe

            fig, ax1 = plt.subplots()

            color = 'tab:red'
            ax1.set_xlabel('time')
            ax1.set_ylabel('skt', color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_title("")
            x.plot(ax=ax1, color=color)
            plt.title('rfe and skt against time')

            # instantiate a second axes that shares the same x-axis
            ax2 = ax1.twinx()
            color = 'tab:blue'
            ax2.set_ylabel('rfe', color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            y.plot(ax=ax2, color=color)
            plt.title('rfe and skt against time')

            # otherwise the right y-label is slightly clipped
            fig.tight_layout()
            plt.show()

    def compare_rainfall_products(self, latitude, longitude, start, end):

        with self.out:

            clear_output()
            print("Getting data...")

            p1 = self.get_data_from_datacube('tamsat',
                                             'rfe',
                                             np.datetime64(start),
                                             np.datetime64(end),
                                             latitude,
                                             longitude)

            p2 = self.get_data_from_datacube('chirps',
                                             'rfe',
                                             np.datetime64(start),
                                             np.datetime64(end),
                                             latitude,
                                             longitude)

            plt.figure(figsize=(8, 6))

            p1.rfe.plot(label='TAMSAT')
            p2.rfe.plot(label='CHIRPS')

            plt.legend()
            plt.show()

    def compare_temperature_subproducts(self, latitude, longitude, start, end):

        with self.out:

            clear_output()
            print("Getting data...")

            p1 = self.get_data_from_datacube('era5',
                                             'skt',
                                             np.datetime64(start),
                                             np.datetime64(end),
                                             latitude,
                                             longitude)

            p2 = self.get_data_from_datacube('era5',
                                             't2m',
                                             np.datetime64(start),
                                             np.datetime64(end),
                                             latitude,
                                             longitude)

            plt.figure(figsize=(8, 6))

            p1.rfe.plot(label='skt')
            p2.rfe.plot(label='t2m')

            plt.legend()
            plt.show()

    def compare_rainfall_years(self, product, latitude, longitude,
                               year1, year2):

        with self.out:

            clear_output()
            print("Getting data...")

            product_name = product.lower()

            y1 = self.get_data_from_datacube(
                product_name,
                'rfe',
                np.datetime64(f"{int(year1)}-01-01"),
                np.datetime64(f"{int(year1)}-12-31"),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            y2 = self.get_data_from_datacube(
                product_name,
                'rfe',
                np.datetime64(f"{int(year2)}-01-01"),
                np.datetime64(f"{int(year2)}-12-31"),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            plt.figure(figsize=(8, 6))

            y1.rfe.plot(label=int(year1))
            y2.rfe.plot(label=int(year2))

            plt.legend()
            plt.show()

    def compare_temperature_years(self, product, latitude, longitude,
                                  year1, year2):

        with self.out:

            clear_output()
            print("Getting data...")

            product_name = product.lower()

            y1 = self.get_data_from_datacube(
                product_name,
                'skt',
                np.datetime64(f"{int(year1)}-01-01"),
                np.datetime64(f"{int(year1)}-12-31"),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            y2 = self.get_data_from_datacube(
                product_name,
                'skt',
                np.datetime64(f"{int(year2)}-01-01"),
                np.datetime64(f"{int(year2)}-12-31"),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            plt.figure(figsize=(8, 6))

            y1.skt.plot(label=int(year1))
            y2.skt.plot(label=int(year2))

            plt.legend()
            plt.show()

    def data_to_csv(self, product, subproduct,
                    latitude, longitude, start, end):
        """
        TODO: REMOVE REPEATED CODE
        """
        with self.out:

            clear_output()
            print("Getting data...")

            data = self.get_data_from_datacube(product,
                                               subproduct,
                                               pd.to_datetime(start),
                                               pd.to_datetime(end),
                                               latitude,
                                               longitude)

            st = pd.to_datetime(start)
            en = pd.to_datetime(end)
            filename = f"{product}_{subproduct}_{latitude}_{longitude}" \
                       f"_{st.date()}_{en.date()}.csv"
            data.to_dataframe().to_csv(filename)
            localfile = FileLink(filename)
            display(localfile)

            plt.figure(figsize=(8, 6))
            data.__getitem__(subproduct).plot()
            plt.show()

    def data_to_csv(self, product, subproduct,
                    projection, y, x, start, end):

        with self.out:
            clear_output()
            print("Getting data...")

            lat, lon = self.reproject_coords(y, x, projection)
            data = self.get_data_from_datacube(product,
                                               subproduct,
                                               start,  # pd.to_datetime(start),
                                               end,  # pd.to_datetime(end),
                                               lat,
                                               lon,
                                               projection)
            st = pd.to_datetime(start)
            en = pd.to_datetime(end)
            filename = f"{product}_{subproduct}_{projection}_{y}_{x}" \
                       f"_{st.date()}_{en.date()}.csv"
            data.to_dataframe().to_csv(filename)
            localfile = FileLink(filename)
            display(localfile)

            plt.figure(figsize=(8, 6))
            data.__getitem__(subproduct).plot()
            plt.show()

    def plot_rainfall_year_vs_climatology(self, product, latitude, longitude,
                                          start, end):

        with self.out:

            clear_output()
            print("1/3 Getting data for request year...")

            product_name = product.lower()

            y1 = self.get_data_from_datacube(
                product_name,
                'rfe',
                np.datetime64(start),
                np.datetime64(end),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            print("2/3 Calculating climatology...")

            clim = self.get_data_from_datacube(
                product_name,
                'rfe',
                np.datetime64(f"2000-01-01"),
                np.datetime64(f"2019-12-31"),
                latitude,
                longitude)

            std = clim.groupby("time.dayofyear").std()
            mean = clim.groupby("time.dayofyear").mean()

            print("3/3 Plotting data")

            mean = mean.sel(dayofyear=slice(mean.dayofyear.values.min(),
                                            mean.dayofyear.values.max()))

            std = std.sel(dayofyear=slice(std.dayofyear.values.min(),
                                          std.dayofyear.values.max()))

            std_min = mean - std
            std_min.rfe.values[std_min.rfe.values < 0] = 0

            plt.figure(figsize=(8, 6))

            y1.rfe.plot(label="2018")

            mean.rfe.plot(label="Climatology", color='gray', alpha=0.6)
            plt.fill_between(mean.dayofyear.values,
                             (mean + std).rfe.values,
                             std_min.rfe.values,
                             color='Grey', alpha=0.3)

            plt.legend()
            plt.show()

    def calculate_degree_days(self, latitude, longitude, start, end, lower,
                              upper):

        with self.out:

            clear_output()
            print("1/3 Getting data...")

            temp = self.get_data_from_datacube(
                'era5',
                'skt',
                np.datetime64(start),
                np.datetime64(end+datetime.timedelta(hours=23)),
                latitude,
                longitude).skt - 273.15

            print("2/3 Calculating degree days...")

            temp.values[temp.values > upper] = lower
            temp.values[temp.values < lower] = lower
            temp.values = (temp.values - lower) / 24
            temp = temp.resample(time="1D").sum()

            temp.plot()
            plt.show()

    def combine_date_hour(self, date, hour):

        # to get start date and hour
        d = date.value
        x = d.strftime("%Y-%m-%d ")
        h = hour.value
        if h < 10:
            y = ("0" + str(h) + ":00:00")
        else:
            y = (str(h) + ":00:00")
        start = "\"" + x + y + "\""

        # to get end date and hour
        d = date.value
        x = d.strftime("%Y-%m-%d ")
        h = hour.value
        if h < 10:
            y = ("0" + str(h) + ":00:00")
        else:
            y = (str(h) + ":00:00")
        return "\"" + x + y + "\""

    def compare_two_locations(self, product, subproduct, lat1, lon1,
                              lat2, lon2, start_date, start_hour,
                              end_date, end_hour):

        with self.out:
            clear_output()
            print("Getting data...")

            # to get start date and hour
            start = Data.combine_date_hour(self, start_date, start_hour)

            # to get end date and hour
            end = Data.combine_date_hour(self, end_date, end_hour)

            fig, ax1 = plt.subplots(figsize=(8, 4))

            # latlon1
            list_of_results = Data.get_data_from_datacube(
                product, subproduct, start, end, lat1, lon1,)

            x = list_of_results
            x.__getitem__(subproduct).plot(label=(lat1, lon1))

            # latlon2
            list_of_results = Data.get_data_from_datacube(
                product, subproduct, start, end, lat2, lon2,)

            y = list_of_results
            y.__getitem__(subproduct).plot(label=(lat2, lon2))

            list_x = x.__getitem__(subproduct).values
            list_y = y.__getitem__(subproduct).values
            max_val = max([list_x.max(), list_y.max()]) + 2
            min_val = min([list_x.min(), list_y.min()]) - 2

            plt.title('comparing two locations')
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            ax1.set_ylim([min_val, max_val])
            fig.tight_layout()
            plt.show()

    def calculate_timesteps(self, years, period=16):
        """For Modis products, There is always a time step on 1st Jan each year
        Returns a list of all possible product dates in the years requested
        prepended with the last date in the previous year and the first date in
        the following year to allow for looking for nearest dates at the start or
        end of a year.

        years:  A list of years
        period: period of product in days
        """

        n = 366//period
        # get last date in preceeding year
        dates = [datetime.date(years[0]-1, 1, 1) + datetime.timedelta(days=n*period)]
        if dates[0].year == years[0]:  # day 366 but not a leap year
            dates = [datetime.date(years[0]-1, 1, 1) + datetime.timedelta(days=(n-1)*period)]
        for year in years:
            start = datetime.date(year, 1, 1)
            dates = dates + [start + datetime.timedelta(days=i*period) for i in range(n)]
            if dates[-1].year != year:
                # if last date was day 366 but this was not a leap year, remove date
                dates = dates[:-1]
        dates = dates + [datetime.date(years[-1]+1, 1, 1)]

        return dates

    def get_dates(self, dataset, start, end):
        # start = np.datetime64(start)
        # end = np.datetime64(end)
        first_date = dataset.first_timestep
        last_date = dataset.last_timestep
        if end < start:
            print('End date before start date.')
            raise ValueError('End date before start date.')
        if end < first_date:
            print(f'First available date {first_date}')
            raise ValueError('Requested dates outside of available dates.')
        if start > last_date:
            print(f'Last available date {last_date}')
            raise ValueError('Requested dates outside of available dates.')

        # check start date
        if start <= first_date:
            first = first_date
        else:
            timesteps = self.calculate_timesteps([start.year])
            first = self.closest_later_date(timesteps, start)
        # check end date
        if end >= last_date:
            last = last_date
        else:
            timesteps = self.calculate_timesteps([end.year])
            last = self.closest_earlier_date(timesteps, end)
        return first, last

    def closest_earlier_date(self, date_list, date):

        earlier = filter(lambda d: d <= date, date_list)
        try:
            closest = min(earlier, key=lambda d: abs(d - date))
        except ValueError:
            closest = None
        return closest

    def closest_later_date(self, date_list, date):

        earlier = filter(lambda d: d >= date, date_list)
        try:
            closest = min(earlier, key=lambda d: abs(d - date))
        except ValueError:
            closest = None
        return closest

    def check_date(self, product, subproduct, date):

        ds = Dataset(product=product,
                     subproduct=subproduct,
                     identfile=self.keyfile)

        first_date = ds.first_timestep
        last_date = ds.last_timestep
        available = True
        if np.datetime64(date) < first_date:
            print(f'{date} not available. First available date {first_date}')
            available = False
        elif np.datetime64(date) > last_date:
            print(f'{date} not available. Last available date {last_date}')
            available = False
        elif product == 'MOD13A2':
            year = date.year
            timesteps = self.calculate_timesteps([year], period=16)
            available = date in timesteps
            if not available:
                print(type(date), type(timesteps[0]))
                date1 = self.closest_earlier_date(timesteps, date)
                date2 = self.closest_later_date(timesteps, date)
                print(f'{date} not available. Nearest available dates: {date1} and {date2}')

        if not available:
            raise ValueError(f'{date} not available.')

        return available

    def reproject_coords(self, y, x, projection):

        if projection == "British National Grid":
            lat, lon = self.bng_to_latlon(y, x)
        else:
            # Assuming coords in lat lon if not BNG
            lat, lon = y, x
        return lat, lon

    def bng_to_latlon(self, northing, easting, to_latlon=True):
        """ convert British National Grid easting and northing to latitude and longitude"""
        bng_proj = Proj(
            '+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +towgs84=446.448,-125.157,542.06,0.1502,0.247,0.8421,-20.4894 +units=m +no_defs=True')
        latlon_proj = Proj(init='epsg:4326')

        # TODO: PROBLEM HERE
        lat, lon = transform(bng_proj, latlon_proj, northing, easting)

        nort, east = transform(latlon_proj, bng_proj, lat, lon)

        if to_latlon:
            return lat, lon
        else:
            return nort, east

    @staticmethod
    def shape_to_geojson(input_shp, output_geoJson):

        cmd = "ogr2ogr -f GeoJSON -t_srs crs:84 " + output_geoJson + " " + input_shp
        subprocess.call(cmd, shell=True)
