import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# setting the style for seaborn
sns.set(style="darkgrid")
st.set_page_config(
    page_title="Ford GoBike Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

# configuring the sidebar
st.sidebar.header("Filter Options")

#connecting to the SQLite database and loading data
@st.cache_data
def load_data():
    conn = sqlite3.connect('fordgobike.db')
    query = """
    SELECT f.*, u.user_type, u.gender, u.age, t.day_of_week, t.hour
    FROM fact_trips f
    LEFT JOIN dim_user u ON f.user_id = u.user_id
    LEFT JOIN dim_time t ON f.time_id = t.time_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()

# filtering options in the sidebar whether to include all user types or specific ones (customer, subscriber)
user_types = df['user_type'].dropna().unique().tolist()
selected_user_type = st.sidebar.multiselect("Select User Type:", user_types, default=user_types)

# applying the filter to the data
filtered_df = df[df['user_type'].isin(selected_user_type)]

# Dashboard Title and Description
st.title("Ford GoBike Performance Dashboard")
st.markdown("An interactive overview of bike trips, user behaviors, and key usage metrics.")
st.divider()

# 4. Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Trips", value=f"{len(filtered_df):,}")

with col2:
    avg_duration = filtered_df['duration_min'].mean()
    st.metric(label="Avg Duration (Mins)", value=f"{avg_duration:.1f}")

with col3:
    subscribers = len(filtered_df[filtered_df['user_type'] == 'Subscriber'])
    st.metric(label="Total Subscribers", value=f"{subscribers:,}")

with col4:
    customers = len(filtered_df[filtered_df['user_type'] == 'Customer'])
    st.metric(label="Casual Customers", value=f"{customers:,}")

st.divider()

# Graphs and Visualizations
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Trip Duration Distribution")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(filtered_df['duration_min'], bins=40, color='teal', kde=True, ax=ax)
    ax.set_xlim(0, 60)
    ax.set_xlabel("Duration (Minutes)")
    st.pyplot(fig)

with row1_col2:
    st.subheader("Trips by Day of Week")
    fig, ax = plt.subplots(figsize=(6, 4))
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sns.countplot(data=filtered_df, x='day_of_week', order=day_order, palette='viridis', ax=ax)
    ax.set_xlabel("Day of Week")
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.divider()


row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Top 10 Start Stations")
    fig, ax = plt.subplots(figsize=(6, 4))
    top_stations = filtered_df['start_station_id'].value_counts().head(10)
    sns.barplot(x=top_stations.values, y=top_stations.index.astype(str), palette='Blues_r', ax=ax)
    ax.set_xlabel("Number of Trips")
    ax.set_ylabel("Station ID")
    st.pyplot(fig)

with row2_col2:
    st.subheader("Peak Usage Hours")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(data=filtered_df, x='hour', color='coral', ax=ax)
    ax.set_xlabel("Hour of Day (0-23)")
    st.pyplot(fig)