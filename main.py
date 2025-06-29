from flask import Flask, Response
import requests
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

@app.route("/bbc", methods=["GET", "POST"])
def bbc_news():
    text = "Sorry, I couldn't load the news right now."

    try:
        rss = requests.get("http://feeds.bbci.co.uk/news/rss.xml", timeout=5)
        root = ET.fromstring(rss.content)
        items = root.findall(".//item")[:3]
        headlines = [item.find("title").text for item in items]
        if headlines:
            text = "Here are today's top headlines from BBC News. " + " ".join(headlines)
    except Exception as e:
        print("Error fetching news:", e)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">{text}</Say>
</Response>"""
    return Response(twiml, mimetype='text/xml')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
