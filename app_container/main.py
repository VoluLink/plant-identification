import os

import httpx
import requests
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()

if os.path.isdir("public"):  # <-- geändert
    app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get("/")
async def root():
    """Return the main application page.

    Returns:
        FileResponse: The frontend HTML file served from ``public/index.html``.
    """
    return FileResponse("public/index.html")


@app.get("/blur_status")
async def blur_status():
    """Return the health status of the blurring service.

    Returns:
        dict: A JSON object containing the service name and the reported
        health status.
    """
    url = "http://blurring:9001/api/blur/health"

    async with httpx.AsyncClient() as client:
        response = await client.post(url)
        data = response.json()

    return {"service": "blurring", "status": data.get("status")}


@app.post("/blur")
def blur_image(file: UploadFile = File(...)):
    """Proxy an uploaded image to the blurring service and return the result.

    Args:
        file (UploadFile): Uploaded image to be blurred.

    Raises:
        HTTPException: If the downstream blurring service request fails.

    Returns:
        Response: The blurred image content and content type from the service.
    """
    try:
        file.file.seek(0)

        response = requests.post(
            "http://blurring:9001/api/blur/blurring",
            files={
                "file": (
                    file.filename or "upload.jpg",
                    file.file,
                    file.content_type or "application/octet-stream",
                )
            },
            timeout=60,
        )

        response.raise_for_status()

        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "image/jpeg"),
            status_code=response.status_code,
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502, detail=f"Blur-Service Fehler: {exc}"
        ) from exc


@app.get("/ident_status")
async def ident_status():
    """Return the health status of the identification service.

    Returns:
        dict: A JSON object containing the service name and the reported
        health status.
    """
    url = "http://identification:9002/api/ident/health"

    async with httpx.AsyncClient() as client:
        response = await client.post(url)
        data = response.json()

    return {"service": "identification", "status": data.get("status")}


@app.post("/ident/plant_classification")
async def plant_classification(file: UploadFile = File(...)):
    """Proxy an uploaded image to the plant classification service.

    Args:
        file (UploadFile): Uploaded image to be classified.

    Returns:
        dict: JSON response with the plant classification from the identification service.
    """
    file_bytes = await file.read()
    url = "http://identification:9002/api/ident/plant_classification"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, files={"file": (file.filename, file_bytes, file.content_type)}
        )
    return response.json()


@app.post("/ident/plant_health")
async def plant_health(file: UploadFile = File(...)):
    """Proxy an uploaded image to the plant health service.

    Args:
        file (UploadFile): Uploaded image to be analyzed.

    Returns:
        dict: JSON response with the plant health information from the identification service.
    """
    file_bytes = await file.read()
    url = "http://identification:9002/api/ident/plant_health"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, files={"file": (file.filename, file_bytes, file.content_type)}
        )
    return response.json()

@app.get("/rag_status")
async def rag_status():
    """Return the health status of the rag service.

    Returns:
        dict: A JSON object containing the service name and the reported
        health status.
    """
    url = "http://rag:9003/api/rag/health"

    async with httpx.AsyncClient() as client:
        response = await client.post(url)
        data = response.json()

    return {"service": "rag", "status": data.get("status")}

@app.post("/rag/query")
async def rag_query(query: str = Body(...)):
    url = "http://rag:9003/api/rag/query"

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=query)
            response.raise_for_status()
            data = response.json()

        return data

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="RAG-Service hat nicht rechtzeitig geantwortet.",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text,
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"RAG-Service nicht erreichbar: {exc}",
        ) from exc

@app.get("/rag/documents")
async def rag_documents():
    """Return a list of rag documents.

    Returns:
        dict: A JSON object containing the documents from the RAG service.
    """
    url = "http://rag:9003/api/rag/documents"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    return data