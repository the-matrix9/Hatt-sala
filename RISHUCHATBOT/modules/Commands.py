import requests
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError
from pyrogram.enums import ChatAction   # ✅ Added import
from RISHUCHATBOT import RISHUCHATBOT as app


# API endpoint
API_URL = "https://rellllll.anshppt19.workers.dev/?prompt="


# Function: Send text to API & get reply
def get_ai_reply(prompt: str) -> str:
    try:
        url = API_URL + requests.utils.quote(prompt)
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get("reply", "Sorry, mujhe samajh nahi aaya 🥲")
        else:
            return "⚠️ API error, baad me try karo!"
    except Exception:
        return "😅 Reply generate karne me problem ho gayi!"


# Main Chatbot Handler
@app.on_message(filters.incoming & filters.text, group=1)
async def chatbot(client: Client, message: Message):
    if not message.from_user or message.from_user.is_bot:
        return

    # Ignore if message starts with command symbols
    if any(message.text.startswith(prefix) for prefix in ["!", "/", "@", ".", "?", "#"]):
        return

    try:
        user_text = message.text.strip()

        # Show typing action
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)  # ✅ Fixed

        # Simulate typing delay
        await asyncio.sleep(1.5)

        # Get AI reply from API
        ai_reply = get_ai_reply(user_text)

        # Send reply
        await message.reply_text(ai_reply, disable_web_page_preview=True)

    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError):
        return
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return