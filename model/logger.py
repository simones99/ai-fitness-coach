import sqlite3
from datetime import datetime
from parser.csv_parser import parse_csv_file  # Updated import

def log_workout(file_path, stats):
    conn = sqlite3.connect('data/workout_log.db')
    cursor = conn.cursor()

    # Ensure table has required columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        date TEXT,
        file_name TEXT,
        total_distance REAL,
        duration_min REAL,
        avg_heart_rate REAL,
        avg_cadence REAL,
        avg_power REAL,
        avg_elevation REAL,
        elevation_gain REAL,
        total_calories REAL
    )
    ''')
    
    # Get today's date and file name
    today = datetime.now().strftime("%Y-%m-%d")
    file_name = file_path.split("/")[-1]

    # Safely access cadence and calories with .get() to avoid KeyError
    avg_cadence = stats.get('avg_cadence', None)
    total_calories = stats.get('total_calories', None)
    avg_power = stats.get('avg_power', None)
    avg_elevation = stats.get('avg_elevation', None)
    elevation_gain = stats.get('elevation_gain', None)
    # Check if cadence and calories are None, and set to 0 if so
    if avg_cadence is None:
        avg_cadence = 0
    if total_calories is None:
        total_calories = 0
    # Check if power and elevation are None, and set to 0 if so
    if avg_power is None:
        avg_power = 0
    if avg_elevation is None:
        avg_elevation = 0
    if elevation_gain is None:
        elevation_gain = 0

    # Insert workout data into the database
    cursor.execute('''
    INSERT INTO workouts (date, file_name, total_distance, duration_min, avg_heart_rate, avg_cadence, avg_power, avg_elevation, elevation_gain, total_calories)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (today, file_name, round(stats['total_distance'], 2), round(stats['workout_duration'], 1),
          stats['avg_heart_rate'], avg_cadence, avg_power, avg_elevation, elevation_gain, total_calories))
    conn.commit()
    conn.close()