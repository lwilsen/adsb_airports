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

import os
import json
import datetime
import base64
import requests

import streamlit as st
import h3
import geopandas as gpd
from utils import st_plot_image
from streamlit_plotly_events import plotly_events
import plotly.graph_objs as go
import pandas as pd
from sentinelhub import SHConfig
from sentinelhub import (
    BBox,
    DataCollection,
    MimeType,
    SentinelHubRequest,
)
from openai import OpenAI




def airports():

    CLIENT_ID = "f25d7929-8ba4-44b5-8271-85fecb35f8a7"  # updated as of 12/17/2024
    CLIENT_SECRET = os.environ.get("SENTINAL_API_KEY")  # updated 12/17/2024

    config = SHConfig()

    config.sh_client_id = CLIENT_ID
    config.sh_client_secret = CLIENT_SECRET
    config.save("my-profile")

    st.title("Data Visualization Page")
    st.subheader("Choose a Distance, Hex Resolution and 'Level of Significance'")
    DISTANCE = int(st.radio("Distance", ["500", "100", "200", "300", "400", "50"]))

    RESOLUTION = st.select_slider("Resolution", options=[6, 7, 8, 9, 10, 11], value=10)

    SIGNIFICANCE = st.number_input("Significance", 0, 1000, value=1)

    params = {
        "Distance": DISTANCE,
        "Resolution": RESOLUTION,
        "Significance": SIGNIFICANCE,
    }

    actual_url = "http://airport_fastapi_route:5001/map"

    if SIGNIFICANCE >= 0:
        """Inputs parameters to fastapi backend,returns df's needed to make plot"""
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
    point_dict = fig2.data[0]["geojson"][
        "features"
    ]  # can select using indices of selected hexes
    st.write(
        """Click on a cell, and then press the button below 
        to see the satellite image of that location."""
    )

    hex_gjson_indx = []
    for hexx in selected_hexes:
        hex_gjson_indx.append(hexx["pointIndex"])

    h3cell_id_list = []
    for hex_idx in hex_gjson_indx:
        h3cell_id = point_dict[hex_idx]["id"]
        h3cell_id_list.append(h3cell_id)
        st.write(f"H3 cell centroid coordinates: {h3.cell_to_latlng(h3cell_id)}")

    filtered_df = h3_df[h3_df[f"H3_{RESOLUTION}_cell"].isin(h3cell_id_list)]
    st.write(filtered_df)

    st.subheader("Choose satellite box width and height")
    x_adjust = st.number_input("Choose latitude Adjustment", value=0.02)
    y_adjust = st.number_input("Choose longitude Adjustment", value=0.02)

    today = datetime.date.today()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    beginning = st.date_input("Choose starting date", yesterday)
    ending = st.date_input("Choose end date (up to today)", today)

    try:
        box_params = {
            "x_adjust": x_adjust,
            "y_adjust": y_adjust,
            "cell_id": h3cell_id_list[0],
        }
    except Exception as e:
        if st.button("debug"):
            st.write(f"Error: {e}")
        st.write("Please click on a cell to view the satellite image.")

    # Now need to copy paste below funcionality into fastapi app

    if st.button("Show me the satellite image!"):
        try:
            response = requests.post(actual_url, json={"data": box_params}, timeout=10)
        except Exception as e:
            if st.button("debug"):
                st.write(f"Error: {e}")
            st.write("Please select a cell to view")

        if response.status_code == 200:
            try:
                result = response.json()

                evalscript_true_color = result.get("evalscript_true_color")
                tampa_bbox_dict = result.get("tampa_bbox")

                tampa_box_coords = {
                    "min_x": tampa_bbox_dict["min_x"],
                    "max_x": tampa_bbox_dict["max_x"],
                    "min_y": tampa_bbox_dict["min_y"],
                    "max_y": tampa_bbox_dict["max_y"],
                }

                tampa_box_crs = tampa_bbox_dict["_crs"]

                tampa_bbox = BBox(tampa_box_coords, tampa_box_crs)
                tampa_size = result.get("tampa_size")
                st.write(result.get("bcords_str"))  # writes new box center cords
                st.write(result.get("nw_rs_str"))  # writes new box resolution (pixels)

                beginning_str = beginning.strftime("%Y-%m-%d")
                ending_str = ending.strftime("%Y-%m-%d")

                tamp_request_tc = SentinelHubRequest(
                    evalscript=evalscript_true_color,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=DataCollection.SENTINEL2_L1C,
                            time_interval=(beginning_str, ending_str),
                        )
                    ],
                    responses=[
                        SentinelHubRequest.output_response("default", MimeType.PNG)
                    ],
                    bbox=tampa_bbox,
                    size=tampa_size,
                    config=config,
                )
                tamp_tc_imgs = tamp_request_tc.get_data()
                tamp = tamp_tc_imgs[0]
                image_path = st_plot_image(
                    tamp, factor=3.5 / 255, clip_range=(0, 1), filename="sat_plot.jpg"
                )

                OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
                client = OpenAI(api_key=OPENAI_KEY)

                # Function to encode the image
                def encode_image(image_path):
                    with open(image_path, "rb") as image_file:
                        return base64.b64encode(image_file.read()).decode("utf-8")

                # Getting the base64 string
                base64_image = encode_image(image_path)

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Tell me about this image.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=300,
                )
                st.subheader(response.choices[0].message.content)

            except requests.exceptions.JSONDecodeError:
                st.error("Error: The response is not in JSON format.")
                st.write("Response content:", response.text)
