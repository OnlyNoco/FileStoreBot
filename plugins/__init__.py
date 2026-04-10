#(©)Codeflix Bots (ProYato)

from aiohttp import web

from .route import routes

#===============================================================#

async def web_server(client=None):
    web_app = web.Application(client_max_size=30000000)
    web_app["bot_client"] = client
    web_app.add_routes(routes)
    return web_app
