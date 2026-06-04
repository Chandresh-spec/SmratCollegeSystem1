import os
import google.generativeai as genai
import time

def ask_llm(context, question):
    """
    Sends a question + context to Google Gemini API.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY is not set. Please add it to your Railway environment variables."

    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        model = genai.GenerativeModel('gemini-pro')

    if context and context.strip():
        context = context[:20000] # Gemini has a large context window
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
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini attempt {attempt+1} failed: {e}")
            time.sleep(1)
            
    return "The AI service is taking too long to respond. Please try again in a moment."
