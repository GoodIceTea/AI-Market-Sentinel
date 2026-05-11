import json
import requests
from textblob import TextBlob

def categorize_sentiment(result):
    if result > 0.1:
        return "positive"
    elif result < -0.1:
        return "negative"
    else:
        return "neutral"

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

    print(f"Tytuł: {title}")
    print(f"Sentyment: {category} (Wartość: {result:.2f})")
    print("-"*50)
