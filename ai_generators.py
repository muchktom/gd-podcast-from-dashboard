from openai import OpenAI
from pathlib import Path
from datetime import datetime

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
          "In the attachment there is first a snapshot of the dashboard and then a snapshot of the previous day's dashboard. "
          "Your task is to describe the current state of the dashboard, but take into account the previous state."
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
    export_path = Path.cwd() / "public"
    export_path.mkdir(parents=True, exist_ok=True)
    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    response.stream_to_file(export_path / (file+".mp3"))

def generate_summary(text, timestamp):
    client = OpenAI()

    message = [
        {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": (
              "Act as a podcaster and data analyst publishing a new podcast episode. Generate output in JSON format with two fields: 'title' and 'description'."
              " - 'title' should be a string of 6 to 10 words, following this pattern: '<Month> <Day>, <Year> - <Short Episode Title>' (e.g. 'June 1, 2025 - Exploring the Dynamic Expansion of LEGO Sets')."
              " - 'description' should be a very short and brief summary of the episode, suitable for RSS feeds."
              "Important: Output only raw JSON. Do not include any Markdown formatting, code block markers, or extra commentary."
              f"Text to summarize: {text}"
              f"Current date is: {timestamp}"

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