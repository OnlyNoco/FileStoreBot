import asyncio
import math
import random

from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked


def build_broadcast_status(stats: dict, title: str = "Broadcast Completed") -> str:
    return f"""<blockquote><b><u>{title}</u></b></blockquote>
<blockquote expandable><b>Total Users :</b> <code>{stats["total"]}</code>
<b>Successful :</b> <code>{stats["successful"]}</code>
<b>Blocked Users :</b> <code>{stats["blocked"]}</code>
<b>Deleted Accounts :</b> <code>{stats["deleted"]}</code>
<b>Unsuccessful :</b> <code>{stats["unsuccessful"]}</code></blockquote>"""


def choose_subset(items: list, percentage: int | None = None, limit: int | None = None) -> list:
    selected_items = list(items)
    if not selected_items:
        return []

    if percentage is not None:
        percentage = max(1, min(100, int(percentage)))
        sample_size = max(1, math.ceil(len(selected_items) * (percentage / 100)))
        selected_items = random.sample(selected_items, min(sample_size, len(selected_items)))

    if limit is not None:
        limit = max(1, int(limit))
        if limit < len(selected_items):
            selected_items = random.sample(selected_items, limit)

    return selected_items


async def _run_broadcast(client, user_ids: list[int], sender) -> dict:
    stats = {
        "total": 0,
        "successful": 0,
        "blocked": 0,
        "deleted": 0,
        "unsuccessful": 0,
    }

    for chat_id in user_ids:
        try:
            await sender(chat_id)
            stats["successful"] += 1
        except FloodWait as flood_wait:
            wait_seconds = getattr(flood_wait, "value", getattr(flood_wait, "x", 1))
            await asyncio.sleep(wait_seconds)
            try:
                await sender(chat_id)
                stats["successful"] += 1
            except Exception:
                stats["unsuccessful"] += 1
        except UserIsBlocked:
            await client.mongodb.del_user(chat_id)
            stats["blocked"] += 1
        except InputUserDeactivated:
            await client.mongodb.del_user(chat_id)
            stats["deleted"] += 1
        except Exception:
            stats["unsuccessful"] += 1
        finally:
            stats["total"] += 1

    return stats


async def broadcast_reply_message(client, reply_message, user_ids: list[int]) -> dict:
    async def sender(chat_id: int):
        await reply_message.copy(chat_id)

    return await _run_broadcast(client, user_ids, sender)


async def broadcast_source_message(client, from_chat_id: int, message_id: int, user_ids: list[int]) -> dict:
    async def sender(chat_id: int):
        await client.copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
        )

    return await _run_broadcast(client, user_ids, sender)
