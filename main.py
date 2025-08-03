from numpy import expand_dims
from cv2 import VideoCapture, imwrite, imread, resize
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
from requests import post, get
from time import sleep
from os import remove

# Load the pre-trained ResNet50 model
model = ResNet50(weights='imagenet')

# Path to the input image
cap = VideoCapture(0)
input("\033[92mPress enter to capture the webcam")
print("\033[37m")
ret, frame = cap.read()
imwrite('captured_image.jpg', frame)
img_path = 'captured_image.jpg'  # The image to classify
cap.release()

# Load and preprocess the image
img = imread(img_path)
img = resize(img, (224, 224))
x = image.img_to_array(img)
x = expand_dims(x, axis=0)
x = preprocess_input(x)


# Make predictions
preds = model.predict(x)

# Decode and display predictions
result = decode_predictions(preds, top=1)[0][0]
object = result[1]
chance = result[2]
print("\033[92mObject detected: " + object)

remove(img_path) 

API_KEY = input("Enter the API Key from https://www.beatoven.ai/api (50/month): ")
print("\033[37m")
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
    response = post(f"{BASE_URL}/api/v1/tracks/compose", json=payload, headers=headers)
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
        status_resp = get(f"{BASE_URL}/api/v1/tasks/{task_id}", headers=headers)
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

        sleep(5)

if __name__ == "__main__":
    text_prompt = object
    music_url = create_music(text_prompt)
    if music_url:
        print("\033[92mYour generated music URL:", music_url)
        input("Press enter to exit (click the URL to download)")