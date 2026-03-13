import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from forecasting import forecast_future


st.set_page_config(
    page_title="PJM Energy Forecast Dashboard",
    layout="wide"
)

st.title("PJM Hourly Energy Consumption Forecast")


@st.cache_data
def load_data():

    df = pd.read_excel("data/PJMW_MW_Hourly.xlsx", parse_dates=["Datetime"])
    df.set_index("Datetime", inplace=True)
    return df

import os
import streamlit as st

@st.cache_data
def load_data():

    base_dir = os.path.dirname("Power_Analysis")
    file_path = os.path.join(base_dir, "data", "PJMW_MW_Hourly.xlsx")

    df = pd.read_excel(file_path, parse_dates=["Datetime"])
    df.set_index("Datetime", inplace=True)

    return df

df = load_data()


# Load trained model and scaler
model = load_model("model/lstm_model.h5")
scaler = joblib.load("model/scaler.pkl")


st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Select Section",
    [
        "Home Dashboard",
        "Dataset Overview",
        "Energy Trends",
        "Seasonal Patterns",
        "Model Performance",
        "30 Day Forecast"
    ]
)


# HOME DASHBOARD

if page == "Home Dashboard":

    st.header("Energy Demand Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Current Demand",
        f"{int(df.iloc[-1].values[0])} MW"
    )

    col2.metric(
        "Average Demand",
        f"{int(df.mean().values[0])} MW"
    )

    col3.metric(
        "Peak Demand",
        f"{int(df.max().values[0])} MW"
    )

    st.subheader("Recent Energy Consumption Trend")

    st.line_chart(df.tail(1000))


# DATASET OVERVIEW

elif page == "Dataset Overview":

    st.header("Dataset Overview")

    st.write("Dataset Shape:", df.shape)

    st.dataframe(df.head())

    fig = px.line(
        df,
        y=df.columns[0],
        title="Energy Consumption Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)


# ENERGY TRENDS

elif page == "Energy Trends":

    st.header("Hourly Energy Demand Pattern")

    df["hour"] = df.index.hour

    hourly_pattern = df.groupby("hour").mean()

    fig = px.bar(
        hourly_pattern,
        y=hourly_pattern.columns[0],
        title="Average Hourly Demand"
    )

    st.plotly_chart(fig, use_container_width=True)


# SEASONAL PATTERNS

elif page == "Seasonal Patterns":

    st.header("Seasonal Energy Demand")

    df["month"] = df.index.month

    monthly = df.groupby("month").mean()

    fig = px.line(
        monthly,
        y=monthly.columns[0],
        title="Monthly Energy Consumption Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
    """
**Insights**

• Electricity demand increases during summer due to cooling loads.

• Winter months also show increased demand because of heating usage.

• Spring and fall generally show relatively lower energy consumption.
"""
    )


# MODEL PERFORMANCE

elif page == "Model Performance":

    st.header("Model Performance")

    st.write("Selected Model: **LSTM**")

    st.metric("Accuracy Difference vs XGBoost", "0.15%")

    st.metric("MAE Difference", "~7")

    st.success(
    """
The LSTM model is deployed due to its ability to capture temporal dependencies
in time-series electricity demand data while maintaining competitive performance.
"""
    )


# FORECAST PAGE

elif page == "30 Day Forecast":

    st.header("Energy Demand Forecast")

    days = st.slider(
        "Forecast Horizon (Days)",
        min_value=1,
        max_value=30,
        value=30
    )

    forecast_df = forecast_future(
        model,
        scaler,
        df,
        seq_length=24,
        days=days
    )

    st.subheader("Forecasted Energy Demand")

    st.line_chart(forecast_df)

    st.subheader("Forecast Preview")

    st.dataframe(forecast_df.head(48))


    # INSIGHTS

    st.subheader("Forecast Insights")

    peak = int(forecast_df["Forecast"].max())
    minimum = int(forecast_df["Forecast"].min())
    avg = int(forecast_df["Forecast"].mean())

    col1, col2, col3 = st.columns(3)

    col1.metric("Predicted Peak Demand", f"{peak} MW")
    col2.metric("Predicted Minimum Demand", f"{minimum} MW")
    col3.metric("Average Demand", f"{avg} MW")


    # RECOMMENDATIONS

    st.subheader("Operational Recommendations")

    st.markdown(
"""
**Peak Demand Planning**

Utilities should ensure adequate generation capacity during predicted peak demand periods.

**Grid Stability**

High demand may strain transmission infrastructure; therefore, load balancing strategies should be implemented.

**Maintenance Scheduling**

Forecasted low-demand periods can be used for infrastructure maintenance.

**Seasonal Preparedness**

Energy demand varies significantly between seasons, requiring adaptive generation planning.

**Demand Management**

Encouraging off-peak electricity usage can reduce stress on the grid during peak hours.
"""
    )
