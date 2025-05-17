import sqlite3
from datetime import datetime
import re
from parser.csv_parser import parse_csv_file  # Updated import

def log_workout(file, stats, workout_type):
    conn = sqlite3.connect('data/workout_log.db')
    cursor = conn.cursor()

    # Ensure table has required columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        file_name TEXT,
        workout_type TEXT,
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
    
    # Extract date from filename using regex
    file_name = str(file.name)
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', file_name)
    if date_match:
        extracted_date = date_match.group(0)
    else:
        extracted_date = datetime.now().strftime("%Y-%m-%d")

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
    cursor.execute("""
    INSERT INTO workouts (
        date, file_name, workout_type, total_distance, duration_min,
        avg_heart_rate, avg_cadence, avg_power, avg_elevation,
        elevation_gain, total_calories
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        extracted_date,
        file.name,
        workout_type,
        stats.get("total_distance"),
        stats.get("workout_duration"),
        stats.get("avg_heart_rate"),
        stats.get("avg_cadence"),
        stats.get("avg_power"),
        stats.get("avg_elevation"),
        stats.get("elevation_gain"),
        stats.get("total_calories"),
    ))
    conn.commit()
    conn.close()