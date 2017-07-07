from contextlib import contextmanager
import re
import time
from collections import deque


@contextmanager
def rj():
    out = open("./rj.txt", 'r', encoding='utf-8')
    yield out
    out.close()


# Targets are lines like these, with brackets in the front
# [Aside] Villain and he be many miles asunder.--
IS_TARGET_REG = re.compile(r"^\s*\[.*]\s*(.*$)")

TRAILING_PUNCT_LIST = [
    ";",
    "'",
    ".",
    '"',
    ",",
    ":",
    "-",
]

TRAILING_PUNCT = "".join(TRAILING_PUNCT_LIST)

# we don't consider "'" punctuation
TRAILING_PUNCT_SET = set(TRAILING_PUNCT_LIST)



def is_target(line):
    # go down the list of targets until you find one.
    # a simpler implementation might be to ignore all targets, and
    # only match brackets.
    return IS_TARGET_REG.match(line)


# this happens twice. I could just ignore the two lines, but that's a
# little brittle, isn't it?
IS_NOISE_REG = re.compile("^[Nn]oise")


def is_noisy(tokens):
    return IS_NOISE_REG.match(tokens[0])


TITLES = set([
    "LADY",
    "Lady",
    "First",
    "Second",
    "Third",
    "FRIAR",
])
is_voice_reg = re.compile(r"\A[a-zA-Z]+\s*$")


def is_voice(tokens):
    num_words = len(tokens)
    if num_words == 1:
        word = tokens[0]
        return word not in HEADINGS and is_voice_reg.match(word)
    elif num_words == 2:
        # maybe:
        title, name = tokens
        if title in TITLES:
            return is_voice_reg.match(name)


# any line starting with these indicates non-dialog. Ignore this line
# and any lines after it, until a character speaks.
HEADINGS = set([
    "PROLOGUE",
    "SCENE",
    "ACT",
])


def is_heading(tokens):
    return tokens[0] in HEADINGS


ACTIONS = set([
    "enter",
    "beats",
    "re-enter",
    "retiring",
    "retires",
    "dies",  # :(
    "laying",
    "advances",
    "falls",
    "singing",  # mercutio does this once. Only occurence
    "exeunt",
    "exit",
    "drawing",  # twice, both actions.
])


def is_action(tokens):
    # since there's a ton of these, we're going to just take the first
    # word, downcase it, and see if it's in ACTIONS.
    if tokens[0].lower() in ACTIONS:
        return True
    return len(tokens) >= 2 and tokens[:2] == ["They", "fight"]


def rj_stream():
    '''
    Top level function for intermediary deque structure containing map
    between names and contiguous soliliquys (and... witty one liners)
    '''
    out = deque()
    pass


def soliliquy_pull():
    '''Generator that pulls in names and the dialog after them,
    yielding tuples mapping names to dialog. The only non-dialog
    portion is the prologue of the first act, so we tag it here to be
    imported as common.'''
    out = ['COMMON', []]
    stream = sanitized_pull()

    for line in stream:
        if is_voice(line):
            yield out
            # reinitialize with name
            out = [line, []]
        # okay, it's text. Good idea to tokenize here and extend
        # the list.
        else:
            out[1].extend(tokenize[line])


def sanitized_pull():
    with rj() as rjf:
        line = rjf.readline()
        while line:
            # keep reading lines until we get visible text.
            # if we encounter any junk, remove it here.
            targeted = is_target(line)
            if targeted:
                yield targeted.groups()[0]
            # if I were to redo this class based, I would wrap lines
            # in some class that had this metadata constructed at init
            else:
                # we're not interested in punctuation right now.
                # rstrip it.
                tokens = [tok.rstrip(TRAILING_PUNCT)
                          for tok in line.split()]
                if tokens and not (
                        is_noisy(tokens) or
                        is_action(tokens) or
                        is_heading(tokens)):
                    yield line

            # no matter what, read the next line, even if you haven't
            # yielded.
            line = rjf.readline.strip()


def tokenize(line):
    whitesep = line.split()
    out = []
    for token in whitesep:
        # expecting a singleton out of maybe_split_token
        # otherwise we'll get garbage characters
        out.extend(maybe_split_token(token))
    return out


def maybe_split_token(token):
    '''Always return a list . Returning a string is gonna be messy'''
    # we're only interested in trailing punctuation. Everything else
    # we'll consider a word.
    # oh, and an apostrophe is not punctuation.
    out = []
    chars = reversed(token)
    for char in chars:
        if char in TRAILING_PUNCT_SET:
            out.append(char)
        else:
            break

    # if there's any punctuation, take the rest of the token and add
    # it to out otherwise this token should just be returned in a
    # singleton
    if out:
        out.append(token[:-len(out)])
        return list(reversed(out))
    return [token]




# ==================== DEMO STUFF ====================


def loop(skip=0):
    # is there a 'start the loop' construct in python?
    lines = _pull()
    for hop in range(skip):
        next(lines)
    count = skip
    for line in lines:
        out = _prompt()
        count += 1
        if out == 'q':
            break
        else:
            print(_result(_annotate(line), count, line))


def lazy_loop(skip=0):
    # unimport sleep when this is over
    lines = _pull()
    for hop in range(skip):
        next(lines)
    count = skip
    for line in lines:
        print(_result(_annotate(line), count, line))
        count += 1
        time.sleep(0.8)


def _result(annotate, count, line):
    return "{}: {} {}".format(annotate, count, line)


def _pull():
    with rj() as rjf:
        # initialize the loop
        line = rjf.readline()
        # while line isn't the empty string
        while line:
            # keep reading lines until we get visible text
            if not line:
                yield line
            line = rjf.readline()


def _prompt():
    while True:
        out = input("Continue or quit? (c/q): ")
        if out in ['c', 'q']:
            return out


def _annotate(line):
    if is_heading(line):
        return "L"
    if is_action(line):
        return "A"
    if is_voice(line):
        return "V"
    else:
        return "S"
