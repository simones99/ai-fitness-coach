import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def plot_monthly_workout_volume(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%b')
    monthly_counts = df.groupby('month').size().reindex([
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ])

    plt.figure(figsize=(10, 4))
    sns.barplot(x=monthly_counts.index, y=monthly_counts.values, palette="viridis")
    plt.title("Total Workouts per Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Workouts")
    st.pyplot(plt)

def plot_workout_type_distribution(df, workout_type=None):
    if 'workout_type' not in df.columns:
        st.warning("No 'workout_type' column found in workout log.")
        return
    
    type_counts = df['workout_type'].value_counts()

    plt.figure(figsize=(8, 6))
    type_counts.plot(kind='barh', color='skyblue')
    plt.title("Workout Type Distribution")
    plt.xlabel("Number of Sessions")
    plt.ylabel("Workout Type")
    st.pyplot(plt)

    if workout_type and workout_type in type_counts:
        st.markdown(f"🔍 **Current workout type:** {workout_type} — {type_counts[workout_type]} sessions")