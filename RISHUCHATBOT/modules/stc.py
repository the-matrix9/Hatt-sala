import requests
import asyncio
import re
import json
from pyrogram import filters
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError

from RISHUCHATBOT import RISHUCHATBOT as app  # Bot instance
from RISHUCHATBOT.modules.helpers import CLOSE_BTN


# ------------------- Config -------------------
OWNER_ID = 5738579437
SAVED_NUMBERS = ["8418894051"]
SEARCH_HISTORY = []
API_URL = "https://flipcartstore.serv00.net/PHONE/1.php?api_key=cyberGen123&mobile="


# ------------------- Helpers -------------------
def normalize_number(number: str) -> str:
    number = number.strip()
    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("0"):
        number = number[1:]
    return number


def is_valid_number(number: str) -> bool:
    num = normalize_number(number)
    return bool(re.match(r"^[6-9]\d{9}$", num)) and num not in SAVED_NUMBERS


# ------------------- /number Command -------------------
@app.on_message(filters.command("number") & (filters.private | filters.group))
async def number_command_handler(client, message):
    try:
        if len(message.command) != 2:
            return await message.reply_text("Usage:<code> /number mobile_number</code>")

        number = normalize_number(message.command[1])

        if number in SAVED_NUMBERS:
            return await message.reply_text("⚠️ Ye number saved hai, info show nahi ki jaa sakti!")

        if not is_valid_number(number):
            return await message.reply_text("⚠️ Sirf valid Indian number hi chalega!")

        # Add search info
        SEARCH_HISTORY.append({
            "user_id": message.from_user.id,
            "chat_id": message.chat.id,
            "number": number
        })

        processing_msg = await message.reply_text("**⏳ Processing...**")
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        # API Call
        try:
            response = requests.get(API_URL + number, timeout=10)
        except requests.exceptions.RequestException:
            return await processing_msg.edit_text("⚠️ API request fail ho gayi!")

        if response.status_code != 200:
            return await processing_msg.edit_text("⚠️ API se data fetch nahi ho paaya!")

        try:
            data = response.json()
        except ValueError:
            return await processing_msg.edit_text("⚠️ Invalid API response!")

        # Remove unwanted keys from API data
        for key in ["credit", "developer"]:
            data.pop(key, None)

        # Add only Rishu credit in JSON
        output_json = {
            "Developer": "Powered by @Ur_Rishu_143",
            "number_info": data
        }

        # Format output as a copyable JSON code block
        text = "🔋 **Number Search Result **\n\n"
        json_text = "```json\n" + json.dumps(output_json, indent=4) + "\n```"
        mention_text = f"\n**👤 Searched by: [{message.from_user.first_name}](tg://user?id={message.from_user.id})**"

        if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            mention_text += f"\n🆔 Chat ID: {message.chat.id}"

        await processing_msg.delete()
        sent_msg = await message.reply_text(
            text + json_text + mention_text,
            reply_markup=InlineKeyboardMarkup(CLOSE_BTN),
            disable_web_page_preview=True
        )

        # Auto delete after 5 minutes
        await asyncio.sleep(300)
        await sent_msg.delete()

    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError):
        return
    except Exception as e:
        await message.reply_text(f"😅 Unexpected Error:\n{e}")


# ------------------- Close Button -------------------
@app.on_callback_query(filters.regex(r"close_number_msg"))
async def close_number_callback(client, callback_query):
    try:
        await callback_query.message.delete()
    except Exception:
        pass


# ------------------- /save Command (Owner Only) -------------------
@app.on_message(filters.command("save") & filters.user(OWNER_ID))
async def save_number_handler(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: /save number")

    number = normalize_number(message.command[1])
    if number in SAVED_NUMBERS:
        return await message.reply_text("⚠️ Ye number pehle se saved hai!")

    SAVED_NUMBERS.append(number)
    await message.reply_text(f"**✅ Number {number} ab saved hai aur info show nahi hogi.**")


# ------------------- /history Command (Owner Only) -------------------
@app.on_message(filters.command("history") & filters.user(OWNER_ID))
async def history_handler(client, message):
    if not SEARCH_HISTORY:
        return await message.reply_text("ℹ️ Abhi tak koi number search nahi hua.")

    text = "**📜 Search History (Last 20)**\n\n"
    for idx, entry in enumerate(SEARCH_HISTORY[-20:], start=1):
        text += (
            f"{idx}. User ID: {entry['user_id']}, \n"
            f"Chat ID: {entry['chat_id']}, \n"
            f"Number: {entry['number']}\n\n"
        )

    await message.reply_text(text)