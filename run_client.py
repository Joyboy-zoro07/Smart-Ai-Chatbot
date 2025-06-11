from text_client import text_chat_loop
from voice_client import voice_chat_loop

def main():
    print("🎛️ AI Chatbot (Text + Voice, Secured)")
    session_id = input("🆔 Enter your session ID: ").strip() or "default_user"

    while True:
        mode = input("💬 Choose mode — 'text', 'voice', or 'exit': ").strip().lower()

        if mode == "text":
            text_chat_loop(session_id)
        elif mode == "voice":
            voice_chat_loop(session_id)
        elif mode == "exit":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please type 'text', 'voice', or 'exit'.")

if __name__ == "__main__":
    main()
