"""
This is a Streamlit app for analyzing air quality data. It allows users to filter data,
apply smoothing, and visualize trends, comparisons, and correlations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.markdown(
    """
<style>
div.stButton > button:first-child {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 12px;
    border: 2px solid #4CAF50;
    transition-duration: 0.4s;
}
div.stButton > button:hover {
    background-color: white;
    color: #4CAF50;
}
div.stDownloadButton > button:first-child {
    background-color: #008CBA;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 12px;
    border: 2px solid #008CBA;
    transition-duration: 0.4s;
}
div.stDownloadButton > button:hover {
    background-color: white;
    color: #008CBA;
}
</style>
""",
    unsafe_allow_html=True,
)


def filter_data():
    """Filter the data based on selected stations and date range."""
    return data[
        (data["station"].isin(selected_stations))
        & (data["datetime"].dt.date >= date_range[0])
        & (data["datetime"].dt.date <= date_range[1])
    ]


def analyze_data():
    """Trigger the analysis and update the session state."""
    st.session_state.filtered_data = filter_data()
    st.session_state.analysis_triggered = True


def smooth_data(series, method="EMA", window=90):
    """Apply smoothing to a series using the specified method."""
    if method == "EMA":
        return series.ewm(span=window, adjust=False).mean()
    if method == "SMA":
        return series.rolling(window=window).mean()
    return series


# Define pollutant thresholds (example values, can be adjusted)
THRESHOLDS = {"PM25": 150.4, "NO2": 200, "PM10": 350, "SO2": 180, "CO": 8000, "O3": 235}

# Color palette
COLOR_PALETTE = px.colors.qualitative.Plotly
MA_COLOR_PALETTE = px.colors.qualitative.Set2

# Load the data
data = pd.read_csv("data/all_stations_cleaned.csv")

# Convert datetime to datetime format
data["datetime"] = pd.to_datetime(data["datetime"])

# Initialize session state
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = data
if "analysis_triggered" not in st.session_state:
    st.session_state.analysis_triggered = False


# Sidebar filters
st.sidebar.header("Filter Data")
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun", options=data["station"].unique()
)
selected_pollutants = st.sidebar.multiselect(
    "Pilih Polutan", options=["PM25", "PM10", "SO2", "NO2", "CO", "O3"]
)
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal", value=[data["datetime"].min(), data["datetime"].max()]
)
smoothing_method = st.sidebar.selectbox(
    "Pilih Metode Smoothing", options=["EMA", "SMA"], index=1
)
smoothing_window = st.sidebar.slider(
    "Window Smoothing", min_value=1, max_value=180, value=90
)

# Filter data based on user selection
filtered_data = data[
    (data["station"].isin(selected_stations))
    & (data["datetime"].dt.date >= date_range[0])
    & (data["datetime"].dt.date <= date_range[1])
]

# Data Export and Analysis Options in Sidebar
col1, col2 = st.sidebar.columns(2)

with col1:
    # This will download the filtered data
    st.download_button(
        label="📥Unduh",
        data=st.session_state.filtered_data.to_csv(index=False),
        file_name="air_quality_data.csv",
        mime="text/csv",
    )

with col2:
    # Trigger analysis when the button is clicked
    if st.button("🔍Analisis"):
        analyze_data()

# Main content
if st.session_state.analysis_triggered:
    if len(selected_pollutants) > 0 and len(selected_stations):
        st.success("Analisis data dimulai!")
        st.title("📈 Analisis Tren Polutan")
        tabs = st.tabs(selected_pollutants)

        for i, (pollutant, tab) in enumerate(zip(selected_pollutants, tabs)):
            with tab:
                st.subheader(f"Trend {pollutant} dari Waktu ke Waktu")

                # Create the base line chart
                line_fig = px.line(
                    st.session_state.filtered_data,
                    x="datetime",
                    y=pollutant,
                    color="station",
                    labels={
                        "datetime": "Tanggal",
                        pollutant: f"Konsentrasi {pollutant} (µg/m³)",
                    },
                    color_discrete_sequence=COLOR_PALETTE,
                )

                # Add smoothed trend line (dotted) with different color
                for j, station in enumerate(selected_stations):
                    station_data = st.session_state.filtered_data[
                        st.session_state.filtered_data["station"] == station
                    ]
                    smoothed_series = smooth_data(
                        station_data[pollutant],
                        method=smoothing_method,
                        window=smoothing_window,
                    )
                    line_fig.add_trace(
                        go.Scatter(
                            x=station_data["datetime"],
                            y=smoothed_series,
                            mode="lines",
                            line={
                                "dash": "dot",
                                "width": 3,
                                "color": MA_COLOR_PALETTE[j % len(MA_COLOR_PALETTE)],
                            },
                            name=f"{station} (MA)",
                        )
                    )

                # Adding a horizontal line for safe threshold
                if pollutant in THRESHOLDS:
                    line_fig.add_hline(
                        y=THRESHOLDS[pollutant],
                        line_dash="dash",
                        annotation_text=f"Batas Aman {pollutant} ({THRESHOLDS[pollutant]} µg/m³)",
                        annotation_position="bottom right",
                        line_color="red",
                        line_width=2,
                    )

                # Improve tooltips
                line_fig.update_traces(
                    mode="lines+markers",
                    hovertemplate="Tanggal: %{x}<br>Konsentrasi: %{y:.2f} µg/m³<br>Stasiun: %{text}",
                )
                st.plotly_chart(line_fig, use_container_width=True)

        # Bar Chart for Comparison
        st.title("📊 Perbandingan Polutan di Berbagai Lokasi")
        bar_fig = px.bar(
            st.session_state.filtered_data,
            x="station",
            y=selected_pollutants,
            barmode="group",
            title="Perbandingan Polutan",
            labels={"station": "Stasiun", "value": "Konsentrasi (µg/m³)"},
            color_discrete_sequence=COLOR_PALETTE,
        )

        # Improve layout and tooltips
        bar_fig.update_layout(
            xaxis_title="Stasiun",
            yaxis_title="Konsentrasi Polutan (µg/m³)",
            legend_title="Polutan",
        )
        bar_fig.update_traces(
            hovertemplate="Stasiun: %{x}<br>Konsentrasi: %{y:.2f} µg/m³"
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        # Correlation Heatmap
        st.title("🔥 Korelasi Antar Polutan")
        corr_data = st.session_state.filtered_data[selected_pollutants].corr()
        heatmap_fig = px.imshow(
            corr_data,
            labels={"color": "Korelasi"},
            x=selected_pollutants,
            y=selected_pollutants,
            color_continuous_scale="RdBu_r",
        )
        heatmap_fig.update_layout(title="Heatmap Korelasi Antar Polutan")
        st.plotly_chart(heatmap_fig, use_container_width=True)

        # Summary Statistics
        st.title("📊 Ringkasan Statistik")
        summary_stats = st.session_state.filtered_data[selected_pollutants].describe()
        st.dataframe(summary_stats)

        # Notification Feature
        st.title("🚨 Notifikasi Kualitas Udara")
        for pollutant in selected_pollutants:
            if pollutant in THRESHOLDS:
                max_value = st.session_state.filtered_data[pollutant].max()
                if max_value > THRESHOLDS[pollutant]:
                    st.error(
                        f"⚠️ Peringatan: Kualitas udara melebihi batas aman untuk {pollutant}!"
                    )
                    st.metric(
                        label=f"Nilai Tertinggi {pollutant}",
                        value=f"{max_value:.2f} µg/m³",
                        delta=f"{max_value - THRESHOLDS[pollutant]:.2f} µg/m³",
                    )
            else:
                st.success(f"✅ Kualitas udara untuk {pollutant} dalam batas aman.")

    else:
        st.warning("Tidak ada data yang dipilih. Silakan pilih data untuk analisis.")

else:
    st.info(
        "Silakan pilih filter data dan klik tombol 'Analisis' untuk memulai analisis."
    )
