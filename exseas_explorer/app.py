# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# import plotly.express as px
# import pandas as pd
import dash
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import geopandas
from dash import Dash, dcc, html

filename = "/ytpool/data/ETH/INTEXseas/land_patches_40y_era5_RTOT_djf_ProbDry.geojson"
file = open(filename)
df = geopandas.read_file(file)

filtered = df[df['key'] < 1952]
# geo_j = filtered['geometry'].to_json()

app = Dash(__name__)
app.layout = html.Div([
    dbc.Navbar(),
    dl.Map(center=[0, 0], zoom=2,
           children=[dl.TileLayer(),
           dl.GeoJSON(data=filtered.__geo_interface__, id="patches")],
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
