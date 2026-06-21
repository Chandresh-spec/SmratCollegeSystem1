import os
from huggingface_hub import InferenceClient
import time

def ask_llm(context, question):
    """
    Sends a question + context to Hugging Face Inference API.
    """
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key or api_key == "your_huggingface_key_here":
        return "HUGGINGFACE_API_KEY is not set or is using the default placeholder. Please add a valid Hugging Face token to your .env file."

    from openai import OpenAI

    if context and context.strip():
        # Trim context to prevent context window overflow
        context = context[:6000]
        user_prompt = (
            "System Instruction: You are a helpful AI assistant. Answer the user's question using the provided context.\n\n"
            f"--- Document Context ---\n{context}\n--- End Context ---\n\nQuestion: {question}\nAnswer:"
        )
    else:
        user_prompt = f"Question: {question}\nAnswer:"

    for attempt in range(2):
        try:
            client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=api_key,
            )

            completion = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V4-Pro:novita",
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
            )
            
            content = completion.choices[0].message.content.strip()
            
            if not content:
                raise ValueError("Model returned an empty string.")
            return content
        except Exception as e:
            print(f"Hugging Face attempt {attempt+1} failed: {e}")
            if attempt == 1:
                return f"Hugging Face API Error: {str(e)}"
            time.sleep(1)
            
    return "The AI service is taking too long to respond. Please try again in a moment."
