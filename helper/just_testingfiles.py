# transfer_db.py
import os
import asyncio
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message
from database import MongoDB
from config import OWNER_ID

# ✅ PUT REAL URIS HERE (do NOT keep placeholders)
OLD_URI = "YOUR_OLD_MONGO_URI_HERE"
NEW_URI = "YOUR_NEW_MONGO_URI_HERE"

OLD_DB = "old_db"
NEW_DB = "new_db"

# ✅ Init both DBs
old_db = MongoDB(OLD_URI, OLD_DB)
new_db = MongoDB(NEW_URI, NEW_DB)

EDIT_EVERY = 50
SLEEP_BETWEEN = 0.03

@Client.on_message(filters.command("transfer") & filters.user(OWNER_ID))
async def transfer_handler(client: Client, message: Message):
    status = await message.reply("🔄 Preparing transfer...")

    # ✅ Ping DB
    try:
        await old_db.client.admin.command("ping")
        await new_db.client.admin.command("ping")
    except Exception:
        await status.edit("❌ DB connection failed\n" + traceback.format_exc(limit=1))
        return

    success = 0
    failed = 0
    skipped = 0

    try:
        users = await old_db.full_userbase()
        total = len(users)

        if total == 0:
            await status.edit("ℹ️ No users found in old DB.")
            return

        await status.edit(f"🔄 Starting transfer 0/{total}")

        for i, user_id in enumerate(users, start=1):
            try:
                if not isinstance(user_id, int):
                    skipped += 1

                elif not await new_db.present_user(user_id):
                    await new_db.add_user(user_id)
                    success += 1

                else:
                    skipped += 1

            except Exception as e:
                failed += 1
                await status.edit(
                    f"⚠️ Error on `{user_id}`\n"
                    f"{e}\n"
                    f"{i}/{total} | ✅{success} ❌{failed} ➖{skipped}"
                )

            if i % EDIT_EVERY == 0 or i == total:
                await status.edit(
                    f"🔄 Transferring...\n"
                    f"📦 {i}/{total}\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"➖ Skipped: {skipped}"
                )

            await asyncio.sleep(SLEEP_BETWEEN)

        await status.edit(
            f"✅ Transfer Complete!\n"
            f"📦 Total: {total}\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}\n"
            f"➖ Skipped: {skipped}"
        )

    except Exception:
        await status.edit(
            "❌ Fatal Error\n" + traceback.format_exc()
        )