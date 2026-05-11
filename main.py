import os
import json
import requests
import psycopg2
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

def categorize_sentiment(result):
    if result > 0.1:
        return "positive"
    elif result < -0.1:
        return "negative"
    else:
        return "neutral"

#db con
print("Connecting to PostgreSQL database...")
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()
    print("Connected to PostgreSQL database.\n")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hn_trends (
            id SERIAL PRIMARY KEY,
            hn_id INTEGER UNIQUE,
            title TEXT,
            sentiment_category VARCHAR(50),
            sentiment_score FLOAT
        )
    """)
    conn.commit()

except Exception as e:
    print (f"Error connecting to AWS database: {e}")
    print("Check your database credentials and try again.")
    exit(1)

print("Connecting to Hacker News API...")

url_new_stories = "https://hacker-news.firebaseio.com/v0/newstories.json"
response = requests.get(url_new_stories)

if response.status_code != 200:
    print(f"Failed to fetch new stories: {response.status_code}")
    exit(1)

story_ids = response.json()

if not story_ids:
    print("No new stories found.")
    exit()

top10_ids = story_ids[:10]

print("Fetching top 10 stories...\n")

for story_id in top10_ids:
    url_item = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    item_response = requests.get(url_item)
    post_data = item_response.json()

    title = post_data.get("title", "No title available")
    text = post_data.get("text", "")

    content_to_analyze = f"{title} {text}".strip()

    analyse = TextBlob(content_to_analyze)
    result = analyse.sentiment.polarity
    category = categorize_sentiment(result)

    print(f"Title: {title}")
    print(f"Sentiment: {category} (Result: {result:.2f})")

    #load to db
    try:
        cursor.execute("""
                INSERT INTO hn_trends (hn_id, title, sentiment_category, sentiment_score) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (hn_id) DO NOTHING""",
            (story_id, title, category, result)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print("Succesfully inserted NEW record into database.")
        else:
            print("Record already exists in database.")
    except Exception as e:
        print(f"Error inserting into database: {e}")
        conn.rollback()

    print("-"*50)

cursor.close()
conn.close()
print("ETL process completed successfully.")
