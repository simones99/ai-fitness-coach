import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def plot_workout_by_weekday_heatmap(df):
    """
    Displays a heatmap of workout counts by day of week and week number.
    Assumes df has a 'date' column in datetime format or convertible string format.
    """
    df['date'] = pd.to_datetime(df['date'])
    df['count'] = 1  # count 1 workout per day

    heatmap_data = df.groupby(df['date'].dt.date).agg({'count': 'sum'}).reset_index()
    heatmap_data['date'] = pd.to_datetime(heatmap_data['date'])
    heatmap_data['dow'] = heatmap_data['date'].dt.day_name()
    heatmap_data['week'] = heatmap_data['date'].dt.isocalendar().week

    pivot_table = heatmap_data.pivot_table(index='dow', columns='week', values='count', fill_value=0)
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_table = pivot_table.reindex(ordered_days)

    if pivot_table.empty:
        st.warning("Not enough data to generate weekday heatmap.")
        return

    plt.figure(figsize=(12, 4))
    sns.heatmap(pivot_table, cmap="YlGnBu", linewidths=.5, annot=True, fmt=".0f", cbar=False)
    plt.title("Workout Frequency by Weekday and Week Number")
    plt.xlabel("Week Number")
    plt.ylabel("Day of Week")
    st.pyplot(plt)

def plot_calendar_month_heatmap(df):
    """
    Displays a heatmap calendar of workouts by day of month and month.
    """
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%b')
    df['day'] = df['date'].dt.day
    df['count'] = 1

    pivot_table = df.pivot_table(index='day', columns='month', values='count', aggfunc='sum', fill_value=0)
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_table = pivot_table.reindex(columns=months_order, fill_value=0)

    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_table, cmap="YlOrBr", linewidths=.5, annot=True, fmt=".0f", cbar=False)
    plt.title("Workout Frequency Calendar (Day x Month)")
    plt.xlabel("Month")
    plt.ylabel("Day of Month")
    st.pyplot(plt)