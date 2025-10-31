import json
import os
import re
from typing import Tuple

from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from RISHUCHATBOT import RISHUCHATBOT as app

from RISHUCHATBOT.modules.Babu import (
    is_admin,
    get_config, update_config,
    increment_warning, reset_warnings,
    is_whitelisted, add_whitelist, remove_whitelist, get_whitelist
)

# ---------------------------
# Configuration / constants
# ---------------------------
BIO_STATE_FILE = "bio_state.json"  # persistence file for bio ON/OFF per chat

URL_PATTERN = re.compile(
    r'(https?://|www\.)[a-zA-Z0-9.\-]+(\.[a-zA-Z]{2,})+(/[a-zA-Z0-9._%+-]*)*'
)

START_IMG_URL = "https://graph.org/file/e9eed432610bc524cd1b1-b423df52eace6fae7c.jpg"
HELP_IMG_URL = START_IMG_URL
CONFIG_IMG_URL = START_IMG_URL

BOT_OWNER = "Rishu1286"
BOT_OWNER_USERNAME = "Rishu1286"

# ---------------------------
# Persistence helpers
# ---------------------------
def _ensure_file():
    if not os.path.exists(BIO_STATE_FILE):
        with open(BIO_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_bio_state() -> dict:
    _ensure_file()
    try:
        with open(BIO_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_bio_state(state: dict):
    with open(BIO_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def set_bio_state(chat_id: int, enabled: bool):
    state = load_bio_state()
    state[str(chat_id)] = bool(enabled)
    save_bio_state(state)

def get_bio_state(chat_id: int) -> bool:
    state = load_bio_state()
    return bool(state.get(str(chat_id), False))  # default OFF

# ---------------------------
# Start / Help commands
# ---------------------------
@app.on_message(filters.command("biostart"))
async def start_handler(client: Client, message):
    chat_id = message.chat.id
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"
    try:
        await client.send_photo(
            chat_id=chat_id,
            photo=START_IMG_URL,
            caption=(
                "<b>✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ʙɪᴏʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʙᴏᴛ! ✨</b>\n\n"
                "🛡️ ɪ ʜᴇʟᴘ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘs ғʀᴏᴍ ᴜsᴇʀs ᴡɪᴛʜ ʟɪɴᴋs ɪɴ ᴛʜᴇɪʀ ʙɪᴏ.\n\n"
                "<b>🔹 ᴋᴇʏ ғᴇᴀᴛᴜʀᴇs:</n>\n"
                "   • ᴀᴜᴛᴏ ᴜʀʟ ᴅᴇᴛᴇᴄᴛɪᴏɴ ɪɴ ᴜsᴇʀ ʙɪᴏs\n"
                "   • ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ\n"
                "   • ᴀᴜᴛᴏ-ᴍᴜᴛᴇ ᴏʀ ʙᴀɴ ᴡʜᴇɴ ʟɪᴍɪt ɪs ʀᴇᴀᴄʜᴇᴅ\n"
                "   • ᴡʜɪᴛᴇʟɪsᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ғᴏʀ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs\n\n"
                "<b>ᴜsᴇ /bio &lt;on|off|status&gt; ᴛᴏ ᴛᴏɢɢʟᴇ ʙɪᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ (ᴅᴇꜰᴀᴜʟᴛ: OFF)</b>"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=add_url)],
                [
                    InlineKeyboardButton("🛠️ sᴜᴘᴘᴏʀᴛ", url="https://t.me/ll_KHAYALI_PULAO_ll"),
                    InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url=f"https://t.me/{BOT_OWNER_USERNAME}" if BOT_OWNER_USERNAME else f"tg://user?id={BOT_OWNER}")
                ],
                [InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )
    except Exception as e:
        print(f"Error sending image: {e}")
        await client.send_message(chat_id, "Welcome to Bio Protector Bot! Use /bio <on|off|status> to manage protection.")

@app.on_message(filters.command("bhelp"))
async def help_handler(client: Client, message):
    chat_id = message.chat.id
    help_text = (
        "<b>🛠️ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs & ᴜsᴀɢᴇ</b>\n\n"
        "`/config` – sᴇᴛ ᴡᴀʀɴ-ʟɪᴍɪᴛ & ᴘᴜɴɪsʜᴍᴇɴᴛ ᴍᴏᴅᴇ\n"
        "`/config set <mode|limit|penalty> <value>` – e.g. `/config set limit 3`\n"
        "`/free` – ᴡʜɪᴛᴇʟɪsᴛ ᴀ ᴜsᴇʀ (ʀᴇᴘʟʏ ᴏʀ ᴜsᴇʀ/ɪᴅ)\n"
        "`/unfree` – ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ᴡʜɪᴛᴇʟɪsᴛ\n"
        "`/freelist` – ʟɪsᴛ ᴀʟʟ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs\n\n"
        "<b>ᴡʜᴇɴ sᴏᴍᴇᴏɴᴇ ʜᴀs ᴀ ᴜʀʟ ɪɴ ᴛʜᴇɪʀ ʙɪᴏ ᴏɴ ᴀɴᴅ ʙɪᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ɪs ᴏɴ, ɪ'ʟʟ</b>\n"
        " 1. ⚠️ ᴡᴀʀɴ ᴛʜᴇᴍ\n"
        " 2. 🔇 ᴍᴜᴛᴇ ɪғ ᴛʜᴇʏ ᴇxᴄᴇᴇᴅ ʟɪᴍɪᴛ\n"
        " 3. 🔨 ʙᴀɴ ɪғ sᴇᴛ ᴛᴏ ʙᴀɴ\n\n"
        "<b>ᴜsᴇ /bio &lt;on|off|status&gt; ᴛᴏ ᴛᴏɢɢʟᴇ ᴛʜᴇ ғᴇᴀᴛᴜʀᴇ (ᴀᴅᴍɪɴs ᴏɴʟʏ).</b>"
    )
    try:
        await client.send_photo(chat_id=chat_id, photo=HELP_IMG_URL, caption=help_text)
    except Exception as e:
        print(f"Error sending help image: {e}")
        await client.send_message(chat_id, help_text)

# ---------------------------
# Config commands (command-based, admin only)
# Usage:
#   /config                 -> show current settings
#   /config set <option> <value>
# options: mode (warn|mute|ban), limit (int), penalty (mute|ban)
# ---------------------------
@app.on_message(filters.group & filters.command("config"))
async def configure_cmd(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("❌ Only admins may view or change configuration.")

    cmd = message.command
    mode, limit, penalty = await get_config(chat_id)

    if len(cmd) == 1:
        # show current config
        text = (
            f"<b>⚙️ Current Bio Protector Configuration</b>\n\n"
            f"<b>Mode:</b> {mode}\n"
            f"<b>Warn limit:</b> {limit}\n"
            f"<b>Penalty when limit reached:</b> {penalty}\n\n"
            "Usage:\n"
            "  /config set mode <warn|mute|ban>\n"
            "  /config set limit <3|4|5>\n"
            "  /config set penalty <mute|ban>\n"
        )
        return await message.reply_text(text)

    # set subcommand
    if len(cmd) >= 4 and cmd[1].lower() == "set":
        opt = cmd[2].lower()
        val = cmd[3].lower()

        if opt == "mode":
            if val not in ("warn", "mute", "ban"):
                return await message.reply_text("❌ Invalid mode. Choose: warn, mute, ban.")
            await update_config(chat_id, mode=val)
            return await message.reply_text(f"✅ Mode set to <b>{val}</b>")

        if opt == "limit":
            try:
                n = int(val)
                if n < 1 or n > 20:
                    return await message.reply_text("❌ Limit must be between 1 and 20.")
            except ValueError:
                return await message.reply_text("❌ Limit must be a number.")
            await update_config(chat_id, limit=n)
            return await message.reply_text(f"✅ Warn limit set to <b>{n}</b>")

        if opt == "penalty":
            if val not in ("mute", "ban"):
                return await message.reply_text("❌ Penalty must be either 'mute' or 'ban'.")
            await update_config(chat_id, penalty=val)
            return await message.reply_text(f"✅ Penalty set to <b>{val}</b>")

        return await message.reply_text("❌ Unknown option. Use /config to see usage.")

    # fallback
    return await message.reply_text("❌ Invalid usage. Use /config to see usage.")

# ---------------------------
# Whitelist / free / unfree / freelist (kept callback-enabled responses)
# ---------------------------
@app.on_message(filters.group & filters.command("free"))
async def command_free(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await client.send_message(chat_id, "<b>ʀᴇᴘʟʏ ᴏʀ ᴜsᴇ /free ᴜsᴇʀ ᴏʀ ɪᴅ ᴛᴏ ᴡʜɪᴛᴇʟɪsᴛ sᴏᴍᴇᴏɴᴇ.</b>")

    await add_whitelist(chat_id, target.id)
    await reset_warnings(chat_id, target.id)

    text = f"<b>✅ {target.mention} ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴡʜɪᴛᴇʟɪsᴛ</b>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 ᴜɴᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"unwhitelist_{target.id}"), InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]
    ])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(filters.group & filters.command("unfree"))
async def command_unfree(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await client.send_message(chat_id, "<b>ʀᴇᴘʟʏ ᴏʀ ᴜsᴇ /unfree ᴜsᴇʀ ᴏʀ ɪᴅ ᴛᴏ ᴜɴᴡʜɪᴛᴇʟɪsᴛ sᴏᴍᴇᴏɴᴇ.</b>")

    if await is_whitelisted(chat_id, target.id):
        await remove_whitelist(chat_id, target.id)
        text = f"<b>🚫 {target.mention} ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴡʜɪᴛᴇʟɪsᴛ</b>"
    else:
        text = f"<b>ℹ️ {target.mention} ɪs ɴᴏᴛ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ.</b>"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ ᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"whitelist_{target.id}"), InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(filters.group & filters.command("freelist"))
async def command_freelist(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    ids = await get_whitelist(chat_id)
    if not ids:
        await client.send_message(chat_id, "<b>⚠️ ɴᴏ ᴜsᴇʀs ᴀʀᴇ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>")
        return

    text = "<b>📋 ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs:</b>\n\n"
    for i, uid in enumerate(ids, start=1):
        try:
            user = await client.get_users(uid)
            name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
            text += f"{i}: {name} [`{uid}`]\n"
        except:
            text += f"{i}: [ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ] [`{uid}`]\n"

    await client.send_message(chat_id, text)

# ---------------------------
# /bio command (command-based) - admin only
# Usage: /bio on | /bio off | /bio status
# ---------------------------
@app.on_message(filters.group & filters.command("bio"))
async def toggle_bio_protection_cmd(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("❌ Only admins can toggle bio protection.")

    cmd = message.command
    if len(cmd) == 1:
        status = get_bio_state(chat_id)
        return await message.reply_text(f"🧬 Bio protection is currently: {'🟢 ON' if status else '🔴 OFF'}")

    action = cmd[1].lower()
    if action in ("on", "enable", "1"):
        set_bio_state(chat_id, True)
        return await message.reply_text("✅ Bio protection has been turned ON.")
    if action in ("off", "disable", "0"):
        set_bio_state(chat_id, False)
        return await message.reply_text("✅ Bio protection has been turned OFF.")

    return await message.reply_text("❌ Invalid argument. Use: /bio on | /bio off | /bio status")

# ---------------------------
# Command-based replacements for a few actions previously exposed via callbacks
# (we KEEP callback handling for whitelist/unwhitelist/unmute/unban/cancel_warn etc.)
# ---------------------------
@app.on_message(filters.group & filters.command("cancel_warn"))
async def cmd_cancel_warn(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return
    if len(message.command) < 2:
        return await message.reply_text("Usage: /cancel_warn <user_id>")
    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid user id.")

    await reset_warnings(chat_id, target_id)
    await message.reply_text(f"✅ Warnings for <code>{target_id}</code> have been cleared.")

@app.on_message(filters.group & filters.command("unmute"))
async def cmd_unmute(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return
    if len(message.command) < 2:
        return await message.reply_text("Usage: /unmute <user_id>")
    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid user id.")

    try:
        await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=True))
        await reset_warnings(chat_id, target_id)
        await message.reply_text(f"✅ <code>{target_id}</code> has been unmuted.")
    except errors.ChatAdminRequired:
        await message.reply_text("I don't have permission to unmute users.")

@app.on_message(filters.group & filters.command("unban"))
async def cmd_unban(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return
    if len(message.command) < 2:
        return await message.reply_text("Usage: /unban <user_id>")
    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid user id.")

    try:
        await client.unban_chat_member(chat_id, target_id)
        await reset_warnings(chat_id, target_id)
        await message.reply_text(f"✅ <code>{target_id}</code> has been unbanned.")
    except errors.ChatAdminRequired:
        await message.reply_text("I don't have permission to unban users.")

@app.on_message(filters.group & filters.command("whitelist"))
async def cmd_whitelist(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await message.reply_text("Usage: /whitelist <reply|user_id|username>")

    await add_whitelist(chat_id, target.id)
    await reset_warnings(chat_id, target.id)
    await message.reply_text(f"✅ {target.mention} has been whitelisted.")

@app.on_message(filters.group & filters.command("unwhitelist"))
async def cmd_unwhitelist(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await message.reply_text("Usage: /unwhitelist <reply|user_id|username>")

    await remove_whitelist(chat_id, target.id)
    await message.reply_text(f"✅ {target.mention} has been removed from whitelist.")

# ---------------------------
# Callback handler (keeps callbacks for most moderation actions EXCEPT config/warn toggles)
# - still handles: close, unwhitelist_, whitelist_, unmute_, unban_, cancel_warn_
# ---------------------------
@app.on_callback_query()
async def callback_handler(client: Client, callback_query):
    data = callback_query.data or ""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    async def admin_check():
        if not await is_admin(client, chat_id, user_id):
            await callback_query.answer("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ", show_alert=True)
            return False
        return True

    # CLOSE
    if data == "close":
        try:
            await callback_query.message.delete()
        except:
            pass
        return await callback_query.answer()

    # callbacks that we KEEP
    if data.startswith("unwhitelist_"):
        if not await admin_check():
            return
        target_id = int(data.split("_")[1])
        try:
            await remove_whitelist(chat_id, target_id)
            user = await client.get_chat(target_id)
            mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("ᴡʜɪᴛᴇʟɪsᴛ✅", callback_data=f"whitelist_{target.id}"), InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]])
            await callback_query.message.edit_text(f"<b>❌ {mention} [<code>{target_id}</code>] ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴡʜɪᴛᴇʟɪsᴛ.</b>", reply_markup=kb)
        except Exception:
            await callback_query.message.edit_text("Error removing whitelist.")
        return await callback_query.answer()

    if data.startswith("whitelist_"):
        if not await admin_check():
            return
        target_id = int(data.split("_")[1])
        try:
            await add_whitelist(chat_id, target_id)
            await reset_warnings(chat_id, target_id)
            user = await client.get_chat(target_id)
            mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚫 ᴜɴᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"unwhitelist_{target_id}"), InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]])
            await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] ʜᴀs ʙᴇᴇɴ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ!**", reply_markup=kb)
        except Exception:
            await callback_query.message.edit_text("Error whitelisting user.")
        return await callback_query.answer()

    if data.startswith(("unmute_", "unban_")):
        if not await admin_check():
            return
        action, uid = data.split("_")
        target_id = int(uid)
        try:
            if action == "unmute":
                await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=True))
            else:
                await client.unban_chat_member(chat_id, target_id)
            await reset_warnings(chat_id, target_id)
            msg = f"<b> {target_id} ʜᴀs ʙᴇᴇɴ {'ᴜɴᴍᴜᴛᴇᴅ' if action=='unmute' else 'ᴜɴʙᴀɴɴᴇᴅ'} </b>."
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("ᴡʜɪᴛᴇʟɪsᴛ ✅", callback_data=f"whitelist_{target_id}"), InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]])
            await callback_query.message.edit_text(msg, reply_markup=kb)
        except errors.ChatAdminRequired:
            await callback_query.message.edit_text(f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {action} ᴜsᴇʀs.")
        return await callback_query.answer()

    if data.startswith("cancel_warn_"):
        if not await admin_check():
            return
        target_id = int(data.split("_")[-1])
        await reset_warnings(chat_id, target_id)
        user = await client.get_chat(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("ᴡʜɪᴛᴇʟɪsᴛ✅", callback_data=f"whitelist_{target_id}"), InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]])
        await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] ʜᴀs ɴᴏ ᴍᴏʀᴇ ᴡᴀʀɴɪɴɢs!**", reply_markup=kb)
        return await callback_query.answer()

    # fallback
    await callback_query.answer()

# ---------------------------
# Message handler that enforces bio policy (only if enabled)
# ---------------------------
@app.on_message(filters.group)
async def check_bio(client: Client, message):
    # ignore commands
    if message.text and message.text.startswith("/"):
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # If bio protection is OFF for this chat -> do nothing
    if not get_bio_state(chat_id):
        # still reset warnings for users who don't have URL in bio (original behavior)
        try:
            await reset_warnings(chat_id, user_id)
        except Exception:
            pass
        return

    # skip admins & whitelisted users
    if await is_admin(client, chat_id, user_id) or await is_whitelisted(chat_id, user_id):
        return

    # get user's bio
    try:
        user = await client.get_chat(user_id)
    except Exception:
        return

    bio = user.bio or ""
    full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
    mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    if URL_PATTERN.search(bio):
        # delete the triggering message (if possible)
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return await message.reply_text("ᴘʟᴇᴀsᴇ ɢʀᴀɴᴛ ᴍᴇ ᴅᴇʟᴇᴛᴇ ᴘᴇʀᴍɪssɪᴏɴ.")

        mode, limit, penalty = await get_config(chat_id)
        if mode == "warn":
            count = await increment_warning(chat_id, user_id)
            warning_text = (
                "<b>🚨 ᴡᴀʀɴɪɴɢ ɪssᴜᴇᴅ</b> 🚨\n\n"
                f"👤 <b>ᴜsᴇʀ:</b> {mention} `[{user_id}]`\n"
                "❌ <b>ʀᴇᴀsᴏɴ:</b> ᴜʀʟ ғᴏᴜɴᴅ ɪɴ ʙɪᴏ\n"
                f"⚠️ <b>ᴡᴀʀɴɪɴɢ:</b> {count}/{limit}\n\n"
                "<b>ɴᴏᴛɪᴄᴇ: ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ᴀɴʏ ʟɪɴᴋs ғʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ.</b>\n\n"
                "If you want to clear warning or whitelist the user, admins can use the inline buttons provided or these commands:\n"
                "/cancel_warn <user_id>  or  /whitelist <reply|user_id>"
            )
            # keep inline buttons for quick actions (whitelist/unwhitelist/unmute/unban)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ ", callback_data=f"cancel_warn_{user_id}"), InlineKeyboardButton("✅ ᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"whitelist_{user_id}")],
                [InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]
            ])
            sent = await message.reply_text(warning_text, reply_markup=keyboard)
            if count >= limit:
                try:
                    if penalty == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton("ᴜɴᴍᴜᴛᴇ ✅", callback_data=f"unmute_{user_id}")]])
                        await sent.edit_text(f"<b>{mention} ʜᴀs ʙᴇᴇɴ 🔇 ᴍᴜᴛᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].</b>", reply_markup=kb)
                    else:
                        await client.ban_chat_member(chat_id, user_id)
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton("ᴜɴʙᴀɴ ✅", callback_data=f"unban_{user_id}")]])
                        await sent.edit_text(f"<b>{mention} ʜᴀs ʙᴇᴇɴ 🔨 ʙᴀɴɴᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].</b>", reply_markup=kb)
                except errors.ChatAdminRequired:
                    await sent.edit_text(f"<b>ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {penalty} ᴜsᴇʀs.</b>")
        else:
            try:
                if mode == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                    await message.reply_text(f"{mention} ʜᴀs ʙᴇᴇɴ 🔇 ᴍᴜᴛᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].\nUse inline buttons or /unmute <user_id> to unmute.")
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    await message.reply_text(f"{mention} ʜᴀs ʙᴇᴇɴ 🔨 ʙᴀɴɴᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].\nUse inline buttons or /unban <user_id> to unban.")
            except errors.ChatAdminRequired:
                return await message.reply_text(f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {mode} ᴜsᴇʀs.")
    else:
        # If no url in bio -> reset warnings
        await reset_warnings(chat_id, user_id)