# config/gemini.py
import os
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API = os.getenv("GEMINI_API_KEY")

if not GEMINI_API:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

# Create and export client
client = genai.Client(api_key=GEMINI_API)
