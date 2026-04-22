from huggingface_hub import InferenceClient

# Initialize client once

client = InferenceClient(api_key="")

def ask_llm(context, question):
    """
    Sends a question + context to Falcon/Mistral instruct model.
    Handles Hugging Face API safely (text_generation).
    """
    prompt = f"""
You are a helpful AI assistant.
Answer ONLY using the context.
If the answer is not in the context, say "I don't know".

Context:
{context}

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
  




    return response





