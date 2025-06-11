import openai
import traceback
import os
import redis
import re
import tiktoken
import time
import whisper
import uuid
import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from memory_store import MemoryStore
from gtts import gTTS
from cryptography.fernet import Fernet
from textblob import TextBlob
from better_profanity import profanity
from datetime import datetime

# ========== LOAD CONFIG ==========
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
API_KEY = os.getenv("API_KEY")
fernet_key = os.getenv("ENCRYPTION_KEY")
if not fernet_key:
    raise ValueError("❌ ENCRYPTION_KEY missing in .env")

# Encryption handler
fernet = Fernet(fernet_key)
profanity.load_censor_words()

# ========== APP SETUP ==========
app = FastAPI()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
memory = MemoryStore()
whisper_model = whisper.load_model("base")
MAX_CONTEXT = 10
ABUSE_LOG_FILE = "abuse_log.txt"

# 🔒 Suppress access logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# ========== DATA MODELS ==========
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

class TTSRequest(BaseModel):
    text: str

# ========== UTILITY FUNCTIONS ==========
# Encrypts plain text using Fernet
def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

# Decrypts Fernet token back to plain text
def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

# Validates API key for authentication
def verify_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# Determines sentiment-based emotion of input text
def detect_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity < -0.3:
        return "sad"
    elif polarity > 0.3:
        return "happy"
    else:
        return "neutral"

# Implements simple rate limiting per session
def is_rate_limited(session_id):
    key = f"rate:{session_id}"
    last = r.get(key)
    now = time.time()
    if last and now - float(last) < 1.5:
        return True
    r.set(key, now)
    return False

# Retrieves recent chat history with user from Redis (decrypted)
def get_history(session_id):
    history = r.lrange(session_id, -MAX_CONTEXT * 2, -1)
    result = []
    for i in range(0, len(history), 2):
        try:
            result.append({"role": "user", "content": decrypt(history[i])})
            if i + 1 < len(history):
                result.append({"role": "assistant", "content": decrypt(history[i + 1])})
        except Exception:
            continue
    return result

# Saves latest chat exchange to Redis (encrypted)
def save_history(session_id, user_msg, bot_msg):
    r.rpush(session_id, encrypt(user_msg), encrypt(bot_msg))
    r.ltrim(session_id, -MAX_CONTEXT * 2, -1)

# Extracts keywords (4+ letter words) from message to build user topic context
def extract_keywords(text):
    words = re.findall(r'\b\w{4,}\b', text.lower())
    ignore = {"what", "your", "about", "this", "that", "have", "with", "from", "there", "where"}
    return list(set(words) - ignore)

# Updates topic keywords for the session
def update_user_context(session_id, user_msg):
    keywords = extract_keywords(user_msg)
    if keywords:
        r.sadd(f"{session_id}:topics", *keywords)

# Retrieves stored user preferences from Redis
def get_preferences(session_id):
    return r.hgetall(f"{session_id}:prefs")

# Logs abusive messages in Redis and a local file
def log_abuse(session_id, message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    r.rpush(f"{session_id}:abuse_log", message)
    with open(ABUSE_LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] [Session: {session_id}] {message}\n")

# ========== REST ENDPOINT: /chat ==========
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, x_api_key: str = Header(...)):
    verify_key(x_api_key)
    if is_rate_limited(request.session_id):
        raise HTTPException(status_code=429, detail="Too many requests. Slow down.")

    if profanity.contains_profanity(request.message):
        log_abuse(request.session_id, request.message)
        return ChatResponse(reply="⚠️ Please avoid using offensive language.")

    try:
        cache_key = f"cache:{request.message.strip().lower()}"
        cached = r.get(cache_key)
        if cached:
            return ChatResponse(reply=decrypt(cached))

        # Constructing conversation context
        history = get_history(request.session_id)
        emotion = detect_emotion(request.message)
        prefs = get_preferences(request.session_id)
        personality = prefs.get("personality", "neutral")

        # System messages for LLM behavior
        history.insert(0, {
            "role": "system",
            "content": f"You are a {personality} chatbot. The user seems {emotion}. Respond appropriately."
        })

        # Add memory-based context
        for mem in memory.retrieve(request.message):
            history.insert(1, {"role": "assistant", "content": f"Memory: {mem}"})

        # Topic and preference enrichment
        topics = list(r.smembers(f"{request.session_id}:topics"))
        if topics:
            history.insert(1, {"role": "system", "content": f"User is interested in: {', '.join(topics)}"})
        if prefs:
            pref_str = "; ".join(f"{k}: {v}" for k, v in prefs.items())
            history.insert(1, {"role": "system", "content": f"User preferences: {pref_str}"})

        # Append current user input
        history.append({"role": "user", "content": request.message})

        # OpenAI chat completion call
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=history
        )
        reply = response.choices[0].message.content.strip()

        # Store conversation & cache
        save_history(request.session_id, request.message, reply)
        update_user_context(request.session_id, request.message)
        if len(request.message) > 20:
            memory.add_memory(request.message)

        r.set(cache_key, encrypt(reply), ex=3600)
        return ChatResponse(reply=reply)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {e}")

# ========== REST ENDPOINT: /tts ==========
@app.post("/tts")
async def text_to_speech(request: TTSRequest, x_api_key: str = Header(...)):
    verify_key(x_api_key)
    try:
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=request.text.strip(), lang="en")
        tts.save(filename)
        return FileResponse(path=filename, media_type="audio/mpeg", filename="reply.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")

# ========== REST ENDPOINT: /stt ==========
@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...), x_api_key: str = Header(...)):
    verify_key(x_api_key)
    try:
        path = f"temp_{audio.filename}"
        with open(path, "wb") as f:
            f.write(await audio.read())
        result = whisper_model.transcribe(path)
        os.remove(path)
        return {"text": result["text"].strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT Error: {str(e)}")

# ========== WEBSOCKET ENDPOINT ==========
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    session_id = websocket.query_params.get("session_id", "default_user")
    x_api_key = websocket.headers.get("x-api-key")
    if x_api_key != API_KEY:
        await websocket.close(code=1008)
        return

    try:
        while True:
            msg = await websocket.receive_text()

            if profanity.contains_profanity(msg):
                log_abuse(session_id, msg)
                await websocket.send_text("⚠️ Please avoid using offensive language.")
                continue

            history = get_history(session_id)
            emotion = detect_emotion(msg)
            prefs = get_preferences(session_id)
            personality = prefs.get("personality", "neutral")

            history.insert(0, {
                "role": "system",
                "content": f"You are a {personality} chatbot. The user seems {emotion}. Respond appropriately."
            })

            for mem in memory.retrieve(msg):
                history.insert(1, {"role": "assistant", "content": f"Memory: {mem}"})
            topics = list(r.smembers(f"{session_id}:topics"))
            if topics:
                history.insert(1, {"role": "system", "content": f"User is interested in: {', '.join(topics)}"})
            if prefs:
                pref_str = "; ".join(f"{k}: {v}" for k, v in prefs.items())
                history.insert(1, {"role": "system", "content": f"User preferences: {pref_str}"})

            history.append({"role": "user", "content": msg})

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=history
                )
                reply = response.choices[0].message.content.strip()
                await websocket.send_text(reply)

                save_history(session_id, msg, reply)
                update_user_context(session_id, msg)
                if len(msg) > 20:
                    memory.add_memory(msg)

            except Exception as e:
                await websocket.send_text("[ERROR] " + str(e))

    except WebSocketDisconnect:
        pass
