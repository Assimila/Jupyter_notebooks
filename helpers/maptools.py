from __future__ import print_function
import json
import warnings
import os
import datetime
import ipywidgets as widgets
import matplotlib.pyplot as plt
from ipyleaflet import (
    Map, Marker, basemaps, basemap_to_tiles,
    TileLayer, ImageOverlay, Polyline, Polygon, Rectangle,
    GeoJSON, WidgetControl, DrawControl, LayerGroup, FullScreenControl,
    interactive)
from IPython.display import display, clear_output
from ipyleaflet import LayersControl, WidgetControl
from ipywidgets import FloatSlider
import rioxarray
import xarray_leaflet
import subprocess

warnings.filterwarnings("ignore", category=FutureWarning)


class MapTools:
    """
    Set of tools to manipulate ipyleaflet.Map object.
    """

    def __init__(self, center, zoom, width, height, os_api=False):
        """
        Initialise parameters and create Map object.

        :param center: tuple defining center of the map when displayed
        :param zoom:   zoom level of the map when displayed
        :param width:  width of the displayed map in pixels
        :param height: height of the displayed map in pixels

        :return:
        """
        self.center = center
        self.zoom = zoom
        self.width = width
        self.height = height
        self.key = 'k49EE9jmNlTQtGq6rGMXKgeQ2BYYADJG'
        self.dc = DrawControl()
        self.layers_list = []
        
        if os_api:
            self.basemap = self.os_map_api()
            self.map = Map(basemap=self.basemap, center=self.center, zoom=self.zoom,
                           layout=dict(width=self.width, height=self.height))
        else:
            self.map = Map(center=self.center, zoom=self.zoom,
                           layout=dict(width=self.width, height=self.height))
    
    def os_map_api(self):
        """
        Retrieve the OS basemap used in the displayed map.

        :return os_maps_api: dictionary containing endpoint URL with key and
                             other map attributes.
        """
        #secret_key = 'GL5RryNtcbGzCBw7'
        os_maps_api = {'url': f'https://api.os.uk/maps/raster/v1/zxy/Light_3857/{{z}}/{{x}}/{{y}}.png?key={self.key}',
                       'min_zoom': 7,
                       'max_zoom': 20,
                       'attribution': f'Contains OS data &copy; Crown copyright and database rights{datetime.datetime.now().year}'}

        return os_maps_api

    def prepare_map(self, rect=True):
        """
        Set up map properties and define options for rectangle and
        marker drawing.

        :return:
        """
        if rect:
            self.dc.rectangle = {'shapeOptions': {'color': '#FF0000'}}
        self.dc.marker = {"shapeOptions": {"fillColor": "#fca45d",
                                           "color": "#fca45d", "fillOpacity": 1.0}}
        self.dc.polyline = {}
        self.dc.polygon = {}
        self.dc.circlemarker = {}

    def prepare_map_africa_colombia(self):
        """
        Set up map properties and define options for rectangle and
        marker drawing. GeoJSON layers for Africa and Colombia are added.

        :return:
        """

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
        Add a marker point to the map with given latitude and longitude.

        :param lon: the longitude of the point location
        :param lat: the latitude of the point location

        :return:
        """
        if len(self.layers_list) != 0:
            self.map.remove_layer(self.layers_list.pop(0))
            
        marker = Marker(location=(lat, lon), draggable=True, )
        self.map.add_layer(marker)
        self.layers_list.append(marker)

    def add_map_rect(self, north, east, south, west):
        """
        Add a rectangular bounding box tho the map with given coordinates.

        :param north: northern boundary latitude
        :param east: eastern boundary longitude
        :param south: southern boundary latitude
        :param west: western boundary longitude

        :return:
        """
        if len(self.layers_list) != 0:
            self.map.remove_layer(self.layers_list.pop(0))
        
        rectangle = Rectangle(bounds=((south, west), (north, east)), color='#FF0000')
        self.map.add_layer(rectangle)
        self.layers_list.append(rectangle)

    @staticmethod
    def get_coords_point(geo_json):
        """
        Find the coordinates of a point drawn on the map with DrawControl().

        :param geo_json: map GeoJSON passed to function from on_draw method.

        :return north, east, south, west: lat/long coords of map point
        """
        #self.layers_list.append(geo_json)
        
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
        Find the coordinates of a rectangle drawn on the map with DrawControl().

        :param geo_json: map GeoJSON passed to function from on_draw method.

        :return north, east, south, west: lat/long coords of map point
        """
        #self.layers_list.append(geo_json)
        
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
        Add a layer onto the map using a .geojson file saved locally on server.

        :param fname: filename of .geojson file to be added to the map.

        :return north, east, south, west: lat/long coords of map point
        """
        if len(self.layers_list) != 0:
            self.map.remove_layer(self.layers_list.pop(0))
            
        with open(fname, 'r') as f:
            data = json.load(f)

        geo_json = GeoJSON(
            data=data,
            style={
                'shapeOptions': {'color': '#FF0000'}
            }
        )
        self.layers_list.append(geo_json)
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
        Add image as an overlay onto the map at the bounding box.

        :param bounds: tuple of 2 tuples defining NW and SW corners of
                       the images position.

        :return:
        """
        image = ImageOverlay(
            url='/ui.png',
            bounds=bounds
        )

        self.map.add_layer(image)
    
    def data_overlay(self, ds):
        """
        Plots a data layer on the map to allow for better visualisation.
        Sliding widget allows user to change opacity of image.  
        Plot image is the first timestep in the xarray.
        
        :param ds: dataset to be overlaid
        
        :return:
        """
        def set_opacity(*args):
            l.opacity = args[0]['new']
            
        ds.to_netcdf('tmp.nc')
        ds = rioxarray.open_rasterio('tmp.nc')
        ds_to_plot = ds[0]
        ds_to_plot = ds_to_plot.rename({'x': 'longitude','y': 'latitude'})
        l = ds_to_plot.leaflet.plot(self.map, colormap=plt.cm.viridis, )

        # Insert slider and layer control
        layers_control = LayersControl(position='topright')
        self.map.add_control(layers_control)

        opacity_slider = FloatSlider(description='Opacity:', min=0, max=1, value=1)
        opacity_slider.observe(set_opacity, names='value')
        slider_control = WidgetControl(widget=opacity_slider, position='bottomleft')
        self.map.add_control(slider_control)
        
        subprocess.call('rm tmp.nc', shell = True)
        
    @staticmethod
    def update_nesw(x):
        """
        Update the NESW coordinate boxes on the map when layers are
        added using DrawControl().

        :param x: value to be updated in the boxes.

        :return w: interactive widget to be linked to a value.
        """
        def create_wid(a):
            w.observe(on_change)
            return a
        w = interactive(create_wid, a=x)

        def on_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                x.value = change['new']
        w.observe(on_change)
        return w

    def mouse_interaction(self, label):
        """
        Handle mouse hovering over the map and display live coordinates
        which correspond to the mouse position.

        :param label: label widget which is displayed on the map as coords.
        """
        def handle_interaction(**kwargs):
            if kwargs.get('type') == 'mousemove':
                label.value = str(kwargs.get('coordinates'))
        self.map.on_interaction(handle_interaction)
        display(label)
