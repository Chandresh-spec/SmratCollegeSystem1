import os
from huggingface_hub import InferenceClient
import time

def ask_llm(context, question):
    """
    Sends a question + context to Hugging Face Inference API.
    """
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        return "HUGGINGFACE_API_KEY is not set. Please add it to your Railway environment variables."

    # Using Mistral 7B, a fast and highly available model that is rarely asleep on the free tier
    client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3", token=api_key)

    if context and context.strip():
        # Trim context to prevent context window overflow
        context = context[:6000]
        user_prompt = (
            "System Instruction: You are a helpful AI assistant. Answer the user's question using the provided context. "
            "If the context does NOT contain any information related to the question at all, "
            "say: 'This topic is not covered in the uploaded document.'\n\n"
            f"--- Document Context ---\n{context}\n--- End Context ---\n\nQuestion: {question}"
        )
    else:
        user_prompt = f"Question: {question}"

    messages = [
        {"role": "user", "content": user_prompt}
    ]

    for attempt in range(2):
        try:
            response = client.chat_completion(
                messages=messages,
                max_tokens=512
            )
            content = response.choices[0].message.content.strip()
            if not content:
                raise ValueError("Model returned an empty string.")
            return content
        except Exception as e:
            print(f"Hugging Face attempt {attempt+1} failed: {e}")
            if attempt == 1:
                return f"Hugging Face API Error: {str(e)}"
            time.sleep(1)
            
    return "The AI service is taking too long to respond. Please try again in a moment."
