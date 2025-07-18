import pandas as pd

from pathlib import Path

FOLDER_PATH = Path("/Users/diegonaranjo/Documents/master/misw4408_design_thinking/mvp_design_thinking/results")
csv_files = list(FOLDER_PATH.glob("*.csv"))
FILE_PATH = "/Users/diegonaranjo/Documents/master/misw4408_design_thinking/mvp_design_thinking/results/mvp_output_p1.csv"

def main():

    dict_files = {"linestring": [],
                  "file_name": [],
                  "test_id": []}

    for count, f in enumerate(csv_files, start=1):
        df = read_data(f)
        linestring = build_linestring_wkt(df)
        dict_files["linestring"].append(linestring)
        dict_files["file_name"].append(f.name)
        dict_files["test_id"].append(count)  # Assuming
    
    df = dict_to_dataframe(dict_files)
    safe_dataframe_to_csv(df, "./results/mvp_output_linestrings.csv")
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
    coords = [f"{lon} {lat}" for lon, lat in zip(df['lon'], df['lat'])]
    wkt = f"LINESTRING({', '.join(coords)})"
    return wkt

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
    df.to_csv(file_path, index=False)


if __name__ == "__main__":
    main()

