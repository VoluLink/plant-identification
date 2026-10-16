#from langchain_core.prompts import ChatPromptTemplate
try:
    from rag_container.retrieve_matching_vectors import retrieve_matching_vector, filter_answerability
except ModuleNotFoundError:
    from retrieve_matching_vectors import retrieve_matching_vector, filter_answerability

import os
from openai import OpenAI

# OLLAMA VARIANTE (auskommentiert)
# from ollama import chat

def main(query):
    #query = "Nenne mir interessante Zahlen zu Kartoffeln?" #"Welche Kartoffelsorten gibt es?" 
    
    # Verbessung mit z.B. Query Expansion; Quellenfiltern nach Metadata Topic usw., höherer k
    similar_docs = retrieve_matching_vector(query, 5)
    relevant_docs = filter_answerability(query,similar_docs)  

    # Verhindern, dass leere Kontexte an Modell gesendet werden
    if not relevant_docs:
        return {
            "answer": "Ich kann basierend auf meiner Wissensbasis diese Frage nicht eindeutig beantworten.",
            "sources": []
        }

    context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f""" 

    Beantworte die Frage ausschließlich basierend auf dem folgenden Kontext:  
    
    

    {context}

    
    ---

    Wenn die Frage NICHT eindeutig aus dem Kontext beantwortet werden kann, sage exakt:
    "Ich kann basierend auf meiner Wissensbasis diese Frage nicht eindeutig beantworten."

    ---

    Frage: {query}

    """
    
    # OLLAMA VARIANTE (auskommentiert)
    # response = chat(
    #     model='llama3.1:8b', #Modell muss auf dem System installiert sein
    #     messages=[{'role': 'user', 'content': prompt}],
    #     keep_alive="1m"
    # )

    # OPENAI VARIANTE
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Alternativen: "gpt-4", "gpt-4-turbo-preview"
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.7,
        max_tokens=2000
    )

    # OPENAI VARIANTE: response.choices[0].message.content
    # OLLAMA VARIANTE: response.message.content (auskommentiert)
    
    #sources = [doc.metadata.get("source", None) for doc in relevant_docs] #.get("source", None)
    #pages = [doc.metadata.get("page", None) for doc in relevant_docs]
    references = []
    seen_references = set()
    for doc in relevant_docs:
        source = doc.metadata.get("source")
        page = doc.metadata.get("page")
        if source is None or page is None:
            continue

        reference_key = (source, page)
        if reference_key in seen_references:
            continue

        seen_references.add(reference_key)
        references.append({
            "Dokument": source,
            "Seite": page + 1
        })
    result = {
        "answer": response.choices[0].message.content,
        "sources": references
    }
    print(f"{result['answer']}\nQuellen: {references}")
    return result

if __name__ == "__main__":
    main("Welche Kartoffelsorten gibt es?")
