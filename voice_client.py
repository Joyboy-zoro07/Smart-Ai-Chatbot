import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import requests
import asyncio
import uuid
import os
import subprocess
import threading
from websockets.client import connect
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
fs = 16000

def record_audio():
    print("🎤 Recording... Press [Enter] again to STOP")
    recording = []
    def callback(indata, frames, time_info, status):
        recording.append(indata.copy())
    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        input()
    print("✅ Recording stopped. Processing...")
    audio = np.concatenate(recording, axis=0)
    filename = f"input_{uuid.uuid4().hex}.wav"
    write(filename, fs, audio)
    return filename

def transcribe_audio(filename):
    try:
        with open(filename, "rb") as f:
            res = requests.post("http://127.0.0.1:8000/stt", files={"audio": f}, headers={"x-api-key": API_KEY})
        os.remove(filename)
        return res.json()["text"].strip() if res.status_code == 200 else None
    except Exception:
        return None

def play_audio(reply):
    try:
        res = requests.post("http://127.0.0.1:8000/tts", json={"text": reply}, headers={"x-api-key": API_KEY})
        if res.status_code != 200: return
        with open("reply.mp3", "wb") as f:
            f.write(res.content)
        process = subprocess.Popen(["mpg321", "reply.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("🗣️ Speaking... Press 'q' then Enter to stop.")
        threading.Thread(target=lambda: (input().strip().lower() == 'q' and process.terminate()), daemon=True).start()
        process.wait()
        os.remove("reply.mp3")
    except Exception: pass

async def try_websocket(text, session_id):
    uri = f"ws://localhost:8000/ws/chat?session_id={session_id}"
    headers = {
        "x-api-key": API_KEY,
        "session-id": session_id
    }
    try:
        async with connect(uri, extra_headers=headers) as ws:
            await ws.send(text)
            reply = await asyncio.wait_for(ws.recv(), timeout=5)
            print("🤖 WebSocket Bot:", reply)
            play_audio(reply)
            return True
    except Exception:
        return False

def call_rest(text, session_id):
    try:
        res = requests.post("http://127.0.0.1:8000/chat", json={"session_id": session_id, "message": text}, headers={"x-api-key": API_KEY})
        if res.status_code == 200:
            reply = res.json().get("reply", "")
            print("🤖 REST Bot:", reply)
            play_audio(reply)
    except Exception: pass

def voice_chat_loop(session_id):
    while True:
        cmd = input("🔴 Press [Enter] to record or type 'back' to switch mode or 'exit' to quit: ").strip().lower()
        if cmd == "back":
            break
        elif cmd == "exit":
            print("👋 Goodbye!")
            exit()

        fname = record_audio()
        text = transcribe_audio(fname)
        print("📝 You said:", text)
        if not asyncio.run(try_websocket(text, session_id)):
            call_rest(text, session_id)