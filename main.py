from flask import Flask, Response
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello! Append /bbc to get BBC headlines in TwiML."

@app.route("/bbc", methods=["GET"])
def bbc_headlines():
    rss_url = "http://feeds.bbci.co.uk/news/rss.xml"
    try:
        response = requests.get(rss_url, timeout=5)
        root = ET.fromstring(response.content)
        items = root.findall(".//item")[:3]
        headlines = [item.find("title").text for item in items]
        spoken = "Here are today's top headlines from BBC News. " + " ".join(headlines)
    except Exception as e:
        spoken = "Sorry, I couldn't fetch the news. Try again later."

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">{spoken}</Say>
</Response>"""
    return Response(twiml, mimetype='text/xml')

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
