import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError
from RISHUCHATBOT import RISHUCHATBOT as app


# Stickers list (tumhare diye huye file_ids)
STICKERS = [
    "CAACAgUAAxkBAAENygdnrrSuukBGTLd_k2q-kPf80pPMqgAClw0AAmdr-Fcu4b8ZzcizqDYE",
    "CAACAgUAAxkBAAENygtnrrVXr5zEE-h_eiG8lRUkRkMwfwACExMAAjRk6VbUUzZjByHDfzYE",
    "CAACAgUAAxkBAAEN5DBnvSPr9qQMqsdEnDDRP-imKi5dQQACLhMAAuC0gFVXNUFTYLnPgzYE",
    "CAACAgUAAxkBAAEN5DFnvSPrXLlJIqpci9G9DLlYo-N9sQAC7xYAAmNogVVdydtoPbvZ3DYE",
    "CAACAgUAAxkBAAEN5DJnvSPrBKiEnBsXYV-cPA0NNFPWxAAC9xEAAleLgFUHZXfeMQ2XIjYE",
    "CAACAgUAAxkBAAEN5DtnvSjlPXpQ9p4e7NnjcQ8u9D02ZgACmxQAAq38gVVMR2r-x8yK7jYE",
    "CAACAgUAAxkBAAEN5D1nvSjrBVYlBio74f8n2CDj_I0sEwACixYAAotv6VVIuORutfwQczYE",
    "CAACAgUAAxkBAAEN5D9nvSjuUsbAf8LQ1KaU5PsfR3CJcwACmhEAAqFq6FUaXZOdkV85bDYE",
    "CAACAgUAAxkBAAEN5EFnvSj0My9zoTWkmtIiL8D6vOReAAO_EQACvC_pVfIqri8bdMRBNgQ",
    "CAACAgUAAxkBAAEN5ENnvSj6VnxialvLOmfRL7yZx-Q9HgACbhQAAhfA8FWBN9ZyZA5LuTYE",
    "CAACAgUAAxkBAAEN5EVnvSkQhPZHx-aPu_79kWLtFKCnYwACAREAArvxgVUYx9DFORkVmjYE",
    "CAACAgUAAxkBAAEN5EdnvSkak4zQxNnvMO76ZVlsXQhz7AACJhQAAoWcgVVYjdtsjmF0czYE",
    "CAACAgUAAxkBAAEBVQlomyMVxIgWqJlXt8A3qXM1A2F0SQAC8hcAApMo2FTM-votZN5grR4E",
    "CAACAgUAAxkBAAEBVQJomyLjzGn6HBR0qg00U_Z5KuFPhAACrRcAAiWZ2VQe8gd5Mo6vPR4E",
    "CAACAgUAAxkBAAEBVPpomyLIlh2RagaaYEF8gEis4Q17IwACgBYAApDK2VTv_3S15PHWIB4E",
    "CAACAgUAAxkBAAEBVQVomyLt6lUrfBqinZexWnz4HOl6QAAC_RcAAk2N2FQPqAvrBzmnFB4E",
    "CAACAgUAAxkBAAEBVP9omyLYpD3GXTxZ2K-rKFvYQHvDpAACsRcAAiLc4FQPSOGteFJaTR4E",
]


# Sticker handler
@app.on_message(filters.incoming & filters.sticker, group=1)
async def sticker_reply(client: Client, message: Message):
    try:
        random_sticker = random.choice(STICKERS)
        await message.reply_sticker(random_sticker)
    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError):
        return
    except Exception as e:
        print(f"Error in sticker_reply: {e}")
        return