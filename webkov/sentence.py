#!/usr/bin/env python3

from collections import deque

# handle post, get requests.
# get requests simply display some index. No other paths are supported
# maybe mention POSTs...

# interface?
# sha256sum is the hash of the total mapping.
# is there a way to check if a signature already exists?


# markov.jarmac.org/?id=<sha256sum>&token=<word>&strict=False

import re

WORDSEP = re.compile("[- ]+")

# case insensitive.
# only interested in words that end with '.'
# what about ellipses?...
# ABBREVS = set([
#     mr.
#     ms.
#     esq.
#     dr.
#     p.s.
#     etc.
#     ])

# take a stream of characters and extract sentences out of them.
# perhaps return a generator that does this?


# present a unified interface to tokens?

def nothing():
    a = 1
    while True:
        a+= 1
        yield a

def split_chunk_to_tokens(chunk):
    # replace re with just split? this saves some stack traversal.
    raw_tokens =  WORDSEP.split(chunk)
    out = deque()
    for tok in raw_tokens:
        # empty token string. can happen with two sequential spaces
        if not tok:
            continue
        # okay not empty. parse as usual
        result = parse_token(tok) 
        if not result:
            continue
        if type(tok) == str:
            out.append(result)
        elif type(tok) == deque:
            # deques are consumed from the right.
            out.extendleft(tok)
    return out

FRONT_PUNC = set([
    '(',
    '[',
    '"',
    '{',  # I have never seen someone use this in prose but *shrugs*
    "'"
])

BACK_PUNC = set([
    ')',
    ']',
    '"',
    '}'
    "'",
])

SENTENCE_PUNC = set([
    '.',
    ',',
    ';',
    '!',
])

def parse_token(token):
    # the only thing we're interested in is surrounding punctuation.
    # check first letter for punctuation. this is rare. grounds to recurse?
    if token[0] in FRONT_PUNC:
        if len(token) == 1:
            # just a standalone front punc. ignore it.
            return None
        else:
            return parse_token(token[1:])
    if token[-1] in BACK_PUNC:
        if len(token) == 1:
            # just a standalone back punc. ignore it.
            return None
        else:
            return parse_token(token[-1:])
    if token[-1] in SENTENCE_PUNC:
        pass
    # check last letter for punctuation. If it's a period, check for ellipses.
    # if it's a comma, 

