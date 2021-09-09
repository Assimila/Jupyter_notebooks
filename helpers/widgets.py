from __future__ import print_function
import warnings
import os
import datetime
from traitlets import traitlets
from ipywidgets import HBox, VBox, Box
import ipywidgets as widgets
from ipyleaflet import (
    Map, Marker, basemaps, basemap_to_tiles,
    TileLayer, ImageOverlay, Polyline, Polygon, Rectangle,
    GeoJSON, WidgetControl, DrawControl, LayerGroup, FullScreenControl,
    interactive)
from IPython.display import display, clear_output
from DQTools.DQTools.search import Search

warnings.filterwarnings("ignore", category=FutureWarning)


class Widgets:
    """
    Controls the majority of the widget set-up and displaying on the UI.
    """

    def __init__(self, width=None, height=None):
        """
        Initialise the DQTools Search class and different layout styles
        for different types of widgets.

        :param width [optional]:  user-defined widget width
        :param height [optional]: user-defined widget height

        :return:
        """
        
        # Lots of Layout objects must be defined to allow dynamic control
        # over the visibility of widgets when certain operations are selected.
        
        self.search = Search()
        self.item_layout_user = widgets.Layout(height=height, width=width)

        self.item_layout = widgets.Layout(width='auto', height='auto')
        self.item_layout_date12 = widgets.Layout(width='auto', height='auto')
        self.item_layout_date34 = widgets.Layout(width='auto', height='auto')
        self.item_layout_subproduct1 = widgets.Layout(width='auto', height='auto')
        self.item_layout_subproduct2 = widgets.Layout(width='auto', height='auto')
        self.item_layout_product1 = widgets.Layout(width='auto', height='auto')
        self.item_layout_product2 = widgets.Layout(width='auto', height='auto')
        self.item_layout_radio = widgets.Layout(width='auto', height='auto')
        self.item_layout_loc = widgets.Layout(width='auto', height='auto')
        self.item_layout_coords = widgets.Layout(width='60%', height='auto')
        self.item_layout_trends = widgets.Layout(width='60%', height='auto')
        self.item_layout_average = widgets.Layout(width='60%', height='auto')
        self.item_layout_frequency = widgets.Layout(width='60%', height='auto')
        self.carousel_layout = widgets.Layout(overflow='scroll hidden',
                                              width='500px',
                                              height='60px',
                                              flex_flow='row',
                                              display='flex')
        self.save_layout = widgets.Layout(width='auto', height='auto')
        
        self.projection_list = {" "       : " ",
                                "MOD11A1" : "Surface temperature",
                                "MOD13A2" : "Vegetation indices",
                                "MCD43A3" : "Albedo",
                                "era5"    : "Temperature"}

    def get_lat_lon_widgets(self):
        """
        Calls the latitude and longitde methods which display the
        relevant widgets to the UI.

        :return lattitude(), longitude(): methods which display widgets.
        """
        return self.latitude(), self.longitude()

    def get_product_widgets(self):
        """
        Calls the product() method which returns the relevant
        product list widget.

        :return product(): method to displaya product list.
        """
        return self.product()

    def longitude(self):
        """
        Call the BoundedFloatText method from widgets to display a
        longitude text box.

        :return widgets.BoundedFloatText: bounded longitude text box.
        """
        return widgets.BoundedFloatText(value=7.5,
                                        min=-180,
                                        max=180.0,
                                        step=0.0001,
                                        description='Longitude (x):',
                                        disabled=False,
                                        layout=self.item_layout)

    def latitude(self):
        """
        Call the BoundedFloatText method from widgets to display a
        lattitude text box.

        :return widgets.BoundedFloatText: bounded lattitude text box.
        """
        return widgets.BoundedFloatText(value=7.5,
                                        min=-90.0,
                                        max=90.0,
                                        step=0.0001,
                                        description='Latitude (y):',
                                        disabled=False,
                                        layout=self.item_layout)

    def get_point(self, value, description):
        """
        Return a bounded text box with a specified value and description,
        depending on CRS.

        :param value: the value to be displayed in the coordinate box.
        :param description: the description of the coordinate box,
                            varies between CRS's.

        :return widgets.BoundedFloatText: bounded text box containing specified
                                          value and description.
        """
        return widgets.BoundedFloatText(value=value,
                                        min=-9999999,
                                        max=9999999,
                                        description=description,
                                        layout=self.item_layout_coords,
                                        disabled=False,
                                        readout=False,
                                        readout_format='d')

    def product(self, description=None, layout=None, peat=False):
        """
        Return a dropdown list of products for the user to choose from.
        Optional params used for COP26 demo, default None for generic.

        :param description:     description to be displayed next to widget.
        :param peat [optional]: if True [default], peatland products are returned,
                                else, all products are returned.

        :return widgets.Dropdown: Dropdown widget object.
        """
        if peat:
            projection_list = list(self.projection_list.values())
        else:
            projection_list = self.search.products().name.tolist()
            
        if layout == 'product1':
            return widgets.Dropdown(
                options=list(projection_list),
                description=description,
                layout=self.item_layout_product1,
                disabled=False, 
                tooltip='Select the satellite data option required')

        elif layout == 'product2':
            return widgets.Dropdown(
                options=list(projection_list),
                description=description,
                layout=self.item_layout_product2,
                disabled=False, 
                tooltip='Select the satellite data option required')
            
        else:
            return widgets.Dropdown(
                options=projection_list,
                description="Product:",
                layout=self.item_layout,
                disabled=False, )

    def subproduct(self, description=None, layout=None):
        """
        Return an empty dropdown subproduct list. Once populated the user can
        choose subproducts from it. Optional params used for COP26 demo, 
        default None for generic.

        :param description: description to be displayed next to widget.
        :param layout:      the layout to be specified to each subproduct list.

        :return widgets.Dropdown: Dropdown object widget.
        """
        if description and layout:
            if layout == 'subproduct1':
                return widgets.Dropdown(description=description,
                                        layout=self.item_layout_subproduct1)
            elif layout == 'subproduct2':
                return widgets.Dropdown(description=description,
                                        layout=self.item_layout_subproduct2)
        else:
            return widgets.Dropdown(description='Subproduct:',
                                        layout=self.item_layout)
            
    def projection(self):
        """
        Return radio buttons defining different CRS projections for the
        user to choose from.

        :return widgets.Dropdown: WGS84, BNG, Sinusoidal radio button options.
        """
        projection_list = ['Lat/Lon', 'National Grid', 'Sinusoidal']
        return widgets.RadioButtons(
            options=projection_list,
            description='Coordinates:',
            layout=self.item_layout_radio,
            disabled=False,
            tooltip='Select a coordinate reference system to be displayed on the map')

    def operation(self):
        """
        Return a widgets dropdown menu with 4 different results analysis
        operations for the user to choose from.

        :return widgets.Dropdown: dropdown menu of choices.
        """
        return widgets.Dropdown(options=[" ",
                                         "Average of one sub-product",
                                         "Subtraction of one sub-product",
                                         "Trend analysis for one sub-product",
                                         "Identifying change"],
                                description="Operation:",
                                tooltip='Select which operation mode you would like to use',
                                layout=self.item_layout)

    def get_projection_widgets(self):
        """
        Get the projection list.

        :return projection(): Projection list.
        """
        return self.projection()

    def upload_file(self):
        """
        Return a button which allows the user to upload file(s)
        from the UI.

        :return widgets.FileUpload: widget to allow file upload.
        """
        return widgets.FileUpload(description="Shapefile",
                                  accept='.shp, .shx, .prj, .dbf, .geojson',
                                  multiple=True)

    def average(self):
        """
        Return a dropdown widget to allow the user to select which method
        they would like to use to average the chosen subproduct.

        :return widgets.Dropdown: dropdown list of options.
        """
        return widgets.Dropdown(options=[' ', 'by pixel', 'by area'],
                                description="Average",
                                placeholder='Select averaging method',
                                disabled=True,
                                layout=self.item_layout_average)

    def trends(self):
        """
        Return a dropdown widget to allow the user to select if they would
        like to see timeseries results overlaid or side-by-side.

        :return widgets.Dropdown: dropdown list of options.
        """
        return widgets.Dropdown(options=['side-by-side', 'overlaid'],
                                description="Trends",
                                placeholder='Select plot type',
                                disabled=True,
                                layout=self.item_layout_trends)

    def frequency(self):
        """
        Return a dropdown widget which allows the user to select the number
        of datetimes they would like to be analysed and displayed.

        :return widgets.Dropdown: dropdown list of options.
        """
        return widgets.Dropdown(options=[' ', 2, 3, 4, 5],
                                description="Frequency",
                                placeholder='Select analysis frequency',
                                disabled=True,
                                layout=self.item_layout_frequency)

    def date_carousel(self):
        """
        Return an empty scrolling horizontal carousel which can be populated
        with datetime selector objects depending on the user input frequency.

        :return carousel: widgets.Box object with carousel of datetimes.
        """
        items = []
        carousel = widgets.Box(children=items, layout=self.carousel_layout)
        return carousel

    def save_format(self):
        """
        Return a dropdown allowing the user to select which format they would
        like their results to be saved in.

        :return widgets.Dropdown: dropdown list of options.
        """

        return widgets.Dropdown(description='Save Format',
                                disabled=False,
                                layout=self.save_layout)
    
    def number_of_products(self, options):
        """
        Return radio button options to allow the user to select how many 
        products/subproducts they would like to visuslise.
        
        :return widgets.RadioButtons: 
        """
        return widgets.RadioButtons(
                    options=options,
                    description='Number of Products:',
                    layout=self.item_layout_radio,
                    disabled=False)


    def rainfall_products(self):
        """
        Return a dropdown which contains different rainfall products for the
        user to select from.

        :return widgets.Dropdown: dropdown list of options.
        """
        return widgets.Dropdown(options=['TAMSAT', 'CHIRPS', 'GPM'],
                                description='Product:',
                                layout=self.item_layout,
                                disabled=False, )

    def temperature_products(self):
        """
        Return a dropdown which contains different temperature products for the
        user to select from.

        :return widgets.Dropdown: dropdown list of options.
        """
        return widgets.Dropdown(options=['skt'],
                                description='Product:',
                                layout=self.item_layout,
                                disabled=False, )

    def get_year_widgets(self):
        """
        Return BoundedFloatText allowing the user to select two
        different years.

        :return y1, y2: widgets.BoundedFloatText selectors
        """

        y1 = widgets.BoundedFloatText(value=2018, min=2000, max=2019, step=1,
                                      description='Year 1 :', disabled=False,
                                      layout=self.item_layout)

        y2 = widgets.BoundedFloatText(value=2019, min=2000, max=2019, step=1,
                                      description='Year 2 :', disabled=False,
                                      layout=self.item_layout)

        return y1, y2

    def get_date(self, value, description, layout=None):
        """
        Return a date selector widget to allow interactive date selection.

        :param value:       the initial date displayed on the selector.
        :param description: the description displayed next to the selector.
        :param layout:      [optional] to allow dynamic displaying widgets in COP26 demo.

        :return widgets.DatePicker: date selection object
        """
        if layout == 'date12':
            return widgets.DatePicker(description=description,
                                      layout=self.item_layout_date12,
                                      value=value,
                                      disabled=False,
                                      tooltip='Select a start and end date')
        elif layout == 'date34':
            return widgets.DatePicker(description=description,
                                      layout=self.item_layout_date34,
                                      value=value,
                                      disabled=False)
        else:
            return widgets.DatePicker(description=description,
                                      layout=self.item_layout,
                                      value=value,
                                      disabled=False,
                                      tooltip='Select a start and end date')          

    def get_hour(self, value, description):
        """
        Return an integer slider selector widget to allow
        interactive hour selection.

        :param value:       the initial hour displayed on the selector.
        :param description: the description displayed next to the selector.

        :return widgets.IntSlider: hour selector object.
        """
        return widgets.IntSlider(description=description,
                                 layout=self.item_layout,
                                 value=value,
                                 disabled=False,
                                 min='00',
                                 max='23')

    def degree_day_threshold(self, min_val, max_val, value, string):
        """
        Return a BoundedFloatBox which contains degree day thresholds.
        
        :param min_val: minimum float value allowed
        :param max_val: maximum float value allowed
        :param value:   initial value displayed
        :param string:  description displayed next to box

        :return widgets.BoundedFloatText.
        """
        return widgets.BoundedFloatText(value=value,
                                        min=min_val,
                                        max=max_val,
                                        step=0.0001,
                                        description=string,
                                        disabled=False,
                                        layout=self.item_layout)
    
    def degree_day_temp(self):
        """
        Return a dropdown which contains different temperature products for the
        user to select from.

        :return widgets.Dropdown: dropdown list of options.
        """
        return widgets.Dropdown(options=['skt', 't2m'],
                                description='Temperature:',
                                layout=self.item_layout,
                                disabled=False, )
    
    def cutoff_type(self):
        """
        Return RadioButtons to allow user to select degree day 
        calculation cut-off type
        
        :return widgets.RadioButtons.
        """
        return widgets.RadioButtons(
            options=['Vertical', 'Horizontal'],
            description='Cut-off type:',
            layout=self.item_layout,
            disabled=False)

    def set_up_button(self, method, description, layout='default'):
        """
        Sets up buttons who's value traits can be accessed.
        
        :param method:            the function exectuted when the button 
                                  is pressed.
        :param description:       description displayed on button.
        :param layout [optional]: indicates if a button is a save-related
                                  so that it's layout can be hidden as req.
        
        return button: widget.LoadedButton object.
        """
        if layout == 'default':
            button = LoadedButton(description=description,
                                  layout=self.item_layout)
        elif layout == 'save':
            button = LoadedButton(description=description,
                                  layout=self.save_layout)
        button.on_click(method)
        button.button_style = 'primary'

        return button
    
    @ staticmethod
    def display_widget(widget_list):
        """
        Display a generic list of widgets
        
        :param widget_list: list of widgets
        """
        for w in widget_list:
            display(w)
    
    
    @staticmethod
    def display_widgets(product, subproduct, north, east, south,
                        west, date, hour, button, m):
        """
        Display widgets for request_bounding_box_for_time_step.ipynb.
        """
        
        from ipywidgets import HBox, VBox

        box1 = VBox([product, subproduct, north, east, south,
                     west, date, hour, button])

        box2 = HBox([box1, m])
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            width='100%')
        display(box2)
    
    
    @staticmethod
    def display_widgets_csv(num_prods, product1, subproduct1, product2, subproduct2, 
                            latitude, longitude, start, end, button, m):
        """
        Display widgets for extract_csv_from_datacube.ipynb.
        """
        
        from ipywidgets import HBox, VBox

        box1 = VBox([num_prods, product1, subproduct1, product2, subproduct2, 
                     latitude, longitude, start, end, button])

        box2 = HBox([box1, m])
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            width='100%')
        display(box2)
  
    @staticmethod
    def display_widget_comparison(product, subproduct, north, east, south,
                                  west, date1, hour1, date2, hour2, button, m):
        """
        Display widgets for compare_bounding_box_2_timesteps.ipynb
        """
        from ipywidgets import HBox, VBox

        box1 = VBox([product, subproduct, north, east, south,
                     west, date1, hour1, date2, hour2, button])
        box2 = HBox([m, box1])
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            width='100%')
        display(box2)

    @staticmethod
    def display_widget_comparison_reduced(operation, product1, subproduct1, product2, subproduct2,
                                          projection, date_carousel, north, east, south, west, button_loc, date1,
                                          date2, date3, date4, upload_file, button, m, average,
                                          trends, frequency, save_map, save_format, save_data):
        """
        Displays the widgets and map on the UI using Boxes. Used for COP26 demo notebook.
        
        :param operation:     operation selection dropdown widget
        :param product1:      product1 selection dropdown widget
        :param subproduct1:   subproduct1 selection dropdown widget  
        :param product2:      product2 selection dropdown widget
        :param subproduct2:   subproduct2 selection dropdown widget
        :param projection:    CRS projection radio button widget
        :param date_carousel: scrolling box of date selection widgets
        :param north:         north coordinate selection flaot box widget
        :param east:          east coordinate selection flaot box widget
        :param south:         south coordinate selection flaot box widget
        :param west:          west coordinate selection flaot box widget
        :param button_loc:    get location button widget
        :param date1:         date 1 selection widget
        :param date2:         date 2 selection widget
        :param date3:         date 3 selection widget
        :param date4:         date 4 selection widget
        :param upload_file:   file upload widget
        :param button:        get data selection weidget
        :param m:             ipywidget Map object 
        :param average:       averaging method dropdown widget
        :param trends:        trend display dropdown widget
        :param frequency:     number of date selections for carousel 
                              dropdown widget
        :param save_map:      save map button
        :param save_format:   file format for saving, dropdown widget
        :param save_data:     save data to file format button 
        
        :return:
        """
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            align_content='center',
            width='100%')

        box_save = HBox([save_map, save_format, save_data], layout=box_layout)

        box1 = VBox([operation, product1, subproduct1, date1, date2, product2, subproduct2,
                     date3, date4, projection, average, frequency, trends, date_carousel, north,
                     east, south, west, button_loc, upload_file, button, box_save])

        box2 = HBox([m, box1], layout=box_layout)

        display(box2)
        
    @staticmethod
    def display_widget_bounding_box(product, subproduct, north, east, south,
                                          west, date1,  date2, button, m):
        """
        Used for peatlands_compare_bounding_box_for_2_timesteps.ipynb notebook.
        """
        from ipywidgets import HBox, VBox

        box1 = VBox([product, subproduct, north, east, south,
                     west, date1, date2, button])
        box2 = HBox([box1, m])
        box_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            width='100%')
        display(box2)

    @staticmethod
    def display_output():
        """
        Returns an output widget, used as a context manager to output
        to different areas of the UI.
        
        :return out: output widget 
        """

        out = widgets.Output()
        display(out)
        return out

    @staticmethod
    def show_save_options(save_map, save_format, save_data):
        """
        Shows the saving options in the UI once plots appear.
        
        :param save_map:    save map widget 
        :param save_format: save format dropdown widget 
        :param save_data:   save data format button.
        
        :return:
        """  
        save_map.layout.visibility = 'visible'
        save_format.layout.visibility = 'visible'
        save_data.layout.visibility = 'visible'

    @staticmethod
    def hide_save_options(save_map, save_format, save_data):
        """
        Hides the saving options in the UI when no plots are displayed.
        
        :param save_map:    save map widget 
        :param save_format: save format dropdown widget 
        :param save_data:   save data format button.
        
        :return:
        """  
        save_map.layout.visibility = 'hidden'
        save_format.layout.visibility = 'hidden'
        save_data.layout.visibility = 'hidden'

    def get_subproduct_list(self, product, peat=False):
        """
        Finds the list of availible subproducts for a given product.
        Used to populate the dropdown subproduct widget.
        
        :param product: name of the product 
        :param peat: [optional] set True for peatlands project.
        
        :return: list of availible subproducts
        """
        if peat:
            if product == 'Temperature':
                return ['skt']
            else:
                for key, value in self.projection_list.items():
                    if value == product:
                        return self.search.get_subproduct_list_of_product(key)
        else:
                return self.search.get_subproduct_list_of_product(product)

    def get_subproduct_trend_analysis(self, product):
        """
        Finds the reduced list of availible subproducts for a given
        product when the 'trend analysis' operation is selected. Used
        to populate the dropdown subproduct widget.
        
        :param product: name of the product 
        
        :return: list of availible subproducts
        """

        if product == 'Vegetation indices':
            return ['1_km_16_days_EVI']

        else:
            return self.get_subproduct_list(product, peat=True)

    def get_date_widgets(self):
        """
        Reutrns the start and end date methods.
        
        :return start_date(), end_date(): DatePicker widget
        """

        return self.start_date(), self.end_date()

    def start_date(self):
        """
        Return a DatePicker widget to allow the user to interactivley
        select dates.
        
        :return widgets.Datepicker: widget
        """
        return widgets.DatePicker(description='Start Date: ',
                                  layout=self.item_layout,
                                  value=datetime.datetime(2000, 1, 1),
                                  disabled=False)

    def end_date(self):
        """
        Return a DatePicker widget to allow the user to interactivley
        select dates.
        
        :return widgets.Datepicker: widget
        """
        return widgets.DatePicker(description='End Date: ',
                                  layout=self.item_layout,
                                  value=datetime.datetime(2000, 2, 1),
                                  disabled=False)

    def get_x_attributes(self, projection):
        """
        Depending on the projection, set the relevant widget x-attributes.
        
        :param projection: the CRS projection
        
        :return sttributes: dictionary containing widget attributes
        """
        if projection == "British National Grid":
            attributes = {"min": -9999999, "max": 9999999, "description": "Easting (x)"}
        else:
            attributes = {"min": -180, "max": 180, "description": "Longitude (x)"}
        return attributes

    def get_y_attributes(self, projection):
        """
        Depending on the projection, set the relevant widget y-attributes.
        
        :param projection: the CRS projection
        
        :return sttributes: dictionary containing widget attributes
        """
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
