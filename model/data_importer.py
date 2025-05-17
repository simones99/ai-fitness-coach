import pandas as pd
import os

def load_csv_file(file_path):
    """
    Loads and parses a CSV file and returns a list of data.
    """
    # Read the CSV file into a DataFrame, assuming tab-delimited or comma-delimited data
    df = pd.read_csv(file_path, delimiter=';')  # Update delimiter as per CSV format (use ',' if it's comma-delimited)

    # Extract relevant data from the DataFrame and return it as a list of dictionaries
    data = []
    for _, row in df.iterrows():
        point_data = {
            'timestamp': row['timestamp'],
            'date': row['date'],
            'ISO8601': row['ISO8601'],
            'heart_rate': row['heart_rate'] if pd.notna(row['heart_rate']) else None,
            'power': row['power'] if pd.notna(row['power']) else None,
            'cadence': row['cadence'] if pd.notna(row['cadence']) else None,
            'latitude': row['latitude'] if pd.notna(row['latitude']) else None,
            'longitude': row['longitude'] if pd.notna(row['longitude']) else None,
            'elevation': row['elevation'] if pd.notna(row['elevation']) else None,
            'distance': row['distance'] if pd.notna(row['distance']) else None,
            'lap': row['lap'] if pd.notna(row['lap']) else None,
            'since_start': row['since_start'] if pd.notna(row['since_start']) else None
        }
        data.append(point_data)

    return data