import sqlite3
from datetime import datetime
from parser.csv_parser import parse_csv_file  # Updated import
from utils.stats_utils import analyze_workout_data, format_stats_for_ai
from model.llm_handler import ask_local_llm
from model.logger import log_workout  # Updated import

"""# Initialize SQLite database and create the workouts table if not already created
def init_db():
    conn = sqlite3.connect('data/workout_log.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        file_name TEXT,
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
    conn.commit()
    conn.close()
"""
"""
def main():
    # Initialize DB and ensure the table is there
    init_db()

    # File upload and parsing
    uploaded_file = input("Enter the path to your CSV file (e.g., data/run1.csv): ").strip()  # Updated prompt

    if not uploaded_file:
        print("❌ No file selected.")
        return

    workout_data = parse_csv_file(uploaded_file)  # Updated parser function
    stats = analyze_workout_data(workout_data)
    
    # Display workout summary
    print(f"Workout summary: {stats}")

    # Generate AI prompt
    prompt = format_stats_for_ai(stats)
    
    # Get workout suggestion from AI
    suggestion = ask_local_llm(prompt)
    print("Suggested workout:", suggestion)

    # Log the workout in SQLite
    log_workout(uploaded_file, stats)

if __name__ == "__main__":
    main()
"""