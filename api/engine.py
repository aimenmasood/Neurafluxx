import os
import google.generativeai as genai
from groq import Groq
from rag.retriever import retrieve
from rag.prompt import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini & Groq
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.5-flash')
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_response(query):
    # --- STEP 0: STATELESS GUARDRAILS ---
    clean_query = query.lower().strip()
    
    # Handle Greetings
    greetings = ["hello", "hi", "hey", "assalam o alaikum"]
    if clean_query in greetings:
        return "Hello! Welcome to NeuraFlux. What brings you to us today as you look to explore AI for your business?"

    # Handle "Yes" (Intent Expansion for RAG)
    if clean_query in ["yes", "yeah", "yup", "sure", "ok", "okay"]:
        query = "Tell me how the NeuraFlux free AI growth audit helps my business and where to book it."

    # Step 1: Context Retrieval Layer
    try:
        context = retrieve(query)
    except Exception as e:
        print(f"[DEBUG] Retrieval failed: {e}")
        context = "" 

    # Step 2: Generation (Groq with Gemini Fallback)
    # We use a 200 token limit as requested
    try:
        print("[DEBUG] Attempting Groq (Llama 3.3)...")
        user_message = f"Context:\n{context}\n\nUser Question: {query}" if context.strip() else f"(No context found)\n\nUser Question: {query}"
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            timeout=5.0, 
            temperature=0.1,
            max_tokens=200 
        )
        answer = chat_completion.choices[0].message.content.strip()

    except Exception as groq_err:
        print(f"[DEBUG] Groq failed. Switching to Gemini...")
        
        try:
            # Gemini uses a single prompt string for generate_content
            full_prompt = f"{SYSTEM_PROMPT}\n\nUser Message: {user_message}"
            response = gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.1,
                )
            )
            answer = response.text.strip() if response.text else "I'm having trouble retrieving that right now."

        except Exception as gemini_err:
            return "Our systems are currently busy. Please try asking again in a few seconds!"

    # --- STEP 3: POST-PROCESSING (Cleanup) ---
    # Remove any accidental list symbols and ensure the sentence is closed
    final_answer = answer.replace("- ", "").replace("* ", "").replace("Certainly,", "").replace("Absolutely,", "")
    
    if final_answer and final_answer[-1] not in ['.', '!', '?']:
        last_period = final_answer.rfind('.')
        if last_period != -1:
            final_answer = final_answer[:last_period + 1]

    return final_answer.strip()