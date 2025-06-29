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
        items = root.findall(".//item")[:10]  # Read top 10 headlines
        headlines = [item.find("title").text for item in items]

        # Add pause between headlines using SSML <break>
        ssml_headlines = "<break time='900ms'/>".join(
            [f"<p>{h}</p>" for h in headlines]
        )

        # Wrap in full SSML to control speaking rate
        text = f"""
        <speak>
          <prosody rate="slow">
            Here are today's top headlines from BBC News.
            <break time="800ms"/>
            {ssml_headlines}
          </prosody>
        </speak>
        """
    except Exception as e:
        print("Error fetching news:", e)
        text = "<speak><prosody rate='slow'>Sorry, I couldn't load the news right now.</prosody></speak>"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="en-GB">{text}</Say>
</Response>"""
    return Response(twiml, mimetype='text/xml')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
