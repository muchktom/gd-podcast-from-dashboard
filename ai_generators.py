from openai import OpenAI
from pathlib import Path

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
    export_path = Path.cwd() / "public"
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
              "Important: Don't use any markdown formatting, just plain text."
              "Act as a podcaster and data analyst who publishes the new podcast episode. "
              "In the first line, add the title of the episode (e.g. 'June 1, 2025 - Exploring the Dynamic Expansion of LEGO Sets')."
              "On the second line and following lines, generate a very short and brief description of the new podcast episode. This description will be used in the RSS feed. "
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