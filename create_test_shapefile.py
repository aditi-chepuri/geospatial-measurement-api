import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point
import os
import zipfile


# Create test geometries
polygon = Polygon([
    (78.4700, 17.4000),
    (78.4800, 17.4000),
    (78.4800, 17.4100),
    (78.4700, 17.4100),
    (78.4700, 17.4000)
])

line = LineString([
    (78.4700, 17.4000),
    (78.4800, 17.4000)
])

point = Point(78.4750, 17.4050)


# Create GeoDataFrame
gdf = gpd.GeoDataFrame(
    {
        "name": ["Test Polygon", "Test Line", "Test Point"],
        "type": ["polygon", "line", "point"]
    },
    geometry=[polygon, line, point],
    crs="EPSG:4326"
)


# Create test folder
os.makedirs("test_shapefile", exist_ok=True)


# Shapefile path
shapefile_path = "test_shapefile/test_data.shp"


# Save Shapefile
# Shapefiles normally contain one geometry type per file,
# so create separate files for each geometry type.

polygon_gdf = gdf[gdf["type"] == "polygon"]
line_gdf = gdf[gdf["type"] == "line"]
point_gdf = gdf[gdf["type"] == "point"]


polygon_gdf.to_file(
    "test_shapefile/polygon.shp",
    driver="ESRI Shapefile"
)

line_gdf.to_file(
    "test_shapefile/line.shp",
    driver="ESRI Shapefile"
)

point_gdf.to_file(
    "test_shapefile/point.shp",
    driver="ESRI Shapefile"
)


# ZIP only the polygon Shapefile components
# because our API expects one Shapefile per ZIP.

files_to_zip = [
    "test_shapefile/polygon.shp",
    "test_shapefile/polygon.shx",
    "test_shapefile/polygon.dbf",
    "test_shapefile/polygon.prj"
]


with zipfile.ZipFile(
    "test_shapefile.zip",
    "w"
) as zip_file:

    for file in files_to_zip:
        zip_file.write(
            file,
            arcname=os.path.basename(file)
        )


print("Test Shapefile created successfully.")
print("Created: test_shapefile.zip")