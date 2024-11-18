import streamlit as st
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

CLIENT_ID = '139dda82-905a-4f6c-8aaa-3a6635c5216c'
CLIENT_SECRET = os.environ.get("SENTINAL_API_KEY")

config = SHConfig()

config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET
config.save("my-profile")


st.title("Data Visualization Page")
st.subheader("Choose a Distance, Hex Resolution and 'Level of Significance'")
DISTANCE = int(st.radio("Distance", ["500","100", "200", "300", "400", "50"]))
RESOLUTION = st.select_slider("Resolution", options = [6,7,8,9,10,11], value=10)
SIGNIFICANCE = st.number_input("Significance", 0,1000, value=1)

with open('fl_airports.pkl', 'rb') as f:
    tam_air = pickle.load(f)

with open('gdf_all_res.pkl','rb') as f: #resolution = 10
    gdf = pickle.load(f)

gdf = gdf[gdf['distance'] <= DISTANCE/69]

def count_categories(categories):
    return Counter(categories)

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

fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

selected_hexes = plotly_events(fig2, click_event= True, select_event = True)
point_dict = fig2.data[0]['geojson']['features'] #can select using indices of selected hexes
st.write("Click on a cell, and then press the button below to see the satellite image of that location.")

hex_gjson_indx = []
for hex in selected_hexes:
    hex_gjson_indx.append(hex['pointIndex'])

h3cell_id_list = []
for hex_idx in hex_gjson_indx:  
    h3cell_id = point_dict[hex_idx]['id']
    h3cell_id_list.append(h3cell_id)
    st.write(f"H3 cell centroid coordinates: {h3.cell_to_latlng(h3cell_id)}")

filtered_df = h3_df[h3_df[f"H3_{RESOLUTION}_cell"].isin(h3cell_id_list)]
st.write(filtered_df)

with st.expander("ADS-B aircraft category **A** information"):
    st.subheader("A Category")
    st.markdown("""
    * **A0:** No ADS-B emitter category information.
    * **A1:** Light (< 15500 lbs) - Any airplane with a maximum takeoff weight less than 15,500 pounds.
    * **A2:** Small (15500 to 75000 lbs) - Any airplane with a maximum takeoff weight greater than or equal to 15,500 pounds but less than 75,000 pounds.
    * **A3:** Large (75000 to 300000 lbs) - Any airplane with a maximum takeoff weight greater than or equal to 75,000 pounds but less than 300,000 pounds that does not qualify for the high vortex category.
    * **A4:** High vortex large (aircraft such as B-757) - Any airplane with a maximum takeoff weight greater than or equal to 75,000 pounds but less than 300,000 pounds that has been determined to generate a high wake vortex.
    * **A5:** Heavy (> 300000 lbs) - Any airplane with a maximum takeoff weight equal to or above 300,000 pounds.
    * **A6:** High performance (> 5g acceleration and 400 kts) - Any airplane, regardless of weight, which can maneuver in excess of 5 G's and maintain true airspeed above 400 knots.
    * **A7:** Rotorcraft - Any rotorcraft regardless of weight.
    """)
with st.expander("ADS-B aircraft category **B** information"):
    st.subheader("B Category")
    st.markdown("""
    * **B0:** No ADS-B emitter category information.
    * **B1:** Glider / sailplane - Any glider or sailplane regardless of weight.
    * **B2:** Lighter-than-air - Any lighter than air (airship or balloon) regardless of weight.
    * **B3:** Parachutist / skydiver
    * **B4:** Ultralight / hang-glider / paraglider - A vehicle that meets the requirements of 14 CFR § 103.1.
    * **B5:** Reserved
    * **B6:** Unmanned aerial vehicle - Any unmanned aerial vehicle or unmanned aircraft system regardless of weight.
    * **B7:** Space / trans-atmospheric vehicle
    """)

with st.expander("ADS-B aircraft category **C** information"):
    st.subheader("C Category")
    st.markdown("""
    * **C0:** No ADS-B emitter category information.
    * **C1:** Surface vehicle - emergency vehicle
    * **C2:** Surface vehicle - service vehicle
    * **C3:** Point obstacle (includes tethered balloons)
    * **C4:** Cluster obstacle
    * **C5:** Line obstacle
    * **C6:** Reserved
    * **C7:** Reserved
    """)

#st.write(fig2.data)
def center_to_bbox(center_lat, center_lon, x_adjust, y_adjust):

    if (x_adjust > 180) | (x_adjust < -180):
        return("Error, X adjustments are too big in magnitude, convert to lat/lon degrees")

    if (y_adjust > 180) | (y_adjust < -180):
        return("Error, Y adjustments are too big in magnitude, convert to lat/lon degrees")


    lower_corner = (center_lat - x_adjust, center_lon - y_adjust)
    upper_corner = (center_lat + x_adjust, center_lon + y_adjust)

    return (lower_corner[0], lower_corner[1], upper_corner[0], upper_corner[1])

def cellToBbox(cell_id, x_adjust, y_adjust):
    center = h3.cell_to_latlng(cell_id)
    return(
        center_to_bbox(center[1], center[0], x_adjust, y_adjust)
    )

st.subheader("Choose satellite box width and height")
x_adjust = st.number_input("Choose latitude Adjustment", value = 0.02)
y_adjust = st.number_input("Choose longitude Adjustment", value = 0.02)

if st.button("Show me the satellite image!"):

    tampa_box_cords = cellToBbox(h3cell_id_list[0], 
                                 x_adjust = x_adjust, 
                                 y_adjust = y_adjust)
    tampa_res = 1
    tampa_bbox = BBox(bbox = tampa_box_cords, crs=CRS.WGS84)
    tampa_size = bbox_to_dimensions(tampa_bbox, resolution=tampa_res)
    
    st.write(f"Box coordinates: {tampa_box_cords}")
    st.write(f"Image shape at {tampa_res} m resolution: {tampa_size} pixels")

    if max(tampa_size) != 2500:
        new_res = max(tampa_size) / 2500
        tampa_bbox = BBox(bbox = tampa_box_cords, crs=CRS.WGS84)
        tampa_size = bbox_to_dimensions(tampa_bbox, resolution=new_res)
        st.write(f"New Image shape at {new_res} m resolution: {tampa_size} pixels")

    evalscript_true_color = """
        //VERSION=3

        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"]
                }],
                output: {
                    bands: 3
                }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
    """

    tamp_request_tc = SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=("2023-06-12", "2023-06-13"),
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=tampa_bbox,
        size=tampa_size,
        config=config,
    )

    tamp_tc_imgs = tamp_request_tc.get_data()
    tamp = tamp_tc_imgs[0]
    st_plot_image(tamp, factor=3.5 / 255, clip_range=(0, 1))
    st.write("Image plotted")