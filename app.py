import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="CarDekho Dashboard", layout="wide")
st.title("🚗 CarDekho Interactive EDA Dashboard")

# Load dataset (prebuilt)
@st.cache_data
def load_data():
    df = pd.read_csv("cardekho_dataset.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns="Unnamed: 0")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

brands = st.sidebar.multiselect("Select Brand(s)", options=sorted(df["brand"].unique()), default=None)
fuels = st.sidebar.multiselect("Select Fuel Type(s)", options=sorted(df["fuel_type"].unique()), default=None)
transmissions = st.sidebar.multiselect("Select Transmission(s)", options=sorted(df["transmission_type"].unique()), default=None)
sellers = st.sidebar.multiselect("Select Seller Type(s)", options=sorted(df["seller_type"].unique()), default=None)

# Vehicle Age Range filter
min_age, max_age = int(df["vehicle_age"].min()), int(df["vehicle_age"].max())
age_range = st.sidebar.slider("Select Vehicle Age Range", min_age, max_age, (min_age, max_age))

# Apply filters
filtered_df = df.copy()
if brands:
    filtered_df = filtered_df[filtered_df["brand"].isin(brands)]
if fuels:
    filtered_df = filtered_df[filtered_df["fuel_type"].isin(fuels)]
if transmissions:
    filtered_df = filtered_df[filtered_df["transmission_type"].isin(transmissions)]
if sellers:
    filtered_df = filtered_df[filtered_df["seller_type"].isin(sellers)]

filtered_df = filtered_df[(filtered_df["vehicle_age"] >= age_range[0]) & (filtered_df["vehicle_age"] <= age_range[1])]

# Tabs for dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Dataset Overview", "👥 Seller & Transmission", "⛽ Fuel Analysis", "📈 Scatter Plots"
])

with tab1:
    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head())

    st.subheader("Summary Statistics")
    st.write(filtered_df.describe())

    st.subheader("Top Car Models")
    top_models = filtered_df["model"].value_counts().nlargest(20).reset_index()
    top_models.columns = ["model", "count"]
    fig = px.bar(top_models, y="model", x="count", orientation="h", title="Top 20 Car Models", color="count")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Seller Type Distribution")
    if not filtered_df.empty:
        fig = px.pie(filtered_df, names="seller_type", title="Seller Type Distribution")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Transmission Type Distribution")
    if not filtered_df.empty:
        fig = px.pie(filtered_df, names="transmission_type", title="Transmission Type Distribution")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Fuel Type Distribution")
    if not filtered_df.empty:
        fig = px.pie(filtered_df, names="fuel_type", title="Fuel Type Distribution")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Selling Price vs Vehicle Age")
    if not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="vehicle_age",
            y="selling_price",
            color="brand",
            hover_data=["model", "mileage", "fuel_type"],
            title="Selling Price vs Vehicle Age",
            size_max=10
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Selling Price vs Mileage")
    if not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="mileage",
            y="selling_price",
            color="fuel_type",
            hover_data=["model", "brand", "vehicle_age"],
            title="Selling Price vs Mileage",
            size_max=10
        )
        st.plotly_chart(fig, use_container_width=True)
