from fastapi import FastAPI, HTTPException, Request
import h3
import geopandas as gpd
import pickle
from utils import hexagons_dataframe_to_geojson, cell_to_shapely, plot_image, st_plot_image
import plotly_express as px
from collections import Counter
from streamlit_plotly_events import plotly_events
import plotly.graph_objs as go
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
from sentinelhub import SHConfig
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    SentinelHubRequest,
    bbox_to_dimensions,
)
import pandas as pd

'''SENTINAL SETUP'''

CLIENT_ID = '139dda82-905a-4f6c-8aaa-3a6635c5216c'
CLIENT_SECRET = os.environ.get("SENTINAL_API_KEY")

config = SHConfig()

config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET
config.save("my-profile")
    
'''Unpickling data sets'''

with open('fl_airports.pkl', 'rb') as f:
    tam_air = pickle.load(f)

with open('gdf_all_res.pkl','rb') as f: #resolution = 10
    gdf = pickle.load(f)

'''Fast API'''

app = FastAPI()

@app.post("/map")
async def make_map(request : Request):

    try:
    
        data = await request.json()

        params = data.get("params")

        DISTANCE = params["Distance"]
        RESOLUTION = params["Resolution"]
        SIGNIFICANCE = params["Resolution"]

        def count_categories(categories):
            return Counter(categories)
        
        gdf = gdf[gdf['distance'] <= DISTANCE/69]

        h3_df = gdf.groupby(f'H3_{RESOLUTION}_cell').agg(count=(f'H3_{RESOLUTION}_cell', 
                                                                'size'),
                                                        category_counts=('category', 
                                                                        count_categories)).reset_index()

        h3_df = h3_df[h3_df['count'] >= SIGNIFICANCE]

        #should create resolution columns beforehand, and just select from themm
        h3_geoms = h3_df[f"H3_{RESOLUTION}_cell"].apply(lambda x: cell_to_shapely(x))
        h3_gdf = gpd.GeoDataFrame(data=h3_df, geometry=h3_geoms, crs=4326)

        geojson_obj_h3_gdf = hexagons_dataframe_to_geojson(h3_gdf,
                                                    hex_id_field=f'H3_{RESOLUTION}_cell',
                                                    value_field='count',
                                                    geometry_field='geometry')

        fig2 = go.Figure(
            data=[
                go.Choroplethmapbox(
                    geojson=geojson_obj_h3_gdf,
                    locations=h3_gdf[f'H3_{RESOLUTION}_cell'],
                    z=h3_gdf['count'],
                    zmax=50,
                    zmin=0,
                    colorscale = 'inferno',
                    reversescale=False,
                    marker_opacity=0.7,
                    marker_line_color='white',
                    marker_line_width=0.5,
                    colorbar_title="Number of Planes"
                )
            ],
            layout=go.Layout(
                mapbox_style="open-street-map",
                mapbox_center={"lat": 27.842490, "lon": -82.503222},
                mapbox_zoom=8,
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
        )


        # insert some json below
        return {"fig2": fig2, "h3_df":h3_df}

    except Exception as e:
        
        return {"Error during map making": str(e), "Data": data}
