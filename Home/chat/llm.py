import requests
import time

def ask_llm(context, question):
    """
    Sends a question + context to a highly reliable free API (Pollinations.ai).
    """
    api_url = "https://text.pollinations.ai/"

    if context and context.strip():
        # Trim context if it's extremely long to prevent LLM timeout
        context = context[:3000]
        prompt = (
            "You are a helpful AI assistant. Answer the user's question using the provided context from their document. "
            "If the context contains information relevant to the question, provide a detailed answer based on it. "
            "If the context does NOT contain any information related to the question at all, "
            "say: 'This topic is not covered in the uploaded document.'\n\n"
            f"--- Document Context ---\n{context}\n--- End Context ---\n\n"
            f"Question: {question}\n\nAnswer:"
        )
    else:
        prompt = f"Question: {question}\n\nAnswer:"

    for attempt in range(2):
        try:
            response = requests.post(
                api_url, 
                json={'messages': [{'role': 'user', 'content': prompt}]},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.text
                if "Answer:" in result:
                    return result.split("Answer:")[-1].strip()
                return result.strip()
                
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(1)
            
    return "The AI service is taking too long to respond. Please try again in a moment."
