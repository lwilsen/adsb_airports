"""
This Python script utilizes Streamlit to create a data visualization 
application focusing on ADS-B aircraft data and satellite imagery. 

Users can select various parameters including distance, resolution, 
and significance level to retrieve data points. The script also allows 
users to choose a specific H3 cell and display its corresponding 
satellite image.

This script relies on several external libraries:

* Streamlit
* h3
* geopandas
* utils (assumed to be a custom library containing st_plot_image)
* streamlit_plotly_events
* plotly.graph_objs
* sentinelhub
* requests
* pandas
* datetime
"""

import streamlit as st
import h3
import geopandas as gpd
from utils import st_plot_image, hexagons_dataframe_to_geojson, cell_to_shapely
from streamlit_plotly_events import plotly_events
import plotly.graph_objs as go
import os
import json
import pandas as pd
from sentinelhub import SHConfig
from sentinelhub import (
    BBox,
    DataCollection,
    MimeType,
    SentinelHubRequest,
)
import requests
import datetime
from openai import OpenAI
import pickle

import base64

CLIENT_ID = "f25d7929-8ba4-44b5-8271-85fecb35f8a7"  # updated as of 12/17/2024
CLIENT_SECRET = os.environ.get("SENTINAL_API_KEY")  # updated 12/17/2024

config = SHConfig()

config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET
config.save("my-profile")


st.title("Data Visualization Page")
st.subheader("Choose a Distance, Hex Resolution and 'Level of Significance'")

with open("geo_dataframe.pkl", "rb") as f:
    geo_dataframe = pickle.load(f)


DISTANCE = int(st.radio("Distance", ["500", "100", "200", "300", "400", "50"]))


RESOLUTION = st.select_slider("Resolution", options=[6, 7, 8, 9, 10, 11], value=6)


SIGNIFICANCE = st.number_input("Significance", 0, 1000, value=1)


params = {"Distance": DISTANCE, "Resolution": RESOLUTION, "Significance": SIGNIFICANCE}

temp_url = "http://127.0.0.1:8000/map"
actual_url = "http://airport_fastapi_route:5001/map"


if SIGNIFICANCE >= 0:

    response = requests.post(actual_url, json={"data": params}, timeout=10)

    if response.status_code == 200:
        try:
            result = response.json()
            geojson_obj_h3_gdf = result.get("geojson_obj_h3_gdf")
            h3_df = pd.read_json(result.get("h3_df"))
            h3_gdf = json.loads(result.get("h3_gdf"))
            h3_gdf = gpd.GeoDataFrame.from_features(h3_gdf["features"])

        except requests.exceptions.JSONDecodeError:
            st.error("Error: The response is not in JSON format.")
            st.write("Response content:", response.text)

fig2 = go.Figure(
    data=[
        go.Choroplethmapbox(
            geojson=geojson_obj_h3_gdf,
            locations=h3_gdf[f"H3_{RESOLUTION}_cell"],
            z=h3_gdf["count"],
            zmax=50,
            zmin=0,
            colorscale="inferno",
            reversescale=False,
            marker_opacity=0.7,
            marker_line_color="white",
            marker_line_width=0.5,
            colorbar_title="Number of Planes",
        )
    ],
    layout=go.Layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": 27.842490, "lon": -82.503222},
        mapbox_zoom=8,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    ),
)
fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

selected_hexes = plotly_events(fig2, click_event=True, select_event=True)
point_dict = fig2.data[0]["geojson"]["features"]

hex_gjson_indx = []
for hex in selected_hexes:
    hex_gjson_indx.append(hex["pointIndex"])

h3cell_id_list = []
for hex_idx in hex_gjson_indx:
    h3cell_id = point_dict[hex_idx]["id"]
    h3cell_id_list.append(h3cell_id)

try:
    cell_gdf = geo_dataframe[
        geo_dataframe[f"H3_{RESOLUTION}_cell"] == h3cell_id_list[0]
    ]

    flights_in_hex = cell_gdf["flight"].unique()

    flights_in_hex_gdf = geo_dataframe[geo_dataframe["flight"].isin(flights_in_hex)]
    types_in_hex = cell_gdf["type"].unique()

    st.write("Total Observations of flights within selected hex:")
    st.write(
        flights_in_hex_gdf.groupby(["flight", "type"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    selected_flight = st.selectbox("Select a flight to track", tuple(flights_in_hex))

    selected_type = st.selectbox("Select the type of aircraft", tuple(types_in_hex))

    st.write(f"You selected flight: {selected_flight}")

    selected_f_gdf = geo_dataframe[
        (geo_dataframe[f"flight"] == selected_flight)
        & (geo_dataframe["type"] == selected_type)
    ]

    st.write("Please select a starting and end date.")
    flight_dates = list(selected_f_gdf["timestamp"].dt.date.unique())
    start_date = st.radio("Start date", flight_dates)
    end_date = st.radio("End date", flight_dates)

    flight_date_gdf = selected_f_gdf[
        (selected_f_gdf["timestamp"].dt.date >= start_date)
        & (selected_f_gdf["timestamp"].dt.date <= end_date)
    ]

    first_timestamp = flight_date_gdf["timestamp"].min()
    flight_date_gdf["time_from_start"] = (
        flight_date_gdf["timestamp"] - first_timestamp
    ).dt.total_seconds() / 3600

    flight_date_geoms = flight_date_gdf[f"H3_{RESOLUTION}_cell"].apply(
        lambda x: cell_to_shapely(x)
    )
    h3_gdf_plane = gpd.GeoDataFrame(
        data=flight_date_gdf, geometry=flight_date_geoms, crs=4326
    )

    geojson_obj_h3_gdf_plane = hexagons_dataframe_to_geojson(
        h3_gdf_plane,
        hex_id_field=f"H3_{RESOLUTION}_cell",
        value_field="time_from_start",
        geometry_field="geometry",
    )
    try:
        mb_center = h3.cell_to_latlng(flight_date_gdf[f"H3_{RESOLUTION}_cell"].iloc[0])

        fig2 = go.Figure(
            data=[
                go.Choroplethmapbox(
                    geojson=geojson_obj_h3_gdf_plane,
                    locations=flight_date_gdf[f"H3_{RESOLUTION}_cell"],
                    z=(flight_date_gdf["time_from_start"]),
                    colorscale="Viridis",
                    reversescale=False,
                    marker_opacity=0.7,
                    marker_line_color="white",
                    marker_line_width=0.5,
                    colorbar_title="Time from start",
                )
            ],
            layout=go.Layout(
                mapbox_style="open-street-map",
                mapbox_center={"lat": mb_center[0], "lon": mb_center[1]},
                mapbox_zoom=8,
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
            ),
        )

        fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        st.plotly_chart(fig2)
    except Exception as e:
        st.error("Select a valid Flight number and aircraft type combo")

except Exception as e:
    st.error("Click on a Hex!")