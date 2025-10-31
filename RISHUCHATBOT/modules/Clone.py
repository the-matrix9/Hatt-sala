
import logging
import os
import asyncio
import time
import requests
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.types import BotCommand
from config import API_HASH, API_ID, OWNER_ID
from RISHUCHATBOT import RISHUCHATBOT as app, save_clonebot_owner, db as mongodb

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ---------- Globals ----------
CLONES = set()
clonebotdb = mongodb.clonebotdb
RUNNING_CLIENTS = {}  # bot_id -> Client
TOKEN_WATCHER_STARTED = False
TOKEN_WATCHER_LOCK = asyncio.Lock()

BOT_BIO_DESC = (
    "🔋ᴍᴀᴋᴇ ʏᴏᴜʀ ʙᴏᴛ ғʀᴏᴍ @DikshaChatBot \n"
    "🤖 ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Ur_Rishu_143 | ᴄʜᴀᴛ ʙᴏᴛ sʏsᴛᴇᴍ"
)
BDOC = (
    "🔋 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ʙᴏᴛ ᴇᴀsɪʟʏ → @DikshaChatBot\n"
    "🤖 ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Ur_Rishu_143 | ᴄʜᴀᴛ ʙᴏᴛ sʏsᴛᴇᴍ\n"
    "✨ ᴀᴅᴠᴀɴᴄᴇᴅ ғᴇᴀᴛᴜʀᴇs: ʀᴇsᴘᴏɴsɪᴠᴇ, ɪɴᴛᴇʟʟɪɢᴇɴᴛ & ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ\n"
    "🌐 ᴊᴏɪɴ ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ → @Ur_Rishu_143\n"
    "⚡ ʙᴜɪʟᴅ ᴄʜᴀᴛ ᴀᴜᴛᴏᴍᴀᴛᴇ ʜᴀᴠᴇ ғᴜɴ!"
)

# ---------- Helpers ----------
def set_bot_bio_description(bot_token):
    """Set bot description and short description (sync; used in executor)."""
    for attempt in range(3):
        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/setMyDescription",
                data={"description": BDOC},
                timeout=30
            )
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/setMyShortDescription",
                data={"short_description": BOT_BIO_DESC},
                timeout=30
            )
            return True
        except Exception as e:
            logger.warning("[Attempt %s] Failed to set bio/description: %s", attempt+1, e)
            time.sleep(3)
    logger.error("Failed to set bio/description for bot token: %s after 3 attempts.", bot_token)
    return False

def validate_token_sync(bot_token: str, timeout: int = 10) -> dict:
    """Synchronous validation via bot API getMe."""
    try:
        r = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=timeout)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def validate_token(bot_token: str) -> dict:
    """Async wrapper around validate_token_sync."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, validate_token_sync, bot_token)

async def ensure_token_watcher_started():
    """Start the background token watcher once."""
    global TOKEN_WATCHER_STARTED
    async with TOKEN_WATCHER_LOCK:
        if not TOKEN_WATCHER_STARTED:
            TOKEN_WATCHER_STARTED = True
            asyncio.create_task(token_watcher())
            logger.info("Token watcher started.")

async def token_watcher():
    """Background loop: every 10 minutes check tokens and remove invalid ones immediately."""
    while True:
        try:
            logger.info("Token watcher: scanning cloned bots...")
            bots = [bot async for bot in clonebotdb.find({}, {"token": 1, "bot_id": 1, "user_id": 1})]
            for bot_data in bots:
                bot_token = bot_data.get("token")
                bot_id = bot_data.get("bot_id")
                user_id = bot_data.get("user_id")
                if not bot_token:
                    continue
                res = await validate_token(bot_token)
                if not res.get("ok"):
                    # invalid or error — remove
                    await clonebotdb.delete_one({"bot_id": bot_id})
                    CLONES.discard(bot_id)
                    # stop running client if present
                    client = RUNNING_CLIENTS.get(bot_id)
                    if client:
                        try:
                            await client.stop()
                        except Exception:
                            logger.exception("Failed stopping client for bot %s", bot_id)
                        RUNNING_CLIENTS.pop(bot_id, None)
                    # notify owner and the user who created the clone
                    msg = (f"🔔 Removed cloned bot (ID: `{bot_id}`) due to invalid/expired token.\n"
                           f"Reason: `{res.get('error', 'invalid token / getMe failed')}`")
                    try:
                        await app.send_message(int(OWNER_ID), msg)
                        if user_id:
                            await app.send_message(int(user_id), f"⚠️ Your cloned bot (ID `{bot_id}`) was removed because its token became invalid.")
                    except Exception:
                        logger.exception("Failed to send notification about removed clone.")
                    logger.info("Removed invalid token for bot_id %s: %s", bot_id, res)
        except Exception as e:
            logger.exception("Exception in token_watcher loop: %s", e)
        # sleep 10 minutes
        await asyncio.sleep(600)

# ------------------- Clone Bot Command -------------------
@app.on_message(filters.command(["clone", "host", "deploy"]))
async def clone_txt(client, message):
    await ensure_token_watcher_started()

    if len(message.command) < 2:
        await message.reply_text(
            "⚠️ Provide Bot Token after /clone command from @BotFather.\n\n"
            "Example: `/clone your_bot_token_here`"
        )
        return

    bot_token = message.text.split("/clone", 1)[1].strip()
    mi = await message.reply_text("⏳ Checking the bot token...")

    # validate token first (fast)
    res = await validate_token(bot_token)
    if not res.get("ok"):
        await mi.edit_text("❌ Invalid or unreachable bot token. Please provide a valid one from @BotFather.")
        return

    # token ok, show progress
    await mi.edit_text("✅ Token OK. Starting clone...")

    try:
        ai = Client(
            bot_token,
            API_ID,
            API_HASH,
            bot_token=bot_token,
            plugins=dict(root="RISHUCHATBOT/mplugin")
        )
        await mi.edit_text("⏳ Starting the bot client...")
        await ai.start()
        bot = await ai.get_me()
        bot_id = bot.id
        user_id = message.from_user.id

        # Save clone owner
        await save_clonebot_owner(bot_id, user_id)

        # Set bot commands
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get the help menu"),
            BotCommand("clone", "Make your own chatbot"),
            BotCommand("gen", "Generate high quality Image"),
            BotCommand("number", "Get info of number "),
            BotCommand("ping", "Check if the bot is alive or dead"),
            BotCommand("id", "Get users user_id"),
            BotCommand("stats", "Check bot stats"),
            BotCommand("gcast", "Broadcast any message to groups/users"),
            BotCommand("status", "Check chatbot enable or disable in chat"),
            BotCommand("shayri", "Get random shayri for love"),
        ]
        await mi.edit_text("⏳ Setting commands and descriptions...")
        await ai.set_bot_commands(commands)

        # Set bio & description with retries (sync) - run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, set_bot_bio_description, bot_token)

        # Save to DB
        details = {
            "bot_id": bot.id,
            "is_bot": True,
            "user_id": user_id,
            "name": bot.first_name,
            "token": bot_token,
            "username": bot.username,
            "created_at": int(time.time())
        }
        await clonebotdb.insert_one(details)
        CLONES.add(bot.id)
        RUNNING_CLIENTS[bot.id] = ai

        total_clones = await clonebotdb.count_documents({})

        # Notify owner
        try:
            await app.send_message(
                int(OWNER_ID),
                f"**#New_Clone**\n\n**Bot:- @{bot.username}**\n\n**Details:-**\n{details}\n\n**Total Cloned:-** {total_clones}"
            )
        except Exception:
            logger.exception("Failed sending new clone notification to owner")

        await mi.edit_text(
            f"✅ Bot @{bot.username} has been successfully cloned and started.\n"
            f"Manage your clones with: /myclones\nRemove clone by: /delclone <token>\nCheck all cloned bots by: /cloned"
        )

    except (AccessTokenExpired, AccessTokenInvalid):
        await mi.edit_text("❌ Invalid bot token. Please provide a valid one.")
    except Exception as e:
        logger.exception("Error during cloning process:")
        await mi.edit_text(
            f"⚠️ Unexpected error:\n<code>{e}</code>\nForward this message to @Rishu1286 for assistance."
        )

# ------------------- List Cloned Bots (Admin) -------------------
@app.on_message(filters.command("cloned"))
async def list_cloned_bots(client, message):
    try:
        cloned_bots_list = await clonebotdb.find().to_list(length=None)
        if not cloned_bots_list:
            await message.reply_text("No bots have been cloned yet.")
            return
        text = f"**Total Cloned Bots:** {len(cloned_bots_list)}\n\n"
        for bot in cloned_bots_list:
            text += f"**Bot ID:** `{bot.get('bot_id')}`\n"
            text += f"**Bot Name:** {bot.get('name')}\n"
            text += f"**Bot Username:** @{bot.get('username')}\n\n"
        await message.reply_text(text)
    except Exception as e:
        logger.exception(e)
        await message.reply_text("⚠️ An error occurred while listing cloned bots.")

# ------------------- My Clones (user-level) -------------------
@app.on_message(filters.command("myclones"))
async def my_clones(client, message):
    await ensure_token_watcher_started()
    user_id = message.from_user.id
    try:
        user_clones = await clonebotdb.find({"user_id": user_id}).to_list(length=None)
        if not user_clones:
            await message.reply_text("You have no cloned bots.")
            return
        text = f"**Your Cloned Bots ({len(user_clones)}):**\n\n"
        for bot in user_clones:
            text += f"• @{bot.get('username', 'unknown')} (ID: `{bot.get('bot_id')}`)\n"
        await message.reply_text(text)
    except Exception as e:
        logger.exception(e)
        await message.reply_text("⚠️ Error fetching your clones.")

# ------------------- Delete Specific Cloned Bot (by token) -------------------
@app.on_message(filters.command(["delclone", "deleteclone"]))
async def delete_cloned_bot(client, message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ Please provide the bot token after the command.\n\nExample: `/delclone your_bot_token_here`")
        return

    bot_token = " ".join(message.command[1:])
    ok = await message.reply_text("⏳ Checking the bot token...")

    try:
        cloned_bot = await clonebotdb.find_one({"token": bot_token})
        if cloned_bot:
            bot_id = cloned_bot["bot_id"]
            # stop if running
            client_inst = RUNNING_CLIENTS.get(bot_id)
            if client_inst:
                try:
                    await client_inst.stop()
                except Exception:
                    logger.exception("Failed stopping running client during deletion.")
                RUNNING_CLIENTS.pop(bot_id, None)
            await clonebotdb.delete_one({"token": bot_token})
            CLONES.discard(bot_id)
            await ok.edit_text(
                f"✅ Your cloned bot has been removed from the database.\n"
                f"⚠️ Revoke your bot token from @BotFather to stop it completely."
            )
        else:
            await ok.edit_text(
                "⚠️ Provide valid Bot Token after /delclone command from @BotFather.\n\n"
                "Example: `/delclone your_bot_token_here`"
            )
    except Exception as e:
        logger.exception(e)
        await ok.edit_text(f"⚠️ An error occurred while deleting the cloned bot: {e}")

# ------------------- Delete All Cloned Bots (owner only) -------------------
@app.on_message(filters.command("delallclone") & filters.user(int(OWNER_ID)))
async def delete_all_cloned_bots(client, message):
    try:
        a = await message.reply_text("⏳ Deleting all cloned bots...")
        # stop running clients
        for bot_id, c in list(RUNNING_CLIENTS.items()):
            try:
                await c.stop()
            except Exception:
                logger.exception("Failed to stop client %s", bot_id)
        RUNNING_CLIENTS.clear()
        await clonebotdb.delete_many({})
        CLONES.clear()
        await a.edit_text("✅ All cloned bots have been deleted successfully.")
        # optional restart (keep if you want auto-restart)
        os.system(f"kill -9 {os.getpid()} && bash start")
    except Exception as e:
        logger.exception(e)
        await a.edit_text(f"⚠️ An error occurred while deleting all cloned bots: {e}")

# ------------------- Restart Cloned Bots -------------------
async def restart_bots():
    """Restart all cloned bots after main bot restarts."""
    global CLONES
    try:
        logger.info("Restarting all cloned bots...")
        bots = [bot async for bot in clonebotdb.find()]

        async def restart_bot(bot_data):
            bot_token = bot_data["token"]
            try:
                ai = Client(bot_token, API_ID, API_HASH, bot_token=bot_token,
                            plugins=dict(root="RISHUCHATBOT/mplugin"))
                await ai.start()
                bot_info = await ai.get_me()

                # Restore commands (minimal)
                await ai.set_bot_commands([
                    BotCommand("start", "Start the bot"),
                    BotCommand("help", "Get the help menu"),
                    BotCommand("clone", "Make your own chatbot"),
                    BotCommand("ping", "Check if the bot is alive or dead"),
                ])

                # Restore bio & description
                # run sync function without blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, set_bot_bio_description, bot_token)

                CLONES.add(bot_info.id)
                RUNNING_CLIENTS[bot_info.id] = ai

            except (AccessTokenExpired, AccessTokenInvalid):
                try:
                    await clonebotdb.delete_one({"token": bot_token})
                except Exception:
                    logger.exception("Failed removing expired token record for bot_data: %s", bot_data)
                logger.info("Removed expired or invalid token for bot ID: %s", bot_data.get("bot_id"))
            except Exception as e:
                logger.exception("Error while restarting bot: %s", e)

        await asyncio.gather(*(restart_bot(bot_data) for bot_data in bots))

    except Exception as e:
        logger.exception("Error while restarting bots: %s", e)