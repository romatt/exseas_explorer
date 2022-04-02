# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# import plotly.express as px
# import pandas as pd
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_bootstrap_components as dbc
import geopandas
import numpy as np
from dash import Dash, dcc, html
import matplotlib

# Load data
filename = "/ytpool/data/ETH/INTEXseas/land_patches_40y_era5_RTOT_djf_ProbDry.geojson"
file = open(filename)
df = geopandas.read_file(file)

filtered = df[0:10]
# geo_j = filtered['geometry'].to_json()

labels = filtered['lab']

# Define colors
classes = np.arange(np.nanmin(labels), np.nanmax(labels), 10)
cmap = matplotlib.cm.get_cmap('Spectral', classes.size)
colors = [cmap(x/np.max(classes)) for x in classes] # Assign colors to labels
colors = [matplotlib.colors.to_hex(x) for x in colors] # Convert colors to hex

style = dict(weight=2,
             opacity=1,
             color='white',
             dashArray='3',
             fillOpacity=0.7)

# Create colorbar.
ctg = [
    "{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])
] + ["{}+".format(classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg,
                                    colorscale=colors,
                                    width=400,
                                    height=30,
                                    position="bottomleft")

app = Dash(__name__)
app.layout = html.Div([
    dbc.Navbar(),
    dl.Map(center=[0, 0],
           zoom=2,
           children=[
               dl.TileLayer(),
               dl.GeoJSON(data=filtered.__geo_interface__, id="patches"),
               colorbar
           ],
           style={
               'width': '90%',
               'height': '70vh',
               'margin': "auto",
               "display": "block"
           },
           id="map")
])

if __name__ == '__main__':
    app.run_server(debug=True)
