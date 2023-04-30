import streamlit as st

import numpy as np
import pandas as pd
import geopandas as gpd  

from pyproj import CRS  
#import xyzservices.providers as xyz  

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_notebook, show
from bokeh.models.mappers import LogColorMapper
from bokeh.palettes import RdYlGn10 as palette
from bokeh.models import ColumnDataSource,HoverTool, Select
from bokeh.transform import transform
from bokeh.layouts import column
from bokeh.models import CustomJS, Select
from bokeh.models import ColorBar


#tile_provider = get_provider(Vendors.OSM)

st.title("_:blue[Land Prices]_ :moneybag: :cityscape:")

st.subheader("The app you need! :sunglasses:")


# No need to change the functions from the quick start
def getPolyCoords(row, geom, coord_type):
    
    if row[geom].geom_type == "MultiPolygon":
        g_obj = row[geom].geoms[0]
    else:
        g_obj = row[geom] 
    if coord_type == 'x':
        return list(g_obj.exterior.coords.xy[0])
    elif coord_type == 'y':
        return list(g_obj.exterior.coords.xy[1])

def transform_gdf(gdf):
    
    gdf['x'] = gdf.apply(getPolyCoords, geom = 'geometry', coord_type = 'x', axis = 1)
    gdf['y'] = gdf.apply(getPolyCoords, geom = 'geometry', coord_type = 'y', axis = 1)
    p_df = gdf.drop('geometry', axis = 1).copy()
    
    return p_df

# Settings
cities = ["Berlin", "Bremen" ,"Dresden", "Frankfurt_am_Main", "Köln"]


# Enable notebook output
output_notebook()

# Neighborhood is built inside the loop.
neighborhood = gpd.GeoDataFrame()
ranges = {}

# THIS NEEDS TO BE 3857 and not what was in the example notebook (3395). Otherwise Frankfurt is in Darmstadt :/
mercator_crs = CRS.from_user_input(3857)

merged_cities = pd.read_csv(f"../data/interim/nb_level_merged_all_cities_with_amenties.csv")

for city in cities:

    neighborhoods_in_city = gpd.read_file(f"../data/raw/3 Neighborhoods/Neighborhoods_{city}.gpkg")

    land_prices = pd.read_csv(f"../data/raw/1 Land Prices/Land_Prices_Neighborhood_{city}.csv", sep = ";")

    neighborhoods_in_city = pd.merge(neighborhoods_in_city, land_prices, on='Neighborhood_FID', how='left')

    all_city_data = merged_cities.query("City_Name == @city")

    neighborhoods_in_city = pd.merge(neighborhoods_in_city, all_city_data, on='Neighborhood_Name', how='left', suffixes=("", "_"))    

    neighborhoods_in_city["Land_Value"] = neighborhoods_in_city["Land_Value"].round(0)


    neighborhood = pd.concat([neighborhood, neighborhoods_in_city])

    ranges[city] = {
        "x": (neighborhoods_in_city.to_crs(mercator_crs).total_bounds[0], neighborhoods_in_city.to_crs(mercator_crs).total_bounds[2]),
        "y": (neighborhoods_in_city.to_crs(mercator_crs).total_bounds[1], neighborhoods_in_city.to_crs(mercator_crs).total_bounds[3])
    }    

neighborhood_mercator = neighborhood.to_crs(mercator_crs)
neighborhood_b = transform_gdf(neighborhood_mercator)

x_range = ranges[cities[0]]["x"]
y_range = ranges[cities[0]]["y"]
mapper = LogColorMapper(palette = palette)


p = figure(title = f"Neighborhoods in {cities[0]}", x_range=x_range, y_range=y_range,
           x_axis_type="mercator", y_axis_type="mercator", match_aspect=False)
     
p.patches('x', 'y', source = ColumnDataSource(neighborhood_b), line_color = "grey", line_width = 0.8,
          fill_color= transform('Land_Value',mapper),
          fill_alpha = 0.7)

cb = ColorBar (color_mapper = mapper, location = (5,6))
p.add_layout(cb, 'right')
#p.add_tile(tile_provider)

TOOLTIPS = [
    ("Neighborhood", "@Neighborhood_Name"),
    ("Land Value", "@Land_Value €/m2"),
    ("Area count", "@Area_Count"),
    ("Living area below 30 sqm", "@w_less_30"),
    ("Restaurants", "@restaurant"),
    ("Fountains", "@fountain")
    
]

p.add_tools(HoverTool(tooltips=TOOLTIPS))

callback = CustomJS(
    args = dict(xr = p.x_range, yr = p.y_range, locations = ranges, title = p.title),
    code = """

    var select_vals = cb_obj.value;

    title.text = `Neighborhoods in ${select_vals}`;

    xr.start = locations[select_vals]["x"][0];
    xr.end = locations[select_vals]["x"][1];
    yr.start = locations[select_vals]["y"][0];
    yr.end = locations[select_vals]["y"][1];
""")

select = Select(title="Select city:", value=cities[0], options=cities)
select.js_on_change("value", callback)

layout = column(select , p)
show(layout)

st.markdown("**Land prices in ...**")
st.bokeh_chart(layout, use_container_width=True)


st.markdown("**What should you care to sell your property for higher prices?**")



from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral10
from bokeh.transform import factor_cmap
from bokeh.io import show
import streamlit as st

features = ['Living space less than 30 sqm', 'Restaurants', 'Fountains', 'Benchs', 'Unusual apartment type', 'Holding German and other pass', 'Greek', 'EU27 pass', 'Waste bin', 'Cafe']
counts = [178, 124, 102, 81, 76, 76, 75, 74, 70, 68]

source = ColumnDataSource(data=dict(features=features, counts=counts, color=Spectral10))

# sorting the bars means sorting the range factors
sorted_features = sorted(features, key=lambda x: counts[features.index(x)], reverse=False)


feature_chart = figure(y_range=sorted_features, plot_height=350, plot_width=600, title="Most Important Features",
           toolbar_location=None, tools="")

feature_chart.hbar(y='features', right='counts', height=0.8, source=source, 
                   color=factor_cmap('features', palette=Spectral10, factors=sorted_features))

feature_chart.xgrid.grid_line_color = None
feature_chart.yaxis.major_label_text_font_size = "12pt"
feature_chart.axis.axis_line_color = None
feature_chart.outline_line_color = None

st.bokeh_chart(feature_chart)