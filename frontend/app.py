import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import json


st.set_page_config(page_title="Logistics Analysis", layout="wide")

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

@st.cache_data
def load_api_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
        response.raise_for_status() 
        return pd.DataFrame(response.json())
    except Exception as e:
        return pd.DataFrame()

@st.cache_data
def load_geo_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

df_rating = load_api_data("api/rating")
df_delivery = load_api_data("api/corel")
if os.path.exists("backend/brazil_geo.json"):
    brazil_states = load_geo_json("backend/brazil_geo.json")
else:
    # Fallback if running from frontend directory locally
    brazil_states = load_geo_json("../backend/brazil_geo.json")

st.set_page_config(
    page_title="Аналіз доставки Olist",
    layout="wide", # Це ключ до адаптивності на великих екранах
)

# Custom CSS to make the sidebar footer sticky
st.markdown(
    """
    <style>
        div[data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        div[data-testid="stSidebar"] > div:first-child > div:last-child {
            margin-top: auto;
        }

        /* Custom Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px; /* Small gap between tabs */
            width: 100%; /* Full width container */
        }

        .stTabs [data-baseweb="tab"] {
            height: 60px; /* Increased height */
            flex: 1; /* Tabs take equal width (50% each) */
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            padding-top: 15px;
            padding-bottom: 10px;
            color: #555;
            border: none; /* Remove default borders */
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .stTabs [data-baseweb="tab"] p {
            font-size: 24px; /* Larger font size as requested */
            font-weight: 700;
            margin: 0;
        }

        /* Selected Tab Text Color */
        .stTabs [aria-selected="true"] p {
            color: #FF4B4B !important;
        }

        /* Selected Tab Styling */
        .stTabs [aria-selected="true"] {
            background-color: transparent;
        }
        
        /* 
           Specific Styling for "Project" Tab (1st Child) 
           - Content pushed to the right half
           - Line on the right half
        */
        .stTabs [data-baseweb="tab"]:nth-child(1) {
            padding-left: 50%; /* Push text area to the right half */
        }
        
        .stTabs [data-baseweb="tab"]:nth-child(1) [aria-selected="true"]::after {
            content: "";
            position: absolute;
            bottom: 0px;
            right: 0; /* Align line to right */
            width: 50%; /* Line covers the text area (right half) */
            height: 4px;
            background-color: #FF4B4B;
            border-radius: 2px;
        }

        /* 
           Specific Styling for "Results" Tab (2nd Child) 
           - Content pushed to the left half
           - Line on the left half
        */
        .stTabs [data-baseweb="tab"]:nth-child(2) {
             padding-right: 50%; /* Push text area to the left half */
        }

        .stTabs [data-baseweb="tab"]:nth-child(2) [aria-selected="true"]::after {
            content: "";
            position: absolute;
            bottom: 0px;
            left: 0; /* Align line to left */
            width: 50%; /* Line covers the text area (left half) */
            height: 4px;
            background-color: #FF4B4B;
            border-radius: 2px;
        }

        /* Hide default underline */
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Contacts")
st.sidebar.divider()
st.sidebar.markdown("**Yurii Borysonok**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/yurii-borysonok)")
st.sidebar.markdown("**Email:** borysonokyurii@gmail.com")
st.sidebar.markdown("**City:** Lviv, Ukraine")
with st.sidebar:
    # Spacer is handled by CSS margin-top: auto on the last element
    try:
        # Increased timeout to 3 seconds to handle potential latency
        check = requests.get(f"{API_BASE_URL}/api/rating", timeout=3)
        s_text, s_col = ("● API Connected", "green") if check.status_code == 200 else ("○ API Issue", "orange")
    except:
        s_text, s_col = "○ API Offline", "red"
    
    st.markdown("---")
    st.markdown(f"**Status:** <span style='color:{s_col}'>{s_text}</span>", unsafe_allow_html=True)
    if st.button("↻ Check Status"):
        st.rerun()

st.title("Logistics and Customer Satisfaction Analysis Brazilian E-Commerce")

tab1, tab2 = st.tabs(["Project", "Results"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.header("About the project")
        st.write("This analysis identifies critical factors that affect delivery quality and customer experience")
        st.write("I used this dataset to demonstrate the full data lifecycle: from ETL processes to building business hypotheses")

        st.subheader("Main goal:")
        st.write("Find out why orders are late and how this translates into reputational damage for the marketplace")

        st.header("Stack")
        st.markdown("""
        * **SQL (PostgreSQL):** Complex queries, window functions, CTE for calculating Delay Rate
        * **Python:** Preprocessing data, removing duplicates, and converting types
        * **Tableau:** Correlation analysis and visualization of insights
        * **SQLAlchemy:** Integrating Python with the database to automate updates
        """)

    with col2:
        st.header("Process")
        st.subheader("1. Data preparation and transformation")
        st.write("At the initial stage, using **Python** and **SQLAlchemy**, the following was performed:")
        st.markdown("""
        * Conversion of text date fields to `TIMESTAMP` format for correct calculations
        * Cleaning duplicates and validating data
        * Loading cleaned data into PostgreSQL
        """)

        st.subheader("2. Key SQL metrics")
        st.write("To analyze logistics, queries were developed to calculate:")
        st.markdown("""
        * **Delay Rate:** Percentage of orders delivered later than the promised delivery date
        * **Average Review Score:** Comparison of ratings for on-time and late deliveries
        * **Weighted Delivery Analysis:** The impact of product weight on the likelihood of delay
        """)

with tab2:
    st.header("Results")
    
    st.subheader("1. Impact of delays on customer experience")
    st.write("The analysis showed a high correlation between on-time delivery and user ratings:")
    st.markdown("""
    * **On-time delivery:** Average rating — **4.29** 
    * **Delays:** Average rating drops to **2.57**
    * **Conclusion:** Late delivery is the main driver of negative reviews
    """)
    
    if not df_rating.empty:
        rating = px.bar(
            df_rating,
            x = "avg_review_score",
            y= "delivery_status",
            color = "delivery_status",
            color_discrete_map= {
                "Late Delivery": "#A0001B",
                "On Time": "#05B431"
            },
            text="total_orders",
            orientation="h",
            labels={'delivery_status':'Delivery status',
                    'avg_review_score': 'Rating'}
            )
        
        # rating.update_layout(width='stretch')
        st.plotly_chart(rating, width='stretch')
    else:
        st.info("No rating data available. Please ensure the database is populated.")
    
    st.subheader("2. Correlation between product weight and logistics speed")
    st.write("I discovered a certain correlation:")
    st.markdown("""
    * The higher the average weight of goods in the seller's city, the higher the **Delay Rate**
    * Goods weighing more than **10 kg** have a 2-3 times higher risk of delay compared to light parcels
    * The P-value of this data is **0.03**, which indicates its significance
    """)
    
    if not df_delivery.empty:
        corellation = px.scatter(
            df_delivery,
            x="avg_weight_per_order",
            y ="Delay_Rate",
            hover_name="seller_city",
            color="avg_weight_per_order",
            color_continuous_scale="Pinkyl",
            template="plotly_white",
            labels={'avg_weight_per_order': 'Average weght (g)',
                    'Delay_Rate':'Delay rate (%)'}
            )
        
        # Calculate trendline using numpy manually with error handling
        try:
            # Ensure we work with clean data for fitting
            # Create a copy to avoid SettingWithCopyWarning or affecting original df
            df_clean = df_delivery.dropna(subset=["avg_weight_per_order", "Delay_Rate"]).copy()
            
            if len(df_clean) > 1:
                x = df_clean["avg_weight_per_order"]
                y = df_clean["Delay_Rate"]
                m, b = np.polyfit(x, y, 1)
                
                # Create a simple line based on min/max x
                x_trend = np.array([x.min(), x.max()])
                y_trend = m * x_trend + b
                
                corellation.add_trace(
                    go.Scatter(
                        x=x_trend, 
                        y=y_trend, 
                        mode='lines', 
                        name='Trendline',
                        line=dict(color='red')
                    )
                )
        except Exception as e:
            # Log error but don't crash
            print(f"Trendline calculation error: {e}")
            pass

        corellation.update_xaxes(rangemode="tozero")
        corellation.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20), # Зменшуємо поля для економії місця
        )
        corellation.update_traces(marker=dict(size=8))
        st.plotly_chart(corellation, width='stretch')
        with st.expander("See details"):
            st.write(df_delivery)
    else:
        st.info("No delivery data available.")
    
    st.subheader("3. Geographical anomalies")
    st.write("The cities with the highest levels of delays were identified. For example, the city of **Sombrio** shows a high level of delays, which directly correlates with the high average weight of goods in this region **22 kg**")
    
    if not df_delivery.empty:
        df_delivery["seller_state"] = df_delivery["seller_state"].astype(str).str.upper().str.strip()
        
        world_map = px.choropleth_map(
                df_delivery,
                geojson=brazil_states,
                locations="seller_state",      
                featureidkey="id",         
                color="Delay_Rate",
                color_continuous_scale="Reds",
                range_color=(0, df_delivery["Delay_Rate"].max()),
                map_style="carto-positron",
                opacity=0.5,
                zoom=3,
                center={"lat": -14.235, "lon": -51.925},
                title="Geographical map of deliveries by states and cities",
                labels={'Delay_Rate': 'Late (%)'}
            )
        
        
        world_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(world_map, width='stretch')
    else:
        st.info("No geographical data available.")
    
    st.link_button("Graphic in Tableau", "https://bit.ly/3Mx0e2Z")
    
    st.header("Recommendations")
    st.markdown("""
    1. **Dynamic delivery times:** Implement an algorithm that automatically adds +1-2 days to the expected delivery date for goods weighing more than **10 kg**
    2. **Optimize partnerships:** Review logistics partners in cities with a Delay_Rate > 15% to identify the causes of delays
    3. **Manage expectations:** Warn customers about possible delays for large items at the checkout stage
    """)