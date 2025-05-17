import streamlit as st
import pandas as pd
import sqlite3
from parser.csv_parser import parse_csv_file  
from utils.stats_utils import analyze_workout_data, format_stats_for_ai, extract_text_after_tag
from model.llm_handler import ask_local_llm
from model.logger import log_workout
from visualisations.calendar import plot_workout_by_weekday_heatmap, plot_calendar_month_heatmap
from visualisations.charts import plot_monthly_workout_volume, plot_workout_type_distribution
import os
import re

# Function to initialize SQLite database and create the workouts table if not already created
def init_db():
    conn = sqlite3.connect('data/workout_log.db')
    cursor = conn.cursor()
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
def display_workout_data(uploaded_file, user_gender, weight_kg, height_cm, age, fitness_goal, fitness_level, workout_preference, has_injury, weekly_availability, time_per_session, target_focus):
    # Save the uploaded file temporarily
    temp_file_path = "temp.csv"  # Updated to handle CSV file
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Parse and analyze the CSV file
    workout_data = parse_csv_file(uploaded_file)  # Updated function to parse CSV
    stats = analyze_workout_data(workout_data, user_gender, weight_kg, height_cm, age)
    
    # Display stats
    if stats.get('workout_type') is not None:
        st.subheader(f"📊 Summary of the Last {stats['workout_type'].capitalize()} Workout")
    else:
        st.subheader("📊 Last Workout Summary")
    st.write(f"**Distance**: {stats['total_distance']/1000:.2f} km")
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
     
    # Infer workout type from file name or let user select
    file_name = uploaded_file.name.lower()
    if "outdoor" in file_name and "run" in file_name:
        inferred_type = "Outdoor Run"
    elif "outdoor" in file_name and "walk" in file_name:
        inferred_type = "Outdoor Walk"
    elif "functional" in file_name and "strength" in file_name:
        inferred_type = "Functional Strength Training"
    elif "indoor" in file_name and "run" in file_name:
        inferred_type = "Indoor Running"
    elif "indoor" in file_name and "cycling" in file_name: 
        inferred_type = "Indoor Cycling"
    elif "indoor" in file_name and "walk" in file_name:
        inferred_type = "Indoor Walk"
    elif "traditional" in file_name and "strength" in file_name:
        inferred_type = "Traditional Strength Training"
    elif "outdoor" in file_name and "cycling" in file_name:
        inferred_type = "Outdoor Cycling"
    elif "hiking" in file_name or "trekking" in file_name:
        inferred_type = "Hiking"
    elif "swimming" in file_name:  
        inferred_type = "Swimming"
    elif "yoga" in file_name:
        inferred_type = "Yoga"
    elif "tennis" in file_name:
        inferred_type = "Tennis"
    else:
        inferred_type = None

    if inferred_type:
        workout_type = inferred_type
    else:
        workout_type = st.selectbox("Select the type of workout", [
            "Outdoor Run", "Indoor Run", "Outdoor Walk", "Indoor Walk", "Wheelchair Walk Pace", "Wheelchair Run Pace",
            "Outdoor Cycle", "Indoor Cycle",
            "Pool Swim", "Open Water Swim",
            "Traditional Strength Training", "Functional Strength Training", "Core Training", "High Intensity Interval Training (HIIT)",
            "Cross Training", "Step Training", "Stepper", "Stair Stepper", "Mixed Cardio", "Cool Down", "Stretching", "Flexibility",
            "Yoga", "Pilates", "Tai Chi", "Mind & Body",
            "Elliptical", "Rower",
            "Dance", "Social Dance", "Barre",
            "Kickboxing", "Boxing", "Martial Arts", "Wrestling",
            "Basketball", "Soccer", "Tennis", "Volleyball", "Baseball", "Softball", "Handball", "Lacrosse", "Rugby", "Hockey",
            "American Football", "Australian Football", "Cricket", "Squash", "Table Tennis", "Badminton", "Racquetball",
            "Alpine Skiing", "Cross-Country Skiing", "Downhill Skiing", "Snowboarding", "Snow Sports", "Surfing", "Water Fitness",
            "Water Polo", "Water Sports", "Paddling", "Sailing", "Fishing",
            "Hiking", "Climbing", "Equestrian Sports", "Hunting", "Archery",
            "Gymnastics", "Fencing", "Curling", "Disc Sports", "Jump Rope", "Rolling", "Play", "Skating", "Multisport", "Other Activity"
        ])     

    # Extract date from filename using regex
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
    if date_match:
        workout_date = date_match.group(1)
    else:
        workout_date = st.date_input("Select the date of the workout").strftime("%Y-%m-%d")

    # Insert workout visualisations here (after stats and before AI prompt)
    workout_log = fetch_workout_log()
    if not workout_log.empty:
        st.subheader("📊 Last Workout in Context")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Weekday vs. Week Number")
            plot_workout_by_weekday_heatmap(workout_log)

        with col2:
            st.markdown("### Day of Month vs. Month")
            plot_calendar_month_heatmap(workout_log)

        st.subheader("📈 Workout Insights")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### Monthly Workout Volume")
            plot_monthly_workout_volume(workout_log)

        with col4:
            st.markdown("### Workout Type Distribution")
            plot_workout_type_distribution(workout_log, workout_type)
    else:
        st.warning("No old workout data available to display visualisations.")
        
    # Generate AI prompt and display the workout suggestion
    prompt = format_stats_for_ai(stats, user_gender, age, weight_kg, height_cm, fitness_goal, workout_type, fitness_level, workout_preference, has_injury, weekly_availability, time_per_session, target_focus)
    st.subheader("🤖 AI Suggested Workout")
    with st.spinner("Thinking..."):
        # Call the AI function directly
        try:
            suggestion = ask_local_llm(prompt)
            suggested_workout = extract_text_after_tag(suggestion, r'</think>')
        except Exception as e:
            error_msg = f"Error processing workout: {e}"
            print(error_msg)
    st.success(suggested_workout)

    # Log workout in SQLite
    log_workout(uploaded_file, stats, workout_type)

    # Remove the temp file after processing
    os.remove(temp_file_path)
    

# Streamlit app layout
st.title("🏃 AI Fitness Coach")

st.sidebar.header("User Information")
user_gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
weight_kg = st.sidebar.number_input("Weight (kg)", min_value=30, max_value=200, step=1)
height_cm = st.sidebar.number_input("Height (cm)", min_value=100, max_value=250, step=1)
age = st.sidebar.number_input("Age", min_value=10, max_value=100, step=1)
fitness_goal = st.sidebar.selectbox("Fitness Goal", ["Gain muscle", "Lose weight", "Maintain form"])
fitness_level = st.sidebar.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
workout_preference = st.sidebar.selectbox("Workout Preference", ["No preference", "Outdoor", "Indoor", "Low impact", "High intensity"])
has_injury = st.sidebar.text_input("Injury or limitations (optional)")
weekly_availability = st.sidebar.slider("Days available to train per week", 1, 7, 3)
time_per_session = st.sidebar.slider("Time per workout session (minutes)", 15, 120, 45, step=15)
target_focus = st.sidebar.selectbox("Primary fitness goal", ["Endurance", "Strength", "Flexibility", "Cardio", "General fitness"])


init_db()

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")  # Updated to accept CSV files

if uploaded_file:
    display_workout_data(uploaded_file, user_gender, weight_kg, height_cm, age, fitness_goal, fitness_level, workout_preference, has_injury, weekly_availability, time_per_session, target_focus)

# Display past workout log
st.subheader("📜 Workout Log")
workout_log = fetch_workout_log()

if workout_log.empty:
    st.write("No past workout data found.")
else:
    st.dataframe(workout_log)