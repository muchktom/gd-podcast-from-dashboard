import os
import base64
from pdf2image import convert_from_path
from dotenv import load_dotenv
from openai import OpenAI
from gooddata_sdk import GoodDataSdk
from pathlib import Path
from datetime import datetime
import io

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
  export_path = Path.cwd() / "output"
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
            "Act as a podcaster and data analyst who sends echo about the new podcast episode. "
            "Generate a brief (1-2 paragraphs) summary of the new podcast episode. " 
            "The generated text will be included in the e-mail body, " 
            "don't add subject, format it as an email and name the sender " 
            "as Paul from GoodData Daily Podcast." 
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



def main():
    workspace_id = os.environ.get("GOODDATA_WORKSPACE_ID")
    dashboard_id = os.environ.get("GOODDATA_DASHBOARD_ID")
    images = export_dashboard_to_images(workspace_id, dashboard_id, "test")

    language = "en"
    response = describe_dashboard(images, language)
    timestamp = datetime.now().strftime("%m-%d-%Y")
    file_name = f"podcast_{timestamp}_{language}"
    generate_audio(response, file_name)
   # summary = generate_summary(response)

if __name__ == "__main__":
    main()