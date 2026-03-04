import random
from typing import Optional
import os
import requests
from locust import HttpUser, between, task

API_BASE_URL = "http://localhost:8000"
IMAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PRELOADED_IMAGES = [
    (img_name, open(os.path.join(IMAGE_DIR, img_name), "rb").read())
    for img_name in os.listdir(IMAGE_DIR)
    if img_name.endswith((".jpg", ".jpeg", ".png"))
]

def login(username: str, password: str) -> Optional[str]:
    """This function calls the login endpoint of the API to authenticate the user and get a token.

    Args:
        username (str): email of the user
        password (str): password of the user

    Returns:
        Optional[str]: token if login is successful, None otherwise
    """
    # DONE
    # 1 - make a request to the login endpoint
    # 2 - check if the response status code is 200
    # 3 - if it is, return the access_token
    # 4 - if it is not, return None
    url = f"{API_BASE_URL}/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


class APIUser(HttpUser):
    # Put your stress tests here.
    # See https://docs.locust.io/en/stable/writing-a-locustfile.html for help.
    # DONE
    wait_time = between(1, 5)

    def on_start(self):
        self.token = login("admin@example.com", "admin")
        if not self.token:
            self.environment.runner.quit()

    @task(1)
    def index(self):
        self.client.get("/docs", name="index")

    @task(3)
    def predict(self):
        image_name, image_bytes = random.choice(PRELOADED_IMAGES)
        
        files = {"file": (image_name, image_bytes, "image/jpeg")}
        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.post("/model/predict", headers=headers, files=files, name="predict", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("prediction") is None:
                        response.failure("API returned 200 but prediction was None")
                except Exception:
                    response.failure("Failed to parse JSON")
            else:
                response.failure(f"Status code: {response.status_code}")