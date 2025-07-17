import geopandas as gpd
import numpy as np
import xml.etree.ElementTree as ET

from shapely.geometry import Point
from pathlib import Path
from geopy.distance import geodesic
from typing import List, Tuple, Optional

KML_PATH = "/Users/diegonaranjo/Documents/master/misw4408_design_thinking/mvp_design_thinking/20250716-220345 - Test.kml"
TOTAL_TIME_SEC = 5*60+49

def extract_kml_coordinates(kml_path: str | Path) -> List[Tuple[float, float, Optional[float]]]:
    """
    Parse a KML file and return a list of (lon, lat, alt) tuples.
    Alt is None if not present.
    """
    kml_path = Path(kml_path)
    tree = ET.parse(kml_path)
    root = tree.getroot()

    # Common KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    coords: List[Tuple[float, float, Optional[float]]] = []

    # Find every <coordinates> element in the document
    for coord_elem in root.findall('.//kml:coordinates', ns):
        text = (coord_elem.text or '').strip()
        if not text:
            continue

        # Coordinates can be separated by spaces/newlines
        for token in text.split():
            # Each token is "lon,lat[,alt]"
            parts = token.split(',')
            if len(parts) < 2:
                continue
            try:
                lon = float(parts[0])
                lat = float(parts[1])
            except ValueError:
                continue  # skip malformed

            alt = None
            if len(parts) >= 3 and parts[2] != '':
                try:
                    alt = float(parts[2])
                except ValueError:
                    pass

            coords.append((lon, lat, alt))

    return coords

def coords_to_geodataframe(coords):
    """
    coords: list of (lon, lat, alt)
    returns: GeoDataFrame (2D: lon/lat)
    """
    # Drop altitude for geometry; keep in column
    records = []
    for lon, lat, alt in coords:
        records.append({'lon': lon, 'lat': lat, 'alt': alt, 'geometry': Point(lon, lat)})
    gdf = gpd.GeoDataFrame(records, geometry='geometry', crs='EPSG:4326')
    return gdf

def compute_distance(p1: Point, p2: Point) -> float:
    """Returns geodesic distance in meters between two Points."""
    return geodesic((p1.y, p1.x), (p2.y, p2.x)).meters

def velocity_column(df, total_time):

    num_points = len(df)
    distances = [0.0]  # First point has 0 distance
    dt = total_time / (num_points - 1)  # Time interval between points

    for i in range(1, num_points):
        d = compute_distance(df.geometry.iloc[i-1], df.geometry.iloc[i])
        distances.append(d)

    df['distance_m'] = distances
    df['velocity_mps'] = df['distance_m'] / dt  # velocity in m/s
    df['velocity_kph'] = df['velocity_mps'] * 3.6  # optional: km/h

    # Compute acceleration
    df['acceleration_mps2'] = df['velocity_mps'].diff() / dt

    return df

def main():
    coords = extract_kml_coordinates(KML_PATH)
    print(f"Extracted {len(coords)} coordinate triples.")

    df = coords_to_geodataframe(coords)
    df = velocity_column(df, TOTAL_TIME_SEC)
    print(df.head(10))
    # print(coords[:5])

if __name__ == "__main__":

    main()