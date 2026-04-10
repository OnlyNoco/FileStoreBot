import math
import random
from datetime import datetime

from aiohttp import ClientSession, ClientTimeout
from pyrogram import Client, filters
from pyrogram.types import Message


def _normalize_bot_name(bot_name: str) -> str:
    return " ".join(bot_name.strip().lower().split())


def _parse_pipe_args(command_text: str) -> list[str]:
    payload = command_text.split(maxsplit=1)
    if len(payload) < 2:
        return []
    return [part.strip() for part in payload[1].split("|")]


def _format_remote_bot_list(remote_bots: dict) -> str:
    if not remote_bots:
        return "_No remote bots added yet._"

    lines = []
    for bot_key in sorted(remote_bots):
        bot_data = remote_bots[bot_key]
        status = "active" if bot_data.get("is_active", True) else "inactive"
        token_status = "yes" if bot_data.get("api_key") else "no"
        lines.append(
            f"• <b>{bot_data.get('name', bot_key)}</b>\n"
            f"URL: <code>{bot_data.get('url', '-')}</code>\n"
            f"Status: <code>{status}</code> | Token: <code>{token_status}</code>"
        )
    return "\n\n".join(lines)


def _select_remote_bots(target_spec: str, remote_bots: dict) -> tuple[list[dict], str | None]:
    bot_items = list(remote_bots.values())
    if not bot_items:
        return [], "No active remote bots are available."

    normalized_spec = target_spec.strip().lower()
    if normalized_spec in {"", "all"}:
        return bot_items, None

    if normalized_spec.endswith("%") and normalized_spec[:-1].isdigit():
        percent = int(normalized_spec[:-1])
        if percent <= 0 or percent > 100:
            return [], "Percentage must be between 1% and 100%."
        sample_size = max(1, math.ceil(len(bot_items) * (percent / 100)))
        return random.sample(bot_items, min(sample_size, len(bot_items))), None

    if normalized_spec.isdigit():
        requested_count = int(normalized_spec)
        if requested_count <= 0:
            return [], "Bot count must be greater than 0."
        return random.sample(bot_items, min(requested_count, len(bot_items))), None

    requested_names = {
        _normalize_bot_name(bot_name)
        for bot_name in target_spec.split(",")
        if bot_name.strip()
    }
    selected_bots = [
        bot_data
        for bot_data in bot_items
        if _normalize_bot_name(bot_data.get("name", "")) in requested_names
    ]
    if not selected_bots:
        return [], "No matching bot names were found."
    return selected_bots, None


async def _send_remote_broadcast(remote_bot: dict, payload: dict) -> tuple[bool, str]:
    endpoint = remote_bot["url"].rstrip("/") + "/broadcast"
    headers = {"Content-Type": "application/json"}
    if remote_bot.get("api_key"):
        headers["X-Broadcast-Key"] = remote_bot["api_key"]

    timeout = ClientTimeout(total=60)
    async with ClientSession(timeout=timeout) as session:
        try:
            async with session.post(endpoint, json=payload, headers=headers) as response:
                response_text = await response.text()
                if response.status >= 400:
                    return False, f"HTTP {response.status}: {response_text[:180]}"
                return True, response_text[:180]
        except Exception as exc:
            return False, str(exc)


@Client.on_message(filters.command("bots") & filters.private)
async def list_remote_bots(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    remote_bots = await client.mongodb.get_remote_bots()
    usage = (
        "<b>Remote Bot Manager</b>\n\n"
        f"{_format_remote_bot_list(remote_bots)}\n\n"
        "<b>Usage:</b>\n"
        "<code>/addbot name | https://your-bot-url | optional-token</code>\n"
        "<code>/editbot name | https://new-url | optional-token</code>\n"
        "<code>/delbot name</code>\n"
        "<code>/togglebot name</code>\n"
        "<code>/multibroadcast all</code>\n"
        "<code>/multibroadcast 50%</code>\n"
        "<code>/multibroadcast 3</code>\n"
        "<code>/multibroadcast bot one, bot two</code>\n\n"
        "Reply to a message that the receiver bots can copy."
    )
    await message.reply(usage, disable_web_page_preview=True)


@Client.on_message(filters.command("addbot") & filters.private)
async def add_remote_bot(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    parts = _parse_pipe_args(message.text)
    if len(parts) < 2:
        return await message.reply(
            "Use:\n<code>/addbot name | https://your-bot-url | optional-token</code>",
            disable_web_page_preview=True,
        )

    bot_name = parts[0]
    bot_url = parts[1].rstrip("/")
    api_key = parts[2] if len(parts) > 2 else ""

    if not bot_url.startswith(("http://", "https://")):
        return await message.reply("Bot URL must start with <code>http://</code> or <code>https://</code>.")

    await client.mongodb.upsert_remote_bot(
        bot_name,
        {
            "url": bot_url,
            "api_key": api_key,
            "is_active": True,
            "added_by": message.from_user.id,
            "updated_at": datetime.utcnow().isoformat(),
        },
    )
    await message.reply(
        f"Saved remote bot <b>{bot_name}</b>\nURL: <code>{bot_url}</code>",
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("editbot") & filters.private)
async def edit_remote_bot(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    parts = _parse_pipe_args(message.text)
    if len(parts) < 2:
        return await message.reply(
            "Use:\n<code>/editbot name | https://new-url | optional-token</code>",
            disable_web_page_preview=True,
        )

    bot_name = parts[0]
    existing_bot = await client.mongodb.get_remote_bot(bot_name)
    if not existing_bot:
        return await message.reply(f"No saved remote bot found for <code>{bot_name}</code>.")

    bot_url = parts[1].rstrip("/")
    if not bot_url.startswith(("http://", "https://")):
        return await message.reply("Bot URL must start with <code>http://</code> or <code>https://</code>.")

    updated_bot = dict(existing_bot)
    updated_bot["url"] = bot_url
    if len(parts) > 2:
        updated_bot["api_key"] = parts[2]
    updated_bot["updated_by"] = message.from_user.id
    updated_bot["updated_at"] = datetime.utcnow().isoformat()

    await client.mongodb.upsert_remote_bot(bot_name, updated_bot)
    await message.reply(
        f"Updated remote bot <b>{bot_name}</b>\nNew URL: <code>{bot_url}</code>",
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("delbot") & filters.private)
async def delete_remote_bot(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Use:\n<code>/delbot bot name</code>")

    bot_name = parts[1].strip()
    removed = await client.mongodb.remove_remote_bot(bot_name)
    if not removed:
        return await message.reply(f"No saved remote bot found for <code>{bot_name}</code>.")

    await message.reply(f"Removed remote bot <b>{bot_name}</b>.")


@Client.on_message(filters.command("togglebot") & filters.private)
async def toggle_remote_bot(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Use:\n<code>/togglebot bot name</code>")

    bot_name = parts[1].strip()
    new_status = await client.mongodb.toggle_remote_bot_status(bot_name)
    if new_status is None:
        return await message.reply(f"No saved remote bot found for <code>{bot_name}</code>.")

    status_text = "active" if new_status else "inactive"
    await message.reply(f"Remote bot <b>{bot_name}</b> is now <code>{status_text}</code>.")


@Client.on_message(filters.command("multibroadcast") & filters.private)
async def multi_bot_broadcast(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    if not message.reply_to_message:
        return await message.reply(
            "Reply to a message and use one of these:\n"
            "<code>/multibroadcast all</code>\n"
            "<code>/multibroadcast 50%</code>\n"
            "<code>/multibroadcast 3</code>\n"
            "<code>/multibroadcast bot one, bot two</code>"
        )

    remote_bots = await client.mongodb.get_active_remote_bots()
    parts = message.text.split(maxsplit=1)
    target_spec = parts[1] if len(parts) > 1 else "all"
    selected_bots, error_message = _select_remote_bots(target_spec, remote_bots)
    if error_message:
        return await message.reply(error_message)

    waiting_message = await message.reply(
        f"Sending broadcast job to <b>{len(selected_bots)}</b> remote bot(s)..."
    )
    payload = {
        "from_chat_id": message.reply_to_message.chat.id,
        "message_id": message.reply_to_message.id,
    }

    sent_count = 0
    failed_count = 0
    result_lines = []
    for remote_bot in selected_bots:
        ok, details = await _send_remote_broadcast(remote_bot, payload)
        if ok:
            sent_count += 1
            result_lines.append(f"• {remote_bot['name']}: sent")
        else:
            failed_count += 1
            result_lines.append(f"• {remote_bot['name']}: failed - <code>{details}</code>")

    summary = (
        "<b>Multi Bot Broadcast Finished</b>\n\n"
        f"Targeted bots: <code>{len(selected_bots)}</code>\n"
        f"Sent: <code>{sent_count}</code>\n"
        f"Failed: <code>{failed_count}</code>\n\n"
        + "\n".join(result_lines)
    )
    await waiting_message.edit(summary, disable_web_page_preview=True)
