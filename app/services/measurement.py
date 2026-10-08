import json
import math

import geopandas as gpd
import pandas as pd


def prepare_for_measurement(gdf: gpd.GeoDataFrame):

    if gdf.crs is None:
        raise ValueError("Input file does not contain a CRS.")

    if gdf.empty:
        raise ValueError("Input file does not contain any features.")

    if gdf.crs.is_geographic:

        projected_crs = gdf.estimate_utm_crs()

        if projected_crs is None:
            raise ValueError(
                "Could not determine a suitable projected CRS."
            )

        return gdf.to_crs(projected_crs)

    return gdf


def clean_value(value):

    # Convert missing values such as NaN and NaT to JSON null.
    if pd.isna(value):
        return None

    # Convert NumPy numeric values to normal Python numbers.
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass

    # JSON does not support infinity.
    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def calculate_measurements(gdf: gpd.GeoDataFrame):

    measurement_gdf = prepare_for_measurement(gdf)

    results = []

    for index, row in measurement_gdf.iterrows():

        geometry = row.geometry

        properties = {}

        for column in gdf.columns:

            if column == "geometry":
                continue

            value = clean_value(row[column])
            properties[column] = value

        if geometry is None:

            results.append({
                "feature_id": int(index),
                "geometry_type": "Unknown",
                "properties": json.dumps(properties),
                "geometry": None,
                "area": None,
                "length": None,
                "message": "Feature has no geometry."
            })

            continue

        geometry_type = geometry.geom_type

        result = {
            "feature_id": int(index),
            "geometry_type": geometry_type,
            "properties": json.dumps(properties),
            "geometry": geometry.wkt,
            "area": None,
            "length": None,
            "message": None
        }

        if geometry_type == "Polygon":

            result["area"] = geometry.area

        elif geometry_type == "LineString":

            result["length"] = geometry.length

        elif geometry_type == "Point":

            result["message"] = (
                "Point geometry does not have area or length."
            )

        elif geometry_type == "MultiPolygon":

            result["area"] = geometry.area

        elif geometry_type == "MultiLineString":

            result["length"] = geometry.length

        elif geometry_type == "MultiPoint":

            result["message"] = (
                "MultiPoint geometry does not have area or length."
            )

        else:

            result["message"] = (
                f"Measurement not supported for {geometry_type}."
            )

        results.append(result)

    return results