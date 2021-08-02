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

import sys
sys.path.append("..")

warnings.filterwarnings("ignore", category=FutureWarning)

# matplotlib.use('nbagg')



class MapTools:
    """
    Set of tools to manipulate ipyleaflet.Map object.
    """

    def __init__(self, center, zoom, width, height):

        self.center = center
        self.zoom = zoom
        self.width = width
        self.height = height
        self.dc = DrawControl()
        self.map = Map(center=self.center, zoom=self.zoom,
                       layout=dict(width=self.width, height=self.height))

    def prepare_map(self):

        self.dc.rectangle = {'shapeOptions': {'color': '#FF0000'}}
        self.dc.marker = {"shapeOptions": {"fillColor": "#fca45d",
                                           "color": "#fca45d", "fillOpacity": 1.0}}
        self.dc.polyline = {}
        self.dc.polygon = {}
        self.dc.circlemarker = {}

    def prepare_map_africa_colombia(self):

        self.dc.rectangle = {'shapeOptions': {'color': '#FF0000'}}
        self.dc.marker = {"shapeOptions": {"fillColor": "#fca45d",
                                           "color": "#fca45d", "fillOpacity": 1.0}}
        self.dc.polyline = {}
        self.dc.polygon = {}
        self.dc.circlemarker = {}

        # Create a group of layers and add it to the Map
        group = LayerGroup()
        self.map.add_layer(group)

        # given Africa: N: 38.25, S: -36.25, E: 53.25, W: -19.25
        africa = GeoJSON(
            data={'type': 'Feature', 'properties':
                  {'name': "Africa", 'style':
                   {'color': '#0000FF', 'clickable': True}},
                  'geometry': {'type': 'Polygon',
                               'coordinates': [[[-19, 38], [53, 38],
                                                [53, -36], [-19, -36]]]}},
            hover_style={'fillColor': '03449e'})

        group.add_layer(africa)

        # given Colombia: N: 13.75, S: -5.25, E: -62.75, W: -83.25
        colombia = GeoJSON(data={'type': 'Feature',
                                 'properties': {'name': "Colombia",
                                                'style': {'color': '#0000FF',
                                                          'clickable': True}},
                                 'geometry': {'type': 'Polygon',
                                              'coordinates': [[[-83, 14],
                                                               [-63, 14],
                                                               [-63, -5],
                                                               [-83, -5]]]}},
                           hover_style={'fillColor': '03449e'})

        group.add_layer(colombia)

    def add_map_point(self, lon, lat):
        """
        add a marker point to the map with given latitude and longitude.
        """
        marker = Marker(location=(lat, lon), draggable=True, )
        self.map.add_layer(marker)

    def add_map_rect(self, north, east, south, west):
        """
        add a rectangular bounding box tho the map with given coordinates.
        """
        rectangle = Rectangle(bounds=((south, west), (north, east)), color='#FF0000')
        self.map.add_layer(rectangle)

    @staticmethod
    def get_coords_point(geo_json):
        """
        returnt the coordinates of a user-drawn marker point on the map.
        """
        coords = (geo_json.get('geometry', 'Point'))
        x = coords.get('coordinates')[0]
        y = coords.get('coordinates')[1]
        north = y
        south = y
        east = x
        west = x
        return north, east, south, west

    @staticmethod
    def get_coords_polygon(geo_json):
        """
        return the north east south and west coordinated of the user-drawn polygon on the map.
        """
        poly = (geo_json.get('geometry', 'Polygon'))
        coords = poly.get('coordinates')[0]
        SW = coords[0]
        NW = coords[1]
        NE = coords[2]
        SE = coords[3]
        north = (NW[1] + NE[1]) / 2
        east = (NE[0] + SE[0]) / 2
        south = (SW[1] + SW[1]) / 2
        west = (NW[0] + SW[0]) / 2

        return north, east, south, west

    def add_geojson(self, fname):
        """
        return the north east south and west coords of a .geojson file defined 
        rectangular bounding box and add this as a layer to the map.
        """
        with open(fname, 'r') as f:
            data = json.load(f)

        geo_json = GeoJSON(
            data=data,
            style={
                'shapeOptions': {'color': '#FF0000'}
            }
        )
        self.map.add_layer(geo_json)
        coords = data["features"][0]["geometry"]["coordinates"][0]

        SW = coords[0]
        SE = coords[1]
        NE = coords[2]
        NW = coords[3]

        north = (NW[1] + NE[1]) / 2
        east = (NE[0] + SE[0]) / 2
        south = (SW[1] + SW[1]) / 2
        west = (NW[0] + SW[0]) / 2

        return north, east, south, west
    
    def add_image(self, bounds):
        """
        add image as an overlay onto the map at the bounding box.
        """
        image = ImageOverlay(
                            url='/ui.png',
                            bounds=bounds
                            )
        
        self.map.add_layer(image)
    
    def remove_layer(self):
        """
        remove a layer from the map.
        """
        self.map.remove_layer(layer)
        
    def save_map(self):
        """
        save the map and layers as a static HTML.
        """
        self.map.save('map.html', title='My Map')
        
    @staticmethod
    def update_nesw(x):
        def create_wid(a):
            w.observe(on_change)
            return a
        w = interactive(create_wid, a=x)

        def on_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                x.value = change['new']
                # print(x.value)
        w.observe(on_change)
        return w

    def mouse_interaction(self, label):
        def handle_interaction(**kwargs):
            if kwargs.get('type') == 'mousemove':
                label.value = str(kwargs.get('coordinates'))
        self.map.on_interaction(handle_interaction)
        display(label)
