import requests
import time

API_KEY = ""
BASE_URL = "https://public-api.beatoven.ai"

def create_music(prompt_text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": {"text": prompt_text},
        "format": "wav",     # optional
        "looping": False     # optional
    }

    # Step 1: Start composition
    response = requests.post(f"{BASE_URL}/api/v1/tracks/compose", json=payload, headers=headers)
    if response.status_code != 200:
        print("Error creating music:", response.text)
        return None
    
    data = response.json()
    if data.get("status") not in ["started", "composing"]:
        print("Failed to start composition:", data)
        return None

    task_id = data.get("task_id")
    print(f"Music generation started. Task ID: {task_id}")

    # Step 2: Poll for completion
    while True:
        status_resp = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}", headers=headers)
        status_resp.raise_for_status()
        status_data = status_resp.json()

        status = status_data.get("status")
        print(f"Current status: {status}")

        if status == "composed":
            track_url = status_data["meta"]["track_url"]
            print("Music generation complete!")
            return track_url
        elif status in ["failed", "error"]:
            print("Music generation failed.")
            return None

        time.sleep(5)

if __name__ == "__main__":
    text_prompt = "30 seconds peaceful lo-fi chill hop track"
    music_url = create_music(text_prompt)
    if music_url:
        print("Your generated music URL:", music_url)
