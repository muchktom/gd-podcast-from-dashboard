import os
import requests
from datetime import datetime, timedelta

def upload_episode(path, summary, season_number, episode_number):
    API_TOKEN = os.getenv("BUZZSPROUT_API_TOKEN")
    PODCAST_ID = os.getenv("BUZZSPROUT_PODCAST_ID")

    # Endpoint
    url = f"https://www.buzzsprout.com/api/{PODCAST_ID}/episodes.json?"

    # Metadata (customize as needed)
    data = {
        "title": summary.split("\n")[0],
        "description": "\n".join(summary.split("\n")[1:]),
        "summary": "\n".join(summary.split("\n")[1:]),
        "artist": "GoodData AI Assistant",
        "episode_number": episode_number,
        "season_number": season_number,
        "explicit": False,
        "private": False,
        
        "published_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "email_user_after_audio_processed": True,
        "artwork_url": "https://www.gooddata.com/img/blog/_1200x630/01_21_2022_goodatasociallaunch_rebrand_og.png.webp"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BuzzsproutBot/1.0)",
        "Accept": "application/json",
        "Authorization": f"Token token={API_TOKEN}"
    }

    # File upload
    files = {
        "audio_file": (os.path.basename(path), open(path, "rb"), "audio/mpeg")
    }

    # POST request
    response = requests.post(url, data=data, headers=headers, files=files)

    # Handle response
    if response.status_code == 201:
        episode = response.json()
        print("✅ Episode created:")
        print(f"🎧 Title: {episode['title']}")
        print(f"🔗 Link: {episode['audio_url']}")
    else:
        print("❌ Failed to create episode")
        print(response.status_code, response.text) 