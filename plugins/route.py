import os

from aiohttp import web
import markdown

from helper.broadcasting import (
    broadcast_source_message,
    build_broadcast_status,
    choose_subset,
)


routes = web.RouteTableDef()


def _get_project_readme_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "README.md"))


def _get_broadcast_api_key() -> str:
    return os.getenv("BROADCAST_API_KEY", "").strip()


def _is_authorized(request: web.Request, payload: dict) -> bool:
    expected_key = _get_broadcast_api_key()
    if not expected_key:
        return True

    request_key = request.headers.get("X-Broadcast-Key", "").strip()
    if not request_key:
        request_key = str(payload.get("api_key", "")).strip()
    return request_key == expected_key


@routes.get("/", allow_head=True)
async def root_route_handler(request: web.Request):
    readme_path = _get_project_readme_path()
    if not os.path.exists(readme_path):
        return web.Response(text="README.md not found", status=404)

    with open(readme_path, "r", encoding="utf-8") as readme_file:
        md_text = readme_file.read()

    html = markdown.markdown(md_text, extensions=["fenced_code", "codehilite", "tables"])
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>FileStoreBot README</title>
        <style>
            body {{
                font-family: sans-serif;
                max-width: 900px;
                margin: auto;
                padding: 2rem;
                background: #f9f9f9;
                color: #333;
            }}
            pre {{
                background: #282c34;
                color: #f8f8f2;
                padding: 1em;
                overflow-x: auto;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.5;
                white-space: pre;
            }}
            code {{
                font-family: Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 0.5rem;
                text-align: left;
            }}
            h1, h2, h3 {{
                border-bottom: 1px solid #ddd;
                padding-bottom: 0.3em;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    return web.Response(text=html_page, content_type="text/html")


@routes.get("/health")
async def health_route_handler(request: web.Request):
    client = request.app.get("bot_client")
    if client is None or not getattr(client, "is_connected", False):
        return web.json_response({"ok": False, "status": "offline"}, status=503)

    return web.json_response(
        {
            "ok": True,
            "status": "online",
            "bot_username": getattr(client, "username", None),
            "bot_name": getattr(client, "name", None),
        }
    )


@routes.get("/bot-info")
async def bot_info_route_handler(request: web.Request):
    client = request.app.get("bot_client")
    if client is None:
        return web.json_response({"ok": False, "error": "Bot client is unavailable"}, status=503)

    total_users = await client.mongodb.full_userbase()
    return web.json_response(
        {
            "ok": True,
            "bot_username": getattr(client, "username", None),
            "bot_name": getattr(client, "name", None),
            "total_users": len(total_users),
        }
    )


@routes.post("/broadcast")
async def broadcast_route_handler(request: web.Request):
    client = request.app.get("bot_client")
    if client is None:
        return web.json_response({"ok": False, "error": "Bot client is unavailable"}, status=503)

    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "Invalid JSON payload"}, status=400)

    if not _is_authorized(request, payload):
        return web.json_response({"ok": False, "error": "Unauthorized request"}, status=401)

    try:
        source_chat_id = int(payload["from_chat_id"])
        source_message_id = int(payload["message_id"])
    except (KeyError, TypeError, ValueError):
        return web.json_response(
            {
                "ok": False,
                "error": "Payload must include integer from_chat_id and message_id values",
            },
            status=400,
        )

    user_ids = await client.mongodb.full_userbase()
    percentage = payload.get("user_percentage")
    limit = payload.get("user_limit")
    selected_users = choose_subset(user_ids, percentage=percentage, limit=limit)

    stats = await broadcast_source_message(
        client,
        from_chat_id=source_chat_id,
        message_id=source_message_id,
        user_ids=selected_users,
    )

    return web.json_response(
        {
            "ok": True,
            "bot_username": getattr(client, "username", None),
            "bot_name": getattr(client, "name", None),
            "targeted_users": len(selected_users),
            "stats": stats,
            "status_text": build_broadcast_status(stats),
        }
    )
