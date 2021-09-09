from __future__ import print_function
import pickle
import subprocess
import warnings
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
import pandas as pd
import osr
import sys
import pickle
sys.path.append("../../")
from IPython.display import display, clear_output
from IPython.lib.display import FileLink
from DQTools.DQTools.dataset import Dataset
from DQTools.DQTools.search import Search
from DQTools.DQTools.connect import connect

warnings.filterwarnings("ignore", category=FutureWarning)


class Data:
    """
    Data reading, analysing and plotting methods.
    """

    def __init__(self, out, keyfile=None):
        """
        :param out:                 Output() widget to capture generated output.
        :param keyfile [optional]:  user crediential file.

        :return:
        """

        self.out = out
        if keyfile is None:
            self.keyfile = os.path.join(os.path.expanduser("~"),
                                        '.assimila_dq.txt')
        else:
            self.keyfile = keyfile

    def get_data_from_datacube_latlon(self, product, subproduct, start, end,
                                      latitude, longitude):
        """
        Get a datacube dataset for a point location request.

        :param product:     the name of the datacube product
        :param subproduct:  the name of the datacube subproduct
        :param start:       the start date of the period
        :param end:         the end date of the period
        :param latitude     the latitude of the point location
        :param longitude    the longitude of the point location

        :return: xarray of datacube dataset data
        """

        with self.out:
            clear_output()
            print("Getting data...")

            ds = Dataset(product=product,
                         subproduct=subproduct,
                         identfile=self.keyfile)

            ds.get_data(start=start, stop=end,
                        latlon=[latitude, longitude])
           
            return ds.data

    def get_data_from_datacube_nesw(self, product, subproduct, north, east,
                                    south, west, start, end):
        """
        Get a datacube dataset for a region location request.

        :param product:     the name of the datacube product
        :param subproduct:  the name of the datacube subproduct
        :param north:       northern latitude
        :param east:        eatern longitude
        :param south:       southern latitude
        :param west:        western latitude
        :param start:       the start date of the period
        :param end:         the end date of the period

        :return: xarray of datacube dataset data
        """

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
        """
        Check that the north, east, south, west, start and end
        parameters given make sense.

        :param north: northern latitude
        :param east:  eatern longitude
        :param south: southern latitude
        :param west:  western latitude
        :param start: datetime object for the start date
        :param end:   datetime object for the end date

        :return:
        """

        if str(end) < str(start):
            raise ValueError('End date should not be before start date')

        if east and west and east < west:
            raise ValueError('East value should be greater than west')

        if north and south and north < south:
            raise ValueError('North value should be greater than south')

    def coord_transform_plot(self, y, subproduct, proj):
        """
        Reproject the cell coordinates so that the plot seen by the user
        has coordinate units which match their selection choice.
        
        :param y:          the DataArray who's coordinates are being transformed 
        :param subproduct: the name of the subproduct being investigated
        :proj:             the user selected projection
        
        :return y:         the reprojected DataArray
        """
        #######################
        # No conversion cases #
        #######################
        if y[subproduct].crs == "+init=epsg:4326" and proj == 'Lat/Lon':
            return y
        
        elif y[subproduct].crs[:11] == "+proj:tmerc" and proj == 'National Grid':
            return y
            
        elif y[subproduct].crs[:10] == "+proj=sinu" and proj == 'Sinusoidal':
            return y
        
        ####################
        # Conversion cases #
        ####################
        if y[subproduct].crs == "+init=epsg:4326" and proj == 'National Grid':
            conv = "latlon_to_bng"
        
        elif y[subproduct].crs[:11] == "+proj:tmerc" and proj == 'Lat/Lon':
            conv='bng_to_latlon'
        
        elif y[subproduct].crs[:10] == "+proj=sinu" and proj == 'National Grid':
            conv='sinu_to_bng'
        
        elif y[subproduct].crs[:11] == "+proj:tmerc" and proj == 'Sinusoidal':
            conv='sinu_to_bng'
            
        elif y[subproduct].crs[:10] == "+proj=sinu" and proj == 'Lat/Lon':
            conv='sinu_to_latlon'
            
        elif y[subproduct].crs == "+init=epsg:4326" and proj == 'Sinusoidal':
            conv='latlon_to_sinu'
            
            
        y["latitude"] = [self.coord_transform(0, i, conv)[1] for i in y["latitude"].data]
        y["longitude"] = [self.coord_transform(i, 0, conv)[0] for i in y["longitude"].data]
        
        return y
    
    @staticmethod
    def get_units(product, subproduct):
        """
        Get the units of a specified product/subproduct.
        
        :param product:    the name of the product
        :param subproduct: the name of the subproduct
        
        :return units:     the required unit
        """
        conn = connect.Connect(identfile='../../DQTools/DQTools/connect/.assimila_dq')
        _product = conn.get_all_table_data(tablename='product')
        product_id = _product[_product.name==product].idproduct.values[0]
        _subproduct = conn.get_all_table_data(tablename='subproduct')
        units = _subproduct[_subproduct.idproduct==product_id][_subproduct.name==subproduct].units.values[0]
        
        if units == "Kelvin":
            return "K"
        else:
            return units

    def average_subproduct(self, product, subproduct, frequency, average, north,
                               east, south, west, date1, date2, proj):
            """
            Find the average of a subproduct over an area or point over 2 given dates.
            Averaging done by area or by pixel with an averaging frequency of days/
            months/years.

            :param product:     the name of the datacube product
            :param subproduct:  the name of the datacube subproduct
            :param frequency:   the time period over which to average 
            :param north:       northern latitude
            :param east:        eatern longitude
            :param south:       southern latitude
            :param west:        western latitude
            :param date1:       the start of the analysis period
            :param date2:       the end of the analysis period

            :return fig: figure object for the plot
            """      

            def by_pixel(freq):
                """
                Average the subproduct by pixel using resampling (up and down) to find 
                the average per specified time increment ['1D', '1MS', '1YS'].
                """
                if north == south and east == west:
                    pixel_average = y[subproduct].resample(time=freq).mean('time').mean('time')
                    print(f"""
    ==================================================
    Product:    {product}
    Subproduct: {subproduct}
    Lat/Lon:    {north}/{east}
    Date 1:     {date1}
    Date 2:     {date2}
    ================================================== 
    Average = {pixel_average.data} {units}
    """)
                    return pixel_average

                else:
                    #y_reproj = self.coord_transform_plot(y, subproduct, proj)
                    fig, axs = plt.subplots(figsize=(9, 6),
                                            sharex=True, sharey=True)
                    
                    y[subproduct].resample(time=freq).mean('time').mean('time').plot.imshow(ax=axs, cbar_kwargs={"label" : str(subproduct) + " (" + str(units) + ")"})
                    
                    axs.set_aspect('equal')
                    if freq == '1D':
                        plt.title(f'average: days')
                    elif freq == '1MS':
                        plt.title(f'average: months')
                    elif freq == '1YS':
                        plt.title(f'average: years')
                    plt.tight_layout()
                    plt.show(block=False)

                    return y[subproduct].resample(time=freq).mean('time').mean('time'), fig 

            def by_area(freq):
                """
                Average the subproduct by area using resampling (up and down) to find 
                the average per specified time increment ['1D', '1MS', '1YS'].
                """
                area_average = y[subproduct].resample(time=freq).mean('time').mean(['longitude', 'latitude']).mean('time')
                print(f"""
    ==================================================
    Product:    {product}
    Subproduct: {subproduct}
    Lat/Lon:    {north}/{east}
    Date 1:     {date1}
    Date 2:     {date2}
    ================================================== 
    Average = {area_average.data} {units}
    """)
                return area_average

            with self.out:
                clear_output()

                try:
                    plt.close('all')
                except ValueError:
                    pass

                self.check_date(product, subproduct, date1)
                self.check_date(product, subproduct, date2)

                self.check(north, east, south, west, date1, date2)
                
                # Get the units of the subproduct
                units = Data.get_units(product, subproduct)
                
                if north == south and east == west:

                    list_of_results = Data.get_data_from_datacube_latlon(
                        self, product, subproduct, date1, date2, north, east)

                else:
                    list_of_results = Data.get_data_from_datacube_nesw(
                        self, product, subproduct, north, east,
                        south, west, date1, date2)

                y = list_of_results
                if frequency == 'days':
                    freq='1D'
                    if average == 'by pixel':
                        return by_pixel(freq)

                    elif average == 'by area':
                        return by_area(freq)

                elif frequency == 'months':
                    freq='1MS'
                    if average == 'by pixel':
                        return by_pixel(freq)

                    elif average == 'by area':
                        return by_area(freq)

                elif frequency == 'years':
                    freq='1YS'
                    if average == 'by pixel':
                        return by_pixel(freq)

                    elif average == 'by area':
                        return by_area(freq)

                    
    def color_map_subtraction(self, product, subproduct, north, east, south,
                              west, date1, date2):
        """
        Plot a colour map of a subproduct subtraction over 2 dates.

        :param product:     the name of the datacube product
        :param subproduct:  the name of the datacube subproduct
        :param north:       northern latitude
        :param east:        eatern longitude
        :param south:       southern latitude
        :param west:        western latitude
        :param date1:       the first date (being subtracted from)
        :param date2:       the second date (being subtracted)

        :return fig: figure object for the plot
        """
        with self.out:
            clear_output()

            # Close all existing figures
            try:
                plt.close('all')
            except ValueError:
                pass

            self.check_date(product, subproduct, date1)
            self.check_date(product, subproduct, date2)
            self.check(north, east, south, west, date1, date2)
            
            # Get the units of the subproduct
            units = Data.get_units(product, subproduct)
                
            if north == south and east == west:
                list_of_results1 = Data.get_data_from_datacube_latlon(
                    self, product, subproduct, date1, date1, north, east)

                y1 = list_of_results1

                list_of_results2 = Data.get_data_from_datacube_latlon(
                    self, product, subproduct, date2, date2, north, east)

                y2 = list_of_results2

                difference = y2[subproduct][0] - y1[subproduct][0]

                print(f"""
==========================================================
Product:    {product}
Subproduct: {subproduct}
Lat/Lon:    {north}/{east}
==========================================================
Change was {difference.data} {units} from {date1} to {date2}.""")
                
                return difference
                
            else:
                list_of_results1 = Data.get_data_from_datacube_nesw(
                    self, product, subproduct, north, east,
                    south, west, date1, date1)

                y1 = list_of_results1

                list_of_results2 = Data.get_data_from_datacube_nesw(
                    self, product, subproduct, north, east,
                    south, west, date2, date2)

                y2 = list_of_results2

                difference = y2[subproduct][0] - y1[subproduct][0]

                fig, axs = plt.subplots(figsize=(9, 6))
             
                difference.plot.imshow(ax=axs, cbar_kwargs={"label" : str(subproduct) + " (" + str(units) + ")"})

                # Set aspect to equal to avoid any deformation
                axs.set_aspect('equal')

                plt.tight_layout()

                # plt.show()
                plt.show(block=False)

                return y2[subproduct][0] - y1[subproduct][0], fig


    def trend_analysis(self, product, subproduct, north, east,
                       south, west, date1, date2, date3, date4, trends):
        """
        Plot a timeseries of points if a point location is given and a
        colour map if an area is given, identifying trends in subproducts
        over 2 defined periods.


        :param product:     the name of the datacube product
        :param subproduct:  the name of the datacube subproduct
        :param north:       northern latitude
        :param east:        eatern longitude
        :param south:       southern latitude
        :param west:        western latitude
        :param date1:       the start of the first analysis period
        :param date2:       the end of the first analysis period
        :param date3:       the start of the second analysis period
        :param date4:       the end of the second analysis period

        :return fig: figure object for the plot
        """

        with self.out:
            clear_output()

            try:
                plt.close('all')
            except ValueError:
                pass

            self.check_date(product, subproduct, date1)
            self.check_date(product, subproduct, date2)
            self.check_date(product, subproduct, date3)
            self.check_date(product, subproduct, date4)
            self.check(north, east, south, west, date1, date2)
            self.check(north, east, south, west, date3, date4)
            
            # Get the units of the subproduct to display on the colorbar
            units = Data.get_units(product, subproduct)
            
            if north == south and east == west:

                list_of_results1 = Data.get_data_from_datacube_latlon(
                    self, product, subproduct, date1, date2, north, east)

                y1 = list_of_results1

                list_of_results2 = Data.get_data_from_datacube_latlon(
                    self, product, subproduct, date3, date4, north, east)

                y2 = list_of_results2
                
                if trends == 'overlaid':
                    fig = plt.figure(figsize=(15, 4))
                    
                    axs0 = fig.add_subplot(111)
                    axs1 = axs0.twiny()
                    
                    y1[subproduct].plot(ax=axs0, label='Period 1')
                    y2[subproduct].plot(ax=axs1, color='orange', label='Period 2')
                    
                    axs0.set_xlabel('Period 1')
                    axs1.set_xlabel('Period 2')
                    
                    axs0.set_ylabel(str(subproduct) + ' (' + str(units) + ')')
                    
                    fig.legend()
                    plt.tight_layout()
                    plt.show(block=False)
                    
                elif trends == 'side-by-side':
                    fig, axs = plt.subplots(1, 2, figsize=(15, 4))

                    y1[subproduct].plot(ax=axs[0])
                    y2[subproduct].plot(ax=axs[1])

                    axs[0].set_ylabel(str(subproduct) + ' (' + str(units) + ')')
                    axs[1].set_ylabel(str(subproduct) + ' (' + str(units) + ')')
                    
                    plt.tight_layout()
                    plt.show(block=False)

                return y1[subproduct], y2[subproduct], fig

            else:

                list_of_results1 = Data.get_data_from_datacube_nesw(
                    self, product, subproduct, north, east,
                    south, west, date1, date2)

                y1 = list_of_results1

                list_of_results2 = Data.get_data_from_datacube_nesw(
                    self, product, subproduct, north, east,
                    south, west, date3, date4)

                y2 = list_of_results2

                # Share axis to allow zooming on both plots simultaneously
                fig, axs = plt.subplots(1, 2, figsize=(15, 4),
                                        sharex=True, sharey=True)

                y1[subproduct].mean('time').plot.imshow(ax=axs[0], cbar_kwargs={"label" : str(subproduct) + " (" + str(units) + ")"})
                y2[subproduct].mean('time').plot.imshow(ax=axs[1], cbar_kwargs={"label" : str(subproduct) + " (" + str(units) + ")"})

                # Set aspect to equal to avoid any deformation
                axs[0].set_aspect('equal')
                axs[1].set_aspect('equal')

                axs[0].set_title(date1)
                axs[1].set_title(date2)

                plt.tight_layout()
                plt.show(block=False)

                return y1[subproduct].mean('time'), y2[subproduct].mean('time'), fig


    def color_map_identifying_change(self, product1, subproduct1, product2, subproduct2, 
                                     north, east, south, west, dates):
        
        """
        Plot a colour maps of a subproduct comparing different dates.

        :param product1:     the name of the datacube product1
        :param subproduct1:  the name of the datacube subproduct1
        :param
        :param
        :param north:       northern latitude
        :param east:        eatern longitude
        :param south:       southern latitude
        :param west:        western latitude
        :param dates:       list of dates which will be displayed

        :return fig: figure object for the plot
        """

        with self.out:
            clear_output()

            try:
                plt.close('all')
            except ValueError:
                pass

            results_arr1 = []
            results_arr2 = []

            # Get the units of the subproduct to display on the colorbar
            units1 = Data.get_units(product1, subproduct1)
            units2 = Data.get_units(product2, subproduct2)
            
            for count, date in enumerate(dates):
                self.check_date(product1, subproduct1, date)
                self.check_date(product2, subproduct2, date)
                
                if north == south and east == west:
                    results1 = Data.get_data_from_datacube_latlon(
                        self, product1, subproduct1, dates[count], dates[count], north, east)
                    
                    results2 = Data.get_data_from_datacube_latlon(
                        self, product2, subproduct2, dates[count], dates[count], north, east)

                else:
                    results1 = Data.get_data_from_datacube_nesw(
                        self, product1, subproduct1, north, east,
                        south, west, dates[count], dates[count])
                    
                    results2 = Data.get_data_from_datacube_nesw(
                        self, product2, subproduct2, north, east,
                        south, west, dates[count], dates[count])

                results_arr1.append(results1)
                results_arr2.append(results2)

            if north == south and east == west:
                print(f"""
==================================================
Product:    {product1}
Subproduct: {subproduct1}
Lat/Lon:    {north}/{east}
================================================== """)
                for count, date in enumerate(dates):
                    print(f"""
{results_arr1[count][subproduct1][0].data} {units1} for {date}""")
            
                print(f"""
==================================================
Product:    {product2}
Subproduct: {subproduct2}
Lat/Lon:    {north}/{east}
================================================== """)
                for count, date in enumerate(dates):
                    print(f"""
{results_arr2[count][subproduct2][0].data} {units2} for {date}""")
                
                return results_arr1, results_arr2 
            
            else:

                fig1, axs1 = plt.subplots(1, len(dates), figsize=(15, 4),
                                        sharex=True, sharey=True)
                
                fig2, axs2 = plt.subplots(1, len(dates), figsize=(15, 4),
                                        sharex=True, sharey=True)

                for i in range(len(dates)):
                    axs1[i].set_aspect('equal')
                    results_arr1[i][subproduct1][0].plot.imshow(ax=axs1[i], cbar_kwargs={"label" : str(subproduct1) + " (" + str(units1) + ")"})

                    axs2[i].set_aspect('equal')
                    results_arr2[i][subproduct2][0].plot.imshow(ax=axs2[i], cbar_kwargs={"label" : str(subproduct1) + " (" + str(units2) + ")"})

                fig1.tight_layout()
                fig1.show()
                
                fig2.tight_layout()
                fig2.show()

                return results_arr1, fig1, results_arr2, fig2   

            
    def color_map_nesw(self, product, subproduct, north, east, south, west,
                       date, hour):
        """
        Plot a colour map of the subproduct over a bounding box.

        :param product:     the name of the datacube product
        :param subproduct:  the name of the datacube subproduct
        :param north:       northern latitude
        :param east:        eatern longitude
        :param south:       southern latitude
        :param west:        western latitude
        :param date:        the date of the analysis
        :param hour:        the hour of the analysis

        :return:
        """
        with self.out:
            clear_output()
            print("Getting data...")

            start = Data.combine_date_hour(self, date, hour)
            end = Data.combine_date_hour(self, date, hour)
            
            
            Data.check(self, north, east, south, west, start, end)
            self.check_date(product, subproduct, date)
            
            list_of_results = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east, south, west, start, end)

            y = list_of_results
            y.__getitem__(subproduct).plot(figsize=(10,8))
            plt.show()
            
            
    def color_map_nesw_compare(self, product, subproduct, north, east, south,
                               west, date1, hour1, date2, hour2):
        """
        Data function for notebook compare_bounding_box_for_2_time_steps.ipynb
        """

        with self.out:
            clear_output()
            FORMAT = '%Y-%m-%d %H:%M:%S'
            start1 = Data.combine_date_hour(self, date1, hour1)
            end1 = Data.combine_date_hour(self, date1, hour1)
            start2 = Data.combine_date_hour(self, date2, hour2)
            end2 = Data.combine_date_hour(self, date2, hour2)
            
            Data.check(self, north, east, south, west, start1, end1)
            Data.check(self, north, east, south, west, start2, end2)
            
            self.check_date(product, subproduct, datetime.datetime.strptime(start1, "%Y-%m-%d %H:%M:%S"))
            self.check_date(product, subproduct, datetime.datetime.strptime(start2, "%Y-%m-%d %H:%M:%S"))

            list_of_results1 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, start1, end1)

            y1 = list_of_results1

            list_of_results2 = Data.get_data_from_datacube_nesw(
                self, product, subproduct, north, east,
                south, west, start2, end2)

            y2 = list_of_results2
            
            fig, axs = plt.subplots(1, 2, figsize=(16, 8))
            y1.__getitem__(subproduct).plot(ax=axs[0])
            y2.__getitem__(subproduct).plot(ax=axs[1])
            plt.tight_layout()
            plt.show()

            return fig

    def color_map_nesw_compare_reduced(self, product, subproduct, north, east, south,
                                       west, date1, date2):

        with self.out:
            clear_output()

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
            plt.show()

            return fig

    def compare_rfe_skt_time(self, longitude, latitude, start, end):

        Data.check(self, None, None, None, None, start, end)

        with self.out:
            clear_output()
            print("Getting data...")

            # temperature
            list_of_results = self.get_data_from_datacube_latlon('era5', 'skt',
                                                          start, end,
                                                          latitude, longitude)
            x = list_of_results.skt - 273.15

            # rainfall
            list_of_results = self.get_data_from_datacube_latlon('tamsat', 'rfe',
                                                          start, end,
                                                          latitude, longitude)
            y = list_of_results.rfe

            fig, ax1 = plt.subplots(figsize=(16, 8))

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
            
            return fig

    def compare_rainfall_products(self, latitude, longitude, start, end):

        with self.out:

            clear_output()
            print("Getting data...")

            data1 = self.get_data_from_datacube_latlon('tamsat',
                                                     'rfe',
                                                     np.datetime64(start),
                                                     np.datetime64(end),
                                                     latitude,
                                                     longitude)

            data2 = self.get_data_from_datacube_latlon('chirps',
                                                     'rfe',
                                                     np.datetime64(start),
                                                     np.datetime64(end),
                                                     latitude,
                                                     longitude)

            plt.figure(figsize=(16, 8))

            data1.rfe.plot(label='TAMSAT')
            data2.rfe.plot(label='CHIRPS')
            
            plt.tight_layout()
            plt.legend()
            plt.show()
            
            filename1 = f"tamsat_rfe_{latitude}_{longitude}" \
                       f"_{start}_{end}.csv"
            
            filename2 = f"chirps_rfe_{latitude}_{longitude}" \
                       f"_{start}_{end}.csv"
            
            data1.to_dataframe().to_csv(filename1)
            data2.to_dataframe().to_csv(filename2)
            
            display(FileLink(filename1))
            display(FileLink(filename2))

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

            y1 = self.get_data_from_datacube_latlon(
                product_name,
                'rfe',
                np.datetime64(f"{int(year1)}-01-01"),
                np.datetime64(f"{int(year1)}-12-31"),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            y2 = self.get_data_from_datacube_latlon(
                product_name,
                'rfe',
                np.datetime64(f"{int(year2)}-01-01"),
                np.datetime64(f"{int(year2)}-12-31"),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            plt.figure(figsize=(16, 10))

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

    def data_to_csv(self, product1, subproduct1,
                    latitude, longitude, start, end, product2=None, subproduct2=None):
        """
        Extract a timeseries for a product/subproduct with start/end.
        
        :param product:     the name of the datacube product
        :param subproduct:  the name of the datacube subproduct
        :param latitude     the latitude of the point location
        :param longitude    the longitude of the point location
        :param start:       the start date of the period
        :param end:         the end date of the period

        :return:
        """
        with self.out:
            clear_output()
            
            self.check_date(product1, subproduct1, start)
            self.check_date(product1, subproduct1, end)
            data = self.get_data_from_datacube_latlon(product1,
                                                       subproduct1,
                                                       pd.to_datetime(start),
                                                       pd.to_datetime(end),
                                                       latitude,
                                                       longitude)
            
            st = pd.to_datetime(start)
            en = pd.to_datetime(end)
            
            filename1 = f"{product1}_{subproduct1}_{latitude}_{longitude}" \
                       f"_{st.date()}_{en.date()}.csv"
            data.to_dataframe().to_csv(filename1)
            localfile1 = FileLink(filename1)
            
            fig, ax1 = plt.subplots(figsize=(18, 8))
            ln1 = data.__getitem__(subproduct1).plot(ax=ax1, label=subproduct1)
            
            if product2 is not None and subproduct2 is not None:
                self.check_date(product2, subproduct2, start)
                self.check_date(product2, subproduct2, end)
                data = self.get_data_from_datacube_latlon(product2,
                                                           subproduct2,
                                                           pd.to_datetime(start),
                                                           pd.to_datetime(end),
                                                           latitude,
                                                           longitude)
                
                filename2 = f"{product2}_{subproduct2}_{latitude}_{longitude}" \
                           f"_{st.date()}_{en.date()}.csv"
                data.to_dataframe().to_csv(filename2)
                localfile2 = FileLink(filename2)
                display(localfile2) 
                
                ax2 = ax1.twinx()
                ln2 = data.__getitem__(subproduct2).plot(ax=ax2, color='red', label=subproduct2) 
            
                lns = ln1 + ln2
            
                labs = [l.get_label() for l in lns]
                ax1.legend(lns, labs, loc=0)

            display(localfile1)

            plt.show()
            
    def data_to_csv(self, product, subproduct,
                    projection, y, x, start, end):

        with self.out:
            clear_output()
            print("Getting data...")
            data = self.get_data_from_datacube_latlon(product,
                                               subproduct,
                                               start,
                                               end, 
                                               y,
                                               x)
            st = pd.to_datetime(start)
            en = pd.to_datetime(end)
            filename = f"{product}_{subproduct}_{y}_{x}" \
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

            y1 = self.get_data_from_datacube_latlon(
                product_name,
                'rfe',
                np.datetime64(start),
                np.datetime64(end),
                latitude,
                longitude).groupby('time.dayofyear').mean()

            print("2/3 Calculating climatology...")

            clim = self.get_data_from_datacube_latlon(
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

            plt.figure(figsize=(18, 8))

            y1.rfe.plot(label="2018")

            mean.rfe.plot(label="20 year climatology", color='gray', alpha=0.6)
            plt.fill_between(mean.dayofyear.values,
                             (mean + std).rfe.values,
                             std_min.rfe.values,
                             color='Grey', alpha=0.3)

            plt.legend()
            plt.show()
     
    @staticmethod
    def complete_days_idx(timeseries):
        """
        Use the time dimension of an array to return the indices of all days
        with 24 timesteps.

        :param timeseries: xarray of time data.
        
        :return timeseries of data with days which contain a full 24 hours.
        :return:
        """
        # Resample the time series and count how many time steps in each day
        timesteps_daily = timeseries.resample(time='1D').count().values

        # Use this to generate a list which is equal in length to
        # timeseries, and where each value is the number of hours in the
        # day for that particular index
        day_hours = np.concatenate([np.ones(t) * t for t in timesteps_daily])

        # Return all indices where number of hours in the day == 24
        return np.where(day_hours == 24)[0]
    
    
    def calculate_degree_days(self, latitude, longitude, start, end, lower,
                              upper, temp_metric, cutoff):
        """
        Calculate the number of degree days at a location between 2 dates with
        a user specified cut-off type and temperature thresholds.
        
        :param latitude     the latitude of the point location
        :param longitude    the longitude of the point location
        :param start:       the start date of the period
        :param end:         the end date of the period
        :param upper:       the upper temperature threshold
        :param lower:       the lower temperature threshold
        :param temp_metric: the temperature measurement to use [subproduct]
        :param cutoff:      the calculation cutoff type [vertical/horizontal]
        
        :return:
        """

        with self.out:
            # Convert datetime to date unless already date.
            try:
                start_date = start.date()
            except:
                start_date = start
            
            try: 
                end_date = end.date()
            except: 
                end_date = end
            
            # Number of days 
            days = end_date-start_date
            
            clear_output()
            
            if temp_metric == 'skt':
                temp = self.get_data_from_datacube_latlon(
                            product='era5',
                            subproduct='skt',
                            start=np.datetime64(start),
                            end=np.datetime64(end+datetime.timedelta(hours=23)),
                            latitude=latitude,
                            longitude=longitude).skt - 273.15
            
            elif temp_metric == 't2m':
                temp = self.get_data_from_datacube_latlon(
                            product='era5',
                            subproduct='t2m',
                            start=np.datetime64(start),
                            end=np.datetime64(end+datetime.timedelta(hours=23)),
                            latitude=latitude,
                            longitude=longitude).t2m - 273.15
            
            temp_orig = temp.copy(deep=True)
            if cutoff == 'Vertical':
            # Set temperatures higher than upper threshold to lower threshold
            # to address pest mortality
                temp.values[temp.values > upper] = lower
                temp.values[temp.values < lower] = lower
                
            if cutoff == 'Horizontal':
            # Set temperatures higher than upper threshold to upper threshold
            # to address pest mortality
                temp.values[temp.values > upper] = upper
                temp.values[temp.values < lower] = lower
                
            # Calculate degree day hours
            temp.values = (temp.values - lower) / 24
            
            # Remove any days with fewer than 24 time steps
            temp = temp.isel(time=self.complete_days_idx(temp.time))
            
            # Take daily sum 
            temp = temp.resample(time="1D").sum()

            # Plot
            fig, axs = plt.subplots(2, 1, figsize=(16, 10))
            
            temp.plot(ax=axs[0], label='degree days')
            
            temp_orig.plot(ax=axs[1], label='temperature')
            
            if cutoff == 'Vertical':
                axs[1].fill_between(temp_orig.time.data, lower, temp_orig.data, 
                                    where=(temp_orig.data>=lower)&(temp_orig.data<=upper), 
                                    facecolor='green', interpolate=True, alpha=0.3)
                
            elif cutoff == 'Horizontal':
                axs[1].fill_between(temp_orig.time.data, lower, temp_orig.data, 
                                    where=temp_orig.data>=lower, 
                                    facecolor='green', interpolate=True, alpha=0.3)

                axs[1].fill_between(temp_orig.time.data, upper, temp_orig.data, 
                        where=temp_orig.data>=upper, 
                        facecolor='white', interpolate=True, alpha=1)
            
            axs[1].axhline(upper, color='red', linestyle='--', label='upper threshold')
            axs[1].axhline(lower, color='blue', linestyle='--', label='lower threshold')

            
            axs[0].set_ylabel('degree days')
            
            if temp_metric == 'skt':
                axs[1].set_ylabel('skt ($^\circ$C)')
            elif temp_metric == 't2m':
                axs[1].set_ylabel('t2m ($^\circ$C)')
            plt.legend()
            plt.tight_layout()
            plt.show()
            print("""
=========================================
{:.2f} degree days occurred over {} days
=========================================
""".format(temp.data.sum(), days.days))
            
            temp.rename("degree days")
            filename = f"degree_day_{latitude}_{longitude}" \
                       f"_{start}_{end}_{lower}_{upper}.csv"
            temp.to_dataframe().to_csv(filename)
            display(FileLink(filename))

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
        return str(x) + str(y)
        #return "\"" + x + y + "\""

    def compare_two_locations(self, product, subproduct, lat1, lon1,
                              lat2, lon2, start_date, start_hour,
                              end_date, end_hour):

        with self.out:
            clear_output()
            print("Getting data...")
            
            # check if dates availible # TODO: include hour check
            self.check_date(product, subproduct, start_date)
            self.check_date(product, subproduct, end_date)
            
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
        """
        For Modis products, There is always a time step on 1st Jan each year
        Returns a list of all possible product dates in the years requested
        prepended with the last date in the previous year and the first date in
        the following year to allow for looking for nearest dates at the start or
        end of a year.

        :param years:             A list of years
        :param period [optional]: period of product in days
        
        :return dates:            A list of dates
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
        """
        Check whether the requested subproduct date is available. If so, return 
        True, if not, return False and display the closest earlier and later datetimes.
        
        :param product:    the name of the requested product
        :param subproduct: the name of the requested subproduct
        
        :return available: True/False if the requested date is available or not.
        """

        ds = Dataset(product=product,
                     subproduct=subproduct,
                     identfile=self.keyfile)

        first_date = ds.first_timestep
        last_date = ds.last_timestep
        available = True
        
        if not isinstance(date, datetime.date):
            date = date.value

        if np.datetime64(date) < first_date:
            print(f'{date} not available. First available date {first_date}')
            available = False

        if np.datetime64(date) > last_date:
            print(f'{date} not available. Last available date {last_date}')
            available = False
  
        if product == 'MOD13A2':
            year = date.year
            timesteps = self.calculate_timesteps([year], period=16)
            available = date in timesteps
            if not available:
                print(type(date), type(timesteps[0]))
                date1 = self.closest_earlier_date(timesteps, date)
                date2 = self.closest_later_date(timesteps, date)
                print(f'{date} not available. Nearest available dates: {date1} and {date2}')
        
#         # If date not available (wrong frequency), try to find a date before and after.
#         if ds.get_data(start=date, stop=date) is None:
#             for i in range(400):
#                 if ds.get_data(start=date+datetime.timedelta(hours=i),
#                                stop=date+datetime.timedelta(hours=i)) is None:
#                     continue
#                 else:
#                     date1 = date+datetime.timedelta(hours=i)
#                     break
#             for i in range(400):
#                 if ds.get_data(start=date-datetime.timedelta(hours=i),
#                                stop=date-datetime.timedelta(hours=i)) is None:
#                     continue
#                 else:
#                     date2 = date+datetime.timedelta(hours=i)
#                     break
            
#             print(f'{date} not available. Nearest available dates {date1} and {date2}')
#             available = False
        
        if not available:
            raise ValueError(f'{date} not available.')
                
        return available

    def reproject_coords(self, x, y, projection):
        """
        Coords must be reprojected to WSG84 before being passed to DataCube.

        :param x:           the x-coordinate in the respective base
        :param y:           the y-cooordinate in the respective base
        :param projection:  the coordinate projection of x and y

        :return x, y:       reprojected x, y coordinates in WGS84 base
        """
        if projection == "Lat/Lon":
            return x, y

        elif projection == "National Grid":
            x, y = self.coord_transform(x, y, conv='bng_to_latlon')
            return x, y

        elif projection == 'Sinusoidal':
            x, y = self.coord_transform(x, y, conv='sinu_to_latlon')
            return x, y

    def coord_transform(self, x, y, conv):
        """
        Convert a given set of coordinates between 3 coordinate systems: WGS84,
        British National Grid and Sinusoidal.

        :param x:     the x-coordinate in the respective base
        :param y:     the y-coordinate in the respective base

        :param: conv: the conversion required: ['bng_to_latlon'
                                                'latlon_to_bng',
                                                'bng_to_sinu',
                                                'sinu_to_bng',
                                                'latlon_to_sinu',
                                                'sinu_to_latlon']

        :return x, y:  reprojected x, y coordinates in the required base
        """

        # Sinusoidal definition
        # from https://spatialreference.org/ref/sr-org/6842/
        # It fully match with the metadata in the MODIS products
        sinusoidal_srs = (f'+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 '
                          f'+b=6371007.181 +units=m +no_defs ')

        # British National Grid (BNG) definition
        # from https://spatialreference.org/ref/epsg/osgb-1936-british-national-grid/
        # User should pass those parameters?
        bng_srs = (f' +proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 '
                   f' +x_0=400000 +y_0=-100000 +ellps=airy +datum=OSGB36 '
                   f' +units=m +no_defs ')

        # Sinu spatial reference system
        sinu = osr.SpatialReference()
        sinu.ImportFromProj4(sinusoidal_srs)

        # BNG spatial reference system
        bng = osr.SpatialReference()
        bng.ImportFromProj4(bng_srs)

        # lat/lon spatial reference system
        latlon = osr.SpatialReference()
        latlon.ImportFromEPSG(4326)
        
        if conv is None:
            return x, y

        elif conv == 'bng_to_latlon':
            transform = osr.CoordinateTransformation(bng, latlon)
            x, y, z = transform.TransformPoint(x, y)
            return round(x, 6), round(y, 6)

        elif conv == 'latlon_to_bng':
            transform = osr.CoordinateTransformation(latlon, bng)
            x, y, z = transform.TransformPoint(x, y)
            return round(x, 6), round(y, 6)

        elif conv == 'bng_to_sinu':
            transform = osr.CoordinateTransformation(bng, sinu)
            x, y, z = transform.TransformPoint(x, y)
            return round(x, 6), round(y, 6)

        elif conv == 'sinu_to_bng':
            transform = osr.CoordinateTransformation(sinu, bng)
            x, y, z = transform.TransformPoint(x, y)
            return x, y

        elif conv == 'latlon_to_sinu':
            transform = osr.CoordinateTransformation(latlon, sinu)
            x, y, z = transform.TransformPoint(x, y)
            return round(x, 6), round(y, 6)

        elif conv == 'sinu_to_latlon':
            transform = osr.CoordinateTransformation(sinu, latlon)
            x, y, z = transform.TransformPoint(x, y)
            return round(x, 6), round(y, 6)
        

    def check_coords(self, north, east, south, west, projection):
        """
        When drawing onto the map make sure the correct CRS choice is
        displayed in the NESW boxes.

        :param north:        northern latitude in original CRS
        :param east:         eatern longitude in original CRS
        :param south:        southern latitude in original CRS
        :param west:         western latitude in original CRS
        :param projection:   required projection to be displayed on the UI

        :return north, east,
                south, west: coordinates after reprojection to
                                          required CRS.
        """
        if projection == 'Lat/Lon':
            return north, east, south, west

        if projection == 'National Grid':
            x1, y1 = self.coord_transform(x=east, y=north, conv='latlon_to_bng')
            x2, y2 = self.coord_transform(x=west, y=south, conv='latlon_to_bng')
            north, east, south, west = y1, x1, y2, x2
            return north, east, south, west

        if projection == 'Sinusoidal':
            x1, y1 = self.coord_transform(x=east, y=north, conv='latlon_to_sinu')
            x2, y2 = self.coord_transform(x=west, y=south, conv='latlon_to_sinu')
            north, east, south, west = y1, x1, y2, x2
            return north, east, south, west
        
    @staticmethod
    def get_gdalogr2ogr_path():
        """
        Method to return the conda path for the gdalogr2ogr bin given the
        activated environment for the current python run.
        
        :return: Full path of ogr2ogr bin
        """
        conda_prefix = os.environ['CONDA_PREFIX']
        gdal_bin_path = os.path.join(conda_prefix, 'bin')
        return os.path.join(gdal_bin_path, 'ogr2ogr')


    @staticmethod
    def shape_to_geojson(input_shp, output_geoJson):
        """
        Use GDAL to convert shapefiles into geojsons.

        :param input_shp:      the name of the read-in shapefiles
        :param output_geoJson: the desired name of the converted file

        :return:
        """
        path = Data.get_gdalogr2ogr_path()
        cmd = path + " -f GeoJSON -t_srs crs:84 " + output_geoJson + " " + input_shp
        subprocess.call(cmd, shell=True)
        
        
    @staticmethod
    def geojson_to_shape(input_geojson, output_shp):
        cmd = "ogr2ogr -nlt POLYGON -skipfailures " + output_shp + " " + input_geojson + "OGRGeoJSON"
        subprocess.call(cmd, shell=True)
    
    
    @staticmethod
    def pickle_data(filename, your_content):
        """
        Convert the a dataset into a pickle file which is
        saved an allows fast access to predefined DataCube data.
        
        :param filename:     name of pickle file to be saved
        :param your_content: DataCube dataset to be pickled.
        
        :return:
        """
        with open(filename, 'wb') as f:
            pickle.dump(your_content, f)

    @staticmethod
    def load_pickle(filename):
        """
        Load a pickle file and return the contents to be used.
        
        :param filename: filename/path of .pickle file to be read
        
        :return data:    unpickled file back to it's original format
        """
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data
    
    
