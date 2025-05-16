import streamlit as st
import pandas as pd
import sqlite3
from parser.csv_parser import parse_csv_file  
from utils.stats_utils import analyze_workout_data, format_stats_for_ai
from model.llm_handler import ask_local_llm
from model.logger import log_workout
import os

# Function to initialize SQLite database and create the workouts table if not already created
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
        cadence INTEGER,
        power INTEGER,
        elevation INTEGER,
        calories INTEGER
    )
    ''')
    conn.commit()
    conn.close()

# Function to fetch workout log from SQLite
def fetch_workout_log():
    conn = sqlite3.connect('data/workout_log.db')
    query = "SELECT * FROM workouts ORDER BY date DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Function to display workout data and AI suggestion
def display_workout_data(uploaded_file, user_gender, weight_kg, height_cm, age):
    # Save the uploaded file temporarily
    temp_file_path = "temp.csv"  # Updated to handle CSV file
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Parse and analyze the CSV file
    workout_data = parse_csv_file(temp_file_path)  # Updated function to parse CSV
    stats = analyze_workout_data(workout_data, user_gender, weight_kg, height_cm, age)
    
    # Display stats
    st.subheader("📊 Workout Summary")
    st.write(f"**Distance**: {stats['total_distance']:.2f} km")
    st.write(f"**Duration**: {stats['workout_duration']:.1f} min")
    if stats.get('avg_heart_rate'):  # Use .get() to avoid KeyError
        st.write(f"**Avg HR**: {stats['avg_heart_rate']:.0f} bpm")
    
    # Handle cadence
    if stats.get('avg_cadence') is not None:
        st.write(f"**Cadence**: {stats['avg_cadence']:.0f} steps/min")
    else:
        st.write("**Cadence**: Not available")
    
    # Handle calories
    if stats.get('total_calories') is not None:
        st.write(f"**Calories burned**: {stats['total_calories']:.0f} kcal")
    else:
        st.write("**Calories burned**: Not available")

    # Handle power
    if stats.get('avg_power') is not None:
        st.write(f"**Power**: {stats['avg_power']:.0f} W")
    else:   
        st.write("**Power**: Not available")
    # Handle elevation  
    if stats.get('avg_elevation') is not None:
        st.write(f"**Average Elevation**: {stats['avg_elevation']:.0f} m")
    else:
        st.write("**Elevation**: Not available")
    # Handle elevation gain
    if stats.get('elevation_gain') is not None:
        st.write(f"**Elevation Gain**: {stats['elevation_gain']:.0f} m")
    else:
        st.write("**Elevation Gain**: Not available")
     
    # Generate AI prompt and display the workout suggestion
    prompt = format_stats_for_ai(stats)
    st.subheader("🤖 AI Suggested Workout")
    with st.spinner("Thinking..."):
        suggestion = ask_local_llm(prompt)
    st.success(suggestion)

    # Log workout in SQLite
    log_workout(temp_file_path, stats)

    # Optionally, remove the temp file after processing
    os.remove(temp_file_path)
    

# Streamlit app layout
st.title("🏃 AI Fitness Coach")

st.sidebar.header("User Information")
user_gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
weight_kg = st.sidebar.number_input("Weight (kg)", min_value=30, max_value=200, step=1)
height_cm = st.sidebar.number_input("Height (cm)", min_value=100, max_value=250, step=1)
age = st.sidebar.number_input("Age", min_value=10, max_value=100, step=1)

user_ready = st.sidebar.button("Continue")

if not user_ready:
    st.stop()

# Initialize DB and ensure the table is there
init_db()

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")  # Updated to accept CSV files

if uploaded_file:
    display_workout_data(uploaded_file, user_gender, weight_kg, height_cm, age)

# Display past workout log
st.subheader("📜 Workout Log")
workout_log = fetch_workout_log()

if workout_log.empty:
    st.write("No past workout data found.")
else:
    st.dataframe(workout_log)