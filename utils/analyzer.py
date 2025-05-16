'''import streamlit as st
import pandas as pd
from model.logger import log_workout  # Keep the import for log_workout
import os
import datetime as dt
from model.llm_handler import ask_local_llm
from parser.csv_parser import parse_csv_file  # Import the CSV parser
import sqlite3


def analyze_workout_data(workout_data, user_gender, weight_kg, height_cm, age):
    if not workout_data:
        raise ValueError("No workout data available")  # Ensure workout_data is not empty

    # Create DataFrame from workout_data
    try:
        df = pd.DataFrame(workout_data)
    except ValueError:
        raise ValueError("Workout data is improperly formatted, expected a list of dictionaries.")

    # Calculate total distance and other stats
    total_distance = df['distance'].sum()  # Assuming 'distance' is one of the columns in your CSV data
    workout_duration = len(df)  # Simple example logic for duration (number of points)

    # Average heart rate from the 'heart_rate' field
    avg_heart_rate = df['heart_rate'].mean() if 'heart_rate' in df else None

    # Average cadence and calories
    avg_cadence = df['cadence'].mean() if 'cadence' in df else None
    total_calories = estimate_total_calories_burned(user_gender, weight_kg, height_cm, age, avg_heart_rate, workout_duration)

    stats = {
        'total_distance': total_distance,
        'workout_duration': workout_duration,
        'avg_heart_rate': avg_heart_rate,
        'avg_cadence': avg_cadence,
        'total_calories': total_calories
    }

    return stats

def format_stats_for_ai(stats):
    """
    Formats workout stats into a natural language summary for input to an AI model.
    """
    summary = (
        f"In the last workout, you covered {stats['total_distance']:.2f} km "
        f"in {stats['workout_duration']} minutes. "
    )
    if stats['avg_heart_rate'] is not None:
        summary += f"Your average heart rate was {stats['avg_heart_rate']:.0f} bpm. "
    if stats['avg_cadence'] is not None:
        summary += f"Your average cadence was {stats['avg_cadence']:.0f} steps/min. "
    if stats['total_calories'] is not None:
        summary += f"You burned around {stats['total_calories']} kcal. "
    if stats['elevation'] is not None:
        summary += f"You worked out at {stats['elevation']}. "
    if stats['elevation_gain'] is not None:
        summary += f"During your workout, your elevation gain was {stats['elevation_gain']} m."
    
    summary += "Based on this performance and training history, suggest the next workout."
    return summary

def display_workout_data(uploaded_file):
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join("temp", uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Parse the workout data from CSV
        workout_data = parse_csv_file(temp_file_path)

        # Analyze the workout data
        stats = analyze_workout_data(workout_data)
        
        # Display the workout summary
        st.write("📊 Workout Summary")
        st.write(f"**Total Distance:** {stats['total_distance']:.2f} km")
        st.write(f"**Workout Duration:** {stats['workout_duration']} minutes")
        st.write(f"**Average Heart Rate:** {stats['avg_heart_rate'] if stats['avg_heart_rate'] is not None else 'N/A'} bpm")
        st.write(f"**Average Cadence:** {stats['avg_cadence'] if stats['avg_cadence'] is not None else 'N/A':.2f} steps/min")
        st.write(f"**Average Elevation:** {stats['avg_elevation'] if stats['avg_elevation'] is not None else 'N/A':.2f} m")
        st.write(f"**Elevation Gain:** {stats['elevation_gain'] if stats['elevation_gain'] is not None else 'N/A'} m")
        st.write(f"**Total Calories Burned:** {stats['total_calories'] if stats['total_calories'] is not None else 'N/A'} kcal")

        # Ask the AI for workout suggestions based on the stats
        prompt = format_stats_for_ai(stats)
        st.write("🧠 Asking AI for the next workout suggestion...")
        suggestion = ask_local_llm(prompt)
        st.write(f"**Suggested Workout:** {suggestion}")

        # Log the workout data into the SQLite database
        log_workout(temp_file_path, stats)
    else:
        st.warning("Please upload a CSV file to analyze your workout data.")

def main():
    st.title("AI Fitness Coach - Workout Analyzer")

    # File upload widget
    uploaded_file = st.file_uploader("Upload your workout CSV file", type=["csv"])

    # Display workout data and stats
    display_workout_data(uploaded_file)

if __name__ == "__main__":
    main()
'''