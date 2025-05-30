from feedgen.feed import FeedGenerator
import os
from datetime import datetime
import time

def generate_rss_feed(site_url="https://your-username.github.io/dashboard-podcast", audio_dir="public/podcast", output_file="public/feed.xml"):
    fg = FeedGenerator()
    fg.load_extension('podcast')  # optional, for iTunes tags
    fg.title("GoodData Dashboard Podcast")
    fg.link(href=site_url, rel='alternate')
    fg.description("Your dashboards, now as audio episodes.")
    fg.language("en")

    audio_files = sorted([
        f for f in os.listdir(audio_dir)
        if f.endswith(".mp3")
    ], reverse=True)

    for file_name in audio_files:
        file_path = os.path.join(audio_dir, file_name)
        file_url = f"{site_url}/{audio_dir}/{file_name}"
        pub_date = datetime.fromtimestamp(os.path.getmtime(file_path))

        fe = fg.add_entry()
        fe.id(file_name)
        fe.title(f"Dashboard Insights – {pub_date.strftime('%b %d, %Y')}")
        fe.description(f"Insights generated on {pub_date.strftime('%A, %B %d, %Y')}")
        fe.enclosure(file_url, str(os.path.getsize(file_path)), 'audio/mpeg')
        fe.pubDate(pub_date.strftime('%a, %d %b %Y %H:%M:%S GMT'))

    fg.rss_file(output_file)
    print(f"RSS feed generated at {output_file}")


if __name__ == "__main__":
    generate_rss_feed()
