# app/agent/llm.py

import os
import hashlib
from dotenv import load_dotenv
import google.generativeai as genai
from app.agent.redis_client import redis_client

# Load .env from project root
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("DEBUG GEMINI_API_KEY:", "***" + api_key[-4:] if api_key else None)  # Only show last 4 chars for security

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set.\n"
        "Create a .env file in the project root with:\n"
        "GEMINI_API_KEY=your_real_key_here"
    )

# Configure Gemini API
genai.configure(api_key=api_key)

CACHE_TTL = 3600  # 1 hour


def ask_llm(prompt: str, model: str = "gemini-2.0-flash") -> str:
    """
    Sends a prompt to Google Gemini model and returns plain text.
    Uses Redis caching to avoid redundant API calls.
    """
    # Generate cache key from prompt hash
    cache_key = f"llm:{hashlib.sha256(prompt.encode()).hexdigest()}"

    # Check cache first
    try:
        cached = redis_client.get(cache_key)
        if cached:
            print(f"[CACHE HIT] {cache_key[:20]}...")
            return cached
    except Exception as e:
        print(f"[CACHE ERROR] {e}")

    # Cache miss - call Gemini
    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(prompt)
    result = response.text

    # Store in cache
    try:
        redis_client.setex(cache_key, CACHE_TTL, result)
        print(f"[CACHE SET] {cache_key[:20]}...")
    except Exception as e:
        print(f"[CACHE ERROR] {e}")

    return result
