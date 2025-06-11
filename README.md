# 🤖 AI Chatbot with FastAPI | WebSocket + REST | TTS + STT | Redis-Persisted Memory

This project is a **secure, intelligent, and interactive chatbot** powered by **OpenAI**, built using **FastAPI**, supporting both **text** and **voice** conversations via **WebSocket** and **REST API**.  
It features:
- 🎙️ Speech-to-Text (STT) using Whisper
- 🔊 Text-to-Speech (TTS) using gTTS
- 🔐 Encrypted memory using Redis + FAISS
- 💬 Emotional intelligence (sentiment detection)
- 🧠 Long-term memory with semantic search
- 🔒 API key-based access control and abuse detection

---

## 📁 Project Structure

| File/Folder         | Purpose                                      |
|---------------------|----------------------------------------------|
| `main.py`           | FastAPI backend (REST + WebSocket)           |
| `run_client.py`     | Unified text + voice client                  |
| `text_client.py`    | Text-only interactive client                 |
| `voice_client.py`   | Voice-only interactive client                |
| `memory_store.py`   | Vector memory store using FAISS + Redis      |
| `.env`              | Secrets like `API_KEY`, `OPENAI_API_KEY`, etc. |
| `requirements.txt`  | Python dependencies                          |
| `abuse_log.txt`     | Logged abusive messages                      |

---

## 🧠 Features

- ✅ **WebSocket + REST fallback** for reliability
- ✅ **Speech-to-Text (STT)** using Whisper
- ✅ **Text-to-Speech (TTS)** using gTTS
- ✅ **Encrypted chat history** in Redis
- ✅ **Semantic memory** via FAISS vector search
- ✅ **Sentiment detection** using TextBlob
- ✅ **Profanity detection & abuse logging**
- ✅ **Rate limiting** per session
- ✅ **Secure access control with `x-api-key`**

---

 🛠️ Setup Instructions

 1. Clone the Repository & Create Virtual Environment
```bash
git clone https://bitbucket.org/your-repo-name/chatbot.git
cd chatbot
python -m venv .venv
source .venv/bin/activate

2. Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

3. Configure .env File
Create a .env file in the root directory:

OPENAI_API_KEY=sk-xxxxxxx             # OpenAI GPT API Key
API_KEY=your-fastapi-secret-key       # Internal auth key for client → backend
ENCRYPTION_KEY=xxxxxxxxxxxxxxxxxxxxx= # 32-byte base64 key for chat encryption

Generate a secure encryption key via Python:

from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())

🚀 Running the App
1. Start FastAPI Server
uvicorn main:app --reload

2. Run the Client

python run_client.py
You'll be asked to:

🆔 Enter a session ID (used across voice & text)

💬 Choose between 'text' or 'voice' mode

🧪 API Endpoints 

| Method | Endpoint   | Description                |
| ------ | ---------- | -------------------------- |
| POST   | `/chat`    | Main chatbot interface     |
| POST   | `/stt`     | Speech-to-text conversion  |
| POST   | `/tts`     | Text-to-speech (MP3 reply) |
| WS     | `/ws/chat` | Real-time WebSocket chat   |

Note: All endpoints require the header x-api-key: your-api-key 

🔐 Security Design 
| Key              | Purpose                              |
| ---------------- | ------------------------------------ |
| `OPENAI_API_KEY` | Used **internally** to access OpenAI |
| `API_KEY`        | Used by clients to access backend    |
| `ENCRYPTION_KEY` | Encrypts/decrypts chat history       |


🧠 Redis-Based Memory System
Chat History: Stored & encrypted by session_id

Memory Store: FAISS-powered persistent embeddings

Abuse Logs: Logged per session in Redis + file

👤 Contributors

Developer: Umang Singh

Organization: HestaBit Technologies

Project: Launchpad Internship (AI Track)