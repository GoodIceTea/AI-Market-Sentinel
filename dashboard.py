import os
import pandas as pd
import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Market Sentinel", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title("AI Market Sentinel Dashboard")
st.markdown("Automatic technology market trend monitoring and Sentiment Analysis using Hacker News.")
st.markdown("New data everyday at 8:00 AM UTC.")

@st.cache_data(ttl=600)
def load_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        query = "SELECT * FROM hn_trends ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        cursor = conn.cursor()
        return df
    except Exception as e:
        st.error(f"AWS database connection error: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data available. Please check your database connection.")
else:
    st.success("Data loaded successfully.")

    st.markdown("---")

    st.subheader("Hacker News Trends")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("All posts", len(df))
    col2.metric("Positive posts ", len(df[df['sentiment_category'] == 'positive']))
    col3.metric("Negative posts ", len(df[df['sentiment_category'] == 'negative']))
    col4.metric("Neutral posts ", len(df[df['sentiment_category'] == 'neutral']))

    st.markdown("---")

    leftcol, rightcol = st.columns(2)

    with leftcol:
        st.subheader("Sentiment Distribution")
        sentiment_counts = df['sentiment_category'].value_counts()
        st.bar_chart(sentiment_counts, color="#ff4b4b")

    with rightcol:
        st.subheader("Latest Hacker News Posts")
        st.dataframe(df[['title','sentiment_category', 'sentiment_score']],use_container_width=True)

