import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import os
import json
import plotly.graph_objects as go

st.set_page_config(page_title="Logistics Analysis", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"

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
brazil_states = load_geo_json("brazil_geo.json")

st.sidebar.header("Contacts")
st.sidebar.divider()
st.sidebar.markdown("**Yurii Borysonok**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/yurii-borysonok)")
st.sidebar.markdown("**Email:** borysonokyurii@gmail.com")
st.sidebar.markdown("**City:** Lviv, Ukraine")
with st.sidebar:
    for i in range(26):
        st.write("\n")
    try:
        check = requests.get(f"{API_BASE_URL}/api/rating", timeout=1)
        s_text, s_col = ("● API Connected", "green") if check.status_code == 200 else ("○ API Issue", "orange")
    except:
        s_text, s_col = "○ API Offline", "red"
    st.markdown(f"<span style='color:{s_col}'>{s_text}</span>", unsafe_allow_html=True)

st.title("Logistics and Customer Satisfaction Analysis Brazilian E-Commerce")

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

st.header("Results")

st.subheader("1. Impact of delays on customer experience")
st.write("The analysis showed a high correlation between on-time delivery and user ratings:")
st.markdown("""
* **On-time delivery:** Average rating — **4.29** 
* **Delays:** Average rating drops to **2.57**
* **Conclusion:** Late delivery is the main driver of negative reviews
""")

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
st.plotly_chart(rating, width='stretch')

st.subheader("2. Correlation between product weight and logistics speed")
st.write("I discovered a certain correlation:")
st.markdown("""
* The higher the average weight of goods in the seller's city, the higher the **Delay Rate**
* Goods weighing more than **10 kg** have a 2-3 times higher risk of delay compared to light parcels
* The P-value of this data is **0.03**, which indicates its significance
""")

corellation = px.scatter(
    df_delivery,
    x="avg_weight_per_order",
    y ="Delay_Rate",
    trendline="ols",
    hover_name="seller_city",
    color="avg_weight_per_order",
    color_continuous_scale="Pinkyl",
    template="plotly_white",
    labels={'avg_weight_per_order': 'Average weght (g)',
            'Delay_Rate':'Delay rate (%)'}
)
corellation.update_traces(marker=dict(size=8))
st.plotly_chart(corellation)
st.write("Details:", df_delivery)
st.subheader("3. Geographical anomalies")
st.write("The cities with the highest levels of delays were identified. For example, the city of **Sombrio** shows a high level of delays, which directly correlates with the high average weight of goods in this region **22 kg**")

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

st.write("**Graphic in Tableau** [https://bit.ly/3Mx0e2Z]")

st.header("Recommendations")
st.markdown("""
1. **Dynamic delivery times:** Implement an algorithm that automatically adds +1-2 days to the expected delivery date for goods weighing more than **10 kg**
2. **Optimize partnerships:** Review logistics partners in cities with a Delay_Rate > 15% to identify the causes of delays
3. **Manage expectations:** Warn customers about possible delays for large items at the checkout stage
""")