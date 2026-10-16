## Directory Overview

```
chroma_langchain_db/ 
    -> lokale Speicherung der Vektor-Datenbank
src/
└──rag/
    └── rag_data/
            └── pdf/
                -> Daten für Vektor-Datenbank

```
## Files
create_vector_db.py 
    -> erstellt Chroma Vektor-Datenbank lokal 
    -> füllt diese initial mit allen Dokumenten im Verzeichnis rag_data/pdf
create_embeddings.py
    -> nutzt ein Embeddings-Modell zur Generierung von Embeddings
    -> https://ollama.com/jina/jina-embeddings-v2-base-de
    -> ollama pull jina/jina-embeddings-v2-base-de:latest (dafür muss ollama installiert sein)  --> WICHTIG: CUDA-fähige GPU mit korrekter Installation
retrieve_matching_vector.py
    -> soll gegeben einem Input die besten k Treffer ausgeben
    -> soll nach (Übereinstimmungs-Score filtern) und nach Answerability
    -> https://ollama.com/library/llama3.1
    -> ollama pull llama3.1:8b (dafür muss ollama installiert sein)  --> WICHTIG: CUDA-fähige GPU mit korrekter Installation
answer_query_based_on_sources.py
    -> soll gegeben Input-Query mit Hilfe der relevanten Quellen beantworten und Quellen als Referenz mit ausgeben
add_to_vector_db.py
    -> fügt Dokumente zur Vektor-Datenbank hinzu
    -> Dokumentenname wird als Argument übergeben
delete_from_vector_db.py
    -> löscht Dokumente auf Vektor-Datenbank
    -> zu löschendes Dokument wird mit Dokumentennamen als Argument übergeben

    