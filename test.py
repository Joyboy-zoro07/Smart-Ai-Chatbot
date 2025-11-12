import redis
import json

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Fetch all stored memory texts and vectors
texts = r.lrange("memory:texts", 0, -1)
vectors = r.lrange("memory:vectors", 0, -1)

# Sanity check
if len(texts) != len(vectors):
    print(f"⚠️ Mismatch! {len(texts)} texts vs {len(vectors)} vectors")
else:
    print(f"✅ Found {len(texts)} memory entries\n")

# Print each memory item with decoded vector info
for i, (text, vec_json) in enumerate(zip(texts, vectors), 1):
    vector = json.loads(vec_json)
    print(f"{i:02d}. 📝 Text: {text}")
    print(f"    🔢 Vector Shape: ({len(vector)},), Sample: {vector[:5]} ...\n")
