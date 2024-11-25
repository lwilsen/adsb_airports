"""
Utilities used by example notebooks
"""
from __future__ import annotations

from geojson import Feature, Point, FeatureCollection
import json
import h3
from shapely.geometry import Polygon

from typing import Any

import matplotlib.pyplot as plt
import numpy as np

import streamlit as st


def plot_image(
    image: np.ndarray, factor: float = 1.0, clip_range: tuple[float, float] | None = None, **kwargs: Any
) -> None:
    """Utility function for plotting RGB images."""
    _, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])

def st_plot_image(image: np.ndarray, 
                  factor: float = 1.0, 
                  clip_range: tuple[float, float] | None = None, 
                  **kwargs: Any) -> None:
    """Utility function for plotting RGB images in a Streamlit app using Matplotlib."""
    if clip_range is not None:
        image = np.clip(image * factor, *clip_range)
    else:
        image = image * factor

    # Create a Matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 10))  # Adjust figure size as needed
    ax.imshow(image, **kwargs)
    ax.axis('off')  # Turn off axis labels and ticks

    # Display the Matplotlib figure in Streamlit
    st.pyplot(fig)



def hexagons_dataframe_to_geojson(df_hex, hex_id_field,geometry_field, value_field,file_output = None):

    list_features = []

    for i, row in df_hex.iterrows():
        feature = Feature(geometry = row[geometry_field],
                          id = row[hex_id_field],
                          properties = {"value": row[value_field]})
        list_features.append(feature)

    feat_collection = FeatureCollection(list_features)

    if file_output is not None:
        with open(file_output, "w") as f:
            json.dump(feat_collection, f)

    else :
      return feat_collection
    
def cell_to_shapely(cell):

    coords = h3.cell_to_boundary(cell)
    flipped = tuple(coord[::-1] for coord in coords)
    return Polygon(flipped)

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