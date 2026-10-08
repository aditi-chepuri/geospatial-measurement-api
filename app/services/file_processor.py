import os
import zipfile
import tempfile

import geopandas as gpd


ALLOWED_EXTENSIONS = {".zip", ".kml"}


def process_file(file_path: str, filename: str):
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only .zip and .kml files are supported.")

    # KML file
    if extension == ".kml":
        gdf = gpd.read_file(file_path, driver="KML")
        return gdf

    # ZIP file containing Shapefile
    with tempfile.TemporaryDirectory() as temp_dir:

        with zipfile.ZipFile(file_path, "r") as zip_ref:

            # Security check:
            # Prevent files from being extracted outside temp_dir.
            for member in zip_ref.infolist():

                member_path = os.path.abspath(
                    os.path.join(temp_dir, member.filename)
                )

                if not member_path.startswith(
                    os.path.abspath(temp_dir) + os.sep
                ):
                    raise ValueError(
                        "ZIP file contains an unsafe file path."
                    )

            zip_ref.extractall(temp_dir)

        # Find Shapefiles inside the ZIP
        shapefiles = []

        for root, _, files in os.walk(temp_dir):
            for file in files:

                if file.lower().endswith(".shp"):
                    shapefiles.append(
                        os.path.join(root, file)
                    )

        if not shapefiles:
            raise ValueError(
                "ZIP file does not contain a Shapefile."
            )

        if len(shapefiles) > 1:
            raise ValueError(
                "ZIP file contains multiple Shapefiles."
            )

        shp_path = shapefiles[0]

        gdf = gpd.read_file(shp_path)

        return gdf