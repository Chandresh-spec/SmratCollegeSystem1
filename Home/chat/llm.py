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

    # Using Zephyr, a highly reliable model for instruction following
    client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=api_key)

    if context and context.strip():
        # Trim context to prevent context window overflow
        context = context[:6000]
        system_prompt = (
            "You are a helpful AI assistant. Answer the user's question using the provided context from their document. "
            "If the context contains information relevant to the question, provide a detailed answer based on it. "
            "If the context does NOT contain any information related to the question at all, "
            "say: 'This topic is not covered in the uploaded document.'"
        )
        user_prompt = f"--- Document Context ---\n{context}\n--- End Context ---\n\nQuestion: {question}"
    else:
        system_prompt = "You are a helpful AI assistant."
        user_prompt = f"Question: {question}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    for attempt in range(2):
        try:
            response = client.chat_completion(
                messages=messages,
                max_tokens=512
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Hugging Face attempt {attempt+1} failed: {e}")
            time.sleep(1)
            
    return "The AI service is taking too long to respond. Please try again in a moment."
