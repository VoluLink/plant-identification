from langchain_chroma import Chroma
from uuid import uuid4
try:
    from rag_container.create_embeddings import EmbeddingFunction
except ModuleNotFoundError:
    from create_embeddings import EmbeddingFunction
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

def create_vector_store():
    return Chroma(
        collection_name="example_collection",
        embedding_function=EmbeddingFunction(),
        persist_directory="./chroma_langchain_db",
        collection_metadata={"hnsw:space": "cosine"},
    )

def collect_files(path):
    files = [f"./{str(p)}" for p in Path(path).iterdir() if p.is_file()]
    print(f"Es wurden folgende Dateien: {files} im Pfad: {path} gefunden.")
    return files

def load_documents(files):
    docs = []
    for file in files:
        loader = PyPDFLoader(
            file,
            mode="page",
        )
        docs.append(loader.load())
    return docs

def split_text(docs):
    texts = []
    for doc in docs:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len, add_start_index=True)
        split_text = text_splitter.split_documents(doc)
        texts.append(split_text)
        print(f"Das Dokument wurde in {len(split_text)} Chunks geteilt.")
    return texts

def initial_db_population(vector_store, texts):
    for text in texts:
        uuids = [str(uuid4()) for _ in range(len(text))]
        vector_store.add_documents(documents=text, ids=uuids)
    print("Datenbank initial befüllt.")

def main():
    try:
        vector_store = create_vector_store()
    except Exception as e:
        print(f"Fehler beim initialen Erstellen der Vektor-Datenbank: {e}")
        return None
    
    try:
        data_path = "./rag_data/"
        files = collect_files(data_path)
    except Exception as e:
        print(f"Fehler beim Einsammeln der Dateien im Pfad {data_path}: {e}")
        return None
    
    try:
        docs = load_documents(files)
    except Exception as e:
        print(f"Fehler beim Laden der Dateien {files}: {e}")
        return None
    
    try:
        texts = split_text(docs)
    except Exception as e:
        print(f"Fehler beim Splitten der Dokumente: {e}")
        return None
    
    try:
        initial_db_population(vector_store, texts)
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Dokumente zur Vektor-Datenbank: {e}")
        return
    
    return None
    
if __name__ == "__main__":
    main()
