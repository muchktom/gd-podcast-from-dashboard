import os
from dotenv import load_dotenv
from gooddata_sdk import GoodDataSdk
from pathlib import Path
from datetime import datetime
from dashboard_export import export_dashboard_to_images
from episode_upload import upload_episode
from ai_generators import describe_dashboard, generate_audio, generate_summary

load_dotenv()  # take environment variables from .env.

# GoodData base URL, e.g. "https://www.example.com"
host = os.environ.get("GOODDATA_ENDPOINT")
token = os.environ.get("GOODDATA_API_TOKEN")
sdk = GoodDataSdk.create(host, token)

def main():
    workspace_id = os.environ.get("GOODDATA_WORKSPACE_ID")
    dashboard_id = os.environ.get("GOODDATA_DASHBOARD_ID")
    language = "en"
    timestamp = datetime.now().strftime("%m-%d-%Y")
    
    exported_dashboard = export_dashboard_to_images(sdk, workspace_id, dashboard_id)
    
    if exported_dashboard:
        dashboard_as_text = describe_dashboard(exported_dashboard, language)
        file_name = f"podcast_{timestamp}_{language}"
        generate_audio(dashboard_as_text, file_name)
        summary = generate_summary(dashboard_as_text, timestamp)
        
        audio_path = Path.cwd() / "public" / f"{file_name}.mp3"
        upload_episode(audio_path, summary, 1, 1)

if __name__ == "__main__":
    main()