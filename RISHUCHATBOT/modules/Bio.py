
import json
import os
import re
from typing import Tuple

from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from RISHUCHATBOT import RISHUCHATBOT as app

from RISHUCHATBOT.modules.babu import (
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
# Start / Help / Config commands
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
                "   • ᴀᴜᴛᴏ-ᴍᴜᴛᴇ ᴏʀ ʙᴀɴ ᴡʜᴇɴ ʟɪᴍɪᴛ ɪs ʀᴇᴀᴄʜᴇᴅ\n"
                "   • ᴡʜɪᴛᴇʟɪsᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ғᴏʀ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs\n\n"
                "<b>ᴜsᴇ /bio ᴛᴏ ᴛᴏɢɢʟᴇ ʙɪᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ (ᴅᴇꜰᴀᴜʟᴛ: OFF)</b>"
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
        await client.send_message(chat_id, "Welcome to Bio Protector Bot! Use /bio to manage protection.")

@app.on_message(filters.command("bhelp"))
async def help_handler(client: Client, message):
    chat_id = message.chat.id
    help_text = (
        "<b>🛠️ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs & ᴜsᴀɢᴇ</b>\n\n"
        "`/config` – sᴇᴛ ᴡᴀʀɴ-ʟɪᴍɪᴛ & ᴘᴜɴɪsʜᴍᴇɴᴛ ᴍᴏᴅᴇ\n"
        "`/free` – ᴡʜɪᴛᴇʟɪsᴛ ᴀ ᴜsᴇʀ (ʀᴇᴘʟʏ ᴏʀ ᴜsᴇʀ/ɪᴅ)\n"
        "`/unfree` – ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ᴡʜɪᴛᴇʟɪsᴛ\n"
        "`/freelist` – ʟɪsᴛ ᴀʟʟ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs\n\n"
        "<b>ᴡʜᴇɴ sᴏᴍᴇᴏɴᴇ ʜᴀs ᴀ ᴜʀʟ ɪɴ ᴛʜᴇɪʀ ʙɪᴏ ᴏɴ ᴀɴᴅ ʙɪᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ɪs ᴏɴ, ɪ'ʟʟ</b>\n"
        " 1. ⚠️ ᴡᴀʀɴ ᴛʜᴇᴍ\n"
        " 2. 🔇 ᴍᴜᴛᴇ ɪғ ᴛʜᴇʏ ᴇxᴄᴇᴇᴅ ʟɪᴍɪᴛ\n"
        " 3. 🔨 ʙᴀɴ ɪғ sᴇᴛ ᴛᴏ ʙᴀɴ\n\n"
        "<b>ᴜsᴇ /bio ᴛᴏ ᴛᴏɢɢʟᴇ ᴛʜᴇ ғᴇᴀᴛᴜʀᴇ (ᴀᴅᴍɪɴs ᴏɴʟʏ).</b>"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]])
    try:
        await client.send_photo(chat_id=chat_id, photo=HELP_IMG_URL, caption=help_text, reply_markup=kb)
    except Exception as e:
        print(f"Error sending help image: {e}")
        await client.send_message(chat_id, help_text, reply_markup=kb)

# ---------------------------
# Config command (existing)
# ---------------------------
@app.on_message(filters.group & filters.command("config"))
async def configure(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    mode, limit, penalty = await get_config(chat_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴡᴀʀɴ", callback_data="warn")],
        [
            InlineKeyboardButton("ᴍᴜᴛᴇ ✅" if penalty == "mute" else "ᴍᴜᴛᴇ", callback_data="mute"),
            InlineKeyboardButton("ʙᴀɴ ✅" if penalty == "ban" else "ʙᴀɴ", callback_data="ban")
        ],
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
    ])
    try:
        await client.send_photo(
            chat_id=chat_id,
            photo=CONFIG_IMG_URL,
            caption="<b>ᴄʜᴏᴏsᴇ ᴘᴇɴᴀʟᴛʏ ғᴏʀ ᴜsᴇʀs ᴡɪᴛʜ ʟɪɴᴋs ɪɴ ʙɪᴏ:</b>",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error sending config image: {e}")
        await client.send_message(chat_id, "<b>ᴄʜᴏᴏsᴇ ᴘᴇɴᴀʟᴛʏ ғᴏʀ ᴜsᴇʀs ᴡɪᴛʜ ʟɪɴᴋs ɪɴ ʙɪᴏ:</b>", reply_markup=keyboard)
    await message.delete()

# ---------------------------
# Whitelist / free / unfree / freelist
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
        [
            InlineKeyboardButton("🚫 ᴜɴᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"unwhitelist_{target.id}"),
            InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")
        ]
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

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"whitelist_{target.id}"),
            InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")
        ]
    ])
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

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]])
    await client.send_message(chat_id, text, reply_markup=keyboard)

# ---------------------------
# /bio command (toggle) - admin only
# ---------------------------
@app.on_message(filters.group & filters.command("bio"))
async def toggle_bio_protection(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("❌ Only admins can toggle bio protection.")

    current = get_bio_state(chat_id)  # default False
    text = f"<b>🧬 ʙɪᴏ ʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ:</b> {'🟢 ON' if current else '🔴 OFF'}"
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Turn ON" if not current else "🔴 Turn OFF", callback_data=f"togglebio_{'on' if not current else 'off'}"),
        ],
        [InlineKeyboardButton("🗑️ Close", callback_data="close")]
    ])
    await message.reply_text(text, reply_markup=kb)

# ---------------------------
# Unified callback handler (handles existing callbacks + bio toggle)
# ---------------------------
@app.on_callback_query()
async def callback_handler(client: Client, callback_query):
    data = callback_query.data or ""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    # admin check for administrative actions
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

    # ----------------- bio toggle (new) -----------------
    if data.startswith("togglebio_"):
        if not await admin_check():
            return
        action = data.split("_", 1)[1]
        if action == "on":
            set_bio_state(chat_id, True)
        else:
            set_bio_state(chat_id, False)
        status = get_bio_state(chat_id)
        new_text = f"<b>🧬 ʙɪᴏ ʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ɪs ɴᴏᴡ:</b> {'🟢 ON' if status else '🔴 OFF'}"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 Turn ON" if not status else "🔴 Turn OFF", callback_data=f"togglebio_{'on' if not status else 'off'}")],
            [InlineKeyboardButton("🗑️ Close", callback_data="close")]
        ])
        try:
            await callback_query.message.edit_text(new_text, reply_markup=kb)
        except:
            try:
                await callback_query.message.edit_caption(new_text, reply_markup=kb)
            except:
                pass
        return await callback_query.answer("Toggled successfully ✅")

    # ----------------- existing callback handling from original code -----------------
    if not await admin_check():
        return

    # Back to config menu
    if data == "back":
        mode, limit, penalty = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴡᴀʀɴ", callback_data="warn")],
            [
                InlineKeyboardButton("ᴍᴜᴛᴇ ✅" if penalty=="mute" else "ᴍᴜᴛᴇ", callback_data="mute"),
                InlineKeyboardButton("ʙᴀɴ ✅" if penalty=="ban" else "ʙᴀɴ", callback_data="ban")
            ],
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ])
        try:
            if callback_query.message.photo:
                await callback_query.message.edit_caption(caption="<b>ᴄʜᴏᴏsᴇ ᴘᴇɴᴀʟᴛʏ ғᴏʀ ᴜsᴇʀs ᴡɪᴛʜ ʟɪɴᴋs ɪɴ ʙɪᴏ:</b>", reply_markup=kb)
            else:
                await callback_query.message.edit_text("<b>ᴄʜᴏᴏsᴇ ᴘᴇɴᴀʟᴛʏ ғᴏʀ ᴜsᴇʀs ᴡɪᴛʜ ʟɪɴᴋs ɪɴ ʙɪᴏ:</b>", reply_markup=kb)
        except Exception as e:
            print(f"Error updating callback message: {e}")
            await callback_query.message.edit_text("<b>ᴄʜᴏᴏsᴇ ᴘᴇɴᴀʟᴛʏ ғᴏʀ ᴜsᴇʀs ᴡɪᴛʜ ʟɪɴᴋs ɪɴ ʙɪᴏ:</b>", reply_markup=kb)
        return await callback_query.answer()

    # Warn selection submenu
    if data == "warn":
        _, selected_limit, _ = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"3 ✅" if selected_limit==3 else "3", callback_data="warn_3"),
             InlineKeyboardButton(f"4 ✅" if selected_limit==4 else "4", callback_data="warn_4"),
             InlineKeyboardButton(f"5 ✅" if selected_limit==5 else "5", callback_data="warn_5")],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back"), InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ])
        try:
            if callback_query.message.photo:
                await callback_query.message.edit_caption(caption="<b>sᴇʟᴇᴄᴛ ɴᴜᴍʙᴇʀ ᴏғ ᴡᴀʀɴs ʙᴇғᴏʀᴇ ᴘᴇɴᴀʟᴛʏ:</b>", reply_markup=kb)
            else:
                await callback_query.message.edit_text("<b>sᴇʟᴇᴄᴛ ɴᴜᴍʙᴇʀ ᴏғ ᴡᴀʀɴs ʙᴇғᴏʀᴇ ᴘᴇɴᴀʟᴛʏ:</b>", reply_markup=kb)
        except Exception:
            await callback_query.message.edit_text("<b>sᴇʟᴇᴄᴛ ɴᴜᴍʙᴇʀ ᴏғ ᴡᴀʀɴs ʙᴇғᴏʀᴇ ᴘᴇɴᴀʟᴛʏ:</b>", reply_markup=kb)
        return await callback_query.answer()

    # Mute / Ban selection
    if data in ["mute", "ban"]:
        await update_config(chat_id, penalty=data)
        mode, limit, penalty = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴡᴀʀɴ", callback_data="warn")],
            [
                InlineKeyboardButton("ᴍᴜᴛᴇ ✅" if penalty=="mute" else "ᴍᴜᴛᴇ", callback_data="mute"),
                InlineKeyboardButton("ʙᴀɴ ✅" if penalty=="ban" else "ʙᴀɴ", callback_data="ban")
            ],
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ])
        try:
            if callback_query.message.photo:
                await callback_query.message.edit_caption(caption="<b>ᴘᴜɴɪsʜᴍᴇɴᴛ sᴇʟᴇᴄᴛᴇᴅ:</b>", reply_markup=kb)
            else:
                await callback_query.message.edit_text("<b>ᴘᴜɴɪsʜᴍᴇɴᴛ sᴇʟᴇᴄᴛᴇᴅ:</b>", reply_markup=kb)
        except:
            await callback_query.message.edit_text("<b>ᴘᴜɴɪsʜᴍᴇɴᴛ sᴇʟᴇᴄᴛᴇᴅ:</b>", reply_markup=kb)
        return await callback_query.answer()

    # Warn count selection
    if data.startswith("warn_"):
        count = int(data.split("_")[1])
        await update_config(chat_id, limit=count)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"3 ✅" if count==3 else "3", callback_data="warn_3"),
             InlineKeyboardButton(f"4 ✅" if count==4 else "4", callback_data="warn_4"),
             InlineKeyboardButton(f"5 ✅" if count==5 else "5", callback_data="warn_5")],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back"), InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ])
        try:
            if callback_query.message.photo:
                await callback_query.message.edit_caption(caption=f"<b>ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ {count} </b>", reply_markup=kb)
            else:
                await callback_query.message.edit_text(f"<b>ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ {count} </b>", reply_markup=kb)
        except:
            await callback_query.message.edit_text(f"<b>ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ {count} </b>", reply_markup=kb)
        return await callback_query.answer()

    # unmute_ / unban_
    if data.startswith(("unmute_", "unban_")):
        action, uid = data.split("_")
        target_id = int(uid)
        user = await client.get_chat(target_id)
        name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        try:
            if action == "unmute":
                await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=True))
            else:
                await client.unban_chat_member(chat_id, target_id)
            await reset_warnings(chat_id, target_id)
            msg = f"<b> {name} (`{target_id}`) ʜᴀs ʙᴇᴇɴ {'ᴜɴᴍᴜᴛᴇᴅ' if action=='unmute' else 'ᴜɴʙᴀɴɴᴇᴅ'} </b>."
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ᴡʜɪᴛᴇʟɪsᴛ ✅", callback_data=f"whitelist_{target_id}"),
                    InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")
                ]
            ])
            await callback_query.message.edit_text(msg, reply_markup=kb)
        except errors.ChatAdminRequired:
            await callback_query.message.edit_text(f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {action} ᴜsᴇʀs.")
        return await callback_query.answer()

    # cancel_warn_
    if data.startswith("cancel_warn_"):
        target_id = int(data.split("_")[-1])
        await reset_warnings(chat_id, target_id)
        user = await client.get_chat(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴡʜɪᴛᴇʟɪsᴛ✅", callback_data=f"whitelist_{target_id}"),
             InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] ʜᴀs ɴᴏ ᴍᴏʀᴇ ᴡᴀʀɴɪɴɢs!**", reply_markup=kb)
        return await callback_query.answer()

    # whitelist_ / unwhitelist_
    if data.startswith("whitelist_"):
        target_id = int(data.split("_")[1])
        await add_whitelist(chat_id, target_id)
        await reset_warnings(chat_id, target_id)
        user = await client.get_chat(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 ᴜɴᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"unwhitelist_{target_id}"),
             InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] ʜᴀs ʙᴇᴇɴ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ!**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith("unwhitelist_"):
        target_id = int(data.split("_")[1])
        await remove_whitelist(chat_id, target_id)
        user = await client.get_chat(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴡʜɪᴛᴇʟɪsᴛ✅", callback_data=f"whitelist_{target_id}"),
             InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"<b>❌ {mention} [<code>{target_id}</code>] ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴡʜɪᴛᴇʟɪsᴛ.</b>", reply_markup=kb)
        return await callback_query.answer()

    # fallback
    await callback_query.answer()

# ---------------------------
# Message handler that enforces bio policy (only if enabled)
# ---------------------------
@app.on_message(filters.group)
async def check_bio(client: Client, message):
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
                "<b>ɴᴏᴛɪᴄᴇ: ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ᴀɴʏ ʟɪɴᴋs ғʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ.</b>"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ ", callback_data=f"cancel_warn_{user_id}"),
                 InlineKeyboardButton("✅ ᴡʜɪᴛᴇʟɪsᴛ", callback_data=f"whitelist_{user_id}")],
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
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton("ᴜɴᴍᴜᴛᴇ", callback_data=f"unmute_{user_id}")]])
                    await message.reply_text(f"{mention} ʜᴀs ʙᴇᴇɴ 🔇 ᴍᴜᴛᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].", reply_markup=kb)
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton("ᴜɴʙᴀɴ", callback_data=f"unban_{user_id}")]])
                    await message.reply_text(f"{mention} ʜᴀs ʙᴇᴇɴ 🔨 ʙᴀɴɴᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].", reply_markup=kb)
            except errors.ChatAdminRequired:
                return await message.reply_text(f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {mode} ᴜsᴇʀs.")
    else:
        # If no url in bio -> reset warnings
        await reset_warnings(chat_id, user_id)
