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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Dataset Overview", "👥 Seller & Transmission", "⛽ Fuel Analysis", "📈 Scatter Plots", "📊 Histogram & Boxplot"
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

    # Download filtered dataset
    st.subheader("⬇️ Download Filtered Dataset")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_cardekho.csv",
        mime="text/csv"
    )

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
    st.subheader("Interactive Scatter Plot")

    # Let user select X and Y variables
    numeric_cols = filtered_df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    if len(numeric_cols) >= 2:
        x_axis = st.selectbox("Select X-axis", options=numeric_cols, index=numeric_cols.index("vehicle_age") if "vehicle_age" in numeric_cols else 0)
        y_axis = st.selectbox("Select Y-axis", options=numeric_cols, index=numeric_cols.index("selling_price") if "selling_price" in numeric_cols else 1)
        color_by = st.selectbox("Color By", options=["brand", "fuel_type", "transmission_type", "seller_type"], index=0)

        if not filtered_df.empty:
            fig = px.scatter(
                filtered_df,
                x=x_axis,
                y=y_axis,
                color=color_by,
                hover_data=["model", "brand", "mileage", "fuel_type"],
                title=f"{y_axis} vs {x_axis}",
                size_max=10
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough numeric columns available for scatter plots.")

with tab5:
    st.subheader("Interactive Histogram & Boxplot")

    if not filtered_df.empty:
        numeric_cols = filtered_df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        col_choice = st.selectbox("Select Variable", options=numeric_cols, index=numeric_cols.index("selling_price") if "selling_price" in numeric_cols else 0)
        color_by = st.selectbox("Group By (optional)", options=["None"] + ["brand", "fuel_type", "transmission_type", "seller_type"], index=0)

        if color_by == "None":
            fig_hist = px.histogram(filtered_df, x=col_choice, nbins=40, title=f"Histogram of {col_choice}")
            fig_box = px.box(filtered_df, y=col_choice, title=f"Boxplot of {col_choice}")
        else:
            fig_hist = px.histogram(filtered_df, x=col_choice, color=color_by, nbins=40, barmode="overlay", title=f"Histogram of {col_choice} grouped by {color_by}")
            fig_box = px.box(filtered_df, x=color_by, y=col_choice, title=f"Boxplot of {col_choice} by {color_by}")

        st.plotly_chart(fig_hist, use_container_width=True)
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No data available for Histogram/Boxplot.")
