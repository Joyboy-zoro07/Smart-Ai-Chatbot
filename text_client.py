import asyncio
from websockets.client import connect
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_session_id():
    sid = input("🪪 Enter your session ID (or press Enter for 'default_user'): ").strip()
    return sid or "default_user"

async def try_websocket(session_id, user_input):
    uri = f"ws://localhost:8000/ws/chat?session_id={session_id}"
    headers = {
        "x-api-key": API_KEY,
        "session-id": session_id
    }
    try:
        async with connect(uri, extra_headers=headers) as websocket:
            await websocket.send(user_input)
            reply = await asyncio.wait_for(websocket.recv(), timeout=5)
            print("🤖 WebSocket Bot:", reply)
            return True
    except Exception as e:
        print("⚠️ WebSocket failed:", e)
        return False

def call_rest(session_id, user_input):
    try:
        res = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"session_id": session_id, "message": user_input},
            headers={"x-api-key": API_KEY}
        )
        if res.status_code == 200:
            print("🤖 REST Bot:", res.json().get("reply", "[No reply]"))
        else:
            print("❌ REST error:", res.text)
    except Exception as e:
        print("❌ REST exception:", e)

def text_chat_loop(session_id):
    while True:
        msg = input("You (type 'back' to switch mode or 'exit' to quit): ").strip()
        if msg.lower() == "back":
            break
        elif msg.lower() == "exit":
            print("👋 Goodbye!")
            exit()

        success = asyncio.run(try_websocket(session_id, msg))
        if not success:
            call_rest(session_id, msg)
