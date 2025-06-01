import os
import base64
from pdf2image import convert_from_path
from dotenv import load_dotenv
from openai import OpenAI
from gooddata_sdk import GoodDataSdk
from pathlib import Path
from datetime import datetime
import io
from generate_feed import generate_rss_feed
import requests

load_dotenv()  # take environment variables from .env.

# GoodData base URL, e.g. "https://www.example.com"
host = os.environ.get("GOODDATA_ENDPOINT")
token = os.environ.get("GOODDATA_API_TOKEN")
sdk = GoodDataSdk.create(host, token)

def export_dashboard_to_images(workspace_id, dashboard_id, export_file_name):
  # Export a dashboard in PDF format
  export_path = Path.cwd() / "input"
  export_path.mkdir(parents=True, exist_ok=True)
  sdk.export.export_pdf(
    workspace_id = workspace_id,
    dashboard_id = dashboard_id,
    file_name = export_file_name,
    store_path = export_path,
    metadata = {}
  )

  # Convert PDF to images
  images = convert_from_path(export_path / (export_file_name + ".pdf"), dpi=300)  # Change dpi for quality
  
  image_data = []
  for i, img in enumerate(images):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    image_data.append(img_str)  # Store base64 string if needed

  # Return the list of base64-encoded images (or just `images` if raw images are needed)
  return image_data  # or `return image_data` if you need base64 strings

def describe_dashboard(images, language="en"):
    client = OpenAI()

    message = [
      {
      "role": "user",
      "content": [
        {
        "type": "text",
        "text": (
          "Act as a data analyst who creates a daily data summary podcast. "
          "Start with the current day and a brief introduction of the dashboard, "
          "then describe the dashboard in a way that is easy to understand for a "
          "non-technical audience. Don't mention there is actually a dashboard or "
          "1, 2, 3…, make it sound like you are reading a daily summary report. "
          f"Write the text in {language}."
        ),
        }
      ]
      }
    ]

    for image in images:
      message[0]["content"].append(
        {
          "type": "image_url",
          "image_url": {"url": f"data:image/jpeg;base64,{image}"},
        }
      )

    outcome = client.chat.completions.create(
      model="gpt-4o",
      messages=message
    )
    return outcome.choices[0].message.content

def generate_audio(text, file, voice="alloy"):
  export_path = Path.cwd() / "public" / "podcast"
  client = OpenAI()

  response = client.audio.speech.create(
      model="tts-1",
      voice=voice,
      input=text,
  )
  response.stream_to_file(export_path / (file+".mp3"))

def generate_summary(text):
  client = OpenAI()

  message = [
      {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": (
            "Act as a podcaster and data analyst who publishes the new podcast episode. "
            "In the first line, add the title of the episode (e.g. 'June 1, 2025 - Exploring the Dynamic Expansion of LEGO Sets')."
            "On the second line and following lines, generate a very short and brief description of the new podcast episode. This description will be used in the RSS feed. "
            "Don't use any markdown formatting."
            f"Text to summarize: {text}"
          ),
        }
      ]
      }
    ]

  outcome = client.chat.completions.create(
      model="gpt-4o",
      messages=message
    )
  return outcome.choices[0].message.content


def upload_episode(file_name, path, summary, season_number, episode_number):
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
    "published_at": datetime.utcnow().isoformat(),
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


def main():
    workspace_id = os.environ.get("GOODDATA_WORKSPACE_ID")
    dashboard_id = os.environ.get("GOODDATA_DASHBOARD_ID")
    images = export_dashboard_to_images(workspace_id, dashboard_id, "test")
    language = "en"
    response = describe_dashboard(images, language)
    timestamp = datetime.now().strftime("%m-%d-%Y")
    file_name = f"podcast_{timestamp}_{language}"
    generate_audio(response, file_name)
    summary = generate_summary(response)
    path = Path("public") / "podcast" / (file_name + ".mp3")
    upload_episode(file_name, path, summary, 1, 1)
    
    """ # Store the summary as a .txt file next to the audio file
    export_path = Path.cwd() / "public" / "podcast"
    summary_file = export_path / f"{file_name}.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)
    generate_rss_feed() """

if __name__ == "__main__":
    main()