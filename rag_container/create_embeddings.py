import os
from openai import OpenAI

# OLLAMA VARIANTE (auskommentiert)
# from ollama import embed
# 
# class EmbeddingFunction:
#     def embed_documents(self, texts):
#         response = embed(
#             model='jina/jina-embeddings-v2-base-de:latest',
#             input=texts
#         )
#         return response['embeddings']
#
#     def embed_query(self, text):
#         response = embed(
#             model='jina/jina-embeddings-v2-base-de:latest',
#             input=text
#         )
#         return response['embeddings'][0]

# OPENAI VARIANTE
class EmbeddingFunction:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "text-embedding-3-small"  # Alternativen: "text-embedding-3-large"
    
    def embed_documents(self, texts):
        """Embeddings für eine Liste von Dokumenten erstellen."""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text):
        """Embedding für eine Abfrage erstellen."""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding