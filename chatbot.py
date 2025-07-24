# chatbot.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY missing. Check your .env file.")

# Configure Gemini
genai.configure(api_key=api_key)

# Choose the model (list available models if unsure)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

try:
    response = model.generate_content("Hello!")
    print(response.text)
except Exception as e:
    print("Gemini error:", e)
