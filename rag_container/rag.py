from contextlib import asynccontextmanager
import traceback
import create_vector_db
from fastapi import Body, FastAPI, HTTPException
from pathlib import Path
import os

from answer_query_based_on_sources import main as answer_query_based_on_sources

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown resources.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.state.rag = create_vector_db.main()
    try:
        yield
    finally:
        app.state.rag.close()

app = FastAPI(lifespan=lifespan)

@app.post("/api/rag/health")
async def test_health():
    """Returns the current health status of the API.

    Returns:
        dict: A status indicating the service is running.
    """
    return {"status": "online"}

@app.get("/api/rag/documents")
async def list_documents():
    """List all documents in the rag_data folder.
    
    Returns:
        dict: List of documents with metadata (name, size, type).
    """
    data_path = Path("./rag_data")
    
    if not data_path.exists():
        return {"documents": [], "total_documents": 0}
    
    try:
        documents = []
        for f in sorted(data_path.glob("*.pdf")):
            size_bytes = os.path.getsize(f)
            # Convert to MB
            size_mb = size_bytes / (1024 * 1024)
            documents.append({
                "name": f.name,
                "size": round(size_mb, 2),
                "size_unit": "MB",
                "type": f.suffix
            })
        
        return {"documents": documents, "total_documents": len(documents)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Auflisten der Dokumente: {e}",
        )

@app.post("/api/rag/query")
async def query_rag(query: str = Body(...)):
    """Answer a user query with the RAG pipeline.

    Args:
        query (str): User question to answer based on the local references.

    Returns:
        dict: Answer text and source references.
    """
    query = query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query darf nicht leer sein.")

    try:
        return answer_query_based_on_sources(query)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"RAG-Anfrage fehlgeschlagen: {exc}",
        ) from exc
    
