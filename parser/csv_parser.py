import pandas as pd

def parse_csv_file(file_path):
    """
    Parses a CSV file containing workout data and returns a list of dictionaries
    with keys like time, latitude, longitude, elevation, cadence, etc.
    """
    # Read the CSV file using tab as delimiter and handle decimal commas
    try:
        df = pd.read_csv(
            file_path,
            delimiter=';',
            decimal=',',
            engine='python',
            on_bad_lines='skip'
        )
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    # Clean and convert columns with European decimal format
    for col in ['latitude', 'longitude', 'elevation', 'distance']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Create structured data output
    data = []
    for _, row in df.iterrows():
        point_data = {
            'timestamp': row.get('timestamp'),
            'date': row.get('date'),
            'ISO8601': row.get('ISO8601'),
            'heart_rate': row.get('hr') if pd.notna(row.get('hr')) else None,
            'power': row.get('power') if pd.notna(row.get('power')) else None,
            'cadence': row.get('cadence') if pd.notna(row.get('cadence')) else None,
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'elevation': row.get('elevation'),
            'distance': row.get('distance'),
            'lap': row.get('lap') if pd.notna(row.get('lap')) else None,
            'since_start': row.get('since_start') if pd.notna(row.get('since_start')) else None
        }
        data.append(point_data)

    return data