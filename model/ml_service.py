import io
import json
import os
import time

from PIL import Image as PILImage

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

# DONE
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(host=settings.REDIS_IP, port=settings.REDIS_PORT, decode_responses=True)

# DONE
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """

    class_name = None
    pred_probability = None
    # DONE
    # Implement the code to predict the class of the image_name
    # Load image — read bytes into memory with retry, then open via BytesIO
    # to avoid filesystem cache/visibility race conditions on Docker volumes
    image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
    img_bytes = None
    for attempt in range(5):
        try:
            if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                with open(image_path, "rb") as f:
                    img_bytes = f.read()
                if img_bytes:
                    break
        except OSError:
            pass
        print(f"File not ready yet (attempt {attempt + 1}): {image_path}")
        time.sleep(0.5)
    if not img_bytes:
        raise ValueError(f"Could not read image after retries: {image_path}")
    img = image.load_img(io.BytesIO(img_bytes), target_size=(224, 224))
    img = image.img_to_array(img)
    # Apply preprocessing (match model input dimensions (including batch) and use the resnet50 preprocessing)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    # Get predictions using model methods and decode predictions using resnet50 decode_predictions
    _, class_name, pred_probability = decode_predictions(model.predict(img), top=1)[0][0]
    # Convert probabilities to float and round it
    pred_probability = round(float(pred_probability), 4)

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # DONE
        # Take a new job from Redis
        job = db.brpop(settings.REDIS_QUEUE)

        # Decode the JSON data for the given job
        job_data = json.loads(job[1])

        # Important! Get and keep the original job ID
        job_id = job_data["id"]

        # Run the loaded ml model (use the predict() function)
        print(f"[JOB {job_id[:8]}] Processing image: {job_data['image_name']}")
        try:
            class_name, pred_probability = predict(job_data["image_name"])
            # Prepare a new JSON with the results
            output = {"prediction": class_name, "score": pred_probability}
            # Store the job results on Redis using the original job ID as the key
            db.set(job_id, json.dumps(output))
            print(f"[JOB {job_id[:8]}] Done -> class={class_name}, score={pred_probability}")
        except Exception as e:
            print(f"[JOB {job_id[:8]}] ERROR: {e}")
            output = {"prediction": None, "score": None}
            db.set(job_id, json.dumps(output))

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
