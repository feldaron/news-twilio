from flask import Flask, request, Response
import requests
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

# Available news sources
SOURCES = {
    "1": ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
    "2": ("The Guardian", "https://www.theguardian.com/uk/rss"),
    "3": ("Sky News", "https://feeds.skynews.com/feeds/rss/home.xml"),
    "4": ("Ynet News", "https://www.ynetnews.com/category/3082/rss")
}

@app.route("/voice", methods=["GET", "POST"])
def voice():
    # Main menu
    menu = """
    <Response>
        <Gather numDigits="1" action="/handle-source" method="POST">
            <Say voice="Polly.Amy" language="en-GB">
                Welcome to the news hotline.
                Press 1 for BBC News.
                Press 2 for the Guardian.
                Press 3 for Sky News.
                Press 4 for Ynet News.
            </Say>
        </Gather>
        <Say voice="Polly.Amy" language="en-GB">We didn't receive any input. Goodbye.</Say>
    </Response>
    """
    return Response(menu, mimetype="text/xml")

@app.route("/handle-source", methods=["POST"])
def handle_source():
    digit = request.form.get("Digits")
    if digit not in SOURCES:
        return Response("""<Response><Say voice="Polly.Amy" language="en-GB">Invalid choice. Goodbye.</Say></Response>""", mimetype="text/xml")
    
    # Ask if user wants descriptions
    prompt = f"""
    <Response>
        <Gather numDigits="1" action="/read-news?src={digit}" method="POST">
            <Say voice="Polly.Amy" language="en-GB">
                You selected {SOURCES[digit][0]}.
                Press 1 for headlines only.
                Press 2 for headlines with descriptions.
            </Say>
        </Gather>
        <Say voice="Polly.Amy" language="en-GB">We didn't receive any input. Goodbye.</Say>
    </Response>
    """
    return Response(prompt, mimetype="text/xml")

@app.route("/read-news", methods=["POST"])
def read_news():
    digit = request.args.get("src")
    with_desc = request.form.get("Digits") == "2"

    name, url = SOURCES.get(digit, ("Unknown", None))
    speech = f"<p>{name}</p>"

    try:
        rss = requests.get(url, timeout=5)
        root = ET.fromstring(rss.content)
        items = root.findall(".//item")[:7]

        for item in items:
            title = item.find("title").text or ""
            desc = item.find("description").text or ""
            desc = desc.replace("&nbsp;", " ").replace("&amp;", "and")
            segment = f"<p>{title}</p>"
            if with_desc:
                segment += f"<break time='300ms'/><p>{desc}</p>"
            speech += segment + "<break time='600ms'/>"
    except Exception as e:
        print("News error:", e)
        speech = "<p>Sorry, that feed could not be loaded.</p>"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Amy" language="en-GB">
    <speak><prosody rate="slow">{speech}</prosody></speak>
  </Say>
</Response>"""
    return Response(xml, mimetype='text/xml')

# Render compatibility
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
