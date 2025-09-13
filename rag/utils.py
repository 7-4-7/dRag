def load_model(model_name):
    model = "all_lama_mini_v6"
    return model

def load_prompts():
    PROMPT_1 = """
You are an AI assistant performing context validation. 
The user asked: "{query}".
The available context is: "{context}".

Determine if the context is sufficient to answer the query. 
If sufficient, set "search_mode": false. 
If insufficient, set "search_mode": true and suggest the missing information in "search_query" (5-6 words). 
Provide a concise reason in "detail".

Strictly respond in JSON format like this:
{
  "search_mode": true or false,
  "detail": "Concise explanation of missing context or why context is enough.",
  "search_query": "Short phrase (5-6 words) to retrieve missing context if needed."
}
"""

    PROMPT_2 = """
You are a helpful AI assistant. 
The user asked: "{query}". 
The available context is: "{context}".

Using the provided context, generate a clear, accurate, and concise answer. 
Include the sources from the context that you used. 

Strictly respond in JSON format like this:
{
  "answer": "Your answer here.",
  "references": ["Reference 1 from context", "Reference 2 from context"]
}
"""

    return {
        "validate_context": PROMPT_1,
        "generate_answer": PROMPT_2
    }

def perform_search(query):
    pass