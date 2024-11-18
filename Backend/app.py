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
async def predict(request : Request):

    try:
    
        data = await request.json()

        


        # insert some json below
        return {}

    except Exception as e:
        
        return {"Error during prediction": str(e), "Data": data}
