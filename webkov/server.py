from aiohttp import web
from hashlib import md5
from webkov.servant import pretty, legible, get_characters


async def handle(request):
    # get name, translating hyphens to spaces, uppercasing the result
    name = request.match_info.get(
        "name", "COMMON").translate(
            # map hyphens to spaces.
            {45: " "}).upper()

    # if name isn't in characters, aiohttp returns a 404 on our behalf.
    if name in get_characters():
        toks = legible(name=name)
        text = pretty(toks)
        return web.Response(text=text)


def main():
    muse = int(md5("shakespeare".encode("utf-8")).hexdigest(), base=16)
    port = muse % 65535  # should be 18293
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/{name}', handle)
    web.run_app(app, port=port)
