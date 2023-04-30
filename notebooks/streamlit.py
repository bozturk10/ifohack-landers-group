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
from bokeh.tile_providers import get_provider, Vendors

tile_provider = get_provider(Vendors.OSM)

st.title("Land Prices")

st.subheader("Running a streamlit app")

st.markdown("""
With an entrypoint file called `app.py`
- `streamlit run app.py`
""")

x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

p = figure(
    title='simple line example',
    x_axis_label='x',
    y_axis_label='y')

p.line(x, y, legend_label='Trend', line_width=2)

st.bokeh_chart(p, use_container_width=True)





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

for city in cities:

    neighborhoods_in_city = gpd.read_file(f"../data/raw/3 Neighborhoods/Neighborhoods_{city}.gpkg")

    land_prices = pd.read_csv(f"../data/raw/1 Land Prices/Land_Prices_Neighborhood_{city}.csv", sep = ";")

    neighborhoods_in_city = pd.merge(neighborhoods_in_city, land_prices, on='Neighborhood_FID', how='left')

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


p = figure(title = f"Neighborhoods in {cities[0]}", x_range=x_range, y_range=y_range,
           x_axis_type="mercator", y_axis_type="mercator", match_aspect=False)
     
p.patches('x', 'y', source = ColumnDataSource(neighborhood_b), line_color = "grey", line_width = 0.8,
          fill_color= transform('Land_Value', LogColorMapper(palette = palette)),
          fill_alpha = 0.7)

#p.add_tile(tile_provider)

TOOLTIPS = [
    ("Land Value", "@Land_Value"),
    ("Area count", "@Area_Count")
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

st.bokeh_chart(p, use_container_width=True)