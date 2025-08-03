import numpy as np
import cv2
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import requests
import time

# Load the pre-trained ResNet50 model
model = ResNet50(weights='imagenet')

# Path to the input image
img_path = 'football.jpg'  # The image to classify

# Load and preprocess the image
img = cv2.imread(img_path)
img = cv2.resize(img, (224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

# Make predictions
preds = model.predict(x)

# Decode and display predictions
result = decode_predictions(preds, top=1)[0][0]
object = result[1]
chance = result[2]

API_KEY = input("Enter the API Key from Beatoven.ai: ")
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
    text_prompt = object
    music_url = create_music(text_prompt)
    if music_url:
        print("Your generated music URL:", music_url)
