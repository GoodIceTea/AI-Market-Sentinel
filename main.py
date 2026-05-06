import json
from textblob import TextBlob

def categorize_sentiment(result):
    if result > 0.1:
        return "positive"
    elif result < -0.1:
        return "negative"
    else:
        return "neutral"

with open ("mock_reddit_data.json") as f:
    data = json.load(f)

    for post in data:
        title = post["title"]
        text = post["text"]

        analyse = TextBlob(text)
        result = analyse.sentiment.polarity

        category = categorize_sentiment(result)

        print(title, category)
