import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from RISHUCHATBOT import RISHUCHATBOT as app


# Command: /img sun set view
@app.on_message(filters.command(["img", "gen", "image", "make"]))
async def image_gen_handler(client, message):
    if (
        message.text.startswith(f"/img@DikshaChatBot")
        and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    elif len(message.command) > 1:
        user_input = " ".join(message.command[1:])
    else:
        await message.reply_text("ᴇxᴀᴍᴘʟᴇ :- `/gen sun set view`")
        return

    try:
        # Show effects
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(1.5)

        await client.send_chat_action(message.chat.id, ChatAction.RECORD_VIDEO)
        await asyncio.sleep(1.5)

        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        await asyncio.sleep(1.5)

        # Encode prompt to handle spaces
        encoded_prompt = requests.utils.quote(user_input)
        api_url = f"https://direct-img.rishuapi.workers.dev/?prompt={encoded_prompt}"

        # Send image as spoiler
        await message.reply_photo(
            api_url,
            caption=f"🎨 ɢᴇɴᴇʀᴀᴛᴇᴅ ғᴏʀ: `{user_input}`\n🍭 ɢᴇɴᴇʀᴀᴛᴇᴅ  @DikshaChatBot",
            has_spoiler=True
        )

    except Exception as e:
        await message.reply_text("⚠️ ᴇʀʀᴏʀ ɪɴ ɪᴍᴀɢᴇ ɢᴇɴᴇʀᴀᴛɪᴏɴ!")