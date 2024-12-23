"""
This module provides functionality for setting up a FastAPI application, 
interacting with Sentinel Hub APIs, and working with utility functions, 
file handling, and databases.

Imports:
- **FastAPI**: The core FastAPI class to create and configure the API.
- **Request**: Used to handle HTTP requests in FastAPI routes.
- **pickle**: A module for serializing and deserializing Python objects to and 
from byte streams.
- **utils**: Custom utility functions for converting cell data to bounding boxes 
(cellToBbox) and creating DataFrames (make_dfs).
- **os**: Provides a way to interact with the operating system, including file 
and directory management.
- **sentinelhub.SHConfig**: Configuration class to set up Sentinel Hub access.
- **sentinelhub**:
    - **CRS**: Represents coordinate reference systems used in Sentinel Hub.
    - **BBox**: A class to define bounding boxes used for spatial queries.
    - **bbox_to_dimensions**: A utility function to calculate image 
    dimensions from bounding box coordinates.
- **sqlite3**: A module for interacting with SQLite databases, 
allowing queries and database management.
- **json**: A module to parse and handle JSON data.
"""
import os
import pickle
import sqlite3
from fastapi import FastAPI, Request
from utils import cellToBbox, make_dfs
from sentinelhub import SHConfig
from sentinelhub import (
    CRS,
    BBox,
    bbox_to_dimensions,
)


"""SENTINAL SETUP"""

CLIENT_ID = "139dda82-905a-4f6c-8aaa-3a6635c5216c"
CLIENT_SECRET = os.environ.get("SENTINAL_API_KEY")

config = SHConfig()

config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET
config.save("my-profile")

"""Unpickling data sets"""

with open("gdf_all_res.pkl", "rb") as f:  # resolution = 10
    gdf = pickle.load(f)

"""SQLITE3 Databse conversion"""


def get_db_connection():
    conn = sqlite3.connect("adsb_data.db")
    conn.row_factory = sqlite3.Row  # To get rows as dictionaries
    return conn


"""Fast API"""

app = FastAPI()


@app.get("/data/gdf_expanded")
def get_expanded_data():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM 'gdf_expanded'").fetchall()
    conn.close()
    return [dict(row) for row in data]


@app.post("/map")
async def handle_request(request: Request):
    """
    Processes user request for H3 grid data or bounding box information.

    Args:
        request : Request
            The FastAPI request object containing the user data.

    Returns
        dict:
            A dictionary containing the requested data or an error message.

            - If "Distance" is present in the request data:
                - "h3_df": JSON string containing H3 grid data.
                - "h3_gdf": JSON string containing GeoPandas DataFrame data.
                - "geojson_obj_h3_gdf": GeoJSON object of the H3 grid data.
            - If "x_adjust" is present in the request data:
                - "bcords_str": String containing the bounding box coordinates.
                - "nw_rs_str": (Optional) String containing the new image shape
                            information (if adjusted resolution is needed).
                - "for_st": Dictionary containing the processing parameters.
                    - "evalscript_true_color": String containing the evaluation script.
                    - "tampa_bbox": SentinelHub BBox object.
                    - "tampa_size": Tuple representing the image dimensions.
            - If an error occurs:
                - "Error during map making": String describing the error.
                - "data": The original user data.

    Raises
        Exception:
            Any exception that occurs during processing.
    """
    try:
        data = await request.json()

        if "Distance" in data.get("data"):

            params = data.get("data")

            DISTANCE = params["Distance"]
            RESOLUTION = params["Resolution"]
            SIGNIFICANCE = params["Resolution"]
            #
            h3_df, h3_gdf, geojson_obj_h3_gdf = make_dfs(
                DISTANCE, RESOLUTION, SIGNIFICANCE, Geom_DF=gdf
            )
            h3_df = h3_df.to_json(orient="records")
            h3_gdf = h3_gdf.to_json()

            return {
                "h3_df": h3_df,
                "h3_gdf": h3_gdf,
                "geojson_obj_h3_gdf": geojson_obj_h3_gdf,
            }

        if "x_adjust" in data.get("data"):
            box_params = data.get("data")

            x_adjust = box_params["x_adjust"]
            y_adjust = box_params["y_adjust"]
            cell_id = box_params["cell_id"]
            tampa_box_cords = cellToBbox(cell_id, x_adjust=x_adjust, y_adjust=y_adjust)
            tampa_res = 1
            tampa_bbox = BBox(bbox=tampa_box_cords, crs=CRS.WGS84)
            tampa_size = bbox_to_dimensions(tampa_bbox, resolution=tampa_res)

            box_coords_string = f"Box coordinates: {tampa_box_cords}"

            if max(tampa_size) != 2500:
                new_res = max(tampa_size) / 2500
                tampa_bbox = BBox(bbox=tampa_box_cords, crs=CRS.WGS84)
                tampa_size = bbox_to_dimensions(tampa_bbox, resolution=new_res)
                new_res_string = (
                    f"New Image shape at {new_res} m resolution: {tampa_size} pixels"
                )

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
            print(type(tampa_bbox))
            print(type(tampa_size))
            for_st = {
                "evalscript_true_color": evalscript_true_color,
                "tampa_bbox": tampa_bbox,
                "tampa_size": tampa_size,
                "bcords_str": box_coords_string,
                "nw_rs_str": new_res_string,
            }

            return for_st

    except Exception as e:

        return {"Error during map making": str(e), "data": data}
