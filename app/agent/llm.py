# app/agent/llm.py

import os
import hashlib
from dotenv import load_dotenv
from openai import OpenAI
from app.agent.redis_client import redis_client

# Load .env from project root
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print("DEBUG OPENAI_API_KEY:", api_key)  # you should see your key once on startup

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set.\n"
        "Create a .env file in the project root with:\n"
        "OPENAI_API_KEY=your_real_key_here"
    )

client = OpenAI(api_key=api_key)

CACHE_TTL = 3600  # 1 hour


def ask_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Sends a prompt to OpenAI chat model and returns plain text.
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

    # Cache miss - call OpenAI
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    result = resp.choices[0].message.content

    # Store in cache
    try:
        redis_client.setex(cache_key, CACHE_TTL, result)
        print(f"[CACHE SET] {cache_key[:20]}...")
    except Exception as e:
        print(f"[CACHE ERROR] {e}")

    return result

