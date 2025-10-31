from pyrogram import Client, filters, enums
from RISHUCHATBOT import RISHUCHATBOT as app
import asyncio
import random
import config
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram.errors import ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError
from pyrogram.types import Message
from pyrogram.enums import ChatAction

# -------------------- MongoDB --------------------
mongodb = MongoCli(config.MONGO_URL)
db = mongodb.Anonymous

sticker_db = db.stickers.sticker
lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status
lock_db = db.locked_words.words  # Locked words collection

CHAT_STORAGE = [
    "mongodb+srv://chatbot1:a@cluster0.pxbu0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot2:b@cluster0.9i8as.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot3:c@cluster0.0ak9k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot4:d@cluster0.4i428.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot5:e@cluster0.pmaap.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot6:f@cluster0.u63li.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot7:g@cluster0.mhzef.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot8:h@cluster0.okxao.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot9:i@cluster0.yausb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot10:j@cluster0.9esnn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
]

VIPBOY = MongoCli(random.choice(CHAT_STORAGE))
chatdb = VIPBOY.Anonymous
chatai = chatdb.Word.WordDb
storeai = VIPBOY.Anonymous.Word.NewWordDb  

reply = []
status_cache = []
sticker = []
LOAD = "FALSE"

# -------------------- Cache Loader --------------------
async def load_caches():
    global reply, sticker, LOAD, status_cache
    if LOAD == "TRUE":
        return
    LOAD = "TRUE"
    reply.clear()
    sticker.clear()
    print("All cache cleaned ✅")
    await asyncio.sleep(1)
    try:
        print("Loading All Caches...")
        reply = await chatai.find().to_list(length=10000)
        print("Replies Loaded ✅")
        await asyncio.sleep(1)
        status_cache = await status_db.find().to_list(length=None)
        print("Status Loaded ✅")
        sticker = await sticker_db.find().to_list(length=None)
        if not sticker:
            sticker_id = "CAACAgUAAxkBAAENzH5nsI3qB-eJNDAUZQL9v3SQl_m-DAACigYAAuT1GFUScU-uCJCWAjYE"
            await sticker_db.insert_one({"sticker_id": sticker_id})
        print("Sticker Loaded ✅")
        print("All caches loaded 👍 ✅")
        LOAD = "FALSE"
    except Exception as e:
        print(f"Error loading caches: {e}")
        LOAD = "FALSE"
    return

# -------------------- Chat Reply --------------------
async def get_reply(message_text: str):
    global reply
    matched_replies = [reply_data for reply_data in reply if reply_data["word"] == message_text]
    if matched_replies:
         return random.choice(matched_replies)
    return random.choice(reply) if reply else None

async def get_chat_status_from_cache(chat_id, bot_id):
    global status_cache
    for entry in status_cache:
        if entry.get("chat_id") == chat_id and entry.get("bot_id") == bot_id:
            return entry.get("status", "enabled")
    return None

# -------------------- Chatbot Enable/Disable --------------------
@app.on_message(filters.command("chatbot", prefixes=[".", "/"]))
async def chatbot_command(client: Client, message: Message):
    command = message.text.split()
    if len(command) > 1:
        flag = command[1].lower()
        chat_id = message.chat.id
        bot_id = client.me.id if client.me else None
        if not bot_id:
            return

        if flag in ["on", "enable"]:
            await status_db.update_one(
                {"chat_id": chat_id, "bot_id": bot_id},
                {"$set": {"status": "enabled"}},
                upsert=True
            )
            await message.reply_text(f"Chatbot has been **enabled** for this chat ✅.")
            await load_caches()
        elif flag in ["off", "disable"]:
            await status_db.update_one(
                {"chat_id": chat_id, "bot_id": bot_id},
                {"$set": {"status": "disabled"}},
                upsert=True
            )
            await message.reply_text(f"Chatbot has been **disabled** for this chat ❌.")
            await load_caches()
        else:
            await message.reply_text("Invalid option! Use `/chatbot on` or `/chatbot off`.")
    else:
        await message.reply_text(
            "Please specify an option to enable or disable the chatbot.\n\n"
            "Example: `/chatbot on` or `/chatbot off`"
        )

# -------------------- Save Replies --------------------
async def save_reply(original_message: Message, reply_message: Message):
    global reply
    try:
        reply_data = {
            "word": original_message.text,
            "text": None,
            "check": "none",
        }

        if getattr(reply_message, "sticker", None):
            reply_data["text"] = reply_message.sticker.file_id
            reply_data["check"] = "sticker"
        elif getattr(reply_message, "photo", None):
            reply_data["text"] = reply_message.photo.file_id
            reply_data["check"] = "photo"
        elif getattr(reply_message, "video", None):
            reply_data["text"] = reply_message.video.file_id
            reply_data["check"] = "video"
        elif getattr(reply_message, "audio", None):
            reply_data["text"] = reply_message.audio.file_id
            reply_data["check"] = "audio"
        elif getattr(reply_message, "animation", None):
            reply_data["text"] = reply_message.animation.file_id
            reply_data["check"] = "gif"
        elif getattr(reply_message, "voice", None):
            reply_data["text"] = reply_message.voice.file_id
            reply_data["check"] = "voice"
        elif getattr(reply_message, "text", None):
            reply_data["text"] = reply_message.text
            reply_data["check"] = "none"

        is_chat = await chatai.find_one(reply_data)
        if not is_chat:
            await chatai.insert_one(reply_data)
            reply.append(reply_data)

    except Exception as e:
        print(f"Error in save_reply: {e}")

# -------------------- Reply with Typing --------------------
async def reply_message(client, chat_id, bot_id, message_text, message):
    try:
        reply_data = await get_reply(message_text)
        if reply_data:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(random.uniform(0.5, 2))

            check = reply_data.get("check")
            text = reply_data.get("text")

            if check == "sticker" and text:
                await message.reply_sticker(text)
            elif check == "photo" and text:
                await message.reply_photo(text)
            elif check == "video" and text:
                await message.reply_video(text)
            elif check == "audio" and text:
                await message.reply_audio(text)
            elif check == "gif" and text:
                await message.reply_animation(text)
            elif check == "voice" and text:
                await message.reply_voice(text)
            elif text:
                await message.reply_text(text, disable_web_page_preview=True)

    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError):
        return
    except Exception as e:
        print(f"Error in reply_message: {e}")

# -------------------- Lock System --------------------
@app.on_message(filters.command("lock", prefixes=[".", "/"]) & filters.user(config.OWNER_ID))
async def lock_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please specify a word to lock.\nExample: `/lock badword`")
    word_to_lock = message.text.split(None, 1)[1].lower().strip()
    exists = await lock_db.find_one({"word": word_to_lock})
    if exists:
        return await message.reply_text(f"The word `{word_to_lock}` is already locked.")
    await lock_db.insert_one({"word": word_to_lock})
    await message.reply_text(f"✅ The word `{word_to_lock}` has been locked. The bot will no longer reply to it.")

@app.on_message(filters.command("unlock", prefixes=[".", "/"]) & filters.user(config.OWNER_ID))
async def unlock_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please specify a word to unlock.\nExample: `/unlock badword`")
    word_to_unlock = message.text.split(None, 1)[1].lower().strip()
    await lock_db.delete_one({"word": word_to_unlock})
    await message.reply_text(f"✅ The word `{word_to_unlock}` has been unlocked. The bot can reply to it now.")

async def is_word_locked(message_text: str):
    word_text = message_text.lower()
    locked = await lock_db.find_one({"word": word_text})
    return bool(locked)

# -------------------- Main Chatbot Handler (Fixed) --------------------
@app.on_message(filters.incoming, group=1)
async def chatbot(client: Client, message: Message):
    global sticker
    bot_id = client.me.id if client.me else None
    if not bot_id:
        return

    if not sticker:
        await load_caches()
        return

    if not message.from_user or message.from_user.is_bot:
        return

    chat_id = message.chat.id

    try:
        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", "@", ".", "?", "#"]):
            return

        is_reply_from_bot = (
            message.reply_to_message 
            and message.reply_to_message.from_user 
            and message.reply_to_message.from_user.id == bot_id
        )

        if is_reply_from_bot or (not message.reply_to_message):
            chat_status = await get_chat_status_from_cache(chat_id, bot_id)
            if chat_status == "disabled":
                return

            message_text = message.text.lower() if message.text else ""

            if await is_word_locked(message_text):
                return

            greetings = {
                "gn": f"Good Night! Sweet dreams {message.from_user.mention} 🌙✨",
                "good night": f"Good Night! Sweet dreams {message.from_user.mention} 🌙✨",
                "gm": f"Good Morning ji! {message.from_user.mention} 🙈",
                "good morning": f"Good Morning ji! {message.from_user.mention} 🙈",
                "hello": f"Hi {message.from_user.mention} 😁 kaise ho??",
                "hii": f"Hi {message.from_user.mention} 😁 kaise ho??",
                "hey": f"Hi {message.from_user.mention} 😁 kaise ho??",
                "bye": f"Goodbye! Take care! {message.from_user.mention} 👋😏",
                "goodbye": f"Goodbye! Take care! {message.from_user.mention} 👋😏",
                "thanks": "hehe welcome! 😜",
                "thank you": "hehe welcome! 😜"
            }

            for key, val in greetings.items():
                if key in message_text:
                    await client.send_chat_action(chat_id, ChatAction.TYPING)
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    return await message.reply_text(val)

            await reply_message(client, chat_id, bot_id, message_text, message)

        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)

    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError, asyncio.TimeoutError):
        return
    except Exception as e:
        print(f"Error in chatbot handler: {e}")