from contextlib import asynccontextmanager
from blurring import blur_people_in_image_bytes, create_detector
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown resources.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.state.detector = create_detector()
    try:
        yield
    finally:
        app.state.detector.close()


app = FastAPI(title="person-blur-service", lifespan=lifespan)


@app.post("/api/blur/health")
async def test_health():
    """Returns the current health status of the API.

    Returns:
        dict: A status indicating the service is running.
    """
    return {"status": "online"}


@app.post("/api/blur/blurring")
async def blur_image(file: UploadFile = File(...)):
    """Blurs all detected people in an uploaded image.

    Args:
        file (UploadFile): The image file to process.

    Raises:
        HTTPException: 400 - Raises error for invalid file format.
        HTTPException: 500 - Raises further errors.

    Returns:
        Response: Returns the blurred image.
    """
    try:
        image_bytes = await file.read()
        output = blur_people_in_image_bytes(image_bytes, app.state.detector)
        return Response(content=output, media_type="image/jpeg")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"processing failed: {exc}"
        ) from exc
