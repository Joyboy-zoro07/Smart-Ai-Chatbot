import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import redis
import json

class MemoryStore:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dim)
        self.texts = []
        self.redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self._load_from_redis()

    def embed(self, text):
        embedding = self.model.encode([text])[0]
        return np.array(embedding, dtype=np.float32)

    def add_memory(self, text):
        if self.redis.sismember("memory:text_set", text):
            return  # Skip duplicates
        embedding = self.embed(text)
        self.index.add(np.array([embedding]))
        self.texts.append(text)

        # Save to Redis
        self.redis.rpush("memory:texts", text)
        vector_list = embedding.tolist()
        self.redis.rpush("memory:vectors", json.dumps(vector_list))
        self.redis.sadd("memory:text_set", text)

    def retrieve(self, query, top_k=3):
        if not self.texts:
            return []
        embedding = self.embed(query)
        D, I = self.index.search(np.array([embedding]), top_k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

    def _load_from_redis(self):
        try:
            texts = self.redis.lrange("memory:texts", 0, -1)
            vectors_json = self.redis.lrange("memory:vectors", 0, -1)

            if len(texts) != len(vectors_json):
                print("⚠️ Inconsistent Redis memory. Clearing...")
                self.redis.delete("memory:texts", "memory:vectors", "memory:text_set")
                return

            self.texts = texts
            if texts:
                vectors = [json.loads(v) for v in vectors_json]
                vectors_np = np.array(vectors, dtype=np.float32)
                self.index.add(vectors_np)
                print(f"✅ Loaded {len(texts)} memory items from Redis")
            else:
                print("ℹ️ No previous memory found in Redis.")

        except Exception as e:
            print("❌ Error loading memory from Redis:", e)
            self.index = faiss.IndexFlatL2(self.dim)
            self.texts = []
