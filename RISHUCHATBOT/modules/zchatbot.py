import asyncio
from pyrogram import filters, enums

@app.on_message(filters.command("gen"))
async def generate_image(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a prompt. Example: /gen cow")
        return

    prompt = " ".join(message.command[1:])
    img_url = f"https://direct-img.rishuapi.workers.dev/?prompt={prompt}"

    try:
        # Step 1: Thinking
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await asyncio.sleep(1)  # simulate thinking

        # Step 2: Recording
        await client.send_chat_action(message.chat.id, enums.ChatAction.RECORD_VIDEO)
        await asyncio.sleep(1)

        # Step 3: Uploading
        await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)

        # Step 4: Send image as spoiler
        await message.reply_photo(
            photo=img_url,
            caption=f"Here’s your image for: {prompt}",
            has_spoiler=True
        )

    except Exception as e:
        await message.reply_text(f"❌ Failed to generate image.\nError: {e}")