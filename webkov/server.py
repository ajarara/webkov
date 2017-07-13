from aiohttp import web
from hashlib import md5
from webkov.servant import pretty, legible, get_characters
from webkov.servant import gen_models, generate_tokens


def gen_coroutine(token_generator):
    async def coroutine(request):
        # get name, translating hyphens to spaces, uppercasing the result
        name = request.match_info.get(
            "name", "COMMON").translate(
                # map hyphens to spaces.
                {45: " "}).upper()

        # if name isn't in characters, aiohttp returns a 404 on our behalf.
        if name in get_characters():
            print(dir(request))
            toks = token_generator(
                name=name,
                num_tokens=int(request.query.get(
                    'tokens', 200)),
                order=int(request.query.get(
                    'order', '1')))
            text = pretty(toks) + "\n"
            return web.Response(text=text)

        return web.Response(
            status=404,
            text=(
                "That character either does not exist or does \n"
                "not have enough lines to build a model from. \n"
                "\n"
                "Sorry! Please direct all complaints to /dev/null"))
    return coroutine


def main():
    print("Generating models.. (this will take a while)")
    # we don't care about the return value, just that they're cached.
    gen_models()
    print("Filtering list of eligible characters..")
    get_characters()

    muse = int(md5("shakespeare".encode("utf-8")).hexdigest(), base=16)
    port = muse % 65535  # should be 18293
    app = web.Application()
    basic_handle = gen_coroutine(generate_tokens)
    legible_handle = gen_coroutine(legible)
    
    app.router.add_get('/', basic_handle)
    app.router.add_get('/{name}', basic_handle)
    app.router.add_get('/legible/', legible_handle)
    app.router.add_get('/legible/{name}', legible_handle)
    web.run_app(app, port=port)
