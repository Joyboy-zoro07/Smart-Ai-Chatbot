# 🤖 Smart AI Chatbot

A **voice + text intelligent chatbot** built using **FastAPI**, **OpenAI GPT**, **Whisper**, **Redis**, and **FAISS**.  
This chatbot supports both **real-time conversations via WebSockets** and **RESTful APIs**, with **emotional intelligence**, **memory**, and **security features**.

---

## 🚀 Features

- 💬 **Text + Voice Chat Support** (TTS & STT using Whisper and gTTS)
- 🧠 **Long-term memory** with FAISS vector database  
- ⚡ **Short-term memory** caching with Redis  
- 🔐 **Data encryption** using Fernet for secure conversation storage  
- 🧍 **Sentiment analysis** and emotion-based response personalization  
- 🧩 **Rate limiting & abuse detection** for user safety  
- 🌐 **FastAPI backend** with both REST and WebSocket endpoints  
- 🧠 **Context awareness** through topic tracking and keyword extraction  

---

## 🧰 Tech Stack

- **FastAPI** – API framework for backend  
- **OpenAI GPT-4o-mini** – Response generation  
- **Whisper** – Speech-to-text transcription  
- **gTTS** – Text-to-speech output  
- **Redis** – Short-term memory, caching, and rate limiting  
- **FAISS** – Long-term vector memory  
- **Sentence Transformers** – Text embedding  
- **TextBlob** – Sentiment detection  
- **Fernet (Cryptography)** – Secure encryption  
- **Uvicorn** – ASGI server  
- **Python-dotenv** – Environment variable management  

---

## ⚙️ Setup Instructions

### Step1️⃣ Clone the repository
```bash
git clone https://github.com/Joyboy-zoro07/Smart-Ai-Chatbot.git
cd Smart-Ai-Chatbot
Step 2
python3 -m venv .venv
source .venv/bin/activate
Step 3 
pip install -r requirements.txt
Step 4
OPENAI_API_KEY=your_openai_key
API_KEY=your_custom_key
ENCRYPTION_KEY=your_fernet_key
Step 5
redis-server
Step 6
uvicorn main:app --reload
Step 7 
python run_client.py

--------------------------------------
Api Endpoints 
| Method | Endpoint   | Description                      |
| ------ | ---------- | -------------------------------- |
| POST   | `/chat`    | Send a message (text) to chatbot |
| POST   | `/tts`     | Convert text to speech           |
| POST   | `/stt`     | Convert speech to text           |
| WS     | `/ws/chat` | Real-time chat via WebSocket     |
----------------------------------------
Project Structure 
📁 Smart-Ai-Chatbot
├── main.py                # Core FastAPI app with all endpoints
├── memory_store.py        # Long-term memory using FAISS + Redis
├── run_client.py          # Client interface (text + voice)
├── text_client.py         # Text chat client
├── voice_client.py        # Voice chat client
├── requirements.txt       # Dependencies
├── .env                   # Environment file (not uploaded)
├── .gitignore             # Ignore secrets & cache files
└── README.md              # Documentation
--------------------------------------
Security & Optimization

AES-level encryption via Fernet

Rate limiting (1.5s between messages)

Abuse detection using profanity filter

Caching to minimize OpenAI API calls and reduce costs 
--------------------------------------------------
Author

Umang 
B.Tech CSE (AIML), Sharda University
📧 Email: leoumang007@gmail.com


