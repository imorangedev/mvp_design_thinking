import pandas as pd

from pathlib import Path
from shapely.geometry import LineString

FOLDER_PATH = Path("/Users/diegonaranjo/Documents/master/misw4408_design_thinking/mvp_design_thinking/results")
csv_files = list(FOLDER_PATH.glob("*.csv"))
FILE_PATH = "/Users/diegonaranjo/Documents/master/misw4408_design_thinking/mvp_design_thinking/results/mvp_output_p1.csv"

def main():

    dict_files = {"linestring": [],
                  "file_name": [],
                  "file_id": [],
                  "test_id": []}

    for count, f in enumerate(csv_files, start=1):
        df = read_data(f)
        linestring = build_linestring_wkt(df)
        dict_files["linestring"].append(linestring)
        dict_files["file_name"].append(f.name)
        file_id = f.stem.split("_")[-1]
        dict_files["file_id"].append(file_id)
        dict_files["test_id"].append(count)  # Assuming
    
    df = dict_to_dataframe(dict_files)
    safe_dataframe_to_csv(df, "./results/linestring/mvp_output_linestrings.xlsx")
    print(df)

def read_data(file_path: str) -> pd.DataFrame:
    """
    Reads data from a CSV file and returns a DataFrame.
    """
    return pd.read_csv(file_path)

def build_linestring_wkt(df):
    """
    Expects df with columns 'lon' and 'lat'
    Returns a LINESTRING WKT string
    """
    # Create a list of (lon, lat) tuples
    coords = [(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]
    # Create and return a LineString object
    return LineString(coords)

def dict_to_dataframe(dict_data):
    """
    Converts a dictionary to a DataFrame.
    """
    return pd.DataFrame(dict_data)

def safe_dataframe_to_csv(df: pd.DataFrame, file_path: str):
    """
    Saves a DataFrame to a CSV file, ensuring the directory exists.
    """
    folder = Path(file_path).parent
    folder.mkdir(parents=True, exist_ok=True)
    df.to_excel(file_path)


if __name__ == "__main__":
    main()

