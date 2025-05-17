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
        avg_heart_rate INTEGER,
        avg_cadence INTEGER,
        avg_power INTEGER,
        avg_elevation INTEGER,
        elevation_gain INTEGER,
        total_calories INTEGER
    )
    ''')
    
    # Extract date from filename using regex
    file_name = str(file.name)
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', file_name)
    extracted_date = date_match.group(0) if date_match else datetime.now().strftime("%Y-%m-%d")

    # Safely access and default stat values
    def safe_stat(key):
        return stats.get(key) if stats.get(key) is not None else 0

    total_distance = stats.get("total_distance")
    duration_min = stats.get("workout_duration")
    avg_heart_rate = stats.get("avg_heart_rate")
    avg_cadence = safe_stat("avg_cadence")
    avg_power = safe_stat("avg_power")
    avg_elevation = safe_stat("avg_elevation")
    elevation_gain = safe_stat("elevation_gain")
    total_calories = safe_stat("total_calories")

    # Insert workout data into the database
    cursor.execute("""
    INSERT INTO workouts (
        date, file_name, workout_type, total_distance, duration_min,
        avg_heart_rate, avg_cadence, avg_power, avg_elevation,
        elevation_gain, total_calories
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        extracted_date,
        file_name,
        workout_type,
        total_distance,
        duration_min,
        avg_heart_rate,
        avg_cadence,
        avg_power,
        avg_elevation,
        elevation_gain,
        total_calories,
    ))
    conn.commit()
    conn.close()