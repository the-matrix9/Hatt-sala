import asyncio
import requests
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from RISHUCHATBOT import RISHUCHATBOT as app


# ChatGPT Text API class
class ChatGptEs:
    TEXT_API = "https://chatapi.anshppt19.workers.dev/?prompt="

    def ask_question(self, message: str) -> str:
        try:
            url = self.TEXT_API + requests.utils.quote(message)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return str(data.get("reply", "❖ Error: API ne reply nahi diya.")).strip()
        except Exception as e:
            return f"❖ I got an error: {str(e)}"


chatbot_api = ChatGptEs()


# ✅ Commands ko ignore karega, sirf normal text par chalega
@app.on_message(filters.text & ~filters.bot & ~filters.command)
async def chatbot_handler(_, m: Message):
    try:
        # Typing action
        await m._client.send_chat_action(m.chat.id, ChatAction.TYPING)
        await asyncio.sleep(1.5)

        reply = chatbot_api.ask_question(m.text)
        await m.reply_text(reply)

    except Exception as e:
        await m.reply_text(f"❖ Error: {str(e)}")