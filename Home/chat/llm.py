import os
from huggingface_hub import InferenceClient

# Initialize client with API key from environment variable
api_key = os.getenv("HUGGINGFACE_API_KEY")
client = InferenceClient(api_key=api_key)

def ask_llm(context, question):
    """
    Sends a question + context to Falcon/Mistral instruct model.
    Handles Hugging Face API safely (text_generation).
    """
    if context and context.strip():
        prompt = f"""
You are a helpful study assistant.
Answer ONLY using the context provided below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""
    else:
        prompt = f"""
You are a helpful, general-purpose AI assistant. 
Answer the following question using your general knowledge in a conversational manner.

Question:
{question}

Answer:
"""

    
    response = client.chat.completions.create(
        model="Qwen/Qwen3-Coder-Next:novita",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
  




    try:
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        print("LLM Error:", e)
        return "I encountered an error generating an answer."



