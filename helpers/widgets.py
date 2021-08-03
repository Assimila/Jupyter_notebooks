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
from ipywidgets import HBox, VBox, Box
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

import sys
sys.path.append("..")

warnings.filterwarnings("ignore", category=FutureWarning)


class Widgets:
    """
    UI widget related functions.
    """

    def __init__(self, width=None, height=None):

        self.search = Search()
        self.item_layout_user = widgets.Layout(height=height, width=width)

#         self.item_layout = widgets.Layout(height='30px', width='250px')
#         self.item_layout_subproduct1 = widgets.Layout(height='30px', width='250px')
#         self.item_layout_subproduct2 = widgets.Layout(height='30px', width='250px')
#         self.item_layout_radio = widgets.Layout(height='70px', width='250px')
#         self.item_layout_loc = widgets.Layout(height='30px', width='100px', align_items='center')

        self.item_layout = widgets.Layout(width='auto', height='auto')
        self.item_layout_subproduct1 = widgets.Layout(width='auto', height='auto')
        self.item_layout_subproduct2 = widgets.Layout(width='auto', height='auto')
        self.item_layout_radio = widgets.Layout(width='auto', height='auto')
        self.item_layout_loc = widgets.Layout(width='auto', height='auto')
        self.carousel_layout = widgets.Layout(overflow='scroll hidden',
                                              width='500px',
                                              height='60px',
                                              flex_flow='row',
                                              display='flex')
        self.save_layout = widgets.Layout(width='auto', height='auto')

    def get_lat_lon_widgets(self):
        """
        call the latitude() and longitde() methods which return BoundedFloatText widgets.
        """
        return self.latitude(), self.longitude()

    def get_product_widgets(self):
        """
        call the product() method, returning the relevant product list widget.
        """
        return self.product()

    def longitude(self):

        return widgets.BoundedFloatText(value=7.5,
                                        min=-180,
                                        max=180.0,
                                        step=0.0001,
                                        description='Longitude (x):',
                                        disabled=False,
                                        layout=self.item_layout)

    def latitude(self):

        return widgets.BoundedFloatText(value=7.5,
                                        min=-90.0,
                                        max=90.0,
                                        step=0.0001,
                                        description='Latitude (y):',
                                        disabled=False,
                                        layout=self.item_layout)

    def get_point(self, value, description):
        return widgets.BoundedFloatText(value=value,
                                        min=-180,
                                        max=180,
                                        description=description,
                                        layout=self.item_layout,
                                        disabled=False,
                                        readout=False,
                                        readout_format='d')

    def product(self, description, peat=True):

        if peat:
            projection_list = [' ', 'MOD11A1', 'MOD13A2', 'MCD43A3', 'era5']
            return widgets.Dropdown(
                options=projection_list,
                description=description,
                layout=self.item_layout,
                disabled=False, )
        else:
            return widgets.Dropdown(
                options=self.search.products().name.tolist(),
                description="Product:",
                layout=self.item_layout,
                disabled=False, )

    def subproduct(self, description, layout):

        if layout == 'subproduct1':
            return widgets.Dropdown(description=description,
                                    layout=self.item_layout_subproduct1)
        elif layout == 'subproduct2':
            return widgets.Dropdown(description=description,
                                    layout=self.item_layout_subproduct2)

    def projection(self):

        projection_list = ['WGS84', 'BNG', 'Sinusoidal']
        return widgets.RadioButtons(
            options=projection_list,
            description='CRS:',
            layout=self.item_layout_radio,
            disabled=False)

    def operation(self):
        return widgets.Dropdown(options=[" ",
                                         "Average of one sub-product",
                                         "Subtraction of one sub-product",
                                         "Trend analysis for one sub-product",
                                         "Identifying change"],
                                description="Operation:",
                                layout=self.item_layout)

    def get_projection_widgets(self):
        return self.projection()

    def upload_file(self):

        return widgets.FileUpload(description="Shapefile",
                                  accept='.shp, .shx, .prj, .dbf, .geojson',
                                  multiple=True)

    def average(self):

        return widgets.Dropdown(options = [' ', 'by pixel', 'by area'],
                                description="Average",
                                placeholder='Select averaging method',
                                disabled = True)

    def trends(self):

        return widgets.Dropdown(options = [' ', 'timeseries', 'area plot'],
                                description="Trends",
                                placeholder='Select plot type',
                                disabled = True)

    def frequency(self):

        return widgets.Dropdown(options = [' ', 2, 3, 4, 5],
                                description="Frequency",
                                placeholder = 'Select analysis frequency',
                                disabled=True)
    
    def date_carousel(self):
        
        items = []#[self.get_date(value=datetime.date(2018,1,1), description=f'Date {i+1}:') for i in range(n)]
        carousel = widgets.Box(children=items, layout = self.carousel_layout)
        return carousel
    
    
    def save_format(self):
        # csv of netCDF is timeseries
        # netCDF or shp if area
        
        return widgets.Dropdown(description='Save Format',
                               disabled=True,
                               layout = self.save_layout)
            

    def rainfall_products(self):

        return widgets.Dropdown(options=['TAMSAT', 'CHIRPS', 'GPM'],
                                description='Product:',
                                layout=self.item_layout,
                                disabled=False, )

    def temperature_products(self):

        return widgets.Dropdown(options=['skt'],
                                description='Product:',
                                layout=self.item_layout,
                                disabled=False, )

    def get_year_widgets(self):

        y1 = widgets.BoundedFloatText(value=2018, min=2000, max=2019, step=1,
                                      description='Year 1 :', disabled=False,
                                      layout=self.item_layout)

        y2 = widgets.BoundedFloatText(value=2019, min=2000, max=2019, step=1,
                                      description='Year 2 :', disabled=False,
                                      layout=self.item_layout)

        return y1, y2

    def get_date(self, value, description):

        return widgets.DatePicker(description=description,
                                  layout=self.item_layout,
                                  value=value,
                                  disabled=False)

    def get_hour(self, value, description):

        return widgets.IntSlider(description=description,
                                 layout=self.item_layout,
                                 value=value,
                                 disabled=False,
                                 min='00',
                                 max='23')

    def degree_day_threshold(self, min_val, max_val, value, string):

        return widgets.BoundedFloatText(value=value,
                                        min=min_val,
                                        max=max_val,
                                        step=0.0001,
                                        description=string,
                                        disabled=False,
                                        layout=self.item_layout)

    def set_up_button(self, method, description, layout='default'):
        
        if layout=='default':
            button = LoadedButton(description=description,
                                  layout=self.item_layout)
        elif layout=='save':
            button = LoadedButton(description=description,
                              layout=self.save_layout)
        button.on_click(method)
        button.button_style = 'primary'

        return button



    @ staticmethod
    def display_widget(widget_list):

        for w in widget_list:
            display(w)


    @ staticmethod
    def display_widget_comparison_reduced(operation, product1, subproduct1, product2, subproduct2,
                                          projection, date_carousel, north, east, south, west, button_loc, date1,
                                          date2, date3, date4, upload_file, button, m, average, 
                                          trends, frequency, save_map, save_format, save_data):
        
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            align_content='center',
            width='100%')
        
        box_save = HBox([save_map, save_format, save_data], layout=box_layout)
        
        box1 = VBox([operation, product1, subproduct1, date1, date2, product2, subproduct2,
                     date3, date4, projection, average, trends, frequency, date_carousel, north, 
                     east, south, west, button_loc, upload_file, button, box_save])



        box2 = HBox([m, box1], layout=box_layout)

        display(box2)
        
    @staticmethod
    def output_widgets(save_map, save_data, save_format):
        
        box_layout5 = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            align_content='center',
            width='100%')
        
        box = HBox([save_map, save_format, save_data], layout=box_layout5)

        display(box)
            
            

    @ staticmethod
    def gridspec_display(operation, product1, subproduct1, product2, subproduct2,
                         projection, north, east, south, west, button_loc, date1,
                         date2, date3, date4, upload_file, button, m, average, trends, frequency):

        from ipywidgets import GridspecLayout

        grid = GridspecLayout(20, 20)
        grid.layout.height = '2000 px'

        grid[:1, :8] = operation
        grid[:9, :8] = m

        grid[:2, 9:11] = upload_file
        grid[2, 9:12] = button_loc

        grid[0, 12:16] = north
        grid[2:3, 12:16] = east
        grid[2, 12:16] = south
        grid[3, 12:16] = west

        grid[:3, 16:] = projection

#         grid[3:5, 9:13] = product1
#         grid[6:8, 9:13] = date1
#         grid[3:5, 13:16] = subproduct1
#         grid[4:6, 13:18] = date2

#         grid[7:8, 9:11] = product2
#         grid[8:9, 9:11] = date3
#         grid[7:8, 13:18] = subproduct2
        grid[8:9, 13:17] = date4

        grid[9:11, :5] = average
        grid[9:11, 6:10] = trends
        grid[9:11, 13:20] = frequency

        display(grid)

    @ staticmethod
    def display_output():

        out = widgets.Output()
        display(out)
        return out
    
    
    @staticmethod
    def show_save_options(save_map, save_format, save_data):
        """
        show the saving options in the UI once plots appear.
        """
        save_map.layout.visibility = 'visible'
        save_format.layout.visibility = 'visible'
        save_data.layout.visibility = 'visible'
    
    
    @staticmethod
    def hide_save_options(save_map, save_format, save_data):
        """
        hide saving options in the UI when no plots are displayed.
        """
        save_map.layout.visibility = 'hidden'
        save_format.layout.visibility = 'hidden'
        save_data.layout.visibility = 'hidden'

        
    def get_subproduct_list(self, product):

        if product == 'era5':
            return['skt']
        else:
            return self.search.get_subproduct_list_of_product(product)
    
    
    def get_subproduct_trend_analysis(self, product):
        
        if product == 'MOD13A2':
            return ['1_km_16_days_EVI']
        
        else:
            return self.get_subproduct_list(product)
        

    def get_date_widgets(self):

        return self.start_date(), self.end_date()

    def start_date(self):

        return widgets.DatePicker(description='Start Date: ',
                                  layout=self.item_layout,
                                  value=datetime.datetime(2000, 1, 1),
                                  disabled=False)

    def end_date(self):
        return widgets.DatePicker(description='EndDate: ',
                                  layout=self.item_layout,
                                  value=datetime.datetime(2000, 2, 1),
                                  disabled=False)

    def get_x_attributes(self, projection):

        if projection == "British National Grid":
            attributes = {"min": -9999999, "max": 9999999, "description": "Easting (x)"}
        else:
            attributes = {"min": -180, "max": 180, "description": "Longitude (x)"}
        return attributes

    def get_y_attributes(self, projection):

        if projection == "British National Grid":
            attributes = {"min": -9999999, "max": 9999999, "description": "Northing (y)"}
        else:
            attributes = {"min": -90, "max": 90, "description": "Latitude (y)"}
        return attributes


class LoadedButton(widgets.Button):
    """A button that can holds a value as a attribute."""

    def __init__(self, value=None, *args, **kwargs):
        super(LoadedButton, self).__init__(*args, **kwargs)
        self.add_traits(value=traitlets.Any(value))
