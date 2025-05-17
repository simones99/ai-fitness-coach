import pandas as pd
import streamlit as st
import numpy as np
import os
import re
import datetime as dt
from model.llm_handler import ask_local_llm
from model.logger import log_workout  # Updated import
from parser.csv_parser import parse_csv_file  # Import the CSV parser
import sqlite3

def calculate_bmr(user_gender, weight_kg, height_cm, age):
    '''
    # Calculate BMR using the Harris-Benedict equation for men or women
    '''
    if user_gender == 'male':
        bmr = 66.5 + (0.0144 * weight_kg) + (0.0238 * height_cm) - (0.0006 * age)
    else:
        bmr = 655.1 + (0.0096 * weight_kg) + (0.0175 * height_cm) - (0.0002 * age)

    return bmr 

def calculate_act_int_factor(age, avg_heart_rate):
    ''' 
    Calculate activity intensity factor based on heart rate
    '''
    max_heart_rate = 220 - age  # Approximate maximum heart rate
    target_hr_reserve = max_heart_rate * 0.65  # Assuming moderate-intensity workout
    high_intensity_threshold = max_heart_rate * 0.85

    if avg_heart_rate <= target_hr_reserve:
        activity_intensity_factor = 0.6
    elif (avg_heart_rate > target_hr_reserve) and (avg_heart_rate <= high_intensity_threshold):
        activity_intensity_factor = 1.0
    else:
        activity_intensity_factor = 1.4  # Example for very high intensity
    
    return activity_intensity_factor

def estimate_total_calories_burned(user_gender, weight, height_cm, age, activity_intensity, workout_duration):
    """
    Estimate total calories burned using MET values based on activity intensity.
    """
    # Use MET values based on activity intensity
    intensity_to_met = {
        "low": 3.5,       # e.g., walking or light cycling
        "moderate": 6.0,  # e.g., jogging, steady cycling
        "high": 8.0       # e.g., running, intense cardio
    }

    met = intensity_to_met.get(str(activity_intensity).lower(), 6.0)  # Default to moderate if unknown

    duration_hours = workout_duration / 60.0

    total_calories = met * weight * duration_hours

    return total_calories

def analyze_workout_data(workout_data, user_gender, weight_kg, height_cm, age):
    if not workout_data:
        raise ValueError("No workout data available")  # Ensure workout_data is not empty

    # Create DataFrame from workout_data
    try:
        df = pd.DataFrame(workout_data)
    except ValueError:
        raise ValueError("Workout data is improperly formatted, expected a list of dictionaries.")

    # Calculate total distance and other stats
    if 'distance' in df and not df['distance'].empty:
        total_distance = float(df['distance'].max())
    else:
        total_distance = 0.0
    df['date'] = pd.to_datetime(df['date'])
    workout_duration = (df.loc[len(df) - 1, 'date'] - df.loc[0, 'date']).total_seconds() / 60

    # Average heart rate from the 'heart_rate' field
    avg_heart_rate = df['heart_rate'].mean() if 'heart_rate' in df else None

    # Average cadence and calories
    avg_cadence = df['cadence'].mean() if 'cadence' in df else None
    avg_power = df['power'].mean() if 'power' in df else None
    total_calories = estimate_total_calories_burned(user_gender, weight_kg, height_cm, age, avg_heart_rate, workout_duration)

   # Elevation and Elevation Gain
    avg_elevation = df['elevation'].mean() if 'elevation' in df else None
    elevation_gain = (df['elevation'].max() - df['elevation'].min()) if 'elevation' in df else None


    stats = {
        'total_distance': total_distance,
        'workout_duration': workout_duration,
        'avg_heart_rate': avg_heart_rate,
        'avg_cadence': avg_cadence,
        'avg_power': avg_power,
        'avg_elevation': avg_elevation,
        'elevation_gain': elevation_gain,
        'total_calories': total_calories
    }

    return stats

def format_stats_for_ai(stats, user_gender, age, weight_kg, height_cm, fitness_goal, workout_type, fitness_level, workout_preference, has_injury, weekly_availability, time_per_session, target_focus):
    """
    Formats workout stats into a natural language summary for input to an AI model.
    """
    summary = (
        f"User profile: {fitness_level.lower()} level, goal is to {fitness_goal.lower()} with a focus on {target_focus.lower()}. "
        f"Prefers {workout_preference.lower()} workouts, available {weekly_availability} days/week for {time_per_session} minutes per session. "
    )
    summary += f"Your goal is to {fitness_goal.lower()}. This was a {workout_type.lower()} workout. "
    summary += (
        f"You are a {user_gender} and you are {age} years old."
        f"You weigh {weight_kg} kg and are {height_cm} m tall."
        f"In the last workout, you covered {stats['total_distance']:.2f} m "
        f"in {stats['workout_duration']} minutes. "
    )
    if stats['avg_heart_rate'] is not None:
        summary += f"Your average heart rate was {stats['avg_heart_rate']:.0f} bpm. "
    if stats['avg_cadence'] is not None:
        summary += f"Your average cadence was {stats['avg_cadence']:.0f} steps/min. "
    if stats['avg_power'] is not None:
        summary += f"Your average power output was {stats['avg_power']:.0f} watts. "
    if stats['total_calories'] is not None:
        summary += f"You burned around {stats['total_calories']} kcal. "
    if stats['avg_elevation'] is not None:
        summary += f"You worked out at {stats['avg_elevation']:.0f}. "
    if stats['elevation_gain'] is not None:
        summary += f"During your workout, your elevation gain was {stats['elevation_gain']:.2f} m."
    if has_injury:
        summary += f"Note: the user has the following injury or limitation: {has_injury}. "
    summary += "Based on this performance and training history, suggest the next workout."
    return summary

def extract_text_after_tag(text, tag):
    '''
    Extracts the text that appears after a given tag in the input text.
    The tag itself is not included in the returned result.
    '''
    match = re.search(tag, text, re.IGNORECASE)
    if match:
        return text[match.end():].strip()
    else:
        return ""  # or return None, depending on your needs
    
'''
def display_workout_data(uploaded_file):
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join("temp", uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Parse the workout data from CSV
        workout_data = parse_csv_file(temp_file_path)

        user_gender = st.selectbox("Select your gender", options=["male", "female"])
        weight_kg = st.number_input("Enter your weight (kg)", min_value=0.0, format="%.2f")
        height_cm = st.number_input("Enter your height (cm)", min_value=0.0, format="%.2f")
        age = st.number_input("Enter your age", min_value=0, format="%d")

        # Analyze the workout data
        stats = analyze_workout_data(workout_data, user_gender, weight_kg, height_cm, age)
        
        # Display the workout summary
        st.write("📊 Workout Summary")
        st.write(f"**Total Distance:** {stats['total_distance']:.2f} m")
        st.write(f"**Workout Duration:** {stats['workout_duration']} minutes")
        st.write(f"**Average Heart Rate:** {stats['avg_heart_rate'] if stats['avg_heart_rate'] is not None else 'N/A'} bpm")
        st.write(f"**Average Cadence:** {stats['avg_cadence'] if stats['avg_cadence'] is not None else 'N/A':.2f} steps/min")
        st.write(f"**Average Elevation:** {stats['avg_elevation'] if stats['avg_elevation'] is not None else 'N/A':.2f} m")
        st.write(f"**Average Power:** {stats['avg_power'] if stats['avg_power'] is not None else 'N/A':.2f} watts")
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
'''
def main():
    st.title("AI Fitness Coach - Workout Analyzer")

    # File upload widget
    uploaded_file = st.file_uploader("Upload your workout CSV file", type=["csv"])

    # Display workout data and stats
    display_workout_data(uploaded_file)

if __name__ == "__main__":
    main()