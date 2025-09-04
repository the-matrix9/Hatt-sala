

from . import db

chatbotdb = db.chatbot  # collection bana lo

async def is_chatbot_enabled(chat_id: int) -> bool:
    chat = await chatbotdb.find_one({"chat_id": chat_id})
    return chat.get("enabled", False) if chat else False

async def enable_chatbot(chat_id: int):
    await chatbotdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": True}},
        upsert=True,
    )

async def disable_chatbot(chat_id: int):
    await chatbotdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": False}},
        upsert=True,
    )