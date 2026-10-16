import base64

import requests
from fastapi import FastAPI, File, UploadFile

safeMode = False  # False, wenn API-Anfrage funktionieren soll

API_URL = "https://plant.id/api/v3/identification"
API_KEY = "wUNokoUU2EeUHAk7wxQKgbCHpkBMrq071S87fG1w4Rcs9d52xE"

app = FastAPI()


@app.post("/api/ident/health")
async def test_health():
    """Returns the current health status of the API.

    Returns:
        dict: A status indicating the service is running.
    """
    return {"status": "online"}


@app.post("/api/ident/plant_classification")
async def plant_classification(file: UploadFile = File(...)):
    """Classifies the plant in an uploaded image using the plant.id API.

    Args:
        file (UploadFile): The image file to classify (e.g. JPEG, PNG).

    Returns:
        dict: In normal mode, a dictionary with the plant.id HTTP status code
            and the full JSON response, e.g.
            ``{"status_code": 200, "response": {...}}``.
            In safe mode, ``{"response": "safeMode is activated"}``.
    """

    # Bilddaten lesen
    image_bytes = await file.read()

    # plant.id API Format bauen
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [image_base64],
        "similar_images": True,
        "classification_level": "all",
        "latitude": 51.482,
        "longitude": 11.971,
    }
    headers = {"Api-Key": f"{API_KEY}", "Content-Type": "application/json"}

    # Bild an plant.id API senden
    if not safeMode:
        response = requests.post(API_URL, headers=headers, json=payload)
        return {"status_code": response.status_code, "response": response.json()}
    else:
        return {"response": "safeMode is activated"}


@app.post("/api/ident/plant_health")
async def plant_health(file: UploadFile = File(...)):
    """Assesses the health of a plant in an uploaded image using the plant.id API.

    Args:
        file (UploadFile): The image file to assess (e.g. JPEG, PNG).

    Returns:
        dict: In normal mode, a dictionary with the Plant.ID HTTP status code
            and the full JSON response, e.g.
            ``{"status_code": 200, "response": {...}}``.
            In safe mode, ``{"response": "safeMode is activated"}``.
    """

    # Bilddaten lesen
    image_bytes = await file.read()

    # plant.id API Format bauen
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "images": [image_base64],
        "similar_images": True,
        "health": "only",
        "latitude": 51.482,
        "longitude": 11.971,
    }
    headers = {"Api-Key": f"{API_KEY}", "Content-Type": "application/json"}

    # Bild an plant.id API senden
    if not safeMode:
        response = requests.post(API_URL, headers=headers, json=payload)
        return {"status_code": response.status_code, "response": response.json()}
    else:
        return {"response": "safeMode is activated"}
