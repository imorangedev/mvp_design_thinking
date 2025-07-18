import geopandas as gpd
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import json

from shapely.geometry import Point
from pathlib import Path
from geopy.distance import geodesic
from typing import List, Tuple, Optional
from datetime import datetime

METADATA_PATH = "/Users/diegonaranjo/Documents/master/misw4408_design_thinking/mvp_design_thinking/data/metadata.json"
FOLDER_PATH = Path("/Users/diegonaranjo/Documents/master/misw4408_design_thinking/mvp_design_thinking/data")
kml_files = list(FOLDER_PATH.glob("*.kml"))

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

def get_metadata(metadata_path: str | Path) -> dict:
    """
    Reads metadata from a JSON file and returns it as a dictionary.
    """
    metadata_path = Path(metadata_path)
    with open(metadata_path, 'r') as f:
        return json.load(f)

def main():

    metadata = get_metadata(METADATA_PATH)
    combined_df = pd.DataFrame()

    for file in kml_files:

        file_id = file.stem.split('- ')[-1]
        date_str = file.stem.split('-')[0]
        date_obj = datetime.strptime(date_str, "%Y%m%d").date()
        coords = extract_kml_coordinates(file)
        print(f"Extracted {len(coords)} coordinate triples.")

        time = next((item['time'] for item in metadata['time'] if item['file'] == file_id), None)
        print(time)

        df = coords_to_geodataframe(coords)
        df['file_id'] = file_id 
        df['date'] = date_obj
        df = velocity_column(df, int(time))
        combined_df = pd.concat([combined_df, df], ignore_index=True)
        df.to_csv(f"./results/mvp_output_{file_id}.csv", index=False)
        # print(df.head(10))
        # print(coords[:5])

    print(combined_df.head(10))
    combined_df.to_csv("./results/mvp_output_combined.csv", index=False)

if __name__ == "__main__":

    main()





