import json import os import re from typing import Optional

from pyrogram import Client, filters, errors from pyrogram.types import ChatPermissions from SONALI import app

from SONALI.plugins.tools.Babu import ( is_admin, get_config, update_config, increment_warning, reset_warnings, is_whitelisted, add_whitelist, remove_whitelist, get_whitelist )

---------------------------

Configuration / constants

---------------------------

BIO_STATE_FILE = "bio_state.json"  # persistence file for bio ON/OFF per chat

URL_PATTERN = re.compile( r'(https?://|www.)[a-zA-Z0-9.-]+(.[a-zA-Z]{2,})+(/[a-zA-Z0-9._%+-])' )

START_IMG_URL = "https://graph.org/file/e9eed432610bc524cd1b1-b423df52eace6fae7c.jpg" HELP_IMG_URL = START_IMG_URL CONFIG_IMG_URL = START_IMG_URL

BOT_OWNER_USERNAME = "Rishu1286"

---------------------------

Persistence helpers

---------------------------

def _ensure_file(): if not os.path.exists(BIO_STATE_FILE): with open(BIO_STATE_FILE, "w", encoding="utf-8") as f: json.dump({}, f)

def load_bio_state() -> dict: _ensure_file() try: with open(BIO_STATE_FILE, "r", encoding="utf-8") as f: return json.load(f) except Exception: return {}

def save_bio_state(state: dict): with open(BIO_STATE_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=2)

def set_bio_state(chat_id: int, enabled: bool): state = load_bio_state() state[str(chat_id)] = bool(enabled) save_bio_state(state)

def get_bio_state(chat_id: int) -> bool: state = load_bio_state() return bool(state.get(str(chat_id), False))  # default OFF

---------------------------

Utility to resolve target user from reply or arg

---------------------------

async def _resolve_target(client: Client, message, arg_index: int = 1) -> Optional[int]: """Return user_id or None""" if message.reply_to_message: return message.reply_to_message.from_user.id parts = message.text.split() if len(parts) > arg_index: arg = parts[arg_index] try: if arg.isdigit(): return int(arg) else: user = await client.get_users(arg) return user.id except Exception: return None return None

---------------------------

Start / Help / Config commands

---------------------------

@app.on_message(filters.command("biostart")) async def start_handler(client: Client, message): chat_id = message.chat.id try: bot = await client.get_me() add_url = f"https://t.me/{bot.username}?startgroup=true" caption = ( "<b>✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ʙɪᴏʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʙᴏᴛ! ✨</b>\n\n" "🛡️ ɪ ʜᴇʟᴘ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘs ғʀᴏᴍ ᴜsᴇʀs ᴡɪᴛʜ ʟɪɴᴋs ɪɴ ᴛʜᴇɪʀ ʙɪᴏ.\n\n" "<b>🔹 ᴋᴇʏ ғᴇᴀᴛᴜʀᴇs:</n>\n" "   • ᴀᴜᴛᴏ ᴜʀʟ ᴅᴇᴛᴇᴄᴛɪᴏɴ ɪɴ ᴜsᴇʀ ʙɪᴏs\n" "   • ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ\n" "   • ᴀᴜᴛᴏ-ᴍᴜᴛᴇ ᴏʀ ʙᴀɴ ᴡʜᴇɴ ʟɪᴍɪᴛ ɪs ʀᴇᴀᴄʜᴇᴅ\n" "   • ᴡʜɪᴛᴇʟɪsᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ғᴏʀ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs\n\n" "<b>ᴜsᴇ /bioon ᴏʀ /biooff ᴛᴏ ᴛᴏɢɢʟᴇ ʙɪᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ (ᴀᴅᴍɪɴs ᴏɴʟʏ)</b>" ) await client.send_photo(chat_id=chat_id, photo=START_IMG_URL, caption=caption) except Exception as e: print(f"Error sending image: {e}") await client.send_message(chat_id, "Welcome to Bio Protector Bot! Use /bioon or /biooff to manage protection.")

@app.on_message(filters.command("bhelp")) async def help_handler(client: Client, message): chat_id = message.chat.id help_text = ( "<b>🛠️ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs & ᴜsᴀɢᴇ</b>\n\n" "/config – sʜᴏᴡ current settings and how to change them\n" "/setlimit <3|4|5> – sᴇᴛ ᴡᴀʀɴ ʟɪᴍɪᴛ (admins only)\n" "/setpenalty <mute|ban|warn> – sᴇᴛ ᴘᴇɴᴀʟᴛʏ (admins only)\n" "/free – ᴡʜɪᴛᴇʟɪsᴛ ᴀ ᴜsᴇʀ (ʀᴇᴘʟʏ ᴏʀ ᴜsᴇʀ/ɪᴅ)\n" "/unfree – ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ᴡʜɪᴛᴇʟɪsᴛ\n" "/freelist – ʟɪsᴛ ᴀʟʟ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs\n" "/bioon – ᴛᴜʀɴ ʙɪᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ON (admins only)\n" "/biooff – ᴛᴜʀɴ ʙɪᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ OFF (admins only)\n" "/biostatus – sʜᴏᴡ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs\n" "/unmute – ᴜɴᴍᴜᴛᴇ ᴀ ᴜsᴇʀ (ʀᴇᴘʟʏ ᴏʀ ɪᴅ)\n" "/unban – ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ (ɪᴅ only)\n" "/cancelwarn – ʀᴇsᴇᴛ ᴡᴀʀɴɪɴɢs (ʀᴇᴘʟʏ ᴏʀ ɪᴅ)\n" ) try: await client.send_photo(chat_id=chat_id, photo=HELP_IMG_URL, caption=help_text) except Exception as e: print(f"Error sending help image: {e}") await client.send_message(chat_id, help_text)

---------------------------

Config commands (now command-based)

---------------------------

@app.on_message(filters.group & filters.command("config")) async def configure(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return

mode, limit, penalty = await get_config(chat_id)
text = (
    f"<b>Current Config:</b>\n"
    f"Mode: <b>{mode}</b>\n"
    f"Warn limit: <b>{limit}</b>\n"
    f"Penalty: <b>{penalty}</b>\n\n"
    "Use /setlimit <3|4|5> and /setpenalty <mute|ban|warn> to change settings."
)
await message.reply_text(text)

@app.on_message(filters.group & filters.command("setlimit")) async def set_limit_cmd(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return await message.reply_text("❌ Only admins can change settings.")

parts = message.text.split()
if len(parts) < 2 or not parts[1].isdigit():
    return await message.reply_text("Usage: /setlimit <3|4|5>")
count = int(parts[1])
if count not in (3, 4, 5):
    return await message.reply_text("Allowed values: 3, 4, 5")

await update_config(chat_id, limit=count)
await message.reply_text(f"✅ Warn limit set to {count}")

@app.on_message(filters.group & filters.command("setpenalty")) async def set_penalty_cmd(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return await message.reply_text("❌ Only admins can change settings.")

parts = message.text.split()
if len(parts) < 2:
    return await message.reply_text("Usage: /setpenalty <mute|ban|warn>")
val = parts[1].lower()
if val not in ("mute", "ban", "warn"):
    return await message.reply_text("Allowed values: mute, ban, warn")

await update_config(chat_id, penalty=val)
await message.reply_text(f"✅ Penalty set to {val}")

---------------------------

Whitelist / free / unfree / freelist (keep same commands but without callback buttons)

---------------------------

@app.on_message(filters.group & filters.command("free")) async def command_free(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return

target_id = await _resolve_target(client, message)
if not target_id:
    return await client.send_message(chat_id, "<b>ʀᴇᴘʟʏ ᴏʀ ᴜsᴇ /free ᴜsᴇʀ ᴏʀ ɪᴅ ᴛᴏ ᴡʜɪᴛᴇʟɪsᴛ sᴏᴍᴇᴏɴᴇ.</b>")

await add_whitelist(chat_id, target_id)
await reset_warnings(chat_id, target_id)

await client.send_message(chat_id, f"<b>✅ User [`{target_id}`] has been added to the whitelist.</b>")

@app.on_message(filters.group & filters.command("unfree")) async def command_unfree(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return

target_id = await _resolve_target(client, message)
if not target_id:
    return await client.send_message(chat_id, "<b>ʀᴇᴘʟʏ ᴏʀ ᴜsᴇ /unfree ᴜsᴇʀ ᴏʀ ɪᴅ ᴛᴏ ᴜɴᴡʜɪᴛᴇʟɪsᴛ sᴏᴍᴇᴏɴᴇ.</b>")

if await is_whitelisted(chat_id, target_id):
    await remove_whitelist(chat_id, target_id)
    await client.send_message(chat_id, f"<b>🚫 User [`{target_id}`] removed from whitelist.</b>")
else:
    await client.send_message(chat_id, f"<b>ℹ️ User [`{target_id}`] is not whitelisted.</b>")

@app.on_message(filters.group & filters.command("freelist")) async def command_freelist(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return

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
    except Exception:
        text += f"{i}: [ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ] [`{uid}`]\n"

await client.send_message(chat_id, text)

---------------------------

Commands replacing previous callback actions (unmute, unban, cancelwarn)

---------------------------

@app.on_message(filters.group & filters.command("unmute")) async def cmd_unmute(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return

target_id = await _resolve_target(client, message)
if not target_id:
    return await message.reply_text("Usage: reply to the user or /unmute <user_id or username>")

try:
    await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=True))
    await reset_warnings(chat_id, target_id)
    await message.reply_text(f"✅ Unmuted [`{target_id}`] and reset warnings.")
except errors.ChatAdminRequired:
    await message.reply_text("I don't have permission to unmute users.")
except Exception as e:
    await message.reply_text(f"Error: {e}")

@app.on_message(filters.group & filters.command("unban")) async def cmd_unban(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return

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

@app.on_message(filters.group & filters.command("cancelwarn")) async def cmd_cancelwarn(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return

target_id = await _resolve_target(client, message)
if not target_id:
    return await message.reply_text("Usage: reply to the user or /cancelwarn <user_id or username>")

await reset_warnings(chat_id, target_id)
await message.reply_text(f"✅ Reset warnings for [`{target_id}`].")

---------------------------

/bio command replacements: /bioon /biooff /biostatus

---------------------------

@app.on_message(filters.group & filters.command("bioon")) async def cmd_bioon(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return await message.reply_text("❌ Only admins can toggle bio protection.")

set_bio_state(chat_id, True)
await message.reply_text("🟢 Bio link protection is now ON.")

@app.on_message(filters.group & filters.command("biooff")) async def cmd_biooff(client: Client, message): chat_id = message.chat.id user_id = message.from_user.id if not await is_admin(client, chat_id, user_id): return await message.reply_text("❌ Only admins can toggle bio protection.")

set_bio_state(chat_id, False)
await message.reply_text("🔴 Bio link protection is now OFF.")

@app.on_message(filters.group & filters.command("biostatus")) async def cmd_biostatus(client: Client, message): chat_id = message.chat.id status = get_bio_state(chat_id) await message.reply_text(f"🧬 Bio link protection is: {'🟢 ON' if status else '🔴 OFF'}")

---------------------------

Message handler that enforces bio policy (only if enabled)

---------------------------

@app.on_message(filters.group) async def check_bio(client: Client, message): # ignore bot messages if message.from_user is None: return

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
            "Admins may use /free, /unfree, /unmute, /unban, or /cancelwarn as needed."
        )
        sent = await message.reply_text(warning_text)
        if count >= limit:
            try:
                if penalty == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                    await sent.edit_text(f"<b>{mention} ʜᴀs ʙᴇᴇɴ 🔇 ᴍᴜᴛᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].</b>\nAdmins: use /unmute <id> to unmute.")
                else:
                    await client.ban_chat_member(chat_id, user_id)
                    await sent.edit_text(f"<b>{mention} ʜᴀs ʙᴇᴇɴ 🔨 ʙᴀɴɴᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ].</b>\nAdmins: use /unban <id> to unban.")
            except errors.ChatAdminRequired:
                await sent.edit_text(f"<b>ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {penalty} ᴜsᴇʀs.</b>")
    else:
        try:
            if mode == "mute":
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await message.reply_text(f"{mention} ʜᴀs ʙᴇᴇɴ 🔇 ᴍᴜᴛᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ]. Admins: use /unmute <id> to unmute.")
            else:
                await client.ban_chat_member(chat_id, user_id)
                await message.reply_text(f"{mention} ʜᴀs ʙᴇᴇɴ 🔨 ʙᴀɴɴᴇᴅ ғᴏʀ [ʟɪɴᴋ ɪɴ ʙɪᴏ]. Admins: use /unban <id> to unban.")
        except errors.ChatAdminRequired:
            return await message.reply_text(f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {mode} ᴜsᴇʀs.")
else:
    # If no url in bio -> reset warnings
    await reset_warnings(chat_id, user_id)