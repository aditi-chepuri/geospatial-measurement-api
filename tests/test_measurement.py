import unittest

import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

from app.services.measurement import (
    prepare_for_measurement,
    calculate_measurements
)


class TestMeasurement(unittest.TestCase):

    def setUp(self):
        self.polygon = Polygon([
            (78.4700, 17.4000),
            (78.4800, 17.4000),
            (78.4800, 17.4100),
            (78.4700, 17.4100),
            (78.4700, 17.4000)
        ])

        self.line = LineString([
            (78.4700, 17.4000),
            (78.4800, 17.4000)
        ])

        self.point = Point(78.4750, 17.4050)

    def test_polygon_area(self):
        gdf = gpd.GeoDataFrame(
            {"name": ["Test Polygon"]},
            geometry=[self.polygon],
            crs="EPSG:4326"
        )

        result = calculate_measurements(gdf)

        self.assertEqual(result[0]["geometry_type"], "Polygon")
        self.assertIsNotNone(result[0]["area"])
        self.assertGreater(result[0]["area"], 0)

    def test_linestring_length(self):
        gdf = gpd.GeoDataFrame(
            {"name": ["Test Line"]},
            geometry=[self.line],
            crs="EPSG:4326"
        )

        result = calculate_measurements(gdf)

        self.assertEqual(result[0]["geometry_type"], "LineString")
        self.assertIsNotNone(result[0]["length"])
        self.assertGreater(result[0]["length"], 0)

    def test_point_has_no_measurement(self):
        gdf = gpd.GeoDataFrame(
            {"name": ["Test Point"]},
            geometry=[self.point],
            crs="EPSG:4326"
        )

        result = calculate_measurements(gdf)

        self.assertEqual(result[0]["geometry_type"], "Point")
        self.assertIsNone(result[0]["area"])
        self.assertIsNone(result[0]["length"])
        self.assertIsNotNone(result[0]["message"])

    def test_geographic_crs_is_projected(self):
        gdf = gpd.GeoDataFrame(
            {"name": ["Test Polygon"]},
            geometry=[self.polygon],
            crs="EPSG:4326"
        )

        projected_gdf = prepare_for_measurement(gdf)

        self.assertFalse(projected_gdf.crs.is_geographic)

    def test_missing_crs(self):
        gdf = gpd.GeoDataFrame(
            {"name": ["Test Polygon"]},
            geometry=[self.polygon]
        )

        with self.assertRaises(ValueError):
            prepare_for_measurement(gdf)


if __name__ == "__main__":
    unittest.main()
