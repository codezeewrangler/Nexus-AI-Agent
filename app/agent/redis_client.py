import os
import redis

# Connect to Redis, supporting Docker (REDIS_HOST env) or localhost
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True  # Return strings instead of bytes
)

