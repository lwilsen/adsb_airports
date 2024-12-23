"""
Utils imports 
"""

from __future__ import annotations
from typing import Any
from collections import Counter
import json

from geojson import Feature, FeatureCollection
import h3
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import streamlit as st



def plot_image(
    image: np.ndarray,
    factor: float = 1.0,
    clip_range: tuple[float, float] | None = None,
    **kwargs: Any,
) -> None:
    """
    Plots an RGB image using Matplotlib.

    Args:
        image: The image data as a NumPy array.
        factor: A scaling factor to apply to the image.
        clip_range: A tuple of (min, max) values to clip the image intensities.
        **kwargs: Additional keyword arguments to pass to `plt.imshow`.
    """

    _, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])


def st_plot_image(
    image: np.ndarray,
    factor: float = 1.0,
    clip_range: tuple[float, float] | None = None,
    filename: str = "image.jpg",
    **kwargs: Any,
) -> str:
    """Utility function for plotting RGB images in a Streamlit app using Matplotlib.

    Args:
        image: The image to plot as a NumPy array.
        factor: A scaling factor to apply to the image.
        clip_range: A tuple specifying the minimum and maximum values to clip the image to.
        filename: The desired filename for the saved image.
        **kwargs: Additional keyword arguments to pass to `plt.imshow`.

    Returns:
        The path to the saved image file.
    """

    if clip_range is not None:
        image = np.clip(image * factor, *clip_range)
    else:
        image = image * factor

    # Create a Matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 10))  # Adjust figure size as needed
    ax.imshow(image, **kwargs)
    ax.axis("off")  # Turn off axis labels and ticks

    # Save the image to the specified filename
    plt.savefig(filename)

    # Display the Matplotlib figure in Streamlit
    st.pyplot(fig)

    return filename


def hexagons_dataframe_to_geojson(
    df_hex, hex_id_field, geometry_field, value_field, file_output=None
):
    """
    Converts a GeoDataFrame of hexagons to a GeoJSON FeatureCollection.

    Args:
        df_hex: The GeoDataFrame containing hexagon data.
        hex_id_field: The name of the column in `df_hex` containing hexagon IDs.
        geometry_field: The name of the column in `df_hex` containing the geometry.
        value_field: The name of the column in `df_hex` containing the value to be associated
            with each hexagon.
        file_output: Optional file path to save the GeoJSON to.

    Returns:
        A GeoJSON FeatureCollection object.
    """

    list_features = []

    for row in df_hex.iterrows():
        feature = Feature(
            geometry=row[geometry_field],
            id=row[hex_id_field],
            properties={"value": row[value_field]},
        )
        list_features.append(feature)

    feat_collection = FeatureCollection(list_features)

    if file_output is not None:
        with open(file_output, "w") as f:
            json.dump(feat_collection, f)

    else:
        return feat_collection


def cell_to_shapely(cell):
    """
    Converts an H3 cell ID to a Shapely Polygon.

    Args:
        cell: The H3 cell ID.

    Returns:
        A Shapely Polygon object representing the hexagon.
    """
    coords = h3.cell_to_boundary(cell)
    flipped = tuple(coord[::-1] for coord in coords)
    return Polygon(flipped)


def center_to_bbox(center_lat, center_lon, x_adjust, y_adjust):
    """
    Calculates the bounding box coordinates given a center point and adjustments.

    Args:
        center_lat: The latitude of the center point.
        center_lon: The longitude of the center point.
        x_adjust: The adjustment in latitude.
        y_adjust: The adjustment in longitude.

    Returns:
        A tuple of (lower_lat, lower_lon, upper_lat, upper_lon).
    """
    if (x_adjust > 180) | (x_adjust < -180):
        return (
            "Error, X adjustments are too big in magnitude, convert to lat/lon degrees"
        )

    if (y_adjust > 180) | (y_adjust < -180):
        return (
            "Error, Y adjustments are too big in magnitude, convert to lat/lon degrees"
        )

    lower_corner = (center_lat - x_adjust, center_lon - y_adjust)
    upper_corner = (center_lat + x_adjust, center_lon + y_adjust)

    return (lower_corner[0], lower_corner[1], upper_corner[0], upper_corner[1])


def cellToBbox(cell_id, x_adjust, y_adjust):
    """
    Calculates the bounding box coordinates for an H3 cell with adjustments.

    Args:
        cell_id: The H3 cell ID.
        x_adjust: The adjustment in latitude.
        y_adjust: The adjustment in longitude.

    Returns:
        A tuple of (lower_lat, lower_lon, upper_lat, upper_lon).
    """
    center = h3.cell_to_latlng(cell_id)
    return center_to_bbox(center[1], center[0], x_adjust, y_adjust)


def count_categories(categories):
    """
    Counts the occurrences of each category in a list.

    Args:
        categories: A list of categories.

    Returns:
        A Counter object containing category counts.
    """
    return Counter(categories)


def make_dfs(DISTANCE, RESOLUTION, SIGNIFICANCE, Geom_DF):
    """
    Creates a choropleth map of H3 hexagons based on given parameters and a GeoDataFrame.

    Args:
        DISTANCE: Maximum distance from a point to consider for aggregation.
        RESOLUTION: H3 resolution for hexagons.
        SIGNIFICANCE: Minimum count of points in a hexagon to be displayed.
        Geom_DF: GeoDataFrame containing spatial data.

    Returns:
        A tuple containing:
            - h3_df: Aggregated H3 cell data as a DataFrame.
            - h3_gdf: GeoDataFrame containing H3 cell geometries.
            - geojson_obj_h3_gdf: GeoJSON FeatureCollection of H3 cells.
    """

    Geom_DF = Geom_DF[Geom_DF["distance"] <= DISTANCE / 69]

    h3_df = (
        Geom_DF.groupby(f"H3_{RESOLUTION}_cell")
        .agg(
            count=(f"H3_{RESOLUTION}_cell", "size"),
            category_counts=("category", count_categories),
        )
        .reset_index()
    )

    h3_df = h3_df[h3_df["count"] >= SIGNIFICANCE]

    h3_geoms = h3_df[f"H3_{RESOLUTION}_cell"].apply(lambda x: cell_to_shapely(x))
    h3_gdf = gpd.GeoDataFrame(data=h3_df, geometry=h3_geoms, crs=4326)

    geojson_obj_h3_gdf = hexagons_dataframe_to_geojson(
        h3_gdf,
        hex_id_field=f"H3_{RESOLUTION}_cell",
        value_field="count",
        geometry_field="geometry",
    )

    return (h3_df, h3_gdf, geojson_obj_h3_gdf)
