import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from RISHUCHATBOT import RISHUCHATBOT as app


# Command: /img dog
@app.on_message(filters.command(["img", "gen", "image"]))
async def image_gen_handler(client, message):
    if (
        message.text.startswith(f"/img@{app.username}")
        and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    elif len(message.command) > 1:
        user_input = " ".join(message.command[1:])
    else:
        await message.reply_text("ᴇxᴀᴍᴘʟᴇ :- `/img dog`")
        return

    try:
        # Show typing, recording, upload effects
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(1.5)

        await client.send_chat_action(message.chat.id, ChatAction.RECORD_VIDEO)
        await asyncio.sleep(1.5)

        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        await asyncio.sleep(1.5)

        # API call
        api_url = f"https://direct-img.rishuapi.workers.dev/?prompt={user_input}"

        # Send generated image
        await message.reply_photo(api_url, caption=f"🎨 ɢᴇɴᴇʀᴀᴛᴇᴅ ғᴏʀ: `{user_input}`")

    except Exception as e:
        await message.reply_text("⚠️ ᴇʀʀᴏʀ ɪɴ ɪᴍᴀɢᴇ ɢᴇɴᴇʀᴀᴛɪᴏɴ!")