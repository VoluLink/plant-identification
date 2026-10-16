from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models/efficientdet_lite2.tflite"


def create_detector():
    """Creates and returns a MediaPipe object detector configured for person detection.

    Returns:
        vision.ObjectDetector: A ready-to-use detector instance for
            identifying people in static images.
    """
    options = vision.ObjectDetectorOptions(
        base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.IMAGE,
        score_threshold=0.2,
        category_allowlist=["person"],
        max_results=-1,
    )
    return vision.ObjectDetector.create_from_options(options)


def blur_people_in_image_bytes(image_bytes: bytes, detector) -> bytes:
    """Detects all people in an image and blurs their bounding boxes.

    Args:
        image_bytes (bytes): Raw bytes of the input image (e.g. JPEG, PNG).
        detector (vision.ObjectDetector): A MediaPipe ObjectDetector instance
            pre-configured for person detection, as returned by ``create_detector()``.

    Raises:
        ValueError: If image_bytes cannot be decoded into a valid image.
        ValueError: If the processed image cannot be re-encoded as JPEG.

    Returns:
        bytes: JPEG-encoded image bytes with all detected people blurred.
    """
    np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image format.")

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = detector.detect(mp_image)

    for detection in result.detections:
        box = detection.bounding_box
        x = max(0, box.origin_x)
        y = max(0, box.origin_y)
        w = min(box.width, img.shape[1] - x)
        h = min(box.height, img.shape[0] - y)

        if w <= 0 or h <= 0:
            continue

        person = img[y : y + h, x : x + w]
        if person.size == 0:
            continue

        img[y : y + h, x : x + w] = cv2.GaussianBlur(person, (51, 51), 0)

    ok, encoded = cv2.imencode(".jpg", img)
    if not ok:
        raise ValueError("Image could not be processed.")

    return encoded.tobytes()
