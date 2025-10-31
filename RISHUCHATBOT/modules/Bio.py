# bio_protector.py
"""
Bio Link Protector (command-only version)
- No callback queries — all admin actions are via commands.
- Commands:
  /bioon, /biooff, /biostatus
  /config, /setlimit <3|4|5>, /setpenalty <mute|ban|warn>
  /free (reply or id/username), /unfree, /freelist
  /unmute (reply or id/username), /unban <id>
  /cancelwarn (reply or id/username)
"""
import json
import os
import re
from typing import Optional

from pyrogram import Client, filters, errors
from pyrogram.types import ChatPermissions
from SONALI import app

from SONALI.plugins.tools.babu import (
    is_admin,
    get_config, update_config,
    increment_warning, reset_warnings,
    is_whitelisted, add_whitelist, remove_whitelist, get_whitelist
)

# ---------- Config ----------
BIO_STATE_FILE = "bio_state.json"
START_IMG_URL = "https://graph.org/file/e9eed432610bc524cd1b1-b423df52eace6fae7c.jpg"
HELP_IMG_URL = START_IMG_URL
CONFIG_IMG_URL = START_IMG_URL

# robust URL pattern (covers typical links)
URL_PATTERN = re.compile(
    r"(https?://|www\.)[^\s'\"<>]+", re.IGNORECASE
)

# ---------- Persistence helpers ----------
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
    return bool(state.get(str(chat_id), False))

# ---------- Helpers ----------
async def _resolve_target_id(client: Client, message, arg_index: int = 1) -> Optional[int]:
    """
    Resolve a target user id from:
      - reply_to_message.from_user
      - /command <user_id_or_username>
    Returns None if not resolvable.
    """
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id

    parts = message.text.split()
    if len(parts) <= arg_index:
        return None

    arg = parts[arg_index].strip()
    if not arg:
        return None

    # if numeric id
    if arg.isdigit():
        return int(arg)

    # try username or mention
    try:
        user = await client.get_users(arg)
        return user.id
    except Exception:
        return None

def _format_mention(user):
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

# ---------- Start / Help ----------
@app.on_message(filters.command("biostart"))
async def start_handler(client: Client, message):
    chat_id = message.chat.id
    caption = (
        "<b>✨ Bio Link Protector ✨</b>\n\n"
        "Protects your group from users with links in their bios.\n"
        "Use /bioon or /biooff to toggle (admins only).\n"
        "Use /bhelp for commands."
    )
    try:
        await client.send_photo(chat_id=chat_id, photo=START_IMG_URL, caption=caption)
    except Exception:
        await client.send_message(chat_id, caption)

@app.on_message(filters.command("bhelp"))
async def help_handler(client: Client, message):
    chat_id = message.chat.id
    help_text = (
        "<b>Commands (admins only where noted)</b>\n\n"
        "/bioon - Turn bio protector ON (admins only)\n"
        "/biooff - Turn bio protector OFF (admins only)\n"
        "/biostatus - Show on/off status\n"
        "/config - Show current config\n"
        "/setlimit <3|4|5> - Set warn limit (admins only)\n"
        "/setpenalty <mute|ban|warn> - Set punishment mode (admins only)\n"
        "/free - Whitelist a user (reply or id/username) (admins only)\n"
        "/unfree - Remove from whitelist (admins only)\n"
        "/freelist - Show whitelisted users (admins only)\n"
        "/unmute - Unmute a user (reply or id/username) (admins only)\n"
        "/unban <user_id> - Unban by id (admins only)\n"
        "/cancelwarn - Reset warnings for a user (reply or id/username) (admins only)\n"
    )
    try:
        await client.send_photo(chat_id=chat_id, photo=HELP_IMG_URL, caption=help_text)
    except Exception:
        await client.send_message(chat_id, help_text)

# ---------- Config commands ----------
@app.on_message(filters.group & filters.command("config"))
async def configure(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    mode, limit, penalty = await get_config(chat_id)
    text = (
        f"<b>Current Config</b>\n"
        f"Mode: <b>{mode}</b>\n"
        f"Warn limit: <b>{limit}</b>\n"
        f"Penalty: <b>{penalty}</b>\n\n"
        "Use /setlimit and /setpenalty to change."
    )
    await message.reply_text(text)

@app.on_message(filters.group & filters.command("setlimit"))
async def set_limit_cmd(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("❌ Only admins can change settings.")

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply_text("Usage: /setlimit <3|4|5>")
    count = int(parts[1])
    if count not in (3, 4, 5):
        return await message.reply_text("Allowed values: 3, 4, 5")

    await update_config(chat_id, limit=count)
    await message.reply_text(f"✅ Warn limit set to {count}")

@app.on_message(filters.group & filters.command("setpenalty"))
async def set_penalty_cmd(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("❌ Only admins can change settings.")

    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply_text("Usage: /setpenalty <mute|ban|warn>")
    val = parts[1].lower()
    if val not in ("mute", "ban", "warn"):
        return await message.reply_text("Allowed values: mute, ban, warn")

    await update_config(chat_id, penalty=val)
    await message.reply_text(f"✅ Penalty set to {val}")

# ---------- Whitelist commands ----------
@app.on_message(filters.group & filters.command("free"))
async def command_free(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    target_id = await _resolve_target_id(client, message)
    if not target_id:
        return await client.send_message(chat_id, "<b>Reply or use /free <id|username></b>")

    await add_whitelist(chat_id, target_id)
    await reset_warnings(chat_id, target_id)
    await client.send_message(chat_id, f"<b>✅ User [`{target_id}`] added to whitelist.</b>")

@app.on_message(filters.group & filters.command("unfree"))
async def command_unfree(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    target_id = await _resolve_target_id(client, message)
    if not target_id:
        return await client.send_message(chat_id, "<b>Reply or use /unfree <id|username></b>")

    if await is_whitelisted(chat_id, target_id):
        await remove_whitelist(chat_id, target_id)
        await client.send_message(chat_id, f"<b>🚫 User [`{target_id}`] removed from whitelist.</b>")
    else:
        await client.send_message(chat_id, f"<b>ℹ️ User [`{target_id}`] is not whitelisted.</b>")

@app.on_message(filters.group & filters.command("freelist"))
async def command_freelist(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    ids = await get_whitelist(chat_id)
    if not ids:
        return await client.send_message(chat_id, "<b>⚠️ No whitelisted users.</b>")

    lines = []
    for i, uid in enumerate(ids, start=1):
        try:
            user = await client.get_users(uid)
            name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
            lines.append(f"{i}: {name} [`{uid}`]")
        except Exception:
            lines.append(f"{i}: [user not found] [`{uid}`]")

    await client.send_message(chat_id, "<b>📋 Whitelisted users:</b>\n\n" + "\n".join(lines))

# ---------- Admin actions (unmute/unban/cancelwarn) ----------
@app.on_message(filters.group & filters.command("unmute"))
async def cmd_unmute(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    target_id = await _resolve_target_id(client, message)
    if not target_id:
        return await message.reply_text("Usage: reply or /unmute <id|username>")

    try:
        await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=True))
        await reset_warnings(chat_id, target_id)
        await message.reply_text(f"✅ Unmuted [`{target_id}`] and reset warnings.")
    except errors.ChatAdminRequired:
        await message.reply_text("I don't have permission to unmute users.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.group & filters.command("unban"))
async def cmd_unban(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply_text("Usage: /unban <user_id>")
    target_id = int(parts[1])

    try:
        await client.unban_chat_member(chat_id, target_id)
        await reset_warnings(chat_id, target_id)
        await message.reply_text(f"✅ Unbanned [`{target_id}`] and reset warnings.")
    except errors.ChatAdminRequired:
        await message.reply_text("I don't have permission to unban users.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.group & filters.command("cancelwarn"))
async def cmd_cancelwarn(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    target_id = await _resolve_target_id(client, message)
    if not target_id:
        return await message.reply_text("Usage: reply or /cancelwarn <id|username>")

    await reset_warnings(chat_id, target_id)
    await message.reply_text(f"✅ Reset warnings for [`{target_id}`].")

# ---------- Bio toggle commands ----------
@app.on_message(filters.group & filters.command("bioon"))
async def cmd_bioon(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("❌ Only admins can toggle bio protection.")
    set_bio_state(chat_id, True)
    await message.reply_text("🟢 Bio link protection is now ON.")

@app.on_message(filters.group & filters.command("biooff"))
async def cmd_biooff(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("❌ Only admins can toggle bio protection.")
    set_bio_state(chat_id, False)
    await message.reply_text("🔴 Bio link protection is now OFF.")

@app.on_message(filters.group & filters.command("biostatus"))
async def cmd_biostatus(client: Client, message):
    chat_id = message.chat.id
    status = get_bio_state(chat_id)
    await message.reply_text(f"🧬 Bio link protection is: {'🟢 ON' if status else '🔴 OFF'}")

# ---------- Enforcement: runs on every group message ----------
@app.on_message(filters.group)
async def check_bio(client: Client, message):
    # ignore service/bot messages
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # If OFF -> reset warnings and return
    if not get_bio_state(chat_id):
        try:
            await reset_warnings(chat_id, user_id)
        except Exception:
            pass
        return

    # skip admins & whitelisted
    if await is_admin(client, chat_id, user_id) or await is_whitelisted(chat_id, user_id):
        return

    # fetch user's bio
    try:
        user = await client.get_chat(user_id)
    except Exception:
        return

    bio = (user.bio or "").strip()
    mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    if bio and URL_PATTERN.search(bio):
        # attempt to delete triggering message
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return await message.reply_text("Please grant me delete permission to remove messages from users with links in bio.")

        mode, limit, penalty = await get_config(chat_id)
        if mode == "warn":
            count = await increment_warning(chat_id, user_id)
            text = (
                "<b>🚨 Warning issued</b>\n\n"
                f"👤 <b>User:</b> {mention} `[{user_id}]`\n"
                "❌ <b>Reason:</b> URL found in bio\n"
                f"⚠️ <b>Warning:</b> {count}/{limit}\n\n"
                "<b>Notice:</b> Please remove links from your bio."
            )
            sent = await message.reply_text(text)
            if count >= limit:
                try:
                    if penalty == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                        await sent.edit_text(f"<b>{mention} has been muted for links in bio.</b>\n\nAdmins: use /unmute <id> to unmute.")
                    else:
                        await client.ban_chat_member(chat_id, user_id)
                        await sent.edit_text(f"<b>{mention} has been banned for links in bio.</b>\n\nAdmins: use /unban <id> to unban.")
                except errors.ChatAdminRequired:
                    await sent.edit_text(f"<b>I don't have permission to {penalty} users.</b>")
        else:
            # immediate action (mute/ban)
            try:
                if mode == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                    await message.reply_text(f"{mention} has been muted for links in bio. Admins: use /unmute <id> to unmute.")
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    await message.reply_text(f"{mention} has been banned for links in bio. Admins: use /unban <id> to unban.")
            except errors.ChatAdminRequired:
                await message.reply_text(f"I don't have permission to {mode} users.")
    else:
        # no url in bio -> reset warnings
        await reset_warnings(chat_id, user_id)