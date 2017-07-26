from aiohttp import web
from hashlib import md5
import argparse
from webkov.servant import pretty, legible, CHARACTERS
from webkov.servant import gen_models, generate_tokens
import os


async def handler(request):
    name = request.match_info.get(
        "name", "COMMON").translate({45: " "}).upper()

    if name not in CHARACTERS:
        return web.Response(
            status=404,
            text='''
Either the character was not found or doesn't have enough dialog to
build a model from. Sorry!

Please direct all complaints to /dev/null. Thank you!
''')
    pairargs = [keyvalstring for keyvalstring
                in request.query_string.split("&")]
    args = {}
    for keyvalstring in pairargs:
        if len(keyvalstring.split("=")) == 2:
            key, value = keyvalstring.split("=")
            args[key] = value

    if 'tokens' in args and int(args['tokens']) > 75000:
        return web.Response(
            status=403,
            text='''
A plague o' all your API calls!
There is a maximum of 75000 tokens per request.
            ''')

    num_tokens = int(args.get('tokens', '200'))
    if bool(args.get('legible', False)):
        toks = legible(
            name=name,
            num_tokens=num_tokens,
            tag=bool(args.get('tag', False)))
    else:
        toks = generate_tokens(
            name=name,
            num_tokens=num_tokens,
            order=int(args.get(
                'order', '1')))
    text = pretty(toks) + "\n"
    return web.Response(text=text)


def _muse():
    return int(
        md5("shakespeare".encode("utf-8")).hexdigest(),
        base=16) % 65535  # should be 18293


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--port', metavar='18293',
                           type=int, default=_muse(),
                           dest='port',
                           help='Port to run shakespeare on')
    argparser.add_argument('--addr', metavar='0.0.0.0',
                           default='0.0.0.0',
                           dest='addr',
                           help='Interface to bind to. Defaults to all.')
    argparser.add_argument('--uid', metavar='18294',
                           # probably gonna bite me later for using muse
                           type=int, default=_muse()+1,
                           dest='uid',
                           help='User to drop after initializing')
    argparser.add_argument('--gid', metavar='18294',
                           # ah screw it let's double down on bad decisions
                           type=int, default=_muse()+1,
                           dest='gid',
                           help='User to drop after initializing')
    
    args = argparser.parse_args()
    print("Generating models..")
    # we don't care about the return value, just that they're cached.
    gen_models()

    # drop privileges to our own dedicated user
    os.setuid(args.uid)
    os.setgid(args.gid)

    app = web.Application()

    app.router.add_get('/', handler)
    app.router.add_get('/{name}', handler)
    web.run_app(app, host=args.addr, port=args.port)
