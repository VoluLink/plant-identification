try:
    from rag_container.create_vector_db import create_vector_store
except ModuleNotFoundError:
    from create_vector_db import create_vector_store

import os
from openai import OpenAI

# OLLAMA VARIANTE (auskommentiert)
# from ollama import chat

def retrieve_matching_vector(query, k):
    vector_store = create_vector_store()
    similar_docs = vector_store.similarity_search(query, k=k)
    return similar_docs

def filter_answerability(query, similar_docs):
    relevant_docs = [
        (doc) for doc in similar_docs
        if can_answer(doc, query)
    ]
    #print(len(relevant_docs))
    return relevant_docs

def can_answer(context, query): #Kann die Frage VOLLSTÄNDIG mit Hilfe des Kontexts beantwortet werden?
    prompt = f"""
    Kontext:
    {context}

    Frage:
    {query}

    Ist der Kontext hilfreich bei der Beantwortung der Frage?
    Antworte nur mit JA oder NEIN.
    """

    # OLLAMA VARIANTE (auskommentiert)
    # response = chat(
    #     model='llama3.1:8b',
    #     messages=[{'role': 'user', 'content': prompt}],
    #     keep_alive="1m"
    # )
    # return "JA" in response.message.content.upper()

    # OPENAI VARIANTE
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.3,
        max_tokens=10
    )

    return "JA" in response.choices[0].message.content.upper()

""" def main():
    query = "Was ist eine Kartoffel?"
    similar_docs = retrieve_matching_vector(query, 4)
    relevant_docs = filter_answerability(query,similar_docs)
    print(len(relevant_docs))

if __name__ == "__main__":
    main()
 """
