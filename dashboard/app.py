import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
data = pd.read_csv('data/all_stations_cleaned.csv')

# Convert datetime to datetime format
data['datetime'] = pd.to_datetime(data['datetime'])

# Sidebar filters
st.sidebar.header("Filter Data")
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun", options=data["station"].unique(), default=["Huairou","Shunyi"]
)
selected_pollutants = st.sidebar.multiselect(
    "Pilih Polutan", options=["PM25", "PM10", "SO2", "NO2", "CO", "O3"], default=["PM25", "NO2"]
)
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal", value=[data['datetime'].min(), data['datetime'].max()]
)

# Filter data based on user selection
filtered_data = data[
    (data["station"].isin(selected_stations)) &
    (data["datetime"].dt.date >= date_range[0]) &
    (data["datetime"].dt.date <= date_range[1])
]

# Line Chart for Trend Analysis
st.title("Analisis Tren Polutan")
for pollutant in selected_pollutants:
    line_fig = px.line(
        filtered_data, x="datetime", y=pollutant, color="station",
        title=f'Trend {pollutant} dari Waktu ke Waktu'
    )
    st.plotly_chart(line_fig)

# Bar Chart for Comparison
st.title("Perbandingan Polutan di Berbagai Lokasi")
bar_fig = px.bar(
    filtered_data, x="station", y=selected_pollutants,
    barmode="group", title="Perbandingan Polutan"
)
st.plotly_chart(bar_fig)

# Notification Feature
thresholds = {"PM25": 35, "NO2": 40}
st.title("Notifikasi Kualitas Udara")
for pollutant in selected_pollutants:
    if (filtered_data[pollutant] > thresholds.get(pollutant, float('inf'))).any():
        st.warning(f"{pollutant} melebihi batas aman di beberapa lokasi!")

# Data Export Option
st.title("Ekspor Data")
st.download_button(
    label="Unduh Data",
    data=filtered_data.to_csv(index=False),
    file_name='filtered_air_quality_data.csv'
)
