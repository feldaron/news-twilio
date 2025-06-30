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
    "4": ("Jerusalem Post", "https://www.jpost.com/RSS/RSSFeedsHeadlines.aspx"),
    "5": ("Arutz Sheva", "https://www.israelnationalnews.com/rss.xml")
}

@app.route("/voice", methods=["GET", "POST"])
def voice():
    menu = """
    <Response>
        <Gather numDigits="1" action="/handle-source" method="POST">
            <Say language="en-GB">
                Welcome to the news hotline.
                Press 1 for BBC News.
                Press 2 for the Guardian.
                Press 3 for Sky News.
                Press 4 for the Jerusalem Post
                Press 5 for Israel National News
            </Say>
        </Gather>
        <Say language="en-GB">We didn't receive any input. Goodbye.</Say>
    </Response>
    """
    return Response(menu, mimetype="text/xml")

@app.route("/handle-source", methods=["POST"])
def handle_source():
    digit = request.form.get("Digits")
    if digit not in SOURCES:
        return Response("""<Response><Say language="en-GB">Invalid choice. Goodbye.</Say></Response>""", mimetype="text/xml")
    
    prompt = f"""
    <Response>
        <Gather numDigits="1" action="/read-news?src={digit}" method="POST">
            <Say language="en-GB">
                You selected {SOURCES[digit][0]}.
                Press 1 for headlines only.
                Press 2 for headlines with descriptions.
            </Say>
        </Gather>
        <Say language="en-GB">We didn't receive any input. Goodbye.</Say>
    </Response>
    """
    return Response(prompt, mimetype="text/xml")

@app.route("/read-news", methods=["GET", "POST"])
def read_news():
    digit = request.args.get("src")
    with_desc = request.form.get("Digits") == "2"

    name, url = SOURCES.get(digit, ("Unknown", None))
    speech_lines = [f"You selected {name}. Here are the latest headlines."]

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        rss = requests.get(url, headers=headers, timeout=5)

        # Print the first 300 bytes for debugging
        print("RSS snippet:", rss.content[:300])

        if not rss.content.strip().startswith(b"<?xml"):
            raise ValueError("Invalid RSS format")

        root = ET.fromstring(rss.content)
        items = root.findall(".//item")[:10]

        for item in items:
            title = item.find("title").text or ""
            desc = item.find("description").text or ""
            title = title.replace("&", "and").strip()
            desc = desc.replace("&", "and").strip()
            segment = title
            if with_desc:
                segment += ". " + desc
            speech_lines.append(segment)

    except Exception as e:
        print("News error:", e)
        speech_lines = ["Sorry, the news feed could not be loaded."]

    speech = ".  ".join(speech_lines)

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-GB">
        {speech}
    </Say>
</Response>"""

    return Response(xml, mimetype="text/xml")

# Ensure it works on Render or Replit
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
