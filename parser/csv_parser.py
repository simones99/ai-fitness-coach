import pandas as pd
import re

def find_column_value(row, keywords):
    for col in row.index:
        clean_col = col.lower().strip()
        clean_col = re.sub(r'\s*\(.*?\)', '', clean_col)  # Remove parentheses and inside
        for kw in keywords:
            if kw in clean_col and pd.notna(row[col]):
                return row[col]
    return None

def parse_csv_file(file_path):
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

    # Clean column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Clean and convert columns with European decimal format
    for col in ['latitude', 'longitude', 'elevation', 'distance']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    data = []
    for _, row in df.iterrows():
        point_data = {
            'timestamp': row.get('timestamp'),
            'date': row.get('date'),
            'iso8601': row.get('iso8601'),
            'heart_rate': find_column_value(row, ['hr', 'heart_rate']),
            'power': find_column_value(row, ['power']),
            'cadence': find_column_value(row, ['cadence']),
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'elevation': find_column_value(row, ['elevation']),
            'distance': find_column_value(row, ['distance']),
            'lap': find_column_value(row, ['lap']),
            'since_start': find_column_value(row, ['since_start']),
        }
        data.append(point_data)

    return data